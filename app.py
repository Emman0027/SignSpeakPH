"""
SignSpeakPH - Flask backend (BATCH version)

Fixes both the speed problem AND an accuracy problem caused by it:
the old per-frame streaming design required a full network round trip for
EACH of the 30 frames. At 300-500ms/frame, collecting a "30-frame" sequence
took 10-15+ seconds of real time - but the model was trained on 30 frames
captured in under a second (natural webcam speed). Stretching that same
30-frame sequence across 15 seconds gives the LSTM a completely different,
much slower motion pattern than what it learned, which degrades accuracy -
independent of whether MediaPipe/TFLite themselves are fast or accurate.

This version has the BROWSER capture all 30 frames locally first (fast,
no network involved, matching how gesture data was originally recorded),
then sends them together in ONE request. The server processes all 30 and
returns a single prediction. This is fully stateless per request - no
shared sequence_buffer between requests/visitors needed anymore, which
also directly fixes the multi-instance slowdown you saw (no more
contention over one global buffer).

Local run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

import base64
import json
import logging
import os
import time
from typing import Optional

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

log.info("Starting SignSpeakPH backend...")

# MediaPipe tries GPU/EGL acceleration by default and silently falls back
# to CPU when it fails - but it retries this failed attempt on EVERY frame,
# wasting time each call. Render's servers have no GPU, so disable this
# attempt entirely before mediapipe is imported (must be set before import).
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request

# tflite-runtime has no official Windows wheels on PyPI (Linux/macOS only),
# so it works fine on deployment (Render's Linux containers) but fails to
# install on a Windows dev machine. Fall back to full TensorFlow's built-in
# tf.lite.Interpreter for local testing - it's the exact same API, so
# nothing else in this file needs to change either way.
try:
    import tflite_runtime.interpreter as tflite
except ModuleNotFoundError:
    import tensorflow as tf
    tflite = tf.lite
    log.info("tflite_runtime not found - using tensorflow.lite.Interpreter instead (fine for local testing)")

from utils.mediapipe_utils import create_models, mediapipe_detection, extract_keypoints
from constants import SIGN_INFO
from config import SEQUENCE_LENGTH, NUM_FEATURES, THRESHOLD

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

interpreter = tflite.Interpreter(model_path=os.path.join(BASE_DIR, "action.tflite"))
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

try:
    with open(os.path.join(BASE_DIR, "labels.json")) as f:
        ACTIONS = json.load(f)
    log.info("Labels loaded successfully")
except FileNotFoundError:
    log.error(f"Labels file not found: {os.path.join(BASE_DIR, 'labels.json')}")
    raise
except json.JSONDecodeError as e:
    log.error(f"Invalid JSON in labels file: {e}")
    raise
except Exception as e:
    log.error(f"Unexpected error loading labels: {e}")
    raise

from constants import SIGN_INFO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB - generous for 30 small JPEGs, blocks abuse

# Pose + Hands models reused across requests.
models = create_models()


def warm_up_model() -> None:
    """
    Run one dummy prediction at startup so the interpreter's internal graph
    setup happens now, not on the first real request from a user - keeps
    the very first live prediction from being slower than the rest.
    """
    try:
        dummy_input = np.zeros((1, SEQUENCE_LENGTH, NUM_FEATURES), dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        interpreter.invoke()
        _ = interpreter.get_tensor(output_details[0]['index'])
        log.info("Model warm-up completed successfully")
    except Exception as e:
        log.warning(f"Model warm-up failed (non-fatal): {e}")


warm_up_model()


def decode_base64_image(data_url: str) -> Optional[np.ndarray]:
    """Convert a data:image/jpeg;base64,... string from the browser into an OpenCV frame."""
    try:
        header, encoded = data_url.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        log.warning(f"Failed to decode image: {e}")
        return None


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/signs")
def signs():
    """
    Returns the sign guide content - only for actions actually present in
    labels.json, so this always matches whatever model is deployed (works
    the same whether you're running the 5-sign backup or the full 22-sign
    model, no manual syncing needed).
    """
    result = []
    for slug in ACTIONS:
        info = SIGN_INFO.get(slug, {"display": slug, "description": "Description not yet added."})
        result.append({"slug": slug, "display": info["display"], "description": info["description"]})
    return jsonify(result)


@app.route("/config")
def get_config():
    """Lets the frontend initialize its adjustable-threshold slider from the real server default."""
    return jsonify({"threshold": THRESHOLD, "sequence_length": SEQUENCE_LENGTH})


@app.route("/predict_batch", methods=["POST"])
def predict_batch():
    """
    Receives all SEQUENCE_LENGTH frames at once (captured locally by the
    browser at native speed), processes them, returns a single prediction.
    Fully stateless - no buffer shared across requests or visitors.
    """
    log.info("Received prediction request")
    payload = request.get_json()
    if not payload or "images" not in payload:
        log.warning("Prediction request missing images")
        return jsonify({"error": "no images provided"}), 400

    images = payload["images"]
    if len(images) != SEQUENCE_LENGTH:
        log.warning(f"Prediction request has incorrect number of frames: expected {SEQUENCE_LENGTH}, got {len(images)}")
        return jsonify({"error": f"expected {SEQUENCE_LENGTH} frames, got {len(images)}"}), 400

    # Optional per-request threshold override (e.g. from a settings slider in
    # the UI) - falls back to the server default from config.json if not
    # provided or invalid, so this endpoint keeps working with old clients.
    effective_threshold = THRESHOLD
    if "threshold" in payload:
        try:
            candidate = float(payload["threshold"])
            if 0.0 <= candidate <= 1.0:
                effective_threshold = candidate
        except (TypeError, ValueError):
            pass

    t0 = time.time()
    sequence = []
    for data_url in images:
        frame = decode_base64_image(data_url)
        if frame is None:
            log.warning("Failed to decode an image in prediction request")
            return jsonify({"error": "could not decode an image"}), 400
        _, results = mediapipe_detection(frame, models)
        keypoints = extract_keypoints(results)
        sequence.append(keypoints)
    t1 = time.time()

    try:
        input_data = np.expand_dims(sequence, axis=0).astype(np.float32)  # (1, 30, 258)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        res = interpreter.get_tensor(output_details[0]['index'])[0]
    except Exception as e:
        log.error(f"Model inference failed: {e}")
        return jsonify({"error": "model inference failed"}), 500
    t2 = time.time()

    idx = int(np.argmax(res))
    confidence = float(res[idx])

    log.info(f"[timing] mediapipe_total={(t1-t0)*1000:.0f}ms ({(t1-t0)*1000/SEQUENCE_LENGTH:.0f}ms/frame) tflite={(t2-t1)*1000:.0f}ms")

    if confidence > effective_threshold:
        log.info(f"Prediction successful: {ACTIONS[idx]} with confidence {confidence:.2f}")
        return jsonify({"text": ACTIONS[idx], "confidence": confidence, "threshold_used": effective_threshold})

    # Below threshold - still report the top guess as a "suggestion" so the
    # UI can show "Did you mean X?" instead of just a bare rejection.
    log.info(f"Prediction below threshold: top guess {ACTIONS[idx]} with confidence {confidence:.2f}")
    return jsonify({
        "text": "",
        "confidence": confidence,
        "suggestion": ACTIONS[idx],
        "threshold_used": effective_threshold,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)