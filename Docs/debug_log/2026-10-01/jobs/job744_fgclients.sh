#!/bin/bash
# 10-01 §8.8: foxglove_bridge 클라이언트 접속 기록 — 주행(f2a2 12:58·f2a3 13:41) 중 연결된 클라이언트가 있었나, 지금 연결은 누구인가
python3 - <<'PY'
import re, datetime
for l in open('/tmp/sensors.log', errors='replace'):
    if 'foxglove' not in l: continue
    if not re.search(r'connect|Client|subscri|disconnect|Subscribe|Unsubscribe', l, re.I): continue
    m = re.search(r'\[(\d{10})\.\d+\]', l); t = datetime.datetime.fromtimestamp(int(m.group(1))).strftime('%H:%M:%S') if m else '?'
    print(t, re.sub(r'\[\d{10}\.\d+\]', '', l).strip()[:200])
PY
echo "-- 지금 8765 연결:"; ss -tnp 2>/dev/null | grep -a ":8765" | head
echo "-- sensors.log 시작: $(head -c 300 /tmp/sensors.log | grep -aoE '\[[0-9]{10}' | head -1 | tr -d '[' | xargs -I{} date -d @{} +%T)"
