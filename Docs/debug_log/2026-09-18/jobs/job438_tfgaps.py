#!/usr/bin/env python3
"""TF 발행 공백·시각 어긋남 점검 (2026-09-18, 간헐 중단 원인). 인자: BAG GOAL_EPOCH T_END [EVENT_T ...] 반복은 '--' 로 구분
  map->odom(slam_toolbox), odom->base_link(EKF) 각각: 수신 간격 최대·0.2 s 넘는 공백 목록, (헤더 stamp − 수신 시각) 범위.
  EVENT_T 가 있으면 그 전후 ±1.5 s 의 두 TF 최신 stamp 추이를 0.1 s 간격으로 — 'extrapolation into the future' 는
  요청 시각(보통 odom->base 최신 stamp)이 map->odom 최신 stamp 보다 뒤일 때 난다.
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage


def run(bag, G, tend, events):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    S = {'mo': [], 'ob': []}
    while r.has_next():
        topic, data, ts = r.read_next()
        if topic != '/tf':
            continue
        rt = ts * 1e-9 - G
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                S['mo'].append((rt, st))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                S['ob'].append((rt, st))
    name = bag.split('_')[-1]
    for k, lab in (('mo', 'map->odom(SLAM)'), ('ob', 'odom->base(EKF)')):
        A = np.array(sorted(S[k])); A = A[(A[:, 0] >= 0) & (A[:, 0] <= tend)]
        g = np.diff(A[:, 0]); lag = A[:, 1] - A[:, 0]
        big = [(A[i, 0], g[i]) for i in np.where(g > 0.2)[0]]
        # stamp 기준 공백(수신은 이어져도 stamp 가 안 늘면 공백)
        sm = np.maximum.accumulate(A[:, 1]); sg = np.diff(sm)
        sbig = [(A[i + 1, 0], sg[i]) for i in np.where(sg > 0.2)[0]]
        print('  %-5s %-16s %5d 개 | 수신 간격 최대 %.3f s, >0.2 s %d 회 %s | stamp−수신 %+.3f~%+.3f s | stamp 증가 공백 >0.2 s %d 회 %s' % (
            name, lab, len(A), g.max() if len(g) else 0, len(big), ' '.join('@%.1f(%.2f)' % b for b in big[:4]), lag.min(), lag.max(),
            len(sbig), ' '.join('@%.1f(%.2f)' % b for b in sbig[:4])))
    for ev in events:
        print('  -- %s 사건 t=%.2f 전후: 수신 시각별 최신 stamp (map->odom / odom->base) 와 차' % (name, ev))
        mo = sorted(S['mo']); ob = sorted(S['ob'])
        mrt = [m[0] for m in mo]; ort = [o[0] for o in ob]
        for t in np.arange(ev - 1.5, ev + 1.51, 0.1):
            i = bisect.bisect_right(mrt, t) - 1; j = bisect.bisect_right(ort, t) - 1
            ms = max(m[1] for m in mo[max(0, i - 3):i + 1]) if i >= 0 else float('nan')
            os_ = max(o[1] for o in ob[max(0, j - 3):j + 1]) if j >= 0 else float('nan')
            print('     t %6.2f | map->odom 최신 stamp %7.3f | odom->base 최신 stamp %7.3f | 차(map−odom) %+.3f%s' % (t, ms, os_, ms - os_, '  ← odom 이 앞섬' if ms < os_ else ''))


args = sys.argv[1:]
groups, cur = [], []
for a in args:
    if a == '--':
        groups.append(cur); cur = []
    else:
        cur.append(a)
if cur:
    groups.append(cur)
for g in groups:
    run(g[0], float(g[1]), float(g[2]), [float(x) for x in g[3:]])
