#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "== git in ~/ros2_ws/src: $(cd ~/ros2_ws/src 2>/dev/null && git rev-parse --short HEAD 2>&1 | head -1)"
echo "== nav2_params.yaml 실체: $(readlink -f ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)"
echo "== nvpmodel: $(nvpmodel -q 2>/dev/null | tr '\n' ' ')"
echo "== 노드: $(timeout 8 ros2 node list 2>/dev/null | tr '\n' ' ')"
T0=$(date +%s.%N); timeout 20 ros2 param dump /controller_server > /tmp/pd_test.yaml 2>&1; echo "== param dump controller_server: rc $? $(wc -l < /tmp/pd_test.yaml) 줄, $(echo "$(date +%s.%N) - $T0" | bc) s"; grep -nE "critics|CostCritic|ObstaclesCritic" /tmp/pd_test.yaml | head -5
echo "== 토픽 크기 후보:"; for tp in /depth_relay/points /camera/camera/depth/color/points /local_costmap/costmap_raw; do timeout 6 ros2 topic bw $tp 2>/dev/null | grep -a "average" | head -1 | sed "s#^#  $tp: #"; done
echo "== 토픽 목록 수: $(timeout 8 ros2 topic list 2>/dev/null | wc -l)"; timeout 8 ros2 topic list 2>/dev/null | grep -aE "relay|points|costmap_raw|trajector|smooth" | tr '\n' ' '
