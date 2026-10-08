# 10-08 §2: '전역에 nvblox 를 넣었다면' — 순회 bag 에서 카메라만 본 장애물 칸(유령 후보)과 상자 ② 첫 표시 시각.
#   인자: bag 디렉터리 [출력 접두]
#   카메라만 본 칸 = nvblox 슬라이스 거리 ≤ 0.05 m 칸 중 (a) 저장 지도 벽에서 0.15 m 넘게 떨어진 빈 곳 (b) 같은 시각 라이다 점에서 0.10 m 넘게 떨어진 곳.
import math, sys, time, numpy as np
from pathlib import Path
from scipy import ndimage
from scipy.spatial import cKDTree
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts = get_typestore(Stores.ROS2_HUMBLE)
ts.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
LX, LYAW = 0.152, math.pi - 0.04677
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo = ob = M = None; scan = None; last = 0; cells = {}; box2 = []; plans = []
with AnyReader([Path(sys.argv[1])], default_typestore=ts) as r:
    con = [c for c in r.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice', '/map', '/scan', '/plan')]
    for c, t_ns, raw in r.messages(connections=con):
        t = t_ns * 1e-9
        if c.topic == '/plan': plans.append(t); continue
        m = r.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for x in m.transforms:
                k = (x.header.frame_id, x.child_frame_id); v = (x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
                if k == ('map', 'odom'): mo = v
                elif k == ('odom', 'base_link'): ob = v
            continue
        if c.topic == '/map':   # 첫 지도만 씀(위치 추정 모드가 10 s 마다 다시 발행 — 첫 판은 그 메시지를 슬라이스로 잘못 처리해 멈춤)
            if M is None:
                g = np.asarray(m.data, np.int16).reshape(m.info.height, m.info.width); M = (g, m.info.resolution, m.info.origin.position.x, m.info.origin.position.y)
                free = (g >= 0) & (g < 50); WALLD = ndimage.distance_transform_edt(free) * m.info.resolution
            continue
        if c.topic == '/scan': scan = m; continue
        if M is None or mo is None or ob is None or scan is None or t - last < 1.0: continue
        last = t; d = np.asarray(m.data, np.float32).reshape(m.height, m.width); res = m.resolution
        jy, ix = np.nonzero((d <= 0.05) & (d != m.unknown_value))
        qx, qy = m.origin.x + (ix + .5) * res, m.origin.y + (jy + .5) * res
        cm, sm = math.cos(mo[2]), math.sin(mo[2]); X, Y = mo[0] + cm * qx - sm * qy, mo[1] + sm * qx + cm * qy
        rx, ry, rth = mo[0] + cm * ob[0] - sm * ob[1], mo[1] + sm * ob[0] + cm * ob[1], mo[2] + ob[2]
        rr = np.asarray(scan.ranges, np.float32); a = scan.angle_min + scan.angle_increment * np.arange(len(rr)) + LYAW; ok = np.isfinite(rr) & (rr > .05) & (rr < 6)
        bx, by = LX + rr[ok] * np.cos(a[ok]), rr[ok] * np.sin(a[ok]); c_, s_ = math.cos(rth), math.sin(rth)
        P = np.c_[rx + c_ * bx - s_ * by, ry + s_ * bx + c_ * by]; dl, _ = cKDTree(P).query(np.c_[X, Y])
        g, mres, mox, moy = M; mi, mj = ((X - mox) / mres).astype(int), ((Y - moy) / mres).astype(int)
        inm = (mi >= 0) & (mi < g.shape[1]) & (mj >= 0) & (mj < g.shape[0]); wd = np.zeros(len(X)); wd[inm] = WALLD[mj[inm], mi[inm]]
        sel = (wd > 0.15) & (dl > 0.10)
        for kx, ky in set(zip(np.round(X[sel] / 0.1).astype(int), np.round(Y[sel] / 0.1).astype(int))):
            e = cells.setdefault((kx, ky), [t, t, 0]); e[1] = t; e[2] += 1
        b2 = int(((X > 1.05) & (X < 1.35) & (Y > -0.30) & (Y < 0.10)).sum()); box2.append((t, rx, ry, b2))
# 묶음(8 이웃)
keys = list(cells); idx = {k: i for i, k in enumerate(keys)}; lab = [-1] * len(keys); nlab = 0
for i, k in enumerate(keys):
    if lab[i] >= 0: continue
    st = [i]; lab[i] = nlab
    while st:
        j = st.pop(); kx, ky = keys[j]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = idx.get((kx + dx, ky + dy))
                if n is not None and lab[n] < 0: lab[n] = nlab; st.append(n)
    nlab += 1
g, mres, mox, moy = M; T0 = box2[0][0] if box2 else 0
print('== 카메라만 본 장애물 묶음(0.1 m 칸, 저장 지도 벽 0.15 m 밖·라이다 0.10 m 밖) — 지속 10 s 넘거나 칸 4 개 이상만')
rows = []
for L in range(nlab):
    ks = [keys[i] for i in range(len(keys)) if lab[i] == L]; t0 = min(cells[k][0] for k in ks); t1 = max(cells[k][1] for k in ks); fr = max(cells[k][2] for k in ks)
    cx, cy = np.mean([k[0] for k in ks]) * 0.1, np.mean([k[1] for k in ks]) * 0.1
    w = WALLD[int((cy - moy) / mres), int((cx - mox) / mres)] if 0 <= int((cy - moy) / mres) < g.shape[0] and 0 <= int((cx - mox) / mres) < g.shape[1] else 0
    if t1 - t0 > 10 or len(ks) >= 4: rows.append((len(ks), t1 - t0, fr, cx, cy, w, t0))
for n, dur, fr, cx, cy, w, t0 in sorted(rows, key=lambda r: -r[0] * r[1]):
    print('  중심 map (%5.2f, %5.2f) · 칸 %3d · 지속 %5.0f s(관측 프레임 최대 %3d) · 벽까지 %.2f m%s · 처음 %s' % (cx, cy, n, dur, fr, w, ' ← 통로(반폭 ≤ 0.5)' if w <= 0.5 else '', time.strftime('%H:%M:%S', time.localtime(t0))))
np.savez(sys.argv[2] if len(sys.argv) > 2 else 'whatif.npz', rows=np.array([r[:6] for r in rows]), map=g, meta=np.array([mres, mox, moy]), keys=np.array(keys), lab=np.array(lab), dur=np.array([cells[k][1]-cells[k][0] for k in keys]))
print('== 상자 ② 자리 nvblox 칸 첫 표시(복귀 구간) · 경로 발행 시각')
seen = [(t, x, y, b) for t, x, y, b in box2 if b > 0]
for t, x, y, b in seen[:1] + seen[-1:]: print('  %s 로버 (%.2f, %.2f) 상자 ② 칸 %d' % (time.strftime('%H:%M:%S', time.localtime(t)), x, y, b))
print('  경로 발행:', ' '.join(time.strftime('%H:%M:%S', time.localtime(p)) for p in plans[-6:]))
