#!/bin/bash
# 원시 lidar 각도(θ_lidar, TF 무관) 분석 — 코너(정면+좌측 벽) ground truth와 대조해 회전 vs 반전 판정
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s): super().__init__('a'); s.acc=[]; s.m=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment)
rclpy.init(); n=A(); t0=time.time()
while time.time()<t0+4: rclpy.spin_once(n,timeout_sec=0.2)
M=np.nanmedian(np.vstack([r for r in n.acc if len(r)==len(n.acc[0])]),axis=0)
a0,ai=n.m; ang=np.degrees(a0+ai*np.arange(len(M)))
print("RAW lidar 프레임(θ_lidar, 0deg=하드웨어+x, 반시계+). 30deg bin 중앙거리:")
rows=[]
for c in range(-180,180,30):
    m=(ang>=c)&(ang<c+30)&np.isfinite(M)
    v=np.nanmedian(M[m]) if m.sum()>=3 else float('nan')
    rows.append((c+15,v))
    bar='#'*int(min(v,4)*8) if np.isfinite(v) else ''
    tag='← 근거리(벽)' if (np.isfinite(v) and v<1.0) else ('← 트임' if (np.isfinite(v) and v>2.0) else '')
    print(f"  θ_lidar [{c:+4d}..{c+30:+4d}]  {v:5.2f} m  {bar} {tag}")
near=[a for a,v in rows if np.isfinite(v) and v<1.0]
openg=[a for a,v in rows if np.isfinite(v) and v>2.0]
print(f"\n근거리(벽) 방향들: {near}")
print(f"트임 방향들: {openg}")
print("ground truth: 정면벽 φ=0, 좌측벽 φ=+90, 우측 트임 φ=-90, 후방 트임 φ=+180")
print("→ 근거리 두 벽의 θ_lidar 중심을 φ(0,+90)에 대응시켜 회전/반전 판정")
n.destroy_node(); rclpy.shutdown()
PY
