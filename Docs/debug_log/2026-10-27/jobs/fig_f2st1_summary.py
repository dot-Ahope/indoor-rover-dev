#!/usr/bin/env python3
"""fig_f2st1_summary — §11 f2st1 결과를 f2sa3(10-26, tol 0.25) · f2rp4(10-23, B0 NavFn)와 한 장으로 (2026-10-27 §12, PC).
  값의 출처(손으로 옮긴 것 — 원문 위치):
    목표별 시간 = 각 run_*.txt('목표 N SUCCEEDED'): 10-27 outputs/drives/f2st1/run_f2st1.txt · 10-26 outputs/drives/f2sa3/run_f2sa3.txt · f2rp4 = 10-26 SUMMARY §14.1 인용값
    통로 최소 여유 = anal_band_run_*.txt(전체 최소 · 남행 좁은 곳 구간 최소) · 정지 = anal_stops_*.txt · 상자 복귀 = anal_contact_*_d30.txt · Smac 실패 = nav2 로그 'SmacHybrid: failed'
  인자: 출력.png"""
import sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
G = ['1 B', '2 C', '3 통로 북', '4 남행(통로)', '5 북행(통로)', '6 위 복도', '7 W3', '8 출발']
T = {'f2rp4 · B0 NavFn(10-23)': [51.7, 54.1, 28.5, 26.2, 32.6, 24.4, 98.6, 101.3],
     'f2sa3 · Smac tol 0.25(10-26)': [52.3, 55.4, 26.4, 39.7, 49.8, 22.9, 96.7, 104.4],
     'f2st1 · Smac tol 0.35(10-27)': [51.3, 55.3, 27.7, 24.7, 31.9, 23.9, 103.4, 108.8]}
C = ['#9aa4b0', '#c2255c', '#1f7a72']
fig, (a, b) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [1.5, 1]})
x = np.arange(len(G)); w = 0.27
for i, (k, v) in enumerate(T.items()):
    a.bar(x + (i - 1) * w, v, w, color=C[i], label='%s · 총 %.1f s' % (k, sum(v)))
for j in (3, 4):
    for i, (k, v) in enumerate(T.items()): a.text(x[j] + (i - 1) * w, v[j] + 1.5, '%.1f' % v[j], ha='center', fontsize=9)
a.set_xticks(x); a.set_xticklabels(G, fontsize=9.5, rotation=20); a.set_ylabel('목표까지 시간 (s)'); a.legend(fontsize=9.5, frameon=False, loc='upper left')
a.set_title('목표별 시간 — 통로 남행(4) · 북행(5)', loc='left', fontsize=12); a.grid(axis='y', color='#e5e7eb'); a.set_axisbelow(True)
# 오른쪽: 통로 · 정지 · 상자 지표(f2sa3 대 f2st1)
M = [('통로 남행 좁은 곳 최소 여유 (cm)', 0.8, 4.1, '↑'), ('통로 전체 최소 여유 (cm)', 0.8, 2.9, '↑'), ('여유 < 2.7 cm 프레임', 7, 0, '↓'),
     ('1 s 넘는 정지 횟수', 5, 1, '↓'), ('1 s 넘는 정지 합 (s)', 15.3, 4.7, '↓'), ('통로 Smac 실패(남행 · 북행)', '3 · 2', '0 · 3', ''), ('출발 상자 복귀 최소 (cm)', 13.2, 16.3, '↑')]
b.axis('off'); b.set_xlim(0, 1); b.set_ylim(0, 1); y = 0.95
b.text(0.0, y, '지표', fontsize=11, weight='bold'); b.text(0.62, y, 'f2sa3', fontsize=11, weight='bold', color=C[1]); b.text(0.82, y, 'f2st1', fontsize=11, weight='bold', color=C[2])
for name, v0, v1, good in M:
    y -= 0.10; b.text(0.0, y, name, fontsize=10.5); b.text(0.62, y, str(v0), fontsize=11); b.text(0.82, y, str(v1), fontsize=11, weight='bold', color=C[2])
    b.plot([0, 1], [y - 0.035, y - 0.035], color='#e5e7eb', lw=0.8)
b.text(0.0, 0.0, '남행은 Smac 경로(통로 가운데 쪽)로 바뀜.\n북행은 남쪽 끝 출발에서 Smac 실패 → NavFn 그대로\n(전체 최소 2.9 cm 도 그 구간).\nf2sa3 통로 Smac 실패 5 = 남행 3 · 북행 2(10-26 §19). 각 1 회 주행.', fontsize=9.5, color='#5b6470', va='bottom')
b.set_title('통로 · 정지 · 상자 지표', loc='left', fontsize=12)
fig.suptitle('f2st1 — Smac 허용치 0.25 → 0.35 만 바꾼 no5 주행(8/8)', x=0.01, ha='left', fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(sys.argv[1], dpi=110); print('저장', sys.argv[1])
