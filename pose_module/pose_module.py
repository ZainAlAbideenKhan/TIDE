# pose_module/pose_module.py

from pose_module.preprocessing.frame_preprocessor import FramePreprocessor
from pose_module.inference.movenet_inference import MoveNetInference
from pose_module.feature_extraction.pose_features import PoseFeatureExtractor
from pose_module.temporal_aggregation.pose_aggregator import PoseAggregator

class PoseModule:
  def __init__(self, model_path):
    self.inference = MoveNetInference(model_path)
    self.extractor = PoseFeatureExtractor()
    self.aggregators = {}
    self.prev_keypoints = {}
    self.smooth_alpha = 0.6

  def smooth_keypoints(self, person_id, keypoints):
    """
    keypoints shape: [1, 1, 17, 3]  -> (y, x, confidence)
    """
    if person_id not in self.prev_keypoints:
        self.prev_keypoints[person_id] = keypoints.copy()
        return keypoints

    prev = self.prev_keypoints[person_id]
    alpha = self.smooth_alpha

    smoothed = keypoints.copy()

    for i in range(17):
        # only smooth x,y; keep confidence as-is
        smoothed[0, 0, i, 0] = alpha * keypoints[0, 0, i, 0] + (1 - alpha) * prev[0, 0, i, 0]
        smoothed[0, 0, i, 1] = alpha * keypoints[0, 0, i, 1] + (1 - alpha) * prev[0, 0, i, 1]

    self.prev_keypoints[person_id] = smoothed
    return smoothed

  def process_frame(self, frame, timestamp, person_id):
    # ---- init per-person aggregator ----
    if person_id not in self.aggregators:
      self.aggregators[person_id] = PoseAggregator()

    agg = self.aggregators[person_id]

    # ---- timing (per person, ONLY place time is handled) ----
    if agg.last_time is None:
      agg.last_time = timestamp

    delta_t = timestamp - agg.last_time
    agg.last_time = timestamp

    # ---- inference ----
    preprocessed = FramePreprocessor.preprocess(frame)
    raw_keypoints = self.inference.infer(preprocessed)
    keypoints = self.smooth_keypoints(person_id, raw_keypoints)

    # ---- feature extraction ----
    features = self.extractor.extract(keypoints)

    # ---- temporal aggregation ----
    agg.update(features, delta_t)

    # ---- interpretable pose signals ----
    pose_features = {
      "hands_bent_above_shoulders": agg.hands_bent_score > 0.9,
      "forward_leaning": agg.lean_move_score > 0.8,
      "crouch_tactical": agg.crouch_score > 0.6,
      "sudden_motion": agg.accel_score > 0.7
    }

    return {
      "person_id": person_id,
      "pose_features": pose_features,
      "pose_scores": {
        "hands_bent": agg.hands_bent_score,
        "lean_move": agg.lean_move_score,
        "crouch": agg.crouch_score,
        "accel": agg.accel_score,
        "stance": agg.stance_score
      },
      "pose_risk": agg.pose_risk(),
      "persistence_time": agg.persistence_time,
      "keypoints": keypoints,
      "timestamp": timestamp
    }
