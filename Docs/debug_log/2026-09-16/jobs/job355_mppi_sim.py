#!/usr/bin/env python3
"""MPPI 오프라인 시뮬레이터 — bag 의 정지 장면(로컬 코스트맵·변환 경로·자세)에서 Humble MPPI 의 배치·크리틱·softmax 갱신을
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
         cycles=40, seed=1, label='')
for a in sys.argv[3:]:
    k, v = a.split('='); P[k] = v if k == 'label' else float(v)
for k in ('iters', 'batch', 'steps', 'align_off', 'align_step', 'follow_off', 'angle_off', 'cycles', 'seed'):
    P[k] = int(P[k])
rng = np.random.default_rng(P['seed'])
HL, HW, PAD = 0.25, 0.165, 0.01


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
ob, lcs, tplans, cmds = [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/local_costmap/costmap':
        lcs.append((t, deserialize_message(data, OccupancyGrid)))
    elif topic == '/transformed_global_plan':
        tplans.append((t, deserialize_message(data, Path)))
    elif topic == '/cmd_vel':
        m = deserialize_message(data, Twist); cmds.append((t, m.linear.x, m.angular.z))
ob.sort(); T0 = ob[0][0]


def latest(seq, t):
    ts = [s[0] for s in seq]; i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


t = T0 + AT
pose = latest(ob, t); gl = latest(lcs, t); tp = latest(tplans, t); cm = latest(cmds, t)
G = gl[1]; RES = G.info.resolution; OX, OY = G.info.origin.position.x, G.info.origin.position.y; W, H = G.info.width, G.info.height
grid = np.array(G.data, dtype=np.int16).reshape(H, W)
cost_tab = np.zeros(101); cost_tab[1:99] = 1.0 + (np.arange(1, 99) - 1) * 251.0 / 97.0; cost_tab[99] = 253.0; cost_tab[100] = 254.0
COST = np.where(grid < 0, 255.0, cost_tab[np.clip(grid, 0, 100)])   # (H, W) costmap_2d 비용
path = np.array([[q.pose.position.x, q.pose.position.y] for q in tp[1].poses])
x0, y0, th0 = pose[1], pose[2], pose[3]
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
    # PathAlign
    if furthest >= P['align_off']:
        js = np.arange(0, T, P['align_step'])
        dd = np.hypot(X[:, js][:, :, None] - path[None, None, :, 0], Y[:, js][:, :, None] - path[None, None, :, 1]).min(axis=2)
        align = P['align_w'] * dd.mean(axis=1)
    else:
        align = np.zeros(B)
    # PathFollow
    tf_ = path[min(furthest + P['follow_off'], len(path) - 1)]
    follow = P['follow_w'] * np.hypot(ex - tf_[0], ey - tf_[1])
    # PathAngle
    ta = path[min(furthest + P['angle_off'], len(path) - 1)]
    cur = abs(wrap(math.atan2(ta[1] - ry, ta[0] - rx) - rth))
    angle = P['angle_w'] * np.abs(wrap(np.arctan2(ta[1] - ey, ta[0] - ex) - eth)) if cur > P['angle_max'] else np.zeros(B)
    fwd = P['fwd_w'] * np.clip(-V, 0, None).sum(axis=1) * P['dt']
    total = obst + align + follow + angle + fwd
    return total, dict(obst=obst, align=align, follow=follow, angle=angle, fwd=fwd, coll=traj_coll, furthest=furthest, cur=cur, dend=np.hypot(ex - rx, ey - ry))


def rollout(V, Wz, rx, ry, rth):
    TH = rth + np.cumsum(Wz, axis=1) * P['dt']
    THp = np.concatenate([np.full((V.shape[0], 1), rth), TH[:, :-1]], axis=1)   # 스텝 시작 heading
    X = rx + np.cumsum(V * np.cos(THp), axis=1) * P['dt']; Y = ry + np.cumsum(V * np.sin(THp), axis=1) * P['dt']
    return X, Y, wrap(TH)


B, T = P['batch'], P['steps']
mean_v = np.full(T, cm[1] if cm else 0.0); mean_w = np.full(T, cm[2] if cm else 0.0)
rx, ry, rth = x0, y0, th0
print('%s bag %s t=%.1f 자세 (%.3f,%.3f) yaw %+.1f° 초기 cmd v %+.3f w %+.3f | 경로 %d점(간격 %.3f) | 파라미터 %s' % (
    P['label'], BAG.split('/')[-1], AT, x0, y0, math.degrees(th0), mean_v[0], mean_w[0], len(path), np.hypot(*(path[1] - path[0])),
    ' '.join('%s=%g' % (k, P[k]) for k in ('vx_std', 'wz_std', 'temperature', 'iters', 'align_w', 'align_off', 'follow_w', 'follow_off', 'angle_w', 'angle_max', 'rep_w'))))
print('  cyc |  cmd v    w  | 로버 x y yaw | furth | 충돌% | 끝단전방 중앙/최대 | 평균비용 obst align follow angle | 최저후보 v w | 평균열 최대비용/충돌스텝')
for cyc in range(P['cycles']):
    for it in range(P['iters']):
        nv = rng.normal(0, P['vx_std'], (B, T)); nw = rng.normal(0, P['wz_std'], (B, T))
        V = np.clip(mean_v[None, :] + nv, P['vx_min'], P['vx_max']); Wz = np.clip(mean_w[None, :] + nw, -P['wz_max'], P['wz_max'])
        X, Y, TH = rollout(V, Wz, rx, ry, rth)
        cost, m = critics(X, Y, TH, V, Wz, rx, ry, rth)
        bnv = V - mean_v[None, :]; bnw = Wz - mean_w[None, :]
        cost = cost + P['gamma'] / P['vx_std'] ** 2 * (mean_v[None, :] * bnv).sum(axis=1) + P['gamma'] / P['wz_std'] ** 2 * (mean_w[None, :] * bnw).sum(axis=1)
        cn = cost - cost.min(); wgt = np.exp(-cn / P['temperature']); wgt /= wgt.sum()
        mean_v = (V * wgt[:, None]).sum(axis=0); mean_w = (Wz * wgt[:, None]).sum(axis=0)
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
    v0, w0 = mean_v[0], mean_w[0]
    rx += v0 * math.cos(rth) * P['dt']; ry += v0 * math.sin(rth) * P['dt']; rth = wrap(rth + w0 * P['dt'])
    mean_v = np.concatenate([mean_v[1:], mean_v[-1:]]); mean_w = np.concatenate([mean_w[1:], mean_w[-1:]])
dx = (rx - x0) * math.cos(th0) + (ry - y0) * math.sin(th0); dy = -(rx - x0) * math.sin(th0) + (ry - y0) * math.cos(th0)
print('  → %d 주기(%.1f s) 후: 전진 %+.3f 횡 %+.3f 회전 %+.1f°, 최종 cmd v %+.3f w %+.3f' % (P['cycles'], P['cycles'] * P['dt'], dx, dy, math.degrees(wrap(rth - th0)), mean_v[0], mean_w[0]))
