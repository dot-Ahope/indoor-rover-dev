#!/usr/bin/env python3
"""라이다·카메라 장착 yaw 측정 (2026-09-18). 로버 옆면(트랙 앞뒤 모두)을 곧은 벽에 붙여 두고 정지 상태에서 실행.
  라이다: /scan 을 URDF 공칭 변환(lidar_yaw = π, 위치 0,0)으로 base_link 에 옮겨 옆벽 직선을 RANSAC+최소제곱 → 벽 각도.
     벽은 실제로 몸체 x 축과 나란하므로, 보이는 각도 = −(장착 오차 e). 권장 lidar_yaw = π + e.
  카메라: 포인트클라우드를 camera_link(URDF camera_joint rpy 0 → base 와 같은 방향)로 옮겨 같은 벽 직선 각도.
  예측(가설): SLAM 게걸음 +2.7° → 벽이 +2.7° 로 보이고 권장 lidar_yaw ≈ π − 0.047.
"""
import time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan, PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros

LYAW = math.pi   # URDF 공칭


def fit_line(P, iters=400, thr=0.01, rng=np.random.default_rng(0)):
    best = None
    for _ in range(iters):
        i, j = rng.choice(len(P), 2, replace=False)
        d = P[j] - P[i]; n = np.linalg.norm(d)
        if n < 0.2:
            continue
        d /= n; nor = np.array([-d[1], d[0]])
        res = np.abs((P - P[i]) @ nor); inl = res < thr
        if best is None or inl.sum() > best.sum():
            best = inl
    Q = P[best]; c = Q.mean(0); U, S, Vt = np.linalg.svd(Q - c); d = Vt[0]
    if d[0] < 0:
        d = -d
    ang = math.degrees(math.atan2(d[1], d[0]))
    nor = np.array([-d[1], d[0]]); rms = float(np.sqrt(np.mean(((Q - c) @ nor) ** 2)))
    dist = float(abs(c @ nor))
    return ang, dist, int(best.sum()), rms, float(Q[:, 0].min()), float(Q[:, 0].max())


rclpy.init(); n = Node('wallyaw432'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'scan': [], 'cloud': []}
n.create_subscription(LaserScan, '/scan', lambda m: S['scan'].append(m), qos_profile_sensor_data)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: S['cloud'].append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 8.0:
    rclpy.spin_once(n, timeout_sec=0.1)
print('수신: scan %d, cloud %d' % (len(S['scan']), len(S['cloud'])))

# ── 라이다 ──
side = None
if S['scan']:
    angs, per = [], []
    for m in S['scan'][5:]:
        r = np.asarray(m.ranges, dtype=np.float64); a = m.angle_min + np.arange(r.size) * m.angle_increment
        ok = np.isfinite(r) & (r > 0.05) & (r < 3.0)
        px, py = r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok])
        bx = px * math.cos(LYAW) - py * math.sin(LYAW); by = px * math.sin(LYAW) + py * math.cos(LYAW)
        P = np.stack([bx, by], 1)
        if side is None:   # 옆벽이 있는 쪽: |x|<0.8 에서 0.1<|y|<0.5 인 점이 많은 쪽
            L = ((np.abs(P[:, 0]) < 0.8) & (P[:, 1] > 0.1) & (P[:, 1] < 0.5)).sum(); R_ = ((np.abs(P[:, 0]) < 0.8) & (P[:, 1] < -0.1) & (P[:, 1] > -0.5)).sum()
            side = 1 if L >= R_ else -1
            print('라이다: 옆벽은 %s (점 수 왼 %d / 오 %d)' % ('왼쪽(+y)' if side > 0 else '오른쪽(−y)', L, R_))
        sel = (np.abs(P[:, 0]) < 0.9) & (side * P[:, 1] > 0.1) & (side * P[:, 1] < 0.5)
        if sel.sum() < 30:
            continue
        per.append(fit_line(P[sel]))
        fs = (P[:, 0] > 0.55) & (P[:, 0] < 1.2) & (np.abs(P[:, 1]) < 0.45)
        if fs.sum() >= 30:
            S.setdefault('lfront', []).append(fit_line(P[fs], thr=0.012))
    if per:
        A = np.array([p[0] for p in per]); D = np.array([p[1] for p in per])
        print('라이다 벽 각도(base, 공칭 TF): 중앙 %+.3f°, 사분위 %+.3f~%+.3f° (%d 스캔), 벽까지 %.3f m, 인라이어 중앙 %d 점, 잔차 RMS 중앙 %.4f m, x 범위 %.2f~%.2f' % (
            np.median(A), np.percentile(A, 25), np.percentile(A, 75), len(A), np.median(D), int(np.median([p[2] for p in per])), np.median([p[3] for p in per]),
            np.median([p[4] for p in per]), np.median([p[5] for p in per])))
        e = -math.radians(np.median(A))
        print('  → 장착 오차 e = %+.3f° , 권장 lidar_yaw = π %+.4f rad = %.5f' % (math.degrees(e), e, math.pi + e))
    if S.get('lfront'):
        F = S['lfront']; A = np.array([f[0] for f in F])
        print('라이다 앞면 각도(base, 공칭 TF): 중앙 %+.3f° (%d 스캔), 거리 %.3f m, 인라이어 %d, 잔차 %.4f m, x %.2f~%.2f' % (np.median(A), len(A), np.median([f[1] for f in F]), int(np.median([f[2] for f in F])), np.median([f[3] for f in F]), np.median([f[4] for f in F]), np.median([f[5] for f in F])))

# ── 카메라 ──
if S['cloud']:
    m = S['cloud'][-1]
    try:
        T = buf.lookup_transform('camera_link', m.header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=2.0)).transform
        q = T.rotation; qx, qy, qz, qw = q.x, q.y, q.z, q.w
        R = np.array([[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
                      [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
                      [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]])
        angs = []
        for m in S['cloud'][-8:]:
            arr = pc2.read_points(m, field_names=('x', 'y', 'z'), skip_nans=True)
            P3 = np.stack([arr['x'], arr['y'], arr['z']], 1).astype(np.float64) @ R.T + np.array([T.translation.x, T.translation.y, T.translation.z])
            cs = side if side else 1
            # camera_link → base 위치(URDF: cam_dx 0.0822, cam_dy 0.0475) — 방향은 같다(rpy 0)
            P3 = P3 + np.array([0.0822, 0.0475, 0.0])
            fr = (P3[:, 0] > 0.55) & (P3[:, 0] < 1.2) & (np.abs(P3[:, 1]) < 0.45) & (np.abs(P3[:, 2]) < 0.20)
            if fr.sum() >= 200:
                Qf = P3[fr][:, :2]
                if len(Qf) > 6000: Qf = Qf[np.random.default_rng(2).choice(len(Qf), 6000, replace=False)]
                S.setdefault('cfront', []).append(fit_line(Qf, thr=0.015))
            s = (P3[:, 0] > 0.40) & (P3[:, 0] < 0.72) & (np.abs(P3[:, 2]) < 0.20) & (cs * P3[:, 1] > 0.15) & (cs * P3[:, 1] < 0.35)
            if s.sum() < 200:
                continue
            Q = P3[s][:, :2]
            if len(Q) > 6000:
                Q = Q[np.random.default_rng(1).choice(len(Q), 6000, replace=False)]
            angs.append(fit_line(Q, thr=0.015))
        if angs:
            A = np.array([a[0] for a in angs])
            print('카메라 옆벽 각도(base 방향): 중앙 %+.3f° (%d 프레임), 벽까지 %.3f m, 인라이어 %d, 잔차 RMS %.4f m, x 범위 %.2f~%.2f' % (
                np.median(A), len(A), np.median([a[1] for a in angs]), int(np.median([a[2] for a in angs])), np.median([a[3] for a in angs]),
                np.median([a[4] for a in angs]), np.median([a[5] for a in angs])))
        else:
            print('카메라 옆벽: 점 부족 (x 0.40~0.72, 옆 0.15~0.35 m 창)')
        if S.get('cfront'):
            F = S['cfront']; A = np.array([f[0] for f in F])
            print('카메라 앞면 각도(base 방향): 중앙 %+.3f° (%d 프레임), 거리 %.3f m, 인라이어 %d, 잔차 %.4f m, x %.2f~%.2f' % (np.median(A), len(A), np.median([f[1] for f in F]), int(np.median([f[2] for f in F])), np.median([f[3] for f in F]), np.median([f[4] for f in F]), np.median([f[5] for f in F])))
    except Exception as ex:
        print('카메라 TF 실패:', ex)
rclpy.shutdown()
