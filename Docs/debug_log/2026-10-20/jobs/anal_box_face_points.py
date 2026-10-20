#!/usr/bin/env python3
"""anal_box_face_points — 정지 bag 에서 깊이 '점' 자체가 상자 면 밖으로 얼마나 나오나(센서 몫) vs nvblox 칸 면(지도 몫). (2026-10-20 §8, PC)
  상자(기록): 지도 x 1.151~1.261, y −0.20~−0.02. 점 = 깊이 영상 → 그 순간 tf(map→odom→base→광학)로 지도 좌표, 높이 z 0.03~0.17(바닥 · 윗면 위 제외).
  북 면(로버 쪽, y = −0.02): x 1.17~1.24(모서리 제외) 띠 안 점의 y — 프레임마다 최댓값 · 99 % · 95 %, 면보다 +1 / +2.5 cm 넘은 점 비율.
  서 면(정면, x = 1.151): y −0.18~−0.04 띠 안 점의 x — 최솟값 · 1 % · 5 %. 상자 밖 0.15 m 까지 본다(그 너머는 다른 물체). 인자: 이름=bag ..."""
import sys, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
TS = get_typestore(Stores.ROS2_HUMBLE)
FN, FW = -0.02, 1.151


def qm(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def T(tr):
    M = np.eye(4); M[:3, :3] = qm(tr.rotation); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


for arg in sys.argv[1:]:
    nm, bag = arg.split('='); static = {}; MO, OB = [], []; K = None; frames = []
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/camera/camera/depth/camera_info', '/camera/camera/depth/image_rect_raw')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf_static':
                for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T(tr.transform))
            elif c.topic == '/tf':
                for tr in m.transforms:
                    st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, T(tr.transform)))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, T(tr.transform)))
            elif c.topic.endswith('camera_info'):
                if K is None: K = np.array(m.k).reshape(3, 3); WH = (m.width, m.height)
            else:
                frames.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.header.frame_id, np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width).copy()))
    MO.sort(key=lambda q: q[0]); OB.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
    at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
    f = frames[0][1]; Bc = np.eye(4)
    while f != 'base_link':
        p, A = static[f]; Bc = A @ Bc; f = p
    fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]; H, W = frames[0][2].shape; vv, uu = np.mgrid[0:H, 0:W]
    cam = (at(MO, MOt, frames[0][0]) @ at(OB, OBt, frames[0][0]) @ Bc)[:3, 3]
    N, Wf, nN, nW, allN, allW = [], [], [], [], [], []
    for st, fid, img in frames:
        z = img.astype(np.float32) / 1000.0; ok = z > 0
        P = np.stack([(uu[ok] - cx) / fx * z[ok], (vv[ok] - cy) / fy * z[ok], z[ok], np.ones(ok.sum())]); G = (at(MO, MOt, st) @ at(OB, OBt, st) @ Bc @ P)[:3]
        hz = (G[2] > 0.03) & (G[2] < 0.17)
        bn = hz & (G[0] > 1.17) & (G[0] < 1.24) & (G[1] > -0.20) & (G[1] < FN + 0.15)
        bw = hz & (G[1] > -0.18) & (G[1] < -0.04) & (G[0] > FW - 0.15) & (G[0] < 1.26)
        if bn.sum() >= 3:
            y = G[1][bn]; N.append((y.max(), np.percentile(y, 99), np.percentile(y, 95), bn.sum())); allN.append(y)
        if bw.sum() >= 3:
            x = G[0][bw]; Wf.append((x.min(), np.percentile(x, 1), np.percentile(x, 5), bw.sum())); allW.append(x)
    N, Wf = np.array(N), np.array(Wf); yN = np.concatenate(allN); xW = np.concatenate(allW)
    print('== %s: 깊이 %d×%d · %d 장 · 카메라 지도 (%.2f, %.2f, %.2f) m · fx %.1f → 1.2 m 에서 화소 한 칸 %.1f cm'
          % (nm, W, H, len(frames), cam[0], cam[1], cam[2], fx, 120 / fx))
    print('  북 면(y = −0.02) 띠 점: 프레임당 %d 점(중앙) · 면 밖 최댓값 중앙 %+.1f cm · 99 %% %+.1f · 95 %% %+.1f | 전체 점 중 면 밖 > 1 cm %.1f %% · > 2.5 cm %.1f %%'
          % (np.median(N[:, 3]), 100 * (np.median(N[:, 0]) - FN), 100 * (np.median(N[:, 1]) - FN), 100 * (np.median(N[:, 2]) - FN),
             100 * (yN > FN + 0.01).mean(), 100 * (yN > FN + 0.025).mean()))
    print('  서 면(x = 1.151) 띠 점: 프레임당 %d 점(중앙) · 면 밖 최댓값 중앙 %+.1f cm · 1 %% %+.1f · 5 %% %+.1f | 전체 점 중 면 밖 > 1 cm %.1f %% · > 2.5 cm %.1f %%'
          % (np.median(Wf[:, 3]), 100 * (FW - np.median(Wf[:, 0])), 100 * (FW - np.median(Wf[:, 1])), 100 * (FW - np.median(Wf[:, 2])),
             100 * (xW < FW - 0.01).mean(), 100 * (xW < FW - 0.025).mean()))
