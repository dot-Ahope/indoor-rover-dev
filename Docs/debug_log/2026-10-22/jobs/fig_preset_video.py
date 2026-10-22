#!/usr/bin/env python3
"""fig_preset_video — 두 주행을 나란히 같은 경과 시간으로 재생하는 지도 영상(2026-10-22 §10, PC).
  왜: 사용자 — 프리셋 3 채택 뒤 "영상으로도" 시각화. 프리셋 없음(f2dr2) vs 프리셋 3(f2pr1): 카메라(nvblox)가 찍는 칸과 계획기가 보는 전역 코스트맵이 어떻게 다른지.
  화면(각 판): 회색 점 = 저장 지도 벽, 바탕 = 전역 코스트맵(빨강 치명 100 · 주황 내접 99 · 연회색 팽창), 자홍 네모 = 지금 nvblox 조각 장애물 칸(카메라가 본 것),
        파란 점 = 라이다, 보라 선 = 전역 경로(/plan), 초록 = 차체 · 지나온 길, 흰 테두리 = 출발점 낮은 상자, 점선 = 맨바닥 영역 A.
  아래 글 = 경과 시간, 맨바닥 A 안 자홍 칸 수 · 상자 영역 칸 수.
  인자: 출력.mp4 이름=bag 이름=bag [배속=2]"""
import sys, math, bisect
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Polygon
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False; plt.rcParams['animation.ffmpeg_path'] = 'C:/ffmpeg/bin/ffmpeg.exe'
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
out = sys.argv[1]; args = [a for a in sys.argv[2:] if '=' in a]; SPEED = float(next((a for a in sys.argv[2:] if '=' not in a), 2)); FPS = 10; DT = SPEED / FPS
BOX = (1.151, 1.261, -0.20, -0.02); ZA = (1.45, 2.65, -0.35, 0.45); VX = (-1.5, 6.3, -2.9, 1.6)
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
def last(L, Lt, t): return L[max(bisect.bisect_right(Lt, t) - 1, 0)]
R = []
for a in args:
    nm, bag = a.split('='); D = {'MO': [], 'OB': [], 'GC': [], 'SL': [], 'PL': [], 'SC': [], 'MAP': None, 'LS': None}
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        T0 = rd.start_time * 1e-9; dur = (rd.end_time - rd.start_time) * 1e-9
        want = ('/tf', '/tf_static', '/map', '/global_costmap/costmap', '/nvblox_node/static_map_slice', '/plan', '/scan')
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
            tt = t * 1e-9 - T0; m = rd.deserialize(raw, c.msgtype)
            if c.topic in ('/tf', '/tf_static'):
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': D['MO'].append((tt, v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': D['OB'].append((tt, v))
                    elif tr.child_frame_id == 'lidar_link': D['LS'] = v   # base_link → lidar_link(/scan 프레임 — 10-22 확인)
            elif c.topic == '/map': D['MAP'] = m
            elif c.topic == '/global_costmap/costmap':
                g = m.info; D['GC'].append((tt, (g.origin.position.x, g.origin.position.y, g.resolution, g.width, g.height), np.array(m.data, np.int16).reshape(g.height, g.width)))
            elif c.topic == '/plan': D['PL'].append((tt, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
            elif c.topic == '/scan':
                a_ = m.angle_min + np.arange(len(m.ranges)) * m.angle_increment; r_ = np.array(m.ranges); k = np.isfinite(r_) & (r_ > 0.15)
                D['SC'].append((tt, np.c_[r_[k] * np.cos(a_[k]), r_[k] * np.sin(a_[k])][::2]))
            else:
                st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
                d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
                D['SL'].append((tt, st - T0, np.c_[m.origin.x + (ix + 0.5) * r, m.origin.y + (iy + 0.5) * r], m.header.frame_id))
    for k in ('MO', 'OB'): D[k].sort(key=lambda q: q[0]); D[k + 't'] = [q[0] for q in D[k]]
    for k in ('GC', 'SL', 'PL', 'SC'): D[k + 't'] = [q[0] for q in D[k]]
    D['nm'], D['dur'] = nm, dur; R.append(D); print(nm, '읽음', len(D['SL']), '조각', len(D['GC']), '코스트맵', '%.0f s' % dur)
TEND = max(D['dur'] for D in R)
cmap = ListedColormap([(0, 0, 0, 0), (0.75, 0.75, 0.75, 0.35), (1, 0.55, 0.15, 0.6), (0.85, 0.1, 0.1, 0.75)])
fig, axs = plt.subplots(1, len(R), figsize=(8 * len(R), 5.2), facecolor='white')
wr = FFMpegWriter(fps=FPS, bitrate=3000)
with wr.saving(fig, out, dpi=90):
    t = 0.0; nfr = 0
    while t <= TEND:
        for ax, D in zip(axs, R):
            ax.clear(); ax.set_xlim(VX[0], VX[1]); ax.set_ylim(VX[2], VX[3]); ax.set_aspect('equal'); ax.tick_params(labelsize=7)
            M = D['MAP']
            if M is not None:
                g = np.array(M.data).reshape(M.info.height, M.info.width); yy, xx = np.nonzero(g >= 65); r = M.info.resolution
                ax.scatter(M.info.origin.position.x + (xx + .5) * r, M.info.origin.position.y + (yy + .5) * r, s=1, c='#999999', marker='s', lw=0)
            tc = min(t, D['dur']); mo = last(D['MO'], D['MOt'], tc)[1]; p = comp(mo, last(D['OB'], D['OBt'], tc)[1])
            if D['GC']:
                _, (ox, oy, r, w, h), A = last(D['GC'], D['GCt'], tc); L = np.zeros_like(A); L[(A > 0) & (A < 99)] = 1; L[A == 99] = 2; L[A >= 100] = 3
                ax.imshow(L, origin='lower', extent=(ox, ox + w * r, oy, oy + h * r), cmap=cmap, vmin=0, vmax=3, interpolation='nearest')
            nA = nB = 0
            if D['SL']:
                tt, st, P, fr = last(D['SL'], D['SLt'], tc)
                if fr != 'map':
                    m2 = last(D['MO'], D['MOt'], st)[1]; c, s = math.cos(m2[2]), math.sin(m2[2]); P = np.c_[m2[0] + c * P[:, 0] - s * P[:, 1], m2[1] + s * P[:, 0] + c * P[:, 1]]
                ax.scatter(P[:, 0], P[:, 1], s=9, c='#d81b9a', marker='s', lw=0)
                nA = int(np.sum((P[:, 0] >= ZA[0]) & (P[:, 0] <= ZA[1]) & (P[:, 1] >= ZA[2]) & (P[:, 1] <= ZA[3])))
                nB = int(np.sum((P[:, 0] >= 1.10) & (P[:, 0] <= 1.40) & (P[:, 1] >= -0.25) & (P[:, 1] <= 0.10)))
            if D['SC'] and D['LS']:
                S_ = last(D['SC'], D['SCt'], tc)[1]; l = comp(p, D['LS']); c, s = math.cos(l[2]), math.sin(l[2])
                ax.scatter(l[0] + c * S_[:, 0] - s * S_[:, 1], l[1] + s * S_[:, 0] + c * S_[:, 1], s=1.5, c='#1e88e5', lw=0)
            if D['PL']:
                pl = last(D['PL'], D['PLt'], tc)[1]
                if len(pl): ax.plot(pl[:, 0], pl[:, 1], color='#7b1fa2', lw=1.4)
            tr = [comp(last(D['MO'], D['MOt'], q)[1], ob) for q, ob in D['OB'][::10] if q <= tc]
            if tr: tr = np.array(tr); ax.plot(tr[:, 0], tr[:, 1], color='#2e7d32', lw=0.8, alpha=0.6)
            c, s = math.cos(p[2]), math.sin(p[2]); ax.add_patch(Polygon(np.c_[p[0] + c * FP[:, 0] - s * FP[:, 1], p[1] + s * FP[:, 0] + c * FP[:, 1]], closed=True, fc='#43a047', ec='#1b5e20', alpha=0.85))
            ax.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fill=False, ec='black', lw=1.2))
            ax.add_patch(Rectangle((ZA[0], ZA[2]), ZA[1] - ZA[0], ZA[3] - ZA[2], fill=False, ec='#666666', lw=0.8, ls='--'))
            ax.set_title('%s  ·  %5.1f s%s' % (D['nm'], tc, '  (끝)' if t > D['dur'] else ''), fontsize=12)
            ax.set_xlabel('카메라 칸: 맨바닥 영역 A %d · 상자 둘레 %d' % (nA, nB), fontsize=10)
        fig.suptitle('자홍 = nvblox(카메라) 장애물 칸 · 빨강/주황/연회색 = 전역 코스트맵 치명/내접/팽창 · 파랑 = 라이다 · 보라 = 전역 경로 · 검은 테두리 = 낮은 상자 · 점선 = 맨바닥 영역 A   (%.0f 배속)' % SPEED, fontsize=9)
        plt.tight_layout(rect=(0, 0, 1, 0.96)); wr.grab_frame(); t += DT; nfr += 1
print('영상', out, nfr, '장')
