#!/usr/bin/env python3
"""anal_fp_global — 전역 코스트맵(계획기가 보는 지도)에서 '차체(패딩 포함)가 치명 칸에 걸리는가' 를 자세마다 셈 (2026-10-23 Phase P, PC).
  왜: 오프라인 비교에서 Smac Hybrid 가 서쪽 통로 장면 2 개를 모든 설정에서 'no valid path found'. Smac 은 경로 위 자세마다
      차체 다각형 아래 칸에 치명(254 = 기록 100)이 하나라도 있으면 그 자세를 못 씀(Humble GridCollisionChecker, 풋프린트 비원형).
      로버가 실제로 지나간 자세들도 이 지도에선 '충돌' 인지 보면, 실패가 Smac 탐색 문제인지 지도 자체가 막혀 있는지 가를 수 있음.
  방법: 풋프린트(0.262/−0.248 × ±0.165) + 패딩 0.01 을 자세로 돌려, 그 다각형 안 칸 중심 + 다각형 둘레 점(2.5 cm 간격)이 놓인 칸의 최대값.
        (costmap_2d footprintCost 는 둘레 선분이 지나는 칸을 봄 — 둘레 점 표본으로 근사, 안쪽 칸도 함께 봄 = 더 엄격 쪽)
  출력: 장면 출발 · 목표 자세의 최대값, 실제 주행 궤적(그 구간)에서 치명이 걸린 자세 비율 · 위치 · 그 자세의 최소 '치명 칸까지 거리'.
  인자: 장면.npz bag(압축 푼 폴더) 장면이름 시작HH:MM:SS 끝HH:MM:SS"""
import sys, json, math, bisect, time
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]]); PAD = 0.01
FPp = FP + PAD * np.sign(FP)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
sc = np.load(sys.argv[1]); bag, name, h0, h1 = sys.argv[2:6]
G = sc[name + '/grid'].astype(np.int16); ox, oy, r, _ = sc[name + '/info']
# 차체 좌표계 표본점: 안쪽 격자(2.5 cm) + 둘레
xs = np.arange(FPp[:, 0].min(), FPp[:, 0].max() + 1e-9, 0.025); ys = np.arange(FPp[:, 1].min(), FPp[:, 1].max() + 1e-9, 0.025)
IN = np.array([[x, y] for x in xs for y in ys])
def fpmax(p):
    c, s = math.cos(p[2]), math.sin(p[2]); W = np.c_[p[0] + c * IN[:, 0] - s * IN[:, 1], p[1] + s * IN[:, 0] + c * IN[:, 1]]
    mx = np.floor((W[:, 0] - ox) / r).astype(int); my = np.floor((W[:, 1] - oy) / r).astype(int); ok = (mx >= 0) & (my >= 0) & (mx < G.shape[1]) & (my < G.shape[0])
    v = G[my[ok], mx[ok]]; return int(v.max()), W[ok][v >= 100]
L = np.argwhere(G >= 100); LC = np.c_[ox + (L[:, 1] + 0.5) * r, oy + (L[:, 0] + 0.5) * r]
def lethal_gap(p):   # 차체(패딩 없음) 둘레에서 가장 가까운 치명 칸 중심까지(칸 반쪽 빼지 않음 — 대략치)
    c, s = math.cos(p[2]), math.sin(p[2]); d = LC - np.array(p[:2]); bx = c * d[:, 0] + s * d[:, 1]; by = -s * d[:, 0] + c * d[:, 1]
    dx = np.maximum(np.maximum(FP[:, 0].min() - bx, bx - FP[:, 0].max()), 0); dy = np.maximum(np.maximum(-0.165 - by, by - 0.165), 0)
    return float(np.hypot(dx, dy).min())
st, gl = sc[name + '/start'], sc[name + '/goal']
for lab, p in (('출발', st), ('목표', gl)):
    v, _ = fpmax(p); print('%s (%.2f, %.2f, %.0f°): 차체 아래 최대 %d%s · 치명까지 %.3f m' % (lab, p[0], p[1], math.degrees(p[2]), v, ' ← 치명 걸림' if v >= 100 else '', lethal_gap(p)))
MO, OB = [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((t * 1e-9, v))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((t * 1e-9, v))
for Lq in (MO, OB): Lq.sort(key=lambda q: q[0])
at = lambda Lq, t: Lq[max(bisect.bisect_right([q[0] for q in Lq], t) - 1, 0)][1]
d0 = time.strftime('%Y-%m-%d ', time.localtime(OB[0][0])); ep = lambda s: time.mktime(time.strptime(d0 + s, '%Y-%m-%d %H:%M:%S'))
hits = []; n = 0
for t in np.arange(ep(h0), ep(h1), 0.2):
    p = comp(at(MO, t), at(OB, t)); v, W = fpmax(p); n += 1
    if v >= 100: hits.append((t, p, len(W), lethal_gap(p)))
print('실제 궤적 %s~%s: 자세 %d 개 중 차체(패딩) 아래 치명 칸 걸림 %d 개' % (h0, h1, n, len(hits)))
for t, p, k, g in hits[:40]:
    print('  %s (%.2f, %.2f, %.0f°) 걸린 표본 %d · 치명 칸 중심까지 %.3f m' % (time.strftime('%H:%M:%S', time.localtime(t)) + '.%d' % int(t % 1 * 10), p[0], p[1], math.degrees(p[2]), k, g))
