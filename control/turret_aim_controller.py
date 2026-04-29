class TurretAimController:
  def __init__(self, calibration_config):
    self.center_angle = calibration_config["center_angle"]
    self.kp = calibration_config["kp"]
    self.min_angle = calibration_config["min_angle"]
    self.max_angle = calibration_config["max_angle"]

    # Internal state
    self.current_angle = self.center_angle
    self.previous_angle = self.center_angle

    # Tunable parameters (important)
    self.alpha = calibration_config.get("alpha", 0.2)  # smoothing factor
    self.dead_zone = calibration_config.get("dead_zone", 10)  # pixels
    self.min_step = calibration_config.get("min_step", 0.2)  # degrees

  def clamp(self, angle):
    return max(self.min_angle, min(self.max_angle, angle))

  def update(self, target_x, frame_width):
    if target_x is None:
      return self.current_angle  # no target → hold position

    center_x = frame_width / 2
    error_x = target_x - center_x

    # --- DEAD ZONE ---
    if abs(error_x) < self.dead_zone:
      return self.current_angle

    # --- PROPORTIONAL CONTROL ---
    delta = self.kp * error_x
    new_angle = self.current_angle + delta

    # --- CLAMP ---
    new_angle = self.clamp(new_angle)

    # --- SMOOTHING (EXPONENTIAL) ---
    smoothed_angle = (
      self.alpha * new_angle +
      (1 - self.alpha) * self.previous_angle
    )

    # --- MINIMUM STEP CHECK ---
    if abs(smoothed_angle - self.current_angle) < self.min_step:
      return self.current_angle

    # Update state
    self.previous_angle = smoothed_angle
    self.current_angle = smoothed_angle

    return self.current_angle