#!/bin/bash
# (10-20 §9.2) N-SHM S2 정지 A/B — U(UDP) → S(dds_shm) → U. 각 prep → 20 s → 60 s 측정 → 25 s 기록. 마지막은 S 로 둔다(다음 단계용). 로버 안 움직임
set +u
for n in sh_u1 sh_s sh_u2; do [ -e /home/jetson/bags/$n ] && { echo "★ 이름 충돌 ~/bags/$n — 중단"; exit 1; }; done
printf '/camera/camera/depth/image_rect_raw:\n  reliability: best_effort\n  history: keep_last\n  depth: 10\n  durability: volatile\n/tf:\n  reliability: best_effort\n  history: keep_last\n  depth: 100\n  durability: volatile\n' > /tmp/sh_qos.yaml
rb() { awk '/^Udp:/{n++} n==2 && /^Udp:/{print $6; exit}' /proc/net/snmp; }
CN=isaac_ros_dev-aarch64-container
for C in u1 s u2 s_end; do
  case $C in s|s_end) SA="emitter_off:=true vslam:=shadow dds_shm:=true";; *) SA="emitter_off:=true vslam:=shadow";; esac
  echo "########## $C ($SA) ##########"
  SENSORS_ADD="$SA" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|불합격\|★\|SHM 고아\|cuVSLAM(컨테이너)" | tail -3
  [ $C = s_end ] && break
  echo "  위치 추정: $(timeout 8 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE 'Translation|RPY \(degree' | tail -2 | tr -s ' ' | tr '\n' ' ')"
  P=$(pgrep -f 'realsense2_camera_container' | head -1); echo "  카메라 프로파일: $(tr '\0' '\n' < /proc/$P/environ 2>/dev/null | grep FASTRTPS | sed 's#.*/##') · cuVSLAM 프로파일: $(grep -ao 'DDS [a-z_]*.xml' /tmp/cuvslam_up.log /tmp/sensors.log 2>/dev/null | tail -1)"
  sleep 20
  V0=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); G0=$(grep -ac 'Delta between' /tmp/cuvslam.log); E0=$(rb)
  python3 -u /tmp/chk_vslam_live.py 60 2>&1 | grep -av "^\[INFO\]"
  V1=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); G1=$(grep -ac 'Delta between' /tmp/cuvslam.log); E1=$(rb)
  echo "  EKF 위반 +$((V1-V0)) · cuVSLAM 프레임 간격 경고 +$((G1-G0)) · 수신 버퍼 버림 $(( (E1-E0)/60 ))/s · SHM 오류 $(cat /tmp/sensors.log /tmp/cuvslam.log 2>/dev/null | grep -acE 'open_and_lock_file|RTPS_TRANSPORT_SHM|init_port')"
  L=/tmp/nvblox_node.log; n=$(grep -an "NVBlox Rates" $L | tail -1 | cut -d: -f1); echo "  nvblox $(sed -n "$((n+4)),$((n+5))p" $L | tr -s ' \t' ' ' | tr '\n' '|')"
  timeout 25 ros2 bag record -o /home/jetson/bags/sh_$C --qos-profile-overrides-path /tmp/sh_qos.yaml /tf /tf_static /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info /nvblox_node/static_map_slice > /tmp/sh_rec_$C.log 2>&1
done
echo "  /dev/shm fastrtps 지금 $(ls /dev/shm | grep -c fastrtps)"
