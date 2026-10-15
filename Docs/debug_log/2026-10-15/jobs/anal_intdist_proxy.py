#!/usr/bin/env python3
"""anal_intdist_proxy — nvblox 최대 통합 거리 1.4 → 1.0 의 효과를 기록 bag 으로 어림(실주행 대체, 배터리 부족). (2026-10-15 §30.1, 오늘만)
  한계: bag 에 깊이 영상이 없어 nvblox 를 1.0 으로 다시 돌릴 수 없음 → '그 칸이 처음 치명이 된 순간 카메라 거리'만 본다.
       1.0 m 보다 멀리서 처음 생긴 칸은 1.0 설정이면 그 순간엔 안 생김(나중에 가까이서 볼 때 생기는지는 알 수 없음).
  칸: 지도 좌표에 고정(2.5 cm 반올림)한 로컬 코스트맵 치명 칸 중 상자 구역(x 1.0~1.45, y −0.30~+0.20)만.
      과장 칸 = 기록 상자(x 1.151~1.261, y −0.20~−0.02) 바깥으로 칸 중심이 2.5 cm 넘게 떨어진 칸, 상자 칸 = 칸 중심이 상자 안 또는 2.5 cm 안.
  카메라 자세 = map→odom ∘ odom→base_link ∘ base_link→camera_link(tf_static). 거리 = 카메라 ↔ 칸 중심 수평 거리, 방위 = 카메라 앞축 기준.
  출력: 칸 종류별 처음 찍힌 거리 분포(≤ 1.0 · 1.0~1.4 · > 1.4), 방위 범위, 그리고 과장 칸 중 '처음 찍힌 뒤 1.0 m 안 · 시야 ±40° 에서 다시 보였는데도 남은' 비율.
  인자: 이름=bag ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

BOX = (1.151, 1.261, -0.20, -0.02); REG = (1.0, 1.45, -0.30, 0.20)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
compose = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])


def box_dist(x, y):
    return math.hypot(max(BOX[0] - x, 0, x - BOX[1]), max(BOX[2] - y, 0, y - BOX[3]))


ALL = {}
for arg in sys.argv[1:]:
    nm, bag = arg.split('=')
    mo = ob = cam = None; first = {}; seen_after = {}; present = {}
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo = v
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob = v
                    elif tr.header.frame_id == 'base_link' and tr.child_frame_id == 'camera_link': cam = v
                continue
            if mo is None or ob is None or cam is None: continue
            C = compose(compose(mo, ob), cam)
            a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100); r = m.info.resolution
            ox_, oy_ = m.info.origin.position.x + (ix + 0.5) * r, m.info.origin.position.y + (iy + 0.5) * r
            gx = mo[0] + math.cos(mo[2]) * ox_ - math.sin(mo[2]) * oy_; gy = mo[1] + math.sin(mo[2]) * ox_ + math.cos(mo[2]) * oy_
            k = (gx > REG[0]) & (gx < REG[1]) & (gy > REG[2]) & (gy < REG[3])
            now = set()
            for x, y in zip(gx[k], gy[k]):
                key = (round(x / 0.025) * 0.025, round(y / 0.025) * 0.025); now.add(key)
                if key not in first:
                    d = math.hypot(x - C[0], y - C[1]); b = math.degrees(math.atan2(math.sin(math.atan2(y - C[1], x - C[0]) - C[2]), math.cos(math.atan2(y - C[1], x - C[0]) - C[2])))
                    first[key] = (t / 1e9, d, b)
            # 처음 찍힌 뒤: 1.0 m 안 · 시야 ±40° 에서 다시 보인 프레임 수와 그때 치명이었던 수
            for key in first:
                d = math.hypot(key[0] - C[0], key[1] - C[1]); b = math.atan2(key[1] - C[1], key[0] - C[0]) - C[2]; b = abs(math.degrees(math.atan2(math.sin(b), math.cos(b))))
                if 0.45 <= d <= 1.0 and b <= 40:
                    s = seen_after.setdefault(key, [0, 0]); s[0] += 1; s[1] += key in now
    rows = []
    for key, (ts, d, b) in first.items():
        bd = box_dist(*key); kind = '과장' if bd > 0.025 else '상자'
        s = seen_after.get(key, [0, 0]); rows.append((kind, d, b, bd, s[0], s[1], key))
    ALL[nm] = rows
    print('\n== %s · 상자 구역 칸 %d' % (nm, len(rows)))
    for kind in ('상자', '과장'):
        R = [q for q in rows if q[0] == kind]
        if not R: print('  %s 칸 0' % kind); continue
        D = np.array([q[1] for q in R]); B = np.array([q[2] for q in R])
        print('  %s 칸 %d: 처음 찍힌 거리 ≤ 1.0 m %d · 1.0~1.4 %d · > 1.4 %d (중앙 %.2f m), 방위 %+.0f~%+.0f°'
              % (kind, len(R), (D <= 1.0).sum(), ((D > 1.0) & (D <= 1.4)).sum(), (D > 1.4).sum(), np.median(D), B.min(), B.max()))
        if kind == '과장':
            V = [q for q in R if q[4] > 0]
            if V:
                frac = np.array([q[5] / q[4] for q in V])
                print('    과장 칸 중 처음 찍힌 뒤 1.0 m 안 · 시야 ±40° 에서 다시 보인 칸 %d: 그때 치명으로 남아 있던 비율 중앙 %.0f %% (칸별 %s)'
                      % (len(V), 100 * np.median(frac), ' '.join('%.0f' % (100 * f) for f in frac)))
            far = [q for q in R if q[1] > 1.0]
            print('    1.0 m 넘어서 처음 생긴 과장 칸 %d 개의 기록 상자 거리: %s cm' % (len(far), ' '.join('%.1f' % (100 * q[3]) for q in sorted(far, key=lambda q: -q[3]))))
