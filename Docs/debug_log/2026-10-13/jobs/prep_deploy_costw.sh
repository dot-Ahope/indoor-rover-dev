#!/bin/bash
# (10-13 §12) MPPI CostCritic cost_weight 를 Jetson 의 nav2_params.yaml(소스·설치본)에 반영 → 순회 prep(lite, 15) → 실행 중 값 확인. 인자: 값(기본 11.43). 로버 안 움직임
V=${1:-11.43}
for f in $(find ~/ros2_ws/src ~/ros2_ws/install -name nav2_params.yaml 2>/dev/null); do
  python3 - "$f" "$V" <<'PY'
import sys, re
p, v = sys.argv[1], sys.argv[2]; s = open(p, encoding='utf-8').read()
s2, n = re.subn(r'(\n\s+CostCritic: \{enabled: true, cost_power: 1, cost_weight: )[0-9.]+', r'\g<1>' + v, s); open(p, 'w', encoding='utf-8').write(s2)
print('  %s: CostCritic cost_weight %d 곳 → %s (%s)' % (p, n, v, '바뀜' if s2 != s else '이미 같은 값'))
PY
done
bash /tmp/prep_patrol.sh lite 15.0
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
g() { timeout 15 ros2 param get $1 $2 2>&1 | tail -1 | sed 's/.*is: //'; }
echo "  실행 중: CostCritic cost_weight $(g /controller_server FollowPath.CostCritic.cost_weight) · critics $(g /controller_server FollowPath.critics | cut -c1-150)"
echo "  실행 중: 전역 감쇠 $(g /global_costmap/global_costmap inflation_layer.cost_scaling_factor) · 로컬 패딩 $(g /local_costmap/local_costmap footprint_padding) · 전역 패딩 $(g /global_costmap/global_costmap footprint_padding)"
