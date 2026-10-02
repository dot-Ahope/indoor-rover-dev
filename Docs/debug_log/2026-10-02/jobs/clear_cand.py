# 10-02 §5: 경로 계획용 격자에서 지울 후보(움직이는 물체) 찾기 — office_v3 점유 칸 중 이후 주행에서 "비어 있음" 증거가 쌓인 칸
#   증거 ① 라이다: 기록 자세(map)로 빔을 지도 위에 그어 칸마다 통과(pass)·맞음(hit) 횟수. 자세가 틀린 스캔은 스캔-지도 잔차 > GATE 로 버림.
#   증거 ② nvblox 슬라이스(6~30 cm): 관측된 칸 중 거리 > 0.10 m = 빈 칸(free), ≤ 0.05 m = 장애물(occ). odom → map 은 기록 map→odom.
#   판정(칸): 지도 점유 & [라이다 pass ≥ 5 & hit 비율 ≤ 0.1] → L, & [nv free ≥ 3 & nv occ = 0] → N.  A = L&N, B = L 만, C = N 만(라이다 pass < 5).
#   보수 규칙: 라이다 hit ≥ 3 인 '확인된 벽' 칸에서 1 칸(5 cm) 안은 후보에서 뺌 — 자세 오차 5 cm 로 벽 가장자리를 깎지 않기 위해(병목 여유 7~12 cm).
import glob, math, sys, numpy as np
from PIL import Image
from scipy import ndimage
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v3.pgm')); H, W = im.shape; OX, OY, RES = -5.29, -6.96, 0.05
OCC = im == 0
dt = ndimage.distance_transform_edt(~OCC) * RES
LIDAR_X, LIDAR_YAW = 0.152, math.pi - 0.04677
GATE, STEP, RMAX, NEAR, TAIL = 0.06, 0.025, 6.0, 0.25, 0.15
def cell(x, y):
    j = np.floor((x - OX) / RES).astype(int); i = H - 1 - np.floor((y - OY) / RES).astype(int); return i, j
def resid(px, py):
    i, j = cell(px, py); ok = (i >= 0) & (i < H) & (j >= 0) & (j < W)
    d = np.full(px.shape, 0.3); d[ok] = np.minimum(dt[i[ok], j[ok]], 0.3); return math.sqrt(np.mean(d ** 2))
pas = np.zeros(H * W, np.int64); hit = np.zeros(H * W, np.int64); nvf = np.zeros(H * W, np.int64); nvo = np.zeros(H * W, np.int64)
stat = []
for f in sorted(glob.glob(SP + r'\evid\*.npz')):
    Z = np.load(f, allow_pickle=True); amin, ainc, rmx, nb = Z['meta']; P = Z['poses']; R = Z['ranges'].astype(np.float32); T = Z['t']
    k = np.arange(0, int(nb), 2); ang0 = amin + ainc * k
    used = 0; good_t = []
    for (x, y, th), rr, t in zip(P, R[:, k], T):
        a = th + LIDAR_YAW + ang0; lx, ly = x + math.cos(th) * LIDAR_X, y + math.sin(th) * LIDAR_X
        ok = np.isfinite(rr) & (rr > 0.2)
        ex, ey = lx + rr[ok] * np.cos(a[ok]), ly + rr[ok] * np.sin(a[ok])
        if ok.sum() < 50 or resid(ex[rr[ok] < 6], ey[rr[ok] < 6]) > GATE: continue
        used += 1; good_t.append(t)
        # 맞음: 끝점(최대 거리 미만)
        hm = ok & (rr < min(rmx - 0.05, RMAX)); i, j = cell(lx + rr[hm] * np.cos(a[hm]), ly + rr[hm] * np.sin(a[hm])); v = (i >= 0) & (i < H) & (j >= 0) & (j < W)
        hit += np.bincount(i[v] * W + j[v], minlength=H * W)
        # 통과: NEAR ~ (끝점 − TAIL), 최대 RMAX. 반사가 안 돌아온 빔(inf·최대 거리)은 증거에서 뺌 — 1 차 시도에서 이 빔을 RMAX 까지
        #   통과로 셌더니 바깥벽 너머까지 '통과' 가 찍혀 벽 전체가 후보가 됐다(검은 표면·유리·각도 탓으로 반사가 안 온 빔은 '비어 있음' 증거가 아님)
        rr2 = np.where(np.isfinite(rr) & (rr < rmx - 0.05), rr, 0.0); rr2 = np.minimum(rr2 - TAIL, RMAX)
        s = np.arange(NEAR, RMAX, STEP); m = s[None, :] < rr2[:, None]
        px = lx + s[None, :] * np.cos(a)[:, None]; py = ly + s[None, :] * np.sin(a)[:, None]
        i, j = cell(px[m], py[m]); v = (i >= 0) & (i < H) & (j >= 0) & (j < W); idx = np.unique((i[v] * W + j[v]).reshape(-1))
        # 같은 빔이 한 칸을 여러 표본으로 지나가도 1 번으로: 빔별 고유화 대신 스캔별 고유화(스캔 하나 = 그 칸을 '봤다' 1 회)
        pas[idx] += 1
    gt = np.array(good_t); nsl = 0
    for d in Z['sl']:
        if not len(gt) or np.min(np.abs(gt - d['t'])) > 0.5: continue   # 자세가 맞은 스캔 근처 슬라이스만
        nsl += 1; arr = d['d'].astype(np.float32); ox, oy, res, unk = d['o']; tx, ty, tw = d['mo']; c, s_ = math.cos(tw), math.sin(tw)
        ii, jj = np.indices(arr.shape); obs = arr < unk * 0.5
        X = ox + (jj + .5) * res; Y = oy + (ii + .5) * res; mx, my = tx + c * X - s_ * Y, ty + s_ * X + c * Y
        for msk, acc in ((obs & (arr > 0.10), nvf), (obs & (arr <= 0.05), nvo)):
            i, j = cell(mx[msk], my[msk]); v = (i >= 0) & (i < H) & (j >= 0) & (j < W)
            acc += np.bincount(np.unique(i[v] * W + j[v]), minlength=H * W)
    stat.append((f.split('\\')[-1], len(P), used, nsl))
for s in stat: print('%-14s 스캔 %4d → 자세 통과 %4d (%.0f%%), nvblox 슬라이스 %d' % (s[0], s[1], s[2], 100 * s[2] / max(s[1], 1), s[3]))
pas, hit, nvf, nvo = [a.reshape(H, W) for a in (pas, hit, nvf, nvo)]
L = OCC & (pas >= 5) & (hit <= 0.1 * (pas + hit)); N = OCC & (nvf >= 3) & (nvo == 0)
solid = OCC & (hit >= 3); guard = ndimage.binary_dilation(solid, structure=np.ones((3, 3), bool))
A = L & N & ~guard; B = L & ~N & ~guard; C = N & ~L & (pas < 5) & ~guard
print('지도 점유 %d 칸 | 확인된 벽(hit ≥ 3) %d | 후보 A(라이다+nvblox) %d · B(라이다만) %d · C(nvblox만) %d | 벽 1 칸 안이라 뺀 L/N %d' % (
    OCC.sum(), solid.sum(), A.sum(), B.sum(), C.sum(), ((L | N) & guard).sum()))
lab, n = ndimage.label(A | B | C, structure=np.ones((3, 3), bool)); out = []
for k in range(1, n + 1):
    m = lab == k; ii, jj = np.where(m); cx = OX + (jj.mean() + .5) * RES; cy = OY + (H - 1 - ii.mean() + .5) * RES
    out.append((m.sum(), cx, cy, (A & m).sum(), (B & m).sum(), (C & m).sum(), int(pas[m].mean()), int(nvf[m].mean())))
out.sort(key=lambda r: -r[0])
print('묶음 %d 개 (3 칸 이상 %d)' % (n, sum(1 for r in out if r[0] >= 3)))
for q, r in enumerate([r for r in out if r[0] >= 3]):
    print('  #%-2d %3d 칸 중심 (%+.2f, %+.2f) A %d B %d C %d | 라이다 통과 평균 %d nv 빈칸 평균 %d' % ((q + 1,) + r))
np.savez(SP + r'\clear_cand.npz', pas=pas, hit=hit, nvf=nvf, nvo=nvo, A=A, B=B, C=C, solid=solid, lab=lab)
