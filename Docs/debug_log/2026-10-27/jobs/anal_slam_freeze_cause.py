#!/usr/bin/env python3
"""anal_slam_freeze_cause — §22 SLAM map→odom stamp 정체가 통신(UDP) 탓인가 처리 탓인가 (2026-10-27, PC).
  정체 = 새 stamp 간격 > 0.4 s. 각 정체 구간 [이전 stamp 수신, 다음 새 stamp 수신] 에서:
    (가) /scan 의 bag 수신 최대 간격 · (나) odom→base_link(/tf, EKF) bag 수신 최대 간격 · (다) map→odom 발행 자체의 최대 간격
    (라) 1 s top 의 SLAM 프로세스 %CPU(구간과 겹치는 초의 최대) · (마) slam.log 'Message Filter dropping' 수
  기준선: 정체 아닌 같은 길이 구간 무작위 200 개의 같은 지표.
  주의: bag 기록기도 UDP 로 받는 별도 프로세스 — bag 에서 입력이 고르게 왔다면 '보내는 쪽 · 망' 은 정상이었다는 뜻이고,
        SLAM 프로세스 안쪽 수신(같은 UDP 경로)이 늦었는지는 직접 못 봄 → (라) CPU 와 함께 판단.
  인자: bag폴더 top1s.txt slam.log SLAM_PID"""
import sys, re, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
MO, SC, OB = [], [], []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/scan')]):
        ts = t * 1e-9
        if c.topic == '/scan': SC.append(ts); continue
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append(ts)
MO = np.array(MO); SC = np.array(SC); OB = np.array(sorted(OB))
# top 1 s: 시각 → SLAM %CPU
PID = sys.argv[4]; cpu = {}; cur = None; day = '2026-10-27 '
for l in open(sys.argv[2], encoding='utf-8', errors='replace'):
    m = re.match(r'top - (\d\d:\d\d:\d\d)', l)
    if m: cur = time.mktime(time.strptime(day + m[1], '%Y-%m-%d %H:%M:%S')); continue
    p = l.split()
    if cur and p and p[0] == PID: cpu[cur] = float(p[8])
CT = np.array(sorted(cpu)); CV = np.array([cpu[t] for t in CT])
drops = []
for l in open(sys.argv[3], encoding='utf-8', errors='replace'):
    if 'Message Filter dropping' in l:
        m = re.search(r'\[(\d{10}\.\d+)\]', l)
        if m: drops.append(float(m[1]))
drops = np.array(drops)
def maxgap(T, a, b):
    s = T[(T >= a) & (T <= b)]; s = np.r_[T[T < a][-1:] if (T < a).any() else [], s, T[T > b][:1] if (T > b).any() else []]
    return float(np.diff(s).max()) if len(s) > 1 else float('nan')
def feats(a, b):
    k = (CT >= np.floor(a)) & (CT <= np.ceil(b) + 1)
    return (maxgap(SC, a, b), maxgap(OB, a, b), maxgap(MO[:, 0], a, b), CV[k].max() if k.any() else np.nan, int(((drops >= a - 0.3) & (drops <= b)).sum()))
# 정체 구간
new = np.r_[True, np.diff(MO[:, 1]) != 0]; NI = np.nonzero(new)[0]
fz = [(MO[NI[i], 0], MO[NI[i + 1], 0]) for i in range(len(NI) - 1) if MO[NI[i + 1], 1] - MO[NI[i], 1] > 0.4]
t0, t1 = MO[0, 0] + 2, MO[-1, 0] - 2
F = np.array([feats(a, b) for a, b in fz])
rng = np.random.default_rng(0); L = np.median([b - a for a, b in fz]); base = []
while len(base) < 200:
    a = rng.uniform(t0, t1 - L)
    if any(a < y and a + L > x for x, y in fz): continue
    base.append(feats(a, a + L))
B = np.array(base)
lab = ['/scan 최대 수신 간격 s', 'odom→base_link 최대 수신 간격 s', 'map→odom 발행 최대 간격 s', 'SLAM %CPU(최대, 1 s top)', 'SLAM 스캔 버림 수']
print('정체(새 stamp 간격 > 0.4 s) %d 구간 · 길이 중앙 %.2f s | 기준선(정체 아님, 같은 길이) 200 구간' % (len(fz), L))
for j, nm in enumerate(lab):
    print('  %-32s 정체: 중앙 %.3f · 90%% %.3f | 기준선: 중앙 %.3f · 90%% %.3f' % (nm, np.nanmedian(F[:, j]), np.nanpercentile(F[:, j], 90), np.nanmedian(B[:, j]), np.nanpercentile(B[:, j], 90)))
print('  정체 중 /scan 간격 > 0.2 s 인 구간 %d/%d · odom→base_link 간격 > 0.2 s %d/%d · SLAM CPU ≥ 90 %% %d/%d · 스캔 버림 ≥ 1 %d/%d' % (
    (F[:, 0] > 0.2).sum(), len(F), (F[:, 1] > 0.2).sum(), len(F), (F[:, 3] >= 90).sum(), len(F), (F[:, 4] >= 1).sum(), len(F)))
print('  SLAM %%CPU 전체 분포: 중앙 %.0f · 90%% %.0f · 최대 %.0f (top 은 코어 1 개 = 100 %%)' % (np.median(CV), np.percentile(CV, 90), CV.max()))
