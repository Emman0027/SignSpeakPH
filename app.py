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
import sys
import time

# MediaPipe tries GPU/EGL acceleration by default and silently falls back
# to CPU when it fails - but it retries this failed attempt on EVERY frame,
# wasting time each call. Render's servers have no GPU, so disable this
# attempt entirely before mediapipe is imported (must be set before import).
os.environ["MEDIAPIPE_DISABLE_GPU"] = os.environ.get("MEDIAPIPE_DISABLE_GPU", "1")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

# Monitoring and error tracking imports
import sentry_sdk
from flask import Flask, jsonify, render_template, request  # noqa: E402

# Security hardening imports
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sentry_sdk.integrations.flask import FlaskIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "httpserver_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "httpserver_request_duration_seconds",
    "HTTP Request Latency",
    ["method", "endpoint"],
)
PREDICTION_CONFIDENCE = Histogram(
    "prediction_confidence_scores", "Confidence scores of predictions", ["sign"]
)
FEEDBACK_SUBMISSIONS = Counter(
    "feedback_submissions_total", "Total feedback submissions", ["rating"]
)

try:
    import tflite_runtime.interpreter as tflite
except ModuleNotFoundError:
    import tensorflow as tf

    tflite = tf.lite

from src.config.settings import (
    CONFIG_PATH,
    LABELS_PATH,
    MODEL_PATH,
    PROHIBITED_SIGNS,
    SEQUENCE_LENGTH,
    THRESHOLD,
)
from src.utils.mediapipe_utils import create_models  # noqa: E402
from src.utils.mediapipe_utils import extract_keypoints, mediapipe_detection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

interpreter = tflite.Interpreter(model_path=str(MODEL_PATH), num_threads=2)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

with open(LABELS_PATH, "r") as f:
    ACTIONS = json.load(f)

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

app = Flask(__name__)

# Initialize CORS
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://",
)

# Pose + Hands models reused across requests.
models = create_models()

# Initialize Sentry for error tracking
sentry_dsn = os.environ.get("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        environment=os.environ.get("FLASK_ENV", "production"),
    )
    logger.info("Sentry initialized for error tracking")
else:
    logger.warning("SENTRY_DSN not set, Sentry error tracking disabled")


# Middleware to collect metrics
@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    if hasattr(request, "start_time"):
        request_latency = time.time() - request.start_time
        REQUEST_LATENCY.labels(
            method=request.method, endpoint=request.endpoint or request.path
        ).observe(request_latency)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or request.path,
            http_status=response.status_code,
        ).inc()
    return response


def decode_base64_image(data_url):
    """Convert a data:image/jpeg;base64,... string from the
    browser into an OpenCV frame."""
    header, encoded = data_url.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame


# Security headers
@app.after_request
def add_security_headers(response):
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


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
        return (
            jsonify(
                {"error": f"expected {SEQUENCE_LENGTH} frames, " f"got {len(images)}"}
            ),
            400,
        )

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
    interpreter.set_tensor(input_details[0]["index"], input_data)
    interpreter.invoke()
    res = interpreter.get_tensor(output_details[0]["index"])[0]
    t2 = time.time()

    idx = int(np.argmax(res))
    confidence = float(res[idx])

    # Check if the predicted sign is prohibited
    predicted_sign = ACTIONS[idx]
    if predicted_sign in PROHIBITED_SIGNS:
        return jsonify(
            {
                "text": "",
                "confidence": confidence,
                "prohibited": True,
                "message": "This sign is not allowed",
            }
        )

    print(
        f"[timing] mediapipe_total={(t1-t0)*1000:.0f}ms "
        f"({(t1-t0)*1000/SEQUENCE_LENGTH:.0f}ms/frame) "
        f"tflite={(t2-t1)*1000:.0f}ms"
    )

    if confidence > THRESHOLD:
        return jsonify({"text": ACTIONS[idx], "confidence": confidence})
    return jsonify({"text": "", "confidence": confidence})


@app.route("/feedback", methods=["POST"])
def handle_feedback():
    """Handle customer satisfaction feedback"""
    try:
        feedback_data = request.get_json()
        if not feedback_data:
            return jsonify({"error": "no feedback data provided"}), 400

        # Validate rating is between 1-5
        rating = feedback_data.get("rating")
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return (
                        jsonify({"error": "rating must be between 1 and 5"}),
                        400,
                    )
                feedback_data["rating"] = rating
            except (ValueError, TypeError):
                return (
                    jsonify({"error": "rating must be a number between 1 and 5"}),
                    400,
                )

        # Add timestamp
        feedback_data["timestamp"] = time.time()
        feedback_data["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Store feedback (simple JSON file approach)
        feedback_file = os.path.join(BASE_DIR, "data", "feedback", "feedback.json")

        os.makedirs(os.path.dirname(feedback_file), exist_ok=True)

        # Read existing feedback or create empty list
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                feedbacks = json.load(f)
        else:
            feedbacks = []

        # Add new feedback
        feedbacks.append(feedback_data)

        # Write back to file
        with open(feedback_file, "w") as f:
            json.dump(feedbacks, f, indent=2)

        return (
            jsonify({"status": "success", "message": "Feedback received"}),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/feedback/<int:feedback_id>", methods=["PUT"])
def update_feedback(feedback_id):
    """Update existing feedback"""
    try:
        feedback_data = request.get_json()
        if not feedback_data:
            return jsonify({"error": "no feedback data provided"}), 400

        # Validate rating is between 1-5 if provided
        if "rating" in feedback_data:
            try:
                rating = int(feedback_data["rating"])
                if rating < 1 or rating > 5:
                    return (
                        jsonify({"error": "rating must be between 1 and 5"}),
                        400,
                    )
                feedback_data["rating"] = rating
            except (ValueError, TypeError):
                return (
                    jsonify({"error": "rating must be a number between 1 and 5"}),
                    400,
                )

        # Update timestamp
        feedback_data["timestamp"] = time.time()
        feedback_data["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # Store feedback (simple JSON file approach)
        feedback_file = os.path.join(BASE_DIR, "data", "feedback", "feedback.json")

        # Read existing feedback
        if not os.path.exists(feedback_file):
            return jsonify({"error": "feedback not found"}), 404

        with open(feedback_file, "r") as f:
            feedbacks = json.load(f)

        # Check if feedback_id exists
        if feedback_id < 0 or feedback_id >= len(feedbacks):
            return jsonify({"error": "feedback not found"}), 404

        # Update the feedback
        feedbacks[feedback_id] = feedback_data

        # Write back to file
        with open(feedback_file, "w") as f:
            json.dump(feedbacks, f, indent=2)

        return (
            jsonify({"status": "success", "message": "Feedback updated"}),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/feedback/<int:feedback_id>", methods=["DELETE"])
def delete_feedback(feedback_id):
    """Delete existing feedback"""
    try:
        # Store feedback (simple JSON file approach)
        feedback_file = os.path.join(BASE_DIR, "data", "feedback", "feedback.json")

        # Read existing feedback
        if not os.path.exists(feedback_file):
            return jsonify({"error": "feedback not found"}), 404

        with open(feedback_file, "r") as f:
            feedbacks = json.load(f)

        # Check if feedback_id exists
        if feedback_id < 0 or feedback_id >= len(feedbacks):
            return jsonify({"error": "feedback not found"}), 404

        # Remove the feedback
        deleted_feedback = feedbacks.pop(feedback_id)

        # Write back to file
        with open(feedback_file, "w") as f:
            json.dump(feedbacks, f, indent=2)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Feedback deleted",
                    "deleted": deleted_feedback,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
