#!/usr/bin/env python3
"""chk_nvlayer_tffix_1027 — §17 수정 층 정지 확인 (2026-10-27, Jetson, 로버 안 움직임).
  SEC 초 동안 전역 · 로컬 코스트맵과 /tf 를 받아, 전역 메시지마다 '로버 2.5 m 안 로컬 치명 칸(odom → map 으로 옮김) 중
  전역에서도 치명(±1 칸)인 비율' 을 잰다. 정상이면 높고 고르게, 단위 변환으로 적힌 장(§15 서명)이면 그 장만 크게 떨어진다.
  끝에 /tmp/nav2.log 의 [NvbloxCostmapLayer] 경고 수(prep 이후). 인자: [SEC=120]"""
import sys, math, time, re
import numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from tf2_msgs.msg import TFMessage
SEC = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class N(Node):
    def __init__(s):
        super().__init__('chk_nvlayer_tffix')
        tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
        s.create_subscription(OccupancyGrid, '/global_costmap/costmap', s.g, tl)
        s.create_subscription(OccupancyGrid, '/local_costmap/costmap', s.l, tl)
        s.create_subscription(TFMessage, '/tf', s.tf, 50)
        s.mo = s.ob = s.L = None; s.rows = []

    def tf(s, m):
        for t in m.transforms:
            v = (t.transform.translation.x, t.transform.translation.y, yaw(t.transform.rotation))
            if t.header.frame_id == 'map' and t.child_frame_id == 'odom': s.mo = v
            elif t.header.frame_id == 'odom' and t.child_frame_id == 'base_link': s.ob = v

    def l(s, m):
        i = m.info; g = np.array(m.data, np.int16).reshape(i.height, i.width); J, I = np.nonzero(g == 100)
        s.L = np.c_[i.origin.position.x + (I + .5) * i.resolution, i.origin.position.y + (J + .5) * i.resolution]

    def g(s, m):
        if s.mo is None or s.ob is None or s.L is None: return
        i = m.info; G = np.array(m.data, np.int16).reshape(i.height, i.width) == 100
        c, sn = math.cos(s.mo[2]), math.sin(s.mo[2])
        P = np.c_[s.mo[0] + c * s.L[:, 0] - sn * s.L[:, 1], s.mo[1] + sn * s.L[:, 0] + c * s.L[:, 1]]
        rx, ry = s.mo[0] + c * s.ob[0] - sn * s.ob[1], s.mo[1] + sn * s.ob[0] + c * s.ob[1]
        P = P[np.hypot(P[:, 0] - rx, P[:, 1] - ry) < 2.5]
        if not len(P): return
        ii = ((P[:, 0] - i.origin.position.x) / i.resolution).astype(int); jj = ((P[:, 1] - i.origin.position.y) / i.resolution).astype(int)
        hit = 0
        for a, b in zip(ii, jj):
            hit += bool(G[max(b - 1, 0):b + 2, max(a - 1, 0):a + 2].any())
        s.rows.append((time.time(), len(P), hit / len(P)))


rclpy.init(); n = N(); t0 = time.time()
while time.time() - t0 < SEC: rclpy.spin_once(n, timeout_sec=0.1)
R = np.array([r[2] for r in n.rows]) if n.rows else np.zeros(0)
print('전역 메시지 %d 장 · 로버 2.5 m 안 로컬 치명 칸 중앙 %d · 전역 일치율 중앙 %.3f · 최소 %.3f · 0.8 미만 장 %d' % (
    len(R), int(np.median([r[1] for r in n.rows])) if n.rows else 0, np.median(R) if len(R) else -1, R.min() if len(R) else -1, int((R < 0.8).sum())))
for t, k, f in n.rows:
    if f < 0.8: print('  낮음 %s 칸 %d 일치 %.3f' % (time.strftime('%H:%M:%S', time.localtime(t)), k, f))
try:
    W = [l for l in open('/tmp/nav2.log', errors='replace') if 'NvbloxCostmapLayer' in l]
    print('nav2.log [NvbloxCostmapLayer] 줄 %d (Can\'t transform %d · must be 2d %d)' % (len(W), sum("Can't transform" in l for l in W), sum('must be 2d' in l for l in W)))
    for l in W[-3:]: print('  ', re.sub(r'\x1b\[[0-9;]*m', '', l.strip())[:200])
except OSError as e: print('nav2.log 못 읽음', e)
