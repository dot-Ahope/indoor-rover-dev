#!/usr/bin/env python3
"""anal_cam_vs_lidar — 카메라(nvblox 거리 지도 조각)가 라이다로 확인되는 면을 실제보다 앞에(과대) / 같게 / 뒤에(과소) 찍는지, 아예 못 찍는지(누락). (2026-10-15 §9, 오늘만)
  왜: 대책 (가)(카메라만 본 칸 한 겹을 '넘을 수 있는 칸'으로) 의 전제 — 사용자: "카메라가 물체 크기를 과대평가할 수는 있어도 과소평가하지는 못할 때 적절".
      라이다 점 = 그 높이(0.185 m)의 실제 면(기준). 카메라 슬라이스는 z 0.06~0.30 이라 라이다 높이를 포함한다.
  방법: 1 s 마다 최신 /nvblox_node/static_map_slice(odom, 0.05 m) 와 /scan. 카메라 위치(base_link → camera_link)에서 시야(|방위| ≤ 40°) · 거리 0.3~1.3 m 안의 라이다 점마다,
        카메라 → 점 방향으로 1 cm 씩 나가며 조각 거리 ≤ 0(점유)인 첫 지점 s 를 찾는다(최대 점 + 0.15 m). 차이 = s − 라이다 거리:
        ≤ −2.5 cm = 앞(과대) · ±2.5 cm = 같음 · > +2.5 cm = 뒤(과소) · 끝까지 점유 없음 = 누락(그 칸이 '미지' 면 미관측으로 따로 셈).
        5 cm 칸이라 ±2.5 cm 는 칸 반올림 범위.
  한계: 라이다 높이에서 튀어나온 것이 그 아래 높이에 있으면(예: 종이백 아래 상자) 카메라가 '앞'으로 나오는 것은 실제로 맞는 값 — 과대에 섞인다. 과소 · 누락 쪽 판단에는 영향 없음.
  인자: [저장 폴더] 이름=bag@HH:MM:SS~HH:MM:SS ... (저장 폴더가 있으면 점마다 거리 · 방위 · 로버 속도 · 차이 · 지도 x · y 를 cvl_<이름>.npy 로)"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
tm = lambda x, y, P: (P[0] + math.cos(P[2]) * x - math.sin(P[2]) * y, P[1] + math.sin(P[2]) * x + math.cos(P[2]) * y)
OUTD = sys.argv.pop(1) if len(sys.argv) > 1 and not '=' in sys.argv[1] else '.'
print('구간            점 수   앞(과대)        같음(±2.5)      뒤(과소)        누락(관측됨)    미관측   차이 중앙값 · 5 % · 95 %(cm, − = 앞)')
for spec in sys.argv[1:]:
    nm, rest = spec.split('='); bag, rng = rest.split('@'); h0, h1 = rng.split('~')
    ob = lid = cam = None; sl = None; sc = None; last = 0; D = []; miss = 0; unk = 0; META = []; VLAST = 0.0
    with AnyReader([Path(bag)], default_typestore=ts_) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/scan', '/nvblox_node/static_map_slice', '/odometry/filtered')]):
            m = rd.deserialize(raw, c.msgtype); tsec = t / 1e9
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                    elif tr.child_frame_id == 'camera_link' and tr.header.frame_id == 'base_link': cam = v
                    elif tr.child_frame_id == 'lidar_link':
                        q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
                continue
            if c.topic == '/scan': sc = m; continue
            if c.topic == '/odometry/filtered': VLAST = abs(m.twist.twist.linear.x) + 0.3 * abs(m.twist.twist.angular.z); continue
            sl = m
            h = time.strftime('%H:%M:%S', time.localtime(tsec))
            if not (h0 <= h <= h1) or tsec - last < 1.0 or ob is None or lid is None or cam is None or sc is None: continue
            last = tsec
            d = np.array(sl.data, np.float32).reshape(sl.height, sl.width); res = sl.resolution; sox, soy = sl.origin.x, sl.origin.y
            def look(x, y):
                ix = int((x - sox) / res); iy = int((y - soy) / res)
                if 0 <= ix < sl.width and 0 <= iy < sl.height: return d[iy, ix]
                return sl.unknown_value
            C = tm(cam[0], cam[1], ob) + (ob[2] + cam[2],)
            r = np.array(sc.ranges); an = sc.angle_min + np.arange(len(r)) * sc.angle_increment; ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
            px, py = r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
            lx, ly = tm(bx, by, ob)
            for x, y in list(zip(lx, ly))[::3]:
                dx, dy = x - C[0], y - C[1]; R = math.hypot(dx, dy); b = math.degrees(math.atan2(dy, dx) - C[2]); b = (b + 180) % 360 - 180
                if abs(b) > 40 or R < 0.3 or R > 1.3: continue
                ux, uy = dx / R, dy / R; hit = None; sawunk = False
                for s in np.arange(0.15, R + 0.15, 0.01):
                    v = look(C[0] + ux * s, C[1] + uy * s)
                    if v == sl.unknown_value: sawunk = True if s > R - 0.15 else sawunk; continue
                    if v <= 0: hit = s; break
                if hit is None:
                    if sawunk: unk += 1
                    else: miss += 1; META.append((R, b, VLAST, np.nan, x, y))
                else: D.append(hit - R); META.append((R, b, VLAST, hit - R, x, y))
    D = np.array(D); n = len(D) + miss + unk
    np.save('%s/cvl_%s.npy' % (OUTD, nm.split('(')[0]), np.array(META))
    f = lambda k: '%5d (%4.1f %%)' % (k, 100 * k / max(n, 1))
    print('%-14s %6d   %s %s %s %s %5d    %+.1f · %+.1f · %+.1f' % (nm, n, f((D <= -0.025).sum()), f((np.abs(D) < 0.025).sum()), f((D >= 0.025).sum()), f(miss), unk,
          100 * np.median(D), 100 * np.percentile(D, 5), 100 * np.percentile(D, 95)))
