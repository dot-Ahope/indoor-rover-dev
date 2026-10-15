#!/usr/bin/env python3
"""anal_map_vs_lidar — 그 순간의 라이다 점(지도 좌표)을 저장 지도(office_v3) 점유 칸과 겹쳐, 서쪽 벽 · 동쪽 면이 각각 얼마나 어긋나는지. (2026-10-15 §10, 오늘만)
  왜: 저장 지도의 서쪽 벽이 x −2.10 까지 점유인데 오늘 라이다 서쪽 면은 −2.23(§9.1). 사용자: 그 자리 물체는 무겁고 옮기지 않는다 → 물체 변화가 아니라
      지도 오차(번짐)인지, 그 자리에서 위치 추정(map→odom)이 어긋난 것인지. 양쪽 면이 같은 방향으로 밀렸으면 위치 어긋남, 한쪽만이면 지도 번짐.
  방법: y 띠(5 cm)마다 — 라이다: 통로 중심 x0 기준 서쪽 점 중 가장 동쪽 · 동쪽 점 중 가장 서쪽. 저장 지도: 같은 행에서 x0 기준 서쪽 점유 칸 중 가장 동쪽 칸의 동쪽 가장자리 · 동쪽 점유 칸 중 가장 서쪽 칸의 서쪽 가장자리.
  인자: bag HH:MM:SS.f x0 y0 y1 [지도 yaml=Docs/04_navigation/maps/office_v3.yaml]"""
import sys, time, math
from pathlib import Path
import numpy as np, yaml
from PIL import Image
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
tm = lambda x, y, P: (P[0] + math.cos(P[2]) * x - math.sin(P[2]) * y, P[1] + math.sin(P[2]) * x + math.cos(P[2]) * y)
bag, hh = sys.argv[1:3]; X0, Y0, Y1 = [float(v) for v in sys.argv[3:6]]; MY = sys.argv[6] if len(sys.argv) > 6 else 'Docs/04_navigation/maps/office_v3.yaml'
hms, _, fr = hh.partition('.'); ob = mo = lid = None; sc = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    T = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/scan')]):
        ts = t / 1e9
        if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
        if ts > T: break
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/scan': sc = m; continue
        for tr in m.transforms:
            v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
            elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
            elif tr.child_frame_id == 'lidar_link':
                q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
r = np.array(sc.ranges); an = sc.angle_min + np.arange(len(r)) * sc.angle_increment; ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
px, py = r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
lx, ly = tm(*tm(bx, by, ob), mo)
Y = yaml.safe_load(open(MY, encoding='utf-8')); img = np.array(Image.open(MY.replace('.yaml', '.pgm'))); res = Y['resolution']; ox, oy = Y['origin'][:2]; H = img.shape[0]
print('%s · map→odom (%.3f, %.3f, %+.2f°) · 통로 중심 기준 x0 %.2f' % (hh, mo[0], mo[1], math.degrees(mo[2]), X0))
print('y 띠    라이다 서 · 동     지도 서 · 동      서쪽 차(라이다−지도)  동쪽 차   (+ = 라이다가 지도보다 동쪽)')
dw = []; de = []
for y in np.arange(Y0, Y1, -0.05):
    k = np.abs(ly - y) < 0.025; W = lx[k & (lx < X0)]; E = lx[k & (lx > X0)]
    row = int(H - 1 - (y - oy) / res); xs = ox + (np.arange(img.shape[1]) + 0.5) * res; occ = img[row] < 50
    mw = xs[occ & (xs < X0)]; me = xs[occ & (xs > X0)]
    lw = W.max() if len(W) else np.nan; le = E.min() if len(E) else np.nan; gw = mw.max() + res / 2 if len(mw) else np.nan; ge = me.min() - res / 2 if len(me) else np.nan
    dw.append(lw - gw); de.append(le - ge)
    print('%+.2f   %+.3f · %+.3f   %+.3f · %+.3f      %+5.1f cm            %+5.1f cm' % (y, lw, le, gw, ge, 100 * (lw - gw), 100 * (le - ge)))
print('중앙값: 서쪽 %+.1f cm · 동쪽 %+.1f cm' % (100 * np.nanmedian(dw), 100 * np.nanmedian(de)))
