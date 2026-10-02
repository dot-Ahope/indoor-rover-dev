# 10-02 §14 R2 판정 계산 — EKF A/B(+ 라이브 EKF) 를 줄자·SLAM·구석 벽 일관성으로 비교
import numpy as np, math
SP = 'f2a6/'
LX, LY = 0.152, math.pi - 0.04677
def srt(a): return a[np.argsort(a[:, 0])] if len(a) else a
def at(A, t): i = min(max(np.searchsorted(A[:, 0], t) - 1, 0), len(A) - 1); return A[i, 1:4]
def disp(P, ta, tb):
    p0, p1 = at(P, ta), at(P, tb); c, s = math.cos(p0[2]), math.sin(p0[2]); d = p1[:2] - p0[:2]; return c * d[0] + s * d[1], -s * d[0] + c * d[1]
def load(b):
    Z = np.load(SP + 'r2_%s.npz' % b, allow_pickle=True); D = {k: (srt(Z[k]) if k in ('A', 'B', 'mo', 'ob') else Z[k]) for k in Z.files}
    if D['A'].ndim < 2 or len(D['A']) == 0: print('   (%s: 재생 EKF A 출력 없음 — 같은 설정인 라이브 EKF 로 대신)' % b); D['A'] = D['ob']
    return D
# R2-a rot3
Z = load('rot3'); t0, t1 = Z['ob'][0, 0] + 1, Z['ob'][-1, 0] - 1
print('R2-a rot3 끝 이동(시작 자세 기준, 앞+/왼+) — 줄자 (-0.275, -0.245)')
for k in ('A', 'B', 'ob'):
    dx, dy = disp(Z[k], t0, t1); print('   %-4s (%+.3f, %+.3f) 크기 %.3f | 줄자와 차 %.3f m' % ({'ob': '라이브'}.get(k, k), dx, dy, math.hypot(dx, dy), math.hypot(dx + 0.275, dy + 0.245)))
Z = load('rot2'); t0, t1 = Z['ob'][0, 0] + 1, Z['ob'][-1, 0] - 1
print('   (rot2, 줄자 없음) ' + ' · '.join('%s %.3f m' % (k, math.hypot(*disp(Z[k], t0, t1))) for k in ('A', 'B', 'ob')))
# R2-b f2b4 직진 축척
Z = load('f2b4'); MO, OB = Z['mo'], Z['ob']
def mapP(t):
    mx, my, mt = at(MO, t); ox, oy, ot = at(OB, t); c, s = math.cos(mt), math.sin(mt); return np.array([mx + c * ox - s * oy, my + s * ox + c * oy, mt + ot])
R = []; t = OB[0, 0] + 2
while t < OB[-1, 0] - 3:
    e0, e1 = at(OB, t), at(OB, t + 3)
    if abs(math.degrees(e1[2] - e0[2])) < 3 and math.hypot(*(e1[:2] - e0[:2])) > 0.15:
        m0, m1 = mapP(t), mapP(t + 3); sl = math.hypot(*(m1[:2] - m0[:2]))
        R.append([math.hypot(*(at(Z[k], t + 3)[:2] - at(Z[k], t)[:2])) / sl for k in ('A', 'B', 'ob')])
    t += 3
R = np.array(R); print('R2-b f2b4 직진 3 s 창 %d 개, 이동/SLAM 중앙: A %.3f · B %.3f · 라이브 %.3f' % (len(R), *np.median(R, axis=0)))
# R2-c f2b3 구석 기동: 서쪽 구조물 점(라이브 map 기준 선택)을 각 EKF odom 좌표로 → 중심의 흔들림
Z = load('f2b3'); MO, OB = Z['mo'], Z['ob']
ta, tb = 1790915130 + 26, 1790915130 + 49
C = {k: [] for k in ('A', 'B', 'ob', 'map')}; F = {k: [] for k in ('A', 'B', 'ob', 'map')}
for t, rr, (amin, ainc) in zip(Z['st'], Z['sr'], Z['sa']):
    if t < ta or t > tb: continue
    a = amin + ainc * np.arange(len(rr)) + LY; ok = np.isfinite(rr) & (rr > 0.2) & (rr < 3)
    bx, by = LX + rr[ok] * np.cos(a[ok]), rr[ok] * np.sin(a[ok])
    mp = mapP(t); c, s = math.cos(mp[2]), math.sin(mp[2]); mx, my = mp[0] + c * bx - s * by, mp[1] + s * bx + c * by
    sel = (my > -5.95) & (my < -5.35) & (mx < -1.6) & (mx > -2.1)
    if sel.sum() < 5: continue
    for k in C:
        p = mp if k == 'map' else at(Z[k], t); c, s = math.cos(p[2]), math.sin(p[2]); ox, oy = p[0] + c * bx[sel] - s * by[sel], p[1] + s * bx[sel] + c * by[sel]
        C[k].append((ox.mean(), oy.mean()))
        # 안쪽 면(로버 쪽 가장자리): 시작 자세의 map 방향 기준 x 95 백분위 — 보이는 부분이 바뀌어도 덜 흔들리는 지표
        F[k].append(np.percentile(ox, 95))
print('R2-c f2b3 구석 기동 서쪽 구조물 중심(odom 좌표) 흔들림, 표본 %d' % len(C['A']))
for k in C:
    a = np.array(C[k]); d = np.hypot(a[:, 0] - a[:, 0].mean(), a[:, 1] - a[:, 1].mean())
    print('   %-4s 범위 x %.3f · y %.3f m, 평균에서 최대 %.3f m | 안쪽 면(x 95%%) 범위 %.3f m' % ({'ob': '라이브', 'map': 'SLAM'}.get(k, k), np.ptp(a[:, 0]), np.ptp(a[:, 1]), d.max(), np.ptp(F[k])))
