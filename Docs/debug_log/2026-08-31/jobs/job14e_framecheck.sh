#!/bin/bash
# 라이다 프레임 결정: /scan_raw 원시각도로 가까운 장애물 위치 → yaw=0/π 매핑 대조.
# 라이브 TF(base_link→lidar_link) yaw도 확인.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===== 라이브 TF base_link -> lidar_link ====="
timeout 4 ros2 run tf2_ros tf2_echo base_link lidar_link 2>/dev/null | grep -aA6 "Translation\|Rotation" | head -12
echo ""
echo "===== 원시 스캔 분석 ====="
python3 - << 'PY'
import math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class S(Node):
    def __init__(s):
        super().__init__('fc'); s.got=None
        s.create_subscription(LaserScan,'/scan_raw',s.cb,qos_profile_sensor_data)
    def cb(s,m):
        if s.got is None: s.got=m
rclpy.init(); n=S(); import time; t0=time.time()
while n.got is None and time.time()<t0+5: rclpy.spin_once(n,timeout_sec=0.1)
if n.got is None: print("NO /scan_raw"); raise SystemExit
m=n.got; r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
ok=np.isfinite(r)&(r>0.05)&(r<12); r=r[ok]; a=a[ok]
print(f"frame_id={m.header.frame_id}, angle_min={math.degrees(m.angle_min):.0f} max={math.degrees(m.angle_max):.0f} inc={math.degrees(m.angle_increment):.3f} n={len(r)}")
# 전체 최근접
i=int(np.argmin(r)); ad=math.degrees(a[i])
def mapdir(deg):  # base_link 각도 → 방위
    d=((deg+180)%360)-180
    if -45<=d<45: return "앞(+x)"
    if 45<=d<135: return "좌(+y)"
    if d>=135 or d<-135: return "뒤(-x)"
    return "우(-y)"
pi_deg=ad+180; z_deg=ad
print(f"\n전체 최근접: raw {ad:+.1f}deg, {r[i]*100:.0f}cm")
print(f"  yaw=π 라면 base {((pi_deg+180)%360)-180:+.1f}deg = {mapdir(pi_deg)}")
print(f"  yaw=0 라면 base {((z_deg+180)%360)-180:+.1f}deg = {mapdir(z_deg)}")
# raw 4방위 최소거리
print(f"\nraw 방위별 최소거리 (±20deg 창):")
for name,c in [("raw 0",0),("raw +90",90),("raw 180",180),("raw -90",-90)]:
    dd=np.abs(((np.degrees(a)-c+180)%360)-180)
    mk=dd<20
    if mk.any():
        j=np.argmin(r[mk]); rr=r[mk][j]
        print(f"  {name:8s}: {rr*100:5.0f}cm | yaw=π→{mapdir(c+180):8s} | yaw=0→{mapdir(c):8s}")
    else:
        print(f"  {name:8s}: (점없음)")
PY
