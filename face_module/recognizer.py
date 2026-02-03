# face_module/recognizer.py
import cv2
from face_module.db.loader import load_embeddings
from face_module.models.facenet import get_embedding
from face_module.vision.detector import detect_faces
from face_module.db.preprocess import crop_face
from face_module.scoring.matcher import min_distance
from face_module.scoring.risk import confidence_from_distance, compute_risk
from face_module.config import *
from face_module.utils.tracker import IDTracker

class FaceRecognizer:
  def __init__(self, db_path):
    self.friend_db, self.foe_db = load_embeddings(db_path)
    self.tracker = IDTracker()

  def process_frame(self, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray)

    results = []

    for (x, y, w, h) in faces:
      if w < MIN_FACE_SIZE:
        continue

      face = crop_face(frame, x, y, w, h)
      if face is None:
        continue

      emb = get_embedding(face)

      fd = min_distance(emb, self.friend_db)
      od = min_distance(emb, self.foe_db)

      label = "UNKNOWN"
      dist = min(fd, od)

      if fd < FRIEND_THRESHOLD and fd < od:
        label = "FRIEND"
        dist = fd
      elif od < FOE_THRESHOLD and od < fd:
        label = "FOE"
        dist = od

      confidence = confidence_from_distance(dist)
      risk = compute_risk(label, confidence)

      results.append({
        "face_id": self.tracker.next(),
        "label": label,
        "confidence": round(confidence, 3),
        "risk": round(risk, 3),
        "bbox": [x, y, x + w, y + h]
      })

    return results
