#!/usr/bin/env python3
"""[job776, 2026-10-01 §8.29] job452 + Ackermann 최소 회전 반경(ack_r>0 이면 |ω| ≤ |v|/ack_r — Nav2 1.1.x AckermannMotionModel::applyConstraints 와 같은 규칙, 표본·평균 제어 모두),
   후진 거리·제자리 회전 시간 집계 추가.
   ---- 이하 job452 원문 ----
   [job452, 2026-09-18 §17] job419(09-17 §14, Humble 1.1.20 동작 모드) 에 **CostCritic** 을 추가한 판. 원본 동작은 obst=0 으로 유지.
   obst=0: ObstaclesCritic(둘레 최대비용 → 거리 역산 → margin/repulsion) — 1.1.20 obstacles_critic.cpp
   obst=1: CostCritic(충돌은 차체 둘레 LETHAL, 점수는 **중심 칸 비용** 합/T × cost_w/254, 중심 ≥253 이면 crit_cost) — 1.1.20 cost_critic.cpp
   obst=2: 둘 다(사용자 질의 '주+보조' 재현용)
   추가: near_thr(두 크리틱의 near_goal_distance, 경로 끝 0.5 m 안에서 선호 항 끔 — 09-17 판에는 없던 것), t_abs(절대 epoch 로 시각 지정),
         LETHAL 여유(차체 외곽 ↔ 로컬 코스트맵 LETHAL 셀, 반셀 뺌) 주기별 기록 → 최소·평균 출력.
   나머지(잡음 고정·clip 없음·측정속도 스텝0·SG 필터·shift·구동계 지연/이득/smoother 가속·펌웨어 데드밴드)는 job419 그대로.
   인자: BAG t [key=val ...]  (t_abs=<epoch> 를 주면 t 는 무시)
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import Twist

BAG = sys.argv[1]; AT = float(sys.argv[2])
P = dict(vx_std=0.05, wz_std=0.3, temperature=0.3, gamma=0.015, iters=1, batch=1000, steps=32, dt=0.1,
         vx_max=0.08, vx_min=-0.06, wz_max=0.38,
         align_w=14.0, align_off=3, align_step=3, follow_w=5.0, follow_off=5, angle_w=2.0, angle_off=4, angle_max=0.5,
         rep_w=1.5, crit_w=20.0, margin=0.05, coll_cost=10000.0, fwd_w=5.0, infl_r=0.40, scale=2.5, r_in=0.175,
         goal_w=5.0, goal_thr=1.0, ga_w=3.0, ga_thr=0.4, follow_thr=0.6, align_thr=0.4, angle_thr=0.4, goal_yaw=0.0,
         db=0.0, promote=0.0, eps=0.003, track_b=0.443, prune=1.0,
         humble=0, cons_w=4.0, dyn_path=0, dyn_cost=0, regen=0,
         lag_steps=0, w_gain=1.0, v_gain=1.0, w_acc=0.0,
         obst=0, cost_w=3.81, crit_cost=300.0, cc_coll=1e6, near_thr=0.5, t_abs=0.0,   # 09-18: CostCritic·near_goal·절대 시각
         cycles=40, seed=1, label='', ack_r=0.0)
for a in sys.argv[3:]:
    k, v = a.split('='); P[k] = v if k in ('label', 'wobble_on') else float(v)
for k in ('iters', 'batch', 'steps', 'align_off', 'align_step', 'follow_off', 'angle_off', 'cycles', 'seed', 'lag_steps', 'humble', 'dyn_path', 'dyn_cost', 'regen', 'obst'):
    P[k] = int(P[k])
rng = np.random.default_rng(P['seed'])
HL, HW, PAD = 0.25, 0.165, 0.01


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
ob, lcs, tplans, cmds, gplans, mo = [], [], [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/local_costmap/costmap':
        lcs.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/transformed_global_plan':
        tplans.append((t, deserialize_message(data, Path)))
    elif topic == '/plan':
        gplans.append((t, deserialize_message(data, Path)))
    elif topic == '/cmd_vel':
        m = deserialize_message(data, Twist); cmds.append((t, m.linear.x, m.angular.z))
ob.sort(); mo.sort(); T0 = ob[0][0]
if P['t_abs'] > 0:
    AT = P['t_abs'] - T0


def latest(seq, t):
    ts = [s[0] for s in seq]; i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


t = T0 + AT
pose = latest(ob, t); gl = latest(lcs, t); tp = latest(tplans, t); cm = latest(cmds, t)
G = gl[1]; RES = G.info.resolution; OX, OY = G.info.origin.position.x, G.info.origin.position.y; W, H = G.info.width, G.info.height
grid = np.array(G.data, dtype=np.int16).reshape(H, W)
cost_tab = np.zeros(101); cost_tab[1:99] = 1.0 + (np.arange(1, 99) - 1) * 251.0 / 97.0; cost_tab[99] = 253.0; cost_tab[100] = 254.0
COST = np.where(grid < 0, 255.0, cost_tab[np.clip(grid, 0, 100)])
if tp is not None:
    path = np.array([[q.pose.position.x, q.pose.position.y] for q in tp[1].poses])
else:
    gp = latest(gplans, t); a = latest(mo, t)
    G_ = np.array([[q.pose.position.x, q.pose.position.y] for q in gp[1].poses])
    dx_, dy_ = G_[:, 0] - a[1], G_[:, 1] - a[2]; c_, s_ = math.cos(a[3]), math.sin(a[3])
    O_ = np.stack([dx_ * c_ + dy_ * s_, -dx_ * s_ + dy_ * c_], 1)
    k0 = int(np.argmin(np.hypot(O_[:, 0] - pose[1], O_[:, 1] - pose[2])))
    seg = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(O_[k0:], axis=0).T))])
    path = O_[k0:k0 + int(np.searchsorted(seg, P['prune'])) + 1]
x0, y0, th0 = pose[1], pose[2], pose[3]


def set_cost(tt):
    global G, RES, OX, OY, W, H, COST
    gl_ = latest(lcs, tt); G = gl_[1]; RES = G.info.resolution; OX, OY = G.info.origin.position.x, G.info.origin.position.y; W, H = G.info.width, G.info.height
    g_ = np.array(G.data, dtype=np.int16).reshape(H, W); COST = np.where(g_ < 0, 255.0, cost_tab[np.clip(g_, 0, 100)])
    return gl_[0]


def set_path(tt, rx_, ry_):
    global path
    gp_ = latest(gplans, tt); a_ = latest(mo, tt)
    G_ = np.array([[q.pose.position.x, q.pose.position.y] for q in gp_[1].poses])
    dx_, dy_ = G_[:, 0] - a_[1], G_[:, 1] - a_[2]; c_, s_ = math.cos(a_[3]), math.sin(a_[3])
    O_ = np.stack([dx_ * c_ + dy_ * s_, -dx_ * s_ + dy_ * c_], 1)
    k0_ = int(np.argmin(np.hypot(O_[:, 0] - rx_, O_[:, 1] - ry_)))
    seg_ = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(O_[k0_:], axis=0).T))])
    path = O_[k0_:k0_ + int(np.searchsorted(seg_, P['prune'])) + 1]
    if len(path) < 2: path = O_[-2:]
    return gp_[0]


DYN = dict(plans=set(), costs=set())
perim = np.array([(a, b) for a in np.linspace(-(HL + PAD), HL + PAD, 21) for b in (-(HW + PAD), HW + PAD)] +
                 [(a, b) for b in np.linspace(-(HW + PAD), HW + PAD, 15) for a in (-(HL + PAD), HL + PAD)])
POSS_INSCR = 253.0 * math.exp(-P['scale'] * (math.hypot(HL + PAD, HW + PAD) - P['r_in']))


def cell_cost(x, y):
    i = np.floor((x - OX) / RES).astype(int); j = np.floor((y - OY) / RES).astype(int)
    ok = (i >= 0) & (i < W) & (j >= 0) & (j < H)
    out = np.full(x.shape, 255.0); out[ok] = COST[j[ok], i[ok]]
    return out


def pose_costs(X, Y, TH):
    """(B,T) → (둘레 반영 비용, using_footprint, 중심 비용)"""
    c0 = cell_cost(X, Y); c = c0.copy(); fp = c >= POSS_INSCR
    if fp.any():
        xs = X[fp][:, None] + perim[None, :, 0] * np.cos(TH[fp])[:, None] - perim[None, :, 1] * np.sin(TH[fp])[:, None]
        ys = Y[fp][:, None] + perim[None, :, 0] * np.sin(TH[fp])[:, None] + perim[None, :, 1] * np.cos(TH[fp])[:, None]
        c[fp] = cell_cost(xs, ys).max(axis=1)
    return c, fp, c0


def lethal_clear(rx, ry, rth):
    """차체 외곽(패딩 없음) ↔ 1 m 안 LETHAL(254) 셀 중심 거리 최소 − 반셀 (job416 정의)."""
    jj, ii = np.where(COST == 254.0)
    if not jj.size: return float('nan')
    X = OX + (ii + 0.5) * RES - rx; Y = OY + (jj + 0.5) * RES - ry
    s = (np.abs(X) < 1.0) & (np.abs(Y) < 1.0)
    if not s.any(): return float('nan')
    c, sn = math.cos(-rth), math.sin(-rth); bx = X[s] * c - Y[s] * sn; by = X[s] * sn + Y[s] * c
    return float((np.hypot(np.maximum(np.abs(bx) - HL, 0), np.maximum(np.abs(by) - HW, 0)) - RES / 2).min())


def critics(X, Y, TH, V, Wz, rx, ry, rth):
    B, T = X.shape
    ex, ey, eth = X[:, -1], Y[:, -1], TH[:, -1]
    gx, gy = path[-1]; dgoal = math.hypot(gx - rx, gy - ry)
    near = dgoal < P['near_thr'] if P['near_thr'] > 0 else False
    # 충돌(공통): 둘레 LETHAL(중심 ≥ 외접 비용일 때만 둘레 검사)
    c, fp, c0 = pose_costs(X, Y, TH)
    coll = (c >= 254.0) | ((c == 253.0) & ~fp)
    traj_coll = coll.any(axis=1)
    obst = np.zeros(B)
    if P['obst'] in (0, 2):   # ObstaclesCritic
        d = (P['scale'] * P['r_in'] - np.log(np.clip(c, 1.0, 253.0)) + math.log(253.0)) / P['scale']
        d = np.where(fp, d, d - P['r_in'])
        inzone = (c >= 1.0) & ~coll
        crit = np.where(inzone & (d < P['margin']), P['margin'] - d, 0.0).sum(axis=1)
        rep = np.where(inzone & (d >= P['margin']), P['infl_r'] - d, 0.0).sum(axis=1) if not near else np.zeros(B)
        obst = obst + np.where(traj_coll, P['coll_cost'], P['crit_w'] * crit + P['rep_w'] * rep / T)
    if P['obst'] in (1, 2):   # CostCritic: 중심 칸 비용
        per = np.where(c0 < 1.0, 0.0, np.where(c0 >= 253.0, P['crit_cost'], c0))
        if near: per = np.where(c0 >= 253.0, P['crit_cost'], 0.0)
        obst = obst + np.where(traj_coll, P['cc_coll'], P['cost_w'] / 254.0 * per.sum(axis=1) / T)
    # 배치 furthest
    dend = np.hypot(ex[:, None] - path[None, :, 0], ey[:, None] - path[None, :, 1])
    near_idx = dend.argmin(axis=1); furthest = int(near_idx.max())
    if furthest >= P['align_off'] and dgoal >= P['align_thr']:
        js = np.arange(0, T, P['align_step'])
        dd = np.hypot(X[:, js][:, :, None] - path[None, None, :, 0], Y[:, js][:, :, None] - path[None, None, :, 1]).min(axis=2)
        align = P['align_w'] * dd.mean(axis=1)
    else:
        align = np.zeros(B)
    tf_ = path[min(furthest + P['follow_off'], len(path) - 1)]
    follow = P['follow_w'] * np.hypot(ex - tf_[0], ey - tf_[1]) if dgoal >= P['follow_thr'] else np.zeros(B)
    ta = path[min(furthest + P['angle_off'], len(path) - 1)]
    cur = abs(wrap(math.atan2(ta[1] - ry, ta[0] - rx) - rth))
    angle = P['angle_w'] * np.abs(wrap(np.arctan2(ta[1] - ey, ta[0] - ex) - eth)) if (cur > P['angle_max'] and dgoal >= P['angle_thr']) else np.zeros(B)
    goal = P['goal_w'] * np.hypot(ex - gx, ey - gy) if dgoal < P['goal_thr'] else np.zeros(B)
    gang = P['ga_w'] * np.abs(wrap(eth - P['goal_yaw'])) if dgoal < P['ga_thr'] else np.zeros(B)
    fwd = P['fwd_w'] * np.clip(-V, 0, None).sum(axis=1) * P['dt']
    total = obst + align + follow + angle + fwd + goal + gang
    return total, dict(obst=obst, align=align, follow=follow, angle=angle + goal + gang, fwd=fwd, dgoal=dgoal, coll=traj_coll, furthest=furthest, cur=cur, dend=np.hypot(ex - rx, ey - ry))


def rollout(V, Wz, rx, ry, rth):
    TH = rth + np.cumsum(Wz, axis=1) * P['dt']
    THp = np.concatenate([np.full((V.shape[0], 1), rth), TH[:, :-1]], axis=1)
    X = rx + np.cumsum(V * np.cos(THp), axis=1) * P['dt']; Y = ry + np.cumsum(V * np.sin(THp), axis=1) * P['dt']
    return X, Y, wrap(TH)


B, T = P['batch'], P['steps']
mean_v = np.full(T, cm[1] if cm else 0.0); mean_w = np.full(T, cm[2] if cm else 0.0)
rx, ry, rth = x0, y0, th0
W0LOG = []; PATHLEN = 0.0; MINCOST = []; CLEAR = []
CMDQ = [(mean_v[0], mean_w[0])] * P['lag_steps']; WCLOG = []
WPREV = [mean_w[0]]
ESSLOG = []
REACH = [None]
REV = [0.0]; SPIN = [0.0]
SGF = np.array([-21.0, 14.0, 39.0, 54.0, 59.0, 54.0, 39.0, 14.0, -21.0]) / 231.0
HIST = [(mean_v[0], mean_w[0])] * 4
MEAS = [mean_v[0] * P['v_gain'], mean_w[0] * P['w_gain']]
if P['humble']:
    NVF = rng.normal(0, P['vx_std'], (P['batch'], P['steps'])); NWF = rng.normal(0, P['wz_std'], (P['batch'], P['steps']))


def sg_filter(seq, h):
    s_ = seq.copy(); n = len(s_) - 1
    if n < 20: return s_
    f = lambda d: float(np.dot(d, SGF))
    s_[0] = f([h[0], h[1], h[2], h[3], s_[0], s_[1], s_[2], s_[3], s_[4]])
    s_[1] = f([h[1], h[2], h[3], s_[0], s_[1], s_[2], s_[3], s_[4], s_[5]])
    s_[2] = f([h[2], h[3], s_[0], s_[1], s_[2], s_[3], s_[4], s_[5], s_[6]])
    s_[3] = f([h[3], s_[0], s_[1], s_[2], s_[3], s_[4], s_[5], s_[6], s_[7]])
    i = 4
    while i != n - 4:
        s_[i] = f(s_[i - 4:i + 5]); i += 1
    i += 1; s_[i] = f([s_[i - 4], s_[i - 3], s_[i - 2], s_[i - 1], s_[i], s_[i + 1], s_[i + 2], s_[i + 3], s_[i + 3]])
    i += 1; s_[i] = f([s_[i - 4], s_[i - 3], s_[i - 2], s_[i - 1], s_[i], s_[i + 1], s_[i + 2], s_[i + 2], s_[i + 2]])
    i += 1; s_[i] = f([s_[i - 4], s_[i - 3], s_[i - 2], s_[i - 1], s_[i], s_[i + 1], s_[i + 1], s_[i + 1], s_[i + 1]])
    i += 1; s_[i] = f([s_[i - 4], s_[i - 3], s_[i - 2], s_[i - 1], s_[i], s_[i], s_[i], s_[i], s_[i]])
    return s_


print('%s bag %s t=%.1f 자세 (%.3f,%.3f) yaw %+.1f° 초기 cmd v %+.3f w %+.3f | 경로 %d점(간격 %.3f) | obst=%d %s' % (
    P['label'], BAG.split('/')[-1], AT, x0, y0, math.degrees(th0), mean_v[0], mean_w[0], len(path), np.hypot(*(path[1] - path[0])), P['obst'],
    ' '.join('%s=%g' % (k, P[k]) for k in ('vx_std', 'wz_std', 'temperature', 'iters', 'align_w', 'follow_w', 'follow_off', 'cost_w', 'crit_cost', 'near_thr'))))
print('  cyc |  cmd v    w  | 로버 x y yaw | furth | 충돌% | 끝단전방 중앙/최대 | 평균비용 obst align follow angle+goal | 최저후보 v w | 평균열 최대비용/충돌스텝 | LETHAL 여유')
for cyc in range(P['cycles']):
    _tt = T0 + AT + cyc * P['dt']
    if P['dyn_cost']: DYN['costs'].add(set_cost(_tt))
    if P['dyn_path'] == 1: set_path(T0 + AT, rx, ry)
    elif P['dyn_path'] == 2: DYN['plans'].add(set_path(_tt, rx, ry))
    for it in range(P['iters']):
        if P['humble']:
            if P['regen']:
                NVF = rng.normal(0, P['vx_std'], (B, T)); NWF = rng.normal(0, P['wz_std'], (B, T))
            V = mean_v[None, :] + NVF; Wz = mean_w[None, :] + NWF
            if P['ack_r'] > 0: _lim = np.abs(V) / P['ack_r']; Wz = np.clip(Wz, -_lim, _lim)
            Vs = np.concatenate([np.full((B, 1), MEAS[0]), V[:, :-1]], axis=1); Ws = np.concatenate([np.full((B, 1), MEAS[1]), Wz[:, :-1]], axis=1)
            X, Y, TH = rollout(Vs, Ws, rx, ry, rth)
            cost, m = critics(X, Y, TH, Vs, Ws, rx, ry, rth)
            cost = cost + P['cons_w'] * (np.clip(Vs - P['vx_max'], 0, None) + np.clip(P['vx_min'] - Vs, 0, None)).sum(axis=1) * P['dt']
        else:
            nv = rng.normal(0, P['vx_std'], (B, T)); nw = rng.normal(0, P['wz_std'], (B, T))
            V = np.clip(mean_v[None, :] + nv, P['vx_min'], P['vx_max']); Wz = np.clip(mean_w[None, :] + nw, -P['wz_max'], P['wz_max'])
            if P['ack_r'] > 0: _lim = np.abs(V) / P['ack_r']; Wz = np.clip(Wz, -_lim, _lim)
            X, Y, TH = rollout(V, Wz, rx, ry, rth)
            cost, m = critics(X, Y, TH, V, Wz, rx, ry, rth)
        bnv = V - mean_v[None, :]; bnw = Wz - mean_w[None, :]
        cost = cost + P['gamma'] / P['vx_std'] ** 2 * (mean_v[None, :] * bnv).sum(axis=1) + P['gamma'] / P['wz_std'] ** 2 * (mean_w[None, :] * bnw).sum(axis=1)
        cn = cost - cost.min(); wgt = np.exp(-cn / P['temperature']); wgt /= wgt.sum()
        if it == P['iters'] - 1: ESSLOG.append(1.0 / float((wgt ** 2).sum()))
        mean_v = (V * wgt[:, None]).sum(axis=0); mean_w = (Wz * wgt[:, None]).sum(axis=0)
        if P['humble']:
            mean_v = np.clip(mean_v, P['vx_min'], P['vx_max']); mean_w = np.clip(mean_w, -P['wz_max'], P['wz_max'])
            if P['ack_r'] > 0: _lim = np.abs(mean_v) / P['ack_r']; mean_w = np.clip(mean_w, -_lim, _lim)
    ib = int(np.argmin(cost))
    Xm, Ym, THm = rollout(mean_v[None, :], mean_w[None, :], rx, ry, rth)
    cm_, fpm, _ = pose_costs(Xm, Ym, THm); mean_max_cost = float(cm_.max()); mean_coll = int(np.argmax(cm_ >= 254.0)) if (cm_ >= 254.0).any() else -1
    fwd_end = (X[:, -1] - rx) * math.cos(rth) + (Y[:, -1] - ry) * math.sin(rth)
    clr = lethal_clear(rx, ry, rth); CLEAR.append(clr)
    if cyc % 2 == 0 or cyc == P['cycles'] - 1:
        print('  %3d | %+.3f %+.3f | %.3f %.3f %+5.1f° | %3d | %3.0f%% | %+.3f %+.3f | %6.2f %5.2f %5.2f %5.2f %5.2f | %+.3f %+.3f' % (
            cyc, mean_v[0], mean_w[0], rx, ry, math.degrees(rth), m['furthest'], 100 * m['coll'].mean(), np.median(fwd_end), fwd_end.max(),
            cost[~m['coll']].mean() if (~m['coll']).any() else 9999, m['obst'][~m['coll']].mean() if (~m['coll']).any() else 9999, m['align'].mean(), m['follow'].mean(), m['angle'].mean(), V[ib, 0], Wz[ib, 0]) + ' | %3.0f/%d | %.3f' % (mean_max_cost, mean_coll, clr))
    if P['humble']:
        mean_v = sg_filter(mean_v, [h[0] for h in HIST]); mean_w = sg_filter(mean_w, [h[1] for h in HIST])
        v0, w0 = mean_v[1], mean_w[1]; HIST = HIST[1:] + [(mean_v[1], mean_w[1])]
    else:
        v0, w0 = mean_v[0], mean_w[0]
    if P['w_acc'] > 0:
        _dw = P['w_acc'] * P['dt']; w0 = WPREV[0] + max(-_dw, min(_dw, w0 - WPREV[0]))
    WPREV[0] = w0; WCLOG.append(w0)
    CMDQ.append((v0, w0)); v0, w0 = CMDQ.pop(0) if len(CMDQ) > P['lag_steps'] else (0.0, 0.0)
    v0 *= P['v_gain']; w0 *= P['w_gain']
    if P['db'] > 0 or P['promote'] > 0:
        def fw(vw):
            if abs(vw) < P['eps']: return 0.0
            if abs(vw) < P['promote']: vw = math.copysign(P['promote'], vw)
            return 0.0 if abs(vw) < P['db'] else vw
        vl, vr = fw(v0 - w0 * P['track_b'] / 2), fw(v0 + w0 * P['track_b'] / 2)
        v0, w0 = (vl + vr) / 2, (vr - vl) / P['track_b']
    W0LOG.append(w0); PATHLEN += abs(v0) * P['dt']
    REV[0] += max(0.0, -v0) * P['dt']; SPIN[0] += P['dt'] if (abs(v0) < 0.01 and abs(w0) > 0.05) else 0.0
    MEAS = [v0, w0]
    rx += v0 * math.cos(rth) * P['dt']; ry += v0 * math.sin(rth) * P['dt']; rth = wrap(rth + w0 * P['dt'])
    if REACH[0] is None and math.hypot(path[-1][0] - rx, path[-1][1] - ry) < 0.15: REACH[0] = cyc + 1
    _c, _fp, _ = pose_costs(np.array([[rx]]), np.array([[ry]]), np.array([[rth]])); MINCOST.append(float(_c[0, 0]))
    mean_v = np.concatenate([mean_v[1:], mean_v[-1:]]); mean_w = np.concatenate([mean_w[1:], mean_w[-1:]])
dx = (rx - x0) * math.cos(th0) + (ry - y0) * math.sin(th0); dy = -(rx - x0) * math.sin(th0) + (ry - y0) * math.cos(th0)
print('     후진 거리 %.3f m · 제자리 회전 시간 %.1f s · 경로 끝 도달 %s 주기' % (REV[0], SPIN[0], REACH[0]))
print('  → %d 주기(%.1f s) 후: 전진 %+.3f 횡 %+.3f 회전 %+.1f°, 최종 cmd v %+.3f w %+.3f' % (P['cycles'], P['cycles'] * P['dt'], dx, dy, math.degrees(wrap(rth - th0)), mean_v[0], mean_w[0]))


def _wob(_w):
    _w = np.asarray(_w); _s = np.where(np.abs(_w) > 0.05, np.sign(_w), 0); _nz = _s[_s != 0]
    _fl = int(np.sum(_nz[1:] != _nz[:-1])) if _nz.size > 1 else 0
    _hf = _w - np.convolve(_w, np.ones(10) / 10, mode='same')
    return _fl, (float(np.sqrt(np.mean(_hf[5:-5] ** 2))) if _w.size > 12 else 0.0)


_fc, _rc = _wob(WCLOG); _fa, _ra = _wob(W0LOG)
_cl = np.array([c for c in CLEAR if not math.isnan(c)])
if P['dyn_path'] or P['dyn_cost']: print('     동적 입력: /plan %d 개, 코스트맵 %d 개 사용 (dyn_path=%d dyn_cost=%d)' % (len(DYN['plans']), len(DYN['costs']), P['dyn_path'], P['dyn_cost']))
print('     유효 표본 수 ESS 중앙 %.1f (10/90%% %.1f/%.1f) / 배치 %d → 첫 제어 ω 표본 잡음 추정 wz_std/√ESS = %.3f rad/s' % (np.median(ESSLOG), np.percentile(ESSLOG, 10), np.percentile(ESSLOG, 90), P['batch'], P['wz_std'] / math.sqrt(np.median(ESSLOG))))
print('     흔들림: |ω|>0.05 반전 명령 %d 회 = %.1f 회/m, 차체 %d 회 = %.1f 회/m (이동 %.3f m) | 고주파 RMS 명령 %.3f 차체 %.3f rad/s | 최대 둘레비용 %.0f' % (
    _fc, _fc / max(PATHLEN, 0.01), _fa, _fa / max(PATHLEN, 0.01), PATHLEN, _rc, _ra, max(MINCOST) if MINCOST else 0))
print('     LETHAL 여유(차체 외곽↔1 m 안 LETHAL 셀, 반셀 뺌): 최소 %.3f @%.1f s, 평균 %.3f, 끝 %.3f m' % (
    (_cl.min() if _cl.size else float('nan')), (float(np.nanargmin(CLEAR)) * P['dt'] if _cl.size else 0), (_cl.mean() if _cl.size else float('nan')), CLEAR[-1]))
print('     목표(경로 끝, prune 창 안이면) 까지 거리 %.3f m (xy tol 0.15), 로버 odom (%.3f, %.3f), 허용오차 첫 진입 %s' % (math.hypot(path[-1][0] - rx, path[-1][1] - ry), rx, ry, ('%.1f s' % (REACH[0] * P['dt'])) if REACH[0] else '없음'))
