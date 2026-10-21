#!/bin/bash
W=~/workspaces/isaac_ros-dev/src
echo "== Dockerfile.realsense"; cat $W/isaac_ros_common/docker/Dockerfile.realsense
echo "== scripts"; ls $W/isaac_ros_common/scripts
echo "== git"; for r in isaac_ros_common isaac_ros_nvblox; do (cd $W/$r && echo "$r $(git describe --tags --always 2>/dev/null) $(git branch --show-current 2>/dev/null)"); done
echo "== splitter src"; find $W/isaac_ros_nvblox -maxdepth 4 -iname '*splitter*' | head
echo "== nvblox examples launch realsense"; ls $W/isaac_ros_nvblox/nvblox_examples/nvblox_examples_bringup/launch/sensors 2>&1; ls $W/isaac_ros_nvblox/nvblox_examples/nvblox_examples_bringup/config/sensors 2>&1
echo "== container ws build dirs"; docker exec isaac_ros_dev-aarch64-container bash -c 'ls /workspaces/isaac_ros-dev; ls -d /workspaces/isaac_ros-dev/*/ ; ls /opt/ros/humble/share | grep -i -E "realsense|splitter"; ls /usr/local/lib | grep -i realsense | head -3'
echo "== host camera usb"; lsusb | grep -i intel; ls /dev/video* | head
echo "== container sees video?"; docker exec isaac_ros_dev-aarch64-container bash -c 'ls /dev/video* 2>&1 | head -3; ls /dev/bus/usb 2>&1 | head -2'
