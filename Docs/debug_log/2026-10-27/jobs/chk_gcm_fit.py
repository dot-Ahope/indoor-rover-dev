#!/usr/bin/env python3
"""chk_gcm_fit — §15 틀어진 전역 프레임의 '새로 생긴 치명 칸' 을 만들 수 있는 slice→map 변환 찾기 (2026-10-27, PC).
  slice(odom) 장애 칸(거리 ≤ 0)을 (yaw, tx, ty) 로 옮겨 새로 생긴 칸과 겹침 최대 → 실제 map→odom · 단위 변환과 비교.
  같은 방법으로 정상 프레임(직전과 같은 치명)도 맞춰 기준 확인. 인자: bag폴더 프레임시각…"""
import sys, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag = Path(sys.argv[1])
def ts_of(s):
    h, m, r = s.split(':'); return time.mktime(time.strptime('2026-10-27 %s:%s:00' % (h, m), '%Y-%m-%d %H:%M:%S')) + float(r)
WANT = [ts_of(s) for s in sys.argv[2:]]
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
GM, SL, mo = [], [], []
with AnyReader([bag], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/nvblox_node/static_map_slice', '/tf')]):
        ts = t * 1e-9
        if ts < min(WANT) - 120 or ts > max(WANT) + 3: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, tr.transform.translation.x, tr.transform.translation.y, math.degrees(yaw(tr.transform.rotation))))
        elif c.topic == '/global_costmap/costmap':
            if ts < min(WANT) - 5: continue
            i = m.info; GM.append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
        else:
            if ts < min(WANT) - 5: continue
            d = np.array(m.data, np.float32).reshape(m.height, m.width); J, I = np.nonzero((d <= 0) & (d != m.unknown_value))
            SL.append((ts, np.c_[m.origin.x + (I + .5) * m.resolution, m.origin.y + (J + .5) * m.resolution]))
key = lambda P: set(map(tuple, np.floor(P / 0.05).astype(int)))
def fit(S, target, yc, xc0, yc0):
    best = (0, 0, 0, 0)
    for yd in np.arange(yc - 12, yc + 12.01, 0.5):
        a = math.radians(yd); R = np.c_[math.cos(a) * S[:, 0] - math.sin(a) * S[:, 1], math.sin(a) * S[:, 0] + math.cos(a) * S[:, 1]]
        for tx in np.arange(xc0 - 0.8, xc0 + 0.81, 0.05):
            for ty in np.arange(yc0 - 0.8, yc0 + 0.81, 0.05):
                n = len(target & key(R + [tx, ty]))
                if n > best[0]: best = (n, yd, tx, ty)
    return best
for w in WANT:
    k = next(j for j, x in enumerate(GM) if x[0] >= w); ts, G, ox, oy, r = GM[k]; Pv = GM[k - 1][1]
    cells = lambda msk: set(map(tuple, np.c_[np.nonzero(msk)[1] + int(round(ox / r)), np.nonzero(msk)[0] + int(round(oy / r))]))
    add = cells((G == 100) & (Pv != 100)); keep = cells((G == 100) & (Pv == 100))
    S = min(SL, key=lambda x: abs(x[0] - ts))[1]
    m = min(mo, key=lambda x: abs(x[0] - ts))
    ba = fit(S, add, m[3], m[1], m[2]); bk = fit(S, keep, m[3], m[1], m[2])
    print('%s 전역 · 슬라이스 장애 %d 칸 · 실제 map→odom (%.3f, %.3f, %.2f°)' % (hs(ts), len(S), m[1], m[2], m[3]))
    print('   새로 생긴 %d 칸 최적: 겹침 %d · yaw %.1f° t (%.2f, %.2f)' % (len(add), ba[0], ba[1], ba[2], ba[3]))
    print('   직전과 같은 칸 최적: 겹침 %d · yaw %.1f° t (%.2f, %.2f)' % (bk[0], bk[1], bk[2], bk[3]))
    # 그 변환과 가까운 과거 map→odom 이 있었나
    near = sorted(mo, key=lambda x: abs(x[3] - ba[1]) + 10 * math.hypot(x[1] - ba[2], x[2] - ba[3]))[:1]
    print('   지난 120 s map→odom 중 가장 비슷한 값: %s (%.3f, %.3f, %.2f°)' % (hs(near[0][0]), near[0][1], near[0][2], near[0][3]))
