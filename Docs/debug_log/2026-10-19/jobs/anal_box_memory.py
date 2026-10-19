#!/usr/bin/env python3
"""anal_box_memory — 복귀 길 상자 옆 통과 때 지도의 상자 칸은 언제 · 어디서 본 기억인가, 그 기억이 통과 순간까지 얼마나 밀렸나. (2026-10-19 §11)
  왜: §10 원시 점 — 출발 때(0.8~1.1 m 정면)는 면이 맞음(+1.7 · +0.2 cm), 복귀 때 상자는 남동쪽(1.2~1.8 m, 방위 +37°)에서만 보이고
      옆을 지날 땐 시야 밖. 그 사이 map→odom 이 (−8, +15 cm, −3.2°)까지 변함 → (c) 오도메트리 쪽 의심.
  계산:
   1) 관측 오차: 남동쪽 관측 프레임(anal_box_points 의 상자 점, t 150~170 s)에서 동쪽 면 = x 상위 2 %, 남쪽 면 = y 하위 2 % → 기록(1.261, −0.20) 대비.
      이 값은 '그 순간 지도 자세(map→odom ∘ odom→base)'가 맞다면 0 이어야 함 → 그 순간 자세 오차(또는 외부 보정) 크기.
   2) 기억 밀림: nvblox 는 odom 좌표로 기억. 관측 순간 odom 의 상자 = mo(t_obs)⁻¹ · 상자(지도). 통과 순간 그 odom 점을 지도로 = mo(t_pass) · (그것).
      SLAM 이 맞다고 볼 때, 통과 순간 기억된 상자가 실제보다 밀린 양 = mo(t_pass) · mo(t_obs)⁻¹ · 상자 − 상자.
  인자: bag points_csv"""
import sys, math, bisect, csv
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

bag, pcsv = sys.argv[1:3]
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
MO = []; POSE = []; t0 = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/camera/camera/depth/image_rect_raw')]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic != '/tf':
            if t0 is None: t0 = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            continue
        for tr in m.transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, v))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': POSE.append((st, v))
MO.sort(); POSE.sort(); MOt = [q[0] for q in MO]; Pt = [q[0] for q in POSE]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
mul = lambda A, p: (A[0] + math.cos(A[2]) * p[0] - math.sin(A[2]) * p[1], A[1] + math.sin(A[2]) * p[0] + math.cos(A[2]) * p[1])
inv = lambda A, p: (math.cos(A[2]) * (p[0] - A[0]) + math.sin(A[2]) * (p[1] - A[1]), -math.sin(A[2]) * (p[0] - A[0]) + math.cos(A[2]) * (p[1] - A[1]))

# 1) 남동쪽 관측 프레임 다시 읽기(상자 점 필요) — anal_box_points 와 같은 변환으로 동쪽 · 남쪽 면
R = [r for r in csv.DictReader(open(pcsv, encoding='utf-8')) if 150 <= float(r['t']) <= 170]
print('복귀 남동쪽 관측 프레임 %d (t %.1f~%.1f s), map→odom 첫 (%+.3f, %+.3f, %+.2f°) → 끝 (%+.3f, %+.3f, %+.2f°)'
      % (len(R), float(R[0]['t']), float(R[-1]['t']), float(R[0]['mo_x']), float(R[0]['mo_y']), float(R[0]['mo_yaw']), float(R[-1]['mo_x']), float(R[-1]['mo_y']), float(R[-1]['mo_yaw'])))
print('  서쪽 면 과장 중앙(이 관측에선 서쪽 면이 뒤쪽이라 참고만): %+.1f cm' % np.nanmedian([float(r['west_off']) for r in R]))

# 2) 통과 순간: 로버가 상자 북쪽 옆(지도 x 1.0~1.6, y > 0.05)에 있는 시각
pass_t = [st for st, v in POSE if 1.0 <= mul(at(MO, MOt, st), v[:2])[0] <= 1.6 and mul(at(MO, MOt, st), v[:2])[1] > 0.05 and st - t0 > 100]
tp = pass_t[len(pass_t) // 2]; mp = at(MO, MOt, tp)
print('통과 순간 t %.1f s, map→odom (%+.3f, %+.3f, %+.2f°)' % (tp - t0, mp[0], mp[1], math.degrees(mp[2])))
corners = {'북서': (1.151, -0.02), '북동': (1.261, -0.02), '남동': (1.261, -0.20), '중심': (1.206, -0.11)}
for lab, tobs in (('출발 관측(t 5 s)', t0 + 5), ('남동쪽 관측 첫(t %.0f s)' % float(R[0]['t']), t0 + float(R[0]['t'])), ('남동쪽 관측 끝(t %.0f s)' % float(R[-1]['t']), t0 + float(R[-1]['t']))):
    mo = at(MO, MOt, tobs); out = []
    for k, p in corners.items():
        q = mul(mp, inv(mo, p)); out.append('%s Δ(%+.1f, %+.1f)' % (k, 100 * (q[0] - p[0]), 100 * (q[1] - p[1])))
    print('  %s 에 본 상자가 통과 순간 기억에서 밀린 양(cm, +y = 북 = 로버 쪽): %s' % (lab, ' · '.join(out)))
