# threat_scorer/config.py

# Weights
W_FACE = 0.6
W_POSE = 0.4

# Pose amplification when face is FOE
POSE_FOE_MULTIPLIER = 1.2

# Threat score thresholds (used by State Machine)
SOFT_THRESHOLD = 0.3
HARD_THRESHOLD = 0.6
