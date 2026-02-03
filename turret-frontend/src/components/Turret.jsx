export default function Turret({ yaw, pitch, status = "READY" }) {
  const clampedYaw = Math.max(-75, Math.min(75, yaw));
  const clampedPitch = Math.max(-10, Math.min(45, pitch));

  const getDangerLevel = () => {
    const yawStress = Math.abs(clampedYaw) / 75;
    const pitchStress = Math.abs(clampedPitch) / 45;
    return Math.max(yawStress, pitchStress);
  };

  const dangerLevel = getDangerLevel();
  const isActive = Math.abs(yaw) > 5 || Math.abs(pitch) > 5;

  return (
    <div className="relative">
      {/* Main viewport with CRT screen effect */}
      <div className="relative w-[800px] h-[600px] bg-black rounded-lg overflow-hidden border-4 border-zinc-800 shadow-2xl">
        {/* CRT screen curvature simulation */}
        <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-black/40 pointer-events-none z-50" />

        {/* Scanlines overlay */}
        <div className="absolute inset-0 pointer-events-none z-40 opacity-20">
          <div
            className="w-full h-full"
            style={{
              backgroundImage:
                "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 255, 150, 0.03) 2px, rgba(0, 255, 150, 0.03) 4px)",
            }}
          />
        </div>

        {/* Animated scan line */}
        <div className="absolute inset-0 pointer-events-none z-40 overflow-hidden">
          <div className="w-full h-1 bg-gradient-to-b from-transparent via-cyan-400/40 to-transparent animate-crt-scan" />
        </div>

        {/* RGB color separation effect on edges */}
        <div className="absolute inset-0 pointer-events-none z-30 opacity-30">
          <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-r from-red-500/20 to-transparent" />
          <div className="absolute top-0 right-0 w-2 h-full bg-gradient-to-l from-blue-500/20 to-transparent" />
        </div>

        {/* Main content area */}
        <div className="relative w-full h-full p-8 flex items-center justify-center">
          {/* Background radar sweep */}
          <div className="absolute inset-0 flex items-center justify-center">
            <svg
              className="w-[500px] h-[500px] animate-pulse-slow"
              viewBox="0 0 200 200"
            >
              {/* Concentric circles */}
              {[90, 75, 60, 45, 30].map((r, i) => (
                <circle
                  key={r}
                  cx="100"
                  cy="100"
                  r={r}
                  fill="none"
                  stroke="rgba(0, 255, 150, 0.15)"
                  strokeWidth="0.5"
                  style={{
                    animation: `pulse ${2 + i * 0.5}s ease-in-out infinite`,
                    animationDelay: `${i * 0.1}s`,
                  }}
                />
              ))}

              {/* Crosshair lines */}
              <line
                x1="0"
                y1="100"
                x2="200"
                y2="100"
                stroke="rgba(0, 255, 150, 0.2)"
                strokeWidth="0.5"
              />
              <line
                x1="100"
                y1="0"
                x2="100"
                y2="200"
                stroke="rgba(0, 255, 150, 0.2)"
                strokeWidth="0.5"
              />

              {/* Diagonal guides */}
              <line
                x1="30"
                y1="30"
                x2="170"
                y2="170"
                stroke="rgba(0, 255, 150, 0.1)"
                strokeWidth="0.3"
                strokeDasharray="2,2"
              />
              <line
                x1="170"
                y1="30"
                x2="30"
                y2="170"
                stroke="rgba(0, 255, 150, 0.1)"
                strokeWidth="0.3"
                strokeDasharray="2,2"
              />

              {/* Rotating radar sweep */}
              <g className="origin-center animate-radar-sweep">
                <line
                  x1="100"
                  y1="100"
                  x2="100"
                  y2="10"
                  stroke="url(#radarGradient)"
                  strokeWidth="2"
                />
              </g>

              <defs>
                <linearGradient
                  id="radarGradient"
                  x1="0%"
                  y1="0%"
                  x2="0%"
                  y2="100%"
                >
                  <stop offset="0%" stopColor="rgba(0, 255, 150, 0.8)" />
                  <stop offset="100%" stopColor="rgba(0, 255, 150, 0)" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {/* Angle guide markers */}
          <div className="absolute inset-0 flex items-center justify-center">
            {[-75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75].map((angle) => (
              <div
                key={`angle-${angle}`}
                className="absolute h-[450px] w-[1px] origin-bottom"
                style={{
                  transform: `rotate(${angle}deg)`,
                  background:
                    angle === 0
                      ? "rgba(0, 255, 150, 0.4)"
                      : angle % 30 === 0
                        ? "rgba(0, 255, 150, 0.2)"
                        : "rgba(0, 255, 150, 0.08)",
                }}
              >
                {angle % 30 === 0 && (
                  <div
                    className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] text-cyan-400/60 font-mono"
                    style={{ transform: `rotate(${-angle}deg)` }}
                  >
                    {angle}°
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Central turret assembly */}
          <div
            className="relative transition-transform duration-100 ease-out"
            style={{
              transform: `rotate(${clampedYaw}deg)`,
              filter: `
                drop-shadow(0 0 ${15 + dangerLevel * 25}px rgba(0, 255, 150, ${0.6 + dangerLevel * 0.4}))
                drop-shadow(0 0 ${30 + dangerLevel * 40}px rgba(0, 255, 150, ${0.3 + dangerLevel * 0.3}))
              `,
            }}
          >
            {/* Base platform glow */}
            <div
              className="absolute -bottom-8 left-1/2 -translate-x-1/2 w-40 h-12 bg-cyan-500/20 rounded-full blur-xl"
              style={{
                animation: isActive ? "pulse 1s ease-in-out infinite" : "none",
              }}
            />

            {/* Base platform */}
            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-36 h-10 bg-gradient-to-b from-cyan-600/40 to-cyan-800/60 rounded-full border-2 border-cyan-400/40" />

            {/* Horizontal base turret */}
            <img
              src="/assets/turret/gun.png"
              className="w-[450px] select-none pointer-events-none relative z-10"
              draggable="false"
              alt="Turret base"
              style={{
                filter: "drop-shadow(0 4px 20px rgba(0, 255, 150, 0.3))",
              }}
            />

            {/* Vertical gun barrel */}
            <img
              src="/assets/turret/gun_vertical.png"
              className="
                absolute
                left-0
                top-0
                w-[450px]
                origin-[20%_60%]
                transition-transform
                duration-100
                ease-out
                select-none
                pointer-events-none
                relative
                z-20
              "
              style={{
                transform: `rotate(${-clampedPitch}deg)`,
                filter: "drop-shadow(0 4px 20px rgba(0, 255, 150, 0.4))",
              }}
              alt="Turret barrel"
            />

            {/* Muzzle flash effect */}
            {isActive && (
              <div
                className="absolute w-12 h-12 rounded-full animate-pulse-fast"
                style={{
                  left: "75%",
                  top: "42%",
                  transform: `rotate(${-clampedPitch}deg) translateX(120px)`,
                  background:
                    "radial-gradient(circle, rgba(255, 200, 0, 0.8) 0%, rgba(255, 100, 0, 0.4) 50%, transparent 100%)",
                  boxShadow: "0 0 30px rgba(255, 200, 0, 0.6)",
                }}
              />
            )}

            {/* Energy rings around barrel pivot */}
            <div className="absolute left-[20%] top-[60%] -translate-x-1/2 -translate-y-1/2">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="absolute w-8 h-8 border-2 border-cyan-400/30 rounded-full"
                  style={{
                    animation: `expandFade ${2 + i * 0.5}s ease-out infinite`,
                    animationDelay: `${i * 0.6}s`,
                  }}
                />
              ))}
            </div>
          </div>

          {/* Dynamic crosshair */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-30">
            <div className="relative w-48 h-48">
              {/* Center dot */}
              <div className="absolute top-1/2 left-1/2 w-3 h-3 bg-cyan-400 rounded-full -translate-x-1/2 -translate-y-1/2 animate-pulse-fast shadow-lg shadow-cyan-400/50" />

              {/* Crosshair arms with animation */}
              {[0, 90, 180, 270].map((rotation) => (
                <div
                  key={rotation}
                  className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
                  style={{
                    transform: `translate(-50%, -50%) rotate(${rotation}deg)`,
                  }}
                >
                  <div className="flex items-center">
                    <div className="w-12 h-[2px] bg-gradient-to-r from-cyan-400 to-transparent animate-crosshair-pulse" />
                  </div>
                </div>
              ))}

              {/* Rotating outer ring */}
              <div
                className="absolute inset-0 border-2 border-cyan-400/30 rounded-full animate-spin-slow"
                style={{
                  clipPath: "polygon(0 0, 100% 0, 100% 10%, 0 10%)",
                }}
              />

              {/* Corner brackets */}
              {[
                [0, 0],
                [0, 100],
                [100, 0],
                [100, 100],
              ].map(([x, y], i) => (
                <div
                  key={i}
                  className="absolute w-8 h-8"
                  style={{
                    [y === 0 ? "top" : "bottom"]: 0,
                    [x === 0 ? "left" : "right"]: 0,
                  }}
                >
                  <div
                    className="w-full h-full border-cyan-400/60"
                    style={{
                      borderWidth: "2px",
                      borderTopWidth: y === 0 ? "2px" : "0",
                      borderBottomWidth: y === 100 ? "2px" : "0",
                      borderLeftWidth: x === 0 ? "2px" : "0",
                      borderRightWidth: x === 100 ? "2px" : "0",
                    }}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top-left HUD elements */}
        <div className="absolute top-4 left-4 space-y-3 font-mono z-40">
          {/* Status indicator */}
          <div className="flex items-center gap-3 bg-black/80 px-4 py-2 border-2 border-cyan-400/40 backdrop-blur-sm rounded">
            <div
              className={`w-3 h-3 rounded-sm ${
                status === "READY"
                  ? "bg-cyan-400 animate-pulse-slow"
                  : status === "ACTIVE"
                    ? "bg-yellow-400 animate-pulse-fast"
                    : "bg-red-400 animate-pulse-fast"
              } shadow-lg`}
              style={{
                boxShadow:
                  status === "READY"
                    ? "0 0 10px rgba(0, 255, 255, 0.8)"
                    : status === "ACTIVE"
                      ? "0 0 10px rgba(255, 255, 0, 0.8)"
                      : "0 0 10px rgba(255, 0, 0, 0.8)",
              }}
            />
            <span className="text-cyan-300 text-sm tracking-widest font-bold">
              {status}
            </span>
          </div>

          {/* System online */}
          <div className="bg-black/80 px-4 py-2 border-2 border-cyan-400/40 backdrop-blur-sm rounded">
            <div className="text-cyan-300 text-xs tracking-wider">
              TRACKING SYSTEM
            </div>
            <div className="text-cyan-400 text-sm font-bold tracking-widest mt-1">
              █ ONLINE
            </div>
          </div>
        </div>

        {/* Top-right stress monitor */}
        <div className="absolute top-4 right-4 font-mono z-40">
          <div className="bg-black/80 px-4 py-3 border-2 border-cyan-400/40 backdrop-blur-sm rounded min-w-[180px]">
            <div className="text-cyan-300/60 text-[10px] tracking-widest mb-2">
              SYSTEM LOAD
            </div>
            <div className="space-y-2">
              {["SERVO-A", "SERVO-B", "GYRO"].map((label, i) => (
                <div key={label} className="flex items-center gap-2">
                  <span className="text-cyan-400/70 text-[10px] w-16">
                    {label}
                  </span>
                  <div className="flex-1 h-2 bg-zinc-900 border border-cyan-400/30 overflow-hidden">
                    <div
                      className="h-full transition-all duration-300"
                      style={{
                        width: `${Math.min(100, dangerLevel * 100 + i * 10)}%`,
                        background:
                          dangerLevel > 0.7
                            ? "linear-gradient(90deg, #ef4444, #dc2626)"
                            : dangerLevel > 0.4
                              ? "linear-gradient(90deg, #f59e0b, #d97706)"
                              : "linear-gradient(90deg, #06b6d4, #0891b2)",
                        boxShadow: "0 0 10px currentColor",
                      }}
                    />
                  </div>
                  <span className="text-cyan-400 text-[10px] tabular-nums w-8">
                    {Math.round(Math.min(100, dangerLevel * 100 + i * 10))}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom telemetry displays */}
      <div className="mt-6 flex gap-4 justify-center font-mono">
        {/* Yaw display */}
        <div className="relative bg-black border-3 border-cyan-400/40 backdrop-blur-sm rounded overflow-hidden min-w-[280px]">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-shimmer" />

          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-[9px] text-cyan-300/60 tracking-[0.2em]">
                AZIMUTH
              </div>
              <div className="flex gap-1">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 h-1 bg-cyan-400/60 animate-pulse-slow"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>

            <div className="flex items-baseline gap-3 mb-3">
              <span
                className={`text-4xl font-bold tabular-nums tracking-tight ${
                  Math.abs(clampedYaw) > 60
                    ? "text-red-400 animate-pulse-fast"
                    : Math.abs(clampedYaw) > 40
                      ? "text-yellow-400"
                      : "text-cyan-300"
                }`}
                style={{
                  textShadow: "0 0 20px currentColor",
                }}
              >
                {clampedYaw > 0 ? "+" : ""}
                {clampedYaw.toFixed(1)}
              </span>
              <span className="text-lg text-cyan-400/70">DEG</span>
            </div>

            {/* Visual bar */}
            <div className="relative h-3 bg-zinc-900 border border-cyan-400/30 overflow-hidden mb-2">
              <div
                className="absolute top-0 h-full w-1 bg-cyan-400 transition-all duration-100"
                style={{
                  left: `${((clampedYaw + 75) / 150) * 100}%`,
                  boxShadow: "0 0 10px rgba(0, 255, 255, 0.8)",
                }}
              />
              <div className="absolute top-0 left-1/2 h-full w-[2px] bg-cyan-400/20" />
            </div>

            <div className="flex justify-between text-[9px] text-cyan-400/50">
              <span>-75°</span>
              <span>0°</span>
              <span>+75°</span>
            </div>
          </div>
        </div>

        {/* Pitch display */}
        <div className="relative bg-black border-3 border-cyan-400/40 backdrop-blur-sm rounded overflow-hidden min-w-[280px]">
          <div
            className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-shimmer"
            style={{ animationDelay: "0.5s" }}
          />

          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-[9px] text-cyan-300/60 tracking-[0.2em]">
                ELEVATION
              </div>
              <div className="flex gap-1">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 h-1 bg-cyan-400/60 animate-pulse-slow"
                    style={{ animationDelay: `${0.5 + i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>

            <div className="flex items-baseline gap-3 mb-3">
              <span
                className={`text-4xl font-bold tabular-nums tracking-tight ${
                  clampedPitch > 35 || clampedPitch < -5
                    ? "text-red-400 animate-pulse-fast"
                    : clampedPitch > 25
                      ? "text-yellow-400"
                      : "text-cyan-300"
                }`}
                style={{
                  textShadow: "0 0 20px currentColor",
                }}
              >
                {clampedPitch > 0 ? "+" : ""}
                {clampedPitch.toFixed(1)}
              </span>
              <span className="text-lg text-cyan-400/70">DEG</span>
            </div>

            {/* Visual bar */}
            <div className="relative h-3 bg-zinc-900 border border-cyan-400/30 overflow-hidden mb-2">
              <div
                className="absolute top-0 h-full w-1 bg-cyan-400 transition-all duration-100"
                style={{
                  left: `${((clampedPitch + 10) / 55) * 100}%`,
                  boxShadow: "0 0 10px rgba(0, 255, 255, 0.8)",
                }}
              />
              <div className="absolute top-0 left-[18.18%] h-full w-[2px] bg-cyan-400/20" />
            </div>

            <div className="flex justify-between text-[9px] text-cyan-400/50">
              <span>-10°</span>
              <span>0°</span>
              <span>+45°</span>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes crt-scan {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }
        
        @keyframes radar-sweep {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes expandFade {
          0% {
            transform: scale(0.5);
            opacity: 0.8;
          }
          100% {
            transform: scale(3);
            opacity: 0;
          }
        }
        
        @keyframes crosshair-pulse {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
        
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .animate-crt-scan {
          animation: crt-scan 8s linear infinite;
        }
        
        .animate-radar-sweep {
          animation: radar-sweep 4s linear infinite;
          transform-origin: 100px 100px;
        }
        
        .animate-pulse-fast {
          animation: pulse 0.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        .animate-pulse-slow {
          animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        .animate-spin-slow {
          animation: spin 8s linear infinite;
        }
        
        .animate-crosshair-pulse {
          animation: crosshair-pulse 2s ease-in-out infinite;
        }
        
        .animate-shimmer {
          animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
