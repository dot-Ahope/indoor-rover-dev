#!/usr/bin/env python3
"""anal_goal_block — 목표 주변이 왜 막혔나: 목표점 둘레의 전역 코스트맵 칸 · 라이다 점을 시각별로. (2026-10-21 §10, PC)
  인자: bag 목표x 목표y [반경=0.6] [시각들 t(s, bag 시작 기준) 쉼표]
  출력: 각 시각에 반경 안 100(LETHAL)·≥99(INSCRIBED 포함) 칸 수와 가장 가까운 칸, 라이다 점(map 좌표, SLAM TF) 수와 가장 가까운 점.
  ⚠ 메시지(OccupancyGrid)의 비용은 0~100 으로 바뀌어 있다: 100 = LETHAL(254), 99 = INSCRIBED(253). 첫 판은 ≥253 으로 셌다가 늘 0 — 고침."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, gx, gy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
R = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
TQ = [float(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else None


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


GC, SL, SC, MO, OB, ST = [], [], [], [], [], {}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    t0 = rd.start_time * 1e-9
    want = ('/global_costmap/costmap', '/scan', '/tf', '/tf_static')   # nvblox 슬라이스는 rosbags 기본 형식에 없어 뺌
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
        m = rd.deserialize(raw, c.msgtype); tt = t * 1e-9 - t0
        if c.topic == '/tf' or c.topic == '/tf_static':
            for tr in m.transforms:
                a = (tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if c.topic == '/tf_static': ST[tr.child_frame_id] = (tr.header.frame_id, a)
                elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, a))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, a))
        elif c.topic == '/scan':
            SC.append((tt, m.angle_min, m.angle_increment, np.array(m.ranges)))
        else:
            g = m.info; arr = np.array(m.data, dtype=np.int16).reshape(g.height, g.width)
            (GC if c.topic.startswith('/global') else SL).append((tt, g.origin.position.x, g.origin.position.y, g.resolution, arr))


def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


def at(L, t):
    k = max(bisect.bisect_right([x[0] for x in L], t) - 1, 0); return L[k][1]


# base_link ← lidar_link (2D)
B2L = (0.0, 0.0, 0.0); f = 'lidar_link'; chain = []
while f in ST and f != 'base_link':
    p, a = ST[f]; chain.append(a); f = p
for a in reversed(chain): B2L = comp(B2L, a)


def grid_near(L, t, lo):
    k = max(bisect.bisect_right([x[0] for x in L], t) - 1, 0); tt, ox, oy, r, A = L[k]
    ys, xs = np.nonzero(A >= lo)
    if not len(xs): return tt, 0, None
    px, py = ox + (xs + 0.5) * r, oy + (ys + 0.5) * r; d = np.hypot(px - gx, py - gy); m = d <= R
    return tt, int(m.sum()), (float(d.min()), float(px[d.argmin()]), float(py[d.argmin()]))


def scan_near(t):
    k = max(bisect.bisect_right([x[0] for x in SC], t) - 1, 0); tt, a0, da, rg = SC[k]
    P = comp(comp(at(MO, tt), at(OB, tt)), B2L); ok = np.isfinite(rg) & (rg > 0.05)
    an = a0 + da * np.arange(len(rg)); x = P[0] + rg * np.cos(P[2] + an); y = P[1] + rg * np.sin(P[2] + an)
    x, y = x[ok], y[ok]; d = np.hypot(x - gx, y - gy); m = d <= R
    return int(m.sum()), (float(d.min()), float(x[d.argmin()]), float(y[d.argmin()])), comp(at(MO, tt), at(OB, tt))


ts = TQ or list(np.arange(10, SC[-1][0], 20.0)) + [SC[-1][0] - 0.5]
print('목표 (%.2f, %.2f) 반경 %.2f m · bag 길이 %.0f s' % (gx, gy, R, SC[-1][0]))
for t in ts:
    _, nl, cl = grid_near(GC, t, 100); _, ni, ci = grid_near(GC, t, 99); _, ns, cs = grid_near(SL, t, 50) if SL else (0, 0, None)
    n, cp, pose = scan_near(t)
    f3 = lambda c: '-' if c is None else '%.2f m @(%.2f, %.2f)' % c
    print('t=%5.1f 로버 (%.2f, %.2f, %4.0f°) | 전역 100(LETHAL) %3d 가장 가까움 %s · ≥99(내접 포함) %3d 가장 가까움 %s | 라이다 점 %3d 가장 가까움 %s'
          % (t, pose[0], pose[1], math.degrees(pose[2]), nl, f3(cl), ni, f3(ci), n, f3(cp)))
