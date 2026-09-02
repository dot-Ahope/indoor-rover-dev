#!/bin/bash
# teleop 정지 + 맵 저장 + 통계/PNG + 주행 궤적 정보
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===teleop 정지(안전)==="
pkill -9 -f teleop 2>/dev/null; pkill -9 -f joy_linux 2>/dev/null; sleep 1
timeout 2 ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1
echo "  teleop/joy 종료, 정지 발행"
echo "===현재 로버 위치(주행 후)==="; timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.position 2>/dev/null | grep -E "x:|y:" | head -2
echo "===맵 저장==="
mkdir -p ~/ros2_ws/maps
timeout 20 ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/maps/rover_map_drive --ros-args -p save_map_timeout:=10.0 2>&1 | grep -aiE "map saved|error" | tail -2
ls -la ~/ros2_ws/maps/rover_map_drive.* 2>/dev/null
echo "===통계 + PNG==="
python3 - << 'PY'
import numpy as np, time, rclpy, math
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Odometry
from rclpy.qos import QoSProfile, DurabilityPolicy
class A(Node):
    def __init__(s):
        super().__init__('a'); s.g=None; s.p=None
        q=QoSProfile(depth=1); q.durability=DurabilityPolicy.TRANSIENT_LOCAL
        s.create_subscription(OccupancyGrid,'/map',s.mcb,q)
        s.create_subscription(Odometry,'/odometry/filtered',s.ocb,10)
    def mcb(s,m): s.g=m
    def ocb(s,m): s.p=m.pose.pose
rclpy.init(); n=A(); t=time.time()
while (n.g is None) and time.time()<t+5: rclpy.spin_once(n,timeout_sec=0.2)
if n.g is None: print("NO_MAP"); raise SystemExit
g=n.g; W,H=g.info.width,g.info.height; res=g.info.resolution
d=np.array(g.data,dtype=np.int16).reshape(H,W)
occ=(d>=65).sum(); free=((d>=0)&(d<25)).sum()
print(f"맵: {W}x{H} @{res*100:.0f}cm = {W*res:.1f}x{H*res:.1f}m, 벽 {occ}셀, 자유 {free}셀")
# 탐사 면적(자유공간)
print(f"탐사한 자유공간 ≈ {free*res*res:.1f} m^2")
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    img=np.where(d<0,127,np.where(d>=65,0,255)).astype(np.uint8)
    plt.figure(figsize=(9,9)); plt.imshow(img,origin='lower',cmap='gray',vmin=0,vmax=255)
    plt.title(f"rover SLAM map (joystick drive) {W}x{H} @{res*100:.0f}cm"); plt.tight_layout()
    plt.savefig("/tmp/rover_map_drive.png",dpi=115); print("PNG /tmp/rover_map_drive.png")
except Exception as e: print("PNG fail:",e)
PY
echo END
