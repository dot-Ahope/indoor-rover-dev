#!/bin/bash
# 수정 배포 상태 + 배터리 확인 (회전 테스트 가능 여부)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===scan_restamp 노드/토픽==="
ros2 node list | grep -E "scan_restamp|slam|rplidar" | tr '\n' ' '; echo
echo -n "  /scan_raw: "; timeout 4 ros2 topic hz /scan_raw 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo -n "  /scan:     "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo "===스캔 지연 (재스탬프 효과 유지 확인)==="
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
if n.r: print(f"  /scan_raw {statistics.mean(n.r)*1000:.0f}ms  →  /scan {statistics.mean(n.n)*1000:.0f}ms (재스탬프)")
n.destroy_node(); rclpy.shutdown()
PY
echo "===slam 파라미터==="
for p in minimum_travel_heading minimum_time_interval; do echo -n "  $p: "; ros2 param get /slam_toolbox $p 2>/dev/null | tail -1; done
echo "===배터리·세션==="
echo -n "  battery: "; timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NONE
echo -n "  wheel_odom: "; timeout 5 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
