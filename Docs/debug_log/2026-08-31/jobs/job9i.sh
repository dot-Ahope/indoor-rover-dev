#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f joy_linux 2>/dev/null; pkill -f joy_node 2>/dev/null; sleep 1
setsid nohup ros2 run joy_linux joy_linux_node --ros-args -p dev:=/dev/input/js0 -p deadzone:=0.05 -p autorepeat_rate:=20.0 > /tmp/joy.log 2>&1 &
sleep 3
grep -a "Opened" /tmp/joy.log | tail -1
echo "======= 지금부터 12초! 좌스틱 상하→좌우, 버튼들 눌러주세요 ======="
python3 - << 'PY'
import time, rclpy, sys
from rclpy.node import Node
from sensor_msgs.msg import Joy
class A(Node):
    def __init__(s):
        super().__init__('j'); s.amin=None; s.amax=None; s.btn=set(); s.cnt=0; s.na=0; s.nb=0
        s.create_subscription(Joy,'/joy',s.cb,10)
    def cb(s,m):
        s.cnt+=1
        if s.amin is None: s.amin=list(m.axes); s.amax=list(m.axes); s.na=len(m.axes); s.nb=len(m.buttons)
        for i,v in enumerate(m.axes): s.amin[i]=min(s.amin[i],v); s.amax[i]=max(s.amax[i],v)
        for i,b in enumerate(m.buttons):
            if b: s.btn.add(i)
rclpy.init(); n=A(); e=time.time()+12
while time.time()<e: rclpy.spin_once(n,timeout_sec=0.05)
out=[f"수신 {n.cnt}개, 축{n.na}·버튼{n.nb}"]
mv=[]
for i in range(n.na):
    rng=n.amax[i]-n.amin[i]
    if rng>0.2: mv.append(i)
    out.append(f"  axis[{i}]: {n.amin[i]:+.2f}..{n.amax[i]:+.2f} 폭{rng:.2f}{' ←움직임' if rng>0.2 else ''}")
out.append(f"눌린 버튼: {sorted(n.btn) if n.btn else '없음'}")
out.append(f"=> {'✅ 정상 (움직인 축 '+str(mv)+', 버튼 '+str(sorted(n.btn))+')' if (mv or n.btn) else '❌ 여전히 0'}")
sys.stdout.write("\n".join(out)+"\n"); sys.stdout.flush()
PY
echo END
