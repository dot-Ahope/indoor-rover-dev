#!/usr/bin/env python3
"""anal_tolcp — §5 허용치 · cost_penalty 재질의 표 (2026-10-27, PC, 로버 안 움직임).
  입력: outputs/tolcp/result_<V>.npz · run_<V>.txt(왕복 시간 · 실패 문구), 장면 10-26 scenes_expdbg.npz.
  순간 × 변형: Smac 성공/실패, 왕복 s, 성공이면 경로 길이 · 끝 ↔ 목표 거리(m) · 끝 방향 − 목표 방향(°). 인자: tolcp폴더 장면.npz"""
import sys, json, math, re
from pathlib import Path
import numpy as np
O = Path(sys.argv[1]); SC = np.load(sys.argv[2]); meta = json.loads(str(SC['meta']))
VAR = [('V0', 0.25, 30), ('V1', 0.35, 30), ('V2', 0.50, 30), ('V3', 0.25, 15), ('V4', 0.35, 15)]
TIME = {'sa3_115653': '16:11:56.85 남행', 'sa3_121553': '16:12:15.53 남행', 'sa3_122202': '16:12:22.02 남행', 'sa3_123521': '16:12:35.21 북행', 'sa3_125954': '16:12:59.54 북행', 'sa3_130865': '16:13:08.65 북행'}
LIVE = {'sa3_130865': '성공'}
print('Smac_R10_C{cp}_A10_RS(설치판, 시간 상한 2.0 s) — 칸 = 결과 · 왕복 s [· 길이 m · 끝↔목표 cm · 끝 방향 차 °]')
print('순간(실주행) | ' + ' | '.join('%s tol %.2f cp %.1f' % (n, t, c / 10) for n, t, c in VAR))
rows = {}
for n, t, c in VAR:
    f = O / ('result_%s.npz' % n)
    if not f.exists(): continue
    R = np.load(f); P = 'Smac_R10_C%d_A10_RS' % c
    wall = {}; cur = None
    for l in open(O / ('run_%s.txt' % n), encoding='utf-8', errors='replace'):
        m = re.search(r'(sa3_\d+): 재구성', l)   # 첫 장면 줄 앞에 공백이 붙어 나옴(match 로는 놓침)
        if m: cur = m.group(1)
        m = re.search(P + r'\s+\S+.*?왕복 ([\d.]+) s', l)
        if m and cur: wall[cur] = float(m.group(1))
    for sc in meta:
        k = sc['name']; p = R['%s/%s/path' % (k, P)] if '%s/%s/path' % (k, P) in R else np.zeros((0, 3)); g = SC[k + '/goal']
        if len(p):
            L = float(np.hypot(*np.diff(p[:, :2], axis=0).T).sum()); d = math.hypot(p[-1, 0] - g[0], p[-1, 1] - g[1])
            dy = (math.degrees(p[-1, 2] - g[2]) + 180) % 360 - 180
            cell = '성공 %.2f · %.2f m · %.1f cm · %+.0f°' % (wall.get(k, -1), L, 100 * d, dy)
        else: cell = '실패 %.2f' % wall.get(k, -1)
        rows.setdefault(k, []).append(cell)
for sc in meta:
    k = sc['name']; print('%s(%s) | %s' % (TIME[k], LIVE.get(k, '실패'), ' | '.join(rows.get(k, []))))
