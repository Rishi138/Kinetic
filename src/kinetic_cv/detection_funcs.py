import math

CLINICAL_GREEN_BGR = (113, 204, 46)
CLINICAL_AMBER_BGR = (15, 196, 241)
CLINICAL_ORANGE_BGR = (34, 126, 230)
CLINICAL_RED_BGR = (60, 76, 231)
CLINICAL_GRAY_BGR = (166, 165, 149)
PANEL_BG_BGR = (30, 28, 26)
TEXT_MUTED_BGR = (150, 150, 155)
TEXT_BRIGHT_BGR = (235, 235, 235)


def hip_deviation(hips, neutral_pose):
    lx, ly = hips[0][0], hips[0][1]
    rx, ry = hips[1][0], hips[1][1]

    # Current hip alignment
    dx = rx - lx
    dy = ry - ly

    if abs(dx) < 1e-6:
        bad = ["UNRELIABLE HIP POSITION", 0.0]
        return [bad.copy(), bad.copy()]

    hip_drop = dy / abs(dx)

    # Calibrated neutral hip alignment
    neutral_l = neutral_pose["l_hip"]
    neutral_r = neutral_pose["r_hip"]

    neutral_dx = neutral_r[0] - neutral_l[0]
    neutral_dy = neutral_r[1] - neutral_l[1]

    if abs(neutral_dx) < 1e-6:
        bad = ["UNRELIABLE NEUTRAL HIP POSITION", 0.0]
        return [bad.copy(), bad.copy()]

    neutral_hip_drop = neutral_dy / abs(neutral_dx)

    # Measure change relative to neutral posture
    hip_drop -= neutral_hip_drop

    results = []

    # Index 0 = left hip; index 1 = right hip.
    for deviation, direction in [
        (-hip_drop, "LEFT HIP DROP"),
        (hip_drop, "RIGHT HIP DROP")
    ]:
        deviation = max(0.0, deviation)
        magnitude = deviation

        if magnitude < 0.085:
            tag = "GOOD"
        elif magnitude < 0.095:
            tag = "SLIGHT"
        elif magnitude < 0.015:
            tag = "MILD"
        elif magnitude < 0.25:
            tag = "CONCERNING"
        elif magnitude < 0.35:
            tag = "BAD"
        else:
            tag = "SEVERE"

        scale_pos = min(magnitude / 0.05, 1.0)

        if tag == "GOOD":
            results.append(
                [f"GOOD HIP ALIGNMENT ({deviation:.4f})", scale_pos]
            )
        else:
            results.append(
                [f"{tag} {direction} ({deviation:.4f})", scale_pos]
            )

    return results


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

    # over punish valgus, bigger risk factor
    if knee_dist > 0:
        tag = "VARUS"
        knee_dist *= 0.6
    elif knee_dist < 0:
        tag = "VALGUS"
        knee_dist *= 2.5

    if abs(knee_dist) < 0.035:
        scale_pos = abs(knee_dist) / 0.1
        return f"GOOD ({knee_dist})", scale_pos
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

    scale_pos = abs(knee_dist) / 0.1
    if scale_pos > 1.0:
        scale_pos = 1.0

    return f"{tag2} KNEE {tag} ({knee_dist})", scale_pos
