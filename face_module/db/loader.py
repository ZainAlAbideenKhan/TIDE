# face_module/db/loader.py
import os
import cv2
from face_module.models.facenet import get_embedding
from face_module.db.preprocess import crop_face
from face_module.vision.detector import detect_faces

def load_embeddings(db_path):
  friend, foe = [], []

  for label in ["friend", "foe"]:
    base = os.path.join(db_path, label)
    if not os.path.isdir(base):
      continue

    for person in os.listdir(base):
      person_dir = os.path.join(base, person)
      for file in os.listdir(person_dir):
        if not file.lower().endswith((".jpg", ".png")):
          continue

        img = cv2.imread(os.path.join(person_dir, file))
        if img is None:
          continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray)
        if len(faces) == 0:
          continue

        x, y, w, h = faces[0]
        face = crop_face(img, x, y, w, h)
        if face is None:
          continue

        emb = get_embedding(face)

        (friend if label == "friend" else foe).append(emb)

  return friend, foe
