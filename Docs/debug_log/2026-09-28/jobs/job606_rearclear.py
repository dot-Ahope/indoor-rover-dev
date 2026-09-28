#!/usr/bin/env python3
"""f0a3 관찰 1 확인 (2026-09-28 §15): 목표 2 초반 후진·좌회전 동안 차체(패딩 없는 0.25×0.165)와 상자 사이 거리.
  상자 = **전역** 코스트맵 LETHAL(map 프레임, 슬립 보정 뒤에도 제자리였음 — §14) 중 map x 0.9~1.7, y −0.5~0.2.
  로버 자세 = map→odom ∘ odom→base. 1 s 간격으로 최소 거리와 그때 차체의 어느 부분(앞/뒤·좌/우)인지. 인자: BAG T_GOAL2_START"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


BAG, T2 = sys.argv[1], float(sys.argv[2])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
ob, mo, gc = [], [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/global_costmap/costmap'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        for tr in m.transforms:
            p = (t, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(p)
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(p)
    else: gc.append((t, m))


def last(arr, t):
    k = bisect.bisect_right([a[0] for a in arr], t) - 1; return arr[max(k, 0)]


best = (9, None)
for k in range(0, 26):
    t = T2 + k
    _, x, y, th = last(ob, t); _, mx, my, mth = last(mo, t)
    c0, s0 = math.cos(mth), math.sin(mth); X, Y, TH = mx + c0 * x - s0 * y, my + s0 * x + c0 * y, th + mth
    _, g = last(gc, t); d = np.asarray(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); iy, ix = np.nonzero(d >= 100)
    px = g.info.origin.position.x + (ix + 0.5) * g.info.resolution; py = g.info.origin.position.y + (iy + 0.5) * g.info.resolution
    sel = (px > 0.9) & (px < 1.7) & (py > -0.5) & (py < 0.2); px, py = px[sel] - X, py[sel] - Y
    c, s = math.cos(TH), math.sin(TH); bx, by = c * px + s * py, -s * px + c * py
    dist = np.hypot(np.maximum(np.abs(bx) - 0.25, 0), np.maximum(np.abs(by) - 0.165, 0)) - 0.025   # 셀 반 칸 보정(셀 가장자리까지)
    if not len(dist): continue
    i = int(np.argmin(dist)); part = ('앞' if bx[i] > 0.1 else '뒤' if bx[i] < -0.1 else '옆') + ('·왼' if by[i] > 0.05 else '·오른' if by[i] < -0.05 else '')
    print('  +%2d s map(%.3f, %.3f, %6.1f°) | 차체 ↔ 상자 셀 가장자리 %.3f m (%s, 차체좌표 %+.2f, %+.2f)' % (k, X, Y, math.degrees(math.atan2(math.sin(TH), math.cos(TH))), dist[i], part, bx[i], by[i]))
    if dist[i] < best[0]: best = (dist[i], k)
print('최소 %.3f m @ +%d s (전역 코스트맵 5 cm 셀 기준 — 물리 거리의 추정치)' % best)
