#!/bin/bash
# 고아 Nav2 프로세스 제거(에이전트·보드 세션은 건드리지 않음) 후 링크 재관측.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 고아 Nav2 제거 ==="
for p in "navigation_launch" "controller_server" "planner_server" "bt_navigator" "behavior_server" \
         "velocity_smoother" "smoother_server" "waypoint_follower" "lifecycle_manager_navigation" "stuck_monitor"; do
  pkill -9 -f "$p" 2>/dev/null
done
sleep 5
for p in controller_server planner_server bt_navigator behavior_server velocity_smoother stuck_monitor ekf_node sensor_conditioner realsense rplidar slam_toolbox foxglove; do
  printf "  %-20s %s\n" "$p" "$(pgrep -fc "$p" 2>/dev/null || echo 0)"
done
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  보드 노드: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음')"
echo ""
echo "=== 링크 60초 연속 관측 ==="
python3 - <<'PY'
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray
from sensor_msgs.msg import BatteryState
rclpy.init(); n = Node('obs104')
C = {'odom': 0, 'imu': 0, 'stat': 0, 'bat': 0, 'cond': 0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
n.create_subscription(BatteryState, '/battery', mk('bat'), qos_profile_sensor_data)
n.create_subscription(Odometry, '/wheel_odom/conditioned', mk('cond'), qos_profile_sensor_data)
print("   구간      odom    imu   status  battery  conditioned")
for b in range(12):
    base = dict(C); tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    print("  %3.0f-%3.0fs  %6.2f %6.2f %7.2f %7.2f %9.2f"
          % (b*5, b*5+5, (C['odom']-base['odom'])/el, (C['imu']-base['imu'])/el,
             (C['stat']-base['stat'])/el, (C['bat']-base['bat'])/el, (C['cond']-base['cond'])/el), flush=True)
rclpy.shutdown()
PY
echo ""
echo "=== agent 로그 최근 (세션 이후) ==="
docker logs --tail 6 microros_agent 2>&1 | sed -E 's/\x1b\[[0-9;]*m//g'
