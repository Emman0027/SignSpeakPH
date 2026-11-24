"""Local, review-first storage for user-contributed sign sequences.

Only extracted landmark arrays are stored; raw webcam frames are discarded.
Samples remain pending until a separate review/training workflow approves them.
"""
from __future__ import annotations

import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


_LABEL_RE = re.compile(r"^[a-z][a-z0-9_]{1,39}$")


class LearningStoreError(ValueError):
    """Raised when a learning sample or label is invalid."""


class LearningStore:
    """Persist landmark sequences and metadata outside the source repository."""

    def __init__(
        self,
        root: Path | str,
        sequence_length: int = 30,
        num_features: int = 258,
    ) -> None:
        self.root = Path(root)
        self.samples_dir = self.root / "samples"
        self.database_path = self.root / "learning_samples.sqlite3"
        self.sequence_length = int(sequence_length)
        self.num_features = int(num_features)
        if self.sequence_length < 1 or self.num_features < 1:
            raise ValueError("sequence_length and num_features must be positive")
        self.samples_dir.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_samples (
                    sample_id TEXT PRIMARY KEY,
                    sample_kind TEXT NOT NULL,
                    label TEXT NOT NULL,
                    predicted_label TEXT,
                    confidence REAL,
                    description TEXT,
                    status TEXT NOT NULL DEFAULT 'pending_review',
                    share_consent INTEGER NOT NULL DEFAULT 0,
                    sequence_path TEXT NOT NULL,
                    sequence_length INTEGER NOT NULL,
                    num_features INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_learning_status "
                "ON learning_samples(status)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_learning_label "
                "ON learning_samples(label)"
            )

    @staticmethod
    def validate_label(label: Any) -> str:
        if not isinstance(label, str):
            raise LearningStoreError("label must be a string")
        normalized = label.strip().lower().replace(" ", "_")
        if not _LABEL_RE.fullmatch(normalized):
            raise LearningStoreError(
                "label must be 2-40 characters, start with a letter, "
                "and contain only lowercase letters, numbers, or underscores"
            )
        return normalized

    def validate_sequence(self, sequence: Any) -> np.ndarray:
        try:
            array = np.asarray(sequence, dtype=np.float32)
        except (TypeError, ValueError) as exc:
            raise LearningStoreError("sequence must contain numeric landmarks") from exc

        expected = (self.sequence_length, self.num_features)
        if array.shape != expected:
            raise LearningStoreError(
                f"sequence must have shape {expected}; received {array.shape}"
            )
        if not np.isfinite(array).all():
            raise LearningStoreError("sequence contains invalid numeric values")
        return array

    def save_sample(
        self,
        *,
        sequence: Any,
        sample_kind: str,
        label: str,
        predicted_label: str | None = None,
        confidence: float | None = None,
        description: str | None = None,
        share_consent: bool = False,
    ) -> dict[str, Any]:
        if sample_kind not in {"correction", "new_sign"}:
            raise LearningStoreError("sample_kind must be correction or new_sign")
        clean_label = self.validate_label(label)
        if predicted_label is not None:
            predicted_label = self.validate_label(predicted_label)
        if confidence is not None:
            try:
                confidence = float(confidence)
            except (TypeError, ValueError) as exc:
                raise LearningStoreError("confidence must be numeric") from exc
            if not np.isfinite(confidence) or not 0 <= confidence <= 1:
                raise LearningStoreError("confidence must be between 0 and 1")
        if description is not None:
            if not isinstance(description, str) or len(description) > 300:
                raise LearningStoreError(
                    "description must be text up to 300 characters"
                )
            description = description.strip() or None
        if not isinstance(share_consent, bool):
            raise LearningStoreError("share_consent must be a boolean")

        array = self.validate_sequence(sequence)
        sample_id = uuid.uuid4().hex
        filename = f"{sample_id}.npy"
        final_path = self.samples_dir / filename
        temporary_path = self.samples_dir / f".{sample_id}.tmp"
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            with temporary_path.open("wb") as file_handle:
                np.save(file_handle, array, allow_pickle=False)
            temporary_path.replace(final_path)
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO learning_samples (
                        sample_id, sample_kind, label, predicted_label, confidence,
                        description, status, share_consent, sequence_path,
                        sequence_length, num_features, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'pending_review', ?, ?, ?, ?, ?)
                    """,
                    (
                        sample_id,
                        sample_kind,
                        clean_label,
                        predicted_label,
                        confidence,
                        description,
                        int(share_consent),
                        filename,
                        self.sequence_length,
                        self.num_features,
                        created_at,
                    ),
                )
        except Exception:
            temporary_path.unlink(missing_ok=True)
            final_path.unlink(missing_ok=True)
            raise

        return {
            "sample_id": sample_id,
            "sample_kind": sample_kind,
            "label": clean_label,
            "predicted_label": predicted_label,
            "status": "pending_review",
            "share_consent": share_consent,
            "created_at": created_at,
        }

    def get_sample_sequence(self, sample_id: str) -> np.ndarray:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT sequence_path FROM learning_samples WHERE sample_id = ?",
                (sample_id,),
            ).fetchone()
        if row is None:
            raise LearningStoreError("sample not found")
        path = self.samples_dir / row["sequence_path"]
        if not path.is_file():
            raise LearningStoreError("sample data file is missing")
        return np.load(path, allow_pickle=False)

    def get_summary(self) -> dict[str, Any]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT status, sample_kind, COUNT(*) AS total "
                "FROM learning_samples GROUP BY status, sample_kind"
            ).fetchall()
            total = connection.execute(
                "SELECT COUNT(*) AS total FROM learning_samples"
            ).fetchone()["total"]
        counts = {
            f"{row['status']}_{row['sample_kind']}": row["total"] for row in rows
        }
        return {"total": total, "counts": counts}
