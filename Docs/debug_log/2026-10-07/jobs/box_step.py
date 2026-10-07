#!/usr/bin/env python3
"""10-07 §8.3 전역 카메라 STVL 층 실측 — 한 번 실행 = 한 단계. 상자 ②(map x 1.1~1.3, y −0.1~+0.1)·상자 ①(1.3~1.6, −0.45~−0.3) 칸 수를
   /global_costmap/costmap(0~100, ≥ 99)에서 0.5 s 마다 세고, 둘 밖 카메라 높이 영역(출발 방 x 0.3~2.0, y −0.3~0.4)의 고비용 칸(유령 후보)도 센다.
   단계: mark N(정지 N s) | fwd D(앞으로 D m, 0.05 m/s, 휠·EKF 거리로 정지) | back D(뒤로) | watch N(정지 N s — 그동안 사용자가 상자를 치우거나 놓음)
   결과는 /tmp/box_step.csv 에 덧붙임(t, 단계, 로버 x·y·yaw(map), 상자②, 상자①, 그 밖 고비용)."""
import sys, math, time, numpy as np, rclpy, tf2_ros
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import OccupancyGrid, Odometry
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
rclpy.init(); n = Node('box_step'); pub = n.create_publisher(Twist, '/cmd_vel', 10)
buf = tf2_ros.Buffer(); tf2_ros.TransformListener(buf, n); G = {}; O = {}
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('m', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
n.create_subscription(Odometry, '/odometry/filtered', lambda m: O.__setitem__('p', (m.pose.pose.position.x, m.pose.pose.position.y)), qos_profile_sensor_data)
def spin(sec):
    t = time.time() + sec
    while time.time() < t: rclpy.spin_once(n, timeout_sec=0.02)
def count(x0, x1, y0, y1):
    m = G.get('m')
    if m is None: return -1
    g = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); r = m.info.resolution; ox, oy = m.info.origin.position.x, m.info.origin.position.y
    a = g[int((y0 - oy) / r):int((y1 - oy) / r) + 1, int((x0 - ox) / r):int((x1 - ox) / r) + 1]; return int((a >= 99).sum())
def sample(stage, f):
    try: tr = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; P = (tr.translation.x, tr.translation.y, math.degrees(yaw(tr.rotation)))
    except Exception: P = (float('nan'),) * 3
    b2, b1 = count(1.1, 1.3, -0.1, 0.1), count(1.3, 1.6, -0.45, -0.3); allc = count(0.3, 2.0, -0.3, 0.4)
    f.write('%.2f,%s,%.3f,%.3f,%.1f,%d,%d,%d\n' % (time.time(), stage, *P, b2, b1, allc - (b2 if b2 > 0 else 0))); f.flush(); return P, b2, b1, allc
cmd, val = sys.argv[1], float(sys.argv[2]); f = open('/tmp/box_step.csv', 'a'); t0 = time.time()
spin(3.0)
if cmd in ('fwd', 'back'):
    sg = 1 if cmd == 'fwd' else -1; tw = time.time()
    while 'p' not in O and time.time() - tw < 8: spin(0.2)
    p0 = O['p']; tm = time.time()
    while math.hypot(O['p'][0] - p0[0], O['p'][1] - p0[1]) < val and time.time() - tm < val / 0.05 + 8:
        t = Twist(); t.linear.x = sg * 0.05; pub.publish(t); spin(0.1)
        if int((time.time() - tm) * 2) % 2 == 0: sample(cmd, f)
    for _ in range(10): pub.publish(Twist()); spin(0.05)
    print('%s %.2f m 끝(이동 %.3f m, %.1f s)' % (cmd, val, math.hypot(O['p'][0] - p0[0], O['p'][1] - p0[1]), time.time() - tm)); val = 2.0
last = None
while time.time() - t0 < val + 3:
    P, b2, b1, a = sample(cmd, f); spin(0.5)
    s = '%5.1f s 로버 (%.2f,%.2f,%+.0f°) | 상자② %d · 상자① %d · 출발 방 고비용 %d' % (time.time() - t0, P[0], P[1], P[2], b2, b1, a)
    if s[8:] != last: print(s, flush=True); last = s[8:]
