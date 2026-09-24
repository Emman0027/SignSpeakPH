"""
MediaPipe helper functions - FAST version (Pose + Hands, no Holistic).

Holistic always computes a 468-point face mesh internally even when it's
never used in extract_keypoints() - that face computation was the main
performance cost. This version uses separate Pose and Hands models, which
skip face detection entirely, producing the SAME 258-length feature vector
(pose(132) + lh(63) + rh(63)) but noticeably faster per frame.

IMPORTANT CAVEAT: Pose+Hands uses a different internal pipeline than
Holistic (Holistic uses pose landmarks to help locate hand regions before
running hand detection; standalone Hands finds hands independently via its
own palm-detector). Landmark values can differ slightly from what Holistic
produced during your original data collection. Test recognition accuracy
after switching - if it degrades noticeably, that confirms a distribution
mismatch, and the safer fix is either reverting to Holistic or re-recording
your gesture data using this same Pose+Hands extraction method so training
and inference match exactly.
"""

import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands


def create_models():
    """Create the Pose and Hands model instances once, reused across requests."""
    pose_model = mp_pose.Pose(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    hands_model = mp_hands.Hands(
        max_num_hands=2,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    return pose_model, hands_model


def mediapipe_detection(image, models):
    """Run Pose + Hands on a single BGR frame. `models` is (pose_model, hands_model)."""
    pose_model, hands_model = models
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    rgb_image.flags.writeable = False
    pose_results = pose_model.process(rgb_image)
    hands_results = hands_model.process(rgb_image)
    rgb_image.flags.writeable = True
    return image, (pose_results, hands_results)


def extract_keypoints(results):
    """
    258-length feature vector: pose(33*4=132) + lh(21*3=63) + rh(21*3=63).
    `results` is (pose_results, hands_results) from mediapipe_detection().
    """
    pose_results, hands_results = results

    pose = (
        np.array(
            [
                [r.x, r.y, r.z, r.visibility]
                for r in pose_results.pose_landmarks.landmark
            ]
        ).flatten()
        if pose_results.pose_landmarks
        else np.zeros(33 * 4)
    )

    lh = np.zeros(21 * 3)
    rh = np.zeros(21 * 3)
    if hands_results.multi_hand_landmarks:
        for landmarks, handedness in zip(
            hands_results.multi_hand_landmarks, hands_results.multi_handedness
        ):
            coords = np.array([[r.x, r.y, r.z] for r in landmarks.landmark]).flatten()
            label = handedness.classification[0].label  # 'Left' or 'Right'
            if label == "Left":
                lh = coords
            else:
                rh = coords

    return np.concatenate([pose, lh, rh])
