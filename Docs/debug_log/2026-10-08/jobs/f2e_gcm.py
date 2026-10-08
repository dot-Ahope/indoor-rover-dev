# 10-08 §3.3: 복귀 구간 전역 코스트맵(계획기)과 로컬 코스트맵에 상자 ② 가 들어갔나 — x 0.9~1.6 · y −0.4~0.4 단면
import sys, time, numpy as np, math
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
ts = get_typestore(Stores.ROS2_HUMBLE); K = lambda t: time.strftime('%H:%M:%S', time.localtime(t)); want = ['13:35:55', '13:36:05', '13:36:15', '13:36:25']
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo = None; done = set()
with AnyReader([Path(sys.argv[1])], default_typestore=ts) as r:
    con = [c for c in r.connections if c.topic in ('/global_costmap/costmap', '/local_costmap/costmap', '/tf')]
    for c, t_ns, raw in r.messages(connections=con):
        t = t_ns * 1e-9; k = K(t)
        if c.topic == '/tf':
            m = r.deserialize(raw, c.msgtype)
            for x in m.transforms:
                if (x.header.frame_id, x.child_frame_id) == ('map', 'odom'): mo = (x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            continue
        w = next((w for w in want if k >= w and (c.topic, w) not in done), None)
        if w is None or mo is None: continue
        done.add((c.topic, w)); m = r.deserialize(raw, c.msgtype); g = np.asarray(m.data, np.int16).reshape(m.info.height, m.info.width); res = m.info.resolution
        print('%s %s (%s 프레임) — 행 y, 열 x 1.00~1.50 (0.1 간격), 값 0~100(99 내접·100 치명)' % (k, c.topic, m.header.frame_id))
        for y in np.arange(0.3, -0.35, -0.1):
            row = []
            for x in np.arange(1.0, 1.55, 0.1):
                X, Y = x, y
                if m.header.frame_id == 'odom':
                    c_, s_ = math.cos(mo[2]), math.sin(mo[2]); dx, dy = x - mo[0], y - mo[1]; X, Y = c_ * dx + s_ * dy, -s_ * dx + c_ * dy
                i, j = int((X - m.info.origin.position.x) / res), int((Y - m.info.origin.position.y) / res)
                row.append('%4d' % g[j, i] if 0 <= i < g.shape[1] and 0 <= j < g.shape[0] else '   .')
            print('   y %+.1f ' % y + ' '.join(row))
