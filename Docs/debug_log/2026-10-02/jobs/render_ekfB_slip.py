# 10-02 §16: rf2o 로 vx·vy 를 보정한 EKF B 가 회전 미끄러짐을 실제로 따라갔나 — rot3(줄자 있음)·rot2
#   ① 시작 자세 기준 궤적과 끝점 오차(줄자) ② 누적 이동 크기 시계열(+ 회전 지령 구간) ③ 독립 검사: 각 EKF 자세로 스캔을 odom 좌표에 놓았을 때
#     첫 스캔과의 어긋남(최근접 거리 중앙) — EKF 가 미끄러짐을 따라가면 정적인 벽이 제자리에 있어 어긋남이 작게 유지된다
import numpy as np, math, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
FIG = r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_'
C = {'A': '#c05621', 'B': '#2f855a', 'rf2o': '#805ad5'}
LX, LY = 0.152, math.pi - 0.04677
def srt(a): return a[np.argsort(a[:, 0])]
def at(A, t): i = min(max(np.searchsorted(A[:, 0], t) - 1, 0), len(A) - 1); return A[i, 1:4]
def inframe(P, p0):
    c, s = math.cos(p0[2]), math.sin(p0[2]); d = P[:, 1:3] - p0[:2]; return c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1]
out = {}
for bag in ('rot3', 'rot2'):
    Z = np.load('f2a6/r2_%s.npz' % bag); A, B, OB = srt(Z['A']), srt(Z['B']), srt(Z['ob'])
    R = srt(np.load('f2a6/rf2o_%s.npz' % bag)['rf'])
    t0, t1 = max(A[0, 0], B[0, 0]) + 0.5, min(A[-1, 0], B[-1, 0]) - 0.5
    # 회전 지령 구간: 라이브 EKF 각속도로 근사
    yaw = np.unwrap(OB[:, 3]); w = np.gradient(yaw, OB[:, 0])
    res = {}
    for k, P in (('A', A), ('B', B)):
        P = P[(P[:, 0] >= t0) & (P[:, 0] <= t1)]; x, y = inframe(P, P[0, 1:4]); res[k] = (P[:, 0] - t0, x, y)
    Rr = R[(R[:, 0] >= t0) & (R[:, 0] <= t1)]; x, y = inframe(Rr, Rr[0, 1:4]); res['rf2o'] = (Rr[:, 0] - t0, -x, -y)
    # ③ 스캔 일관성
    cons = {k: [] for k in ('A', 'B')}; ts = []
    ref = {}
    for t, rr, (amin, ainc) in zip(Z['st'], Z['sr'], Z['sa']):
        if t < t0 or t > t1: continue
        a = amin + ainc * np.arange(len(rr)) + LY; ok = np.isfinite(rr) & (rr > 0.2) & (rr < 2.0)
        bx, by = LX + rr[ok] * np.cos(a[ok]), rr[ok] * np.sin(a[ok]); ts.append(t - t0)
        for k, P in (('A', A), ('B', B)):
            p = at(P, t); c, s = math.cos(p[2]), math.sin(p[2]); pts = np.c_[p[0] + c * bx - s * by, p[1] + s * bx + c * by]
            if k not in ref: ref[k] = cKDTree(pts)
            d, _ = ref[k].query(pts); cons[k].append(np.median(d) * 100)
    out[bag] = (res, ts, cons, OB[:, 0] - t0, w)
fig = plt.figure(figsize=(14, 9.6), dpi=100); gs = fig.add_gridspec(2, 3)
# ① rot3 궤적
ax = fig.add_subplot(gs[0, 0]); res = out['rot3'][0]
for k, lab in (('A', 'EKF A(지금)'), ('B', 'EKF B(+ rf2o)')):
    t, x, y = res[k]; ax.plot(x, y, '-' if k != 'rf2o' else ':', color=C[k], lw=2 if k != 'rf2o' else 1.3, label=lab); ax.plot(x[-1], y[-1], 'o', color=C[k], ms=7, mfc='none' if k == 'A' else C[k], mew=2)
ax.plot(-0.275, -0.245, 'X', color='k', ms=13, label='줄자 끝 (-0.275, -0.245)')
tb, xb, yb = res['B']; ax.annotate('', xy=(-0.275, -0.245), xytext=(xb[-1], yb[-1]), arrowprops=dict(arrowstyle='<->', color='k', lw=1))
ax.text((xb[-1] - 0.275) / 2 + 0.01, (yb[-1] - 0.245) / 2, '%.1f cm' % (100 * math.hypot(xb[-1] + 0.275, yb[-1] + 0.245)), fontsize=9)
ax.plot(0, 0, 's', color='k', ms=6); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(fontsize=7, loc='upper left')
ax.set_xlabel('시작 자세 기준 앞(+) m'); ax.set_ylabel('왼(+) m'); ax.set_title('rot3 궤적과 끝점 (줄자 = 정답)', fontsize=10)
# ② 누적 이동 크기 시계열 (rot3, rot2)
for j, bag in enumerate(('rot3', 'rot2')):
    ax = fig.add_subplot(gs[0, 1 + j]); res, ts, cons, tw, w = out[bag]
    for k, lab in (('A', 'EKF A'), ('B', 'EKF B'), ('rf2o', 'rf2o 단독 자세(라이다 위치라 회전 중 출렁임)')):
        t, x, y = res[k]; ax.plot(t, np.hypot(x, y) * 100, '-' if k != 'rf2o' else ':', color=C[k], lw=2 if k != 'rf2o' else 1.3, label=lab)
    if bag == 'rot3': ax.axhline(36.8, color='k', ls='--', lw=1); ax.text(1, 37.8, '줄자 36.8 cm (끝)', fontsize=8)
    ymax = ax.get_ylim()[1]
    for i in range(len(tw) - 1):
        if abs(w[i]) > 0.15: ax.axvspan(tw[i], tw[i + 1], color='#e8e8e8', lw=0, zorder=0)
    ax.set_xlabel('시험 시작 후 s (회색 = 회전 중)'); ax.set_ylabel('시작점에서 거리 (cm)'); ax.grid(alpha=.3); ax.legend(fontsize=7, loc='upper left')
    ax.set_title('%s: 누적 이동을 누가 얼마나 봤나%s' % (bag, '' if bag == 'rot3' else ' (줄자 없음)'), fontsize=10)
# ③ 스캔 일관성
for j, bag in enumerate(('rot3', 'rot2')):
    ax = fig.add_subplot(gs[1, j]); res, ts, cons, tw, w = out[bag]
    for k, lab in (('A', 'EKF A'), ('B', 'EKF B')):
        ax.plot(ts, cons[k], '-o', ms=3, color=C[k], lw=1.6, label='%s — 끝 %.1f cm' % (lab, cons[k][-1]))
    for i in range(len(tw) - 1):
        if abs(w[i]) > 0.15: ax.axvspan(tw[i], tw[i + 1], color='#e8e8e8', lw=0, zorder=0)
    ax.set_xlabel('시험 시작 후 s'); ax.set_ylabel('첫 스캔과의 어긋남 중앙 (cm)'); ax.grid(alpha=.3); ax.legend(fontsize=8)
    ax.set_title('%s 독립 검사: 각 EKF 자세로 놓은 벽이 제자리에 있나' % bag, fontsize=10)
ax = fig.add_subplot(gs[1, 2]); ax.axis('off')
r3 = out['rot3'][0]; eA = math.hypot(r3['A'][1][-1] + 0.275, r3['A'][2][-1] + 0.245); eB = math.hypot(r3['B'][1][-1] + 0.275, r3['B'][2][-1] + 0.245)
ax.text(0, 0.95, '읽는 법', fontsize=11, fontweight='bold', va='top')
ax.text(0, 0.85, ('· 위 왼쪽: 끝점이 X(줄자)에 가까울수록 EKF 가 실제\n  미끄러짐을 잘 인식. A 오차 %.1f cm → B 오차 %.1f cm.\n\n'
                  '· 위 가운데·오른쪽: 회색(회전 중)마다 B 가 rf2o 를 따라\n  계단처럼 늘어남 = 회전할 때 생기는 미끄러짐을 그때그때\n  반영. A 는 0 근처에 머묾.\n\n'
                  '· 아래: 줄자 없이도 쓸 수 있는 검사. 정적인 벽을 각 EKF\n  자세로 놓았을 때, 미끄러짐을 놓치면(A) 벽이 시간이\n  지날수록 어긋남. B 는 낮게 유지.\n\n'
                  '· 오프라인 재생(R2 5 차 설정) 결과이며, 라이브 확인은 R3.') % (eA * 100, eB * 100), fontsize=9.5, va='top')
fig.suptitle('rf2o 로 vx·vy 를 보정한 EKF B 는 회전 중 미끄러짐을 인식했나', fontsize=13)
fig.tight_layout(); fig.savefig(FIG + 'ekfB_slip.png'); print('A %.1f B %.1f' % (eA * 100, eB * 100), {b: (round(out[b][2]['A'][-1], 1), round(out[b][2]['B'][-1], 1)) for b in out})
