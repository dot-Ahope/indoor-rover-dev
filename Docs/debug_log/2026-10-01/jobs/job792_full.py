#!/usr/bin/env python3
"""10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격).
   각 표본: 로버 map 자세, 그 시각 최신 /plan, /scan 점(map 좌표), nvblox 슬라이스(장애물 셀, 있으면), 전역 코스트맵(0~100).
   출력: /tmp/f2a12_full.npz. 인자: BAG T_START T_END (epoch)"""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
LIDAR_X, LIDAR_YAW = 0.152, math.pi - 0.04677
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
print('토픽:', sorted(types))
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo, ob = [], []; last = {}; S = []; nexts = TA
def mb(t):
    i = max(np.searchsorted([a[0] for a in ob], t) - 1, 0); j = max(np.searchsorted([a[0] for a in mo], t) - 1, 0)
    ox, oy, oth = ob[i][1:]; mx, my, mth = mo[j][1:]; c, s = math.cos(mth), math.sin(mth)
    return mx + c * ox - s * oy, my + s * ox + c * oy, mth + oth
slice_ok = True
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if t > TB + 1: break
    if tp == '/tf':
        for x in deserialize_message(data, get_message(types[tp])).transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): mo.append(v)
            elif k == ('odom', 'base_link'): ob.append(v)
        continue
    if t < TA - 2: continue
    if tp in ('/scan', '/plan', '/global_costmap/costmap', '/local_costmap/costmap'):
        last[tp] = (t, data)
    elif tp.startswith('/nvblox') and slice_ok:
        last[tp] = (t, data)
    if t >= nexts and mo and ob and '/local_costmap/costmap' in last:
        X, Y, TH = mb(t); rec = {'t': t - TA, 'pose': np.array([X, Y, TH])}
        jm = max(np.searchsorted([a[0] for a in mo], t) - 1, 0); rec['mo'] = np.array(mo[jm][1:])   # 10-01 §8.37: 로컬 코스트맵(odom)→map 변환용
        if '/scan' in last:
            m = deserialize_message(last['/scan'][1], get_message(types['/scan'])); rr = np.array(m.ranges); a = m.angle_min + m.angle_increment * np.arange(len(rr)) + LIDAR_YAW
            ok = np.isfinite(rr) & (rr > 0.2) & (rr < 6); lx, ly = LIDAR_X + rr[ok] * np.cos(a[ok]), rr[ok] * np.sin(a[ok])
            c, s = math.cos(TH), math.sin(TH); rec['scan'] = np.c_[X + c * lx - s * ly, Y + s * lx + c * ly].astype(np.float32)
        if '/plan' in last:
            m = deserialize_message(last['/plan'][1], get_message(types['/plan'])); rec['plan'] = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses], dtype=np.float32)
        m = deserialize_message(last['/local_costmap/costmap'][1], get_message(types['/local_costmap/costmap']))
        rec['gcm'] = np.array(m.data, dtype=np.int8).reshape(m.info.height, m.info.width); rec['gcm_o'] = np.array([m.info.origin.position.x, m.info.origin.position.y, m.info.resolution])
        for k in [k for k in last if k.startswith('/nvblox')]:
            try:
                m = deserialize_message(last[k][1], get_message(types[k]))
                if hasattr(m, 'data') and hasattr(m, 'width'):
                    d = np.array(m.data, dtype=np.float32).reshape(m.height, m.width)
                    rec['nv'] = d; rec['nv_o'] = np.array([m.origin.x, m.origin.y, m.resolution, getattr(m, 'unknown_value', 1000.0)])
            except Exception as e:
                print('nvblox 슬라이스 해석 실패:', e); slice_ok = False
        S.append(rec); nexts += 1.0
print('표본 %d 개, nvblox 슬라이스 %s' % (len(S), 'nv' in S[0] if S else None))
np.savez_compressed('/tmp/f2a12_full.npz', recs=np.array(S, dtype=object), allow_pickle=True)
