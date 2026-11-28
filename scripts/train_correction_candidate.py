"""Train and evaluate an isolated SignSpeakPH correction candidate.

This script never modifies the production Keras or TFLite model.
"""

import errno
import json
import os
import time
import uuid
from pathlib import Path

import numpy as np
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "data" / "models" / "production"
DATASET_DIR = MODEL_DIR / "MP_Data"
CORRECTIONS_DIR = ROOT / "data" / "corrections" / "approved"
CANDIDATES_DIR = ROOT / "data" / "models" / "candidates"
LABELS_PATH = MODEL_DIR / "labels_v1.1.0.json"
PRODUCTION_KERAS = MODEL_DIR / "action.keras"
VERSION_PATH = MODEL_DIR / "VERSION"
LOCK_PATH = ROOT / "data" / "corrections" / "training.lock"
MIN_CORRECTIONS = int(os.environ.get("SIGNSPEAKPH_TRAINING_THRESHOLD", "5"))
REPLAY_PER_CLASS = 12
CORRECTION_REPEATS = 4
EPOCHS = 5
BATCH_SIZE = 8
LEARNING_RATE = 0.0001
MAX_VALIDATION_ACCURACY_DROP = 0.01


def read_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    temporary.replace(path)


def load_sequence(sequence_dir):
    frame_files = list(sequence_dir.glob("*.npy"))
    try:
        frame_files.sort(key=lambda path: int(path.stem))
    except ValueError:
        frame_files.sort()

    if len(frame_files) != 30:
        raise ValueError(
            f"{sequence_dir}: expected 30 .npy frames, found {len(frame_files)}"
        )

    frames = [
        np.asarray(np.load(path, allow_pickle=False), dtype=np.float32)
        for path in frame_files
    ]
    sequence = np.stack(frames)
    if sequence.shape != (30, 258):
        raise ValueError(f"{sequence_dir}: expected (30, 258), got {sequence.shape}")
    if not np.isfinite(sequence).all():
        raise ValueError(f"{sequence_dir}: contains NaN or infinite values")
    return sequence


def load_replay_dataset(labels):
    rng = np.random.default_rng(20261125)
    replay_x, replay_y, validation_x, validation_y = [], [], [], []
    counts = {}

    for label_index, label in enumerate(labels):
        class_dir = DATASET_DIR / label
        if not class_dir.is_dir():
            raise FileNotFoundError(f"Missing production class folder: {class_dir}")

        def folder_sort_key(path):
            # Keep numeric sequence folders ordered naturally without comparing
            # integers and strings in the same sort operation.
            return (
                (0, int(path.name))
                if path.name.isdigit()
                else (1, path.name.casefold())
            )

        sequence_dirs = sorted(
            [path for path in class_dir.iterdir() if path.is_dir()],
            key=folder_sort_key,
        )
        sequences = [load_sequence(path) for path in sequence_dirs]
        if len(sequences) < 10:
            raise ValueError(
                f"{label}: at least 10 valid sequences are required; found {len(sequences)}"
            )

        indices = rng.permutation(len(sequences))
        validation_count = max(1, round(len(sequences) * 0.20))
        validation_indices = indices[:validation_count]
        training_indices = indices[validation_count:]
        replay_indices = rng.choice(
            training_indices,
            size=min(REPLAY_PER_CLASS, len(training_indices)),
            replace=False,
        )

        validation_x.extend(sequences[index] for index in validation_indices)
        validation_y.extend([label_index] * len(validation_indices))
        replay_x.extend(sequences[index] for index in replay_indices)
        replay_y.extend([label_index] * len(replay_indices))
        counts[label] = len(sequences)

    return (
        np.asarray(replay_x, dtype=np.float32),
        np.asarray(replay_y, dtype=np.int64),
        np.asarray(validation_x, dtype=np.float32),
        np.asarray(validation_y, dtype=np.int64),
        counts,
    )


def load_new_corrections(labels):
    label_to_index = {label: index for index, label in enumerate(labels)}
    examples, targets, correction_ids = [], [], []

    if not CORRECTIONS_DIR.exists():
        return (
            np.empty((0, 30, 258), dtype=np.float32),
            np.empty((0,), dtype=np.int64),
            [],
        )

    for path in sorted(CORRECTIONS_DIR.glob("*.json")):
        item = read_json(path)
        if (
            item.get("status") != "approved"
            or item.get("training_status") == "trained_candidate"
        ):
            continue
        if not item.get("sequence_included") or "sequence" not in item:
            continue

        corrected_label = item.get("corrected_label")
        if corrected_label not in label_to_index:
            raise ValueError(
                f"{path.name}: corrected label is not in production labels"
            )
        sequence = np.asarray(item["sequence"], dtype=np.float32)
        if sequence.shape != (30, 258) or not np.isfinite(sequence).all():
            raise ValueError(f"{path.name}: approved sequence is invalid")

        examples.append(sequence)
        targets.append(label_to_index[corrected_label])
        correction_ids.append(item.get("id", path.stem))

    return (
        np.asarray(examples, dtype=np.float32),
        np.asarray(targets, dtype=np.int64),
        correction_ids,
    )


def get_tflite_predictions(model_path, x, expected_classes):
    """Run the TFLite model and return one predicted class index per sequence."""
    interpreter = tf.lite.Interpreter(model_path=str(model_path), num_threads=2)
    interpreter.allocate_tensors()
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]

    if input_detail["dtype"] != np.float32:
        raise TypeError(f"Expected float32 TFLite input, got {input_detail['dtype']}")
    if int(output_detail["shape"][-1]) != expected_classes:
        raise ValueError(
            f"Expected {expected_classes} output classes, got {output_detail['shape'][-1]}"
        )

    predictions = []
    for sample in x:
        interpreter.set_tensor(
            input_detail["index"], sample[np.newaxis, ...].astype(np.float32)
        )
        interpreter.invoke()
        output = interpreter.get_tensor(output_detail["index"])[0]
        predictions.append(int(np.argmax(output)))
    return np.asarray(predictions, dtype=np.int64)


def accuracy(predictions, targets):
    return float(np.mean(predictions == targets))


def compare_per_class(labels, targets, baseline_predictions, candidate_predictions):
    """Reject a candidate that adds more than one validation error in any class."""
    results = {}
    failed_classes = []
    for class_index, label in enumerate(labels):
        mask = targets == class_index
        sample_count = int(np.sum(mask))
        baseline_errors = int(np.sum(baseline_predictions[mask] != targets[mask]))
        candidate_errors = int(np.sum(candidate_predictions[mask] != targets[mask]))
        allowed_errors = baseline_errors + 1
        passed = candidate_errors <= allowed_errors
        results[label] = {
            "validation_samples": sample_count,
            "baseline_errors": baseline_errors,
            "candidate_errors": candidate_errors,
            "maximum_allowed_errors": allowed_errors,
            "passed": passed,
        }
        if not passed:
            failed_classes.append(label)
    return results, failed_classes


def get_base_model_path():
    pointer = CANDIDATES_DIR / "latest_candidate.json"
    if pointer.exists():
        candidate_info = read_json(pointer)
        candidate = Path(candidate_info["keras_path"])
        if not candidate.is_absolute():
            candidate = ROOT / candidate
        manifest_path = candidate.parent / "manifest.json"
        if not candidate.exists() or not manifest_path.exists():
            raise FileNotFoundError(
                f"Latest candidate checkpoint or manifest is missing: {candidate}"
            )

        manifest = read_json(manifest_path)
        current_version = VERSION_PATH.read_text(encoding="utf-8").strip()
        if manifest.get("status") != "validated":
            raise ValueError("Latest candidate is not marked as validated.")
        if manifest.get("production_version") != current_version:
            print(
                "Latest candidate was trained against a different production "
                "version; restarting from the current production checkpoint."
            )
            return PRODUCTION_KERAS

        print(f"Continuing from latest validated candidate: {candidate}")
        return candidate
    return PRODUCTION_KERAS


def mark_corrections_used(correction_ids, candidate_id):
    for correction_id in correction_ids:
        path = CORRECTIONS_DIR / f"{correction_id}.json"
        item = read_json(path)
        item["training_status"] = "trained_candidate"
        item["candidate_id"] = candidate_id
        item["trained_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        write_json(path, item)


def run_training():
    if not 5 <= MIN_CORRECTIONS <= 10:
        raise ValueError("SIGNSPEAKPH_TRAINING_THRESHOLD must be from 5 to 10.")
    if not DATASET_DIR.is_dir():
        raise FileNotFoundError(f"Replay dataset not found: {DATASET_DIR}")
    if not PRODUCTION_KERAS.exists():
        raise FileNotFoundError(
            f"Production Keras checkpoint not found: {PRODUCTION_KERAS}"
        )

    labels = read_json(LABELS_PATH)
    if len(labels) != 22:
        raise ValueError(f"Expected 22 production labels, found {len(labels)}")

    correction_x, correction_y, correction_ids = load_new_corrections(labels)
    if len(correction_ids) < MIN_CORRECTIONS:
        print(
            f"Waiting for {MIN_CORRECTIONS} eligible approved corrections; "
            f"found {len(correction_ids)}."
        )
        return

    replay_x, replay_y, validation_x, validation_y, class_counts = load_replay_dataset(
        labels
    )
    version = VERSION_PATH.read_text(encoding="utf-8").strip()
    production_tflite = MODEL_DIR / f"action_{version}.tflite"
    if not production_tflite.exists():
        raise FileNotFoundError(
            f"Production TFLite model not found: {production_tflite}"
        )

    baseline_predictions = get_tflite_predictions(
        production_tflite, validation_x, len(labels)
    )
    baseline_accuracy = accuracy(baseline_predictions, validation_y)
    base_model_path = get_base_model_path()
    model = tf.keras.models.load_model(base_model_path, compile=True)

    if model.input_shape != (None, 30, 258) or model.output_shape != (
        None,
        len(labels),
    ):
        raise ValueError(
            f"Checkpoint shape mismatch: {model.input_shape} -> {model.output_shape}"
        )

    loss_name = getattr(model.loss, "__name__", str(model.loss)).lower()
    if "sparse_categorical" in loss_name:
        y_replay = replay_y
        y_corrections = correction_y
        y_validation = validation_y
    elif "categorical" in loss_name:
        y_replay = tf.keras.utils.to_categorical(replay_y, num_classes=len(labels))
        y_corrections = tf.keras.utils.to_categorical(
            correction_y, num_classes=len(labels)
        )
        y_validation = tf.keras.utils.to_categorical(
            validation_y, num_classes=len(labels)
        )
    else:
        raise ValueError(f"Unsupported saved loss function: {model.loss}")

    correction_x_repeated = np.repeat(correction_x, CORRECTION_REPEATS, axis=0)
    correction_y_repeated = np.repeat(y_corrections, CORRECTION_REPEATS, axis=0)
    train_x = np.concatenate([replay_x, correction_x_repeated], axis=0)
    train_y = np.concatenate([y_replay, correction_y_repeated], axis=0)

    learning_rate = model.optimizer.learning_rate
    if hasattr(learning_rate, "assign"):
        learning_rate.assign(LEARNING_RATE)
    else:
        model.optimizer.learning_rate = LEARNING_RATE

    print(f"Baseline production TFLite validation accuracy: {baseline_accuracy:.4f}")
    print(
        f"Training with {len(replay_x)} replay samples and "
        f"{len(correction_ids)} approved corrections."
    )
    print(f"Fine-tuning for up to {EPOCHS} epochs at learning rate {LEARNING_RATE}.")

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=2, restore_best_weights=True
    )
    model.fit(
        train_x,
        train_y,
        validation_data=(validation_x, y_validation),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        shuffle=True,
        callbacks=[early_stopping],
        verbose=2,
    )

    candidate_id = (
        time.strftime("candidate_%Y%m%d_%H%M%S", time.gmtime())
        + "_"
        + uuid.uuid4().hex[:8]
    )
    candidate_dir = CANDIDATES_DIR / candidate_id
    candidate_dir.mkdir(parents=True, exist_ok=False)
    keras_path = candidate_dir / "action.keras"
    tflite_path = candidate_dir / "action.tflite"
    model.save(keras_path)

    # Match the production exporter's fixed-batch TFLite conversion.
    seq_len = model.input_shape[1]
    n_feat = model.input_shape[2]

    fn = tf.function(
        lambda t: model(t, training=False),
        input_signature=[tf.TensorSpec([1, seq_len, n_feat], tf.float32)],
    )

    converter = tf.lite.TFLiteConverter.from_concrete_functions(
        [fn.get_concrete_function()], model
    )
    converter.experimental_enable_resource_variables = True
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]

    tflite_bytes = converter.convert()
    tflite_path.write_bytes(tflite_bytes)

    candidate_predictions = get_tflite_predictions(
        tflite_path, validation_x, len(labels)
    )
    candidate_accuracy = accuracy(candidate_predictions, validation_y)
    accuracy_drop = baseline_accuracy - candidate_accuracy
    per_class_results, failed_classes = compare_per_class(
        labels, validation_y, baseline_predictions, candidate_predictions
    )
    accepted = accuracy_drop <= MAX_VALIDATION_ACCURACY_DROP and not failed_classes

    manifest = {
        "candidate_id": candidate_id,
        "status": "validated" if accepted else "rejected",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_checkpoint": str(base_model_path.relative_to(ROOT)),
        "production_version": version,
        "labels": labels,
        "correction_ids": correction_ids,
        "replay_samples": len(replay_x),
        "correction_repeats": CORRECTION_REPEATS,
        "validation_samples": len(validation_x),
        "dataset_sequences_per_class": class_counts,
        "baseline_production_tflite_accuracy": baseline_accuracy,
        "candidate_tflite_accuracy": candidate_accuracy,
        "validation_accuracy_drop": accuracy_drop,
        "maximum_allowed_drop": MAX_VALIDATION_ACCURACY_DROP,
        "per_class_validation": per_class_results,
        "failed_classes": failed_classes,
        "keras_path": str(keras_path.relative_to(ROOT)),
        "tflite_path": str(tflite_path.relative_to(ROOT)),
        "production_modified": False,
    }
    write_json(candidate_dir / "manifest.json", manifest)

    print(f"Candidate TFLite validation accuracy: {candidate_accuracy:.4f}")
    print(f"Allowed accuracy drop: {MAX_VALIDATION_ACCURACY_DROP:.4f}")
    if not accepted:
        print("Candidate REJECTED. Production model was not changed.")
        if accuracy_drop > MAX_VALIDATION_ACCURACY_DROP:
            print(
                f"Overall accuracy drop {accuracy_drop:.4f} exceeds "
                f"the allowed {MAX_VALIDATION_ACCURACY_DROP:.4f}."
            )
        if failed_classes:
            print("Per-class regression guard failed for: " + ", ".join(failed_classes))
        print(f"Evaluation report: {candidate_dir / 'manifest.json'}")
        return

    write_json(
        CANDIDATES_DIR / "latest_candidate.json",
        {
            "candidate_id": candidate_id,
            "keras_path": str(keras_path.relative_to(ROOT)),
            "tflite_path": str(tflite_path.relative_to(ROOT)),
        },
    )
    mark_corrections_used(correction_ids, candidate_id)
    print("Candidate PASSED validation and was staged for maintainer review.")
    print("The production Keras and TFLite files were NOT changed.")
    print(f"Review report: {candidate_dir / 'manifest.json'}")


def process_is_running(pid):
    if os.name == "nt":
        # os.kill(pid, 0) is not a reliable process-existence probe on every
        # Windows/Python combination. Query the process handle instead.
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        open_process = kernel32.OpenProcess
        open_process.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        open_process.restype = ctypes.c_void_p
        get_exit_code = kernel32.GetExitCodeProcess
        get_exit_code.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        get_exit_code.restype = ctypes.c_int
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [ctypes.c_void_p]
        close_handle.restype = ctypes.c_int
        handle = open_process(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ctypes.get_last_error() == 5  # Access denied means it exists.
        try:
            exit_code = ctypes.c_ulong()
            if not get_exit_code(handle, ctypes.byref(exit_code)):
                return True
            return exit_code.value == 259  # STILL_ACTIVE
        finally:
            close_handle(handle)

    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as error:
        if error.errno == errno.ESRCH:
            return False
        # Treat ambiguous OS errors conservatively: never remove a possibly
        # active training lock.
        return True


def acquire_training_lock():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        try:
            lock_text = LOCK_PATH.read_text(encoding="ascii").strip()
            lock_pid = int(lock_text)
        except (OSError, ValueError):
            lock_pid = None

        if lock_pid is not None and process_is_running(lock_pid):
            raise SystemExit(
                f"Mini-training is already running (PID {lock_pid}; {LOCK_PATH})."
            )

        # A malformed lock is only considered stale after six hours. A valid
        # PID is removed only after the operating system confirms it is gone.
        age_seconds = time.time() - LOCK_PATH.stat().st_mtime
        if lock_pid is None and age_seconds <= 6 * 60 * 60:
            raise SystemExit("Training lock exists but its owner cannot be verified.")
        LOCK_PATH.unlink(missing_ok=True)
        try:
            descriptor = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise SystemExit("Another mini-training process acquired the lock.")

    with os.fdopen(descriptor, "w", encoding="ascii") as lock_file:
        lock_file.write(str(os.getpid()))


def main():
    acquire_training_lock()
    try:
        run_training()
    finally:
        try:
            owner_pid = int(LOCK_PATH.read_text(encoding="ascii").strip())
        except (OSError, ValueError):
            owner_pid = None
        if owner_pid == os.getpid():
            LOCK_PATH.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
