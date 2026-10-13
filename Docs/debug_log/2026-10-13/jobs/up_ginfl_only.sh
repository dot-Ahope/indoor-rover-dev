#!/bin/bash
# (10-13 §6) 전역 inflation 감쇠 계수만 Jetson yaml(소스·설치본)에 반영 — 재기동 없음(실행 중인 Nav2 는 다음 prep 때 바뀜). 인자: 값. 로버 안 움직임
V=${1:-2.0}
for f in $(find ~/ros2_ws/src ~/ros2_ws/install -name nav2_params.yaml 2>/dev/null); do
  python3 - "$f" "$V" <<'PY'
import sys, re
p, v = sys.argv[1], sys.argv[2]; s = open(p, encoding='utf-8').read()
s2 = re.sub(r'(inflation_radius: 0\.70\n\s+cost_scaling_factor: )[0-9.]+', r'\g<1>' + v, s); open(p, 'w', encoding='utf-8').write(s2)
print('  %s → %s (%s)' % (p, re.findall(r'inflation_radius: 0\.70\n\s+cost_scaling_factor: ([0-9.]+)', s2), '바뀜' if s2 != s else '이미 같은 값'))
PY
done
