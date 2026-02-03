# state_machine/states.py

from enum import Enum

class SystemState(Enum):
  MONITORING = "MONITORING"
  EVALUATING = "EVALUATING"
  DECISION_LOCKED = "DECISION_LOCKED"
  RESET = "RESET"
