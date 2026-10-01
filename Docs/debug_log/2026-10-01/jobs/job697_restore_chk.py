#!/usr/bin/env python3
"""09-30 §4 F1-2 복원 확인: 불러온 /map 크기·원점(저장본 office_v1 = 301×213, 원점 (−5.09, −6.96))과
   map→base_link 자세를 1 s 간격 15 회 — 원점 대비 거리·흔들림. 판정: 첫 안정값이 원점에서 ≤ 5 cm, 5 s 안 안정(연속 변화 ≤ 1 cm)."""
import time, math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from tf2_ros import Buffer, TransformListener

rclpy.init(); n = Node('restore_chk'); tb = Buffer(); TransformListener(tb, n)
mp = [None]
n.create_subscription(OccupancyGrid, '/map', lambda m: mp.__setitem__(0, m),
                      QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


t0 = time.time(); P = []
while time.time() - t0 < 16:
    rclpy.spin_once(n, timeout_sec=0.05)
    if len(P) < int(time.time() - t0):
        try:
            t = tb.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
            P.append((time.time() - t0, t.translation.x, t.translation.y, math.degrees(yaw(t.rotation))))
        except Exception:
            P.append((time.time() - t0, float('nan'), float('nan'), float('nan')))
m = mp[0]
if m:
    i = m.info; print('/map %d×%d, 해상도 %.3f, 원점 (%.2f, %.2f) — 저장본 office_v1 301×213 (−5.09, −6.96) · office_v2 333×227 (−5.29, −6.96)' % (i.width, i.height, i.resolution, i.origin.position.x, i.origin.position.y))
else:
    print('/map 수신 없음')
for t, x, y, th in P: print('  %4.1f s  map (%+.4f, %+.4f, %+.2f°)  원점 거리 %.2f cm' % (t, x, y, th, 100 * math.hypot(x, y)))
ok = [p for p in P if not math.isnan(p[1])]
if len(ok) >= 6:
    last = ok[-5:]; spread = max(math.hypot(a[1] - b[1], a[2] - b[2]) for a in last for b in last)
    print('마지막 5 표본 흔들림 %.2f cm, 원점 거리 %.2f cm' % (100 * spread, 100 * math.hypot(last[-1][1], last[-1][2])))
