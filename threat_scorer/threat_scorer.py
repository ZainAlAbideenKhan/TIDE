# threat_scorer/threat_scorer.py

from threat_scorer.config import W_FACE, W_POSE, POSE_FOE_MULTIPLIER

class ThreatScorer:
  def score(self, face, pose):
    """
    face: adapted face signal or None
    pose: adapted pose signal or None
    """

    face_risk = face["risk"] if face else 0.0
    pose_risk = pose["risk"] if pose else 0.0

    # Rule 1: Ally suppresses everything
    if face and face["label"] == "ALLY":
      return {
        "threat_score": 0.0,
        "components": {
          "face": face_risk,
          "pose": pose_risk
        }
      }

    # Rule 2: FOE amplifies pose
    pose_multiplier = (
      POSE_FOE_MULTIPLIER
      if face and face["label"] == "THREAT"
      else 1.0
    )

    raw_score = (
      W_FACE * face_risk +
      W_POSE * (pose_risk * pose_multiplier)
    )

    return {
      "threat_score": min(1.0, raw_score),
      "components": {
        "face": face_risk,
        "pose": pose_risk
      }
    }
