#!/usr/bin/env python3
"""anal_carve — 깊이 원시 화소로, 지정 칸 기둥(지도 x0~x1 · y0~y1 · 높이 z 0.06~0.30 = 조각 띠)에 대해 프레임마다
  (1) 그 기둥 안에 떨어진 점 수(= 칸을 '찍는' 관측) (2) 그 기둥을 지나 더 멀리 끝난 광선 수(= 칸을 '비우는' 관측, TSDF 가 자유 공간으로 깎을 재료)
  (3) 카메라 ↔ 칸 거리 · 방위. (2026-10-22 §11.3, PC)
  왜: 사용자 — "해당 위치를 다시 보았을 때 지워지지 않는 이유". nvblox(TSDF)는 칸을 지나 뒤에 닿은 깊이가 있어야 그 칸을 비운다.
  주의: 광선이 기둥을 지나는지는 광선 위 2 cm 간격 표본으로 판정, 깊이 0(무효) 화소는 광선 없음. 끝점이 1.4 m(통합 거리) 넘으면 따로 셈(nvblox 처리 방식 미확인).
  인자: 깊이bag 시작s 끝s 'x0,x1,y0,y1' [z0,z1=0.06,0.30]   (시각은 bag 시작 기준)
  ⚠ 첫 판 실수: z 0.06~0.30 기둥은 낮은 상자(높이 0.114) 위 빈 공간까지 포함 → 상자 위를 지나간 광선을 '칸을 비우는 광선' 으로 셌다. 상자 높이 칸만 볼 땐 z 0.06,0.11."""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); X0, X1, Y0, Y1 = (float(v) for v in sys.argv[4].split(',')); Z0, Z1 = (float(v) for v in (sys.argv[5] if len(sys.argv) > 5 else '0.06,0.30').split(','))
def qm(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
def T(tr):
    M = np.eye(4); M[:3, :3] = qm(tr.rotation); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M
static = {}; MO, OB = [], []; K = None; FR = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T0 = rd.start_time * 1e-9
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
            if K is None: K = np.array(m.k).reshape(3, 3)
        else:
            st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            if TA <= st - T0 <= TB: FR.append((st, m.header.frame_id, np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width).copy()))
MO.sort(key=lambda q: q[0]); OB.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
def chain(f):
    M = np.eye(4)
    while f != 'base_link': p, A = static[f]; M = A @ M; f = p
    return M
Bc = chain(FR[0][1]); fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]; H, W = FR[0][2].shape; vv, uu = np.mgrid[0:H, 0:W]
S = np.arange(0.02, 1.6, 0.02)   # 광학 z 1.6 m 까지(10-22 §13: 첫 판 1.0 m 는 0.8 m 넘는 접근을 못 봄)
print('bag %s · t %.0f~%.0f s 깊이 %d 장 · 칸 기둥 x %.2f~%.2f y %.2f~%.2f z %.2f~%.2f' % (Path(bag).name, TA, TB, len(FR), X0, X1, Y0, Y1, Z0, Z1))
print('  t(s) | 카메라→칸 거리 · 방위 | 유효 화소 % | 기둥 안 점 | 기둥 지나 뒤에 닿은 광선(끝 ≤1.4 m · >1.4 m) | 기둥을 향한 화소 중 무효(깊이 0)')
agg = []
for st, fid, img in FR[::5]:
    M = at(MO, MOt, st) @ at(OB, OBt, st) @ Bc; o = M[:3, 3]
    z = img.astype(np.float32) / 1000.0; d = np.stack([(uu - cx) / fx, (vv - cy) / fy, np.ones_like(uu, float)], -1).reshape(-1, 3); zz = z.reshape(-1)
    D = (M[:3, :3] @ d.T).T                                  # 광학 z=1 당 지도 방향
    # 화소마다 광선이 기둥을 지나는 깊이 구간(광학 z) — 표본으로
    Pz = o[None, None, :] + D[:, None, :] * S[None, :, None]   # (N, 표본, 3)
    inside = (Pz[..., 0] >= X0) & (Pz[..., 0] <= X1) & (Pz[..., 1] >= Y0) & (Pz[..., 1] <= Y1) & (Pz[..., 2] >= Z0) & (Pz[..., 2] <= Z1)
    hit = inside.any(1)
    if not hit.any(): continue
    zin = np.where(inside, S[None, :], np.inf).min(1); zout = np.where(inside, S[None, :], -np.inf).max(1)
    valid = zz > 0
    ptin = valid & hit & (zz >= zin - 0.01) & (zz <= zout + 0.01)
    carve = valid & hit & (zz > zout + 0.05)
    far = carve & (zz * np.linalg.norm(d, axis=1) > 1.4)
    cc = np.array([(X0 + X1) / 2, (Y0 + Y1) / 2]); dist = float(np.hypot(*(cc - o[:2]))); ax = M[:3, 2]
    bear = math.degrees(math.atan2(math.sin(math.atan2(cc[1] - o[1], cc[0] - o[0]) - math.atan2(ax[1], ax[0])), math.cos(math.atan2(cc[1] - o[1], cc[0] - o[0]) - math.atan2(ax[1], ax[0]))))
    r = (st - T0, dist, bear, 100 * valid.mean(), int(ptin.sum()), int((carve & ~far).sum()), int(far.sum()), int((hit & ~valid).sum()), int(hit.sum()))
    agg.append(r); print('  %6.1f | %.2f m · %+4.0f° | %4.1f | %4d | %4d · %4d | %4d / %d' % r)
if agg:
    A = np.array(agg); print('합: 기둥 안 점 %d · 뒤에 닿은 광선 ≤1.4 m %d · >1.4 m %d · 기둥 향한 무효 화소 %d / %d' % (A[:, 4].sum(), A[:, 5].sum(), A[:, 6].sum(), A[:, 7].sum(), A[:, 8].sum()))
