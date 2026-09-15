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
import os
import time

# MediaPipe tries GPU/EGL acceleration by default and silently falls back
# to CPU when it fails - but it retries this failed attempt on EVERY frame,
# wasting time each call. Render's servers have no GPU, so disable this
# attempt entirely before mediapipe is imported (must be set before import).
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request
import tflite_runtime.interpreter as tflite

from utils.mediapipe_utils import create_models, mediapipe_detection, extract_keypoints

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

interpreter = tflite.Interpreter(model_path=os.path.join(BASE_DIR, "action.tflite"))
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

with open(os.path.join(BASE_DIR, "labels.json")) as f:
    ACTIONS = json.load(f)

with open(os.path.join(BASE_DIR, "config.json")) as f:
    CONFIG = json.load(f)

SEQUENCE_LENGTH = CONFIG["sequence_length"]   # 30
NUM_FEATURES = CONFIG["num_features"]         # 258 - must match model input_shape
THRESHOLD = CONFIG["threshold"]               # 0.7

app = Flask(__name__)

# Pose + Hands models reused across requests.
models = create_models()


def decode_base64_image(data_url):
    """Convert a data:image/jpeg;base64,... string from the browser into an OpenCV frame."""
    header, encoded = data_url.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict_batch", methods=["POST"])
def predict_batch():
    """
    Receives all SEQUENCE_LENGTH frames at once (captured locally by the
    browser at native speed), processes them, returns a single prediction.
    Fully stateless - no buffer shared across requests or visitors.
    """
    payload = request.get_json()
    if not payload or "images" not in payload:
        return jsonify({"error": "no images provided"}), 400

    images = payload["images"]
    if len(images) != SEQUENCE_LENGTH:
        return jsonify({"error": f"expected {SEQUENCE_LENGTH} frames, got {len(images)}"}), 400

    t0 = time.time()
    sequence = []
    for data_url in images:
        frame = decode_base64_image(data_url)
        if frame is None:
            return jsonify({"error": "could not decode an image"}), 400
        _, results = mediapipe_detection(frame, models)
        keypoints = extract_keypoints(results)
        sequence.append(keypoints)
    t1 = time.time()

    input_data = np.expand_dims(sequence, axis=0).astype(np.float32)  # (1, 30, 258)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    res = interpreter.get_tensor(output_details[0]['index'])[0]
    t2 = time.time()

    idx = int(np.argmax(res))
    confidence = float(res[idx])

    print(f"[timing] mediapipe_total={(t1-t0)*1000:.0f}ms ({(t1-t0)*1000/SEQUENCE_LENGTH:.0f}ms/frame) tflite={(t2-t1)*1000:.0f}ms")

    if confidence > THRESHOLD:
        return jsonify({"text": ACTIONS[idx], "confidence": confidence})
    return jsonify({"text": "", "confidence": confidence})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
