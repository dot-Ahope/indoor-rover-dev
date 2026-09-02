#!/bin/bash
# 조이스틱 주행 v4: "중립 안정 대기"(스틱 움직이다 놓으면 자동 감지) → teleop → cmd_vel 게이트
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
CFG=~/ros2_ws/install/rover_bringup/share/rover_bringup/config/joy_teleop.yaml
njoy(){ ros2 node list 2>/dev/null | grep -c '^/joy_node$'; }
echo "===[1] 스테일 제거==="
for i in 1 2 3 4 5; do pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; sleep 1; [ "$(pgrep -f 'teleop_node|joy_linux_node'|wc -l)" = "0" ] && break; done
sleep 2
echo "===[2] joy_linux 단일 기동==="
setsid nohup ros2 run joy_linux joy_linux_node --ros-args --params-file $CFG -r __node:=joy_node > /tmp/joy.log 2>&1 &
sleep 4; echo "  joy_node: $(njoy)개"
[ "$(njoy)" != "1" ] && { echo "  중단(joy 비정상)"; pkill -9 -f joy_linux; exit 1; }
echo "===[3] ★ 스틱을 중립으로 놓아주세요 — 안정되면 자동진행(최대 25초 대기)==="
WAIT=$(python3 - << 'PY'
import time, rclpy, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s): super().__init__('a'); s.a1=0;s.a2=0;s.n=0; s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m):
        s.n+=1
        if len(m.axes)>2: s.a1=m.axes[1]; s.a2=m.axes[2]
rclpy.init(); n=A()
deadline=time.time()+25; stable_since=None; ok=False
while time.time()<deadline:
    rclpy.spin_once(n,timeout_sec=0.05)
    if n.n>0 and abs(n.a1)<0.15 and abs(n.a2)<0.15:
        if stable_since is None: stable_since=time.time()
        elif time.time()-stable_since>2.0: ok=True; break  # 2초 연속 중립
    else:
        stable_since=None
print("OK" if ok else f"TIMEOUT a1={n.a1:.2f} a2={n.a2:.2f}")
rclpy.shutdown()
PY
)
echo "  $WAIT"
[ "$WAIT" != "OK" ] && { echo "  ⚠ 중립 안정 실패 — 중단. 스틱 놓고 재실행."; pkill -9 -f joy_linux; exit 1; }
echo "===[4] teleop 기동==="
setsid nohup ros2 run teleop_twist_joy teleop_node --ros-args --params-file $CFG > /tmp/teleop.log 2>&1 &
sleep 3
echo "===[5] ★ 중립 유지 — cmd_vel=0 게이트(3초)==="
GATE=$(python3 - << 'PY'
import time, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
class A(Node):
    def __init__(s): super().__init__('c'); s.mx=0.0; s.create_subscription(Twist,'/cmd_vel',s.cb,10)
    def cb(s,m): s.mx=max(s.mx,abs(m.linear.x),abs(m.angular.z))
rclpy.init(); n=A(); e=time.time()+3
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
print("OK" if n.mx<0.005 else f"BAD:{n.mx:.3f}")
rclpy.shutdown()
PY
)
[ "$GATE" != "OK" ] && { echo "  ❌ cmd_vel≠0($GATE) — 강제종료·중단."; pkill -9 -f teleop; pkill -9 -f joy_linux; exit 1; }
echo "  ✅✅ 주행 시작 가능! 스틱으로 조종하세요 (놓으면 정지)."
