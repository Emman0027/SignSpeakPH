SignSpeakPH/
├── app.py                          # all routes live here (415 lines)
├── Dockerfile, render.yaml, runtime.txt, pyproject.toml
├── requirements.txt, requirements-dev.txt, requirements-training.txt
├── requirements/            base.txt, dev.txt
├── .flake8, .isort.cfg, .pre-commit-config.yaml, .gitignore, .gitmessage.txt
├── CLAUDE.md, README.md
├── src/
│   ├── __init__.py
│   ├── constants.py
│   ├── config/settings.py
│   ├── utils/        __init__.py, mediapipe_utils.py
│   └── api/, models/, services/    # each holds only an empty __init__.py
├── data/
│   ├── feedback/feedback.json
│   └── models/production/
│       ├── README.md, VERSION
│       ├── config.json, config_v1.0.0.json
│       └── labels.json, labels_v1.0.0.json    # no .tflite
├── templates/index.html
├── static/style.css
├── tests/    conftest.py, unit/test_endpoints.py, unit/test_mediapipe_utils.py
├── notebooks/
│   ├── Action Detection Refined_noholistic.ipynb
│   └── data/models/production/   config.json, labels.json   # duplicate copy
├── docs/STRUCTURE.md
├── scripts/      README.md, file_index.sh, scan_index.py, yuki-dori-ready.sh
├── .github/      workflows/ci.yml, dependabot.yml, pull_request_template.md, commit-message-template.md
├── .ai-context/  CHANGELOG, PRIORITIES, PROJECT_INDEX, ROADMAP, TASKS.md, STATE.json
├── .vibe-wise/   profile.md, progress.md, project-map.md
├── .claude/      mcp.json, .headroom_wrap_settings.lock
├── .yuki-dori-briefing.md, yuki_status.sh
├── graphify-out/ graph.html/json, GRAPH_REPORT.md, manifest.json, dated 2026-09-23 and 09-24 snapshots, cache/ (21 files)
├── graphify_output.json, .file_index (880 KB)
├── action.h5, action.keras, 0.npy  # gitignored but tracked
├── mv                              # empty file
└── utils/__pycache__/mediapipe_utils.cpython-310.pyc   # stale, no source