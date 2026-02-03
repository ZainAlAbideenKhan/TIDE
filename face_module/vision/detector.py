# face_module/vision/detector.py
import cv2

cascade = cv2.CascadeClassifier(
  cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces(gray):
  return cascade.detectMultiScale(gray, 1.3, 5)
