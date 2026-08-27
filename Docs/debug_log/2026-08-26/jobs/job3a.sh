#!/bin/bash
# Step 3 사전: robot_localization 설치 확인 (없으면 apt 설치)
if dpkg -l | grep -q ros-humble-robot-localization; then
  echo INSTALLED
else
  echo INSTALLING
  echo '<PW>' | sudo -S apt-get install -y ros-humble-robot-localization 2>&1 | tail -3
fi
echo "===VERIFY==="
source /opt/ros/humble/setup.bash
ros2 pkg executables robot_localization | head -5
