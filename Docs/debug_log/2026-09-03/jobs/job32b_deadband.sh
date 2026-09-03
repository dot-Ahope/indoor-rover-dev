#!/bin/bash
# 데드밴드 보상 검증: 미세 각속도 지령에 실제 회전하는지 (자이로 측정).
# 플래시 전: ω=0.05 → 68초 무반응(데드락). 보상 후 회전해야 정상.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, numpy as np, rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
LX,LYAW=0.152,math.pi; XMAX,YMAX=0.25,0.165; SWEEP=math.hypot(XMAX,YMAX)
rclpy.init(); n=rclpy.create_node('db')
pub=n.create_publisher(Twist,'/cmd_vel',10)
st={'o':None,'cen':None}
def oc(m):
    q=m.pose.pose.orientation; st['o']=math.atan2(2*(q.w*q.z),1-2*q.z*q.z)
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12)
    if ok.sum():
        th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
        st['cen']=float(np.percentile(np.hypot(px,py),0.5))
n.create_subscription(Odometry,'/odometry/filtered',oc,qos_profile_sensor_data)
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
t0=time.time()
while (st['o'] is None or st['cen'] is None) and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
print(f"회전 여유: 중심기준 {st['cen']*100:.0f}cm (필요 {SWEEP*100:.0f}cm) → {'OK' if st['cen']>SWEEP+0.05 else '부족'}")
if st['cen']<SWEEP+0.05: print("공간 부족 — 중단"); raise SystemExit
def dw(a): return math.degrees(((a+math.pi)%(2*math.pi))-math.pi)
print(f"\n{'지령ω':>8} {'8초간 실회전':>12} {'평균실ω':>10}  판정")
res=[]
for W in [0.05, 0.08, 0.12, 0.20, 0.30]:
    for _ in range(10): pub.publish(Twist()); time.sleep(0.02)
    time.sleep(0.6)
    for _ in range(10): rclpy.spin_once(n,timeout_sec=0.05)
    h0=st['o']; tw=Twist(); tw.angular.z=W; t1=time.time()
    while time.time()-t1<8.0:
        pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.02)
        if st['cen'] is not None and st['cen']<SWEEP+0.03: break
    for _ in range(10): pub.publish(Twist()); time.sleep(0.02)
    time.sleep(0.8)
    for _ in range(10): rclpy.spin_once(n,timeout_sec=0.05)
    d=dw(st['o']-h0); rate=math.radians(d)/8.0
    ok = abs(d) > 2.0
    print(f"{W:8.2f} {d:>10.1f}도 {rate:>9.3f}  {'✓ 회전함' if ok else '✗ 무반응'}")
    res.append((W,d,rate,ok))
    time.sleep(0.5)
for _ in range(15): pub.publish(Twist()); time.sleep(0.02)
print(f"\n=== 판정 ===")
w005=[r for r in res if abs(r[0]-0.05)<1e-6][0]
print(f"  ω=0.05 (플래시 전 데드락 지점): {w005[1]:+.1f}도 → {'✅ 보상 성공' if w005[3] else '❌ 여전히 무반응'}")
bad=[r[0] for r in res if not r[3]]
print(f"  무반응 지령: {bad if bad else '없음 (전 구간 반응)'}")
print(f"  실ω/지령ω 비율: " + ", ".join(f"{r[0]:.2f}→{r[2]/r[0]:.2f}" for r in res if r[3]))
rclpy.shutdown()
PY
