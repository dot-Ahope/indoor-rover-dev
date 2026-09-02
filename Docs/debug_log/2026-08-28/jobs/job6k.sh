#!/bin/bash
# 트인 공간 + 정면 단일 물체: 유일 최근접 반사의 원시 θ_lidar = 로버 정면 하드웨어 각도
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s): super().__init__('a'); s.acc=[]; s.m=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment,msg.range_min)
rclpy.init(); n=A(); t0=time.time()
while time.time()<t0+4: rclpy.spin_once(n,timeout_sec=0.2)
M=np.nanmedian(np.vstack([r for r in n.acc if len(r)==len(n.acc[0])]),axis=0)
a0,ai,rmin=n.m; ang=np.degrees(a0+ai*np.arange(len(M)))
valid=np.isfinite(M)&(M>max(rmin,0.05))
i=int(np.nanargmin(np.where(valid,M,np.inf)))
th=ang[i]; dist=M[i]
# 최근접 주변 클러스터(물체 폭) 확인
near=valid&(M<dist+0.15)
cl=ang[near]
print(f"유일 최근접 물체: θ_lidar = {th:+.1f} deg @ {dist:.2f} m")
print(f"  근접 클러스터 각도범위: {cl.min():+.0f}..{cl.max():+.0f} deg ({near.sum()} beams)")
print(f"  두번째로 가까운 것들(참고): ", end="")
o=np.argsort(np.where(valid,M,np.inf))[:8]
print(" ".join(f"{ang[j]:+.0f}deg/{M[j]:.2f}m" for j in o))
print()
# 물체가 정면(로버 +x)이므로: 정면 φ=0 이 θ_lidar 에 나타남 → yaw = -θ_lidar (90도 격자 스냅)
snap=round(th/90.)*90; snap=180 if snap==-180 else snap
print(f"=> 로버 정면 = 하드웨어 θ_lidar {th:+.0f} deg (스냅 {snap:+d})")
print(f"   필요한 lidar_yaw = {-math.radians(snap):+.4f} rad ({-snap:+d} deg)")
if abs(snap)<=1: print("   → yaw=0 (하드웨어 +x = 로버 전방)")
elif abs(snap)>=179: print("   → yaw=π (하드웨어 +x = 로버 후방)")
else: print(f"   → yaw={-snap:+d}deg (하드웨어 축이 로버 {'좌' if snap<0 else '우'}측 지향)")
n.destroy_node(); rclpy.shutdown()
PY
