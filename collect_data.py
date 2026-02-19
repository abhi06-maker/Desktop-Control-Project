import cv2
import mediapipe as mp
import csv
import os

def collect_gesture_data(gesture_name):

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

    cap = cv2.VideoCapture(0)

    count = 0

    data_dir = "data"
    csv_path = os.path.join(data_dir, "gestures_data.csv")
    image_dir = os.path.join(data_dir, "images", gesture_name)

    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    print("\n📸 Manual Gesture Capture Mode")
    print("👉 Hand rectangle ke andar rakho")
    print("👉 'C' dabao → capture")
    print("👉 'Q' dabao → finish\n")

    # ROI rectangle coordinates
    x1, y1 = 150, 100
    x2, y2 = 450, 400

    while True:
        success, img = cap.read()
        if not success:
            print("❌ Camera error")
            break

        img = cv2.flip(img, 1)

        # Draw rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        roi = img[y1:y2, x1:x2]
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        results = hands.process(roi_rgb)

        cv2.putText(img, f"Captured: {count}",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0), 2)

        cv2.putText(img, f"Gesture: {gesture_name}",
                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (255, 255, 255), 2)

        cv2.putText(img, "Press 'C' to Capture | 'Q' to Quit",
                    (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (200, 200, 200), 2)

        key = cv2.waitKey(1) & 0xFF

        # -------- CAPTURE WHEN C PRESSED --------
        if key == ord('c'):

            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:

                    landmarks = []
                    for lm in hand_lms.landmark:
                        landmarks.extend([lm.x, lm.y])

                    landmarks.append(gesture_name)

                    # Save CSV
                    with open(csv_path, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(landmarks)

                    # Save ROI image
                    img_path = os.path.join(image_dir, f"img_{count+1}.jpg")
                    cv2.imwrite(img_path, roi)

                    count += 1
                    print(f"✅ Captured sample {count}")

            else:
                print("⚠ No hand detected inside rectangle!")

        # -------- EXIT --------
        if key == ord('q'):
            break

        cv2.imshow("Gesture Capture", img)

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n🎉 Finished! Total samples collected: {count}")


if __name__ == "__main__":
    name = input("Enter gesture name: ")
    collect_gesture_data(name)
