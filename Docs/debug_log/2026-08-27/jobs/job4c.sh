#!/bin/bash
f=/opt/ros/humble/share/realsense2_description/urdf/_d455.urdf.xacro
grep -nE 'd455_mesh_x_offset|d455_imu_p[xyz]' "$f" | grep property
echo "===JOINT_CHAIN==="
sed -n '55,75p' "$f"
