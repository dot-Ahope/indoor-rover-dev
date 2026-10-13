#!/usr/bin/env python3
"""anal_odom_drift — 구간마다 '어느 오도메트리 재료가 SLAM 과 얼마나 어긋났나'를 견준다. (2026-10-13)
  왜: 기억된 상자가 오도메트리 어긋남 4~5 cm 만큼 밀려 보였다(§6.2). EKF 가 미끄러짐(vx·vy)을 지금 보고 있는지, rf2o 를 쓰면/안 쓰면 얼마나 다른지 확인.
  방법: 구간의 시작 자세를 기준으로 끝까지의 이동(시작 차체 좌표 x 앞 · y 왼쪽)을 아래 재료로 각각 구하고 SLAM(map→base) 이동과의 차를 낸다.
        · EKF        : odom→base TF(지금 주행에 실제로 쓰인 것)
        · 휠만       : /wheel_odom 의 vx 를 EKF yaw 로 적분(옆 이동 0 가정 = rf2o 없는 구성에 가까움)
        · rf2o(게이트): /odom_rf2o/gated 의 vx·vy 를 EKF yaw 로 적분(게이트가 거부한 순간은 휠 vx 로 메움)
        · 휠 vx+rf2o vy: 앞은 휠, 옆은 rf2o 게이트 출력 — 'rf2o 를 옆 이동에만 쓰면'의 가정 평가
        (/odom_rf2o 원본은 라이다 좌표의 속도라 차체 좌표로 그냥 적분하면 안 된다 — 첫 판에서 3 m 씩 어긋나 뺐다.)
        yaw 는 모두 EKF(자이로) 것을 쓴다 — 병진 재료만 비교하려는 것. SLAM 은 참값이 아니라 기준이다(스캔 정합 오차 수 cm).
  구간: --win 길이(s, 기본 25) 를 --hop(기본 10) 씩 밀며 SLAM 이동 0.5 m 이상인 것 전부 + 지정 구간(이름@HH:MM:SS~HH:MM:SS).
  사용: anal_odom_drift.py bag [--win 25 --hop 10] [이름@HH:MM:SS~HH:MM:SS ...]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
args = sys.argv[1:]; bag = args.pop(0); WIN, HOP = 25.0, 10.0; named = []
while args:
    a = args.pop(0)
    if a == '--win': WIN = float(args.pop(0))
    elif a == '--hop': HOP = float(args.pop(0))
    else: named.append(a)
yawq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
ob = []; mo = []; tw = {'/wheel_odom': [], '/odom_rf2o': [], '/odom_rf2o/gated': []}
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in tw or c.topic == '/tf']):
        ts = t / 1e9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (ts, tr.transform.translation.x, tr.transform.translation.y, yawq(tr.transform.rotation))
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append(v)
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append(v)
        else: tw[c.topic].append((ts, m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z))
ob = np.array(ob); mo = np.array(mo); TW = {k: np.array(v) for k, v in tw.items()}
day = time.strftime('%Y-%m-%d ', time.localtime(ob[0, 0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S'))
def at(A, t): return A[min(np.searchsorted(A[:, 0], t), len(A) - 1)]
def mapbase(t):
    o = at(ob, t); m = at(mo, t); c, s = math.cos(m[3]), math.sin(m[3]); return np.array([m[1] + c * o[1] - s * o[2], m[2] + s * o[1] + c * o[2], m[3] + o[3]])
def body(d, yaw0): c, s = math.cos(yaw0), math.sin(yaw0); return np.array([c * d[0] + s * d[1], -s * d[0] + c * d[1]])
def integ(A, t0, t1, fill=None):   # 차체 속도(vx, vy)를 EKF yaw 로 적분 → odom 좌표 이동. fill = 빈 구간(0.25 s 넘게 표본 없음)을 메울 휠 배열
    T = np.arange(t0, t1, 0.02); out = np.zeros(2); k = np.clip(np.searchsorted(A[:, 0], T) - 1, 0, len(A) - 1); age = T - A[k, 0]; yaw = ob[np.clip(np.searchsorted(ob[:, 0], T), 0, len(ob) - 1), 3]
    vx = A[k, 1].copy(); vy = A[k, 2].copy()
    if fill is not None:
        kf = np.clip(np.searchsorted(fill[:, 0], T) - 1, 0, len(fill) - 1); old = age > 0.25; vx[old] = fill[kf[old], 1]; vy[old] = 0.0
    out[0] = np.sum(vx * np.cos(yaw) - vy * np.sin(yaw)) * 0.02; out[1] = np.sum(vx * np.sin(yaw) + vy * np.cos(yaw)) * 0.02; return out
def seg(t0, t1):
    o0, o1 = at(ob, t0), at(ob, t1); s0, s1 = mapbase(t0), mapbase(t1)
    slam = body(s1[:2] - s0[:2], s0[2]); ekf = body(o1[1:3] - o0[1:3], o0[3]); R = {'EKF': ekf - slam}
    R['휠만'] = body(integ(TW['/wheel_odom'], t0, t1), o0[3]) - slam
    R['rf2o게이트'] = body(integ(TW['/odom_rf2o/gated'], t0, t1, TW['/wheel_odom']), o0[3]) - slam
    G = TW['/odom_rf2o/gated']; Wh = TW['/wheel_odom']; H = G.copy(); H[:, 1] = Wh[np.clip(np.searchsorted(Wh[:, 0], G[:, 0]) - 1, 0, len(Wh) - 1), 1]
    R['휠vx+rf2o vy'] = body(integ(H, t0, t1, Wh), o0[3]) - slam
    nr = ((TW['/odom_rf2o'][:, 0] >= t0) & (TW['/odom_rf2o'][:, 0] < t1)).sum(); ng = ((TW['/odom_rf2o/gated'][:, 0] >= t0) & (TW['/odom_rf2o/gated'][:, 0] < t1)).sum()
    turn = abs(math.degrees(((o1[3] - o0[3] + math.pi) % (2 * math.pi)) - math.pi)); dyaw = math.degrees((((s1[2] - s0[2]) - (o1[3] - o0[3]) + math.pi) % (2 * math.pi)) - math.pi)
    return slam, R, nr, ng, turn, dyaw
K = ['EKF', '휠만', 'rf2o게이트', '휠vx+rf2o vy']
print('구간(시각)              SLAM 이동(앞, 옆 m)  회전    | SLAM 대비 차 (앞, 옆 cm): EKF · 휠만 · rf2o 게이트 · 휠 vx+rf2o vy | 게이트 통과 | yaw 차(SLAM−EKF)')
def show(nm, t0, t1):
    slam, R, nr, ng, turn, dyaw = seg(t0, t1)
    print('%-22s (%+.2f, %+.2f)   %4.0f°  | %s | %3d / %3d | %+.1f°' % (nm, slam[0], slam[1], turn, ' · '.join('(%+5.1f, %+5.1f)' % tuple(R[k] * 100) for k in K), ng, nr, dyaw)); return slam, R, turn
for a in named:
    nm, r = a.split('@'); h0, h1 = r.split('~'); show(nm + ' ' + r, ep(h0), ep(h1))
E = {k: [] for k in K}; ET = {k: [] for k in K}; n = 0
t = max(ob[0, 0], mo[0, 0], TW['/odom_rf2o'][0, 0]) + 2
while t + WIN < min(ob[-1, 0], mo[-1, 0]) - 1:
    slam, R, nr, ng, turn, dyaw = seg(t, t + WIN)
    if np.hypot(*slam) >= 0.5:
        n += 1
        for k in K: E[k].append(np.hypot(*R[k])); (ET[k].append(np.hypot(*R[k])) if turn >= 45 else None)
    t += HOP
print('\n미끄럼 창 %.0f s × %d 개(SLAM 이동 0.5 m 이상) — SLAM 대비 차의 크기(cm): 중앙 / 90 %% / 최대' % (WIN, n))
for k in K: print('  %-13s 전체 %4.1f / %4.1f / %4.1f   |  45° 넘게 돈 창 %d 개: %4.1f / %4.1f' % ((k, np.median(E[k]) * 100, np.percentile(E[k], 90) * 100, max(E[k]) * 100, len(ET[k])) + ((np.median(ET[k]) * 100, max(ET[k]) * 100) if ET[k] else (float('nan'), float('nan')))))
