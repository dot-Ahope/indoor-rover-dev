#!/bin/bash
# SLAM 준비: slam_toolbox 기동 확인/시작 → /map·map→odom TF·현재 pose
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
if pgrep -f slam_toolbox >/dev/null; then echo "slam_toolbox 이미 실행중"; else
  echo "slam_toolbox 시작..."; setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
  sleep 12
fi
echo "===nodes==="; ros2 node list | tr '\n' ' '; echo
echo "===/map==="; timeout 8 ros2 topic hz /map 2>&1 | grep -aE "average|does not" | tail -1
echo "===map→odom TF==="; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation|RPY \(degree\)" | head -2
echo "===map→base_link (전체 체인)==="; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation" | head -1
echo "===map info==="; timeout 6 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE "resolution|width|height|origin" | head -4 | tr '\n' ' '; echo
echo "===slam 경고==="; grep -aiE "error|warn" /tmp/slam.log 2>/dev/null | tail -3 || echo none
echo "===rates 재확인==="; for t in /scan /wheel_odom /odometry/filtered; do printf "  %-20s %s\n" $t "$(timeout 5 ros2 topic hz $t 2>&1 | grep -aE 'average|does not' | tail -1)"; done
