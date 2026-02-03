# threat_scorer/adapters/face_adapter.py

def adapt_face_output(face_results):
    """
    Input: list from FaceRecognizer.process_frame
    Output: normalized face signal or None
    """

    if not face_results:
        return None

    # pick the face with highest risk (POC assumption)
    face = max(face_results, key=lambda x: x["risk"])

    label_map = {
        "FRIEND": "ALLY",
        "FOE": "THREAT",
        "UNKNOWN": "UNKNOWN"
    }

    adapted = {
        "face_id": face["face_id"],
        "label": label_map.get(face["label"], "UNKNOWN"),
        "risk": min(1.0, face["risk"] / 2.0),  # normalize 0–2 → 0–1
        "confidence": face["confidence"],
        "bbox": face["bbox"]
    }

    return adapted
