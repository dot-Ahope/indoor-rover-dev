#!/bin/bash
# (10-20 §6) cuVSLAM 실시간 그림자 구성 배포 + 빌드 — /tmp/vs_* 를 rover_bringup src 에(바뀌는 원본은 날짜 붙여 백업), prep_fast 는 /tmp 판 교체. 로버 안 움직임
D=~/ros2_ws/src/rover_bringup; T=$(date +%m%d_%H%M%S)
for f in CMakeLists.txt launch/ekf.launch.py; do cp -p $D/$f $D/$f.bak_$T; done
cp /tmp/vs_ekf.launch.py $D/launch/ekf.launch.py; cp /tmp/vs_cuvslam_container.launch.py $D/launch/cuvslam_container.launch.py
cp /tmp/vs_cuvslam_up.sh $D/scripts/cuvslam_up.sh; cp /tmp/vs_vslam_twist.py $D/scripts/vslam_twist.py; cp /tmp/vs_CMakeLists.txt $D/CMakeLists.txt
chmod +x $D/scripts/cuvslam_up.sh $D/scripts/vslam_twist.py
echo "백업 접미사 .bak_$T · CMakeLists 차이:"; diff $D/CMakeLists.txt.bak_$T $D/CMakeLists.txt | head -6
source /opt/ros/humble/setup.bash
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -4
ls -la ~/ros2_ws/install/rover_bringup/lib/rover_bringup/ | grep -E "vslam_twist|cuvslam_up"; ls ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/ | grep cuvslam
echo "컨테이너 cuVSLAM 패키지: $(docker exec isaac_ros_dev-aarch64-container bash -lc 'source /opt/ros/humble/setup.bash; ros2 pkg prefix isaac_ros_visual_slam' 2>&1 | tail -1)"
