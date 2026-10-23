#!/usr/bin/env python3
"""anal_plan_compare — 오프라인 계획기 결과(query_planners.py 출력)를 지표 · 그림으로 (2026-10-23 Phase P §4, PC).
  지표(장면 × 계획기):
    · 상자 여유(차체) = 경로 자세마다 차체 직사각형(패딩 없음, 0.262/−0.248 × ±0.165)과 실제 상자(기록 위치 x 1.151~1.261, y −0.20~−0.02) 사이 최소 거리.
      경로 방향 = Smac 은 경로가 준 yaw, NavFn 은 yaw 가 없어 경로 접선(앞뒤 0.1 m). 로버가 경로를 정확히 따른다는 가정의 여유(추종 오차는 별도).
    · 상자 여유(중심) = 경로점 ↔ 상자 − 반폭 0.165 (B0 기록 anal_plan_series 와 같은 정의, 출발 0.3 m 안 제외).
    · 치명까지(차체) = 재구성 전역 코스트맵의 치명 칸 중심까지 차체 최소 거리(칸 반쪽 0.025 를 빼지 않은 대략치) — 상자 외 장면용.
    · 길이 · 최대 꺾임(0.3 m 창 방향 변화) · 계획 시간 · 실패.
  그림: 장면마다 재구성 코스트맵 + 계획기별 경로(+ 차체 몇 개). 인자: 결과.npz 장면.npz 그림폴더"""
import sys, json, math
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
R = np.load(sys.argv[1]); SC = np.load(sys.argv[2]); FIG = Path(sys.argv[3]); FIG.mkdir(parents=True, exist_ok=True)
meta = json.loads(str(SC['meta'])); BOX = (1.151, 1.261, -0.20, -0.02)
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
xs = np.r_[np.linspace(-0.248, 0.262, 21)]; ys = np.linspace(-0.165, 0.165, 15)
EDGE = np.r_[np.c_[xs, np.full_like(xs, 0.165)], np.c_[xs, np.full_like(xs, -0.165)], np.c_[np.full_like(ys, 0.262), ys], np.c_[np.full_like(ys, -0.248), ys]]
BP = np.array([[x, y] for x in np.linspace(BOX[0], BOX[1], 12) for y in np.linspace(BOX[2], BOX[3], 19)])


def yaw_of(P, pid):
    if pid != 'GridBased' and np.any(P[:, 2] != 0): return P[:, 2]
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(P[:, :2], axis=0).T))]; out = np.zeros(len(P))
    for i in range(len(P)):
        a = np.searchsorted(s, s[i] - 0.1); b = min(np.searchsorted(s, s[i] + 0.1), len(P) - 1); a = min(a, b - 1) if b > 0 else 0
        out[i] = math.atan2(P[b, 1] - P[a, 1], P[b, 0] - P[a, 0])
    return out


def body_pts(p, yaw):
    c, s = math.cos(yaw), math.sin(yaw); return np.c_[p[0] + c * EDGE[:, 0] - s * EDGE[:, 1], p[1] + s * EDGE[:, 0] + c * EDGE[:, 1]]


def body_dist(p, yaw, Q):   # 차체 직사각형 ↔ 점들 최소 거리(점이 차체 안이면 0)
    c, s = math.cos(yaw), math.sin(yaw); d = Q - p[:2]; bx = c * d[:, 0] + s * d[:, 1]; by = -s * d[:, 0] + c * d[:, 1]
    dx = np.maximum(np.maximum(-0.248 - bx, bx - 0.262), 0); dy = np.maximum(np.maximum(-0.165 - by, by - 0.165), 0); return float(np.hypot(dx, dy).min())


rows = []
for sc in meta:
    k = sc['name']; G = R[k + '/recon'].astype(np.int16) if k + '/recon' in R.files else SC[k + '/grid'].astype(np.int16)
    ox, oy, res, _ = SC[k + '/info']; L = np.argwhere(G >= 100); LC = np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res]
    pids = sorted({f.split('/')[1] for f in R.files if f.startswith(k + '/') and f.endswith('/path')}, key=lambda s: (s != 'GridBased', s))
    fig, ax = plt.subplots(figsize=(9, 7.5)); st = SC[k + '/start']; gl = SC[k + '/goal']
    cm = ListedColormap(['#eceff1', '#ffffff'] + ['#%02x%02x%02x' % tuple(int(a + (b - a) * i / 97) for a, b in zip((246, 246, 244), (196, 199, 204))) for i in range(98)] + ['#fbe3cc', '#3b4252'])
    ax.imshow(np.clip(G, -1, 100) + 1, origin='lower', extent=(ox, ox + G.shape[1] * res, oy, oy + G.shape[0] * res), cmap=cm, vmin=0, vmax=101, interpolation='nearest')
    cols = {'GridBased': '#d9480f'}; pal = ['#5b3cc4', '#1971c2', '#0ca678', '#9c36b5', '#1098ad', '#2b8a3e']
    for i, pid in enumerate([p for p in pids if p != 'GridBased']): cols[pid] = pal[i % len(pal)]
    allp = [st[:2], gl[:2]]
    for pid in pids:
        P = R['%s/%s/path' % (k, pid)]; tt = R['%s/%s/t' % (k, pid)]
        if len(P) < 2: rows.append((k, pid, None)); continue
        Y = yaw_of(P, pid); s = np.r_[0, np.cumsum(np.hypot(*np.diff(P[:, :2], axis=0).T))]
        bclr = min(body_dist(P[i], Y[i], BP) for i in range(len(P)))
        far = s >= 0.3; cclr = float(np.min(np.hypot(P[far, None, 0] - BP[None, :, 0], P[far, None, 1] - BP[None, :, 1]))) - 0.165 if far.any() else float('nan')
        lclr = min(body_dist(P[i], Y[i], LC) for i in range(0, len(P), max(1, len(P) // 150)))
        h = np.unwrap(np.arctan2(np.diff(P[:, 1]), np.diff(P[:, 0]))); turn = 0.0
        for i in range(len(h)):
            j = np.searchsorted(s[1:], s[i + 1] + 0.3); turn = max(turn, abs(h[min(j, len(h) - 1)] - h[i]))
        rows.append((k, pid, dict(n=len(P), L=s[-1], bclr=bclr, cclr=cclr, lclr=lclr, turn=math.degrees(turn), t=tt[0])))
        ax.plot(P[:, 0], P[:, 1], color=cols[pid], lw=2.4 if pid == 'GridBased' else 1.6, label='%s (차체↔상자 %.1f cm)' % (pid, 100 * bclr) if 'b910' in k else pid, zorder=3)
        allp.append(P[:, :2])
    for pid in ('GridBased', 'Smac_R10_C12'):   # 상자 근처 차체 그림(두 대표만)
        if '%s/%s/path' % (k, pid) not in R.files or len(R['%s/%s/path' % (k, pid)]) < 2: continue
        P = R['%s/%s/path' % (k, pid)]; Y = yaw_of(P, pid)
        for i in range(0, len(P), max(1, len(P) // 25)):
            if math.hypot(P[i, 0] - 1.2, P[i, 1] + 0.1) < 0.7 or 'west' in k:
                c, s_ = math.cos(Y[i]), math.sin(Y[i]); W = np.c_[P[i, 0] + c * FP[:, 0] - s_ * FP[:, 1], P[i, 1] + s_ * FP[:, 0] + c * FP[:, 1]]
                ax.fill(W[:, 0], W[:, 1], fc='none', ec=cols[pid], lw=0.7, alpha=0.6, zorder=2)
    ax.add_patch(plt.Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fc='#e03131', ec='none', alpha=0.85, zorder=4))
    ax.plot(*st[:2], 'o', color='#0f766e', ms=8, zorder=5); ax.annotate('', xy=(st[0] + 0.3 * math.cos(st[2]), st[1] + 0.3 * math.sin(st[2])), xytext=st[:2], arrowprops=dict(arrowstyle='->', color='#0f766e', lw=2))
    ax.plot(*gl[:2], '*', color='#1f2328', ms=13, zorder=5); ax.annotate('', xy=(gl[0] + 0.3 * math.cos(gl[2]), gl[1] + 0.3 * math.sin(gl[2])), xytext=gl[:2], arrowprops=dict(arrowstyle='->', color='#1f2328', lw=2))
    A = np.vstack(allp); m = 0.6; ax.set_xlim(A[:, 0].min() - m, A[:, 0].max() + m); ax.set_ylim(A[:, 1].min() - m, A[:, 1].max() + m); ax.set_aspect('equal')
    ax.set_title('%s — %s' % (k, sc['desc']), fontsize=11, loc='left'); ax.legend(fontsize=8.5, loc='best', framealpha=0.9); ax.tick_params(labelsize=8)
    fig.tight_layout(); fig.savefig(FIG / ('plan_cmp_%s.png' % k), dpi=110); plt.close(fig)
print('장면 · 계획기 | 점 · 길이 m | 상자 여유 차체 · 중심(cm) | 치명까지 차체(cm) | 최대 꺾임 0.3 m(°) | 계획 s')
for k, pid, d in rows:
    if d is None: print('%-16s %-13s | 실패' % (k, pid)); continue
    print('%-16s %-13s | %4d · %5.2f | %6.1f · %6.1f | %6.1f | %5.0f | %.3f' % (k, pid, d['n'], d['L'], 100 * d['bclr'], 100 * d['cclr'], 100 * d['lclr'], d['turn'], d['t']))
