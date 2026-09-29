#!/usr/bin/env python3
"""F0-a 절차 v2.3 §7 판정 계산 (2026-09-29, 09-28 j617 계산을 파일로 남김): 러너 csv → 목표별 xy 진입→끝 시간·ω 부호 바뀜,
   상자 옆 통과 y, map→odom 보정 변화(목표 회전 구간), 줄자 모서리 예측.
   인자: CSV [CSV ...]   (목표: 1 = (2.3, 0), 2 = (0, 0) — map 좌표, 출발 = 원점)"""
import csv, math, sys

GOALS = {1: (2.3, 0.0), 2: (0.0, 0.0)}
XY_TOL = 0.15 + 0.01      # csv 는 10 Hz TF 샘플 — Nav2 판정(0.15) 순간이 행 사이에 빠질 수 있어 1 cm 여유(f0a6·f0a7 끝 행 0.156·0.148 m)
BOX_X = (1.15, 1.26)          # 상자 x 구간(prep 측정, 09-28·09-29 같음)
L2, W2 = 0.25, 0.165          # 차체 반길이·반폭(500 × 330 mm)


def run(path):
    rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(open(path))]
    print('== %s (%d 행)' % (path.replace('\\', '/').split('/')[-1], len(rows)))
    for g, (gx, gy) in GOALS.items():
        R = [r for r in rows if int(r['goal']) == g]
        if not R: continue
        ent = next((r for r in R if math.hypot(r['map_x'] - gx, r['map_y'] - gy) <= XY_TOL), None)
        end = R[-1]
        if ent is None: ent = end; print('  (목표 %d: csv 에서 xy 진입 행 없음 — 끝 행 거리 %.3f m)' % (g, math.hypot(end['map_x'] - gx, end['map_y'] - gy)))
        after = [r for r in R if r['t'] >= ent['t']]
        w = [r['w'] for r in after if abs(r['w']) > 0.02]
        flips = sum(1 for a, b in zip(w, w[1:]) if (a > 0) != (b > 0))
        dyaw = (end['map_yaw'] - ent['map_yaw'] + 180) % 360 - 180   # csv yaw 는 도(°)
        # 목표 회전 구간(출발 직후 |v| 작고 |ω| 큰 구간)의 map→odom 보정 변화 = SLAM 이 odom(EKF) 과 다르게 본 양
        rot = [r for r in R[:120] if abs(r['v']) < 0.02 and abs(r['w']) > 0.10]
        if rot:
            a, b = rot[0], rot[-1]
            dmo = math.hypot(b['mo_x'] - a['mo_x'], b['mo_y'] - a['mo_y'])
            rtxt = '출발 회전 %.1f s 동안 map→odom 변화 %.3f m' % (b['t'] - a['t'], dmo)
        else:
            rtxt = '출발 제자리 회전 없음'
        print('  목표 %d: xy 진입 → 끝 %.1f s, 진입 뒤 yaw 변화 %.1f°, ω 부호 바뀜 %d 회 | %s' % (g, end['t'] - ent['t'], dyaw, flips, rtxt))
    ys = [r['map_y'] for r in rows if int(r['goal']) == 2 and BOX_X[0] - 0.05 <= r['map_x'] <= BOX_X[1] + 0.05]
    if ys: print('  복귀 상자 옆 중심 y %.3f~%.3f (기준 ≥ 0.26)' % (min(ys), max(ys)))
    e = rows[-1]; yr = math.radians(e['map_yaw']); c, s = math.cos(yr), math.sin(yr)
    bx, by = e['map_x'] + c * (-L2) - s * W2, e['map_y'] + s * (-L2) + c * W2       # 끝 자세의 뒤·왼 모서리
    print('  끝 map (%.3f, %.3f, %.1f°) → 뒤·왼 모서리 ↔ 출발 오른쪽 앞 표시(%.2f, %.3f): 세로 %.3f, 가로 %.3f m'
          % (e['map_x'], e['map_y'], e['map_yaw'], L2, -W2, bx - L2, by + W2))
    print('  map→odom 누적 (%.3f, %.3f) m' % (e['mo_x'], e['mo_y']))


for p in sys.argv[1:]: run(p)
