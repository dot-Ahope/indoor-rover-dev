#!/bin/bash
# §21 transform_timeout 1.5 반영 prep(f2tf1 과 같은 구성) + SLAM 파라미터 확인. 로버 안 움직임
bash /tmp/prep_smac_1027.sh
source /opt/ros/humble/setup.bash
echo "slam_toolbox transform_timeout = $(timeout 10 ros2 param get /slam_toolbox transform_timeout 2>&1 | tail -1) · mode = $(timeout 10 ros2 param get /slam_toolbox mode 2>&1 | tail -1)"
echo "nvblox 층 라이브러리 $(stat -c '%y' $(readlink -f ~/ros2_ws/install/nvblox_nav2/lib/libnvblox_nav2.so) | cut -c1-19)"
