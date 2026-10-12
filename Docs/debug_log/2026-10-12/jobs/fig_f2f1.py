# 10-12 §2 그림: f2f1 복귀 상자 구간 — 위 = 그 순간의 로컬 코스트맵(RViz 색)·차체·경로·MPPI 최적 궤적 4 장면, 아래 = 시간축(지령 속도, TF 끊김·사건, CPU)
import math, re, time, collections, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
S = 'C:/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/'
z = np.load(S + 'sc/fz_f2f1.npz', allow_pickle=True); tr, mo, cmd = z['traj'], z['mo'], z['cmd']
pt, pn, pxy = z['plan_t'], z['plan_n'], z['plan_xy']; ps = np.r_[0, np.cumsum(pn)]; lt, lc, lm = z['lcm_t'], z['lcm'], z['lcm_meta']; mt, mopt = z['mppi_t'], z['mppi_opt']
def ep(s): return time.mktime(time.strptime('2026-10-12 ' + s, '%Y-%m-%d %H:%M:%S'))
A, B = ep('10:34:37'), ep('10:35:48')
# odom→base_link TF stamp 끊김(bag)
ts = get_typestore(Stores.ROS2_HUMBLE); ob = []
with AnyReader([Path(S + 'f0_f2f1/bag_f2f1')], default_typestore=ts) as r:
    for c, t_ns, raw in r.messages(connections=[c for c in r.connections if c.topic == '/tf']):
        if not (A - 2 <= t_ns * 1e-9 <= B + 2): continue
        for x in r.deserialize(raw, c.msgtype).transforms:
            if x.child_frame_id == 'base_link': ob.append(x.header.stamp.sec + x.header.stamp.nanosec * 1e-9)
ob = np.array(sorted(ob)); gaps = [(ob[i], ob[i + 1]) for i in np.nonzero(np.diff(ob) > 0.5)[0]]
# top
blocks = []; cur = None
for l in open(S + 'f0_f2f1/top_f2f1.log', errors='replace'):
    m = re.match(r'top - (\d\d:\d\d:\d\d)', l)
    if m: cur = dict(t=ep(m.group(1)), idle=None, p=collections.Counter()); blocks.append(cur); continue
    if cur is None: continue
    m = re.search(r'([\d.]+) id', l)
    if l.startswith('%Cpu') and m: cur['idle'] = float(m.group(1)); continue
    f = l.split()
    if len(f) >= 12 and f[0].isdigit():
        try: cur['p'][f[11][:8]] += float(f[8])
        except ValueError: pass
blocks = [b for b in blocks if A <= b['t'] <= B and b['idle'] is not None]
EV = [('10:35:07', '① 컨트롤러 중단(TF)', '#c0392b', 0.62, 'right'), ('10:35:09', '② 앞 경로 비용 99 가 2 s → 주행 중단·재계획', '#d35400', 0.40, 'left'), ('10:35:14', '③ 계획 서버 응답 시간 초과', '#7d3c98', 0.18, 'left'), ('10:35:28', '④ 컨트롤러 중단 ×2(TF)', '#c0392b', 0.62, 'left')]
SM = ['10:34:48', '10:35:10', '10:35:12', '10:35:18', '10:35:25']   # smoother '충돌' → 원경로 사용
SNAP = ['10:35:02', '10:35:10', '10:35:17', '10:35:31']
fig = plt.figure(figsize=(15, 11.5)); gs = fig.add_gridspec(4, 4, height_ratios=[3.2, 1, 1, 1], hspace=0.38, wspace=0.12)
cmapc = matplotlib.colors.ListedColormap(['#00000000'] + [matplotlib.cm.Blues(0.25 + 0.5 * i / 97) for i in range(98)] + ['#00c8d7', '#d81b9a'])
HL, HW = 0.25, 0.165
for k, s in enumerate(SNAP):
    a = fig.add_subplot(gs[0, k]); t = ep(s); i = np.searchsorted(tr[:, 0], t); x, y, th = tr[i, 1:4]
    j = min(np.searchsorted(mo[:, 0], t), len(mo) - 1); mx, my, mth = mo[j, 1:4]; cm_, sm_ = math.cos(mth), math.sin(mth)
    li = max(np.searchsorted(lt, t) - 1, 0); g = lc[li].astype(float); res, gx, gy = lm[li][:3]; g[g < 0] = 0
    # 로컬 코스트맵(odom) 칸 → map 좌표 산점(회전 작음)
    ys, xs = np.nonzero(g > 0); px = gx + (xs + .5) * res; py = gy + (ys + .5) * res; X = mx + cm_ * px - sm_ * py; Y = my + sm_ * px + cm_ * py; v = g[ys, xs]
    kk = (np.abs(X - x) < 1.25) & (np.abs(Y - y) < 1.25)
    a.scatter(X[kk], Y[kk], c=v[kk], cmap=cmapc, vmin=0, vmax=100, s=26, marker='s', linewidths=0)
    q = max(np.searchsorted(pt, t) - 1, 0); P = pxy[ps[q]:ps[q + 1]]; a.plot(P[:, 0], P[:, 1], c='#27ae60', lw=2, label='계획 경로')
    k0 = tr[:, 0] <= t; a.plot(tr[k0, 1][-400:], tr[k0, 2][-400:], c='#2c3e50', lw=1.2, ls=':', label='지나온 길')
    mi = max(np.searchsorted(mt, t) - 1, 0); O = mopt[mi]; a.plot(mx + cm_ * O[:, 0] - sm_ * O[:, 1], my + sm_ * O[:, 0] + cm_ * O[:, 1], c='#e67e22', lw=2.5, label='MPPI 최적 궤적')
    c, s_ = math.cos(th), math.sin(th); C = [(x + c * u - s_ * w, y + s_ * u + c * w) for u, w in ((HL, HW), (HL, -HW), (-HL, -HW), (-HL, HW))]
    a.add_patch(Polygon(C, closed=True, fc='#f1c40f66', ec='#333', lw=1.5)); a.arrow(x, y, 0.22 * c, 0.22 * s_, head_width=0.07, color='#333', length_includes_head=True)
    cc = cmd[(cmd[:, 0] >= t - 0.5) & (cmd[:, 0] < t + 0.5)]
    a.set_title('%s  지령 v %s' % (s, ('%+.2f m/s' % cc[:, 1].mean()) if len(cc) else '없음(정지)'), fontsize=11)
    a.set_xlim(x - 1.1, x + 1.1); a.set_ylim(y - 1.1, y + 1.1); a.set_aspect('equal'); a.invert_xaxis(); a.tick_params(labelsize=8)
    if k == 0: a.legend(fontsize=8, loc='lower left'); a.set_ylabel('map y [m]')
    a.set_xlabel('map x [m]  (왼쪽 = 출발 방향)')
fig.text(0.5, 0.905, '로컬 코스트맵: 자홍 = 치명(충돌), 청록 = 내접(차체 중심이 오면 닿음), 파랑 = 여유 비용 · 노란 사각 = 차체', ha='center', fontsize=10)
f = lambda t: (t - A)
a1 = fig.add_subplot(gs[1, :]); c_ = cmd[(cmd[:, 0] >= A) & (cmd[:, 0] <= B)]
tt = [c_[0, 0]]; vv = [c_[0, 1]]
for (t0, v0, _), (t1, v1, _) in zip(c_[:-1], c_[1:]):
    if t1 - t0 > 0.3: tt += [t0 + 0.05, t1 - 0.01]; vv += [np.nan, np.nan]
    tt.append(t1); vv.append(v1)
a1.plot([f(t) for t in tt], vv, c='#2471a3', lw=1.2); a1.axhline(0, c='#999', lw=.6); a1.set_ylabel('지령 v [m/s]'); a1.set_ylim(-0.07, 0.095)
for t0, t1 in [(c_[i, 0], c_[i + 1, 0]) for i in np.nonzero(np.diff(c_[:, 0]) > 0.3)[0]]: a1.axvspan(f(t0), f(t1), color='#f5b7b1', alpha=.6)
a1.text(0.005, 0.05, '분홍 = 지령이 아예 안 나온 시간(펌웨어 워치독으로 정지)', transform=a1.transAxes, fontsize=9, color='#922')
a2 = fig.add_subplot(gs[2, :], sharex=a1)
for t0, t1 in gaps: a2.axvspan(f(t0), f(t1), color='#f9e79f')
for s, lab, col, yy, ha in EV: a2.axvline(f(ep(s)), c=col, lw=2); a2.text(f(ep(s)) + (0.4 if ha == 'left' else -0.4), yy, lab, color=col, fontsize=9, va='center', ha=ha, bbox=dict(fc='white', ec='none', alpha=.8, pad=1))
for s in SM: a2.plot(f(ep(s)), 0.06, marker='v', c='#16a085', ms=8)
a2.text(0.005, 0.88, '노랑 = odom→base_link 좌표 변환이 0.5 s 넘게 끊긴 구간(bag 기록) · ▼ = 경로 다듬기 실패(원경로 사용)', transform=a2.transAxes, fontsize=9, bbox=dict(fc='white', ec='none', alpha=.8, pad=1)); a2.set_yticks([]); a2.set_ylim(0, 1.05); a2.set_ylabel('사건')
a3 = fig.add_subplot(gs[3, :], sharex=a1); bt = [f(b['t']) for b in blocks]
a3.plot(bt, [100 - b['idle'] for b in blocks], c='#333', lw=2, label='전체 CPU 사용률 %')
for key, col, lab in (('ekf_node', '#c0392b', 'EKF(2 개 합)'), ('control+', '#2471a3', '컨트롤러'), ('localiz+', '#7d3c98', '위치 추정'), ('nvblox_+', '#16a085', 'nvblox')): a3.plot(bt, [b['p'].get(key, 0) for b in blocks], c=col, lw=1.2, label=lab + ' (코어 1 개 = 100)')
a3.axhline(100, c='#999', lw=.6, ls='--'); a3.set_ylim(0, 110); a3.set_ylabel('CPU'); a3.legend(fontsize=8, ncol=5, loc='lower left'); a3.set_xlabel('10:34:37 부터 경과 [s]  (27 s = 10:35:04 부터 부하 포화)')
a1.set_xlim(0, B - A); a1.set_title('f2f1 복귀, 상자 ② 주변 71 s — 로버가 멈칫거린 구간의 시간축', fontsize=11, loc='left')
fig.savefig('F:/6_Indoor_Rover/Rover/Docs/04_navigation/figures/2026-10-12_f2f1_box_stall.png', dpi=115, bbox_inches='tight'); print('ok', len(gaps))
