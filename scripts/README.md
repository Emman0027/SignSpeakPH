# Scripts Directory

This directory contains utility scripts for SignSpeakPH.

## Available scripts

- `manage_corrections.py` - Local maintainer review of submitted corrections.
- `train_correction_candidate.py` - Isolated mini-training, replay evaluation, and candidate staging.
- `scan_index.py` - Incremental repository state tracker.
- `file_index.sh` - Generate and search a file index.

## Correction review and mini-training

Correction approval is intentionally a local command-line operation. Public visitors can submit corrections, but they cannot approve training data.

From the repository root, with the `tensorflow_2` environment active:

```powershell
python scripts/manage_corrections.py list
python scripts/manage_corrections.py approve <CORRECTION-UUID>
python scripts/manage_corrections.py reject <CORRECTION-UUID>
```

The default mini-training threshold is 5 eligible approved corrections. It can be set from 5 to 10:

```powershell
$env:SIGNSPEAKPH_TRAINING_THRESHOLD = "5"
```

Only approved corrections that include a valid 30 x 258 landmark sequence count toward the threshold. Corrections without sequence consent can be approved for record-keeping, but are not used for training.

When the threshold is reached, the approval command starts the trainer in a separate Python process. The trainer:

1. Loads the production Keras checkpoint, or the latest previously validated candidate.
2. Uses replay samples from the 22 production classes in `data/models/production/MP_Data`.
3. Fine-tunes with the newly approved correction sequences.
4. Converts the result to TFLite and evaluates it against the current production TFLite model on a fixed held-out split.
5. Stages a candidate only if its validation accuracy is no more than 1 percentage point below the production baseline.

Candidate artifacts and reports are written under `data/models/candidates/`. These are local generated files and are not committed to Git. The production Keras and TFLite files are never overwritten by this workflow. A validated candidate still requires maintainer review and a separate, deliberate promotion step.

The production checkpoint, dataset, and production TFLite file must exist locally. Do not delete or rename them before running this workflow.
