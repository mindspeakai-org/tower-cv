from typing import Dict, Any, List
import time

class BehaviorEngine:
    """
    Evaluates contextual events against specific use-case profiles (Elder Care, Pet Monitoring, etc.)
    to generate high-level, meaningful insights rather than just raw event logs.
    """
    def __init__(self, mode: str = "pet_monitoring"):
        # Available modes: elder_care, baby_monitoring, pet_monitoring, home_security
        self.mode = mode
        print(f"BehaviorEngine initialized in '{self.mode}' mode.")
        
        # Keep track of when we last alerted for an object to avoid spamming
        self.last_alert_times: Dict[str, float] = {}
        
    def _can_alert(self, object_id: str, cooldown: float = 300) -> bool:
        """Prevents spamming the same alert for the same object (cooldown in seconds)."""
        now = time.time()
        last_time = self.last_alert_times.get(object_id, 0)
        if (now - last_time) > cooldown:
            self.last_alert_times[object_id] = now
            return True
        return False

    def evaluate(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a contextual event and decides if it constitutes an "unusual" situation 
        or an insight that requires the user's attention.
        """
        insights = []
        event_type = event.get("type")
        obj_id = event.get("object_id", "unknown")
        label = obj_id.split('_')[0] if '_' in obj_id else "unknown"
        zone = event.get("zone")
        pose = event.get("pose")
        
        # --- ELDER CARE LOGIC ---
        if self.mode == "elder_care" and label == "person":
            # 1. Fall detection (Pose is lying down in a non-bed zone)
            if event_type == "pose_changed" and pose == "lying_down":
                if zone not in ["bedroom_bed", "living_room_couch"]:
                    insights.append({
                        "priority": "CRITICAL",
                        "insight": f"Attention: Someone ({obj_id}) may have fallen in the {zone or 'room'}. They are on the floor."
                    })
            
            # 2. Prolonged immobility in unusual places
            if event_type == "stationary_prolonged":
                if zone == "bathroom":
                    insights.append({
                        "priority": "HIGH",
                        "insight": f"Check in requested: {obj_id} has been in the bathroom for longer than usual."
                    })
                elif zone == "living_room_couch" and self._can_alert(obj_id, cooldown=3600):
                    insights.append({
                        "priority": "INFO",
                        "insight": f"Update: {obj_id} is resting in the living room."
                    })

        # --- PET MONITORING LOGIC ---
        elif self.mode == "pet_monitoring" and label in ["dog", "cat"]:
            # 1. Waiting by the door
            if event_type == "stationary_prolonged" and zone == "front_door":
                if self._can_alert(obj_id):
                    insights.append({
                        "priority": "INFO",
                        "insight": f"Your {label} has been waiting near the door for a while. They might need to go outside."
                    })
            
            # 2. Unusual activity (e.g., getting on forbidden furniture)
            if event_type == "zone_entered" and zone == "kitchen_counter":
                if self._can_alert(obj_id, cooldown=60):
                    insights.append({
                        "priority": "WARNING",
                        "insight": f"Your {label} just jumped on the kitchen counter!"
                    })

        # --- BABY MONITORING LOGIC ---
        elif self.mode == "baby_monitoring" and label == "person":
            # 1. Waking up
            if event_type == "movement_resumed" and zone == "crib":
                insights.append({
                    "priority": "INFO",
                    "insight": "The baby is moving in the crib and might be waking up."
                })
        
        # --- GENERAL SENSOR LOGIC (Cross-mode) ---
        if event_type == "audio_detected":
            sound = event.get("sound_class")
            if sound == "glass_breaking":
                insights.append({
                    "priority": "CRITICAL",
                    "insight": "Glass breaking sound detected!"
                })
            elif self.mode == "baby_monitoring" and sound == "baby_crying":
                if self._can_alert("baby_audio", cooldown=120):
                    insights.append({
                        "priority": "HIGH",
                        "insight": "The baby is crying."
                    })
            elif self.mode == "pet_monitoring" and sound == "dog_barking":
                if self._can_alert("pet_audio", cooldown=120):
                    insights.append({
                        "priority": "INFO",
                        "insight": "Your dog is barking."
                    })

        return insights
