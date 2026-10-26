#!/usr/bin/env python3
"""fig_smac_expansion — Smac Hybrid 가 경로를 찾으며 '어디까지 뻗어 봤나'(방문 노드)를 그림 · 영상으로 (2026-10-26 §22, PC, 로버 안 움직임).
  왜: 사용자 — "경로를 못 내다가, 경로를 만드는 부분을 시각화해줄 수 있겠는가?". f2sa3 서쪽 통로에서 Smac 에 물은 6 순간(실패 5 · 성공 1)을
    같은 지도 · 출발 · 목표로 오프라인 재질의하고, 진단 빌드(Docs/06_planner/smac_fork/nav2_smac_planner_rover_expdump.patch, 동작 그대로 기록만)가
    남긴 방문 노드를 그 순간의 전역 코스트맵 위에 겹침.
  입력: 결과.npz(query_planners) · 장면.npz(prep_scenes) · exp 폴더(exp_<n>.txt = n 번째 Smac 질의, 줄 = 칸 x y 방향칸 부모x 부모y; 세계 좌표 = 원점 + (칸 + 0.5) × 해상도,
    방향 = 칸 × 5°(72 칸) — 1.1.20 utils.hpp getWorldCoords 와 같은 식).
  출력: 그림 1 장(6 칸) + 영상 1 개(실패 16:11:56.85 대 성공 16:13:08.65 탐색이 자라는 모양). 인자: 결과.npz 장면.npz exp폴더 그림.png 영상.mp4"""
import sys, json, math, subprocess, tempfile, shutil
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Polygon
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
R = np.load(sys.argv[1]); SC = np.load(sys.argv[2]); EXP = Path(sys.argv[3]); OUT, VID = sys.argv[4], sys.argv[5]
meta = json.loads(str(SC['meta'])); V = 'Smac_R10_C30_A10_RS'
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
TIME = {'sa3_115653': '16:11:56.85', 'sa3_121553': '16:12:15.53', 'sa3_122202': '16:12:22.02', 'sa3_123521': '16:12:35.21', 'sa3_125954': '16:12:59.54', 'sa3_130865': '16:13:08.65'}
XL, YL = (-2.25, -0.95), (-5.85, -3.25)   # 서쪽 통로 창(map)
# 코스트맵 색: 0 흰 → 98 연회색, 99 내접 진회색, 100 치명 검정, 미지 연노랑
cmap = ListedColormap(np.r_[np.linspace([1, 1, 1], [0.78, 0.80, 0.84], 99), [[0.45, 0.47, 0.52]], [[0.08, 0.09, 0.11]], [[0.98, 0.95, 0.80]]])


def fp(x, y, yaw):
    c, s = math.cos(yaw), math.sin(yaw); return np.c_[x + c * FP[:, 0] - s * FP[:, 1], y + s * FP[:, 0] + c * FP[:, 1]]


def load(i, sc):
    k = sc['name']; ox, oy, r, _ = SC[k + '/info']; G = R[k + '/recon'].astype(np.int16) if k + '/recon' in R else SC[k + '/grid'].astype(np.int16)
    G = np.where(G < 0, 101, G)
    f = EXP / ('exp_%d.txt' % i); E = np.loadtxt(f, ndmin=2) if f.exists() and f.stat().st_size else np.zeros((0, 5))
    W = np.c_[ox + (E[:, 0] + .5) * r, oy + (E[:, 1] + .5) * r, np.radians(E[:, 2] * 5.0), ox + (E[:, 3] + .5) * r, oy + (E[:, 4] + .5) * r] if len(E) else np.zeros((0, 5))
    sp = R['%s/%s/path' % (k, V)] if '%s/%s/path' % (k, V) in R else np.zeros((0, 3))
    nf = R['%s/GridBased/path' % k] if '%s/GridBased/path' % k in R else np.zeros((0, 3))
    t = R['%s/%s/t' % (k, V)]; return k, (ox, oy, r), G, W, E, sp, nf, float(t[1])


def draw(ax, k, info, G, W, E, sp, nf, wall, upto=None, title=True):
    ox, oy, r = info; st = SC[k + '/start']; gl = SC[k + '/goal']
    ax.imshow(G, origin='lower', extent=(ox, ox + G.shape[1] * r, oy, oy + G.shape[0] * r), cmap=cmap, vmin=0, vmax=101, interpolation='nearest')
    n = len(W) if upto is None else min(upto, len(W)); Wn = W[:n]
    if n:
        m = Wn[:, 3] > ox   # 부모 있는 노드
        ax.plot(np.c_[Wn[m, 3], Wn[m, 0], np.full(m.sum(), np.nan)].ravel(), np.c_[Wn[m, 4], Wn[m, 1], np.full(m.sum(), np.nan)].ravel(), color='#2f6fb3', lw=0.5, alpha=0.55)
        ax.scatter(Wn[:, 0], Wn[:, 1], c=np.arange(n), cmap='viridis', s=6, zorder=3, vmin=0, vmax=max(len(W), 1))
    if len(nf) and upto is None: ax.plot(nf[:, 0], nf[:, 1], color='#e8590c', lw=1.6, ls='--', zorder=4, label='NavFn 경로(같은 질의)')
    if len(sp) and (upto is None or upto >= len(W)): ax.plot(sp[:, 0], sp[:, 1], color='#0f9d58', lw=2.4, zorder=5, label='Smac 경로')
    ax.add_patch(Polygon(fp(*st), closed=True, fc='#1c7ed6', ec='#1c7ed6', alpha=0.35, lw=1.5, zorder=6))
    ax.annotate('', xy=(st[0] + 0.18 * math.cos(st[2]), st[1] + 0.18 * math.sin(st[2])), xytext=(st[0], st[1]), arrowprops=dict(arrowstyle='->', color='#1c7ed6', lw=1.8), zorder=7)
    ax.add_patch(Polygon(fp(*gl), closed=True, fc='none', ec='#c2255c', ls='--', lw=1.4, zorder=6))
    ax.annotate('', xy=(gl[0] + 0.18 * math.cos(gl[2]), gl[1] + 0.18 * math.sin(gl[2])), xytext=(gl[0], gl[1]), arrowprops=dict(arrowstyle='->', color='#c2255c', lw=1.8), zorder=7)
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    if title:
        res = '성공' if len(sp) else '실패'
        ax.set_title('%s  Smac %s\n방문 노드 %d · 왕복 %.2f s' % (TIME.get(k, k), res, len(W), wall), fontsize=10.5, loc='left', color='#0f7a3c' if len(sp) else '#b3263e')


rows = [load(i, sc) for i, sc in enumerate(meta)]
for k, _, _, W, *_ in rows: print(k, '방문 노드', len(W))
fig, axs = plt.subplots(2, 3, figsize=(13.5, 13.5))
for ax, row in zip(axs.ravel(), rows): draw(ax, *row)
axs[0, 0].legend(loc='lower left', fontsize=8.5, framealpha=0.9)
fig.suptitle('f2sa3 서쪽 통로 — Smac Hybrid 가 탐색하며 방문한 노드(점 색 = 방문 순서, 보라 → 노랑; 파란 선 = 부모에서 뻗은 가지)\n파랑 = 출발 차체 · 방향, 분홍 점선 = 목표 차체 · 방향, 배경 = 그 순간 전역 코스트맵(검정 치명 · 진회색 내접)', x=0.02, ha='left', fontsize=11.5)
fig.tight_layout(); fig.savefig(OUT, dpi=110); print('저장', OUT)

# 영상: 실패 16:11:56.85(가장 많이 뻗은 실패) 대 성공 16:13:08.65 — 방문 순서대로 자람
pick = [r for r in rows if r[0] in ('sa3_115653', 'sa3_130865')]
# 방문 수가 340 556 대 23 이라 선형 눈금이면 성공 쪽이 첫 장에 끝남 → 로그 눈금으로 자라게 하고 끝 장면을 3 s 붙잡음
N = max(len(r[3]) for r in pick); steps = list(np.unique(np.r_[0, np.geomspace(1, N, 150).astype(int)])) + [N] * 45
tmp = tempfile.mkdtemp()
for f, u in enumerate(steps):
    fg, ax2 = plt.subplots(1, 2, figsize=(12.8, 7.2))
    for a, row in zip(ax2, pick):
        draw(a, *row, upto=int(u), title=False)
        k, W, sp = row[0], row[3], row[5]; done = u >= len(W)
        a.set_title('%s  Smac %s\n방문 %d / %d' % (TIME[k], ('성공' if len(sp) else '실패 — 더 뻗을 곳 없음') if done else '탐색 중', min(u, len(W)), len(W)), fontsize=12, loc='left',
                    color=('#0f7a3c' if len(sp) else '#b3263e') if done else '#1b1f24')
    fg.tight_layout(); fg.savefig('%s/f%04d.png' % (tmp, f), dpi=100); plt.close(fg)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '15', '-i', tmp + '/f%04d.png', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-crf', '20', VID], check=True)
shutil.rmtree(tmp, ignore_errors=True); print('저장', VID, '장', len(steps))
