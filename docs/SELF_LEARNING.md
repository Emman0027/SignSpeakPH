# SignSpeakPH Self-Learning MVP

This branch adds the first collection layer for user-confirmed training examples.

## Current behavior

- **Correct a prediction:** submit the original 30-frame sequence, the predicted label, and the user's corrected label.
- **Teach a new sign:** submit a new label and one recorded 30-frame sequence. Repeat the recording action to collect additional examples.
- The server runs the same Pose + Hands MediaPipe extraction path as `/predict_batch`.
- Only the resulting `(30, 258)` float32 landmark sequence is retained. The submitted JPEG frames are not written to disk.
- Samples are written to `data/learning/` in a SQLite metadata database and individual NumPy `.npy` files.
- Every sample starts with `pending_review`. Collection does not change the active labels or production `.tflite` model.
- `share_consent` records whether the contributor agrees that the sample may be considered for future shared training. No central upload is implemented in this milestone.

## API

### `POST /learning/correct`

JSON body:

```json
{
  "images": ["data:image/jpeg;base64,..."],
  "predicted_label": "salamat",
  "correct_label": "kamusta",
  "confidence": 0.81,
  "share_consent": false
}
```

Both labels must already exist in the deployed model vocabulary, and they must differ.

### `POST /learning/teach`

JSON body:

```json
{
  "images": ["data:image/jpeg;base64,..."],
  "label": "bagong_salita",
  "description": "Optional meaning",
  "share_consent": false
}
```

The label must not already exist in the deployed vocabulary. A new label is only a pending dataset proposal; it is not recognized by the current model.

Both endpoints require exactly the configured number of frames (currently 30). Each sample is extracted using the configured feature count (currently 258).

### `GET /learning/summary`

Returns counts by sample status and kind. It does not return sample data.

## Local setup and verification

1. Pull the `self-learning-mvp` branch.
2. Install the project's normal requirements.
3. Run `python app.py` and open the local SignSpeakPH page.
4. Start signing and wait for a prediction.
5. Use **Correct this prediction** to submit a correction. Check that the UI confirms it was saved.
6. Use **Teach a Sign** to record a new label. Record multiple separate samples for that label.
7. Open `http://127.0.0.1:5000/learning/summary` and confirm the sample counts increase.
8. Run `pytest` to execute the automated tests.

The data folder is intentionally ignored by Git. Back it up separately if the collected examples matter.

## Important limitations

- This is a collection MVP, not yet a self-updating model. Samples do not retrain the model automatically.
- Centralized synchronization, contributor authentication, moderation tools, dataset export, training, evaluation, model version promotion, and rollback are later milestones.
- When running locally, the data is stored on the machine hosting Flask. A hosted service may use ephemeral storage; do not treat its local filesystem as durable central storage.
- A new sign needs multiple varied examples and review before it can be included in training. The current model's output layer and label mapping must be retrained together.
- Training and inference must use compatible MediaPipe landmark extraction. The repository documents a possible distribution difference between its historical Holistic training data and current Pose + Hands inference pipeline.
