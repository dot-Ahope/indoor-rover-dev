#!/bin/bash
# 무동작 사전점검: joy 정리 + 전압 + 방향별 여유 + 노드/TF 상태
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== joy 정리 (cmd_vel 단독화) ==="
pkill -f joy_linux; pkill -f teleop_twist_joy; sleep 1; echo "  완료"
echo "=== 배터리 ==="
timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aE "voltage" | head -1 || echo "  (배터리 토픽 없음)"
echo "=== 노드/TF ==="
echo "  노드: $(ros2 node list 2>/dev/null | grep -E 'rover_jupiter|ekf|slam|conditioner|rplidar|scan_deskew' | tr '\n' ' ')"
echo -n "  /odometry/filtered: "; timeout 4 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo -n "  map->base_link TF: "; timeout 4 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE "Translation" | head -1 || echo "없음(slam 확인필요)"
echo "=== 방향별 여유 (로버 프레임, 풋프린트 기준) ==="
python3 - << 'PY'
import math, numpy as np, rclpy, time
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
rclpy.init(); n=rclpy.create_node('pc'); m=[None]
n.create_subscription(LaserScan,'/scan',lambda x:m.__setitem__(0,x),qos_profile_sensor_data)
t0=time.time()
while m[0] is None and time.time()<t0+5: rclpy.spin_once(n,timeout_sec=0.1)
if m[0] is None: print("  NO /scan"); raise SystemExit
r=np.array(m[0].ranges,np.float32); a=m[0].angle_min+m[0].angle_increment*np.arange(len(r))
ok=np.isfinite(r)&(r>0.05)&(r<12); th=a[ok]+LYAW
px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
c=np.sqrt(dx*dx+dy*dy); ang=np.degrees(np.arctan2(py,px))
def sec(lo,hi,wrap=False):
    mk=((ang>=lo)|(ang<hi)) if wrap else ((ang>=lo)&(ang<hi))
    return float(np.min(c[mk]))*100 if mk.any() else None
F=sec(-45,45); L=sec(45,135); B=sec(135,-135,True); R=sec(-135,-45)
f=lambda v: f"{v:.0f}cm" if v is not None else "-"
print(f"  앞{f(F)} | 뒤{f(B)} | 좌{f(L)} | 우{f(R)}")
need=230
print(f"  직진2m 판정(전방>={need}cm): {'OK 주행가능' if (F or 0)>=need else 'X 전방 부족 — 더 트인 곳/방향 필요'}")
rclpy.shutdown()
PY
