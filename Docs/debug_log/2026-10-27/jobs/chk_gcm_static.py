#!/usr/bin/env python3
"""chk_gcm_static — §15 틀어진 전역 프레임에서 새로 생긴 치명 칸이 SLAM 정적 지도(/map) 점유 칸인가 (2026-10-27, PC).
  인자: bag폴더 틀어진프레임시각…(HH:MM:SS.ff 직후 첫 전역 메시지)"""
import sys, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = Path(sys.argv[1])
def ts_of(s):
    h, m, r = s.split(':'); return time.mktime(time.strptime('2026-10-27 %s:%s:00' % (h, m), '%Y-%m-%d %H:%M:%S')) + float(r)
WANT = [ts_of(s) for s in sys.argv[2:]]
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
GM, MP = [], []
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/map')]):
        ts = t * 1e-9
        if ts < min(WANT) - 40 or ts > max(WANT) + 4: continue
        m = rd.deserialize(raw, c.msgtype); i = m.info
        (GM if c.topic == '/global_costmap/costmap' else MP).append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
for w in WANT:
    k = next(j for j, x in enumerate(GM) if x[0] >= w); ts, G, ox, oy, r = GM[k]; Pv = GM[k - 1][1]
    mp = [x for x in MP if x[0] <= ts][-1]; _, M, mx, my, mr = mp
    def sval(msk):
        J, I = np.nonzero(msk); X, Y = ox + (I + .5) * r, oy + (J + .5) * r
        ii = ((X - mx) / mr).astype(int); jj = ((Y - my) / mr).astype(int); ok = (ii >= 0) & (jj >= 0) & (ii < M.shape[1]) & (jj < M.shape[0])
        v = np.full(len(X), -2); v[ok] = M[jj[ok], ii[ok]]; return v
    add = (G == 100) & (Pv != 100); keep = (G == 100) & (Pv == 100); rem = (G != 100) & (Pv == 100)
    va, vk, vr = sval(add), sval(keep), sval(rem)
    f = lambda v: '/map 점유(100) %d · 비움(0) %d · 미지(-1) %d · 밖 %d' % ((v == 100).sum(), (v == 0).sum(), (v == -1).sum(), (v == -2).sum())
    print('%s(직전 %s, /map %s): 새로 생긴 치명 %d → %s' % (hs(ts), hs(GM[k - 1][0]), hs(mp[0]), add.sum(), f(va)))
    print('   직전과 같은 치명 %d → %s' % (keep.sum(), f(vk)))
    print('   사라진 치명 %d → %s' % (rem.sum(), f(vr)))
