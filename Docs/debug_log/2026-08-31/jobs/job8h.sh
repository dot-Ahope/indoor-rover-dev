#!/bin/bash
# scan_deskew 배포 → lidar 재시작 → 정지 시 무결성(스캔 왜곡 없음) 확인
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/*.py
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
pkill -f "lidar.launch" 2>/dev/null; pkill -f rplidar_node 2>/dev/null; pkill -f scan_restamp 2>/dev/null; pkill -f scan_deskew 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup lidar.launch.py > /tmp/lidar.log 2>&1 &
sleep 8
echo "===노드==="; ros2 node list | grep -E "scan_deskew|rplidar" | tr '\n' ' '; echo
echo -n "  /scan_raw: "; timeout 4 ros2 topic hz /scan_raw 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo -n "  /scan:     "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo "===정지 무결성: 정지 상태에서 /scan(deskew) vs /scan_raw 점 수·거리 비교(같아야 정상)==="
python3 - << 'PY'
import numpy as np, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s):
        super().__init__('a'); s.r=None; s.n=None
        s.create_subscription(LaserScan,'/scan_raw',lambda m:setattr(s,'r',np.array(m.ranges,np.float32)),qos_profile_sensor_data)
        s.create_subscription(LaserScan,'/scan',lambda m:setattr(s,'n',np.array(m.ranges,np.float32)),qos_profile_sensor_data)
rclpy.init(); n=A(); t=time.time()
while (n.r is None or n.n is None) and time.time()<t+4: rclpy.spin_once(n,timeout_sec=0.2)
if n.r is not None and n.n is not None:
    rv=np.isfinite(n.r).sum(); nv=np.isfinite(n.n).sum()
    both=np.isfinite(n.r)&np.isfinite(n.n)
    diff=np.abs(n.r[both]-n.n[both]); md=diff.max() if both.sum() else 0
    print(f"  raw 유효 {rv}점, deskew 유효 {nv}점 (정지 시 거의 같아야). 공통점 최대거리차 {md*1000:.0f}mm")
    print(f"  → 정지 무결성 {'OK(왜곡 없음)' if abs(rv-nv)<rv*0.05 and md<0.05 else '점검 필요'}")
PY
echo "===scan_deskew 로그==="; grep -aiE "deskew|error" /tmp/lidar.log | tail -2
