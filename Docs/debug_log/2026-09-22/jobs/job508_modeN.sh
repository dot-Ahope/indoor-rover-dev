#!/bin/bash
# 09-22 N4 팔 N2 준비(Jetson 측, prep 뒤에 실행): nvblox(절단 2.0·감쇠 0.99) 시작 → 로컬 코스트맵을 nvblox 층으로 전환(Nav2 만 재기동) → 클리어·8 s 재관측 → 게이트 J·K·L. 인자: NAME BX BY [YAML]
set +u
NM=$1; BX=$2; BY=$3; Y=${4:-nvblox_n0_t2d99.yaml}; CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
nv_pids() { docker exec $CN bash -c "pgrep -f '^$BIN' || true"; }
for p in $(nv_pids); do docker exec $CN kill -INT $p 2>/dev/null; done; sleep 3; for p in $(nv_pids); do docker exec $CN kill -9 $p 2>/dev/null; done; sleep 1
docker exec -d -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/$Y -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > /tmp/nvblox_$NM.log 2>&1"
echo "== nvblox 시작($Y) → 32 s 적분"; sleep 32
echo "  깊이 콜백: $(grep -aA7 'NVBlox Rates' /tmp/nvblox_$NM.log | grep -aE 'ros/depth_image_callback' | awk '{print $NF}' | tail -1) Hz | 감쇠 실효값: $(docker exec -u admin $CN bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 12 ros2 param get /nvblox_node static_mapper.tsdf_decay_factor 2>&1 | tail -1') | 절단: $(docker exec -u admin $CN bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 12 ros2 param get /nvblox_node static_mapper.projective_integrator_truncation_distance_vox 2>&1 | tail -1')"
echo "== 로컬 코스트맵 → nvblox 층 (Nav2 재기동)"; QUICK=1 bash /tmp/job488_layer_ab.sh nvblox $BX $BY 2>&1 | grep -aE '실행값|오류'
echo "== 클리어·8 s 재관측"; bash /tmp/job442_clearwait.sh 2>&1 | tail -1
echo "== 게이트 J·K·L"; bash /tmp/job505_modeN_gate.sh $NM $BX $BY
