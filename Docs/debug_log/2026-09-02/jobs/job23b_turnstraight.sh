#!/bin/bash
# 관측조건 재현: "90도 회전 → 직진"을 N회 반복, 회전 직후 직진 구간의 휨 측정.
# 비교군: job22b(회전 없는 직진) 평균 |0.4|°/m 이내.
STR=${1:-0.50}; N=${2:-4}; SPD=${3:-0.06}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$STR" "$N" "$SPD" << 'PY'
import math, time, sys, numpy as np, rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
STR=float(sys.argv[1]); N=int(sys.argv[2]); SPD=float(sys.argv[3]); Wz=0.3
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMAX=-0.25,0.25,0.165
SWEEP=math.hypot(XMAX,YMAX); TURN_GUARD=SWEEP+0.04; PATH_GUARD=0.10
rclpy.init(); n=rclpy.create_node('ts')
pub=n.create_publisher(Twist,'/cmd_vel',10)
st={'cen':None,'f':None,'o':None,'w':None}
def yaw(q): return math.atan2(2*(q.w*q.z),1-2*q.z*q.z)
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12)
    if not ok.sum(): return
    th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
    st['cen']=float(np.percentile(np.hypot(px,py),0.5))
    band=np.abs(py)<=(YMAX+0.03); s1=band&(px>XMAX)
    st['f']=float(np.percentile(px[s1]-XMAX,0.5)) if s1.sum()>3 else 9.99
def oc(m): p=m.pose.pose; st['o']=(p.position.x,p.position.y,yaw(p.orientation))
def wc(m): p=m.pose.pose; st['w']=(p.position.x,p.position.y,yaw(p.orientation))
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/odometry/filtered',oc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/wheel_odom',wc,qos_profile_sensor_data)
t0=time.time()
while (st['o'] is None or st['w'] is None or st['cen'] is None) and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
if st['o'] is None: print("준비 안됨"); raise SystemExit
def dw(a): return math.degrees(((a+math.pi)%(2*math.pi))-math.pi)
def stop():
    for _ in range(12): pub.publish(Twist()); time.sleep(0.02)
print(f"'90도 좌회전 → 직진 {STR}m' × {N}회, 속도 {SPD} m/s")
print(f"{'회차':>4} {'회전실제°':>9} {'직진m':>7} {'자이로휨°':>10} {'휠오도휨°':>10} {'°/m':>8}")
res=[]
for i in range(N):
    if st['cen']<TURN_GUARD: print(f"{i+1:>4}  회전공간 부족({st['cen']*100:.0f}cm) — 중단"); break
    # --- 90도 회전 (감속 포함) ---
    h0=st['o'][2]; tw=Twist(); t1=time.time(); TGT=math.radians(90)
    def dh(): return abs(dw(st['o'][2]-h0))*math.pi/180
    while dh()<TGT:
        rem=TGT-dh(); tw.angular.z=Wz if rem>math.radians(15) else Wz*0.35
        pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
        if st['cen']<TURN_GUARD or time.time()-t1>20: break
    stop(); time.sleep(0.8)
    for _ in range(12): rclpy.spin_once(n,timeout_sec=0.05)
    turned=abs(dw(st['o'][2]-h0))
    # --- 회전 직후 직진 ---
    o0=st['o']; w0=st['w']; tgt=min(STR, max(0.0,(st['f'] or 0)-0.35))
    if tgt<0.25: print(f"{i+1:>4} {turned:>9.1f}  전방여유 부족({(st['f'] or 0)*100:.0f}cm) — 직진 생략"); continue
    tw=Twist(); tw.linear.x=SPD; tw.angular.z=0.0; t1=time.time(); why=""
    while True:
        pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
        d=math.hypot(st['o'][0]-o0[0],st['o'][1]-o0[1])
        if st['f'] is not None and st['f']<PATH_GUARD: why="가드"; break
        if d>=tgt: why="완료"; break
        if time.time()-t1>30: why="타임아웃"; break
    stop(); time.sleep(1.0)
    for _ in range(15): rclpy.spin_once(n,timeout_sec=0.05)
    o1=st['o']; w1=st['w']
    dist=math.hypot(o1[0]-o0[0],o1[1]-o0[1])
    g=dw(o1[2]-o0[2]); wd=dw(w1[2]-w0[2]); perm=g/dist if dist>0.05 else float('nan')
    print(f"{i+1:>4} {turned:>9.1f} {dist:>7.3f} {g:>+10.2f} {wd:>+10.2f} {perm:>+8.2f}  [{why}]")
    res.append((turned,dist,g,wd,perm))
    time.sleep(0.5)
if res:
    p=[r[4] for r in res if not math.isnan(r[4])]
    print(f"\n=== 요약 (회전 직후 직진) ===")
    print(f"  자이로 휨: 평균 {np.mean(p):+.2f}°/m, 표준편차 {np.std(p):.2f}, 범위 {min(p):+.2f}~{max(p):+.2f}")
    print(f"  자이로 vs 휠오도 차이 평균: {np.mean([abs(r[2]-r[3]) for r in res]):.2f}°")
    print(f"  ※ 비교군(회전 없는 직진, job22b): 평균 +0.24°/m, 범위 -0.39~+1.93")
rclpy.shutdown()
PY
