#!/bin/bash
source /opt/ros/humble/setup.bash
echo "visual_preset: $(ros2 param get /camera/camera depth_module.visual_preset 2>&1)"
echo "카메라 로그 프리셋 줄: $(grep -aic preset /tmp/sensors.log 2>/dev/null)"
