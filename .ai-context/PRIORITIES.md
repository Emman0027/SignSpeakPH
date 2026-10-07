# Task Prioritization

## Open Tasks (Highest to Lowest Priority)

1. **Fix critical model-data mismatch**: align constants.py with labels.json (only deploy 5 signs)
2. **Establish git workflow**: create PR template (.github/PULL_REQUEST_TEMPLATE.md), commit message template (.gitmessage.txt), and squash improv branch commits
3. ~~**Add basic test suite** for Flask endpoints and MediaPipe utilities~~
4. **Enhance README.md** with architecture overview and development setup
5. ~~**Fix local file path** in requirements-training.txt line 89~~
6. **Add model version tracking system** (store models as action_vX.Y.Z.tflite)
7. ~~**Setup pre-commit hooks** for automated code quality~~
8. ~~**Setup GitHub Actions CI** pipeline for testing and linting~~
9. **Reorganize code structure** into proper src/ package layout
10. **Improve Dockerfile** for production (multiple workers, healthcheck, non-root user)
11. **Add monitoring and error tracking** (logging, Sentry, metrics endpoints)
12. **Implement security hardening** (rate limiting, CORS, security headers)
13. **Optimize performance** (profile extraction, consider quantization, request caching)
14. **Retrain model for all 22 signs** (collect data for missing signs, update action.tflite)

## What Could Be Done Now (Excluding High-Effort Data Collection Tasks)

The following tasks can be worked on immediately without requiring additional data collection or model retraining:

- Establish git workflow: create PR template, commit message template, squash improv branch commits
- ~~Add basic test suite for Flask endpoints and MediaPipe utilities~~
- Enhance README.md with architecture overview and development setup
- Fix local file path in requirements-training.txt line 89
- Add model version tracking system (store models as action_vX.Y.Z.tflite)
- Setup pre-commit hooks for automated code quality
- Setup GitHub Actions CI pipeline for testing and linting
- Reorganize code structure into proper src/ package layout
- Improve Dockerfile for production (multiple workers, healthcheck, non-root user)
- Add monitoring and error tracking (logging, Sentry, metrics endpoints)
- Implement security hardening (rate limiting, CORS, security headers)
- Optimize performance (profile extraction, consider quantization, request caching)

*Note: The two tasks requiring data collection are:*
- *Fix critical model-data mismatch: align constants.py with labels.json (only deploy 5 signs)*
- *Retrain model for all 22 signs (collect data for missing signs, update action.tflite)*