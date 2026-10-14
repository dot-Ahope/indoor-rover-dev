#!/usr/bin/env python3
"""anal_person_event — 주행 중 로버 앞에 무엇이 나타났다 사라졌는지와 그때 속도·전역 경로가 어떻게 변했는지 시간순으로 낸다. (2026-10-14, 오늘만 — f2r2 에서 사람이 지나갔다는 사용자 관찰 확인)
  칸마다(0.5 s): 앞쪽 통로(차체 앞 3 m · 좌우 ±0.35 m)의 가장 가까운 라이다 점 거리, 명령 속도, 전역 경로 길이,
               전역 경로 위(로버 앞 0.3~1.5 m)에서 전역 비용이 내접(99) 이상인 점 수 = BT 의 '앞 경로 막힘' 판정 재료.
  출력은 앞쪽 거리가 1.5 m 안으로 들어온 구간 앞뒤만.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, h0, h1 = sys.argv[1:4]
def T3(tr):
    q = tr.rotation; x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M
static = {}; ob = []; mo = []; glo = []; plans = []; scans = []; cmds = []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/global_costmap/costmap', '/plan', '/scan', '/cmd_vel')]):
        ts = t / 1e9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
        elif c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T3(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T3(tr.transform)))
        elif c.topic == '/plan':
            if len(m.poses) > 1: plans.append((ts, np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses])))
        elif c.topic == '/cmd_vel': cmds.append((ts, m.linear.x, m.angular.z))
        elif c.topic == '/scan':
            r = np.array(m.ranges); a = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 6); scans.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum()), np.ones(ok.sum())]))
        else: glo.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)))
def chain(frame):
    M = np.eye(4)
    while frame != 'base_link': par, mm = static[frame]; M = mm @ M; frame = par
    return M
last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
day = time.strftime('%Y-%m-%d ', time.localtime(ob[0][0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); tA, tB = ep(h0), ep(h1)
rows = []
for t in np.arange(tA, tB, 0.5):
    Mmb = last(mo, t)[1] @ last(ob, t)[1]; sc = last(scans, t); sb = (chain(sc[1]) @ sc[2].T).T; fr = sb[(sb[:, 0] > 0.262) & (sb[:, 0] < 3.3) & (np.abs(sb[:, 1]) < 0.35)]
    ahead = fr[:, 0].min() - 0.262 if len(fr) else float('nan'); pl = last(plans, t)[1]; g = last(glo, t); cm = last(cmds, t)
    d = np.hypot(pl[:, 0] - Mmb[0, 3], pl[:, 1] - Mmb[1, 3]); k0 = int(np.argmin(d)); seg = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pl[k0:], axis=0).T))]); P = pl[k0:][(seg >= 0.30) & (seg <= 1.5)]
    i = ((P[:, 1] - g[2]) / g[3]).astype(int); j = ((P[:, 0] - g[1]) / g[3]).astype(int); ok = (i >= 0) & (i < g[4].shape[0]) & (j >= 0) & (j < g[4].shape[1]); nb = int((g[4][i[ok], j[ok]] >= 99).sum())
    rows.append((t, ahead, cm[1], float(np.hypot(*np.diff(pl, axis=0).T).sum()), nb, last(plans, t)[0]))
R = np.array(rows); near = np.where(R[:, 1] < 1.5)[0]; show = set()
for k in near: show.update(range(max(0, k - 6), min(len(R), k + 7)))
print('시각        앞쪽 가장 가까운 라이다 점   명령 속도   전역 경로 길이   앞 경로 위 내접 이상 점 수   (경로 갱신 시각)'); prev = None
for k in sorted(show):
    if prev is not None and k != prev + 1: print('   …')
    t, a, v, L, nb, tp = R[k]; prev = k
    print('%s.%d      %s                %.3f m/s    %.2f m          %2d                      %s' % (time.strftime('%H:%M:%S', time.localtime(t)), int(t % 1 * 10), ('%.2f m' % a) if a == a else '없음  ', v, L, nb, time.strftime('%H:%M:%S', time.localtime(tp))))
