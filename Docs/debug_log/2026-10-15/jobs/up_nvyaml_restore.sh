#!/bin/bash
# (10-15 §23) Jetson src nvblox_local.yaml 을 가장 최근 백업(site 2.0)으로 되돌림 — 지금 판은 날짜 붙여 따로 보관. 로버 안 움직임
D=~/ros2_ws/src/rover_navigation/config; B=$(ls -1t $D/nvblox_local.yaml.bak_* | head -1)
cp -p $D/nvblox_local.yaml $D/nvblox_local.yaml.site1_$(date +%m%d_%H%M%S) && cp -p $B $D/nvblox_local.yaml || { echo 되돌림 실패; exit 1; }
echo "되돌림 ← $B · site $(grep -o 'esdf_integrator_max_site_distance_vox: *[0-9.]*' $D/nvblox_local.yaml)"
