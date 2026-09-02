#!/bin/bash
# joy_node 기동 + /joy 12초 캡처 (사용자가 스틱·버튼 조작) → 축/버튼 활동 확인
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f joy_node 2>/dev/null; sleep 1
setsid nohup ros2 run joy joy_node --ros-args -p device_id:=0 -p deadzone:=0.05 -p autorepeat_rate:=20.0 > /tmp/joy.log 2>&1 &
sleep 4
echo "===joy_node 상태==="; pgrep -f joy_node >/dev/null && echo "실행중" || echo "기동 실패"; grep -aiE "opened|error|fail" /tmp/joy.log | tail -2
echo -n "  /joy hz: "; timeout 4 ros2 topic hz /joy 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1
echo "=== 지금부터 12초간 스틱을 모두 움직이고 버튼을 눌러주세요 ==="
python3 - << 'PY'
import time, rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s):
        super().__init__('j'); s.na=0; s.nb=0; s.amin=[]; s.amax=[]; s.btn=set(); s.cnt=0
        s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m):
        s.cnt+=1
        if not s.amin: s.amin=list(m.axes); s.amax=list(m.axes); s.na=len(m.axes); s.nb=len(m.buttons)
        for i,v in enumerate(m.axes):
            s.amin[i]=min(s.amin[i],v); s.amax[i]=max(s.amax[i],v)
        for i,b in enumerate(m.buttons):
            if b: s.btn.add(i)
rclpy.init(); n=A(); e=time.time()+12
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
print(f"수신 메시지: {n.cnt}, 축 {n.na}개, 버튼 {n.nb}개")
if n.cnt:
    print("축별 변화폭 (min..max, |폭|>0.1이면 움직임 감지):")
    for i in range(n.na):
        rng=n.amax[i]-n.amin[i]; mk=" ← 움직임" if rng>0.1 else ""
        print(f"  axis[{i}]: {n.amin[i]:+.2f}..{n.amax[i]:+.2f} (폭 {rng:.2f}){mk}")
    print(f"눌린 버튼: {sorted(n.btn) if n.btn else '없음'}")
    print("=> 축 움직임+버튼 감지되면 조이스틱 입력 정상")
else:
    print("!! /joy 메시지 없음 — joy_node/장치 점검 필요")
n.destroy_node(); rclpy.shutdown()
PY
