# CHANGELOG.md

Append-only. Newest entry at the top. Never edit old entries — if an old
entry turns out to be wrong, add a new entry correcting it, don't rewrite
history.

One line per meaningful change: what changed and why (not a diff — the
diff is in git; this is the "why would future-me care" summary).

---
## 2026-10-10
- settings path fix; tracked action_v1.0.0.tflite and scripts/export_tflite.py; requirements fixed with mediapipe pinned; Dockerfile and /health; /config; feedback id returned and stored by the UI; /signs with SIGN_INFO; render.yaml OpenCV headless swap; requirements/base.txt include; removed mv and root patch files; new tests test_config_and_feedback_id.py and test_signs.py.
## 2026-09-28
- Added monitoring and error tracking: logging, Sentry integration, and Prometheus metrics endpoint (/metrics)
- Implemented security hardening: rate limiting (100/hr), CORS, and security headers (HSTS, X-Content-Type-Options, etc.)
- Reorganized code structure: moved config/ and constants.py to src/ package, updated all imports accordingly
- Optimized performance: increased TensorFlow Lite inference speed with num_threads=2 for multi-threaded execution

## YYYY-MM-DD
- (example) Fixed evaluation bug: was scoring on train set instead of test set
- (example) Changed test_size 0.05 -> 0.2, added stratify
