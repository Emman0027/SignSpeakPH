import numpy as np
import pytest

from src.services.learning_store import LearningStore, LearningStoreError


def make_sequence():
    return np.zeros((30, 258), dtype=np.float32)


def test_save_sample_persists_landmarks_and_metadata(tmp_path):
    store = LearningStore(tmp_path)
    result = store.save_sample(
        sequence=make_sequence(),
        sample_kind="correction",
        label="Kamusta",
        predicted_label="salamat",
        confidence=0.82,
    )

    assert result["label"] == "kamusta"
    assert result["predicted_label"] == "salamat"
    assert result["status"] == "pending_review"
    np.testing.assert_array_equal(
        store.get_sample_sequence(result["sample_id"]), make_sequence()
    )
    assert store.get_summary() == {
        "total": 1,
        "counts": {"pending_review_correction": 1},
    }


def test_new_sign_sample_is_not_automatically_approved(tmp_path):
    store = LearningStore(tmp_path)
    result = store.save_sample(
        sequence=make_sequence(),
        sample_kind="new_sign",
        label="bagong_salita",
        description="A sample sign description",
        share_consent=False,
    )

    assert result["status"] == "pending_review"
    assert result["share_consent"] is False
    assert store.get_summary()["total"] == 1


@pytest.mark.parametrize(
    "sequence",
    [
        np.zeros((29, 258), dtype=np.float32),
        np.zeros((30, 257), dtype=np.float32),
        np.full((30, 258), np.nan, dtype=np.float32),
    ],
)
def test_rejects_invalid_sequence(tmp_path, sequence):
    store = LearningStore(tmp_path)
    with pytest.raises(LearningStoreError):
        store.save_sample(
            sequence=sequence,
            sample_kind="correction",
            label="kamusta",
        )


def test_rejects_invalid_label_and_confidence(tmp_path):
    store = LearningStore(tmp_path)
    with pytest.raises(LearningStoreError):
        store.save_sample(
            sequence=make_sequence(),
            sample_kind="correction",
            label="../bad-label",
        )
    with pytest.raises(LearningStoreError):
        store.save_sample(
            sequence=make_sequence(),
            sample_kind="correction",
            label="kamusta",
            confidence=1.5,
        )


def test_missing_sample_raises_clear_error(tmp_path):
    store = LearningStore(tmp_path)
    with pytest.raises(LearningStoreError, match="sample not found"):
        store.get_sample_sequence("missing")
