#!/bin/bash
# 직진 캘리브레이션: 각속도 0으로 전진, 오도 유클리드 거리 TARGET 도달 시 정지. 풋프린트 가드.
# odom(EKF)·wheel_odom 둘 다 시작/끝 기록 → 오도 보고거리. 사용자 줄자 실측과 대조.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
V=0.06; TARGET=2.0; SAFE=0.05; TIMEOUT=60.0   # 0.06m/s로 2m ~ 33s
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
def clr(rng,ang):
    th=ang+LYAW; px=LX+rng*np.cos(th); py=rng*np.sin(th)
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    return np.sqrt(dx*dx+dy*dy)
class R(Node):
    def __init__(s):
        super().__init__('straight'); s.c=None; s.of=None; s.wo=None
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.ecb,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/wheel_odom',s.wcb,qos_profile_sensor_data)
    def sc(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
        if ok.sum(): s.c=float(np.min(clr(r[ok],a[ok])))
    def ecb(s,m): p=m.pose.pose; q=p.orientation; s.of=(p.position.x,p.position.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
    def wcb(s,m): p=m.pose.pose; s.wo=(p.position.x,p.position.y)
def dist(a,b): return math.hypot(b[0]-a[0],b[1]-a[1])
def stop(n):
    t=Twist()
    for _ in range(12): n.pub.publish(t); time.sleep(0.02)
rclpy.init(); n=R(); t0=time.time()
while (n.c is None or n.of is None or n.wo is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
if n.of is None: print("NO_ODOM"); stop(n); raise SystemExit
o0=n.of; w0=n.wo; th0=n.of[2]
print(f"시작 odom=({o0[0]:.3f},{o0[1]:.3f}) heading={math.degrees(th0):.1f}deg, 여유 {n.c*100:.0f}cm")
if n.c<SAFE+0.02: print(f"!! 시작 여유 부족({n.c*100:.0f}cm) — 앞을 더 확보"); stop(n); raise SystemExit
tw=Twist(); tw.linear.x=V; start=time.time(); reason=""
while True:
    n.pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.05)
    d=dist(o0,n.of)
    if n.c is not None and n.c<SAFE: reason=f"GUARD {n.c*100:.1f}cm"; break
    if d>=TARGET: reason="TARGET"; break
    if time.time()-start>TIMEOUT: reason="TIMEOUT"; break
stop(n)
of=n.of; wo=n.wo
od_d=dist(o0,of); wo_d=dist(w0,wo); dth=math.degrees(of[2]-th0)
dth=((dth+180)%360)-180
print(f"정지: {reason}")
print(f"  odom(EKF) 이동거리 = {od_d:.3f} m  (Δx={of[0]-o0[0]:+.3f}, Δy={of[1]-o0[1]:+.3f})")
print(f"  wheel_odom 이동거리 = {wo_d:.3f} m")
print(f"  heading 변화 = {dth:+.1f}deg (0 근처여야 직진)")
print(f"  ★ 줄자로 실제 이동거리 측정 → 스케일 = 실제/{od_d:.3f}")
PY
