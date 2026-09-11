#!/usr/bin/env python3
"""통과 가능성 판정 — 이 배치에서 로버가 지나갈 틈이 있는가 (2026-09-11).

  왜: job231 에서 계획선이 상자로부터 0.191m 를 지났다. 내접반경(차체 반폭 0.165 +
      footprint_padding 0.05)이 0.215m 이므로 **계획선이 내접 영역 안**이고, RPP 는 그것을
      충돌로 본다. NavFn 은 253(inscribed)을 '비싸지만 통과 가능' 으로 보므로 두 모듈의
      기준이 어긋난다. 통로가 좁을 때 이 틈이 드러난다.
      → 먼저 **물리적으로 지나갈 틈이 있는지** 를 재고, 없으면 배치를 바꾸는 것이 맞다.

  방법: 전역 코스트맵에서 로버 진행 방향 전방 각 x 단면마다,
        차체 중심을 놓을 수 있는 y 구간(비용 < 내접 99)을 찾아 폭을 낸다.
        그 폭이 0 이면 그 단면은 통과 불가. 최소 폭과 그 위치를 보고한다.
  로버는 움직이지 않는다.
"""
import math
import time
import rclpy
import tf2_ros
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

INSCRIBED_PUB = 99
HW, PAD = 0.165, 0.05

rclpy.init()
n = Node('pass233')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
S = {}
qos_tl = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                    reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap',
                      lambda m: S.__setitem__('gc', m), qos_tl)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap',
                      lambda m: S.__setitem__('lc', m), qos_tl)


def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y,
                math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z)))
    except Exception:
        return None


t0 = time.time()
while time.time() - t0 < 25 and (pose() is None or 'gc' not in S or 'lc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
p = pose()
if p is None or 'gc' not in S:
    print('준비 실패')
    raise SystemExit(1)
print('로버 map (%.3f, %.3f) hd=%.2f deg' % (p[0], p[1], math.degrees(p[2])))
print('내접반경 = 반폭 %.3f + 패딩 %.2f = %.3f m' % (HW, PAD, HW + PAD))
print()

for key, name in (('gc', '전역'), ('lc', '로컬')):
    g = S[key]
    res = g.info.resolution
    ox, oy = g.info.origin.position.x, g.info.origin.position.y

    def cost(mx, my):
        i = int((mx - ox) / res)
        j = int((my - oy) / res)
        if 0 <= i < g.info.width and 0 <= j < g.info.height:
            return g.data[j * g.info.width + i]
        return -1

    co, si = math.cos(p[2]), math.sin(p[2])
    print('=== %s 코스트맵: 전방 단면별 통과 가능 폭 ===' % name)
    print('  전방x   중심을 놓을 수 있는 y 구간들 (비용<99)          최대폭')
    worst = (99.0, None)
    for k in range(2, 41):
        lx = 0.05 * k
        runs = []
        cur = None
        for m in range(-24, 25):
            ly = 0.05 * m
            mx = p[0] + lx*co - ly*si
            my = p[1] + lx*si + ly*co
            v = cost(mx, my)
            free = (0 <= v < INSCRIBED_PUB)
            if free and cur is None:
                cur = ly
            elif not free and cur is not None:
                runs.append((cur, ly - 0.05))
                cur = None
        if cur is not None:
            runs.append((cur, 1.20))
        widths = [b - a + 0.05 for a, b in runs]
        mw = max(widths) if widths else 0.0
        if lx <= 2.0 and mw < worst[0]:
            worst = (mw, lx)
        if k % 2 == 0 or mw < 0.15:
            txt = ' '.join('[%+.2f~%+.2f]' % (a, b) for a, b in runs) if runs else '(없음)'
            flag = '  <-- 통과 불가' if mw <= 0.0 else ('  <-- 빠듯' if mw < 0.15 else '')
            print('  %.2f   %-48s %.2f m%s' % (lx, txt[:48], mw, flag))
    print('  → 전방 2.0m 이내 최소 통과폭 %.2f m (전방 %.2f m 지점)' % worst)
    print()

print('판정 기준: 최소 통과폭이 0 이면 물리적으로 못 지나간다.')
print('           0 보다 크되 작으면(< 0.15m) 계획이 거의 정확히 중앙을 지나야 하므로')
print('           NavFn 의 경로 길이 선호와 충돌한다.')
