"""
Configuration management for SignSpeakPH
"""
import json
import os
from pathlib import Path

# settings.py lives in <repo>/src/config/, so the repo root is three levels up.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "data" / "models" / "production"


def _get_version():
    """Read version from VERSION file, default to v1.0.0 if not found."""
    version_file = MODELS_DIR / "VERSION"
    try:
        with open(version_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "v1.0.0"


# Model configuration
_version = _get_version()
MODEL_PATH = MODELS_DIR / f"action_{_version}.tflite"
LABELS_PATH = MODELS_DIR / f"labels_{_version}.json"
CONFIG_PATH = MODELS_DIR / f"config_{_version}.json"

# Flask configuration
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

# MediaPipe configuration
MEDIAPIPE_DISABLE_GPU = os.environ.get("MEDIAPIPE_DISABLE_GPU", "1")

# Load configuration from config.json
try:
    with open(CONFIG_PATH, "r") as f:
        config_data = json.load(f)
except FileNotFoundError:
    config_data = {}

SEQUENCE_LENGTH = config_data.get("sequence_length", 30)
NUM_FEATURES = config_data.get("num_features", 258)
THRESHOLD = config_data.get("threshold", 0.7)
PROHIBITED_SIGNS = set(
    config_data.get("prohibited_signs", [])
)  # can be overridden by environment or config

# Feedback storage
FEEDBACK_FILE = BASE_DIR / "data" / "feedback" / "feedback.json"


def load_model_config():
    """Load model labels and config"""
    import json

    with open(LABELS_PATH, "r") as f:
        labels = json.load(f)

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    return labels, config
