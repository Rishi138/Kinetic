import cv2
import numpy as np
import math

CLINICAL_GREEN_BGR = (113, 204, 46)
CLINICAL_AMBER_BGR = (15, 196, 241)
CLINICAL_ORANGE_BGR = (34, 126, 230)
CLINICAL_RED_BGR = (60, 76, 231)
CLINICAL_GRAY_BGR = (166, 165, 149)
PANEL_BG_BGR = (30, 28, 26)
TEXT_MUTED_BGR = (150, 150, 155)
TEXT_BRIGHT_BGR = (235, 235, 235)


def knee_deviation(hip, knee, ankle, offset, side):
    # side true right
    # side false left
    ax, ay = ankle[0], ankle[1]
    hx, hy = hip[0], hip[1]
    kx, ky = knee[0], knee[1]

    vx = hx - ax
    vy = hy - ay

    line_len = math.hypot(vx, vy)

    wx = kx - ax
    wy = ky - ay
    knee_dist = (vx * wy - vy * wx) / line_len

    knee_dist -= offset
    knee_dist /= line_len

    if not side:
        knee_dist = -1 * knee_dist

    if knee_dist > 0:
        tag = "VARUS"
        knee_dist *= 0.6
    elif knee_dist < 0:
        tag = "VALGUS"
        knee_dist *= 2

    if abs(knee_dist) < 0.035:
        return f"GOOD ({knee_dist})"
    elif abs(knee_dist) < 0.045:
        tag2 = "SLIGHT"
    elif abs(knee_dist) < 0.065:
        tag2 = "MILD"
    elif abs(knee_dist) < 0.070:
        tag2 = "CONCERNING"
    elif abs(knee_dist) < 0.095:
        tag2 = "BAD"
    else:
        tag2 = "SEVERE"

    return f"{tag2} KNEE {tag} ({knee_dist})"
