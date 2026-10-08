# 10-08 §4: 주행 중 '도는' 구간 전부(제자리·피벗·호) — 회전축 위치, 트랙 속도, 미끄러짐을 같은 잣대로 비교.
#   실제 자세 = 스캔 직접 정합(구간 첫 스캔 기준, 초기값 = 연속 정합 사슬). SLAM/EKF 안 씀.
#   미끄러짐 = 실제 이동 − 휠 추측항법 이동(전진 속도 = (vL+vR)/2 측정값, 방향은 스캔 각을 써서 '병진 미끄러짐'만 남김).
#   순간 회전축 = 0.6 s 창 차체 속도로 정지점 p = (−vy/ω, vx/ω), 차체(base_link = 트랙 길이 중점·좌우 중심) 좌표.
#   인자: bag...   출력: 구간별 한 줄 + rot2_<bag>.npz
import math, re, sys, numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
ts = get_typestore(Stores.ROS2_HUMBLE)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
L2B = (0.152, 0.0, math.pi - 0.04677)

def load(bag):
    S, C, ST = [], [], []
    with AnyReader([Path(bag)], default_typestore=ts) as r:
        con = [c for c in r.connections if c.topic in ('/scan', '/cmd_vel', '/rover/status')]
        for c, t_ns, raw in r.messages(connections=con):
            t = t_ns * 1e-9
            if c.topic == '/rover/status':   # micro-ROS 끝 군더더기 바이트로 역직렬화 거부 → 문자열 직접(L, R 순)
                f = re.findall(rb'tgt=(-?\d+) v=(-?\d+) d=(-?\d+)', raw)
                if len(f) >= 2: ST.append((t,) + tuple(int(x) for x in f[0] + f[1]))
                continue
            m = r.deserialize(raw, c.msgtype)
            if c.topic == '/scan':
                rr = np.asarray(m.ranges, float); a = m.angle_min + np.arange(len(rr)) * m.angle_increment
                ok = np.isfinite(rr) & (rr > 0.35) & (rr < 8.0); S.append((t, rr[ok], a[ok]))
            else: C.append((t, m.linear.x, m.angular.z))
    return S, np.array(C), np.array(ST, float)

def pts(s):
    _, rr, a = s; x, y = rr * np.cos(a), rr * np.sin(a); c, sn = math.cos(L2B[2]), math.sin(L2B[2])
    return np.c_[L2B[0] + c * x - sn * y, L2B[1] + sn * x + c * y]

def icp(P0, P1, th0, t0=(0, 0)):
    th, t, tree = th0, np.array(t0, float), cKDTree(P0); gate = 0.5
    for _ in range(40):
        c, s = math.cos(th), math.sin(th); Q = P1 @ np.array([[c, s], [-s, c]]) + t
        d, i = tree.query(Q); k = d < gate
        if k.sum() > 20: k &= d <= np.quantile(d[k], 0.8)
        A, B = P1[k], P0[i[k]]; ma, mb = A.mean(0), B.mean(0); H = (A - ma).T @ (B - mb)
        th = math.atan2(H[0, 1] - H[1, 0], H[0, 0] + H[1, 1]); c, s = math.cos(th), math.sin(th)
        t = mb - np.array([[c, -s], [s, c]]) @ ma; gate = max(0.08, gate * 0.7)
    return th, t, float(np.sqrt(np.mean(d[k] ** 2)))

def segments(C, wmin=0.15, dmin=2.0):
    on = np.abs(C[:, 2]) >= wmin; out = []; s = last = None
    for (t, v, w), o in zip(C, on):
        if o and s is None: s = t
        if o: last = t
        if s is not None and not o and t - last > 0.4:
            if last - s >= dmin: out.append((s, last))
            s = None
    if s is not None and last - s >= dmin: out.append((s, last))
    return out

rows = []
if __name__ != "__main__": sys.argv = sys.argv[:1]
for bag in sys.argv[1:]:
    S, C, ST = load(bag); st = np.array([s[0] for s in S]); name = Path(bag).name.replace('bag_', ''); T0 = S[0][0]
    for a, b in segments(C):
        idx = list(range(np.searchsorted(st, a), np.searchsorted(st, b) + 1))
        if len(idx) < 8: continue
        X = [np.zeros(3)]; Pp = pts(S[idx[0]])
        for j0, j1 in zip(idx[:-1], idx[1:]):
            kc = (C[:, 0] >= S[j0][0] - 0.2) & (C[:, 0] < S[j1][0]); P1 = pts(S[j1])
            th, t, _ = icp(Pp, P1, C[kc, 2].mean() * (S[j1][0] - S[j0][0]) if kc.any() else 0)
            x, y, h = X[-1]; c, s = math.cos(h), math.sin(h); X.append(np.array([x + c * t[0] - s * t[1], y + s * t[0] + c * t[1], h + th])); Pp = P1
        X = np.array(X); P0 = pts(S[idx[0]]); Xd = [np.zeros(3)]; rmss = []
        for kk, j in enumerate(idx[1:], 1):
            th, t, rms = icp(P0, pts(S[j]), X[kk, 2], X[kk, :2]); Xd.append(np.array([t[0], t[1], th])); rmss.append(rms)
        X = np.array(Xd); X[:, 2] = np.unwrap(X[:, 2]); T = st[idx]
        # 휠 추측항법(방향 = 스캔 각)
        vl = np.interp(T, ST[:, 0], ST[:, 2]) / 1000; vr = np.interp(T, ST[:, 0], ST[:, 5]) / 1000; vw = (vl + vr) / 2
        D = np.zeros(2)
        for kk in range(len(T) - 1):
            h = (X[kk, 2] + X[kk + 1, 2]) / 2; D += vw[kk] * (T[kk + 1] - T[kk]) * np.array([math.cos(h), math.sin(h)])
        E = X[-1, :2] - D; dth = X[-1, 2]
        # 순간 회전축
        icr = []
        for kk in range(len(X) - 6):
            dt = T[kk + 6] - T[kk]; w_ = (X[kk + 6, 2] - X[kk, 2]) / dt
            if abs(w_) < 0.15: continue
            h = X[kk, 2]; c, s = math.cos(h), math.sin(h); d = X[kk + 6, :2] - X[kk, :2]
            icr.append((-(-s * d[0] + c * d[1]) / dt / w_, (c * d[0] + s * d[1]) / dt / w_))
        icr = np.array(icr) if icr else np.full((1, 2), np.nan)
        k = (ST[:, 0] >= a) & (ST[:, 0] <= b); cv = C[(C[:, 0] >= a) & (C[:, 0] <= b)]
        Lm, Rm = ST[k, 2].mean() / 1000, ST[k, 5].mean() / 1000
        ix, iy = np.nanmedian(icr[:, 0]), np.nanmedian(icr[:, 1])
        kind = '제자리' if abs(iy) < 0.06 else ('피벗형' if abs(iy) < 0.25 else '호')
        per = math.hypot(*E) * math.pi / max(abs(dth), 0.2)
        rows.append((name, a - T0, b - a, cv[:, 1].mean(), cv[:, 2].mean(), math.degrees(dth), Lm, Rm, ix, iy, E[0], E[1], per, max(rmss), kind))
        np.savez('rot2_%s_%d.npz' % (name, int(a - T0)), T=T, X=X, icr=icr, vl=vl, vr=vr)
if len(sys.argv) > 1: print('bag  시작s 길이s | 지령 v   w   | 회전°  | 트랙 측정 L    R    m/s | 회전축(차체) 앞 왼 cm | 미끄러짐(실제−휠) 앞 왼 cm | 180°당 cm | 정합rms최대 | 종류')
for r in sorted(rows, key=lambda r: r[-1]):
    print('%-5s %5.0f %4.1f | %+.3f %+.2f | %+6.1f | %+.3f %+.3f | %+6.1f %+6.1f | %+6.1f %+6.1f | %5.1f | %.3f | %s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8] * 100, r[9] * 100, r[10] * 100, r[11] * 100, r[12] * 100, r[13], r[14]))
np.save('rot2_rows.npy', np.array([r[1:14] for r in rows], float))
