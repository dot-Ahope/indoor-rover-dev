#!/usr/bin/env python3
"""fig_goal_yaw — §20.1 목표 방향 시험 결과를 한 장으로: 순간(행) × 목표 방향 더하기(열), 칸 색 = Smac 성공 · 실패, 오른쪽 = 출발 자세 (2026-10-26, PC).
  입력: outputs/planner_offline/goal_yaw/anal_goal_yaw.txt(jobs/anal_goal_yaw.py 출력). 인자: anal.txt 출력.png"""
import sys, re
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
T = open(sys.argv[1], encoding='utf-8').read()
START = {'115653': '(-1.68, -3.52, -83°) 북쪽 입구', '121553': '(-1.56, -4.57, -60°) 가장 좁은 곳', '122202': '(-1.56, -4.57, -61°) 가장 좁은 곳',
         '123521': '(-1.52, -5.38, -102°) 남쪽 끝', '125954': '(-1.47, -5.26, -183°) 남쪽 끝', '130865': '(-1.52, -4.91, 96°) 통로 안 · 북향'}
TIME = {'115653': '16:11:56.85', '121553': '16:12:15.53', '122202': '16:12:22.02', '123521': '16:12:35.21', '125954': '16:12:59.54', '130865': '16:13:08.65'}   # 장면 이름 꼬리표 → 질의 시각(꼬리표가 시각과 꼭 같지 않음)
OFF = [-90, -60, -45, -30, -15, 0, 15, 30, 45, 60, 90, 135, 180]
rows = []
for tag in START:
    blk = T.split('== %s' % tag)[1].split('\n== ')[0]; d = {}
    for m in re.finditer(r'^\s+([+-]\d+) \|\s+[-\d]+° \|\s+(\d+) ·\s+\d+ \| (성공|실패)', blk, re.M): d[int(m.group(1))] = (m.group(3) == '성공', int(m.group(2)))
    rows.append((tag, d))
fig, ax = plt.subplots(figsize=(11, 3.6))
for i, (tag, d) in enumerate(rows):
    for j, o in enumerate(OFF):
        if o not in d: ax.add_patch(plt.Rectangle((j, i), 1, 1, fc='#eeeeee', ec='white')); continue
        ok, c = d[o]; ax.add_patch(plt.Rectangle((j, i), 1, 1, fc='#1f7a72' if ok else '#b3263e', ec='white', lw=2))
        ax.text(j + .5, i + .5, str(c), ha='center', va='center', color='white', fontsize=8)
    ax.text(-0.2, i + .5, TIME[tag], ha='right', va='center', fontsize=10)
    ax.text(len(OFF) + .2, i + .5, START[tag], ha='left', va='center', fontsize=9, color='#5b6470')
ax.set_xlim(-3.2, len(OFF) + 6.5); ax.set_ylim(len(rows), -0.9); ax.axis('off')
for j, o in enumerate(OFF): ax.text(j + .5, -0.35, '%+d°' % o if o else '원래', ha='center', fontsize=8.5, color='#5b6470')
ax.text(len(OFF) / 2, -0.85, '목표 방향 더하기 — 칸 색 초록 = Smac 성공 · 빨강 = 실패, 칸 숫자 = 목표 자세 차체 아래 치명 칸 수(내 지표)', ha='center', fontsize=9.5)
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=130); print('저장', sys.argv[2])
