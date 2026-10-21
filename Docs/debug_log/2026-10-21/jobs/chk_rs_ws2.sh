#!/bin/bash
# 옛 컨테이너의 nvblox/cuVSLAM 출처(apt?) · 새 이미지에 있나 · 분리 노드 의존성
W=~/workspaces/isaac_ros-dev
grep -E "<(build_)?depend>|<exec_depend>" $W/src/isaac_ros_nvblox/nvblox_examples/realsense_splitter/package.xml
echo "--- 옛 컨테이너 dpkg"; docker exec isaac_ros_dev-aarch64-container bash -c "dpkg -l | awk '/nvblox|visual-slam|isaac-ros-nitros |realsense/ {print \$2, \$3}'" | head -20
echo "--- 새 이미지 dpkg"; docker exec isaac_rs_test bash -c "dpkg -l | awk '/nvblox|visual-slam|isaac-ros-nitros |realsense/ {print \$2, \$3}'" | head -20
echo "--- 옛 컨테이너 diff(apt 로 들어온 것인지)"; docker diff isaac_ros_dev-aarch64-container 2>/dev/null | grep -E "share/(nvblox_ros|isaac_ros_visual_slam)$" | head
docker inspect isaac_ros_dev-aarch64-container -f '{{.Config.Image}} {{.Image}}'; docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}' | head
ls $W/vslam | head
