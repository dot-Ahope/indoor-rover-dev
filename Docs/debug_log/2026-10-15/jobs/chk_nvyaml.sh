#!/bin/bash
# (10-15 §22) nvblox_local.yaml 배포 경로 확인 — 읽기만, 로버 안 움직임
for f in ~/ros2_ws/src/rover_navigation/config/nvblox_local.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml /tmp/nvblox_active.yaml; do
  if [ -e "$f" ]; then echo "$f → $(readlink -f $f) · md5 $(md5sum < $f | cut -c1-12) · site $(grep -o 'esdf_integrator_max_site_distance_vox: *[0-9.]*' $f)"; else echo "$f 없음"; fi
done
grep -a "max_site_distance" /tmp/nvblox_node.log | tail -2
