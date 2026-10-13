#!/bin/bash
# (10-13 §12) MPPI CostCritic cost_weight 만 Jetson yaml(소스·설치본)에 반영하고, 실행 중인 컨트롤러 값도 같이 바꾼다(재기동 없음). 인자: 값. 로버 안 움직임
V=${1:-3.81}
for f in $(find ~/ros2_ws/src ~/ros2_ws/install -name nav2_params.yaml 2>/dev/null); do
  python3 - "$f" "$V" <<'PY'
import sys, re
p, v = sys.argv[1], sys.argv[2]; s = open(p, encoding='utf-8').read()
s2, n = re.subn(r'(\n\s+CostCritic: \{enabled: true, cost_power: 1, cost_weight: )[0-9.]+', r'\g<1>' + v, s); open(p, 'w', encoding='utf-8').write(s2)
print('  %s → %s (%s)' % (p, re.findall(r'CostCritic: \{enabled: true, cost_power: 1, cost_weight: ([0-9.]+)', s2), '바뀜' if s2 != s else '이미 같은 값'))
PY
done
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "  실행 중 값 설정: $(timeout 15 ros2 param set /controller_server FollowPathMPPI.CostCritic.cost_weight $V 2>&1 | tail -1)"
echo "  실행 중 값 확인: $(timeout 15 ros2 param get /controller_server FollowPathMPPI.CostCritic.cost_weight 2>&1 | tail -1)"
