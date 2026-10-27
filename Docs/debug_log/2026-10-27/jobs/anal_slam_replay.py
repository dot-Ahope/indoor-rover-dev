#!/usr/bin/env python3
"""anal_slam_replay — §26 SLAM 재생 변형별: map→odom stamp 정체 · 미래 여유 · SLAM CPU · 원래 주행 SLAM 과의 위치 차 (2026-10-27, PC).
  입력: Docs/tools/run_slam_replay.sh 출력(<변형>.txt: 'MO sim수신 stamp x y yaw' · 'CPU sim 틱') · 원래 bag(map→odom 기준값).
  위치 차: 재생 map→odom 을 원래 map→odom(같은 bag 시각, 마지막 값)과 비교 — 로버 위치 오차와 같음(odom 이 같으므로). 첫 5 s 제외.
  인자: 원bag폴더 변형.txt…"""
import sys, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
REF = []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': REF.append((t * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
REF = np.array(sorted(REF))
print('변형 | MO 수 | 새 stamp 간격 중앙 · 99% · 최대 | >0.4 · >0.5 s | 여유(stamp−수신) 최소 · 중앙 | SLAM CPU 평균 % | 원래 SLAM 대비 위치 차 중앙 · 최대 cm · yaw 차 최대 °')
for f in sys.argv[2:]:
    M = []; C = []
    for l in open(f):
        p = l.split()
        if p[0] == 'MO': M.append(list(map(float, p[1:])))
        elif p[0] == 'CPU': C.append((float(p[1]), int(p[2])))
    M = np.array(M); t0 = M[0, 0]
    new = np.r_[True, np.diff(M[:, 1]) != 0]; S = M[new]; g = np.diff(S[:, 1]); mar = S[:, 1] - S[:, 0]
    cpu = (C[-1][1] - C[0][1]) / 100.0 / (C[-1][0] - C[0][0]) * 100 if len(C) > 2 else float('nan')
    k = M[:, 0] > t0 + 5; Q = M[k]
    j = np.clip(np.searchsorted(REF[:, 0], Q[:, 0]) - 1, 0, len(REF) - 1); R = REF[j]
    dp = np.hypot(Q[:, 2] - R[:, 1], Q[:, 3] - R[:, 2]) * 100; dy = np.degrees(np.abs((Q[:, 4] - R[:, 3] + np.pi) % (2 * np.pi) - np.pi))
    print('%s | %d | %.3f · %.3f · %.3f | %d · %d | %.3f · %.3f | %.0f | %.1f · %.1f · %.2f' % (
        Path(f).stem, len(M), np.median(g), np.percentile(g, 99), g.max(), (g > 0.4).sum(), (g > 0.5).sum(), mar.min(), np.median(mar), cpu, np.median(dp), dp.max(), dy.max()))
