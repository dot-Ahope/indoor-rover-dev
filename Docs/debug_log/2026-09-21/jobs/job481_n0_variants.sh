#!/bin/bash
# N0 (iv) 복셀 0.03 + 입력 해상도 변형(디시메이션 2 → 320x240, 1 → 640x480). 각 조건: nvblox 재시작 → 15 s 대기 → 슬라이스 20 s 측정 → 통계 블록·tegrastats 5 s. 끝에 dec 4·복셀 0.05 복귀. 인자: BX BY
set +u
BX=$1; BY=$2; CN=isaac_ros_dev-aarch64-container
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
X() { docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "$1"; }
run_variant() {   # 이름 yaml dec
  local NM=$1 Y=$2 DEC=$3
  echo "######## $NM (yaml $Y, dec $DEC)"
  timeout 10 ros2 param set /camera/camera decimation_filter.filter_magnitude $DEC 2>&1 | tail -1; sleep 3
  echo "  깊이 이미지: $(timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field width 2>/dev/null | head -1)x$(timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field height 2>/dev/null | head -1) @ $(timeout 8 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1)"
  X 'pkill -INT -f nvblox_node; sleep 2; pkill -9 -f nvblox_node 2>/dev/null; true'
  docker exec -d -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/$Y -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > /tmp/nvblox_$NM.log 2>&1"
  sleep 15
  X "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job474_n0_measure.py $NM 20 $BX $BY /nvblox_node/static_map_slice 2>&1 | grep -av '^\['" &
  sleep 8; timeout 6 tegrastats --interval 1000 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /GR3D_FREQ/) g=$(i+1); if(match($0,/CPU \[[^]]*\]/)) c=substr($0,RSTART,RLENGTH); print "  tegra GPU " g " " c}' | tail -3
  echo "  nvblox CPU: $(top -b -n2 -d2 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk '$12 ~ /nvblox/ {printf "%s%% ", $9}')"
  wait
  awk '/NVBlox Rates/{b=""; f=1} f{b=b"\n"$0} END{print b}' /tmp/nvblox_$NM.log | grep -E "ros/depth |ros/update_esdf|ros/depth_image_callback" | sed 's/^/  rate /' | cut -c1-80
  awk '/NVBlox Delays/{b=""; f=1} f{b=b"\n"$0} END{print b}' /tmp/nvblox_$NM.log | grep -E "esdf_integration|depth_image_callback" | sed 's/^/  delay /' | cut -c1-80
  grep -aE "tsdf/integrate |ros/esdf/integrate " /tmp/nvblox_$NM.log | tail -2 | awk '{printf "  time %s mean %.2f ms\n", $1, $3*1000/$2}'
  grep -ciE "drop|error" /tmp/nvblox_$NM.log | sed 's/^/  drop·error 줄 수: /'
}
run_variant v03_dec4 nvblox_n0_v03.yaml 4
run_variant v05_dec2 nvblox_n0.yaml 2
run_variant v05_dec1 nvblox_n0.yaml 1
echo "######## 복귀: dec 4, 복셀 0.05"; run_variant v05_dec4 nvblox_n0.yaml 4
