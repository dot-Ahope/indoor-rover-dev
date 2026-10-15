#!/usr/bin/env python3
"""anal_cell_first_seen — 기준 순간의 카메라만 치명 칸들이 '처음 치명이 된 순간' 카메라에서 본 방위각 · 거리, 그리고 그 전에 시야 안에 있었는데 안 찍혔던 순간. (2026-10-15 §7, 오늘만)
  왜: 사용자 질문 "카메라 엣지의 왜곡이 원인일까?" — 가장자리(±43° 근처)에서만 처음 찍혔고 가운데서는 안 찍혔다면 가장자리 오차 쪽, 가운데에서 찍혔다면 아님.
  방법: 로컬 코스트맵 프레임마다 칸(지도 좌표 고정, 3 cm 안 같은 칸)이 치명인지 → 처음 치명이 된 프레임 시각. 카메라 자세 = base_link → camera_link(tf_static) ∘ 그때 로버 자세(map).
        방위각 = 카메라 앞축 기준(+ = 왼쪽), 시야 = |방위| ≤ 43° 이고 거리 ≤ 1.4 m(nvblox 통합 거리).
        라이다 확인 칸(기준 순간 라이다 점 3.5 cm 안)도 같은 방법으로 견줌.
  인자: bag 기준HH:MM:SS.f 시작HH:MM:SS 구역x0,x1,y0,y1"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
bag, hb, h0, box = sys.argv[1:5]; X0, X1, Y0, Y1 = [float(v) for v in box.split(',')]
tm = lambda x, y, P: (P[0] + math.cos(P[2]) * x - math.sin(P[2]) * y, P[1] + math.sin(P[2]) * x + math.cos(P[2]) * y)
ob = mo = lid = cam = None; sc = None; F = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/scan')]):
        m = rd.deserialize(raw, c.msgtype); ts = t / 1e9
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                elif tr.child_frame_id == 'camera_link' and tr.header.frame_id == 'base_link': cam = v
                elif tr.child_frame_id == 'lidar_link':
                    q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
            continue
        if c.topic == '/scan': sc = m; continue
        h = time.strftime('%H:%M:%S', time.localtime(ts)) + '.%d' % (int(ts * 10) % 10)
        if h[:8] < h0 or h > hb + '9' or ob is None or mo is None or cam is None: continue
        a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
        cx, cy = tm(m.info.origin.position.x + (ix + 0.5) * m.info.resolution, m.info.origin.position.y + (iy + 0.5) * m.info.resolution, mo)
        R = tm(ob[0], ob[1], mo) + (ob[2] + mo[2],); C = tm(cam[0], cam[1], R) + (R[2] + cam[2],)
        lx = ly = None
        if sc is not None and lid is not None:
            r = np.array(sc.ranges); an = sc.angle_min + np.arange(len(r)) * sc.angle_increment; ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
            px, py = r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
            lx, ly = tm(*tm(bx, by, ob), mo)
        F.append((ts, h, np.c_[cx, cy], C, lx, ly))
base = min(F, key=lambda f: abs(f[0] - (F[-1][0] if True else 0)))  # 마지막 프레임 = 기준 순간 직전
ts_b, h_b, CB, Cb, lxb, lyb = F[-1]
sel = (CB[:, 0] > X0) & (CB[:, 0] < X1) & (CB[:, 1] > Y0) & (CB[:, 1] < Y1)
def bearing(C, p):
    dx, dy = p[0] - C[0], p[1] - C[1]; rng = math.hypot(dx, dy); b = math.degrees(math.atan2(dy, dx) - C[2]); b = (b + 180) % 360 - 180; return b, rng
rows = []
for p in CB[sel]:
    lidar = int((np.hypot(lxb - p[0], lyb - p[1]) < 0.035).sum()) if lxb is not None else -1
    first = None; vis_before = []
    for ts, h, CC, C, lx, ly in F:
        on = (np.hypot(CC[:, 0] - p[0], CC[:, 1] - p[1]) < 0.03).any(); b, rng = bearing(C, p)
        if on: first = (h, b, rng); break
        if abs(b) <= 43 and rng <= 1.4: vis_before.append((h, b, rng))
    # 처음 치명이 된 뒤: 시야 안에 있던 마지막 프레임(방위 · 거리)과 그동안 치명이 아니었던 프레임 수(= 다시 보고 지운 흔적)
    after = []; started = False
    for ts, h, CC, C, lx, ly in F:
        if first and h == first[0]: started = True
        if not started: continue
        on = (np.hypot(CC[:, 0] - p[0], CC[:, 1] - p[1]) < 0.03).any(); b, rng = bearing(C, p)
        if abs(b) <= 43 and rng <= 1.4: after.append((h, b, rng, on))
    rows.append((p, lidar, first, vis_before, after))
print('기준 %s · 구역 x %.2f~%.2f y %.2f~%.2f 치명 칸 %d 개 (방위 + = 카메라 왼쪽, 시야 ±43° · 1.4 m)' % (h_b, X0, X1, Y0, Y1, len(rows)))
print('칸(map)            라이다  처음 치명이 된 프레임: 시각 · 방위 · 거리      | 그 전 시야 안이었는데 안 찍힌 프레임 수(방위 범위 · 거리 범위) | 찍힌 뒤 시야 안 프레임(마지막) · 그중 치명 아님')
for p, lidar, first, vb, af in sorted(rows, key=lambda r: (r[1] > 0, r[0][1])):
    fs = '%s · %+5.1f° · %.2f m' % first if first else '(구간 시작부터 이미 치명)'
    vbs = '%d (%+.0f~%+.0f°, %.2f~%.2f m)' % (len(vb), min(v[1] for v in vb), max(v[1] for v in vb), min(v[2] for v in vb), max(v[2] for v in vb)) if vb else '0'
    afs = '시야 안 %d 프레임(마지막 %s · %+.0f° · %.2f m), 그중 치명 아님 %d' % (len(af), af[-1][0], af[-1][1], af[-1][2], sum(1 for a in af if not a[3])) if af else '찍힌 뒤 시야 안 0'
    print('(%.3f, %.3f)   %3s    %-36s | %s | 찍힌 뒤: %s' % (p[0], p[1], ('라이다' if lidar > 0 else '카메라'), fs, vbs, afs))
