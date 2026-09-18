#!/usr/bin/env python3
"""[job431c] 큰 옆 보정(|δl|>1 cm)의 시각·당시 운동 목록 + 시간대별 누적. 원판 job431:
odom 이 옆 이동을 덜 세는 원인 (2026-09-18). 로버는 움직이지 않는다. 인자: BAG GOAL_EPOCH [T_END] ... (T_END: 목표 도착 s — 주면 그 뒤 정지 구간 보정을 뺀다; 09-18 §11 에서 추가)
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
items = []; i = 0
while i < len(args):
    bag, G = args[i], float(args[i + 1]); i += 2
    te = None
    if i < len(args) and not args[i].startswith('/'):
        te = float(args[i]); i += 1
    items.append((bag, G, te))
for bag, G, te in items:
    name = bag.split('_')[-1]
    mo, ob = load(bag, G)
    obd = ob[ob[:, 0] > -1]
    tend = obd[-1, 0] if te is None else te
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
    big = R[np.abs(R[:, 2]) > 0.01]
    print('==== %s: 보정 %d 회, Σδl %+.3f m, |δl|>1 cm %d 회 Σ %+.3f m' % (name, len(R), R[:, 2].sum(), len(big), big[:, 2].sum()))
    for r in big:
        print('   t %5.1f  δl %+.3f  δf %+.3f  δψ %+.2f°  | 직전 이후 odom Δs %.3f m Δψ %+.1f°' % (r[0], r[2], r[1], math.degrees(r[3]), r[4], math.degrees(r[5])))
    for a_, b_ in ((-1, 5), (5, 12), (12, 18), (18, 25), (25, 40)):
        sel = (R[:, 0] >= a_) & (R[:, 0] < b_)
        print('   구간 t %3d~%3d s: 보정 %2d 회, Σδl %+.3f m, Σδψ %+.2f°, odom Δs %.2f m' % (a_, b_, sel.sum(), R[sel, 2].sum(), math.degrees(R[sel, 3].sum()), R[sel, 4].sum()))
