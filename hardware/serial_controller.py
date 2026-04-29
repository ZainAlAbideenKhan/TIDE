import serial
import time


class SerialController:
  def __init__(self, port='COM6', baudrate=9600, timeout=1):
    self.port = port
    self.baudrate = baudrate
    self.timeout = timeout
    self.ser = None

  def connect(self):
    try:
      self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
      time.sleep(2)  # allow Arduino reset
      print(f"[INFO] Connected to {self.port}")
    except serial.SerialException as e:
      print(f"[ERROR] Serial connection failed: {e}")
      self.ser = None

  def send(self, command: str):
    if self.ser and self.ser.is_open:
      try:
        message = f"{command}\n"
        self.ser.write(message.encode())
      except Exception as e:
        print(f"[ERROR] Failed to send: {e}")
    else:
      print("[WARN] Serial not connected")

  def close(self):
    if self.ser and self.ser.is_open:
      self.ser.close()
      print("[INFO] Serial connection closed")