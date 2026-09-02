#!/bin/bash
# LiDAR yaw 정렬 v2: 개별 최근접 빔 각도 + 근거리(<0.8m) 세밀(10deg) 히스토그램
# 물체(책/상자)를 로버 정면, 스캔면 높이(지면+18.5cm)에 30cm 이내로 둘 것
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s): super().__init__('a'); s.acc=[]; s.m=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment,msg.range_min)
rclpy.init(); n=A(); e=time.time()+5
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.3)
if not n.acc: print("NO_SCAN"); raise SystemExit
R=np.nanmedian(np.vstack([r for r in n.acc if len(r)==len(n.acc[0])]),axis=0)
a0,ai,rmin=n.m; ang=np.degrees(a0+ai*np.arange(len(R)))
valid=np.isfinite(R)&(R>max(rmin,0.05))
# 개별 최근접 빔
i=np.nanargmin(np.where(valid,R,np.inf))
print(f"NEAREST BEAM: {ang[i]:+.1f} deg @ {R[i]:.2f} m")
# 근거리 히스토그램 (10deg bin, <0.8m 만)
print("근거리(<0.8m) 빔 분포 (10deg bin, 개수·최소거리):")
near=valid&(R<0.8)
for c in range(-180,180,10):
    m=near&(ang>=c)&(ang<c+10)
    if m.sum()>0: print(f"  [{c:+4d}..{c+10:+4d}]  n={m.sum():3d}  min={np.nanmin(R[m]):.2f}m  {'#'*m.sum()}")
print("(0deg = lidar +x = 현재 URDF 로버 전방. 정면 물체가 0deg 근처에 뭉쳐야 정렬 정상.")
print(" 다른 각도 X에 뭉치면 lidar_yaw 를 -X(rad) 만큼 회전 보정.)")
n.destroy_node(); rclpy.shutdown()
PY
