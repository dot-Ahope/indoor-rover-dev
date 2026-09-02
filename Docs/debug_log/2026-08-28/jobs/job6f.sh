#!/bin/bash
# 검증: 종이를 base_link 프레임에서 추적 (LaserScan→base_link 변환). 정면이면 0deg, 좌 +90, 우 -90.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
import tf2_ros
from geometry_msgs.msg import PointStamped
import tf2_geometry_msgs
class A(Node):
    def __init__(s):
        super().__init__('a'); s.acc=[]; s.m=None
        s.buf=tf2_ros.Buffer(); s.lis=tf2_ros.TransformListener(s.buf,s)
        s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment,msg.header.frame_id)
rclpy.init(); n=A()
# TF 대기
t0=time.time()
while time.time()<t0+2: rclpy.spin_once(n,timeout_sec=0.1)
print("15초간 로버 정면에서 종이를 흔드세요...")
n.acc=[]; e=time.time()+15
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.2)
A_=[r for r in n.acc if len(r)==len(n.acc[0])]
M=np.vstack(A_); a0,ai,fid=n.m; ang=a0+ai*np.arange(M.shape[1])
# lidar→base_link 회전 (yaw만; 평면 스캔)
try:
    tf=n.buf.lookup_transform('base_link',fid,rclpy.time.Time())
    q=tf.transform.rotation; yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
except Exception as ex:
    print("TF fail:",ex); yaw=0.0
print(f"lidar→base_link yaw = {math.degrees(yaw):.1f} deg")
bang=np.degrees(ang+yaw)  # base_link 프레임 각도
bang=(bang+180)%360-180
finite=np.isfinite(M); near=finite&(M<0.7)
beam_std=np.nanstd(np.where(finite,M,np.nan),axis=0)
print("변동 큰(종이) 섹터 — base_link 프레임 30deg bin (0=전방, +90=좌, -90=우, ±180=후):")
best=(None,-1)
for c in range(-180,180,30):
    m=(bang>=c)&(bang<c+30)
    if m.sum()==0: continue
    sm=np.nanmean(beam_std[m]); cnt=near[:,m].sum()
    if cnt>50 and cnt*sm>best[1]: best=(c+15,cnt*sm)
    if cnt>0: print(f"  [{c:+4d}..{c+30:+4d}]  std={sm:.3f}  near={cnt:5d}  {'#'*min(int(cnt/40),30)}")
b=best[0]
if b is not None:
    d='전방(정렬 정상)' if abs(b)<45 else('후방(yaw 여전히 반대)' if abs(b)>135 else('좌' if b>0 else '우'))
    print(f"\n=> 종이 중심 ≈ {b:+d} deg → {d}")
n.destroy_node(); rclpy.shutdown()
PY
