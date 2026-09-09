#!/bin/bash
# 부하 단계별 보드 토픽 주기 측정 — micro-ROS 링크 붕괴가 CPU 경합 때문인지 가른다.
# 단계: (1) base 만 → (2) +sensors → (3) +slam → (4) +nav2
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

cat > /tmp/_meas.py <<'PY'
import rclpy, time, sys
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray
rclpy.init(); n = Node('meas'); C = {'odom': 0, 'imu': 0, 'stat': 0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
T = float(sys.argv[1]) if len(sys.argv) > 1 else 15.0
t0 = time.time()
while time.time()-t0 < T: rclpy.spin_once(n, timeout_sec=0.05)
el = time.time()-t0
print("    odom %5.2f Hz | imu %5.2f Hz | status %5.2f Hz" % (C['odom']/el, C['imu']/el, C['stat']/el))
rclpy.shutdown()
PY

step() {
  echo "  load: $(cut -d' ' -f1-3 /proc/loadavg) | CPU idle: $(top -bn2 -d1 | awk '/^%Cpu/{v=$8} END{print v}')%"
  python3 /tmp/_meas.py 15
}

echo "=== (1) base 만 (agent + robot_state_publisher) ==="
pkill -f "slam.launch\|slam_toolbox" 2>/dev/null
pkill -f "sensors.launch\|realsense\|rplidar\|scan_deskew\|ekf_node\|sensor_conditioner\|foxglove" 2>/dev/null
sleep 6
step

echo "=== (2) + sensors.launch (카메라/라이다/EKF/컨디셔너/foxglove) ==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 26
grep -a "gyro bias" /tmp/sensors.log | tail -1 | sed 's/^/    /'
step

echo "=== (3) + slam.launch ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 14
step

echo "=== (4) + navigation.launch ==="
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 28
step

echo ""
echo "=== 상위 CPU 소비 ==="
top -b -n2 -d1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -9 | awk '{printf "    %-18s %6s%%\n", $12, $9}'
echo "=== CPU 코어 수 / 전력 모드 ==="
nproc | sed 's/^/    코어: /'
nvpmodel -q 2>/dev/null | tr '\n' ' ' | sed 's/^/    /'; echo
