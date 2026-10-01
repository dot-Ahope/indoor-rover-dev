#!/bin/bash
# 10-01 §8.24: BT(재계획 = 목표 변경·주행 실패 때만)·전역 nvblox 층 제거 배포 → Nav2 만 재시작(위치 추정 유지)
cp /tmp/f14/nav_to_pose_no_spin.xml ~/ros2_ws/src/rover_navigation/config/ && cp /tmp/f14/navigation.launch.py ~/ros2_ws/src/rover_navigation/launch/ && cd ~/ros2_ws && colcon build --packages-select rover_navigation 2>&1 | tail -1
grep -o "RateController hz=\"[0-9.]*\"" ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml
bash /tmp/job760_nav2_restart.sh
echo "  전역 plugins: $(timeout 10 ros2 param get /global_costmap/global_costmap plugins 2>&1 | tail -1) | 로컬: $(timeout 10 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1)"
