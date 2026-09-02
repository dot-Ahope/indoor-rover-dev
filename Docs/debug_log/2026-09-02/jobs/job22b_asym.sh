#!/bin/bash
# 좌/우 트랙 비대칭 정량화: 순수 직진(angular=0) 지령 시 실제 휨 측정.
# 전진↔후진 번갈아 N회. 자이로(EKF) heading변화 vs 휠오도 heading변화 비교.
DIST=${1:-0.90}; N=${2:-4}; SPD=${3:-0.06}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$DIST" "$N" "$SPD" << 'PY'
import math, time, sys, numpy as np, rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
DIST=float(sys.argv[1]); N=int(sys.argv[2]); SPD=float(sys.argv[3])
PATH_GUARD=0.10
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMAX=-0.25,0.25,0.165
rclpy.init(); n=rclpy.create_node('asym')
pub=n.create_publisher(Twist,'/cmd_vel',10)
st={'f':None,'b':None,'o':None,'w':None}
def yaw(q): return math.atan2(2*(q.w*q.z),1-2*q.z*q.z)
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12)
    if not ok.sum(): return
    th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
    band=np.abs(py)<=(YMAX+0.03)
    s1=band&(px>XMAX); s2=band&(px<XMIN)
    st['f']=float(np.percentile(px[s1]-XMAX,0.5)) if s1.sum()>3 else 9.99
    st['b']=float(np.percentile(XMIN-px[s2],0.5)) if s2.sum()>3 else 9.99
def oc(m):
    p=m.pose.pose; st['o']=(p.position.x,p.position.y,yaw(p.orientation))
def wc(m):
    p=m.pose.pose; st['w']=(p.position.x,p.position.y,yaw(p.orientation))
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/odometry/filtered',oc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/wheel_odom',wc,qos_profile_sensor_data)
t0=time.time()
while (st['o'] is None or st['w'] is None or st['f'] is None) and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
if st['o'] is None: print("준비 안됨"); raise SystemExit
def dwrap(a): return math.degrees(((a+math.pi)%(2*math.pi))-math.pi)
print(f"직진 {DIST}m × {N}회 (전진/후진 교대), 속도 {SPD} m/s, angular=0 순수직진")
print(f"{'회차':>4} {'방향':>4} {'거리m':>7} {'자이로휨°':>10} {'휠오도휨°':>10} {'자이로°/m':>10}")
res=[]
for i in range(N):
    DIR='F' if i%2==0 else 'B'
    avail = st['f'] if DIR=='F' else st['b']
    tgt=min(DIST, max(0.0, avail-0.35))
    if tgt<0.3:
        print(f"{i+1:>4} {DIR:>4}  경로여유 {avail*100:.0f}cm 부족 — 건너뜀"); continue
    o0=st['o']; w0=st['w']; tw=Twist(); tw.linear.x=SPD*(1 if DIR=='F' else -1); tw.angular.z=0.0
    t1=time.time(); stop=""
    while True:
        pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
        d=math.hypot(st['o'][0]-o0[0],st['o'][1]-o0[1])
        g = st['f'] if DIR=='F' else st['b']
        if g is not None and g<PATH_GUARD: stop="가드"; break
        if d>=tgt: stop="완료"; break
        if time.time()-t1>40: stop="타임아웃"; break
    for _ in range(12): pub.publish(Twist()); time.sleep(0.02)
    time.sleep(1.0)
    for _ in range(15): rclpy.spin_once(n,timeout_sec=0.05)
    o1=st['o']; w1=st['w']
    dist=math.hypot(o1[0]-o0[0],o1[1]-o0[1])
    gyro_d=dwrap(o1[2]-o0[2]); wheel_d=dwrap(w1[2]-w0[2])
    perm = gyro_d/dist if dist>0.05 else float('nan')
    print(f"{i+1:>4} {DIR:>4} {dist:>7.3f} {gyro_d:>+10.2f} {wheel_d:>+10.2f} {perm:>+10.2f}   [{stop}]")
    res.append((DIR,dist,gyro_d,wheel_d,perm))
    time.sleep(0.5)
if res:
    g=[r[4] for r in res if not math.isnan(r[4])]
    print(f"\n=== 요약 ===")
    print(f"  자이로 휨: 평균 {np.mean(g):+.2f}°/m, 표준편차 {np.std(g):.2f}, 범위 {min(g):+.2f}~{max(g):+.2f}")
    F=[r[4] for r in res if r[0]=='F']; B=[r[4] for r in res if r[0]=='B']
    if F: print(f"  전진 평균 {np.mean(F):+.2f}°/m   (부호 +=좌회전)")
    if B: print(f"  후진 평균 {np.mean(B):+.2f}°/m")
    gw=[abs(r[2]-r[3]) for r in res]
    print(f"  자이로 vs 휠오도 차이: 평균 {np.mean(gw):.2f}° → 작으면 '실제 바퀴속도차', 크면 '슬립 비대칭'")
rclpy.shutdown()
PY
