#!/bin/bash
# 09-29 §9: 단독 확인 정리 — cuVSLAM·전용 카메라 종료(원래 스택은 다음 prep 으로 복귀)
docker exec isaac_ros_dev-aarch64-container bash -lc "pkill -INT -f visual_slam_launch_container; sleep 2; pkill -9 -f visual_slam_launch_container" 2>/dev/null
pkill -INT -f realsense2_camera_node; sleep 3; pkill -9 -f realsense2_camera_node 2>/dev/null
echo "남은: cuVSLAM $(pgrep -fc visual_slam_launch_container), 카메라 $(pgrep -fc realsense2_camera_node) | base $(systemctl --user is-active rover-base)"
