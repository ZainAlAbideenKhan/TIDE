import { useEffect, useRef, useState } from "react"

const WS_URL = "ws://127.0.0.1:8080"
const MAX_RETRIES = 5

export default function useSocket() {
  const socketRef = useRef(null)
  const retryCount = useRef(0)

  const [connected, setConnected] = useState(false)
  const [lockedOut, setLockedOut] = useState(false)
  const [lastMessage, setLastMessage] = useState(null)

  const connect = () => {
    if (lockedOut) return

    socketRef.current = new WebSocket(WS_URL)

    socketRef.current.onopen = () => {
      retryCount.current = 0
      setConnected(true)
      setLockedOut(false)
    }

    socketRef.current.onmessage = e => {
      setLastMessage(e.data)
    }

    socketRef.current.onclose = () => {
      setConnected(false)

      if (retryCount.current < MAX_RETRIES) {
        retryCount.current++
        setTimeout(connect, 1000)
      } else {
        setLockedOut(true)
      }
    }

    socketRef.current.onerror = () => {
      socketRef.current.close()
    }
  }

  useEffect(() => {
    connect()
    return () => socketRef.current?.close()
  }, [])

  return {
    connected,
    lockedOut,
    lastMessage,
    reconnect: connect
  }
}
