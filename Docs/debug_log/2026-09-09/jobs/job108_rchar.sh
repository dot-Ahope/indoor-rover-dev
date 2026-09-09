#!/bin/bash
# 결정적 측정: agent 가 시리얼에서 실제로 읽어들이는 바이트 수(rchar)를 토픽 수신량과 같은 버킷으로 기록.
#   odom 사망 후에도 rchar 가 유지 → 보드는 계속 보냄, 젯슨/agent 가 못 살림
#   odom 사망과 함께 rchar 도 급감  → 보드가 발행을 포기
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

# 컨테이너 내부에서 '실행 파일이 micro_ros_agent 인' pid 를 고른다 (entrypoint sh 제외)
APID=$(docker exec microros_agent sh -c '
for p in $(ls /proc | grep -E "^[0-9]+$"); do
  exe=$(readlink /proc/$p/exe 2>/dev/null)
  case "$exe" in *micro_ros_agent) echo "$p";; esac
done' 2>/dev/null | head -1)
echo "agent pid(컨테이너 내부) = ${APID:-찾기 실패}"
docker exec microros_agent sh -c "ls -l /proc/$APID/fd 2>/dev/null | grep -aiE 'tty|rover|USB'" 2>&1 | sed 's/^/  fd: /'
echo "  io 샘플: $(docker exec microros_agent sh -c "grep -E '^rchar' /proc/$APID/io" 2>&1)"
echo ""

python3 - "$APID" <<'PY'
import rclpy, time, subprocess, sys
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, BatteryState
from diagnostic_msgs.msg import DiagnosticArray
APID = sys.argv[1] if len(sys.argv) > 1 else ''

def rchar():
    if not APID: return None
    try:
        out = subprocess.run(['docker', 'exec', 'microros_agent', 'sh', '-c',
                              'grep -E "^(rchar|wchar)" /proc/%s/io' % APID],
                             capture_output=True, text=True, timeout=4).stdout
        d = {}
        for ln in out.splitlines():
            k, _, v = ln.partition(':')
            if k.strip() in ('rchar', 'wchar'): d[k.strip()] = int(v)
        return d if len(d) == 2 else None
    except Exception:
        return None

rclpy.init(); n = Node('rch')
C = {'odom': 0, 'imu': 0, 'stat': 0, 'bat': 0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
n.create_subscription(BatteryState, '/battery', mk('bat'), qos_profile_sensor_data)
print("   구간     odom   imu  stat  bat |  보드->젯슨 B/s   기대(메시지합) B/s")
prev = rchar()
for b in range(16):
    base = dict(C); tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    cur = rchar()
    d = {k: (C[k]-base[k])/el for k in C}
    payload = d['odom']*720 + d['imu']*330 + d['stat']*280 + d['bat']*100
    if prev and cur:
        io = "%13.0f %18.0f" % ((cur['rchar']-prev['rchar'])/el, payload)
    else:
        io = "     (io 불가) %13.0f" % payload
    prev = cur
    print("  %3.0f-%3.0fs %6.2f %5.2f %5.2f %5.2f |%s"
          % (b*5, b*5+5, d['odom'], d['imu'], d['stat'], d['bat'], io), flush=True)
rclpy.shutdown()
PY
