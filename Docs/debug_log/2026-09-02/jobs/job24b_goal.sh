#!/bin/bash
# Nav2 첫 자율주행: 현재 위치 기준 정면 D미터 목표 전송 + 모니터링
D=${1:-0.5}; TMO=${2:-60}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$D" "$TMO" << 'PY'
import math, time, sys, rclpy, tf2_ros
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
D=float(sys.argv[1]); TMO=float(sys.argv[2])
rclpy.init(); n=rclpy.create_node('nav_goal')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
cmd=n.create_publisher(Twist,'/cmd_vel',10)
def pose():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=t.rotation
        return (t.translation.x,t.translation.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z),q)
    except Exception: return None
t0=time.time()
while pose() is None and time.time()<t0+8: rclpy.spin_once(n,timeout_sec=0.1)
p0=pose()
if p0 is None: print("map->base_link TF 없음 — slam 확인 필요"); raise SystemExit
x0,y0,th0,q0=p0
gx=x0+D*math.cos(th0); gy=y0+D*math.sin(th0)
print(f"현재 위치 map=({x0:.3f},{y0:.3f}) heading={math.degrees(th0):.1f}deg")
print(f"목표     map=({gx:.3f},{gy:.3f}) — 정면 {D}m, 같은 방향")
ac=ActionClient(n,NavigateToPose,'navigate_to_pose')
if not ac.wait_for_server(timeout_sec=10.0): print("navigate_to_pose 액션서버 없음"); raise SystemExit
g=NavigateToPose.Goal()
g.pose=PoseStamped(); g.pose.header.frame_id='map'
g.pose.header.stamp=n.get_clock().now().to_msg()
g.pose.pose.position.x=gx; g.pose.pose.position.y=gy
g.pose.pose.orientation=q0
state={'fb':None,'n':0}
def fbcb(f):
    state['fb']=f.feedback; state['n']+=1
print("목표 전송...")
fut=ac.send_goal_async(g,feedback_callback=fbcb)
rclpy.spin_until_future_complete(n,fut,timeout_sec=10.0)
gh=fut.result()
if gh is None or not gh.accepted: print("목표 거부됨"); raise SystemExit
print("목표 수락 — 주행 시작")
rf=gh.get_result_async()
t1=time.time(); last=0
while not rf.done() and time.time()-t1<TMO:
    rclpy.spin_once(n,timeout_sec=0.2)
    if time.time()-last>3.0:
        last=time.time(); p=pose(); fb=state['fb']
        rem=getattr(fb,'distance_remaining',float('nan')) if fb else float('nan')
        if p: print(f"  t={time.time()-t1:5.1f}s  위치=({p[0]:.3f},{p[1]:.3f}) hd={math.degrees(p[2]):6.1f}  남은거리={rem:.2f}m")
if not rf.done():
    print("!! 타임아웃 — 목표 취소")
    gh.cancel_goal_async(); rclpy.spin_once(n,timeout_sec=2.0)
    for _ in range(10): cmd.publish(Twist()); time.sleep(0.05)
else:
    res=rf.result()
    codes={0:'UNKNOWN',1:'ACCEPTED',2:'EXECUTING',3:'CANCELING',4:'SUCCEEDED',5:'CANCELED',6:'ABORTED'}
    print(f"결과: {codes.get(res.status,res.status)}")
time.sleep(1.0)
for _ in range(10): rclpy.spin_once(n,timeout_sec=0.05)
p1=pose()
if p1:
    err=math.hypot(p1[0]-gx,p1[1]-gy); moved=math.hypot(p1[0]-x0,p1[1]-y0)
    dth=math.degrees(((p1[2]-th0+math.pi)%(2*math.pi))-math.pi)
    print(f"\n=== 결과 ===")
    print(f"  최종 위치 map=({p1[0]:.3f},{p1[1]:.3f}) hd={math.degrees(p1[2]):.1f}deg")
    print(f"  이동 거리 {moved:.3f} m (목표 {D}m)")
    print(f"  목표까지 잔여 오차 {err*100:.1f} cm  (허용 15cm)")
    print(f"  heading 변화 {dth:+.1f}deg (허용 ±14deg)")
    print(f"  판정: {'✅ 목표 도달' if err<0.15 else '△ 허용오차 초과'}")
rclpy.shutdown()
PY
