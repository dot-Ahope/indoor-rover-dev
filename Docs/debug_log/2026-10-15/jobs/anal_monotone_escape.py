#!/usr/bin/env python3
"""anal_monotone_escape — '여유가 줄지 않는 곧은 이동'으로 멈춘 자세에서 빠져나갈 수 있는지, 기록된 실패 순간의 로컬 코스트맵으로 시뮬레이션. (2026-10-15 §25, 오늘만)
  제안(사용자 방향: 카메라 회피는 유지, 가끔 나는 '상자 옆 교착'을 일반적으로 해결): Nav2 가 '후보 전부 충돌'로 서면 우리 복구가 곧게 앞 · 뒤로 천천히 움직이되,
        차체 다각형(패딩 포함) ↔ 모든 치명 칸 사이 정확한 거리가 한 걸음도 줄지 않을 때만 → 어떤 물체에도 지금보다 가까워지지 않음.
  판정(계산 전 선언, SUMMARY §25): 실패 5 건 중 4 건 이상에서, 0.30 m 안에 '거리가 줄지 않은 채 최근접 ≥ 5 cm' 인 자리에 닿는 방향(앞 또는 뒤)이 있으면 구현으로.
  방법: 그 순간 로컬 코스트맵(odom) 치명 칸 중심을 고정 장애물로, 로버를 지금 방향 그대로 1 cm 씩 ±0.30 m 이동. 각 걸음 최근접 거리(차체 다각형 → 칸 중심, 안이면 0).
        '줄지 않음' 은 0.2 mm 허용(부동소수). 목표 여유 5 cm(09-23 칸 검사 막힘 4.4 cm + 여유).
  인자: 이름=bag@HH:MM:SS.f ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
XF, XR, HW = 0.272, -0.258, 0.175; TARGET = 0.05; TOL = 0.0002
def clear(x, y, th, wx, wy):
    c, s = math.cos(th), math.sin(th); bx = c * (wx - x) + s * (wy - y); by = -s * (wx - x) + c * (wy - y)
    inside = (bx >= XR) & (bx <= XF) & (np.abs(by) <= HW)
    d = np.hypot(np.maximum(np.maximum(XR - bx, bx - XF), 0), np.maximum(np.abs(by) - HW, 0)); d = np.where(inside, 0, d); k = int(np.argmin(d))
    return d[k], ('앞' if bx[k] > 0 else '뒤') + ('왼' if by[k] > 0 else '오')
print('사례                    시작 최근접   앞으로: 결과                                   뒤로: 결과')
ok_cases = 0
for spec in sys.argv[1:]:
    nm, rest = spec.split('='); bag, hh = rest.split('@'); hms, _, fr = hh.partition('.'); ob = None; lc = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        T = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
            ts = t / 1e9
            if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
            if ts > T: break
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            else: lc = m
    a = np.array(lc.data, np.int16).reshape(lc.info.height, lc.info.width); iy, ix = np.nonzero(a >= 100)
    wx = lc.info.origin.position.x + (ix + 0.5) * lc.info.resolution; wy = lc.info.origin.position.y + (iy + 0.5) * lc.info.resolution
    d0, side0 = clear(*ob, wx, wy); res = {}
    for sign, lab in ((1, '앞'), (-1, '뒤')):
        prev = d0; out = None
        for k in range(1, 31):
            s = sign * k * 0.01; d, side = clear(ob[0] + s * math.cos(ob[2]), ob[1] + s * math.sin(ob[2]), ob[2], wx, wy)
            if d < prev - TOL: out = '%.2f m 에서 거리 줄어 멈춤(%.1f → %.1f cm, %s)' % (abs(s), 100 * prev, 100 * d, side); break
            prev = d
            if d >= TARGET: out = '★ %.2f m 에서 최근접 %.1f cm 도달(줄지 않음)' % (abs(s), 100 * d); break
        if out is None: out = '0.30 m 끝까지 줄지 않음, 최근접 %.1f cm(5 cm 미달)' % (100 * prev)
        res[lab] = out
    found = any('★' in v for v in res.values()); ok_cases += found
    print('%-22s %4.1f cm(%s)   %-46s %s' % (nm, 100 * d0, side0, res['앞'], res['뒤']))
print('빠져나갈 방향이 있는 사례 %d / %d' % (ok_cases, len(sys.argv) - 1))
