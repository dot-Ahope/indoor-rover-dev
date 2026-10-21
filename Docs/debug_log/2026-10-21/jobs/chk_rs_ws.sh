#!/bin/bash
# 왜 colcon 이 realsense_splitter 를 못 찾나 · nvblox_ros/cuVSLAM 은 어디 설치돼 있나
W=~/workspaces/isaac_ros-dev
find $W/src -maxdepth 4 -name COLCON_IGNORE | head; echo "--- splitter package.xml"; ls $W/src/isaac_ros_nvblox/nvblox_examples/realsense_splitter/
echo "--- ws 최상위"; ls $W; ls $W/install 2>/dev/null | grep -E "nvblox|visual_slam|splitter" | head
docker exec -u admin isaac_rs_test bash -c 'cd /workspaces/isaac_ros-dev; ls src/isaac_ros_nvblox/nvblox_examples/realsense_splitter >/dev/null && echo 컨테이너에서도 보임; ls /opt/ros/humble/share | grep -E "nvblox|visual_slam" | head; source /opt/ros/humble/setup.bash; colcon list --base-paths src 2>/dev/null | grep -E "splitter|nvblox_ros|visual_slam" ; colcon list --base-paths src/isaac_ros_nvblox/nvblox_examples 2>&1 | head'
