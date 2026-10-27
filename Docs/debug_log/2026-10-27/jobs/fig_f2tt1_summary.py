#!/usr/bin/env python3
"""fig_f2tt1_summary — §27 f2tt1(transform_timeout 1.5) 결과를 f2st1 · f2tf1 과 한 장으로 (2026-10-27, PC).
  위: SLAM map→odom '지금 조회 여유'(= 그때까지 받은 최신 stamp - 지금) 시간선 — f2tf1(0.5) vs f2tt1(1.5), 0 아래 = 조회 실패 창,
      nav2 odom→map 외삽 실패 시각(nav2 로그 'Requested time') 점. bag /tf 에서 직접 계산.
  아래 왼쪽: 지표 표(값은 원문에서 옮김 — 출처: run_*.txt · outputs/load/anal_slam_freeze_*.txt · outputs/tffix/anal_tffix_sig_*.txt ·
      outputs/drives/*/anal_stops_* · anal_band_run_* · anal_contact_*_d30). 아래 오른쪽: 목표별 시간.
  인자: f2tf1bag f2tt1bag f2tf1_nav2.log f2tt1_nav2.log 출력.png"""
import sys, re
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
C = {'f2st1': '#9aa4b0', 'f2tf1': '#c2255c', 'f2tt1': '#1f7a72'}


def margin(bag):
    R = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
            for tr in rd.deserialize(raw, c.msgtype).transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': R.append((t * 1e-9, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
    R = np.array(sorted(R)); best = np.maximum.accumulate(R[:, 1])
    tt = np.arange(R[0, 0], R[-1, 0], 0.02); k = np.searchsorted(R[:, 0], tt, side='right') - 1
    return tt - R[0, 0], best[k] - tt, R[0, 0]


def fails(log, t0):
    v = []
    for l in open(log, encoding='utf-8', errors='replace'):
        if 'extrapolation into the future' in l and 'frame [odom] to frame [map]' in l:
            m = re.search(r'Requested time ([\d.]+)', l)
            if m: v.append(float(m[1]) - t0)
    return np.array(v)


fig = plt.figure(figsize=(15, 9.6)); gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1], width_ratios=[1.15, 1], hspace=0.32, wspace=0.12)
a = fig.add_subplot(gs[0, :])
for nm, bag, log, off in (('f2tf1', sys.argv[1], sys.argv[3], 0.0), ('f2tt1', sys.argv[2], sys.argv[4], 0.0)):
    t, m, t0 = margin(bag); fl = fails(log, t0); fl = fl[(fl >= 0) & (fl <= t[-1])]
    lab = '%s · transform_timeout %s · 여유 0 아래 %.1f s · nav2 조회 실패 %d' % (nm, '0.5' if nm == 'f2tf1' else '1.5', 0.02 * (m < 0).sum(), len(fl))
    a.plot(t, m, color=C[nm], lw=0.7, label=lab)
    if len(fl): a.plot(fl, np.interp(fl, t, m), 'v', color=C[nm], ms=7, mec='#1b1f24', mew=0.6)
a.axhline(0, color='#1b1f24', lw=1); a.fill_between([0, 425], -1.2, 0, color='#fde2e4', zorder=0)
a.text(3, -0.55, '0 아래 = SLAM 이 아직 stamp 를 못 냄 → nav2 의 지금 시각 odom→map 조회 실패(▼ = 실제 실패)', fontsize=9.5, color='#b3263e')
a.set_xlim(0, 425); a.set_ylim(-0.9, 2.25); a.set_xlabel('주행 시작부터 시간 (s)'); a.set_ylabel('지금 조회 여유 (s)')
a.legend(loc='upper left', fontsize=10, frameon=False, ncol=1); a.grid(color='#eceef1')
a.set_title('SLAM map→odom 미래 여유 — 정체(톱니가 내려가는 구간)는 두 주행에 같이 있고, 1.5 s 여유가 0 아래로 못 내려가게 막음', loc='left', fontsize=11.5)
# 표
b = fig.add_subplot(gs[1, 0]); b.axis('off'); b.set_xlim(0, 1); b.set_ylim(0, 1)
M = [('nav2 odom→map 조회 실패(층 · 컨트롤러)', '22 · 1', '28 · 5', '0 · 0'),
     ('틀어진 전역 장(§15 서명)', '3', '0', '0'),
     ('SLAM 정체 > 0.5 s · 최대', '26 · 0.91 s', '36 · 1.30 s', '33 · 1.10 s'),
     ('미래 여유 중앙 · 최소', '0.46 · -0.12 s', '0.44 · -0.31 s', '1.45 · 1.14 s'),
     ('Control loop missed', '70', '84', '43'),
     ('1 s 넘는 정지', '1 번 4.7 s', '1 번 5.1 s', '0'),
     ('통로 최소 정확 여유', '2.9 cm', '3.8 cm', '3.1 cm'),
     ('출발 상자 복귀 최소', '16.3 cm', '-1.0 cm(접촉)', '14.4 cm'),
     ('바뀐 것', 'Smac tol 0.35', '+ nvblox 층 수정', '+ timeout 1.5')]
x = [0.0, 0.50, 0.68, 0.86]; y = 0.96
for i, h in enumerate(['지표', 'f2st1', 'f2tf1', 'f2tt1']): b.text(x[i], y, h, fontsize=11, weight='bold', color=('#1b1f24' if i == 0 else C[h]))
for row in M:
    y -= 0.098; b.plot([0, 1], [y + 0.062, y + 0.062], color='#e5e7eb', lw=0.8)
    for i, v in enumerate(row): b.text(x[i], y, v, fontsize=9.6 if i else 10, color=('#1b1f24' if i != 3 else C['f2tt1']), weight=('bold' if i == 3 else 'normal'))
b.set_title('지표(각 1 회 주행)', loc='left', fontsize=11.5)
# 목표 시간
c = fig.add_subplot(gs[1, 1]); G = ['1 B', '2 C', '3 통로 북', '4 남행', '5 북행', '6 위 복도', '7 W3', '8 출발']
T = {'f2st1': [51.3, 55.3, 27.7, 24.7, 31.9, 23.9, 103.4, 108.8], 'f2tf1': [52.3, 54.8, 28.6, 25.7, 29.8, 22.6, 98.0, 100.8], 'f2tt1': [50.7, 54.3, 28.0, 24.7, 32.3, 23.8, 96.6, 101.5]}
xx = np.arange(8); w = 0.27
TOT = {'f2st1': 427.5, 'f2tf1': 412.8, 'f2tt1': 412.2}   # 러너 '총' 값(목표별 값은 0.1 s 반올림이라 합이 조금 다름)
for i, (k, v) in enumerate(T.items()): c.bar(xx + (i - 1) * w, v, w, color=C[k], label='%s · 총 %.1f s' % (k, TOT[k]))
c.set_xticks(xx); c.set_xticklabels(G, rotation=25, fontsize=9); c.set_ylabel('목표까지 시간 (s)'); c.legend(fontsize=9, frameon=False, loc='upper left')
c.grid(axis='y', color='#eceef1'); c.set_axisbelow(True); c.set_title('목표별 시간', loc='left', fontsize=11.5)
fig.suptitle('f2tt1 — SLAM 위치 추정 transform_timeout 0.5 → 1.5: nav2 TF 실패 33 → 0 · 정지 1 → 0 (8/8, 접촉 없음)', x=0.01, ha='left', fontsize=13.5)
fig.savefig(sys.argv[5], dpi=105, bbox_inches='tight'); print('저장', sys.argv[5])
