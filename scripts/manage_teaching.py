"""Local maintainer review tools for new SignSpeakPH sign contributions."""

import argparse
import json
import math
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEACHING_DIR = ROOT / "data" / "teaching"
PENDING_DIR = TEACHING_DIR / "pending"
APPROVED_DIR = TEACHING_DIR / "approved"
REJECTED_DIR = TEACHING_DIR / "rejected"


def read_contribution(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_contribution(item):
    label = item.get("label", "")
    if not isinstance(label, str) or not re.fullmatch(r"[a-z0-9_]{1,40}", label):
        return False, "invalid sign label"

    samples = item.get("samples")
    if not isinstance(samples, list) or not 3 <= len(samples) <= 5:
        return False, "expected 3 to 5 samples"

    sequence_length = item.get("sequence_length")
    num_features = item.get("num_features")
    if sequence_length != 30 or num_features != 258:
        return False, "expected 30 frames and 258 features"

    for sample_number, sequence in enumerate(samples, start=1):
        if not isinstance(sequence, list) or len(sequence) != sequence_length:
            return False, f"sample {sample_number} has an invalid frame count"
        for frame_number, frame in enumerate(sequence, start=1):
            if not isinstance(frame, list) or len(frame) != num_features:
                return (
                    False,
                    f"sample {sample_number}, frame {frame_number} has an invalid feature count",
                )
            try:
                if not all(math.isfinite(float(value)) for value in frame):
                    return False, "sample contains a non-finite landmark value"
            except (TypeError, ValueError):
                return False, "sample contains a non-numeric landmark value"

    return True, "valid"


def list_contributions():
    for title, folder in (
        ("PENDING", PENDING_DIR),
        ("APPROVED", APPROVED_DIR),
        ("REJECTED", REJECTED_DIR),
    ):
        print(f"\n=== {title} ===")
        files = sorted(folder.glob("*.json")) if folder.exists() else []
        if not files:
            print("None")
            continue
        for path in files:
            try:
                item = read_contribution(path)
                valid, reason = validate_contribution(item)
                print(
                    f"{item.get('id', path.stem)} | "
                    f"{item.get('display_name', item.get('label', 'unknown'))} | "
                    f"meaning={item.get('meaning', '')} | "
                    f"samples={item.get('sample_count', 0)} | "
                    f"validation={reason} | "
                    f"status={item.get('status', 'unknown')}"
                )
            except (OSError, json.JSONDecodeError) as error:
                print(f"{path.name} | INVALID JSON: {error}")


def contribution_id(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError):
        raise argparse.ArgumentTypeError("Contribution ID must be a valid UUID.")


def move_contribution(identifier, destination_dir, status):
    source = PENDING_DIR / f"{identifier}.json"
    if not source.exists():
        raise SystemExit(f"Pending teaching contribution not found: {identifier}")

    item = read_contribution(source)
    valid, reason = validate_contribution(item)
    if status == "approved" and not valid:
        raise SystemExit(f"Cannot approve invalid contribution: {reason}")

    item["status"] = status
    item["review_note"] = reason
    item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name
    temporary = destination.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(item, handle, indent=2)
    temporary.replace(destination)
    source.unlink()
    print(f"{status.capitalize()}: {identifier}")
    if status == "approved":
        print(
            "The contribution is approved for dataset preparation only. "
            "It is not added to the live model."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Review new SignSpeakPH sign teaching contributions."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List pending, approved, and rejected signs")
    approve_parser = commands.add_parser("approve", help="Approve a valid contribution")
    approve_parser.add_argument("id", type=contribution_id)
    reject_parser = commands.add_parser("reject", help="Reject a pending contribution")
    reject_parser.add_argument("id", type=contribution_id)
    args = parser.parse_args()

    if args.command == "list":
        list_contributions()
    elif args.command == "approve":
        move_contribution(args.id, APPROVED_DIR, "approved")
    elif args.command == "reject":
        move_contribution(args.id, REJECTED_DIR, "rejected")


if __name__ == "__main__":
    main()
