#!/bin/bash
# (10-13 §12) 실행 중 MPPI CostCritic 값 확인 — 로버 안 움직임
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
timeout 20 ros2 param list /controller_server 2>/dev/null | grep -i "CostCritic\|critics" | head -12
for p in $(timeout 20 ros2 param list /controller_server 2>/dev/null | grep -i "CostCritic.cost_weight\|\.critics$"); do echo "$p = $(timeout 15 ros2 param get /controller_server $p 2>&1 | tail -1 | cut -c1-200)"; done
