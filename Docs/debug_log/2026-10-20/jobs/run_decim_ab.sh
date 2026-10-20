#!/bin/bash
# (10-20 §8.2) 데시메이션 정지 A/B — D4 → D2 → D1 → D4. 각 prep → 20 s → 25 s 기록 + CPU · nvblox 깊이 Hz. 끝나면 D4 복귀. 로버 안 움직임
set +u
for n in dc_d4a dc_d2 dc_d1 dc_d4b; do [ -e /home/jetson/bags/$n ] && { echo "★ 이름 충돌 ~/bags/$n — 중단"; exit 1; }; done
printf '/camera/camera/depth/image_rect_raw:\n  reliability: best_effort\n  history: keep_last\n  depth: 10\n  durability: volatile\n/tf:\n  reliability: best_effort\n  history: keep_last\n  depth: 100\n  durability: volatile\n' > /tmp/dc_qos.yaml
cpu() { head -1 /proc/stat | awk '{print $2+$3+$4+$5+$6+$7+$8, $5+$6}'; }
for C in d4a:4 d2:2 d1:1 d4b:4; do
  nm=${C%%:*}; D=${C##*:}; B=/home/jetson/bags/dc_$nm
  echo "########## $nm (decimation $D) ##########"
  SENSORS_ADD="decimation:=$D" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|불합격\|★" | tail -2
  sleep 20
  a=($(cpu)); timeout 25 ros2 bag record -o $B --qos-profile-overrides-path /tmp/dc_qos.yaml /tf /tf_static /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info /nvblox_node/static_map_slice > /tmp/dc_rec_$nm.log 2>&1; b=($(cpu))
  echo "  CPU(기록 창) $(awk -v t=$((b[0]-a[0])) -v i=$((b[1]-a[1])) 'BEGIN{printf "%.1f", 100*(1-i/t)}') % · EKF 위반 누적 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)"
  L=/tmp/nvblox_node.log; n=$(grep -an "NVBlox Rates" $L | tail -1 | cut -d: -f1); echo "  nvblox $(sed -n "$((n+4)),$((n+5))p" $L | tr -s ' \t' ' ' | tr '\n' '|')"
  ros2 bag info $B 2>/dev/null | grep -aE "depth/image|slice" | sed 's/Serialization Format: cdr//' | cut -c1-110
done
echo "########## 지금 구성(D4)으로 복귀 ##########"; bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK" | tail -1
