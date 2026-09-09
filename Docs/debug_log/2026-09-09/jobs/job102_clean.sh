#!/bin/bash
# 중복 프로세스 완전 정리 후, base 만 남긴 상태에서 /wheel_odom 을 60초 연속 관측.
# pkill 패턴은 for 루프로 하나씩 (ERE 에서 "a\|b" 는 리터럴 파이프라 매칭 실패 — job97/100/101 의 버그)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

echo "=== 정리 전 프로세스 수 ==="
for p in ekf_node sensor_conditioner realsense rplidar slam_toolbox foxglove controller_server planner_server bt_navigator velocity_smoother behavior_server stuck_monitor scan_deskew; do
  c=$(pgrep -fc "$p" 2>/dev/null || echo 0); [ "$c" != "0" ] && printf "  %-20s %s\n" "$p" "$c"
done

echo "=== 종료 (base/agent 는 유지) ==="
for p in "navigation_launch" "controller_server" "planner_server" "bt_navigator" "behavior_server" \
         "velocity_smoother" "smoother_server" "waypoint_follower" "lifecycle_manager_navigation" \
         "stuck_monitor" "slam.launch" "slam_toolbox" "sensors.launch" "realsense" "rplidar" \
         "scan_deskew" "ekf_node" "sensor_conditioner" "foxglove"; do
  pkill -9 -f "$p" 2>/dev/null
done
sleep 6
echo "=== 정리 후 프로세스 수 ==="
LEFT=0
for p in ekf_node sensor_conditioner realsense rplidar slam_toolbox foxglove controller_server planner_server bt_navigator velocity_smoother behavior_server stuck_monitor scan_deskew; do
  c=$(pgrep -fc "$p" 2>/dev/null || echo 0); [ "$c" != "0" ] && { printf "  %-20s %s (잔존)\n" "$p" "$c"; LEFT=1; }
done
[ "$LEFT" = "0" ] && echo "  전부 종료됨"
echo "  agent: $(docker ps --format '{{.Names}} {{.Status}}' | grep -a microros || echo 없음)"
echo "  ros 노드: $(ros2 node list 2>/dev/null | tr '\n' ' ')"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"

echo ""
echo "=== base 단독 상태에서 /wheel_odom 60초 연속 관측 (5초 버킷) ==="
python3 - <<'PY'
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray
rclpy.init(); n = Node('longobs')
C = {'odom': 0, 'imu': 0, 'stat': 0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
print("   구간      odom    imu   status")
t0 = time.time()
for b in range(12):
    base = dict(C); tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    print("  %3.0f-%3.0fs  %6.2f %6.2f %6.2f"
          % (b*5, b*5+5, (C['odom']-base['odom'])/el, (C['imu']-base['imu'])/el, (C['stat']-base['stat'])/el), flush=True)
rclpy.shutdown()
PY
