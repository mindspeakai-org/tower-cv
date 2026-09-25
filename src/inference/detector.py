from typing import List, Dict, Any, Tuple
import cv2
import numpy as np

class ObjectDetector:
    """
    A generic wrapper for edge-friendly object detection models (e.g., YOLOv8, MediaPipe).
    Currently implemented using a placeholder/mock structure, ready to be swapped with a real model.
    """
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        
        # TODO: Initialize real model here. 
        # Example for YOLOv8:
        # from ultralytics import YOLO
        # self.model = YOLO(self.model_path)
        
        print(f"Initialized ObjectDetector (Mock) targeting model: {model_path}")

    def predict(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Runs object detection on a single frame.
        
        Returns:
            - annotated_frame: The frame with bounding boxes drawn.
            - detections: A list of dictionaries representing detected objects.
        """
        annotated_frame = frame.copy()
        detections = []
        
        # --- MOCK DETECTION LOGIC ---
        # In a real implementation, this would be:
        # results = self.model(frame, conf=self.confidence_threshold)[0]
        # for box in results.boxes:
        #     xyxy = box.xyxy[0].cpu().numpy()
        #     centroid = ((xyxy[0] + xyxy[2]) / 2, (xyxy[1] + xyxy[3]) / 2)
        #     detections.append({"id": "...", "centroid": centroid, ...})
        
        # For testing the tracker, let's inject a fake stationary person in the middle of the screen
        height, width = frame.shape[:2]
        center_x, center_y = int(width / 2), int(height / 2)
        
        # Mock detection payload
        mock_detection = {
            "id": "person_0",
            "label": "person",
            "centroid": (center_x, center_y),
            "bbox": (center_x - 50, center_y - 100, center_x + 50, center_y + 100),
            "confidence": 0.95
        }
        detections.append(mock_detection)
        
        # Draw mock bounding box
        x1, y1, x2, y2 = mock_detection["bbox"]
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"person {mock_detection['confidence']:.2f}", 
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
        return annotated_frame, detections
