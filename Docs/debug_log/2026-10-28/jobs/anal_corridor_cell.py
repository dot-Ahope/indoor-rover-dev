#!/usr/bin/env python3
"""anal_corridor_cell — §5 통로 남쪽 좁은 곳에 북행 출발 직후 잠깐 생기는 내접 칸(막힘 판정)의 출처 (2026-10-28, PC, 로버 안 움직임).
  막힘 사건 시각 t 의 전역 코스트맵에서 점 P(막힘 판정 좌표) 0.4 m 안 치명(100) 칸 중 **기준 시각(t − 3 s) 지도에는 없던 칸**을 골라
  칸마다 출처를 본다: 정적 지도(/map, SLAM) 점유 · nvblox 슬라이스(odom → map) 거리 ≤ 0 · 라이다 점(직전 1 s, map 으로) 5 cm 안.
  같은 창에서 0.2 s 마다 P 의 전역 값 · 로버 자세 · P 까지 거리 · 방위도. (anal_block_cell(10-27)과 같은 변환 규칙)
  인자: bag폴더 날짜(YYYY-MM-DD) 사건HH:MM:SS.ff Px Py [기준 앞 s=3]"""
import sys, math, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
bag = Path(sys.argv[1]); day = sys.argv[2]; ev = sys.argv[3]; P = np.array([float(sys.argv[4]), float(sys.argv[5])]); BACK = float(sys.argv[6]) if len(sys.argv) > 6 else 3.0
T = lambda s: time.mktime(time.strptime(day + ' ' + s[:8], '%Y-%m-%d %H:%M:%S')) + float(s[8:] or 0)
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
t_ev = T(ev); t0, t1 = t_ev - BACK - 2, t_ev + 4
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def T3(tr):
    a = yaw(tr.rotation); c, s = math.cos(a), math.sin(a); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
GM, SL, SC, MP, mo, ob, static, PL = [], [], [], [], [], [], {}, []
with AnyReader([bag], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/nvblox_node/static_map_slice', '/scan', '/map', '/tf', '/tf_static', '/plan')]):
        ts = t * 1e-9
        if c.topic == '/tf_static':
            for tr in rd.deserialize(raw, c.msgtype).transforms: static[tr.child_frame_id] = (tr.header.frame_id, T3(tr.transform))
            continue
        if c.topic == '/map':
            if ts <= t1:
                m = rd.deserialize(raw, c.msgtype); i = m.info; MP.append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
            continue
        if not t0 <= ts <= t1: continue
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((ts, T3(tr.transform)))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((ts, T3(tr.transform)))
        elif c.topic == '/plan':
            PL.append((ts, np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses])))
        elif c.topic == '/global_costmap/costmap':
            i = m.info; GM.append((ts, np.array(m.data, np.int16).reshape(i.height, i.width), i.origin.position.x, i.origin.position.y, i.resolution))
        elif c.topic == '/nvblox_node/static_map_slice':
            SL.append((ts, m.origin.x, m.origin.y, m.resolution, np.array(m.data, np.float32).reshape(m.height, m.width), m.unknown_value))
        else:
            a = m.angle_min + m.angle_increment * np.arange(len(m.ranges)); r = np.array(m.ranges, np.float32); ok = np.isfinite(r) & (r > m.range_min) & (r < m.range_max)
            SC.append((ts, m.header.frame_id, np.c_[r[ok] * np.cos(a[ok]), r[ok] * np.sin(a[ok]), np.ones(ok.sum())]))
def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def chain(f):
    M = np.eye(3)
    while f != 'base_link': p, mm = static[f]; M = mm @ M; f = p
    return M
def lethal_near(G):
    ts, g, ox, oy, r = G; J, I = np.nonzero(g == 100); X, Y = ox + (I + .5) * r, oy + (J + .5) * r
    k = np.hypot(X - P[0], Y - P[1]) < 0.4; return set(zip(np.round(X[k], 3), np.round(Y[k], 3)))
print('사건 %s · P (%.2f, %.2f) · 기준 = 사건 %.0f s 전 지도' % (ev, P[0], P[1], BACK))
print('시각 | 로버 map · 방향 | P 까지 · 방위(로버 기준) | 전역 P 값 · 0.4 m 안 치명 칸 수')
for t in np.arange(t_ev - BACK - 1, t_ev + 3, 0.5):
    G = last(GM, t); g = G[1]; v = int(g[int((P[1] - G[3]) / G[4]), int((P[0] - G[2]) / G[4])])
    M = last(mo, t)[1] @ last(ob, t)[1]; rx, ry, ra = M[0, 2], M[1, 2], math.atan2(M[1, 0], M[0, 0])
    print('%s | (%.2f, %.2f) %+.0f° | %.2f m · %+.0f° | %d · %d' % (hs(t), rx, ry, math.degrees(ra), math.hypot(P[0] - rx, P[1] - ry), (math.degrees(math.atan2(P[1] - ry, P[0] - rx) - ra) + 180) % 360 - 180, v, len(lethal_near(G))))
# 10-28: 로그 좌표는 cm 반올림이라 칸 경계에서 이웃 칸을 읽을 수 있음 → 사건 직전 /plan 의 실제 점으로 칸 값을 본다
pl = [q for q in PL if q[0] <= t_ev][-1]; PP = pl[1]; kk = np.hypot(PP[:, 0] - P[0], PP[:, 1] - P[1]) < 0.15
print('\n사건 전 마지막 /plan %s 점 %d — P 15 cm 안 경로 점 %d 개, 지도 판마다 그 점들의 칸 값:' % (hs(pl[0]), len(PP), kk.sum()))
hit = None
for G in [g for g in GM if t_ev - BACK - 1 <= g[0] <= t_ev + 3]:
    vals = [int(G[1][int((y - G[3]) / G[4]), int((x - G[2]) / G[4])]) for x, y in PP[kk]]
    print('  %s 판: %s' % (hs(G[0]), vals))
    if hit is None and G[0] >= t_ev - 2.5 and max(vals) >= 99: hit = G; P[:] = PP[kk][int(np.argmax(vals))]
if hit is None: print('  경로 점 칸 값이 99 에 닿은 판 없음 — 막힘 노드가 본 판이 bag 에 없거나(발행 · 기록 차) 다른 점'); hit = [g for g in GM if g[0] >= t_ev][0]
else: print('  첫 99 판 %s · 기준점(그 경로 점) (%.3f, %.3f)' % (hs(hit[0]), P[0], P[1]))
Ge = hit; Gb = last(GM, Ge[0] - BACK)
new = sorted(lethal_near(Ge) - lethal_near(Gb)); gone = sorted(lethal_near(Gb) - lethal_near(Ge))
print('\n기준 %s 판 → 사건 %s 판: P 0.4 m 안 치명 칸 새로 생김 %d · 없어짐 %d' % (hs(Gb[0]), hs(Ge[0]), len(new), len(gone)))
mp = last(MP, t_ev); S = last(SL, Ge[0]); Mmo = last(mo, Ge[0])[1]
LW = float(__import__("os").environ.get("LID_WIN", "1.0")); Z = [z for z in SC if Ge[0] - LW <= z[0] <= Ge[0]]   # 10-28: 라이다 창(기본 1 s, 환경 LID_WIN)
lid = np.vstack([(last(mo, z[0])[1] @ last(ob, z[0])[1] @ chain(z[1]) @ z[2].T).T[:, :2] for z in Z]) if Z else np.zeros((0, 2))
Minv = np.linalg.inv(Mmo)
cnt = {'정적': 0, 'nvblox': 0, '라이다': 0, '없음': 0}
for x, y in new:
    _, mg, mx, my, mr = mp; vm = int(mg[int((y - my) / mr), int((x - mx) / mr)])
    q = Minv @ np.array([x, y, 1]); _, sx, sy, sr, sd, su = S; ii, jj = int((q[0] - sx) / sr), int((q[1] - sy) / sr)
    vn = float(sd[jj, ii]) if 0 <= ii < sd.shape[1] and 0 <= jj < sd.shape[0] else float('nan')
    nl = int((np.hypot(lid[:, 0] - x, lid[:, 1] - y) < 0.05).sum()) if len(lid) else 0
    src = [k for k, f in (('정적', vm >= 65), ('nvblox', vn == vn and vn != su and vn <= 0.0), ('라이다', nl > 0)) if f] or ['없음']
    for k in src: cnt[k] += 1
    print('  새 칸 (%.3f, %.3f) · P 까지 %.0f cm | /map %d · nvblox 거리 %s · 라이다 점(직전 1 s, 5 cm 안) %d → %s' % (
        x, y, 100 * math.hypot(x - P[0], y - P[1]), vm, ('미지' if vn == su else '%.2f' % vn), nl, '·'.join(src)))
print('출처 합계(겹침 허용):', cnt)
