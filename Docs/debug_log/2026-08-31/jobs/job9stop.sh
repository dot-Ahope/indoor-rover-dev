#!/bin/bash
# 안전 정지: 모든 teleop/joy 종료 → /cmd_vel 중단 → watchdog 정지. 원인 진단.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===teleop/joy 전체 종료==="
pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; pkill -9 -f joy_node 2>/dev/null; sleep 2
echo "잔존: teleop $(pgrep -f teleop | wc -l), joy $(pgrep -f 'joy_linux|joy_node' | wc -l)"
echo "===정지 지령 명시 발행(안전)==="
timeout 3 ros2 topic pub -t 10 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1 && echo "정지 발행"
echo "===현재 로버 실제 속도(정지 확인)==="
timeout 5 ros2 topic echo /odometry/filtered --once --field twist.twist 2>/dev/null | grep -A1 -E "linear:|angular:" | grep -E "x:|z:" | head -2
echo "===원인 진단: 스틱 중립 시 axis1 실제값(오프셋/드리프트?)==="
setsid nohup ros2 run joy_linux joy_linux_node --ros-args -p dev:=/dev/input/js0 -p deadzone:=0.12 -p autorepeat_rate:=20.0 > /tmp/joy.log 2>&1 &
sleep 3
echo "  ★ 스틱에서 손 떼고 3초 기다려주세요 (중립값 측정)"
python3 - << 'PY'
import time, rclpy, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s): super().__init__('a'); s.a=None; s.n=0; s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m): s.n+=1; s.a=list(m.axes)
rclpy.init(); n=A(); e=time.time()+4
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
if n.a: sys.stdout.write(f"  중립 시 축값: {[round(v,3) for v in n.a]}\n  → axis1={n.a[1]:+.3f} axis2={n.a[2]:+.3f} (0 근처여야 정상. 크면 스틱 오프셋/미조작)\n")
else: sys.stdout.write("  /joy 무수신\n")
sys.stdout.flush()
PY
pkill -9 -f joy_linux 2>/dev/null
echo END
