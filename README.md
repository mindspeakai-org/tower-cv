# Tower Computer Vision (Tower CV)

Tower is an AI home monitor designed to understand what’s happening around it, rather than just recording everything like a traditional security camera. This repository contains the computer vision and edge AI components for Tower.

## Goal
To shift from simple event detection ("motion detected") to contextual understanding ("grandma hasn't moved from the living room for longer than usual").

## Project Structure

- `data/`: Sample videos, images, and datasets for testing and evaluation (ignored by git).
- `models/`: Downloaded model weights (e.g., YOLO, MediaPipe, custom models - ignored by git).
- `notebooks/`: Jupyter notebooks for prototyping and exploration.
- `src/`: Main source code directory.
  - `core/`: Configuration, logging, and core utilities.
  - `inference/`: Wrappers for different ML models and inference engines (PyTorch, ONNX, TFLite).
  - `pipeline/`: Video capture, frame processing, and event tracking logic.
  - `utils/`: Helper functions (drawing bounding boxes, format conversions, etc.).
- `tests/`: Unit and integration tests.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
