#!/bin/bash
# 맵 저장 + 통계 + PNG 렌더 + 현재 pose(360° 후 시작 부근 복귀 확인)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
mkdir -p ~/ros2_ws/maps
echo "===맵 저장 (map_saver_cli)==="
timeout 20 ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/maps/rover_map --ros-args -p save_map_timeout:=10.0 2>&1 | grep -aiE "map saved|error|written" | tail -3
ls -la ~/ros2_ws/maps/ 2>/dev/null | grep rover_map
echo "===통계 + PNG 렌더==="
python3 - << 'PY'
import numpy as np, time, rclpy, math
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Odometry
from rclpy.qos import QoSProfile, DurabilityPolicy
class A(Node):
    def __init__(s):
        super().__init__('a'); s.g=None; s.pose=None
        q=QoSProfile(depth=1); q.durability=DurabilityPolicy.TRANSIENT_LOCAL
        s.create_subscription(OccupancyGrid,'/map',s.mcb,q)
        s.create_subscription(Odometry,'/odometry/filtered',s.ocb,10)
    def mcb(s,m): s.g=m
    def ocb(s,m): s.pose=m.pose.pose
rclpy.init(); n=A(); t=time.time()
while (n.g is None or n.pose is None) and time.time()<t+5: rclpy.spin_once(n,timeout_sec=0.2)
if n.g is None: print("NO_MAP"); raise SystemExit
g=n.g; W,H=g.info.width,g.info.height; res=g.info.resolution
d=np.array(g.data,dtype=np.int16).reshape(H,W)
occ=(d>=65).sum(); free=((d>=0)&(d<25)).sum(); unk=(d<0).sum()
print(f"맵: {W}x{H} @ {res*100:.0f}cm = {W*res:.1f}x{H*res:.1f}m")
print(f"점유(벽) {occ}셀 / 자유 {free}셀 / 미탐사 {unk}셀 ({100*occ/(W*H):.1f}% 벽)")
if n.pose:
    p=n.pose; q=p.orientation; yaw=math.degrees(math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z)))
    print(f"360도 후 pose: x={p.position.x*100:+.1f}cm y={p.position.y*100:+.1f}cm yaw={yaw:+.0f}deg (시작=0 부근이어야 정상)")
# ASCII 미리보기 (다운샘플)
step=max(1,max(W,H)//60)
print("맵 미리보기 (#=벽 .=자유 공백=미탐사):")
for r in range(H-1,-1,-step):
    line=""
    for c in range(0,W,step):
        v=d[r,c]; line+=("#" if v>=65 else ("." if 0<=v<25 else " "))
    print("  "+line)
# PNG 렌더
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    img=np.where(d<0,127,np.where(d>=65,0,255)).astype(np.uint8)  # 미탐사 회색, 벽 검정, 자유 흰색
    plt.figure(figsize=(8,8)); plt.imshow(img,origin='lower',cmap='gray',vmin=0,vmax=255)
    plt.title(f"rover SLAM map {W}x{H} @{res*100:.0f}cm (360deg spin)"); plt.tight_layout()
    plt.savefig("/tmp/rover_map.png",dpi=110); print("PNG saved /tmp/rover_map.png")
except Exception as e: print("PNG fail:",e)
n.destroy_node(); rclpy.shutdown()
PY
