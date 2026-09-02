#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===/scan 지연 (deskew ref=end → 대폭 감소 기대)==="
python3 - << 'PY'
import time, statistics, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s):
        super().__init__('t'); s.r=[]; s.n=[]
        s.create_subscription(LaserScan,'/scan_raw',lambda m:s.r.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9)),qos_profile_sensor_data)
        s.create_subscription(LaserScan,'/scan',lambda m:s.n.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9)),qos_profile_sensor_data)
rclpy.init(); n=A(); e=time.time()+5
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
if n.r and n.n: print(f"  /scan_raw {statistics.mean(n.r)*1000:.0f}ms → /scan {statistics.mean(n.n)*1000:.0f}ms (deskew)")
PY
echo "===slam 건강성 (deskew /scan 소비 확인)==="
ros2 node list | grep -q slam_toolbox && echo "  slam 실행중" || echo "  slam 없음!"
echo -n "  /map→odom TF: "; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation" | head -1
echo "  slam 최근 경고/오류:"; grep -aiE "extrapolat|could not|timeout|error|drop" /tmp/slam.log 2>/dev/null | tail -3 || echo "  (없음)"
echo "===/scan 구독자 (slam·foxglove가 deskew /scan 받는지)==="
ros2 topic info /scan 2>/dev/null | grep -E "Subscription count|Publisher count"
