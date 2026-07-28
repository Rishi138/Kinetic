import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
from CustomKalman import KalmanFilter3D
import numpy as np
import detection_funcs


def sides_consistent(r_state, l_state):
    return r_state[0] > l_state[0]


def draw_depth_point(frame, pt, z):
    z_near = -0.6
    z_far = 0.3

    depth = (z_far - z) / (z_far - z_near)
    depth = np.clip(depth, 0, 1)

    radius = int(4 + depth * 8)

    glow_radius = radius * 2
    glow_intensity = int(20 + depth * 80)

    overlay = frame.copy()

    cv2.circle(
        overlay,
        pt,
        glow_radius,
        (0, glow_intensity, 0),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.25,
        frame,
        0.75,
        0,
        frame
    )

    cv2.circle(
        frame,
        pt,
        radius,
        (0, 255, 0),
        -1
    )


base_option = python.BaseOptions(model_asset_path="pose_landmarker_heavy.task")
options = vision.PoseLandmarkerOptions(
    base_options=base_option,
    num_poses=1,
    running_mode=vision.RunningMode.VIDEO
)

detector = vision.PoseLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)

# 23, 24, 25, 26, 27, 28, 11, 12
rh_23_kalman = KalmanFilter3D()
lh_24_kalman = KalmanFilter3D()
rk_25_kalman = KalmanFilter3D()
lk_26_kalman = KalmanFilter3D()
ra_27_kalman = KalmanFilter3D()
la_28_kalman = KalmanFilter3D()
rs_11_kalman = KalmanFilter3D()
ls_12_kalman = KalmanFilter3D()
rf_31_kalman = KalmanFilter3D()
lf_32_kalman = KalmanFilter3D()

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

    if result.pose_landmarks:
        timestamp_s = time.time() - start_time
        pose = result.pose_landmarks[0]

        rh_state = rh_23_kalman.step(
            [pose[23].x, pose[23].y, pose[23].z],
            confidence=pose[23].visibility,
            timestamp=timestamp_s
        )

        lh_state = lh_24_kalman.step(
            [pose[24].x, pose[24].y, pose[24].z],
            confidence=pose[24].visibility,
            timestamp=timestamp_s
        )

        rk_state = rk_25_kalman.step(
            [pose[25].x, pose[25].y, pose[25].z],
            confidence=pose[25].visibility,
            timestamp=timestamp_s
        )

        lk_state = lk_26_kalman.step(
            [pose[26].x, pose[26].y, pose[26].z],
            confidence=pose[26].visibility,
            timestamp=timestamp_s
        )

        ra_state = ra_27_kalman.step(
            [pose[27].x, pose[27].y, pose[27].z],
            confidence=pose[27].visibility,
            timestamp=timestamp_s
        )

        la_state = la_28_kalman.step(
            [pose[28].x, pose[28].y, pose[28].z],
            confidence=pose[28].visibility,
            timestamp=timestamp_s
        )
        rs_state = rs_11_kalman.step(
            [pose[11].x, pose[11].y, pose[11].z],
            confidence=pose[11].visibility,
            timestamp=timestamp_s
        )

        ls_state = ls_12_kalman.step(
            [pose[12].x, pose[12].y, pose[12].z],
            confidence=pose[12].visibility,
            timestamp=timestamp_s
        )

        rf_state = rf_31_kalman.step(
            [pose[31].x, pose[31].y, pose[31].z],
            confidence=pose[31].visibility,
            timestamp=timestamp_s
        )

        lf_state = lf_32_kalman.step(
            [pose[32].x, pose[32].y, pose[32].z],
            confidence=pose[32].visibility,
            timestamp=timestamp_s
        )

        if (
                sides_consistent(rh_state, lh_state) and
                sides_consistent(rk_state, lk_state) and
                sides_consistent(ra_state, la_state) and
                sides_consistent(rs_state, ls_state) and
                sides_consistent(rf_state,lf_state)
        ):

            rh_pt = (int(rh_state[0] * w), int(rh_state[1] * h))
            lh_pt = (int(lh_state[0] * w), int(lh_state[1] * h))

            rk_pt = (int(rk_state[0] * w), int(rk_state[1] * h))
            lk_pt = (int(lk_state[0] * w), int(lk_state[1] * h))

            ra_pt = (int(ra_state[0] * w), int(ra_state[1] * h))
            la_pt = (int(la_state[0] * w), int(la_state[1] * h))

            rs_pt = (int(rs_state[0] * w), int(rs_state[1] * h))
            ls_pt = (int(ls_state[0] * w), int(ls_state[1] * h))

            rf_pt = (int(rf_state[0] * w), int(rf_state[1] * h))
            lf_pt = (int(lf_state[0] * w), int(lf_state[1] * h))

            points = [
                (rh_pt, rh_state[2]),
                (lh_pt, lh_state[2]),
                (rk_pt, rk_state[2]),
                (lk_pt, lk_state[2]),
                (ra_pt, ra_state[2]),
                (la_pt, la_state[2]),
                (rs_pt, rs_state[2]),
                (ls_pt, ls_state[2]),
                (rf_pt, rf_state[2]),
                (lf_pt, lf_state[2]),
            ]

            for pt, z in points:
                draw_depth_point(frame, pt, z)
            # start here
            right_score, right_status = detection_funcs.knee_alignment_score(
                rh_state,
                rk_state,
                ra_state,
                "right"
            )

            left_score, left_status = detection_funcs.knee_alignment_score(
                lh_state,
                lk_state,
                la_state,
                "left"
            )

            detection_funcs.draw_alignment_indicator(
                frame,
                right_score,
                right_status,
                "RIGHT KNEE ALIGNMENT",
                w - 350,
                30
            )

            detection_funcs.draw_alignment_indicator(
                frame,
                left_score,
                left_status,
                "LEFT KNEE ALIGNMENT",
                w - 350,
                100
            )

    cv2.imshow("Kalman Pose", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
