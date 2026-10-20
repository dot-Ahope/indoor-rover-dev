#!/usr/bin/env python3
"""fig_box_static — B 시험(10-20 §2) 그림: 구성별 깊이 영상 한 장(160×120) + 마지막 nvblox 조각의 상자 근처 칸. 인자: 출력.png 이름=bag ..."""
import sys, math, bisect
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BOX = (1.151, 1.261, -0.20, -0.02); yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
out = sys.argv[1]; runs = [a.split('=') for a in sys.argv[2:]]
fig, ax = plt.subplots(2, len(runs), figsize=(6 * len(runs), 9))
for i, (nm, bag) in enumerate(runs):
    MO = []; img = None; sl = None
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/camera/camera/depth/image_rect_raw', '/nvblox_node/static_map_slice')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))))
            elif c.topic.endswith('image_rect_raw'): img = np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width).copy()
            else: sl = m
    a = ax[0, i]; im = a.imshow(np.where(img > 0, img / 1000.0, np.nan), cmap='viridis', vmin=0.3, vmax=3.0); a.set_title('%s 깊이(마지막 장, 검정 = 값 없음) 유효 %.0f %%' % (nm, 100 * (img > 0).mean())); a.set_facecolor('black'); a.axis('off')
    fig.colorbar(im, ax=a, fraction=0.035, label='m')
    MO.sort(key=lambda q: q[0]); st = sl.header.stamp.sec + sl.header.stamp.nanosec * 1e-9; mo = MO[max(bisect.bisect_right([q[0] for q in MO], st) - 1, 0)][1]
    d = np.array(sl.data, np.float32).reshape(sl.height, sl.width); r = sl.resolution; iy, ix = np.nonzero(d != sl.unknown_value)
    lx = sl.origin.x + (ix + 0.5) * r; ly = sl.origin.y + (iy + 0.5) * r; gx = mo[0] + math.cos(mo[2]) * lx - math.sin(mo[2]) * ly; gy = mo[1] + math.sin(mo[2]) * lx + math.cos(mo[2]) * ly; dv = d[iy, ix]
    a = ax[1, i]; z = (gx > 0.2) & (gx < 1.8) & (gy > -0.8) & (gy < 0.8)
    a.scatter(gx[z & (dv > 0)], gy[z & (dv > 0)], s=18, marker='s', c='#d9e7f0', lw=0, label='관측된 빈 칸')
    a.scatter(gx[z & (dv <= 0)], gy[z & (dv <= 0)], s=18, marker='s', c='#d62728', lw=0, label='표면 안 칸')
    a.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fill=False, ec='#1f4fa8', lw=2, label='실제 상자'))
    a.set_xlim(0.2, 1.8); a.set_ylim(-0.8, 0.8); a.set_aspect('equal'); a.grid(alpha=0.3); a.set_title('%s nvblox 조각(지도, 마지막)' % nm); a.legend(fontsize=8, loc='upper left')
fig.tight_layout(); fig.savefig(out, dpi=100); print('그림', out)
