# 10-02 하루 실험 시각화 — rf2o·회전 미끄러짐·번짐·R2 A/B
import numpy as np, math, matplotlib, sys, io, re, contextlib, datetime
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
FIG = r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\figures\2026-10-02_'
C = {'A': '#c05621', 'B': '#2f855a', 'live': '#888888', 'slam': '#2b6cb0', 'rf2o': '#805ad5', 'tape': '#000000'}


def srt(a): return a[np.argsort(a[:, 0])]
def at(A, t): i = min(max(np.searchsorted(A[:, 0], t) - 1, 0), len(A) - 1); return A[i, 1:4]


def inframe(P, p0):
    c, s = math.cos(p0[2]), math.sin(p0[2]); d = P[:, 1:3] - p0[:2]; return c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1]


def mapper(MO, OB):
    def mapP(t):
        mx, my, mt = at(MO, t); ox, oy, ot = at(OB, t); c, s = math.cos(mt), math.sin(mt)
        return np.array([mx + c * ox - s * oy, my + s * ox + c * oy, mt + ot])
    return mapP


# ① rot3 궤적(시작 자세 기준)
Z = np.load('f2a6/r2_rot3.npz'); A, B, MO, OB = srt(Z['A']), srt(Z['B']), srt(Z['mo']), srt(Z['ob']); mapP = mapper(MO, OB)
t0, t1 = OB[0, 0] + 1, OB[-1, 0] - 1
SL = np.array([[t, *mapP(t)] for t in np.arange(t0, t1, 0.1)])
R = srt(np.load('f2a6/rf2o_rot3.npz')['rf']); R = R[(R[:, 0] >= t0) & (R[:, 0] <= t1)]
fig, ax = plt.subplots(figsize=(7.2, 6.2), dpi=110)
for P, col, lab in ((A, C['A'], 'EKF A(지금) — 휠·자이로'), (B, C['B'], 'EKF B — + rf2o 게이트'), (SL, C['slam'], 'SLAM(위치 추정)')):
    P = P[(P[:, 0] >= t0) & (P[:, 0] <= t1)]; x, y = inframe(P, P[0, 1:4]); ax.plot(x, y, '-', color=col, lw=2, label=lab); ax.plot(x[-1], y[-1], 'o', color=col, ms=7 if col != C['A'] else 11, mfc='none' if col == C['A'] else col, mew=2.5)
x, y = inframe(R, R[0, 1:4]); ax.plot(-x, -y, ':', color=C['rf2o'], lw=1.6, label='rf2o 단독(부호 보정)'); ax.plot(-x[-1], -y[-1], 'o', color=C['rf2o'], ms=6)
ax.plot(-0.275, -0.245, 'X', color=C['tape'], ms=13, label='줄자 실측 끝 (-0.275, -0.245)')
ax.plot(0, 0, 's', color='k', ms=6); ax.text(0.01, 0.015, '시작', fontsize=9)
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlabel('시작 자세 기준 앞(+) / 뒤(-) m'); ax.set_ylabel('왼(+) / 오른(-) m'); ax.legend(fontsize=8, loc='upper left')
ax.set_title('rot3: 제자리 ±90° × 3 동안 로버가 실제로 미끄러진 거리 — 누가 봤나', fontsize=10)
fig.tight_layout(); fig.savefig(FIG + 'rot3_paths.png'); plt.close(fig)


# ② rot2(odom) vs rot3(map) 번짐·옛 칸 시계열 — smear_rot.py 를 그대로 돌려 줄을 읽음
def parse(f, frame):
    sys.argv = ['x', f, frame]; buf = io.StringIO()
    src = open('smear_rot.py', encoding='utf-8').read().replace('for o in out[::2]:', 'for o in out:')
    with contextlib.redirect_stdout(buf): exec(src, {'__name__': '__main__'})
    T, SM, ST = [], [], []
    for l in buf.getvalue().splitlines():
        m = re.match(r'\s*([\d.]+)\s+(-?\d+)°\s*\|\s*([\d.]+) / ([\d.]+) / ([\d.]+) \| ([+-][\d.]+) \|\s*(\d+) ·\s*(\d+)', l)
        if m: T.append(float(m.group(1))); SM.append(float(m.group(6)) * 100); ST.append(int(m.group(8)))
    return np.array(T), np.array(SM), np.array(ST)


fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), dpi=105)
for f, fr, col, lab in (('f2a6/rot2_lviz.npz', 'odom', C['A'], 'rot2: 로컬 코스트맵 odom(지금)'), ('f2a6/rot3_lviz.npz', 'map', C['slam'], 'rot3: 로컬 코스트맵 map(시험)')):
    T, SM, ST = parse(f, fr); ax[0].plot(T, SM, '-', color=col, lw=1.6, label=lab); ax[1].plot(T, ST, '-', color=col, lw=1.8, label=lab)
ax[0].axhline(0, color='#999', lw=.8); ax[0].set_ylabel('번짐 = 라이다 - 로컬 치명 (cm)'); ax[0].set_xlabel('시험 시작 후 s')
ax[0].set_title('가장 가까운 장애물이 실제보다 가깝게 표시된 정도', fontsize=10); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].set_ylabel('근거 없는 옛 치명 칸 수'); ax[1].set_xlabel('시험 시작 후 s')
ax[1].set_title('지금 라이다·카메라 근거가 없는 장애물 칸(외곽 0.6 m 안)', fontsize=10); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig(FIG + 'smear_rot23.png'); plt.close(fig)

# ③ f2b3 구석 기동: 로버 쪽 벽 면(x 95 %)을 각 자세로
Z = np.load('f2a6/r2_f2b3.npz', allow_pickle=True); A, B, MO, OB = srt(Z['A']), srt(Z['B']), srt(Z['mo']), srt(Z['ob']); mapP = mapper(MO, OB)
T0 = datetime.datetime(2026, 10, 2, 13, 25, 30).timestamp(); LX, LY = 0.152, math.pi - 0.04677
S = {k: [] for k in ('A', 'B', 'slam')}; TT = []
for t, rr, (amin, ainc) in zip(Z['st'], Z['sr'], Z['sa']):
    if t < T0 + 20 or t > T0 + 55: continue
    a = amin + ainc * np.arange(len(rr)) + LY; ok = np.isfinite(rr) & (rr > 0.2) & (rr < 3); bx, by = LX + rr[ok] * np.cos(a[ok]), rr[ok] * np.sin(a[ok])
    mp = mapP(t); c, s = math.cos(mp[2]), math.sin(mp[2]); mx, my = mp[0] + c * bx - s * by, mp[1] + s * bx + c * by
    sel = (my > -5.95) & (my < -5.35) & (mx < -1.6) & (mx > -2.1)
    if sel.sum() < 5: continue
    TT.append(t - T0)
    for k, P in (('A', A), ('B', B), ('slam', None)):
        p = mp if k == 'slam' else at(P, t); c, s = math.cos(p[2]), math.sin(p[2]); S[k].append(np.percentile(p[0] + c * bx[sel] - s * by[sel], 95))
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=105)
for k, lab in (('A', 'EKF A(지금)'), ('B', 'EKF B(+ rf2o)'), ('slam', 'SLAM(기준)')):
    v = np.array(S[k]); ax.plot(TT, (v - v[0]) * 100, '-o', ms=3, color=C[k], lw=1.6, label='%s — 범위 %.1f cm' % (lab, np.ptp(v) * 100))
ax.axvspan(26, 49, color='#eee', zorder=0)
ax.set_xlabel('13:25:30 기준 s (회색 = 구석 기동, 후진·회전 섞임)'); ax.set_ylabel('로버 쪽 벽 면 위치 변화 (cm, 시작 대비)'); ax.grid(alpha=.3); ax.legend(fontsize=8)
ax.set_title('f2b3 남서 구석: 같은 벽이 각 주행계 좌표에서 얼마나 움직여 보였나 (작을수록 번짐 작음)', fontsize=10)
fig.tight_layout(); fig.savefig(FIG + 'f2b3_wall_AB.png'); plt.close(fig)

# ④ R2 회차별 진행
runs = ['3차\n휠 정상', '4차\n회전 중 휠 σ 0.3', '5차\nG1 시각 맞춤']; err = [29.7, 3.8, 4.3]; g1 = [37, 37, 0.1]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6), dpi=105)
ax[0].bar(runs, err, color=['#bbb', C['B'], C['B']]); ax[0].axhline(5, color='k', ls='--', lw=1); ax[0].text(2.4, 5.6, '기준 5 cm', fontsize=8, ha='right')
ax[0].set_ylabel('rot3 끝 위치 - 줄자 (cm)'); ax[0].set_title('EKF B 의 회전 미끄러짐 오차 (A 는 36.9 cm)', fontsize=10)
for i, v in enumerate(err): ax[0].text(i, v + 0.6, '%.1f' % v, ha='center', fontsize=9)
ax[1].bar(runs, g1, color=['#bbb', '#bbb', C['B']]); ax[1].set_ylabel('G1 거부율 (%) — f2b3, 사람 없음'); ax[1].set_title('자이로 일치 검사의 오거부', fontsize=10)
for i, v in enumerate(g1): ax[1].text(i, v + 0.8, '%.1f' % v, ha='center', fontsize=9)
fig.tight_layout(); fig.savefig(FIG + 'r2_runs.png'); plt.close(fig)
print('ok')
