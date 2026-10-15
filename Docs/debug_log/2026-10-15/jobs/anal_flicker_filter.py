#!/usr/bin/env python3
"""anal_flicker_filter — 후보 3 오프라인 검증: 카메라만 본 칸 중 '시야 안에서 자주 빠지는(깜빡이는)' 칸만 낮춘다면, 실제 면은 남고 과장 칸만 지워지는가. (2026-10-15 §12, 오늘만)
  판정 기준(시험 전 선언, SUMMARY §12): ① 서쪽 통로 상자 — 바깥 줄(과장) 칸 낮춤, 안쪽 줄(실제 면) 칸 유지, 멈춘 순간 최근접 거리 > 4.4 cm
                                       ② 출발점 시험 상자 — 로버가 지날 때 로버 쪽 면 칸이 하나 이상 남음(면 전체가 사라지면 불합격).
  방법: /nvblox_node/static_map_slice(카메라 전용 거리 지도, odom, 0.05 m) 프레임마다, 칸(odom 0.05 m 격자에 고정)이
        '시야 안' = 카메라 기준 |방위| ≤ 43° · 거리 0.15~1.4 m · 그 칸 값이 미지 아님 · 카메라→칸 선 위(칸 앞 1 칸 전까지)에 점유(≤ 0) 칸 없음(가림 없음)
        이면 시야 횟수 +1, 그때 거리 ≤ 0 이면 점유 횟수 +1. 비율 = 점유 / 시야(기준 시각까지 누적).
        라이다 확인 칸(구간 중 라이다 점이 3.5 cm 안에 한 번이라도) 은 제외. 깜빡임 = 시야 ≥ M 이고 비율 < θ. 시야 < M 은 그대로 장애물(보수적).
  출력: 구역의 칸마다 지도 좌표 · 시야 · 점유 · 비율 · 판정(θ 0.8 / 0.9). [정지 평가] 기준 시각의 로컬 치명 칸에서 낮춘 칸을 빼고 차체 최근접 거리.
  인자: bag 시작HH:MM:SS 기준HH:MM:SS.f 구역x0,x1,y0,y1(지도) [M=8]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
tm = lambda x, y, P: (P[0] + np.cos(P[2]) * x - np.sin(P[2]) * y, P[1] + np.sin(P[2]) * x + np.cos(P[2]) * y)
bag, h0, hb, box = sys.argv[1:5]; M = int(sys.argv[5]) if len(sys.argv) > 5 else 8
BX0, BX1, BY0, BY1 = [float(v) for v in box.split(',')]
hms, _, fr = hb.partition('.')
XF, XR, HW = 0.272, -0.258, 0.175; R0 = 0.05; HFOV = math.radians(43); RMAX = 1.4
ob = mo = lid = cam = None; sc = None; lc_last = None
vis = {}; occ = {}; lidar_cells = set(); nfr = 0
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    TB = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/scan', '/nvblox_node/static_map_slice', '/local_costmap/costmap')]):
        tsec = t / 1e9
        if TB is None: day = time.strftime('%Y-%m-%d ', time.localtime(tsec)); TB = time.mktime(time.strptime(day + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0); TA = time.mktime(time.strptime(day + h0, '%Y-%m-%d %H:%M:%S'))
        if tsec > TB + 0.05: break
        m = rd.deserialize(raw, c.msgtype)
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                elif tr.child_frame_id == 'camera_link' and tr.header.frame_id == 'base_link': cam = v
                elif tr.child_frame_id == 'lidar_link':
                    q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
            continue
        if c.topic == '/local_costmap/costmap': lc_last = (m, ob, mo); continue
        if tsec < TA or ob is None or cam is None or mo is None: continue
        if c.topic == '/scan':
            if lid is None: continue
            r = np.array(m.ranges); an = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 3.0)
            px, py = r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
            lx, ly = tm(bx, by, ob)   # odom
            for x, y in zip(lx, ly):   # 3.5 cm 안의 칸 = 라이다 확인(칸 중심 기준 주변 칸까지)
                ix, iy = int(math.floor(x / R0)), int(math.floor(y / R0))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        cx, cy = (ix + dx + 0.5) * R0, (iy + dy + 0.5) * R0
                        if abs(cx - x) < 0.035 and abs(cy - y) < 0.035: lidar_cells.add((ix + dx, iy + dy))
            continue
        # 거리 지도 조각
        nfr += 1
        d = np.array(m.data, np.float32).reshape(m.height, m.width); res = m.resolution; sox, soy = m.origin.x, m.origin.y; UNK = m.unknown_value
        C = (ob[0] + math.cos(ob[2]) * cam[0] - math.sin(ob[2]) * cam[1], ob[1] + math.sin(ob[2]) * cam[0] + math.cos(ob[2]) * cam[1], ob[2] + cam[2])
        # 후보 칸: 카메라 둘레 1.4 m 사각형 안 odom 격자 칸
        ixs = np.arange(int(math.floor((C[0] - RMAX) / R0)), int(math.floor((C[0] + RMAX) / R0)) + 1); iys = np.arange(int(math.floor((C[1] - RMAX) / R0)), int(math.floor((C[1] + RMAX) / R0)) + 1)
        GX, GY = np.meshgrid(ixs, iys); cx = (GX + 0.5) * R0; cy = (GY + 0.5) * R0
        dx = cx - C[0]; dy = cy - C[1]; rng = np.hypot(dx, dy); b = np.arctan2(dy, dx) - C[2]; b = (b + np.pi) % (2 * np.pi) - np.pi
        cand = (rng >= 0.15) & (rng <= RMAX) & (np.abs(b) <= HFOV)
        def look(x, y):
            jx = ((x - sox) / res).astype(int); jy = ((y - soy) / res).astype(int); okk = (jx >= 0) & (jx < m.width) & (jy >= 0) & (jy < m.height)
            out = np.full(x.shape, UNK, np.float32); out[okk] = d[jy[okk], jx[okk]]; return out
        cxv, cyv, rv = cx[cand], cy[cand], rng[cand]; gx, gy = GX[cand], GY[cand]
        val = look(cxv, cyv); known = val != UNK
        # 가림: 카메라→칸 선 위 0.10 m ~ (거리 − 0.075 m) 를 2.5 cm 간격으로, 점유가 있으면 가림
        K = 56; s = np.linspace(0, 1, K)[None, :]
        sx = C[0] + (cxv - C[0])[:, None] * s; sy = C[1] + (cyv - C[1])[:, None] * s
        along = rv[:, None] * s; inside = (along > 0.10) & (along < rv[:, None] - 0.075)
        sv = look(sx.ravel(), sy.ravel()).reshape(sx.shape)
        occl = ((sv <= 0) & (sv != UNK) & inside).any(axis=1)
        seen = known & ~occl
        for x_, y_, v_ in zip(gx[seen], gy[seen], val[seen]):
            k = (int(x_), int(y_)); vis[k] = vis.get(k, 0) + 1
            if v_ <= 0: occ[k] = occ.get(k, 0) + 1
# 구역 칸(지도 좌표) 보고
moB = mo
def to_map(ix, iy):
    x, y = (ix + 0.5) * R0, (iy + 0.5) * R0; return tm(np.array(x), np.array(y), moB)
rows = []
for k, nv in vis.items():
    if occ.get(k, 0) == 0: continue
    mx, my = to_map(*k)
    if not (BX0 <= mx <= BX1 and BY0 <= my <= BY1): continue
    rows.append((float(mx), float(my), nv, occ.get(k, 0), k in lidar_cells, k))
print('%s ~ %s · 거리 지도 프레임 %d · 구역 x %.2f~%.2f y %.2f~%.2f 의 한 번이라도 점유된 칸 %d (M=%d)' % (h0, hb, nfr, BX0, BX1, BY0, BY1, len(rows), M))
print('칸(map)              시야  점유  비율   라이다   θ0.8      θ0.9')
dec = {}
for mx, my, nv, no, isl, k in sorted(rows, key=lambda r: (r[1], r[0])):
    ratio = no / nv
    def judge(th):
        if isl: return '라이다'
        if nv < M: return '유지(적음)'
        return '낮춤' if ratio < th else '유지'
    dec[k] = (judge(0.8), judge(0.9))
    print('(%+.3f, %+.3f)   %4d  %4d  %4.2f   %-5s   %-8s  %-8s' % (mx, my, nv, no, ratio, '예' if isl else '', judge(0.8), judge(0.9)))
# 기준 시각 로컬 코스트맵에서 낮춘 칸을 빼고 차체 최근접 거리
if lc_last is not None:
    lm, lob, lmo = lc_last
    a = np.array(lm.data, np.int16).reshape(lm.info.height, lm.info.width); iy_, ix_ = np.nonzero(a >= 100)
    wx = lm.info.origin.position.x + (ix_ + 0.5) * lm.info.resolution; wy = lm.info.origin.position.y + (iy_ + 0.5) * lm.info.resolution   # odom
    keys = [(int(math.floor(x / R0)), int(math.floor(y / R0))) for x, y in zip(wx, wy)]
    c_, s_ = math.cos(lob[2]), math.sin(lob[2]); bx = c_ * (wx - lob[0]) + s_ * (wy - lob[1]); by = -s_ * (wx - lob[0]) + c_ * (wy - lob[1])
    dist = np.hypot(np.maximum(np.maximum(XR - bx, bx - XF), 0), np.maximum(np.abs(by) - HW, 0)); dist = np.where((bx >= XR) & (bx <= XF) & (np.abs(by) <= HW), 0, dist)
    for i, th in enumerate(('0.8', '0.9')):
        keep = np.array([dec.get(k, ('유지', '유지'))[i] != '낮춤' for k in keys])
        # 낮춘 칸 = 그 칸과 4-이웃(로컬 칸 경계 어긋남 대비)이 아니라 같은 칸만
        nn = int(np.argmin(np.where(keep, dist, 9))); nall = int(np.argmin(dist))
        print('[정지 평가 θ%s] 기준 시각 로컬 치명 %d 칸 중 낮춘 칸 %d · 최근접: 지금 %.1f cm → 낮춘 뒤 %.1f cm' % (th, len(keys), int((~keep).sum()), 100 * dist[nall], 100 * dist[nn]))
