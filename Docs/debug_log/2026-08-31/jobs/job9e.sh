#!/bin/bash
# joy_linux 설치 + joy_linux_node로 /dev/input/js0 읽기 → /joy 12초 캡처
echo '<PW>' | sudo -S -p '' apt-get install -y ros-humble-joy-linux 2>&1 | tail -2
echo '<PW>' | sudo -S -p '' usermod -aG input jetson 2>/dev/null && echo "jetson→input 그룹 추가(다음 로그인부터, 지금은 others r로 접근)"
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f joy_node 2>/dev/null; pkill -f joy_linux 2>/dev/null; sleep 1
setsid nohup ros2 run joy_linux joy_linux_node --ros-args -p dev:=/dev/input/js0 -p deadzone:=0.05 -p autorepeat_rate:=20.0 > /tmp/joy.log 2>&1 &
sleep 4
echo "===joy_linux_node 상태==="; pgrep -f joy_linux >/dev/null && echo "실행중" || echo "실패"
grep -aiE "opened|joystick|error|fail" /tmp/joy.log | tail -3
echo -n "  /joy hz: "; timeout 4 ros2 topic hz /joy 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1
echo "=== 지금부터 12초간 스틱·버튼 조작해주세요 ==="
python3 - << 'PY'
import time, rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s):
        super().__init__('j'); s.amin=[]; s.amax=[]; s.btn=set(); s.cnt=0; s.na=0; s.nb=0
        s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m):
        s.cnt+=1
        if not s.amin: s.amin=list(m.axes); s.amax=list(m.axes); s.na=len(m.axes); s.nb=len(m.buttons)
        for i,v in enumerate(m.axes): s.amin[i]=min(s.amin[i],v); s.amax[i]=max(s.amax[i],v)
        for i,b in enumerate(m.buttons):
            if b: s.btn.add(i)
rclpy.init(); n=A(); e=time.time()+12
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
print(f"수신 {n.cnt}, 축 {n.na}, 버튼 {n.nb}")
for i in range(n.na):
    rng=n.amax[i]-n.amin[i]
    print(f"  axis[{i}]: {n.amin[i]:+.2f}..{n.amax[i]:+.2f} 폭{rng:.2f}{' ←움직임' if rng>0.1 else ''}")
print(f"눌린 버튼: {sorted(n.btn) if n.btn else '없음'}")
print("=> 축 움직임+버튼 감지 = 입력 정상" if n.cnt else "!! 여전히 무입력")
n.destroy_node(); rclpy.shutdown()
PY
