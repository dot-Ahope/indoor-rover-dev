#!/usr/bin/env python3
"""prep_scenes — 계획기 오프라인 비교(Phase P §4 · P7)용 장면 묶음을 bag 에서 뽑는다 (2026-10-23, PC, 로버 안 움직임).
  왜: NavFn(B0)과 Smac Hybrid 를 '같은 지도 · 같은 출발 · 같은 목표' 로 비교하려면 실제 주행 순간을 그대로 꺼내야 함.
  장면 = (이름, 지도 = 그 시각 직전의 /global_costmap/costmap, 출발 = 그 시각 로버 자세(map, /tf), 목표 = 러너 기록의 목표 자세).
    목표 자세는 러너 출력의 '목표 N 출발: map (x, y, yaw°)' 줄(경로 끝 방향 자동 yaw 포함) — BT 가 실제로 받은 목표.
  출력: npz 하나(장면별 grid int8 · origin · res · start · goal · 메타) — Jetson 쪽 query_planners.py 입력.
  인자: 출력.npz 날짜폴더  (장면 목록은 아래 SCENES — 실행마다 고쳐 씀)"""
import sys, math, bisect, time, re, json
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

# (이름, 주행, 지도 시각 HH:MM:SS.ss, 출발 시각(None = 지도 시각), 목표 번호, 설명)
SCENES = [
    ('b910_rp1_replan', 'f2rp1', '14:06:23.13', None, 3, 'f2rp1 상자 막힘 뒤 재계획 자리(B0 실제 여유 15.4 cm)'),
    ('b910_rp2_replan', 'f2rp2', '14:18:30.08', None, 3, 'f2rp2 상자 막힘 뒤 재계획 자리(B0 5.5 cm)'),
    ('b910_rp5_replan', 'f2rp5', '17:22:43.08', None, 3, 'f2rp5 상자 막힘 뒤 재계획 자리(B0 3.1 cm)'),
    ('b910_rp5_full', 'f2rp5', '17:22:43.08', '17:21:40.31', 3, 'f2rp5 복귀 출발(5.4, −2.2)부터, 상자를 아는 지도로'),
    ('west_rp3_g4', 'f2rp3', '14:47:09.00', None, 4, 'f2rp3 서쪽 통로 남행(목표 4) 출발 — B0 경로가 99 칸 지남'),
    ('west_rp3_g5', 'f2rp3', '14:47:43.65', None, 5, 'f2rp3 서쪽 통로 북행(목표 5) 출발'),
]
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


def goals_of(runtxt):
    G = {}
    for line in open(runtxt, encoding='utf-8', errors='replace'):
        m = re.match(r'목표 (\d+) 출발: map \(([-\d.]+), ([-\d.]+), ([-\d.]+)°\)', line.strip())
        if m: G[int(m.group(1))] = (float(m.group(2)), float(m.group(3)), math.radians(float(m.group(4))))
    return G


out, day = sys.argv[1], Path(sys.argv[2]); data = {}; meta = []
import tarfile, tempfile, shutil
for run in sorted({s[1] for s in SCENES}):
    tmp = tempfile.mkdtemp(); tarfile.open(day / 'bags' / ('bag_%s.tgz' % run)).extractall(tmp)
    MO, OB, GR = [], [], []
    with AnyReader([Path(tmp) / ('bag_' + run)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        d0 = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/global_costmap/costmap')]):
            ts = t * 1e-9; m = rd.deserialize(raw, c.msgtype)
            if d0 is None: d0 = time.strftime('%Y-%m-%d ', time.localtime(ts))
            if c.topic == '/tf':
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, v))
            else: GR.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int8).reshape(m.info.height, m.info.width)))
    shutil.rmtree(tmp, ignore_errors=True)
    for L in (MO, OB, GR): L.sort(key=lambda q: q[0])
    at = lambda L, t: L[max(bisect.bisect_right([q[0] for q in L], t) - 1, 0)]
    ep = lambda s: time.mktime(time.strptime(d0 + s[:8], '%Y-%m-%d %H:%M:%S')) + float(s[8:])
    G = goals_of(day / 'outputs' / ('run_%s.txt' % run))
    for name, r, tg, tst, gi, desc in SCENES:
        if r != run: continue
        g = at(GR, ep(tg)); st = comp(at(MO, ep(tst or tg))[1], at(OB, ep(tst or tg))[1])
        data[name + '/grid'] = g[4]; data[name + '/info'] = np.array([g[1], g[2], g[3], g[0]])
        data[name + '/start'] = np.array(st); data[name + '/goal'] = np.array(G[gi])
        meta.append(dict(name=name, run=run, grid_time=tg, grid_stamp=time.strftime('%H:%M:%S', time.localtime(g[0])), start_time=tst or tg, goal=gi, desc=desc))
        print('%-16s 지도 %s(%dx%d) 출발 (%.2f, %.2f, %.0f°) → 목표 %d (%.2f, %.2f, %.0f°) | %s' % (name, meta[-1]['grid_stamp'], g[4].shape[1], g[4].shape[0], st[0], st[1], math.degrees(st[2]), gi, *G[gi][:2], math.degrees(G[gi][2]), desc))
data['meta'] = np.array(json.dumps(meta, ensure_ascii=False))
np.savez_compressed(out, **data); print('저장', out, '장면', len(meta))
