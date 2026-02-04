import tkinter as tk
from gui.theme import THEME

class ControlPanel(tk.Frame):
  def __init__(self, parent, callbacks):
    super().__init__(
      parent,
      bg=THEME["panel"]
    )

    def make_btn(text, cmd, color=None):
      return tk.Button(
        self,
        text=text,
        width=12,
        height=2,
        font=("Courier", 12, "bold"),
        bg=color or THEME["button"],
        activebackground=THEME["button_active"],
        relief="raised",
        bd=4,
        command=cmd
      )

    btn_target = make_btn("TARGET", callbacks["target"])
    btn_fire = make_btn("FIRE", callbacks["fire"], color="#d9534f")
    btn_ignore = make_btn("IGNORE", callbacks["ignore"])
    btn_reset = make_btn("RESET", callbacks["reset"], color="#5bc0de")

    btn_target.pack(side="left", padx=15, pady=8)
    btn_fire.pack(side="left", padx=15, pady=8)
    btn_ignore.pack(side="left", padx=15, pady=8)
    btn_reset.pack(side="left", padx=15, pady=8)
