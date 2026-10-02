# 10-02 §11: 통제 회전 시험 번짐 — 차체 기준 좌표로 라이다(진실)·로컬 치명·nvblox 장애의 외곽 최근접 거리, 옛 칸 수
import sys, numpy as np, math
L = np.load(sys.argv[1], allow_pickle=True)['recs']
def gap(bx, by):
    dx = np.where(bx > 0, np.maximum(bx - 0.262, 0), np.maximum(-bx - 0.248, 0)); dy = np.maximum(np.abs(by) - 0.165, 0); return np.hypot(dx, dy)
def to_base(px, py, X, Y, T):
    c, s = math.cos(T), math.sin(T); return c * (px - X) + s * (py - Y), -s * (px - X) + c * (py - Y)
out = []
P0 = None
for r in L:
    if 'scan' not in r or 'nv' not in r: continue
    X, Y, T = r['pose']; tx, ty, tw = r['mo']; c, s = math.cos(tw), math.sin(tw)
    # base 의 odom 자세 = map→odom 역변환
    ox_ = c * (X - tx) + s * (Y - ty); oy_ = -s * (X - tx) + c * (Y - ty); oth = T - tw
    if P0 is None: P0 = (X, Y, ox_, oy_)
    sx, sy = to_base(r['scan'][:, 0].astype(float), r['scan'][:, 1].astype(float), X, Y, T); gl = gap(sx, sy); near = gl < 0.6
    g = r['gcm']; gx0, gy0, res = r['gcm_o']; ii, jj = np.where(g >= 100); lx, ly = to_base(gx0 + (jj + .5) * res, gy0 + (ii + .5) * res, ox_, oy_, oth); gc = gap(lx, ly)
    nv = r['nv']; nox, noy, nres, unk = r['nv_o']; ii, jj = np.where((nv <= 0.05) & (nv < unk * .5)); vx, vy = to_base(nox + (jj + .5) * nres, noy + (ii + .5) * nres, ox_, oy_, oth); gn = gap(vx, vy)
    # 옛 칸: 외곽 0.6 m 안 로컬 치명 칸 중 0.10 m 안에 라이다 점·nvblox 장애 둘 다 없는 것
    m = gc < 0.6; stale = 0; nvsup = 0
    if m.any():
        dl = np.min(np.hypot(lx[m][:, None] - sx[near][None, :], ly[m][:, None] - sy[near][None, :]), axis=1) if near.any() else np.full(m.sum(), 9.)
        dn = np.min(np.hypot(lx[m][:, None] - vx[None, :], ly[m][:, None] - vy[None, :]), axis=1) if len(vx) else np.full(m.sum(), 9.)
        stale = int(((dl > 0.10) & (dn > 0.10)).sum()); nvsup = int(((dl > 0.10) & (dn <= 0.10)).sum())
    out.append((r['t'], math.degrees(T), gl.min(), gc.min() if len(gc) else np.nan, gn.min() if len(gn) else np.nan, int(m.sum()), stale, nvsup,
                math.hypot(X - P0[0], Y - P0[1]), math.hypot(ox_ - P0[2], oy_ - P0[3])))
print('  t     θ    | 외곽 최근접: 라이다 / 로컬치명 / nvblox | 번짐(라이다−로컬) | 0.6 m 안 치명칸·옛칸(근거 없음)·nvblox만 근거 | 누적 이동 map / odom')
for o in out[::2]:
    print('%5.1f %5.0f° | %.3f / %.3f / %.3f | %+.3f | %3d · %3d · %3d | %.3f / %.3f' % (o[:5] + (o[2] - o[3],) + o[5:]))
a = np.array(out); print('번짐 최대 %.3f m, 마지막 %.3f m | 옛칸 최대 %d | 끝 누적 이동 map %.3f · odom %.3f m' % (np.nanmax(a[:, 2] - a[:, 3]), a[-1, 2] - a[-1, 3], a[:, 6].max(), a[-1, 8], a[-1, 9]))
