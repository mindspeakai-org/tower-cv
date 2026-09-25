import cv2
import os
import glob
from typing import Generator, Optional
import time

class FrameStreamer:
    """
    A unified interface for streaming frames from various sources:
    - Webcam (live)
    - Video file
    - Image directory (simulating a stream, e.g., from a dataset)
    """
    
    def __init__(self, source: str | int = 0, fps: Optional[int] = None):
        self.source = source
        self.fps = fps
        self.is_image_dir = isinstance(source, str) and os.path.isdir(source)
        
        if self.is_image_dir:
            # Grab common image formats and sort them alphabetically
            self.image_paths = sorted(glob.glob(os.path.join(source, "*.[jp][pn]*[g]")))
            if not self.image_paths:
                raise ValueError(f"No images found in directory: {source}")
            self.cap = None
        else:
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                raise ValueError(f"Failed to open video source: {source}")

    def stream(self) -> Generator[cv2.typing.MatLike, None, None]:
        """
        Yields frames one by one. If an FPS is set, it attempts to simulate that framerate.
        """
        delay = 1.0 / self.fps if self.fps else 0

        if self.is_image_dir:
            for path in self.image_paths:
                start_time = time.time()
                frame = cv2.imread(path)
                
                if frame is None:
                    continue
                    
                yield frame
                
                # Simulate framerate for image directories
                if delay > 0:
                    elapsed = time.time() - start_time
                    time.sleep(max(0, delay - elapsed))
        else:
            while self.cap.isOpened():
                start_time = time.time()
                ret, frame = self.cap.read()
                
                if not ret:
                    break
                    
                yield frame
                
                # Simulate framerate if we are reading from a fast video file
                if delay > 0:
                    elapsed = time.time() - start_time
                    time.sleep(max(0, delay - elapsed))

    def release(self):
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    # Example usage:
    # Set to 0 for webcam, or a path to a directory of images
    STREAM_SOURCE = 0 
    
    print(f"Starting stream from: {STREAM_SOURCE}")
    try:
        streamer = FrameStreamer(source=STREAM_SOURCE, fps=30)
        
        for i, frame in enumerate(streamer.stream()):
            # Display the frame
            cv2.imshow('Tower CV Pipeline - Frame Stream', frame)
            
            # Here is where we will inject the Object Detection / AI logic later
            # e.g., frame, detections = detector.predict(frame)
            #       event_tracker.update(detections)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'streamer' in locals():
            streamer.release()
        cv2.destroyAllWindows()
