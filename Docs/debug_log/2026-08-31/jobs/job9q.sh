#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -9 -f joy_linux 2>/dev/null; pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_node 2>/dev/null; sleep 2
setsid nohup ros2 run joy_linux joy_linux_node --ros-args -p dev:=/dev/input/js0 -p deadzone:=0.12 -p autorepeat_rate:=20.0 > /tmp/joy.log 2>&1 &
sleep 2
setsid nohup ros2 run teleop_twist_joy teleop_node --ros-args --params-file ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/joy_teleop.yaml -r /cmd_vel:=/cmd_vel_test > /tmp/teleop.log 2>&1 &
sleep 3
echo "joy_node $(pgrep -f joy_linux | wc -l)개, teleop $(pgrep -f teleop_node | wc -l)개 (각 1이어야)"
echo "======= 15초! 좌스틱 앞→뒤, 우스틱 좌→우 (계속 조작) ======="
python3 - << 'PY'
import time, rclpy, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
class A(Node):
    def __init__(s):
        super().__init__('c'); s.xmn=9;s.xmx=-9;s.zmn=9;s.zmx=-9;s.cc=0;s.jc=0;s.a1mx=-9;s.a1mn=9;s.a2mx=-9;s.a2mn=9
        s.create_subscription(Twist,'/cmd_vel_test',s.cb,10)
        s.create_subscription(Joy,'/joy',s.jb,10)
    def cb(s,m): s.cc+=1;s.xmx=max(s.xmx,m.linear.x);s.xmn=min(s.xmn,m.linear.x);s.zmx=max(s.zmx,m.angular.z);s.zmn=min(s.zmn,m.angular.z)
    def jb(s,m):
        s.jc+=1
        if len(m.axes)>2: s.a1mx=max(s.a1mx,m.axes[1]);s.a1mn=min(s.a1mn,m.axes[1]);s.a2mx=max(s.a2mx,m.axes[2]);s.a2mn=min(s.a2mn,m.axes[2])
rclpy.init(); n=A(); e=time.time()+15
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
o=[f"/joy {n.jc}, /cmd_vel_test {n.cc}"]
o.append(f"  axis1(전후) {n.a1mn:+.2f}~{n.a1mx:+.2f} → linear.x {n.xmn:+.3f}~{n.xmx:+.3f}  (전진+ 후진-)")
o.append(f"  axis2(좌우) {n.a2mn:+.2f}~{n.a2mx:+.2f} → angular.z {n.zmn:+.3f}~{n.zmx:+.3f}  (좌회전+ 우회전-)")
fwd=n.xmx>0.02; bwd=n.xmn<-0.02; lft=n.zmx>0.02; rgt=n.zmn<-0.02
o.append(f"  전진{'✓' if fwd else '✗'} 후진{'✓' if bwd else '✗'} 좌회전{'✓' if lft else '✗'} 우회전{'✓' if rgt else '✗'}")
o.append("  => ✅ 매핑·부호 전부 정상" if (fwd and bwd and lft and rgt) else "  => 일부 미확인(4방향 다 조작?) 또는 부호수정 필요")
sys.stdout.write("\n".join(o)+"\n"); sys.stdout.flush()
PY
echo END
