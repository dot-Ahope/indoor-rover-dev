#!/usr/bin/env python3
"""anal_slice_box — nvblox 거리 지도 조각(실시간 또는 재생)이 출발점 시험 상자를 실제보다 얼마나 크게 찍는지. (2026-10-19 §4)
  왜: 깊이 bag 오프라인 재생으로 nvblox 설정(통합 거리 · 복셀 등)만 바꿔 같은 입력의 과장을 비교(10-15 §29.4 의 로컬 코스트맵 판을 nvblox 조각으로).
  기록 상자(TEST_COURSE §1 · 10-15 §23): 지도 x 1.151~1.261, y −0.20~−0.02. ⚠ 출발 자세 배치 오차 1~2 cm 섞임(모든 설정에 같게 → 설정 간 차이엔 영향 없음).
  입력: 주행 bag(/tf 의 map→odom · odom→base_link) + 조각 bag(그 주행 bag 자체 = 실시간, 또는 replay_<꼬리표>). 조각은 odom 좌표.
  칸: 조각 거리 ≤ 0(표면 안) 이고 unknown 아님. 상자 구역(지도 x 0.95~1.50, y −0.45~+0.25) 안만. 로버가 상자 옆(지도 x 0.9~1.7, |y| < 0.6)에 있을 때의 조각만.
  출력: 조각마다 북쪽(로버 쪽) 면 = 칸 가장자리 최대 y, 서쪽 면, 칸 수 → 중앙값 · 범위, 기록 면 대비 과장(cm). 인자: 주행bag 이름=조각bag ...
  재생 판은 시각이 주행 bag 과 같다(bag play --clock 의 /clock = 원래 시각) — 조각 header.stamp 로 주행 bag 의 tf 를 찾는다."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg

BOX = (1.151, 1.261, -0.20, -0.02); REG = (0.95, 1.50, -0.45, 0.25)
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
compose = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])

drive = sys.argv[1]; MO, OB = [], []
with AnyReader([Path(drive)], default_typestore=TS) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, v))
MO.sort(); OB.sort(); MOt = [m[0] for m in MO]; OBt = [o[0] for o in OB]
at = lambda L, T, t: L[max(bisect.bisect_right(T, t) - 1, 0)][1]

for arg in sys.argv[2:]:
    nm, sb = arg.split('=')
    rows = []
    with AnyReader([Path(sb)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/nvblox_node/static_map_slice']):
            m = rd.deserialize(raw, c.msgtype); st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            mo = at(MO, MOt, st); P = compose(mo, at(OB, OBt, st))
            if m.header.frame_id == 'map': mo = (0.0, 0.0, 0.0)   # 10-19 §12: nvblox global_frame=map 재생 — 조각이 이미 지도 좌표
            if not (0.9 <= P[0] <= 1.7 and abs(P[1]) < 0.6): continue
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            lx = m.origin.x + (ix + 0.5) * r; ly = m.origin.y + (iy + 0.5) * r
            gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly
            k = (gx > REG[0]) & (gx < REG[1]) & (gy > REG[2]) & (gy < REG[3]) & (gy > -0.25)   # 남동쪽 창문틀 · 드론 덩어리(y < −0.3) 제외
            if k.sum() == 0: rows.append((st, np.nan, np.nan, 0)); continue
            rows.append((st, gy[k].max() + r / 2, gx[k].min() - r / 2, int(k.sum())))
    R = np.array([q[1:] for q in rows], float); ok = ~np.isnan(R[:, 0])
    if not ok.any(): print('%s: 상자 옆 조각에 상자 칸 없음 (조각 %d)' % (nm, len(rows))); continue
    N, W, C = R[ok, 0], R[ok, 1], R[ok, 2]
    print('%-14s 상자 옆 조각 %3d (칸 있음 %3d) · 북쪽 면 과장 중앙 %+5.1f cm (범위 %+.1f~%+.1f) · 서쪽 면 과장 중앙 %+5.1f cm · 칸 수 중앙 %d'
          % (nm, len(rows), ok.sum(), 100 * (np.median(N) - BOX[3]), 100 * (N.min() - BOX[3]), 100 * (N.max() - BOX[3]), 100 * (BOX[0] - np.median(W)), int(np.median(C))))
