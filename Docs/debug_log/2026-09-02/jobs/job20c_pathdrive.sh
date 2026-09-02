#!/bin/bash
# 직진 검증 v2 — 경로방향 가드(로버 폭 밴드 내 진행방향 장애물만) + 전역 비상정지(3cm).
# 좁은 공간에서도 주행 가능. 인자: 방향(F/B) 속도(m/s)
DIR=${1:-F}; SPD=${2:-0.06}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$DIR" "$SPD" << 'PY'
import math, time, sys, numpy as np, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
DIR=sys.argv[1]; SPD=float(sys.argv[2]); V=SPD*(1 if DIR=='F' else -1)
PATH_GUARD=0.08   # 진행방향 경로 여유 한계
EMERG=0.03        # 전역 비상(어느 방향이든 풋프린트 3cm)
MARGIN=0.35       # 목표거리 = 경로여유 - 이 값
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
rclpy.init(); n=rclpy.create_node('pd')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
pub=n.create_publisher(Twist,'/cmd_vel',10)
st={'path':None,'emin':None,'o':None,'w':None}
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12)
    if not ok.sum(): return
    th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    st['emin']=float(np.min(np.sqrt(dx*dx+dy*dy)))
    band=np.abs(py)<=(YMAX+0.03)          # 로버 폭 + 3cm 밴드
    sel=(band & (px>XMAX)) if DIR=='F' else (band & (px<XMIN))
    if sel.any():
        st['path']=float(np.min(px[sel]-XMAX)) if DIR=='F' else float(np.min(XMIN-px[sel]))
    else:
        st['path']=9.99                    # 경로상 장애물 없음
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
while (st['o'] is None or st['path'] is None or st['w'] is None) and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
if st['o'] is None: print("odom 준비 안됨"); raise SystemExit
nm='전진' if DIR=='F' else '후진'
TARGET=min(2.0, max(0.0, st['path']-MARGIN))
print(f"{nm} 경로여유 {st['path']*100:.0f}cm (전역최소 {st['emin']*100:.0f}cm) → 목표 {TARGET:.2f}m, 속도 {SPD} m/s")
if TARGET<0.20:
    print("!! 경로여유가 너무 짧음(<20cm 주행) — 중단."); raise SystemExit
o0=st['o']; m0=mb(); w0=st['w']; tw=Twist(); tw.linear.x=V; t1=time.time(); why=""
while True:
    pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
    d=math.hypot(st['o'][0]-o0[0], st['o'][1]-o0[1])
    if st['path'] is not None and st['path']<PATH_GUARD: why=f"경로가드 {st['path']*100:.0f}cm"; break
    # 직진 시 측면 여유는 변하지 않으므로 전역 비상정지는 사용하지 않음(오탐 방지). 경로 가드가 담당.
    if d>=TARGET: why="목표도달"; break
    if time.time()-t1>70: why="타임아웃"; break
t=Twist()
for _ in range(15): pub.publish(t); time.sleep(0.02)
time.sleep(1.2)
for _ in range(20): rclpy.spin_once(n,timeout_sec=0.05)
o1=st['o']; m1=mb(); w1=st['w']
od=math.hypot(o1[0]-o0[0],o1[1]-o0[1]); wd=math.hypot(w1[0]-w0[0],w1[1]-w0[1])
sd=math.hypot(m1[0]-m0[0],m1[1]-m0[1]) if (m0 and m1) else float('nan')
print(f"정지: {why}")
print(f"  휠원시     = {wd:.3f} m")
print(f"  odom(×0.783) = {od:.3f} m   ← 줄자와 비교")
print(f"  slam       = {sd:.3f} m")
print(f"  ★ 줄자 실측을 알려주세요. 실측≈odom 이면 0.783 검증 성공")
rclpy.shutdown()
PY
