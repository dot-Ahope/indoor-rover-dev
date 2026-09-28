#!/usr/bin/env python3
"""제자리 회전 시험 분석 (2026-09-28): SLAM 없이 **정지 구간 스캔끼리 직접 정합(ICP)** 해서 회전별 차체 중심 이동을 잰다.
  왜: slam_toolbox(humble) 의 shouldProcessScan 은 **병진 거리**만 본다(dist² < 0.8·min_dist² 면 스캔을 버림, 회전각은 안 봄).
      v=0 순수 회전에서는 EKF odom 병진 ≈ 0 이라 스캔이 하나도 추가되지 않아 map→odom 이 그대로 → SLAM 으로는 못 잰다.
  방법: bag 의 /cmd_vel 로 회전 구간을 찾고, 회전 직전 정지 스캔 P0 와 회전 뒤 정지 스캔 P1 을 차체 좌표 점으로 바꿔
        P0 ≈ R(θ)·P1 + t 를 점-점 ICP(가까운 80 % 만, 문턱 0.5 → 0.08 m)로 푼다. (t, θ) = 시작 차체 기준 끝 차체의 자세.
        초기값 θ = EKF yaw 차, t = 0. 스캔 3 쌍의 중앙값. 정지 중 1 s 간격 스캔끼리도 정합해 잡음 바닥을 본다.
  인자: BAG   출력: 회전별 (앞+, 왼+) 이동·회전, 블록 누적(합성·직접 정합 두 가지)."""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
try:
    from scipy.spatial import cKDTree
except Exception:
    cKDTree = None


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


BAG = sys.argv[1]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
scans, cmd, ob, l2b = [], [], [], None
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/tf_static', '/scan', '/cmd_vel'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/scan': scans.append((t, m))
    elif tp == '/cmd_vel': cmd.append((t, m.angular.z))
    else:
        for tr in m.transforms:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((t, yaw(tr.transform.rotation)))
            elif tr.child_frame_id == 'lidar_link': l2b = (tr.header.frame_id, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
if l2b is None or l2b[0] != 'base_link':
    print('lidar_link 의 부모가 base_link 가 아님(%s) — URDF 값 사용' % (l2b,)); l2b = ('base_link', 0.0, 0.0, math.pi - 0.04677)
print('라이다→차체: x %.3f y %.3f yaw %.2f° | 스캔 %d 개, KD트리 %s' % (l2b[1], l2b[2], math.degrees(l2b[3]), len(scans), 'scipy' if cKDTree else 'numpy'))


def pts(m):
    rr = np.asarray(m.ranges, dtype=float); a = m.angle_min + np.arange(len(rr)) * m.angle_increment
    ok = np.isfinite(rr) & (rr > 0.40) & (rr < 8.0)
    x = rr[ok] * np.cos(a[ok]); y = rr[ok] * np.sin(a[ok]); c, s = math.cos(l2b[3]), math.sin(l2b[3])
    return np.c_[l2b[1] + c * x - s * y, l2b[2] + s * x + c * y][::2]


def nn(P0, Q, tree):
    if tree is not None: return tree.query(Q)
    d = np.empty(len(Q)); idx = np.empty(len(Q), dtype=int)
    for i in range(0, len(Q), 400):
        D = ((Q[i:i + 400, None, :] - P0[None, :, :]) ** 2).sum(2); idx[i:i + 400] = D.argmin(1); d[i:i + 400] = np.sqrt(D.min(1))
    return d, idx


def icp(P0, P1, th0):
    th = th0; t = np.zeros(2); tree = cKDTree(P0) if cKDTree else None; rms = 9; n = 0
    for it in range(60):
        c, s = math.cos(th), math.sin(th); R = np.array([[c, -s], [s, c]]); Q = P1 @ R.T + t
        d, idx = nn(P0, Q, tree)
        lim = max(0.08, 0.5 * (0.9 ** it)); lim = min(lim, max(0.08, np.percentile(d, 80)))
        k = d < lim; A = P1[k]; B = P0[idx[k]]
        ca, cb = A.mean(0), B.mean(0); H = (A - ca).T @ (B - cb); U, S, Vt = np.linalg.svd(H); Rn = Vt.T @ U.T
        if np.linalg.det(Rn) < 0: Vt[1] *= -1; Rn = Vt.T @ U.T
        th = math.atan2(Rn[1, 0], Rn[0, 0]); t = cb - Rn @ ca; rms = float(np.sqrt((d[k] ** 2).mean())); n = int(k.sum())
    return t, th, rms, n


def scan_at(t):
    k = bisect.bisect_left([s[0] for s in scans], t); return scans[min(max(k, 0), len(scans) - 1)]
def yaw_at(t):
    k = bisect.bisect_left([o[0] for o in ob], t); return ob[min(max(k, 0), len(ob) - 1)][1]


# 회전 구간 = |ω 지령| > 0.01 이 이어지는 덩어리(0.5 s 넘게 끊기면 새 구간)
segs = []
for t, w in cmd:
    if abs(w) > 0.01:
        if segs and t - segs[-1][1] < 0.5: segs[-1][1] = t
        else: segs.append([t, t])
segs = [s for s in segs if s[1] - s[0] > 2.0]
print('회전 구간 %d 개: %s' % (len(segs), ', '.join('%.1f s' % (b - a) for a, b in segs)))


def match(tA, tB):
    """tA 부근 정지 스캔 3 개 ↔ tB 부근 정지 스캔 3 개, 중앙값."""
    out = []
    for da, db in ((0.0, 0.0), (-0.3, 0.3), (-0.6, 0.6)):
        sA = scan_at(tA + da); sB = scan_at(tB + db)
        t, th, rms, n = icp(pts(sA[1]), pts(sB[1]), uw(yaw_at(sB[0]) - yaw_at(sA[0])))
        out.append((t[0], t[1], th, rms, n))
    o = np.array(out); return np.median(o[:, 0]), np.median(o[:, 1]), math.atan2(np.median(np.sin(o[:, 2])), np.median(np.cos(o[:, 2]))), np.median(o[:, 3]), int(np.median(o[:, 4])), o


def compose(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], uw(a[2] + b[2]))


tot = (0.0, 0.0, 0.0); res = []
for k, (a, b) in enumerate(segs):
    tA = a - 0.8; tB = b + 2.5
    # 잡음 바닥: 회전 전 정지 중 1 s 간격
    n0 = match(tA - 1.0, tA)
    x, y, th, rms, n, o = match(tA, tB)
    ek = math.degrees(uw(yaw_at(tB) - yaw_at(tA)))
    res.append((x, y, th)); tot = compose(tot, (x, y, th))
    print('  회전 %d: 중심 이동(시작 차체 기준 앞+/왼+) (%+.3f, %+.3f) = %.3f m | 회전 스캔 %+.2f° vs EKF %+.2f° | 잔차 rms %.3f m, 짝 %d | 3 쌍 산포 x %.3f y %.3f | 잡음 바닥 (%+.3f, %+.3f, %+.2f°)'
          % (k + 1, x, y, math.hypot(x, y), math.degrees(th), ek, rms, n, o[:, 0].max() - o[:, 0].min(), o[:, 1].max() - o[:, 1].min(), n0[0], n0[1], math.degrees(n0[2])))
if segs:
    d = match(segs[0][0] - 0.8, segs[-1][1] + 2.5)
    print('블록 누적(첫 시작 차체 기준 앞+/왼+): 합성 (%+.3f, %+.3f) m, %+.1f° | 처음↔끝 직접 정합 (%+.3f, %+.3f) m, %+.1f° (rms %.3f)'
          % (tot[0], tot[1], math.degrees(tot[2]), d[0], d[1], math.degrees(d[2]), d[3]))
    m = [math.hypot(a[0], a[1]) for a in res]
    print('회전당 이동 크기: %s | 평균 %.3f m' % (' '.join('%.3f' % v for v in m), sum(m) / len(m)))
