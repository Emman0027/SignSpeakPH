#!/usr/bin/env python3
"""
scan_index.py — incremental repo state tracker.

Purpose: let an AI agent know exactly which files changed since it last
looked, without re-reading or re-hashing the whole repo every time, and
without ever re-summarizing a file that hasn't changed.

Usage:
    python scan_index.py --root <repo_path> [--state .ai-context/STATE.json]

Behavior:
    - Walks <repo_path>, skipping noise dirs/files (see EXCLUDES below).
    - For each file, computes a cheap fingerprint (size + mtime); only
      falls back to a real sha256 hash when size+mtime look unchanged
      but you pass --verify (paranoid mode), or when size+mtime alone
      can't be trusted (rare).
    - Compares against the previous STATE.json.
    - Prints a plain diff report: NEW / MODIFIED / DELETED / UNCHANGED (count only).
    - Writes the updated STATE.json.

The agent should only read the *content* of files listed as NEW or
MODIFIED. Everything else it already knows from PROJECT_INDEX.md /
its own memory of prior sessions.
"""

import argparse
import hashlib
import json
import os
import sys
import time

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".next",
    ".ai-context",
    "site-packages",
    ".mypy_cache",
    ".pytest_cache",
}
EXCLUDE_EXT = {".pyc", ".pyo", ".DS_Store"}
# Files above this size get fingerprinted (size+mtime) only, never fully
# hashed, so a 40MB .h5 model file doesn't get read into memory each scan.
HASH_SIZE_LIMIT = 2 * 1024 * 1024  # 2 MB


def sha256_of(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def fingerprint(path):
    try:
        st = os.stat(path)
    except OSError:
        return None
    size = st.st_size
    mtime = int(st.st_mtime)
    if size <= HASH_SIZE_LIMIT:
        digest = sha256_of(path)
    else:
        digest = f"size-mtime:{size}:{mtime}"
    return {"size": size, "mtime": mtime, "hash": digest}


def walk_repo(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")
        ]
        for fn in filenames:
            if os.path.splitext(fn)[1] in EXCLUDE_EXT:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            yield rel, full


def load_state(state_path):
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"generated_at": None, "files": {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Path to the repo root to scan")
    ap.add_argument(
        "--state",
        default=None,
        help="Path to STATE.json (default: <root>/.ai-context/STATE.json)",
    )
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the diff, no header/footer noise",
    )
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    state_path = args.state or os.path.join(root, ".ai-context", "STATE.json")
    os.makedirs(os.path.dirname(state_path), exist_ok=True)

    old_state = load_state(state_path)
    old_files = old_state.get("files", {})

    new_files = {}
    new_set, modified_set, unchanged_set = [], [], []

    for rel, full in walk_repo(root):
        fp = fingerprint(full)
        if fp is None:
            continue
        new_files[rel] = fp
        old = old_files.get(rel)
        if old is None:
            new_set.append(rel)
        elif old.get("hash") != fp["hash"]:
            modified_set.append(rel)
        else:
            unchanged_set.append(rel)

    deleted_set = sorted(set(old_files.keys()) - set(new_files.keys()))

    new_state = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": root,
        "files": new_files,
    }
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(new_state, f, indent=2, sort_keys=True)

    report = {
        "new": sorted(new_set),
        "modified": sorted(modified_set),
        "deleted": deleted_set,
        "unchanged_count": len(unchanged_set),
        "total_files": len(new_files),
        "state_path": state_path,
    }

    if args.quiet:
        print(json.dumps(report, indent=2))
        return

    print(f"Scanned {report['total_files']} files under {root}")
    print(f"  new:       {len(report['new'])}")
    print(f"  modified:  {len(report['modified'])}")
    print(f"  deleted:   {len(report['deleted'])}")
    print(f"  unchanged: {report['unchanged_count']}  (skipped — do not re-read these)")
    if report["new"]:
        print("\nNEW:")
        for p in report["new"]:
            print(f"  + {p}")
    if report["modified"]:
        print("\nMODIFIED:")
        for p in report["modified"]:
            print(f"  * {p}")
    if report["deleted"]:
        print("\nDELETED:")
        for p in report["deleted"]:
            print(f"  - {p}")
    print(f"\nSTATE.json updated at: {state_path}")


if __name__ == "__main__":
    sys.exit(main())
