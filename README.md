# SignSpeakPH - Filipino Sign Language Recognition Website

Real-time Filipino Sign Language recognition with text and voice output.
The browser captures the VISITOR's own webcam via `getUserMedia()` and sends
frames to a Flask backend, which runs MediaPipe + a TFLite model and returns
predictions. No landmark lines are drawn - the video is the plain camera feed.

## Why TFLite instead of full TensorFlow
Full TensorFlow is several hundred MB and memory-hungry - this is what
caused "out of memory" 502 errors on Render's free tier (512MB RAM) and
what made every paid-tier-requiring host (Hugging Face Docker SDK, Google
Cloud Run) seem necessary. Converting the trained model to `.tflite` and
using the tiny `tflite-runtime` package (a few MB) instead removes that
problem at the source - no card, no upgrade, no bigger host needed.

## 1. Convert your model to TFLite (one-time, in your notebook)
Add this cell after `model.save('action.h5')`:
```python
import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('action.tflite', 'wb') as f:
    f.write(tflite_model)
```
This runs on your own machine, where full TensorFlow is already installed -
only the much smaller `action.tflite` output needs to go to the server.

## 2. Copy your files here
Copy these into this folder (next to `app.py`):
- `action.tflite`  <- NEW, replaces action.h5 for deployment
- `labels.json`
- `config.json`  <- must have `"num_features": 258`

(Keep `action.h5` for your notebook/local training work - it's just not
what gets deployed anymore.)

## 3. Test locally first
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## 4. Deploy to Render (free, no credit card)

1. Push this folder (including `action.tflite`, `labels.json`,
   `config.json`) to a GitHub repo.
2. Go to https://render.com, sign up (no card required), **New +** ->
   **Web Service**, connect your repo.
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
   - **Instance Type:** Free
4. Add an environment variable so Render uses a TensorFlow/MediaPipe
   compatible Python version:
   - **Key:** `PYTHON_VERSION`   **Value:** `3.11.9`
5. Deploy. Since the install is now just a few small packages instead of
   full TensorFlow, both the earlier Python-version build error and the
   memory crash should be resolved.

## Free tier behavior to know about
- Sleeps after 15 minutes idle; next visit takes ~30-60s to wake up. Open
  the URL a few minutes before your defense/demo.
- 750 free instance-hours/month - plenty for a demo project.

## Notes
- `opencv-python-headless` avoids missing system GUI libraries.
- `sequence_buffer` in `app.py` is a single global buffer - fine for a solo
  demo. For real multi-user support it would need to be keyed per session.
- `utils/mediapipe_utils.py` uses a 258-feature vector (pose + both hands,
  no face) - confirmed from the notebook's Cell 15 and the model's
  `input_shape=(30,258)` in Cell 49.
- If Render's build still shows any missing-system-library error (e.g.
  `libGL.so.1`), that's a separate, unrelated issue to memory/version - see
  the project history for the Docker + Cloud Run fallback path, which
  remains available if ever needed, just not required for this fix.
