# gui/video_panel.py

import cv2
from PIL import Image, ImageTk
import tkinter as tk

class VideoPanel(tk.Label):
  def __init__(self, parent):
    super().__init__(parent)
    self.image = None

  def update_frame(self, frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    self.configure(image=imgtk)
    self.image = imgtk
