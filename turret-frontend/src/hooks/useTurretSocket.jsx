import { useEffect, useState, useRef } from "react";

export default function useTurretSocket(url = "ws://192.168.1.10:8080") {
  const [yaw, setYaw] = useState(0);
  const [pitch, setPitch] = useState(0);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    let isSubscribed = true;

    const connect = () => {
      if (!isSubscribed) return;

      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("✓ WebSocket connected");
          if (isSubscribed) {
            setConnected(true);
          }
        };

        ws.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);

            if (typeof data.yaw === "number" && isSubscribed) {
              setYaw(data.yaw);
            }

            if (typeof data.pitch === "number" && isSubscribed) {
              setPitch(data.pitch);
            }
          } catch (err) {
            console.error("Failed to parse message:", err);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
        };

        ws.onclose = () => {
          console.log("✗ WebSocket disconnected");
          if (isSubscribed) {
            setConnected(false);
            // Attempt to reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
              if (isSubscribed) {
                console.log("Attempting to reconnect...");
                connect();
              }
            }, 3000);
          }
        };
      } catch (err) {
        console.error("Failed to create WebSocket:", err);
        if (isSubscribed) {
          setConnected(false);
          // Retry connection
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isSubscribed) {
              connect();
            }
          }, 3000);
        }
      }
    };

    connect();

    return () => {
      isSubscribed = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  return { yaw, pitch, connected };
}
