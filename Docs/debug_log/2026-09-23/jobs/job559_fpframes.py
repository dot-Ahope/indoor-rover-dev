#!/usr/bin/env python3
"""F0-a 원인 2 보강 (09-23): 복귀 구간 로컬 코스트맵 **매 프레임**에서 그 순간 자세의 풋프린트(패딩 0.01) 최대 비용과
   LETHAL 셀 수·차체↔LETHAL 최소 거리. 중단(1790141915.79) 직전·중에 풋프린트가 LETHAL 을 밟는 프레임이 있었는지. 인자: BAG"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


BAG = sys.argv[1]; TA = 1790141915.79
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
ob, lc = [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/local_costmap/costmap'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        for tr in m.transforms:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((t, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
    elif TA - 6 <= t <= TA + 14: lc.append((t, m))
FP = [(0.26, 0.175), (0.26, -0.175), (-0.26, -0.175), (-0.26, 0.175)]


def last(arr, t):
    k = bisect.bisect_right([a[0] for a in arr], t) - 1; return arr[max(k, 0)]


print('로컬맵 프레임 %d 개 (%.1f s), 평균 간격 %.2f s' % (len(lc), lc[-1][0] - lc[0][0], (lc[-1][0] - lc[0][0]) / max(len(lc) - 1, 1)))
for t, g in lc:
    d = np.asarray(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); res = g.info.resolution; ox, oy = g.info.origin.position.x, g.info.origin.position.y
    _, x, y, th = last(ob, t); c, s = math.cos(th), math.sin(th)
    cells = [(int((x + c * a - s * b - ox) / res), int((y + s * a + c * b - oy) / res)) for a, b in FP]
    mx = 0; nh = 0
    for k in range(4):
        (x0, y0), (x1, y1) = cells[k], cells[(k + 1) % 4]
        dx, dy = abs(x1 - x0), -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; err = dx + dy; cx, cy = x0, y0
        while True:
            v = int(d[cy, cx]); mx = max(mx, v); nh += v >= 100
            if cx == x1 and cy == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; cx += sx
            if e2 <= dx: err += dx; cy += sy
    iy, ix = np.nonzero(d >= 100); px = ox + (ix + 0.5) * res - x; py = oy + (iy + 0.5) * res - y
    bx, by = c * px + s * py, -s * px + c * py
    dist = np.hypot(np.maximum(np.abs(bx) - 0.26, 0), np.maximum(np.abs(by) - 0.175, 0))
    print('  %+6.2f s | 자세 (%.3f, %.3f, %.1f°) | 풋프린트 최대 %3d %s | 패딩 풋프린트↔LETHAL 최소 %.3f m | LETHAL %d' % (t - TA, x, y, math.degrees(th), mx, '★ LETHAL 밟음 %d 셀' % nh if nh else '', dist.min(), len(dist)))
