# Graph Report - SignSpeakPH  (2026-09-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 28 nodes · 38 edges · 5 communities (3 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8dfb4b88`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- predict_batch
- mediapipe_utils.py
- create_models
- mediapipe_detection

## God Nodes (most connected - your core abstractions)
1. `predict_batch()` - 6 edges
2. `extract_keypoints()` - 4 edges
3. `mediapipe_detection()` - 4 edges
4. `decode_base64_image()` - 3 edges
5. `create_models()` - 3 edges
6. `index()` - 2 edges
7. `SignSpeakPH - Flask backend (BATCH version) Fixes both the speed problem AND an…` - 1 edges
8. `Convert a data:image/jpeg;base64,... string from the browser into an OpenCV…` - 1 edges
9. `Receives all SEQUENCE_LENGTH frames at once (captured locally by the browser at…` - 1 edges
10. `258-length feature vector: pose(33*4=132) + lh(21*3=63) + rh(21*3=63).…` - 1 edges

## Surprising Connections (you probably didn't know these)
- `predict_batch()` --calls--> `mediapipe_detection()`  [EXTRACTED]
  app.py → utils/mediapipe_utils.py
- `predict_batch()` --calls--> `extract_keypoints()`  [EXTRACTED]
  app.py → utils/mediapipe_utils.py

## Import Cycles
- None detected.

## Communities (5 total, 2 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.25
Nodes (7): SignSpeakPH - Flask backend (BATCH version) Fixes both the speed problem AND an…, base64, flask, json, os, tflite_runtime_interpreter, time

### Community 1 - "predict_batch"
Cohesion: 0.25
Nodes (8): decode_base64_image(), index(), predict_batch(), Convert a data:image/jpeg;base64,... string from the browser into an OpenCV…, Receives all SEQUENCE_LENGTH frames at once (captured locally by the browser at…, route, extract_keypoints(), 258-length feature vector: pose(33*4=132) + lh(21*3=63) + rh(21*3=63).…

### Community 2 - "mediapipe_utils.py"
Cohesion: 0.32
Nodes (4): cv2, mediapipe, numpy, MediaPipe helper functions - FAST version (Pose + Hands, no Holistic). Holistic…

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `predict_batch()` connect `predict_batch` to `app.py`, `mediapipe_detection`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `mediapipe_detection()` connect `mediapipe_detection` to `app.py`, `predict_batch`, `mediapipe_utils.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `extract_keypoints()` connect `predict_batch` to `app.py`, `mediapipe_utils.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._