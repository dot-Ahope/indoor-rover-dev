#!/bin/bash
# 목표 전송 + cmd_vel 체인 모니터 (controller→/cmd_vel_nav→smoother→/cmd_vel)
D=${1:-0.5}; ANG=${2:-180}; TMO=${3:-70}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$D" "$ANG" "$TMO" << 'PY'
import math, time, sys, rclpy, tf2_ros
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
D=float(sys.argv[1]); ANG=math.radians(float(sys.argv[2])); TMO=float(sys.argv[3])
rclpy.init(); n=rclpy.create_node('goalmon')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
cv={'nav':(0,0),'out':(0,0),'nav_n':0,'out_n':0}
def cb_nav(m): cv['nav']=(m.linear.x,m.angular.z); cv['nav_n']+=1
def cb_out(m): cv['out']=(m.linear.x,m.angular.z); cv['out_n']+=1
n.create_subscription(Twist,'/cmd_vel_nav',cb_nav,10)
n.create_subscription(Twist,'/cmd_vel',cb_out,10)
def pose():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=t.rotation
        return (t.translation.x,t.translation.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
    except Exception: return None
t0=time.time()
while pose() is None and time.time()<t0+8: rclpy.spin_once(n,timeout_sec=0.1)
p0=pose(); x0,y0,th0=p0; gth=th0+ANG
gx=x0+D*math.cos(gth); gy=y0+D*math.sin(gth)
print(f"현재 hd={math.degrees(th0):.1f} → 목표 hd={math.degrees(gth):.1f} ({math.degrees(ANG):.0f}도 회전 후 {D}m)")
ac=ActionClient(n,NavigateToPose,'navigate_to_pose')
ac.wait_for_server(timeout_sec=10.0)
g=NavigateToPose.Goal(); g.pose=PoseStamped(); g.pose.header.frame_id='map'
g.pose.header.stamp=n.get_clock().now().to_msg()
g.pose.pose.position.x=gx; g.pose.pose.position.y=gy
g.pose.pose.orientation.z=math.sin(gth/2); g.pose.pose.orientation.w=math.cos(gth/2)
fut=ac.send_goal_async(g); rclpy.spin_until_future_complete(n,fut,timeout_sec=10.0)
gh=fut.result()
if gh is None or not gh.accepted: print("거부"); raise SystemExit
print("수락 — 모니터링 (cmd_vel_nav = RPP 출력 / cmd_vel = 스무더 출력)")
rf=gh.get_result_async(); t1=time.time(); last=0
while not rf.done() and time.time()-t1<TMO:
    rclpy.spin_once(n,timeout_sec=0.1)
    if time.time()-last>2.0:
        last=time.time(); p=pose()
        print(f"  t={time.time()-t1:5.1f}s hd={math.degrees(p[2]):+7.1f} | RPP(v={cv['nav'][0]:+.3f} w={cv['nav'][1]:+.3f} n={cv['nav_n']:4d}) | OUT(v={cv['out'][0]:+.3f} w={cv['out'][1]:+.3f} n={cv['out_n']:4d})")
codes={4:'SUCCEEDED',5:'CANCELED',6:'ABORTED'}
if not rf.done():
    print("타임아웃 — 취소"); gh.cancel_goal_async(); rclpy.spin_once(n,timeout_sec=2.0)
else: print(f"결과: {codes.get(rf.result().status,rf.result().status)}")
p1=pose()
print(f"\n최종 hd={math.degrees(p1[2]):.1f}, 회전량 {math.degrees(((p1[2]-th0+math.pi)%(2*math.pi))-math.pi):+.1f}deg, 위치오차 {math.hypot(p1[0]-gx,p1[1]-gy)*100:.1f}cm")
rclpy.shutdown()
PY
