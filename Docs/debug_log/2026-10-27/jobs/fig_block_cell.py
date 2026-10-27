#!/usr/bin/env python3
"""fig_block_cell — §14 막힘 판정 칸 (1.13, 0.14) 원자료 대조 그림 (2026-10-27, PC).
  입력: outputs/block_cell/anal_block_cell_f2st1.txt(도구 jobs/anal_block_cell.py, 0.5 s 간격) 를 그대로 읽어 그림.
  왼쪽: 시간축 — 전역 코스트맵의 P 값(99 = 막힘 판정) · P 0.4 m 안 칸 수(전역 치명 · nvblox ≤0 · 라이다 점) · 로버 ↔ P 거리.
  오른쪽: map 평면 — 기록 상자 · P · 시각별 '가장 가까운 nvblox 장애 칸' 위치(갈 때 / 복귀) · 라이다 근접점.
  인자: anal.txt 출력.png"""
import sys, re, time
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
BOX = (1.151, 1.261, -0.20, -0.02); P = (1.13, 0.14)
f = lambda s: [float(x) for x in s]
rows = []
for l in open(sys.argv[1], encoding='utf-8'):
    m = re.match(r'(\d\d):(\d\d):(\d\d)\.(\d)', l)
    if not m: continue
    t = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 10
    c = l.split(' | ')
    rp = re.search(r'로버 \(([-\d.]+), ([-\d.]+), [-+\d]+°\) · P ([\d.]+) m', c[1])
    gv = re.search(r'map 값 (-?\d+|None)', c[2]); gn = re.search(r'· (\d+)\(밖', c[2])
    nv = re.search(r'\(([-\d.]+), ([-\d.]+)\) (\d+) cm · (\d+)\(밖', c[4])
    li = re.search(r'라이다 (\d+)(?: · (\d+) cm \(([-\d.]+), ([-\d.]+)\))?', c[5])
    rows.append(dict(t=t, rx=float(rp[1]), ry=float(rp[2]), dP=float(rp[3]), g=int(gv[1]) if gv[1] != 'None' else np.nan,
                     gn=int(gn[1]) if gn else 0, nvn=int(nv[4]) if nv else 0, nvx=f(nv.groups()[:2]) if nv else None,
                     ln=int(li[1]), lxy=f(li.groups()[2:]) if li and li[3] else None))
T0 = rows[0]['t']; t = np.array([r['t'] - T0 for r in rows])
fig = plt.figure(figsize=(15, 7.6)); gs = fig.add_gridspec(3, 2, width_ratios=[1.55, 1], hspace=0.12, wspace=0.12)
a1, a2, a3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[2, 0]); b = fig.add_subplot(gs[:, 1])
TB = 11 * 3600 + 24 * 60 + 46.1 - T0; TPL = 11 * 3600 + 23 * 60 + 41.7 - T0; TRET = 11 * 3600 + 24 * 60 + 53.2 - T0
for a in (a1, a2, a3):
    a.axvspan(TB, TB + 2.0, color='#fde2e4', zorder=0); a.axvline(TPL, color='#1c7ed6', lw=1, ls=':'); a.grid(color='#eceef1'); a.set_xlim(t[0], t[-1])
a1.step(t, [r['g'] for r in rows], where='post', color='#1b1f24', lw=1.4); a1.axhline(99, color='#d6336c', lw=0.8, ls='--')
a1.set_ylabel('전역 P 값'); a1.set_ylim(0, 105); a1.text(t[0] + 100, 86, '99 = 내접(막힘 판정 기준)', color='#d6336c', fontsize=9)
a1.text(TPL - 2, 6, '11:23:41.7 복귀 경로 계획\n(이때 P 값 41)', color='#1c7ed6', fontsize=9, ha='right')
a1.text(TB - 3, 50, '11:24:46 막힘 판정\n→ 2 s 뒤 중단(분홍 띠)', color='#b3263e', fontsize=9, ha='right')
a2.step(t, [r['gn'] for r in rows], where='post', color='#1b1f24', lw=1.3, label='전역 치명 칸')
a2.step(t, [r['nvn'] for r in rows], where='post', color='#e8590c', lw=1.3, label='nvblox 장애 칸(카메라)')
a2.step(t, [r['ln'] / 5 for r in rows], where='post', color='#0f9d58', lw=1.3, label='라이다 점 ÷ 5')
a2.set_ylabel('P 0.4 m 안 개수'); a2.legend(fontsize=9, frameon=False, ncol=3, loc='upper center')
a3.plot(t, [r['dP'] for r in rows], color='#5b6470', lw=1.3); a3.set_ylabel('로버 ↔ P (m)')
tk = np.arange(60 - T0 % 60, t[-1] + 1, 60); a3.set_xticks(tk); a3.set_xticklabels([time.strftime('%H:%M', time.gmtime(T0 + x)) for x in tk])
for a in (a1, a2): a.set_xticklabels([])
a3.text(10, 4.5, '갈 때(목표 1)', fontsize=9, color='#5b6470'); a3.text(TPL - 50, 4.5, '복귀(목표 8)', fontsize=9, color='#5b6470')
# 오른쪽 평면
b.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fc='#e9ecef', ec='#5b6470', lw=1.4))
b.text(BOX[1] + 0.01, BOX[2] + 0.01, '기록 상자', fontsize=9, color='#5b6470')
b.add_patch(Circle(P, 0.175, fc='none', ec='#d6336c', ls='--', lw=1)); b.plot(*P, 'x', color='#d6336c', ms=12, mew=2.5)
b.text(P[0] - 0.015, P[1] + 0.035, '막힘 판정 칸 P (1.13, 0.14)\n점선 = 반경 0.175 m(내접)', fontsize=9, color='#b3263e', ha='center', va='bottom')
out = [r['nvx'] for r in rows if r['nvx'] and r['t'] - T0 < 120]; ret = [r['nvx'] for r in rows if r['nvx'] and r['t'] - T0 > TPL + 40]
lfar = [r['lxy'] for r in rows if r['lxy'] and 11 * 3600 + 23 * 60 + 49 - T0 < r['t'] - T0 < 11 * 3600 + 23 * 60 + 56 - T0]
jit = lambda L: np.array(L) + np.random.default_rng(0).normal(0, 0.003, (len(L), 2))
b.scatter(*jit(out).T, s=40, color='#1c7ed6', alpha=0.5, label='nvblox 최근접 칸 · 갈 때 (%d 시각)' % len(out), zorder=4)
b.scatter(*jit(ret).T, s=40, color='#e8590c', alpha=0.6, label='nvblox 최근접 칸 · 복귀 (%d 시각)' % len(ret), zorder=5)
b.scatter(*np.array(lfar).T, s=26, marker='^', color='#0f9d58', label='라이다 최근접 점 · 11:23:50~55 (4.8 m 밖)', zorder=5)
b.set_xlim(0.92, 1.40); b.set_ylim(-0.26, 0.30); b.set_aspect('equal'); b.grid(color='#eceef1'); b.legend(fontsize=8.5, loc='lower left', frameon=True)
b.set_xlabel('map x (m)'); b.set_ylabel('map y (m)'); b.set_title('칸 위치(map, 5 cm 칸 중심)', loc='left', fontsize=11)
a1.set_title('f2st1 출발 상자 주변 — P 값과 원자료(0.5 s 간격)', loc='left', fontsize=11)
fig.suptitle('막힘 판정 칸 (1.13, 0.14) = 상자 모서리 칸 1~2 개의 내접 띠 — 카메라(nvblox)만 봄 · 라이다 0 점', x=0.01, ha='left', fontsize=13)
fig.savefig(sys.argv[2], dpi=110, bbox_inches='tight'); print('저장', sys.argv[2], '갈 때', len(out), '복귀', len(ret), '라이다', len(lfar))
