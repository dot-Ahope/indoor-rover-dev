#!/usr/bin/env python3
"""조향 흔들림 분석 (2026-09-17, mp9·mp10·mp11 bag). 로버는 움직이지 않는다.

  명령 ω (/cmd_vel, velocity_smoother 출력 20 Hz) 와 실제 yaw rate (/odometry/filtered, 카메라 자이로 융합) 를 goal 이후 주행 구간에서 비교.
  - 부호반전: |ω| 문턱 0.01 / 0.05 / 0.10 별, 구간별(시작프레임 전진 x: 접근 <0.6, 통로 0.6~1.45, 복귀 ≥1.45), 1 m 당
  - 흔들림 성분: ω − 1.0 s 이동평균 의 RMS (의도된 조향을 뺀 고주파), 반전 간격(주기) 중앙값
  - 실제 yaw rate 의 같은 지표 → 명령 흔들림이 차체로 전달되는지
  - 원인 후보와의 시간 일치: (a) map->odom 점프(>1 cm 또는 >0.5°) (b) /plan 수신(1 Hz 재계획) — 반전 ±0.3 s 안에 든 비율
  인자: BAG GOAL_EPOCH [BAG GOAL_EPOCH ...]
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def load(bag, G):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    cmd, odo, mo, plans, ob = [], [], [], [], []
    while r.has_next():
        topic, data, ts = r.read_next(); t = ts * 1e-9 - G
        if topic == '/cmd_vel':
            m = deserialize_message(data, get_message(types[topic])); cmd.append((t, m.linear.x, m.angular.z))
        elif topic == '/odometry/filtered':
            m = deserialize_message(data, get_message(types[topic])); odo.append((t, m.twist.twist.linear.x, m.twist.twist.angular.z))
        elif topic == '/plan':
            plans.append(t)
        elif topic == '/tf':
            m = deserialize_message(data, get_message(types[topic]))
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                    mo.append((t, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob.append((t, tr.transform.translation.x, tr.transform.translation.y))
    return cmd, odo, mo, plans, ob


def resample(seq, t0, t1, dt=0.05, idx=2):
    ts = np.array([s[0] for s in seq]); vs = np.array([s[idx] for s in seq])
    grid = np.arange(t0, t1, dt)
    k = np.clip(np.searchsorted(ts, grid, side='right') - 1, 0, len(ts) - 1)
    return grid, vs[k]


def flips(w, v, thr):
    s = np.where(np.abs(w) > thr, np.sign(w), 0)
    mov = np.abs(v) > 0.03
    idx = [i for i in range(len(s)) if s[i] != 0 and mov[i]]
    out = []
    for a, b in zip(idx, idx[1:]):
        if s[a] != s[b]:
            out.append(b)
    return out


print('%-8s %-12s | %28s | %28s | %s' % ('run', '구간', '명령ω 반전/m (|ω|>.01 .05 .10)', '실제 yaw 반전/m (.01 .05 .10)', '고주파 RMS 명령/실제, 반전간격 중앙'))
args = sys.argv[1:]
for k in range(0, len(args), 2):
    bag, G = args[k], float(args[k + 1]); name = bag.split('_')[-1]
    cmd, odo, mo, plans, ob = load(bag, G)
    tend = max(c[0] for c in cmd if abs(c[1]) > 0.02)
    grid, wc = resample(cmd, 0.0, tend); _, vc = resample(cmd, 0.0, tend, idx=1)
    _, wo = resample(odo, 0.0, tend); _, vo = resample(odo, 0.0, tend, idx=1)
    # 위치(odom) → 전진 거리 구간
    obt = np.array([o[0] for o in ob]); obx = np.array([o[1] for o in ob]); oby = np.array([o[2] for o in ob])
    kk = np.clip(np.searchsorted(obt, grid, side='right') - 1, 0, len(obt) - 1)
    X = obx[kk]; Y = oby[kk]
    step = np.hypot(np.diff(X, prepend=X[0]), np.diff(Y, prepend=Y[0]))
    regions = [('전체', np.ones_like(X, bool)), ('접근 <0.6', X < 0.6), ('통로 0.6~1.45', (X >= 0.6) & (X < 1.45)), ('복귀 ≥1.45', X >= 1.45)]
    ma = lambda a: np.convolve(a, np.ones(20) / 20, mode='same')
    hc = wc - ma(wc); ho = wo - ma(wo)
    for rname, m in regions:
        dist = step[m].sum()
        if dist < 0.05:
            continue
        fc = [len([i for i in flips(np.where(m, wc, 0), vc, thr) if m[i]]) / dist for thr in (0.01, 0.05, 0.10)]
        fo = [len([i for i in flips(np.where(m, wo, 0), vo, thr) if m[i]]) / dist for thr in (0.01, 0.05, 0.10)]
        fl = flips(np.where(m, wc, 0), vc, 0.05); fl = [i for i in fl if m[i]]
        per = np.median(np.diff(grid[fl])) if len(fl) > 2 else float('nan')
        print('%-8s %-12s | %8.1f %8.1f %8.1f   | %8.1f %8.1f %8.1f   | %.3f / %.3f rad/s, %.2f s (%.2f m)' % (
            name, rname, *fc, *fo, np.sqrt(np.mean(hc[m] ** 2)), np.sqrt(np.mean(ho[m] ** 2)), per, dist))
    # 원인 후보 시간 일치 (전체 구간, |ω|>0.05 반전)
    fl = flips(wc, vc, 0.05); ft = grid[fl]
    mot = np.array([o[0] for o in mo]); jumps = []
    for i in range(1, len(mo)):
        if mo[i][0] < 0 or mo[i][0] > tend: continue
        d = math.hypot(mo[i][1] - mo[i - 1][1], mo[i][2] - mo[i - 1][2]); a = abs(math.degrees((mo[i][3] - mo[i - 1][3] + math.pi) % (2 * math.pi) - math.pi))
        if d > 0.01 or a > 0.5: jumps.append(mo[i][0])
    pl = [p for p in plans if 0 <= p <= tend]
    near = lambda ts, events: sum(1 for t in ts if any(abs(t - e) <= 0.3 for e in events)) / max(len(ts), 1)
    # 무작위 기준선: 같은 수의 반전을 균일 분포로 놓았을 때 우연 일치율
    rng = np.random.default_rng(0); rt = rng.uniform(0, tend, (200, max(len(ft), 1)))
    base_p = np.mean([near(r, pl) for r in rt]); base_j = np.mean([near(r, jumps) for r in rt]) if jumps else 0
    print('%-8s 원인 일치: |ω|>.05 반전 %d 회 | /plan 수신 %d 회 → 반전 ±0.3 s 안 %.0f%% (우연 기준 %.0f%%) | map->odom 점프 %d 회 → %.0f%% (우연 %.0f%%)' % (
        name, len(ft), len(pl), 100 * near(ft, pl), 100 * base_p, len(jumps), 100 * near(ft, jumps), 100 * base_j))
    print()
