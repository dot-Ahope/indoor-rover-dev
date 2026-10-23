#!/usr/bin/env python3
"""chk_ctrl_gap — 컨트롤러 출력 토픽(/trajectories · /transformed_global_plan)이 정지 구간에 실제로 나왔나: 수신 간격 · header 시각(2026-10-23 §7, PC).
  왜: §7 첫 표에서 정지 5 s 동안 최적 궤적 값이 소수 셋째 자리까지 그대로 — 새로 계산되지 않은 것인지 확인.
  인자: bag 시작s 끝s"""
import sys
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
R = {}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/trajectories', '/transformed_global_plan', '/cmd_vel', '/local_costmap/costmap', '/plan')]):
        tt = t * 1e-9 - T0
        if TA <= tt <= TB:
            m = rd.deserialize(raw, c.msgtype)
            h = m.markers[0].header if c.topic == '/trajectories' and m.markers else getattr(m, 'header', None)
            R.setdefault(c.topic, []).append((tt, (h.stamp.sec + h.stamp.nanosec * 1e-9 - T0) if h else np.nan))
for k, v in R.items():
    a = np.array(v); g = np.diff(a[:, 0]); i = int(np.argmax(g)) if len(g) else 0
    print('%-28s %4d 개 · 최대 수신 간격 %.2f s (t %.2f → %.2f) · header 시각 최대 간격 %.2f s' % (k, len(a), g.max() if len(g) else 0, a[i, 0], a[i + 1, 0] if len(a) > 1 else 0, np.nanmax(np.diff(a[:, 1])) if len(a) > 1 else 0))
