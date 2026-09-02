#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo -n "battery: "; timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NONE
echo "스캔 지연(재스탬프):"
python3 - << 'PY'
import time, statistics, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s):
        super().__init__('t'); s.r=[]; s.n=[]
        s.create_subscription(LaserScan,'/scan_raw',lambda m:s.r.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9)),qos_profile_sensor_data)
        s.create_subscription(LaserScan,'/scan',lambda m:s.n.append((s.get_clock().now().nanoseconds*1e-9)-(m.header.stamp.sec+m.header.stamp.nanosec*1e-9)),qos_profile_sensor_data)
rclpy.init(); n=A(); e=time.time()+5
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
if n.r and n.n: print(f"  /scan_raw {statistics.mean(n.r)*1000:.0f}ms → /scan {statistics.mean(n.n)*1000:.0f}ms")
else: print(f"  raw={len(n.r)} new={len(n.n)}")
PY
echo "시작 여유(로버 외곽↔벽):"
python3 - << 'PY'
import math, numpy as np, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
class A(Node):
    def __init__(s): super().__init__('a'); s.c=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
        if ok.sum():
            th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
            dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
            s.c=float(np.min(np.sqrt(dx*dx+dy*dy)))
rclpy.init(); n=A(); t=time.time()
while n.c is None and time.time()<t+4: rclpy.spin_once(n,timeout_sec=0.2)
print(f"  최소 여유 = {n.c*100:.0f}cm" if n.c else "  NO_SCAN")
PY
