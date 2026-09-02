#!/bin/bash
# 회전 포함 드리프트 재측정 (올바른 스케일 0.783 적용 후).
# 가드: 직진=경로밴드, 회전=스윕반경. 측정=백분위 0.5%(스퍼리어스 점 무시).
# 인자: 변(0.30) 방향(L) 속도(0.06)
SIDE=${1:-0.30}; DIR=${2:-L}; SPD=${3:-0.06}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$SIDE" "$DIR" "$SPD" << 'PY'
import math, time, sys, numpy as np, rclpy, tf2_ros
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
SIDE=float(sys.argv[1]); DIR=sys.argv[2]; SPD=float(sys.argv[3])
Wz=0.3*(1 if DIR=='L' else -1)
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
SWEEP=math.hypot(XMAX,YMAX)      # 0.2995 m
TURN_GUARD=SWEEP+0.04            # 회전 시 중심기준 이 거리보다 가까우면 정지
PATH_GUARD=0.08                  # 직진 시 경로 여유 한계
rclpy.init(); n=rclpy.create_node('loop')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
pub=n.create_publisher(Twist,'/cmd_vel',10)
st={'cen':None,'fwd':None,'o':None}
def sc(m):
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12)
    if not ok.sum(): return
    th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
    dc=np.hypot(px,py)
    st['cen']=float(np.percentile(dc,0.5))          # 강건 최소(중심기준)
    band=np.abs(py)<=(YMAX+0.03); sel=band&(px>XMAX)
    st['fwd']=float(np.percentile(px[sel]-XMAX,0.5)) if sel.sum()>3 else 9.99
def oc(m):
    p=m.pose.pose; q=p.orientation
    st['o']=(p.position.x,p.position.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
n.create_subscription(Odometry,'/odometry/filtered',oc,qos_profile_sensor_data)
def mb():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=t.rotation
        return (t.translation.x,t.translation.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
    except Exception: return None
t0=time.time()
while (st['o'] is None or st['cen'] is None) and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
if st['o'] is None: print("odom 준비 안됨"); raise SystemExit
print(f"시작: 중심기준 최근접 {st['cen']*100:.0f}cm (회전 필요 {TURN_GUARD*100:.0f}cm), 전방경로 {st['fwd']*100:.0f}cm")
if st['cen']<TURN_GUARD: print("!! 회전 공간 부족 — 중단."); raise SystemExit
o0=st['o']; m0=mb()
if m0 is None: print("(주의) slam TF 미확보 — odom만 기록됨")
ABORT=""
for leg in range(4):
    s=st['o']; tw=Twist(); tw.linear.x=SPD; t1=time.time()
    while math.hypot(st['o'][0]-s[0],st['o'][1]-s[1])<SIDE:
        pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
        if st['fwd'] is not None and st['fwd']<PATH_GUARD: ABORT=f"{leg+1}변 경로가드 {st['fwd']*100:.0f}cm"; break
        if time.time()-t1>30: break
    for _ in range(8): pub.publish(Twist()); time.sleep(0.02)
    if ABORT: break
    h0=st["o"][2]; tw=Twist(); t1=time.time()
    def dh(): d=st["o"][2]-h0; return abs(((d+math.pi)%(2*math.pi))-math.pi)
    TGT=math.radians(90)
    while dh()<TGT:
        rem=TGT-dh()
        tw.angular.z=Wz if rem>math.radians(15) else Wz*0.35   # 목표 15도 전 감속(오버슈트 억제)
        pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.03)
        if st['cen'] is not None and st['cen']<TURN_GUARD: ABORT=f"{leg+1}코너 회전가드 {st['cen']*100:.0f}cm"; break
        if time.time()-t1>20: break
    for _ in range(8): pub.publish(Twist()); time.sleep(0.02)
    if ABORT: break
    print(f"  {leg+1}변 완료: odom=({st['o'][0]:.3f},{st['o'][1]:.3f}) hd={math.degrees(st['o'][2]):.1f}")
for _ in range(15): pub.publish(Twist()); time.sleep(0.02)
time.sleep(1.5)
for _ in range(25): rclpy.spin_once(n,timeout_sec=0.05)
o1=st['o']; m1=mb()
od=math.hypot(o1[0]-o0[0],o1[1]-o0[1]); odh=math.degrees(((o1[2]-o0[2]+math.pi)%(2*math.pi))-math.pi)
print(f"\n=== 결과 ({'중단: '+ABORT if ABORT else '4변 완주'}) ===")
print(f"  odom 이동 {od*100:.1f}cm, heading {odh:+.1f}deg")
if m0 and m1:
    sd=math.hypot(m1[0]-m0[0],m1[1]-m0[1]); sdh=math.degrees(((m1[2]-m0[2]+math.pi)%(2*math.pi))-math.pi)
    print(f"  slam 이동 {sd*100:.1f}cm, heading {sdh:+.1f}deg  (지면검증)")
    print(f"  ★ 드리프트: 위치 {abs(od-sd)*100:.1f}cm 이상, heading {abs(odh-sdh):.1f}deg")
    print(f"    (스케일 교정 전 기준값: 위치 ~10cm/루프 — 단 그건 잘못된 스케일 기반이라 무효)")
else:
    print("  slam TF 미확보 — 드리프트 비교 불가")
rclpy.shutdown()
PY
