#!/bin/bash
# 10-19 §23: IMU 켬 판 내보내기 재실행 + 두 판 요약 출력(읽기 위주)
CN=isaac_ros_dev-aarch64-container
for I in true false; do echo "== IMU $I"; timeout 120 docker exec -u admin $CN bash -c "source /opt/ros/humble/setup.bash; cd /workspaces/isaac_ros-dev/vslam; python3 export_vslam.py out_imu_$I vslam_$I" 2>&1 | grep -v "^\[INFO\]" | tail -4; done
ls /home/jetson/workspaces/isaac_ros-dev/vslam/*.csv
