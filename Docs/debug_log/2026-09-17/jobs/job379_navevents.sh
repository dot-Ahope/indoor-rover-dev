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
echo "=== SLAM 생존(주행 후) ==="; export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\["
printf "로버 map 자세: "; timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "=== top: 프로세스별 CPU 평균/최대 (주행 중) ==="
python3 - "$NAME" <<'PY'
import sys, re, collections
name = sys.argv[1]; S = collections.defaultdict(list); snaps = 0; loads = []
try:
    lines = open('/tmp/top_%s.log' % name, errors='replace').read().splitlines()
except Exception as e:
    print('top 로그 없음', e); sys.exit()
for l in lines:
    if l.startswith('top -'):
        snaps += 1; m = re.search(r'load average: ([\d.]+)', l); loads.append(float(m.group(1)) if m else 0)
    m = re.match(r'\s*(\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S\s+([\d.]+)\s+[\d.]+\s+\S+\s+(.*)', l)
    if m and snaps > 1:
        S[m.group(3).strip()[:40]].append(float(m.group(2)))
print('스냅샷 %d (2 s), load 평균 %.1f 최대 %.1f' % (snaps, sum(loads) / max(1, len(loads)), max(loads) if loads else 0))
tot = snaps - 1
for k, v in sorted(S.items(), key=lambda kv: -sum(kv[1]))[:12]:
    print('  %-40s 평균 %5.1f%% 최대 %5.1f%%' % (k, sum(v) / max(1, tot), max(v)))
PY
