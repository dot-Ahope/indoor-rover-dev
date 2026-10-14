#!/usr/bin/env python3
"""anal_path_endyaw — 계획기 경로(/plan)와 컨트롤러가 받은 경로(/transformed_global_plan)의 끝 방향을 시간순으로 견준다. (2026-10-14, 오늘만)
  왜: 10-07 f2c1 목표 4(남서 구석) 정체가 오늘 서쪽 통로와 같은 BT 결함(스무딩 실패 → TruncatePath 가 끝 방향 0°)이었는지 확인.
  출력: 4 s 간격으로 두 끝 방향(지도 좌표로 맞춤)·그 차이·로버 방향·로버와 목표 거리.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS [날짜 YYYY-MM-DD]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, h0, h1 = sys.argv[1:4]; day = (sys.argv[4] if len(sys.argv) > 4 else '2026-10-14') + ' '
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); A, B = ep(h0), ep(h1)
pl = []; tp = []; ob = []; mo = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/plan', '/transformed_global_plan', '/tf')]):
        ts = t / 1e9
        if ts < A - 5 or ts > B: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (ts, tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append(v)
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append(v)
        elif m.poses:
            q = m.poses[-1].pose; (pl if c.topic == '/plan' else tp).append((ts, q.position.x, q.position.y, yq(q.orientation)))
last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
print('시각       계획기 끝 방향   컨트롤러 끝 방향(지도로)   차이     로버 방향   로버→목표')
for t in np.arange(A, B, 4.0):
    p = last(pl, t); q = last(tp, t); o = last(ob, t); m = last(mo, t)
    cyaw = q[3] + m[3]; ryaw = o[3] + m[3]; c, s = math.cos(m[3]), math.sin(m[3]); rx = m[1] + c * o[1] - s * o[2]; ry = m[2] + s * o[1] + c * o[2]
    print('%s   %+6.1f°          %+6.1f°                %+6.1f°   %+6.1f°     %.2f m' % (time.strftime('%H:%M:%S', time.localtime(t)), math.degrees(p[3]), math.degrees(cyaw), math.degrees(wrap(cyaw - p[3])), math.degrees(ryaw), math.hypot(p[1] - rx, p[2] - ry)))
