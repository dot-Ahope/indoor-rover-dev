#!/bin/bash
# 10-12 §3.2: 전역 정적 층이 지도를 못 받음(no map received) → Nav2 만 재시작(B 구성 인자 그대로) + 전역 코스트맵에 지도가 들어왔는지 확인. 로버 안 움직임
export NAV_EXTRA="global_camera:=nvblox replan_hz:=0.5 mppi_viz:=true"
bash /tmp/job760_nav2_restart.sh
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
sleep 25
echo "  'no map received' 경고(재시작 뒤 누적): $(grep -ac 'no map received' /tmp/nav2.log)"
for i in 1 2 3; do r=$(timeout 10 ros2 lifecycle get /nav_map_server 2>&1 | tail -1); echo "$r" | grep -q '\[' && break; done; echo "  nav_map_server: $r · /map_nav 발행자 $(timeout 8 ros2 topic info /map_nav 2>&1 | grep -a 'Publisher count')"
python3 /tmp/job956_gcmchk.py
for k in "FollowPathMPPI.PreferForwardCritic.cost_weight" "FollowPathMPPI.visualize"; do for i in 1 2 3; do r=$(timeout 15 ros2 param get /controller_server $k 2>&1 | tail -1); echo "$r" | grep -q value && break; done; echo "  $k: $r"; done
for i in 1 2 3; do r=$(timeout 15 ros2 param get /global_costmap/global_costmap nvblox_layer.nav2_costmap_global_frame 2>&1 | tail -1); echo "$r" | grep -q value && break; done; echo "  전역 nvblox 프레임: $r · BT $(grep -o 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml)"
