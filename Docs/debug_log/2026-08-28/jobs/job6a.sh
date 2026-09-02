#!/bin/bash
# 스택 상태 확인 + LiDAR yaw 정렬 사전 점검(현재 스캔 섹터별 거리 스냅샷)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===NODES==="; ros2 node list | tr '\n' ' '; echo
echo "===RATES==="; for t in /scan /wheel_odom /odometry/filtered /camera/camera/imu; do printf "  %-24s %s\n" $t "$(timeout 5 ros2 topic hz $t 2>&1 | grep -aE 'average|does not' | tail -1)"; done
echo "===현재 lidar_link yaw (URDF)==="; timeout 5 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -aE "RPY \(degree\)" | head -1
echo "===현재 스캔 섹터별 중앙거리 (정렬 기준선 — 손 없이)==="
python3 - << 'PY'
import numpy as np, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s): super().__init__('a'); s.acc=[]; s.m=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment)
rclpy.init(); n=A(); e=time.time()+4
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.3)
if not n.acc: print("NO_SCAN"); raise SystemExit
R=np.nanmedian(np.vstack([r for r in n.acc if len(r)==len(n.acc[0])]),axis=0)
a0,ai=n.m; ang=np.degrees(a0+ai*np.arange(len(R)))
for c in range(-180,180,45):
    m=(ang>=157.5)|(ang<-157.5) if c==-180 else (ang>=c-22.5)&(ang<c+22.5)
    v=np.nanmedian(R[m]); print(f"  sector {c:+4d} deg: {v:5.2f} m  {'#'*int(min(v,6)*5) if np.isfinite(v) else 'nan'}")
print("  (0deg = lidar +x = 현재 URDF상 로버 전방. 정렬 확인은 손 테스트 job4y 로)")
n.destroy_node(); rclpy.shutdown()
PY
