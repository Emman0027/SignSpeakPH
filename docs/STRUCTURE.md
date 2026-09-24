# SignSpeakPH Project Structure

## Overview
This document describes the organized project structure for SignSpeakPH, a Filipino Sign Language recognition system.

## Directory Structure
```
SignSpeakPH/
├── app.py                    # Application entry point
├── config/                   # Configuration management
│   └── settings.py           # Centralized configuration
├── src/                      # Source code
│   ├── __init__.py
│   ├── api/                  # Flask routes and API
│   │   ├── __init__.py
│   │   └── routes.py         # Route definitions
│   ├── models/               # ML model handling
│   │   ├── __init__.py
│   │   ├── model_loader.py   # Model loading and prediction
│   │   └── trainer.py        # Model training functions
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── mediapipe_utils.py # MediaPipe processing
│   └── services/             # Business logic
│       ├── __init__.py
│       ├── prediction_service.py
│       └── feedback_service.py
├── templates/                # HTML templates
│   └── index.html            # Main template
├── static/                   # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   └── images/
├── data/                     # Data storage
│   ├── feedback/             # User feedback storage
│   ├── logs/                 # Application logs
│   └── models/               # ML models
│       ├── production/       # Production-ready models
│       ├── staging/          # Staging models
│       └── experiments/      # Experimental models
├── docs/                     # Documentation
│   └── STRUCTURE.md          # This file
├── scripts/                  # Utility scripts
│   ├── train.py              # Model training script
│   ├── evaluate.py           # Model evaluation script
│   └── deploy.py             # Deployment script
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── conftest.py           # Test configuration
├── notebooks/                # Jupyter Lab notebooks for experimentation
├── experiments/              # Experiment tracking and results
├── requirements/             # Dependency files
│   ├── base.txt              # Production dependencies
│   └── dev.txt               # Development dependencies
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose (if needed)
└── README.md                 # Project overview and instructions
```

## Key Improvements

### 1. **Separation of Concerns**
- **Configuration**: Centralized in `config/` directory
- **Source Code**: Organized by concern in `src/` directory
- **Data**: Separated by type in `data/` directory
- **Tests**: Isolated in `tests/` directory
- **Documentation**: Maintained in `docs/` directory

### 2. **Improved Configuration Management**
- Environment-based configuration
- Centralized settings in `config/settings.py`
- Easy deployment across different environments

### 3. **Enhanced ML Workflow**
- Organized model storage (`data/models/`)
- Separation of production, staging, and experimental models
- Dedicated directories for notebooks and experiment tracking

### 4. **Better Development Workflow**
- Clear separation between code, config, and data
- Structured approach to testing and documentation
- Standardized locations for scripts and utilities

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements/base.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the application**:
   Open http://localhost:5000 in your browser

## Model Management

- **Production models**: `data/models/production/`
- **Staging models**: `data/models/staging/`
- **Experimental models**: `data/models/experiments/`

## Feedback Storage

User feedback is stored in:
- `data/feedback/feedback.json`

## Notes

This structure follows software engineering best practices for:
- Maintainability
- Scalability
- Collaboration
- Deployment readiness

The application entry point remains `app.py` in the project root for simplicity.