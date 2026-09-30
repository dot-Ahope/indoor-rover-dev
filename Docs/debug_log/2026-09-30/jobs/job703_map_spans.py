#!/usr/bin/env python3
"""09-30 §8 F1-3: 저장 지도(office_v1.pgm/yaml)에서 구간 길이 측정 — 한 점에서 한 방향으로 빈 셀을 따라가 양쪽 벽(점유 셀) 사이 거리.
   출력은 벽 안쪽 면 사이(빈 셀 수 × 해상도). 인자: pgm yaml"""
import sys, math, yaml
import numpy as np
from PIL import Image
m = yaml.safe_load(open(sys.argv[2])); g = np.array(Image.open(sys.argv[1])); res = m['resolution']; ox, oy = m['origin'][:2]; H, W = g.shape
occ = g < 50; free = g > 250


def cell(x, y): return H - 1 - int((y - oy) / res), int((x - ox) / res)


def run(x, y, dx, dy, lim=6.0):
    """(x,y) 에서 (dx,dy) 로 점유 셀을 만날 때까지 거리(m), 미지 셀이면 None."""
    s = 0.0
    while s < lim:
        i, j = cell(x + dx * s, y + dy * s)
        if not (0 <= i < H and 0 <= j < W): return None
        if occ[i, j]: return s
        if not free[i, j]: return None
        s += res / 4
    return None


def width(x, y, ax):
    dx, dy = (1, 0) if ax == 'x' else (0, 1)
    a = run(x, y, -dx, -dy); b = run(x, y, dx, dy)
    return a, b, (a + b) if a is not None and b is not None else None


def thick(x, y, dx, dy, lim=1.0):
    """(x,y) 에서 (dx,dy) 로 가다 처음 만난 점유 띠의 두께."""
    s0 = run(x, y, dx, dy)
    if s0 is None: return None, None
    s = s0
    while s < s0 + lim:
        i, j = cell(x + dx * s, y + dy * s)
        if not occ[i, j]: return s0, s - s0
        s += res / 4
    return s0, None


print('해상도 %.3f m — 측정 불확도 약 ±1 셀(±%.0f cm)' % (res, res * 100))
for x in (-0.5, 0.0, 0.5, 1.0):
    a, b, w = width(x, 0.0, 'y'); print('출발 방 남북 폭 @ x=%+.1f: 남쪽 벽까지 %s, 북쪽 벽까지 %s → 폭 %s' % (x, a, b, None if w is None else '%.3f m' % w))
for y in (-0.60, -0.65, -0.70):
    a, b, w = width(2.25, y, 'x'); print('문 폭 @ y=%.2f (x=2.25 에서): 서 %s, 동 %s → 폭 %s' % (y, a, b, None if w is None else '%.3f m' % w))
for y in (0.0, 0.5, 1.0, 2.0):
    s0, t = thick(2.0, y, 1, 0); print('두 방 사이 벽 두께 @ y=%.1f (x=2.0 에서 동쪽): 벽 시작 +%s m, 두께 %s' % (y, s0, None if t is None else '%.3f m' % t))
