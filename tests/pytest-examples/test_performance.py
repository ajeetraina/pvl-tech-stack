import pytest
import requests
import time
import can
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Constants
SCOOTER_API_URL = "http://scooter-api:8080"
CAN_INTERFACE = "can0"

@pytest.fixture
def setup_can_bus():
    """Set up CAN bus connection to scooter"""
    bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
    yield bus
    bus.shutdown()

@pytest.fixture
def setup_api_connection():
    """Set up REST API connection to scooter"""
    # Check if API is available
    response = requests.get(f"{SCOOTER_API_URL}/status")
    assert response.status_code == 200, "API is not available"
    return SCOOTER_API_URL

def test_motor_performance(setup_can_bus, setup_api_connection):
    """Test motor performance under various load conditions"""
    bus = setup_can_bus
    api_url = setup_api_connection
    
    # Test parameters
    speeds = [10, 20, 30]  # km/h
    test_duration = 30  # seconds per speed
    
    performance_data = []
    
    for target_speed in speeds:
        # Set target speed
        response = requests.post(
            f"{api_url}/motor/speed",
            json={"speed": target_speed}
        )
        assert response.status_code == 200, f"Failed to set speed to {target_speed}"
        
        # Collect data for test duration
        start_time = time.time()
        speed_data = []
        current_data = []
        voltage_data = []
        temperature_data = []
        
        while time.time() - start_time < test_duration:
            # Read CAN messages
            message = bus.recv(1.0)  # 1s timeout
            
            if message is not None:
                if message.arbitration_id == 0x100:  # Speed message
                    speed = int.from_bytes(message.data[0:2], byteorder='big') / 10.0
                    speed_data.append(speed)
                    
                elif message.arbitration_id == 0x200:  # Current message
                    current = int.from_bytes(message.data[0:2], byteorder='big') / 10.0
                    current_data.append(current)
                    
                elif message.arbitration_id == 0x300:  # Voltage message
                    voltage = int.from_bytes(message.data[0:2], byteorder='big') / 10.0
                    voltage_data.append(voltage)
                    
                elif message.arbitration_id == 0x400:  # Temperature message
                    temp = int.from_bytes(message.data[0:2], byteorder='big') / 10.0
                    temperature_data.append(temp)
        
        # Stop motor
        requests.post(f"{api_url}/motor/speed", json={"speed": 0})
        
        # Calculate metrics
        avg_speed = np.mean(speed_data) if speed_data else 0
        avg_current = np.mean(current_data) if current_data else 0
        avg_voltage = np.mean(voltage_data) if voltage_data else 0
        avg_temperature = np.mean(temperature_data) if temperature_data else 0
        power = avg_voltage * avg_current
        
        performance_data.append({
            "target_speed": target_speed,
            "actual_speed": avg_speed,
            "current": avg_current,
            "voltage": avg_voltage,
            "temperature": avg_temperature,
            "power": power
        })
        
        # Allow motor to cool down
        time.sleep(10)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(performance_data)
    
    # Assert performance requirements
    for index, row in df.iterrows():
        # Speed accuracy within 5%
        speed_accuracy = abs(row["actual_speed"] - row["target_speed"]) / row["target_speed"]
        assert speed_accuracy <= 0.05, f"Speed accuracy out of range at {row['target_speed']} km/h"
        
        # Temperature should be below 70°C
        assert row["temperature"] < 70, f"Motor temperature too high at {row['target_speed']} km/h"
        
        # Power consumption should be within expected range
        expected_power = calculate_expected_power(row["target_speed"])
        power_deviation = abs(row["power"] - expected_power) / expected_power
        assert power_deviation <= 0.15, f"Power consumption out of range at {row['target_speed']} km/h"
    
    # Create performance report
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(df["target_speed"], df["actual_speed"], 'o-')
    plt.plot(df["target_speed"], df["target_speed"], '--')
    plt.xlabel("Target Speed (km/h)")
    plt.ylabel("Actual Speed (km/h)")
    plt.title("Speed Accuracy")
    
    plt.subplot(2, 2, 2)
    plt.plot(df["target_speed"], df["power"], 'o-')
    plt.xlabel("Speed (km/h)")
    plt.ylabel("Power (W)")
    plt.title("Power Consumption")
    
    plt.subplot(2, 2, 3)
    plt.plot(df["target_speed"], df["current"], 'o-')
    plt.xlabel("Speed (km/h)")
    plt.ylabel("Current (A)")
    plt.title("Motor Current")
    
    plt.subplot(2, 2, 4)
    plt.plot(df["target_speed"], df["temperature"], 'o-')
    plt.xlabel("Speed (km/h)")
    plt.ylabel("Temperature (°C)")
    plt.title("Motor Temperature")
    
    plt.tight_layout()
    plt.savefig("motor_performance_report.png")

def calculate_expected_power(speed):
    """Calculate expected power consumption based on speed"""
    # This is a simplified model - would be calibrated for actual scooter
    return 100 + 5 * speed + 0.5 * speed**2
