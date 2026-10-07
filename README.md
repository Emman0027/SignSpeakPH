# SignSpeakPH - Batch capture version

Fixes an accuracy problem caused by the streaming version's latency, not just speed. See app.py's top comment for the full explanation:

Short version: streaming one frame per HTTP request meant a "30-frame" sequence was stretched across 10-15+ seconds of real time (300-500ms round trip x 30), while the model was trained on 30 frames captured in under a second. That mismatch degrades accuracy independent of whether MediaPipe/TFLite themselves are fast or correct.

This version captures all 30 frames in the BROWSER first, at native webcam speed (~1 second, no network involved - matching how your gesture data was originally recorded), then sends them together in one request. The server processes all 30 and returns one prediction.

## Architecture Overview

SignSpeakPH follows a client-server architecture designed to minimize latency-induced accuracy degradation in sign language recognition:

### System Components
1. **Frontend (Browser)**: Captures 30 consecutive frames at native webcam speed using getUserMedia API
2. **Backend (Flask API)**: Receives batch of frames, processes them through MediaPipe pipeline, runs inference with TensorFlow Lite model
3. **Model**: TensorFlow Lite model trained on sequences of 258-dimensional keypoint vectors (pose + left hand + right hand)
4. **MediaPipe Pipeline**: Optimized Pose+Hands solution (no Holistic) for faster processing while maintaining required 258-feature vector

### Data Flow
1. Browser accesses `index.html` served by Flask
2. User performs sign, browser captures 30 frames locally via webcam
3. Frames converted to base64 and sent as JSON payload to `/predict_batch` endpoint
4. Backend decodes images, processes each through MediaPipe Pose+Hands
5. Keypoints extracted to form 30-frame sequence tensor (1, 30, 258)
6. TensorFlow Lite model runs inference, returns predicted sign and confidence
7. Result returned to browser for display

### Key Design Decisions
- **Batch Processing**: Eliminates network latency accumulation by processing all frames in single request
- **Pose+Hands over Holistic**: Avoids unnecessary face mesh computation for 2x speed improvement
- **Stateless Backend**: No shared buffer between requests, enabling horizontal scaling
- **Browser-side Timing Match**: Captures frames at same speed as original training data collection

## Project Structure
```
SignSpeakPH/
├── app.py                 # Main Flask application
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pyproject.toml        # Code formatting/linting configuration
├── Dockerfile            # Containerization configuration
├── src/
│   └── utils/
│       └── mediapipe_utils.py  # Optimized MediaPipe helper functions
├── config/
│   └── settings.py       # Configuration constants and paths
├── data/
│   └── feedback/         # Stores user feedback (JSON format)
├── tests/
│   ├── unit/             # Unit tests for endpoints and utilities
│   └── integration/      # Integration tests (to be implemented)
├── templates/
│   └── index.html        # Main user interface
├── static/               # Static assets (CSS, JavaScript, images)
├── notebooks/            # Jupyter notebooks for experimentation
└── .ai-context/          # Project memory system (TASKS.md, PRIORITIES.md, etc.)
```

## Development Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git (for version control)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SignSpeakPH
   ```

2. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install pre-commit hooks (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Available Scripts and Commands

#### Running the Application
```bash
# Development mode
python app.py

# Production (using Gunicorn or similar)
# See Dockerfile for production deployment example
```

#### Code Quality Tools
```bash
# Check code formatting with black
black --check .

# Format code with black
black .

# Lint code with flake8
flake8 .

# Type checking with mypy
mypy .

# Run all checks (via pre-commit)
pre-commit run --all-files
```

#### Testing
```bash
# Run unit tests
python -m pytest tests/unit/ -v

# Run tests with coverage (when configured)
# python -m pytest tests/ --cov=src --cov=app -v
```

#### Environment Variables
- `PORT`: Port to run the application on (default: 5000)
- `MEDIAPIPE_DISABLE_GPU`: Set to "1" to disable GPU acceleration attempts (important for CPU-only environments)

### Configuration
Configuration is managed through `config/settings.py` which loads from JSON files:
- `config.json`: Main configuration parameters
- `labels.json`: Mapping of model output indices to sign labels
- `MODEL_PATH`: Path to TensorFlow Lite model file (set in config.json)

### Directory Purposes
- `data/feedback/`: Stores user feedback submitted through the `/feedback` endpoints
- `tests/unit/`: Unit tests for individual components (endpoints, utility functions)
- `tests/integration/`: Integration tests for full workflows (to be implemented)
- `src/utils/`: Contains optimized MediaPipe utilities (Pose+Hands instead of Holistic)
- `templates/`: HTML templates served by Flask
- `static/`: Static assets (CSS, JavaScript, images)

## 1. Copy your trained files here
- `action.tflite`
- `labels.json`
- `config.json`

## 2. Test locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 - you'll see a red "Recording sign..." badge for about 1 second, then "processing...", then the result. This cycle repeats automatically.

## 3. Deploy
Same as before - push to your repo, redeploy on Render (or wherever you're hosting), using the same Dockerfile.

## What to expect
- Each full cycle = ~1s capture + however long server-side processing of 30 frames takes (check the terminal's [timing] line, or the on-screen "capture Xms + process Yms" readout).
- Recognition accuracy should now much more closely match what you saw in your notebook's live test loop (Cell 70), since frame timing is restored to near-native speed.
- If processing time is still high, that's now purely a MediaPipe/TFLite compute question (already using Pose+Hands, model_complexity=0, 320x240 frames, GPU disabled) - not a latency-accumulation problem anymore.

## Feedback System
The application includes a feedback system to collect user experiences:
- POST `/feedback`: Submit feedback with rating (1-5) and optional comment
- PUT `/feedback/<id>`: Update existing feedback
- DELETE `/feedback/<id>`: Delete feedback
- Feedback is stored as JSON in `data/feedback/feedback.json`

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `python -m pytest tests/unit/ -v`
5. Format code: `black .`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

Please ensure your code follows the project's coding standards:
- PEP 8 compliance (enforced via flake8)
- Type hints where possible
- Immutable data patterns preferred
- Comprehensive error handling
- Clear, descriptive naming conventions

## License
[Specify your license here]