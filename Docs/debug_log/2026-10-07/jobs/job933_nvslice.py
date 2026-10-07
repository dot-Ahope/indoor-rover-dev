#!/usr/bin/env python3
"""10-07 §16: 상자 시험 bag(bag_box1)의 nvblox 슬라이스로 — 같은 장면에서 nvblox 가 '가까이서 기억(C1)'·'치운 뒤 갱신(C2)' 을 만족했나(읽기만).
   상자 ② 자리(map x 1.05~1.35, y −0.30~+0.10)를 슬라이스(odom 프레임) 좌표로 옮겨 거리 ≤ 0.05 m 인 칸 수를 2 s 마다, 로버 위치와 함께."""
import math, numpy as np, rosbag2_py, time
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_box1', storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}; print('slice 형:', types.get('/nvblox_node/static_map_slice'))
r.set_filter(rosbag2_py.StorageFilter(topics=['/nvblox_node/static_map_slice', '/tf']))
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo = ob = None; last = 0
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9; m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        for x in m.transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): mo = v
            elif k == ('odom', 'base_link'): ob = v
        continue
    if t - last < 2 or mo is None or ob is None: continue
    last = t; W, H = m.width, m.height; res = m.resolution; ox, oy = m.origin.x, m.origin.y; d = np.array(m.data, np.float32).reshape(H, W)
    c, s = math.cos(mo[2]), math.sin(mo[2]); n = 0; tot = 0
    for X in np.arange(1.075, 1.35, 0.05):
        for Y in np.arange(-0.275, 0.10, 0.05):
            dx, dy = X - mo[0], Y - mo[1]; qx, qy = c * dx + s * dy, -s * dx + c * dy   # map → odom
            i, j = int((qx - ox) / res), int((qy - oy) / res)
            if 0 <= i < W and 0 <= j < H:
                tot += 1; v = d[j, i]; n += int(v <= 0.05 and v != m.unknown_value)
    rx, ry = mo[0] + c * ob[0] - s * ob[1], mo[1] + s * ob[0] + c * ob[1]
    print('%s 로버 map (%.2f, %.2f) | 상자 ② 자리 nvblox 장애물 칸 %2d / %d' % (time.strftime('%H:%M:%S', time.localtime(t)), rx, ry, n, tot))
