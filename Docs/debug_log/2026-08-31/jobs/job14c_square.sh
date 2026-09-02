#!/bin/bash
# 사각형 루프 드리프트 정량화 (좁은공간). 인자: 변길이(기본0.35), 회전방향(기본 L=CCW)
# 각 변: 직진 side → 90도 회전(자이로 피드백). 4변 후 시작점 복귀. odom 닫힘 + 사용자 줄자 실측.
SIDE=${1:-0.35}; DIR=${2:-L}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$SIDE" "$DIR" << 'PY'
import math, time, sys, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
SIDE=float(sys.argv[1]); DIR=sys.argv[2]
V=0.06; Wz=0.3*(1 if DIR=='L' else -1); SAFE=0.05
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
def clr(rng,ang):
    th=ang+LYAW; px=LX+rng*np.cos(th); py=rng*np.sin(th)
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    return np.sqrt(dx*dx+dy*dy)
class R(Node):
    def __init__(s):
        super().__init__('sq'); s.c=None; s.o=None
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.oc,qos_profile_sensor_data)
    def sc(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
        if ok.sum(): s.c=float(np.min(clr(r[ok],a[ok])))
    def oc(s,m):
        p=m.pose.pose; q=p.orientation; s.o=(p.position.x,p.position.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
def spin(n,t): n.pub.publish(t); rclpy.spin_once(n,timeout_sec=0.03)
def stop(n):
    t=Twist()
    for _ in range(10): n.pub.publish(t); time.sleep(0.02)
def guard(n): return n.c is not None and n.c<SAFE
rclpy.init(); n=R(); t0=time.time()
while (n.c is None or n.o is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
if n.o is None: print("NO_ODOM"); stop(n); raise SystemExit
o0=n.o
print(f"시작 odom=({o0[0]:.3f},{o0[1]:.3f}) hd={math.degrees(o0[2]):.1f}, 여유{n.c*100:.0f}cm, 변{SIDE}m {DIR}")
if n.c<0.10: print("!! 여유 부족 — 공간 확보/변 축소"); stop(n); raise SystemExit
ABORT=False
for leg in range(4):
    # 직진 side
    st=n.o; tw=Twist(); tw.linear.x=V; t1=time.time()
    while math.hypot(n.o[0]-st[0],n.o[1]-st[1])<SIDE:
        spin(n,tw)
        if guard(n): print(f"  [{leg+1}변] GUARD {n.c*100:.1f}cm 직진중 — 중단"); ABORT=True; break
        if time.time()-t1>20: break
    stop(n)
    if ABORT: break
    # 90도 회전 (자이로 피드백)
    h0=n.o[2]; tw=Twist(); tw.angular.z=Wz; t1=time.time()
    def dh(): d=n.o[2]-h0; return abs(((d+math.pi)%(2*math.pi))-math.pi)
    while dh()<math.radians(88):
        spin(n,tw)
        if guard(n): print(f"  [{leg+1}코너] GUARD {n.c*100:.1f}cm 회전중 — 중단"); ABORT=True; break
        if time.time()-t1>15: break
    stop(n)
    if ABORT: break
    print(f"  {leg+1}변 완료: odom=({n.o[0]:.3f},{n.o[1]:.3f}) hd={math.degrees(n.o[2]):.1f}")
stop(n)
of=n.o
close=math.hypot(of[0]-o0[0],of[1]-o0[1])
dh=math.degrees(((of[2]-o0[2]+math.pi)%(2*math.pi))-math.pi)
print(f"\n=== 결과 ===")
print(f"odom 시작 ({o0[0]:.3f},{o0[1]:.3f}) → 끝 ({of[0]:.3f},{of[1]:.3f})")
print(f"odom 닫힘오차 = {close*100:.1f} cm, heading오차 = {dh:+.1f}deg (0 근처면 odom은 닫혔다고 봄)")
print(f"★ 로버가 물리적으로 시작표시에서 얼마나 벗어났는지 줄자로 측정 → 그게 실제 드리프트")
print(f"  (중단됨: {ABORT})" if ABORT else "  (4변 완주)")
PY
