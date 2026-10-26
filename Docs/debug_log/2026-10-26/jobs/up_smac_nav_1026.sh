#!/bin/bash
# 10-26 §7 planner:=smac 배포(로버 안 움직임): navigation.launch.py · nav2_params.yaml · copy_path_action.cpp → ~/ros2_ws/src/rover_navigation, prep_patrol.sh → /tmp. rover_navigation 빌드.
#   실행본 = 이 머리 + 스크래치패드가 base64 로 붙인 /tmp/up_*.  실행 중 스택엔 미적용(다음 prep 부터). B0(planner 기본 navfn)는 BT · 계획기 동작 그대로.
R=~/ros2_ws/src/rover_navigation; set -e
for f in launch/navigation.launch.py config/nav2_params.yaml src/copy_path_action.cpp; do echo "이전 $f $(sha256sum < $R/$f | cut -c1-12)"; done
cp /tmp/up_navigation.launch.py $R/launch/navigation.launch.py; cp /tmp/up_nav2_params.yaml $R/config/nav2_params.yaml; cp /tmp/up_copy_path_action.cpp $R/src/copy_path_action.cpp
cp /tmp/up_prep_patrol.sh /tmp/prep_patrol.sh; chmod +x /tmp/prep_patrol.sh
for f in launch/navigation.launch.py config/nav2_params.yaml src/copy_path_action.cpp; do echo "새 $f $(sha256sum < $R/$f | cut -c1-12)"; done; echo "prep_patrol $(sha256sum < /tmp/prep_patrol.sh | cut -c1-10)"
source /opt/ros/humble/setup.bash; cd ~/ros2_ws
colcon build --symlink-install --packages-select rover_navigation 2>&1 | tail -4
for f in config/nav2_params.yaml launch/navigation.launch.py; do I=install/rover_navigation/share/rover_navigation/$f
  if [ -L "$I" ]; then echo "설치본 $f = 링크 → $(readlink $I)"; else cp $R/$f $I; echo "설치본 $f 일반 파일(prep sed 탓) → 저장소 판으로 덮음 $(sha256sum < $I | cut -c1-12)"; fi; done
grep -c 'REEDS_SHEPP' $R/config/nav2_params.yaml; strings install/rover_navigation/lib/librover_copy_path_bt_node.so | grep -c '0 보다 크면' || true
