#!/bin/bash
# 10-26 §11 MPPI PathAlign · PathFollow cost_weight 를 Jetson yaml(소스 · 설치본)에만 반영. 인자: PathAlign PathFollow(기본 28 5, 되돌리기 14 10).
#   실행 중 값은 안 바꿈 — 다음 prep 으로 적용(10-14 실행 중 변경 멈칫 교훈). 저장소 기본값은 그대로(시험 뒤 되돌림). 로버 안 움직임
A=${1:-28.0}; F=${2:-5.0}
for f in $(find ~/ros2_ws/src/rover_navigation ~/ros2_ws/install/rover_navigation -name nav2_params.yaml 2>/dev/null); do
  [ -L "$f" ] && { echo "  링크(건너뜀) $f"; continue; }
  python3 - "$f" "$A" "$F" <<'PY'
import sys, re
p, a, f = sys.argv[1:4]; s = open(p, encoding='utf-8').read()
s2 = re.sub(r'(\n\s+PathAlignCritic: \{enabled: true, cost_power: 1, cost_weight: )[0-9.]+', r'\g<1>' + a, s)
s2 = re.sub(r'(\n\s+PathFollowCritic: \{enabled: true, cost_power: 1, cost_weight: )[0-9.]+', r'\g<1>' + f, s2)
if s2 != s: open(p, 'w', encoding='utf-8').write(s2)
print('  %s → PathAlign %s · PathFollow %s (%s)' % (p, re.findall(r'PathAlignCritic: \{enabled: true, cost_power: 1, cost_weight: ([0-9.]+)', s2), re.findall(r'PathFollowCritic: \{enabled: true, cost_power: 1, cost_weight: ([0-9.]+)', s2), '바뀜' if s2 != s else '같음'))
PY
done
