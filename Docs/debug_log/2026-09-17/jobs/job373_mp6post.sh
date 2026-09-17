#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "=== nav2.log goal 이후 ==="
python3 - <<'PY'
import re
pat = re.compile(r'\[(\d{10}\.\d+)\]'); t0 = None
for line in open('/tmp/nav2.log', errors='replace'):
    m = pat.search(line)
    if not m: continue
    t = float(m.group(1))
    if 'Begin navigating' in line and t > 1789607900: t0 = t
    if t0 and t >= t0 and re.search(r'Begin navigating|Failed to make progress|STUCK|Aborting|missed its desired|Goal succeeded|clear|cancel|Reached|collision|Optimizer', line):
        print('%6.1f %s' % (t - t0, line.strip()[:150]))
PY
echo "=== drive 로그 주요 ==="; grep -aE "상자 확정|출발|^결과|①|②|③|⑥|조향" /tmp/drive_mp6.log | cut -c1-160
[ -d /tmp/bag_mp6 ] && tar czf /tmp/bag_mp6.tgz -C /tmp bag_mp6 && echo "bag tgz $(stat -c %s /tmp/bag_mp6.tgz)"
