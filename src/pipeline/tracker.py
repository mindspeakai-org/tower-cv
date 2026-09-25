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

    def _estimate_pose(self, det: Dict[str, Any]) -> str:
        """
        Estimates the pose of a person based on bounding box proportions.
        If the width is significantly larger than the height, they might be lying down.
        """
        if det.get("label") != "person":
            return "unknown"
            
        bbox = det.get("bbox")
        if not bbox:
            return "unknown"
            
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        # Very simple heuristic
        if width > height * 1.2:
            return "lying_down"
        elif height > width * 2:
            return "standing"
        else:
            return "sitting_or_bending"

    def update(self, detections: List[Dict[str, Any]], current_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Takes in a list of raw detections for the current frame and updates internal state.
        Returns a list of contextual events if any thresholds are met.
        
        Expected detection format: {"id": "person_1", "centroid": (x, y), "label": "person"}
        """
        if current_time is None:
            current_time = time.time()
            
        events = []
        
        # Keep track of which IDs were seen in this frame
        seen_ids = set()
        
        # Update state for current detections
        for det in detections:
            obj_id = det.get("id")
            centroid = det.get("centroid")
            label = det.get("label", "unknown")
            
            if not obj_id or not centroid:
                continue
                
            seen_ids.add(obj_id)
                
            if obj_id not in self.objects:
                # New object detected
                pose_state = self._estimate_pose(det)
                self.objects[obj_id] = {
                    "last_pos": centroid,
                    "last_moved_time": current_time,
                    "first_seen_time": current_time,
                    "last_seen_time": current_time,
                    "state": "active",
                    "pose": pose_state,
                    "label": label
                }
                events.append({
                    "type": "object_entered",
                    "description": f"A {label} ({obj_id}) has entered the view in a {pose_state} pose.",
                    "object_id": obj_id,
                    "timestamp": current_time
                })
            else:
                # Existing object, calculate movement
                obj = self.objects[obj_id]
                dist = self._calculate_distance(obj["last_pos"], centroid)
                
                # Check for pose changes
                current_pose = self._estimate_pose(det)
                if current_pose != "unknown" and current_pose != obj["pose"]:
                    events.append({
                        "type": "pose_changed",
                        "description": f"The {label} ({obj_id}) changed pose from {obj['pose']} to {current_pose}.",
                        "object_id": obj_id,
                        "timestamp": current_time,
                        "pose": current_pose
                    })
                    obj["pose"] = current_pose
                
                # Update last seen
                obj["last_seen_time"] = current_time
                
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
                        
        # Cleanup objects that have disappeared from view
        # If we haven't seen an object for 5 seconds, consider it gone.
        LOST_THRESHOLD_SEC = 5.0
        lost_ids = []
        for obj_id, obj in self.objects.items():
            if obj_id not in seen_ids:
                if (current_time - obj["last_seen_time"]) > LOST_THRESHOLD_SEC:
                    events.append({
                        "type": "object_left",
                        "description": f"The {obj['label']} ({obj_id}) has left the view.",
                        "object_id": obj_id,
                        "timestamp": current_time
                    })
                    lost_ids.append(obj_id)
                    
        for obj_id in lost_ids:
            del self.objects[obj_id]
            
        return events
