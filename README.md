# SignSpeakPH - Batch capture version

Fixes an accuracy problem caused by the streaming version's latency, not
just speed. See app.py's top comment for the full explanation:

Short version: streaming one frame per HTTP request meant a "30-frame"
sequence was stretched across 10-15+ seconds of real time (300-500ms
round trip x 30), while the model was trained on 30 frames captured in
under a second. That mismatch degrades accuracy independent of whether
MediaPipe/TFLite themselves are fast or correct.

This version captures all 30 frames in the BROWSER first, at native
webcam speed (~1 second, no network involved - matching how your
gesture data was originally recorded), then sends them together in one
request. The server processes all 30 and returns one prediction.

## 1. Copy your trained files here
- `action.tflite`
- `labels.json`
- `config.json`

## 2. Test locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 - you'll see a red "Recording sign..." badge
for about 1 second, then "processing...", then the result. This cycle
repeats automatically.

## 3. Deploy
Same as before - push to your repo, redeploy on Render (or wherever
you're hosting), using the same Dockerfile.

## What to expect
- Each full cycle = ~1s capture + however long server-side processing
  of 30 frames takes (check the terminal's [timing] line, or the
  on-screen "capture Xms + process Yms" readout).
- Recognition accuracy should now much more closely match what you saw
  in your notebook's live test loop (Cell 70), since frame timing is
  restored to near-native speed.
- If processing time is still high, that's now purely a MediaPipe/TFLite
  compute question (already using Pose+Hands, model_complexity=0,
  320x240 frames, GPU disabled) - not a latency-accumulation problem
  anymore.
