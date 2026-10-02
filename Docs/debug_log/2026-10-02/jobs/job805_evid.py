#!/usr/bin/env python3
"""10-02 §5: 지우기 증거 추출 — bag 하나에서 (1) 라이다 스캔(5 Hz)과 그 시각 로버 map 자세 (2) nvblox 슬라이스(1 Hz)와 그 시각 map→odom.
   출력 npz: scans_t, poses(N×3 map base_link), ranges(N×B float16), amin, ainc, rmax / sl(list: dict t, mo, d, o)
   인자: BAG OUT"""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG, OUT = sys.argv[1], sys.argv[2]
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
mo, ob, scans, sls = [], [], [], []; t0 = None; ls = -1; lsl = -1; meta = None
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if t0 is None: t0 = t
    if tp == '/tf':
        for x in deserialize_message(data, get_message(types[tp])).transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): mo.append(v)
            elif k == ('odom', 'base_link'): ob.append(v)
    elif tp == '/scan' and t - ls >= 0.19:
        m = deserialize_message(data, get_message(types[tp])); ls = t
        if meta is None: meta = (m.angle_min, m.angle_increment, m.range_max, len(m.ranges))
        scans.append((t, np.array(m.ranges, dtype=np.float32)))
    elif tp == '/nvblox_node/static_map_slice' and t - lsl >= 0.99:
        m = deserialize_message(data, get_message(types[tp])); lsl = t
        d = np.array(m.data, dtype=np.float32).reshape(m.height, m.width)
        sls.append((t, d.astype(np.float16), np.array([m.origin.x, m.origin.y, m.resolution, getattr(m, 'unknown_value', 1000.0)])))
mo = np.array(mo); ob = np.array(ob)
def at(A, t): i = max(np.searchsorted(A[:, 0], t) - 1, 0); return A[i, 1:]
P, T, RR = [], [], []
for t, rr in scans:
    if not len(mo) or not len(ob) or t < mo[0, 0] or t < ob[0, 0]: continue
    mx, my, mth = at(mo, t); ox, oy, oth = at(ob, t); c, s = math.cos(mth), math.sin(mth)
    P.append((mx + c * ox - s * oy, my + s * ox + c * oy, mth + oth)); T.append(t - t0); RR.append(rr.astype(np.float16))
SL = []
for t, d, o in sls:
    if not len(mo) or t < mo[0, 0]: continue
    SL.append({'t': t - t0, 'mo': at(mo, t), 'd': d, 'o': o})
np.savez_compressed(OUT, t=np.array(T), poses=np.array(P), ranges=np.array(RR), meta=np.array(meta), sl=np.array(SL, dtype=object))
print('%s: 스캔 %d (빔 %d), 슬라이스 %d, 길이 %.0f s' % (BAG.split('/')[-1], len(T), meta[3], len(SL), (scans[-1][0] - t0) if scans else 0), flush=True)
