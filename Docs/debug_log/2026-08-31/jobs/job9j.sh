#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pgrep -f joy_linux >/dev/null || { setsid nohup ros2 run joy_linux joy_linux_node --ros-args -p dev:=/dev/input/js0 -p deadzone:=0.05 -p autorepeat_rate:=20.0 > /tmp/joy.log 2>&1 & sleep 3; }
echo "======= 지금부터 10초! 데드맨으로 쓸 버튼을 눌러주세요 (여러개 눌러도 됨) ======="
python3 - << 'PY'
import time, rclpy, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s):
        super().__init__('j'); s.first=None; s.pressed={}
        s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m):
        for i,b in enumerate(m.buttons):
            if b:
                if i not in s.pressed: s.pressed[i]=0
                s.pressed[i]+=1
rclpy.init(); n=A(); e=time.time()+10
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
if n.pressed:
    sys.stdout.write(f"눌린 버튼(번호:횟수): {dict(sorted(n.pressed.items()))}\n")
    sys.stdout.write(f"=> 가장 많이 눌린 버튼 = {max(n.pressed,key=n.pressed.get)}번 (데드맨 후보)\n")
else:
    sys.stdout.write("버튼 감지 안됨 — 다시 시도\n")
sys.stdout.flush()
PY
echo END
