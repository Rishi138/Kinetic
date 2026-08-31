import { useEffect, useRef, useState } from 'react'
import SeverityBar from './SeverityBar'
import TrendChart from './TrendChart'
import './App.css'

const FRAME_WS_URL = 'ws://localhost:8000/view'
const DATA_WS_URL = 'ws://localhost:8000/view_data'

function App() {
  const imgRef = useRef(null)
  const [connected, setConnected] = useState(false)
  const [dataCycle, setDataCycle] = useState([])

  // frame stream
  useEffect(() => {
    const ws = new WebSocket(FRAME_WS_URL)
    ws.binaryType = 'arraybuffer'

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)

    ws.onmessage = (event) => {
      const blob = new Blob([event.data], { type: 'image/jpeg' })
      const url = URL.createObjectURL(blob)

      if (imgRef.current) {
        const prevUrl = imgRef.current.dataset.currentUrl
        imgRef.current.src = url
        imgRef.current.dataset.currentUrl = url
        if (prevUrl) URL.revokeObjectURL(prevUrl)
      }
    }

    return () => ws.close()
  }, [])

  // data_cycle stream
  useEffect(() => {
    const ws = new WebSocket(DATA_WS_URL)

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data)
        setDataCycle(parsed)
      } catch (e) {
        // ignore malformed frames
      }
    }

    return () => ws.close()
  }, [])

  return (
    <div className="app">
      <div className="stream-pane">
        <img ref={imgRef} alt="live feed" className="stream-video" />
        <div className="status-row">
          <span className={`status-dot ${connected ? 'status-dot--live' : ''}`} />
          <span className="status-label">{connected ? 'live' : 'disconnected'}</span>
        </div>
      </div>

      <div className="data-pane">
        <div className="data-pane__header">metrics</div>

        {dataCycle.length === 0 && (
          <div className="data-empty">no signal</div>
        )}

        {dataCycle.map((entry, i) => (
          <div className="metric-block" key={i}>
            <div className="metric-title">{entry.title}</div>
            <div className="metric-rows">
              {entry.labels.map((label, j) => (
                <div className="metric-row" key={j}>
                  <div className="metric-row__top">
                    <span className="metric-label">{label}</span>
                    <span className="metric-value">{String(entry.display[j])}</span>
                  </div>
                  {entry.scale_pos && entry.bands && (
                    <SeverityBar
                      scalePos={entry.scale_pos[j]}
                      bands={entry.bands}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="trend-pane">
        <div className="data-pane__header">session trend</div>

        {dataCycle.length === 0 && (
          <div className="data-empty">no signal</div>
        )}

        {dataCycle.map((entry, i) =>
          entry.curr_session_trend && entry.bands ? (
            <TrendChart
              key={i}
              title={entry.title}
              series={entry.curr_session_trend}
              bands={entry.bands}
              seriesLabels={entry.labels}
            />
          ) : null
        )}
      </div>
    </div>
  )
}

export default App
