#!/usr/bin/env python3
"""anal_path_center — 서쪽 통로 목표(출발점) x 를 바꾸면 남서로 가는 계획 경로가 상자 옆을 얼마나 띄워 지나는지, 기록된 전역 코스트맵으로 다시 계산. (2026-10-15 §9, 오늘만)
  왜: 대책 1(사용자 결정) — 서쪽 통로 목표를 통로 가운데로. 통로 가운데선이 꺾여(북쪽 −1.83, 남쪽 출구 −1.56) 목표만 옮겨서는 상자 옆에서 다시 동쪽으로 붙을 수 있다.
        전역 감쇠(cost_scaling)는 10-13 §5 에서 2.0 → 3.0 이 5 cm 밖에 못 옮겨 되돌렸으므로 참고로만 함께 본다.
  방법: 전역 코스트맵 한 장(OccupancyGrid → 원가 역변환) — 치명(254)은 그대로 두고, inflation 은 치명 칸에서 거리로 다시 계산(반경 0.70, 감쇠 값을 바꿔 가며; 내접 반경 0.175).
        NavFn 비용 변환(253 이상 장애물, 50 + 0.8 × 원가) 8-연결 다익스트라. 출발 = (x0, −3.70), 목표 = (−1.60, −5.50).
        경로가 y −3.90 ~ −4.40(상자 옆) 에서 지나는 x 와, 차체(반폭 0.175) 동쪽 끝 → 상자 앞면(카메라 안쪽 줄, 사용자 확인 x ≈ −1.43)까지 · 서쪽 끝 → 서쪽 벽(라이다 x ≈ −2.23)까지 여유.
  한계: NavFn 은 퍼텐셜 + 기울기 따라가기라 정확히 같지 않다(경향만). 전역 지도에 상자가 카메라로 찍혀 있는지는 그 시각 지도에 달렸다.
  인자: bag HH:MM:SS.f"""
import sys, time, math, heapq
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, hh = sys.argv[1:3]; hms, _, fr = hh.partition('.')
gc = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/global_costmap/costmap']):
        ts = t / 1e9
        if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
        if ts > T + 0.05: break
        gc = rd.deserialize(raw, c.msgtype)
g = np.array(gc.data, np.int16).reshape(gc.info.height, gc.info.width); r = gc.info.resolution; ox, oy = gc.info.origin.position.x, gc.info.origin.position.y
leth = g >= 100
dist = distance_transform_edt(~leth) * r   # 칸 중심 사이 거리(근사)
cell = lambda x, y: (int((y - oy) / r), int((x - ox) / r))
def raw_cost(scaling):
    if scaling is None:   # 기록된 그대로(발행값 역변환)
        return np.where(g == 0, 0, np.where(g == 99, 253, np.where(g == 100, 254, np.where(g < 0, 255, 1 + (g - 1) * 251.0 / 97))))
    c = np.where(dist <= 0, 254, np.where(dist <= 0.175, 253, np.where(dist <= 0.70, np.floor(252 * np.exp(-scaling * (dist - 0.175))), 0)))
    return np.where(g < 0, 255, c)
def plan(raw, s, e):
    cost = np.where(raw >= 253, np.inf, 50 + 0.8 * raw); cost = np.where(raw == 255, 253.0, cost); cost[s] = 50.0
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
    if not np.isfinite(D[e]): return None
    path = [e]
    while path[-1] != s: path.append(P[path[-1]])
    return np.array([[ox + (c_ + 0.5) * r, oy + (r_ + 0.5) * r] for r_, c_ in path[::-1]])
BOX, WWALL, HW = -1.43, -2.23, 0.175
e = cell(-1.60, -5.50)
print('전역 코스트맵 %s (%d×%d, %.2f m) · 상자 옆 구간 y −3.90~−4.40 · 상자 앞면 x %.2f · 서쪽 벽 x %.2f' % (hh, g.shape[1], g.shape[0], r, BOX, WWALL))
print('출발 x   감쇠       상자 옆 경로 x(최소~최대)   동쪽 여유(차체→상자) 최소   서쪽 여유 최소   y −4.60 출구 x')
for sc in (None, 3.0, 5.0):
    raw = raw_cost(sc)
    for x0 in (-1.65, -1.75, -1.80, -1.85):
        p = plan(raw, cell(x0, -3.70), e)
        if p is None: print('%+.2f   %-8s 경로 없음' % (x0, '기록값' if sc is None else sc)); continue
        k = (p[:, 1] <= -3.90) & (p[:, 1] >= -4.40); xs = p[k, 0]
        ex = p[np.argmin(np.abs(p[:, 1] + 4.60)), 0]
        print('%+.2f   %-8s %+.3f ~ %+.3f               %5.1f cm                    %5.1f cm        %+.3f' % (x0, '기록값(2.0)' if sc is None else '%.1f' % sc, xs.min(), xs.max(), 100 * (BOX - (xs.max() + HW)), 100 * ((xs.min() - HW) - WWALL), ex))
