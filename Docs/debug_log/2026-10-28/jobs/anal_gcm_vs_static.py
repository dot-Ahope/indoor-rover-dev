#!/usr/bin/env python3
"""anal_gcm_vs_static — 전역 코스트맵 덤프의 치명(100) 칸을 정적 /map 점유(≥65)와 비교해 문자 격자로(10-28 §16, PC).
  # = 치명이고 정적 지도에도 점유 · N = 치명인데 정적 지도는 빈 칸(센서 층이 넣은 것) · + = 내접 99 · ~ 닿는 칸 · . 그 밖 · @ 로버
  인자: npz x0 x1 y0 y1"""
import sys, collections, numpy as np
D = np.load(sys.argv[1]); g = D['global_costmap_costmap']; ox, oy, r = D['global_costmap_costmap_o']; m = D['map']; mx, my, mr = D['map_o']; R = D['robot']
x0, x1, y0, y1 = map(float, sys.argv[2:6]); H, W = g.shape; ok = g <= 98
s = (int((R[1] - oy) / r), int((R[0] - ox) / r)); seen = np.zeros_like(ok); q = collections.deque([s]); seen[s] = True
while q:
    j, i = q.popleft()
    for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = j + dj, i + di
        if 0 <= a < H and 0 <= b < W and ok[a, b] and not seen[a, b]: seen[a, b] = True; q.append((a, b))
def st(x, y):
    j, i = int((y - my) / mr), int((x - mx) / mr)
    return 0 <= j < m.shape[0] and 0 <= i < m.shape[1] and m[j, i] >= 65
nN = 0
print('x %.2f..%.2f (칸 5 cm) · 로버 (%.2f, %.2f)' % (x0, x1, R[0], R[1]))
for y in np.arange(y1, y0 - 1e-6, -r):
    row = ''
    for x in np.arange(x0, x1 + 1e-6, r):
        j, i = int((y - oy) / r), int((x - ox) / r); v = g[j, i]
        if abs(x - R[0]) < r / 2 + 1e-3 and abs(y - R[1]) < r / 2 + 1e-3: row += '@'
        elif v >= 100: c = '#' if st(x, y) else 'N'; nN += c == 'N'; row += c
        elif v == 99: row += '+'
        elif seen[j, i]: row += '~'
        else: row += '.'
    print('  %+.2f %s' % (y, row))
print('창 안 치명 · 정적 지도엔 빈 칸(N) %d 칸' % nN)
