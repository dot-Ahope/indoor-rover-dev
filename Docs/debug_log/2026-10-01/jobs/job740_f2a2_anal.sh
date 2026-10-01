#!/bin/bash
# 10-01 §8.4: f2a2 분석 — 실주행 map→odom 결손(job734), 주행 구간 Nav2 경고·오류(job732 형식), 위치 추정 노드 CPU(top)
python3 /tmp/job734_tflag_bag.py /tmp/bag_f2a2 2>&1 | grep -av "^\["
echo "-- transformPose 오류 수(12:58:48~13:00:00): $(python3 - <<'PY'
import re, datetime
t0 = datetime.datetime.now().replace(hour=12, minute=58, second=48, microsecond=0).timestamp(); n = 0
for l in open('/tmp/nav2.log', errors='replace'):
    m = re.search(r'\[(\d{10})\.\d+\]', l)
    if m and t0 <= int(m.group(1)) <= t0 + 72 and 'transformPose' in l: n += 1
print(n)
PY
)"
bash /tmp/job732_abort_why.sh 12 58 48 72 | head -30
grep -a "localiz" /tmp/top_f2a2.log | awk '{s+=$9; if($9>m)m=$9; n++} END{printf "-- 위치 추정 노드 CPU(top 표본 %d): 평균 %.0f %% 최대 %.0f %%\n", n, s/n, m}'
