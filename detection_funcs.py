import cv2
import numpy as np


def knee_alignment_score(
        hip_state,
        knee_state,
        ankle_state,
        side,
        tolerance=0.08,
        severe=0.35
):
    """
    Returns:
        score  : 0-1
        status : Clinical severity string
    """

    hip = np.array(hip_state[:2])
    knee = np.array(knee_state[:2])
    ankle = np.array(ankle_state[:2])

    hip_to_ankle = ankle - hip
    hip_to_knee = knee - hip

    length = np.linalg.norm(hip_to_ankle)
    femur = np.linalg.norm(knee - hip)

    if length < 1e-6 or femur < 1e-6:
        return 0.0, "NORMAL"

    deviation = np.cross(
        hip_to_ankle,
        hip_to_knee
    ) / length

    normalized = deviation / femur

    # inward positive
    if side == "left":
        normalized *= -1

    if abs(normalized) <= tolerance:
        return 0.0, "NORMAL"

    if normalized > tolerance:

        score = (
            normalized - tolerance
        ) / (severe - tolerance)

        score = float(np.clip(score, 0, 1))

        if score < 0.33:
            status = "MILD VALGUS"
        elif score < 0.66:
            status = "MODERATE VALGUS"
        else:
            status = "SEVERE VALGUS"

        return score, status

    score = (
        -normalized - tolerance
    ) / (severe - tolerance)

    score = float(np.clip(score, 0, 1))

    if score < 0.33:
        status = "MILD VARUS"
    elif score < 0.66:
        status = "MODERATE VARUS"
    else:
        status = "SEVERE VARUS"

    return score, status


def draw_alignment_indicator(
        frame,
        score,
        status,
        label,
        x,
        y
):

    panel_w = 330
    panel_h = 58

    bar_w = 140
    bar_h = 8

    bar_x = x + 175
    bar_y = y + 38

    # Clinical colors
    if status == "NORMAL":
        color = (80, 200, 80)

    elif "MILD" in status:
        color = (0, 220, 255)

    elif "MODERATE" in status:
        color = (0, 170, 255)

    else:
        color = (0, 60, 255)

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (x, y),
        (x + panel_w, y + panel_h),
        (18, 18, 18),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.80,
        frame,
        0.20,
        0,
        frame
    )

    cv2.putText(
        frame,
        label,
        (x + 12, y + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        (230, 230, 230),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        status,
        (x + 12, y + 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        color,
        1,
        cv2.LINE_AA
    )

    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + bar_w, bar_y + bar_h),
        (65, 65, 65),
        -1
    )

    fill = int(bar_w * score)

    if fill > 0:
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + fill, bar_y + bar_h),
            color,
            -1
        )