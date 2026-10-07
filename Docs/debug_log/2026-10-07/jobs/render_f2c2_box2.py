# 10-07 §2.5: 복귀 마지막 60 s — 로컬 코스트맵 치명 칸(라이다+nvblox, map 좌표로)을 라이다 점과 겹침 → 라이다에 없는 치명 칸 = 카메라만 본 낮은 물체(상자 후보)
import numpy as np, math, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
Z = np.load('x912_f2c2.npz'); T0 = 1791338894.0; G6 = T0 + 307.8; LX, LY = 0.152, math.pi - 0.04677; XB, XF, HW = -0.248, 0.262, 0.165
tr, mo = Z['traj'], Z['mo']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
def pose(t): j = np.argmin(np.abs(tr[:, 0] - t)); return tr[j, 1:]
def m2(t): i = np.argmin(np.abs(mo[:, 0] - t)); return mo[i, 1:]
L = []
for k, t in enumerate(Z['lcm_t']):
    if t < G6 + 60: continue
    g = Z['lcm'][k]; res, ox, oy = Z['lcm_meta'][k]; iy, ix = np.nonzero(g >= 100); wx, wy = ox + (ix + .5) * res, oy + (iy + .5) * res
    mx, my, mth = m2(t); c, s = math.cos(mth), math.sin(mth); L.append(np.c_[mx + c * wx - s * wy, my + s * wx + c * wy, np.full(len(wx), t - G6)])
L = np.vstack(L); P = []
for k, t in enumerate(Z['scan_t']):
    if t < G6 + 60: continue
    r = Z['scan_r'][k]; a0, da = Z['scan_a'][k]; a = a0 + da * np.arange(len(r)) + LY; ok = np.isfinite(r) & (r > .05) & (r < 3)
    bx, by = LX + r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]); x, y, th = pose(t); c, s = math.cos(th), math.sin(th); P.append(np.c_[x + c * bx - s * by, y + s * bx + c * by])
P = np.vstack(P)
# 라이다 점에서 7.5 cm 넘게 떨어진 치명 칸 = 카메라만 본 칸
from scipy.spatial import cKDTree
dd, _ = cKDTree(P).query(L[:, :2]); cam = dd > 0.075
print('치명 칸 표본 %d, 라이다 근처 아님 %d' % (len(L), cam.sum()))
H = np.round(L[cam, :2] / 0.05).astype(int); u, cnt = np.unique(H, axis=0, return_counts=True); top = np.argsort(-cnt)[:15]
for i in top: print('   카메라만 치명 (%.2f, %.2f) 로컬 표본 %d 회' % (u[i, 0] * .05, u[i, 1] * .05, cnt[i]))
fig, a = plt.subplots(figsize=(11, 7.5), dpi=110)
a.scatter(P[:, 0], P[:, 1], s=1, c='#aaa', label='라이다 점')
a.scatter(L[~cam, 0], L[~cam, 1], s=4, c='#555', marker='s', label='치명 칸(라이다 근처)')
sc = a.scatter(L[cam, 0], L[cam, 1], s=10, c=L[cam, 2], cmap='autumn', marker='s', label='치명 칸(라이다 없음 = 카메라)')
for k in np.flatnonzero(pt >= G6 - 1): Q = pxy[off[k]:off[k + 1]]; a.plot(Q[:, 0], Q[:, 1], '--', lw=1.2, label='계획 %+.0f s' % (pt[k] - G6))
cm = plt.get_cmap('viridis')
for t in np.arange(G6 + 60, G6 + 121, 2):
    x, y, th = pose(t); c, s = math.cos(th), math.sin(th); C = np.array([[XF, HW], [XF, -HW], [XB, -HW], [XB, HW], [XF, HW]])
    a.plot(x + c * C[:, 0] - s * C[:, 1], y + s * C[:, 0] + c * C[:, 1], color=cm((t - G6 - 60) / 60), lw=.9); a.plot([x, x + .3 * c], [y, y + .3 * s], color=cm((t - G6 - 60) / 60), lw=1.5)
a.plot(0, 0, 'k*', ms=12); a.set_aspect('equal'); a.set_xlim(-0.6, 3.0); a.set_ylim(-1.8, 0.9); a.grid(alpha=.3); a.legend(fontsize=7, loc='lower left')
plt.colorbar(sc, label='카메라 치명 칸이 보인 시각(목표 6 시작 뒤 s)', shrink=.7)
a.set_title('f2c2 복귀 마지막 60 s — 로컬 코스트맵 치명 칸(map 좌표) · 라이다 점 · 계획 경로 · 차체 외곽(2 s 마다)', fontsize=10)
fig.tight_layout(); fig.savefig('f2c2_box2.png'); print('ok')
