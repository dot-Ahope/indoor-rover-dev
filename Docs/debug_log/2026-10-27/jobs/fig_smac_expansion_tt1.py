#!/usr/bin/env python3
"""fig_smac_expansion_tt1 — f2tt1 통로 세 순간의 Smac 탐색이 자라는 영상(fig_smac_expansion_v2 의 3 칸 구성, 장면 목록만 바꿈) (2026-10-27 §27, PC).
  장면(실주행 모두 Smac 성공 — 세 번째는 오프라인 재질의에서 실패: 15:58:09 지도 = 방문 12 697 뒤 실패, 15:58:11.40 지도 = 출발 칸 문제로 방문 0 즉시 실패): 15:57:41 남행(목표 4) · 15:58:05.80 북행(목표 5, 남쪽 끝 출발) · 15:58:11.40 북행 재계획(막힘 뒤).
  입력: outputs/tt1_exp/result_V1.npz · scenes_tt1.npz · exp 폴더(exp_<i> = 장면 순서). 세계 좌표 = 원점 + (칸 + 0.5) × 해상도, 방향 = 칸 × 5°.
  인자: 결과.npz 장면.npz exp폴더 영상.mp4 [마지막장.png]"""
import sys, json, math, subprocess, tempfile, shutil
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
R = np.load(sys.argv[1]); SC = np.load(sys.argv[2]); EXP = Path(sys.argv[3]); VID = sys.argv[4]; LAST = sys.argv[5] if len(sys.argv) > 5 else None
meta = json.loads(str(SC['meta'])); V = 'Smac_R10_C30_A10_RS'; order = [m['name'] for m in meta]
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
TIME = {'tt1_157741': '15:57:41.17', 'tt1_158058': '15:58:05.80', 'tt1_158114': '15:58:11.40'}
WHERE = {'tt1_157741': '남행 · 통로 북쪽 입구 출발', 'tt1_158058': '북행 · 남쪽 끝 출발(-85°)', 'tt1_158114': '북행 재계획 · 남쪽 끝(-168°)\n15:58:09 지도 재질의 · 실주행은 성공'}
XL, YL = (-2.25, -0.95), (-5.85, -3.25)
cmap = ListedColormap(np.r_[np.linspace([1, 1, 1], [0.78, 0.80, 0.84], 99), [[0.45, 0.47, 0.52]], [[0.08, 0.09, 0.11]], [[0.98, 0.95, 0.80]]])
fp = lambda x, y, a: np.c_[x + math.cos(a) * FP[:, 0] - math.sin(a) * FP[:, 1], y + math.sin(a) * FP[:, 0] + math.cos(a) * FP[:, 1]]


def load(k):
    i = order.index(k); ox, oy, r, _ = SC[k + '/info']
    G = R[k + '/recon'].astype(np.int16) if k + '/recon' in R else SC[k + '/grid'].astype(np.int16); G = np.where(G < 0, 101, G)
    E = np.loadtxt(EXP / ('exp_%d.txt' % i), ndmin=2)
    W = np.c_[ox + (E[:, 0] + .5) * r, oy + (E[:, 1] + .5) * r, np.radians(E[:, 2] * 5.0), ox + (E[:, 3] + .5) * r, oy + (E[:, 4] + .5) * r]
    sp = R['%s/%s/path' % (k, V)] if '%s/%s/path' % (k, V) in R else np.zeros((0, 3))
    return dict(k=k, info=(ox, oy, r), G=G, W=W, sp=sp, st=SC[k + '/start'], gl=SC[k + '/goal'])


def draw(ax, d, n, title, tcolor):
    ox, oy, r = d['info']; G, W = d['G'], d['W']
    ax.imshow(G, origin='lower', extent=(ox, ox + G.shape[1] * r, oy, oy + G.shape[0] * r), cmap=cmap, vmin=0, vmax=101, interpolation='nearest')
    n = min(n, len(W)); Wn = W[:n]
    if n:
        m = Wn[:, 3] > ox
        ax.plot(np.c_[Wn[m, 3], Wn[m, 0], np.full(m.sum(), np.nan)].ravel(), np.c_[Wn[m, 4], Wn[m, 1], np.full(m.sum(), np.nan)].ravel(), color='#2f6fb3', lw=0.5, alpha=0.5)
        ax.scatter(Wn[:, 0], Wn[:, 1], c=np.arange(n), cmap='viridis', s=6, zorder=3, vmin=0, vmax=max(len(W), 1))
    if len(d['sp']) and n >= len(W): ax.plot(d['sp'][:, 0], d['sp'][:, 1], color='#0f9d58', lw=2.6, zorder=5)
    st, gl = d['st'], d['gl']
    ax.add_patch(Polygon(fp(*st), closed=True, fc='#1c7ed6', ec='#1c7ed6', alpha=0.35, lw=1.5, zorder=6))
    ax.annotate('', xy=(st[0] + 0.18 * math.cos(st[2]), st[1] + 0.18 * math.sin(st[2])), xytext=(st[0], st[1]), arrowprops=dict(arrowstyle='->', color='#1c7ed6', lw=1.8), zorder=7)
    ax.add_patch(Polygon(fp(*gl), closed=True, fc='none', ec='#c2255c', ls='--', lw=1.4, zorder=6))
    ax.annotate('', xy=(gl[0] + 0.18 * math.cos(gl[2]), gl[1] + 0.18 * math.sin(gl[2])), xytext=(gl[0], gl[1]), arrowprops=dict(arrowstyle='->', color='#c2255c', lw=1.8), zorder=7)
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=11, loc='left', color=tcolor)


D = [load(k) for k in ('tt1_157741', 'tt1_158058', 'tt1_158114')]
N = max(len(d['W']) for d in D); steps = list(np.unique(np.r_[0, np.geomspace(1, N, 120).astype(int)])) + [N] * 45
tmp = tempfile.mkdtemp()
for f, u in enumerate(steps):
    fg, axs = plt.subplots(1, 3, figsize=(14.4, 8.1))
    for a, d in zip(axs, D):
        done = u >= len(d['W']); ok = len(d['sp']) > 0
        t = '%s  %s\n%s · 방문 %d / %d' % (TIME[d['k']], ('Smac 성공' if ok else 'Smac 실패') if done else '탐색 중', WHERE[d['k']], min(u, len(d['W'])), len(d['W']))
        draw(a, d, int(u), t, ('#0f7a3c' if ok else '#b3263e') if done else '#1b1f24')
    fg.suptitle('f2tt1 서쪽 통로 — Smac Hybrid(tol 0.35 · cp 3.0) 탐색. 분홍 점선 = 목표, 파랑 = 출발, 점 = 방문 노드(색 = 순서), 초록 = 만든 경로', x=0.01, ha='left', fontsize=11.5)
    fg.tight_layout(); fg.savefig('%s/f%04d.png' % (tmp, f), dpi=100)
    if LAST and f == len(steps) - 1: fg.savefig(LAST, dpi=110)
    plt.close(fg)
subprocess.run(['C:/ffmpeg/bin/ffmpeg', '-y', '-loglevel', 'error', '-framerate', '15', '-i', tmp + '/f%04d.png', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-crf', '20', VID], check=True)
shutil.rmtree(tmp, ignore_errors=True); print('저장', VID, '장', len(steps), '· 방문', [len(d['W']) for d in D], '· 성공', [len(d['sp']) > 0 for d in D])
