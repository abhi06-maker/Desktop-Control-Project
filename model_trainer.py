import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os


# ==============================
# DATA AUGMENTATION FUNCTION
# ==============================
def augment_landmarks(X, y, times=2):
    """
    Create augmented landmark data by adding:
    - Gaussian noise
    - Scaling
    - Shifting
    """
    X_aug = []
    y_aug = []

    for _ in range(times):
        for landmarks, label in zip(X.values, y.values):

            pts = np.array(landmarks, dtype=float)

            # ---- Noise ----
            noise = np.random.normal(0, 0.01, pts.shape)
            pts_noise = pts + noise

            # ---- Scale ----
            scale = np.random.uniform(0.9, 1.1)
            pts_scale = pts * scale

            # ---- Shift ----
            shift = np.random.uniform(-0.02, 0.02, pts.shape)
            pts_shift = pts + shift

            X_aug.extend([pts_noise, pts_scale, pts_shift])
            y_aug.extend([label, label, label])

    return np.array(X_aug), np.array(y_aug)


# ==============================
# TRAIN MODEL FUNCTION
# ==============================
def train_model():
    """
    One-click retraining pipeline:
    - Load CSV data
    - Apply augmentation
    - Train RandomForest
    - Save model
    """

    data_path = "data/gestures_data.csv"
    model_dir = "data"
    model_path = os.path.join(model_dir, "gesture_model.pkl")

    # Ensure folder exists
    os.makedirs(model_dir, exist_ok=True)

    # ---------- CHECK DATA ----------
    if not os.path.exists(data_path):
        return False, "❌ No gesture data found. Capture gestures first."

    try:
        # ---------- LOAD DATA ----------
        df = pd.read_csv(data_path, header=None)

        X = df.iloc[:, :-1]   # landmarks
        y = df.iloc[:, -1]    # labels

        print(f"📊 Original samples: {len(X)}")

        # ---------- AUGMENT DATA ----------
        X_aug, y_aug = augment_landmarks(X, y, times=2)

        print(f"✨ Augmented samples created: {len(X_aug)}")

        # Combine original + augmented
        X_final = np.vstack([X.values, X_aug])
        y_final = np.hstack([y.values, y_aug])

        print(f"🚀 Total training samples: {len(X_final)}")

        # ---------- TRAIN MODEL ----------
        clf = RandomForestClassifier(
            n_estimators=150,
            max_depth=None,
            random_state=42,
            n_jobs=-1
        )

        clf.fit(X_final, y_final)

        # ---------- SAVE MODEL ----------
        with open(model_path, "wb") as f:
            pickle.dump(clf, f)

        print("✅ Model trained & saved successfully!")

        return True, "Model retrained with data augmentation."

    except Exception as e:
        return False, f"❌ Training failed: {str(e)}"


# ==============================
# RUN DIRECTLY
# ==============================
if __name__ == "__main__":
    success, msg = train_model()
    print(msg)
