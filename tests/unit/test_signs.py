"""Tests for GET /signs and for keeping SIGN_INFO in sync with the model labels."""

import json

from app import app
from src.config.settings import LABELS_PATH
from src.constants import SIGN_INFO


def test_signs_endpoint_returns_guide_entries():
    response = app.test_client().get("/signs")
    assert response.status_code == 200
    signs = response.get_json()
    assert len(signs) == len(SIGN_INFO)
    for sign in signs:
        assert isinstance(sign["display"], str) and sign["display"]
        assert isinstance(sign["description"], str)


def test_sign_info_matches_model_labels():
    with open(LABELS_PATH) as f:
        labels = json.load(f)
    assert [s["label"] for s in SIGN_INFO] == labels
