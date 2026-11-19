#!/usr/bin/env python3
"""anal_box_history — 로버가 장애물 옆에서 멈췄을 때, 그 장애물 칸이 코스트맵에 '언제부터' 있었는지와 로버·경로가 '어떻게' 다가갔는지를 시간순으로 낸다. (2026-10-13)
  왜: f2o1 목표 3 정지(상자 옆 여유 4.8 cm). MPPI·경로가 상자 쪽으로 붙은 것인지, 상자 칸이 늦게 나타난 것인지 가린다.
  방법: 지정 시각(정지 때)의 로컬 코스트맵에서 차체에 가장 가까운 치명 칸이 속한 덩어리(연결된 칸)를 '상자'로 잡아 지도(map) 좌표로 고정한다.
        그 뒤 주행 전체의 로컬·전역 코스트맵마다 그 자리 칸 중 몇 개가 치명이었는지, 로버가 상자에서 얼마나 떨어져 있었는지,
        상자가 카메라 정면에서 몇 도였는지, 전역 경로(/plan)가 상자에 얼마나 가깝게 그려졌는지를 본다.
  한계: 상자 자리는 정지 순간의 코스트맵으로 정한 것이다(상자의 참 위치가 아님). map↔odom 보정이 그 사이 움직이면 자리도 그만큼 어긋난다.
  사용: anal_box_history.py bag HH:MM:SS(정지 시각) [시작 HH:MM:SS]"""
# 11-19 §3: bag 읽기 · 변환 · 상자 정의 · 차체 여유는 lib_rover 로(옛 판과 출력 비교, 11-19 SUMMARY §3). 표본 고르기는 옛 규칙 그대로(L.after = t 이상 첫 것).
import sys, math
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L
bag, hms = sys.argv[1], sys.argv[2]; hms0 = sys.argv[3] if len(sys.argv) > 3 else None

D = L.read_bag(bag, ['/tf', '/local_costmap/costmap', '/global_costmap/costmap', '/plan']); ob, mo = D['ob'], D['mo']
M = lambda seq, t: L.after(seq, t)[1]
tgt = L.hms_epoch(D['day'], hms); tA = L.hms_epoch(D['day'], hms0) if hms0 else ob[0][0]
# 상자 = 정지 때 로컬 코스트맵에서 차체에 가장 가까운 치명 칸의 8 연결 덩어리(L.box_cells)
g = min(D['loc'], key=lambda x: abs(x[0] - tgt)); ts, res = g[0], g[3]
BOX = L.box_cells(g, M(ob, ts), M(mo, ts))   # 지도 좌표의 상자 칸(중심)
bc = BOX.mean(0); print('상자(정지 %s 때 로컬 코스트맵 기준): 치명 칸 %d 개, 지도 좌표 중심 (%.2f, %.2f), 폭 x %.2f · y %.2f m' % (L.hms(ts), len(BOX), bc[0], bc[1], np.ptp(BOX[:, 0]) + res, np.ptp(BOX[:, 1]) + res))


def count(g, Tin):   # 코스트맵 g 에서 상자 자리 칸 중 치명 수(창 밖이면 None). Tin = map → 코스트맵 좌표
    _, ox, oy, res, G = g; P = L.w2(Tin, BOX); j = ((P[:, 0] - ox) / res).astype(int); i = ((P[:, 1] - oy) / res).astype(int); ok = (i >= 0) & (i < G.shape[0]) & (j >= 0) & (j < G.shape[1])
    if ok.sum() < len(BOX) * 0.8: return None
    v = G[i[ok], j[ok]]; return int((v >= 100).sum()), int((v >= 99).sum())
print('\n시각      로버→상자 중심 거리  차체 여유  상자 방위(로버 앞 기준, +왼쪽)  로컬: 그 자리 치명/내접이상 칸  전역: 치명/내접이상  전역 경로가 상자 칸에 가장 가까운 거리')
last = -9
for g in D['loc']:
    ts = g[0]
    if ts < tA or ts > tgt + 3 or ts - last < 1.9: continue
    last = ts; Mmo = M(mo, ts); Mmb = Mmo @ M(ob, ts); Pb = L.w2(np.linalg.inv(Mmb), BOX); cb = Pb.mean(0)
    lc = count(g, np.linalg.inv(Mmo)); gg = [x for x in D['glo'] if x[0] <= ts]; gc = count(gg[-1], np.eye(4)) if gg else None
    p = [x for x in D['raws'] if x[0] <= ts]; pd = float('nan')
    if p and len(p[-1][1]) > 1:
        xy = p[-1][1]; pd = np.hypot(xy[:, None, 0] - BOX[None, :, 0], xy[:, None, 1] - BOX[None, :, 1]).min()
    f = lambda c: '창 밖' if c is None else '%2d / %2d' % c
    print('%s   %.2f m            %5.1f cm    %+5.0f°                         %-8s                   %-8s            %.2f m' % (L.hms(ts), np.hypot(*cb), L.rect_clear(Pb).min() * 100, math.degrees(math.atan2(cb[1], cb[0])), f(lc), f(gc), pd))
