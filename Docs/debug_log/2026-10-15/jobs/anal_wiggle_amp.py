#!/usr/bin/env python3
"""anal_wiggle_amp — 좌우 틀기의 '크기': 명령 각속도 부호 바뀜을 문턱 0.05 · 0.10 · 0.20 rad/s 로 각각 세고, 명령 ω 와 실제 차체 각속도(EKF)의 흔들림 크기(RMS, 1 s 이동평균을 뺀 고주파 성분). (2026-10-15 §16, 오늘만)
  왜: 사용자 육안 — f2v2 넓은 통로에서 멈칫 · 좌우 틀기가 보이지 않았고 어제보다 빨랐다. 내 지표(|ω| > 0.05 부호 바뀜)가 눈에 안 보이는 작은 흔들림까지 센 것인지.
  출력(구간별): 평균 명령 v, 멈칫 /분, 부호 바뀜 /분(문턱 3 개), 명령 ω 고주파 RMS(rad/s), 실제 차체 각속도 고주파 RMS(rad/s), 실제 차체 방향 고주파 흔들림 RMS(°).
  인자: 이름=bag@HH:MM:SS~HH:MM:SS ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
def hp(t, x, win=1.0):
    g = np.arange(t[0], t[-1], 0.05); y = np.interp(g, t, x); k = max(1, int(win / 0.05)); m = np.convolve(y, np.ones(k) / k, mode='same'); return y - m
print('구간                 평균v   멈칫/분  부호바뀜/분(0.05·0.10·0.20)   명령ω 흔들림   실제ω 흔들림   방향 흔들림')
for spec in sys.argv[1:]:
    nm, rest = spec.split('='); bag, rng = rest.split('@'); h0, h1 = rng.split('~'); cm = []; od = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/cmd_vel', '/odometry/filtered')]):
            h = time.strftime('%H:%M:%S', time.localtime(t / 1e9))
            if not (h0 <= h <= h1): continue
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/cmd_vel': cm.append((t / 1e9, m.linear.x, m.angular.z))
            else:
                q = m.pose.pose.orientation; od.append((t / 1e9, m.twist.twist.angular.z, math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))))
    C = np.array(cm); O = np.array(od); T = (C[-1, 0] - C[0, 0]) / 60
    cruise = False; dips = 0
    for x in C[:, 1]:
        if x >= 0.06: cruise = True
        elif x < 0.03 and cruise: dips += 1; cruise = False
    def flips(th):
        s = np.sign(np.where(np.abs(C[:, 2]) > th, C[:, 2], 0)); s = s[s != 0]; return int((s[1:] != s[:-1]).sum()) / T
    yaw = np.unwrap(O[:, 2])
    print('%-20s %.3f   %5.1f    %6.1f · %5.1f · %5.1f              %.3f          %.3f          %.2f' % (nm, C[:, 1].mean(), dips / T, flips(0.05), flips(0.10), flips(0.20),
          np.sqrt(np.mean(hp(C[:, 0], C[:, 2]) ** 2)), np.sqrt(np.mean(hp(O[:, 0], O[:, 1]) ** 2)), math.degrees(np.sqrt(np.mean(hp(O[:, 0], yaw, 2.0) ** 2)))))
