#!/bin/bash
# 10-20: 하루 시작 상태 + f2z1 cuVSLAM 결과 유무(읽기만)
echo "uptime: $(uptime -p) · base $(systemctl --user is-active rover-base)"
ls -la /home/jetson/workspaces/isaac_ros-dev/vslam/ | grep -aE "f2z1|csv" 
echo "스택 프로세스: $(pgrep -fc "controller_server|slam_toolbox|realsense2_camera")"; ls /tmp/prep_fast.sh /tmp/prep_patrol.sh 2>&1 | tr "
" " "; echo; df -h /home/jetson | tail -1
