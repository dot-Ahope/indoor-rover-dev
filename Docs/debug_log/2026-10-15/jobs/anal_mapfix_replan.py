#!/usr/bin/env python3
"""anal_mapfix_replan — 저장 지도 서쪽 벽(서쪽 통로 y −3.85~−4.45)을 오늘 라이다 위치로 고쳤다면 계획 경로가 상자 옆을 얼마나 띄워 지나는지. (2026-10-15 §11, 오늘만 — 실제 지도는 안 바꿈)
  왜: §10 — 저장 지도 서쪽 벽이 라이다보다 약 10 cm 두꺼움(지도 번짐 추정). 사용자 "진행하라": 고친 사본으로 효과를 먼저 계산.
  방법: 기록된 전역 코스트맵 한 장에서 치명 칸만 꺼내, 고칠 칸(그 y 구간 · x 칸 중심 −2.19~−2.06 = 저장 지도엔 점유, 라이다 면 −2.20~−2.25 보다 통로 쪽)을 '고친 판' 에서만 비움.
        두 판 모두 같은 방식으로 inflation 을 다시 계산(반경 0.70 · 감쇠 2.0 · 내접 0.175 — nav2_params 전역 값)하고 NavFn 비용 변환 8-연결 다익스트라(§9 와 같음).
        고칠 칸이 그 순간 로컬 코스트맵(카메라 + 라이다, 정적 층 없음)에서 치명인지도 확인 — 치명이면 지도만 고쳐서는 소용없음.
        출력: 상자 옆(y −3.90~−4.40) 경로 x, 차체(반폭 0.175) 동쪽 끝 → 상자 앞면(x −1.43, 사용자 확인) 여유, → 카메라 과장 칸 가장자리(x −1.505) 여유(칸 검사 막힘 기준 약 4.4 cm 와 비교).
        f2v1 에서 로버는 경로보다 약 4 cm 동쪽(−1.70 vs −1.74)에 섰다 — 그 치우침을 더한 값도 함께.
  인자: bag HH:MM:SS.f(전역 지도) HH:MM:SS.f(로컬 지도 확인)"""
import sys, time, math, heapq
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
bag, hg, hl = sys.argv[1:4]
def at(h):
    hms, _, fr = h.partition('.'); return hms, (float('0.' + fr) if fr else 0)
gc = lc = mo = None
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    day = None
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/local_costmap/costmap', '/tf')]):
        ts = t / 1e9
        if day is None: day = time.strftime('%Y-%m-%d ', time.localtime(ts)); TG = time.mktime(time.strptime(day + at(hg)[0], '%Y-%m-%d %H:%M:%S')) + at(hg)[1]; TL = time.mktime(time.strptime(day + at(hl)[0], '%Y-%m-%d %H:%M:%S')) + at(hl)[1]
        if ts > max(TG, TL) + 0.05: break
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/global_costmap/costmap' and ts <= TG + 0.05: gc = m
        elif c.topic == '/local_costmap/costmap' and ts <= TL + 0.05: lc = (m, mo)
        elif c.topic == '/tf':
            for tr in m.transforms:
                if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
g = np.array(gc.data, np.int16).reshape(gc.info.height, gc.info.width); r = gc.info.resolution; ox, oy = gc.info.origin.position.x, gc.info.origin.position.y
xc = ox + (np.arange(g.shape[1]) + 0.5) * r; yc = oy + (np.arange(g.shape[0]) + 0.5) * r
# 칸 중심이 저장 지도 서쪽 면(−2.09)과 오늘 라이다 면(−2.20~−2.25) 사이인 칸: x 중심 ∈ (−2.19, −2.06). 전역 지도 원점이 0.05 의 배수가 아니라 범위로 고름
FIX = ((xc[None, :] > -2.19) & (xc[None, :] < -2.06)) & ((yc[:, None] <= -3.85 + 0.01) & (yc[:, None] >= -4.45 - 0.01))
leth0 = g >= 100
# 고칠 칸이 로컬(카메라 + 라이다)에서도 치명인가
lm, lmo = lc; la = np.array(lm.data, np.int16).reshape(lm.info.height, lm.info.width); iy, ix = np.nonzero(la >= 100)
lx0 = lm.info.origin.position.x + (ix + 0.5) * lm.info.resolution; ly0 = lm.info.origin.position.y + (iy + 0.5) * lm.info.resolution
c_, s_ = math.cos(lmo[2]), math.sin(lmo[2]); lx = lmo[0] + c_ * lx0 - s_ * ly0; ly = lmo[1] + s_ * lx0 + c_ * ly0
fy, fx = np.nonzero(FIX); fixpts = np.c_[xc[fx], yc[fy]]
loc_hit = sum(1 for p in fixpts if (np.hypot(lx - p[0], ly - p[1]) < 0.03).any())
print('고칠 칸 %d 개(그중 전역에서 치명 %d) · 로컬(카메라 + 라이다)에서도 치명인 칸 %d' % (len(fixpts), int(leth0[FIX].sum()), loc_hit))
def inflate(leth):
    dist = distance_transform_edt(~leth) * r
    c = np.where(leth, 254, np.where(dist <= 0.175, 253, np.where(dist <= 0.70, np.floor(252 * np.exp(-2.0 * (dist - 0.175))), 0)))
    return np.where(g < 0, 255, c)
cell = lambda x, y: (int((y - oy) / r), int((x - ox) / r))
def plan(raw, s, e):
    cost = np.where(raw >= 253, np.inf, 50 + 0.8 * raw); cost = np.where(raw == 255, 253.0, cost); cost[s] = 50.0
    D = np.full(g.shape, np.inf); D[s] = 0; P = {}; pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > D[u]: continue
        if u == e: break
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if not dx and not dy: continue
                v = (u[0] + dy, u[1] + dx)
                if not (0 <= v[0] < g.shape[0] and 0 <= v[1] < g.shape[1]) or not np.isfinite(cost[v]): continue
                nd = d + cost[v] * (1.4142 if dx and dy else 1.0)
                if nd < D[v]: D[v] = nd; P[v] = u; heapq.heappush(pq, (nd, v))
    path = [e]
    while path[-1] != s: path.append(P[path[-1]])
    return np.array([[ox + (c2 + 0.5) * r, oy + (r2 + 0.5) * r] for r2, c2 in path[::-1]])
BOX, CAMEDGE, HW, BIAS = -1.43, -1.505, 0.175, 0.04
print('판          상자 옆 경로 x(최소~최대 · 중앙)   차체→상자 앞면 최소   차체→카메라 과장 칸   + 로버 치우침 4 cm 때(과장 칸)   통로 단면 지날 수 있는 폭(y −4.10)')
for lab, leth in (('지금 지도', leth0), ('서쪽 벽 고침', leth0 & ~FIX)):
    raw = inflate(leth); p = plan(raw, cell(-1.65, -3.70), cell(-1.60, -5.50))
    k = (p[:, 1] <= -3.90) & (p[:, 1] >= -4.40); xs = p[k, 0]
    row = cell(-1.8, -4.10)[0]; free = xc[(raw[row] < 253) & (xc > -2.4) & (xc < -1.2)]
    print('%-10s  %+.3f ~ %+.3f · %+.3f              %5.1f cm           %5.1f cm               %5.1f cm                        %.2f m (x %+.2f~%+.2f)' % (
        lab, xs.min(), xs.max(), np.median(xs), 100 * (BOX - (xs.max() + HW)), 100 * (CAMEDGE - (xs.max() + HW)), 100 * (CAMEDGE - (xs.max() + BIAS + HW)), free.max() - free.min() + r, free.min(), free.max()))
# 진단: y −4.10 · −4.25 행의 다시 계산한 비용(253 이상 = 계획기 장애물), 두 판
for yy in (-4.10, -4.25):
    row = cell(-1.8, yy)[0]; sel = (xc > -2.30) & (xc < -1.35)
    print('y %+.2f x:   ' % yy + ' '.join('%5.2f' % v for v in xc[sel]))
    for lab, leth in (('지금 지도', leth0), ('서쪽 벽 고침', leth0 & ~FIX)):
        raw = inflate(leth); print('  %-9s ' % lab + ' '.join('%5d' % v for v in raw[row][sel]))
