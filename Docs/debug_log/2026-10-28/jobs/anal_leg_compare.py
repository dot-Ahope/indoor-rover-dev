#!/usr/bin/env python3
"""anal_leg_compare — 같은 구간(통로 북쪽 → 위 복도/C)을 place_server 주행(bag)과 no5 러너 주행(job550 csv)에서 비교 (2026-10-28 §12, PC).
  둘 다 10 Hz 로 맞춘 map 자세 · 지령(v, ω)으로: 소요 · 이동 거리 · 국면별 시간(전진 |v|≥0.02 · 제자리 회전 |v|<0.02 & |ω|≥0.05 · 정지 그 밖)
  · 목표까지 거리가 0.30 / 0.15 m 안에 처음 든 시각 · 그 뒤 남은 시간 · 2 s 마다 자세 · 목표 거리 · 지령.
  인자: --bag 폴더 시작HH:MM:SS.fff 끝HH:MM:SS.fff gx gy 이름   (map 자세 = /tf map→odom × odom→base_link, 지령 = /cmd_vel)
        --csv 파일 목표번호 gx gy 이름                          (job550 csv: t, goal, map_x, map_y, map_yaw, ..., v, w)
  여러 개를 이어 줄 수 있다."""
import sys, math, time, csv
import numpy as np
from pathlib import Path


def summarize(name, T, X, Y, A, V, W, gx, gy):
    T = np.asarray(T) - T[0]; X, Y, A, V, W = map(np.asarray, (X, Y, A, V, W))
    dt = np.diff(T, append=T[-1]); d = np.hypot(gx - X, gy - Y)
    mv = np.abs(V) >= 0.02; rot = (~mv) & (np.abs(W) >= 0.05); st = ~(mv | rot)
    L = float(np.sum(np.hypot(np.diff(X), np.diff(Y))))
    def first(r):
        k = np.nonzero(d <= r)[0]; return (T[k[0]], T[-1] - T[k[0]]) if len(k) else (None, None)
    f30, f15 = first(0.30), first(0.15)
    print('\n== %s : 소요 %.1f s · 이동 %.2f m · 출발 (%.2f, %.2f, %.0f°) → 끝 (%.2f, %.2f, %.0f°) · 목표 (%.2f, %.2f) 끝 거리 %.3f m' % (
        name, T[-1], L, X[0], Y[0], math.degrees(A[0]), X[-1], Y[-1], math.degrees(A[-1]), gx, gy, d[-1]))
    print('   국면: 전진 %.1f s · 제자리 회전 %.1f s · 정지 %.1f s | 평균 전진 속도 %.3f m/s' % (dt[mv].sum(), dt[rot].sum(), dt[st].sum(), L / max(dt[mv].sum(), 1e-3)))
    print('   목표 0.30 m 안 처음 %s s(남은 %s s) · 0.15 m 안 처음 %s s(남은 %s s)' % tuple('%.1f' % v if v is not None else '—' for v in (*f30, *f15)))
    print('   t s | map x, y, yaw | 목표까지 | v, ω')
    nxt = 0.0
    for i in range(len(T)):
        if T[i] >= nxt:
            print('   %5.1f | %+.2f, %+.2f, %+4.0f° | %.2f | %+.3f, %+.3f' % (T[i], X[i], Y[i], math.degrees(A[i]), d[i], V[i], W[i])); nxt += 2.0


def from_bag(folder, s0, s1, gx, gy, name):
    from rosbags.highlevel import AnyReader
    from rosbags.typesys import Stores, get_typestore
    yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
    with AnyReader([Path(folder)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        day = time.strftime('%Y-%m-%d', time.localtime(rd.start_time * 1e-9))
        T = lambda s: time.mktime(time.strptime(day + ' ' + s[:8], '%Y-%m-%d %H:%M:%S')) + float(s[8:] or 0)
        t0, t1 = T(s0), T(s1); mo, ob, cv = [], [], []
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/cmd_vel')]):
            ts = t * 1e-9
            if not t0 - 2 <= ts <= t1: continue
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/cmd_vel': cv.append((ts, m.linear.x, m.angular.z)); continue
            for tr in m.transforms:
                p = (ts, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(p)
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(p)
    last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
    R = []
    for t in np.arange(t0, t1, 0.1):
        _, mx, my, ma = last(mo, t); _, ox, oy, oa = last(ob, t); c, s = math.cos(ma), math.sin(ma)
        k = last(cv, t); v, w = (k[1], k[2]) if t - k[0] < 0.6 else (0.0, 0.0)   # 지령이 0.6 s 넘게 없으면 0(컨트롤러 멈춤)
        R.append((t, mx + c * ox - s * oy, my + s * ox + c * oy, math.atan2(math.sin(ma + oa), math.cos(ma + oa)), v, w))
    summarize(name, *zip(*R), gx, gy)


def from_csv(path, goal, gx, gy, name):
    R = [r for r in csv.DictReader(open(path)) if int(r['goal']) == goal]
    summarize(name, [float(r['t']) for r in R], [float(r['map_x']) for r in R], [float(r['map_y']) for r in R],
              [math.radians(float(r['map_yaw'])) for r in R], [float(r['v']) for r in R], [float(r['w']) for r in R], gx, gy)


a = sys.argv[1:]
while a:
    if a[0] == '--bag': from_bag(a[1], a[2], a[3], float(a[4]), float(a[5]), a[6]); a = a[7:]
    elif a[0] == '--csv': from_csv(a[1], int(a[2]), float(a[3]), float(a[4]), a[5]); a = a[6:]
    else: sys.exit('인자: --bag ... | --csv ...')
