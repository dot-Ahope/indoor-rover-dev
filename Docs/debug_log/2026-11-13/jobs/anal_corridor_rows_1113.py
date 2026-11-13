#!/usr/bin/env python3
# anal_corridor_rows_1113 — 11-13 §6: 서쪽 통로 y 줄마다 '비용 < 99 연속 구간 중 가장 넓은 것'의 폭 · x 범위(가운데 열 기준이던 anal_corridor_width_1113 의 한계 보완).
#   PC, 로버 안 움직임. 인자: crop txt(anal_costmap_crop_1113 출력) 키(HHMMSS)… [--rr1 f2rr1bag] [--rr1t HH:MM:SS] . 출력: 표준 출력.
import sys, io, base64, numpy as np
args = sys.argv[1:]; rr1 = None; rr1t = '14:55:44'
if '--rr1t' in args: i = args.index('--rr1t'); rr1t = args[i + 1]; args = args[:i] + args[i + 2:]   # 11-13 §6: f2rr1 비교 시각(기본은 통로 안쪽 들어가기 전이라 안쪽 비교엔 부적합)
if '--rr1' in args: i = args.index('--rr1'); rr1 = args[i + 1]; args = args[:i] + args[i + 2:]
txt, keys = args[0], args[1:]
z = np.load(io.BytesIO(base64.b64decode([l for l in open(txt, encoding='utf-8', errors='replace') if l.startswith('NPZ ')][0][4:])))
G = [(k, z['g' + k], z['meta' + k]) for k in keys]
if rr1:
    sys.argv = ['x', rr1, txt, '', '', '']
    src = open(__file__.replace('anal_corridor_rows_1113.py', 'fig_corridor_cmp_1113.py'), encoding='utf-8').read().split('BLK =')[0]
    exec(src); g, (ox, oy, res) = crop_from_bag(rr1, rr1t, '2026-11-11'); G.insert(0, ('f2rr1 ' + rr1t, g, np.array([0, res, ox, oy])))
def best(row, xs):
    f = row < 99; bw, ba, bb = 0, 0, 0; j = 0
    while j < len(f):
        if f[j]:
            k = j
            while k + 1 < len(f) and f[k + 1]: k += 1
            if k - j + 1 > bw: bw, ba, bb = k - j + 1, xs[j], xs[k]
            j = k + 1
        else: j += 1
    return bw * (xs[1] - xs[0]), ba, bb
print('y     | ' + ' | '.join(f'{k:^22s}' for k, _, _ in G))
for y in np.arange(-5.2, -2.3, 0.1):
    cells = []
    for k, g, m in G:
        res, ox, oy = m[1], m[2], m[3]; r = int((y - oy) / res); xs = ox + res * np.arange(g.shape[1]); sel = (xs >= -2.5) & (xs <= -1.0)
        w, a, b = best(g[r][sel], xs[sel]); cells.append(f'{w:4.2f} ({a:5.2f}~{b:5.2f})')
    print(f'{y:5.2f} | ' + ' | '.join(cells))
