import time
import random
from typing import List, Dict, Any

class SensorHub:
    """
    Interfaces with physical smart home sensors (e.g., GPIO pins on a Raspberry Pi).
    Monitors changes and emits contextual events.
    """
    def __init__(self):
        print("Initialized SensorHub targeting GPIO/I2C sensors.")
        
        # Simulated state
        self.last_check_time = time.time()
        
        # Baseline environmental values
        self.current_temp = 22.0 # Celsius
        self.current_humidity = 45.0 # Percentage
        self.door_open = False
        
    def poll(self) -> List[Dict[str, Any]]:
        """
        Polls sensors (mocked for now) and returns a list of significant events.
        """
        current_time = time.time()
        events = []
        
        # Only poll every 5 seconds to avoid spamming
        if current_time - self.last_check_time < 5.0:
            return events
            
        self.last_check_time = current_time
        
        # --- MOCK SENSOR READINGS ---
        
        # 1. Door Sensor Simulation (5% chance of door opening/closing)
        if random.random() < 0.05:
            self.door_open = not self.door_open
            state = "opened" if self.door_open else "closed"
            events.append({
                "type": "door_sensor",
                "description": f"The front door was {state}.",
                "sensor_id": "front_door_contact",
                "state": state,
                "timestamp": current_time
            })
            
        # 2. Temperature Simulation (gradual drift)
        temp_change = random.uniform(-0.5, 0.5)
        self.current_temp += temp_change
        
        # Trigger event if temp gets unusually high (e.g., potential fire or left stove)
        if self.current_temp > 30.0:
            events.append({
                "type": "temperature_alert",
                "description": f"High temperature detected: {self.current_temp:.1f}°C",
                "sensor_id": "living_room_temp",
                "value": self.current_temp,
                "timestamp": current_time
            })
            # Cool it down so it doesn't spam forever
            self.current_temp = 25.0 
            
        return events
