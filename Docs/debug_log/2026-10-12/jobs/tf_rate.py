# 10-12 §3.3: bag 의 /tf 발행량 추이 — 10 s 칸마다 프레임 쌍별 변환 수(Hz)와 /tf 메시지 수. 인자: bag
import sys, time, collections
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
ts = get_typestore(Stores.ROS2_HUMBLE); H = collections.defaultdict(collections.Counter); t0 = None
with AnyReader([Path(sys.argv[1])], default_typestore=ts) as r:
    pubs = collections.Counter()
    for c in r.connections:
        if c.topic == '/tf': pubs[c.msgcount] += 1
    print('/tf 연결(발행자별 기록) 수:', sum(pubs.values()), '메시지 수', sorted(pubs.elements(), reverse=True)[:8])
    for c, t_ns, raw in r.messages(connections=[c for c in r.connections if c.topic == '/tf']):
        t = t_ns * 1e-9; t0 = t0 or t; b = int((t - t0) // 10); H[b]['msg'] += 1
        for x in r.deserialize(raw, c.msgtype).transforms: H[b]['%s→%s' % (x.header.frame_id, x.child_frame_id)] += 1
keys = [k for k, _ in sum((collections.Counter(h) for h in H.values()), collections.Counter()).most_common(8)]
print('시각     ' + ' '.join('%18s' % k[:18] for k in keys) + '   (10 s 평균 Hz)')
for b in sorted(H): print(time.strftime('%H:%M:%S', time.localtime(t0 + 10 * b)) + ' ' + ' '.join('%18.1f' % (H[b][k] / 10) for k in keys))
