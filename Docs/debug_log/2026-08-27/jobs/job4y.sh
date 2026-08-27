#!/bin/bash
# LiDAR yaw 정렬 측정: 로버 정면(카메라 방향) 0.3m에 손/책을 5초간 두고 실행 → lidar_yaw 산출
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s):
        super().__init__('axis_check'); s.acc=[]; s.meta=None
        s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,m):
        r=np.array(m.ranges,dtype=np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.meta=(m.angle_min,m.angle_increment)
rclpy.init(); n=A(); end=time.time()+5
while time.time()<end: rclpy.spin_once(n,timeout_sec=0.3)
if not n.acc: print('NO_SCAN'); raise SystemExit
L=len(n.acc[0]); R=np.nanmedian(np.vstack([r for r in n.acc if len(r)==L]),axis=0)
a0,ai=n.meta; ang=np.degrees(a0+ai*np.arange(L))
print(f"{'sector(deg)':>12s} {'median_m':>9s}   (현재 lidar_link 프레임, 0deg = +x)")
best=(None,1e9)
for c in range(-180,180,45):
    m=(ang>=c-22.5)&(ang<c+22.5)
    if c==-180: m=(ang>=157.5)|(ang<-157.5)
    v=np.nanmedian(R[m]); bar='#'*int(min(v,8)*4) if np.isfinite(v) else ''
    if np.isfinite(v) and v<best[1]: best=(c,v)
    print(f"{c:>10d}   {v:9.2f}   {bar}")
print(f"\nNEAREST sector: {best[0]} deg ({best[1]:.2f} m)  ← 손이 있는 방향이어야 함")
snap=int(round(best[0]/90.0)*90); snap=180 if snap==-180 else snap
print(f"이 값은 '현재 URDF lidar_yaw가 적용된' 프레임 기준. 손이 정면(0deg)에 안 나오면 lidar_yaw를 (현재값 - {math.radians(snap):.4f}) 로 보정")
n.destroy_node(); rclpy.shutdown()
PY
