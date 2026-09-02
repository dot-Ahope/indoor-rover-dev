#!/bin/bash
# Nav2 방향 지정 목표: 현재 heading 기준 ANG도 방향으로 D미터, 목표자세=진행방향
D=${1:-0.5}; ANG=${2:-180}; TMO=${3:-90}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$D" "$ANG" "$TMO" << 'PY'
import math, time, sys, rclpy, tf2_ros
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
D=float(sys.argv[1]); ANG=math.radians(float(sys.argv[2])); TMO=float(sys.argv[3])
rclpy.init(); n=rclpy.create_node('navdir')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
cmd=n.create_publisher(Twist,'/cmd_vel',10)
def pose():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=t.rotation
        return (t.translation.x,t.translation.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
    except Exception: return None
t0=time.time()
while pose() is None and time.time()<t0+8: rclpy.spin_once(n,timeout_sec=0.1)
p0=pose()
if p0 is None: print("map->base_link TF 없음"); raise SystemExit
x0,y0,th0=p0; gth=th0+ANG
gx=x0+D*math.cos(gth); gy=y0+D*math.sin(gth)
print(f"현재 map=({x0:.3f},{y0:.3f}) hd={math.degrees(th0):.1f}deg")
print(f"목표 map=({gx:.3f},{gy:.3f}) hd={math.degrees(gth):.1f}deg  ← 현재 기준 {math.degrees(ANG):.0f}도 방향 {D}m")
print(f"  → 로버는 {math.degrees(ANG):.0f}도 회전 후 {D}m 주행해야 함")
ac=ActionClient(n,NavigateToPose,'navigate_to_pose')
if not ac.wait_for_server(timeout_sec=10.0): print("액션서버 없음"); raise SystemExit
g=NavigateToPose.Goal(); g.pose=PoseStamped(); g.pose.header.frame_id='map'
g.pose.header.stamp=n.get_clock().now().to_msg()
g.pose.pose.position.x=gx; g.pose.pose.position.y=gy
g.pose.pose.orientation.z=math.sin(gth/2); g.pose.pose.orientation.w=math.cos(gth/2)
fb={'d':float('nan')}
def fbcb(f): fb['d']=getattr(f.feedback,'distance_remaining',float('nan'))
print("목표 전송...")
fut=ac.send_goal_async(g,feedback_callback=fbcb)
rclpy.spin_until_future_complete(n,fut,timeout_sec=10.0)
gh=fut.result()
if gh is None or not gh.accepted: print("목표 거부됨"); raise SystemExit
print("수락 — 자율주행 시작")
rf=gh.get_result_async(); t1=time.time(); last=0
while not rf.done() and time.time()-t1<TMO:
    rclpy.spin_once(n,timeout_sec=0.2)
    if time.time()-last>3.0:
        last=time.time(); p=pose()
        if p: print(f"  t={time.time()-t1:5.1f}s  ({p[0]:+.3f},{p[1]:+.3f}) hd={math.degrees(p[2]):+7.1f}  남은={fb['d']:.2f}m")
codes={0:'UNKNOWN',1:'ACCEPTED',2:'EXECUTING',3:'CANCELING',4:'SUCCEEDED',5:'CANCELED',6:'ABORTED'}
if not rf.done():
    print("!! 타임아웃 — 취소"); gh.cancel_goal_async(); rclpy.spin_once(n,timeout_sec=2.0)
    for _ in range(10): cmd.publish(Twist()); time.sleep(0.05)
else:
    print(f"결과: {codes.get(rf.result().status, rf.result().status)}")
time.sleep(1.0)
for _ in range(12): rclpy.spin_once(n,timeout_sec=0.05)
p1=pose()
if p1:
    err=math.hypot(p1[0]-gx,p1[1]-gy)
    dth=math.degrees(((p1[2]-gth+math.pi)%(2*math.pi))-math.pi)
    turned=math.degrees(((p1[2]-th0+math.pi)%(2*math.pi))-math.pi)
    print(f"\n=== 결과 ===")
    print(f"  최종 map=({p1[0]:.3f},{p1[1]:.3f}) hd={math.degrees(p1[2]):.1f}deg")
    print(f"  실제 회전량 {turned:+.1f}deg (지시 {math.degrees(ANG):.0f}deg)")
    print(f"  목표 위치 오차 {err*100:.1f}cm (허용 15cm) / 자세 오차 {dth:+.1f}deg (허용 ±14deg)")
    print(f"  판정: {'✅ 도달' if err<0.15 and abs(dth)<14 else '△ 오차 초과'}")
rclpy.shutdown()
PY
