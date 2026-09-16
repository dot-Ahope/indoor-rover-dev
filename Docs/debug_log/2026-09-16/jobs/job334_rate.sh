#!/bin/bash
# mp3 nav2.log: 제어 루프 지연 경고 수·시각 분포, 진행 실패, MPPI 메시지
LOGT=${1:-1789525870}
python3 - "$LOGT" <<'PY'
import re, sys
lt = float(sys.argv[1]); pat = re.compile(r'\[(\d{10}\.\d+)\]')
miss = []; prog = []; other = []
for line in open('/tmp/nav2.log', errors='replace'):
    m = pat.search(line)
    if not m or float(m.group(1)) < lt: continue
    t = float(m.group(1)) - lt
    if 'missed its desired rate' in line: miss.append(t)
    elif 'Failed to make progress' in line: prog.append(t)
    elif re.search(r'Optimizer|MPPI|mppi|collision|Aborting|Begin navigating|clear', line): other.append('%6.1f %s' % (t, line.strip()[:150]))
print('루프 지연 경고 %d 건 (goal 후 %.1f ~ %.1f s)' % (len(miss), min(miss) if miss else 0, max(miss) if miss else 0))
import collections
b = collections.Counter(int(t // 10) * 10 for t in miss)
print('  10 s 구간별: ' + ' '.join('%d~:%d' % (k, b[k]) for k in sorted(b)))
print('진행 실패: ' + ' '.join('%.1f' % t for t in prog))
print('\n'.join(other[:20]))
PY
echo "--- 현재 load: $(cut -d' ' -f1-3 /proc/loadavg)   depth_relay CPU: $(top -bn1 | grep -a depth_relay | awk '{print $9}' | head -1)"
