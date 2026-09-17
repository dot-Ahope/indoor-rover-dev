#!/usr/bin/env python3
"""[job419, 2026-09-17 §14] humble=1 이면 nav2_mppi_controller 1.1.20 소스 대조로 확인한 동작을 따른다:
   (a) 노이즈는 목표 시작/reset 때 한 번만 생성해 모든 주기·반복에 재사용(regenerate_noises 기본 false)
   (b) 후보 제어를 한계로 자르지 않는다 — vx 초과분은 ConstraintCritic(4·Σ초과·dt), wz 는 벌점 없음. 평균열만 갱신 뒤 clip
   (c) 롤아웃 속도: 스텝 0 = 측정 속도(odom twist), 스텝 k = 제어 k−1 (DiffDrive::predict)
   (d) 최적화 뒤 Savitzky-Golay 9점 필터(적용 제어 이력 4개, idx 27 건너뜀 포함) → 출력 = 제어열[1] (shift_control_sequence: 주기=model_dt) → 이력 갱신 → roll −1
   humble=0 이면 job410 과 같다(매 반복 새 잡음·후보 clip·출력 [0]).

MPPI 오프라인 시뮬레이터 — bag 의 정지 장면(로컬 코스트맵·변환 경로·자세)에서 Humble MPPI 의 배치·크리틱·softmax 갱신을
   그대로 흉내 내어, 파라미터 변형별로 명령 평균이 0 으로 붕괴하는지/출구를 찾는지 본다 (2026-09-16, 사용자 질문:
   "회피 로직과 추종 로직이 무엇이 충돌하는가, 과한 값인가").

  Humble 의미론(nav2_mppi_controller 1.1.x):
    - 잡음: 스텝마다 독립 N(0, std), 제어 = 평균열 + 잡음 → 한계로 클리핑
    - furthest_reached_path_point: **배치 전체**에서 끝단이 닿은 경로 index 의 최대값 (모든 크리틱이 공유)
    - PathAlign: furthest ≥ offset 일 때만, trajectory_point_step 마다 경로 최근접거리 평균 × w
    - PathFollow: 끝단 ↔ path[furthest+offset] 거리 × w   / PathAngle: 현재자세→path[furthest+offset] 각 > max 일 때 끝단 heading 오차 × w
    - Obstacles: 둘레 최대비용 → 거리 → repulsion/critical, LETHAL 이면 collision_cost
    - 갱신: cost += gamma/std² Σ mean·noise ; w_i = softmax(−(cost−min)/temperature) ; 평균열 = Σ w_i·제어_i ; 한 스텝 shift
    - 로버는 첫 제어를 dt 동안 적용해 움직인다(정적 장면)
  인자: BAG t [key=val ...]   keys: vx_std wz_std temperature gamma iters batch steps dt align_w align_off follow_w follow_off
        angle_w angle_off angle_max rep_w crit_w margin coll_cost fwd_w cycles seed
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
         humble=0, cons_w=4.0, dyn_path=0, dyn_cost=0, regen=0,   # regen=1: regenerate_noises true (매 반복 새 잡음)   # dyn_path 1=같은 /plan 을 매 주기 로버 기준 재가지치기(Humble transformGlobalPlan), 2=+bag 의 /plan·map->odom 시간 재생 / dyn_cost 1=bag 로컬 코스트맵 시간 재생   # 09-17 §14: Humble 1.1.20 동작 모드, ConstraintCritic 가중
         lag_steps=0, w_gain=1.0, v_gain=1.0, w_acc=0.0,   # w_acc: velocity_smoother max_accel wz (1.2 rad/s²), 0 = 제한 없음   # 09-17: 실측 명령ω→EKF ω 지연 0.10 s·이득 0.68~0.75 (job409)
         cycles=40, seed=1, label='')
for a in sys.argv[3:]:
    k, v = a.split('='); P[k] = v if k in ('label', 'wobble_on') else float(v)
for k in ('iters', 'batch', 'steps', 'align_off', 'align_step', 'follow_off', 'angle_off', 'cycles', 'seed', 'lag_steps', 'humble', 'dyn_path', 'dyn_cost', 'regen'):
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


def latest(seq, t):
    ts = [s[0] for s in seq]; i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


t = T0 + AT
pose = latest(ob, t); gl = latest(lcs, t); tp = latest(tplans, t); cm = latest(cmds, t)
G = gl[1]; RES = G.info.resolution; OX, OY = G.info.origin.position.x, G.info.origin.position.y; W, H = G.info.width, G.info.height
grid = np.array(G.data, dtype=np.int16).reshape(H, W)
cost_tab = np.zeros(101); cost_tab[1:99] = 1.0 + (np.arange(1, 99) - 1) * 251.0 / 97.0; cost_tab[99] = 253.0; cost_tab[100] = 254.0
COST = np.where(grid < 0, 255.0, cost_tab[np.clip(grid, 0, 100)])   # (H, W) costmap_2d 비용
if tp is not None:
    path = np.array([[q.pose.position.x, q.pose.position.y] for q in tp[1].poses])
else:
    # 09-17: visualize off 이면 /transformed_global_plan 이 없다 → /plan(map) 을 odom 으로 옮기고 로버 최근접점부터 prune m 만 남긴다
    gp = latest(gplans, t); a = latest(mo, t)
    G_ = np.array([[q.pose.position.x, q.pose.position.y] for q in gp[1].poses])
    dx_, dy_ = G_[:, 0] - a[1], G_[:, 1] - a[2]; c_, s_ = math.cos(a[3]), math.sin(a[3])
    O_ = np.stack([dx_ * c_ + dy_ * s_, -dx_ * s_ + dy_ * c_], 1)
    k0 = int(np.argmin(np.hypot(O_[:, 0] - pose[1], O_[:, 1] - pose[2])))
    seg = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(O_[k0:], axis=0).T))])
    path = O_[k0:k0 + int(np.searchsorted(seg, P['prune'])) + 1]
x0, y0, th0 = pose[1], pose[2], pose[3]

def set_cost(tt):
    """09-17 §14: bag 로컬 코스트맵을 시각 tt 것으로 교체 (발행 2 Hz — 실제 갱신 5 Hz 보다 성김)."""
    global G, RES, OX, OY, W, H, COST
    gl_ = latest(lcs, tt); G = gl_[1]; RES = G.info.resolution; OX, OY = G.info.origin.position.x, G.info.origin.position.y; W, H = G.info.width, G.info.height
    g_ = np.array(G.data, dtype=np.int16).reshape(H, W); COST = np.where(g_ < 0, 255.0, cost_tab[np.clip(g_, 0, 100)])
    return gl_[0]


def set_path(tt, rx_, ry_):
    """/plan(map) → map->odom(tt) 로 odom 변환 → 로버 최근접점부터 prune m. 반환: 사용한 /plan 수신 시각."""
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
    """(B,T) → 비용, using_footprint"""
    c = cell_cost(X, Y); fp = c >= POSS_INSCR
    if fp.any():
        xs = X[fp][:, None] + perim[None, :, 0] * np.cos(TH[fp])[:, None] - perim[None, :, 1] * np.sin(TH[fp])[:, None]
        ys = Y[fp][:, None] + perim[None, :, 0] * np.sin(TH[fp])[:, None] + perim[None, :, 1] * np.cos(TH[fp])[:, None]
        c[fp] = cell_cost(xs, ys).max(axis=1)
    return c, fp


def critics(X, Y, TH, V, Wz, rx, ry, rth):
    B, T = X.shape
    # Obstacles
    c, fp = pose_costs(X, Y, TH)
    coll = (c >= 254.0) | ((c == 253.0) & ~fp)
    traj_coll = coll.any(axis=1)
    d = (P['scale'] * P['r_in'] - np.log(np.clip(c, 1.0, 253.0)) + math.log(253.0)) / P['scale']
    d = np.where(fp, d, d - P['r_in'])
    inzone = (c >= 1.0) & ~coll
    crit = np.where(inzone & (d < P['margin']), P['margin'] - d, 0.0).sum(axis=1)
    rep = np.where(inzone & (d >= P['margin']), P['infl_r'] - d, 0.0).sum(axis=1)
    obst = np.where(traj_coll, P['coll_cost'], P['crit_w'] * crit + P['rep_w'] * rep / T)
    # 배치 furthest
    ex, ey, eth = X[:, -1], Y[:, -1], TH[:, -1]
    dend = np.hypot(ex[:, None] - path[None, :, 0], ey[:, None] - path[None, :, 1])
    near_idx = dend.argmin(axis=1); furthest = int(near_idx.max())
    gx, gy = path[-1]; dgoal = math.hypot(gx - rx, gy - ry)
    # PathAlign (목표 근처에서는 꺼짐)
    if furthest >= P['align_off'] and dgoal >= P['align_thr']:
        js = np.arange(0, T, P['align_step'])
        dd = np.hypot(X[:, js][:, :, None] - path[None, None, :, 0], Y[:, js][:, :, None] - path[None, None, :, 1]).min(axis=2)
        align = P['align_w'] * dd.mean(axis=1)
    else:
        align = np.zeros(B)
    # PathFollow
    tf_ = path[min(furthest + P['follow_off'], len(path) - 1)]
    follow = P['follow_w'] * np.hypot(ex - tf_[0], ey - tf_[1]) if dgoal >= P['follow_thr'] else np.zeros(B)
    # PathAngle
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
    THp = np.concatenate([np.full((V.shape[0], 1), rth), TH[:, :-1]], axis=1)   # 스텝 시작 heading
    X = rx + np.cumsum(V * np.cos(THp), axis=1) * P['dt']; Y = ry + np.cumsum(V * np.sin(THp), axis=1) * P['dt']
    return X, Y, wrap(TH)


B, T = P['batch'], P['steps']
mean_v = np.full(T, cm[1] if cm else 0.0); mean_w = np.full(T, cm[2] if cm else 0.0)
rx, ry, rth = x0, y0, th0
W0LOG = []; PATHLEN = 0.0; MINCOST = []   # 09-17 흔들림 지표
CMDQ = [(mean_v[0], mean_w[0])] * P['lag_steps']; WCLOG = []
WPREV = [mean_w[0]]
ESSLOG = []   # softmax 유효 표본 수 1/Σw² (마지막 반복) — 평균 제어열의 표본 잡음 ≈ std/√ESS
REACH = [None]
SGF = np.array([-21.0, 14.0, 39.0, 54.0, 59.0, 54.0, 39.0, 14.0, -21.0]) / 231.0
HIST = [(mean_v[0], mean_w[0])] * 4          # 적용 제어 이력(중간 시작이므로 bag 명령으로 채움)
MEAS = [mean_v[0] * P['v_gain'], mean_w[0] * P['w_gain']]   # 측정 속도(odom twist) 근사
if P['humble']:
    NVF = rng.normal(0, P['vx_std'], (P['batch'], P['steps'])); NWF = rng.normal(0, P['wz_std'], (P['batch'], P['steps']))


def sg_filter(seq, h):
    """utils::savitskyGolayFilter (Humble 1.1.20) 을 그대로 — 제자리 갱신, 끝단 반복, idx 27 건너뜀."""
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
   # 목표 xy 허용오차(0.15) 안에 처음 들어온 주기 — goal checker 대용
print('%s bag %s t=%.1f 자세 (%.3f,%.3f) yaw %+.1f° 초기 cmd v %+.3f w %+.3f | 경로 %d점(간격 %.3f) | 파라미터 %s' % (
    P['label'], BAG.split('/')[-1], AT, x0, y0, math.degrees(th0), mean_v[0], mean_w[0], len(path), np.hypot(*(path[1] - path[0])),
    ' '.join('%s=%g' % (k, P[k]) for k in ('vx_std', 'wz_std', 'temperature', 'iters', 'align_w', 'align_off', 'follow_w', 'follow_off', 'angle_w', 'angle_max', 'rep_w'))))
print('  cyc |  cmd v    w  | 로버 x y yaw | furth | 충돌% | 끝단전방 중앙/최대 | 평균비용 obst align follow angle+goal | 최저후보 v w | 평균열 최대비용/충돌스텝')
for cyc in range(P['cycles']):
    _tt = T0 + AT + cyc * P['dt']
    if P['dyn_cost']: DYN['costs'].add(set_cost(_tt))
    if P['dyn_path'] == 1: set_path(T0 + AT, rx, ry)
    elif P['dyn_path'] == 2: DYN['plans'].add(set_path(_tt, rx, ry))
    for it in range(P['iters']):
        if P['humble']:
            if P['regen']:
                NVF = rng.normal(0, P['vx_std'], (B, T)); NWF = rng.normal(0, P['wz_std'], (B, T))
            V = mean_v[None, :] + NVF; Wz = mean_w[None, :] + NWF          # (a)(b) 고정 잡음, clip 없음
            Vs = np.concatenate([np.full((B, 1), MEAS[0]), V[:, :-1]], axis=1); Ws = np.concatenate([np.full((B, 1), MEAS[1]), Wz[:, :-1]], axis=1)   # (c)
            X, Y, TH = rollout(Vs, Ws, rx, ry, rth)
            cost, m = critics(X, Y, TH, Vs, Ws, rx, ry, rth)
            cost = cost + P['cons_w'] * (np.clip(Vs - P['vx_max'], 0, None) + np.clip(P['vx_min'] - Vs, 0, None)).sum(axis=1) * P['dt']
        else:
            nv = rng.normal(0, P['vx_std'], (B, T)); nw = rng.normal(0, P['wz_std'], (B, T))
            V = np.clip(mean_v[None, :] + nv, P['vx_min'], P['vx_max']); Wz = np.clip(mean_w[None, :] + nw, -P['wz_max'], P['wz_max'])
            X, Y, TH = rollout(V, Wz, rx, ry, rth)
            cost, m = critics(X, Y, TH, V, Wz, rx, ry, rth)
        bnv = V - mean_v[None, :]; bnw = Wz - mean_w[None, :]
        cost = cost + P['gamma'] / P['vx_std'] ** 2 * (mean_v[None, :] * bnv).sum(axis=1) + P['gamma'] / P['wz_std'] ** 2 * (mean_w[None, :] * bnw).sum(axis=1)
        cn = cost - cost.min(); wgt = np.exp(-cn / P['temperature']); wgt /= wgt.sum()
        if it == P['iters'] - 1: ESSLOG.append(1.0 / float((wgt ** 2).sum()))
        mean_v = (V * wgt[:, None]).sum(axis=0); mean_w = (Wz * wgt[:, None]).sum(axis=0)
        if P['humble']:   # applyControlSequenceConstraints
            mean_v = np.clip(mean_v, P['vx_min'], P['vx_max']); mean_w = np.clip(mean_w, -P['wz_max'], P['wz_max'])
    ib = int(np.argmin(cost))
    # 평균 제어열을 굴린 궤적의 위험: 둘레 최대비용(254=LETHAL) 과 첫 충돌 스텝
    Xm, Ym, THm = rollout(mean_v[None, :], mean_w[None, :], rx, ry, rth)
    cm_, fpm = pose_costs(Xm, Ym, THm); mean_max_cost = float(cm_.max()); mean_coll = int(np.argmax(cm_ >= 254.0)) if (cm_ >= 254.0).any() else -1
    fwd_end = (X[:, -1] - rx) * math.cos(rth) + (Y[:, -1] - ry) * math.sin(rth)
    if cyc % 2 == 0 or cyc == P['cycles'] - 1:
        print('  %3d | %+.3f %+.3f | %.3f %.3f %+5.1f° | %3d | %3.0f%% | %+.3f %+.3f | %6.2f %5.2f %5.2f %5.2f %5.2f | %+.3f %+.3f' % (
            cyc, mean_v[0], mean_w[0], rx, ry, math.degrees(rth), m['furthest'], 100 * m['coll'].mean(), np.median(fwd_end), fwd_end.max(),
            cost[~m['coll']].mean() if (~m['coll']).any() else 9999, m['obst'][~m['coll']].mean() if (~m['coll']).any() else 9999, m['align'].mean(), m['follow'].mean(), m['angle'].mean(), V[ib, 0], Wz[ib, 0]) + ' | %3.0f/%d' % (mean_max_cost, mean_coll))
    # 로버 이동(첫 제어) + shift
    if P['humble']:   # (d) SG 필터 → 출력 [1] → 이력
        mean_v = sg_filter(mean_v, [h[0] for h in HIST]); mean_w = sg_filter(mean_w, [h[1] for h in HIST])
        v0, w0 = mean_v[1], mean_w[1]; HIST = HIST[1:] + [(mean_v[1], mean_w[1])]
    else:
        v0, w0 = mean_v[0], mean_w[0]
    # 09-17 구동계 모델: 명령은 lag_steps 주기 늦게, 이득 곱해 적용 (MPPI 내부 롤아웃은 이를 모른다 — 실제와 같음)
    if P['w_acc'] > 0:   # velocity_smoother max_accel wz (상류 — 이 값이 bag 의 /cmd_vel 에 해당)
        _dw = P['w_acc'] * P['dt']; w0 = WPREV[0] + max(-_dw, min(_dw, w0 - WPREV[0]))
    WPREV[0] = w0; WCLOG.append(w0)
    CMDQ.append((v0, w0)); v0, w0 = CMDQ.pop(0) if len(CMDQ) > P['lag_steps'] else (0.0, 0.0)
    v0 *= P['v_gain']; w0 *= P['w_gain']
    if P['db'] > 0 or P['promote'] > 0:   # 09-17: 펌웨어 휠 속도 처리 모델 (microros_task 승격 → speed_controller 정지 문턱)
        def fw(vw):
            if abs(vw) < P['eps']: return 0.0
            if abs(vw) < P['promote']: vw = math.copysign(P['promote'], vw)
            return 0.0 if abs(vw) < P['db'] else vw
        vl, vr = fw(v0 - w0 * P['track_b'] / 2), fw(v0 + w0 * P['track_b'] / 2)
        v0, w0 = (vl + vr) / 2, (vr - vl) / P['track_b']
    W0LOG.append(w0); PATHLEN += abs(v0) * P['dt']
    MEAS = [v0, w0]   # 다음 주기 측정 속도 = 차체에 실제로 걸린 속도(지연·이득·펌웨어 반영)
    rx += v0 * math.cos(rth) * P['dt']; ry += v0 * math.sin(rth) * P['dt']; rth = wrap(rth + w0 * P['dt'])
    if REACH[0] is None and math.hypot(path[-1][0] - rx, path[-1][1] - ry) < 0.15: REACH[0] = cyc + 1
    _c, _fp = pose_costs(np.array([[rx]]), np.array([[ry]]), np.array([[rth]])); MINCOST.append(float(_c[0, 0]))
    mean_v = np.concatenate([mean_v[1:], mean_v[-1:]]); mean_w = np.concatenate([mean_w[1:], mean_w[-1:]])
dx = (rx - x0) * math.cos(th0) + (ry - y0) * math.sin(th0); dy = -(rx - x0) * math.sin(th0) + (ry - y0) * math.cos(th0)
print('  → %d 주기(%.1f s) 후: 전진 %+.3f 횡 %+.3f 회전 %+.1f°, 최종 cmd v %+.3f w %+.3f' % (P['cycles'], P['cycles'] * P['dt'], dx, dy, math.degrees(wrap(rth - th0)), mean_v[0], mean_w[0]))
def _wob(_w):
    _w = np.asarray(_w); _s = np.where(np.abs(_w) > 0.05, np.sign(_w), 0); _nz = _s[_s != 0]
    _fl = int(np.sum(_nz[1:] != _nz[:-1])) if _nz.size > 1 else 0
    _hf = _w - np.convolve(_w, np.ones(10) / 10, mode='same')
    return _fl, (float(np.sqrt(np.mean(_hf[5:-5] ** 2))) if _w.size > 12 else 0.0)
_fc, _rc = _wob(WCLOG); _fa, _ra = _wob(W0LOG)
if P['dyn_path'] or P['dyn_cost']: print('     동적 입력: /plan %d 개, 코스트맵 %d 개 사용 (dyn_path=%d dyn_cost=%d)' % (len(DYN['plans']), len(DYN['costs']), P['dyn_path'], P['dyn_cost']))
print('     유효 표본 수 ESS 중앙 %.1f (10/90%% %.1f/%.1f) / 배치 %d → 첫 제어 ω 표본 잡음 추정 wz_std/√ESS = %.3f rad/s' % (np.median(ESSLOG), np.percentile(ESSLOG, 10), np.percentile(ESSLOG, 90), P['batch'], P['wz_std'] / math.sqrt(np.median(ESSLOG))))
print('     흔들림: |ω|>0.05 반전 명령 %d 회 = %.1f 회/m, 차체 %d 회 = %.1f 회/m (이동 %.3f m) | 고주파 RMS 명령 %.3f 차체 %.3f rad/s | 최대 둘레비용 %.0f' % (
    _fc, _fc / max(PATHLEN, 0.01), _fa, _fa / max(PATHLEN, 0.01), PATHLEN, _rc, _ra, max(MINCOST) if MINCOST else 0))
print('     목표(경로 끝, prune 창 안이면) 까지 거리 %.3f m (xy tol 0.15), 로버 odom (%.3f, %.3f), 허용오차 첫 진입 %s' % (math.hypot(path[-1][0] - rx, path[-1][1] - ry), rx, ry, ('%.1f s' % (REACH[0] * P['dt'])) if REACH[0] else '없음'))
