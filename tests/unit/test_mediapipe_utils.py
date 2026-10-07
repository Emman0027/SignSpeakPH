import cv2
import mediapipe as mp
import numpy as np
import pytest

from src.utils.mediapipe_utils import (
    create_models,
    extract_keypoints,
    mediapipe_detection,
)


def test_create_models():
    """Test that create_models returns valid MediaPipe model instances"""
    pose_model, hands_model = create_models()

    # Check that we got model instances
    assert pose_model is not None
    assert hands_model is not None

    # Check that they are the correct types
    assert isinstance(pose_model, mp.solutions.pose.Pose)
    assert isinstance(hands_model, mp.solutions.hands.Hands)


def test_mediapipe_detection():
    """Test mediapipe_detection function with a dummy image"""
    # Create a dummy black image (BGR format)
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)

    # Create models
    pose_model, hands_model = create_models()
    models = (pose_model, hands_model)

    # Run detection
    processed_image, results = mediapipe_detection(dummy_image, models)

    # Check that we got results
    assert processed_image is not None
    assert results is not None

    # Check that image is still the same shape
    assert processed_image.shape == dummy_image.shape

    # Check that results is a tuple of (pose_results, hands_results)
    assert isinstance(results, tuple)
    assert len(results) == 2


def test_extract_keypoints_no_detection():
    """Test extract_keypoints when no pose or hands are detected"""
    # Create dummy results with no detections
    pose_results = type("PoseResults", (), {"pose_landmarks": None})()
    hands_results = type(
        "HandsResults", (), {"multi_hand_landmarks": None, "multi_handedness": None}
    )()

    results = (pose_results, hands_results)

    # Extract keypoints
    keypoints = extract_keypoints(results)

    # Should return a 258-element array (132 + 63 + 63)
    assert isinstance(keypoints, np.ndarray)
    assert keypoints.shape == (258,)

    # Should be all zeros when nothing is detected
    assert np.allclose(keypoints, np.zeros(258))


def test_extract_keypoints_with_detection():
    """Test extract_keypoints with simulated detections"""
    # Create mock pose landmarks (33 landmarks with x, y, z, visibility)
    mock_pose_landmarks = []
    for i in range(33):
        mock_pose_landmarks.append(
            type(
                "Landmark",
                (),
                {
                    "x": float(i) / 100.0,
                    "y": float(i) / 100.0,
                    "z": float(i) / 100.0,
                    "visibility": 1.0,
                },
            )()
        )

    pose_results = type(
        "PoseResults",
        (),
        {
            "pose_landmarks": type(
                "PoseLandmarks", (), {"landmark": mock_pose_landmarks}
            )()
        },
    )()

    # Create mock hand landmarks for left hand (21 landmarks with x, y, z)
    mock_left_hand_landmarks = []
    for i in range(21):
        mock_left_hand_landmarks.append(
            type(
                "Landmark",
                (),
                {"x": float(i) / 50.0, "y": float(i) / 50.0, "z": float(i) / 50.0},
            )
        )

    # Create a mock hand landmarks object that has the 'landmark' attribute
    mock_hand_landmarks_object = type(
        "HandLandmarksObject", (), {"landmark": mock_left_hand_landmarks}
    )()

    # Create mock handedness for left hand
    mock_handedness_object = type(
        "HandednessObject",
        (),
        {"classification": [type("Classification", (), {"label": "Left"})()]},
    )()

    # Create mock hand results
    hands_results = type(
        "HandsResults",
        (),
        {
            "multi_hand_landmarks": [mock_hand_landmarks_object],
            "multi_handedness": [mock_handedness_object],
        },
    )()

    results = (pose_results, hands_results)

    # Extract keypoints
    keypoints = extract_keypoints(results)

    # Should return a 258-element array
    assert isinstance(keypoints, np.ndarray)
    assert keypoints.shape == (258,)

    # Check that we got non-zero values (since we provided mock data)
    assert not np.allclose(keypoints, np.zeros(258))

    # Check pose section (first 132 elements) - 33 landmarks * 4 values
    pose_section = keypoints[:132]
    assert not np.allclose(pose_section, np.zeros(132))

    # Check left hand section (next 63 elements) - 21 landmarks * 3 values
    lh_section = keypoints[132:195]
    assert not np.allclose(lh_section, np.zeros(63))

    # Check right hand section (last 63 elements) - should be zeros since we didn't provide right hand
    rh_section = keypoints[195:258]
    assert np.allclose(rh_section, np.zeros(63))


def test_extract_keypoints_shape_consistency():
    """Test that extract_keypoints always returns consistent shape"""
    # Test with no detections
    pose_results_none = type("PoseResults", (), {"pose_landmarks": None})()
    hands_results_none = type(
        "HandsResults", (), {"multi_hand_landmarks": None, "multi_handedness": None}
    )()
    results_none = (pose_results_none, hands_results_none)

    keypoints_none = extract_keypoints(results_none)
    assert keypoints_none.shape == (258,)

    # Test with pose only
    mock_pose_landmarks = []
    for i in range(33):
        mock_pose_landmarks.append(
            type("Landmark", (), {"x": 0.5, "y": 0.5, "z": 0.5, "visibility": 1.0})()
        )
    pose_results_only = type(
        "PoseResults",
        (),
        {
            "pose_landmarks": type(
                "PoseLandmarks", (), {"landmark": mock_pose_landmarks}
            )()
        },
    )()
    hands_results_none = type(
        "HandsResults", (), {"multi_hand_landmarks": None, "multi_handedness": None}
    )()
    results_pose_only = (pose_results_only, hands_results_none)

    keypoints_pose_only = extract_keypoints(results_pose_only)
    assert keypoints_pose_only.shape == (258,)

    # Pose section should have values, hands should be zero
    assert not np.allclose(keypoints_pose_only[:132], np.zeros(132))
    assert np.allclose(keypoints_pose_only[132:], np.zeros(126))  # 63+63
