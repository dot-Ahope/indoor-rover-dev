#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "노드: $(ros2 node list | grep -E 'joy|teleop' | tr '\n' ' ')"
echo "/joy 구독자(teleop 연결?): $(ros2 topic info /joy 2>/dev/null | grep -c Subscription)"
echo "======= 15초! 좌스틱 앞으로 끝까지 + 우스틱 좌우 크게 ======="
python3 - << 'PY'
import time, rclpy, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
class A(Node):
    def __init__(s):
        super().__init__('m'); s.a1=[]; s.a2=[]; s.x=[]; s.z=[]; s.jc=0; s.cc=0
        s.create_subscription(Joy,'/joy',s.jcb,10)
        s.create_subscription(Twist,'/cmd_vel_test',s.ccb,10)
    def jcb(s,m):
        s.jc+=1
        if len(m.axes)>2: s.a1.append(m.axes[1]); s.a2.append(m.axes[2])
    def ccb(s,m): s.cc+=1; s.x.append(m.linear.x); s.z.append(m.angular.z)
rclpy.init(); n=A(); e=time.time()+15
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
def rng(v): return (min(v),max(v)) if v else (0,0)
a1=rng(n.a1); a2=rng(n.a2); x=rng(n.x); z=rng(n.z)
o=[f"/joy 수신 {n.jc}, /cmd_vel_test 수신 {n.cc}"]
o.append(f"  axis[1] 범위: {a1[0]:+.2f}~{a1[1]:+.2f}   → linear.x: {x[0]:+.3f}~{x[1]:+.3f}")
o.append(f"  axis[2] 범위: {a2[0]:+.2f}~{a2[1]:+.2f}   → angular.z: {z[0]:+.3f}~{z[1]:+.3f}")
joymoved = (a1[1]-a1[0]>0.2) or (a2[1]-a2[0]>0.2)
cmdmoved = (x[1]-x[0]>0.01) or (z[1]-z[0]>0.01)
if not joymoved: o.append("  => /joy 자체가 안 움직임 (스틱 조작 안됨/joy_node 문제)")
elif joymoved and not cmdmoved: o.append("  => /joy는 움직이나 cmd_vel 0 = teleop 설정 문제")
else: o.append("  => ✅ joy→cmd_vel 정상 매핑")
sys.stdout.write("\n".join(o)+"\n"); sys.stdout.flush()
PY
echo END
