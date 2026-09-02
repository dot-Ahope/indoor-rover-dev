#!/bin/bash
# 직진 스케일 vs 속도: 인자 방향(F/B) 속도(m/s). odom·slam·휠원시 기록.
DIR=${1:-F}; SPD=${2:-0.06}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$DIR" "$SPD" << 'PY'
import math, time, sys, numpy as np, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
DIR=sys.argv[1]; SPD=float(sys.argv[2]); V=SPD*(1 if DIR=='F' else -1); GUARD=0.06
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
rclpy.init(); n=rclpy.create_node('spd')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
pub=n.create_publisher(Twist,'/cmd_vel',10)
st={'c':None,'d':None,'o':None,'w':None}
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12)
    if not ok.sum(): return
    th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    c=np.sqrt(dx*dx+dy*dy); st['c']=float(np.min(c))
    ang=np.degrees(np.arctan2(py,px))
    mk=(ang>=-30)&(ang<30) if DIR=='F' else ((ang>=150)|(ang<-150))
    st['d']=float(np.min(c[mk])) if mk.any() else None
def oc(m): p=m.pose.pose; st['o']=(p.position.x,p.position.y)
def wc(m): p=m.pose.pose; st['w']=(p.position.x,p.position.y)
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/odometry/filtered',oc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/wheel_odom',wc,qos_profile_sensor_data)
def mb():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform
        return (t.translation.x,t.translation.y)
    except Exception: return None
t0=time.time()
while (st['o'] is None or st['d'] is None or st['w'] is None or mb() is None) and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
if st['o'] is None or mb() is None: print("준비 안됨"); raise SystemExit
TARGET=min(2.0, max(0.0,(st['d'] or 0)-0.5))
nm='전진' if DIR=='F' else '후진'
print(f"{nm} 여유 {st['d']*100:.0f}cm → 목표 {TARGET:.2f}m, 속도 {SPD} m/s")
if TARGET<1.0: print("!! 여유 부족 — 중단."); raise SystemExit
o0=st['o']; m0=mb(); w0=st['w']; tw=Twist(); tw.linear.x=V; t1=time.time(); why=""
while True:
    pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
    d=math.hypot(st['o'][0]-o0[0], st['o'][1]-o0[1])
    if st['c'] is not None and st['c']<GUARD: why=f"가드 {st['c']*100:.0f}cm"; break
    if d>=TARGET: why="목표도달"; break
    if time.time()-t1>70: why="타임아웃"; break
t=Twist()
for _ in range(15): pub.publish(t); time.sleep(0.02)
time.sleep(1.2)
for _ in range(20): rclpy.spin_once(n,timeout_sec=0.05)
o1=st['o']; m1=mb(); w1=st['w']
od=math.hypot(o1[0]-o0[0],o1[1]-o0[1]); sd=math.hypot(m1[0]-m0[0],m1[1]-m0[1]); wd=math.hypot(w1[0]-w0[0],w1[1]-w0[1])
print(f"정지: {why}  (속도 {SPD} m/s)")
print(f"  휠원시 = {wd:.3f} m")
print(f"  odom(EKF) = {od:.3f} m")
print(f"  slam = {sd:.3f} m")
print(f"  ★ 줄자 실측을 알려주세요. (0.10에선 실측1.06 vs odom1.386 = 31% 과대였음)")
rclpy.shutdown()
PY
