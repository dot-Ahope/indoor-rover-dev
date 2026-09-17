#!/bin/bash
source /opt/ros/humble/setup.bash; cd /tmp
python3 /tmp/job327_mp2why.py /tmp/bag_mp6 0 0 0 54 2>&1 | grep -av 'Opened database' | sed -n '/=== t=54/,$p' | cut -c1-60
python3 - <<'PY'
import math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from nav_msgs.msg import OccupancyGrid
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_mp6', storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
last = None
while r.has_next():
    topic, data, ts = r.read_next()
    if topic == '/global_costmap/costmap': last = deserialize_message(data, OccupancyGrid)
g = last; res = g.info.resolution; d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)
def c(x, y):
    i = int((x - g.info.origin.position.x) / res); j = int((y - g.info.origin.position.y) / res); return int(d[j, i])
print('전역 코스트맵(마지막) 목표 (2.20, 0.01) 셀 비용 %d' % c(2.2, 0.01))
print('목표 주변 비용 (y 행 +0.30 → -0.40, x 1.90 → 2.50):')
for y in np.arange(0.30, -0.41, -0.05):
    print('  %+.2f ' % y + ' '.join('%3d' % c(x, y) for x in np.arange(1.90, 2.51, 0.05)))
jj, ii = np.where(d >= 100); X = g.info.origin.position.x + (ii + .5) * res; Y = g.info.origin.position.y + (jj + .5) * res
s = (X > 1.8) & (X < 2.8) & (Y > -0.8) & (Y < 0.6)
print('목표 근처 LETHAL 셀 x %.2f~%.2f, y %+.2f~%+.2f, %d셀; 목표에서 최근접 %.3f m' % (X[s].min(), X[s].max(), Y[s].min(), Y[s].max(), s.sum(), np.hypot(X[s] - 2.2, Y[s] - 0.01).min()))
PY
