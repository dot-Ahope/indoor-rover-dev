#!/usr/bin/env python3
"""anal_cmd_timeline — 한 구간의 0.5 s 칸마다 로버 자세 · 명령 · 명령 끊김 · 지도 여유. (2026-10-15 §32, 오늘만)
  왜: 사용자 "남서쪽 작은 통로를 이동할 때, 박스쪽으로 몸을 틀다가 빠져나왔는데, 이건 연산 비용이 컸나?" — 몸을 튼 시각과
      제어 주기 놓침(= /cmd_vel 간격이 0.1 s 보다 길어짐) · 재계획 이벤트가 겹치는지.
  열: 시각 | 로버 지도 (x, y, yaw) | yaw 변화(°/0.5 s) | 명령 v · ω 평균 | 명령 수 · 최대 간격(ms) | 지도 여유(cm, 패딩 포함 ↔ 치명 칸 중심) · 그 칸 몸체 위치
  인자: bag 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

XF, XR, HW = 0.272, -0.258, 0.175
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
compose = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])
bag, h0, h1 = sys.argv[1:4]
mo = ob = None; P = []; CMD = []; CL = []; T0 = T1 = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/cmd_vel', '/local_costmap/costmap')]):
        ts = t / 1e9
        if T0 is None:
            day = time.strftime('%Y-%m-%d ', time.localtime(ts)); T0 = time.mktime(time.strptime(day + h0, '%Y-%m-%d %H:%M:%S')); T1 = time.mktime(time.strptime(day + h1, '%Y-%m-%d %H:%M:%S'))
        if ts > T1 + 1: break
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo = v
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob = v
                    if mo is not None and ts >= T0 - 1: P.append((ts, *compose(mo, ob)))
        elif ts < T0 - 1: continue
        elif c.topic == '/cmd_vel': CMD.append((ts, m.linear.x, m.angular.z))
        elif ob is not None:
            a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100); r = m.info.resolution
            wx = m.info.origin.position.x + (ix + 0.5) * r; wy = m.info.origin.position.y + (iy + 0.5) * r
            cc, ss = math.cos(ob[2]), math.sin(ob[2]); dx, dy = wx - ob[0], wy - ob[1]; bx = cc * dx + ss * dy; by = -ss * dx + cc * dy
            d = np.hypot(np.maximum(np.maximum(XR - bx, bx - XF), 0), np.maximum(np.abs(by) - HW, 0)); k = int(np.argmin(d))
            CL.append((ts, float(d[k]), float(bx[k]), float(by[k])))
P = np.array(P); CMD = np.array(CMD); hms = lambda s: time.strftime('%H:%M:%S', time.localtime(s)) + '.%d' % (int(s * 10) % 10)
print('구간 %s ~ %s · /cmd_vel %d · 전체 간격 중앙 %.0f ms · > 150 ms 간격 %d' % (h0, h1, len(CMD), 1000 * np.median(np.diff(CMD[:, 0])), int((np.diff(CMD[:, 0]) > 0.15).sum())))
print('  시각       | 로버 지도 (x, y, yaw)        | Δyaw/0.5s | v · ω 평균        | 명령 수 · 최대 간격 | 지도 여유 · 칸 몸체')
prev_yaw = None
for s in np.arange(T0, T1, 0.5):
    kp = (P[:, 0] >= s) & (P[:, 0] < s + 0.5)
    if not kp.any(): continue
    x, y, yw = P[kp][-1, 1:4]; dyaw = 0 if prev_yaw is None else math.degrees(math.atan2(math.sin(yw - prev_yaw), math.cos(yw - prev_yaw))); prev_yaw = yw
    kc = (CMD[:, 0] >= s) & (CMD[:, 0] < s + 0.5); cm = CMD[kc]
    gap = np.diff(np.concatenate([CMD[CMD[:, 0] < s][-1:, 0], cm[:, 0]])).max() * 1000 if len(cm) else float('nan')
    cl = [q for q in CL if s <= q[0] < s + 0.5]
    cls = '%5.1f (%+.2f, %+.2f)' % (100 * cl[-1][1], cl[-1][2], cl[-1][3]) if cl else '      -'
    print('  %s | (%+.3f, %+.3f, %+6.1f°) | %+6.1f | %+.3f · %+.3f | %2d · %4.0f ms | %s'
          % (hms(s), x, y, math.degrees(yw), dyaw, cm[:, 1].mean() if len(cm) else float('nan'), cm[:, 2].mean() if len(cm) else float('nan'), len(cm), gap, cls))
