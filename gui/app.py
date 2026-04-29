import sys, os, time, cv2, tkinter as tk

# ---- fix imports ----
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# ---- core modules ----
from pose_module.pose_module import PoseModule
from face_module import FaceRecognizer
from threat_scorer.threat_module import ThreatModule
from state_machine.state_machine import StateMachine

# ---- GUI ----
from gui.video_panel import VideoPanel
from gui.status_panel import StatusPanel
from gui.control_panel import ControlPanel
from gui.config import WINDOW_TITLE, WINDOW_SIZE
from gui.theme import THEME

# ---- calibration + control ----
from tools.calibration.save_load import load_config
from control.turret_aim_controller import TurretAimController

# ---- hardware ----
from hardware.serial_controller import SerialController
from hardware.turret_controller import TurretController


# =========================
# INIT CORE MODULES
# =========================
pose = PoseModule("pose_module/model/movenet_thunder.tflite")
face = FaceRecognizer(db_path="database")
threat = ThreatModule()
state_machine = StateMachine()

# =========================
# LOAD CALIBRATION
# =========================
config = load_config()
if config is None or config.get("center_angle") is None:
  raise RuntimeError("[ERROR] Calibration not found. Run calibration tool first.")

controller = TurretAimController(config)

# =========================
# INIT HARDWARE
# =========================
serial_ctrl = SerialController(port='COM6')
serial_ctrl.connect()

turret = TurretController(serial_ctrl)

# =========================
# STATE
# =========================
gun_status = "IDLE"
target_source = "NONE"

# =========================
# SMOOTHING (ANTI-JITTER)
# =========================
smooth_x = None
ALPHA = 0.2

def smooth(value):
  global smooth_x

  if value is None:
    return None

  if smooth_x is None:
    smooth_x = value
  else:
    smooth_x = ALPHA * value + (1 - ALPHA) * smooth_x

  return smooth_x

cap = cv2.VideoCapture(0)

# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry(WINDOW_SIZE)

main_frame = tk.Frame(root, bg=THEME["bg"])
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

status_panel = StatusPanel(main_frame)
status_panel.pack(side="left", fill="y", padx=10)

video_container = tk.Frame(
  main_frame,
  bg=THEME["panel"],
  bd=4,
  relief="sunken"
)
video_container.pack(side="right", fill="both", expand=True)

video_panel = VideoPanel(video_container)
video_panel.pack(padx=5, pady=5)

action_bar = tk.Frame(
  root,
  bg=THEME["panel"],
  bd=3,
  relief="ridge"
)
action_bar.pack(fill="x", padx=10, pady=10)

# =========================
# CONTROL CALLBACKS
# =========================
def on_target():
  global gun_status, target_source
  gun_status = "TRACKING"
  target_source = "OPERATOR"

def on_fire():
  global gun_status
  gun_status = "FIRING"
  # trigger ON
  turret.fire(True)
  # auto reset after 1 second
  root.after(1000, lambda: turret.fire(False))

def on_ignore():
  global gun_status, target_source
  gun_status = "IDLE"
  target_source = "NONE"
  state_machine._reset()

def on_reset():
  global gun_status, target_source
  gun_status = "IDLE"
  target_source = "NONE"
  state_machine._reset()
  print("[SYSTEM] Manual reset triggered")

controls = ControlPanel(
  action_bar,
  callbacks={
    "target": on_target,
    "fire": on_fire,
    "ignore": on_ignore,
    "reset": on_reset
  }
)
controls.pack()

# =========================
# DRAWING HELPERS
# =========================
def draw_face_bbox(frame, bbox, label):
  if bbox is None:
    return

  x1, y1, x2, y2 = map(int, bbox)

  color_map = {
    "ALLY": (0, 255, 0),
    "UNKNOWN": (0, 255, 255),
    "THREAT": (0, 0, 255)
  }

  color = color_map.get(label, (255, 255, 255))

  cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
  cv2.putText(frame, label, (x1, y1 - 8),
              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def draw_skeleton(frame, keypoints, conf_thresh=0.4):
  if keypoints is None:
    return

  h, w, _ = frame.shape
  kp = keypoints[0][0]

  SKELETON = [
    (5, 6), (5, 7), (7, 9),
    (6, 8), (8, 10),
    (5, 11), (6, 12), (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16)
  ]

  for y, x, c in kp:
    if c > conf_thresh:
      cv2.circle(frame, (int(x*w), int(y*h)), 4, (0,255,255), -1)

  for i, j in SKELETON:
    y1, x1, c1 = kp[i]
    y2, x2, c2 = kp[j]
    if c1 > conf_thresh and c2 > conf_thresh:
      cv2.line(frame,
        (int(x1*w), int(y1*h)),
        (int(x2*w), int(y2*h)),
        (0,255,0), 2)

# =========================
# MAIN LOOP
# =========================
def update():
  global gun_status, target_source

  ret, frame = cap.read()
  frame = cv2.flip(frame, 1)
  if not ret:
    root.after(10, update)
    return

  ts = time.time()

  pose_out = pose.process_frame(frame, ts, person_id=0)
  face_out = face.process_frame(frame)
  threat_data = threat.update(face_out, pose_out)
  state_data = state_machine.update(threat_data)

  # ---- AUTO TARGET ----
  if state_data["state"] == "DECISION_LOCKED":
    gun_status = "TRACKING"
    target_source = "AI"

  # ---- STATUS PANEL ----
  pose_risk = threat_data["pose_risk"]
  pose_risk_label = "LOW" if pose_risk < 0.3 else "MEDIUM" if pose_risk < 0.6 else "HIGH"

  status_panel.update({
    "state": state_data["state"],
    "threat_score": state_data["threat_score"],
    "face_label": threat_data.get("face_label", "NONE"),
    "pose_risk_label": pose_risk_label,
    "gun_status": gun_status,
    "target_source": target_source
  })

  # =========================
  # TARGET → CONTROL → HARDWARE
  # =========================
  img_x = None
  h, w, _ = frame.shape

  if gun_status == "TRACKING" and threat_data.get("pose_keypoints") is not None:
    kp = threat_data["pose_keypoints"][0][0]

    ls_y, ls_x, ls_c = kp[5]
    rs_y, rs_x, rs_c = kp[6]

    if ls_c > 0.4 and rs_c > 0.4:
      img_x = ((ls_x + rs_x) / 2) * w
    else:
      n_y, n_x, n_c = kp[0]
      if n_c > 0.4:
        img_x = n_x * w

  img_x = smooth(img_x)

  # ---- CONTROL ----
  angle = controller.update(img_x, w)
  turret.set_angle(int(angle))

  # ---- FIRE LOGIC ----
  fire = (state_data["state"] == "DECISION_LOCKED")
  turret.fire(fire)

  # ---- MOVEMENT LED ----
  movement = (int(angle) != turret.last_angle)
  turret.set_movement(movement)

  # ---- DRAW ----
  draw_face_bbox(frame,
    threat_data.get("face_bbox"),
    threat_data.get("face_label"))

  draw_skeleton(frame,
    threat_data.get("pose_keypoints"))

  video_panel.update_frame(frame)

  root.after(10, update)


update()
root.mainloop()

cap.release()
serial_ctrl.close()