import "./NetworkStatus.css"

export default function NetworkStatus({ socketState }) {
  const { connected, lockedOut, reconnect } = socketState

  if (!connected && !lockedOut) {
    return (
      <div className="network-overlay">
        <div className="network-card">
          <p>Reconnecting…</p>
        </div>
      </div>
    )
  }
  

  return (
    <div className="network-overlay">
      <div className="network-card">
        <h3>Network Disconnected</h3>

        {lockedOut ? (
          <button onClick={reconnect}>Connect to Network</button>
        ) : (
          <p>Attempting reconnection…</p>
        )}
      </div>
    </div>
  )
}
