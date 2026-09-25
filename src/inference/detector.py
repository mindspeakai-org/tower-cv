from typing import List, Dict, Any, Tuple
import cv2
import numpy as np

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

class ObjectDetector:
    """
    A generic wrapper for edge-friendly object detection models using YOLOv8.
    """
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        
        if ULTRALYTICS_AVAILABLE:
            print(f"Loading YOLO model from: {self.model_path}...")
            # Load the model (will download yolov8n.pt if not exists locally)
            self.model = YOLO(self.model_path)
        else:
            self.model = None
            print("WARNING: ultralytics package not found. Running in MOCK mode.")

    def predict(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Runs object detection on a single frame.
        
        Returns:
            - annotated_frame: The frame with bounding boxes drawn.
            - detections: A list of dictionaries representing detected objects.
        """
        annotated_frame = frame.copy()
        detections = []
        
        if self.model is None:
            # --- MOCK DETECTION LOGIC FALLBACK ---
            height, width = frame.shape[:2]
            center_x, center_y = int(width / 2), int(height / 2)
            mock_detection = {
                "id": "person_0",
                "label": "person",
                "centroid": (center_x, center_y),
                "bbox": (center_x - 50, center_y - 100, center_x + 50, center_y + 100),
                "confidence": 0.95
            }
            detections.append(mock_detection)
            x1, y1, x2, y2 = mock_detection["bbox"]
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"person {mock_detection['confidence']:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            return annotated_frame, detections

        # --- REAL YOLO INFERENCE WITH TRACKING ---
        # Run inference using the built-in tracker (ByteTrack by default)
        results = self.model.track(frame, conf=self.confidence_threshold, persist=True, verbose=False)[0]
        
        # Loop through detected boxes
        if results.boxes.id is not None:
            # We have tracking IDs
            track_ids = results.boxes.id.int().cpu().tolist()
            boxes = results.boxes.xyxy.cpu().numpy().astype(int)
            confs = results.boxes.conf.cpu().numpy()
            clss = results.boxes.cls.cpu().numpy().astype(int)
            
            for i in range(len(boxes)):
                track_id = track_ids[i]
                x1, y1, x2, y2 = boxes[i]
                conf = float(confs[i])
                cls_id = clss[i]
                
                # Get class name mapping (e.g., 0 -> 'person', 16 -> 'dog')
                label = self.model.names[cls_id]
                
                # We are mostly interested in people and pets for Tower
                if label not in ['person', 'dog', 'cat', 'bird']:
                    continue
                    
                centroid = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                
                # Use the tracking ID assigned by YOLO's tracker
                obj_id = f"{label}_{track_id}"
                
                detection = {
                    "id": obj_id,
                    "label": label,
                    "centroid": centroid,
                    "bbox": (x1, y1, x2, y2),
                    "confidence": conf
                }
                detections.append(detection)
                
                # Draw bounding box, label, and tracking ID
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(annotated_frame, f"{obj_id} {conf:.2f}", 
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        
        return annotated_frame, detections
