import time
from typing import Dict, Any, List, Optional
import math

class ContextualTracker:
    """
    Maintains the state of detected objects over time to extract contextual events
    rather than just momentary detections.
    """
    
    def __init__(self, movement_threshold: float = 50.0, time_threshold_sec: float = 10.0):
        # Dictionary to keep track of objects (e.g. users, pets)
        # Format: { "object_id": {"last_pos": (x, y), "last_moved_time": float, "first_seen_time": float, "state": str} }
        self.objects: Dict[str, Dict[str, Any]] = {}
        
        # How many pixels of movement is considered "moving"
        self.movement_threshold = movement_threshold
        
        # How long (in seconds) an object must remain stationary to trigger a "resting/stationary" event
        self.time_threshold_sec = time_threshold_sec

    def _calculate_distance(self, pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def update(self, detections: List[Dict[str, Any]], current_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Takes in a list of raw detections for the current frame and updates internal state.
        Returns a list of contextual events if any thresholds are met.
        
        Expected detection format: {"id": "person_1", "centroid": (x, y), "label": "person"}
        """
        if current_time is None:
            current_time = time.time()
            
        events = []
        
        # Update state for current detections
        for det in detections:
            obj_id = det.get("id")
            centroid = det.get("centroid")
            label = det.get("label", "unknown")
            
            if not obj_id or not centroid:
                continue
                
            if obj_id not in self.objects:
                # New object detected
                self.objects[obj_id] = {
                    "last_pos": centroid,
                    "last_moved_time": current_time,
                    "first_seen_time": current_time,
                    "state": "active",
                    "label": label
                }
                events.append({
                    "type": "object_entered",
                    "description": f"A {label} ({obj_id}) has entered the view.",
                    "object_id": obj_id,
                    "timestamp": current_time
                })
            else:
                # Existing object, calculate movement
                obj = self.objects[obj_id]
                dist = self._calculate_distance(obj["last_pos"], centroid)
                
                if dist > self.movement_threshold:
                    # Object moved significantly
                    if obj["state"] == "stationary":
                        events.append({
                            "type": "movement_resumed",
                            "description": f"The {label} ({obj_id}) has started moving again.",
                            "object_id": obj_id,
                            "timestamp": current_time
                        })
                    obj["last_pos"] = centroid
                    obj["last_moved_time"] = current_time
                    obj["state"] = "active"
                else:
                    # Object hasn't moved much, check time threshold
                    time_stationary = current_time - obj["last_moved_time"]
                    if time_stationary >= self.time_threshold_sec and obj["state"] != "stationary":
                        obj["state"] = "stationary"
                        events.append({
                            "type": "stationary_prolonged",
                            "description": f"The {label} ({obj_id}) has been stationary for over {int(self.time_threshold_sec)} seconds.",
                            "object_id": obj_id,
                            "timestamp": current_time
                        })
                        
        # TODO: Handle objects that have disappeared from view (cleanup and "object_left" events)
        
        return events
