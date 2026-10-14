#!/usr/bin/env python3
"""anal_navfn_replay — 발행된 전역 코스트맵 위에서 NavFn 과 같은 비용 변환으로 다익스트라 최단 경로를 다시 구해, bag 의 /plan 과 견준다. (2026-10-14 §24, 오늘만)
  왜: f2u2 16:30:06.6 /plan 이 전역 내접 칸(99 = 253)을 50 cm 연속 지났다. NavFn(humble 소스)은 253 이상을 장애물로 두므로 그럴 수 없다.
      (1) 그 시각 지도에 내접을 피해 목표로 가는 길이 있었나, (2) 있었다면 그 길과 실제 /plan 이 어떻게 다른가.
  비용 변환(navfn.cpp setCostmap): 253 이상 = 장애물, 255(미지) = allow_unknown 이면 253, 그 외 50 + 0.8 × 원가(최대 253).
        OccupancyGrid 값 → 원가: 0 → 0, 1~98 → 1 + (v − 1) × 251 / 97(발행 변환의 역), 99 → 253, 100 → 254, −1 → 255.
  한계: NavFn 은 퍼텐셜(2 차 보간 전파) + 기울기 따라가기라 정확히 같은 경로는 아니다 — 8-연결 다익스트라로 '같은 비용 장에서 가능한 길'만 본다.
  인자: bag HH:MM:SS.f 목표x 목표y"""
import sys, time, math, heapq
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, hh, gx, gy = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]); hms, _, fr = hh.partition('.')
gc = None; plan = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/plan')]):
        ts = t / 1e9
        if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/plan':
            if ts >= T - 0.05: plan = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]); break
        elif ts <= T + 0.05: gc = m
g = np.array(gc.data, np.int16).reshape(gc.info.height, gc.info.width); r = gc.info.resolution; ox, oy = gc.info.origin.position.x, gc.info.origin.position.y
raw = np.where(g == 0, 0, np.where(g == 99, 253, np.where(g == 100, 254, np.where(g < 0, 255, 1 + (g - 1) * 251.0 / 97))))
cost = np.where(raw >= 253, np.inf, 50 + 0.8 * raw); cost = np.where(raw == 255, 253.0, cost)
cell = lambda x, y: (int((y - oy) / r), int((x - ox) / r))
s = cell(plan[0, 0], plan[0, 1]); e = cell(gx, gy)
print('시작 칸 원가 %.0f · 목표 칸 원가 %.0f' % (raw[s], raw[e]))
cost[s] = 50.0   # nav2 navfn 은 시작(로봇) 칸을 비움
D = np.full(g.shape, np.inf); D[s] = 0; P = {}; pq = [(0.0, s)]
while pq:
    d, u = heapq.heappop(pq)
    if d > D[u]: continue
    if u == e: break
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if not dx and not dy: continue
            v = (u[0] + dy, u[1] + dx)
            if not (0 <= v[0] < g.shape[0] and 0 <= v[1] < g.shape[1]) or not np.isfinite(cost[v]): continue
            nd = d + cost[v] * (1.4142 if dx and dy else 1.0)
            if nd < D[v]: D[v] = nd; P[v] = u; heapq.heappush(pq, (nd, v))
if not np.isfinite(D[e]): print('내접(253 이상)을 피해서는 목표에 닿는 길이 없다'); sys.exit()
path = [e]
while path[-1] != s: path.append(P[path[-1]])
path = path[::-1]; xy = np.array([[ox + (c_ + 0.5) * r, oy + (r_ + 0.5) * r] for r_, c_ in path])
acc = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]; k = min(int(np.searchsorted(acc, 0.3)), len(xy) - 1)
print('다익스트라(내접 회피) 길이 %.2f m · 0.3 m 앞 방향 %+.0f° · 지나는 칸 원가 최대 %.0f' % (acc[-1], math.degrees(math.atan2(xy[k, 1] - xy[0, 1], xy[k, 0] - xy[0, 0])), max(raw[p] for p in path)))
pa = np.r_[0, np.cumsum(np.hypot(*np.diff(plan, axis=0).T))]; k2 = min(int(np.searchsorted(pa, 0.3)), len(plan) - 1)
pr = [raw[cell(p[0], p[1])] for p in plan]
print('bag /plan          길이 %.2f m · 0.3 m 앞 방향 %+.0f° · 지나는 칸 원가 최대 %.0f · 253 이상 점 %d/%d' % (pa[-1], math.degrees(math.atan2(plan[k2, 1] - plan[0, 1], plan[k2, 0] - plan[0, 0])), max(pr), sum(v >= 253 for v in pr), len(pr)))
print('다익스트라 경로 처음 1 m(0.1 m 마다):', ' '.join('(%.2f,%.2f)' % tuple(xy[min(int(np.searchsorted(acc, q)), len(xy) - 1)]) for q in np.arange(0, 1.01, 0.1)))
print('bag /plan 처음 1 m(0.1 m 마다):     ', ' '.join('(%.2f,%.2f)' % tuple(plan[min(int(np.searchsorted(pa, q)), len(plan) - 1)]) for q in np.arange(0, 1.01, 0.1)))
