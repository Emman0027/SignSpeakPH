# Graph Report - SignSpeakPH  (2026-09-23)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 38 nodes · 45 edges · 11 communities (5 shown, 6 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `834a0052`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- src/utils/mediapipe_utils.py
- app.py
- settings.py
- predict_batch
- handle_feedback

## God Nodes (most connected - your core abstractions)
1. `predict_batch()` - 6 edges
2. `decode_base64_image()` - 3 edges
3. `extract_keypoints()` - 3 edges
4. `mediapipe_detection()` - 3 edges
5. `handle_feedback()` - 3 edges
6. `create_models()` - 2 edges
7. `load_model_config()` - 2 edges
8. `index()` - 2 edges
9. `SignSpeakPH - Flask backend (BATCH version) Fixes both the speed problem AND an…` - 1 edges
10. `Configuration management for SignSpeakPH` - 1 edges

## Surprising Connections (you probably didn't know these)
- `predict_batch()` --calls--> `extract_keypoints()`  [EXTRACTED]
  app.py → src/utils/mediapipe_utils.py
- `predict_batch()` --calls--> `mediapipe_detection()`  [EXTRACTED]
  app.py → src/utils/mediapipe_utils.py

## Import Cycles
- None detected.

## Communities (11 total, 6 thin omitted)

### Community 0 - "src/utils/mediapipe_utils.py"
Cohesion: 0.32
Nodes (4): cv2, mediapipe, numpy, create_models()

### Community 1 - "app.py"
Cohesion: 0.29
Nodes (6): SignSpeakPH - Flask backend (BATCH version) Fixes both the speed problem AND an…, base64, flask, tensorflow, tflite_runtime_interpreter, time

### Community 2 - "settings.py"
Cohesion: 0.29
Nodes (6): load_model_config(), Configuration management for SignSpeakPH, Load model labels and config, json, os, pathlib

### Community 3 - "predict_batch"
Cohesion: 0.33
Nodes (6): decode_base64_image(), predict_batch(), Convert a data:image/jpeg;base64,... string from the browser into an OpenCV…, Receives all SEQUENCE_LENGTH frames at once (captured locally by the browser at…, extract_keypoints(), mediapipe_detection()

### Community 4 - "handle_feedback"
Cohesion: 0.50
Nodes (4): handle_feedback(), index(), Handle customer satisfaction feedback, route

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `predict_batch()` connect `predict_batch` to `app.py`, `handle_feedback`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `handle_feedback()` connect `handle_feedback` to `app.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._