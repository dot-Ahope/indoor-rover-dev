#!/usr/bin/env python3
"""상자 옆 여유가 어디서 줄어드는가 — 원경로(NavFn) → 스무딩(SimpleSmoother 재현) → 실제(MPPI) 분해 (2026-09-18 §15).
인자: NAME BAG GOAL_EPOCH [NAME BAG GOAL_EPOCH ...]

- 기준 코스트맵: 전역(map 프레임, 로버가 그 x 에 도착한 시각의 최신 메시지). 세 단계를 같은 코스트맵으로 잰다.
- 여유 = 차체 외곽(반길이 0.25·반폭 0.165) ↔ 상자 영역(map x 0.9~1.6, y −0.35~+0.2) LETHAL 셀 중심 거리 − 반셀 (job416 과 같은 정의).
- 목표 x X* = 1.10/1.15/1.20/1.25(복귀 회전 자리, §12.3)와 1.35/1.45/1.55(상자 뒤 모서리).
  로버가 X* 에 처음 닿은 시각 t_arr. 그 L 초 전(L = 3, 2) 마지막 /plan(원경로)을 X* 에서 보간(y, 접선 방향)해 차체를 놓는다.
  NavFn 은 매 계획을 로버 현재 자리에서 시작하므로 L=0 은 의미 없다(계획 = 로버 자리).
- 스무딩: bag 에 스무딩 결과가 없다 → nav2_smoother SimpleSmoother(Humble) 를 그대로 옮겨 원경로에 적용.
  w_data 0.2·w_smooth 0.3(기본값, YAML 미지정), tolerance 1e-10, max_its 1000, 정밀화 4 회, 점별 중심 비용 > 252 면 그 반복 직전 경로로 중단.
  중심 비용은 계획 시각의 전역 코스트맵(발행값 99/100 = 253/254 로 환산).
  ★ 가정: 방향 전환 구간 분할은 생략(이 코스는 전진만). 스무더 서버의 충돌 검사(footprint LETHAL)는 여유 계산으로 대신 본다.
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid, Path
HL, HW = 0.25, 0.165
XS = [1.10, 1.15, 1.20, 1.25, 1.35, 1.45, 1.55]
LEADS = [3.0, 2.0]


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def load(bag, G):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    ob, mo, gcs, plans = [], {}, [], []
    while r.has_next():
        topic, data, ts = r.read_next(); t = ts * 1e-9 - G
        if topic == '/tf':
            for tr in deserialize_message(data, TFMessage).transforms:
                st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
                v = (st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation))
                if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                    ob.append(v)
                elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                    mo[round(st, 4)] = v        # 같은 stamp 두 번 → 마지막 값
        elif topic == '/global_costmap/costmap' and -3 < t < 45:
            gcs.append((t, deserialize_message(data, OccupancyGrid)))
        elif topic == '/plan' and -1 < t < 45:
            m = deserialize_message(data, Path)
            plans.append((t, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
    ob.sort(); mo = sorted(mo.values())
    return ob, mo, gcs, plans


def pose_fn(ob, mo):
    obt = [o[0] for o in ob]; mot = [m[0] for m in mo]

    def at(t):
        _, ox, oy, oth = ob[min(max(bisect.bisect_left(obt, t), 0), len(ob) - 1)]
        _, ax, ay, ath = mo[min(max(bisect.bisect_right(mot, t) - 1, 0), len(mo) - 1)]
        return (ax + ox * math.cos(ath) - oy * math.sin(ath), ay + ox * math.sin(ath) + oy * math.cos(ath), ath + oth)
    return at


def latest(seq, t):
    ts = [s[0] for s in seq]; k = bisect.bisect_right(ts, t) - 1
    return seq[k] if k >= 0 else None


def grid(m):
    d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)
    return d, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution


def box_cells(m):
    d, ox, oy, res = grid(m); jj, ii = np.where(d >= 100)
    X = ox + (ii + 0.5) * res; Y = oy + (jj + 0.5) * res
    s = (X > 0.9) & (X < 1.6) & (Y > -0.35) & (Y < 0.2)
    return X[s], Y[s], res


def clear(cells, x, y, th):
    X, Y, res = cells
    if X.size == 0:
        return float('nan')
    c, s = math.cos(-th), math.sin(-th); dx, dy = X - x, Y - y
    rx, ry = dx * c - dy * s, dx * s + dy * c
    return float((np.hypot(np.maximum(np.abs(rx) - HL, 0), np.maximum(np.abs(ry) - HW, 0)) - res / 2).min())


def center_cost(m):
    d, ox, oy, res = grid(m)

    def cost(x, y):
        i = int((x - ox) / res); j = int((y - oy) / res)
        if i < 0 or j < 0 or i >= d.shape[1] or j >= d.shape[0]:
            return 255
        v = int(d[j, i])
        return 255 if v < 0 else (254 if v >= 100 else (253 if v >= 99 else int(round(v * 252 / 98))))
    return cost


def smooth_impl(P, cost, dw=0.2, sw=0.3, tol=1e-10, max_its=1000, ctr=0):
    """nav2_smoother SimpleSmoother::smoothImpl (Humble) 이식. P: (N,2) 원 데이터."""
    new = P.copy(); last = P.copy(); its = 0; change = tol + 1
    while change >= tol:
        its += 1; change = 0.0
        if its >= max_its:
            return last, False
        for i in range(1, len(P) - 1):
            for j in range(2):
                yi = new[i, j]; yo = yi
                yi += dw * (P[i, j] - yi) + sw * (new[i + 1, j] + new[i - 1, j] - 2.0 * yi)
                new[i, j] = yi; change += abs(yi - yo)
            c = cost(new[i, 0], new[i, 1])
            if c > 252 and c != 255:
                return last, False
        last = new.copy()
    if ctr < 4:
        new, _ = smooth_impl(new, cost, dw, sw, tol, max_its, ctr + 1)
    return new, True


def at_x(P, xs, x0):
    """경로를 로버 계획 시작점 이후 처음으로 x = xs 를 지나는 자리에서 보간 → (y, 접선 방향)."""
    for k in range(len(P) - 1):
        a, b = P[k], P[k + 1]
        if (a[0] - xs) * (b[0] - xs) <= 0 and a[0] != b[0] and max(a[0], b[0]) >= x0:
            u = (xs - a[0]) / (b[0] - a[0]); y = a[1] + u * (b[1] - a[1])
            k0, k1 = max(k - 2, 0), min(k + 3, len(P) - 1)
            th = math.atan2(P[k1, 1] - P[k0, 1], P[k1, 0] - P[k0, 0])
            return y, th
    return float('nan'), float('nan')


a = sys.argv[1:]
summary = []
for k in range(0, len(a), 3):
    name, bag, G = a[k], a[k + 1], float(a[k + 2])
    ob, mo, gcs, plans = load(bag, G); at = pose_fn(ob, mo)
    T = np.arange(0, 40, 0.05); PX = np.array([at(t)[0] for t in T])
    print('==== %s: /plan %d, 전역 코스트맵 %d' % (name, len(plans), len(gcs)))
    print('   X*   | 도착 t | 실제 y  방향 여유   | L | 원경로 y 방향 여유  | 스무딩 y 방향 여유 (수렴) | 원→스무딩 Δ여유 | 스무딩→실제 Δ여유')
    cache = {}
    for xs in XS:
        idx = np.where(PX >= xs)[0]
        if not idx.size:
            continue
        ta = float(T[idx[0]]); p = at(ta); gc = latest(gcs, ta)
        cells = box_cells(gc[1]); ca = clear(cells, *p)
        for L in LEADS:
            pl = latest(plans, ta - L)
            if pl is None:
                continue
            tp, P = pl
            if tp not in cache:
                g0 = latest(gcs, tp) or gcs[0]
                S, ok = smooth_impl(P, center_cost(g0[1])); cache[tp] = (S, ok)
            S, ok = cache[tp]; x0 = at(tp)[0]
            yr, thr = at_x(P, xs, x0); ys, ths = at_x(S, xs, x0)
            cr = clear(cells, xs, yr, thr) if not math.isnan(yr) else float('nan')
            cs = clear(cells, xs, ys, ths) if not math.isnan(ys) else float('nan')
            print('  %.2f | %5.1f | %+.3f %+5.1f° %.3f | %.0f | %+.3f %+5.1f° %.3f | %+.3f %+5.1f° %.3f (%s) | %+.3f | %+.3f' % (
                xs, ta, p[1], math.degrees(p[2]), ca, L, yr, math.degrees(thr), cr, ys, math.degrees(ths), cs, 'Y' if ok else 'N', cs - cr, ca - cs))
            summary.append((name, xs, L, cr, cs, ca))
S = np.array([(x, L, cr, cs, ca) for _, x, L, cr, cs, ca in summary], dtype=float)
print('==== 통합 (구간별 평균, 단위 cm)')
for lo, hi, lab in ((1.09, 1.26, '복귀 회전 자리 x 1.10~1.25'), (1.34, 1.56, '상자 뒤 모서리 x 1.35~1.55')):
    for L in LEADS:
        s = (S[:, 0] > lo) & (S[:, 0] < hi) & (S[:, 1] == L) & np.isfinite(S[:, 2]) & np.isfinite(S[:, 3])
        if s.any():
            print('  %s, L=%.0f s (%d 표본): 원경로 %.1f → 스무딩 %.1f → 실제 %.1f | 스무딩 Δ %+.1f, 컨트롤러 Δ %+.1f' % (
                lab, L, s.sum(), 100 * S[s, 2].mean(), 100 * S[s, 3].mean(), 100 * S[s, 4].mean(), 100 * (S[s, 3] - S[s, 2]).mean(), 100 * (S[s, 4] - S[s, 3]).mean()))
