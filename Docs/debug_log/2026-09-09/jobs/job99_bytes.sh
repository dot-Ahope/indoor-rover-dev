#!/bin/bash
# 보드가 UART 로 실제 몇 바이트를 보내는지 측정 → 펌웨어 발행 실패 vs agent 드롭 을 가른다.
#   기대치: odom 720B x 29Hz + imu ~330B x 29Hz ≈ 30 kB/s
#           battery/status/mag 만이면 ≈ 2 kB/s
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
PID=$(pgrep -f micro_ros_agent | head -1)
echo "agent pid = ${PID:-없음}"
if [ -n "$PID" ]; then
  A=$(grep '^rchar' /proc/$PID/io 2>/dev/null | awk '{print $2}')
  W=$(grep '^wchar' /proc/$PID/io 2>/dev/null | awk '{print $2}')
  sleep 10
  B=$(grep '^rchar' /proc/$PID/io 2>/dev/null | awk '{print $2}')
  X=$(grep '^wchar' /proc/$PID/io 2>/dev/null | awk '{print $2}')
  echo "  UART 수신(보드->젯슨): $(( (B-A)/10 )) B/s"
  echo "  UART 송신(젯슨->보드): $(( (X-W)/10 )) B/s"
fi
echo ""
echo "=== BEST_EFFORT 로 30초간 /wheel_odom, /imu/data_raw, /rover/status 동시 수신 ==="
python3 - <<'PY'
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray
rclpy.init(); n = Node('bytechk'); C = {'odom': 0, 'imu': 0, 'stat': 0}
last = {}
def mk(k):
    def cb(m):
        C[k] += 1; last[k] = m
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
t0 = time.time()
while time.time()-t0 < 30: rclpy.spin_once(n, timeout_sec=0.1)
el = time.time()-t0
for k, exp in (('odom', 29), ('imu', 29), ('stat', 5)):
    print("  %-6s 수신 %4d  = %5.2f Hz  (기대 %d)" % (k, C[k], C[k]/el, exp))
if 'stat' in last:
    s = last['stat'].status
    print("  status level=%s" % [ord(x.level) if isinstance(x.level, str) else x.level for x in s])
    for st in s:
        print("    %s: %s" % (st.name, st.message))
        for kv in st.values: print("      %s = %s" % (kv.key, kv.value))
rclpy.shutdown()
PY
