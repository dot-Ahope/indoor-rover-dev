#!/usr/bin/env python3
"""fig_return_video — 복귀 때 상자를 어떤 값으로 알고 있었고 왜 붙어 지나갔는지 보는 영상(2026-10-22 §17, PC).
  왜: 사용자 — f2pi1 "진행을 영상으로 시각화 해달라. 복귀 시 상자를 어떤 값으로 인식했고 왜 못 피해갔는지 알고자 한다."
  화면
    왼쪽(큰 판, 상자 둘레 확대, 지도 좌표):
      바탕 = 로컬 코스트맵(MPPI 가 보는 지도, odom → 그 순간 map→odom 으로 옮김): 빨강 치명 100 · 주황 내접 99 · 옅은 노랑~회색 = 팽창 비용
      자홍 네모 테두리 = 지금 nvblox 조각 장애물 칸(카메라 기억 포함), 검정 굵은 사각 = 실제 상자(10-19 실측), 파란 점 = 라이다
      보라 선 = 전역 경로(/plan_smoothed), 청록 선 = 컨트롤러가 받은 경로(/transformed_global_plan), 초록 = 차체 · 지나온 길
      노란 부채꼴 = 카메라 깊이 시야(±43°, 2.0 m)
    오른쪽 위: 지금 깊이 영상(160×120, 프리셋 3) — 검정 = 깊이 0(무효), 밝을수록 가까움. 빨강 점 = 실제 상자 모서리를 영상에 투영한 자리(시야 안일 때)
    오른쪽 아래: 시간 그래프 — 실제 여유(차체 ↔ 실제 상자) · 지도 여유(차체 ↔ 로컬 코스트맵 치명 칸 중 상자 둘레) · 전진 명령 v, 세로선 = 지금
  아래 글: 시각, 로버 자세, 상자 쪽 화소 중 유효 깊이 수, 최근 nav2 사건(PathBlockedAhead · 스무더 충돌 · TF 외삽 중단)
  인자: bag nav_events.txt 출력.mp4 시작s 끝s [배속=1]"""
import sys, math, bisect, datetime
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Polygon, Wedge
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False; plt.rcParams['animation.ffmpeg_path'] = 'C:/ffmpeg/bin/ffmpeg.exe'
TS = get_typestore(Stores.ROS2_HUMBLE)
TS.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag, evf, out, TA, TB = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]); SPEED = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
FPS = 10; DT = SPEED / FPS
BOX = (1.151, 1.261, -0.20, -0.02); BOXH = 0.114; REG = (BOX[0] - 0.15, BOX[1] + 0.15, BOX[2] - 0.15, BOX[3] + 0.15)
VX = (0.2, 2.8, -1.1, 0.9); FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
KST = datetime.timezone(datetime.timedelta(hours=9))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
def qm(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
def T4(tr):
    M = np.eye(4); M[:3, :3] = qm(tr.rotation); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M
def last(L, Lt, t): return L[max(bisect.bisect_right(Lt, t) - 1, 0)]
def pts_of(m):
    if hasattr(m, 'poses'): return np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]) if m.poses else np.zeros((0, 2))
    P = [[p.x, p.y] for mk in m.markers[:1] for p in mk.points]; return np.array(P) if P else np.zeros((0, 2))

MO, OB, LC, SL, PL, TP, SC, CMD, DEP = [], [], [], [], [], [], [], [], []
static = {}; K = None; dframe = None; LS = None
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    T0 = rd.start_time * 1e-9
    want = ('/tf', '/tf_static', '/map', '/local_costmap/costmap', '/nvblox_node/static_map_slice', '/plan_smoothed', '/transformed_global_plan', '/scan', '/cmd_vel',
            '/camera/camera/depth/image_rect_raw', '/camera/camera/depth/camera_info')
    MAP = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
        tt = t * 1e-9 - T0
        if c.topic not in ('/tf', '/tf_static', '/map', '/camera/camera/depth/camera_info') and not (TA - 3 <= tt <= TB + 1): continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T4(tr.transform))
        elif c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((tt, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((tt, v))
        elif c.topic == '/map': MAP = m
        elif c.topic == '/local_costmap/costmap':
            g = m.info; LC.append((tt, m.header.frame_id, g.origin.position.x, g.origin.position.y, g.resolution, np.array(m.data, np.int16).reshape(g.height, g.width)))
        elif c.topic == '/nvblox_node/static_map_slice':
            d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value)); r = m.resolution
            SL.append((tt, m.header.frame_id, np.c_[m.origin.x + (ix + .5) * r, m.origin.y + (iy + .5) * r], r))
        elif c.topic == '/plan_smoothed': PL.append((tt, m.header.frame_id, pts_of(m)))
        elif c.topic == '/transformed_global_plan': TP.append((tt, m.header.frame_id if hasattr(m, 'header') else 'odom', pts_of(m)))
        elif c.topic == '/scan':
            a_ = m.angle_min + np.arange(len(m.ranges)) * m.angle_increment; r_ = np.array(m.ranges); k = np.isfinite(r_) & (r_ > 0.15)
            SC.append((tt, np.c_[r_[k] * np.cos(a_[k]), r_[k] * np.sin(a_[k])][::2]))
        elif c.topic == '/cmd_vel': CMD.append((tt, m.linear.x))
        elif c.topic.endswith('camera_info'):
            if K is None: K = np.array(m.k).reshape(3, 3)
        else:
            dframe = m.header.frame_id; DEP.append((tt, np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width).copy()))
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; LCt = [q[0] for q in LC]; SLt = [q[0] for q in SL]; PLt = [q[0] for q in PL]; TPt = [q[0] for q in TP]
SCt = [q[0] for q in SC]; CMt = [q[0] for q in CMD]; DEt = [q[0] for q in DEP]
def chain(f):
    M = np.eye(4)
    while f != 'base_link': p, A = static[f]; M = A @ M; f = p
    return M
Bc = chain(dframe); Bl = chain('lidar_link') if 'lidar_link' in static else None
mo_at = lambda t: last(MO, MOt, t)[1]
def to_map(P, fr, t):
    if fr == 'map' or len(P) == 0: return P
    a = mo_at(t); c, s = math.cos(a[2]), math.sin(a[2]); return np.c_[a[0] + c * P[:, 0] - s * P[:, 1], a[1] + s * P[:, 0] + c * P[:, 1]]
def pose(t): return comp(mo_at(t), last(OB, OBt, t)[1])
def poly(p):
    c, s = math.cos(p[2]), math.sin(p[2]); return np.c_[p[0] + c * FP[:, 0] - s * FP[:, 1], p[1] + s * FP[:, 0] + c * FP[:, 1]]
def poly_dist(Q, pts):   # 차체 사각형(지도) ↔ 점들 최소 거리(안이면 0)
    if len(pts) == 0: return np.nan
    from matplotlib.path import Path as MP
    if MP(Q).contains_points(pts).any(): return 0.0
    d = np.inf
    for i in range(4):
        a, b = Q[i], Q[(i + 1) % 4]; ab = b - a; u = np.clip(((pts - a) @ ab) / (ab @ ab), 0, 1); d = min(d, float(np.min(np.linalg.norm(pts - (a + u[:, None] * ab), axis=1))))
    return d
BOXPTS = np.array([[x, y] for x in np.linspace(BOX[0], BOX[1], 6) for y in np.linspace(BOX[2], BOX[3], 8)])
# 시간 그래프용 미리 계산
TT = np.arange(TA, TB + 1e-6, 0.2); CL_true, CL_map, CL_sl = [], [], []
for t in TT:
    Q = poly(pose(t)); CL_true.append(poly_dist(Q, BOXPTS))
    tt, fr, ox, oy, r, A = last(LC, LCt, t); ys, xs = np.nonzero(A >= 100); P = to_map(np.c_[ox + (xs + .5) * r, oy + (ys + .5) * r], fr, tt)
    k = (P[:, 0] > REG[0]) & (P[:, 0] < REG[1]) & (P[:, 1] > REG[2]) & (P[:, 1] < REG[3]) if len(P) else np.zeros(0, bool)
    CL_map.append(poly_dist(Q, P[k]) if k.any() else np.nan)
    tt, fr, P, r = last(SL, SLt, t); P = to_map(P, fr, tt); k = (P[:, 0] > REG[0]) & (P[:, 0] < REG[1]) & (P[:, 1] > REG[2]) & (P[:, 1] < REG[3]) if len(P) else np.zeros(0, bool)
    CL_sl.append(poly_dist(Q, P[k]) if k.any() else np.nan)
CL_true, CL_map, CL_sl = (np.array(v) for v in (CL_true, CL_map, CL_sl))
EV = []
for line in open(evf, encoding='utf-8', errors='replace'):
    if any(k in line for k in ('PathBlockedAhead', 'collision', 'extrapolation into the future', 'Running', 'failed to create plan')):
        hh, mm, ss = line[:11].split(':'); sec = int(hh) * 3600 + int(mm) * 60 + float(ss)
        b = datetime.datetime.fromtimestamp(T0, KST); t = sec - (b.hour * 3600 + b.minute * 60 + b.second + b.microsecond * 1e-6)
        txt = 'PathBlockedAhead' if 'PathBlockedAhead' in line else ('스무더 충돌' if 'collision' in line else ('TF 외삽 중단' if 'extrapolation' in line else line[12:60].strip()))
        if 'PathBlockedAhead' in line: txt = line[12:].split(':', 1)[-1].strip()[:40] if ':' in line[12:] else txt
        EV.append((t, txt))
lc_cmap = ListedColormap([(0, 0, 0, 0), (0.95, 0.9, 0.6, 0.45), (0.95, 0.75, 0.35, 0.55), (1, 0.55, 0.15, 0.7), (0.85, 0.1, 0.1, 0.8)])
fig = plt.figure(figsize=(14, 7.6), facecolor='white'); gs = fig.add_gridspec(2, 2, width_ratios=[1.45, 1], height_ratios=[1, 1])
axM = fig.add_subplot(gs[:, 0]); axD = fig.add_subplot(gs[0, 1]); axT = fig.add_subplot(gs[1, 1])
wr = FFMpegWriter(fps=FPS, bitrate=3200); clock = lambda t: datetime.datetime.fromtimestamp(T0 + t, KST).strftime('%H:%M:%S.%f')[:10]
with wr.saving(fig, out, dpi=90):
    t = TA; nfr = 0
    while t <= TB:
        p = pose(t); Q = poly(p)
        axM.clear(); axM.set_xlim(VX[0], VX[1]); axM.set_ylim(VX[2], VX[3]); axM.set_aspect('equal'); axM.tick_params(labelsize=7); axM.grid(alpha=0.25)
        if MAP is not None:
            g = np.array(MAP.data).reshape(MAP.info.height, MAP.info.width); yy, xx = np.nonzero(g >= 65); r = MAP.info.resolution
            axM.scatter(MAP.info.origin.position.x + (xx + .5) * r, MAP.info.origin.position.y + (yy + .5) * r, s=4, c='#9e9e9e', marker='s', lw=0)
        tt, fr, ox, oy, r, A = last(LC, LCt, t); L = np.zeros_like(A); L[(A > 0) & (A < 50)] = 1; L[(A >= 50) & (A < 99)] = 2; L[A == 99] = 3; L[A >= 100] = 4
        a = mo_at(tt) if fr != 'map' else (0, 0, 0)
        ys, xs = np.nonzero(L > 0)
        if len(xs):
            P = to_map(np.c_[ox + (xs + .5) * r, oy + (ys + .5) * r], fr, tt); vals = L[ys, xs]
            for lv, col in ((1, (0.95, 0.9, 0.6, 0.45)), (2, (0.95, 0.75, 0.35, 0.55)), (3, (1, 0.55, 0.15, 0.75)), (4, (0.85, 0.1, 0.1, 0.85))):
                k = vals == lv
                if k.any(): axM.scatter(P[k, 0], P[k, 1], s=26, c=[col], marker='s', lw=0)
        tt, fr, P, r = last(SL, SLt, t); P = to_map(P, fr, tt)
        if len(P): axM.scatter(P[:, 0], P[:, 1], s=34, facecolors='none', edgecolors='#c2185b', marker='s', lw=1.1)
        if SC and Bl is not None:
            S_ = last(SC, SCt, t)[1]; lp = comp(p, (Bl[0, 3], Bl[1, 3], math.atan2(Bl[1, 0], Bl[0, 0]))); c, s = math.cos(lp[2]), math.sin(lp[2])
            axM.scatter(lp[0] + c * S_[:, 0] - s * S_[:, 1], lp[1] + s * S_[:, 0] + c * S_[:, 1], s=2, c='#1e88e5', lw=0)
        for L_, Lt_, col, lw in ((PL, PLt, '#7b1fa2', 1.6), (TP, TPt, '#00897b', 1.2)):
            if L_:
                tt, fr, P = last(L_, Lt_, t); P = to_map(P, fr, tt)
                if len(P): axM.plot(P[:, 0], P[:, 1], color=col, lw=lw)
        tr = np.array([comp(mo_at(q), ob)[:2] for q, ob in OB[::10] if TA - 3 <= q <= t])
        if len(tr): axM.plot(tr[:, 0], tr[:, 1], color='#2e7d32', lw=0.8, alpha=0.6)
        Mc = np.eye(4); Mc[:2, :2] = [[math.cos(p[2]), -math.sin(p[2])], [math.sin(p[2]), math.cos(p[2])]]; Mc[0, 3], Mc[1, 3] = p[0], p[1]; Mc = Mc @ Bc
        co = Mc[:3, 3]; ax_ = Mc[:3, 2]; cyaw = math.degrees(math.atan2(ax_[1], ax_[0]))
        axM.add_patch(Wedge((co[0], co[1]), 2.0, cyaw - 43, cyaw + 43, fc=(1, 0.85, 0.1, 0.10), ec=(0.9, 0.7, 0, 0.5), lw=0.6))
        axM.add_patch(Polygon(Q, closed=True, fc=(0.26, 0.63, 0.28, 0.55), ec='#1b5e20', lw=1.2))
        axM.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fill=False, ec='black', lw=2.2))
        i = int(np.clip(round((t - TA) / 0.2), 0, len(TT) - 1))
        axM.set_title('%s (t %.1f s) · 로버 (%.2f, %.2f, %.0f°) · 실제 여유 %s · 지도(로컬 치명) 여유 %s' % (clock(t), t, p[0], p[1], math.degrees(p[2]),
                      ('%.1f cm' % (100 * CL_true[i])), ('-' if np.isnan(CL_map[i]) else '%.1f cm' % (100 * CL_map[i]))), fontsize=10)
        # 깊이 영상
        axD.clear(); axD.set_xticks([]); axD.set_yticks([]); nvalid = 0
        if DEP:
            dt_, img = last(DEP, DEt, t); z = img.astype(np.float32) / 1000.0
            vis = np.where(z > 0, 1 - np.clip(z / 3.0, 0, 1), 0); axD.imshow(vis, cmap='gray', vmin=0, vmax=1, interpolation='nearest')
            Mi = np.linalg.inv(Mc); cn = np.array([[x, y, zz, 1] for x in (BOX[0], BOX[1]) for y in (BOX[2], BOX[3]) for zz in (0.0, BOXH)]).T
            Pc = (Mi @ cn)[:3]; ok = Pc[2] > 0.1
            if ok.all() and K is not None:
                u = K[0, 0] * Pc[0] / Pc[2] + K[0, 2]; v = K[1, 1] * Pc[1] / Pc[2] + K[1, 2]; H, W = img.shape
                if (u.max() >= 0) and (u.min() < W) and (v.max() >= 0) and (v.min() < H):
                    axD.scatter(u, v, s=10, c='red'); u0, u1, v0, v1 = [int(np.clip(q, 0, lim - 1)) for q, lim in ((u.min(), W), (u.max(), W), (v.min(), H), (v.max(), H))]
                    axD.add_patch(Rectangle((u0, v0), u1 - u0, v1 - v0, fill=False, ec='red', lw=1)); sub = img[v0:v1 + 1, u0:u1 + 1]; nvalid = int((sub > 0).sum()); ntot = sub.size
                    axD.set_xlabel('상자 쪽 화소 %d 중 유효 깊이 %d' % (ntot, nvalid), fontsize=9)
                else: axD.set_xlabel('상자가 영상 밖', fontsize=9)
            else: axD.set_xlabel('상자가 카메라 뒤', fontsize=9)
            axD.set_xlim(0, img.shape[1]); axD.set_ylim(img.shape[0], 0)
        axD.set_title('깊이 영상(160×120, 프리셋 3) · 검정 = 깊이 0', fontsize=9)
        # 시간 그래프
        axT.clear(); axT.plot(TT, 100 * CL_true, color='black', lw=1.4, label='실제 여유(차체↔실제 상자)')
        axT.plot(TT, 100 * CL_map, color='#d32f2f', lw=1.2, label='지도 여유(차체↔로컬 치명 칸)'); axT.plot(TT, 100 * CL_sl, color='#c2185b', lw=0.8, ls='--', label='카메라 칸까지(조각)')
        axT.set_ylim(-2, 60); axT.set_xlim(TA, TB); axT.set_ylabel('cm'); axT.axvline(t, color='#555555', lw=0.8); axT.grid(alpha=0.3); axT.tick_params(labelsize=7)
        ax2 = axT.twinx(); cv = np.array([q for q in CMD if TA <= q[0] <= TB])
        if len(cv): ax2.plot(cv[:, 0], cv[:, 1], color='#1565c0', lw=0.7, alpha=0.7)
        ax2.set_ylim(-0.1, 0.12); ax2.set_ylabel('전진 명령 m/s', color='#1565c0', fontsize=8); ax2.tick_params(labelsize=7)
        for te, txt in EV:
            if TA <= te <= TB: axT.axvline(te, color='#ff9800', lw=0.6, alpha=0.7)
        axT.legend(fontsize=7, loc='upper left'); axT.set_xlabel('bag 시각 t (s) · 주황 세로선 = nav2 사건', fontsize=8)
        rec = [txt for te, txt in EV if t - 2.0 <= te <= t]
        fig.suptitle('f2pi1 복귀 · 상자 둘레 — 자홍 테두리 = 카메라(nvblox) 칸 · 빨강/주황/노랑 = 로컬 코스트맵(MPPI) · 검정 사각 = 실제 상자 · 보라 = 전역 경로 · 청록 = 컨트롤러 경로 · 노랑 부채꼴 = 깊이 시야 2.0 m'
                     + ('\n최근 2 s 사건: ' + ' / '.join(rec[-2:]) if rec else '\n '), fontsize=9)
        plt.tight_layout(rect=(0, 0, 1, 0.93)); wr.grab_frame(); t += DT; nfr += 1
print('영상', out, nfr, '장 · 실제 여유 최소 %.1f cm @ t %.1f · 지도 여유 그때 %s' % (100 * np.nanmin(CL_true), TT[np.nanargmin(CL_true)],
      '%.1f cm' % (100 * CL_map[np.nanargmin(CL_true)]) if not np.isnan(CL_map[np.nanargmin(CL_true)]) else '-'))
