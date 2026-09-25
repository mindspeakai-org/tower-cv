import json
import cv2
import argparse
from src.pipeline.capture import FrameStreamer
from src.inference.detector import ObjectDetector
from src.pipeline.tracker import ContextualTracker
from src.core.logger import EventLogger

def main(source, show_video=True):
    # Initialize components
    streamer = FrameStreamer(source=source, fps=30)
    detector = ObjectDetector(model_path="yolov8n-pose.pt")
    logger = EventLogger(db_path="data/tower_events.db")
    
    # Define some sample zones for contextual tracking
    # Format: "zone_name": (x1, y1, x2, y2)
    sample_zones = {
        "living_room_couch": (100, 100, 500, 400),
        "front_door": (0, 0, 150, 600)
    }
    
    # We set time_threshold_sec low (e.g. 3 seconds) for quick testing of "stationary" events
    tracker = ContextualTracker(movement_threshold=20.0, time_threshold_sec=3.0, zones=sample_zones)
    
    print("--- Tower CV Pipeline Started ---")
    print("Waiting for contextual events...\n")
    
    try:
        for frame in streamer.stream():
            # 1. Run inference
            annotated_frame, detections = detector.predict(frame)
            
            # 2. Update tracking state and get contextual events
            events = tracker.update(detections)
            
            # 3. Output events (The Contextual API)
            for event in events:
                # In a real system, this JSON would be sent to an MQTT broker, WebSocket, or local DB
                print(json.dumps(event, indent=2))
                # Log to local DB
                logger.log_event(event)
                
            # 4. Display the video feed (optional)
            if show_video:
                cv2.imshow("Tower CV - Realtime Analysis", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
    except KeyboardInterrupt:
        print("\nPipeline stopped by user.")
    finally:
        streamer.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Tower CV pipeline")
    parser.add_argument("--source", default=0, help="Video source: 0 for webcam, or path to image dir/video")
    parser.add_argument("--headless", action="store_true", help="Run without showing video window")
    args = parser.parse_args()
    
    # Convert source to int if it's '0'
    source = int(args.source) if args.source == '0' else args.source
    
    main(source=source, show_video=not args.headless)
