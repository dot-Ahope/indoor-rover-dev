#!/bin/bash
# 09-22 감쇠 정지 측정: nvblox(YAML) 시작 → 32 s 적분 → 깊이 스트림 차단(enable_depth false) → 상자 셀 소실 시각 기록(job506_decay.py, 호스트) → 깊이 복구 → nvblox 정지. 인자: YAML NAME BX BY [SEC]
set +u
Y=$1; NM=$2; BX=$3; BY=$4; SEC=${5:-80}; CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
nv_pids() { docker exec $CN bash -c "pgrep -f '^$BIN' || true"; }
nv_stop() { local p; for p in $(nv_pids); do docker exec $CN kill -INT $p 2>/dev/null; done; sleep 3; for p in $(nv_pids); do docker exec $CN kill -9 $p 2>/dev/null; done; sleep 1; }
nv_start() { docker exec -d -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/$1 -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > /tmp/nvblox_$2.log 2>&1"; }
echo "## $NM ($Y): 벤더 기본값 대조"; grep -n "tsdf_decay_factor\|decay_tsdf_rate_hz\|decayed_weight_threshold\|decayed_free_distance\|exclude_last_view" /home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_examples/nvblox_examples_bringup/config/nvblox/nvblox_base.yaml | cut -c1-90; echo "  이번 yaml: $(grep -h 'tsdf_decay_factor' /tmp/$Y | tr -s ' ' | cut -c1-60)"
nv_stop; nv_start $Y $NM; sleep 32
echo "  깊이 콜백: $(grep -aA7 'NVBlox Rates' /tmp/nvblox_$NM.log | grep -aE 'ros/depth_image_callback' | awk '{print $NF}' | tail -1) Hz (pid $(nv_pids | tr '\n' ' '))"
python3 /tmp/job506_decay.py $NM $BX $BY $SEC 2>&1 | grep -av '^\[' &
sleep 6; echo "  t=5: enable_depth false → $(timeout 15 ros2 param set /camera/camera enable_depth false 2>&1 | tail -1)"; sleep 4
echo "  깊이 토픽 Hz(차단 뒤): $(timeout 6 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3 || echo 0)"
wait
echo "  복구: enable_depth true → $(timeout 15 ros2 param set /camera/camera enable_depth true 2>&1 | tail -1)"; sleep 6
echo "  깊이 토픽 Hz(복구 뒤): $(timeout 8 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3) | 점군 $(timeout 8 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3) | odom $(timeout 6 ros2 topic hz /odometry/filtered 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3)"
nv_stop; echo "  nvblox 정지"
