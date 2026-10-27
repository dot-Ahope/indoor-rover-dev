#!/usr/bin/env python3
"""chk_gcm_rot — §15 틀어진 코스트맵 프레임이 정상 프레임을 얼마나 돌리고 옮긴 것인가 (2026-10-27, PC).
  전역 · 로컬 각 메시지: 로버 3 m 안 치명 칸을 직전 메시지 기준으로 회전(로버 중심, ±40° 0.5°) + 이동(±0.3 m) 탐색 → 겹침 최대 값.
  로컬은 odom 프레임 그대로 비교(TF 안 씀). 인자: bag폴더 시작HH:MM:SS 끝HH:MM:SS"""
import sys, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = Path(sys.argv[1])
t0 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[2], '%Y-%m-%d %H:%M:%S')); t1 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[3], '%Y-%m-%d %H:%M:%S'))
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
M = {'g': [], 'l': []}; mo, ob = [], []
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/local_costmap/costmap', '/tf')]):
        ts = t * 1e-9
        if ts < t0 - 3 or ts > t1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (ts, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(v)
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(v)
            continue
        i = m.info; g = np.array(m.data, np.int16).reshape(i.height, i.width); J, I = np.nonzero(g == 100)
        M[c.topic[1]].append((ts, np.c_[i.origin.position.x + (I + .5) * i.resolution, i.origin.position.y + (J + .5) * i.resolution], m.header.frame_id))
near = lambda L, t: min(L, key=lambda x: abs(x[0] - t))
def key(P): return set(map(tuple, np.round(P / 0.05).astype(int)))
def search(A, B, c):
    ka = key(A); best = (len(ka & key(B)), 0.0, 0.0, 0.0)
    for deg in np.arange(-40, 40.5, 0.5):
        a = math.radians(deg); X = B - c; R = np.c_[math.cos(a) * X[:, 0] - math.sin(a) * X[:, 1], math.sin(a) * X[:, 0] + math.cos(a) * X[:, 1]] + c
        for dx in np.arange(-0.3, 0.31, 0.05):
            for dy in np.arange(-0.3, 0.31, 0.05):
                n = len(ka & key(R + [dx, dy]))
                if n > best[0]: best = (n, deg, dx, dy)
    return best
for k in ('g', 'l'):
    print('== %s (%s) — 로버 3 m 안 치명 칸 · 직전과 그대로 겹침 · 최적(겹침, 회전°, 이동 m)' % ('전역' if k == 'g' else '로컬', M[k][0][2] if M[k] else '-'))
    for j in range(1, len(M[k])):
        ts, P, fr = M[k][j]
        if ts < t0: continue
        o = near(ob, ts); m_ = near(mo, ts)
        if fr == 'map':
            c_, s_ = math.cos(m_[3]), math.sin(m_[3]); cx, cy = m_[1] + c_ * o[1] - s_ * o[2], m_[2] + s_ * o[1] + c_ * o[2]
        else: cx, cy = o[1], o[2]
        c = np.array([cx, cy]); sel = lambda Q: Q[np.hypot(Q[:, 0] - cx, Q[:, 1] - cy) < 3.0]
        A, B = sel(M[k][j - 1][1]), sel(P); n0 = len(key(A) & key(B))
        if k == 'l' and j % 3: continue   # 로컬은 10 Hz → 0.3 s 간격만
        bst = search(A, B, c) if n0 < 0.9 * min(len(A), len(B)) else (n0, 0, 0, 0)
        print('%s 칸 %d(직전 %d) · 그대로 %d · 최적 %d %+.1f° (%+.2f, %+.2f)' % (hs(ts), len(B), len(A), n0, bst[0], bst[1], bst[2], bst[3]))
