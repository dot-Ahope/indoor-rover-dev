#!/bin/bash
# (10-13 §4) 상주 경로 조회기 정지 시험: 경로 계산만 요청(로버 안 움직임). 목표 3 개를 한 프로세스로 연달아 조회한다.
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
S=$(date +%s); (sleep 8; echo "2.25 -1.6 -0.6"; sleep 2; echo "5.5 -2.2 0.05"; sleep 2; echo "0 0 2.8"; sleep 2) | timeout 40 python3 -u /tmp/job613_pathyaw.py --serve; echo "끝 $(( $(date +%s) - S )) s · 남은 조회기 프로세스 $(pgrep -fc job613_pathyaw)"
echo "--- 한 번 실행 방식(호환)"; timeout 30 python3 /tmp/job613_pathyaw.py 2.25 -1.6 -0.6
