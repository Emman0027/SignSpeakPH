"""
MediaPipe helper functions - Updated for MediaPipe Tasks API (v0.10.30+).

This version uses the new MediaPipe Tasks API which replaces the legacy
`mp.solutions` API. The feature extraction logic produces the SAME
258-length feature vector (pose(132) + lh(63) + rh(63)) for compatibility
with existing models.

IMPORTANT: The new Tasks API uses a different internal pipeline. Landmark
values can differ slightly from what the legacy Holistic/Pose+Hands produced
during original data collection. Test recognition accuracy after switching -
if it degrades noticeably, that confirms a distribution mismatch, and the
safer fix is either reverting to the legacy API (requires older Python/mediapipe)
or re-recording gesture data using this same extraction method so training
and inference match exactly.
"""

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    PoseLandmarker,
    PoseLandmarkerOptions,
)

# Global model instances (reused across requests)
_pose_landmarker = None
_hand_landmarker = None


def create_models():
    """Create the PoseLandmarker and HandLandmarker instances once, reused across requests."""
    global _pose_landmarker, _hand_landmarker

    import os

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    POSE_MODEL_PATH = os.path.join(
        BASE_DIR, "models", "mediapipe", "pose_landmarker.task"
    )
    HAND_MODEL_PATH = os.path.join(
        BASE_DIR, "models", "mediapipe", "hand_landmarker.task"
    )

    # Pose Landmarker options
    pose_options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=POSE_MODEL_PATH),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False,
    )

    # Hand Landmarker options
    hand_options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    _pose_landmarker = PoseLandmarker.create_from_options(pose_options)
    _hand_landmarker = HandLandmarker.create_from_options(hand_options)

    return _pose_landmarker, _hand_landmarker


def mediapipe_detection(image, models):
    """Run PoseLandmarker and HandLandmarker on a single BGR frame.

    `models` is (pose_model, hands_model).
    """
    pose_model, hands_model = models
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Convert to MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    pose_results = pose_model.detect(mp_image)
    hands_results = hands_model.detect(mp_image)

    return image, (pose_results, hands_results)


def extract_keypoints(results):
    """
    258-length feature vector: pose(33*4=132) + lh(21*3=63) + rh(21*3=63).
    `results` is (pose_results, hands_results) from mediapipe_detection().
    """
    pose_results, hands_results = results

    # Pose: 33 landmarks * 4 (x, y, z, visibility) = 132
    pose = np.zeros(33 * 4, dtype=np.float32)
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks[0]  # First (and only) detected pose
        for i, landmark in enumerate(landmarks):
            if i < 33:
                idx = i * 4
                pose[idx] = landmark.x
                pose[idx + 1] = landmark.y
                pose[idx + 2] = landmark.z
                pose[idx + 3] = landmark.visibility

    # Left hand: 21 landmarks * 3 (x, y, z) = 63
    lh = np.zeros(21 * 3, dtype=np.float32)
    # Right hand: 21 landmarks * 3 (x, y, z) = 63
    rh = np.zeros(21 * 3, dtype=np.float32)

    if hands_results.hand_landmarks:
        for landmarks, handedness in zip(
            hands_results.hand_landmarks, hands_results.handedness
        ):
            coords = np.array(
                [[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32
            ).flatten()
            # Handedness label: 'Left' or 'Right'
            label = handedness[0].category_name if handedness else "Right"
            if label == "Left":
                lh = coords
            else:
                rh = coords

    return np.concatenate([pose, lh, rh])


if __name__ == "__main__":
    # Quick test
    import sys

    print("Testing MediaPipe Tasks API...")
    try:
        pose, hands = create_models()
        print("✓ Models created successfully")
        # Test with a dummy image
        dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, (pose_res, hands_res) = mediapipe_detection(dummy_img, (pose, hands))
        kpts = extract_keypoints((pose_res, hands_res))
        print(f"✓ Keypoints extracted: shape={kpts.shape}")
        assert kpts.shape == (258,), f"Expected 258, got {kpts.shape}"
        print("✓ All tests passed!")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
