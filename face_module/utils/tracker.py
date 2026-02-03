# face_module/utils/tracker.py
class IDTracker:
  def __init__(self):
    self._id = 0
  def next(self):
    i = self._id
    self._id += 1
    return i
