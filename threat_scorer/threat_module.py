# threat_scorer/threat_module.py

from threat_scorer.adapters.face_adapter import adapt_face_output
from threat_scorer.adapters.pose_adapter import adapt_pose_output
from threat_scorer.threat_scorer import ThreatScorer

class ThreatModule:
  def __init__(self):
    self.scorer = ThreatScorer()

  def update(self, face_results, pose_output):
    """
    face_results: output from FaceRecognizer.process_frame
    pose_output: output from PoseModule.process_frame
    """

    face = adapt_face_output(face_results)
    pose = adapt_pose_output(pose_output)

    score_data = self.scorer.score(face, pose)

    return {
      "threat_score": score_data["threat_score"],
      "components": score_data["components"],

      # ---- passthrough for GUI ----
      "face_bbox": face["bbox"] if face else None,
      "face_label": face["label"] if face else None,
      "pose_keypoints": pose["keypoints"] if pose else None,

      # ---- debug / trace ----
      "face_risk": face["risk"] if face else 0.0,
      "pose_risk": pose["risk"] if pose else 0.0
    }
