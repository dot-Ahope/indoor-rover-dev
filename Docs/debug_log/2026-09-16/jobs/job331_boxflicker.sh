#!/bin/bash
# 상자 셀 최대 y 의 시간 변동(게이트 창 0.186 vs 0.235 오락가락 원인): job315 를 N회 반복
BX=${1:-1.159}; BY=${2:-0.054}; N=${3:-6}
source /opt/ros/humble/setup.bash
for i in $(seq 1 $N); do
  printf "%s  상자 셀 최대 y: " "$(date +%T)"
  python3 /tmp/job315_boxcells.py $BX $BY 2>&1 | grep -av '^\[' | tail -1
  sleep 4
done
echo "--- 로컬 코스트맵 상자 주변 셀 (y 0.15~0.30, x 1.05~1.35) 값 ---"
python3 - "$BX" "$BY" <<'PY'
import sys, rclpy, numpy as np
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
bx, by = float(sys.argv[1]), float(sys.argv[2])
rclpy.init(); n = Node('j331'); got = {}
def cb(m): got['g'] = m
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', cb, 1)
import time; t0 = time.time()
while 'g' not in got and time.time() - t0 < 10: rclpy.spin_once(n, timeout_sec=0.5)
g = got['g']; res = g.info.resolution; ox, oy = g.info.origin.position.x, g.info.origin.position.y
d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)
ys = np.arange(0.30, 0.10, -res); xs = np.arange(1.05, 1.36, res)
print('   y\x ' + ' '.join('%5.2f' % x for x in xs))
for y in ys:
    row = []
    for x in xs:
        i = int((x - ox) / res); j = int((y - oy) / res)
        row.append('%5d' % d[j, i] if 0 <= i < g.info.width and 0 <= j < g.info.height else '    ?')
    print('%5.2f ' % y + ' '.join(row))
print('(로컬 코스트맵은 odom 프레임; map->odom 0 이라 동일)')
rclpy.shutdown()
PY
