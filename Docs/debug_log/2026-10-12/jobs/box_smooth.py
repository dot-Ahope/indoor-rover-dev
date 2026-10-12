# 10-12 §2: 복귀 때 상자 ② 주변(map x 2.6 → 0.4)에서 '매끄럽지 못한' 구간 분석. 인자: 이름=npz ...
#   1 s 표: 자세, 지령 v·w(1 s 평균·최소), 차체 외곽 ↔ 로컬 치명 칸 최소 거리, 차체 안 내접 칸 수, 그 1 s 안 새 경로 수와 경로의 옆 이동(로버 앞 0.3~1.0 m 구간).
#   요약: 평균 속도, 느린 시간(v < 0.04), 후진 시간, |w| > 0.1 부호 반전 횟수, 경로 옆 이동 > 0.10 m 횟수.
import sys, math, numpy as np
HL, HW = 0.25, 0.165
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
for arg in sys.argv[1:]:
    nm, f = arg.split('='); z = np.load(f, allow_pickle=True); tr, mo, cmd = z['traj'], z['mo'], z['cmd']
    pt, pn, pxy = z['plan_t'], z['plan_n'], z['plan_xy']; ps = np.r_[0, np.cumsum(pn)]
    lt, lc, lm = z['lcm_t'], z['lcm'], z['lcm_meta']
    # 복귀 구간: 마지막 목표(끝점이 원점 근처인 경로)가 시작된 뒤 x 가 2.6 아래로 내려온 때부터 0.4 까지
    g3 = [i for i in range(len(pt)) if math.hypot(*pxy[ps[i + 1] - 1]) < 0.3]; t3 = pt[g3[0]]
    k = (tr[:, 0] >= t3) & (tr[:, 1] <= 2.6) & (tr[:, 1] >= 0.4); T0, T1 = tr[k, 0][0], tr[k, 0][-1]
    print('== %s  복귀 상자 구간 %.0f s (x 2.6 → 0.4), 시작 %s' % (nm, T1 - T0, __import__('time').strftime('%H:%M:%S', __import__('time').localtime(T0))))
    print('   t s | map x y yaw | v 평균/최소  w 평균 | 치명까지 m | 차체 안 내접 | 새 경로 · 옆 이동 m')
    prev = None; rows = []; flips = 0; lastsign = 0; jumps = 0
    for t in np.arange(T0, T1, 1.0):
        i = np.searchsorted(tr[:, 0], t); x, y, th = tr[i, 1:4]
        c = cmd[(cmd[:, 0] >= t) & (cmd[:, 0] < t + 1)]
        j = min(np.searchsorted(mo[:, 0], t), len(mo) - 1); mx, my, mth = mo[j, 1:4]
        # map → odom 로 로버 자세
        cm, sm = math.cos(-mth), math.sin(-mth); ox = cm * (x - mx) - sm * (y - my); oy = sm * (x - mx) + cm * (y - my); oth = th - mth
        li = max(np.searchsorted(lt, t) - 1, 0); g = lc[li]; res, gx, gy = lm[li][:3]
        ys, xs = np.nonzero(g >= 99); px = gx + (xs + .5) * res; py = gy + (ys + .5) * res; val = g[ys, xs]
        co, so = math.cos(oth), math.sin(oth); u = co * (px - ox) + so * (py - oy); v_ = -so * (px - ox) + co * (py - oy)
        d = np.hypot(np.maximum(np.abs(u) - HL, 0), np.maximum(np.abs(v_) - HW, 0))
        dl = d[val >= 100].min() if (val >= 100).any() else 9.0; nin = int(((val == 99) & (d == 0)).sum())
        # 경로 옆 이동
        ids = [q for q in range(len(pt)) if t <= pt[q] < t + 1]; sh = 0.0
        for q in ids:
            P = pxy[ps[q]:ps[q + 1]]; dr = np.hypot(P[:, 0] - x, P[:, 1] - y); seg = P[(dr > 0.3) & (dr < 1.0)]
            if prev is not None and len(seg) and len(prev): sh = max(sh, float(np.median([np.hypot(prev[:, 0] - a, prev[:, 1] - b).min() for a, b in seg])))
            if len(seg): prev = seg
        if sh > 0.10: jumps += 1
        for w in c[:, 2]:
            s = 1 if w > 0.1 else (-1 if w < -0.1 else 0)
            if s and lastsign and s != lastsign: flips += 1
            if s: lastsign = s
        rows.append((c[:, 1].mean() if len(c) else 0, c[:, 1].min() if len(c) else 0, dl, nin))
        print('  %5.0f | %.2f %+.2f %+5.0f° | %+.3f/%+.3f %+.2f | %.2f | %2d | %d · %.2f' % (t - T0, x, y, math.degrees(wrap(th)), rows[-1][0], rows[-1][1], c[:, 2].mean() if len(c) else 0, dl, nin, len(ids), sh))
    R = np.array(rows)
    print('   요약: 평균 v %.3f m/s · 느린 시간(v<0.04) %d s · 후진 포함 %d s · w 부호 반전 %d 회 · 경로 옆 이동>0.10 m %d 회 · 치명까지 최소 %.2f m · 차체 안 내접 있던 시간 %d s' % (
        R[:, 0].mean(), (R[:, 0] < 0.04).sum(), (R[:, 1] < -0.005).sum(), flips, jumps, R[:, 2].min(), (R[:, 3] > 0).sum()))
