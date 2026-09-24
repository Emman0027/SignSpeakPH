# PROJECT_INDEX.md — example (SignSpeakPH)

This is a worked example of what a *good* index looks like: short,
opinionated about what matters, not a dump of every file. Copy this
structure, not this content, into a new repo.

---

## What this is

SignSpeakPH — real-time Filipino Sign Language recognition delivered as
a website. PLMUN capstone/thesis project. Browser camera → Flask backend
→ MediaPipe keypoints → LSTM classifier → predicted gesture → text/voice
output.

## Tech stack

- Model: Python/TensorFlow 2.14.1, conda env `tensorflow_2` (must match
  exactly when deploying — version drift breaks the saved model)
- Backend: Flask, MediaPipe Holistic
- Frontend: browser `getUserMedia()`, JPEG frames POSTed to `/predict`
  roughly every 150ms
- Hosting: needs HTTPS (Render/Railway/PythonAnywhere free tier) —
  camera permissions don't work over plain HTTP off localhost

## Key files/folders (what each is for — not what's inside it)

- `Action_Detection_Refined.ipynb` — training notebook; produces
  `action.h5`, `labels.json`, `config.json`
- `app.py` — Flask app; `/predict` endpoint runs MediaPipe + model
  server-side per frame
- `utils/mediapipe_utils.py` — keypoint extraction helpers
- `templates/index.html`, `static/style.css` — the browser UI
- `requirements.txt` — Python deps for the Flask app (separate from the
  conda training env)

## Model architecture (stable — rarely needs re-reading)

LSTM(64) → LSTM(128) → LSTM(64) → Dense(64) → Dense(32) → Dense(5, softmax)
Input: 30 frames × 1662 features (pose+hands keypoints) — currently being
reduced to 258 features (dropped face landmarks) per the feature-engineering
pass, see ROADMAP.md.
Classes: kamusta, salamat, mahalkita, oo, hindi.

## Known limitations (don't re-discover these — they're already known)

- `sequence_buffer` in `app.py` is a single global buffer — fine for a
  solo demo, not multi-user safe.
- Large model/notebook files (`action.h5`, the `.ipynb`) are tracked by
  the scanner as fingerprint-only — their *content* is never re-read
  automatically, only re-described by hand when they meaningfully change.

## Decisions log

- 2026-xx-xx: Pivoted from server-side `cv2.VideoCapture` (localhost-only)
  to browser-camera architecture, because the deliverable must be a
  website, not a notebook.
- 2026-xx-xx: Chose to retrain with feature engineering (drop face
  landmarks, normalize keypoints) rather than record more training data
  first.

(See `references/protocol.md` for how/when to add to this section.)
