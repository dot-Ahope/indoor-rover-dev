#!/bin/bash
# 중복 정리 → 단일 lidar 파이프라인 재시작 → 정지 무결성 재확인
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===전체 lidar 관련 종료==="
pkill -9 -f rplidar_node 2>/dev/null; pkill -9 -f scan_restamp 2>/dev/null; pkill -9 -f scan_deskew 2>/dev/null; pkill -f "lidar.launch" 2>/dev/null
sleep 3
echo "잔존: $(pgrep -af 'rplidar_node|scan_deskew|scan_restamp' | wc -l)개"
echo "===단일 lidar.launch (rplidar→scan_deskew→/scan)==="
setsid nohup ros2 launch rover_bringup lidar.launch.py > /tmp/lidar.log 2>&1 &
sleep 9
echo "  rplidar 프로세스: $(pgrep -f rplidar_node | wc -l)개 (1이어야)"
echo "  scan_deskew: $(pgrep -f scan_deskew | wc -l)개"
echo -n "  /scan_raw hz: "; timeout 4 ros2 topic hz /scan_raw 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1
echo -n "  /scan hz: "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1
echo "===정지 무결성: 같은 순간 /scan_raw vs /scan (deskew, 정지=ω<deadband → 재분류 없이 동일해야)==="
python3 - << 'PY'
import numpy as np, time, rclpy, math
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
class A(Node):
    def __init__(s):
        super().__init__('a'); s.r=None; s.n=None; s.w=None
        s.create_subscription(LaserScan,'/scan_raw',lambda m:setattr(s,'r',np.array(m.ranges,np.float32)),qos_profile_sensor_data)
        s.create_subscription(LaserScan,'/scan',lambda m:setattr(s,'n',np.array(m.ranges,np.float32)),qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',lambda m:setattr(s,'w',m.twist.twist.angular.z),qos_profile_sensor_data)
rclpy.init(); n=A(); t=time.time()
while (n.r is None or n.n is None) and time.time()<t+4: rclpy.spin_once(n,timeout_sec=0.2)
print(f"  현재 ω = {n.w:.4f} rad/s (정지 확인)" if n.w is not None else "  ω 없음")
if n.r is not None and n.n is not None:
    rv=np.isfinite(n.r).sum(); nv=np.isfinite(n.n).sum()
    both=np.isfinite(n.r)&np.isfinite(n.n); md=np.abs(n.r[both]-n.n[both]).max() if both.sum() else 0
    print(f"  raw {rv}점 / deskew {nv}점, 공통 최대거리차 {md*1000:.0f}mm")
    print(f"  → {'OK(정지 시 동일)' if abs(rv-nv)<20 and md<0.05 else '점검 필요(중복/타이밍)'}")
PY
