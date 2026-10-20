#!/usr/bin/env python3
"""anal_box_static — 정지 상태 짧은 bag 에서 깊이 품질과 nvblox 조각의 시험 상자 · 빈 바닥 표현을 잰다. (2026-10-20 §2, PC)
  깊이: 프레임마다 유효 비율(전체 · 아래 절반), 상자 부피(지도 x 1.10~1.32, y −0.25~+0.03, z 0.02~0.17) 안 점 수 — 그 순간 tf(map→odom→base→광학).
  조각: 마지막 5 s 조각들의 중앙값 — 상자 칸(실제 상자 ± 1 칸 = 지도 x 1.10~1.31, y −0.25~+0.03) 수, 북 · 서 면(anal_slice_box 정의),
        빈 바닥(x 0.40~1.05, |y| < 0.45)의 표면 안 칸(유령) 수 · 미지 칸 비율.
  인자: 이름=bag ..."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
BOX = (1.151, 1.261, -0.20, -0.02); BOXV = (1.10, 1.32, -0.25, 0.03, 0.02, 0.17); BOXC = (1.10, 1.31, -0.25, 0.03); FLOOR = (0.40, 1.05, -0.45, 0.45)


def qm(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def T(tr):
    M = np.eye(4); M[:3, :3] = qm(tr.rotation); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


for arg in sys.argv[1:]:
    nm, bag = arg.split('='); static = {}; MO, OB = [], []; K = None; frames = []; SL = []
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/camera/camera/depth/camera_info', '/camera/camera/depth/image_rect_raw', '/nvblox_node/static_map_slice')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf_static':
                for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T(tr.transform))
            elif c.topic == '/tf':
                for tr in m.transforms:
                    st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, T(tr.transform)))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, T(tr.transform)))
            elif c.topic.endswith('camera_info'):
                if K is None: K = np.array(m.k).reshape(3, 3)
            elif c.topic.endswith('image_rect_raw'):
                frames.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.header.frame_id, np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width).copy()))
            else:
                SL.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m))
    MO.sort(key=lambda q: q[0]); OB.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
    at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
    f = frames[0][1]; Bc = np.eye(4)
    while f != 'base_link':
        p, A = static[f]; Bc = A @ Bc; f = p
    fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]; H, W = frames[0][2].shape; vv, uu = np.mgrid[0:H, 0:W]
    va, vl, nb = [], [], []
    for st, fid, img in frames:
        z = img.astype(np.float32) / 1000.0; ok = z > 0
        va.append(ok.mean()); vl.append(ok[H // 2:].mean())
        P = np.stack([(uu[ok] - cx) / fx * z[ok], (vv[ok] - cy) / fy * z[ok], z[ok], np.ones(ok.sum())]); G = (at(MO, MOt, st) @ at(OB, OBt, st) @ Bc @ P)[:3]
        nb.append(int(((G[0] > BOXV[0]) & (G[0] < BOXV[1]) & (G[1] > BOXV[2]) & (G[1] < BOXV[3]) & (G[2] > BOXV[4]) & (G[2] < BOXV[5])).sum()))
    tl = SL[-1][0]; rows = []
    for st, m in SL:
        if st < tl - 5: continue
        mo = at(MO, MOt, st); mo2 = (mo[0, 3], mo[1, 3], math.atan2(mo[1, 0], mo[0, 0]))
        d = np.array(m.data, np.float32).reshape(m.height, m.width); r = m.resolution
        iy, ix = np.nonzero(np.ones_like(d, bool)); lx = m.origin.x + (ix + 0.5) * r; ly = m.origin.y + (iy + 0.5) * r
        gx = mo2[0] + math.cos(mo2[2]) * lx - math.sin(mo2[2]) * ly; gy = mo2[1] + math.sin(mo2[2]) * lx + math.cos(mo2[2]) * ly; dv = d[iy, ix]
        occ = (dv <= 0) & (dv != m.unknown_value); unk = dv == m.unknown_value
        inb = occ & (gx > BOXC[0]) & (gx < BOXC[1]) & (gy > BOXC[2]) & (gy < BOXC[3])
        fl = (gx > FLOOR[0]) & (gx < FLOOR[1]) & (gy > FLOOR[2]) & (gy < FLOOR[3])
        reg = occ & (gx > 0.95) & (gx < 1.50) & (gy > -0.25) & (gy < 0.25)
        north = 100 * (gy[reg].max() + r / 2 - BOX[3]) if reg.any() else np.nan; west = 100 * (BOX[0] - (gx[reg].min() - r / 2)) if reg.any() else np.nan
        rows.append((int(inb.sum()), north, west, int((occ & fl).sum()), (unk & fl).sum() / max(fl.sum(), 1)))
    R = np.array(rows, float); md = np.nanmedian(R, axis=0)
    print('== %s: 깊이 %d 장 · 유효 전체 %.3f · 아래 절반 %.3f · 상자 부피 점 중앙 %d (범위 %d~%d) | 조각(마지막 5 s, %d 개) 상자 칸 %.0f · 북 %+.1f · 서 %+.1f cm · 빈 바닥 유령 칸 %.0f · 빈 바닥 미지 %.0f %%'
          % (nm, len(frames), np.median(va), np.median(vl), np.median(nb), min(nb), max(nb), len(R), md[0], md[1], md[2], md[3], 100 * md[4]))
