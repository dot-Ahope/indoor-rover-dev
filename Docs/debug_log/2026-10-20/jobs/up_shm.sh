#!/bin/bash
# (10-20 §9.1) N-SHM S1 배포 + 빌드 — /tmp/vs_* 를 rover_bringup src 에(원본 날짜 백업), 새 config 파일이라 colcon 빌드. 로버 안 움직임
D=~/ros2_ws/src/rover_bringup; T=$(date +%m%d_%H%M%S)
for f in launch/camera.launch.py launch/ekf.launch.py scripts/cuvslam_up.sh; do cp -p $D/$f $D/$f.bak_$T; done
cp /tmp/vs_camera.launch.py $D/launch/camera.launch.py; cp /tmp/vs_ekf.launch.py $D/launch/ekf.launch.py
cp /tmp/vs_cuvslam_up.sh $D/scripts/cuvslam_up.sh; chmod +x $D/scripts/cuvslam_up.sh; cp /tmp/vs_fastdds_shm_udp.xml $D/config/fastdds_shm_udp.xml
source /opt/ros/humble/setup.bash; cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -3
ls -la ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_shm_udp.xml | cut -c1-150
echo "백업 .bak_$T"
