#!/bin/bash
# 10-23 §5 MPPI PathAlignCritic cost_weight 만 Jetson yaml(소스 · 설치본)에 반영(인자: 값, 기본 28). 실행 중 값은 안 바꿈 — 다음 prep 으로 적용(10-14 실행 중 변경 멈칫 교훈). 로버 안 움직임
V=${1:-28.0}
for f in $(find ~/ros2_ws/src ~/ros2_ws/install -name nav2_params.yaml 2>/dev/null); do
  ls -l "$f" | awk '{print "  " $1, $NF}'
  python3 - "$f" "$V" <<'PY'
import sys, re
p, v = sys.argv[1], sys.argv[2]; s = open(p, encoding='utf-8').read()
s2, n = re.subn(r'(\n\s+PathAlignCritic: \{enabled: true, cost_power: 1, cost_weight: )[0-9.]+', r'\g<1>' + v, s)
if s2 != s: open(p, 'w', encoding='utf-8').write(s2)
print('  %s → %s (%s)' % (p, re.findall(r'PathAlignCritic: \{enabled: true, cost_power: 1, cost_weight: ([0-9.]+)', s2), '바뀜' if s2 != s else '이미 같은 값'))
PY
done
