# 10-07 §1: G4 켠 뒤 남은 오차의 성격 — 회전 구간마다 진실 대용(T) 이동 vs 시험 B 이동(시작 자세 기준, cm).
#   |B| < |T| 이고 방향 같음 = 미끄러짐을 덜 봄(버림 비용), 방향 다름 = 걸러지지 않은 오염
import numpy as np, math, glob, os
def srt(a): return a[np.argsort(a[:, 0])]
for c in ('clean', 'A_walk08', 'C_sway', 'D_inout', 'E_fast'):
    out = []
    for tag, f in (('끔', 'occ/occm_%s.npz' % {'clean': 'X', 'A_walk08': 'A_walk08', 'C_sway': 'C_arc50_sway', 'D_inout': 'D_arc30_inout', 'E_fast': 'E_arc50_fast'}[c]), ('켬', 'g4/g4_%s.npz' % c)):
        if not os.path.exists(f): continue
        Z = np.load(f); B, T = srt(Z['B']), srt(Z['T']); t = T[:, 0]; yaw = np.unwrap(T[:, 3]); w = np.gradient(yaw, t)
        rot = np.abs(w) > 0.1; edges = np.flatnonzero(np.diff(rot.astype(int)))
        segs = [(t[a + 1], t[b]) for a, b in zip(edges[::2], edges[1::2]) if t[b] - t[a + 1] > 2][:6]
        def at(A, x): return A[min(np.searchsorted(A[:, 0], x), len(A) - 1), 1:3]
        r = []
        for s, e in segs:
            dT = at(T, e) - at(T, s); dB = at(B, e) - at(B, s); r.append((100 * np.linalg.norm(dT), 100 * np.linalg.norm(dB), 100 * np.linalg.norm(dB - dT)))
        out.append('%s: ' % tag + ' '.join('T%.0f/B%.0f/차%.0f' % x for x in r) + ' | 차 합 %.0f' % sum(x[2] for x in r))
    print('%-9s' % c, ' || '.join(out))
