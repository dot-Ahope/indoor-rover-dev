#!/usr/bin/env python3
"""anal_stops — 주행 중 '멈춤' 구간 찾기: EKF 속도(|v| < 0.01 m/s 이고 |ω| < 0.05 rad/s)가 1 s 넘게 이어진 구간. (2026-10-21 §11, PC)
  구간마다: 시각(시계 · bag 기준 t), 위치, 그동안 /cmd_vel(명령이 0 이었나 · 회전만 했나), 앞쪽 라이다 최소 거리(차체 앞 ±30°),
  /rover/stuck 메시지, nav2 사건(PathBlockedAhead · Optimizer fail · 계획 실패 — 별도 파일, '시각 메시지' 줄)을 붙인다.
  인자: bag [nav2사건파일]"""
import sys, math, bisect, datetime
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import os
MIN_STOP = float(os.environ.get("MIN_STOP", "1.0"))   # 멈춤으로 셀 최소 길이(s)
bag = sys.argv[1]; evf = sys.argv[2] if len(sys.argv) > 2 else None
OD, CV, SC, STK = [], [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/odometry/filtered', '/cmd_vel', '/scan', '/rover/stuck')]):
        m = rd.deserialize(raw, c.msgtype); tt = t * 1e-9
        if c.topic == '/odometry/filtered': OD.append((tt, m.twist.twist.linear.x, m.twist.twist.angular.z, m.pose.pose.position.x, m.pose.pose.position.y))
        elif c.topic == '/cmd_vel': CV.append((tt, m.linear.x, m.angular.z))
        elif c.topic == '/scan':
            rg = np.array(m.ranges); an = m.angle_min + m.angle_increment * np.arange(len(rg))
            an = np.angle(np.exp(1j * (an + math.pi)))   # 라이다가 뒤집혀 달림(yaw π) → 차체 앞 = 라이다 π 근처
            k = (np.abs(an) < math.radians(30)) & np.isfinite(rg) & (rg > 0.05)
            SC.append((tt, float(rg[k].min()) if k.any() else float('nan')))
        else: STK.append((tt, str(getattr(m, 'data', m))))
OD = np.array(OD); CV = np.array(CV); t0 = OD[0, 0]
hm = lambda t: datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S')
mv = (np.abs(OD[:, 1]) >= 0.01) | (np.abs(OD[:, 2]) >= 0.05)
# 주행 구간 = 처음 움직인 때 ~ 마지막 움직인 때
i0, i1 = np.nonzero(mv)[0][[0, -1]]
EV = []
if evf:
    for l in open(evf, encoding='utf-8', errors='replace'):
        p = l.strip().split(' ', 1)
        if len(p) == 2 and p[0].count(':') == 2: EV.append((p[0], p[1]))
stops, k = [], i0
while k <= i1:
    if not mv[k]:
        j = k
        while j <= i1 and not mv[j]: j += 1
        if OD[j - 1, 0] - OD[k, 0] >= MIN_STOP: stops.append((k, j - 1))
        k = j
    else: k += 1
tot = OD[i1, 0] - OD[i0, 0]
print('주행 %s ~ %s (%.1f s) · 멈춤(%.1f s 넘게 정지) %d 번 · 합 %.1f s' % (hm(OD[i0, 0]), hm(OD[i1, 0]), tot, MIN_STOP, len(stops), sum(OD[b, 0] - OD[a, 0] for a, b in stops)))
for a, b in stops:
    ta, tb = OD[a, 0], OD[b, 0]
    c = CV[(CV[:, 0] >= ta) & (CV[:, 0] <= tb)]
    cz = (np.abs(c[:, 1]) < 0.005) & (np.abs(c[:, 2]) < 0.02) if len(c) else np.array([])
    sc = [s for t, s in SC if ta <= t <= tb]
    ev = [e for e in EV if hm(ta - 2) <= e[0] <= hm(tb)]
    print('\n%s~%s (t %.1f~%.1f, %.1f s) @ (%.2f, %.2f) | cmd_vel %d 개 중 0 명령 %d · 최대 |v| %.3f · 최대 |ω| %.2f | 앞 ±30° 라이다 최소 %.2f m'
          % (hm(ta), hm(tb), ta - t0, tb - t0, tb - ta, OD[a, 3], OD[a, 4], len(c), int(cz.sum()) if len(c) else 0,
             np.abs(c[:, 1]).max() if len(c) else 0, np.abs(c[:, 2]).max() if len(c) else 0, np.nanmin(sc) if sc else float('nan')))
    for s in [s for t, s in STK if ta - 2 <= t <= tb]: print('   stuck:', s[:120])
    for e in ev[:8]: print('   ', e[0], e[1][:150])
FIG = os.environ.get('FIG')
if FIG:   # 속도 · 명령 시간축 그림: 멈춤 구간 회색, cmd_vel 공백(> 0.3 s) 주황 눈금, nav2 사건 세로선
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
    fg, ax = plt.subplots(3, 1, figsize=(12, 7.5), sharex=True)
    ax[0].plot(OD[:, 0] - t0, OD[:, 1], lw=1, label='EKF 전진 속도'); ax[0].step(CV[:, 0] - t0, CV[:, 1], where='post', lw=1, label='/cmd_vel 전진 명령')
    ax[1].plot(OD[:, 0] - t0, OD[:, 2], lw=1, label='EKF 회전 속도'); ax[1].step(CV[:, 0] - t0, CV[:, 2], where='post', lw=1, label='/cmd_vel 회전 명령')
    g = np.diff(CV[:, 0]); gi = np.nonzero(g > 0.3)[0]
    ax[2].vlines(CV[gi, 0] - t0, 0, g[gi], color='#d9822b', lw=2, label='/cmd_vel 공백 길이(> 0.3 s)')
    st = np.array([t for t, s in SC]) - t0; ax[2].plot(st, [s for t, s in SC], lw=0.8, color='#4a6fa5', label='앞 ±30° 라이다 최소(m)')
    ax[2].set_ylim(0, 3)
    for a in ax:
        for p, q in stops: a.axvspan(OD[p, 0] - t0, OD[q, 0] - t0, color='#cccccc', alpha=0.6)
        a.grid(alpha=0.3); a.legend(fontsize=8, loc='upper right')
    base = datetime.datetime.fromtimestamp(t0)
    for hh, msg in EV:
        tt = (datetime.datetime.combine(base.date(), datetime.datetime.strptime(hh, '%H:%M:%S').time()) - base).total_seconds()
        col = '#c0392b' if ('Aborting' in msg or 'fail' in msg) else ('#8e44ad' if 'PathBlocked' in msg else None)
        if col: ax[2].axvline(tt, color=col, lw=0.8, alpha=0.7)
    ax[0].set_ylabel('m/s'); ax[1].set_ylabel('rad/s'); ax[2].set_ylabel('s · m'); ax[2].set_xlabel('t (s, bag 시작 기준) — 회색 = 멈춤, 빨간 선 = 컨트롤러 중단/실패, 보라 선 = PathBlockedAhead')
    ax[0].set_title('복귀 주행 속도와 명령'); fg.tight_layout(); fg.savefig(FIG, dpi=110); print('그림', FIG)
