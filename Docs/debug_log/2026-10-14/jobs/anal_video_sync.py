#!/usr/bin/env python3
"""anal_video_sync — 휴대폰 영상(촬영 시각 정보 없음)을 bag 시각에 맞춘다. (2026-10-14, 오늘만)
  방법: 영상은 5 fps 회색 축소 프레임의 '앞 프레임과의 차이'(움직임 크기), bag 은 로버의 실제 속도(|v|/0.08 + |ω|/0.38, /odometry/filtered).
        둘을 표준화해 지정한 bag 구간 안에서 0.2 s 간격으로 밀어 가며 상관이 가장 큰 시작 시각을 찾는다. 1 등과 2 등(5 s 넘게 떨어진 것)의 상관을 함께 내 확신도를 본다.
  한계: 손으로 든 촬영이면 카메라 흔들림도 '움직임'으로 잡힌다. 결과는 장면 비교로 눈으로 다시 확인해야 한다.
  인자: 영상 bag 탐색시작HH:MM:SS 탐색끝HH:MM:SS"""
import sys, time, math, subprocess
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
vid, bag, h0, h1 = sys.argv[1:5]; FPS = 5; W, H = 54, 96
raw = subprocess.run(['C:/ffmpeg/bin/ffmpeg', '-loglevel', 'error', '-i', vid, '-vf', 'fps=%d,scale=%d:%d,format=gray' % (FPS, W, H), '-f', 'rawvideo', '-'], capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
mv = np.r_[0, np.abs(np.diff(F, axis=0)).mean(axis=(1, 2))]
# 손떨림(전체 밝기 이동)을 줄이려고 중앙값 대비 큰 변화만 남기고 1 s 이동 평균
k = np.ones(FPS) / FPS; sv = np.convolve(mv, k, mode='same'); dur = len(F) / FPS
sp = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw2 in rd.messages(connections=[c for c in rd.connections if c.topic == '/odometry/filtered']):
        m = rd.deserialize(raw2, c.msgtype); sp.append((t / 1e9, abs(m.twist.twist.linear.x) / 0.08 + abs(m.twist.twist.angular.z) / 0.38))
sp = np.array(sp); day = time.strftime('%Y-%m-%d ', time.localtime(sp[0, 0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S'))
A, B = ep(h0), ep(h1); grid = np.arange(sp[0, 0], sp[-1, 0], 1.0 / FPS); bs = np.convolve(np.interp(grid, sp[:, 0], sp[:, 1]), k, mode='same')
z = lambda x: (x - x.mean()) / (x.std() + 1e-9); zv = z(sv); res = []
for s in np.arange(max(A, grid[0]), B - dur, 0.2):
    i = int((s - grid[0]) * FPS); seg = bs[i:i + len(zv)]
    if len(seg) < len(zv): break
    res.append((s, float(np.dot(zv, z(seg)) / len(zv))))
R = np.array(res); o = np.argsort(-R[:, 1]); best = R[o[0]]; second = next((R[j] for j in o if abs(R[j, 0] - best[0]) > 5), None)
# 첫 움직임: 영상 움직임이 처음 중앙값 + 3 × MAD 를 넘는 시각, bag 은 속도가 처음 0.3 을 넘는 시각(구간 안)
mad = np.median(np.abs(sv - np.median(sv))); fv = next((i / FPS for i, x in enumerate(sv) if x > np.median(sv) + 3 * mad), float('nan'))
fb = next((t for t, x in sp if A <= t <= B and x > 0.3), float('nan'))
print('  영상 첫 큰 움직임 %.1f s · bag 구간 첫 움직임 %s' % (fv, time.strftime('%H:%M:%S', time.localtime(fb)) if fb == fb else '-'))
print('%s: 길이 %.1f s → 영상 0 s = bag %s.%d (상관 %.2f) · 2 등 %s (상관 %.2f)' % (Path(vid).name, dur, time.strftime('%H:%M:%S', time.localtime(best[0])), int(best[0] % 1 * 10), best[1],
      time.strftime('%H:%M:%S', time.localtime(second[0])) if second is not None else '-', second[1] if second is not None else float('nan')))
