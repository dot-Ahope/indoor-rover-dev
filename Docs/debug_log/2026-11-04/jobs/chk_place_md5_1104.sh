#!/bin/bash
# 11-04 §4: Jetson src 의 F2.5 파일 md5(CR 제거) — 출발 전 검사 ⓐ 배포 여부 확인, 읽기만
for f in rover_navigation/scripts/place_server.py rover_navigation/scripts/place_cmd.py rover_navigation/scripts/place_web.py rover_navigation/scripts/path_end_yaw.py rover_navigation/config/places.yaml; do [ -f ~/ros2_ws/src/$f ] && echo "$(tr -d '\r' < ~/ros2_ws/src/$f | md5sum | cut -c1-8) $f" || echo "없음 $f"; done
grep -n "start_check\|출발 전\|ⓐ" ~/ros2_ws/src/rover_navigation/scripts/place_server.py | head -3; wc -l < ~/ros2_ws/src/rover_navigation/scripts/place_server.py
