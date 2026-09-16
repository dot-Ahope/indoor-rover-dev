#!/bin/bash
source /opt/ros/humble/setup.bash
X=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml
echo "BT SmoothPath 노드: $(grep -c '<SmoothPath' $X)  ForceSuccess: $(grep -c ForceSuccess $X)  controller: $(grep -o 'controller_id=\"FollowPathMPPI\"' $X | head -1)"
echo "bt_navigator 로그 오류: $(grep -a 'bt_navigator' /tmp/nav2.log | grep -aci 'error')"
grep -a "bt_navigator" /tmp/nav2.log | grep -ai "error\|fail\|unknown\|not registered" | tail -3 | cut -c1-170
echo "=== job248 감사 (기준 표 0.9~1.4 행 + 틈) ==="
BOX_HINT='1.085 -0.008' python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자:|^   \[|^   (0\.9|1\.[0-4])0 |틈|최소폭' | cut -c1-150
