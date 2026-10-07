import json
import os

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test the index route returns a successful response"""
    response = client.get("/")
    assert response.status_code == 200
    # Check that we get HTML content
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data.lower()


def test_predict_batch_no_images(client):
    """Test predict_batch endpoint with no images provided"""
    response = client.post("/predict_batch", json={})
    # Should return 400 Bad Request when no images provided
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "no images provided"


def test_predict_batch_wrong_length(client):
    """Test predict_batch endpoint with wrong number of images"""
    # Import SEQUENCE_LENGTH from config to use correct value
    from src.config.settings import SEQUENCE_LENGTH

    # Send wrong number of images
    wrong_count = SEQUENCE_LENGTH + 1
    images = [
        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQECAQECAQEAMEQ="
    ] * wrong_count
    response = client.post("/predict_batch", json={"images": images})
    # Should return 400 Bad Request for wrong length
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert f"expected {SEQUENCE_LENGTH} frames" in data["error"]


def test_feedback_post_missing_data(client):
    """Test POST /feedback with missing required data"""
    response = client.post("/feedback", json={})
    # Should return 400 for missing data
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_feedback_post_invalid_rating(client):
    """Test POST /feedback with invalid rating"""
    feedback_data = {
        "rating": 10,  # Invalid - should be 1-5
        "comment": "Test feedback",
    }
    response = client.post("/feedback", json=feedback_data)
    # Should return 400 for invalid rating
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "rating must be between 1 and 5" in data["error"]


def test_feedback_post_valid_data(client):
    """Test POST /feedback with valid data"""
    feedback_data = {"rating": 5, "comment": "Great app!", "user_id": "test_user_123"}
    response = client.post("/feedback", json=feedback_data)
    # Should return 200 for valid feedback
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "Feedback received" in data["message"]


def test_feedback_put_nonexistent(client):
    """Test PUT /feedback/<id> for nonexistent feedback"""
    response = client.put("/feedback/99999", json={"rating": 5})
    # Should return 404 for nonexistent resource
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "feedback not found" in data["error"]


def test_feedback_delete_nonexistent(client):
    """Test DELETE /feedback/<id> for nonexistent feedback"""
    response = client.delete("/feedback/99999")
    # Should return 404 for nonexistent resource
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "feedback not found" in data["error"]
