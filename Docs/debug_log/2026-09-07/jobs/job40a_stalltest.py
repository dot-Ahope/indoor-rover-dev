#!/usr/bin/env python3
"""스톨 정책 검증 (받침대): /cmd_vel 을 20Hz 로 DUR 초 발행하며 /rover/status 전이·휠별 텔레메트리·휠 속도를 기록.
사용: python3 job40a_stalltest.py DUR VX [WZ]
values[] (펌웨어 2026-09-07 텔레메트리): L/R = "tgt=목표mm/s v=측정mm/s d=duty% pps=펄스/s T=평균주기us cv=주기변동계수% sc=스톨창샘플"
기대: 휠을 기계적으로 세우면 level1 'STALL — auto-recovering' → 1.5s 후 재개 → 10s 내 3회면 level2 'STALL latched'."""
import sys, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from diagnostic_msgs.msg import DiagnosticArray
from nav_msgs.msg import Odometry

dur = float(sys.argv[1]); vx = float(sys.argv[2]); wz = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
rclpy.init(); n = Node('stalltest')
pub = n.create_publisher(Twist, '/cmd_vel', 10)
t0 = time.time(); last = None; odo = [None, None]; events = []; kv = {}

def lvl(x): return x[0] if isinstance(x, (bytes, bytearray)) else int(x)
def st_cb(m):
    global last
    for s in m.status:
        for v in s.values: kv[v.key] = v.value
        key = (lvl(s.level), s.message)
        if key != last:
            last = key; ev = f"[{time.time()-t0:6.2f}s] status level={key[0]} '{key[1]}'"; events.append(ev); print(ev, flush=True)
def od_cb(m): odo[0] = m.twist.twist.linear.x; odo[1] = m.twist.twist.angular.z
n.create_subscription(DiagnosticArray, '/rover/status', st_cb, qos_profile_sensor_data)
n.create_subscription(Odometry, '/wheel_odom', od_cb, qos_profile_sensor_data)

cmd = Twist(); cmd.linear.x = vx; cmd.angular.z = wz
print(f"cmd_vel vx={vx} wz={wz} for {dur}s  (20Hz)", flush=True)
next_pub = time.time(); next_log = time.time()
while time.time() - t0 < dur:
    rclpy.spin_once(n, timeout_sec=0.01)
    now = time.time()
    if now >= next_pub: pub.publish(cmd); next_pub += 0.05
    if now >= next_log:
        if odo[0] is None: print(f"[{now-t0:6.2f}s] wheel_odom 없음", flush=True)
        else:
            B = 0.245  # 펌웨어 WHEEL_BASE — v_l/v_r 역산 (raw, 스케일 미보정)
            print(f"[{now-t0:6.2f}s] L={odo[0]-odo[1]*B/2:.4f} R={odo[0]+odo[1]*B/2:.4f} | L[{kv.get('L','-')}] R[{kv.get('R','-')}]", flush=True)
        next_log += 0.5
for _ in range(10): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.05)
print("=== 정지. 이벤트 요약 ==="); [print("  " + e) for e in events]
print(f"최종 status: {last}")
