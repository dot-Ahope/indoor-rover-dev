#!/usr/bin/env python3
"""anal_f2o1_options — f2o1 정지(상자 옆 4.8 cm)에 대한 대책 후보의 사전 평가 3 가지. (2026-10-13 §5, 오늘만 쓰는 분석 — 로버 안 움직임)
  A. 전역 경로(/plan)와 다듬은 경로(/plan_smoothed) 중 어느 쪽이 상자에 더 가까웠나 — 스무더가 모서리를 깎았는지.
  B. 기록된 전역 코스트맵의 치명 칸에서 inflation 을 다시 계산해(반경 r · 감쇠 k 를 바꿔 가며) 격자 최단 비용 경로를 다시 그리면 상자와의 거리가 얼마나 달라지나.
     계획기 흉내: 8 방향 Dijkstra, 칸 비용 = 50 + 0.8 × inflation 비용(NavFn 의 COST_NEUTRAL·COST_FACTOR), 치명·내접 칸은 통과 불가. NavFn 과 똑같지는 않다(검증: 현재 값으로 기록된 경로와 비교).
  C. 정지 자세에서 조금 움직인 자세(직후진·전진·제자리 회전)의 풋프린트 둘레 최대 비용 — 어느 움직임이 '충돌 아님'이었나(탈출 수단 평가).
  사용: anal_f2o1_options.py bag 정지HH:MM:SS 계획시각HH:MM:SS"""
import sys, time, math, heapq, os
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools'))
from anal_box_history import load, near, grid, FP
bag, hstop, hplan = sys.argv[1:4]
D, ob, mo = load(bag, ['/local_costmap/costmap', '/global_costmap/costmap', '/plan', '/plan_smoothed'])
day = time.strftime('%Y-%m-%d ', time.localtime(ob[0][0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); tS, tP = ep(hstop), ep(hplan)
PAD = 0.01; FPP = FP + np.sign(FP) * PAD; RINS = 0.165 + PAD


def clear_pts(pb): return np.hypot(np.maximum.reduce([FP[:, 0].min() - pb[:, 0], np.zeros(len(pb)), pb[:, 0] - FP[:, 0].max()]), np.maximum.reduce([FP[:, 1].min() - pb[:, 1], np.zeros(len(pb)), pb[:, 1] - FP[:, 1].max()]))
# 상자 끝(정지 때 로컬 코스트맵에서 차체에 가장 가까운 치명 칸의 연결 덩어리) → 지도 좌표
ts, m = min(D['/local_costmap/costmap'], key=lambda x: abs(x[0] - tS)); ox, oy, res, G = grid(m); Mob = near(ob, ts); Mmo = near(mo, ts)
L = np.argwhere(G >= 100); Lo = np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res, np.ones(len(L))]; d = clear_pts((np.linalg.inv(Mob) @ Lo.T).T)
lab, _ = ndimage.label(G >= 100, structure=np.ones((3, 3))); sel = lab[L[:, 0], L[:, 1]] == lab[L[int(np.argmin(d)), 0], L[int(np.argmin(d)), 1]]; BOX = (Mmo @ Lo[sel].T).T[:, :2]
dbox = lambda xy: np.hypot(xy[:, None, 0] - BOX[None, :, 0], xy[:, None, 1] - BOX[None, :, 1]).min() if len(xy) else float('nan')
P = lambda msg: np.array([[q.pose.position.x, q.pose.position.y] for q in msg.poses])

print('== A. 전역 경로 대 다듬은 경로 — 상자 끝까지 가장 가까운 거리(m)')
print('  시각      /plan   /plan_smoothed(그 직후 것)')
for tp, pm in D['/plan']:
    if tp < tS - 35 or tp > tS + 2: continue
    sm = [x for x in D['/plan_smoothed'] if tp <= x[0] < tp + 1.5]
    print('  %s   %.3f   %s' % (time.strftime('%H:%M:%S', time.localtime(tp)), dbox(P(pm)), '%.3f' % dbox(P(sm[0][1])) if sm else '없음(스무더 실패 → 원경로 사용)'))

print('\n== B. inflation 을 바꿔 경로를 다시 그리면(계획 시각 %s 의 전역 코스트맵, 출발 = 그때 로버 위치, 도착 = 목표 3 (0, 0))' % hplan)
tg, gm = [x for x in D['/global_costmap/costmap'] if x[0] <= tP][-1]; gx, gy, gres, GG = grid(gm); leth = GG >= 100
dist = ndimage.distance_transform_edt(~leth) * gres; Mmb = near(mo, tP) @ near(ob, tP); s = (int((Mmb[1, 2] - gy) / gres), int((Mmb[0, 2] - gx) / gres)); g = (int((0 - gy) / gres), int((0 - gx) / gres))
print('  전역 코스트맵 %s, 상자 끝 자리 치명 %d / %d 칸, 출발 지도 (%.2f, %.2f)' % (time.strftime('%H:%M:%S', time.localtime(tg)), int(leth[((BOX[:, 1] - gy) / gres).astype(int), ((BOX[:, 0] - gx) / gres).astype(int)].sum()), len(BOX), Mmb[0, 2], Mmb[1, 2]))
rec = [x for x in D['/plan'] if x[0] >= tP][0]; print('  기록된 경로(%s): 상자 끝까지 %.3f m, 길이 %.2f m' % (time.strftime('%H:%M:%S', time.localtime(rec[0])), dbox(P(rec[1])), np.hypot(*np.diff(P(rec[1]), axis=0).T).sum()))


def plan(r, k):
    c = np.where(dist <= RINS, 253.0, np.where(dist <= r, 252.0 * np.exp(-k * (dist - RINS)), 0.0)); c[leth] = 254; cost = 50 + 0.8 * c; block = c >= 253
    H, W = c.shape; best = np.full((H, W), np.inf); prev = {}; best[s] = 0; pq = [(0.0, s)]
    nb = [(-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
    while pq:
        dcur, u = heapq.heappop(pq)
        if u == g: break
        if dcur > best[u]: continue
        for di, dj, w in nb:
            v = (u[0] + di, u[1] + dj)
            if not (0 <= v[0] < H and 0 <= v[1] < W) or (block[v] and v != g): continue
            nd = dcur + w * cost[v]
            if nd < best[v]: best[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if g not in prev: return None
    path = [g]
    while path[-1] != s: path.append(prev[path[-1]])
    xy = np.array([[gx + (j + 0.5) * gres, gy + (i + 0.5) * gres] for i, j in path[::-1]]); return xy, c


print('  반경 r · 감쇠 k   상자 끝까지 최소 거리   그때 차체 옆 여유(= 거리 − 반폭 0.165, 칸 중심 기준)   경로 길이   경로 위 최대 비용')
RINS0 = RINS
for r, k, pad in ((0.70, 2.0, 0.01), (0.70, 1.0, 0.01), (0.70, 3.0, 0.01), (0.70, 5.0, 0.01), (1.00, 2.0, 0.01), (1.00, 3.0, 0.01), (0.70, 2.0, 0.05), (0.70, 3.0, 0.05), (0.70, 2.0, 0.08), (0.70, 3.0, 0.08), (0.80, 3.0, 0.10), (0.80, 3.0, 0.15)):
    RINS = 0.165 + pad; o = plan(r, k)
    if o is None: print('  패딩 %.2f | %.2f · %.1f   경로 없음' % (pad, r, k)); continue
    xy, c = o; ij = (((xy[:, 1] - gy) / gres).astype(int), ((xy[:, 0] - gx) / gres).astype(int))
    print('  패딩 %.2f | %.2f · %.1f%s      %.3f m                %5.1f cm                                              %.2f m      %3.0f' % (pad, r, k, ' (현재)' if (r, k, pad) == (0.70, 2.0, 0.01) else '       ', dbox(xy), (dbox(xy) - 0.165) * 100, np.hypot(*np.diff(xy, axis=0).T).sum(), c[ij][3:-3].max()))

print('\n== C. 정지 자세에서 움직여 본 자세의 풋프린트 둘레 최대 비용(로컬 코스트맵 %s, 100 = 치명 · 99 = 내접)' % time.strftime('%H:%M:%S', time.localtime(ts)))
def edge(Pg, step=0.01):
    o = []
    for i in range(4):
        a, b = Pg[i], Pg[(i + 1) % 4]; n = max(int(np.linalg.norm(b - a) / step), 1); o.append(a + (b - a) * np.linspace(0, 1, n, endpoint=False)[:, None])
    return np.vstack(o)
E = edge(FPP)
def fcost(dx, dth, snap=G):
    c_, s_ = math.cos(dth), math.sin(dth); Mv = np.array([[c_, -s_, dx], [s_, c_, 0], [0, 0, 1]]); W = (Mob @ Mv @ np.c_[E, np.ones(len(E))].T).T
    return int(snap[((W[:, 1] - oy) / res).astype(int), ((W[:, 0] - ox) / res).astype(int)].max())
print('  직후진 거리(cm):   ' + '  '.join('%d→%d' % (b, fcost(-b / 100, 0)) for b in (0, 2, 4, 6, 8, 10, 15, 20, 30)))
print('  직전진 거리(cm):   ' + '  '.join('%d→%d' % (b, fcost(b / 100, 0)) for b in (2, 4, 6, 8, 10, 15, 20)))
print('  제자리 회전(°, +왼쪽): ' + '  '.join('%+d→%d' % (a, fcost(0, math.radians(a))) for a in (-40, -30, -20, -10, -5, 5, 10, 20, 30, 40)))
print('  후진 10 cm 뒤 회전(°): ' + '  '.join('%+d→%d' % (a, max(fcost(-0.10, 0), fcost(-0.10, math.radians(a)))) for a in (-40, -20, -10, 10, 20, 40)))
def funk(dx, dth):
    c_, s_ = math.cos(dth), math.sin(dth); Mv = np.array([[c_, -s_, dx], [s_, c_, 0], [0, 0, 1]]); W = (Mob @ Mv @ np.c_[E, np.ones(len(E))].T).T
    return int((G[((W[:, 1] - oy) / res).astype(int), ((W[:, 0] - ox) / res).astype(int)] < 0).sum())
print('  미확인(−1) 칸에 걸린 둘레 표본 수 — 현재 %d · 후진 10 cm %d · 후진 20 cm %d · 전진 10 cm %d | 로컬 코스트맵 전체의 미확인 칸 %d 개' % (funk(0, 0), funk(-0.1, 0), funk(-0.2, 0), funk(0.1, 0), int((G < 0).sum())))
print('  (같은 자세를 정지 뒤 6 s 동안의 로컬 코스트맵 전부로 다시 본 현재 자세 비용: %s)' % ' '.join(str(fcost(0, 0, grid(mm)[3])) for tt, mm in D['/local_costmap/costmap'] if tS - 3 <= tt <= tS + 6 and grid(mm)[3].shape == G.shape and abs(grid(mm)[0] - ox) < 1e-6 and abs(grid(mm)[1] - oy) < 1e-6))
