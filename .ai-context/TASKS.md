# TASKS.md

Track what needs to be done and what's been completed. Updated during the session, read at session start for quick orientation.

## Here's what's open

* [ ] Fix critical model-data mismatch: align constants.py with labels.json (only deploy 5 signs)
* [ ] Retrain model for all 22 signs (collect data for missing signs, update action.tflite)
* [ ] Improve UI the design layout to be presentable.
* [ ] [Gate 1] Add a model evaluation (script or notebook cell): held-out accuracy, per-sign precision/recall, confusion matrix, list of misclassified clips, saved to docs/testing/model_evaluation.md; target >=90% (manuscript p.63)
* [ ] [Gate 1] Document dataset coverage (signers, sessions, lighting, backgrounds; today 60 sequences x 5 signs) and record more sessions with different signers and lighting before claiming accuracy
* [ ] [Gate 1] Measure end-to-end latency and fps on the deployed host (capture, upload, MediaPipe, TFLite, response) and log it; manuscript requires >=15 fps
* [ ] [Gate 1] Create docs/testing/ALPHA_TEST_LOG.md covering the 8 Table 2 areas with pass/fail, date, evidence, and defects found/fixed
* [ ] [Gate 1] Add a hand/pose landmark overlay to the live camera view (required by manuscript Tables 2-3 and output requirements); decide first whether to return landmarks from /predict_batch or run MediaPipe in the browser
* [ ] [Gate 1] Decide real-time behavior: manuscript says continuous update as the gesture changes but the app records 30 frames then predicts; implement a sliding window or document the capture-then-recognize design
* [ ] [Gate 1] Voice output fallback: check speechSynthesis.getVoices() for a Filipino/Tagalog voice, show a clear message if none exists, and document supported browsers/devices
* [ ] [Gate 2] Create docs/testing/BETA_TEST_PLAN.md (the 5 Table 3 areas, a tester task script, a consent note) plus evaluation forms matching Table 4 (7 characteristics) and Table 5 (4 characteristics) on the Table 6 Likert scale
* [ ] [Gate 2] Add scripts/analyze_survey.py: read exported responses (CSV), compute mean per characteristic and overall, interpret with Table 6 ranges (4.51-5.00 Excellent ... 1.00-1.50 Poor)
* [ ] [Gate 2] Beta readiness: stable public URL, uptime check, rate limits that allow a full tester session, feedback stored so tester data is not lost on redeploy
* [ ] [Gate 3] Write docs/testing/IT_EXPERT_READINESS.md: for each of the 7 Table 4 characteristics, what an evaluator will check and the evidence in the repo; no known high-severity issue before beta
* [ ] [P2] Add .venv/ to .gitignore and keep signspeakph-patch-7-plan-leftovers.patch out of Git
* [ ] [P2] Pin exact versions in requirements.txt using pip freeze from the first working Render or Docker deploy (keep mediapipe==0.10.21)
* [ ] [P2] Show the sign's display name instead of the raw label in the recognized text and voice output (the app returns and speaks "mahalkita")
* [ ] [P2] Write how-to-perform descriptions for each sign in SIGN_INFO and check them against an FSL reference (descriptions are currently meanings only)
## Here's what you just finished
* [x] Set up Project-Dori project memory system (.ai-context/ with INDEX, CHANGELOG, ROADMAP)
* [x] Extended Project-Dori with TASKS.md convention for session-start task reminders
* [x] Initialized TASKS.md in repository with open/completed task tracking
* [x] Moved Jupyter notebooks to notebooks/ directory
* [x] Cleaned up backup files and temporary fix scripts (fix_*.py, backups/, compare_extraction.py)
* [x] Added model files to .gitignore: *.h5, *.keras, *.tflite, *.npy, action.*
* [x] Created memory consolidation system (project-overview, recent-work, protected notebook)
* [x] Updated .gitignore with comprehensive binary file patterns
* [x] Remove duplicate import in app.py line 87: "from constants import SIGN_INFO"
* [x] Cleaned up backup files and temporary fix scripts (fix_*.py, backups/, compare_extraction.py)
* [x] Create markdown file index of all SignSpeakPH files and store in vault as SignSpeakPH-file-index.md
* [x] Establish git workflow: create PR template, commit message template, squash improv branch commits
* [x] Add basic test suite for Flask endpoints and MediaPipe utilities
* [x] Enhance README.md with architecture overview and development setup
* [x] Create requirements-dev.txt separating dev/prod dependencies
* [x] Fix local file path in requirements-training.txt line 89
* [x] Add code quality tools (black, flake8, mypy) via pyproject.toml
* [x] Setup pre-commit hooks for automated code quality
* [x] Setup GitHub Actions CI pipeline for testing and linting
* [x] Improve Dockerfile for production (multiple workers, healthcheck, non-root user)
* [x] Add monitoring and error tracking (logging, Sentry, metrics endpoints)
* [x] Implement security hardening (rate limiting, CORS, security headers)
* [x] Reorganize code structure into proper src/ package layout
* [x] Optimize performance (profile extraction, consider quantization, request caching)
* [x] Add model version tracking system (store models as action_vX.Y.Z.tflite)
* [x] Fixed the duplicate /signs route in app.py: one route remains and reads src/constants.SIGN_INFO (label, display, description; descriptions are English meanings only)
* [x] Added tests/unit/test_signs.py (checks /signs and that SIGN_INFO matches the model labels)
* [x] render.yaml buildCommand swaps OpenCV for the headless build so Render does not need libGL.so.1 (not yet tested on Render)
* [x] requirements/base.txt now includes ../requirements.txt
* [x] Removed the empty mv file and the two signspeakph-patches-*.patch files from the repo root