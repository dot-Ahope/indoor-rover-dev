#!/bin/bash
# 10-08 §3.3: nvblox_nav2 층의 프레임 파라미터 기본값·사용처(읽기만)
f=$(grep -rl "nav2_costmap_global_frame" ~/ros2_ws/src 2>/dev/null | head -3); echo "$f"
for x in $f; do grep -n "nav2_costmap_global_frame\|lookupTransform\|global_frame_" $x | head -12; done
echo "== 실행 중 값"; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for n in global_costmap/global_costmap local_costmap/local_costmap; do echo "$n: $(timeout 10 ros2 param get /$n nvblox_layer.nav2_costmap_global_frame 2>&1 | tail -1)"; done
