# state_machine/state_machine.py

import time
from state_machine.states import SystemState
from state_machine.config import SOFT_THRESHOLD, HARD_THRESHOLD, CONFIRM_TIME

class StateMachine:
  def __init__(self):
    self.state = SystemState.MONITORING
    self.eval_start_time = None
    self.locked_target = None
    self.locked_score = None

  def update(self, threat_data, user_action=None, target_lost=False):
    """
    threat_data: output from ThreatModule.update()
    user_action: None | "FIRE" | "IGNORE"
    target_lost: bool
    """

    score = threat_data["threat_score"]
    current_time = time.time()

    # ---------------- MONITORING ----------------
    if self.state == SystemState.MONITORING:
      if score >= SOFT_THRESHOLD:
        self.state = SystemState.EVALUATING
        self.eval_start_time = current_time

    # ---------------- EVALUATING ----------------
    elif self.state == SystemState.EVALUATING:
      if score < SOFT_THRESHOLD:
        self.state = SystemState.MONITORING
        self.eval_start_time = None

      elif score >= HARD_THRESHOLD:
        elapsed = current_time - self.eval_start_time
        if elapsed >= CONFIRM_TIME:
          self.state = SystemState.DECISION_LOCKED
          self.locked_target = threat_data
          self.locked_score = score

    # ---------------- DECISION LOCKED ----------------
    elif self.state == SystemState.DECISION_LOCKED:
      if user_action in ("FIRE", "IGNORE") or target_lost:
        self.state = SystemState.RESET

    # ---------------- RESET ----------------
    elif self.state == SystemState.RESET:
      self._reset()
      self.state = SystemState.MONITORING

    return self._state_output(threat_data)

  def _reset(self):
    self.eval_start_time = None
    self.locked_target = None
    self.locked_score = None

  def _state_output(self, threat_data):
    """
    Output for GUI / control panel
    """

    return {
      "state": self.state.value,
      "threat_score": (
        self.locked_score
        if self.state == SystemState.DECISION_LOCKED
        else threat_data["threat_score"]
      ),
      "face_bbox": threat_data.get("face_bbox"),
      "pose_keypoints": threat_data.get("pose_keypoints"),
      "controls_enabled": self.state == SystemState.DECISION_LOCKED
    }
