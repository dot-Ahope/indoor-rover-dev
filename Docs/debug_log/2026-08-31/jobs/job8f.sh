#!/bin/bash
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
W=0.22; SAFE=0.03; TARGET=math.radians(180); TIMEOUT=40.0
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
def clr(rng,ang):
    th=ang+LYAW; px=LX+rng*np.cos(th); py=rng*np.sin(th)
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    return np.sqrt(dx*dx+dy*dy)
class R(Node):
    def __init__(s):
        super().__init__('map_spin'); s.c=None; s.yaw=None; s.acc=0.0; s.wrate=0.0
        # 동적 follow: /scan·/scan_raw 지연 실측(회전 중)
        s.slat=[]; s.rlat=[]
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.sc,qos_profile_sensor_data)
        s.create_subscription(LaserScan,'/scan_raw',s.scr,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.od,qos_profile_sensor_data)
    def sc(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
        if ok.sum(): s.c=float(np.min(clr(r[ok],a[ok])))
        s.slat.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9))
    def scr(s,m): s.rlat.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9))
    def od(s,m):
        q=m.pose.pose.orientation; y=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
        s.wrate=m.twist.twist.angular.z
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
if n.c<SAFE: print("ABORT tight",flush=True); stop(n); raise SystemExit
tw=Twist(); tw.angular.z=W; start=time.time(); reason=""; minc=n.c; last=0
while True:
    n.pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.05)
    if n.c is not None:
        minc=min(minc,n.c)
        if n.c<SAFE: reason=f"GUARD {n.c*100:.1f}cm"; break
    if abs(n.acc)>=TARGET*0.98: reason="DONE_180"; break
    if time.time()-start>TIMEOUT: reason="TIMEOUT"; break
    if time.time()-last>2: print(f"  ...{math.degrees(n.acc):+.0f}deg",flush=True); last=time.time()
stop(n)
sm=np.mean(n.slat)*1000 if n.slat else 0; rm=np.mean(n.rlat)*1000 if n.rlat else 0
wr=abs(n.wrate)
print(f"SPIN_END reason={reason} acc={math.degrees(n.acc):+.0f}deg",flush=True)
print(f"  회전중 지연: /scan_raw {rm:.0f}ms(밀림 {math.degrees(rm/1000*0.22):.2f}deg) → /scan {sm:.0f}ms(밀림 {math.degrees(sm/1000*0.22):.2f}deg @0.22rad/s)",flush=True)
n.destroy_node(); rclpy.shutdown()
PY
echo "SPIN_EXIT $(date '+%T')"
