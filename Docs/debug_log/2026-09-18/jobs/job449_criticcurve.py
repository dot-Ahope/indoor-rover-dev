#!/usr/bin/env python3
"""상자 옆 통과 중 '옆 여유 c' 에 따른 장애물 크리틱 비용 곡선 — 1.1.20 소스(obstacles_critic.cpp, cost_critic.cpp) 그대로 (2026-09-18 §15).
정적 근사: 궤적 32 점이 모두 같은 옆 여유 c 로 상자(오른쪽)·왼쪽 장애물(통로 폭 W) 사이를 지난다. 로컬 코스트맵 inflation 0.40 / 2.5,
내접 0.175(반폭 0.165 + 패딩 0.01), 외접 0.3134. 셀 양자화는 무시(연속 거리). 경로 크리틱은 계획 여유 c_plan 에서 벗어난 옆 거리 |c − c_plan|
에 PathAlign 14 + PathFollow 10 = 24 /m 로 근사(둘 다 거리 선형).
"""
import math
R_IN, R_CIRC, K, R_INF = 0.175, math.sqrt(0.26 ** 2 + 0.175 ** 2), 2.5, 0.40
HW = 0.165


def layer_cost(d):          # InflationLayer::computeCost (d = 셀↔장애물 거리, m)
    if d <= 0: return 254.0
    if d <= R_IN: return 253.0
    if d > R_INF: return 0.0
    return 252.0 * math.exp(-K * (d - R_IN))


POSS = layer_cost(R_CIRC)


def costs(c, W):
    cl = W - 2 * HW - c                                   # 왼쪽 여유
    center = max(layer_cost(HW + c), layer_cost(HW + cl))
    foot = max(layer_cost(c), layer_cost(cl))             # 둘레 최대(옆면이 가장 가까움)
    return center, foot


def obstacles(c, W, s, R, margin, cw=20.0, rw=1.5, n=32):
    center, foot = costs(c, W)
    if center < 1: return 0.0
    if center >= POSS:
        cost, fp = foot, True
    else:
        cost, fp = center, False
    if cost >= 254: return 10000.0
    dist = (s * R_IN - math.log(cost) + math.log(253.0)) / s - (0 if fp else R_IN)
    crit = rep = 0.0
    if dist < margin: crit = n * (margin - dist)
    else: rep = n * (R - dist)
    return cw * crit + rw * rep / n


def costcritic(c, W, w=3.81, critical=300.0, n=32):
    center, foot = costs(c, W)
    if center < 1: return 0.0
    if (center >= POSS and foot >= 254) or center >= 254: return 1e6
    per = critical if center >= 253 else center
    return (w / 254.0) * n * per / n


CFG = [('현재 Obstacles(s10,R0.55,m0.05)', lambda c, W: obstacles(c, W, 10.0, 0.55, 0.05)),
       ('Obstacles 값 맞춤(s2.5,R0.40,m0.05)', lambda c, W: obstacles(c, W, 2.5, 0.40, 0.05)),
       ('Obstacles 값 맞춤+m0.10', lambda c, W: obstacles(c, W, 2.5, 0.40, 0.10)),
       ('CostCritic w3.81', lambda c, W: costcritic(c, W, 3.81)),
       ('CostCritic w8', lambda c, W: costcritic(c, W, 8.0)),
       ('CostCritic w12', lambda c, W: costcritic(c, W, 12.0))]
for W in (0.55, 0.60):
    cs = [i / 100 for i in range(1, int((W - 2 * HW) * 100))]
    print('==== 통로 폭 W %.2f (로버 가운데면 양쪽 %.1f cm)' % (W, 100 * (W - 2 * HW) / 2))
    print('  %-34s | 옆 여유 c(cm): %s' % ('', ' '.join('%5d' % round(100 * c) for c in cs[::2])))
    for name, f in CFG:
        print('  %-34s | 비용          : %s' % (name, ' '.join('%5.2f' % min(f(c, W), 99.99) for c in cs[::2])))
    print('  -- 계획 여유 c_plan 일 때 (장애물 + 경로 24/m·|c−c_plan|) 최소가 되는 c (cm)')
    for name, f in CFG:
        row = []
        for cp in (0.03, 0.05, 0.07, 0.10):
            best = min(cs, key=lambda c: f(c, W) + 24.0 * abs(c - cp))
            row.append('plan %2d → %2d' % (round(cp * 100), round(best * 100)))
        print('  %-34s | %s' % (name, ' | '.join(row)))
