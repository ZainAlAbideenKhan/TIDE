# tools/calibration/calibrator.py

class TurretCalibrator:
  def __init__(self):
    self.angle = 90  # simulated servo angle
    self.center_angle = None

    self.min_angle = 50
    self.max_angle = 130

    self.kp = 0.05

  def move_left(self, step=1):
    self.angle = max(self.min_angle, self.angle - step)

  def move_right(self, step=1):
    self.angle = min(self.max_angle, self.angle + step)

  def set_center(self):
    self.center_angle = self.angle

  def compute_angle(self, error_x):
    if self.center_angle is None:
      return self.angle

    target_angle = self.center_angle + self.kp * error_x
    target_angle = max(self.min_angle, min(self.max_angle, target_angle))
    return target_angle

  def get_state(self):
    return {
      "angle": self.angle,
      "center_angle": self.center_angle,
      "kp": self.kp,
      "min_angle": self.min_angle,
      "max_angle": self.max_angle
    }