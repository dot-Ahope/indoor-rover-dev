#!/bin/bash
# N2~N3 1단계 (2026-09-21): 호스트 ros2_ws 에 nvblox_msgs + nvblox_nav2(+ isaac_ros_common cmake 패키지) 만 소스 빌드 — CUDA 불필요. 호스트 Nav2 가 nvblox 코스트맵 층을 로드하기 위함.
#   되돌리기: rm ~/ros2_ws/src/{isaac_ros_common,nvblox_msgs,nvblox_nav2} (심볼릭) + rm -rf ~/ros2_ws/{build,install}/{isaac_ros_common,nvblox_msgs,nvblox_nav2}
set +u
source /opt/ros/humble/setup.bash
cd ~/workspaces/isaac_ros-dev/src
[ -d isaac_ros_nvblox ] || git clone -q --depth 1 -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox.git isaac_ros_nvblox
echo "isaac_ros_nvblox: $(git -C isaac_ros_nvblox log -1 --format='%h %cs' ) | 패키지: $(ls isaac_ros_nvblox | tr '\n' ' ')"
echo "의존 확인: tf2_eigen $(dpkg -l | grep -c 'ros-humble-tf2-eigen ') nav2_costmap_2d $(dpkg -l | grep -c 'ros-humble-nav2-costmap-2d ') pluginlib $(dpkg -l | grep -c 'ros-humble-pluginlib ')"
cd ~/ros2_ws/src
ln -sfn ~/workspaces/isaac_ros-dev/src/isaac_ros_common/isaac_ros_common isaac_ros_common
ln -sfn ~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_msgs nvblox_msgs
ln -sfn ~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_nav2 nvblox_nav2
ls -la ~/ros2_ws/src | grep -E "isaac|nvblox" | awk '{print "  "$9" -> "$11}'
cd ~/ros2_ws
T0=$(date +%s); colcon build --symlink-install --packages-select isaac_ros_common nvblox_msgs nvblox_nav2 --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | grep -aE "Starting|Finished|Failed|error|Error|Summary" | tail -12 | cut -c1-160; echo "빌드 소요 $(( $(date +%s) - T0 )) s"
source ~/ros2_ws/install/setup.bash
echo "pkg: $(ros2 pkg list 2>/dev/null | grep -E 'nvblox|isaac_ros_common' | tr '\n' ' ')"
echo "플러그인 등록: $(ros2 pkg xml nvblox_nav2 2>/dev/null | grep -c costmap) | .so: $(ls ~/ros2_ws/install/nvblox_nav2/lib/*.so 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"
echo "msg: $(ros2 interface list 2>/dev/null | grep -c nvblox_msgs) 개 | DistanceMapSlice: $(ros2 interface show nvblox_msgs/msg/DistanceMapSlice 2>/dev/null | grep -c .) 줄"
echo "기존 패키지 무손상: $(ls ~/ros2_ws/install | tr '\n' ' ')"
