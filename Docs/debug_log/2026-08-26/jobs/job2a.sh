#!/bin/bash
# Step 2 사전 점검: colcon, 필요한 ROS 패키지, 기존 워크스페이스
echo "===COLCON==="
which colcon || echo NO_COLCON
echo "===ROS_PKGS==="
dpkg -l | grep -oE "ros-humble-(robot-state-publisher|teleop-twist-keyboard|joint-state-publisher|xacro|tf2-tools)" | sort -u
echo "===WS==="
ls ~/ros2_ws 2>/dev/null || echo NO_WS
echo "===ROSDEP==="
which rosdep || echo NO_ROSDEP
