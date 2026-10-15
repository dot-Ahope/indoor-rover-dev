#!/usr/bin/env python3
"""anal_replan_trace — 한 구간 동안 (1) 계획기 경로(/plan)가 나올 때마다 처음 0.6 m 방향과 상자 구역에 가장 가까이 가는 거리, (2) 상자 구역의 카메라만 치명 칸 수(로컬),
  (3) 로버 지도 자세를 시간순으로 함께. (2026-10-15 §19, 오늘만)
  왜: 사용자 관찰 "복귀 시 상자 쪽으로 경로를 만들었다가, 카메라로 인식 후 경로를 수정해 돌아온 것 같다" — 경로가 상자 쪽이었다가 칸이 생긴 뒤 바뀌었는지.
  상자 구역(지도): 사용자 실측 기준 상자 앞면 x ≈ −1.43, 북쪽 끝 y ≈ −3.90 → 구역 x −1.50~−1.35, y −4.40~−3.80.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
bag, h0, h1 = sys.argv[1:4]; BX = (-1.50, -1.35, -4.40, -3.80)
ob = mo = None; ev = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/plan', '/local_costmap/costmap')]):
        m = rd.deserialize(raw, c.msgtype); ts = t / 1e9; h = time.strftime('%H:%M:%S', time.localtime(ts)) + '.%d' % (int(ts * 10) % 10)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
            continue
        if not (h0 <= h[:8] <= h1) or ob is None or mo is None: continue
        rx = mo[0] + math.cos(mo[2]) * ob[0] - math.sin(mo[2]) * ob[1]; ry = mo[1] + math.sin(mo[2]) * ob[0] + math.cos(mo[2]) * ob[1]; ryaw = math.degrees(ob[2] + mo[2])
        if c.topic == '/plan':
            P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]); acc = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
            k = min(int(np.searchsorted(acc, 0.6)), len(P) - 1); d06 = math.degrees(math.atan2(P[k, 1] - P[0, 1], P[k, 0] - P[0, 0]))
            dx = np.maximum(np.maximum(BX[0] - P[:, 0], P[:, 0] - BX[1]), 0); dy = np.maximum(np.maximum(BX[2] - P[:, 1], P[:, 1] - BX[3]), 0); dmin = np.hypot(dx, dy).min()
            ymin = P[:, 1].min()
            ev.append((ts, '%s 경로   시작 (%.2f, %.2f) · 0.6 m 앞 방향 %+4.0f° · 상자 구역까지 최소 %.2f m · 경로 최남단 y %.2f · 길이 %.2f m' % (h, P[0, 0], P[0, 1], d06, dmin, ymin, acc[-1])))
        else:
            a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
            wx = m.info.origin.position.x + (ix + 0.5) * m.info.resolution; wy = m.info.origin.position.y + (iy + 0.5) * m.info.resolution
            mx = mo[0] + math.cos(mo[2]) * wx - math.sin(mo[2]) * wy; my = mo[1] + math.sin(mo[2]) * wx + math.cos(mo[2]) * wy
            n = int(((mx > BX[0]) & (mx < BX[1] - 0.04) & (my > BX[2]) & (my < BX[3])).sum())   # x < −1.39: 종이백(라이다 −1.37) 앞, 상자 쪽 칸만
            ev.append((ts, '%s 지도   상자 앞 칸(x −1.50~−1.39) %2d · 로버 (%.2f, %.2f, %+4.0f°)' % (h, n, rx, ry, ryaw)))
last = None
for ts, s in sorted(ev):
    if s.split(' ', 1)[1].startswith('지도') and last is not None and ts - last < 1.0: continue
    if s.split(' ', 1)[1].startswith('지도'): last = ts
    print(s)
