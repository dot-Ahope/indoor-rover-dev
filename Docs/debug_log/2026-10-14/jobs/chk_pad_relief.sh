#!/bin/bash
# (10-14 §8.2) pad_relief 정지 시험: 가짜 컨트롤러 실패 로그로 켜짐·시간 한도 복귀·종료 때 복귀를 확인 — 로버 안 움직임(주행 명령 없음)
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f pad_relief.py 2>/dev/null; rm -f /tmp/pad_relief.log
python3 -u /tmp/pad_relief.py > /tmp/pad_relief_node.log 2>&1 & NP=$!
rm -f /tmp/pad_relief_step4; (while [ ! -f /tmp/pad_relief_step4 ]; do sleep 0.2; done; kill -TERM $NP) &
python3 -u - <<'PY'
import time, rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Log
from geometry_msgs.msg import PolygonStamped
rclpy.init(); n = Node('chk_pad_relief'); pub = n.create_publisher(Log, '/rosout', 100); fp = {'s': None}
def cb(m):
    P = [(p.x, p.y) for p in m.polygon.points]; e = sorted(((P[i][0] - P[(i + 1) % len(P)][0]) ** 2 + (P[i][1] - P[(i + 1) % len(P)][1]) ** 2) ** 0.5 for i in range(len(P))); fp['s'] = e[0]
n.create_subscription(PolygonStamped, '/local_costmap/published_footprint', cb, 10)
def spin(sec):
    t = time.time()
    while time.time() - t < sec: rclpy.spin_once(n, timeout_sec=0.05)
def fake(k):
    for _ in range(k):
        m = Log(); m.stamp = n.get_clock().now().to_msg(); m.level = 40; m.name = 'controller_server'; m.msg = 'Optimizer fail to compute path (시험용 가짜 로그)'; pub.publish(m); spin(0.2)
def short(): return -1.0 if fp['s'] is None else fp['s']
spin(6.0); print('0) 처음 짧은 변 %.3f m' % short(), flush=True)
fake(2); spin(3.5); a = short(); print('1) 가짜 2 회 뒤 %.3f m → %s' % (a, '통과(안 켜짐)' if abs(a - 0.350) < 0.003 else '실패'), flush=True)
fake(4); spin(2.0); b = short(); print('2) 가짜 4 회 뒤 2 s: %.3f m → %s' % (b, '통과(내려감)' if abs(b - 0.330) < 0.003 else '실패'), flush=True)
t = time.time(); back = None
while time.time() - t < 20:
    spin(0.5)
    if abs(short() - 0.350) < 0.003: back = time.time() - t + 2.0; break
print('3) 시간 한도 복귀: %s → %s' % ('%.1f s 뒤 %.3f m' % (back, short()) if back else '20 s 안에 복귀 안 함(%.3f m)' % short(), '통과' if back and 13 <= back <= 18 else '실패'), flush=True)
spin(3.5); fake(4); spin(2.0); c = short(); print('4a) 다시 4 회 뒤 %.3f m (내려가야 함: %s)' % (c, '예' if abs(c - 0.330) < 0.003 else '아니오'), flush=True)
open('/tmp/pad_relief_step4', 'w').write('go'); spin(4.0); d = short(); print('4b) 노드 종료 뒤 %.3f m → %s' % (d, '통과(되돌림)' if abs(c - 0.330) < 0.003 and abs(d - 0.350) < 0.003 else '실패'), flush=True)
rclpy.shutdown()
PY
sleep 1; echo "--- 노드 기록(/tmp/pad_relief.log)"; cut -d' ' -f2- /tmp/pad_relief.log; echo "남은 pad_relief 프로세스 $(pgrep -fc pad_relief.py)"
timeout 10 ros2 param get /local_costmap/local_costmap footprint_padding 2>&1 | tail -1
