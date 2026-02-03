# threat_scorer/adapters/pose_adapter.py

def adapt_pose_output(pose_output):
    """
    Input: PoseModule.process_frame output
    """

    if pose_output is None:
        return None

    return {
        "person_id": pose_output.get("person_id", 0),
        "risk": pose_output.get("pose_risk", 0.0),
        "persistence": pose_output.get("persistence_time", 0.0),
        "keypoints": pose_output.get("keypoints")  # for skeleton drawing
    }
