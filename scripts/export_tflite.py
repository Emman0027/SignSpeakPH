"""Export the trained Keras model (action.h5) to the TFLite file the app loads.

Why this script exists
----------------------
app.py loads data/models/production/action_<VERSION>.tflite (see
src/config/settings.py) but nothing in the repo produced that file.

The model uses LSTM(activation='relu'). Converting it the default way needs
"Select TF ops", which the lightweight tflite-runtime package CANNOT run.
Fixing the batch size to 1 lets the converter use built-in ops only, so the
result runs on tflite-runtime. This script converts that way and then checks
the TFLite output against the Keras model before writing the final file.

Usage (run from the repo root, in the training environment that has
TensorFlow installed):

    python scripts/export_tflite.py
    python scripts/export_tflite.py --h5 path/to/action.h5

Needs: tensorflow (2.14 - 2.16). With TF >= 2.16 also: pip install tf_keras
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Must be set before TensorFlow is imported: keep the Keras 2 loader so that
# h5 files saved with TF 2.14 load correctly on newer TensorFlow too.
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402

try:
    import tf_keras as keras  # noqa: E402
except ImportError:  # TF <= 2.15 ships Keras 2 as tf.keras
    keras = tf.keras

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = REPO_ROOT / "data" / "models" / "production"


def read_version() -> str:
    version_file = MODELS_DIR / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "v1.0.0"


def find_h5(explicit):
    if explicit:
        return Path(explicit)
    for candidate in (MODELS_DIR / "action.h5", REPO_ROOT / "action.h5"):
        if candidate.exists():
            return candidate
    sys.exit("action.h5 not found. Pass it with --h5 <path>.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--h5", help="path to the trained action.h5")
    parser.add_argument("--out", help="output .tflite path (default: versioned)")
    parser.add_argument("--tolerance", type=float, default=1e-3)
    args = parser.parse_args()

    version = read_version()
    h5_path = find_h5(args.h5)
    out_path = Path(args.out) if args.out else MODELS_DIR / f"action_{version}.tflite"

    model = keras.models.load_model(h5_path, compile=False)
    _, seq_len, n_feat = model.input_shape
    n_classes = model.output_shape[-1]
    print(f"Loaded {h5_path.name}: input={seq_len}x{n_feat}, classes={n_classes}")

    labels_path = MODELS_DIR / f"labels_{version}.json"
    if labels_path.exists():
        n_labels = len(json.loads(labels_path.read_text()))
        if n_labels != n_classes:
            sys.exit(
                f"Model has {n_classes} classes but {labels_path.name} has "
                f"{n_labels} labels. Fix the labels/model mismatch first."
            )

    # Fixed batch size of 1 -> built-in TFLite ops only (no Select TF ops).
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

    # Verify the converted model against Keras on random sequences.
    interpreter = tf.lite.Interpreter(model_content=tflite_bytes)
    interpreter.allocate_tensors()
    in_idx = interpreter.get_input_details()[0]["index"]
    out_idx = interpreter.get_output_details()[0]["index"]
    rng = np.random.default_rng(0)
    worst = 0.0
    for _ in range(8):
        x = rng.random((1, seq_len, n_feat), dtype=np.float32)
        expected = model.predict(x, verbose=0)[0]
        interpreter.set_tensor(in_idx, x)
        interpreter.invoke()
        got = interpreter.get_tensor(out_idx)[0]
        worst = max(worst, float(np.abs(expected - got).max()))
        if int(np.argmax(expected)) != int(np.argmax(got)):
            sys.exit("Converted model predicts a different class. Not saved.")
    if worst > args.tolerance:
        sys.exit(f"Max difference {worst:.2e} > tolerance. Not saved.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(tflite_bytes)
    print(
        f"Verified (max diff {worst:.2e}). Wrote {out_path} "
        f"({len(tflite_bytes) / 1024:.0f} KB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
