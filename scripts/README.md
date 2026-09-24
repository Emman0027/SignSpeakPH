# Scripts Directory

This directory contains utility scripts for the SignSpeakPH project.

## Available Scripts

- `train.py` - Model training script
- `evaluate.py` - Model evaluation script  
- `deploy.py` - Deployment script
- `scan_index.py` - Incremental repo state tracker (tracks file changes)
- `file_index.sh` - Generate and search a file index for fast file lookup

## Usage

Add your implementation to these scripts as needed for your workflow.

### file_index.sh
Create a searchable index of all files to avoid repeated filesystem scanning:
- `./file_index.sh --build`    # Build/update the file index
- `./file_index.sh --search "pattern"`  # Search the index for files matching pattern
- `./file_index.sh --help`     # Show help

The index is saved as `.file_index` in the repository root.