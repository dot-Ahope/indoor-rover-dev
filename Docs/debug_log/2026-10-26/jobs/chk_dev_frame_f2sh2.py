#!/usr/bin/env python3
"""chk_dev_frame_f2sh2 — f2sh2 복귀 굽은 곳(13:18:25~13:18:38) 경로 이탈이 컨트롤러 탓인지 위치 보정(map→odom) 탓인지 가름 (2026-10-26 §9, PC).
  ① odom 좌표: 로버(odom→base_link) ↔ 컨트롤러가 받은 경로(/transformed_global_plan, odom) 옆 거리 — 컨트롤러가 자기 좌표에서 경로를 벗어났나
  ② map→odom 변화량(같은 창) — SLAM 보정이 경로를 로버 밑에서 옮겼나
  ③ map 좌표 이탈(기존 anal_track_dev 와 같은 정의) 참고. 부호 + = 상자(map 1.2, −0.1) 쪽.  인자: bag"""
import sys, math, bisect, time
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
MO, OB, TP = [], [], []
with AnyReader([Path(sys.argv[1])], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/transformed_global_plan')]):
        m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, v))
        elif len(m.poses) > 2: TP.append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
for L in (MO, OB, TP): L.sort(key=lambda q: q[0])
at = lambda L, t: L[max(bisect.bisect_right([q[0] for q in L], t) - 1, 0)][1]
d0 = time.strftime('%Y-%m-%d ', time.localtime(OB[0][0])); ep = lambda s: time.mktime(time.strptime(d0 + s[:8], '%Y-%m-%d %H:%M:%S')) + float(s[8:])
BOXm = np.array([1.206, -0.11])
def sdist(P, q, toward):
    a, b = P[:-1], P[1:]; ab = b - a; u = np.clip(np.einsum('ij,ij->i', q - a, ab) / np.maximum(np.einsum('ij,ij->i', ab, ab), 1e-9), 0, 1)
    F = a + u[:, None] * ab; k = int(np.argmin(np.linalg.norm(F - q, axis=1))); d = float(np.linalg.norm(F[k] - q))
    return d if np.linalg.norm(q - toward) < np.linalg.norm(F[k] - toward) else -d
mo0 = at(MO, ep('13:18:25.0'))
print(' 시각     | odom: 로버↔컨트롤러 경로(+ 상자 쪽) | map→odom 변화(25.0 s 대비) x y yaw')
for t in np.arange(ep('13:18:25.0'), ep('13:18:38.0'), 0.5):
    mo = at(MO, t); ob = at(OB, t); P = at(TP, t)
    # 상자 위치를 odom 으로: map→odom 의 역변환
    c, s = math.cos(mo[2]), math.sin(mo[2]); dx, dy = BOXm[0] - mo[0], BOXm[1] - mo[1]; box_o = np.array([c * dx + s * dy, -s * dx + c * dy])
    e = sdist(P, np.array(ob[:2]), box_o)
    print(' %s | %+6.1f cm | %+5.1f %+5.1f cm %+5.2f°' % (time.strftime('%H:%M:%S', time.localtime(t)) + '.%d' % int(t % 1 * 10), 100 * e, 100 * (mo[0] - mo0[0]), 100 * (mo[1] - mo0[1]), math.degrees(mo[2] - mo0[2])))
