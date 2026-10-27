#!/usr/bin/env python3
"""anal_sys_perf — §30 현재 시스템 성능 요약용 수치: tegrastats(CPU · GPU · RAM · 전력 · 온도) 주행 구간 통계 (2026-10-27, PC).
  인자: 이름=tegra.log=시작HH:MM:SS=끝HH:MM:SS …"""
import sys, re, time
import numpy as np
for a in sys.argv[1:]:
    nm, f, t0, t1 = a.split('=')
    T0 = time.mktime(time.strptime('2026-10-27 ' + t0, '%Y-%m-%d %H:%M:%S')); T1 = time.mktime(time.strptime('2026-10-27 ' + t1, '%Y-%m-%d %H:%M:%S'))
    R = []
    for l in open(f, encoding='utf-8', errors='replace'):
        m = re.match(r'(\d\d-\d\d-\d{4} \d\d:\d\d:\d\d) RAM (\d+)/(\d+)MB.*?CPU \[([^\]]+)\].*?GR3D_FREQ (\d+)%.*?tj@([\d.]+)C.*?VDD_IN (\d+)mW', l)
        if not m: continue
        t = time.mktime(time.strptime(m[1], '%m-%d-%Y %H:%M:%S'))
        if not T0 <= t <= T1: continue
        cores = [int(x) for x in re.findall(r'(\d+)%@', m[4])]
        R.append((int(m[2]), int(m[3]), np.mean(cores), int(m[5]), float(m[6]), int(m[7])))
    R = np.array(R)
    print('%s: %d s · CPU 코어 평균 중앙 %.0f %%(90 %% %.0f) · GPU 중앙 %.0f %%(90 %% %.0f) · RAM %.0f/%.0f MB · 전력 VDD_IN 평균 %.2f W(최대 %.2f) · tj 최대 %.1f °C' % (
        nm, len(R), np.median(R[:, 2]), np.percentile(R[:, 2], 90), np.median(R[:, 3]), np.percentile(R[:, 3], 90), R[:, 0].mean(), R[0, 1], R[:, 5].mean() / 1000, R[:, 5].max() / 1000, R[:, 4].max()))
