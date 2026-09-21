#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
BOX_HINT='1.15 -0.10' timeout 100 python3 /tmp/job248_audit.py 2>&1 | grep -av '^\[' | head -12 | cut -c1-180
