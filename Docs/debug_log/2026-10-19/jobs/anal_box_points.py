#!/usr/bin/env python3
"""anal_box_points — 깊이 영상 화소를 그 순간의 tf 로 지도 좌표 점으로 바꿔, 출발점 시험 상자의 면이 관측마다 어디에 찍히는지. (2026-10-19 §10)
  왜: §9 — nvblox 설정 · 깊이 잡음 대책이 과장(+5.3 cm)을 못 바꿈 → 원인 후보 (a) 기록 상자 위치 (b) 카메라 외부 보정 각도 (c) SLAM/오도메트리.
      원시 점(nvblox 전)에서도 북쪽 면이 +5 cm 면 위치 · 보정 쪽, 점은 맞고 nvblox 만 +5 면 지도 만들기 쪽.
  방법: 깊이(160×120, mm) × camera_info K → 광학 프레임 점 → tf_static(base_link→…→광학) → odom→base_link · map→odom(깊이 시각 직전 값) → 지도 점.
       상자 점 = 지도 x 1.05~1.40, y −0.32~+0.15, 높이 z 0.04~0.17 m(바닥 · 상자 위 14 cm 너머 제외), 카메라 거리 0.45~1.6 m.
       면: 북쪽 = 상자 x 구간(1.16~1.25) 점의 y 상위 2 %(로버 쪽 끝), 서쪽 = y 구간(−0.18~−0.04) 점의 x 하위 2 %. 점 30 개 미만이면 건너뜀.
  기록 상자: x 1.151~1.261, y −0.20~−0.02. 출력 = 프레임 표(csv) + 묶음 요약(구간 · 로버 방향 · 카메라 방위 · 거리).
  인자: bag 출력csv [통과시각 s — 주면 상자 점을 그 순간의 오도메트리 기억 위치로도 옮김(§14)]"""
import sys, math, bisect, csv
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

BOX = (1.151, 1.261, -0.20, -0.02)
bag, outcsv = sys.argv[1:3]


def qm(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def T(tr):
    M = np.eye(4); M[:3, :3] = qm(tr.rotation); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


static = {}; MO, OB = [], []; K = None; frames = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
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
            frames.append((st, m.header.frame_id, np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width).copy()))
MO.sort(key=lambda q: q[0]); OB.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]


def chain(frame):
    M = np.eye(4)
    while frame != 'base_link':
        p, A = static[frame]; M = A @ M; frame = p
    return M


def at(L, Lt, t):
    i = bisect.bisect_right(Lt, t) - 1
    return L[max(i, 0)][1] if i >= 0 else None


TPASS = float(sys.argv[3]) if len(sys.argv) > 3 else None   # 10-19 §14: 통과 순간(첫 깊이 프레임 기준 s)
MP = at(MO, MOt, frames[0][0] + TPASS) if TPASS is not None else None
Bc = chain(frames[0][1]); fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]
H, W = frames[0][2].shape; vv, uu = np.mgrid[0:H, 0:W]
t0 = frames[0][0]; rows = []
for st, fid, img in frames:
    mo = at(MO, MOt, st); ob = at(OB, OBt, st)
    if mo is None or ob is None: continue
    z = img.astype(np.float32) / 1000.0; ok = (z > 0.45) & (z < 1.6)
    if ok.sum() < 30: continue
    P = np.stack([(uu[ok] - cx) / fx * z[ok], (vv[ok] - cy) / fy * z[ok], z[ok], np.ones(ok.sum())])
    Mmap = mo @ ob @ Bc; G = (Mmap @ P)[:3]
    k = (G[0] > 1.05) & (G[0] < 1.40) & (G[1] > -0.32) & (G[1] < 0.15) & (G[2] > 0.04) & (G[2] < 0.17)
    if k.sum() < 30: continue
    gx, gy = G[0][k], G[1][k]
    nm = (gx > 1.16) & (gx < 1.25); wm = (gy > -0.18) & (gy < -0.04)
    north = np.percentile(gy[nm], 98) if nm.sum() >= 15 else np.nan
    sm = (gx > 1.16) & (gx < 1.25); em = (gy > -0.18) & (gy < -0.04)
    south = np.percentile(gy[sm], 2) if sm.sum() >= 15 else np.nan
    east = np.percentile(gx[em], 98) if em.sum() >= 15 else np.nan
    # 10-19 §14: 통과 순간(TPASS) 오도메트리 기억으로 옮긴 상자 점 중심 — odom 점 = (map→odom 관측 시각)⁻¹ · 지도 점, 다시 map→odom(통과 시각) 으로
    if MP is not None:
        Gh = np.vstack([G[:, k], np.ones(k.sum())]); Gp = (MP @ np.linalg.inv(mo) @ Gh)[:3]; pc = (float(np.median(Gp[0])), float(np.median(Gp[1])))
    else: pc = (np.nan, np.nan)
    west = np.percentile(gx[wm], 2) if wm.sum() >= 15 else np.nan
    R = mo @ ob; rx, ry = R[0, 3], R[1, 3]; ryaw = math.degrees(math.atan2(R[1, 0], R[0, 0]))
    C = Mmap; cxw, cyw = C[0, 3], C[1, 3]
    # 카메라 광축(광학 z)의 지도 방향과 상자 중심 방위
    ax = C[:3, 2]; cam_yaw = math.atan2(ax[1], ax[0]); bc = (1.206 - cxw, -0.11 - cyw)
    bear = math.degrees(math.atan2(math.sin(math.atan2(bc[1], bc[0]) - cam_yaw), math.cos(math.atan2(bc[1], bc[0]) - cam_yaw)))
    rows.append(dict(t=round(st - t0, 2), rx=rx, ry=ry, ryaw=ryaw, rng=math.hypot(*bc), bear=bear, n=int(k.sum()),
                     north=north, west=west, north_off=100 * (north - BOX[3]) if not np.isnan(north) else np.nan,
                     west_off=100 * (BOX[0] - west) if not np.isnan(west) else np.nan,
                     south_off=100 * (BOX[2] - south) if not np.isnan(south) else np.nan, east_off=100 * (east - BOX[1]) if not np.isnan(east) else np.nan,
                     cx_obs=float(np.median(gx)), cy_obs=float(np.median(gy)), cx_pass=pc[0], cy_pass=pc[1],
                     mo_x=mo[0, 3], mo_y=mo[1, 3], mo_yaw=math.degrees(math.atan2(mo[1, 0], mo[0, 0]))))
with open(outcsv, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
print('상자 점이 30 개 넘는 깊이 프레임 %d / %d · 카메라 광학 프레임 %s' % (len(rows), len(frames), frames[0][1]))
A = lambda key, sel: np.array([r[key] for r in rows if sel(r)], float)
def summ(lab, sel):
    no = A('north_off', sel); we = A('west_off', sel); no = no[~np.isnan(no)]; we = we[~np.isnan(we)]
    if len(no) == 0 and len(we) == 0: return
    s = lambda v: ('%+5.1f (n %3d, 사분위 %+.1f~%+.1f)' % (np.median(v), len(v), np.percentile(v, 25), np.percentile(v, 75))) if len(v) else '      -'
    print('  %-34s 북쪽 면 과장 %s · 서쪽 면 과장 %s' % (lab, s(no), s(we)))
print('묶음별(과장 + = 로버 쪽 · 실제 면보다 밖, cm):')
summ('전체', lambda r: True)
# 구간: 시간 순 큰 틈으로 나뉜 관측 덩어리
ts = [r['t'] for r in rows]; cuts = [0] + [i for i in range(1, len(ts)) if ts[i] - ts[i - 1] > 5] + [len(ts)]
for a, b in zip(cuts, cuts[1:]):
    seg = rows[a:b]; summ('구간 t %.0f~%.0f s (로버 yaw %+.0f~%+.0f°)' % (seg[0]['t'], seg[-1]['t'], min(r['ryaw'] for r in seg), max(r['ryaw'] for r in seg)), lambda r, s=seg: r in s)
for lo, hi in ((-50, -20), (-20, 0), (0, 20), (20, 50)):
    summ('카메라 방위 %+d~%+d° (+ = 왼쪽)' % (lo, hi), lambda r, lo=lo, hi=hi: lo <= r['bear'] < hi)
for lo, hi in ((0.45, 0.8), (0.8, 1.1), (1.1, 1.6)):
    summ('카메라 ↔ 상자 중심 %.2f~%.2f m' % (lo, hi), lambda r, lo=lo, hi=hi: lo <= r['rng'] < hi)
