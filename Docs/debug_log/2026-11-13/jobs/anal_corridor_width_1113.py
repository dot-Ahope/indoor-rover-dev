#!/usr/bin/env python3
# anal_corridor_width_1113 — 11-13 §3: 서쪽 통로 y 줄마다(5 cm) '비용 < 99 인 통과 가능 폭'과 '저장 지도(office_v3) 벽 사이 빈 폭'을 f2rr1 · f2rd1 로 나란히.
#   저장 지도엔 없는데 코스트맵에서 좁아진 줄 = 그때 센서(라이다 · nvblox)가 새로 본 물체 또는 위치 어긋남. PC, 로버 안 움직임.
#   인자: f2rr1 bag 폴더 · f2rd1 crop txt · 출력 txt. 통로 중심선 근처 x −2.4 ~ −1.2 에서 x = −1.75 를 포함하는 연속 구간 폭.
import sys, numpy as np
sys.argv += []
exec(open(__file__.replace('anal_corridor_width_1113.py', 'fig_corridor_cmp_1113.py'), encoding='utf-8').read().split('BLK =')[0].replace('bag1, crop2, csv1, csv2, outp = sys.argv[1:6]', 'bag1, crop2 = sys.argv[1:3]'))
import yaml, PIL.Image
Y = yaml.safe_load(open('Docs/04_navigation/maps/office_v3.yaml'))
img = np.array(PIL.Image.open('Docs/04_navigation/maps/' + Y['image']))[::-1]   # 아래 줄 = origin y
occ = (255 - img) / 255.0 > Y['occupied_thresh']
def width_row(free, xs, xc=-1.75):
    j = int(np.argmin(abs(xs - xc)))
    if not free[j]: return 0.0, xs[j], xs[j]
    a = j; b = j
    while a > 0 and free[a - 1]: a -= 1
    while b < len(free) - 1 and free[b + 1]: b += 1
    return (b - a + 1) * (xs[1] - xs[0]), xs[a], xs[b]
A = crop_from_bag(bag1, '14:55:44', '2026-11-11'); Bk = crop_from_npz(crop2, '154803'); C = crop_from_npz(crop2, '154906')
out = open(sys.argv[3], 'w', encoding='utf-8')
def pr(s): print(s); out.write(s + '\n')
pr('y      | 저장지도 빈 폭(x 범위)        | f2rr1 14:55:44 (<99)         | f2rd1 15:48:03               | f2rd1 15:49:06')
for y in np.arange(-5.4, -2.0, 0.1):
    row = []
    r = Y['resolution']; ry = int((y - Y['origin'][1]) / r)
    xs = np.arange(-2.4, -1.1, r); cx = ((xs - Y['origin'][0]) / r).astype(int)
    w, a, b = width_row(~occ[ry, cx], xs); row.append(f'{w:4.2f} ({a:5.2f}~{b:5.2f})')
    for g, (ox, oy, res) in (A, Bk, C):
        rr = int((y - oy) / res); xs2 = ox + res * np.arange(g.shape[1]); m = (xs2 >= -2.4) & (xs2 <= -1.1)
        w, a, b = width_row((g[rr] < 99)[m], xs2[m]); row.append(f'{w:4.2f} ({a:5.2f}~{b:5.2f})')
    pr(f'{y:5.2f}  | ' + ' | '.join(row))
