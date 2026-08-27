#!/bin/bash
# D455 camera_link 오프셋 (Intel realsense2_description xacro)
f=/opt/ros/humble/share/realsense2_description/urdf/_d455.urdf.xacro
ls -l "$f"
echo "===PROPERTIES==="
grep -E 'property name="d455_cam_' "$f"
echo "===BOTTOM_SCREW_TO_CAMERA_LINK==="
grep -n -A4 'bottom_screw_frame' "$f" | grep -E 'origin|joint' | head -6
echo "===IMU_FRAME==="
grep -n -B1 -A3 'imu' "$f" | grep -E 'origin|joint name' | head -6
