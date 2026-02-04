import { useEffect, useRef, useState } from "react"
import GunView from "./GunView"
import gunSide from "../../assets/gun_side.png"
import gunTop from "../../assets/gun_top.png"
import "./Turret.css"

const YAW_MIN = -75
const YAW_MAX = 75
const PITCH_MIN = -10
const PITCH_MAX = 45

const clamp = (v, min, max) => Math.min(Math.max(v, min), max)
const lerp = (a, b, t) => a + (b - a) * t

function xToYaw(x, w) {
  const normalized = (x / w) * 2 - 1
  return clamp(normalized * YAW_MAX, YAW_MIN, YAW_MAX)
}

function yToPitch(y, h) {
  const normalized = 1 - y / h
  return clamp(normalized * PITCH_MAX, PITCH_MIN, PITCH_MAX)
}

export default function Turret({ socketState }) {
  const [yaw, setYaw] = useState(0)
  const [pitch, setPitch] = useState(0)

  const targetYaw = useRef(0)
  const targetPitch = useRef(0)

  const screen = useRef({
    w: window.innerWidth,
    h: window.innerHeight
  })

  useEffect(() => {
    if (!socketState.lastMessage) return
  
    let msg
    try {
      msg = JSON.parse(socketState.lastMessage)
    } catch {
      return
    }
  
    if (msg.screen?.w && msg.screen?.h) {
      screen.current.w = Math.max(1, msg.screen.w)
      screen.current.h = Math.max(1, msg.screen.h)
    }
  
    if (Number.isFinite(msg.x)) {
      targetYaw.current = xToYaw(
        clamp(msg.x, 0, screen.current.w),
        screen.current.w
      )
    }
  
    if (Number.isFinite(msg.y)) {
      targetPitch.current = yToPitch(
        clamp(msg.y, 0, screen.current.h),
        screen.current.h
      )
    }
  }, [socketState.lastMessage])
  
  useEffect(() => {
    if (!socketState.connected) {
      targetYaw.current = yaw
      targetPitch.current = pitch
    }
  }, [socketState.connected])
  
  useEffect(() => {
    let running = true
  
    const update = () => {
      if (!running) return
      setYaw(y => lerp(y, targetYaw.current, 0.18))
      setPitch(p => lerp(p, targetPitch.current, 0.18))
      requestAnimationFrame(update)
    }
  
    update()
    return () => { running = false }
  }, [])
  

  // Smooth animation loop
  useEffect(() => {
    let rafId

    const update = () => {
      setYaw(y => lerp(y, targetYaw.current, 0.18))
      setPitch(p => lerp(p, targetPitch.current, 0.18))
      rafId = requestAnimationFrame(update)
    }

    update()
    return () => cancelAnimationFrame(rafId)
  }, [])

  return (
    <div className="turret-stage">

      <GunView
        image={gunTop}
        className="gun top-view"
        style={{
          transform: `translateX(-50%) rotate(${yaw}deg)`
        }}
      />

      <GunView
        image={gunSide}
        className="gun side-view"
        style={{
          transform: `translateX(-50%) rotate(${pitch}deg)`
        }}
      />

    </div>
  )
}
