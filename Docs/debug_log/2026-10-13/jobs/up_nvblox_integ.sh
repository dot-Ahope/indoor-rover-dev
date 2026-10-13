#!/bin/bash
# (10-13 §14) nvblox 통합 거리(projective_integrator_max_integration_distance_m)를 Jetson 의 nvblox_local.yaml(소스·설치본)에 반영 — 재기동 없음(다음 prep 때 적용). 인자: 값. 로버 안 움직임
V=${1:-2.0}
for f in $(find ~/ros2_ws/src ~/ros2_ws/install -name nvblox_local.yaml 2>/dev/null); do
  [ -L "$f" ] && { echo "  (링크) $f"; continue; }
  sed -i -E "s/^(\s+projective_integrator_max_integration_distance_m: )[0-9.]+/\1$V/" "$f"; echo "  $f → $(grep -o 'max_integration_distance_m: [0-9.]*' $f)"
done
echo "  nvblox 가 읽는 파일: $(grep -rhoE '[^ ]*nvblox[^ ]*\.yaml' /tmp/nvblox_up.sh ~/nvblox_up.sh ~/ros2_ws/src/rover_navigation/launch/nvblox.launch.py 2>/dev/null | sort -u | head -4 | tr '\n' ' ')"
echo "  실행 중 nvblox 로그의 통합 거리: $(grep -a 'max_integration_distance' /tmp/nvblox_node.log 2>/dev/null | tail -1 | cut -c1-120)"
