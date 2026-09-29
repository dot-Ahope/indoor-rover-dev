#!/bin/bash
# 09-29 §9 준비: 컨테이너 cuVSLAM 노드·파라미터, realsense_splitter 유무, 호스트 realsense 드라이버 버전
CN=isaac_ros_dev-aarch64-container
X() { docker exec -u admin $CN bash -lc "source /opt/ros/humble/setup.bash; $1"; }
X "ros2 pkg executables isaac_ros_visual_slam; ros2 pkg list | grep -E 'realsense|splitter' ; ls /opt/ros/humble/share/isaac_ros_visual_slam/launch/ /opt/ros/humble/share/isaac_ros_visual_slam/params 2>/dev/null"
X "grep -hE 'name=|parameters|remappings' /opt/ros/humble/share/isaac_ros_visual_slam/launch/isaac_ros_visual_slam_realsense.launch.py 2>/dev/null | head -40; sed -n 1,200p /opt/ros/humble/share/isaac_ros_visual_slam/launch/isaac_ros_visual_slam_realsense.launch.py 2>/dev/null | grep -vE '^#|^$' | head -90"
dpkg-query -W -f='${Package} ${Version}\n' ros-humble-realsense2-camera librealsense2 2>/dev/null
