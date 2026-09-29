#!/usr/bin/env python3
"""09-29 §12: F0 나머지 코스 계획용 — bag 의 마지막 /map(OccupancyGrid)을 npz 로 저장(해상도·원점·격자).
   인자: BAG OUT.npz"""
import sys
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
last = None
while r.has_next():
    tp, data, ts = r.read_next()
    if tp == '/map': last = data
m = deserialize_message(last, get_message(types['/map']))
g = np.array(m.data, dtype=np.int8).reshape(m.info.height, m.info.width)
o = m.info.origin.position
np.savez_compressed(sys.argv[2], grid=g, res=m.info.resolution, ox=o.x, oy=o.y)
print('map %d×%d, 해상도 %.3f m, 원점 (%.2f, %.2f) | 점유 %d · 빈 %d · 미지 %d 셀'
      % (m.info.width, m.info.height, m.info.resolution, o.x, o.y, (g > 50).sum(), (g == 0).sum(), (g < 0).sum()))
