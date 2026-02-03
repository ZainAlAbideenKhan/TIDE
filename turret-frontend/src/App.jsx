import Turret from "./components/Turret";
import useTurretSocket from "./hooks/useTurretSocket";
import { useState, useEffect } from "react";

export default function App() {
  const { yaw, pitch, connected } = useTurretSocket();
  const [status, setStatus] = useState("STANDBY");
  const [time, setTime] = useState(new Date());
  const [bootComplete, setBootComplete] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    setTimeout(() => setBootComplete(true), 1500);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!connected) {
      setStatus("OFFLINE");
    } else if (Math.abs(yaw) > 50 || Math.abs(pitch) > 30) {
      setStatus("ACTIVE");
    } else if (Math.abs(yaw) > 5 || Math.abs(pitch) > 5) {
      setStatus("TRACKING");
    } else {
      setStatus("READY");
    }
  }, [yaw, pitch, connected]);

  if (!bootComplete) {
    return (
      <div className="w-screen h-screen bg-black flex items-center justify-center p-15">
        <div className="text-center space-y-6 ">
          <div className="text-cyan-400 text-2xl font-mono tracking-widest animate-pulse">
            INITIALIZING TURRET CONTROL SYSTEM
          </div>
          <div className="flex justify-center gap-2">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="w-3 h-3 bg-cyan-400 rounded-sm animate-pulse"
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-screen h-screen bg-black relative overflow-hidden p-14">
      {/* Animated background grid */}
      <div className="absolute inset-0">
        <div
          className="absolute inset-0 opacity-15"
          style={{
            backgroundImage: `
              linear-gradient(rgba(0, 255, 255, 0.15) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 255, 255, 0.15) 1px, transparent 1px)
            `,
            backgroundSize: "50px 50px",
            animation: "gridMove 20s linear infinite",
          }}
        />
      </div>

      {/* Radial vignette */}
      <div className="absolute inset-0 bg-gradient-radial from-transparent via-black/30 to-black/80" />

      {/* Top command bar */}
      <div className="absolute top-0 left-0 right-0 h-16 bg-gradient-to-b from-black/95 to-transparent backdrop-blur-md border-b-2 border-cyan-400/30 z-40">
        <div className="h-full flex items-center justify-between px-6 max-w-[1800px] mx-auto">
          {/* Left - System ID */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 bg-cyan-400/10 border-2 border-cyan-400 flex items-center justify-center">
                <div className="absolute -top-1 -right-1 w-2 h-2 bg-cyan-400 rounded-sm animate-pulse-fast" />
              </div>
            </div>

            <div>
              <h1
                className="text-2xl font-black tracking-[0.3em] text-cyan-300"
                style={{
                  fontFamily: "Orbitron, sans-serif",
                  textShadow: "0 0 20px rgba(0, 255, 255, 0.5)",
                }}
              >
                AW//SYSTEM
              </h1>
              <div className="text-[9px] text-cyan-400/60 tracking-[0.2em] font-mono">
                AUTONOMOUS WEAPONS PLATFORM v4.2.1
              </div>
            </div>
          </div>

          {/* Center - Connection Status */}
          <div className="flex items-center gap-3">
            <div
              className={`relative px-5 py-2 font-mono text-xs border-2 ${
                connected
                  ? "bg-cyan-400/10 border-cyan-400 text-cyan-300"
                  : "bg-red-500/10 border-red-500 text-red-400 animate-pulse"
              }`}
            >
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  {[...Array(4)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-1 ${connected ? "bg-cyan-400" : "bg-red-400"}`}
                      style={{
                        height: `${(i + 1) * 5}px`,
                        opacity: connected ? 1 : i < 2 ? 1 : 0.3,
                      }}
                    />
                  ))}
                </div>
                <span className="tracking-widest font-bold text-xs">
                  {connected ? "UPLINK ACTIVE" : "SIGNAL LOST"}
                </span>
              </div>
              {connected && (
                <div className="absolute inset-0 border-2 border-cyan-400 animate-pulse-slow opacity-50" />
              )}
            </div>
          </div>

          {/* Right - Time */}
          <div className="text-right font-mono">
            <div
              className="text-xl tracking-widest text-cyan-300 font-bold"
              style={{
                textShadow: "0 0 10px rgba(0, 255, 255, 0.5)",
              }}
            >
              {time.toLocaleTimeString("en-US", {
                hour12: false,
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              })}
            </div>
            <div className="text-[9px] text-cyan-400/60 tracking-[0.15em]">
              {time
                .toLocaleDateString("en-US", {
                  day: "2-digit",
                  month: "short",
                  year: "numeric",
                })
                .toUpperCase()}
            </div>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-shimmer" />
      </div>

      {/* Main content area */}
      <div className="relative z-10 w-full h-full flex flex-col items-center justify-center pt-16 pb-20">
        <Turret yaw={yaw} pitch={pitch} status={status} />
      </div>

      {/* Bottom status bar */}
      <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-black/95 to-transparent backdrop-blur-md border-t-2 border-cyan-400/30 z-40">
        <div className="h-full flex items-center justify-between px-6 max-w-[1000px] mx-auto">
          {/* Left - System telemetry */}
          <div className="flex gap-3 font-mono text-xs">
            {[
              { label: "RANGE", value: "150m", icon: "◈" },
              { label: "CALIBER", value: "12.7mm", icon: "◉" },
              { label: "ROUNDS", value: "250", icon: "◙" },
              { label: "POWER", value: "98%", icon: "◆" },
            ].map((item) => (
              <div
                key={item.label}
                className="bg-black/60 px-3 py-2 border border-cyan-400/30 backdrop-blur-sm"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-cyan-400 text-xs">{item.icon}</span>
                  <span className="text-cyan-300/60 text-[8px] tracking-wider">
                    {item.label}
                  </span>
                </div>
                <div className="text-cyan-300 font-bold tracking-wider text-sm">
                  {item.value}
                </div>
              </div>
            ))}
          </div>

          {/* Center - Status Messages */}
          <div className="flex-1 flex justify-center px-6">
            {!connected && (
              <div className="flex items-center gap-2 px-5 py-2 bg-red-500/20 border-2 border-red-500 animate-pulse">
                <div className="text-red-400 text-base">⚠</div>
                <span className="text-red-300 font-mono text-xs tracking-wider font-bold">
                  NETWORK CONNECTION INTERRUPTED
                </span>
              </div>
            )}
            {connected && (Math.abs(yaw) > 70 || Math.abs(pitch) > 40) && (
              <div className="flex items-center gap-2 px-5 py-2 bg-yellow-500/20 border-2 border-yellow-500 animate-pulse">
                <div className="text-yellow-400 text-base">⚠</div>
                <span className="text-yellow-300 font-mono text-xs tracking-wider font-bold">
                  APPROACHING MECHANICAL LIMITS
                </span>
              </div>
            )}
            {connected && Math.abs(yaw) < 70 && Math.abs(pitch) < 40 && (
              <div className="flex items-center gap-2 px-5 py-2 bg-cyan-400/10 border-2 border-cyan-400/40">
                <div className="text-cyan-400 text-base">✓</div>
                <span className="text-cyan-300 font-mono text-xs tracking-wider">
                  ALL SYSTEMS OPERATIONAL
                </span>
              </div>
            )}
          </div>

          {/* Right - Coordinates */}
          <div className="bg-black/60 px-4 py-2 border-2 border-cyan-400/40 backdrop-blur-sm font-mono text-xs">
            <div className="text-cyan-300/60 text-[8px] tracking-widest mb-1">
              POSITION
            </div>
            <div className="text-cyan-300 tabular-nums tracking-wider font-bold">
              {yaw >= 0 ? "+" : ""}
              {yaw.toFixed(2)}° × {pitch >= 0 ? "+" : ""}
              {pitch.toFixed(2)}°
            </div>
          </div>
        </div>

        <div
          className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-shimmer"
          style={{ animationDelay: "1s" }}
        />
      </div>

      {/* Corner UI elements - smaller */}
      <div className="absolute top-16 left-0 w-32 h-32 border-l-2 border-t-2 border-cyan-400/20 pointer-events-none z-30">
        <div className="absolute top-3 left-3 w-1.5 h-1.5 bg-cyan-400 animate-pulse-slow" />
      </div>
      <div className="absolute top-16 right-0 w-32 h-32 border-r-2 border-t-2 border-cyan-400/20 pointer-events-none z-30">
        <div
          className="absolute top-3 right-3 w-1.5 h-1.5 bg-cyan-400 animate-pulse-slow"
          style={{ animationDelay: "0.5s" }}
        />
      </div>
      <div className="absolute bottom-20 left-0 w-32 h-32 border-l-2 border-b-2 border-cyan-400/20 pointer-events-none z-30">
        <div
          className="absolute bottom-3 left-3 w-1.5 h-1.5 bg-cyan-400 animate-pulse-slow"
          style={{ animationDelay: "1s" }}
        />
      </div>
      <div className="absolute bottom-20 right-0 w-32 h-32 border-r-2 border-b-2 border-cyan-400/20 pointer-events-none z-30">
        <div
          className="absolute bottom-3 right-3 w-1.5 h-1.5 bg-cyan-400 animate-pulse-slow"
          style={{ animationDelay: "1.5s" }}
        />
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        
        @keyframes gridMove {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .animate-shimmer {
          animation: shimmer 3s ease-in-out infinite;
        }
        
        .animate-pulse-fast {
          animation: pulse 0.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        .animate-pulse-slow {
          animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
    </div>
  );
}
