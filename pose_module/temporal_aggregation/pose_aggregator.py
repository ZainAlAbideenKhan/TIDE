# pose_module/temporal_aggregation/pose_aggregator.py
from pose_module.config import DECAY_FACTOR
import math

# weights (tunable)
WEIGHTS = {
    "hands_bent": 0.35,
    "lean_move": 0.30,
    "crouch": 0.15,
    "accel": 0.15,
    "stance": 0.05
}

class PoseAggregator:
    def __init__(self):
        self.hands_bent_score = 0.0
        self.lean_move_score = 0.0
        self.crouch_score = 0.0
        self.accel_score = 0.0
        self.stance_score = 0.0
        self.persistence_time = 0.0
        self.last_shoulder = None
        self.last_time = None
        self.last_velocity = 0.0

    def update(self, features, delta_t):
        # decay
        self.hands_bent_score *= DECAY_FACTOR
        self.lean_move_score *= DECAY_FACTOR
        self.crouch_score *= DECAY_FACTOR
        self.accel_score *= DECAY_FACTOR
        self.stance_score *= DECAY_FACTOR

        # hands bent detection
        hands_above = features["left_wrist_above"] and features["right_wrist_above"]
        elbow_bent = (features["left_elbow_angle"] < 115.0) and (features["right_elbow_angle"] < 115.0)
        if hands_above and elbow_bent:
            self.hands_bent_score += 1.0

        # crouch detection: hip_knee_gap small -> crouch
        if features["hip_knee_gap"] < 0.06:   # tune per camera
            self.crouch_score += 0.9

        # torso lean & motion: compute forward velocity
        if self.last_shoulder is not None and delta_t > 0:
            cur = features["shoulder_center"]
            dx = cur - self.last_shoulder
            speed = (dx[1]**2 + dx[0]**2)**0.5 / delta_t
        else:
            speed = 0.0

        # forward lean: torso_angle > 18 deg and forward speed > 0.15
        if features["torso_angle"] > 18.0 and speed > 0.12:
            self.lean_move_score += 1.2

        # acceleration: compare last velocity
        accel = abs(speed - self.last_velocity) / (delta_t + 1e-6)
        if accel > 0.5:
            self.accel_score += 1.5

        # stance: hands near hips and feet distance wide (low weight)
        # simple: wrist-hip distance
        lw = features["left_wrist"]; rw = features["right_wrist"]; hip = features["hip_center"]
        if (math.hypot(lw[0]-hip[0], lw[1]-hip[1]) < 0.06 and math.hypot(rw[0]-hip[0], rw[1]-hip[1]) < 0.06):
            self.stance_score += 0.3

        # suppression: if both elbows nearly straight and speed low, subtract
        if features["left_elbow_angle"] > 150 and features["right_elbow_angle"] > 150 and speed < 0.05:
            # strong suppression so casual standing/waving doesn't flag
            self.hands_bent_score = max(0.0, self.hands_bent_score - 0.8)
            self.lean_move_score = max(0.0, self.lean_move_score - 0.4)

        # update temporal markers
        self.persistence_time += delta_t
        self.last_shoulder = features["shoulder_center"]
        self.last_velocity = speed

    def pose_risk(self):
        score = (
            WEIGHTS["hands_bent"] * self.hands_bent_score +
            WEIGHTS["lean_move"] * self.lean_move_score +
            WEIGHTS["crouch"] * self.crouch_score +
            WEIGHTS["accel"] * self.accel_score +
            WEIGHTS["stance"] * self.stance_score
        )
        return score
