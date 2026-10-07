#!/bin/bash
# 10-07 §8.3: 상자 시험 녹화 시작|끝 — 카메라 점군 포함(오프라인 A/B: 옛 구성 vs STVL 을 같은 입력으로 다시 계산하려고)
source /opt/ros/humble/setup.bash; export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
if [ "$1" = start ]; then rm -rf /tmp/bag_box1 /tmp/box_step.csv
  setsid nohup ros2 bag record -o /tmp/bag_box1 /camera/depth/points_filtered /scan /tf /tf_static /global_costmap/costmap /local_costmap/costmap /odometry/filtered /cmd_vel /nvblox_node/static_map_slice /map_nav > /tmp/bag_box1.log 2>&1 < /dev/null &
  sleep 4; echo "녹화 $(pgrep -fc 'bag record -o /tmp/bag_box1')"
else pkill -INT -f "bag record -o /tmp/bag_box1"; sleep 4; du -sh /tmp/bag_box1; tar czf /tmp/bag_box1.tgz -C /tmp bag_box1 && ls -la /tmp/bag_box1.tgz; fi
