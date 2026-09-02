#!/bin/bash
# 종이 흔들기 추적: 15초간 근거리(<0.7m) 변동이 큰 섹터를 검출 → 종이 방향(lidar 프레임) 판정
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s): super().__init__('a'); s.acc=[]; s.m=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg):
        r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r)
        s.m=(msg.angle_min,msg.angle_increment)
rclpy.init(); n=A(); e=time.time()+15
print("15초간 종이를 흔드세요...")
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.2)
A_=[r for r in n.acc if len(r)==len(n.acc[0])]
M=np.vstack(A_); a0,ai=n.m; ang=np.degrees(a0+ai*np.arange(M.shape[1]))
# 각 빔의 시간축 표준편차(흔들리는 물체=변동 큼), 근거리에서만
finite=np.isfinite(M)
near=finite&(M<0.7)
std=np.where(finite,M,np.nan)
beam_std=np.nanstd(std,axis=0)
beam_nearcnt=near.sum(axis=0)
print(f"scans={M.shape[0]}")
print("변동 큰(종이) 섹터 — 30deg bin, 평균 std + 근거리 빔수:")
best=(None,-1)
for c in range(-180,180,30):
    m=(ang>=c)&(ang<c+30)
    s=np.nanmean(beam_std[m]); cnt=beam_nearcnt[m].sum()
    score=cnt*s
    if cnt>5 and score>best[1]: best=(c+15,score)
    if cnt>0: print(f"  [{c:+4d}..{c+30:+4d}]  std={s:.3f}  near_beams={cnt:4d}  {'#'*min(int(cnt/20),40)}")
print(f"\n=> 종이(가장 변동+근거리) 중심 ≈ {best[0]:+d} deg (lidar +x 기준)")
if best[0] is not None:
    b=best[0]
    fb='앞(0deg 근처)' if abs(b)<45 else ('뒤(±180 근처)' if abs(b)>135 else ('좌(+90)' if b>0 else '우(-90)'))
    corr=-math.radians(round(b/90.)*90)
    print(f"   → 로버 기준 {fb}. lidar_yaw 보정 후보 = {corr:+.4f} rad ({-int(round(b/90.)*90):+d} deg)")
n.destroy_node(); rclpy.shutdown()
PY
