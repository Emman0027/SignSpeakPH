---
type: spec
status: active
tags: [vibe-wise, project-map, signspeakph]
relatedTo: []
---

# Project Map

## Purpose
Create a real-time sign language recognition system that processes 30 consecutive frames in batch to reduce latency-induced accuracy degradation, using MediaPipe for keypoint extraction and TensorFlow Lite for inference.

## Requirements
- Capture 30 consecutive frames at native webcam speed in the browser
- Process frames through MediaPipe Pose+Hands pipeline (258-dimensional keypoint vectors)
- Run inference with TensorFlow Lite model trained on sign language sequences
- Return predicted sign and confidence to the user
- Minimize latency by batch processing all frames in a single request
- Avoid unnecessary computations (e.g., face mesh) for speed
- Provide user feedback submission and storage
- Support cross-platform deployment via Docker

## Components
- **app.py**: Main Flask application handling HTTP requests and model inference
- **src/utils/mediapipe_utils.py**: Optimized MediaPipe helper functions for Pose+Hands extraction
- **config/settings.py**: Configuration management loading from JSON files
- **config.json**: Main configuration parameters (including MODEL_PATH)
- **labels.json**: Mapping of model output indices to sign labels
- **templates/index.html**: Main user interface for webcam capture and result display
- **static/**: Static assets (CSS, JavaScript, images)
- **data/feedback/**: Storage for user feedback submitted via /feedback endpoints
- **tests/unit/**: Unit tests for endpoints and utility functions
- **requirements.txt**: Production dependencies (Flask, TensorFlow, MediaPipe, etc.)
- **requirements-dev.txt**: Development dependencies (testing, formatting tools)
- **pyproject.toml**: Code formatting/linting configuration (black, flake8, mypy)
- **Dockerfile**: Containerization configuration for deployment

## Main Flow
[Browser] 
    ↓ (getUserMedia)
[Webcam Capture: 30 frames at native speed]
    ↓ (base64 encoding)
[HTTP POST to /predict_batch]
    ↓ (Flask endpoint)
[Backend: decode images]
    ↓ (MediaPipe Pose+Hands processing)
[Keypoint extraction: 30-frame tensor (1, 30, 258)]
    ↓ (TensorFlow Lite inference)
[Predicted sign and confidence]
    ↓ (HTTP response)
[Browser: display result]

## Data and Trust Boundaries
- **Input**: Webcam video frames (user-controlled via browser permissions)
- **Processing**: Local MediaPipe keypoint extraction, TensorFlow Lite inference (all server-side)
- **Output**: Predicted sign label and confidence score
- **Storage**: User feedback stored as JSON in data/feedback/feedback.json
- **External Dependencies**: TensorFlow Lite model file, labels.json, config.json (must be provided)

## Build and Deployment
- **Dependencies**: See requirements.txt (Flask, opencv-python, mediapipe, tensorflow, etc.)
- **Installation**: pip install -r requirements.txt && pip install -r requirements-dev.txt
- **Execution**: Development: python app.py; Production: gunicorn or similar (see Dockerfile example)
- **Configuration**: 
  - Model path set in config.json (MODEL_PATH)
  - Labels mapping in labels.json
  - Other parameters in config.json (DEBUG, PORT, etc.)
  - Environment variables: PORT, MEDIAPIPE_DISABLE_GPU

## Unknowns
- **Model Accuracy**: Current TensorFlow Lite model performance with batch processing
- **Frame Rate Impact**: Processing time for 30 frames on target hardware
- **Webcam Compatibility**: Variability across different webcam drivers and resolutions
- **Deployment Scaling**: Horizontal scaling considerations for stateless backend
- **Feedback Integration**: How user feedback is used to improve the model
- **Error Handling**: Robustness to missing model files or invalid inputs
- **Security**: Input validation and sanitization for HTTP endpoints