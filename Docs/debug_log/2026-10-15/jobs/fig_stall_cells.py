#!/usr/bin/env python3
"""fig_stall_cells — 서쪽 통로 남쪽 정지 자리: 멈추기 전 · 멈춘 순간 · 복귀 출발의 로컬 치명 칸(라이다 확인 / 카메라만)과 차체, 그리고 차체 옆 여유의 시간 변화. (2026-10-15 §6, 오늘만)
  위 3 판(지도 좌표, 1.3 × 1.3 m 확대): 파랑 네모 = 라이다 점이 3.5 cm 안에 있는 치명 칸, 주황 네모 = 라이다 점 없는 치명 칸(카메라 · nvblox 만),
        회색 점 = 라이다, 초록 = 차체(패딩 포함), 노랑 부채꼴 = 카메라 시야(±43°, 1.4 m), 빨간 선 = 차체에서 가장 가까운 치명 칸까지(값 cm).
  아래 그래프: 로컬 코스트맵 프레임마다 차체 → 가장 가까운 치명 칸 거리(검정) · 카메라만 본 칸 중 가장 가까운 것(주황) · 차체 8 cm 안 카메라 칸 수(막대).
        회색 띠 = Nav2 '후보 전부 충돌' 기록 시각, 점선 = 4.4 cm(09-23 에 5 cm 칸 검사가 닿음으로 판정한 여유).
  인자: 출력.png bag_f2v1 bag_f2v1r"""
import sys, time, math
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Rectangle
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
out, bagA, bagB = sys.argv[1:4]
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
XF, XR, HW = 0.272, -0.258, 0.175; CAMX = 0.234; HFOV = math.radians(43); CAMR = 1.4
tm = lambda x, y, P: (P[0] + math.cos(P[2]) * x - math.sin(P[2]) * y, P[1] + math.sin(P[2]) * x + math.cos(P[2]) * y)
FAILS = ['10:15:54.3', '10:15:54.5', '10:15:59.7', '10:15:59.9', '10:16:00.3', '10:16:00.5', '10:16:05.7']   # outputs/navlog_f2v1.txt

def frames(bag, h0, h1):
    """로컬 코스트맵 프레임마다: 시각, 로버(map), map 좌표 치명 칸, 칸별 라이다 확인 여부"""
    ob = mo = lid = None; sc = None; out_ = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/scan')]):
            m = rd.deserialize(raw, c.msgtype); ts = t / 1e9
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                    elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                    elif tr.child_frame_id == 'lidar_link':
                        q = tr.transform.rotation; lid = (v[0], v[1], np.array([[1 - 2 * (q.y * q.y + q.z * q.z), 2 * (q.x * q.y - q.z * q.w)], [2 * (q.x * q.y + q.z * q.w), 1 - 2 * (q.x * q.x + q.z * q.z)]]))
                continue
            if c.topic == '/scan': sc = m; continue
            h = time.strftime('%H:%M:%S', time.localtime(ts))
            if not (h0 <= h <= h1) or ob is None or mo is None or sc is None: continue
            a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
            cx, cy = tm(m.info.origin.position.x + (ix + 0.5) * m.info.resolution, m.info.origin.position.y + (iy + 0.5) * m.info.resolution, mo)
            r = np.array(sc.ranges); an = sc.angle_min + np.arange(len(r)) * sc.angle_increment; ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
            px, py = r[ok] * np.cos(an[ok]), r[ok] * np.sin(an[ok]); bx = lid[0] + lid[2][0, 0] * px + lid[2][0, 1] * py; by = lid[1] + lid[2][1, 0] * px + lid[2][1, 1] * py
            lx, ly = tm(*tm(bx, by, ob), mo)
            near = (np.abs(lx[:, None] - cx[None, :]) < 0.035) & (np.abs(ly[:, None] - cy[None, :]) < 0.035)
            seen = near.any(axis=0)
            rx, ry = tm(ob[0], ob[1], mo); ryaw = ob[2] + mo[2]
            out_.append((ts, (rx, ry, ryaw), cx, cy, seen, lx, ly))
    return out_

def dist_body(P, cx, cy):
    c_, s_ = math.cos(P[2]), math.sin(P[2]); bx = c_ * (cx - P[0]) + s_ * (cy - P[1]); by = -s_ * (cx - P[0]) + c_ * (cy - P[1])
    inside = (bx >= XR) & (bx <= XF) & (np.abs(by) <= HW)
    d = np.hypot(np.maximum(np.maximum(XR - bx, bx - XF), 0), np.maximum(np.abs(by) - HW, 0)); return np.where(inside, 0, d)

A = frames(bagA, '10:15:30', '10:16:08'); B = frames(bagB, '10:25:14', '10:25:24')
day = time.strftime('%Y-%m-%d ', time.localtime(A[0][0])); ep = lambda s: time.mktime(time.strptime(day + s[:8], '%Y-%m-%d %H:%M:%S')) + float('0' + s[8:])
pick = lambda F, s: min(F, key=lambda f: abs(f[0] - ep(s)))
snaps = [('멈추기 14 s 전', pick(A, '10:15:40.0')), ('멈춘 순간(첫 실패)', pick(A, '10:15:54.2')), ('9 분 뒤 복귀 출발', pick(B, '10:25:20.0'))]
fig = plt.figure(figsize=(15, 10.2)); gs = fig.add_gridspec(2, 3, height_ratios=[1.35, 1], hspace=0.34, wspace=0.14)
cx0, cy0 = snaps[1][1][1][0], snaps[1][1][1][1]
for i, (title, f) in enumerate(snaps):
    ax = fig.add_subplot(gs[0, i]); ts, P, cx, cy, seen, lx, ly = f
    W = 0.65; ax.set_xlim(cx0 - W, cx0 + W); ax.set_ylim(cy0 - W, cy0 + W); ax.set_aspect('equal')
    ax.set_facecolor('#f7f8fa'); ax.grid(color='#c9d1d9', lw=0.4)
    for x, y, s in zip(cx, cy, seen):
        ax.add_patch(Rectangle((x - 0.025, y - 0.025), 0.05, 0.05, fc='#2b6cb0' if s else '#e07b24', ec='white', lw=0.5, alpha=0.9))
    ax.scatter(lx, ly, s=3, color='#555', zorder=3)
    c_, s_ = math.cos(P[2]), math.sin(P[2]); fp = np.array([[XF, HW], [XF, -HW], [XR, -HW], [XR, HW], [XF, HW]])
    ax.plot(P[0] + c_ * fp[:, 0] - s_ * fp[:, 1], P[1] + s_ * fp[:, 0] + c_ * fp[:, 1], color='#2f855a', lw=2.2, zorder=4)
    ax.annotate('', xy=(P[0] + 0.22 * c_, P[1] + 0.22 * s_), xytext=(P[0], P[1]), arrowprops=dict(arrowstyle='->', color='#2f855a', lw=1.8), zorder=4)
    camx, camy = P[0] + CAMX * c_, P[1] + CAMX * s_
    ax.add_patch(Wedge((camx, camy), CAMR, math.degrees(P[2] - HFOV), math.degrees(P[2] + HFOV), fc='#f6e05e', ec='none', alpha=0.18, zorder=1))
    d = dist_body(P, cx, cy); k = int(np.argmin(d))
    # 가장 가까운 칸까지 선(차체 위 가장 가까운 점 → 칸 중심)
    bx = c_ * (cx[k] - P[0]) + s_ * (cy[k] - P[1]); by = -s_ * (cx[k] - P[0]) + c_ * (cy[k] - P[1]); qx, qy = np.clip(bx, XR, XF), np.clip(by, -HW, HW)
    ax.plot([P[0] + c_ * qx - s_ * qy, cx[k]], [P[1] + s_ * qx + c_ * qy, cy[k]], color='#c53030', lw=2, zorder=5)
    ncam = int(((d <= 0.08) & ~seen).sum())
    ax.set_title('%s  %s\n최근접 치명 칸 %.1f cm(%s)\n차체 8 cm 안 카메라 칸 %d 개' % (title, time.strftime('%H:%M:%S', time.localtime(ts)), 100 * d[k], '카메라만' if not seen[k] else '라이다 확인', ncam), fontsize=10, loc='left')
    ax.set_xlabel('map x (m)')
    if i == 0: ax.set_ylabel('map y (m)')
    if i == 1: ax.text(cx[k] + 0.03, cy[k] + 0.05, '%.1f cm' % (100 * d[k]), color='#c53030', fontsize=10, fontweight='bold', zorder=6)
from matplotlib.lines import Line2D
fig.legend(handles=[Rectangle((0, 0), 1, 1, fc='#2b6cb0'), Rectangle((0, 0), 1, 1, fc='#e07b24'), Line2D([], [], marker='o', ls='', color='#555', ms=3), Line2D([], [], color='#2f855a', lw=2), Rectangle((0, 0), 1, 1, fc='#f6e05e', alpha=0.4), Line2D([], [], color='#c53030', lw=2)],
           labels=['치명 칸 — 라이다 확인', '치명 칸 — 카메라만(라이다 점 없음)', '라이다 점', '차체(패딩 포함) · 화살표 = 앞', '카메라 시야 ±43°', '가장 가까운 치명 칸까지'], loc='upper center', ncol=6, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.975))
# 아래: 시간 그래프 — 왼쪽 2/3 = f2v1, 오른쪽 1/3 = 복귀
for j, (F, lab, span) in enumerate([(A, 'f2v1 목표 4 시작 ~ Nav2 포기', gs[1, 0:2]), (B, '9 분 뒤 복귀 주행 출발', gs[1, 2])]):
    ax = fig.add_subplot(span); T = np.array([f[0] for f in F]); t0 = T[0]
    dall = []; dcam = []; ncam = []
    for ts, P, cx, cy, seen, lx, ly in F:
        d = dist_body(P, cx, cy); dall.append(100 * d.min()); dc = d[~seen]; dcam.append(100 * dc.min() if len(dc) else np.nan); ncam.append(int(((d <= 0.08) & ~seen).sum()))
    tt = T - t0
    ax.bar(tt, ncam, width=0.45, color='#e07b24', alpha=0.28, label='차체 8 cm 안 카메라 칸 수(개)')
    ax.plot(tt, dall, color='#1d2329', lw=2, marker='o', ms=3, label='가장 가까운 치명 칸(cm)')
    ax.plot(tt, dcam, color='#e07b24', lw=1.6, ls='-', marker='s', ms=3, label='가장 가까운 카메라만 칸(cm)')
    ax.axhline(4.4, color='#c53030', ls='--', lw=1); ax.text(tt[-1], 4.6, '4.4 cm', color='#c53030', fontsize=9, ha='right')
    ax.set_ylim(0, 16)
    if j == 0:
        for s in FAILS: ax.axvspan(ep(s) - t0 - 0.15, ep(s) - t0 + 0.15, color='#9aa5ae', alpha=0.5)
        ax.text(0.3, 15.3, '회색 세로 띠 = Nav2 \'후보 전부 충돌\' 기록 시각', fontsize=9, color='#4a5664', va='top')
    ax.set_title(lab + '  (가로 = %s 부터 초)' % time.strftime('%H:%M:%S', time.localtime(t0)), fontsize=10, loc='left')
    ax.set_xlabel('s'); ax.set_ylabel('cm / 개'); ax.set_ylim(0, 16); ax.grid(color='#c9d1d9', lw=0.4)
    if j == 0: ax.legend(fontsize=8.5, loc='upper right')
fig.suptitle('서쪽 통로 남쪽 정지 자리 — 차체 옆 카메라 기억 칸이 생겼다 사라짐(f2v1 10:15 · 복귀 10:25)', fontsize=12, x=0.01, ha='left', y=0.995)
fig.savefig(out, dpi=125, bbox_inches='tight'); print('저장', out)
