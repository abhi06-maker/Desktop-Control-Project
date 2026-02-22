import cv2
import mediapipe as mp
import pickle
import pyautogui
import os
import time
import json
from collections import deque

MODEL_PATH = "data/gesture_model.pkl"
MAPPING_PATH = "data/mapping.json"


# ================= LOAD MAPPING =================
def load_mapping():
    try:
        with open(MAPPING_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(" Mapping load failed:", e)
        return {}


# ================= MAIN ENGINE =================
def run_gesture_engine(shared_state, get_frame):


    # ---- Model Check ----
    if not os.path.exists(MODEL_PATH):
        shared_state["status"] = "Error: Model file missing."
        return

    try:
        with open(MODEL_PATH, "rb") as f:
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

    # ====== SMOOTHING ======
    pred_buffer = deque(maxlen=5)

    # ====== ACTION CONTROL ======
    last_action_time = 0
    action_cooldown = 1.2
    last_triggered_action = None

    shared_state["status"] = "System Operational"

    # ================= MAIN LOOP =================
    while True:
        img = get_frame()

        if img is None:
            time.sleep(0.01)
            continue

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:

                # ===== LANDMARKS =====
                landmarks = []
                for lm in hand_lms.landmark:
                    landmarks.extend([lm.x, lm.y])

                try:
                    # ===== RAW PRED =====
                    raw_pred = model.predict([landmarks])[0]
                    pred_buffer.append(raw_pred)

                    # ===== SMOOTHED PRED =====
                    if len(pred_buffer) == pred_buffer.maxlen:
                        prediction = max(set(pred_buffer), key=pred_buffer.count)
                    else:
                        prediction = raw_pred

                    shared_state["last_gesture"] = prediction
                    print("Prediction:", prediction)

                    
                    mapping = load_mapping()
                    action = mapping.get(prediction)

                    print("Mapped Action:", action)

                    current_time = time.time()

                    # ===== TRIGGER LOGIC =====
                    if (
                        action
                        and action != last_triggered_action
                        and current_time - last_action_time > action_cooldown
                    ):
                        print(" TRIGGERING ACTION:", action)

                        if action == "alt_tab":
                            pyautogui.hotkey("alt", "tab")

                        elif action == "play_pause":
                            pyautogui.press("playpause")

                        elif action == "volume_up":
                            pyautogui.press("volumeup")

                        last_action_time = current_time
                        last_triggered_action = action

                except Exception as e:
                    print("Prediction error:", e)

        else:
            
            last_triggered_action = None

        time.sleep(0.01)

