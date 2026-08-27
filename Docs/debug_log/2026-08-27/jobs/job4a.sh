#!/bin/bash
# Step 4 사전: 필요 패키지 apt 가용성 + 현재 USB 장치
for p in ros-humble-rplidar-ros ros-humble-sllidar-ros2 ros-humble-slam-toolbox ros-humble-realsense2-camera ros-humble-realsense2-description ros-humble-foxglove-bridge ros-humble-laser-filters; do
  v=$(apt-cache policy $p 2>/dev/null | grep Candidate | awk '{print $2}')
  echo "$p: ${v:-NOT_AVAILABLE}"
done
echo "===INSTALLED==="
dpkg -l | grep -oE "ros-humble-(rplidar-ros|sllidar-ros2|slam-toolbox|realsense2-camera|realsense2-description|foxglove-bridge)" | sort -u
echo "===LSUSB==="
lsusb | grep -viE "hub|root|bluetooth"
