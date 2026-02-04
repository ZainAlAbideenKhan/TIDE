# gui/status_panel.py

import tkinter as tk
from gui.config import FONT_TEXT, FONT_TITLE
from gui.theme import THEME

class StatusPanel(tk.Frame):
  def __init__(self, parent):
    super().__init__(
        parent,
        bg=THEME["panel"],
        bd=3,
        relief="ridge"
      )

    # ---- STATE BANNER ----
    self.state_banner = tk.Label(
      self,
      text="MONITORING",
      font=("Courier", 18, "bold"),
      width=30,
      height=2,
      bg=THEME["monitor"],
      fg="black"
    )
    self.state_banner.pack(fill="x", pady=5)

    # ---- INFO LABELS ----
    self.threat = tk.Label(self, font=("Courier", 12), bg=THEME["panel"], fg=THEME["text"])
    self.face = tk.Label(self, font=("Courier", 12), bg=THEME["panel"], fg=THEME["text"])
    self.pose = tk.Label(self, font=("Courier", 12), bg=THEME["panel"], fg=THEME["text"])
    self.gun = tk.Label(self, font=("Courier", 12), bg=THEME["panel"], fg=THEME["text"])
    self.source = tk.Label(self, font=("Courier", 12), bg=THEME["panel"], fg=THEME["text"])

    for lbl in [self.threat, self.face, self.pose, self.gun, self.source]:
      lbl.pack(anchor="w", padx=10, pady=2)

  def update(self, data):
    state = data["state"]

    # ---- STATE COLOR ----
    if state == "MONITORING":
      bg = THEME["monitor"]
    elif state == "EVALUATING":
      bg = THEME["evaluate"]
    else:
      bg = THEME["locked"]

    self.state_banner.config(text=state, bg=bg)

    score = data.get("threat_score")
    score_text = f"{score:.2f}" if isinstance(score, (int, float)) else "--"

    self.threat.config(text=f"Threat Score : {score_text}")
    self.face.config(text=f"Face Status  : {data['face_label']}")
    self.pose.config(text=f"Pose Risk    : {data['pose_risk_label']}")
    self.gun.config(text=f"Gun Status   : {data['gun_status']}")
    self.source.config(text=f"Target Src  : {data['target_source']}")
