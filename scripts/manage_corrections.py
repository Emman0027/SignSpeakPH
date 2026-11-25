"""Local maintainer tools for reviewing SignSpeakPH corrections.

Approvals are intentionally CLI-only; public visitors cannot approve training data.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORRECTIONS_DIR = ROOT / "data" / "corrections"
PENDING_DIR = CORRECTIONS_DIR / "pending"
APPROVED_DIR = CORRECTIONS_DIR / "approved"
REJECTED_DIR = CORRECTIONS_DIR / "rejected"
TRAINER = ROOT / "scripts" / "train_correction_candidate.py"


def read_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    temporary.replace(path)


def correction_id(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError):
        raise argparse.ArgumentTypeError("Correction ID must be a valid UUID.")


def training_threshold():
    try:
        value = int(os.environ.get("SIGNSPEAKPH_TRAINING_THRESHOLD", "5"))
    except ValueError:
        raise RuntimeError(
            "SIGNSPEAKPH_TRAINING_THRESHOLD must be an integer from 5 to 10."
        )
    if not 5 <= value <= 10:
        raise RuntimeError("SIGNSPEAKPH_TRAINING_THRESHOLD must be from 5 to 10.")
    return value


def sequence_is_valid(data):
    sequence = data.get("sequence")
    if not data.get("sequence_included") or sequence is None:
        return False, "no consented sequence"
    try:
        import numpy as np

        array = np.asarray(sequence, dtype=np.float32)
    except (TypeError, ValueError):
        return False, "sequence is not numeric"
    if array.shape != (30, 258):
        return False, f"wrong sequence shape {array.shape}; expected (30, 258)"
    if not np.isfinite(array).all():
        return False, "sequence contains NaN or infinite values"
    return True, "valid"


def list_corrections():
    for title, folder in (("PENDING", PENDING_DIR), ("APPROVED", APPROVED_DIR)):
        print(f"\n=== {title} ===")
        files = sorted(folder.glob("*.json")) if folder.exists() else []
        if not files:
            print("None")
            continue
        for path in files:
            try:
                item = read_json(path)
                valid, reason = sequence_is_valid(item)
                print(
                    f"{item.get('id', path.stem)} | "
                    f"{item.get('predicted_label')} -> {item.get('corrected_label')} | "
                    f"sequence={reason} | "
                    f"training={item.get('training_status', 'not approved')}"
                )
            except Exception as error:
                print(f"{path.name} | INVALID JSON: {error}")


def eligible_untrained_count():
    count = 0
    if not APPROVED_DIR.exists():
        return count
    for path in APPROVED_DIR.glob("*.json"):
        try:
            item = read_json(path)
            valid, _ = sequence_is_valid(item)
            if (
                item.get("status") == "approved"
                and item.get("training_status") != "trained_candidate"
                and valid
            ):
                count += 1
        except Exception:
            continue
    return count


def approve(identifier):
    source = PENDING_DIR / f"{identifier}.json"
    if not source.exists():
        raise SystemExit(f"Pending correction not found: {identifier}")

    item = read_json(source)
    valid, reason = sequence_is_valid(item)
    item["status"] = "approved"
    item["reviewed_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    item["training_status"] = "pending" if valid else "not_eligible"
    item["training_note"] = reason if not valid else "Awaiting mini-training batch"

    destination = APPROVED_DIR / source.name
    write_json(destination, item)
    source.unlink()
    print(f"Approved: {identifier}")
    if not valid:
        print(
            f"Approved for record-keeping only; not eligible for training ({reason})."
        )
        return

    threshold = training_threshold()
    count = eligible_untrained_count()
    print(f"Eligible approved corrections: {count}/{threshold}")
    if count < threshold:
        print("Mini-training will start automatically when the threshold is reached.")
        return

    print("Threshold reached. Starting candidate mini-training...")
    result = subprocess.run([sys.executable, str(TRAINER)], cwd=ROOT, check=False)
    if result.returncode:
        print(f"Candidate training did not complete (exit code {result.returncode}).")
        print("Approved corrections remain available for another attempt.")
    else:
        print(
            "Candidate training process finished. Review its evaluation report before promotion."
        )


def reject(identifier):
    candidates = [
        PENDING_DIR / f"{identifier}.json",
        APPROVED_DIR / f"{identifier}.json",
    ]
    source = next((path for path in candidates if path.exists()), None)
    if source is None:
        raise SystemExit(f"Correction not found: {identifier}")
    item = read_json(source)
    item["status"] = "rejected"
    item["rejected_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    destination = REJECTED_DIR / source.name
    write_json(destination, item)
    source.unlink()
    print(f"Rejected: {identifier}")


def main():
    parser = argparse.ArgumentParser(
        description="Review SignSpeakPH correction submissions."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List pending and approved corrections")
    approve_parser = commands.add_parser("approve", help="Approve one correction")
    approve_parser.add_argument("id", type=correction_id)
    reject_parser = commands.add_parser("reject", help="Reject one correction")
    reject_parser.add_argument("id", type=correction_id)
    args = parser.parse_args()

    if args.command == "list":
        list_corrections()
    elif args.command == "approve":
        approve(args.id)
    elif args.command == "reject":
        reject(args.id)


if __name__ == "__main__":
    main()
