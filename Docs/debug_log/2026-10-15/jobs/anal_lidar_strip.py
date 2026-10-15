#!/usr/bin/env python3
"""anal_lidar_strip — 지도 좌표의 좁은 띠(x 범위 · y 범위) 안에 라이다 점이 언제 · 몇 개 · 라이다에서 어느 방위 · 거리로 찍혔는지 시간순. (2026-10-15 §12, 오늘만)
  왜: §12 후보 3 계산에서 '실물 없는 과장 칸'이라 했던 바깥 줄(x ≈ −1.47~−1.48)이 구간 중 라이다 확인 칸으로 나옴. §5 의 '그 순간 라이다 점 0' 과 맞추려면 언제 보였는지 필요.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS x0,x1,y0,y1"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
tm = lambda x, y, P: (P[0] + np.cos(P[2]) * x - np.sin(P[2]) * y, P[1] + np.sin(P[2]) * x + np.cos(P[2]) * y)
bag, h0, h1, box = sys.argv[1:5]; X0, X1, Y0, Y1 = [float(v) for v in box.split(',')]
ob = mo = lid = None; last = 0
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/scan')]):
        m = rd.deserialize(raw, c.msgtype); ts = t / 1e9
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                elif tr.child_frame_id == 'lidar_link':
                    q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
            continue
        h = time.strftime('%H:%M:%S', time.localtime(ts))
        if not (h0 <= h <= h1) or ob is None or lid is None or mo is None: continue
        r = np.array(m.ranges); an = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < m.range_max)
        px, py = r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
        mx, my = tm(*tm(bx, by, ob), mo)
        k = (mx >= X0) & (mx <= X1) & (my >= Y0) & (my <= Y1)
        if k.any() and ts - last >= 0.5:
            last = ts; L = tm(np.array(lid[0]), np.array(lid[1]), ob); L = tm(L[0], L[1], mo); yaw = ob[2] + mo[2] + math.atan2(lid[2][1, 0], lid[2][0, 0])
            rngs = np.hypot(mx[k] - L[0], my[k] - L[1]); brg = np.degrees((np.arctan2(my[k] - L[1], mx[k] - L[0]) - (ob[2] + mo[2]) + np.pi) % (2 * np.pi) - np.pi)
            print('%s.%d 점 %2d · x %.3f~%.3f · y %.3f~%.3f · 로버 기준 방위 %+.0f~%+.0f° · 거리 %.2f~%.2f m · 로버 지도 (%.2f, %.2f)' % (
                h, int(ts * 10) % 10, k.sum(), mx[k].min(), mx[k].max(), my[k].min(), my[k].max(), brg.min(), brg.max(), rngs.min(), rngs.max(), *[float(v) for v in tm(np.array(ob[0]), np.array(ob[1]), mo)]))
