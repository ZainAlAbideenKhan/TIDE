# pose_module/feature_extraction/pose_features.py
import numpy as np
import math

# helper
def angle(a, b, c):
    ba = a - b
    bc = c - b
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-6
    cos_angle = np.dot(ba, bc) / denom
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

def dist(a, b):
    return np.linalg.norm(a - b)

class PoseFeatureExtractor:
    def __init__(self):
        pass

    def extract(self, keypoints):
        kp = keypoints[0][0]  # shape [17,3] y,x,conf
        # convert to (x,y)
        pts = np.array([[p[1], p[0]] for p in kp])  # [x,y]

        # indices (MoveNet)
        NOSE, LS, RS, LE, RE, LW, RW, LH, RH, LK, RK = 0,5,6,7,8,9,10,11,12,13,14

        left_shoulder = pts[LS]; right_shoulder = pts[RS]
        left_elbow = pts[LE]; right_elbow = pts[RE]
        left_wrist = pts[LW]; right_wrist = pts[RW]
        left_hip = pts[LH]; right_hip = pts[RH]
        left_knee = pts[LK]; right_knee = pts[RK]

        shoulder_center = (left_shoulder + right_shoulder) / 2.0
        hip_center = (left_hip + right_hip) / 2.0

        # elbow angles (shoulder-elbow-wrist)
        left_elbow_angle = angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = angle(right_shoulder, right_elbow, right_wrist)

        # torso lean: angle between hip->shoulder and vertical vector (0,1)
        torso_vec = shoulder_center - hip_center
        vertical = np.array([0.0, 1.0])
        # compute angle between torso_vec and vertical
        torso_angle = np.degrees(
            math.acos(
                np.clip(
                    np.dot(torso_vec, vertical) / ((np.linalg.norm(torso_vec)+1e-6) * (np.linalg.norm(vertical)+1e-6)),
                    -1.0, 1.0
                )
            )
        )

        # cuff: hips vs knees vertical difference (simple)
        hip_y = hip_center[1]; knee_y = (left_knee[1] + right_knee[1]) / 2.0
        hip_knee_gap = knee_y - hip_y  # larger when standing; smaller when crouched

        # wrist relative to shoulders (y coordinate)
        left_wrist_above = left_wrist[1] < left_shoulder[1] - 0.03
        right_wrist_above = right_wrist[1] < right_shoulder[1] - 0.03

        features = {
            "left_elbow_angle": left_elbow_angle,
            "right_elbow_angle": right_elbow_angle,
            "torso_angle": torso_angle,
            "hip_knee_gap": hip_knee_gap,
            "left_wrist_above": left_wrist_above,
            "right_wrist_above": right_wrist_above,
            "shoulder_center": shoulder_center,
            "hip_center": hip_center,
            "left_wrist": left_wrist,
            "right_wrist": right_wrist
        }
        return features