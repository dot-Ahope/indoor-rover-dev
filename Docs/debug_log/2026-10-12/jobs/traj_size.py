# 10-12 §7.3: /trajectories(MPPI 궤적 발행) 메시지의 크기·주기 추이 — 10 s 칸마다 메시지 수, 직렬화 크기(kB), 마커 수. 인자: bag...
import sys, time, collections, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
ts = get_typestore(Stores.ROS2_HUMBLE)
for bag in sys.argv[1:]:
    H = collections.defaultdict(list); t0 = None; first = None
    with AnyReader([Path(bag)], default_typestore=ts) as r:
        con = [c for c in r.connections if c.topic == '/trajectories']
        for c, t_ns, raw in r.messages(connections=con):
            t = t_ns * 1e-9; t0 = t0 or t; H[int((t - t0) // 10)].append(len(raw))
            if first is None: m = r.deserialize(raw, c.msgtype); first = (len(m.markers), collections.Counter(x.ns for x in m.markers))
    allb = [x for v in H.values() for x in v]
    print('== %s  메시지 %d · 첫 메시지 마커 %s' % (Path(bag).name, len(allb), first))
    if not allb: continue
    print('   크기 kB 중앙 %.0f 최소 %.0f 최대 %.0f → 평균 %.2f MB/s' % (np.median(allb) / 1e3, min(allb) / 1e3, max(allb) / 1e3, sum(allb) / 1e6 / (10 * len(H))))
    print('   10 s 칸: ' + ' '.join('%s %.1fHz/%.0fkB' % (time.strftime('%M:%S', time.localtime(t0 + 10 * b)), len(H[b]) / 10, np.median(H[b]) / 1e3) for b in sorted(H)))
