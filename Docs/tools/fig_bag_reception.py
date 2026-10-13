#!/usr/bin/env python3
"""fig_bag_reception — bag 기록기가 토픽별로 '제때 받았는지'를 시간축으로 그린다. (2026-10-13)
  왜: 포화가 생긴 주행(f2m1)과 기록기 /tf 를 best effort 로 바꾼 주행(f2n1)에서 수신에 문제가 있었는지 눈으로 비교.
  그림: 주행마다 ① 토픽 × 시간(2 s 칸) 수신 부족률(= 1 − 받은 수 / 그 토픽의 평상 수, 평상 = 기준 주행의 칸 중앙값) ② /tf 메시지 간격(가장 긴 간격, 칸마다).
  주의: bag 시각은 기록기가 받은 시각이다. 발행 자체가 멈춘 것(목표 사이 대기 등)과 못 받은 것은 이 그림만으로는 구분되지 않는다.
  사용: fig_bag_reception.py 출력.png 기준이름 이름=bag폴더[:세로선 HH:MM:SS:설명] ..."""
import sys, time, collections
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
TS = get_typestore(Stores.ROS2_HUMBLE); STEP = 2.0
out, ref = sys.argv[1], sys.argv[2]; runs = []
for a in sys.argv[3:]:
    name, rest = a.split('=', 1); mark = None
    if '|' in rest: rest, m = rest.split('|', 1); mark = m.split('|')
    runs.append((name, rest, mark))
D = {}
for name, path, mark in runs:
    stamps = collections.defaultdict(list)
    with AnyReader([Path(path)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(): stamps[c.topic].append(t / 1e9)
    t0 = min(v[0] for v in stamps.values()); t1 = max(v[-1] for v in stamps.values())
    D[name] = dict(st={k: np.array(v) for k, v in stamps.items()}, t0=t0, n=int((t1 - t0) / STEP))
def binned(d, topic): return np.histogram(d['st'].get(topic, np.array([])) - d['t0'], bins=d['n'], range=(0, d['n'] * STEP))[0] / STEP
# 평상 주기 = 기준 주행의 칸 중앙값. 1 Hz 미만 토픽은 2 s 칸으로 판단할 수 없어 뺀다.
nom = {t: np.median(binned(D[ref], t)) for t in D[ref]['st']}
topics = [t for t in sorted(nom, key=lambda t: -nom[t]) if nom[t] >= 1.0 and all(t in D[r[0]]['st'] for r in runs)]
fig, axes = plt.subplots(2 * len(runs), 1, figsize=(13, 5.4 * len(runs)), gridspec_kw=dict(height_ratios=[3.2, 1] * len(runs), hspace=0.62))
for i, (name, path, mark) in enumerate(runs):
    d = D[name]; ax = axes[2 * i]; ax2 = axes[2 * i + 1]
    M = np.array([np.clip(1 - binned(d, t) / nom[t], 0, 1) for t in topics]) * 100
    im = ax.imshow(M, aspect='auto', cmap='Reds', vmin=0, vmax=100, extent=(0, d['n'] * STEP, len(topics), 0), interpolation='nearest')
    ax.set_yticks(np.arange(len(topics)) + 0.5); ax.set_yticklabels(['%s (%.0f Hz)' % (t, nom[t]) for t in topics], fontsize=8)
    ax.set_title('%s — 토픽별 수신 부족률(2 s 칸, 흰색 = 평상만큼 받음, 진한 빨강 = 하나도 못 받음)' % name, fontsize=11, loc='left')
    for y in range(1, len(topics)): ax.axhline(y, color='white', lw=0.6)
    tf = d['st']['/tf'] - d['t0']; gap = np.diff(tf); idx = (tf[1:] / STEP).astype(int); g = np.zeros(d['n'])
    for k, v in zip(idx, gap):
        if k < d['n']: g[k] = max(g[k], v)
    x = (np.arange(d['n']) + 0.5) * STEP; g[g == 0] = np.nan   # 한 개도 못 받은 칸은 간격을 잴 수 없어 비움(다음 칸에 긴 간격으로 나타남)
    ax2.plot(x, g * 1000, color='#1f4e79', lw=1.6); ax2.axhline(20, color='#888', lw=0.8, ls=':'); ax2.set_yscale('log'); ax2.set_ylim(10, 20000)
    ax2.set_ylabel('/tf 최대 간격 (ms)\n점선 = 평상 20 ms', fontsize=8); ax2.set_xlim(0, d['n'] * STEP); ax.set_xlim(0, d['n'] * STEP)
    ax2.set_xlabel('bag 시작부터 (s) — 시작 %s' % time.strftime('%H:%M:%S', time.localtime(d['t0'])), fontsize=9); ax2.grid(axis='y', color='#ddd', lw=0.5)
    ax2.set_title('최대 %.0f ms · 100 ms 넘는 간격 %d 번' % (gap.max() * 1000, (gap > 0.1).sum()), fontsize=9, loc='left', color='#333')
    if mark:
        tm = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(d['t0'])) + mark[0], '%Y-%m-%d %H:%M:%S')) - d['t0']
        for a_ in (ax, ax2): a_.axvline(tm, color='#222', lw=1.2, ls='--')
        ax2.text(tm + 1.5, 9000, mark[1], fontsize=9, color='#222', va='top')
cb = fig.colorbar(im, ax=axes, fraction=0.012, pad=0.01); cb.set_label('수신 부족률 (%)', fontsize=9)
fig.savefig(out, dpi=130, bbox_inches='tight'); print('저장', out, '토픽', len(topics))
for name, _, _ in runs:
    d = D[name]; print(name, ' '.join('%s %.0f%%' % (t.split('/')[-1], 100 * len(d['st'][t]) / (nom[t] * d['n'] * STEP)) for t in topics))
