#!/usr/bin/env python3
"""09-29 §3.2: L2 회전 2 안전 정지 때 가장 가까운 라이다 점이 **바닥(map) 어디**였는지, 그리고 시작 때 여유 측정의
   가까운 물체(오른쪽 0.58·뒤왼 0.70 m)와 같은 것인지 확인한다. 사용자: 가까운 물체는 사용자가 앉은 의자, 시작 때 로버 왼쪽 뒤.
   방법: bag 의 /tf(map→odom→base_link)·/tf_static(base_link→laser)로 스캔 점을 map 좌표로 바꾼 뒤,
         L1 첫 정지 자세(첫 시작 차체) 기준 좌표(앞+/왼+)로 표시한다. 가까운 점은 차체 중심 기준 1.0 m 안, 5 cm 격자로 묶어 요약.
   인자: 없음 (/tmp/bag_l1, /tmp/bag_l2)"""
import math
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def read(bag):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    scans, mo, ob, cmd, l2b = [], [], [], [], None
    while r.has_next():
        tp, data, ts = r.read_next(); t = ts * 1e-9
        if tp not in ('/tf', '/tf_static', '/scan', '/cmd_vel'): continue
        m = deserialize_message(data, get_message(types[tp]))
        if tp == '/scan': scans.append((t, m))
        elif tp == '/cmd_vel': cmd.append((t, m.angular.z))
        else:
            for tr in m.transforms:
                p, q = tr.transform.translation, tr.transform.rotation
                v = (t, p.x, p.y, yaw(q))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(v)
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(v)
                elif tr.child_frame_id in ('laser', 'lidar', 'laser_frame', 'lidar_link') and l2b is None: l2b = v
    return scans, mo, ob, cmd, l2b


def at(lst, t):
    ts = [x[0] for x in lst]; k = int(np.searchsorted(ts, t)); return lst[min(max(k, 0), len(lst) - 1)]


def compose(a, b):
    x, y, th = a; c, s = math.cos(th), math.sin(th)
    return (x + c * b[0] - s * b[1], y + s * b[0] + c * b[1], th + b[2])


def pose_map(mo, ob, t):
    a = at(mo, t); b = at(ob, t); return compose(a[1:], b[1:])


def pts_map(scan, pose, l2b):
    rs = np.array(scan.ranges); an = scan.angle_min + np.arange(len(rs)) * scan.angle_increment
    ok = np.isfinite(rs) & (rs > scan.range_min) & (rs < 6.0)
    lx, ly = rs[ok] * np.cos(an[ok]), rs[ok] * np.sin(an[ok])
    lp = pose if l2b is None else compose(pose, l2b[1:])
    c, s = math.cos(lp[2]), math.sin(lp[2])
    return np.c_[lp[0] + c * lx - s * ly, lp[1] + s * lx + c * ly]


def to_start(P, st):
    c, s = math.cos(st[2]), math.sin(st[2]); d = P - np.array(st[:2])
    return np.c_[c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1]]


def near(P, center, rmax=1.0):
    d = np.hypot(P[:, 0] - center[0], P[:, 1] - center[1]); k = np.argsort(d)
    return [(d[i], P[i]) for i in k if d[i] < rmax]


s1, mo1, ob1, cmd1, l2b = read('/tmp/bag_l1')
s2, mo2, ob2, cmd2, _ = read('/tmp/bag_l2')
print('라이다 고정 변환:', 'base_link→(%.3f, %.3f, %.1f°)' % (l2b[1], l2b[2], math.degrees(l2b[3])) if l2b else '없음(차체=라이다로 가정)')
t0 = next(t for t, w in cmd1 if abs(w) > 0.01) - 1.0            # L1 첫 회전 직전
ST = pose_map(mo1, ob1, t0)
print('L1 시작 자세(map): (%.3f, %.3f, %.1f°)' % (ST[0], ST[1], math.degrees(ST[2])))
sc0 = at(s1, t0)[1]; P0 = to_start(pts_map(sc0, ST, l2b), ST)
print('\n[시작 때] 차체 중심 1.0 m 안 가까운 점(첫 시작 차체 기준 앞+/왼+):')
for d, p in near(P0, (0, 0))[:1]: print('  최근접 %.2f m at (%+.2f, %+.2f)' % (d, p[0], p[1]))
for lab, ang in (('오른(−90°)', -90), ('뒤왼(135°)', 135), ('왼(90°)', 90), ('뒤오른(−135°)', -135)):
    a = np.degrees(np.arctan2(P0[:, 1], P0[:, 0])); m = np.abs((a - ang + 180) % 360 - 180) < 22.5
    if m.any():
        d = np.hypot(P0[m, 0], P0[m, 1]); i = np.argmin(d); print('  %-12s 최근접 %.2f m at (%+.2f, %+.2f)' % (lab, d[i], P0[m][i, 0], P0[m][i, 1]))
# L2 회전 2 정지 순간: 마지막 회전 구간의 끝
segs = []
for t, w in cmd2:
    if abs(w) > 0.01:
        if segs and t - segs[-1][1] < 0.5: segs[-1][1] = t
        else: segs.append([t, t])
te = segs[-1][1]
PE = pose_map(mo2, ob2, te); PEs = to_start(np.array([PE[:2]]), ST)[0]
print('\n[L2 회전 2 정지 %.1f s] 차체 중심(첫 시작 기준) (%+.3f, %+.3f), 방향 %+.1f°' % (te - segs[-1][0], PEs[0], PEs[1], math.degrees(PE[2] - ST[2])))
sc = at(s2, te)[1]; PP = to_start(pts_map(sc, PE, l2b), ST)
nn = near(PP, PEs)
print('  그 순간 중심에서 가까운 점(첫 시작 차체 좌표):')
for d, p in nn[:5]: print('    %.2f m at (%+.2f, %+.2f)' % (d, p[0], p[1]))
# 정지 때 최근접 점이 시작 때도 같은 자리에 있었나(바닥 고정 물체인가)
if nn:
    q = nn[0][1]; dd = np.hypot(P0[:, 0] - q[0], P0[:, 1] - q[1]).min()
    print('  → 그 점과 시작 때 스캔의 가장 가까운 점 거리 %.2f m (≤0.05 면 같은 고정 물체)' % dd)
# 시작 때와 끝 때 사이 사람·의자 움직임: 1 m 안 점 집합 비교
sE = s2[-1][1]; PEe = to_start(pts_map(sE, pose_map(mo2, ob2, s2[-1][0]), l2b), ST)
from scipy.spatial import cKDTree
kd = cKDTree(P0); dist, _ = kd.query(PEe); m = (np.hypot(PEe[:, 0], PEe[:, 1]) < 1.5) & (dist > 0.10)
print('\n[끝 스캔에서 시작 때 없던 점(첫 시작 중심 1.5 m 안, 10 cm 넘게 떨어짐)] %d 개' % m.sum())
if m.sum():
    Q = PEe[m]; print('  범위 앞뒤 %+.2f~%+.2f, 좌우 %+.2f~%+.2f' % (Q[:, 0].min(), Q[:, 0].max(), Q[:, 1].min(), Q[:, 1].max()))
