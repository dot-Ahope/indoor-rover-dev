# 10-08 §3.3: f2e1(B: 전역 nvblox + 재계획 0.5 Hz) — 상자 ②: nvblox 첫 표시 → 상자를 피하는 새 경로까지 시간, 경로 ↔ 상자 칸 거리; 재계획 수·경로 옆 변화
import math, sys, time, numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts = get_typestore(Stores.ROS2_HUMBLE)
ts.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
K = lambda t: time.strftime('%H:%M:%S', time.localtime(t))
mo = ob = None; plans = []; box = []; boxcells = None; last = 0
with AnyReader([Path(sys.argv[1])], default_typestore=ts) as r:
    con = [c for c in r.connections if c.topic in ('/tf', '/nvblox_node/static_map_slice', '/plan')]
    for c, t_ns, raw in r.messages(connections=con):
        t = t_ns * 1e-9; m = r.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for x in m.transforms:
                k = (x.header.frame_id, x.child_frame_id); v = (x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
                if k == ('map', 'odom'): mo = v
                elif k == ('odom', 'base_link'): ob = v
        elif c.topic == '/plan':
            plans.append((t, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses]), (mo, ob)))
        elif mo is not None and t - last >= 0.5:
            last = t; d = np.asarray(m.data, np.float32).reshape(m.height, m.width); res = m.resolution
            jy, ix = np.nonzero((d <= 0.05) & (d != m.unknown_value)); qx, qy = m.origin.x + (ix + .5) * res, m.origin.y + (jy + .5) * res
            cm, sm = math.cos(mo[2]), math.sin(mo[2]); X, Y = mo[0] + cm * qx - sm * qy, mo[1] + sm * qx + cm * qy
            sel = (X > 1.0) & (X < 1.45) & (Y > -0.25) & (Y < 0.20)   # 상자 ② 자리(넉넉히)
            box.append((t, np.c_[X[sel], Y[sel]]))
def rpos(mo, ob):
    c, s = math.cos(mo[2]), math.sin(mo[2]); return mo[0] + c * ob[0] - s * ob[1], mo[1] + s * ob[0] + c * ob[1]
first = next(((t, b) for t, b in box if len(b) >= 2), None)
print('경로 발행 %d 회' % len(plans))
if first:
    t0, B0 = first; print('상자 ② nvblox 첫 표시 %s (칸 %d, 중심 %.2f, %.2f)' % (K(t0), len(B0), *B0.mean(0)))
    # 이후 경로마다: 상자 칸(그 시각 최신)과 경로(로버 앞 남은 부분) 최소 거리
    for t, P, (mo_, ob_) in plans:
        if t < t0 - 20: continue
        bi = max([i for i, (tb, _) in enumerate(box) if tb <= t] or [0]); Bc = box[bi][1]
        rx, ry = rpos(mo_, ob_); j = np.argmin(np.hypot(P[:, 0] - rx, P[:, 1] - ry)); Pa = P[j:]
        dmin = np.hypot(Pa[:, None, 0] - Bc[None, :, 0], Pa[:, None, 1] - Bc[None, :, 1]).min() if len(Bc) and len(Pa) else float('nan')
        q = Pa[(Pa[:, 0] > 0.9) & (Pa[:, 0] < 1.6)]
        print('  %s (+%5.1f s) 로버 (%.2f,%.2f) | 경로 ↔ 상자 ② 칸 최소 %.2f m (칸 %d) | 경로가 x 0.9~1.6 에서 지나는 y %s' % (K(t), t - t0, rx, ry, dmin, len(Bc), ('%.2f~%.2f' % (q[:, 1].min(), q[:, 1].max())) if len(q) else '-'))
# 경로 옆 변화(연속 경로끼리, 공통 구간에서 최대 옆 거리)
flips = 0
for (t1, P1, _), (t2, P2, _) in zip(plans, plans[1:]):
    if np.hypot(*(P1[-1] - P2[-1])) > 0.2 or len(P1) < 2 or len(P2) < 2: continue   # 다른 목표
    d = np.hypot(P2[:, None, 0] - P1[None, :, 0], P2[:, None, 1] - P1[None, :, 1]).min(1).max()
    if d > 0.3: flips += 1; print('  옆 변화 %.2f m: %s → %s' % (d, K(t1), K(t2)))
print('같은 목표 안 0.3 m 넘는 경로 변화 %d 회' % flips)
print('== 상자 ② 자리 nvblox 칸 위치(복귀 구간)')
for tt in (t0 + 169, t0 + 175, t0 + 185, t0 + 195, t0 + 205, t0 + 215):
    bi = min(range(len(box)), key=lambda i: abs(box[i][0] - tt)); B = box[bi][1]
    print('  %s 칸 %2d' % (K(box[bi][0]), len(B)) + ('  x %.2f~%.2f · y %.2f~%.2f' % (B[:, 0].min(), B[:, 0].max(), B[:, 1].min(), B[:, 1].max()) if len(B) else ''))
