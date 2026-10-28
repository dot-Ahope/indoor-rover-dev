#!/usr/bin/env python3
"""anal_place_clear — place_server 목표 여유 검사가 왜 0 이 나왔나 (2026-10-28 §8, PC, 로버 안 움직임).
  bag 의 전역 코스트맵(/global_costmap/costmap) 판 중 시각 t 직전 판에서, 목표 (gx, gy) 주변 치명(≥100) 칸을 찾고
  place_server.clearance() 와 같은 식(차체 반길이 0.26 · 반폭 0.175 직사각형 바깥까지 거리)으로 방향별 여유를 다시 계산한다.
  같은 칸이 정적 지도(/map, SLAM)에서 점유(≥65)인지도 본다. 목표 둘레 1 m 를 문자 격자로 그린다(# 치명 · + 99 · . 그 밖, @ 목표).
  인자: bag폴더 날짜(YYYY-MM-DD) 시각HH:MM:SS.ff gx gy [방향도 여러 개, 기본 -90,0,90,180]"""
import sys, math, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
HL, HW = 0.26, 0.175   # place_server 와 같은 값
ts_ = get_typestore(Stores.ROS2_HUMBLE)
bag = Path(sys.argv[1]); day = sys.argv[2]; ev = sys.argv[3]; gx, gy = float(sys.argv[4]), float(sys.argv[5])
yaws = [float(a) for a in sys.argv[6].split(',')] if len(sys.argv) > 6 else [-90, 0, 90, 180]
T = lambda s: time.mktime(time.strptime(day + ' ' + s[:8], '%Y-%m-%d %H:%M:%S')) + float(s[8:] or 0)
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
t_ev = T(ev); GM, MP = [], []
with AnyReader([bag], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/map')]):
        ts = t * 1e-9
        if ts > t_ev + 1: continue
        m = rd.deserialize(raw, c.msgtype); i = m.info
        (GM if c.topic == '/global_costmap/costmap' else MP).append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
def last(L, t): return [x for x in L if x[0] <= t][-1]
def clear(G, th):
    _, g, ox, oy, r = G; J, I = np.nonzero(g >= 100); X = ox + (I + .5) * r - gx; Y = oy + (J + .5) * r - gy
    lx = X * math.cos(th) + Y * math.sin(th); ly = -X * math.sin(th) + Y * math.cos(th)
    d = np.hypot(np.maximum(np.abs(lx) - HL, 0), np.maximum(np.abs(ly) - HW, 0)); k = int(np.argmin(d))
    return d[k], X[k] + gx, Y[k] + gy, int((d == 0).sum())
G = last(GM, t_ev); M = last(MP, t_ev)
print('사건 %s · 목표 (%.2f, %.2f) · 전역 판 %s (판 %d 개 중) · 정적 지도 판 %s' % (ev, gx, gy, hs(G[0]), len(GM), hs(M[0])))
for th in yaws:
    d, x, y, n = clear(G, math.radians(th))
    _, mg, mx, my, mr = M; vm = int(mg[int((y - my) / mr), int((x - mx) / mr)])
    print('  방향 %+4.0f° : 여유 %.3f m · 가장 가까운 치명 칸 (%.3f, %.3f) · 그 칸 /map 값 %d · 차체 안 치명 칸 %d' % (th, d, x, y, vm, n))
print('\n전역 코스트맵 목표 둘레 ±0.5 m (위 = +y, 한 글자 5 cm; # 치명 · + 99 · : 1~98 · . 0 · ? 미지 · @ 목표)')
_, g, ox, oy, r = G
for yy in np.arange(gy + 0.5, gy - 0.5 - 1e-9, -r):
    row = ''
    for xx in np.arange(gx - 0.5, gx + 0.5 + 1e-9, r):
        v = int(g[int((yy - oy) / r), int((xx - ox) / r)])
        row += '@' if abs(xx - gx) < r / 2 and abs(yy - gy) < r / 2 else ('#' if v >= 100 else '+' if v == 99 else ':' if v > 0 else '?' if v < 0 else '.')
    print('  %+.2f %s' % (yy, row))
print('\n정적 지도(/map) 같은 범위 (# 점유≥65 · . 빈 · ? 미지)')
_, g, ox, oy, r = M
for yy in np.arange(gy + 0.5, gy - 0.5 - 1e-9, -r):
    row = ''
    for xx in np.arange(gx - 0.5, gx + 0.5 + 1e-9, r):
        v = int(g[int((yy - oy) / r), int((xx - ox) / r)])
        row += '@' if abs(xx - gx) < r / 2 and abs(yy - gy) < r / 2 else ('#' if v >= 65 else '?' if v < 0 else '.')
    print('  %+.2f %s' % (yy, row))
# 시간에 따라: 출발 전 첫 판부터 사건까지 판마다 남북(-90°) 여유
print('\n판마다 -90° 여유(전체 창):')
for Gk in GM[::max(1, len(GM) // 25)] + [G]:
    d, x, y, n = clear(Gk, math.radians(-90)); print('  %s  %.3f m  (%.2f, %.2f)  차체 안 %d' % (hs(Gk[0]), d, x, y, n))
