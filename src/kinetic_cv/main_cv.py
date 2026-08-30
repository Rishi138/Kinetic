import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import numpy as np
from CustomKalman import KalmanFilter3D
import detection_funcs
import asyncio
import websockets


WS_URL = "ws://localhost:8000/engine"
_ws = None
_loop = asyncio.new_event_loop()

async def _connect():
    global _ws
    _ws = await websockets.connect(WS_URL)

_loop.run_until_complete(_connect())

def send_frame(frame):
    _, jpeg = cv2.imencode(".jpg", frame)
    _loop.run_until_complete(_ws.send(jpeg.tobytes()))


LANDMARKS = {
    "r_shoulder": 11, "l_shoulder": 12,
    "r_hip": 23, "l_hip": 24,
    "r_knee": 25, "l_knee": 26,
    "r_ankle": 27, "l_ankle": 28,
    "r_foot": 31, "l_foot": 32,
}


def draw_depth_point(frame, pt, z):
    z_near = -0.6
    z_far = 0.3

    depth = (z_far - z) / (z_far - z_near)
    depth = np.clip(depth, 0, 1)

    radius = int(4 + depth * 8)
    glow_radius = radius * 2
    glow_intensity = int(20 + depth * 80)

    overlay = frame.copy()
    cv2.circle(overlay, pt, glow_radius, (46, glow_intensity, 20), -1)
    cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)
    cv2.circle(frame, pt, radius, detection_funcs.CLINICAL_GREEN_BGR, -1)


def bias_hip_outward(hip, opposite_hip, amount=0.05):
    direction = hip - opposite_hip
    length = np.linalg.norm(direction[:2])

    if length < 1e-6:
        return hip

    direction = direction / length

    corrected = hip.copy()
    corrected[0] -= direction[0] * amount
    corrected[1] -= direction[1] * amount

    return corrected


base_option = python.BaseOptions(model_asset_path="pose_landmarker_heavy.task")
options = vision.PoseLandmarkerOptions(
    base_options=base_option,
    num_poses=1,
    running_mode=vision.RunningMode.VIDEO,
)

detector = vision.PoseLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)

image_filters = {name: KalmanFilter3D() for name in LANDMARKS}
world_filters = {name: KalmanFilter3D() for name in LANDMARKS}

start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    timestamp_ms = int((time.time() - start_time) * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    if result.pose_landmarks and result.pose_world_landmarks:
        timestamp_s = time.time() - start_time
        pose = result.pose_landmarks[0]
        pose_world = result.pose_world_landmarks[0]

        image_states = {}
        world_states = {}

        for name, idx in LANDMARKS.items():
            lm = pose[idx]
            wlm = pose_world[idx]
            conf = lm.visibility

            image_states[name] = image_filters[name].step(
                [lm.x, lm.y, lm.z], confidence=conf, timestamp=timestamp_s
            )
            world_states[name] = world_filters[name].step(
                [wlm.x, wlm.y, wlm.z], confidence=conf, timestamp=timestamp_s
            )

        for name, state in image_states.items():
            pt = (int(state[0] * w), int(state[1] * h))
            draw_depth_point(frame, pt, state[2])

        # Here
        HIP_BIAS = -0.035

        r_hip_corrected = bias_hip_outward(
            world_states["r_hip"],
            world_states["l_hip"],
            HIP_BIAS
        )

        l_hip_corrected = bias_hip_outward(
            world_states["l_hip"],
            world_states["r_hip"],
            HIP_BIAS
        )

        r_score = detection_funcs.knee_deviation(
            r_hip_corrected,
            world_states["r_knee"],
            world_states["r_ankle"],
            offset=-0.03,
            side=True
        )

        l_score = detection_funcs.knee_deviation(
            l_hip_corrected,
            world_states["l_knee"],
            world_states["l_ankle"],
            offset=0.03,
            side=False
        )

        panel_x = w - 420
        panel_y = 20
        panel_w = 400
        panel_h = 120

        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            detection_funcs.PANEL_BG_BGR,
            -1
        )

        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (panel_x + panel_w, panel_y + panel_h),
            detection_funcs.CLINICAL_GRAY_BGR,
            2
        )

        cv2.putText(
            frame,
            "KNEE ALIGNMENT",
            (panel_x + 15, panel_y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            detection_funcs.TEXT_BRIGHT_BGR,
            2
        )

        cv2.putText(
            frame,
            f"RIGHT: {r_score}",
            (panel_x + 15, panel_y + 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            detection_funcs.CLINICAL_GREEN_BGR,
            2
        )

        cv2.putText(
            frame,
            f"LEFT:  {l_score}",
            (panel_x + 15, panel_y + 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            detection_funcs.CLINICAL_GREEN_BGR,
            2
        )
    send_frame(frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
