#!/usr/bin/env python3
"""fig_box_end_plans — 복귀 길 상자 끝(출발점 동쪽)에서 계획기 경로가 '곧게' 나온 주행과 '상자 끝을 감아 돌게' 나온 주행을 나란히. (2026-10-14 §24, 오늘만)
  왜: §22 — 같은 자리(map x ≈ 1.36)를 지날 때 B 는 경로가 상자 쪽으로 꺾여(−151°) 후보 전부 충돌로 멈췄고, A · A2 는 곧은 경로(+171 ~ −177°)로 통과.
      계획기(NavFn)가 보는 전역 코스트맵과 그 경로를 같은 화면에 두고 무엇이 다른지 본다.
  그림(판마다): 바탕 = 전역 코스트맵(검정 100 치명 · 진회색 99 내접 · 회색 감쇠), 빨간 점 = 그 순간 로컬 코스트맵 치명 칸(지도 좌표로 옮김),
        파란 점 = 라이다(지도 좌표), 보라 선 = /plan(그 시각 직후 첫 경로), 초록 = 차체(패딩 포함) 외곽, 회색 별 = 목표 (0, 0).
  인자: 출력.png 이름=bag@HH:MM:SS.f ..."""
import sys, time, math
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
out = sys.argv[1]; specs = sys.argv[2:]
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
XF, XR, HW = 0.272, -0.258, 0.175
def tomap(x, y, T): c, s = math.cos(T[2]), math.sin(T[2]); return T[0] + c * x - s * y, T[1] + s * x + c * y
fig, axs = plt.subplots(1, len(specs), figsize=(5.2 * len(specs), 5.6))
cm = ListedColormap(['#ffffff', '#e4e7ea', '#b9c0c6', '#8a949c', '#4a5258', '#111111']); nm_ = BoundaryNorm([-0.5, 0.5, 40, 70, 98.5, 99.5, 101], cm.N)
for ax, sp in zip(np.atleast_1d(axs), specs):
    name, rest = sp.split('='); bag, hh = rest.split('@'); hms, _, fr = hh.partition('.')
    mo = ob = None; lid = None; gc = lc = scan = None; plan = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        day = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/global_costmap/costmap', '/local_costmap/costmap', '/scan', '/plan')]):
            ts = t / 1e9
            if day is None: day = time.strftime('%Y-%m-%d ', time.localtime(ts)); T = time.mktime(time.strptime(day + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/plan':
                if ts >= T - 0.05: plan = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]); break
                continue
            if ts > T + 0.05: continue
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                    elif tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                    elif tr.child_frame_id == 'lidar_link':
                        q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
            elif c.topic == '/global_costmap/costmap': gc = m
            elif c.topic == '/local_costmap/costmap': lc = m
            else: scan = m
    g = np.array(gc.data, np.int16).reshape(gc.info.height, gc.info.width); r = gc.info.resolution; ox, oy = gc.info.origin.position.x, gc.info.origin.position.y
    ax.imshow(np.where(g < 0, 0, g), origin='lower', extent=(ox, ox + g.shape[1] * r, oy, oy + g.shape[0] * r), cmap=cm, norm=nm_, interpolation='nearest')
    a = np.array(lc.data, np.int16).reshape(lc.info.height, lc.info.width); iy, ix = np.nonzero(a >= 100)
    lx, ly = tomap(lc.info.origin.position.x + (ix + 0.5) * lc.info.resolution, lc.info.origin.position.y + (iy + 0.5) * lc.info.resolution, mo)
    ax.scatter(lx, ly, s=9, marker='s', color='#d64545', alpha=0.55, lw=0, label='로컬 치명 칸')
    rr = np.array(scan.ranges); an = scan.angle_min + np.arange(len(rr)) * scan.angle_increment; ok = np.isfinite(rr) & (rr > scan.range_min) & (rr < scan.range_max)
    px, py = rr[ok] * np.cos(an[ok]), rr[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
    bx, by = tomap(bx, by, ob); mx, my = tomap(bx, by, mo); ax.scatter(mx, my, s=4, color='#2b6cb0', lw=0, label='라이다')
    rx, ry = tomap(ob[0], ob[1], mo); ryaw = ob[2] + mo[2]; c_, s_ = math.cos(ryaw), math.sin(ryaw)
    fp = np.array([[XF, HW], [XF, -HW], [XR, -HW], [XR, HW], [XF, HW]]); ax.plot(rx + c_ * fp[:, 0] - s_ * fp[:, 1], ry + s_ * fp[:, 0] + c_ * fp[:, 1], color='#2f855a', lw=1.8, label='차체(패딩 포함)')
    ax.plot(plan[:, 0], plan[:, 1], color='#7b3294', lw=2, label='계획기 경로')
    acc = np.r_[0, np.cumsum(np.hypot(*np.diff(plan, axis=0).T))]; k = min(int(np.searchsorted(acc, 0.3)), len(plan) - 1)
    d = math.degrees(math.atan2(plan[k, 1] - plan[0, 1], plan[k, 0] - plan[0, 0]))
    ax.plot([0], [0], marker='*', color='#555', ms=12)
    ax.set_xlim(0.55, 2.05); ax.set_ylim(-0.75, 0.75); ax.set_aspect('equal'); ax.grid(color='#9aa5ae', lw=0.3, alpha=0.5)
    ax.set_title('%s  %s\n로버 (%.2f, %.2f) %+.0f° · 경로 0.3 m 앞 %+.0f°' % (name, hh, rx, ry, math.degrees(math.atan2(s_, c_)), d), fontsize=10, loc='left')
    ax.set_xlabel('map x (m)')
np.atleast_1d(axs)[0].set_ylabel('map y (m)'); np.atleast_1d(axs)[0].legend(loc='lower left', fontsize=8)
fig.suptitle('복귀 길 상자 끝 — 바탕 = 전역 코스트맵(계획기가 보는 지도), 보라 = 그 순간 계획기 경로', fontsize=11, x=0.01, ha='left')
fig.tight_layout(); fig.savefig(out, dpi=130); print('저장', out)
