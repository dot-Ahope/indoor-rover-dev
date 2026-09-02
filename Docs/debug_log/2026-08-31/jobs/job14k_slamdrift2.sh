#!/bin/bash
# SLAM 지면검증 드리프트 v2: 시작 여유 게이트 추가(사용자 근처면 중단).
SIDE=${1:-0.40}; DIR=${2:-L}; GUARD=${3:-0.03}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$SIDE" "$DIR" "$GUARD" << 'PY'
import math, time, sys, numpy as np, rclpy, tf2_ros
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
SIDE=float(sys.argv[1]); DIR=sys.argv[2]; GUARD=float(sys.argv[3])
V=0.06; Wz=0.3*(1 if DIR=='L' else -1)
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
class R(Node):
    def __init__(s):
        super().__init__('sd'); s.o=None; s.c=None
        s.buf=tf2_ros.Buffer(); s.tl=tf2_ros.TransformListener(s.buf,s)
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.oc,qos_profile_sensor_data)
    def sc(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
        ok=np.isfinite(r)&(r>0.05)&(r<12)
        if not ok.sum(): return
        th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
        dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
        s.c=float(np.min(np.sqrt(dx*dx+dy*dy)))
    def oc(s,m):
        p=m.pose.pose; q=p.orientation; s.o=(p.position.x,p.position.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
def tf(n,a,b):
    try:
        t=n.buf.lookup_transform(a,b,rclpy.time.Time()); tr=t.transform
        q=tr.rotation; yaw=math.atan2(2*(q.w*q.z),1-2*q.z*q.z)
        return (tr.translation.x,tr.translation.y,yaw)
    except Exception: return None
def spin(n,t): n.pub.publish(t); rclpy.spin_once(n,timeout_sec=0.03)
def stop(n):
    t=Twist()
    for _ in range(10): n.pub.publish(t); time.sleep(0.02)
rclpy.init(); n=R(); t0=time.time()
while (n.o is None or n.c is None or tf(n,'map','odom') is None) and time.time()<t0+5: rclpy.spin_once(n,timeout_sec=0.1)
mo0=tf(n,'map','odom'); mb0=tf(n,'map','base_link'); o0=n.o
if mo0 is None or o0 is None: print("TF/odom 준비 안됨"); stop(n); raise SystemExit
# 시작 여유 게이트 — 사용자가 로버 근처면 중단
if n.c is not None and n.c < 0.20:
    print(f"!! 시작 여유 {n.c*100:.0f}cm — 사용자님 로버에서 1.5m 이상 떨어져 가만히 계세요. 재실행 필요."); stop(n); raise SystemExit
print(f"시작 여유 {n.c*100:.0f}cm OK. 3초 후 주행 (그동안 완전히 물러나세요)...")
for _ in range(60): rclpy.spin_once(n,timeout_sec=0.05)
print(f"시작: map->odom=({mo0[0]*100:.1f},{mo0[1]*100:.1f})cm {math.degrees(mo0[2]):+.1f}deg")
print(f"      odom->base=({o0[0]:.3f},{o0[1]:.3f}) {math.degrees(o0[2]):.1f}deg | map->base=({mb0[0]:.3f},{mb0[1]:.3f}) {math.degrees(mb0[2]):.1f}deg")
maxoff=0.0; ABORT=False
def track():
    global maxoff
    m=tf(n,'map','odom')
    if m: maxoff=max(maxoff, math.hypot(m[0]-mo0[0],m[1]-mo0[1]))
for leg in range(4):
    st=n.o; tw=Twist(); tw.linear.x=V; t1=time.time()
    while math.hypot(n.o[0]-st[0],n.o[1]-st[1])<SIDE:
        spin(n,tw); track()
        if n.c is not None and n.c<GUARD: print(f"  [{leg+1}변] 가드정지"); ABORT=True; break
        if time.time()-t1>20: break
    stop(n)
    if ABORT: break
    h0=n.o[2]; tw=Twist(); tw.angular.z=Wz; t1=time.time()
    def dh(): d=n.o[2]-h0; return abs(((d+math.pi)%(2*math.pi))-math.pi)
    while dh()<math.radians(89):
        spin(n,tw); track()
        if n.c is not None and n.c<GUARD: print(f"  [{leg+1}코너] 가드정지"); ABORT=True; break
        if time.time()-t1>15: break
    stop(n)
    if ABORT: break
    m=tf(n,'map','odom')
    print(f"  {leg+1}변: odom=({n.o[0]:.3f},{n.o[1]:.3f}) | map->odom오프셋={math.hypot(m[0]-mo0[0],m[1]-mo0[1])*100:.1f}cm {math.degrees(m[2]-mo0[2]):+.1f}deg")
stop(n); time.sleep(1.0)
for _ in range(20): rclpy.spin_once(n,timeout_sec=0.05)
mo1=tf(n,'map','odom'); mb1=tf(n,'map','base_link'); of=n.o
dmo=(math.hypot(mo1[0]-mo0[0],mo1[1]-mo0[1]), math.degrees(((mo1[2]-mo0[2]+math.pi)%(2*math.pi))-math.pi))
od=math.hypot(of[0]-o0[0],of[1]-o0[1]); odh=math.degrees(((of[2]-o0[2]+math.pi)%(2*math.pi))-math.pi)
sd=math.hypot(mb1[0]-mb0[0],mb1[1]-mb0[1]); sdh=math.degrees(((mb1[2]-mb0[2]+math.pi)%(2*math.pi))-math.pi)
print(f"\n=== 결과 ({'중단' if ABORT else '완주'}) ===")
print(f"odom 이동(추측항법): {od*100:.1f}cm, {odh:+.1f}deg")
print(f"slam 이동(실제,map->base): {sd*100:.1f}cm, {sdh:+.1f}deg")
print(f"★ 드리프트 = Δ(map->odom) = 위치 {dmo[0]*100:.1f}cm, heading {dmo[1]:+.1f}deg (주행 중 최대 {maxoff*100:.1f}cm)")
print(f"  해석: slam이 이 루프에서 위치 {dmo[0]*100:.1f}cm·heading {dmo[1]:+.1f}deg 만큼 odom을 보정함")
PY
