#!/usr/bin/env python3
"""오늘 출발 자세 vs 어제 mp5 출발 자세 — 라이다 스캔 정합(ICP)으로 로버 변위를 구해, 어제 상자 위치(깊이 1.174/−0.013)가
   오늘 로버 기준 어디여야 하는지 계산 (2026-09-17, 상자 거리 불일치 교차검증). 상자는 라이다에 안 보이므로 가구·벽으로 정합한다.
   인자: BAG(어제) NOW_NPY [box_x box_y]
"""
import sys, math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import LaserScan

BAG = sys.argv[1]; NOW = sys.argv[2]
BX, BY = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (1.174, -0.013)
LX, LYAW = 0.152, math.pi          # lidar_link → base_link (job338 정적 TF: 0.152, 0, 180°)


def to_base(amin, ainc, ranges):
    r = np.asarray(ranges, dtype=np.float64); a = amin + np.arange(r.size) * ainc
    ok = np.isfinite(r) & (r > 0.25) & (r < 6.0)
    px, py = r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok])
    bx = LX + px * math.cos(LYAW) - py * math.sin(LYAW); by = py * math.cos(LYAW) + px * math.sin(LYAW)
    return np.stack([bx, by], 1)


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
scans = []
while r.has_next() and len(scans) < 30:
    topic, data, ts = r.read_next()
    if topic == '/scan':
        m = deserialize_message(data, LaserScan); scans.append(to_base(m.angle_min, m.angle_increment, m.ranges))
ref = np.concatenate(scans[5:25])     # 어제 출발 직후 2 s (정지 구간)
v = np.load(NOW); cur = to_base(v[0], v[1], v[2:])
print('기준(어제 mp5 출발) 점 %d, 현재 점 %d' % (len(ref), len(cur)))


def nn(A, B):
    d = np.empty(len(A)); idx = np.empty(len(A), int)
    for s in range(0, len(A), 400):
        D = (A[s:s + 400, None, 0] - B[None, :, 0]) ** 2 + (A[s:s + 400, None, 1] - B[None, :, 1]) ** 2
        idx[s:s + 400] = D.argmin(1); d[s:s + 400] = np.sqrt(D.min(1))
    return d, idx


best = None
for yaw0 in np.radians(np.arange(-10, 10.1, 2.5)):
    for x0 in (-0.3, -0.15, 0.0, 0.15, 0.3):
        th, tx, ty = yaw0, x0, 0.0
        for it in range(40):
            c, s_ = math.cos(th), math.sin(th)
            C = cur @ np.array([[c, -s_], [s_, c]]).T + [tx, ty]      # 현재 스캔을 어제 기준 프레임으로
            d, idx = nn(C, ref)
            thr = max(0.05, np.percentile(d, 70))
            m = d < thr
            if m.sum() < 50:
                break
            A = C[m]; B = ref[idx[m]]
            ma, mb = A.mean(0), B.mean(0)
            Hm = (A - ma).T @ (B - mb); U, _, Vt = np.linalg.svd(Hm); Rm = Vt.T @ U.T
            if np.linalg.det(Rm) < 0:
                Vt[1] *= -1; Rm = Vt.T @ U.T
            dth = math.atan2(Rm[1, 0], Rm[0, 0]); dt = mb - Rm @ ma
            # 누적 (C' = Rm C + dt)
            th += dth
            Rn = np.array([[math.cos(dth), -math.sin(dth)], [math.sin(dth), math.cos(dth)]])
            tx, ty = Rn @ np.array([tx, ty]) + dt
            if abs(dth) < 1e-5 and np.hypot(*dt) < 1e-5:
                break
        c, s_ = math.cos(th), math.sin(th)
        d, _ = nn(cur @ np.array([[c, -s_], [s_, c]]).T + [tx, ty], ref)
        score = np.median(d); inl = (d < 0.05).mean()
        if best is None or score < best[0]:
            best = (score, inl, th, tx, ty)
score, inl, th, tx, ty = best
print('ICP: 오늘 출발 base_link = 어제 기준으로 (x %+.3f, y %+.3f, yaw %+.2f°) | 잔차 중앙 %.3f m, 5 cm 내 %.0f%%' % (tx, ty, math.degrees(th), score, 100 * inl))
# 어제 상자(어제 기준 프레임) → 오늘 로버 프레임
dx, dy = BX - tx, BY - ty
ex = dx * math.cos(th) + dy * math.sin(th); ey = -dx * math.sin(th) + dy * math.cos(th)
print('상자가 어제 자리 그대로라면 오늘 로버 기준: 전면 x %.3f, 중심 y %+.3f' % (ex, ey))
