
#   pip install fastapi uvicorn --break-system-packages
#   python server.py

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

# Set of currently-connected browser viewers
viewers: set[WebSocket] = set()


@app.websocket("/main_cv")
async def cv_socket(websocket: WebSocket):
    await websocket.accept()
    print("[server] cv connected")
    try:
        while True:
            frame_bytes = await websocket.receive_bytes()
            # broadcast to every connected viewer, drop any that fail
            dead = []
            for viewer in viewers:
                try:
                    await viewer.send_bytes(frame_bytes)
                except Exception:
                    dead.append(viewer)
            for d in dead:
                viewers.discard(d)
    except WebSocketDisconnect:
        print("[server] cv disconnected")


@app.websocket("/view")
async def view_socket(websocket: WebSocket):
    """Browsers connect here to receive the frame stream."""
    await websocket.accept()
    viewers.add(websocket)
    print(f"[server] viewer connected ({len(viewers)} total)")
    try:
        while True:
            # we don't expect messages from the viewer, just keep the
            # connection alive until it disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        viewers.discard(websocket)
        print(f"[server] viewer disconnected ({len(viewers)} total)")


uvicorn.run(app, host="0.0.0.0", port=8000)
