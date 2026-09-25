import json
import cv2
import argparse
from src.pipeline.capture import FrameStreamer
from src.inference.detector import ObjectDetector
from src.inference.audio import AudioDetector
from src.pipeline.sensors import SensorHub
from src.pipeline.tracker import ContextualTracker
from src.core.logger import EventLogger
from src.core.interpreter import EventInterpreter

def main(source, show_video=True):
    # Initialize components
    streamer = FrameStreamer(source=source, fps=30)
    detector = ObjectDetector(model_path="yolov8n-pose.pt")
    audio_detector = AudioDetector()
    sensor_hub = SensorHub()
    logger = EventLogger(db_path="data/tower_events.db")
    interpreter = EventInterpreter(use_llm=False)  # Set to True if Ollama is running locally
    
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
            
            # 2. Update tracking state and get contextual visual events
            events = tracker.update(detections)
            
            # 2.5 Listen for audio events (mock buffer for now)
            audio_events = audio_detector.listen(audio_buffer=None)
            events.extend(audio_events)
            
            # 2.6 Poll physical sensors (door contacts, temp)
            sensor_events = sensor_hub.poll()
            events.extend(sensor_events)
            
            # 3. Output events (The Contextual API)
            for event in events:
                # Log to local DB
                logger.log_event(event)
                
                # Interpret into natural language
                human_msg = interpreter.translate(event)
                print(f"[TOWER ALERT] {human_msg}")
                # You can still see the raw JSON if you need to debug
                # print(json.dumps(event, indent=2))
                
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
