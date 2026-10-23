#!/bin/bash
# 10-23 §20.2 PathBlockedAhead only_new 배포: 저장소 cpp · BT xml 을 Jetson 소스에 두고 rover_navigation 만 빌드. 로버 안 움직임(실행 중 스택은 다음 prep 때 새 노드 · xml 을 읽음)
# 실행 형태: 스크래치패드 묶음이 /tmp/up_pba.cpp · /tmp/up_bt.xml 을 base64 로 풀어 놓은 뒤 이 본문 실행(본문 = 아래)
R=~/ros2_ws/src/rover_navigation; set -e
for f in src/path_blocked_ahead_condition.cpp config/nav_to_pose_no_spin.xml; do echo "이전 $f $(sha256sum < $R/$f | cut -c1-12)"; done
cp /tmp/up_pba.cpp $R/src/path_blocked_ahead_condition.cpp; cp /tmp/up_bt.xml $R/config/nav_to_pose_no_spin.xml
for f in src/path_blocked_ahead_condition.cpp config/nav_to_pose_no_spin.xml; do echo "새 $f $(sha256sum < $R/$f | cut -c1-12)"; done
grep -c 'only_new="true"' $R/config/nav_to_pose_no_spin.xml
source /opt/ros/humble/setup.bash; cd ~/ros2_ws
colcon build --symlink-install --packages-select rover_navigation 2>&1 | tail -6
ls -la install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml | cut -c1-160
L=$(ls install/rover_navigation/lib/*path_blocked* 2>/dev/null | head -1); ls -la $L; strings $L | grep -c "only_new"
