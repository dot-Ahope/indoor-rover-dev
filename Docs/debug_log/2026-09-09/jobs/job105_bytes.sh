#!/bin/bash
# 결정적 측정: 보드->젯슨 UART 실바이트 유입량과 토픽 수신량을 같은 5초 버킷으로 동시 기록.
#   붕괴 후에도 바이트가 계속 들어오면  → 보드는 보내는데 agent 가 못 살림 (젯슨/에이전트 문제)
#   붕괴와 함께 바이트도 줄면          → 보드가 발행을 포기 (펌웨어/전송 계층 문제)
# 컨테이너 안에서 /proc/<agent>/io 를 읽으므로 호스트 sudo 불필요.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
APID=$(docker exec microros_agent sh -c "ls /proc | grep -E '^[0-9]+$' | while read p; do grep -qa micro_ros_agent /proc/\$p/cmdline 2>/dev/null && echo \$p; done" 2>/dev/null | head -1)
echo "agent 내부 pid = ${APID:-찾기 실패}"
if [ -z "$APID" ]; then echo "io 카운터 접근 불가 — 토픽만 기록합니다"; fi

python3 - "$APID" <<'PY'
import rclpy, time, subprocess, sys
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, BatteryState
from diagnostic_msgs.msg import DiagnosticArray

APID = sys.argv[1] if len(sys.argv) > 1 else ''

def io_counters():
    if not APID:
        return None
    try:
        out = subprocess.run(['docker', 'exec', 'microros_agent', 'cat', '/proc/%s/io' % APID],
                             capture_output=True, text=True, timeout=4).stdout
        d = {}
        for ln in out.splitlines():
            k, _, v = ln.partition(':')
            if k in ('rchar', 'wchar'):
                d[k] = int(v)
        return d if len(d) == 2 else None
    except Exception:
        return None

rclpy.init(); n = Node('obs105')
C = {'odom': 0, 'imu': 0, 'stat': 0, 'bat': 0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
n.create_subscription(BatteryState, '/battery', mk('bat'), qos_profile_sensor_data)

print("   구간      odom    imu  status  bat |  보드->젯슨 B/s  젯슨->보드 B/s")
prev = io_counters()
for b in range(18):
    base = dict(C); tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    cur = io_counters()
    if prev and cur:
        rx = (cur['rchar']-prev['rchar'])/el; tx = (cur['wchar']-prev['wchar'])/el
        io = "%14.0f %14.0f" % (rx, tx)
    else:
        io = "        (측정 불가)"
    prev = cur
    print("  %3.0f-%3.0fs  %6.2f %6.2f %6.2f %5.2f |%s"
          % (b*5, b*5+5, (C['odom']-base['odom'])/el, (C['imu']-base['imu'])/el,
             (C['stat']-base['stat'])/el, (C['bat']-base['bat'])/el, io), flush=True)
rclpy.shutdown()
PY
