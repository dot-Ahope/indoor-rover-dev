#!/bin/bash
# 보드가 /rover/status 로 보고하는 발행 시도/실패 카운터를 5초 간격 차분으로 본다.
#   c   = 스핀 루프 사이클 누적
#   ot/of = odom 발행 시도/실패,  orc = 마지막 실패 rc
#   it/if = imu  발행 시도/실패
# 동시에 실제 수신 주기도 기록해, '보드가 시도했는데 실패' 인지 '아예 시도 안 함' 인지 가른다.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - <<'PY'
import rclpy, time, re
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, BatteryState
from diagnostic_msgs.msg import DiagnosticArray
rclpy.init(); n = Node('txdiag')
C = {'odom': 0, 'imu': 0, 'stat': 0, 'bat': 0}
TX = {}
def mk(k):
    def cb(m): C[k] += 1
    return cb
def cb_stat(m):
    C['stat'] += 1
    for st in m.status:
        for kv in st.values:
            if kv.key == 'TX':
                d = dict(re.findall(r'(\w+)=(-?\d+)', kv.value))
                TX.update({k: int(v) for k, v in d.items()})
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(BatteryState, '/battery', mk('bat'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', cb_stat, qos_profile_sensor_data)

t0 = time.time()
while time.time()-t0 < 15 and not TX: rclpy.spin_once(n, timeout_sec=0.1)
if not TX:
    print("TX 필드 수신 실패 — 펌웨어 반영 확인 필요"); raise SystemExit(1)
print("보드 보고 시작:", TX)
print("")
print("   구간 | 보드측(초당)                        | 실제 수신(Hz)")
print("        | 루프  odom시도 odom실패  imu시도 imu실패 | odom   imu  stat   bat   | 마지막 rc")
prev = dict(TX); pc = dict(C)
for b in range(14):
    tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    d = {k: (TX.get(k, 0)-prev.get(k, 0))/el for k in ('c', 'ot', 'of', 'it', 'if')}
    r = {k: (C[k]-pc[k])/el for k in C}
    prev = dict(TX); pc = dict(C)
    print("  %3.0fs | %5.1f %8.1f %8.1f %8.1f %7.1f | %5.1f %5.1f %5.1f %5.1f | %d"
          % (b*5+5, d['c'], d['ot'], d['of'], d['it'], d['if'],
             r['odom'], r['imu'], r['stat'], r['bat'], TX.get('orc', 0)), flush=True)
print("")
print("판정 기준:")
print("  odom시도>0 & odom실패≈시도  → rcl_publish 가 거부 (버퍼/스트림). rc 값이 원인 코드")
print("  odom시도>0 & odom실패≈0     → 보드는 성공했다고 보는데 전달 안 됨 (전송 계층/링크)")
print("  odom시도≈0                  → 게이트/루프가 안 돎")
rclpy.shutdown()
PY
