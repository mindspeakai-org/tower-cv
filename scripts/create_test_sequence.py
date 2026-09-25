import cv2
import os
import shutil
import numpy as np

def create_sequence():
    """
    Creates a mock image sequence using a sample image from the YouHome-Dataset repository.
    Simulates a person standing still for 30 frames, and then "falling" (rotated 90 degrees) for 30 frames.
    """
    sample_img_path = "data/YouHome-Dataset/readme/human_detection_1.jpg"
    out_dir = "data/sample_sequence"
    
    if not os.path.exists(sample_img_path):
        print(f"Error: Could not find {sample_img_path}. Did you clone the repo?")
        return
        
    # Clean up output directory
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    
    # Read the base image
    img = cv2.imread(sample_img_path)
    if img is None:
        print("Error: Failed to load image.")
        return
        
    print(f"Generating test sequence in {out_dir}...")
    
    # Generate 30 frames of the normal image (simulating 1 second of standing/sitting)
    for i in range(30):
        frame_path = os.path.join(out_dir, f"frame_{i:04d}.jpg")
        cv2.imwrite(frame_path, img)
        
    # Generate 30 frames of the image rotated 90 degrees (simulating a fall)
    # YOLO should still detect the person, but the bounding box / keypoints will indicate lying down
    rotated_img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    
    for i in range(30, 60):
        frame_path = os.path.join(out_dir, f"frame_{i:04d}.jpg")
        cv2.imwrite(frame_path, rotated_img)
        
    print(f"Successfully generated 60 frames in {out_dir}/")
    print("\nYou can now test the pipeline by running:")
    print("python -m src.pipeline.main --source data/sample_sequence")

if __name__ == "__main__":
    create_sequence()
