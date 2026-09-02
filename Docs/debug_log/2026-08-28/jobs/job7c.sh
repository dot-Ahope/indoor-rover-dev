#!/bin/bash
# SLAM 맵핑용 제자리 360° 회전 + 실시간 충돌 가드. 접지·사방 확보 상태, 사용자 입회.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import numpy as np
W=0.22; START_MIN=0.28; GUARD=0.22; TARGET=math.radians(360); TIMEOUT=45.0
class R(Node):
    def __init__(s):
        super().__init__('map_spin'); s.minr=None; s.yaw=None; s.y0=None; s.acc=0.0
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.scan,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.odom,qos_profile_sensor_data)
    def scan(s,m):
        r=np.array(m.ranges,np.float32); r=r[np.isfinite(r)&(r>0.05)]
        s.minr=float(np.min(r)) if r.size else None
    def odom(s,m):
        q=m.pose.pose.orientation; y=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
        if s.yaw is not None:
            d=y-s.yaw
            if d>math.pi: d-=2*math.pi
            if d<-math.pi: d+=2*math.pi
            s.acc+=d
        s.yaw=y
def stop(n):
    t=Twist()
    for _ in range(10): n.pub.publish(t); time.sleep(0.02)
rclpy.init(); n=R()
t0=time.time()
while (n.minr is None or n.yaw is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
if n.minr is None: print("NO_SCAN"); stop(n); raise SystemExit
print(f"시작 최근접 = {n.minr:.2f}m")
if n.minr < START_MIN:
    print(f"!! 공간 부족 (최근접 {n.minr:.2f} < {START_MIN}m) — 회전 중단. 주변 더 확보 요망."); stop(n); raise SystemExit
print(f"360도 회전 시작 (W={W} rad/s, 가드 {GUARD}m)...")
tw=Twist(); tw.angular.z=W; start=time.time(); reason=""
while True:
    n.pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.05)
    if n.minr is not None and n.minr < GUARD: reason=f"충돌가드 발동 (최근접 {n.minr:.2f}m)"; break
    if abs(n.acc) >= TARGET*0.98: reason="360도 완료"; break
    if time.time()-start > TIMEOUT: reason="타임아웃"; break
stop(n)
print(f"정지. 사유: {reason}. 누적 회전 = {math.degrees(n.acc):+.0f} deg, 종료 최근접 = {n.minr:.2f}m")
n.destroy_node(); rclpy.shutdown()
PY
echo "===회전 후 맵 상태==="
timeout 8 ros2 topic hz /map 2>&1 | grep -aE "average|does not" | tail -1
timeout 6 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE "width|height" | tr '\n' ' '; echo
