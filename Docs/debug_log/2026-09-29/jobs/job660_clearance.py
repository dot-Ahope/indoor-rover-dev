#!/usr/bin/env python3
"""09-29 §12.2 B-b 여유: 주행 중(목표 진행 구간) 라이다 점 ↔ 차체 외곽(0.50 × 0.33 m 직사각, base_link 중심) 최소 거리.
   bag 의 /scan + /tf_static(base_link→라이다) + /tf(map→odom→base_link). 차체 안쪽 점(자기 몸·데크)은 제외.
   문 구간 = 차체 중심이 map (2.23, −0.65) 에서 0.6 m 안. 인자: BAG"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

L2, W2 = 0.25, 0.165
DOOR = (2.23, -0.65)


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
scans, mo, ob, cmd, l2b = [], [], [], [], None
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/scan', '/tf', '/tf_static', '/cmd_vel'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/scan': scans.append((t, m))
    elif tp == '/cmd_vel': cmd.append((t, m.linear.x, m.angular.z))
    else:
        for tr in m.transforms:
            p, q = tr.transform.translation, tr.transform.rotation; v = (t, p.x, p.y, yaw(q))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(v)
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(v)
            elif tr.header.frame_id == 'base_link' and 'laser' in tr.child_frame_id or tr.child_frame_id in ('lidar_link', 'laser'): l2b = v
print('라이다 고정 변환:', l2b and '(%.3f, %.3f, %.1f°)' % (l2b[1], l2b[2], math.degrees(l2b[3])))
mo.sort(); ob.sort()


def at(lst, t):
    k = bisect.bisect_left([x[0] for x in lst], t); return lst[min(max(k, 0), len(lst) - 1)]


act = [c[0] for c in cmd if abs(c[1]) > 0.005 or abs(c[2]) > 0.01]
t_on, t_off = act[0], act[-1]
res = []
for t, s in scans:
    if t < t_on or t > t_off: continue
    rs = np.array(s.ranges); an = s.angle_min + np.arange(len(rs)) * s.angle_increment
    ok = np.isfinite(rs) & (rs > s.range_min) & (rs < 4.0)
    lx, ly = rs[ok] * np.cos(an[ok]), rs[ok] * np.sin(an[ok])
    c, sn = math.cos(l2b[3]), math.sin(l2b[3])
    bx, by = l2b[1] + c * lx - sn * ly, l2b[2] + sn * lx + c * ly
    dx = np.maximum(np.abs(bx) - L2, 0); dy = np.maximum(np.abs(by) - W2, 0)
    inside = (np.abs(bx) <= L2) & (np.abs(by) <= W2)
    d = np.hypot(dx, dy)[~inside]
    if not len(d): continue
    k = int(np.argmin(d))
    A = at(mo, t); B = at(ob, t); ca, sa = math.cos(A[3]), math.sin(A[3])
    mx, my = A[1] + ca * B[1] - sa * B[2], A[2] + sa * B[1] + ca * B[2]
    res.append((t - t_on, d[k], mx, my, bx[~inside][k], by[~inside][k]))
R = np.array(res)
i = int(np.argmin(R[:, 1]))
print('주행 %.0f s, 스캔 %d 개 | 전체 최소 여유 %.3f m @ t %.1f s, 로버 map (%.2f, %.2f), 점 차체 (%+.2f, %+.2f)' % (t_off - t_on, len(R), R[i, 1], R[i, 0], R[i, 2], R[i, 3], R[i, 4], R[i, 5]))
door = R[np.hypot(R[:, 2] - DOOR[0], R[:, 3] - DOOR[1]) < 0.6]
if len(door):
    j = int(np.argmin(door[:, 1]))
    print('문 구간(중심 0.6 m 안) 스캔 %d 개 | 최소 여유 %.3f m @ t %.1f s, 로버 map (%.2f, %.2f), 점 차체 (%+.2f, %+.2f)' % (len(door), door[j, 1], door[j, 0], door[j, 2], door[j, 3], door[j, 4], door[j, 5]))
for lo, hi in ((0, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 9)):
    print('  최소 여유 %.2f~%.2f m 인 스캔 %d 개' % (lo, hi, int(((R[:, 1] >= lo) & (R[:, 1] < hi)).sum())))
