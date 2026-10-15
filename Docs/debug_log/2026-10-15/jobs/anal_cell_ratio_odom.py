#!/usr/bin/env python3
"""anal_cell_ratio_odom — §7 재검: 칸을 odom 격자에 고정해, 시야 안 프레임마다 로컬 코스트맵 치명 여부와 nvblox 조각 점유 여부를 함께 셈. (2026-10-15 §12, 오늘만)
  왜: §7 은 칸을 '지도 좌표 3 cm 안' 으로 맞춰 셌는데, 그동안 map→odom 이 바뀌어(회전 0.2° · 이동 약 2 cm) 같은 odom 칸이 지도에서 2~3 cm 움직였다 → 이웃 칸과 번갈아 잡혀 '깜빡임' 이 분석에서 생겼을 수 있음.
        조각과 코스트맵은 odom 에서 원점 위상이 같다(anal_grid_phase) → odom 칸 번호 floor(x/0.05) 로 바로 맞출 수 있다.
  시야 안 = 카메라 |방위| ≤ 43° · 거리 ≤ 1.4 m(가림은 안 봄 — 상자 옆 띠는 앞에 가리는 것이 없음).
  인자: bag 시작HH:MM:SS 끝HH:MM:SS 지도좌표 칸 목록 'x,y;x,y;...'"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
bag, h0, h1, cells = sys.argv[1:5]; MC = [tuple(float(v) for v in s.split(',')) for s in cells.split(';')]
ob = mo = cam = None; sl = None; keys = None; st = {}
# 1 차: 끝 시각(기준 순간)의 map→odom — 지도 좌표 칸을 그 순간 odom 칸에 고정하려고(bag 맨 앞 값은 수 cm~15 cm 다름)
MO_END = None
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/tf']):
        if time.strftime('%H:%M:%S', time.localtime(t / 1e9)) > h1: break
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': MO_END = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/nvblox_node/static_map_slice', '/local_costmap/costmap')]):
        m = rd.deserialize(raw, c.msgtype); ts = t / 1e9; h = time.strftime('%H:%M:%S', time.localtime(ts))
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                elif tr.child_frame_id == 'camera_link' and tr.header.frame_id == 'base_link': cam = v
            continue
        if c.topic == '/nvblox_node/static_map_slice': sl = m; continue
        if h > h1 or ob is None or mo is None or cam is None or sl is None: continue
        if keys is None:   # 지도 좌표 칸을 기준 순간의 map→odom 으로 odom 칸 번호에 한 번만 고정
            keys = []
            for x, y in MC:
                c_, s_ = math.cos(MO_END[2]), math.sin(MO_END[2]); dx, dy = x - MO_END[0], y - MO_END[1]; xo = c_ * dx + s_ * dy; yo = -s_ * dx + c_ * dy
                keys.append(((x, y), (int(math.floor(xo / 0.05)), int(math.floor(yo / 0.05)))))
        if h < h0: continue
        C = (ob[0] + math.cos(ob[2]) * cam[0] - math.sin(ob[2]) * cam[1], ob[1] + math.sin(ob[2]) * cam[0] + math.cos(ob[2]) * cam[1], ob[2] + cam[2])
        a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); d = np.array(sl.data, np.float32).reshape(sl.height, sl.width)
        for (mc, (kx, ky)) in keys:
            cx, cy = (kx + 0.5) * 0.05, (ky + 0.5) * 0.05; R = math.hypot(cx - C[0], cy - C[1]); b = math.degrees(math.atan2(cy - C[1], cx - C[0]) - C[2]); b = (b + 180) % 360 - 180
            if abs(b) > 43 or R > 1.4: continue
            jx = int(round((cx - m.info.origin.position.x) / 0.05 - 0.5)); jy = int(round((cy - m.info.origin.position.y) / 0.05 - 0.5))
            sx = int(round((cx - sl.origin.x) / sl.resolution - 0.5)); sy = int(round((cy - sl.origin.y) / sl.resolution - 0.5))
            lv = a[jy, jx] >= 100 if 0 <= jx < m.info.width and 0 <= jy < m.info.height else None
            sv = (d[sy, sx] <= 0 and d[sy, sx] != sl.unknown_value) if 0 <= sx < sl.width and 0 <= sy < sl.height else None
            e = st.setdefault(mc, [0, 0, 0]); e[0] += 1; e[1] += int(bool(lv)); e[2] += int(bool(sv))
print('칸(지도, 기준 순간 map→odom 으로 odom 칸에 고정)   시야 안 코스트맵 프레임   코스트맵 치명   조각 점유')
for mc, (n, l, s) in st.items(): print('(%+.3f, %+.3f)                               %3d                %3d (%3.0f %%)   %3d (%3.0f %%)' % (mc[0], mc[1], n, l, 100 * l / n, s, 100 * s / n))
