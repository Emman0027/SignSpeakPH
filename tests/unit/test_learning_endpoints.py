import numpy as np
import pytest

import app as app_module
from src.services.learning_store import LearningStore


@pytest.fixture
def learning_client(tmp_path, monkeypatch):
    app_module.app.config["TESTING"] = True
    monkeypatch.setattr(
        app_module,
        "learning_store",
        LearningStore(tmp_path, sequence_length=30, num_features=258),
    )
    monkeypatch.setattr(
        app_module,
        "extract_learning_sequence",
        lambda images: np.zeros((30, 258), dtype=np.float32),
    )
    with app_module.app.test_client() as client:
        yield client


def valid_images():
    return ["data:image/jpeg;base64,ZmFrZQ=="] * 30


def test_correction_endpoint_saves_confirmed_existing_label(learning_client):
    response = learning_client.post(
        "/learning/correct",
        json={
            "images": valid_images(),
            "predicted_label": "salamat",
            "correct_label": "kamusta",
            "confidence": 0.81,
        },
    )

    assert response.status_code == 201
    sample = response.get_json()["sample"]
    assert sample["sample_kind"] == "correction"
    assert sample["label"] == "kamusta"
    assert sample["predicted_label"] == "salamat"
    assert sample["status"] == "pending_review"


def test_correction_endpoint_rejects_same_label(learning_client):
    response = learning_client.post(
        "/learning/correct",
        json={
            "images": valid_images(),
            "predicted_label": "kamusta",
            "correct_label": "kamusta",
        },
    )
    assert response.status_code == 400
    assert "must differ" in response.get_json()["error"]


def test_teach_endpoint_saves_new_label_without_adding_it_to_model(learning_client):
    response = learning_client.post(
        "/learning/teach",
        json={
            "images": valid_images(),
            "label": "bagong_salita",
            "description": "A new sign to review",
            "share_consent": False,
        },
    )

    assert response.status_code == 201
    sample = response.get_json()["sample"]
    assert sample["sample_kind"] == "new_sign"
    assert sample["label"] == "bagong_salita"
    assert sample["status"] == "pending_review"
    assert sample["share_consent"] is False


def test_teach_endpoint_rejects_existing_model_label(learning_client):
    response = learning_client.post(
        "/learning/teach",
        json={"images": valid_images(), "label": "kamusta"},
    )
    assert response.status_code == 400
    assert "already exists" in response.get_json()["error"]


def test_learning_summary_does_not_expose_sample_data(learning_client):
    response = learning_client.get("/learning/summary")
    assert response.status_code == 200
    assert response.get_json() == {"total": 0, "counts": {}}
