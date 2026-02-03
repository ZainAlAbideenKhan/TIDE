# face_module/db/preprocess.py
import cv2

def crop_face(frame, x, y, w, h):
    face = frame[y:y+h, x:x+w]
    if face.size == 0:
        return None
    return cv2.resize(face, (160, 160))
