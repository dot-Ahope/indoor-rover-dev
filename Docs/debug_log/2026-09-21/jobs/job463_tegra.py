#!/usr/bin/env python3
"""S5 기준선: tegrastats 로그 요약 (2026-09-21 §7). 인자: tegra_<이름>.log [...]
  RAM 사용, CPU 코어 평균 부하·클럭, GR3D(GPU) 사용률, 온도(cpu/gpu/tj), 전력(VDD_IN, VDD_CPU_GPU_CV) — 평균·최대. 주행 창 = 파일 전체(러너가 주행 앞뒤 4 s 만 더 기록).
"""
import sys, re
import numpy as np
for p in sys.argv[1:]:
    ram, cpu, clk, gpu, tcpu, tgpu, tj, pin, pcg = [], [], [], [], [], [], [], [], []
    for ln in open(p, encoding='utf-8', errors='replace'):
        m = re.search(r'RAM (\d+)/(\d+)MB', ln)
        if not m: continue
        ram.append(int(m.group(1)))
        cores = re.findall(r'(\d+)%@(\d+)', ln); cpu.append(np.mean([int(c[0]) for c in cores])); clk.append(np.mean([int(c[1]) for c in cores]))
        g = re.search(r'GR3D_FREQ (\d+)%', ln); gpu.append(int(g.group(1)) if g else 0)
        for key, lst in (('cpu@', tcpu), ('gpu@', tgpu), ('tj@', tj)):
            t = re.search(key + r'([\d.]+)C', ln); lst.append(float(t.group(1)) if t else float('nan'))
        v = re.search(r'VDD_IN (\d+)mW', ln); pin.append(int(v.group(1)) if v else float('nan'))
        v = re.search(r'VDD_CPU_GPU_CV (\d+)mW', ln); pcg.append(int(v.group(1)) if v else float('nan'))
    n = len(ram)
    if not n: print('%s: 표본 없음' % p); continue
    f = lambda a: (np.nanmean(a), np.nanmax(a))
    print('%s: %d s | RAM %.0f/%.0f MB(최대) | CPU 6코어 평균 %.0f%% 최대 %.0f%%, 클럭 평균 %.0f MHz | GPU(GR3D) 평균 %.1f%% 최대 %.0f%% | 온도 cpu %.1f gpu %.1f tj %.1f(최대 %.1f) °C | 전력 VDD_IN 평균 %.0f 최대 %.0f mW, CPU+GPU+CV 평균 %.0f mW' % (
        p.split('/')[-1], n, np.mean(ram), np.max(ram), *f(cpu), np.mean(clk), *f(gpu), np.nanmean(tcpu), np.nanmean(tgpu), np.nanmean(tj), np.nanmax(tj), *f(pin), np.nanmean(pcg)))
