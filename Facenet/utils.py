import cv2
import os
import time

# ===== INPUT =====
name = input("Enter name: ").strip()

# ===== OUTPUT DIR =====
output_dir = f"dataset/good/{name}"
os.makedirs(output_dir, exist_ok=True)

# ===== OPEN CAMERA =====
cap = cv2.VideoCapture(0)  # 0 = default camera

if not cap.isOpened():
    print("❌ Cannot access camera")
    exit()

print("🎥 Camera started... Recording for 5 seconds")
start_time = time.time()

img_count = 1
frame_interval = 1  # save 1 frame per second
last_saved = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    elapsed = time.time() - start_time

    # Show live camera
    cv2.imshow("Recording (Press Q to stop)", frame)

    # Save 1 frame per second
    if int(elapsed) > last_saved:
        img_path = os.path.join(output_dir, f"{img_count}.png")
        cv2.imwrite(img_path, frame)
        print(f"✅ Saved {img_path}")
        img_count += 1
        last_saved = int(elapsed)

    # Stop after 5 seconds
    if elapsed >= 5:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("🎉 Done! Images saved successfully.")
