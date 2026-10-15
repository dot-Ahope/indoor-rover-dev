#!/bin/bash
# (10-15 §22) /tmp/nvblox_local.yaml(PC 저장소 판)을 Jetson src 로 배포 — 원본은 날짜 붙여 백업. 설치본은 src 링크라 다음 기동부터 적용. 로버 안 움직임
D=~/ros2_ws/src/rover_navigation/config; B=$D/nvblox_local.yaml.bak_$(date +%m%d_%H%M%S)
cp -p $D/nvblox_local.yaml $B && cp /tmp/nvblox_local.yaml $D/nvblox_local.yaml || { echo 배포 실패; exit 1; }
echo "백업 $B"; echo "배포 뒤 site: $(grep -o 'esdf_integrator_max_site_distance_vox: *[0-9.]*' $D/nvblox_local.yaml) · 설치본 링크 $(grep -o 'esdf_integrator_max_site_distance_vox: *[0-9.]*' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml)"
