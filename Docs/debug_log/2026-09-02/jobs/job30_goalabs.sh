#!/bin/bash
# 절대좌표(map) 목표: x y yaw_deg timeout
GX=${1:-0}; GY=${2:-0}; GTH=${3:-0}; TMO=${4:-150}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$GX" "$GY" "$GTH" "$TMO" << 'PY'
import math, time, sys, rclpy, tf2_ros
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
GX=float(sys.argv[1]); GY=float(sys.argv[2]); GTH=math.radians(float(sys.argv[3])); TMO=float(sys.argv[4])
rclpy.init(); n=rclpy.create_node('goalabs')
buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n)
cv={'o':(0,0)}
def cbo(m): cv['o']=(m.linear.x,m.angular.z)
from geometry_msgs.msg import Twist as TW
n.create_subscription(TW,'/cmd_vel',cbo,10)
def pose():
    try:
        t=buf.lookup_transform('map','base_link',rclpy.time.Time()).transform; q=t.rotation
        return (t.translation.x,t.translation.y,math.atan2(2*(q.w*q.z),1-2*q.z*q.z))
    except Exception: return None
t0=time.time()
while pose() is None and time.time()<t0+8: rclpy.spin_once(n,timeout_sec=0.1)
p0=pose()
print(f"현재 map=({p0[0]:.3f},{p0[1]:.3f}) hd={math.degrees(p0[2]):.1f} → 목표 map=({GX:.2f},{GY:.2f}) hd={math.degrees(GTH):.0f}")
ac=ActionClient(n,NavigateToPose,'navigate_to_pose'); ac.wait_for_server(timeout_sec=10.0)
g=NavigateToPose.Goal(); g.pose=PoseStamped(); g.pose.header.frame_id='map'
g.pose.header.stamp=n.get_clock().now().to_msg()
g.pose.pose.position.x=GX; g.pose.pose.position.y=GY
g.pose.pose.orientation.z=math.sin(GTH/2); g.pose.pose.orientation.w=math.cos(GTH/2)
fut=ac.send_goal_async(g); rclpy.spin_until_future_complete(n,fut,timeout_sec=10.0)
gh=fut.result()
if gh is None or not gh.accepted: print("거부"); raise SystemExit
print("수락 — 주행")
rf=gh.get_result_async(); t1=time.time(); last=0
while not rf.done() and time.time()-t1<TMO:
    rclpy.spin_once(n,timeout_sec=0.1)
    if time.time()-last>3.0:
        last=time.time(); p=pose()
        d=math.hypot(p[0]-GX,p[1]-GY)
        print(f"  t={time.time()-t1:5.1f}s ({p[0]:+.2f},{p[1]:+.2f}) hd={math.degrees(p[2]):+6.1f} 목표까지={d:.2f}m cmd(v={cv['o'][0]:+.2f} w={cv['o'][1]:+.2f})")
codes={4:'SUCCEEDED',5:'CANCELED',6:'ABORTED'}
if not rf.done():
    print("타임아웃 — 취소"); gh.cancel_goal_async(); rclpy.spin_once(n,timeout_sec=2.0)
    from geometry_msgs.msg import Twist as T2
    pub=n.create_publisher(T2,'/cmd_vel',10)
    for _ in range(10): pub.publish(T2()); time.sleep(0.05)
    res='TIMEOUT'
else: res=codes.get(rf.result().status,rf.result().status); print(f"결과: {res}")
p1=pose(); err=math.hypot(p1[0]-GX,p1[1]-GY)
dth=math.degrees(((p1[2]-GTH+math.pi)%(2*math.pi))-math.pi)
print(f"최종 ({p1[0]:+.3f},{p1[1]:+.3f}) hd={math.degrees(p1[2]):.1f} | 위치오차 {err*100:.1f}cm 자세오차 {dth:+.1f}deg | 소요 {time.time()-t1:.0f}s")
rclpy.shutdown()
PY
