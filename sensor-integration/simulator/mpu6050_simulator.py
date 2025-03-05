#!/usr/bin/env python3
'''
MPU6050 Accelerometer/Gyroscope Sensor Simulator

Provides a simulated MPU6050 sensor for testing without hardware
'''

import time
import math
import random
numpy_available = False
try:
    import numpy as np
    numpy_available = True
except ImportError:
    pass

class MPU6050Simulator:
    '''
    Simulates an MPU6050 accelerometer and gyroscope with realistic data patterns
    including synthetic fall and pothole events
    '''
    def __init__(self):
        '''
        Initialize the simulated sensor
        '''
        # Base acceleration values (gravity is primarily on z-axis when flat)
        self._accel_x = 0.0
        self._accel_y = 0.0
        self._accel_z = 9.8  # Earth gravity in m/s^2
        
        # Base gyroscope values (zero when not rotating)
        self._gyro_x = 0.0
        self._gyro_y = 0.0
        self._gyro_z = 0.0
        
        # Sensor temperature
        self._temperature = 25.0
        
        # Simulation parameters
        self._init_time = time.time()
        self._last_update = self._init_time
        self._scenario = "normal"  # normal, fall, pothole
        self._scenario_start = 0
        self._scenario_duration = 0
        self._scenario_progress = 0
        
        # Schedule random events
        self._schedule_next_event()
    
    def _schedule_next_event(self):
        '''
        Schedule the next simulation event (fall or pothole)
        '''
        # Events occur randomly every 20-60 seconds
        next_event_time = random.uniform(20, 60)
        self._scenario_start = time.time() + next_event_time
        
        # 30% chance of fall, 70% chance of pothole
        event_type = random.random()
        if event_type < 0.3:
            self._scenario = "fall"
            self._scenario_duration = 2.0  # Falls last about 2 seconds
        else:
            self._scenario = "pothole"
            self._scenario_duration = 0.5  # Potholes last about 0.5 seconds
            
    def _update_normal_riding(self):
        '''
        Simulate normal riding conditions with small vibrations
        '''
        # Small random vibrations
        self._accel_x = random.uniform(-0.5, 0.5)
        self._accel_y = random.uniform(-0.5, 0.5)
        self._accel_z = 9.8 + random.uniform(-0.3, 0.3)
        
        # Small random rotations
        self._gyro_x = random.uniform(-0.2, 0.2)
        self._gyro_y = random.uniform(-0.2, 0.2)
        self._gyro_z = random.uniform(-0.1, 0.1)
        
        # Occasionally simulate turns (changes in gyro_z)
        if random.random() < 0.05:  # 5% chance per reading
            turn_direction = 1 if random.random() < 0.5 else -1
            self._gyro_z = turn_direction * random.uniform(0.5, 1.5)
            
    def _update_fall(self, progress):
        '''
        Simulate a fall event
        
        Args:
            progress: Value from 0 to 1 indicating progress through the event
        '''
        if progress < 0.1:
            # Initial lean (bike starting to tip)
            lean_angle = progress * 10 * math.pi / 180  # Convert to radians
            self._accel_x = 9.8 * math.sin(lean_angle)
            self._accel_z = 9.8 * math.cos(lean_angle)
            self._gyro_x = random.uniform(0.5, 1.0)  # Rotation rate increasing
        
        elif progress < 0.3:
            # Free fall phase (near-zero acceleration)
            self._accel_x = random.uniform(-1.0, 1.0)
            self._accel_y = random.uniform(-1.0, 1.0)
            self._accel_z = random.uniform(-1.0, 1.0)
            self._gyro_x = random.uniform(2.0, 5.0)  # High rotation rate
            self._gyro_y = random.uniform(-2.0, 2.0)
        
        elif progress < 0.4:
            # Impact
            impact_direction = random.choice(["side", "front"])
            if impact_direction == "side":
                self._accel_x = random.uniform(25.0, 35.0)  # High side impact
                self._accel_y = random.uniform(-5.0, 5.0)
                self._accel_z = random.uniform(5.0, 10.0)
            else:
                self._accel_x = random.uniform(-5.0, 5.0)
                self._accel_y = random.uniform(25.0, 35.0)  # High front impact
                self._accel_z = random.uniform(5.0, 10.0)
            
            # Sudden stop in rotation
            self._gyro_x = random.uniform(-10.0, 10.0)  # Chaotic rotation during impact
            self._gyro_y = random.uniform(-10.0, 10.0)
            self._gyro_z = random.uniform(-10.0, 10.0)
        
        else:
            # Stationary after fall
            fall_angle = random.uniform(60, 90) * math.pi / 180  # Final resting angle
            self._accel_x = 9.8 * math.sin(fall_angle)  # Gravity component on x-axis
            self._accel_y = random.uniform(-1.0, 1.0)
            self._accel_z = 9.8 * math.cos(fall_angle)  # Reduced gravity on z-axis
            
            # Very little rotation after fall
            self._gyro_x = random.uniform(-0.1, 0.1)
            self._gyro_y = random.uniform(-0.1, 0.1)
            self._gyro_z = random.uniform(-0.1, 0.1)
    
    def _update_pothole(self, progress):
        '''
        Simulate hitting a pothole
        
        Args:
            progress: Value from 0 to 1 indicating progress through the event
        '''
        if progress < 0.3:
            # Initial drop (front wheel hitting pothole)
            self._accel_z = -9.8 - random.uniform(5.0, 15.0)  # Strong negative z acceleration
            self._accel_x = random.uniform(-2.0, 2.0)  # Small x component
            self._accel_y = random.uniform(-2.0, 2.0)  # Small y component
            
            # Rotation around x-axis (pitch) as front wheel drops
            self._gyro_x = random.uniform(2.0, 4.0)
            self._gyro_y = random.uniform(-0.5, 0.5)
            self._gyro_z = random.uniform(-0.5, 0.5)
        
        elif progress < 0.7:
            # Impact as wheel exits pothole (strong positive z acceleration)
            self._accel_z = 9.8 + random.uniform(5.0, 15.0)  # Strong positive z acceleration
            self._accel_x = random.uniform(-3.0, 3.0)  # Possible x component
            self._accel_y = random.uniform(-3.0, 3.0)  # Possible y component
            
            # Reverse rotation around x-axis (pitch) as wheel comes up
            self._gyro_x = random.uniform(-3.0, -1.0)
            self._gyro_y = random.uniform(-0.5, 0.5)
            self._gyro_z = random.uniform(-0.5, 0.5)
        
        else:
            # Settling after pothole (oscillations damping out)
            self._accel_z = 9.8 + random.uniform(-2.0, 2.0) * (1.0 - progress) * 2  # Oscillations damping
            self._accel_x = random.uniform(-1.0, 1.0) * (1.0 - progress) * 2
            self._accel_y = random.uniform(-1.0, 1.0) * (1.0 - progress) * 2
            
            # Decreasing oscillations in rotation
            self._gyro_x = random.uniform(-1.0, 1.0) * (1.0 - progress) * 2
            self._gyro_y = random.uniform(-0.5, 0.5) * (1.0 - progress) * 2
            self._gyro_z = random.uniform(-0.5, 0.5) * (1.0 - progress) * 2
    
    def _update_simulation(self):
        '''
        Update the simulated sensor readings based on the current time and scenario
        '''
        now = time.time()
        elapsed = now - self._last_update
        self._last_update = now
        
        # Update temperature with small random drift
        self._temperature += random.uniform(-0.05, 0.05) * elapsed
        self._temperature = min(45.0, max(15.0, self._temperature))  # Keep within reasonable bounds
        
        # Check if we should be in a special event scenario
        if self._scenario != "normal" and now >= self._scenario_start:
            # Calculate progress through the event
            event_elapsed = now - self._scenario_start
            progress = min(1.0, event_elapsed / self._scenario_duration)
            self._scenario_progress = progress
            
            # Update based on the current scenario
            if self._scenario == "fall":
                self._update_fall(progress)
            elif self._scenario == "pothole":
                self._update_pothole(progress)
            
            # Check if the event is complete
            if progress >= 1.0:
                self._scenario = "normal"
                self._schedule_next_event()
        else:
            # Normal riding simulation
            self._update_normal_riding()
    
    @property
    def acceleration(self):
        '''
        Get the current acceleration values
        
        Returns:
            Tuple of (x, y, z) acceleration in m/s^2
        '''
        self._update_simulation()
        return (self._accel_x, self._accel_y, self._accel_z)
    
    @property
    def gyro(self):
        '''
        Get the current gyroscope values
        
        Returns:
            Tuple of (x, y, z) rotation rates in rad/s
        '''
        # No need to update again, acceleration property already did
        return (self._gyro_x, self._gyro_y, self._gyro_z)
    
    @property
    def temperature(self):
        '''
        Get the current temperature
        
        Returns:
            Temperature in degrees Celsius
        '''
        # No need to update again, acceleration property already did
        return self._temperature

# Simple test function
def test_simulator():
    '''
    Test the simulator by printing values for a few seconds
    '''
    sensor = MPU6050Simulator()
    
    print("Testing MPU6050 simulator for 10 seconds...")
    start_time = time.time()
    
    while time.time() - start_time < 10:
        accel = sensor.acceleration
        gyro = sensor.gyro
        temp = sensor.temperature
        
        # Calculate magnitude of acceleration
        if numpy_available:
            accel_mag = np.sqrt(accel[0]**2 + accel[1]**2 + accel[2]**2)
        else:
            accel_mag = math.sqrt(accel[0]**2 + accel[1]**2 + accel[2]**2)
        
        print(f"Accel (m/s²): X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}, Mag={accel_mag:.2f}")
        print(f"Gyro (rad/s): X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f}")
        print(f"Temp (°C): {temp:.2f}")
        print("---")
        
        time.sleep(0.5)

if __name__ == "__main__":
    test_simulator()
