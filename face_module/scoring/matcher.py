# face_module/scoring/matcher.py
import numpy as np

def min_distance(embedding, db):
  if not db:
    return float("inf")
  return min(np.linalg.norm(embedding - e) for e in db)
