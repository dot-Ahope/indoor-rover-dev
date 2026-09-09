#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== /wheel_odom 퍼블리셔 목록/QoS ==="
ros2 topic info /wheel_odom --verbose 2>/dev/null | grep -aE "Publisher count|Node name|Reliability|Durability|Topic type" | sed 's/^/  /'
echo ""
echo "=== BEST_EFFORT 로 10초 수신 ==="
python3 - <<'PY'
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
rclpy.init(); n = Node('wchk'); D = []
n.create_subscription(Odometry, '/wheel_odom',
                      lambda m: D.append((time.time(),
                                          m.header.stamp.sec + m.header.stamp.nanosec*1e-9,
                                          m.pose.pose.position.x, m.pose.pose.position.y,
                                          m.twist.twist.linear.x, m.twist.twist.angular.z)),
                      qos_profile_sensor_data)
t0 = time.time()
while time.time()-t0 < 10: rclpy.spin_once(n, timeout_sec=0.1)
if not D:
    print("  수신 0 (BEST_EFFORT 로도 못 받음)")
else:
    a, b = D[0], D[-1]
    print("  수신 %d (%.1f Hz)" % (len(D), len(D)/(b[0]-a[0]+1e-9)))
    print("  보드 pose x %.3f -> %.3f (dx %+.4f), y %.3f -> %.3f" % (a[2], b[2], b[2]-a[2], a[3], b[3]))
    print("  |v| max %.4f  |w| max %.4f  (정지 상태이므로 0 이어야 정상)"
          % (max(abs(r[4]) for r in D), max(abs(r[5]) for r in D)))
    print("  헤더 stamp 끝 %.3f, host %.3f, 오프셋 %+.3f s" % (b[1], b[0], b[1]-b[0]))
rclpy.shutdown()
PY
echo ""
echo "=== ekf 설정 (odom0 관련) ==="
grep -nE "odom0|imu0|two_d_mode|frequency|differential|relative|publish_tf" ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/ekf.yaml 2>/dev/null | head -30
echo ""
echo "=== sensors.log 중 ekf/conditioner 경고 ==="
grep -aiE "ekf|conditioner" /tmp/sensors.log | grep -aiE "warn|error|jump|timestamp|extrapol|reset" | tail -12
