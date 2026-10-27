#!/usr/bin/env python3
"""fig_smac_expansion_tol — (v2 에서 갈라짐, 2026-10-27 §7) 같은 순간 16:11:56.85 남행을 허용 · cp 만 바꾼 세 판으로: 기준 tol 0.25 · cp 3.0 실패 / tol 0.35 · cp 3.0 성공 / tol 0.25 · cp 1.5 성공.
  인자: 결과0.npz 장면.npz exp0폴더 결과1.npz exp1폴더 결과2.npz exp2폴더 영상.mp4 마지막장.png
  (아래는 v2 설명)
  fig_smac_expansion_v2 — Smac 탐색이 자라는 영상, 같은 일끼리 비교하도록 다시 짬 (2026-10-27 §3, PC, 로버 안 움직임).
  왜: 사용자 — 10-26 영상(smac_expansion_fail_vs_ok.mp4)은 왼쪽 남행(목표 4) 실패와 오른쪽 북행(목표 5) 성공을 붙여 같은 일이 아니었음.
  mode north: 북행(목표 5 (−1.65, −3.70, 82°)) 세 순간 — 16:12:35.21 실패 · 16:12:59.54 실패(남쪽 끝 출발) · 16:13:08.65 성공(좁은 곳 바로 남쪽 · 북향 출발).
  mode south: 남행(목표 4 (−1.60, −5.50, −100°)) 16:11:56.85 실패 하나 — 끝에서 목표에 가장 가까이 간 방문 노드와 그 부모 사슬(출발까지)을 표시.
  입력: 10-26 §22 진단 빌드 결과(result_expdbg.npz · scenes_expdbg.npz · exp_expdbg.tgz 를 푼 exp 폴더; exp_<n> = 장면 순서 115653 · 121553 · 122202 · 123521 · 125954 · 130865).
  세계 좌표 = 원점 + (칸 + 0.5) × 해상도, 방향 = 칸 × 5°(1.1.20 utils.hpp getWorldCoords).
  인자: 결과.npz 장면.npz exp폴더 mode(north|south) 영상.mp4 [마지막장.png]"""
import sys, json, math, subprocess, tempfile, shutil
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
R = np.load(sys.argv[1]); SC = np.load(sys.argv[2]); EXP = Path(sys.argv[3]); VID, LAST = sys.argv[8], sys.argv[9]
meta = json.loads(str(SC['meta'])); V = 'Smac_R10_C30_A10_RS'; order = [m['name'] for m in meta]
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
TIME = {'sa3_115653': '16:11:56.85', 'sa3_121553': '16:12:15.53', 'sa3_122202': '16:12:22.02', 'sa3_123521': '16:12:35.21', 'sa3_125954': '16:12:59.54', 'sa3_130865': '16:13:08.65'}
WHERE = {'sa3_115653': '통로 북쪽 입구 출발', 'sa3_123521': '남쪽 끝 출발(-102°)', 'sa3_125954': '남쪽 끝 출발(-183°)', 'sa3_130865': '좁은 곳 바로 남쪽 · 북향 출발'}
XL, YL = (-2.25, -0.95), (-5.85, -3.25)
cmap = ListedColormap(np.r_[np.linspace([1, 1, 1], [0.78, 0.80, 0.84], 99), [[0.45, 0.47, 0.52]], [[0.08, 0.09, 0.11]], [[0.98, 0.95, 0.80]]])
fp = lambda x, y, a: np.c_[x + math.cos(a) * FP[:, 0] - math.sin(a) * FP[:, 1], y + math.sin(a) * FP[:, 0] + math.cos(a) * FP[:, 1]]


def load(k):
    i = order.index(k); ox, oy, r, _ = SC[k + '/info']
    G = R[k + '/recon'].astype(np.int16) if k + '/recon' in R else SC[k + '/grid'].astype(np.int16); G = np.where(G < 0, 101, G)
    E = np.loadtxt(EXP / ('exp_%d.txt' % i), ndmin=2)
    W = np.c_[ox + (E[:, 0] + .5) * r, oy + (E[:, 1] + .5) * r, np.radians(E[:, 2] * 5.0), ox + (E[:, 3] + .5) * r, oy + (E[:, 4] + .5) * r]
    sp = R['%s/%s/path' % (k, V)] if '%s/%s/path' % (k, V) in R else np.zeros((0, 3))
    return dict(k=k, info=(ox, oy, r), G=G, E=E, W=W, sp=sp, st=SC[k + '/start'], gl=SC[k + '/goal'])


def nearest_chain(d):
    """목표에 가장 가까운 방문 노드와 출발까지의 부모 사슬(부모는 (x, y) 로만 기록 → 같은 (x, y) 방문 노드에 붙임)."""
    E, W, g = d['E'], d['W'], d['gl']
    dist = np.hypot(W[:, 0] - g[0], W[:, 1] - g[1]); i = int(np.argmin(dist))
    idx = {}
    for j, (a, b) in enumerate(E[:, :2]): idx.setdefault((round(float(a), 4), round(float(b), 4)), j)
    c = [i]
    while E[c[-1], 3] >= 0 and len(c) < 10000:
        p = idx.get((round(float(E[c[-1], 3]), 4), round(float(E[c[-1], 4]), 4)))
        if p is None or p == c[-1]: break
        c.append(p)
    return i, float(dist[i]), c


def draw(ax, d, n, title, tcolor, chain=None):
    ox, oy, r = d['info']; G, W = d['G'], d['W']
    ax.imshow(G, origin='lower', extent=(ox, ox + G.shape[1] * r, oy, oy + G.shape[0] * r), cmap=cmap, vmin=0, vmax=101, interpolation='nearest')
    n = min(n, len(W)); Wn = W[:n]
    if n:
        m = Wn[:, 3] > ox
        ax.plot(np.c_[Wn[m, 3], Wn[m, 0], np.full(m.sum(), np.nan)].ravel(), np.c_[Wn[m, 4], Wn[m, 1], np.full(m.sum(), np.nan)].ravel(), color='#2f6fb3', lw=0.5, alpha=0.5)
        ax.scatter(Wn[:, 0], Wn[:, 1], c=np.arange(n), cmap='viridis', s=6, zorder=3, vmin=0, vmax=max(len(W), 1))
    if len(d['sp']) and n >= len(W): ax.plot(d['sp'][:, 0], d['sp'][:, 1], color='#0f9d58', lw=2.6, zorder=5)
    if chain is not None:
        i, dd, c = chain; ax.plot(W[c, 0], W[c, 1], color='#e8590c', lw=2.4, zorder=5)
        ax.add_patch(Polygon(fp(*W[i, :3]), closed=True, fc='#e8590c', ec='#e8590c', alpha=0.25, lw=1.5, zorder=5))
        ax.plot(*W[i, :2], 'o', color='#e8590c', ms=7, zorder=8)
    st, gl = d['st'], d['gl']
    ax.add_patch(Polygon(fp(*st), closed=True, fc='#1c7ed6', ec='#1c7ed6', alpha=0.35, lw=1.5, zorder=6))
    ax.annotate('', xy=(st[0] + 0.18 * math.cos(st[2]), st[1] + 0.18 * math.sin(st[2])), xytext=(st[0], st[1]), arrowprops=dict(arrowstyle='->', color='#1c7ed6', lw=1.8), zorder=7)
    ax.add_patch(Polygon(fp(*gl), closed=True, fc='none', ec='#c2255c', ls='--', lw=1.4, zorder=6))
    ax.annotate('', xy=(gl[0] + 0.18 * math.cos(gl[2]), gl[1] + 0.18 * math.sin(gl[2])), xytext=(gl[0], gl[1]), arrowprops=dict(arrowstyle='->', color='#c2255c', lw=1.8), zorder=7)
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=11, loc='left', color=tcolor)



# 세 판: (결과, exp 폴더, Smac 이름, exp 번호, 제목)
PAN = [(R, EXP, 'Smac_R10_C30_A10_RS', 0, '기준 tol 0.25 · cp 3.0'), (np.load(sys.argv[4]), Path(sys.argv[5]), 'Smac_R10_C30_A10_RS', 0, 'tol 0.35 · cp 3.0'),
       (np.load(sys.argv[6]), Path(sys.argv[7]), 'Smac_R10_C15_A10_RS', 0, 'tol 0.25 · cp 1.5')]
D = []
for RR, EE, VV, ei, lab in PAN:
    R, EXP, V = RR, EE, VV   # load() 가 쓰는 전역을 판마다 바꿈(장면 · 순간은 같음)
    order_k = 'sa3_115653'
    i0 = order.index(order_k); ox, oy, r, _ = SC[order_k + '/info']
    d = load(order_k) if ei == order.index(order_k) else None
    if d is None:
        E = np.loadtxt(EXP / ('exp_%d.txt' % ei), ndmin=2)
        G = R[order_k + '/recon'].astype(np.int16); G = np.where(G < 0, 101, G)
        d = dict(k=order_k, info=(ox, oy, r), G=G, E=E, W=np.c_[ox + (E[:, 0] + .5) * r, oy + (E[:, 1] + .5) * r, np.radians(E[:, 2] * 5.0), ox + (E[:, 3] + .5) * r, oy + (E[:, 4] + .5) * r],
                 sp=R['%s/%s/path' % (order_k, V)] if '%s/%s/path' % (order_k, V) in R else np.zeros((0, 3)), st=SC[order_k + '/start'], gl=SC[order_k + '/goal'])
    d['lab'] = lab; d['chain'] = nearest_chain(d) if not len(d['sp']) else None; D.append(d)
tmp = tempfile.mkdtemp(); N = max(len(d['W']) for d in D)
steps = list(np.unique(np.r_[0, np.geomspace(1, N, 130).astype(int)])) + [N] * 45
for f, u in enumerate(steps):
    fg, axs = plt.subplots(1, 3, figsize=(14.4, 8.1))
    for a, d in zip(axs, D):
        done = u >= len(d['W']); ok = len(d['sp']) > 0
        if done and ok:
            p = d['sp']; g = d['gl']; dd = math.hypot(p[-1, 0] - g[0], p[-1, 1] - g[1]); dy = (math.degrees(p[-1, 2] - g[2]) + 180) % 360 - 180
            t = '%s → Smac 성공\n방문 %d · 경로 끝 목표 %.1f cm 앞 · 방향 차 %+.0f°' % (d['lab'], len(d['W']), 100 * dd, dy); c = '#0f7a3c'
        elif done:
            t = '%s → Smac 실패\n방문 %d · 목표 %.1f cm 앞까지 갔으나 수락 안 됨' % (d['lab'], len(d['W']), 100 * d['chain'][1]); c = '#b3263e'
        else:
            t = '%s → 탐색 중\n방문 %d / %d' % (d['lab'], min(u, len(d['W'])), len(d['W'])); c = '#1b1f24'
        draw(a, d, int(u), t, c, chain=d['chain'] if (done and not ok) else None)
    fg.suptitle('16:11:56.85 남행 · 같은 지도 · 출발(파랑) · 목표(분홍 점선) — 허용치(tol) · cost_penalty(cp) 만 다름. 점 = 방문 노드, 초록 = 만든 경로, 주황 = 실패 판의 가장 가까운 노드와 사슬', x=0.01, ha='left', fontsize=11)
    fg.tight_layout(rect=(0, 0, 1, 0.96)); fg.savefig('%s/f%04d.png' % (tmp, f), dpi=100)
    if f == len(steps) - 1: fg.savefig(LAST, dpi=110)
    plt.close(fg)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '15', '-i', tmp + '/f%04d.png', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-crf', '20', VID], check=True)
shutil.rmtree(tmp, ignore_errors=True); print('저장', VID, '장', len(steps), '· 방문', [len(d['W']) for d in D])
