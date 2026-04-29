from hardware.serial_controller import SerialController
from hardware.turret_controller import TurretController
import time

PORT = 'COM6'
serial_ctrl = SerialController(port=PORT)
serial_ctrl.connect()

turret = TurretController(serial_ctrl)

try:
  while True:
    cmd = input("Enter command (angle/fire/move/quit): ")

    if cmd == "quit":
      break

    elif cmd.startswith("angle"):
      angle = int(cmd.split()[1])
      turret.set_angle(angle)

    elif cmd == "fire on":
      turret.fire(True)

    elif cmd == "fire off":
      turret.fire(False)

    elif cmd == "move on":
      turret.set_movement(True)

    elif cmd == "move off":
      turret.set_movement(False)

except KeyboardInterrupt:
  pass

finally:
  serial_ctrl.close()