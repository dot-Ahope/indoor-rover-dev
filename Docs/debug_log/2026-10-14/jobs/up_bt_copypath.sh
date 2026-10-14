#!/bin/bash
# (10-14 §14) CopyPath BT 노드 배포: 저장소 파일 4 개를 Jetson 소스에 두고 rover_navigation 만 빌드 — 로버 안 움직임(실행 중 스택은 다음 prep 때 새 노드를 읽음)
R=~/ros2_ws/src/rover_navigation; set -e
cp /tmp/up_copy_path_action.cpp $R/src/copy_path_action.cpp; cp /tmp/up_CMakeLists.txt $R/CMakeLists.txt; cp /tmp/up_nav2_params.yaml $R/config/nav2_params.yaml; cp /tmp/up_bt.xml $R/config/nav_to_pose_no_spin.xml
grep -c "rover_copy_path_bt_node" $R/CMakeLists.txt $R/config/nav2_params.yaml; grep -c "<CopyPath" $R/config/nav_to_pose_no_spin.xml
source /opt/ros/humble/setup.bash; cd ~/ros2_ws
ls -la install/rover_navigation/share/rover_navigation/config/nav2_params.yaml | cut -c1-140
colcon build --symlink-install --packages-select rover_navigation 2>&1 | tail -6
ls -la install/rover_navigation/lib/librover_copy_path_bt_node.so && nm -D install/rover_navigation/lib/librover_copy_path_bt_node.so | grep -c BT_RegisterNodesFromPlugin
