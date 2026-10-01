#!/bin/bash
# 10-01 §8.15: f2a6 목표 3(D) CANCELED 166.6 s — 원인
grep -aE "STUCK|nav_guard|취소" /tmp/nav2.log | tail -10 | cut -c1-230
python3 - <<'PY'
import re, datetime, collections
t0 = datetime.datetime.now().replace(hour=14, minute=32, second=0, microsecond=0).timestamp(); c = collections.Counter(); first = {}
for l in open("/tmp/nav2.log", errors="replace"):
    m = re.search(r"\[(\d{10})\.\d+\]", l)
    if not m or not (t0 <= int(m.group(1)) <= t0 + 240): continue
    if not re.search(r"WARN|ERROR", l): continue
    k = re.sub(r"\[\d{10}\.\d+\]", "", l); k = re.sub(r"[-+]?\d+\.\d+", "#", k).strip()[:150]; c[k] += 1; first.setdefault(k, datetime.datetime.fromtimestamp(int(m.group(1))).strftime("%H:%M:%S"))
for k, n in c.most_common(25): print("%4d  %s  %s" % (n, first[k], k))
PY
