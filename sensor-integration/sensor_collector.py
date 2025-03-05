#!/usr/bin/env python3
'''
BME680 Sensor Data Collection for Electric Scooter Testing

This script reads data from a BME680 environmental sensor connected to a Jetson Orin,
stores it in Neo4j, and prepares it for visualization in Grafana.
'''

import time
import datetime
import json
import uuid
import logging
import argparse
from typing import Dict, Any, Optional

# BME680 sensor library
try:
    import bme680
except ImportError:
    # For testing without actual hardware
    from simulator.bme680_simulator import BME680Simulator as bme680

# Neo4j connection
from py2neo import Graph, Node, Relationship

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sensor_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SensorCollector:
    '''
    Collects data from BME680 sensor and stores it in Neo4j
    '''
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str,
                 collection_interval: int = 10, mock: bool = False):
        '''
        Initialize sensor collector
        
        Args:
            neo4j_uri: URI for Neo4j connection
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            collection_interval: Data collection interval in seconds
            mock: Use simulated data instead of real sensor
        '''
        self.collection_interval = collection_interval
        self.mock = mock
        
        # Initialize Neo4j connection
        self.graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
        logger.info("Connected to Neo4j database")
        
        # Initialize sensor
        self._init_sensor()
    
    def _init_sensor(self) -> None:
        '''
        Initialize the BME680 sensor
        '''
        try:
            if self.mock:
                self.sensor = bme680.BME680()
                logger.info("Using simulated BME680 sensor")
            else:
                self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
                logger.info("BME680 sensor initialized")
                
            # Configure the sensor
            self.sensor.set_humidity_oversample(bme680.OS_2X)
            self.sensor.set_pressure_oversample(bme680.OS_4X)
            self.sensor.set_temperature_oversample(bme680.OS_8X)
            self.sensor.set_filter(bme680.FILTER_SIZE_3)
            
            # Configure gas sensor
            self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
            self.sensor.set_gas_heater_temperature(320)
            self.sensor.set_gas_heater_duration(150)
            self.sensor.select_gas_heater_profile(0)
            
            logger.info("BME680 sensor configured")
        except Exception as e:
            logger.error(f"Failed to initialize sensor: {e}")
            if not self.mock:
                logger.warning("Falling back to simulated sensor")
                self.mock = True
                self._init_sensor()
    
    def read_sensor(self) -> Dict[str, Any]:
        '''
        Read current sensor data
        
        Returns:
            Dictionary with sensor readings
        '''
        try:
            if self.sensor.get_sensor_data():
                data = {
                    "temperature": round(self.sensor.data.temperature, 2),  # °C
                    "pressure": round(self.sensor.data.pressure, 2),  # hPa
                    "humidity": round(self.sensor.data.humidity, 2),  # %RH
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # Add gas resistance if available (air quality indicator)
                if self.sensor.data.heat_stable:
                    data["gas_resistance"] = self.sensor.data.gas_resistance  # Ohms
                
                logger.debug(f"Sensor data: {data}")
                return data
            else:
                logger.warning("Failed to get sensor data")
                return {}
        except Exception as e:
            logger.error(f"Error reading sensor: {e}")
            return {}
    
    def store_in_neo4j(self, data: Dict[str, Any]) -> Optional[str]:
        '''
        Store sensor data in Neo4j graph database
        
        Args:
            data: Sensor data dictionary
            
        Returns:
            ID of the created data node or None if failed
        '''
        if not data:
            return None
        
        try:
            # Create unique ID for this reading
            reading_id = str(uuid.uuid4())
            
            # Create timestamp node
            timestamp_node = Node("Timestamp",
                                 value=data["timestamp"],
                                 year=datetime.datetime.fromisoformat(data["timestamp"]).year,
                                 month=datetime.datetime.fromisoformat(data["timestamp"]).month,
                                 day=datetime.datetime.fromisoformat(data["timestamp"]).day,
                                 hour=datetime.datetime.fromisoformat(data["timestamp"]).hour,
                                 minute=datetime.datetime.fromisoformat(data["timestamp"]).minute)
            
            # Create environmental data node
            env_data = dict(data)
            env_data.pop("timestamp", None)  # Remove timestamp from properties
            env_data["id"] = reading_id
            
            env_node = Node("EnvironmentalData", **env_data)
            
            # Create relationship
            measured_at = Relationship(env_node, "MEASURED_AT", timestamp_node)
            
            # Create transaction and commit
            tx = self.graph.begin()
            tx.create(env_node)
            tx.create(timestamp_node)
            tx.create(measured_at)
            tx.commit()
            
            logger.info(f"Stored sensor reading {reading_id} in Neo4j")
            return reading_id
        except Exception as e:
            logger.error(f"Failed to store in Neo4j: {e}")
            return None
    
    def run(self, duration: Optional[int] = None) -> None:
        '''
        Run the data collection loop
        
        Args:
            duration: Optional duration in seconds to run, or None for indefinite
        '''
        start_time = time.time()
        count = 0
        
        try:
            while True:
                # Check if we've reached the duration
                if duration and (time.time() - start_time) > duration:
                    logger.info(f"Reached collection duration of {duration} seconds")
                    break
                
                # Read sensor data
                data = self.read_sensor()
                
                # Store in Neo4j
                if data:
                    reading_id = self.store_in_neo4j(data)
                    if reading_id:
                        count += 1
                        if count % 10 == 0:
                            logger.info(f"Collected {count} readings so far")
                
                # Wait for next collection interval
                time.sleep(self.collection_interval)
        except KeyboardInterrupt:
            logger.info("Collection stopped by user")
        finally:
            logger.info(f"Collection complete. Collected {count} readings.")

def main():
    '''
    Main entry point
    '''
    parser = argparse.ArgumentParser(description="BME680 sensor data collector for EV testing")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j connection URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="password", help="Neo4j password")
    parser.add_argument("--interval", type=int, default=10, help="Collection interval in seconds")
    parser.add_argument("--duration", type=int, help="Collection duration in seconds (optional)")
    parser.add_argument("--mock", action="store_true", help="Use simulated sensor data")
    
    args = parser.parse_args()
    
    collector = SensorCollector(
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password,
        collection_interval=args.interval,
        mock=args.mock
    )
    
    collector.run(args.duration)

if __name__ == "__main__":
    main()
