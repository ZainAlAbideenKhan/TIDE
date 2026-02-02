# pose_module/preprocessing/frame_preprocessor.py

import cv2
import numpy as np
from pose_module.config import MODEL_INPUT_SIZE

class FramePreprocessor:
    @staticmethod
    def preprocess(frame):
        img = cv2.resize(frame, (MODEL_INPUT_SIZE, MODEL_INPUT_SIZE))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.uint8)

        img = np.expand_dims(img, axis=0)
        return img
