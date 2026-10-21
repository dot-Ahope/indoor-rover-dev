#!/usr/bin/env python3
"""anal_topic_gaps — bag 안 토픽별 수신 시각(기록 시각) 기준 평균 Hz · 0.5 s 넘는 끊김 수 · 최대 간격. (2026-10-21 §7, PC)
  인자: bag 토픽...   bag 기록 시각이므로 기록기 몫 지연도 포함된다(10-20 §9.6 기준 2 의 '≤ 2' 는 그 몫 감안)."""
import sys
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, tops = sys.argv[1], sys.argv[2:]
T = {t: [] for t in tops}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in T]):
        T[c.topic].append(t * 1e-9)
for tp, ts in T.items():
    ts = np.array(sorted(ts))
    if len(ts) < 2: print('%-34s 메시지 %d' % (tp, len(ts))); continue
    d = np.diff(ts)
    print('%-34s %6d 개 · %.1f Hz · 0.5 s 넘는 끊김 %d · 최대 간격 %.2f s @ t=%.1f' % (tp, len(ts), (len(ts) - 1) / (ts[-1] - ts[0]), (d > 0.5).sum(), d.max(), ts[d.argmax()] - ts[0]))
