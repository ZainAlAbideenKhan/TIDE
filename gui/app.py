# gui/app.py

import sys, os, time, cv2, tkinter as tk

# ---- fix imports ----
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from pose_module.pose_module import PoseModule
from face_module import FaceRecognizer
from threat_scorer.threat_module import ThreatModule
from state_machine.state_machine import StateMachine

from gui.video_panel import VideoPanel
from gui.status_panel import StatusPanel
from gui.control_panel import ControlPanel
from gui.config import WINDOW_TITLE, WINDOW_SIZE
from gui.theme import THEME

# ---- init core modules ----
pose = PoseModule("pose_module/model/movenet_thunder.tflite")
face = FaceRecognizer(db_path="database")
threat = ThreatModule()
state_machine = StateMachine()

gun_status = "IDLE"
target_source = "NONE"

cap = cv2.VideoCapture(0)

# ---- GUI ----
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry(WINDOW_SIZE)

# ---- MAIN CONTAINER ----
main_frame = tk.Frame(root, bg=THEME["bg"])
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ---- LEFT: STATUS PANEL ----
status_panel = StatusPanel(main_frame)
status_panel.pack(side="left", fill="y", padx=10)

# ---- RIGHT: CAMERA PANEL ----
video_container = tk.Frame(
  main_frame,
  bg=THEME["panel"],
  bd=4,
  relief="sunken"
)
video_container.pack(side="right", fill="both", expand=True)

video_panel = VideoPanel(video_container)
video_panel.pack(padx=5, pady=5)

# ---- BOTTOM ACTION BAR ----
action_bar = tk.Frame(
  root,
  bg=THEME["panel"],
  bd=3,
  relief="ridge"
)
action_bar.pack(fill="x", padx=10, pady=10)

def on_target():
  global gun_status, target_source
  gun_status = "TRACKING"
  target_source = "OPERATOR"

def on_fire():
  global gun_status
  gun_status = "FIRING"

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

import cv2

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
  cv2.putText(
    frame,
    label,
    (x1, y1 - 8),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    color,
    2
  )

def draw_skeleton(frame, keypoints, conf_thresh=0.4):
  """
  Draw stick-man skeleton using MoveNet keypoints
  keypoints shape: [1, 1, 17, 3] -> (y, x, confidence)
  """

  if keypoints is None:
    return

  h, w, _ = frame.shape
  kp = keypoints[0][0]  # MoveNet output

  # ---- MoveNet keypoint indices ----
  NOSE = 0
  LEFT_EYE = 1
  RIGHT_EYE = 2
  LEFT_EAR = 3
  RIGHT_EAR = 4
  LEFT_SHOULDER = 5
  RIGHT_SHOULDER = 6
  LEFT_ELBOW = 7
  RIGHT_ELBOW = 8
  LEFT_WRIST = 9
  RIGHT_WRIST = 10
  LEFT_HIP = 11
  RIGHT_HIP = 12
  LEFT_KNEE = 13
  RIGHT_KNEE = 14
  LEFT_ANKLE = 15
  RIGHT_ANKLE = 16

  # ---- Skeleton connections (bones) ----
  SKELETON = [
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_SHOULDER, LEFT_ELBOW),
    (LEFT_ELBOW, LEFT_WRIST),
    (RIGHT_SHOULDER, RIGHT_ELBOW),
    (RIGHT_ELBOW, RIGHT_WRIST),

    (LEFT_SHOULDER, LEFT_HIP),
    (RIGHT_SHOULDER, RIGHT_HIP),
    (LEFT_HIP, RIGHT_HIP),

    (LEFT_HIP, LEFT_KNEE),
    (LEFT_KNEE, LEFT_ANKLE),
    (RIGHT_HIP, RIGHT_KNEE),
    (RIGHT_KNEE, RIGHT_ANKLE)
  ]

  # ---- Draw joints ----
  for y, x, c in kp:
    if c > conf_thresh:
      cx, cy = int(x * w), int(y * h)
      cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)

  # ---- Draw bones ----
  for i, j in SKELETON:
    y1, x1, c1 = kp[i]
    y2, x2, c2 = kp[j]

    if c1 > conf_thresh and c2 > conf_thresh:
      p1 = (int(x1 * w), int(y1 * h))
      p2 = (int(x2 * w), int(y2 * h))
      cv2.line(frame, p1, p2, (0, 255, 0), 2)

# ---- main loop ----
def update():
  global gun_status, target_source

  ret, frame = cap.read()
  if not ret:
    root.after(10, update)
    return

  ts = time.time()

  pose_out = pose.process_frame(frame, ts, person_id=0)
  face_out = face.process_frame(frame)
  threat_data = threat.update(face_out, pose_out)

  state_data = state_machine.update(threat_data)

  if state_data["state"] == "DECISION_LOCKED":
    gun_status = "TRACKING"
    target_source = "AI"

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

  # ---- draw face bounding box ----
  draw_face_bbox(
    frame,
    threat_data.get("face_bbox"),
    threat_data.get("face_label")
  )
  # draw pose skeleton
  draw_skeleton(
    frame,
    threat_data.get("pose_keypoints")
  )
  video_panel.update_frame(frame)
  root.after(10, update)

update()
root.mainloop()

cap.release()