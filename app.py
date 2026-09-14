"""
SignSpeakPH - Flask backend (browser-camera version, Render-ready)

The browser captures the VISITOR's own webcam via getUserMedia() and POSTs
frames here to /predict. No server-side camera is used, so this works when
deployed online, not just on localhost.

Local run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000

Render deployment: see README.md
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

# Pose + Hands models reused across requests (much faster than Holistic,
# which also runs an unused 468-point face mesh on every single frame).
# NOTE: sequence_buffer is a single global buffer - fine for a solo demo.
# For multiple simultaneous visitors, key this by session/user ID instead.
models = create_models()
sequence_buffer = []


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


@app.route("/predict", methods=["POST"])
def predict():
    global sequence_buffer

    payload = request.get_json()
    if not payload or "image" not in payload:
        return jsonify({"error": "no image provided"}), 400

    frame = decode_base64_image(payload["image"])
    if frame is None:
        return jsonify({"error": "could not decode image"}), 400

    t0 = time.time()
    _, results = mediapipe_detection(frame, models)
    t1 = time.time()
    keypoints = extract_keypoints(results)

    sequence_buffer.append(keypoints)
    sequence_buffer = sequence_buffer[-SEQUENCE_LENGTH:]

    if len(sequence_buffer) < SEQUENCE_LENGTH:
        print(f"[timing] mediapipe={  (t1-t0)*1000:.0f}ms (buffering {len(sequence_buffer)}/30)")
        return jsonify({"text": "", "confidence": 0.0, "buffering": True,
                         "frames_collected": len(sequence_buffer)})

    t2 = time.time()
    input_data = np.expand_dims(sequence_buffer, axis=0).astype(np.float32)  # (1, 30, 258)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    res = interpreter.get_tensor(output_details[0]['index'])[0]
    t3 = time.time()
    idx = int(np.argmax(res))
    confidence = float(res[idx])

    print(f"[timing] mediapipe={(t1-t0)*1000:.0f}ms tflite={(t3-t2)*1000:.0f}ms")

    if confidence > THRESHOLD:
        return jsonify({"text": ACTIONS[idx], "confidence": confidence, "buffering": False})

    return jsonify({"text": "", "confidence": confidence, "buffering": False})


@app.route("/reset", methods=["POST"])
def reset():
    global sequence_buffer
    sequence_buffer = []
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
