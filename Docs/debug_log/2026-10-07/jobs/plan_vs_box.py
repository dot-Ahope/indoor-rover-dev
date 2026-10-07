# 10-07 §10: fused_131646 구간 — 로컬(nvblox) 은 상자를 보는데 계획 경로가 그 위를 지나는가, 그때 전역 코스트맵(계획기가 보는 것)의 상자 칸 값은
import numpy as np, math
Z = np.load('fz_f2d2.npz'); E0, K0 = 1791346297.0, 13 * 3600 + 11 * 60 + 37
def kst(e): s = int(e - E0 + K0); return '%02d:%02d:%02d' % (s // 3600, s // 60 % 60, s % 60)
def at(X, t): i = min(max(np.searchsorted(X[:, 0], t), 0), len(X) - 1); return X[i, 1:4]
tr, mo = Z['traj'], Z['mo']; pt, pn, pxy = Z['plan_t'], Z['plan_n'], Z['plan_xy']; off = np.r_[0, np.cumsum(pn)]
print('계획 발행 시각:', ' '.join(kst(t) for t in pt))
for k, t in enumerate(Z['lcm_t']):
    if not (E0 + 330 <= t <= E0 + 440) or k % 4: continue          # 13:17:07~13:18:57, 2 s 간격
    g = Z['lcm'][k].astype(np.int16); r, ox, oy = Z['lcm_meta'][k]; mx, my, mth = at(mo, t); c, s = math.cos(mth), math.sin(mth)
    iy, ix = np.nonzero(g >= 100); wx, wy = ox + (ix + .5) * r, oy + (iy + .5) * r; LX_, LY_ = mx + c * wx - s * wy, my + s * wx + c * wy
    box = (LX_ > 1.0) & (LX_ < 1.8) & (LY_ > -0.6) & (LY_ < 0.25)       # 상자 ①·② 근처 로컬 치명 칸
    i = np.searchsorted(pt, t) - 1; P = pxy[off[i]:off[i + 1]]; x, y, th = at(tr, t)
    j = np.argmin(np.hypot(P[:, 0] - x, P[:, 1] - y)); Pa = P[j:]                     # 로버 앞쪽 남은 경로
    dmin = np.hypot(Pa[:, None, 0] - LX_[box][None], Pa[:, None, 1] - LY_[box][None]).min() if box.any() and len(Pa) else np.nan
    gi = np.searchsorted(Z['gcm_t'], t) - 1; G = Z['gcm'][gi].astype(np.int16); gr, gox, goy = Z['gcm_meta'][gi]
    gv = G[((LY_[box] - goy) / gr).astype(int), ((LX_[box] - gox) / gr).astype(int)] if box.any() else np.array([])
    print('%s 로버 (%.2f,%.2f) | 로컬 상자 근처 치명 %3d | 남은 경로 ↔ 그 칸 최소 %.2f m (차체 반폭 0.165) | 같은 칸 전역 값: 치명 %d · 내접 %d · <99 %d | 계획 %s' % (
        kst(t), x, y, box.sum(), dmin, (gv >= 100).sum(), (gv == 99).sum(), (gv < 99).sum(), kst(pt[i])))
# 재계획 직후(13:18:01) 로컬 치명인데 전역 < 99 인 칸 위치, 그리고 새 경로가 그 칸에서 얼마나 떨어져 지나가나
t = E0 + 384.0; k = np.searchsorted(Z['lcm_t'], t); g = Z['lcm'][k].astype(np.int16); r, ox, oy = Z['lcm_meta'][k]; mx, my, mth = at(mo, Z['lcm_t'][k]); c, s = math.cos(mth), math.sin(mth)
iy, ix = np.nonzero(g >= 100); wx, wy = ox + (ix + .5) * r, oy + (iy + .5) * r; X, Y = mx + c * wx - s * wy, my + s * wx + c * wy
gi = np.searchsorted(Z['gcm_t'], t) - 1; G = Z['gcm'][gi].astype(np.int16); gr, gox, goy = Z['gcm_meta'][gi]
gv = G[((Y - goy) / gr).astype(int), ((X - gox) / gr).astype(int)]; sel = (X > 0.9) & (X < 1.8) & (Y > -0.6) & (Y < 0.25)
i = np.searchsorted(pt, t) - 1; P = pxy[off[i]:off[i + 1]]
for lab, m in (('전역 치명(100)', sel & (gv >= 100)), ('전역 내접(99)', sel & (gv == 99)), ('전역 < 99(계획기는 통과 가능)', sel & (gv < 99))):
    if m.any(): d = np.hypot(P[:, None, 0] - X[m][None], P[:, None, 1] - Y[m][None]).min(0)
    print('%s %d 칸: x %.2f~%.2f · y %.2f~%.2f | 새 경로(13:17:58)까지 최소 %.2f m' % (lab, m.sum(), X[m].min(), X[m].max(), Y[m].min(), Y[m].max(), d.min()) if m.any() else lab + ' 0')
q = P[(P[:, 0] > 0.9) & (P[:, 0] < 1.8)]; print('새 경로가 x 0.9~1.8 에서 지나는 y: %.2f ~ %.2f' % (q[:, 1].min(), q[:, 1].max()))
