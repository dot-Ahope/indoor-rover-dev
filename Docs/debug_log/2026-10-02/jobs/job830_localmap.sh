#!/bin/bash
# 10-02 §12: navigation.launch.py(local_frame 인자) 배포·빌드 → Nav2 만 재시작(local_frame:=map) → 확인
cp /tmp/f39/navigation.launch.py ~/ros2_ws/src/rover_navigation/launch/ && cd ~/ros2_ws && source /opt/ros/humble/setup.bash && colcon build --packages-select rover_navigation 2>&1 | grep -aE "Finished|Failed|rror" | head -3
source ~/ros2_ws/install/setup.bash
NAV_EXTRA="local_frame:=map" bash /tmp/job760_nav2_restart.sh 2>&1 | tail -8
echo "  local global_frame: $(timeout 15 ros2 param get /local_costmap/local_costmap global_frame 2>&1 | tail -1) · nvblox 층: $(timeout 15 ros2 param get /local_costmap/local_costmap nvblox_layer.nav2_costmap_global_frame 2>&1 | tail -1)"
echo "  /local_costmap/costmap frame: $(timeout 10 ros2 topic echo --once /local_costmap/costmap/header 2>/dev/null | grep -a frame_id)"
grep -aiE "error|exception" /tmp/nav2.log | grep -av "Message Filter" | head -5
