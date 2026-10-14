#!/bin/bash
# (10-14 §9) 순회 prep(viz, 벌점) 뒤 pad_relief 노드를 접속과 분리해 띄운다(mode 인자: on|shadow, 기본 on). 로버 안 움직임
pkill -f pad_relief.py 2>/dev/null; rm -f /tmp/pad_relief.log
bash /tmp/prep_patrol.sh ${1:-lite} ${2:-15.0}
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
setsid nohup python3 -u /tmp/pad_relief.py --ros-args -p mode:=${3:-on} > /tmp/pad_relief_node.log 2>&1 < /dev/null &
for i in 1 2 3 4 5 6 7 8; do sleep 1; grep -q "원래 패딩" /tmp/pad_relief.log 2>/dev/null && break; done
echo "  pad_relief: $(pgrep -fc pad_relief.py) 개 실행 · $(cut -d' ' -f2- /tmp/pad_relief.log 2>/dev/null | tr '\n' '|' | cut -c1-200)"
echo "  실행 중: 로컬 패딩 $(timeout 12 ros2 param get /local_costmap/local_costmap footprint_padding 2>&1 | tail -1 | sed 's/.*is: //') · CostCritic $(timeout 12 ros2 param get /controller_server FollowPathMPPI.CostCritic.cost_weight 2>&1 | tail -1 | sed 's/.*is: //') · 전역 감쇠 $(timeout 12 ros2 param get /global_costmap/global_costmap inflation_layer.cost_scaling_factor 2>&1 | tail -1 | sed 's/.*is: //') · nvblox 통합 $(grep -a 'static_mapper.projective_integrator_max_integration_distance_m' /tmp/nvblox_node.log | tail -1 | sed 's/.*_m: //')"
