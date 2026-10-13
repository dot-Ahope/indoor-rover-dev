#!/bin/bash
# (10-13 §5.3) 전역 inflation 감쇠 계수를 Jetson 의 nav2_params.yaml(소스·설치본)에 반영 → 순회 prep → 실행 중 값 확인. 인자: 값(기본 3.0). 로버 안 움직임
V=${1:-3.0}
for f in $(find ~/ros2_ws/src ~/ros2_ws/install -name nav2_params.yaml 2>/dev/null); do
  [ -L "$f" ] && { echo "  (링크) $f → $(readlink -f $f)"; continue; }
  python3 - "$f" "$V" <<'PY'
import sys, re
p, v = sys.argv[1], sys.argv[2]; s = open(p, encoding='utf-8').read()
n = len(re.findall(r'inflation_radius: 0\.70\n(\s+)cost_scaling_factor: [0-9.]+', s))
s2 = re.sub(r'(inflation_radius: 0\.70\n\s+cost_scaling_factor: )[0-9.]+', r'\g<1>' + v, s)
open(p, 'w', encoding='utf-8').write(s2); print('  %s: 전역 감쇠 %d 곳 → %s (%s)' % (p, n, v, '바뀜' if s2 != s else '이미 같은 값'))
PY
done
bash /tmp/prep_patrol.sh lite 15.0
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "  실행 중 전역 inflation: $(timeout 15 ros2 param get /global_costmap/global_costmap inflation_layer.cost_scaling_factor 2>&1 | tail -1) · $(timeout 15 ros2 param get /global_costmap/global_costmap inflation_layer.inflation_radius 2>&1 | tail -1)"
