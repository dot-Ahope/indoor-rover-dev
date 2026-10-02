# 10-02 §1: 후보 지도 판정 H-1(구멍)·H-3(옛 지도 보존)·H-4(남쪽 벽) — 기준 office_v2(·v1)
import sys, numpy as np, math
from PIL import Image
from scipy import ndimage
M = r'F:\6_Indoor_Rover\Rover\Docs\04_navigation\maps'
def load(p, ox=-5.29, oy=-6.96):
    im = np.array(Image.open(p)); return im, ox, oy
def world(im, ox, oy, x, y):
    H = im.shape[0]; i = H - 1 - int((y - oy) / 0.05); j = int((x - ox) / 0.05)
    return im[i, j] if 0 <= i < H and 0 <= j < im.shape[1] else 205
def region(im, ox, oy, x0, x1, y0, y1):
    return np.array([[world(im, ox, oy, x, y) for x in np.arange(x0 + .025, x1, .05)] for y in np.arange(y1 - .025, y0, -.05)])
cand = load(sys.argv[1]); v2 = load(M + r'\office_v2.pgm'); v1 = load(M + r'\office_v1.pgm', *[float(v) for v in open(M + r'\office_v1.yaml').read().split('origin:')[1].split(']')[0].strip(' [').split(',')[:2]])
print('크기 후보 %s, v2 %s' % (cand[0].shape, v2[0].shape))
# H-1
for nm, m in (('v2', v2), ('후보', cand)):
    s = region(*m, -0.46, 1.54, -6.62, -4.62); print('H-1 %s 점프 지점 ±1 m: 자유 %.0f%% 벽 %.0f%% 미지 %.1f%%' % (nm, 100 * (s == 254).mean(), 100 * (s == 0).mean(), 100 * ((s != 0) & (s != 254)).mean()))
s = region(*cand, -0.5, 0.4, -5.9, -4.9); print('   구멍 상자(x −0.5~0.4, y −5.9~−4.9) 후보 미지 %.1f%%' % (100 * ((s != 0) & (s != 254)).mean()))
# H-3 영역별 최적 이동(후보 점유 → v2 점유 거리)
REG = {'출발 방': (-1.0, 3.0, -0.8, 3.6), '동쪽 방': (3.0, 6.5, -1.6, 3.6), '남쪽': (-2.2, 3.0, -6.6, -2.8), '남동': (3.0, 7.5, -6.6, -2.8), '서쪽 띠': (-5.2, -2.2, -6.6, 3.6)}
for nm, (x0, x1, y0, y1) in REG.items():
    a = region(*v2, x0, x1, y0, y1) == 0; b = region(*cand, x0, x1, y0, y1) == 0
    best = None
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            bb = np.roll(np.roll(b, dy, 0), dx, 1); sc = (a & bb).sum() / max(b.sum(), 1)
            if best is None or sc > best[0]: best = (sc, dx * .05, -dy * .05)
    same = (a & b).sum() / max(a.sum(), 1)
    print('H-3 %-5s v2 점유 %5d 후보 %5d | 그대로 겹침 %.0f%% (v2 기준) | 최적 이동 (%+.2f, %+.2f) m' % (nm, a.sum(), b.sum(), 100 * same, best[1], best[2]))
# H-4 남쪽 벽 — 열마다 y −6.6~−5.9 점유 칸의 가장 북쪽(안쪽 면)
def wall(m):
    out = []
    for x in np.arange(-1.975, 6.0, 0.05):
        ys = [y for y in np.arange(-6.575, -5.9, 0.05) if world(*m, x, y) == 0]
        if ys: out.append((x, max(ys)))
    return np.array(out)
for nm, m in (('v1', v1), ('v2', v2), ('후보', cand)):
    w = wall(m); bins = [w[(w[:, 0] >= a) & (w[:, 0] < a + 2), 1].mean() for a in (0, 2, 4)]
    sel = w[(w[:, 0] >= 0) & (w[:, 0] < 6)]; k = np.polyfit(sel[:, 0], sel[:, 1], 1)[0]
    print('H-4 %-3s 남쪽 벽 안쪽 면 2 m 평균 %.2f / %.2f / %.2f, 기울기 %+.2f°, 열 수 %d' % (nm, *bins, math.degrees(math.atan(k)), len(sel)))
