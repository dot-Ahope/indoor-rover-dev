#!/usr/bin/env python3
"""anal_slam_freeze — §21 SLAM map→odom stamp 멈춤 분석 (2026-10-27, PC).
  bag /tf map→odom: stamp 가 안 바뀐 구간(수신 기준 길이) 분포, 미래 여유(stamp − 수신)가 0 아래로 내려간 구간 = 조회 실패 창.
  slam.log 'Message Filter dropping' 시각 · nav2.log odom→map 외삽 실패 시각과 겹침. 인자: bag폴더 slam.log nav2.log"""
import sys, re, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
R = []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': R.append((t * 1e-9, tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9))
R = np.array(R); t0, t1 = R[0, 0], R[-1, 0]
# 같은 stamp 구간
seg = []; s = 0
for i in range(1, len(R) + 1):
    if i == len(R) or R[i, 1] != R[s, 1]:
        seg.append((R[s, 0], R[i - 1, 0], R[s, 1])); s = i
# 각 stamp 가 '유효한' 마지막 시각 = 다음 stamp 수신 직전; 그 동안 지금 − stamp 가 > 0 이면 '현재 시각 조회 실패' 창
fail = []
for k in range(len(seg) - 1):
    st = seg[k][2]; nxt = seg[k + 1][0]
    if nxt > st: fail.append((st, nxt, nxt - st, seg[k + 1][2] - st))
gap = np.array([seg[k + 1][2] - seg[k][2] for k in range(len(seg) - 1)])
margin = np.array([seg[k][2] - seg[k][0] for k in range(len(seg))])
print('bag %s~%s (%.0f s) · map→odom %d 개 · 서로 다른 stamp %d 개' % (hs(t0), hs(t1), t1 - t0, len(R), len(seg)))
print('stamp 새로 바뀌는 간격: 중앙 %.3f · 99%% %.3f · 최대 %.3f s · > 0.5 s %d 번 · > 0.4 s %d 번' % (np.median(gap), np.percentile(gap, 99), gap.max(), (gap > 0.5).sum(), (gap > 0.4).sum()))
print('새 stamp 가 처음 올 때의 미래 여유(stamp − 수신): 중앙 %.3f · 최소 %.3f s' % (np.median(margin), margin.min()))
print('현재 시각 조회가 실패하는 창(여유 소진) %d 번 · 합 %.2f s:' % (len(fail), sum(f[2] for f in fail)))
drops = []
for l in open(sys.argv[2], encoding='utf-8', errors='replace'):
    if 'Message Filter dropping' in l:
        m = re.search(r'\[(\d{10}\.\d+)\]', l)
        if m and t0 <= float(m[1]) <= t1: drops.append(float(m[1]))
fails = []
for l in open(sys.argv[3], encoding='utf-8', errors='replace'):
    if 'extrapolation into the future' in l and 'frame [odom] to frame [map]' in l:
        m = re.search(r'Requested time ([\d.]+)', l)
        if m and t0 <= float(m[1]) <= t1: fails.append(float(m[1]))
for a, b, d, jump in fail:
    nf = sum(a <= f <= b for f in fails); nd = sum(a - 1.5 <= x <= b for x in drops)
    print('  %s ~ %s  %.2f s (다음 stamp 는 %.2f s 뒤 것) · 그 창 안 nav2 조회 실패 %d · 직전 1.5 s~창 안 SLAM 스캔 버림 %d' % (hs(a), hs(b), d, jump, nf, nd))
inside = sum(any(a <= f <= b for a, b, _, _ in fail) for f in fails)
print('nav2 odom→map 외삽 실패 %d 번 중 위 창 안 %d 번 · SLAM 스캔 버림 %d 번(주행 창)' % (len(fails), inside, len(drops)))
