# 10-01 §8.23: 센서가 새로 막은 칸(자홍)을 원인별로 — 그 칸에서 0.20 m(≈ 내접 0.175 + 셀) 안에
#   nvblox 장애물 칸이 있으면 '카메라', 라이다 점이 있으면 '라이다', 둘 다/둘 다 아님. 프레임 시점의 표시만 보므로
#   과거에 찍혀 남아 있는 칸(누적)은 '둘 다 아님'으로 나온다.
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree
R = np.load(r'f2a6\f2a8_viz.npz', allow_pickle=True)['recs']
im = np.array(Image.open(r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps\office_v2.pgm')); mr = 0.05; mox, moy = -5.29, -6.96; MH, MW = im.shape
d = ndimage.distance_transform_edt(im != 0) * mr
base = np.where(d <= 0.175, 253, np.where(d <= 0.70, 252 * np.exp(-2.0 * (d - 0.175)), 0)); base[im == 0] = 254
baseO = np.where(base >= 254, 100, np.where(base >= 253, 99, np.where(base <= 0, 0, 1 + 97 * (base - 1) / 251)))
yy, xx = np.mgrid[0:MH, 0:MW]; wx = mox + (xx + 0.5) * mr; wy = moy + (MH - 1 - yy + 0.5) * mr
roi = (wx > -2.5) & (wx < 4.3) & (wy > -6.1) & (wy < -1.2)
mid = (wx > 0.6) & (wx < 1.5) & (wy > -3.1) & (wy < -2.1)   # 가운데 입구(+47 s 덩어리)
print(' t | 새로 막힌 칸(ROI) | 카메라만 · 라이다만 · 둘 다 · 그때 근처 표시 없음(누적) | 가운데 입구 칸: 카메라·라이다·없음')
for k in (5, 20, 40, 45, 47, 50, 60, 80, 100, 125, 160, 200):
    rec = R[k]; g = rec['gcm'].astype(float); gox, goy, gres = rec['gcm_o']; GH, GW = g.shape
    gi = ((wy - goy) / gres).astype(int); gj = ((wx - gox) / gres).astype(int); ok = (gi >= 0) & (gi < GH) & (gj >= 0) & (gj < GW)
    G = np.full((MH, MW), -1.0); G[ok] = g[gi[ok], gj[ok]]
    nb = (G >= 99) & (baseO < 99) & roi; P = np.c_[wx[nb], wy[nb]]
    cam = np.zeros(len(P), bool); lid = np.zeros(len(P), bool)
    if 'nv' in rec:
        nv = rec['nv']; nox, noy, nres, unk = rec['nv_o']; oi, oj = np.where((nv <= 0.05) & (nv < unk * 0.5))
        if len(oi): cam = cKDTree(np.c_[nox + (oj + .5) * nres, noy + (oi + .5) * nres]).query(P, distance_upper_bound=0.2)[0] < 0.2
    if 'scan' in rec and len(rec['scan']): lid = cKDTree(rec['scan']).query(P, distance_upper_bound=0.2)[0] < 0.2
    m2 = mid[nb]
    print('%3.0f | %5d | %5d · %5d · %5d · %5d | %d · %d · %d' % (rec['t'], len(P), (cam & ~lid).sum(), (lid & ~cam).sum(), (cam & lid).sum(), (~cam & ~lid).sum(),
          (cam & m2).sum(), (lid & m2 & ~cam).sum(), (m2 & ~cam & ~lid).sum()))
