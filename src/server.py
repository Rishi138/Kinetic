#   pip install fastapi uvicorn --break-system-packages
#   python server.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

# Browsers connected for frames / data respectively
frame_viewers: set[WebSocket] = set()
data_viewers: set[WebSocket] = set()


async def _broadcast_bytes(payload: bytes, viewers: set[WebSocket]):
    dead = []
    for viewer in viewers:
        try:
            await viewer.send_bytes(payload)
        except Exception:
            dead.append(viewer)
    for d in dead:
        viewers.discard(d)


async def _broadcast_text(payload: str, viewers: set[WebSocket]):
    dead = []
    for viewer in viewers:
        try:
            await viewer.send_text(payload)
        except Exception:
            dead.append(viewer)
    for d in dead:
        viewers.discard(d)


@app.websocket("/main_cv")
async def cv_frame_socket(websocket: WebSocket):
    """main_cv connects here and pushes JPEG frame bytes."""
    await websocket.accept()
    print("[server] main_cv (frames) connected")
    try:
        while True:
            frame_bytes = await websocket.receive_bytes()
            await _broadcast_bytes(frame_bytes, frame_viewers)
    except WebSocketDisconnect:
        print("[server] main_cv (frames) disconnected")


@app.websocket("/main_cv_data")
async def cv_data_socket(websocket: WebSocket):
    """main_cv connects here and pushes data_cycle JSON."""
    await websocket.accept()
    print("[server] main_cv (data) connected")
    try:
        while True:
            data_text = await websocket.receive_text()
            await _broadcast_text(data_text, data_viewers)
    except WebSocketDisconnect:
        print("[server] main_cv (data) disconnected")


@app.websocket("/view")
async def view_frame_socket(websocket: WebSocket):
    """Browsers connect here to receive the frame stream."""
    await websocket.accept()
    frame_viewers.add(websocket)
    print(f"[server] frame viewer connected ({len(frame_viewers)} total)")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        frame_viewers.discard(websocket)
        print(f"[server] frame viewer disconnected ({len(frame_viewers)} total)")


@app.websocket("/view_data")
async def view_data_socket(websocket: WebSocket):
    """Browsers connect here to receive the data_cycle stream."""
    await websocket.accept()
    data_viewers.add(websocket)
    print(f"[server] data viewer connected ({len(data_viewers)} total)")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        data_viewers.discard(websocket)
        print(f"[server] data viewer disconnected ({len(data_viewers)} total)")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)