#!/bin/bash
# 무동작 헬스체크: 노드·토픽 라이브 + 배터리 + 새 위치 사방여유(회전공간 확인).
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===== 노드 ====="
ros2 node list 2>/dev/null | grep -E 'rover_jupiter|ekf|scan_deskew|camera|rplidar' | tr '\n' ' '; echo
echo "===== 토픽 발행률 ====="
for t in /wheel_odom /odometry/filtered /scan; do
  echo -n "  $t: "; timeout 4 ros2 topic hz $t 2>&1 | grep -aE "average rate" | head -1 || echo "무발행!"
done
echo "===== 배터리 ====="
timeout 4 ros2 topic echo /battery --once 2>/dev/null | grep -aE "voltage|percentage" | head -2 || \
timeout 4 ros2 topic echo /rover/status --once 2>/dev/null | grep -aiE "volt|batt" | head -2 || echo "  (배터리 토픽 없음)"
echo "===== 사방 여유 (로버 프레임, 풋프린트 모서리 기준) ====="
python3 - << 'PY'
import math, numpy as np, rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
class S(Node):
    def __init__(s):
        super().__init__('hc'); s.m=None
        s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,m): s.m=m
rclpy.init(); n=S(); t0=time.time()
while n.m is None and time.time()<t0+5: rclpy.spin_once(n,timeout_sec=0.1)
if n.m is None: print("  NO /scan"); raise SystemExit
m=n.m; r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
ok=np.isfinite(r)&(r>0.05)&(r<12); r=r[ok]; a=a[ok]
th=a+LYAW; px=LX+r*np.cos(th); py=r*np.sin(th)
dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
c=np.sqrt(dx*dx+dy*dy); ang=np.degrees(np.arctan2(py,px))
def sec(lo,hi,wrap=False):
    mk=((ang>=lo)|(ang<hi)) if wrap else ((ang>=lo)&(ang<hi))
    return float(np.min(c[mk]))*100 if mk.any() else None
F=sec(-45,45); L=sec(45,135); B=sec(135,-135,True); R=sec(-135,-45)
def f(v): return f"{v:.0f}cm" if v is not None else "-"
mn=float(np.min(c))*100
print(f"  앞{f(F)} | 뒤{f(B)} | 좌{f(L)} | 우{f(R)}  (최소 {mn:.0f}cm)")
need=15
gates=[('앞',F),('뒤',B),('좌',L),('우',R)]
bad=[nm for nm,v in gates if v is not None and v<need]
print(f"  회전판정(각방향≥{need}cm): {'✅ 충분' if not bad else '❌ 부족: '+','.join(bad)}")
PY
