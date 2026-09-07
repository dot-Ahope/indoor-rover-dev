#!/usr/bin/env python3
"""텔레메트리 모니터 (구독 전용 — /cmd_vel 을 발행하지 않음).
CLI(UART5)로 모터를 돌리면서 휠별 duty/pps/주기를 관찰할 때 사용.
  사용: python3 job43_mon.py [DUR초=60] [간격초=0.5]
출력: t  L(tgt v d pps T cv w sc) | R(...)  + status level 전이
※ cmd_vel 을 한 번도 발행하지 않으므로 보드의 cmd_vel 워치독(500ms)이 무장되지 않음."""
import sys, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from diagnostic_msgs.msg import DiagnosticArray

dur = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
dt  = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
rclpy.init(); n = Node('telemon')
t0 = time.time(); last = None; kv = {}

def lvl(x): return x[0] if isinstance(x, (bytes, bytearray)) else int(x)
def st_cb(m):
    global last
    for s in m.status:
        for v in s.values: kv[v.key] = v.value
        key = (lvl(s.level), s.message)
        if key != last:
            last = key; print(f"[{time.time()-t0:6.2f}s] >>> status level={key[0]} '{key[1]}'", flush=True)
n.create_subscription(DiagnosticArray, '/rover/status', st_cb, qos_profile_sensor_data)

print(f"모니터 {dur}s (간격 {dt}s). 보드 CLI 로 모터를 조작하세요.", flush=True)
next_log = time.time()
while time.time() - t0 < dur:
    rclpy.spin_once(n, timeout_sec=0.02)
    if time.time() >= next_log:
        print(f"[{time.time()-t0:6.2f}s] L[{kv.get('L','-')}]  R[{kv.get('R','-')}]", flush=True)
        next_log += dt
print("모니터 종료")
