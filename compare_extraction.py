# Run this in your notebook to check how similar the two extraction
# methods actually are, BEFORE trusting the swap in your live app.

import cv2
import numpy as np
import mediapipe as mp

mp_holistic = mp.solutions.holistic
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands


def extract_from_holistic(frame):
    with mp_holistic.Holistic(model_complexity=0, min_detection_confidence=0.5) as holistic:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)
        pose = np.array([[r.x, r.y, r.z, r.visibility] for r in results.pose_landmarks.landmark]).flatten() \
            if results.pose_landmarks else np.zeros(33 * 4)
        lh = np.array([[r.x, r.y, r.z] for r in results.left_hand_landmarks.landmark]).flatten() \
            if results.left_hand_landmarks else np.zeros(21 * 3)
        rh = np.array([[r.x, r.y, r.z] for r in results.right_hand_landmarks.landmark]).flatten() \
            if results.right_hand_landmarks else np.zeros(21 * 3)
        return np.concatenate([pose, lh, rh])


def extract_from_pose_hands(frame):
    with mp_pose.Pose(model_complexity=0, min_detection_confidence=0.5) as pose_model, \
         mp_hands.Hands(max_num_hands=2, model_complexity=0, min_detection_confidence=0.5) as hands_model:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose_model.process(image)
        hands_results = hands_model.process(image)

        pose = np.array([[r.x, r.y, r.z, r.visibility] for r in pose_results.pose_landmarks.landmark]).flatten() \
            if pose_results.pose_landmarks else np.zeros(33 * 4)

        lh = np.zeros(21 * 3)
        rh = np.zeros(21 * 3)
        if hands_results.multi_hand_landmarks:
            for landmarks, handedness in zip(hands_results.multi_hand_landmarks, hands_results.multi_handedness):
                coords = np.array([[r.x, r.y, r.z] for r in landmarks.landmark]).flatten()
                label = handedness.classification[0].label  # 'Left' or 'Right'
                if label == 'Left':
                    lh = coords
                else:
                    rh = coords
        return np.concatenate([pose, lh, rh])


# Grab a few real frames from your webcam to compare on
cap = cv2.VideoCapture(0)
print("Capturing a test frame in 3 seconds - hold a sign steady...")
cv2.waitKey(3000)
ret, test_frame = cap.read()
cap.release()

kp_holistic = extract_from_holistic(test_frame)
kp_pose_hands = extract_from_pose_hands(test_frame)

diff = np.abs(kp_holistic - kp_pose_hands)
print("Mean absolute difference:", diff.mean())
print("Max absolute difference:", diff.max())
print("Pose section diff (first 132):", diff[:132].mean())
print("Left hand diff (132-195):", diff[132:195].mean())
print("Right hand diff (195-258):", diff[195:258].mean())
