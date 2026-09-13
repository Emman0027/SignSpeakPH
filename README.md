# SignSpeakPH Website (browser-camera, Render-ready)

## What this version does
The browser captures the VISITOR's own webcam via `getUserMedia()` and sends
individual frames to Flask's `/predict` endpoint. MediaPipe + your model run
server-side and return a prediction as JSON. No landmark lines are drawn -
the video is the plain camera feed. This works for any visitor online, not
just the machine running the server - which is why it's Render-ready.

## 1. Copy your trained files here
From your notebook, copy these into this folder (next to `app.py`):
- `action.h5`
- `labels.json`
- `config.json`  <- must have `"num_features": 258` (NOT 1662 - see note below)

If your `config.json` still says 1662, fix it in the notebook:
```python
config = {"sequence_length": sequence_length, "num_features": 258, "threshold": 0.7}
with open('config.json', 'w') as f:
    json.dump(config, f)
```

## 2. Test locally first
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 - confirm predictions work before deploying.

## 3. Deploy to Render (free)

1. Push this whole folder (including `action.h5`, `labels.json`, `config.json`)
   to a GitHub repository. `action.h5` is a few MB, fine for a normal repo.
2. Go to https://render.com and sign up (no credit card required).
3. Click **New +** -> **Web Service**, connect your GitHub repo.
4. Render should auto-detect `render.yaml` and fill in the settings. If not,
   set manually:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
   - **Instance Type:** Free
5. Click **Create Web Service**. First build can take a few minutes
   (TensorFlow is a large install).
6. Once live, Render gives you a URL like `https://signspeakph.onrender.com`
   - HTTPS is automatic, so camera permissions will work correctly.

## Free tier behavior to know about
- The free instance **spins down after 15 minutes of inactivity**. The next
  visit triggers a "cold start" that can take 30-60 seconds to wake back up.
  For a defense/demo, open the URL a few minutes beforehand so it's already
  awake.
- Render's free tier includes 750 instance-hours/month - plenty for a demo
  or portfolio project, not meant for high-traffic production use.

## Notes
- `opencv-python-headless` is used instead of `opencv-python` - the headless
  build avoids missing system GUI libraries on Render's minimal Linux image.
- `sequence_buffer` in `app.py` is a single global buffer - fine for one
  visitor at a time (a demo). For real multi-user support it would need to
  be keyed per session instead.
- `utils/mediapipe_utils.py` must always match whatever `extract_keypoints()`
  your notebook actually uses. This version is 258 features (pose + both
  hands, no face) - confirmed directly from your notebook's Cell 15 and the
  model's `input_shape=(30,258)` in Cell 49.
