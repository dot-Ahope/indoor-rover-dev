#!/usr/bin/env python3
"""odom 이 옆 이동을 덜 세는 원인 (2026-09-18). 로버는 움직이지 않는다. 인자: BAG GOAL_EPOCH [BAG GOAL_EPOCH ...]
  SLAM 이 map->odom 을 고칠 때마다 그 보정이 로버 위치를 얼마나 옮겼는지를 **로버 몸체 기준 앞(δf)·옆(δl, +왼쪽)·방향(δψ)** 으로
  나누고, 직전 보정 이후 odom 이 센 이동(Δs 거리, Δψ 회전)과 대조한다.
    - δl 이 회전량 Δψ 에 비례 → 회전 중 **옆미끄럼**(EKF 가 휠 vy=0 을 σ 1 cm/s 로 믿어 못 셈)
    - δl 이 거리 Δs 에 비례·회전 무관 → 방향 오차 누적
    - δψ 가 Δψ 에 비례 → 자이로/휠 회전 스케일 오차,  δf 가 Δs 에 비례 → 전진 스케일 오차
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def load(bag, G):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    mo, ob = [], []
    while r.has_next():
        topic, data, ts = r.read_next()
        if topic != '/tf':
            continue
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    mo.sort(); ob.sort()
    return np.array(mo), np.array(ob)


def odom_at(ob, t):
    ts = ob[:, 0]; k = min(max(bisect.bisect_left(ts, t), 1), len(ts) - 1)
    a, b = ob[k - 1], ob[k]; w = 0.0 if b[0] == a[0] else min(max((t - a[0]) / (b[0] - a[0]), 0), 1)
    return a[1] + w * (b[1] - a[1]), a[2] + w * (b[2] - a[2]), a[3] + w * wrap(b[3] - a[3])


def apply(M, p):
    c, s = math.cos(M[3]), math.sin(M[3])
    return M[1] + c * p[0] - s * p[1], M[2] + s * p[0] + c * p[1], M[3] + p[2]


rows_all = []
print('%-5s | 보정 %3s 회 | 합 δf %+6s δl %+6s δψ %+6s | odom 이동 Δs %5s 회전 Σ|Δψ| %5s | 회귀 δl = a·Δψ + b·Δs (R²) | δψ = c·Δψ | 직선/회전 구간 δl/m' % ('run', '', 'm', 'm', '°', 'm', '°'))
args = sys.argv[1:]
for k in range(0, len(args), 2):
    bag, G = args[k], float(args[k + 1]); name = bag.split('_')[-1]
    mo, ob = load(bag, G)
    obd = ob[ob[:, 0] > -1]
    tend = obd[-1, 0]
    # 보정 시점: map->odom 이 바뀐 곳 (0.5 mm 또는 0.01° 넘게)
    idx = [0]
    for i in range(1, len(mo)):
        j = idx[-1]
        if math.hypot(mo[i, 1] - mo[j, 1], mo[i, 2] - mo[j, 2]) > 0.0005 or abs(wrap(mo[i, 3] - mo[j, 3])) > math.radians(0.01):
            idx.append(i)
    rows = []
    for a, b in zip(idx, idx[1:]):
        t0, t1 = mo[a, 0], mo[b, 0]
        if t1 < 0 or t0 > tend:
            continue
        p = odom_at(ob, t1)
        before = apply(mo[a], p); after = apply(mo[b], p)
        dx, dy = after[0] - before[0], after[1] - before[1]; yawm = before[2]
        df = dx * math.cos(yawm) + dy * math.sin(yawm); dl = -dx * math.sin(yawm) + dy * math.cos(yawm)
        dpsi = wrap(mo[b, 3] - mo[a, 3])
        seg = ob[(ob[:, 0] >= t0) & (ob[:, 0] <= t1)]
        if len(seg) < 2:
            continue
        ds = float(np.sum(np.hypot(np.diff(seg[:, 1]), np.diff(seg[:, 2]))))
        dps = wrap(seg[-1, 3] - seg[0, 3])
        rows.append((t1, df, dl, dpsi, ds, dps))
    R = np.array(rows)
    rows_all.append(R)
    A = np.stack([R[:, 5], R[:, 4]], 1); coef, *_ = np.linalg.lstsq(A, R[:, 2], rcond=None)
    pred = A @ coef; r2 = 1 - np.sum((R[:, 2] - pred) ** 2) / max(np.sum((R[:, 2] - R[:, 2].mean()) ** 2), 1e-12)
    c = float(np.sum(R[:, 5] * R[:, 3]) / max(np.sum(R[:, 5] ** 2), 1e-12))
    st = np.abs(R[:, 5]) < math.radians(2); tu = ~st
    lps = R[st, 2].sum() / max(R[st, 4].sum(), 1e-6); lpt = R[tu, 2].sum() / max(R[tu, 4].sum(), 1e-6)
    print('%-5s | %3d | %+6.3f %+6.3f %+6.2f | %5.2f %6.1f | a %+.3f m/rad, b %+.3f m/m (%.2f) | c %+.3f | 직선 %+.3f (%.2f m) / 회전 %+.3f (%.2f m)' % (
        name, len(R), R[:, 1].sum(), R[:, 2].sum(), math.degrees(R[:, 3].sum()), R[:, 4].sum(), math.degrees(np.abs(R[:, 5]).sum()),
        coef[0], coef[1], r2, c, lps, R[st, 4].sum(), lpt, R[tu, 4].sum()))

R = np.concatenate(rows_all)
A = np.stack([R[:, 5], R[:, 4]], 1); coef, *_ = np.linalg.lstsq(A, R[:, 2], rcond=None)
pred = A @ coef; r2 = 1 - np.sum((R[:, 2] - pred) ** 2) / np.sum((R[:, 2] - R[:, 2].mean()) ** 2)
a1, *_ = np.linalg.lstsq(R[:, 5:6], R[:, 2], rcond=None); p1 = R[:, 5:6] @ a1; r2a = 1 - np.sum((R[:, 2] - p1) ** 2) / np.sum((R[:, 2] - R[:, 2].mean()) ** 2)
b1, *_ = np.linalg.lstsq(R[:, 4:5], R[:, 2], rcond=None); p2 = R[:, 4:5] @ b1; r2b = 1 - np.sum((R[:, 2] - p2) ** 2) / np.sum((R[:, 2] - R[:, 2].mean()) ** 2)
print('통합 %d 보정: δl = %+.4f·Δψ %+.4f·Δs (R² %.2f) | Δψ 만 R² %.2f (a %+.4f m/rad) | Δs 만 R² %.2f (b %+.4f m/m)' % (len(R), coef[0], coef[1], r2, r2a, a1[0], r2b, b1[0]))
print('  해석: a<0 이면 왼쪽 회전(Δψ>0) 때 SLAM 이 로버를 오른쪽으로 옮김 = odom 이 오른쪽 이동을 덜 셈(또는 왼쪽을 더 셈)')
# 회전 방향별 δl 평균 (회전량 1 rad 당)
for lab, sel in (('왼쪽 회전 Δψ>+2°', R[:, 5] > math.radians(2)), ('오른쪽 회전 Δψ<-2°', R[:, 5] < -math.radians(2)), ('직선 |Δψ|<2°', np.abs(R[:, 5]) < math.radians(2))):
    if sel.any():
        print('  %-18s %3d 보정: Σδl %+.3f m, ΣΔψ %+.1f°, ΣΔs %.2f m → δl/rad %+.3f, δl/m %+.3f' % (lab, sel.sum(), R[sel, 2].sum(), math.degrees(R[sel, 5].sum()), R[sel, 4].sum(),
              R[sel, 2].sum() / (R[sel, 5].sum() if abs(R[sel, 5].sum()) > 1e-3 else float('nan')), R[sel, 2].sum() / max(R[sel, 4].sum(), 1e-6)))
