#!/bin/bash
# (10-20 §9.4) N-SHM S3 — S 구성 prep 10 회 + 사고 모사(-9). 건강은 로그로만. 마지막 회 구성 그대로 둠. 로버 안 움직임
set +u; N=${1:-10}; CN=isaac_ros_dev-aarch64-container
SA="emitter_off:=true vslam:=shadow dds_shm:=true"
err() { cat /tmp/sensors.log /tmp/nvblox_node.log /tmp/cuvslam.log 2>/dev/null | grep -acE 'open_and_lock_file|RTPS_TRANSPORT_SHM|init_port'; }
for i in $(seq 1 $N); do
  P=$(SENSORS_ADD="$SA" bash /tmp/prep_patrol.sh lite 2>&1); OK=$(echo "$P" | grep -ac PREP_OK); CL=$(echo "$P" | grep -a "SHM 고아" | sed 's/^ *//' | cut -c1-70)
  sleep 25
  VT=$(grep -a "vslam_twist\]: 출력" /tmp/sensors.log | tail -1 | grep -o "출력 [0-9]* · 버림 [0-9]*")
  L=/tmp/nvblox_node.log; n=$(grep -an "NVBlox Rates" $L | tail -1 | cut -d: -f1); NV=$(sed -n "$((n+4)),$((n+6))p" $L | grep -a depth_image_callback | awk '{print $NF}')
  YW=$(timeout 8 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -a "RPY (degree" | tail -1 | grep -o "\[.*\]" | awk -F', ' '{print $3}' | tr -d ']')
  printf "%02d PREP_OK %s · %s · vslam_twist[%s] · nvblox 깊이 %s Hz · map→odom yaw %s° · SHM 오류 %d" $i $OK "$CL" "$VT" "$NV" "$YW" $(err)
  case $i in
    3|6|9) pkill -9 -f 'realsense2_camera_[c]ontainer'; K="카메라 -9";;
    4|8) docker exec $CN bash -c "pkill -9 -f '^/opt/ros/humble/lib/nvblox_ros/nvblox_[n]ode'"; K="nvblox -9";;
    7) docker exec $CN bash -c "pkill -9 -f '__node:=cuvslam_[c]ontainer'"; K="cuVSLAM -9";;
    *) K="";;
  esac
  if [ -n "$K" ]; then sleep 10; echo -n " | $K → 10 s 뒤: /dev/shm $(ls /dev/shm | grep -c fastrtps) · SHM 오류 $(err) · 남은 카메라 $(pgrep -fc 'realsense2_camera_[c]ontainer') nvblox $(docker exec $CN bash -c "pgrep -fc '^/opt/ros/humble/lib/nvblox_ros/nvblox_[n]ode' || true") cuVSLAM $(docker exec $CN bash -c "pgrep -fc '__node:=cuvslam_[c]ontainer' || true")"; fi
  echo
  cat /tmp/sensors.log /tmp/nvblox_node.log /tmp/cuvslam.log 2>/dev/null | grep -aE 'open_and_lock_file|RTPS_TRANSPORT_SHM|init_port' | head -2 | cut -c1-160
done
echo "끝: /dev/shm fastrtps $(ls /dev/shm | grep -c fastrtps)"
