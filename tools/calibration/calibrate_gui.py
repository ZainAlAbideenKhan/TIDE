# tools/calibration/calibrate_gui.py

import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from tools.calibration.calibrator import TurretCalibrator
from tools.calibration.save_load import save_config

from hardware.serial_controller import SerialController
from hardware.turret_controller import TurretController

# -------------------------
# INIT
# -------------------------
calibrator = TurretCalibrator()
cap = cv2.VideoCapture(0)

serial_ctrl = SerialController(port='COM6')
serial_ctrl.connect()

turret = TurretController(serial_ctrl)
angle = max(50, min(130, int(calibrator.angle)))
turret.set_angle(angle)

# -------------------------
# TKINTER SETUP
# -------------------------
root = tk.Tk()
root.title("Turret Calibration Tool")

frame = ttk.Frame(root)
frame.pack()

video_label = tk.Label(frame)
video_label.grid(row=0, column=0, columnspan=3)

# -------------------------
# CONTROL FUNCTIONS
# -------------------------
def move_left():
  calibrator.move_left()
  turret.set_angle(int(calibrator.angle))
  update_labels()

def move_right():
  calibrator.move_right()
  turret.set_angle(int(calibrator.angle))
  update_labels()

def set_center():
  calibrator.set_center()
  update_labels()

def save_calibration():
  if calibrator.center_angle is None:
    print("[ERROR] Set center before saving!")
    return

  data = calibrator.get_state()
  save_config(data)
  print("Calibration saved!")

def update_kp(val):
  calibrator.kp = float(val)
  update_labels()

# -------------------------
# LABELS
# -------------------------
angle_label = tk.Label(frame, text="Angle: 0")
angle_label.grid(row=1, column=0)

center_label = tk.Label(frame, text="Center: None")
center_label.grid(row=1, column=1)

kp_label = tk.Label(frame, text="KP: 0.05")
kp_label.grid(row=1, column=2)

def update_labels():
  angle_label.config(text=f"Angle: {calibrator.angle}")
  center_label.config(text=f"Center: {calibrator.center_angle}")
  kp_label.config(text=f"KP: {calibrator.kp:.3f}")

# -------------------------
# BUTTONS
# -------------------------
btn_left = ttk.Button(frame, text="LEFT", command=move_left)
btn_left.grid(row=2, column=0)

btn_center = ttk.Button(frame, text="SET CENTER", command=set_center)
btn_center.grid(row=2, column=1)

btn_right = ttk.Button(frame, text="RIGHT", command=move_right)
btn_right.grid(row=2, column=2)

btn_save = ttk.Button(frame, text="SAVE", command=save_calibration)
btn_save.grid(row=3, column=1)

# -------------------------
# KP SLIDER
# -------------------------
kp_slider = ttk.Scale(frame, from_=0.001, to=0.2, orient="horizontal", command=update_kp)
kp_slider.set(calibrator.kp)
kp_slider.grid(row=4, column=0, columnspan=3, sticky="we")

# -------------------------
# VIDEO LOOP
# -------------------------
def update_frame():
  ret, frame_cv = cap.read()
  if not ret:
    root.after(10, update_frame)
    return

  h, w, _ = frame_cv.shape

  # Draw crosshair (center)
  cx, cy = w // 2, h // 2
  cv2.line(frame_cv, (cx - 20, cy), (cx + 20, cy), (0, 255, 0), 2)
  cv2.line(frame_cv, (cx, cy - 20), (cx, cy + 20), (0, 255, 0), 2)

  # Simulated target (center for now)
  target_x, target_y = cx, cy
  cv2.circle(frame_cv, (target_x, target_y), 5, (0, 0, 255), -1)

  # Show angle on frame
  cv2.putText(frame_cv, f"Angle: {calibrator.angle}",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
        0.7, (255, 255, 255), 2)

  frame_rgb = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)
  img = Image.fromarray(frame_rgb)
  imgtk = ImageTk.PhotoImage(image=img)

  video_label.imgtk = imgtk
  video_label.configure(image=imgtk)

  root.after(10, update_frame)

# -------------------------
# START
# -------------------------
update_labels()
update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
serial_ctrl.close()