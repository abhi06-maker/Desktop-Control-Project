import cv2
import mediapipe as mp
import pickle
import pyautogui
import os
import time


def run_gesture_engine(shared_state):

    model_path = "data/gesture_model.pkl"

    # ---- Model Check ----
    if not os.path.exists(model_path):
        shared_state["status"] = "Error: Model file missing."
        return

    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        shared_state["status"] = f"Error loading model: {e}"
        return

    # ---- Mediapipe Init ----
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # ---- Camera Init (Windows stable) ----
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        shared_state["status"] = "Error: Camera not detected"
        return

    last_action_time = 0
    action_cooldown = 1.5

    shared_state["status"] = "System Operational"

    while True:
        success, img = cap.read()

        if not success:
            shared_state["status"] = "Error reading camera frame"
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:

                landmarks = []
                for lm in hand_lms.landmark:
                    landmarks.extend([lm.x, lm.y])

                try:
                    prediction = model.predict([landmarks])[0]

                    # 🔥 DASHBOARD UPDATE
                    shared_state["last_gesture"] = prediction

                    current_time = time.time()

                    if current_time - last_action_time > action_cooldown:

                        if prediction == "Switch_Tab":
                            pyautogui.hotkey("alt", "tab")
                            last_action_time = current_time

                        elif prediction == "Media_Play":
                            pyautogui.press("playpause")
                            last_action_time = current_time

                        elif prediction == "Volume_Up":
                            pyautogui.press("volumeup")
                            last_action_time = current_time

                except Exception as e:
                    print("Prediction error:", e)

        time.sleep(0.01)

    cap.release()
