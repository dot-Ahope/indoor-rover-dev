#!/usr/bin/env python3
"""바닥 데드밴드 스윕 (2026-09-07, PWM 20kHz 이후 재실측).
각 지령 속도를 DWELL 초 유지하며 휠별 duty/pps/측정속도(FG)와 EKF 변위를 기록.
  사용: python3 job44_deadband.py [DWELL=3.0] [속도들 콤마구분=0.005,0.01,0.015,0.02,0.03]
판정: FG 측정속도가 지령에 도달하면 '기동', duty 만 오르고 v≈0 이면 '데드밴드 미만'.
      EKF 변위는 트랙 슬립까지 포함한 실제 이동."""
import sys, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from diagnostic_msgs.msg import DiagnosticArray
from nav_msgs.msg import Odometry

dwell = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
speeds = [float(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "0.005,0.01,0.015,0.02,0.03").split(",")]

rclpy.init(); n = Node('deadband')
pub = n.create_publisher(Twist, '/cmd_vel', 10)
kv = {}; pose = [None, None, None]; events = []

def lvl(x): return x[0] if isinstance(x, (bytes, bytearray)) else int(x)
def st_cb(m):
    for s in m.status:
        for v in s.values: kv[v.key] = v.value
        if lvl(s.level) != 0: events.append((time.time(), lvl(s.level), s.message))
def od_cb(m):
    q = m.pose.pose.orientation
    pose[0] = m.pose.pose.position.x; pose[1] = m.pose.pose.position.y
    pose[2] = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
n.create_subscription(DiagnosticArray, '/rover/status', st_cb, qos_profile_sensor_data)
n.create_subscription(Odometry, '/odometry/filtered', od_cb, 10)

def parse(k):
    d = {}
    for tok in kv.get(k, '').split():
        if '=' in tok:
            a, b = tok.split('=', 1)
            try: d[a] = int(b)
            except ValueError: pass
    return d

def spin(sec, cmd):
    t_end = time.time() + sec; nxt = time.time(); samples = []
    while time.time() < t_end:
        rclpy.spin_once(n, timeout_sec=0.01)
        if time.time() >= nxt: pub.publish(cmd); nxt += 0.05
        if time.time() > t_end - 1.0:      # 마지막 1초만 통계
            L, R = parse('L'), parse('R')
            if L and R: samples.append((L, R))
    return samples

for _ in range(20): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.02)
time.sleep(0.5); rclpy.spin_once(n, timeout_sec=0.2)
print(f"{'지령':>6} | {'L v':>4} {'L d':>4} {'L pps':>5} | {'R v':>4} {'R d':>4} {'R pps':>5} | {'EKF Δ(cm)':>9} {'실속도':>6} | 판정", flush=True)
total0 = pose[0]
for v in speeds:
    cmd = Twist(); cmd.linear.x = v
    p0 = (pose[0], pose[1])
    s = spin(dwell, cmd)
    p1 = (pose[0], pose[1])
    for _ in range(15): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.02)
    time.sleep(0.8); rclpy.spin_once(n, timeout_sec=0.2)
    if not s: print(f"{v*1000:5.0f}  | 데이터 없음", flush=True); continue
    avg = lambda side, key: sum(x[side].get(key, 0) for x in s) / len(s)
    d = math.hypot(p1[0]-p0[0], p1[1]-p0[1]) if None not in p0 + p1 else float('nan')
    vr = d / dwell
    lv, rv = avg(0, 'v'), avg(1, 'v')
    verdict = "기동" if min(lv, rv) > v*1000*0.6 else ("부분" if max(lv, rv) > v*1000*0.3 else "데드밴드 미만")
    print(f"{v*1000:5.0f}  | {lv:4.0f} {avg(0,'d'):4.0f} {avg(0,'pps'):5.0f} | {rv:4.0f} {avg(1,'d'):4.0f} {avg(1,'pps'):5.0f} | {d*100:9.1f} {vr*1000:6.0f} | {verdict}", flush=True)
for _ in range(20): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.02)
if None not in (total0, pose[0]): print(f"총 전진 (EKF): {(pose[0]-total0)*100:.1f} cm")
if events: print("이상 상태:", [(round(t % 1000, 1), l, m) for t, l, m in events[:5]])
