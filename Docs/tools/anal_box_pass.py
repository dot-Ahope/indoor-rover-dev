#!/usr/bin/env python3
"""anal_box_pass — 여러 주행에서 '같은 구역을 지날 때' 차체와 로컬 코스트맵 치명 칸 사이 여유가 얼마였는지 나란히 본다. (2026-10-13)
  왜: 사용자 질문 "통신 포화가 있던 주행은 상자를 피해 도착했는데, 포화가 오히려 도움이 된 것인가". 통과한 주행과 멈춘 주행이 상자 옆에서 실제로 달랐는지 확인.
  방법: 로버 중심이 지정 구역(지도 좌표 사각형)에 있고 지정 방향(yaw 범위, 복귀 = 서쪽)일 때만, 로컬 코스트맵마다 차체 외곽 ↔ 1 m 안 치명 칸 가장자리 거리(시뮬의 'LETHAL 여유'와 같은 정의)를 잰다.
  출력: 주행마다 구역 체류 시간, 최소 여유와 그때 위치, 2 s 넘게 멈춘 적이 있는지, 주행 끝 위치.
  사용: anal_box_pass.py x0,x1,y0,y1 이름=bag ..."""
import sys, time, math
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from anal_box_history import load, near, grid
x0, x1, y0, y1 = [float(v) for v in sys.argv[1].split(',')]; HL0, HL1, HW = 0.262, 0.248, 0.165
print('구역 map x %.1f~%.1f · y %.1f~%.1f, 서쪽(복귀) 방향일 때만' % (x0, x1, y0, y1))
print('주행    구역 체류   최소 여유   그때 위치(map)·시각          5 cm 미만이던 시간   구역 안 정지(2 s+)   주행 끝 위치')
for a in sys.argv[2:]:
    nm, bag = a.split('=', 1); D, ob, mo = load(bag, ['/local_costmap/costmap']); rows = []
    for ts, m in D['/local_costmap/costmap']:
        Mob = near(ob, ts); Mmb = near(mo, ts) @ Mob; px, py = Mmb[0, 2], Mmb[1, 2]; yaw = math.atan2(Mmb[1, 0], Mmb[0, 0])
        if not (x0 <= px <= x1 and y0 <= py <= y1 and abs(yaw) > math.radians(100)): continue
        ox, oy, res, G = grid(m); L = np.argwhere(G >= 100)
        if not len(L): continue
        P = (np.linalg.inv(Mob) @ np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res, np.ones(len(L))].T).T
        d = np.hypot(np.maximum.reduce([-HL1 - P[:, 0], np.zeros(len(P)), P[:, 0] - HL0]), np.maximum.reduce([-HW - P[:, 1], np.zeros(len(P)), P[:, 1] - HW])) - res / 2
        rows.append((ts, d.min(), px, py))
    Mend = near(mo, ob[-1][0]) @ ob[-1][1]
    if not rows: print('%-7s 구역을 서쪽 방향으로 지나지 않음                                                             끝 (%.2f, %.2f)' % (nm, Mend[0, 2], Mend[1, 2])); continue
    R = np.array(rows); k = int(np.argmin(R[:, 1])); dt = np.diff(R[:, 0]); mv = np.hypot(np.diff(R[:, 2]), np.diff(R[:, 3])); still = 0.0; run = 0.0
    for a_, b_ in zip(dt, mv):
        run = run + a_ if b_ < 0.005 else 0.0; still = max(still, run)
    print('%-7s %5.1f s     %5.1f cm    (%.2f, %.2f) %s          %5.1f s             %s          (%.2f, %.2f)' % (nm, R[-1, 0] - R[0, 0], R[k, 1] * 100, R[k, 2], R[k, 3], time.strftime('%H:%M:%S', time.localtime(R[k, 0])),
          float(dt[R[:-1, 1] < 0.05].sum()), ('%.1f s' % still) if still >= 2 else '없음', Mend[0, 2], Mend[1, 2]))
