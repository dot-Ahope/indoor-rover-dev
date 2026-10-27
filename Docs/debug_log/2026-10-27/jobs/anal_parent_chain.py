#!/usr/bin/env python3
"""anal_parent_chain — Smac 탐색 기록에서 '통로 남쪽 노드가 어디를 거쳐 왔나' 를 부모 사슬로 (2026-10-27 §1 ②, PC, 로버 안 움직임).
  입력: exp_<n>.txt(10-26 §22 진단 빌드: 줄 = 칸 x y 방향칸 부모x 부모y) · 장면.npz(원점 · 해상도). 부모는 (x, y) 만 있어 같은 (x, y) 의 방문 노드에 붙임.
  세는 것: 통로 창(x −2.25~−0.95, y −5.85~−3.25) 안 y < −4.9 인 노드마다 출발까지 사슬을 따라가
    · 좁은 곳 창(x −1.85~−1.25, y −4.9~−4.5)을 지났나 · 통로 창 밖으로 나갔다 왔나 · 사슬 길이. 사슬 하나를 그림으로도.
  인자: exp.txt 장면.npz 장면이름 그림.png"""
import sys, math, json
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
E = np.loadtxt(sys.argv[1], ndmin=2); SC = np.load(sys.argv[2]); k = sys.argv[3]
ox, oy, r, _ = SC[k + '/info']; G = SC[k + '/grid'].astype(np.int16)
X, Y = ox + (E[:, 0] + .5) * r, oy + (E[:, 1] + .5) * r
key = lambda a, b: (round(float(a), 4), round(float(b), 4))
idx = {}; dup = 0
for i, (a, b) in enumerate(E[:, :2]):
    kk = key(a, b)
    if kk in idx: dup += 1
    else: idx[kk] = i
WIN = (-2.25, -0.95, -5.85, -3.25); NAR = (-1.85, -1.25, -4.9, -4.5)
inwin = lambda x, y: WIN[0] <= x <= WIN[1] and WIN[2] <= y <= WIN[3]
south = [i for i in range(len(E)) if inwin(X[i], Y[i]) and Y[i] < -4.9]
print('%s: 방문 %d · (x, y) 겹침 %d · 통로 남쪽 노드 %d' % (k, len(E), dup, len(south)))
res = {'좁은 곳 지남': 0, '창 밖으로 돌아옴': 0, '둘 다': 0, '둘 다 아님': 0, '사슬 끊김': 0}; chains = []
for i in south:
    c = [i]; j = i; ok = True
    while E[j, 3] >= 0:
        p = idx.get(key(E[j, 3], E[j, 4]))
        if p is None or p in c[-3:]: ok = False; break
        c.append(p); j = p
        if len(c) > 200000: ok = False; break
    if not ok: res['사슬 끊김'] += 1; continue
    nar = any(NAR[0] <= X[q] <= NAR[1] and NAR[2] <= Y[q] <= NAR[3] for q in c)
    out = any(not inwin(X[q], Y[q]) for q in c)
    res['둘 다' if nar and out else '좁은 곳 지남' if nar else '창 밖으로 돌아옴' if out else '둘 다 아님'] += 1
    chains.append((i, c, nar, out))
print('  사슬 분류:', json.dumps(res, ensure_ascii=False))
if chains:
    L = np.array([len(c) for _, c, _, _ in chains]); print('  사슬 길이(노드) 중앙 %d · 최소 %d · 최대 %d' % (np.median(L), L.min(), L.max()))
    ys = [min(Y[q] for q in c if inwin(X[q], Y[q]) and NAR[0] <= X[q] <= NAR[1]) if any(NAR[0] <= X[q] <= NAR[1] for q in c) else None for _, c, _, _ in chains[:1]]
    # 그림: 지도 전체 + 사슬 몇 개
    fig, ax = plt.subplots(figsize=(9, 8))
    Gs = np.where(G < 0, 50, G)
    ax.imshow(Gs, origin='lower', extent=(ox, ox + G.shape[1] * r, oy, oy + G.shape[0] * r), cmap='Greys', vmin=0, vmax=100, interpolation='nearest')
    ax.scatter(X[::50], Y[::50], s=1, c='#7aa6d6', alpha=0.4)
    pick = sorted(chains, key=lambda q: Y[q[0]])[:: max(1, len(chains) // 6)][:6]
    for n, (i, c, nar, out) in enumerate(pick):
        ax.plot(X[c], Y[c], lw=1.4, label='남쪽 노드 (%.2f, %.2f) 사슬 %d 노드%s%s' % (X[i], Y[i], len(c), ' · 좁은 곳' if nar else '', ' · 창 밖' if out else ''))
    ax.add_patch(plt.Rectangle((WIN[0], WIN[2]), WIN[1] - WIN[0], WIN[3] - WIN[2], fill=False, ec='#c2255c', ls='--', lw=1.2))
    ax.add_patch(plt.Rectangle((NAR[0], NAR[2]), NAR[1] - NAR[0], NAR[3] - NAR[2], fill=False, ec='#e8590c', lw=1.5))
    ax.set_aspect('equal'); ax.legend(fontsize=7.5, loc='upper right'); ax.set_title('%s 탐색: 통로 남쪽 노드의 부모 사슬(분홍 점선 = 통로 창, 주황 = 좁은 곳 창, 하늘색 점 = 방문 노드 1/50)' % k, fontsize=10, loc='left')
    fig.tight_layout(); fig.savefig(sys.argv[4], dpi=110); print('  저장', sys.argv[4])
