#!/usr/bin/env python3
"""S2 근거리 측정 (2026-09-21 §5). 인자: NAME D_FRONT DEC [SEC=10] [W=0.18] [H=0.14] [DEPTH=0.11]
  로버 정지. 상자 전면이 **로버 최앞단(base_link x 0.25)** 에서 D_FRONT 앞. 카메라(URDF x 0.234)까지는 D_FRONT + 0.016.
  두 토픽을 SEC 초 동안 받아 base_link 로 변환(TF) 후 상자 구역 점 수를 프레임별로 센다:
    원시  /camera/camera/depth/color/points   → 센서 한계
    릴레이 /camera/depth/points_filtered       → 코스트맵이 받는 것(min_range 0.45·복셀 3점·5중3 지속)
  구역: x ∈ [0.25+D−0.04, 0.25+D+DEPTH+0.04], |y−yc| < W/2+0.06 (yc = 해당 프레임 점들의 y 중앙값, 상자가 정확히 정면이 아닐 수 있음), z ∈ (0.0, 0.30) (바닥 z≈−0.026 제외)
  밀도 = 점 수 / 정면 면적(W·H, cm²) — 크기가 다른 물체로 일반화하기 위한 값. 기하 예측: 디시메이션 DEC 에서 픽셀 각 = 87°/(640/DEC) 가로, 58°/(480/DEC) 세로
  → 거리 r 에서 정면(W×H)이 차지하는 픽셀 수 ≈ (W/r / rad_h)·(H/r / rad_v).
"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
import tf2_ros
NAME, D, DEC = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
SEC = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
W = float(sys.argv[5]) if len(sys.argv) > 5 else 0.18
H = float(sys.argv[6]) if len(sys.argv) > 6 else 0.14
DEPTH = float(sys.argv[7]) if len(sys.argv) > 7 else 0.11
FRONT, CAMX = 0.25, 0.234
TOPICS = {'raw': '/camera/camera/depth/color/points', 'relay': '/camera/depth/points_filtered'}


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


rclpy.init(); n = Node('nearrange458'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {k: [] for k in TOPICS}; TFC = {}


def to_base(m):
    fid = m.header.frame_id
    if fid not in TFC:
        try:
            t = buf.lookup_transform('base_link', fid, rclpy.time.Time()).transform
            TFC[fid] = (Rq(t.rotation), np.array([t.translation.x, t.translation.y, t.translation.z]))
        except Exception:
            return None
    R, T = TFC[fid]
    off = {f.name: f.offset for f in m.fields}
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
    xyz = np.stack([raw[:, off[k]:off[k] + 4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    return xyz @ R.T + T


SKIP = int(sys.argv[8]) if len(sys.argv) > 8 else 3   # 09-21: dec 2 에서 측정 노드 자체가 CPU 134 % → 3 프레임에 1 개만 처리(CPU 계측 오염 방지)
YFIX = float(sys.argv[9]) if len(sys.argv) > 9 else None   # 고정 y 중심(m). 없으면 x 띠 안 점들의 중앙값
NSEEN = {k: 0 for k in TOPICS}


def cb(key):
    def f(m):
        NSEEN[key] += 1
        if NSEEN[key] % SKIP:
            return
        P = to_base(m)
        if P is None:
            S[key].append(None); return
        x0, x1 = FRONT + D - 0.04, FRONT + D + DEPTH + 0.04
        sel = P[(P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 2] > 0.0) & (P[:, 2] < 0.30) & (np.abs(P[:, 1]) < 0.45)]
        if YFIX is not None:      # 09-21 의자 다리: 다른 다리·가로대가 같은 x 띠에 들어오므로 중앙값 대신 고정 y 창(로버 중심선 ±(W/2+0.06))
            yc = YFIX; sel = sel[np.abs(sel[:, 1] - yc) < W / 2 + 0.06]
        elif len(sel):
            yc = float(np.median(sel[:, 1])); sel = sel[np.abs(sel[:, 1] - yc) < W / 2 + 0.06]
        else:
            yc = float('nan')
        S[key].append((len(P), len(sel), yc, float(np.percentile(sel[:, 0], 5)) if len(sel) else float('nan'),
                       float(sel[:, 2].max()) if len(sel) else float('nan'), float(sel[:, 2].min()) if len(sel) else float('nan'),
                       int((sel[:, 2] < 0.06).sum()) if len(sel) else 0))   # 09-21 의자 바퀴(바닥 위 ~5 cm) 몫
    return f


for k, tp in TOPICS.items():
    n.create_subscription(PointCloud2, tp, cb(k), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < SEC + 2.0:      # TF 대기 여유 2 s
    rclpy.spin_once(n, timeout_sec=0.05)
ELAPSED = time.time() - t0
rclpy.shutdown()
r = D + 0.016 + DEPTH / 2   # 카메라↔상자 전면 (+ 반깊이는 안 더함: 전면 기준) → 아래서 전면 기준 r0 사용
r0 = D + 0.016
rad_h, rad_v = math.radians(87.0) / (640 / DEC), math.radians(58.0) / (480 / DEC)
pix_pred = (W / r0 / rad_h) * (H / r0 / rad_v)
print('==== %s: 상자 전면 앞단 %.2f m = 카메라 %.3f m, dec %d, %.0f s | 정면 %gx%g cm 예상 픽셀 %.0f' % (NAME, D, r0, DEC, SEC, W * 100, H * 100, pix_pred))
for k in TOPICS:
    fr = [x for x in S[k] if x is not None]; notf = sum(1 for x in S[k] if x is None)
    if not fr:
        print('  %-5s 프레임 0 (TF 실패 %d)' % (k, notf)); continue
    cnt = np.array([x[1] for x in fr]); tot = np.array([x[0] for x in fr])
    yc = np.nanmedian([x[2] for x in fr]); xf = np.nanmedian([x[3] for x in fr]); zt = np.nanmedian([x[4] for x in fr]); zb = np.nanmedian([x[5] for x in fr])
    low = np.median([x[6] for x in fr]); print('  %-5s   (z<0.06 바퀴 몫 중앙 %.0f 점, 위 %.0f 점)' % (k, low, np.median(cnt) - low))
    print('  %-5s 프레임 %3d/%3d (수신 %.1f Hz) | 전체 점 중앙 %6.0f | 상자 구역 점: 중앙 %5.0f  최소 %5.0f  최대 %5.0f  0 인 프레임 %3d (%2.0f%%) | 밀도 %.2f 점/cm² | 검출 전면 x %.3f(base) y %+.3f z %.3f~%.3f' % (
        k, len(fr), NSEEN[k], NSEEN[k] / ELAPSED, np.median(tot), np.median(cnt), cnt.min(), cnt.max(), (cnt == 0).sum(), 100 * (cnt == 0).mean(), np.median(cnt) / (W * H * 1e4), xf, yc, zb, zt))
