#!/bin/bash
# Phase N0 1단계 (2026-09-21, 사용자 승인): 센서·SLAM·Nav2 내림(base 유지) → git-lfs(sudo) → ~/workspaces/isaac_ros-dev + isaac_ros_common(release-3.2) → Isaac ROS Dev 이미지 빌드(백그라운드, NGC 프리빌드 층 풀)
# 되돌리기: docker rmi isaac_ros_dev-aarch64 (+ nvcr.io/nvidia/isaac/ros:* 층), rm -rf ~/workspaces, sudo apt-get remove git-lfs, ~/.bashrc 의 ISAAC_ROS_WS 줄 삭제
set +u
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 1. 센서·SLAM·Nav2 내림 (base=에이전트·rsp 유지) ##########"
PATS="depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor realsense2_camera rplidar sensor_conditioner ekf_node scan_deskew slam_toolbox"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
echo "  남은 ros 프로세스: $(pgrep -fc 'ros2|slam_toolbox|realsense|rplidar' ) | 에이전트: $(docker ps --format '{{.Names}}' | grep -c microros_agent) | rsp: $(pgrep -fc '[r]obot_state_publisher') | load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "########## 2. git-lfs (sudo) ##########"
echo '<PW>' | sudo -S apt-get install -y git-lfs 2>&1 | tail -2; git lfs install --skip-repo 2>&1 | tail -1; echo "  git-lfs: $(git lfs version 2>/dev/null | cut -c1-30)"
echo "########## 3. 워크스페이스 ##########"
mkdir -p ~/workspaces/isaac_ros-dev/src
grep -q ISAAC_ROS_WS ~/.bashrc || echo 'export ISAAC_ROS_WS=${HOME}/workspaces/isaac_ros-dev/' >> ~/.bashrc
export ISAAC_ROS_WS=${HOME}/workspaces/isaac_ros-dev/
cd ~/workspaces/isaac_ros-dev/src
[ -d isaac_ros_common ] || git clone -q -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git isaac_ros_common
echo "  isaac_ros_common: $(git -C isaac_ros_common log -1 --format='%h %cs %s' | cut -c1-70) | 이미지 키 기본 ros2_humble, config: $(ls ~/.isaac_ros_common-config 2>/dev/null || echo 없음)"
echo "########## 4. 이미지 빌드 시작(백그라운드) ##########"
cd ~/workspaces/isaac_ros-dev/src/isaac_ros_common/scripts
nohup bash build_image_layers.sh --image_key aarch64.ros2_humble --image_name isaac_ros_dev-aarch64 > /tmp/isaac_build.log 2>&1 &
echo "  pid $! → /tmp/isaac_build.log"; sleep 45; echo "  --- 45 s 후 로그 꼬리 ---"; tail -5 /tmp/isaac_build.log | cut -c1-160; echo "  docker images: $(docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | grep -E 'isaac|nvcr' | tr '\n' ';')"; df -h / | tail -1 | awk '{print "  디스크 여유 "$4}'
