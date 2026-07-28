import numpy as np
import time


class KalmanFilter3D:
    def __init__(self, Q=0.10, R=0.012):
        # Q: Process noise
        # R: Measurement noise (MediaPipe)
        # state: [x, y, z, vx, vy, vz]
        self.state = np.zeros(6)

        # covar matrix
        self.P = np.eye(6) * 1.0

        # noise init
        self.Q_base = Q
        self.R_base = R

        # observe pos
        self.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0]
        ], dtype=float)

        # Identity matrix
        self.I = np.eye(6)

        # Prev time
        self.prev_time = None

    def build_F(self, dt):
        # Build F, update based of change in time, change position based of time passed
        F = np.eye(6)
        F[0, 3] = dt
        F[1, 4] = dt
        F[2, 5] = dt
        return F

    def build_Q(self, dt, q):
        # Build Q scaled to dt
        Q = np.zeros((6, 6))
        block = q * np.array([
            [dt ** 3 / 3, dt ** 2 / 2],
            [dt ** 2 / 2, dt]
        ])
        for i in range(3):  # x, y, z
            idx = [i, i + 3]
            Q[np.ix_(idx, idx)] = block
        return Q

    def predict(self, dt):
        # Build F and Q
        F = self.build_F(dt)
        Q = self.build_Q(dt, self.Q_base)

        self.state[3:] *= 0.92

        # state pred with F
        self.state = F @ self.state

        # Covar matrix update, add process noise
        self.P = F @ self.P @ F.T + Q  # FPF^T + Q

    def update(self, measurement, confidence=1.0, gate_threshold=7.0):
        # 8.515 = chi-squared 96.3% for 3 DOF
        z = np.array(measurement)

        # Adaptive R (measurement noise)
        c = max(confidence, 1e-3)  # Confidence floor of 1*10^-3
        R = np.eye(3) * (self.R_base / c)  # Weight R based on confidence (visibility from mediapipe)

        # total measurement uncertainty (state uncertainty + measurement noise)
        S = self.H @ self.P @ self.H.T + R  # HPH^T + R
        y = z - (self.H @ self.state)  # innovation (measured - stated pred -> y = z - state)

        # mahalanobis gate, currently rejects 3.7%
        # dist: weighted innovation (measurement discrepancy) with S (total measurement uncertainty)
        mahal_sq = float(y.T @ np.linalg.inv(S) @ y)  # mahal distance squared
        if mahal_sq > gate_threshold:
            return False  # skip update, keep predicted state

        K = self.P @ self.H.T @ np.linalg.inv(S)  # Kalman gain (PH/S)
        self.state = self.state + K @ y  # State update (state + Ky)
        self.P = (self.I - K @ self.H) @ self.P  # P update (changed based of certainty, (I-KH)P)
        return True

    def step(self, measurement, confidence=1.0, timestamp=None):
        # Confidence based on visibility returned by MediaPipe
        if timestamp is None:
            timestamp = time.time()

        if self.prev_time is None:
            self.state[:3] = measurement
            self.prev_time = timestamp
            return self.state.copy()

        dt = timestamp - self.prev_time
        self.prev_time = timestamp
        dt = max(dt, 1e-4)

        # ALWAYS predict
        self.predict(dt)

        if confidence > 0.5:
            # Only update if measurement is clean, otherwise skip (make sure not to make covar dirty)
            self.update(measurement, confidence)

        return self.state.copy()
