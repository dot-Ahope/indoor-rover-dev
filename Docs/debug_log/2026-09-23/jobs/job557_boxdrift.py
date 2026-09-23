#!/usr/bin/env python3
"""F0-a 상자 이동 검증 (09-23): 3 s 간격으로 로컬(odom)·전역(map) 코스트맵의 상자 LETHAL(100) 셀 범위를 map 좌표로, 그리고 map→odom.
   상자 영역 = map x 0.95~1.55, y −0.40~0.15. 로컬 이동량이 map→odom 변화와 같으면 'odom 고정 층 + SLAM 보정' 가설 확정. 인자: BAG T0 T1"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
BAG, T0, T1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
mo, lc, gc = [], [], []
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp not in ('/tf', '/local_costmap/costmap', '/global_costmap/costmap'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        for tr in m.transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((t, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
    elif tp.startswith('/local'): lc.append((t, m))
    else: gc.append((t, m))
def last(arr, t):
    k = bisect.bisect_right([a[0] for a in arr], t) - 1; return arr[max(k, 0)]
def box(g, tf):
    d = np.asarray(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); iy, ix = np.nonzero(d >= 100); res = g.info.resolution
    x = g.info.origin.position.x + (ix + 0.5) * res; y = g.info.origin.position.y + (iy + 0.5) * res
    if tf:
        _, tx, ty, th = tf; c, s = math.cos(th), math.sin(th); x, y = tx + c * x - s * y, ty + s * x + c * y
    k = (x > 0.95) & (x < 1.55) & (y > -0.40) & (y < 0.15)
    return (x[k].min(), x[k].max(), y[k].min(), y[k].max(), k.sum()) if k.any() else None
print('   t  | map→odom x    y     yaw  | 로컬 상자(map) x범위 / y범위 / 셀 | 전역 상자(map) x범위 / y범위 / 셀')
t = T0
while t <= T1:
    tf = last(mo, t); L = box(last(lc, t)[1], tf); G = box(last(gc, t)[1], None)
    f = lambda b: '%.3f~%.3f / %+.3f~%+.3f / %2d' % b if b else '없음'
    print('%5.1f | %+.3f %+.3f %+5.2f° | %s | %s' % (t - T0, tf[1], tf[2], math.degrees(tf[3]), f(L), f(G))); t += 3
