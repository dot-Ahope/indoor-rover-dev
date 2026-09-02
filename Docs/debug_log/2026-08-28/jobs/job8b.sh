#!/bin/bash
# 재스탬프+slam튜닝 배포 → lidar/slam 재시작 → 스캔 지연 재측정(개선 확인)
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/*.py
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -2
source ~/ros2_ws/install/setup.bash
echo "===lidar/slam 재시작 (재스탬프 노드 포함)==="
pkill -f rplidar_node 2>/dev/null; pkill -f scan_restamp 2>/dev/null; pkill -f "lidar.launch" 2>/dev/null; pkill -f slam_toolbox 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup lidar.launch.py > /tmp/lidar.log 2>&1 &
sleep 8
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 10
echo "===노드/토픽==="; ros2 node list | grep -E "scan_restamp|rplidar|slam" | tr '\n' ' '; echo
echo "  /scan_raw: $(timeout 4 ros2 topic hz /scan_raw 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
echo "  /scan:     $(timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
echo "===재스탬프 전/후 지연 비교==="
python3 - << 'PY'
import time, statistics, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s):
        super().__init__('t'); s.raw=[]; s.new=[]
        s.create_subscription(LaserScan,'/scan_raw',lambda m:s.raw.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9)),qos_profile_sensor_data)
        s.create_subscription(LaserScan,'/scan',lambda m:s.new.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9)),qos_profile_sensor_data)
rclpy.init(); n=A(); e=time.time()+6
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
if n.raw: print(f"  /scan_raw (원시) now-stamp 평균 = {statistics.mean(n.raw)*1000:+.1f}ms")
if n.new: print(f"  /scan (재스탬프) now-stamp 평균 = {statistics.mean(n.new)*1000:+.1f}ms  (스윕중앙 보정 → ~47ms 감소 기대)")
n.destroy_node(); rclpy.shutdown()
PY
echo "===slam TF (재확인)==="; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation" | head -1
echo "===slam 파라미터 확인==="
for p in minimum_travel_heading minimum_time_interval; do echo -n "  $p: "; ros2 param get /slam_toolbox $p 2>/dev/null | tail -1; done
