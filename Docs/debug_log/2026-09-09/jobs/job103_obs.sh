#!/bin/bash
# 깨끗한 상태(base+sensors+slam, 중복 없음)에서 보드 링크 60초 연속 관측. 아무것도 죽이지 않는다.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 프로세스 중복 점검 ==="
for p in ekf_node sensor_conditioner realsense rplidar slam_toolbox foxglove scan_deskew controller_server; do
  c=$(pgrep -fc "$p" 2>/dev/null || echo 0); printf "  %-20s %s\n" "$p" "$c"
done
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  보드 노드: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음 — RESET 이 안 먹었습니다')"
echo ""
echo "=== 보드 링크 60초 연속 관측 (5초 버킷) ==="
python3 - <<'PY'
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray
from sensor_msgs.msg import BatteryState
rclpy.init(); n = Node('obs103')
C = {'odom': 0, 'imu': 0, 'stat': 0, 'bat': 0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
n.create_subscription(BatteryState, '/battery', mk('bat'), qos_profile_sensor_data)
print("   구간      odom    imu   status  battery   (기대 29 / 29 / 5.0 / 1.0)")
for b in range(12):
    base = dict(C); tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    print("  %3.0f-%3.0fs  %6.2f %6.2f %7.2f %7.2f"
          % (b*5, b*5+5, (C['odom']-base['odom'])/el, (C['imu']-base['imu'])/el,
             (C['stat']-base['stat'])/el, (C['bat']-base['bat'])/el), flush=True)
rclpy.shutdown()
PY
echo ""
echo "=== EKF 입력 확인 ==="
printf "  %-30s " /wheel_odom/conditioned; timeout 8 ros2 topic hz /wheel_odom/conditioned 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
printf "  %-30s " /odometry/filtered;      timeout 8 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
echo -n "  odom->base: "; timeout 5 ros2 run tf2_ros tf2_echo odom base_link 2>/dev/null | grep -aE "Translation" | head -1
