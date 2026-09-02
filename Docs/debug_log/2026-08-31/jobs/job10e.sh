#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; sleep 2
echo "===직전 teleop 로그 마지막==="; tail -3 /tmp/teleop.log 2>/dev/null | cut -c1-100
setsid nohup ros2 run joy_linux joy_linux_node --ros-args --params-file ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/joy_teleop.yaml -r __node:=joy_node > /tmp/joy.log 2>&1 &
sleep 3
echo "===★ 스틱 완전히 놓고 6초 — 제어축 정밀 측정==="
python3 - << 'PY'
import time, rclpy, statistics as st, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s): super().__init__('a'); s.a1=[]; s.a2=[]; s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m):
        if len(m.axes)>2: s.a1.append(m.axes[1]); s.a2.append(m.axes[2])
rclpy.init(); n=A(); e=time.time()+6
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
if n.a1:
    sys.stdout.write(f"axis1(전후): 평균 {st.mean(n.a1):+.3f}, 범위 {min(n.a1):+.3f}~{max(n.a1):+.3f}\n")
    sys.stdout.write(f"axis2(좌우): 평균 {st.mean(n.a2):+.3f}, 범위 {min(n.a2):+.3f}~{max(n.a2):+.3f}\n")
    dz=0.25
    def eff(v): return 0.0 if abs(v)<dz else v
    m1=max(abs(eff(x)) for x in n.a1); m2=max(abs(eff(x)) for x in n.a2)
    sys.stdout.write(f"데드존 {dz} 적용 후 최대: axis1 {m1:.3f}, axis2 {m2:.3f} → {'✅ 중립 0' if m1==0 and m2==0 else '⚠ 데드존 넘는 오프셋 있음'}\n")
    # 필요한 데드존
    need=max(max(abs(x) for x in n.a1), max(abs(x) for x in n.a2))
    sys.stdout.write(f"관측 최대 오프셋 {need:.3f} → 안전 데드존 권장 {min(0.4, round(need+0.1,2))}\n")
sys.stdout.flush()
PY
pkill -9 -f joy_linux 2>/dev/null
echo END
