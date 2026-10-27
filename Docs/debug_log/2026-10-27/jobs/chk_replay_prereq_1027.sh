#!/bin/bash
# §26 재생 준비 확인(읽기만)
ls -d /tmp/bag_f2tt1 /tmp/bag_f2tf1 2>&1; ls ~/slam_ws/install/slam_toolbox/lib/slam_toolbox/ 2>&1 | head; ls ~/maps/office/ | grep v3; python3 -c "import rosbag2_py;print(\"rosbag2_py OK\")"; nproc; free -m | head -2; uptime
