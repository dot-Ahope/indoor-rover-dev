#!/bin/bash
# 사각형 루프 + 벽기반 지면검증(ground truth). 인자: 변(0.40) 방향(L) 가드(0.03)
# 시작/끝 사방 벽거리(중앙값) → 실제 이동 자동계산, odom 이동과 비교 → 드리프트.
SIDE=${1:-0.40}; DIR=${2:-L}; GUARD=${3:-0.03}
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
class R(Node):
    def __init__(s):
        super().__init__('sqgt'); s.m=None; s.o=None; s.c=None
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.oc,qos_profile_sensor_data)
    def sc(s,m):
        s.m=m; r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
        ok=np.isfinite(r)&(r>0.05)&(r<12)
        if not ok.sum(): return
        th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
        dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
        s.c=float(np.min(np.sqrt(dx*dx+dy*dy)))
    def oc(s,m):
        p=m.pose.pose; q=p.orientation; s.o=(p.position.x,p.position.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
def spin(n,t): n.pub.publish(t); rclpy.spin_once(n,timeout_sec=0.03)
def stop(n):
    t=Twist()
    for _ in range(10): n.pub.publish(t); time.sleep(0.02)
def walls(n, dur=1.5):
    # 사방(로버프레임 앞0/좌90/뒤180/우-90) ±10deg 중앙값 벽거리(m). 정지상태에서 호출.
    acc={'앞':[], '좌':[], '뒤':[], '우':[]}; t0=time.time()
    while time.time()-t0<dur:
        rclpy.spin_once(n,timeout_sec=0.05); m=n.m
        if m is None: continue
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
        ok=np.isfinite(r)&(r>0.05)&(r<12); th=a[ok]+LYAW
        px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th); rr=np.hypot(px,py); ph=np.degrees(np.arctan2(py,px))
        for nm,c in [('앞',0),('좌',90),('뒤',180),('우',-90)]:
            dd=np.abs(((ph-c+180)%360)-180); mk=dd<10
            if mk.any(): acc[nm].append(float(np.median(rr[mk])))
    return {k:(float(np.median(v)) if v else None) for k,v in acc.items()}
rclpy.init(); n=R(); t0=time.time()
while (n.c is None or n.o is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
if n.o is None: print("NO_ODOM"); stop(n); raise SystemExit
o0=n.o; W0=walls(n)
def f(v): return f"{v*100:.0f}" if v is not None else "-"
print(f"시작 odom=({o0[0]:.3f},{o0[1]:.3f}) hd={math.degrees(o0[2]):.1f}")
print(f"시작 벽거리(cm): 앞{f(W0['앞'])} 뒤{f(W0['뒤'])} 좌{f(W0['좌'])} 우{f(W0['우'])}")
print(f"변={SIDE}m {DIR}, 가드{GUARD*100:.0f}cm. 주행 시작 (Ctrl-C 중단가능)...")
ABORT=False
for leg in range(4):
    st=n.o; tw=Twist(); tw.linear.x=V; t1=time.time()
    while math.hypot(n.o[0]-st[0],n.o[1]-st[1])<SIDE:
        spin(n,tw)
        if n.c is not None and n.c<GUARD: print(f"  [{leg+1}변] 가드 {n.c*100:.1f}cm 정지"); ABORT=True; break
        if time.time()-t1>20: break
    stop(n)
    if ABORT: break
    h0=n.o[2]; tw=Twist(); tw.angular.z=Wz; t1=time.time()
    def dh(): d=n.o[2]-h0; return abs(((d+math.pi)%(2*math.pi))-math.pi)
    while dh()<math.radians(89):
        spin(n,tw)
        if n.c is not None and n.c<GUARD: print(f"  [{leg+1}코너] 가드 정지"); ABORT=True; break
        if time.time()-t1>15: break
    stop(n)
    if ABORT: break
    print(f"  {leg+1}변: odom=({n.o[0]:.3f},{n.o[1]:.3f}) hd={math.degrees(n.o[2]):.1f}")
stop(n); time.sleep(0.5); of=n.o; W1=walls(n)
print(f"\n끝 odom=({of[0]:.3f},{of[1]:.3f}) hd={math.degrees(of[2]):.1f}")
print(f"끝 벽거리(cm): 앞{f(W1['앞'])} 뒤{f(W1['뒤'])} 좌{f(W1['좌'])} 우{f(W1['우'])}")
# odom 이동
odx=of[0]-o0[0]; ody=of[1]-o0[1]; od=math.hypot(odx,ody)
dhd=math.degrees(((of[2]-o0[2]+math.pi)%(2*math.pi))-math.pi)
# 벽기반 실제 이동 (heading 거의 동일 가정): 전진=((앞0-앞1)+(뒤1-뒤0))/2, 좌=((좌0-좌1)+(우1-우0))/2
def av(a,b): 
    xs=[x for x in (a,b) if x is not None]
    return sum(xs)/len(xs) if xs else None
fwd=av( (W0['앞']-W1['앞']) if W0['앞'] and W1['앞'] else None,
        (W1['뒤']-W0['뒤']) if W0['뒤'] and W1['뒤'] else None)
lat=av( (W0['좌']-W1['좌']) if W0['좌'] and W1['좌'] else None,
        (W1['우']-W0['우']) if W0['우'] and W1['우'] else None)
print(f"\n=== 결과 ({'중단' if ABORT else '완주'}) ===")
print(f"odom 이동: {od*100:.1f}cm (Δx={odx*100:+.1f}, Δy={ody*100:+.1f}), heading {dhd:+.1f}deg")
if fwd is not None and lat is not None:
    phys=math.hypot(fwd,lat)
    print(f"벽기반 실제이동: {phys*100:.1f}cm (전진{fwd*100:+.1f}, 좌{lat*100:+.1f})")
    print(f"★ 드리프트(odom vs 실제) ≈ {abs(phys-od)*100:.1f}cm 이상 (벡터차)")
else:
    print("벽기반 계산불가(일부 방향 벽 없음) — 줄자로 실측 필요")
print(f"(줄자 교차확인: 시작표시~끝 실제거리도 알려주세요)")
PY
