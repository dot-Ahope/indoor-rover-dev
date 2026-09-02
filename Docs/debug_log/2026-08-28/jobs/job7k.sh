#!/bin/bash
# 견고한 detach 회전 코어 — 로그에 진행상황 실시간 flush 기록. WiFi 무관하게 완주.
exec >>/tmp/spin.log 2>&1
echo "SPIN_START $(date '+%T')"
source /opt/ros/humble/setup.bash 2>/dev/null; source ~/ros2_ws/install/setup.bash 2>/dev/null
python3 -u - << 'PY'
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
W=0.28; SAFE=0.03; TARGET=math.radians(360); TIMEOUT=75.0
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
def clr(rng,ang):
    th=ang+LYAW; px=LX+rng*np.cos(th); py=rng*np.sin(th)
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    return np.sqrt(dx*dx+dy*dy)
class R(Node):
    def __init__(s):
        super().__init__('map_spin'); s.c=None; s.yaw=None; s.acc=0.0
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.od,qos_profile_sensor_data)
    def sc(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
        if ok.sum(): s.c=float(np.min(clr(r[ok],a[ok])))
    def od(s,m):
        q=m.pose.pose.orientation; y=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
        if s.yaw is not None:
            d=y-s.yaw; d=(d+math.pi)%(2*math.pi)-math.pi; s.acc+=d
        s.yaw=y
def stop(n):
    t=Twist()
    for _ in range(12): n.pub.publish(t); time.sleep(0.02)
rclpy.init(); n=R(); t0=time.time()
while (n.c is None or n.yaw is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
if n.c is None: print("NO_SCAN",flush=True); stop(n); raise SystemExit
print(f"START clr={n.c*100:.1f}cm",flush=True)
if n.c<SAFE: print(f"ABORT: {n.c*100:.1f}cm<{SAFE*100:.0f}",flush=True); stop(n); raise SystemExit
tw=Twist(); tw.angular.z=W; start=time.time(); reason=""; minc=n.c; last=0
while True:
    n.pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.05)
    if n.c is not None:
        minc=min(minc,n.c)
        if n.c<SAFE: reason=f"GUARD {n.c*100:.1f}cm"; break
    if abs(n.acc)>=TARGET*0.98: reason="DONE_360"; break
    if time.time()-start>TIMEOUT: reason="TIMEOUT"; break
    if time.time()-last>2:
        print(f"  ...{math.degrees(n.acc):+.0f}deg minclr={minc*100:.1f}cm",flush=True); last=time.time()
stop(n)
print(f"SPIN_END reason={reason} acc={math.degrees(n.acc):+.0f}deg minclr={minc*100:.1f}cm",flush=True)
n.destroy_node(); rclpy.shutdown()
PY
echo "SPIN_EXIT $(date '+%T')"
