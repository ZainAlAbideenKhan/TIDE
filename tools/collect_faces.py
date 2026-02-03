import cv2
import os
import time

DB_PATH = "database"

cascade = cv2.CascadeClassifier(
  cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def ensure_dir(path):
  os.makedirs(path, exist_ok=True)


def main():
  print("=== Face Dataset Collection Tool ===")
  role = input("Enter category (friend / foe): ").strip().lower()
  if role not in ["friend", "foe"]:
    print("❌ Invalid category")
    return

  name = input("Enter person name: ").strip()
  if not name:
    print("❌ Invalid name")
    return

  save_dir = os.path.join(DB_PATH, role, name)
  ensure_dir(save_dir)

  cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    print("❌ Camera not available")
    return

  print("\n📷 Camera started")
  print("➡ Press 'c' to capture face")
  print("➡ Press 'q' to quit\n")

  while True:
    ret, frame = cap.read()
    if not ret:
      break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
      # draw bounding box
      cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Face Collector", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("c"):
      if len(faces) == 0:
        print("⚠ No face detected")
        continue

      # take the largest face
      x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
      face = frame[y:y + h, x:x + w]

      if face.size == 0:
        print("❌ Invalid crop")
        continue

      filename = f"{int(time.time())}.jpg"
      path = os.path.join(save_dir, filename)
      cv2.imwrite(path, face)

      print(f"✅ Saved {path}")

    elif key == ord("q"):
      break

  cap.release()
  cv2.destroyAllWindows()
  print("👋 Done")


if __name__ == "__main__":
  main()
