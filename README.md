# Tower Computer Vision (Tower CV)

Tower is an AI home monitor designed to understand what’s happening around it, rather than just recording everything like a traditional security camera. This repository contains the computer vision, multi-modal context, and edge AI components for Tower.

## Goal
To shift from simple event detection ("motion detected") to contextual understanding ("grandma hasn't moved from the living room for longer than usual").

## Architecture
The Tower pipeline is a complete, multi-modal edge AI engine:

1. **Vision:** Uses YOLOv8 with ByteTrack for persistent multi-object tracking and 17-point pose estimation to detect *how* people and pets are positioned.
2. **Audio:** An `AudioDetector` that listens for key environmental sounds (baby crying, glass breaking).
3. **Physical Sensors:** A `SensorHub` that polls GPIO/I2C sensors for door contacts and temperature changes.
4. **Contextual Tracker:** Analyzes raw detections across time and space (e.g., triggering a `stationary_prolonged` event if an object stays in a specific zone).
5. **Behavior Engine:** Evaluates events based on the current mode (`elder_care`, `pet_monitoring`, `baby_monitoring`) to generate meaningful insights (e.g., "Attention: Someone may have fallen").
6. **Data Persistence:** Logs all events to a local SQLite database (`data/tower_events.db`).
7. **Interpreter:** Translates cold JSON events into natural language notifications.
8. **API Server:** A FastAPI application to query historical events and daily summaries.

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The YOLOv8 models will automatically download their weights the first time you run the pipeline).*

### Setting up the YouHome Dataset (Optional for Testing)
Tower was developed and tested using the YouHome Activities of Daily Living (ADL) Dataset, which is excellent for testing indoor multi-modal context since it features irregular poses and lighting.

1. Clone the YouHome Dataset repository into the `data/` folder:
   ```bash
   git clone https://github.com/UIUC-ChenLab/YouHome-Dataset.git data/YouHome-Dataset
   ```
2. The repository contains the training code, but the actual image data is hosted externally. Download the image dataset from their [Official Box Link](https://uofi.box.com/s/21k90kmybyuinsssk8ygsjhbqluu5n7e).
3. Extract the downloaded images into `data/YouHome-Dataset/Images/`.

You can now explore the dataset by running the Tower pipeline directly against one of the activity folders (e.g., `Activity_1`).

## Usage

### 1. Run the Main Pipeline
You can run the main pipeline against different sources. The system will process vision, simulate audio/sensors, and output natural language alerts.

**Use a Live Webcam:**
```bash
python -m src.pipeline.main --source 0
```

**Use a Video File:**
```bash
python -m src.pipeline.main --source path/to/video.mp4
```

**Use a Dataset Image Sequence (e.g. YouHome Dataset):**
```bash
python -m src.pipeline.main --source data/YouHome-Dataset/Images/Activity_1
```
*(Add `--headless` if you are running on a device without a display monitor, like a Raspberry Pi).*

### 2. Run the API Server
To view historical events or connect a frontend dashboard, start the FastAPI server in a separate terminal:
```bash
source .venv/bin/activate
python -m src.api.server
```
You can view the interactive API documentation at: `http://localhost:8000/docs`

### 3. Run the Fall Detection Test
We included a script that uses a sample image from the YouHome dataset to generate a 60-frame synthetic sequence of a person standing, and then suddenly "falling" (rotating 90 degrees). 

Generate the sequence:
```bash
python scripts/create_test_sequence.py
```

Run the pipeline on it (make sure `main.py` has `BehaviorEngine(mode="elder_care")`):
```bash
python -m src.pipeline.main --source data/sample_sequence --headless
```
You should see Tower detect the person, realize their pose changed to `lying_down`, and output a `[CRITICAL]` fall alert!
