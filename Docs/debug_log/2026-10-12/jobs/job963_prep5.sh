#!/bin/bash
# 10-12 §4: PreferForward 5 로 임시 되돌려 prep(B 구성) + 지도 서버·전역 지도·실행 값 확인. 로버 안 움직임
Y=/home/jetson/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
W=${W:-5.0}
sed -i "s/\(PreferForwardCritic: {enabled: true, cost_power: 1, cost_weight: \)[0-9.]*/\1$W/" $Y
echo "  설치본 PreferForward: $(grep -a 'PreferForwardCritic: {' $Y | grep -o 'cost_weight: [0-9.]*')"
bash /tmp/job934_prep.sh 2>&1 | grep -aE "wheel_odom|map->odom|배터리|전역 plugins|RateController|visualize|nvblox 프레임|ekf_node |controller_server "
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
sleep 15
for n in controller_server planner_server bt_navigator nav_map_server; do for i in 1 2 3; do r=$(timeout 15 ros2 lifecycle get /$n 2>&1 | tail -1); echo "$r" | grep -q "\[" && break; done; echo "  $n: $r"; done
python3 /tmp/job956_gcmchk.py
for i in 1 2 3; do r=$(timeout 15 ros2 param get /controller_server FollowPathMPPI.PreferForwardCritic.cost_weight 2>&1 | tail -1); echo "$r" | grep -q value && break; done; echo "  실행 중 PreferForward: $r"
echo "  navmap_ensure: $(grep -a 'navmap_ensure\]' /tmp/nav2.log | tail -1 | cut -c1-120) · no map 경고 $(grep -ac 'no map received' /tmp/nav2.log)"
echo "  map→base: $(timeout 10 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a -m1 Translation) · 잔류 러너 $(pgrep -fc 'job551_f0drive') · /tf Hz $(timeout 8 ros2 topic hz /tf 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
