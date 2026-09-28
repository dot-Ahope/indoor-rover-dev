#!/usr/bin/env python3
"""B2 ICR 식별 (2026-09-28 §26, PC 에서 실행): 회전 시험 스캔 정합 출력에서 회전별 (중심 이동 d, 회전각 θ)를 읽어
  회전축 치우침 p = (I − R(θ))⁻¹·d 를 구하고, 방향별(시계/반시계)·속도별로 모아
  leave-one-out 예측 잔차(보정 없는 이동 대비), 105° 부분 회전 일반화, 속도 의존을 본다.
  사용: python job626_icrfit.py   (outputs/ 의 j567·j568·j572·j573·j574·j576·j578 을 읽음)"""
import math, re, os, statistics as st
import numpy as np

OUT = os.path.join(os.path.dirname(__file__), '..', 'outputs')
# 파일 → (블록, 속도 rad/s, 방향 −1 시계 / +1 반시계, 비고)
SRC = [('j567_s1_scanmatch.txt', 'S1', 0.38, -1), ('j568_s2.txt', 'S2', 0.38, +1), ('j572_r1.txt', 'R1', 0.38, -1),
       ('j573_r1b.txt', 'R1b', 0.38, -1), ('j574_r2.txt', 'R2', 0.20, -1), ('j576_r2b.txt', 'R2b', 0.20, -1), ('j578_r3.txt', 'R3', 0.20, +1)]
pat = re.compile(r'회전 (\d+): 중심 이동\(시작 차체 기준 앞\+/왼\+\) \(([-+0-9.]+), ([-+0-9.]+)\) = [0-9.]+ m \| 회전 스캔 ([-+0-9.]+)°')
data = []
for f, blk, w, dr in SRC:
    for line in open(os.path.join(OUT, f), encoding='utf-8'):
        m = pat.search(line)
        if m: data.append(dict(blk=blk, k=int(m.group(1)), w=w, dir=dr, d=np.array([float(m.group(2)), float(m.group(3))]), th=math.radians(float(m.group(4)))))


def p_of(d, th):
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]); return np.linalg.solve(np.eye(2) - R, d)


def d_of(p, th):
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]); return (np.eye(2) - R) @ p


full = [x for x in data if abs(abs(math.degrees(x['th'])) - 180) < 15]
part = [x for x in data if abs(abs(math.degrees(x['th'])) - 180) >= 15]
for x in data: x['p'] = p_of(x['d'], x['th'])
print('회전 %d 회(완전 %d, 부분 %d)' % (len(data), len(full), len(part)))
print('회별 회전축 치우침 p(차체 기준 앞+/왼+, cm):')
for x in data:
    print('  %-4s %d  %s %.2f rad/s  θ %+7.1f°  d (%+5.1f, %+5.1f) cm → p (%+5.1f, %+5.1f) cm' % (x['blk'], x['k'], '시계' if x['dir'] < 0 else '반시계', x['w'], math.degrees(x['th']), *(x['d'] * 100), *(x['p'] * 100)))

print('\n방향·속도별 p 평균(σ):')
groups = {}
for x in full: groups.setdefault((x['dir'], x['w']), []).append(x['p'])
for key, ps in sorted(groups.items()):
    a = np.array(ps); sd = a.std(axis=0, ddof=1) if len(a) > 1 else np.array([float('nan')] * 2)
    print('  %s %.2f: n=%d  p = (%+5.1f ± %.1f, %+5.1f ± %.1f) cm' % ('시계' if key[0] < 0 else '반시계', key[1], len(a), a[:, 0].mean() * 100, sd[0] * 100, a[:, 1].mean() * 100, sd[1] * 100))

print('\nleave-one-out(방향별 공용 p, 완전 회전):')
res, raw = [], []
for i, x in enumerate(full):
    others = [y['p'] for j, y in enumerate(full) if j != i and y['dir'] == x['dir']]
    if not others: continue
    pbar = np.mean(others, axis=0); e = np.linalg.norm(x['d'] - d_of(pbar, x['th'])); res.append(e); raw.append(np.linalg.norm(x['d']))
    print('  %-4s %d: 실제 %.1f cm → 예측 잔차 %.1f cm' % (x['blk'], x['k'], raw[-1] * 100, e * 100))
print('  잔차 중앙값 %.1f cm (평균 %.1f, 최대 %.1f) | 보정 없는 이동 중앙값 %.1f cm → 비 %.0f %%'
      % (st.median(res) * 100, st.mean(res) * 100, max(res) * 100, st.median(raw) * 100, 100 * st.median(res) / st.median(raw)))
print('  잔차 ≤ 7 cm 비율 %d/%d' % (sum(1 for e in res if e <= 0.07), len(res)))

print('\nleave-one-out(방향·속도별 p):')
res2 = []
for i, x in enumerate(full):
    others = [y['p'] for j, y in enumerate(full) if j != i and y['dir'] == x['dir'] and y['w'] == x['w']]
    if not others: print('  %-4s %d: 같은 방향·속도 다른 표본 없음' % (x['blk'], x['k'])); continue
    e = np.linalg.norm(x['d'] - d_of(np.mean(others, axis=0), x['th'])); res2.append(e)
print('  잔차 중앙값 %.1f cm (n=%d)' % (st.median(res2) * 100, len(res2)))

print('\n부분 회전 일반화(시계 공용 p 로 예측):')
pcw = np.mean([x['p'] for x in full if x['dir'] < 0], axis=0)
for x in part:
    pred = d_of(pcw, x['th'])
    print('  %s θ %+.1f°: 실제 (%+.1f, %+.1f) cm, 예측 (%+.1f, %+.1f) cm → 잔차 %.1f cm'
          % (x['blk'], math.degrees(x['th']), *(x['d'] * 100), *(pred * 100), np.linalg.norm(x['d'] - pred) * 100))
print('\n공용 p(보고용): 시계 (%+.3f, %+.3f) m, 반시계 (%+.3f, %+.3f) m'
      % (*pcw, *np.mean([x['p'] for x in full if x['dir'] > 0], axis=0)))
