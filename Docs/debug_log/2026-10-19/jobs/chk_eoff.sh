#!/bin/bash
# 10-19 §25: 프로젝터 끔 구성 정지 점검(읽기만) — 프로젝터 상태, 원시 IR · 깊이 주기, IR 밝기
echo "== emitter_enabled: $(timeout 8 ros2 param get /camera/camera depth_module.emitter_enabled 2>&1 | tail -1)"
for t in /camera/raw/infra1/image_rect_raw /camera/camera/depth/image_rect_raw /camera/depth/points_filtered /nvblox_node/static_map_slice; do printf "  %-38s %s\n" $t "$(timeout 7 ros2 topic hz $t 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"; done
timeout 6 ros2 topic echo /camera/camera/infra1/metadata --field json_data 2>/dev/null | grep -aoE '"(frame_laser_power|actual_exposure|gain_level)":-?[0-9]+' | head -3 | paste -sd' '
grep -a "Loaded node\|emitter_splitter.*10 s" /tmp/sensors.log | tail -2 | cut -c1-200
