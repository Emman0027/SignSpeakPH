"""Tests for GET /config and for the feedback ID returned by POST /feedback.

Feedback is redirected to a temporary folder, so these tests never touch the
real data/feedback/feedback.json.
"""

import json

import pytest

import app as app_module
from app import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # The feedback routes build their path from app.BASE_DIR
    monkeypatch.setattr(app_module, "BASE_DIR", str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def _stored(tmp_path):
    return json.loads((tmp_path / "data" / "feedback" / "feedback.json").read_text())


def test_config_returns_server_threshold(client):
    response = client.get("/config")
    assert response.status_code == 200
    data = response.get_json()
    assert data["threshold"] == app_module.THRESHOLD
    assert 0 < data["threshold"] <= 1


def test_post_feedback_returns_id_of_new_entry(client, tmp_path):
    first = client.post("/feedback", json={"rating": 4, "prediction": "oo"})
    second = client.post("/feedback", json={"rating": 5, "prediction": "hindi"})
    assert first.status_code == second.status_code == 200
    assert first.get_json()["id"] == 0
    assert second.get_json()["id"] == 1
    assert _stored(tmp_path)[1]["prediction"] == "hindi"


def test_returned_id_works_for_put_and_delete(client, tmp_path):
    new_id = client.post(
        "/feedback", json={"rating": 2, "prediction": "oo"}
    ).get_json()["id"]

    updated = client.put(f"/feedback/{new_id}", json={"rating": 5, "prediction": "oo"})
    assert updated.status_code == 200
    assert _stored(tmp_path)[new_id]["rating"] == 5

    deleted = client.delete(f"/feedback/{new_id}")
    assert deleted.status_code == 200
    assert _stored(tmp_path) == []
