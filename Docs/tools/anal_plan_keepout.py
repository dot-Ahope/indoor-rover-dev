#!/usr/bin/env python3
"""anal_plan_keepout — 전역 지도에서 '카메라(nvblox)가 본 장애물' 둘레만 통과 금지 띠로 두껍게 했을 때 전역 경로가 어떻게 달라지는지 기록된 bag 으로 본다. (2026-10-14)
  왜: 상자 옆을 0.22~0.29 m 로 도는 것이 정지의 한 원인(10-13 §4.6). 전역 감쇠·MPPI 가중은 듣지 않았다. 남은 '더 멀리 돌아간다' 후보.
      실제 구현은 전역 코스트맵 nvblox 층을 비이진 모드로 하고 inflation_distance = D 를 주는 것(그 거리 안을 내접 비용 = 계획기 통과 불가로 찍음).
  방법: 주행 중 일정 간격의 시각마다
        ① 그때의 전역 코스트맵 치명 칸 중 nvblox 슬라이스가 '장애물(거리 ≤ 0)'이라고 한 자리(±1 칸)를 '카메라 칸'으로 가른다(나머지 = 저장 지도·라이다).
        ② inflation 을 다시 계산하고(지금 값: 반경 0.70 · 감쇠 2.0 · 내접 0.175), 카메라 칸에서 D 안은 통과 불가로 덧씌운다.
        ③ 그때 로버 위치 → 그때 목표(기록된 /plan 의 끝점)까지 8 방향 최단 비용 경로(NavFn 흉내: 칸 비용 50 + 0.8 × 비용, 10-13 §5.2 에서 기록 경로와 한 칸 안으로 맞음).
  출력: D 별로 — 경로가 안 나온 시각 수(부작용), 경로 길이 증가, 경로가 카메라 칸에 가장 가까이 간 거리, 지정 시각(정지 직전)의 상자 끝까지 거리.
  한계: 로버가 그 경로를 따라갔을 때 달라질 관측(다른 자리에서 보면 지도도 달라짐)은 반영 못 한다. 계획 한 번씩의 정지 비교다.
  사용: anal_plan_keepout.py bag [--step 8] [--box HH:MM:SS(정지 시각)] [--at HH:MM:SS ...(상자 거리를 볼 계획 시각)]"""
import sys, time, math, heapq
from pathlib import Path
import numpy as np
from scipy import ndimage
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
args = sys.argv[1:]; bag = args.pop(0); STEP = 8.0; BOXT = None; ATS = []
while args:
    a = args.pop(0)
    if a == '--step': STEP = float(args.pop(0))
    elif a == '--box': BOXT = args.pop(0)
    elif a == '--at': ATS.append(args.pop(0))
DS = [0.175, 0.25, 0.30, 0.35, 0.40]; RINS, RAD, K = 0.175, 0.70, 2.0; FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
def T2(tr):
    q = tr.rotation; yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)); c, s = math.cos(yaw), math.sin(yaw); return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])
ob = []; mo = []; glo = []; sl = []; plans = []; loc = []
with AnyReader([Path(bag)], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/global_costmap/costmap', '/nvblox_node/static_map_slice', '/plan', '/local_costmap/costmap')]):
        ts = t / 1e9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T2(tr.transform)))
                elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T2(tr.transform)))
        elif c.topic == '/plan':
            if len(m.poses) > 1: plans.append((ts, np.array([[q.pose.position.x, q.pose.position.y] for q in m.poses])))
        elif c.topic == '/nvblox_node/static_map_slice': sl.append((ts, m.origin.x, m.origin.y, m.resolution, m.unknown_value, np.asarray(m.data, np.float32).reshape(m.height, m.width)))
        else:
            g = (ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)); (glo if c.topic.startswith('/global') else loc).append(g)
def last(L, t): return L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
day = time.strftime('%Y-%m-%d ', time.localtime(ob[0][0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S'))


def camera_mask(t, g):   # 전역 격자와 같은 모양: nvblox 슬라이스가 장애물이라 한 자리(지도 좌표로 옮겨 ±1 칸 넓힘) ∩ 전역 치명
    _, gx, gy, res, G = g; s = last(sl, t); Mmo = last(mo, t)[1]; L = np.argwhere(s[5] <= 0); cam = np.zeros(G.shape, bool)
    if len(L):
        P = (Mmo @ np.c_[s[1] + (L[:, 1] + 0.5) * s[3], s[2] + (L[:, 0] + 0.5) * s[3], np.ones(len(L))].T).T; i = ((P[:, 1] - gy) / res).astype(int); j = ((P[:, 0] - gx) / res).astype(int)
        ok = (i >= 0) & (i < G.shape[0]) & (j >= 0) & (j < G.shape[1]); cam[i[ok], j[ok]] = True; cam = ndimage.binary_dilation(cam, structure=np.ones((3, 3)))
    return cam & (G >= 100)


def plan(g, cam, D, start, goal, goal_relief=False):
    _, gx, gy, res, G = g; leth = G >= 100; dist = ndimage.distance_transform_edt(~leth) * res
    c = np.where(dist <= RINS, 253.0, np.where(dist <= RAD, 252.0 * np.exp(-K * (dist - RINS)), 0.0)); c[leth] = 254
    if cam.any() and D > RINS: c[(ndimage.distance_transform_edt(~cam) * res <= D) & (c < 253)] = 253.0
    block = c >= 253; cost = 50 + 0.8 * c; H, W = c.shape
    s = (int((start[1] - gy) / res), int((start[0] - gx) / res)); e = (int((goal[1] - gy) / res), int((goal[0] - gx) / res))
    # 출발 칸이 금지 띠 안이면(로버가 이미 장애물 옆) 계획기는 실패한다 — Nav2 는 이때 코스트맵을 비우고 다시 시도한다. 여기서는 출발 0.30 m 안의 띠는 풀어 준다(그 사실은 따로 센다).
    inband = bool(block[s]); yy, xx = np.ogrid[:H, :W]; near = (yy - s[0]) ** 2 + (xx - s[1]) ** 2 <= (0.30 / res) ** 2; block = block & ~(near & ~leth)
    if goal_relief: block = block & ~(((yy - e[0]) ** 2 + (xx - e[1]) ** 2 <= (0.45 / res) ** 2) & ~leth)   # 목표가 띠 안이라 막힌 것인지 가르기 위한 재시도
    best = np.full((H, W), np.inf); prev = {}; best[s] = 0; pq = [(0.0, s)]
    while pq:
        dcur, u = heapq.heappop(pq)
        if u == e: break
        if dcur > best[u]: continue
        for di, dj, w in ((-1, 0, 1), (1, 0, 1), (0, -1, 1), (0, 1, 1), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)):
            v = (u[0] + di, u[1] + dj)
            if not (0 <= v[0] < H and 0 <= v[1] < W) or (block[v] and v != e): continue
            nd = dcur + w * cost[v]
            if nd < best[v]: best[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if e not in prev: return None, inband
    p = [e]
    while p[-1] != s: p.append(prev[p[-1]])
    return np.array([[gx + (j + 0.5) * res, gy + (i + 0.5) * res] for i, j in p[::-1]]), inband


BOX = None
if BOXT:   # 상자 끝 = 정지 때 로컬 코스트맵에서 차체에 가장 가까운 치명 칸의 연결 덩어리(10-13 정의)
    tB = ep(BOXT); _, ox, oy, res, G = last(loc, tB); Mob = last(ob, tB)[1]; L = np.argwhere(G >= 100); Lo = np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res, np.ones(len(L))]; pb = (np.linalg.inv(Mob) @ Lo.T).T
    d = np.hypot(np.maximum.reduce([FP[:, 0].min() - pb[:, 0], np.zeros(len(pb)), pb[:, 0] - FP[:, 0].max()]), np.maximum.reduce([FP[:, 1].min() - pb[:, 1], np.zeros(len(pb)), pb[:, 1] - FP[:, 1].max()]))
    lab, _ = ndimage.label(G >= 100, structure=np.ones((3, 3))); sel = lab[L[:, 0], L[:, 1]] == lab[L[int(np.argmin(d)), 0], L[int(np.argmin(d)), 1]]; BOX = (last(mo, tB)[1] @ Lo[sel].T).T[:, :2]
t0 = plans[0][0] + 1; t1 = min(ob[-1][0], plans[-1][0] + 60); times = list(np.arange(t0, t1, STEP)); R = {D: [] for D in DS}; ncam = []
for t in times:
    g = last(glo, t); cam = camera_mask(t, g); ncam.append(int(cam.sum())); Mmb = last(mo, t)[1] @ last(ob, t)[1]; start = Mmb[:2, 2]; goal = last(plans, t)[1][-1]
    if np.hypot(*(goal - start)) < 0.5: continue
    for D in DS:
        xy, inband = plan(g, cam, D, start, goal); why = ''
        if xy is None: why = '목표가 띠 안' if plan(g, cam, D, start, goal, True)[0] is not None else '통로 막힘'
        R[D].append((t, None if xy is None else float(np.hypot(*np.diff(xy, axis=0).T).sum()), inband, why))
print('%s: 계획 시각 %d 개(%.0f s 간격), 카메라 칸 수 중앙 %d' % (Path(bag).name, len(R[DS[0]]), STEP, int(np.median(ncam))))
print('카메라 장애물 금지 띠 D    경로 없음(시각 수)   출발이 띠 안이던 시각 수   경로 길이 증가(지금 대비, 중앙 · 최대)   경로 없음이 난 시각')
base = {r[0]: r[1] for r in R[DS[0]]}
for D in DS:
    fail = [r[0] for r in R[D] if r[1] is None]; inc = [(r[1] - base[r[0]]) for r in R[D] if r[1] is not None and base[r[0]] is not None]
    print('  %.3f m%s          %2d / %2d              %2d                       %+.2f · %+.2f m                    %s' % (D, ' (지금)' if D == DS[0] else '       ', len(fail), len(R[D]), sum(r[2] for r in R[D]), np.median(inc) if inc else float('nan'), max(inc) if inc else float('nan'), ' '.join('%s(%s)' % (time.strftime('%H:%M:%S', time.localtime(r[0])), r[3]) for r in R[D] if r[1] is None)[:230]))
for h in ATS:
    t = ep(h); g = last(glo, t); cam = camera_mask(t, g); Mmb = last(mo, t)[1] @ last(ob, t)[1]; goal = last(plans, t)[1][-1]; row = []
    for D in DS:
        xy, _ = plan(g, cam, D, Mmb[:2, 2], goal)
        row.append('없음' if xy is None else '%.2f m(길이 %.2f)' % (np.hypot(xy[:, None, 0] - BOX[None, :, 0], xy[:, None, 1] - BOX[None, :, 1]).min() if BOX is not None else float('nan'), np.hypot(*np.diff(xy, axis=0).T).sum()))
    inbox = int(cam[((BOX[:, 1] - g[2]) / g[3]).astype(int), ((BOX[:, 0] - g[1]) / g[3]).astype(int)].sum()) if BOX is not None else -1
    print('계획 %s — 경로 ↔ 상자 끝: %s | 그때 전역 지도의 상자 끝 중 카메라 칸 %d / %d' % (h, ' · '.join('D %.3f → %s' % (D, r) for D, r in zip(DS, row)), inbox, len(BOX) if BOX is not None else 0))
