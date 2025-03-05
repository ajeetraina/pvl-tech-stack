#!/usr/bin/env python3
'''
BME680 Sensor Simulator

Provides a simulated BME680 sensor for testing without hardware
'''

import random
import time
import math
from typing import Dict, Any

# Constants for simulated sensor
I2C_ADDR_PRIMARY = 0x76
I2C_ADDR_SECONDARY = 0x77

# Oversample settings
OS_NONE = 0
OS_1X = 1
OS_2X = 2
OS_4X = 3
OS_8X = 4
OS_16X = 5

# Filter settings
FILTER_SIZE_0 = 0
FILTER_SIZE_1 = 1
FILTER_SIZE_3 = 2
FILTER_SIZE_7 = 3
FILTER_SIZE_15 = 4
FILTER_SIZE_31 = 5
FILTER_SIZE_63 = 6
FILTER_SIZE_127 = 7

# Gas sensor settings
ENABLE_GAS_MEAS = 1
DISABLE_GAS_MEAS = 0

class SensorData:
    '''
    Class to hold simulated sensor data
    '''
    def __init__(self):
        self.temperature = 25.0  # Initial temperature °C
        self.pressure = 1013.25  # Initial pressure hPa
        self.humidity = 50.0     # Initial humidity %RH
        self.gas_resistance = 50000.0  # Initial gas resistance Ohms
        self.heat_stable = False

class BME680Simulator:
    '''
    Simulates a BME680 environmental sensor with realistic data patterns
    '''
    def __init__(self, i2c_addr=I2C_ADDR_PRIMARY):
        '''
        Initialize simulated sensor
        
        Args:
            i2c_addr: Simulated I2C address (not used functionally)
        '''
        self.i2c_addr = i2c_addr
        self.data = SensorData()
        
        # Simulation parameters
        self.humidity_oversample = OS_1X
        self.pressure_oversample = OS_1X
        self.temperature_oversample = OS_1X
        self.filter_size = FILTER_SIZE_0
        self.gas_status = DISABLE_GAS_MEAS
        self.gas_heater_temp = 0
        self.gas_heater_duration = 0
        self.gas_heater_profile = 0
        
        # Internal state
        self._last_update = time.time()
        self._temp_trend = 0.0
        self._pressure_trend = 0.0
        self._humidity_trend = 0.0
        self._time_of_day_hours = (time.time() % 86400) / 3600  # 0-24 hours
    
    def set_humidity_oversample(self, value):
        self.humidity_oversample = value
    
    def set_pressure_oversample(self, value):
        self.pressure_oversample = value
    
    def set_temperature_oversample(self, value):
        self.temperature_oversample = value
    
    def set_filter(self, value):
        self.filter_size = value
    
    def set_gas_status(self, value):
        self.gas_status = value
    
    def set_gas_heater_temperature(self, value):
        self.gas_heater_temp = value
    
    def set_gas_heater_duration(self, value):
        self.gas_heater_duration = value
    
    def select_gas_heater_profile(self, value):
        self.gas_heater_profile = value
        
    def get_sensor_data(self):
        '''
        Simulate reading from the sensor with realistic variations
        '''
        now = time.time()
        elapsed = now - self._last_update
        self._last_update = now
        
        # Update time of day (0-24 hours)
        self._time_of_day_hours = (self._time_of_day_hours + (elapsed / 3600)) % 24
        
        # Simulate temperature with daily cycle and random variations
        # Temperature peaks at 14:00 (2PM) and bottoms at 2:00 (2AM)
        daily_temp_cycle = 5.0 * math.sin(((self._time_of_day_hours - 8) / 24) * 2 * math.pi)
        
        # Slowly change trend over time
        self._temp_trend = max(-2.0, min(2.0, self._temp_trend + (random.random() - 0.5) * 0.1 * elapsed))
        
        # Update temperature
        base_temp = 25.0 + self._temp_trend + daily_temp_cycle
        noise = (random.random() - 0.5) * 0.3
        self.data.temperature = round(base_temp + noise, 2)
        
        # Simulate pressure variations (typically 950-1050 hPa)
        # Pressure often inversely correlates with temperature changes
        self._pressure_trend = max(-10.0, min(10.0, self._pressure_trend - (self._temp_trend * 0.5) + (random.random() - 0.5) * 0.5 * elapsed))
        base_pressure = 1013.25 + self._pressure_trend
        pressure_noise = (random.random() - 0.5) * 0.5
        self.data.pressure = round(base_pressure + pressure_noise, 2)
        
        # Simulate humidity (tends to be higher at night, lower during hottest part of day)
        # Humidity is anti-correlated with temperature in many environments
        humidity_cycle = -10.0 * math.sin(((self._time_of_day_hours - 8) / 24) * 2 * math.pi)
        self._humidity_trend = max(-20.0, min(20.0, self._humidity_trend + (random.random() - 0.5) * 0.5 * elapsed))
        base_humidity = 50.0 + self._humidity_trend + humidity_cycle
        humidity_noise = (random.random() - 0.5) * 2.0
        self.data.humidity = round(max(0.0, min(100.0, base_humidity + humidity_noise)), 2)
        
        # Simulate gas resistance (air quality)
        # Lower values typically indicate poorer air quality
        # Affected by humidity and time of day (traffic patterns, etc)
        if self.gas_status == ENABLE_GAS_MEAS:
            # Gas resistance tends to be higher when humidity is lower
            humidity_factor = 1.0 - (self.data.humidity / 150.0)  # Higher humidity, lower resistance
            
            # Air quality tends to be worse during rush hours
            rush_hour_factor = 1.0
            morning_rush = abs(self._time_of_day_hours - 8.0) < 2.0  # 6AM-10AM
            evening_rush = abs(self._time_of_day_hours - 18.0) < 2.0  # 4PM-8PM
            if morning_rush or evening_rush:
                rush_hour_factor = 0.7  # Reduce resistance during rush hours
            
            base_resistance = 50000.0 * humidity_factor * rush_hour_factor
            resistance_noise = (random.random() - 0.3) * 10000.0
            self.data.gas_resistance = max(5000.0, base_resistance + resistance_noise)
            
            # Heat stability depends on heater settings
            if self.gas_heater_temp > 200 and self.gas_heater_duration > 100:
                self.data.heat_stable = True
            else:
                self.data.heat_stable = False
        else:
            self.data.heat_stable = False
        
        return True
