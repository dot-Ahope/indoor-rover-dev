#!/usr/bin/env python3
"""anal_ahead_cells — 로컬 코스트맵 프레임마다 차체 둘레(앞으로 늘린 직사각형) 안 치명 칸 수와 위치를 차체 좌표로. (2026-10-15 §3, 오늘만)
  왜: f2v1 정지 순간 발행된 코스트맵 한 장에는 차체에 닿는 치명 칸이 없었는데 '후보 전부 충돌'. 그 전후 프레임에 잠깐 찍힌 칸이 있었는지.
  영역: 차체 좌표 x −0.30 ~ +0.60(지평 끝 ≈ +0.26 m 앞 + 차체 앞 0.27), |y| ≤ 0.20(차체 반폭 0.175 + 2.5 cm).
  인자: bag 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
bag, h0, h1 = sys.argv[1:4]; ob = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
        h = time.strftime('%H:%M:%S', time.localtime(t / 1e9)); m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            continue
        if not (h0 <= h <= h1) or ob is None: continue
        a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
        wx = m.info.origin.position.x + (ix + 0.5) * m.info.resolution; wy = m.info.origin.position.y + (iy + 0.5) * m.info.resolution
        c_, s_ = math.cos(ob[2]), math.sin(ob[2]); bx = c_ * (wx - ob[0]) + s_ * (wy - ob[1]); by = -s_ * (wx - ob[0]) + c_ * (wy - ob[1])
        k = (bx > -0.30) & (bx < 0.60) & (np.abs(by) <= 0.20)
        pts = ' '.join('(%+.2f,%+.2f)' % (x, y) for x, y in sorted(zip(bx[k], by[k]))[:8])
        print('%s.%d 영역 안 치명 칸 %2d  %s' % (h, int(t / 1e8) % 10, k.sum(), pts))
