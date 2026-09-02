#!/bin/bash
# 사각형 루프 드리프트 정량화 v2: 방향별 여유 출력 + 시작가드 제거 + 가드임계 인자화.
# 인자: 변길이(0.30) 방향(L) 가드m(0.03). Ctrl-C로 중단(워치독 500ms 정지).
SIDE=${1:-0.30}; DIR=${2:-L}; GUARD=${3:-0.03}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$SIDE" "$DIR" "$GUARD" << 'PY'
import math, time, sys, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
SIDE=float(sys.argv[1]); DIR=sys.argv[2]; GUARD=float(sys.argv[3])
V=0.06; Wz=0.3*(1 if DIR=='L' else -1)
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
def to_base(r,a):
    th=a+LYAW; return LX+r*np.cos(th), r*np.sin(th)   # (px,py) base_link
def clr_box(px,py):
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX])
    dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    return np.sqrt(dx*dx+dy*dy)
class R(Node):
    def __init__(s):
        super().__init__('sq'); s.c=None; s.brk=None; s.o=None
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.oc,qos_profile_sensor_data)
    def sc(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
        ok=np.isfinite(r)&(r>0.05)
        if not ok.sum(): return
        px,py=to_base(r[ok],a[ok]); c=clr_box(px,py); s.c=float(np.min(c))
        # 방향별(base_link 각도) 최소 여유
        ang=np.arctan2(py,px); d=np.degrees(ang); sec={}
        for name,lo,hi in [('앞',-45,45),('좌',45,135),('우',-135,-45)]:
            mk=(d>=lo)&(d<hi)
            sec[name]=float(np.min(c[mk])) if mk.any() else None
        bk=(d>=135)|(d<-135); sec['뒤']=float(np.min(c[bk])) if bk.any() else None
        s.brk=sec
    def oc(s,m):
        p=m.pose.pose; q=p.orientation; s.o=(p.position.x,p.position.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
def spin(n,t): n.pub.publish(t); rclpy.spin_once(n,timeout_sec=0.03)
def stop(n):
    t=Twist()
    for _ in range(10): n.pub.publish(t); time.sleep(0.02)
def guard(n): return n.c is not None and n.c<GUARD
rclpy.init(); n=R(); t0=time.time()
while (n.c is None or n.o is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
if n.o is None: print("NO_ODOM"); stop(n); raise SystemExit
o0=n.o
b=n.brk or {}
def fmt(v): return f"{v*100:.0f}cm" if v is not None else "-"
print(f"시작 odom=({o0[0]:.3f},{o0[1]:.3f}) hd={math.degrees(o0[2]):.1f}")
print(f"방향별 여유(풋프린트 모서리 기준): 앞 {fmt(b.get('앞'))} | 뒤 {fmt(b.get('뒤'))} | 좌 {fmt(b.get('좌'))} | 우 {fmt(b.get('우'))}  (최소 {n.c*100:.0f}cm)")
print(f"가드 임계={GUARD*100:.0f}cm, 변={SIDE}m {DIR}. Ctrl-C로 중단 가능.")
ABORT=False
for leg in range(4):
    st=n.o; tw=Twist(); tw.linear.x=V; t1=time.time()
    while math.hypot(n.o[0]-st[0],n.o[1]-st[1])<SIDE:
        spin(n,tw)
        if guard(n): print(f"  [{leg+1}변] 가드 {n.c*100:.1f}cm 직진중 정지"); ABORT=True; break
        if time.time()-t1>20: break
    stop(n)
    if ABORT: break
    h0=n.o[2]; tw=Twist(); tw.angular.z=Wz; t1=time.time()
    def dh(): d=n.o[2]-h0; return abs(((d+math.pi)%(2*math.pi))-math.pi)
    while dh()<math.radians(88):
        spin(n,tw)
        if guard(n): print(f"  [{leg+1}코너] 가드 {n.c*100:.1f}cm 회전중 정지"); ABORT=True; break
        if time.time()-t1>15: break
    stop(n)
    if ABORT: break
    print(f"  {leg+1}변 완료: odom=({n.o[0]:.3f},{n.o[1]:.3f}) hd={math.degrees(n.o[2]):.1f}")
stop(n); of=n.o
close=math.hypot(of[0]-o0[0],of[1]-o0[1])
dhd=math.degrees(((of[2]-o0[2]+math.pi)%(2*math.pi))-math.pi)
print(f"\n=== 결과 ({'중단' if ABORT else '4변완주'}) ===")
print(f"odom 시작({o0[0]:.3f},{o0[1]:.3f}) → 끝({of[0]:.3f},{of[1]:.3f})")
print(f"odom 닫힘오차={close*100:.1f}cm, heading오차={dhd:+.1f}deg")
print(f"★ 로버 물리적 시작표시 이탈거리를 줄자로 → 실제 드리프트")
PY
