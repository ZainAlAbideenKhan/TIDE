# tools/calibration/save_load.py

import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
CONFIG_PATH = os.path.join(BASE_DIR, "calibration", "turret_config.json")


def save_config(data):
  os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

  with open(CONFIG_PATH, "w") as f:
    json.dump(data, f, indent=4)

  print(f"[INFO] Saved calibration to: {CONFIG_PATH}")


def load_config():
  if not os.path.exists(CONFIG_PATH):
    return None

  with open(CONFIG_PATH, "r") as f:
    return json.load(f)