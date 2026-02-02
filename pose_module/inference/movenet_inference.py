# pose_module/inference/movenet_inference.py

import numpy as np
import tensorflow as tf

class MoveNetInference:
    def __init__(self, model_path):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def infer(self, input_tensor):
        self.interpreter.set_tensor(
            self.input_details[0]['index'], input_tensor
        )
        self.interpreter.invoke()
        keypoints = self.interpreter.get_tensor(
            self.output_details[0]['index']
        )
        return keypoints
