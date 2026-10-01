#!/bin/bash
# 10-01 §8.39: PathBlockedAhead BT 조건 노드 배포 — 소스·CMake·package.xml·nav2_params·BT XML 복사 → 빌드 → Nav2 만 재시작(위치 추정 유지) → 플러그인 적재 확인
S=/tmp/f39; P=~/ros2_ws/src/rover_navigation
mkdir -p $P/src && cp $S/path_blocked_ahead_condition.cpp $P/src/ && cp $S/CMakeLists.txt $S/package.xml $P/ && cp $S/nav2_params.yaml $S/nav_to_pose_no_spin.xml $P/config/
cd ~/ros2_ws && source /opt/ros/humble/setup.bash && colcon build --packages-select rover_navigation 2>&1 | grep -aE "error|warning|Finished|Failed" | head -20
ls -la ~/ros2_ws/install/rover_navigation/lib/librover_path_blocked_ahead_bt_node.so || exit 1
source ~/ros2_ws/install/setup.bash
grep -c PathBlockedAhead ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml
bash /tmp/job760_nav2_restart.sh
sleep 3
echo "== bt_navigator 상태: $(timeout 10 ros2 lifecycle get /bt_navigator 2>&1 | tail -1)"
echo "== 플러그인 목록 수: $(timeout 10 ros2 param get /bt_navigator plugin_lib_names 2>&1 | grep -o "_bt_node" | wc -l)"
grep -aiE "PathBlocked|rover_path_blocked|Error loading|failed to load|Exception" /tmp/nav2.log 2>/dev/null | head -5
ls /tmp/*.log | grep -i nav | head
