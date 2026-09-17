#!/usr/bin/env python3
"""저속 정지 출발 실측 (2026-09-17, 펌웨어 STOP 0.010→0.005 플래시 후) — 로버가 움직인다: 사용자 출발 지시 필수.
각 스텝: 정지(1 s) → 지령 DWELL 초 → 정지. 직진 지령과 제자리 회전 지령을 따로.
기록: 휠별 tgt/v/duty/pps(마지막 1 s 평균, /rover/status), EKF 변위·yaw 변화, 스톨 이벤트.
  직진(m/s): 0.003(→승격 0.008) 0.005(→0.008) 0.008 0.010 0.015
  회전(rad/s, 휠 ±ω·0.443/2): 0.020(±4.4→8 mm/s) 0.036(±8.0) 0.050(±11.1)
사용: python3 job397_lowspeed.py [DWELL=3.0]
예상 이동: 직진 합계 ≈ (8+8+8+10+15)×3 mm ≈ 15 cm, 회전 합계 ≈ (0.036+0.036+0.05)×3 rad ≈ 21°"""
import sys, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from diagnostic_msgs.msg import DiagnosticArray
from nav_msgs.msg import Odometry
dwell = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
rclpy.init(); n = Node('lowspeed397')
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
def hold(sec, cmd, stat=False):
    t_end = time.time() + sec; nxt = time.time(); smp = []
    while time.time() < t_end:
        rclpy.spin_once(n, timeout_sec=0.01)
        if time.time() >= nxt: pub.publish(cmd); nxt += 0.05
        if stat and time.time() > t_end - 1.0:
            L, R = parse('L'), parse('R')
            if L and R: smp.append((L, R))
    return smp
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
hold(1.0, Twist())
print('%-10s | %-22s | %-22s | %8s %8s | 판정' % ('지령', 'L tgt/v/duty/pps', 'R tgt/v/duty/pps', 'EKF mm/s', 'yaw °/s'), flush=True)
steps = [('v', 0.003), ('v', 0.005), ('v', 0.008), ('v', 0.010), ('v', 0.015), ('w', 0.020), ('w', 0.036), ('w', 0.050)]
for kind, val in steps:
    hold(1.0, Twist())
    p0 = list(pose); cmd = Twist()
    if kind == 'v': cmd.linear.x = val
    else: cmd.angular.z = val
    s = hold(dwell, cmd, stat=True); p1 = list(pose)
    hold(0.8, Twist())
    if not s or None in p0 + p1: print('%s=%.3f 데이터 없음' % (kind, val), flush=True); continue
    a = lambda side, key: sum(x[side].get(key, 0) for x in s) / len(s)
    dist = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); dyaw = math.degrees(wrap(p1[2] - p0[2]))
    lv, rv = a(0, 'v'), a(1, 'v')
    moving = (abs(lv) > 3 and abs(rv) > 3)
    print('%s=%.3f   | %4.0f/%4.0f/%3.0f/%4.0f     | %4.0f/%4.0f/%3.0f/%4.0f     | %8.1f %8.1f | %s' % (
        kind, val, a(0, 'tgt'), lv, a(0, 'd'), a(0, 'pps'), a(1, 'tgt'), rv, a(1, 'd'), a(1, 'pps'), dist / dwell * 1000, dyaw / dwell,
        '기동' if moving else ('한쪽만' if (abs(lv) > 3 or abs(rv) > 3) else '무반응')), flush=True)
hold(1.0, Twist())
if events: print('이상 상태:', [(round(t % 1000, 1), l, m) for t, l, m in events[:6]])
