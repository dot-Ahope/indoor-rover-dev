#!/bin/bash
source /opt/ros/humble/setup.bash
for hint in "1.17 0.0" "1.45 0.0"; do
  echo "=== BOX_HINT $hint ==="
  BOX_HINT="$hint" python3 /tmp/job248_audit.py 2>&1 | grep -aE "낮은 클러스터|^상자:" | cut -c1-260
done
echo "=== TF camera ==="; timeout 8 ros2 run tf2_ros tf2_echo base_link camera_depth_optical_frame 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
