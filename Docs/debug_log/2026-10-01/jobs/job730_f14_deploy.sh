#!/bin/bash
# 10-01 §7 F1-4 준비: 위치 추정 후보 코드 배포·빌드 → 정지 상태에서 후보별 기동 확인(로버 출발 테이프, 움직이지 않음)
#   F1-4a(선언): 각 후보가 기동해 map→odom 을 내고, 시작 자세가 원점에서 ≤ 5 cm·5 s 안 안정.
set +u
W=~/ros2_ws/src
cp /tmp/f14/slam.launch.py $W/rover_bringup/launch/ && cp /tmp/f14/localization.launch.py /tmp/f14/navigation.launch.py $W/rover_navigation/launch/ && cp /tmp/f14/amcl.yaml $W/rover_navigation/config/
cd ~/ros2_ws && colcon build --packages-select rover_bringup rover_navigation 2>&1 | tail -2; source install/setup.bash
ros2 launch rover_bringup slam.launch.py --show-args 2>/dev/null | grep -aA1 slam_mode
ros2 launch rover_navigation localization.launch.py --show-args 2>/dev/null | grep -aA1 "'map'"
for L in ${LOCS:-slamloc amcl}; do
  echo; echo "################ 후보 $L ################"
  LOC=$L MAP=office_v2 MAPPING=0 bash /tmp/job726_prep_map.sh 2>&1 | grep -aE "지도|odometry/filtered|slam 인자|위치 추정|map->odom|_server|EKF 위반|프로세스|  [a-z_\" ]+ +[0-9]+$"
  python3 /tmp/job697_restore_chk.py 2>&1 | grep -av "^\[" | grep -aE "/map|^ +[1-9]\.0 s|^ +1[0-6]\.0 s|마지막"
  echo "  CPU(위치 추정 노드): $(ps -eo pcpu,comm | grep -aE 'slam_tool|amcl|map_server' | tr '\n' ' ')"
done
