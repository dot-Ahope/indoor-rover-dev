#!/bin/bash
# (10-20 §2) B 시험: 프로젝터 켬(지금) vs 상시 끔 — 각 구성 prep → 20 s 안정 → 20 s 기록 → 마지막에 지금 구성으로 복귀. 로버 안 움직임
#   기록: ~/bags/bt_<on|off> (/tf /tf_static 깊이 camera_info nvblox 조각 로컬 코스트맵). prep 스크립트는 /tmp 에 올려 둔 것.
set +u
rec() {
  local B=/home/jetson/bags/bt_$1; rm -rf $B
  printf '/camera/camera/depth/image_rect_raw:\n  reliability: best_effort\n  history: keep_last\n  depth: 10\n  durability: volatile\n/tf:\n  reliability: best_effort\n  history: keep_last\n  depth: 100\n  durability: volatile\n' > /tmp/bt_qos.yaml
  timeout 25 ros2 bag record -o $B --qos-profile-overrides-path /tmp/bt_qos.yaml /tf /tf_static /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info /nvblox_node/static_map_slice /local_costmap/costmap > /tmp/bt_rec_$1.log 2>&1
  ros2 bag info $B 2>/dev/null | grep -aE "Duration|depth/image|slice|costmap" | sed 's/Serialization Format: cdr//' | cut -c1-120
}
for C in on off; do
  echo "########## 구성 $C ##########"
  if [ $C = on ]; then bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|불합격\|★" | tail -2
  else SENSORS_ADD="emitter_off:=true" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|불합격\|★" | tail -2; fi
  echo "  프로젝터 emitter_enabled: $(timeout 8 ros2 param get /camera/camera depth_module.emitter_enabled 2>&1 | tail -1)"
  sleep 20; rec $C
done
echo "########## 지금 구성으로 복귀 ##########"; bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK" | tail -1
