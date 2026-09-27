# Graph Report - SignSpeakPH  (2026-09-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 62 nodes · 77 edges · 16 communities (7 shown, 9 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0adb785a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- scan_index.py
- route
- app.py
- settings.py
- predict_batch
- mediapipe_utils.py
- file_index.sh
- yuki-dori-ready.sh
- create_models
- extract_keypoints
- yuki_status.sh

## God Nodes (most connected - your core abstractions)
1. `predict_batch()` - 6 edges
2. `main()` - 4 edges
3. `mediapipe_detection()` - 4 edges
4. `extract_keypoints()` - 4 edges
5. `file_index.sh script` - 4 edges
6. `fingerprint()` - 3 edges
7. `delete_feedback()` - 3 edges
8. `handle_feedback()` - 3 edges
9. `update_feedback()` - 3 edges
10. `decode_base64_image()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `predict_batch()` --calls--> `extract_keypoints()`  [EXTRACTED]
  app.py → src/utils/mediapipe_utils.py
- `predict_batch()` --calls--> `mediapipe_detection()`  [EXTRACTED]
  app.py → src/utils/mediapipe_utils.py

## Import Cycles
- None detected.

## Communities (16 total, 9 thin omitted)

### Community 0 - "scan_index.py"
Cohesion: 0.29
Nodes (9): argparse, hashlib, fingerprint(), load_state(), main(), scan_index.py — incremental repo state tracker. Purpose: let an AI agent know…, sha256_of(), walk_repo() (+1 more)

### Community 1 - "route"
Cohesion: 0.25
Nodes (8): delete_feedback(), handle_feedback(), index(), Handle customer satisfaction feedback, Update existing feedback, Delete existing feedback, update_feedback(), route

### Community 2 - "app.py"
Cohesion: 0.29
Nodes (6): SignSpeakPH - Flask backend (BATCH version) Fixes both the speed problem AND an…, base64, flask, tensorflow, tflite_runtime_interpreter, time

### Community 3 - "settings.py"
Cohesion: 0.29
Nodes (6): load_model_config(), Configuration management for SignSpeakPH, Load model labels and config, json, os, pathlib

### Community 4 - "predict_batch"
Cohesion: 0.33
Nodes (6): decode_base64_image(), predict_batch(), Convert a data:image/jpeg;base64,... string from the browser into an OpenCV…, Receives all SEQUENCE_LENGTH frames at once (captured locally by the browser at…, mediapipe_detection(), Run Pose + Hands on a single BGR frame. `models` is (pose_model, hands_model).

### Community 5 - "mediapipe_utils.py"
Cohesion: 0.40
Nodes (4): cv2, mediapipe, numpy, MediaPipe helper functions - FAST version (Pose + Hands, no Holistic). Holistic…

### Community 6 - "file_index.sh"
Cohesion: 0.70
Nodes (4): build_index(), search_index(), file_index.sh script, show_help()

## Knowledge Gaps
- **1 isolated node(s):** `yuki_status.sh script`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 29 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `predict_batch()` connect `predict_batch` to `route`, `app.py`, `extract_keypoints`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `delete_feedback()` connect `route` to `app.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `handle_feedback()` connect `route` to `app.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **What connects `yuki_status.sh script` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._