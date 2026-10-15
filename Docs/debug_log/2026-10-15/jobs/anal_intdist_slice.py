#!/usr/bin/env python3
"""anal_intdist_slice — nvblox 거리 지도 조각(/nvblox_node/static_map_slice)에서 상자 구역 칸이 '표면(거리 ≤ 0)이 되는 순간'의 카메라 거리. (2026-10-15 §30.1, 오늘만)
  왜: anal_intdist_proxy.py 는 로컬 코스트맵(로버 따라 움직이는 3 m 창)이라 '처음 찍힘'이 '창에 들어옴'과 섞임(1.4 m 넘는 값이 나옴 — 한도 1.4 에선 불가능).
      nvblox 조각은 nvblox 가 가진 지도 그대로라 표면이 생기는 순간 = 통합된 순간(감쇠로 사라졌다 다시 생기면 그것도 한 번으로 셈).
  칸 종류: 지도 좌표 칸 중심이 기록 상자(x 1.151~1.261, y −0.20~−0.02) 안 또는 2.5 cm 안 = 상자, 그 밖(상자 구역 x 1.0~1.45, y −0.25~+0.20) = 과장.
  1.0 설정 근사: 생성 순간 카메라 거리 > 1.0 m 인 생성은 1.0 이면 그 순간 안 일어남. 인자: 이름=bag ..."""
import sys, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg

BOX = (1.151, 1.261, -0.20, -0.02); REG = (1.0, 1.45, -0.25, 0.20)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
compose = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
box_dist = lambda x, y: math.hypot(max(BOX[0] - x, 0, x - BOX[1]), max(BOX[2] - y, 0, y - BOX[3]))

for arg in sys.argv[1:]:
    nm, bag = arg.split('=')
    mo = ob = cam = None; prev = {}; ev = []; sframes = 0
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/nvblox_node/static_map_slice')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo = v
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob = v
                    elif tr.header.frame_id == 'base_link' and tr.child_frame_id == 'camera_link': cam = v
                continue
            if mo is None or ob is None or cam is None: continue
            sframes += 1; C = compose(compose(mo, ob), cam)
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.indices(d.shape)
            lx = m.origin.x + (ix + 0.5) * m.resolution; ly = m.origin.y + (iy + 0.5) * m.resolution   # odom
            gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly
            k = (gx > REG[0]) & (gx < REG[1]) & (gy > REG[2]) & (gy < REG[3])
            occ = k & (d <= 0) & (d != m.unknown_value)
            cur = {}
            for x, y, o in zip(gx[k], gy[k], occ[k]):
                cur[(round(x / 0.025) * 0.025, round(y / 0.025) * 0.025)] = bool(o) or cur.get((round(x / 0.025) * 0.025, round(y / 0.025) * 0.025), False)
            for key, o in cur.items():
                if o and not prev.get(key, False):
                    dist = math.hypot(key[0] - C[0], key[1] - C[1]); b = math.atan2(key[1] - C[1], key[0] - C[0]) - C[2]
                    ev.append((t / 1e9, key, dist, math.degrees(math.atan2(math.sin(b), math.cos(b))), box_dist(*key)))
            prev = cur
    print('\n== %s · 조각 %d · 표면 생성 %d 회' % (nm, sframes, len(ev)))
    for kind, sel in (('상자', lambda e: e[4] <= 0.025), ('과장(상자 밖 2.5~7.5 cm)', lambda e: 0.025 < e[4] <= 0.075), ('과장(상자 밖 7.5 cm 넘음)', lambda e: e[4] > 0.075)):
        E = [e for e in ev if sel(e)]
        if not E: print('  %s 생성 0' % kind); continue
        D = np.array([e[2] for e in E]); B = np.abs([e[3] for e in E])
        print('  %s 생성 %d: 카메라 거리 ≤ 1.0 m %d (%.0f %%) · 1.0~1.4 %d · > 1.4 %d · 중앙 %.2f m · |방위| 중앙 %.0f° · 시야 밖(>45°) %d'
              % (kind, len(E), (D <= 1.0).sum(), 100 * (D <= 1.0).mean(), ((D > 1.0) & (D <= 1.4)).sum(), (D > 1.4).sum(), np.median(D), np.median(B), (B > 45).sum()))
        # 통합으로 생길 수 있는 생성만(시야 |방위| ≤ 45° · 거리 ≤ 1.45 m) — 나머지는 지도 좌표 반올림 · 조각 범위 · ESDF 재계산 탓(§30.1)
        F = (B <= 45) & (D <= 1.45)
        if F.any(): print('    시야 안 · 1.45 m 안 생성 %d: ≤ 1.0 m %d (%.0f %%) · 1.0~1.45 m %d' % (F.sum(), (D[F] <= 1.0).sum(), 100 * (D[F] <= 1.0).mean(), (D[F] > 1.0).sum()))
