import time

class TelemetryAggregator:
    def __init__(self, battery_sim, motor_sim, temp_sim):
        """
        Aggregate telemetry from multiple simulator components
        
        Args:
            battery_sim: BatterySimulator instance
            motor_sim: MotorSimulator instance
            temp_sim: TemperatureSimulator instance
        """
        self.battery_sim = battery_sim
        self.motor_sim = motor_sim
        self.temp_sim = temp_sim
        
        self.start_time = time.time()
        self.total_energy = 0.0  # Wh
        self.total_distance = 0.0  # km
        self.last_update = time.time()
    
    def get_aggregated_telemetry(self):
        """
        Get aggregated telemetry from all components
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        
        # Get individual component states
        battery_state = self.battery_sim.get_state()
        motor_state = self.motor_sim.get_state()
        temp_state = self.temp_sim.get_state()
        
        # Calculate energy consumption
        if elapsed > 0:
            # Power (W) * time (h) = energy (Wh)
            energy_delta = (motor_state['power'] * (elapsed / 3600.0))
            self.total_energy += energy_delta
            
            # Speed (km/h) * time (h) = distance (km)
            distance_delta = (motor_state['speed'] * (elapsed / 3600.0))
            self.total_distance += distance_delta
        
        # Calculate efficiency metrics
        wh_per_km = 0.0
        if self.total_distance > 0:
            wh_per_km = self.total_energy / self.total_distance
        
        range_estimate = 0.0
        if wh_per_km > 0:
            remaining_energy = (battery_state['level'] / 100.0) * battery_state['voltage'] * self.battery_sim.capacity
            range_estimate = remaining_energy / wh_per_km
        
        # Return aggregated telemetry
        return {
            "timestamp": now,
            "uptime": now - self.start_time,
            
            # Battery metrics
            "battery_level": battery_state['level'],
            "battery_voltage": battery_state['voltage'],
            "battery_current": battery_state['current'],
            "battery_temperature": battery_state['temperature'],
            "battery_charging": battery_state['charging'],
            
            # Motor metrics
            "speed": motor_state['speed'],
            "target_speed": motor_state['target_speed'],
            "motor_power": motor_state['power'],
            "motor_temperature": motor_state['temperature'],
            "motor_rpm": motor_state['rpm'],
            "motor_torque": motor_state['torque'],
            "motor_efficiency": motor_state['efficiency'],
            
            # Temperature metrics
            "ambient_temperature": temp_state['ambient'],
            "controller_temperature": temp_state['controller'],
            
            # Calculated metrics
            "total_energy_consumed": self.total_energy,  # Wh
            "total_distance": self.total_distance,  # km
            "energy_efficiency": wh_per_km,  # Wh/km
            "estimated_range": range_estimate,  # km
            
            # System status
            "system_health": self._calculate_health(battery_state, motor_state, temp_state)
        }
    
    def _calculate_health(self, battery_state, motor_state, temp_state):
        """
        Calculate overall system health based on component states
        
        Returns a value between 0 (critical) and 100 (perfect)
        """
        # Start with perfect health
        health = 100.0
        
        # Battery factors
        if battery_state['level'] < 20.0:
            health -= (20.0 - battery_state['level'])
        
        if battery_state['temperature'] > 40.0:
            health -= (battery_state['temperature'] - 40.0) * 2.0
        
        # Motor factors
        if motor_state['temperature'] > 60.0:
            health -= (motor_state['temperature'] - 60.0) * 1.5
        
        # Controller factors
        if temp_state['controller'] > 70.0:
            health -= (temp_state['controller'] - 70.0) * 1.5
        
        # Ensure health is within bounds
        return max(0.0, min(100.0, health))
