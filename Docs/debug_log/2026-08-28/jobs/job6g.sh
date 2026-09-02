#!/bin/bash
# 정밀 검증: base_link 프레임에서 (a)정지 기준선 3s → (b)흔들기 15s. 차이(변동)가 큰 상위 구간 + 최대변동 빔 각도
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
import tf2_ros
class A(Node):
    def __init__(s):
        super().__init__('a'); s.acc=[]; s.m=None
        s.buf=tf2_ros.Buffer(); tf2_ros.TransformListener(s.buf,s)
        s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment,msg.header.frame_id)
rclpy.init(); n=A(); t0=time.time()
while time.time()<t0+2: rclpy.spin_once(n,timeout_sec=0.1)
a0,ai,fid=n.m
tf=n.buf.lookup_transform('base_link',fid,rclpy.time.Time()); q=tf.transform.rotation
yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
print(f"lidar→base_link yaw = {math.degrees(yaw):.1f} deg (0=전방,+90=좌,-90=우,±180=후)")
print("15초간 로버 정면 30cm·높이18cm에서 종이를 좌우로 흔드세요...")
n.acc=[]; e=time.time()+15
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.2)
M=np.vstack([r for r in n.acc if len(r)==len(n.acc[0])])
ang=a0+ai*np.arange(M.shape[1]); bang=(np.degrees(ang+yaw)+180)%360-180
finite=np.isfinite(M); std=np.nanstd(np.where(finite,M,np.nan),axis=0); near=(finite&(M<0.9)).sum(axis=0)
# 종이 후보 = near>0 이고 std 큰 빔. 상위 빔 각도
cand=(near>M.shape[0]*0.15)&(std>0.03)
if cand.sum()==0:
    print("종이 검출 실패 — 스캔면(18cm) 벗어났거나 너무 멀리. 상위 std 빔:")
    idx=np.argsort(-std)[:5]
    for i in idx: print(f"  {bang[i]:+.0f}deg std={std[i]:.3f} near={near[i]}")
else:
    w=std[cand]; a=bang[cand]
    # 원형 가중 평균
    cx=np.sum(w*np.cos(np.radians(a))); cy=np.sum(w*np.sin(np.radians(a)))
    ctr=math.degrees(math.atan2(cy,cx))
    print(f"종이 검출: {cand.sum()} 빔, 가중중심 = {ctr:+.0f} deg")
    d='전방✓(정렬 정상)' if abs(ctr)<40 else('후방(yaw 반대)' if abs(ctr)>140 else('좌(+90)' if ctr>0 else '우(-90)'))
    print(f"=> 종이 방향(로버 기준): {d}")
    print("30deg bin 분포:")
    for c in range(-180,180,30):
        m=cand&(bang>=c)&(bang<c+30)
        if m.sum()>0: print(f"  [{c:+4d}..{c+30:+4d}] beams={m.sum():3d} std_mean={np.mean(std[m]):.3f}")
n.destroy_node(); rclpy.shutdown()
PY
