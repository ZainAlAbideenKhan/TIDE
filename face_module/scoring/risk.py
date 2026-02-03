# face_module/scoring/risk.py
from face_module.config import *

def confidence_from_distance(dist):
  return max(0.0, min(1.0, 1.0 - dist / MAX_DIST))

def compute_risk(label, confidence):
  if label == "FRIEND":
    return 0.0
  if label == "UNKNOWN":
    return UNKNOWN_BASE + UNKNOWN_SPREAD * (1 - confidence)
  if label == "FOE":
    return FOE_BASE + FOE_SPREAD * confidence
