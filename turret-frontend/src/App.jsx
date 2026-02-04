import Turret from "./components/Turret/Turret"
import NetworkStatus from "./components/NetworkStatus/NetworkStatus"
import useSocket from "./hooks/useSocket"

export default function App() {
  const socketState = useSocket()

  return (
    <>
      <Turret socketState={socketState} />
      <NetworkStatus socketState={socketState} />
    </>
  )
}
