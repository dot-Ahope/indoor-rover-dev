#!/bin/bash
# vx×1.022 검증: 최대속도 직진, odom vs slam(지면검증) 이동거리 비율.
# 전방 여유에 맞춰 목표거리 자동조절(최대 2.0m). 가드 5cm.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, numpy as np, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
V=0.10; GUARD=0.05          # 최대속도
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
rclpy.init(); n=rclpy.create_node('vxv')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
pub=n.create_publisher(Twist,'/cmd_vel',10)
st={'c':None,'f':None,'o':None}
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12)
    if not ok.sum(): return
    th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    c=np.sqrt(dx*dx+dy*dy); st['c']=float(np.min(c))
    ang=np.degrees(np.arctan2(py,px)); mk=(ang>=-30)&(ang<30)
    st['f']=float(np.min(c[mk])) if mk.any() else None
def oc(m):
    p=m.pose.pose; st['o']=(p.position.x,p.position.y)
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/odometry/filtered',oc,qos_profile_sensor_data)
def mb():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform
        return (t.translation.x,t.translation.y)
    except Exception: return None
t0=time.time()
while (st['o'] is None or st['f'] is None or mb() is None) and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
if st['o'] is None or mb() is None: print("odom/TF 준비 안됨"); raise SystemExit
TARGET=min(2.0, max(0.0,(st['f'] or 0)-0.5))
print(f"전방여유 {st['f']*100:.0f}cm → 목표 직진거리 {TARGET:.2f}m (최대속도 {V} m/s)")
if TARGET < 1.0:
    print("!! 전방 부족(목표<1.0m) — 더 트인 방향으로 로버를 돌려주세요. 중단."); raise SystemExit
o0=st['o']; m0=mb()
tw=Twist(); tw.linear.x=V; t1=time.time(); why=""
while True:
    pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
    d=math.hypot(st['o'][0]-o0[0], st['o'][1]-o0[1])
    if st['c'] is not None and st['c']<GUARD: why=f"가드 {st['c']*100:.0f}cm"; break
    if d>=TARGET: why="목표도달"; break
    if time.time()-t1>50: why="타임아웃"; break
t=Twist()
for _ in range(15): pub.publish(t); time.sleep(0.02)
time.sleep(1.2)
for _ in range(20): rclpy.spin_once(n,timeout_sec=0.05)
o1=st['o']; m1=mb()
od=math.hypot(o1[0]-o0[0],o1[1]-o0[1]); sd=math.hypot(m1[0]-m0[0],m1[1]-m0[1])
print(f"정지: {why}")
print(f"  odom 이동 = {od:.3f} m")
print(f"  slam 이동 = {sd:.3f} m  (지면검증)")
if od>0.05:
    ratio=sd/od
    print(f"  ★ 비율 slam/odom = {ratio:.4f}")
    print(f"    (보정 전이었다면 ~1.022 기대. 1.000 근처면 vx 보정 정확)")
    err=(ratio-1.0)*100
    if abs(err)<1.0: print(f"    → 잔여오차 {err:+.1f}% — 보정 성공, 직진 스케일 정확")
    elif err>0: print(f"    → 여전히 {err:+.1f}% 과소보고 — 스케일을 더 키울 여지")
    else: print(f"    → {err:+.1f}% 과대보고 — 과보정")
rclpy.shutdown()
PY
