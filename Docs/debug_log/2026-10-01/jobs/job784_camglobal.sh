#!/bin/bash
# 10-01 §8.35: 전역 obstacle_layer 에 카메라 점군 소스 추가 배포 → Nav2 만 재시작(위치 추정 유지, NAV_ARGS 저장 지도 유지) → 상자 표시 확인
cp /tmp/f14/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/ && cd ~/ros2_ws && colcon build --packages-select rover_navigation 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
sed -i 's#navigation.launch.py stuck_shadow:=true >#navigation.launch.py stuck_shadow:=true nav_map:=/home/jetson/maps/office/office_v2.yaml >#' /tmp/job760_nav2_restart.sh
grep -c "nav_map:=" /tmp/job760_nav2_restart.sh
bash /tmp/job760_nav2_restart.sh
echo "  전역 obstacle 소스: $(timeout 15 ros2 param get /global_costmap/global_costmap obstacle_layer.observation_sources 2>&1 | tail -1) | static map_topic: $(timeout 15 ros2 param get /global_costmap/global_costmap static_layer.map_topic 2>&1 | tail -1)"
echo "  점군 /camera/depth/points_filtered: $(timeout 8 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
sleep 5
python3 - <<'PY'
import rclpy, numpy as np, time
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node('box_chk'); G = {}
q = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
for tp in ('/global_costmap/costmap', '/local_costmap/costmap'):
    n.create_subscription(OccupancyGrid, tp, lambda m, tp=tp: G.__setitem__(tp, m), q if 'global' in tp else 5)
t0 = time.time()
while time.time() - t0 < 8 and len(G) < 2: rclpy.spin_once(n, timeout_sec=0.2)
for tp, m in G.items():
    g = np.array(m.data).reshape(m.info.height, m.info.width); r = m.info.resolution
    def c(x, y):
        i, j = int((y - m.info.origin.position.y) / r), int((x - m.info.origin.position.x) / r)
        return g[i, j] if 0 <= i < g.shape[0] and 0 <= j < g.shape[1] else None
    box = [c(x, y) for x in (1.15, 1.2, 1.25) for y in (0.0, -0.09, -0.17)]
    print('  %s 상자 자리(1.15~1.25, 0~−0.17) 비용: %s' % (tp, box))
PY
