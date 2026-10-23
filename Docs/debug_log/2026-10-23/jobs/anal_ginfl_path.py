#!/usr/bin/env python3
"""anal_ginfl_path — 전역 inflation 감쇠(cost_scaling_factor)를 바꾸면 복귀 경로가 실제 상자에서 얼마나 떨어지나(2026-10-23 §1, PC, 로버 안 움직임).
  왜: 10-22 §22 사용자 제안 — 경로가 상자 쪽 주황(높은 팽창 비용) 띠를 따라 실제 여유 1.1 cm 로 지나감. 노랑(낮은 비용) 쪽을 따르게 하면?
  방법(10-13 §5.2 B 와 같은 계획기 흉내): 그 시각 기록된 /global_costmap/costmap 의 치명 칸(값 100)에서 inflation 을 다시 계산
    (반경 r, 감쇠 k, 내접 0.175 = 반폭 0.165 + 패딩 0.01), 비용 0~252 → 칸 비용 50 + 0.8 × inflation(NavFn COST_NEUTRAL · COST_FACTOR),
    내접 이상 통과 불가, 8 방향 Dijkstra. 출발 = 그 시각 로버 지도 위치, 도착 = 목표 3 (0, 0).
  검증: 같은 시각 직후 기록된 /plan 의 실제 상자까지 거리와 k 2.0 흉내를 견줌.
  인자: bag 시각들(s, bag 시작 기준, 쉼표) [감쇠들=2,3,4,5]"""
import sys, math, heapq, bisect
from pathlib import Path
import numpy as np
from scipy import ndimage
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = sys.argv[1]; TQ = [float(v) for v in sys.argv[2].split(',')]; KS = [float(v) for v in (sys.argv[3] if len(sys.argv) > 3 else '2,3,4,5').split(',')]
BOX = (1.151, 1.261, -0.20, -0.02); R = 0.70; RINS = 0.165 + 0.01
BOXP = np.array([[x, y] for x in np.linspace(BOX[0], BOX[1], 12) for y in np.linspace(BOX[2], BOX[3], 19)])
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, GC, PL = [], [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/global_costmap/costmap', '/plan')]):
        tt = t * 1e-9 - T0; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
        elif c.topic == '/plan': PL.append((tt, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
        else:
            g = m.info; GC.append((tt, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, np.int16).reshape(g.height, g.width)))
for L in (MO, OB): L.sort(key=lambda q: q[0])
at = lambda L, t: L[max(bisect.bisect_right([q[0] for q in L], t) - 1, 0)][1]
dbox = lambda xy: float(np.min(np.hypot(xy[:, None, 0] - BOXP[None, :, 0], xy[:, None, 1] - BOXP[None, :, 1]))) if len(xy) else float('nan')
near_len = lambda xy: float(np.sum(np.hypot(*np.diff(xy, axis=0).T)[np.min(np.hypot(xy[1:, None, 0] - BOXP[None, :, 0], xy[1:, None, 1] - BOXP[None, :, 1]), axis=1) < 0.40])) if len(xy) > 1 else 0.0
plen = lambda xy: float(np.hypot(*np.diff(xy, axis=0).T).sum())
print('bag %s · 반경 %.2f · 내접 %.3f · 실제 상자 x %.3f~%.3f y %.2f~%.2f · 여유 = 경로 ↔ 실제 상자 − 반폭 0.165' % (Path(bag).name, R, RINS, *BOX))
for tq in TQ:
    tg, gx, gy, gres, GG = [q for q in GC if q[0] <= tq][-1]; leth = GG >= 100
    p = comp(at(MO, tq), at(OB, tq)); s = (int((p[1] - gy) / gres), int((p[0] - gx) / gres)); g = (int((0 - gy) / gres), int((0 - gx) / gres))
    dist = ndimage.distance_transform_edt(~leth) * gres
    bi = (((BOXP[:, 1] - gy) / gres).astype(int), ((BOXP[:, 0] - gx) / gres).astype(int)); nbox = int(np.unique(np.ravel_multi_index(bi, GG.shape)[leth[bi]]).size)
    rec = [q for q in PL if q[0] >= tq]
    print('\n t %.1f s(전역 코스트맵 t %.1f) · 로버 (%.2f, %.2f, %.0f°) · 실제 상자 자리 치명 칸 %d' % (tq, tg, p[0], p[1], math.degrees(p[2]), nbox))
    if rec:
        xy = rec[0][1]; print('   기록된 /plan(t %.1f): 실제 상자까지 %.3f m · 여유 %+5.1f cm · 길이 %.2f m · 상자 0.4 m 안 %.2f m' % (rec[0][0], dbox(xy), 100 * (dbox(xy) - 0.165), plen(xy), near_len(xy)))
    for k in KS:
        c = np.where(dist <= RINS, 253.0, np.where(dist <= R, 252.0 * np.exp(-k * (dist - RINS)), 0.0)); c[leth] = 254; cost = 50 + 0.8 * c; block = c >= 253
        H, W = c.shape; best = np.full((H, W), np.inf); prev = {}; best[s] = 0; pq = [(0.0, s)]
        nb = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
        while pq:
            dcur, u = heapq.heappop(pq)
            if u == g: break
            if dcur > best[u]: continue
            for di, dj, w in nb:
                v = (u[0] + di, u[1] + dj)
                if not (0 <= v[0] < H and 0 <= v[1] < W) or (block[v] and v != g and v != s): continue
                nd = dcur + w * cost[v]
                if nd < best[v]: best[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
        if g not in prev: print('   k %.1f: 경로 없음' % k); continue
        path = [g]
        while path[-1] != s: path.append(prev[path[-1]])
        xy = np.array([[gx + (j + 0.5) * gres, gy + (i + 0.5) * gres] for i, j in path[::-1]])
        print('   흉내 k %.1f%s: 실제 상자까지 %.3f m · 여유 %+5.1f cm · 길이 %.2f m · 상자 0.4 m 안 %.2f m' % (k, ' (현재)' if k == 2.0 else '      ', dbox(xy), 100 * (dbox(xy) - 0.165), plen(xy), near_len(xy)))
