#!/bin/bash
# 마지막 "Begin navigating" 이후 nav2.log 이벤트(경로 전달·반복 제외) + 드라이브 로그 표 + bag 압축
NAME=${1:-mp7}
python3 - <<'PY'
import re
pat = re.compile(r'\[(\d{10}\.\d+)\]'); lines = open('/tmp/nav2.log', errors='replace').read().splitlines()
idx = max(i for i, l in enumerate(lines) if 'Begin navigating' in l)
t0 = float(pat.search(lines[idx]).group(1))
skip = re.compile(r'Passing new path to controller|Received a path to smooth|StaticLayer: Resizing')
for l in lines[idx:]:
    m = pat.search(l)
    if not m or skip.search(l): continue
    print('%6.2f %s' % (float(m.group(1)) - t0, l.strip()[:170]))
PY
echo "=== 드라이브 표 (1 s) ==="; grep -aE "^ +[0-9]+\.[0-9] " /tmp/drive_$NAME.log | awk 'NR%10==1' | cut -c1-110
[ -d /tmp/bag_$NAME ] && tar czf /tmp/bag_$NAME.tgz -C /tmp bag_$NAME && echo "bag tgz $(stat -c %s /tmp/bag_$NAME.tgz)"
