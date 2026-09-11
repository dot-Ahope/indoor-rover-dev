#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 /tmp/job301_back.py 0.8 2>&1 | sed 's/^/  /'
python3 /tmp/job225_face.py 0 2.0 2>&1 | tail -1 | sed 's/^/  /'
echo -n "  최종: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "  상자: $(BOX_HINT='1.27 -0.15' python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:' | head -1 | cut -c1-48)"
