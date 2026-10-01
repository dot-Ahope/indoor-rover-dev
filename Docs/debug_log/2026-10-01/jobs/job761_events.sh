#!/bin/bash
python3 - "$@" <<'PY'
import re
T3 = int(__import__("sys").argv[1])
for l in open("/tmp/nav2.log", errors="replace"):
    m = re.search(r"\[(\d{10}\.\d+)\]", l)
    if not m: continue
    t = float(m.group(1)) - T3
    if not (-1 <= t <= 95): continue
    if re.search(r"transformPose|progress|Progress|Clear|clear|Aborting|recover|Recover|backup|spin|wait|Passing|Received a goal|Goal|collision at", l) and "Smoothed path" not in l:
        print("%6.1f s  %s" % (t, re.sub(r"\[\d{10}\.\d+\]", "", l).strip()[:170]))
PY
