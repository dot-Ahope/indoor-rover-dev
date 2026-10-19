#!/bin/bash
# (10-19 §15) emitter_splitter 배포 + 빌드 — /tmp/spl.tar 를 rover_bringup src 에 풀고(바뀌는 원본은 날짜 붙여 백업) colcon 빌드.
#   같이: 오늘 재생 때 남은 nvblox_node 고아(--params-file /tmp/nvblox_replay.yaml) 정리 — run_nvblox_replay.sh 가 ros2 run 래퍼만 죽였음. 로버 안 움직임
D=~/ros2_ws/src/rover_bringup; T=$(date +%m%d_%H%M%S); mkdir -p /tmp/spl_x && rm -rf /tmp/spl_x/* && tar xf /tmp/spl.tar -C /tmp/spl_x
for f in CMakeLists.txt package.xml launch/camera.launch.py; do cp -p $D/$f $D/$f.bak_$T; done
cp /tmp/spl_x/emitter_splitter.cpp $D/src/; cp /tmp/spl_x/CMakeLists.txt /tmp/spl_x/package.xml $D/
[ -f /tmp/spl_x/camera.launch.py ] && cp /tmp/spl_x/camera.launch.py $D/launch/   # 10-19 §16 emitter_flash 인자
# 10-19: Jetson src 에 scripts/pad_relief.py 가 없어 설치 단계가 실패(저장소 CMakeLists 가 나열) → 저장소 판을 넣는다(기본 off, 동작 변화 없음)
[ -f /tmp/spl_x/pad_relief.py ] && [ ! -f $D/scripts/pad_relief.py ] && cp /tmp/spl_x/pad_relief.py $D/scripts/ && chmod +x $D/scripts/pad_relief.py
for f in $D/CMakeLists.txt $D/package.xml $D/src/emitter_splitter.cpp $D/scripts/pad_relief.py $D/launch/camera.launch.py; do sed -i 's/\r$//' $f; done
echo "백업 접미사 .bak_$T"
CN=isaac_ros_dev-aarch64-container
echo "재생 nvblox 고아(정리 전): $(docker exec $CN pgrep -fc 'nvblox_replay.yaml')"
docker exec $CN bash -c "pkill -INT -f 'nvblox_replay.yaml'; sleep 2; pkill -9 -f 'nvblox_replay.yaml'" 2>/dev/null
echo "재생 nvblox 고아(정리 뒤): $(docker exec $CN pgrep -fc 'nvblox_replay.yaml') · 실시간 nvblox: $(docker exec $CN pgrep -fc 'nvblox_active.yaml')"
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -15
ls -la ~/ros2_ws/install/rover_bringup/lib/rover_bringup/emitter_splitter_node 2>&1
