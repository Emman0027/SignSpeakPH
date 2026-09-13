"""
MediaPipe helper functions.

Matches the notebook's ACTUAL functions (Cells 5 and 15), confirmed
directly from Action_Detection_Refined.ipynb:
  - NO face landmarks in the feature vector.
  - pose(132) + left hand(63) + right hand(63) = 258 features,
    matching model.add(LSTM(64, ..., input_shape=(30,258))) in Cell 49.
"""

import cv2
import numpy as np
import mediapipe as mp

mp_holistic = mp.solutions.holistic


def mediapipe_detection(image, model):
    """Run MediaPipe Holistic on a single BGR frame."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


def extract_keypoints(results):
    """
    258-length feature vector: pose(33*4=132) + lh(21*3=63) + rh(21*3=63).
    No face landmarks - matches the notebook's real extract_keypoints exactly.
    """
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() \
        if results.pose_landmarks else np.zeros(33 * 4)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() \
        if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() \
        if results.right_hand_landmarks else np.zeros(21 * 3)
    return np.concatenate([pose, lh, rh])
