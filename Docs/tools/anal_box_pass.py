#!/usr/bin/env python3
"""anal_box_pass — 여러 주행에서 '같은 구역을 지날 때' 차체와 로컬 코스트맵 치명 칸 사이 여유가 얼마였는지 나란히 본다. (2026-10-13)
  왜: 사용자 질문 "통신 포화가 있던 주행은 상자를 피해 도착했는데, 포화가 오히려 도움이 된 것인가". 통과한 주행과 멈춘 주행이 상자 옆에서 실제로 달랐는지 확인.
  방법: 로버 중심이 지정 구역(지도 좌표 사각형)에 있고 지정 방향(yaw 범위, 복귀 = 서쪽)일 때만, 로컬 코스트맵마다 차체 외곽 ↔ 1 m 안 치명 칸 가장자리 거리(시뮬의 'LETHAL 여유'와 같은 정의)를 잰다.
  출력: 주행마다 구역 체류 시간, 최소 여유와 그때 위치, 2 s 넘게 멈춘 적이 있는지, 주행 끝 위치.
  사용: anal_box_pass.py x0,x1,y0,y1 이름=bag ..."""
# 11-19 §3: 읽기 · 변환은 lib_rover 로(옛 판은 anal_box_history 의 load · near · grid 를 import). 표본 고르기 = L.after(옛 near 와 같음).
import sys, math
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L
x0, x1, y0, y1 = [float(v) for v in sys.argv[1].split(',')]
print('구역 map x %.1f~%.1f · y %.1f~%.1f, 서쪽(복귀) 방향일 때만' % (x0, x1, y0, y1))
print('주행    구역 체류   최소 여유   그때 위치(map)·시각          5 cm 미만이던 시간   구역 안 정지(2 s+)   주행 끝 위치')
for a in sys.argv[2:]:
    nm, bag = a.split('=', 1); D = L.read_bag(bag, ['/tf', '/local_costmap/costmap']); ob, mo = D['ob'], D['mo']; rows = []
    for g in D['loc']:
        ts = g[0]; Mob = L.after(ob, ts)[1]; Mmb = L.after(mo, ts)[1] @ Mob; px, py, yaw = L.xyyaw(Mmb)
        if not (x0 <= px <= x1 and y0 <= py <= y1 and abs(yaw) > math.radians(100)): continue
        if not (g[4] >= 100).any(): continue
        P = L.w2(np.linalg.inv(Mob), L.lethal_cells(g)); rows.append((ts, L.rect_clear(P).min() - g[3] / 2, px, py))   # 칸 가장자리까지 = 중심 − 반 칸
    Mend = L.after(mo, ob[-1][0])[1] @ ob[-1][1]
    if not rows: print('%-7s 구역을 서쪽 방향으로 지나지 않음                                                             끝 (%.2f, %.2f)' % (nm, Mend[0, 3], Mend[1, 3])); continue
    R = np.array(rows); k = int(np.argmin(R[:, 1])); dt = np.diff(R[:, 0]); mv = np.hypot(np.diff(R[:, 2]), np.diff(R[:, 3])); still = 0.0; run = 0.0
    for a_, b_ in zip(dt, mv):
        run = run + a_ if b_ < 0.005 else 0.0; still = max(still, run)
    print('%-7s %5.1f s     %5.1f cm    (%.2f, %.2f) %s          %5.1f s             %s          (%.2f, %.2f)' % (nm, R[-1, 0] - R[0, 0], R[k, 1] * 100, R[k, 2], R[k, 3], L.hms(R[k, 0]),
          float(dt[R[:-1, 1] < 0.05].sum()), ('%.1f s' % still) if still >= 2 else '없음', Mend[0, 3], Mend[1, 3]))
