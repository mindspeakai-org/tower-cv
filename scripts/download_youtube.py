import argparse
import os
import subprocess
import sys

def download_video(url: str, output_path: str = "data/youtube_test.mp4"):
    """
    Downloads a YouTube video to the specified output path using yt-dlp.
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Remove existing file if it exists to avoid conflicts
    if os.path.exists(output_path):
        os.remove(output_path)
        
    print(f"Downloading video from {url}...")
    print("This might take a minute depending on the video length and your internet connection.\n")
    
    try:
        # Use yt-dlp to download the video
        # -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' ensures we get an MP4
        command = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", output_path,
            url
        ]
        
        subprocess.run(command, check=True)
        print(f"\n✅ Successfully downloaded video to: {output_path}")
        print("\nYou can now run the Tower pipeline on this video using:")
        print(f"python -m src.pipeline.main --source {output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error downloading video. Make sure yt-dlp is installed and the URL is valid.")
        print(f"Error details: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: 'yt-dlp' command not found.")
        print("Please ensure you have installed the project requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a YouTube video to test with Tower CV")
    parser.add_argument("url", help="The YouTube URL to download")
    parser.add_argument("--output", default="data/youtube_test.mp4", help="Output path for the downloaded video")
    
    args = parser.parse_args()
    download_video(args.url, args.output)
