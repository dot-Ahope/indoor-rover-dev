#!/bin/bash
# 제자리 360° 회전 + 풋프린트 인식 충돌 가드(로버 외곽 0.50×0.33 vs 벽 실거리). 접지·사용자 입회.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
W=0.28; SAFE=0.03; TARGET=math.radians(360); TIMEOUT=70.0
# 로버 외곽(base_link): x[-0.25,0.25] y[-0.165,0.165]. LiDAR@(0.152,0), yaw=π (확정)
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
def clearances(rng,ang):
    th=ang+LYAW
    px=LX+rng*np.cos(th); py=rng*np.sin(th)          # 벽점 base_link 좌표
    dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX])
    dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
    return np.sqrt(dx*dx+dy*dy)                        # 로버 외곽~벽 실거리
class R(Node):
    def __init__(s):
        super().__init__('map_spin'); s.clr=None; s.yaw=None; s.acc=0.0; s.ang=None
        s.pub=s.create_publisher(Twist,'/cmd_vel',10)
        s.create_subscription(LaserScan,'/scan',s.scan,qos_profile_sensor_data)
        s.create_subscription(Odometry,'/odometry/filtered',s.odom,qos_profile_sensor_data)
    def scan(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
        ok=np.isfinite(r)&(r>0.05)
        if ok.sum(): c=clearances(r[ok],a[ok]); s.clr=float(np.min(c))
    def odom(s,m):
        q=m.pose.pose.orientation; y=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
        if s.yaw is not None:
            d=y-s.yaw; d=(d+math.pi)%(2*math.pi)-math.pi; s.acc+=d
        s.yaw=y
def stop(n):
    t=Twist()
    for _ in range(12): n.pub.publish(t); time.sleep(0.02)
rclpy.init(); n=R(); t0=time.time()
while (n.clr is None or n.yaw is None) and time.time()<t0+3: rclpy.spin_once(n,timeout_sec=0.1)
if n.clr is None: print("NO_SCAN"); stop(n); raise SystemExit
print(f"시작 로버-벽 최소 실거리 = {n.clr*100:.1f} cm")
if n.clr < SAFE: print(f"!! 이미 {n.clr*100:.1f}cm < {SAFE*100:.0f}cm — 회전 불가. 공간 확보 필요."); stop(n); raise SystemExit
print(f"360도 회전 시작 (W={W} rad/s, 풋프린트 가드 {SAFE*100:.0f}cm)...")
tw=Twist(); tw.angular.z=W; start=time.time(); reason=""; minseen=n.clr
while True:
    n.pub.publish(tw); rclpy.spin_once(n,timeout_sec=0.05)
    if n.clr is not None:
        minseen=min(minseen,n.clr)
        if n.clr<SAFE: reason=f"풋프린트 가드 (로버-벽 {n.clr*100:.1f}cm)"; break
    if abs(n.acc)>=TARGET*0.98: reason="360도 완료"; break
    if time.time()-start>TIMEOUT: reason="타임아웃"; break
stop(n)
print(f"정지. 사유: {reason}. 누적회전={math.degrees(n.acc):+.0f}deg, 최소 로버-벽거리={minseen*100:.1f}cm")
n.destroy_node(); rclpy.shutdown()
PY
echo "===맵 상태==="; timeout 6 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE "width|height" | tr '\n' ' '; echo
