# 10-12 §2: 토픽·TF 끊김 찾기 — bag 기록 시각(수신) 간격과 메시지 stamp 간격. 인자: bag [최소 간격 s=0.5]
import sys, time, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
ts = get_typestore(Stores.ROS2_HUMBLE); TH = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
rec = {}; tfp = {}
with AnyReader([Path(sys.argv[1])], default_typestore=ts) as r:
    con = [c for c in r.connections if c.topic in ('/wheel_odom', '/odometry/filtered', '/odometry/ekf_a', '/odom_rf2o', '/scan', '/cmd_vel', '/tf', '/imu/data', '/local_costmap/costmap', '/plan')]
    for c, t_ns, raw in r.messages(connections=con):
        t = t_ns * 1e-9
        if c.topic == '/tf':
            m = r.deserialize(raw, c.msgtype)
            for x in m.transforms:
                k = 'tf %s→%s' % (x.header.frame_id, x.child_frame_id)
                if k in ('tf odom→base_link', 'tf map→odom'): tfp.setdefault(k, []).append((t, x.header.stamp.sec + x.header.stamp.nanosec * 1e-9))
        else: rec.setdefault(c.topic, []).append(t)
f = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + ('%.1f' % (t % 1))[1:]
for k, v in sorted(rec.items()):
    v = np.array(v); d = np.diff(v); g = np.nonzero(d > max(TH, 5 * np.median(d)))[0]
    print('%-24s n %6d 중앙 간격 %.3f s | 끊김 %d: %s' % (k, len(v), np.median(d), len(g), ' '.join('%s(%.1f s)' % (f(v[i]), d[i]) for i in g[:12])))
for k, v in tfp.items():
    v = np.array(v); d = np.diff(v[:, 0]); g = np.nonzero(d > TH)[0]; ds = np.diff(v[:, 1]); gs = np.nonzero(ds > TH)[0]
    print('%-24s n %6d 수신 끊김 %d: %s' % (k, len(v), len(g), ' '.join('%s(%.1f s)' % (f(v[i, 0]), d[i]) for i in g[:12])))
    print('%-24s          stamp 끊김 %d: %s | 수신−stamp 지연 중앙 %.3f 최대 %.3f s' % ('', len(gs), ' '.join('%s(%.1f s)' % (f(v[i, 0]), ds[i]) for i in gs[:12]), np.median(v[:, 0] - v[:, 1]), (v[:, 0] - v[:, 1]).max()))
