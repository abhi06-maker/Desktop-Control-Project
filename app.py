from flask import Flask, render_template, jsonify, request
import threading
from model_trainer import train_model
from collect_data import collect_gesture_data
from gesture_engine import run_gesture_engine

app = Flask(__name__)

# ---- Shared State ----
system_state = {
    "last_gesture": "Waiting...",
    "status": "System Operational",
    "is_retraining": False
}


# ---- Start Gesture Engine ----
def start_engine():
    thread = threading.Thread(target=run_gesture_engine, args=(system_state,))
    thread.daemon = True
    thread.start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start_capture", methods=["POST"])
def start_capture():
    gesture_name = request.json.get("name", "New_Gesture")
    thread = threading.Thread(target=collect_gesture_data, args=(gesture_name,))
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
        return jsonify({"status": "Retrain Failed"})



@app.route("/get_status")
def get_status():
    return jsonify(system_state)


if __name__ == "__main__":
    # 🔥 IMPORTANT: start engine before app.run
    start_engine()

    app.run(port=5000, debug=False, use_reloader=False)
