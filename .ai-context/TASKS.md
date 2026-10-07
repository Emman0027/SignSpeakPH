# TASKS.md

Track what needs to be done and what's been completed. Updated during the session, read at session start for quick orientation.

## Here's what's open

* [ ] Fix critical model-data mismatch: align constants.py with labels.json (only deploy 5 signs)
* [ ] Retrain model for all 22 signs (collect data for missing signs, update action.tflite)
* [ ] Improve UI the design layout to be presentable.

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
* [x] Clean up backup files and temporary fix scripts (fix_*.py, backups/, compare_extraction.py)
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
