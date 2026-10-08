# 10-08 §1: bag_box1 의 nvblox 슬라이스로 상자 ② 자리 장애물 칸 수(2 s 마다) — PC 에서 rosbags 로 읽음(Jetson 무응답).
#   nvblox_msgs/DistanceMapSlice 정의는 PC 에 없어 직접 등록(Isaac ROS 3.x: header·resolution·width·height·origin·unknown_value·data) — data 길이 = width×height 로 검증.
import math, sys, time, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts = get_typestore(Stores.ROS2_HUMBLE)
ts.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo = ob = None; last = 0; bad = 0
with AnyReader([Path(sys.argv[1])], default_typestore=ts) as r:
    con = [c for c in r.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice')]
    for c, t_ns, raw in r.messages(connections=con):
        t = t_ns * 1e-9; m = r.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for x in m.transforms:
                k = (x.header.frame_id, x.child_frame_id); v = (x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
                if k == ('map', 'odom'): mo = v
                elif k == ('odom', 'base_link'): ob = v
            continue
        if len(m.data) != m.width * m.height: bad += 1; continue
        if t - last < 2 or mo is None or ob is None: continue
        last = t; d = np.asarray(m.data, np.float32).reshape(m.height, m.width); res = m.resolution
        c_, s_ = math.cos(mo[2]), math.sin(mo[2]); n = tot = unk = 0; dmin = 9
        for X in np.arange(1.075, 1.35, 0.05):
            for Y in np.arange(-0.275, 0.10, 0.05):
                dx, dy = X - mo[0], Y - mo[1]; qx, qy = c_ * dx + s_ * dy, -s_ * dx + c_ * dy
                i, j = int((qx - m.origin.x) / res), int((qy - m.origin.y) / res)
                if 0 <= i < m.width and 0 <= j < m.height:
                    tot += 1; v = d[j, i]
                    if v == m.unknown_value: unk += 1
                    else: n += int(v <= 0.05); dmin = min(dmin, v)
        rx, ry = mo[0] + c_ * ob[0] - s_ * ob[1], mo[1] + s_ * ob[0] + c_ * ob[1]
        print('%s 로버 map (%.2f, %.2f) | 상자 ② 자리 nvblox 장애물 %2d · 미지 %2d / %d · 최소 거리 %.2f m' % (time.strftime('%H:%M:%S', time.localtime(t)), rx, ry, n, unk, tot, dmin))
print('길이 불일치 메시지', bad)
