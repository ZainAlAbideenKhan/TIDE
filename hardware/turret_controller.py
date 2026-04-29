class TurretController:
  def __init__(self, serial_controller):
    self.serial = serial_controller
    self.last_angle = None
    self.firing = False
    self.moving = False

  def set_angle(self, angle: int):
    angle = max(50, min(130, angle))

    if self.last_angle is None or abs(angle - self.last_angle) > 2:
      self.serial.send(f"A:{angle}")
      self.last_angle = angle

  def fire(self, on: bool):
    if on != self.firing:
      self.serial.send(f"F:{1 if on else 0}")
      self.firing = on

  def set_movement(self, on: bool):
    if on != self.moving:
      self.serial.send(f"M:{1 if on else 0}")
      self.moving = on