# Scripts Directory

This directory contains utility scripts for SignSpeakPH.

## Available scripts

- `manage_corrections.py` - Local maintainer review of submitted corrections.
- `manage_teaching.py` - Local maintainer review of new-sign teaching contributions.
- `train_correction_candidate.py` - Isolated mini-training, replay evaluation, and candidate staging.
- `scan_index.py` - Incremental repository state tracker.
- `file_index.sh` - Generate and search a file index.


## Teach a new sign

Visitors can use **Teach a New Sign** in the web app to submit a proposed Filipino sign. Each contribution requires a sign name, its meaning, and 3 to 5 separate webcam samples. Each sample is captured as 30 frames and converted by the server into 258-feature pose-and-hand landmarks. Raw camera images and video are not retained. Contributions are stored in `data/teaching/pending/` and are not added to the production vocabulary or live TFLite model.

Maintainers can review submissions locally:

```powershell
python scripts/manage_teaching.py list
python scripts/manage_teaching.py approve <TEACHING-UUID>
python scripts/manage_teaching.py reject <TEACHING-UUID>
```

Approval validates the sample count and every 30 x 258 sequence, then moves the contribution to `data/teaching/approved/`. This is approval for dataset preparation only; it does not retrain or change the live model. New-class training needs a separate output-layer expansion and evaluation workflow before any production promotion.

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
5. Compares the candidate against the production TFLite baseline on the same held-out validation sequences. It must stay within 1 percentage point of overall accuracy and must not add more than one validation error in any individual sign class.
6. Stages the candidate only when both validation gates pass. A candidate trained against an older production version is never reused as the next training base.

Candidate artifacts and per-class evaluation reports are written under `data/models/candidates/`. These are local generated files and are not committed to Git. The training lock records its process ID; an active training process is not unlocked merely because it has been running for a long time. The production Keras and TFLite files are never overwritten by this workflow. A validated candidate still requires maintainer review and a separate, deliberate promotion step.

The production checkpoint, dataset, and production TFLite file must exist locally. Do not delete or rename them before running this workflow.
