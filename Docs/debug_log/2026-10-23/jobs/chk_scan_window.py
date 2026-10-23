#!/usr/bin/env python3
"""chk_scan_window — 정지 구간 앞뒤로 라이다 앞쪽(±60°) 가장 가까운 점 · 방위를 1 s 마다, 로버 자세와 함께(2026-10-23 §6.2, PC).
  왜: 사용자 — "경로 정렬 가중치를 올려서 이유없는 정지가 있었다고 보는가?" f2pa2 5.5 s 정지 때 앞에 무엇(사람 등)이 나타났다 사라졌는지 확인.
  라이다 프레임은 로버 뒤를 향해 장착(yaw ≈ π) — 각도는 base_link 기준으로 바꿔 씀(tf_static lidar_link).
  인자: bag 시작s 끝s"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
SC, LY = [], 0.0
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/scan', '/tf_static')]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms:
                if tr.child_frame_id == 'lidar_link': LY = yq(tr.transform.rotation)
            continue
        tt = t * 1e-9 - T0
        if TA <= tt <= TB:
            a = m.angle_min + np.arange(len(m.ranges)) * m.angle_increment + LY; r = np.array(m.ranges); a = np.arctan2(np.sin(a), np.cos(a))
            k = np.isfinite(r) & (r > 0.15) & (np.abs(a) < math.radians(60)); SC.append((tt, r[k], a[k]))
print('bag %s · 라이다 yaw %.1f° · 앞 ±60° 가장 가까운 점(1 s 마다)' % (Path(bag).name, math.degrees(LY)))
nxt = TA
for tt, r, a in SC:
    if tt < nxt or not len(r): continue
    i = int(np.argmin(r)); n05 = int(np.sum(r < 1.2))
    print('  t %6.1f · 최소 %.2f m @ %+4.0f° · 1.2 m 안 점 %d' % (tt, r[i], math.degrees(a[i]), n05)); nxt = tt + 1.0
