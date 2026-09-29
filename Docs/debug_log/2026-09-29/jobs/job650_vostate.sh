#!/bin/bash
# 09-29 §9: VisualSlamStatus 의 vo_state 정의 확인
docker exec isaac_ros_dev-aarch64-container cat /opt/ros/humble/share/isaac_ros_visual_slam_interfaces/msg/VisualSlamStatus.msg | head -20
