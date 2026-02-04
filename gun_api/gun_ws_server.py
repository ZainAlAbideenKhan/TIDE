import asyncio
import json
import websockets
import threading
import time

class GunWebSocketServer:
  def __init__(self, host="127.0.0.1", port=8080):
    self.host = host
    self.port = port

    self.screen_w = None
    self.screen_h = None

    self.client = None
    self.loop = None

    self.running = False

  # ---------------- PUBLIC API ----------------

  def start(self):
    """
    Start WebSocket server in a background thread.
    """
    if self.running:
      return

    self.running = True
    thread = threading.Thread(target=self._run, daemon=True)
    thread.start()

  def send_target(self, img_x, img_y, frame_w, frame_h):
    """
    Send target coordinates to frontend (pixel space).
    Safe to call anytime.
    """
    if not self.client:
      return
    if self.screen_w is None or self.screen_h is None:
      return

    try:
      screen_x = int(img_x / frame_w * self.screen_w)
      screen_y = int(img_y / frame_h * self.screen_h)

      msg = json.dumps({
        "x": screen_x,
        "y": screen_y
      })

      asyncio.run_coroutine_threadsafe(
        self.client.send(msg),
        self.loop
      )

    except Exception:
      # NEVER crash
      pass

  # ---------------- INTERNAL ----------------

  def _run(self):
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)
    self.loop.run_until_complete(self._serve())

  async def _serve(self):
    async with websockets.serve(self._handler, self.host, self.port):
      print(f"[GUN API] WebSocket server running on ws://{self.host}:{self.port}")
      while self.running:
        await asyncio.sleep(1)

  async def _handler(self, websocket):
    print("[GUN API] Frontend connected")
    self.client = websocket

    try:
      async for message in websocket:
        self._handle_message(message)
    except Exception:
      pass
    finally:
      print("[GUN API] Frontend disconnected")
      self.client = None

  def _handle_message(self, message):
    """
    Handle incoming JSON messages safely.
    """
    try:
      data = json.loads(message)
      if not isinstance(data, dict):
        return

      if "screen" in data:
        screen = data["screen"]
        if "w" in screen and "h" in screen:
          self.screen_w = int(screen["w"])
          self.screen_h = int(screen["h"])
          print(f"[GUN API] Screen set: {self.screen_w}x{self.screen_h}")

    except Exception:
      # Ignore bad JSON
      pass
