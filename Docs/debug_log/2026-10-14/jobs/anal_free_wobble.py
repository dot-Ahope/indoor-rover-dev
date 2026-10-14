#!/usr/bin/env python3
"""anal_free_wobble — 로버 둘레가 완전히 빈 칸(비용 0)일 때만 골라 좌우 틀기(|ω|>0.05 부호 바뀜)를 센다. (2026-10-14 §23, 오늘만)
  왜: MPPI CostCritic 은 궤적 점의 중심 칸 비용이 1 미만이면 건너뛴다(humble 소스). 둘레 R 안이 전부 0 인 곳에서도 토글 뒤(B) 흔들림이 늘었다면
      원인은 CostCritic(차체·비용 관련 상태)이 아니라 다른 곳(경로·목표 크리틱, 최적화기 상태)이다.
  분류: 각 /cmd_vel 시각에 직전 로컬 코스트맵에서 로버 중심 반경 R(기본 0.6 m — 지평 32 × 0.1 s × 0.08 m/s ≈ 0.26 m + 차체 반 대각 0.31 m) 안 최대 비용 = 0 이면 '빈 곳'.
  인자: R 이름=bag@HH:MM:SS~HH:MM:SS ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
R = float(sys.argv[1])
print('구간     빈 곳 시간   빈 곳 좌우 틀기 /분   빈 곳 아닌 곳 시간   그곳 좌우 틀기 /분')
for a in sys.argv[2:]:
    nm, rest = a.split('='); bag, rng = rest.split('@'); h0, h1 = rng.split('~'); ob = (0, 0); lc = None; S = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap', '/cmd_vel')]):
            h = time.strftime('%H:%M:%S', time.localtime(t / 1e9)); m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = (tr.transform.translation.x, tr.transform.translation.y)
            elif c.topic == '/local_costmap/costmap':
                g = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.indices(g.shape)
                lc = (m.info.origin.position.x + (ix + 0.5) * m.info.resolution, m.info.origin.position.y + (iy + 0.5) * m.info.resolution, g)
            elif h0 <= h <= h1 and lc is not None:
                d = np.hypot(lc[0] - ob[0], lc[1] - ob[1]) <= R; S.append((t / 1e9, m.angular.z, int(lc[2][d].max()) == 0))
    S = np.array(S); dt = np.median(np.diff(S[:, 0]))
    def flips(mask):
        out = 0; prev = 0
        for w, f in zip(S[:, 1], mask):
            if not f: prev = 0; continue   # 구간이 끊기면 부호 이력도 끊음
            s = 0 if abs(w) <= 0.05 else (1 if w > 0 else -1)
            if s: 
                if prev and s != prev: out += 1
                prev = s
        return out
    fr = S[:, 2] > 0; tf = fr.sum() * dt; tn = (~fr).sum() * dt
    print('%-6s   %5.0f s      %6.1f               %5.0f s           %6.1f' % (nm, tf, flips(fr) / max(tf, 1e-9) * 60, tn, flips(~fr) / max(tn, 1e-9) * 60))
