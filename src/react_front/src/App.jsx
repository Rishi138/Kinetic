import { useEffect, useRef, useState } from 'react'
import './App.css'

const WS_URL = 'ws://localhost:8000/view'

function App() {
  const imgRef = useRef(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket(WS_URL)
    ws.binaryType = 'arraybuffer'

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)

    ws.onmessage = (event) => {
      // event.data is raw JPEG bytes for one frame
      const blob = new Blob([event.data], { type: 'image/jpeg' })
      const url = URL.createObjectURL(blob)

      if (imgRef.current) {
        // revoke the previous frame's object URL to avoid leaking memory
        const prevUrl = imgRef.current.dataset.currentUrl
        imgRef.current.src = url
        imgRef.current.dataset.currentUrl = url
        if (prevUrl) URL.revokeObjectURL(prevUrl)
      }
    }

    return () => ws.close()
  }, [])

  return (
    <div style={{ padding: '1rem', fontFamily: 'sans-serif' }}>
      <p>status: {connected ? 'connected' : 'disconnected'}</p>
      <img
        ref={imgRef}
        alt="live feed"
        style={{ maxWidth: '100%', background: '#111', minHeight: '360px' }}
      />
    </div>
  )
}

export default App
