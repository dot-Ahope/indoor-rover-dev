#!/usr/bin/env python3
"""chk_replan_maps — §28 f2tt1 15:58:11.40 북행 재계획: 실주행 Smac 은 성공, 오프라인 재질의는 실패 — 지도 판마다 무엇이 다른가 (2026-10-27, PC).
  15:58:07~15:58:14 의 전역 코스트맵(발행본) 판마다:
    · 출발 자세(15:58:11.40 map→base_link)의 중심 칸 값 · 차체 외곽 칸 최대 값 (Smac: 중심 ≥ 99(내접 253) 이면 충돌 · 외곽은 100(254) 이면 충돌)
    · 실주행 Smac 경로(/plan 15:58:11.40 직후, 점 간격 > 0.04)가 지나는 칸 중 99 · 100 칸 수와 처음 걸리는 점
    · PathBlockedAhead 가 본 (-1.60, -4.70) 칸 값
  인자: bag폴더"""
import sys, math, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
day = '2026-10-27 '; T = lambda s: time.mktime(time.strptime(day + s[:8], '%Y-%m-%d %H:%M:%S')) + float(s[8:] or 0)
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
GM, PL, mo, ob = [], [], [], []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/plan', '/tf')]):
        ts = t * 1e-9
        if not T('15:58:05') <= ts <= T('15:58:15'): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (ts, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(v)
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(v)
        elif c.topic == '/plan':
            P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]); PL.append((ts, P))
        else:
            i = m.info; GM.append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
def pose(t):
    a = min(mo, key=lambda x: abs(x[0] - t)); b = min(ob, key=lambda x: abs(x[0] - t)); c, s = math.cos(a[3]), math.sin(a[3])
    return a[1] + c * b[1] - s * b[2], a[2] + s * b[1] + c * b[2], a[3] + b[3]
t0 = T('15:58:11.40'); sx, sy, sa = pose(t0)
live = [p for p in PL if p[0] >= t0 - 0.05 and len(p[1]) > 3 and np.median(np.hypot(*np.diff(p[1], axis=0).T)) > 0.04][0]
print('출발 자세(15:58:11.40) map (%.3f, %.3f, %.1f°) · 실주행 Smac 경로 %s 점 %d' % (sx, sy, math.degrees(sa), hs(live[0]), len(live[1])))
# 경로를 2 cm 간격으로 촘촘히
P = live[1]; seg = np.hypot(*np.diff(P, axis=0).T); L = np.r_[0, np.cumsum(seg)]; s = np.arange(0, L[-1], 0.02)
PP = np.c_[np.interp(s, L, P[:, 0]), np.interp(s, L, P[:, 1])]
c, sn = math.cos(sa), math.sin(sa); edge = []
for (x0, y0), (x1, y1) in zip(FP, np.roll(FP, -1, axis=0)):
    for u in np.linspace(0, 1, 15): edge.append((x0 + u * (x1 - x0), y0 + u * (y1 - y0)))
E = np.array(edge); EW = np.c_[sx + c * E[:, 0] - sn * E[:, 1], sy + sn * E[:, 0] + c * E[:, 1]]
for ts, G, ox, oy, r in GM:
    v = lambda x, y: int(G[int((y - oy) / r), int((x - ox) / r)])
    cen = v(sx, sy); fpm = max(v(x, y) for x, y in EW)
    pv = np.array([v(x, y) for x, y in PP]); k99 = np.nonzero(pv >= 99)[0]
    first = ('처음 %.2f m 지점 (%.2f, %.2f) 값 %d' % (s[k99[0]], PP[k99[0], 0], PP[k99[0], 1], pv[k99[0]])) if len(k99) else '없음'
    print('%s 판 | 출발 중심 %d · 차체 외곽 최대 %d | 실주행 경로 위 99 칸 %d · 100 칸 %d (%s) | (-1.60,-4.70) 값 %d' % (
        hs(ts), cen, fpm, int((pv == 99).sum()), int((pv == 100).sum()), first, v(-1.60, -4.70)))
