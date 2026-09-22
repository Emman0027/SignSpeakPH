"""
Configuration management for the SignSpeakPH application.
Loads and provides access to configuration values.
"""

import json
import logging
import os

log = logging.getLogger(__name__)

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load configuration from config.json
def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        log.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON in configuration file: {config_path} - {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error loading configuration file: {config_path} - {e}")
        raise

# Load configuration once at module import
try:
    _CONFIG = load_config()
    log.info("Configuration loaded successfully")
except Exception as e:
    log.error(f"Failed to load configuration: {e}")
    raise

# Configuration values
SEQUENCE_LENGTH = _CONFIG["sequence_length"]   # 30
NUM_FEATURES = _CONFIG["num_features"]         # 258 - must match model input_shape
THRESHOLD = _CONFIG["threshold"]               # 0.7

log.info(f"Loaded configuration: sequence_length={SEQUENCE_LENGTH}, num_features={NUM_FEATURES}, threshold={THRESHOLD}")

# File paths
ACTION_TFLITE_PATH = os.path.join(BASE_DIR, "action.tflite")
LABELS_JSON_PATH = os.path.join(BASE_DIR, "labels.json")
CONFIG_JSON_PATH = os.path.join(BASE_DIR, "config.json")

# Function to get config value (allows for reloading if needed)
def get_config_value(key, default=None):
    """Get a configuration value by key."""
    return _CONFIG.get(key, default)

# Function to reload configuration (useful for development)
def reload_config():
    """Reload configuration from config.json file."""
    global _CONFIG, SEQUENCE_LENGTH, NUM_FEATURES, THRESHOLD
    try:
        _CONFIG = load_config()
        SEQUENCE_LENGTH = _CONFIG["sequence_length"]
        NUM_FEATURES = _CONFIG["num_features"]
        THRESHOLD = _CONFIG["threshold"]
        log.info("Configuration reloaded successfully")
    except Exception as e:
        log.error(f"Failed to reload configuration: {e}")
        raise