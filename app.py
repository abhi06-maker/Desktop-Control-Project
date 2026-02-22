import cv2
import mediapipe as mp
import time
import json
from flask import Flask, render_template, jsonify, request, Response
import threading

from model_trainer import train_model
from collect_data import collect_gesture_data
from gesture_engine import run_gesture_engine

# ================= GLOBAL CAMERA =================
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camera_lock = threading.Lock()
latest_frame = None

# ================= PATHS =================
MAPPING_PATH = "data/mapping.json"

app = Flask(__name__)

# ================= SHARED STATE =================
system_state = {
    "last_gesture": "Waiting...",
    "status": "System Operational",
    "is_retraining": False
}

# ================= MEDIAPIPE SETUP =================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands_cam = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ================= CAMERA READER =================
def camera_reader():
    global latest_frame

    while True:
        success, frame = camera.read()
        if not success:
            time.sleep(0.01)
            continue

        with camera_lock:
            latest_frame = frame.copy()

# ================= FRAME PROVIDER =================
def get_shared_frame():
    global latest_frame
    with camera_lock:
        if latest_frame is None:
            return None
        return latest_frame.copy()

# ================= CAMERA STREAM =================
def generate_frames():
    global latest_frame

    while True:
        if latest_frame is None:
            time.sleep(0.01)
            continue

        with camera_lock:
            frame = latest_frame.copy()

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_cam.process(rgb)

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    hand_lms,
                    mp_hands.HAND_CONNECTIONS
                )

        ret, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

# ================= START GESTURE ENGINE =================
def start_engine():
    thread = threading.Thread(
        target=run_gesture_engine,
        args=(system_state, get_shared_frame)
    )
    thread.daemon = True
    thread.start()

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/start_capture", methods=["POST"])
def start_capture():
    gesture_name = request.json.get("name", "New_Gesture")
    thread = threading.Thread(
        target=collect_gesture_data,
        args=(gesture_name,)
    )
    thread.start()
    return jsonify({"status": f"Started capturing data for {gesture_name}"})

@app.route("/retrain", methods=["POST"])
def retrain():
    system_state["is_retraining"] = True

    success, message = train_model()

    system_state["is_retraining"] = False

    if success:
        return jsonify({"status": "Model Updated Successfully!"})
    else:
        return jsonify({"status": f"Retrain Failed: {message}"})

# ✅ NEW — dynamic mapping route
@app.route("/update_mapping", methods=["POST"])
def update_mapping():
    data = request.json
    gesture = data.get("gesture")
    action = data.get("action")

    try:
        with open(MAPPING_PATH, "r") as f:
            mapping = json.load(f)
    except:
        mapping = {}

    mapping[gesture] = action

    with open(MAPPING_PATH, "w") as f:
        json.dump(mapping, f, indent=4)

    return jsonify({"status": f"Mapping updated: {gesture} → {action}"})


@app.route("/get_status")
def get_status():
    return jsonify(system_state)

# ================= MAIN =================
if __name__ == "__main__":
    # start shared camera reader
    threading.Thread(target=camera_reader, daemon=True).start()

    # start gesture engine
    start_engine()

    app.run(port=5000, debug=False, use_reloader=False)
