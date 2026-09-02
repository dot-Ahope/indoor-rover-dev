#!/bin/bash
# deadzone 0.25 재배포 → 단일 인스턴스 → 중립 cmd_vel=0 검증(/cmd_vel_test, 보드 무영향)
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_bringup ~/ros2_ws/src/
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
echo "===스테일 완전 종료==="
pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; pkill -9 -f joy_node 2>/dev/null; sleep 3
echo "잔존: teleop $(pgrep -f teleop|wc -l), joy $(pgrep -f 'joy_linux|joy_node'|wc -l)"
echo "===단일 기동 (teleop→/cmd_vel_test)==="
setsid nohup ros2 run joy_linux joy_linux_node --ros-args --params-file ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/joy_teleop.yaml -r __node:=joy_node > /tmp/joy.log 2>&1 &
sleep 2
setsid nohup ros2 run teleop_twist_joy teleop_node --ros-args --params-file ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/joy_teleop.yaml -r /cmd_vel:=/cmd_vel_test > /tmp/teleop.log 2>&1 &
sleep 3
echo "노드: $(ros2 node list | grep -E 'joy_node|teleop' | sort | tr '\n' ' ')"
echo "===★ 스틱에서 손 떼주세요 — 중립 6초 측정 (cmd_vel_test=0이어야 안전)==="
python3 - << 'PY'
import time, rclpy, sys
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s): super().__init__('c'); s.x=[];s.z=[];s.a1=[]; s.create_subscription(Twist,'/cmd_vel_test',s.cb,10); s.create_subscription(Joy,'/joy',s.jb,10)
    def cb(s,m): s.x.append(m.linear.x); s.z.append(m.angular.z)
    def jb(s,m):
        if len(m.axes)>1: s.a1.append(m.axes[1])
rclpy.init(); n=A(); e=time.time()+6
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
import statistics as st
if n.x:
    sys.stdout.write(f"중립 axis1 평균 {st.mean(n.a1):+.3f}\n")
    sys.stdout.write(f"중립 cmd_vel: linear.x max|{max(abs(min(n.x)),abs(max(n.x))):.4f}| angular.z max|{max(abs(min(n.z)),abs(max(n.z))):.4f}|\n")
    ok=max(abs(min(n.x)),abs(max(n.x)))<0.005 and max(abs(min(n.z)),abs(max(n.z)))<0.005
    sys.stdout.write("=> ✅ 중립 정지 정상(크리프 없음) — 주행 안전\n" if ok else "=> ❌ 중립에서도 값 있음 — 데드존 더 키우거나 캘리브 필요\n")
sys.stdout.flush()
PY
echo END
