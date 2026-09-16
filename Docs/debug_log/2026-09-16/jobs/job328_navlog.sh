#!/bin/bash
# nav2.log 에서 LOGT 이후의 컨트롤러/복구/오류 줄만 추출 + drive 로그 앞부분
LOGT=${1:-1789520960}
python3 - "$LOGT" <<'PY'
import re, sys
lt = float(sys.argv[1])
pat = re.compile(r'\[(\d{10}\.\d+)\]')
keys = re.compile(r'controller|progress|abort|Abort|recover|Recover|clear|Clear|optim|Optim|MPPI|mppi|trajector|fail|Fail|goal|Goal|behavior|backup|BackUp|wait|Wait|navigat|plan', re.I)
n = 0
for line in open('/tmp/nav2.log', errors='replace'):
    m = pat.search(line)
    if not m or float(m.group(1)) < lt:
        continue
    if keys.search(line):
        print(line.rstrip()[:230]); n += 1
        if n > 80: break
PY
echo "=== drive_mp2.log 앞부분 ==="
head -45 /tmp/drive_mp2.log | cut -c1-200
echo "=== install yaml md5 ==="
md5sum ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/nav2_params.yaml
grep -n "controller_id\|planner_id" ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml | cut -c1-160
