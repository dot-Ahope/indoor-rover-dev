#!/usr/bin/env python3
"""anal_box_layers — 정지 때 차체 옆에 있던 치명 칸(상자 끝)을 '어느 층이 언제' 채웠는지 시간순으로 본다. (2026-10-13)
  왜: f2p1 에서 상자 끝 칸이 로버가 0.34 m 옆에 올 때까지 1/4 만 있다가 갑자기 4/4 가 됐다. 후보 = ① 카메라(nvblox) 층 ② 라이다 층 ③ 지도↔오도메트리 보정이 움직여 자리가 옮겨 보임.
  방법: 상자 끝 칸(anal_box_history 와 같은 정의, 지도 좌표 고정)마다
        · nvblox 거리 슬라이스(/nvblox_node/static_map_slice)의 그 자리 값 — 0 이하 = 장애물(코스트맵 nvblox 층이 치명으로 찍음), 양수 = 가장 가까운 장애물까지 거리, '?' = 미관측
        · 라이다(/scan) 점이 그 칸 안에 몇 개 떨어졌나(라이다 층이 찍을 재료)
        · 로컬 코스트맵의 그 자리 치명 여부
        · map→odom 보정이 정지 때에 견줘 얼마나 달랐나(cm·도) — 크면 '자리가 옮겨 보인 것'
  nvblox_msgs/DistanceMapSlice 정의는 PC 에 없어 직접 등록(10-08 nvslice_pc.py 와 같은 정의).
  사용: anal_box_layers.py bag 정지HH:MM:SS 시작HH:MM:SS [간격 s=1.0]"""
import sys, time, math
from pathlib import Path
import numpy as np
from scipy import ndimage
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
bag, hstop, hstart = sys.argv[1:4]; STEP = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])


def T3(tr):
    q = tr.rotation; x, y, z, w = q.x, q.y, q.z, q.w; M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


static = {}; ob = []; mo = []; loc = []; sl = []; scans = []
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    t0 = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/nvblox_node/static_map_slice', '/scan')]):
        ts = t / 1e9
        if t0 is None:
            t0 = ts; day = time.strftime('%Y-%m-%d ', time.localtime(t0)); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S')); tA, tB = ep(hstart), ep(hstop)
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
            continue
        if ts < tA - 2 or ts > tB + 3: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T3(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T3(tr.transform)))
        elif c.topic == '/local_costmap/costmap': loc.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)))
        elif c.topic == '/scan':
            r = np.array(m.ranges); a = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < 5); scans.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.zeros(ok.sum()), np.ones(ok.sum())]))
        else: sl.append((ts, m.header.frame_id, m.origin.x, m.origin.y, m.resolution, m.unknown_value, np.asarray(m.data, np.float32).reshape(m.height, m.width)))


def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def chain(frame):
    M = np.eye(4)
    while frame != 'base_link': par, mm = static[frame]; M = mm @ M; frame = par
    return M
def w2(M, P): return (M @ np.c_[P[:, 0], P[:, 1], np.zeros(len(P)), np.ones(len(P))].T).T[:, :2]
def yaw(M): return math.atan2(M[1, 0], M[0, 0])


# 상자 끝(지도 좌표) — anal_box_history 와 같은 정의
g = last(loc, tB); _, ox, oy, res, G = g; Mob = last(ob, tB)[1]; MmoS = last(mo, tB)[1]; L = np.argwhere(G >= 100); Lo = np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res]
pb = w2(np.linalg.inv(Mob), Lo); d = np.hypot(np.maximum.reduce([FP[:, 0].min() - pb[:, 0], np.zeros(len(pb)), pb[:, 0] - FP[:, 0].max()]), np.maximum.reduce([FP[:, 1].min() - pb[:, 1], np.zeros(len(pb)), pb[:, 1] - FP[:, 1].max()]))
lab, _ = ndimage.label(G >= 100, structure=np.ones((3, 3))); sel = lab[L[:, 0], L[:, 1]] == lab[L[int(np.argmin(d)), 0], L[int(np.argmin(d)), 1]]; BOX = w2(MmoS, Lo[sel]); BOX = BOX[np.lexsort((BOX[:, 0], -BOX[:, 1]))]
print('상자 끝 칸(지도 좌표, 로버 쪽부터): ' + ' '.join('(%.2f, %.2f)' % tuple(b) for b in BOX))
print('nvblox 슬라이스: 좌표계 %s, 칸 %.3f m, 미관측 값 %.1f, %d 장' % (sl[0][1], sl[0][4], sl[0][5], len(sl)))
print('\n시각      로버→끝  방위   nvblox 거리(m, 칸별; 0 이하 = 장애물, ? = 미관측)   라이다 점 수(칸별)   로컬 치명   map→odom 보정 차(정지 때 대비)')
for t in np.arange(tA, tB + 0.01, STEP):
    Mmo = last(mo, t)[1]; Mmb = Mmo @ last(ob, t)[1]; bb = w2(np.linalg.inv(Mmb), BOX).mean(0)
    s = last(sl, t); Ps = BOX if s[1] == 'map' else w2(np.linalg.inv(Mmo), BOX); j = np.floor((Ps[:, 0] - s[2]) / s[4]).astype(int); i = np.floor((Ps[:, 1] - s[3]) / s[4]).astype(int); nv = []
    for a, b in zip(i, j):
        if not (0 <= a < s[6].shape[0] and 0 <= b < s[6].shape[1]): nv.append('  밖 ')
        else: v = s[6][a, b]; nv.append('   ? ' if v == s[5] else '%5.2f' % v)
    sc = last(scans, t); SP = (Mmb @ chain(sc[1]) @ sc[2].T).T[:, :2]; nl = [int(((np.abs(SP[:, 0] - b[0]) <= 0.025) & (np.abs(SP[:, 1] - b[1]) <= 0.025)).sum()) for b in BOX]
    lc = last(loc, t); Pl = w2(np.linalg.inv(Mmo), BOX); li = ((Pl[:, 1] - lc[2]) / lc[3]).astype(int); lj = ((Pl[:, 0] - lc[1]) / lc[3]).astype(int); inw = (li >= 0) & (li < lc[4].shape[0]) & (lj >= 0) & (lj < lc[4].shape[1])
    lt = ''.join('#' if lc[4][a, b] >= 100 else ('+' if lc[4][a, b] == 99 else '.') for a, b in zip(li, lj)) if inw.all() else '창 밖'
    dM = np.linalg.inv(MmoS) @ Mmo; sh = (dM @ np.r_[BOX.mean(0), 0, 1])[:2] - BOX.mean(0)
    print('%s  %.2f m  %+4.0f°   %s      %s        %s       %+.1f, %+.1f cm · %+.1f°' % (time.strftime('%H:%M:%S', time.localtime(t)), np.hypot(*bb), math.degrees(math.atan2(bb[1], bb[0])), ' '.join(nv), ' '.join('%2d' % n for n in nl), lt, sh[0] * 100, sh[1] * 100, math.degrees(yaw(dM))))
