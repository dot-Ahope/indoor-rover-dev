# 통로 창(16:11:45~16:13:35)에 받은 경로 메시지 목록: 토픽 · 점 수 · 점 간격 중앙(출처 판별) · 시작 · 끝
import sys, time, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = Path(sys.argv[1]); t0s, t1s = sys.argv[2], sys.argv[3]
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    cs = [c for c in rd.connections if c.topic in ('/plan', '/plan_smoothed', '/received_global_plan', '/transformed_global_plan')]
    print('토픽', sorted({c.topic for c in cs}))
    for c, t, raw in rd.messages(connections=[c for c in cs if c.topic in ('/plan', '/plan_smoothed')]):
        hm = time.strftime('%H:%M:%S', time.localtime(t * 1e-9))
        if not (t0s <= hm <= t1s): continue
        m = rd.deserialize(raw, c.msgtype)
        if len(m.poses) < 2: print(hm, c.topic, '점', len(m.poses)); continue
        P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]); d = np.hypot(*np.diff(P, axis=0).T)
        print('%s.%02d %-15s 점 %4d 간격 %.3f 길이 %.2f  (%.2f,%.2f)->(%.2f,%.2f)' % (hm, int(t*1e-7)%100, c.topic, len(P), np.median(d), d.sum(), *P[0], *P[-1]))
