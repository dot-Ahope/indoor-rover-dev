#!/usr/bin/env python3
"""anal_pba_replay — PathBlockedAhead 판정을 bag 으로 다시 돌려 only_new 전후를 비교(2026-10-23 §20.7, PC, 로버 안 움직임).
  왜: f2rp4 에서는 99 칸을 지나는 경로가 안 나와 only_new 가 한 번도 안 쓰임(§20.5). f2rp3 은 서쪽 통로 막힘 5 번이 실제로 난 기록.
  방법(50 Hz): C++ 노드(ros2_ws/src/rover_navigation/src/path_blocked_ahead_condition.cpp)의 판정을 그대로 옮겨, 기록된 입력으로 10 Hz 로 돌림.
    · 경로 = BT 가 컨트롤러에 준 {path}: nav2 로그의 'Received a path to smooth'(BT 계획) 마다, 스무딩 성공이면 그 뒤 /plan_smoothed,
      실패('Smoothed path leads to a collision')면 그 직전 /plan(원경로 = CopyPath). /plan 에는 러너 조회기 경로도 섞이므로 BT 계획 시각에 가장 가까운 것.
    · 지도 = /global_costmap/costmap(bag 에 ≈ 1.5 s 간격), 로버 = /tf map→odom ∘ odom→base_link.
    · 판정 인자 = BT xml 값(앞 1.5 m · 가까이 0.30 m · 2.0 s · 99).
  먼저 only_new=false 로 실제 로그의 막힘 시각을 재현하는지 보고(재현 안 되면 이 시험은 무효), 같은 입력에 only_new=true 를 돌림.
  한계: 기록은 옛 동작(막힘 → 중단 → 재계획)의 결과 — only_new 로 막힘을 안 셌다면 그 뒤 경로 · 로버 움직임은 달라졌을 것(반사실은 재현 못 함).
       그래서 '경로 하나가 쓰인 동안 막힘이 걸리나' 를 경로마다 따짐.
  인자: bag nav2.log"""
import sys, math, bisect, time
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2]); return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])
LOOK, SKIP, HOLD, MINC = 1.5, 0.30, 2.0, 99
DTS = 0.02   # 판정 간격(실제 BT 는 100 Hz). 첫 판 0.1 s 는 f2rp4 상자 막힘 시작을 0.1 s 늦게 봐 재계획 직전 2 s 를 못 채움
# HOLD 비교는 1e-6 여유: 0.1 s 누적 부동소수 오차(1.9999 < 2.0)로 첫 판이 f2rp4 상자 막힘을 놓쳤음
bag, logf = sys.argv[1], sys.argv[2]
MO, OB, GR, RAW, SM = [], [], [], [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/global_costmap/costmap', '/plan', '/plan_smoothed')]):
        ts = t * 1e-9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, v))
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((ts, v))
        elif c.topic == '/global_costmap/costmap':
            GR.append((ts, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)))
        elif len(m.poses) > 1:
            (RAW if c.topic == '/plan' else SM).append((ts, np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])))
for L in (MO, OB, GR, RAW, SM): L.sort(key=lambda q: q[0])
Lt = lambda L: [q[0] for q in L]; MOt, OBt, GRt, RAWt, SMt = map(Lt, (MO, OB, GR, RAW, SM))
at = lambda L, T, t: L[max(bisect.bisect_right(T, t) - 1, 0)]
# BT 계획 사건과 스무딩 성공 여부, 실제 막힘 사건(로그)
ev, real = [], []
for line in open(logf, encoding='utf-8', errors='replace'):
    i = line.find('] [17'); j = line.find(']', i + 3)
    if i < 0: continue
    try: te = float(line[i + 3:j])
    except ValueError: continue
    if 'Received a path to smooth' in line: ev.append([te, True])
    elif 'Smoothed path leads to a collision' in line and ev: ev[-1][1] = False
    elif '지속 → 주행 중단' in line and not (real and te - real[-1] < 0.5): real.append(te)
paths = []   # (받은 시각, 점들, 원경로인가)
for te, ok in ev:
    if ok:
        k = bisect.bisect_left(SMt, te - 0.05)
        if k < len(SM) and SM[k][0] - te < 1.5: paths.append((SM[k][0], SM[k][1], False)); continue
    k = bisect.bisect_right(RAWt, te + 0.05) - 1
    if k >= 0 and te - RAW[k][0] < 1.5: paths.append((te, RAW[k][1], True))
hm = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)


def cost(g, P):
    _, ox, oy, res, G = g; mx = np.floor((P[:, 0] - ox) / res).astype(int); my = np.floor((P[:, 1] - oy) / res).astype(int)
    ok = (mx >= 0) & (my >= 0) & (mx < G.shape[1]) & (my < G.shape[0]); c = np.full(len(P), -1); c[ok] = G[my[ok], mx[ok]]; return c


def run(only_new):
    out = []   # (시각, 점, 비용, 경로 번호)
    for k, (tp, P, israw) in enumerate(paths):
        tn = paths[k + 1][0] if k + 1 < len(paths) else tp + 120
        init = cost(at(GR, GRt, tp), P); since = None; t = tp
        while t < tn:
            g = at(GR, GRt, t); p = comp(at(MO, MOt, t)[1], at(OB, OBt, t)[1]); q = np.array(p[:2])
            i0 = int(np.argmin(np.linalg.norm(P - q, axis=1))); s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P[i0:], axis=0), axis=1))]
            idx = i0 + np.nonzero((s >= SKIP) & (s <= LOOK))[0]; c = cost(g, P[idx]); hit = c >= MINC
            if only_new: hit &= c > init[idx]
            if hit.any():
                if since is None: since = t
                if t - since >= HOLD - 1e-6: out.append((t, P[idx[np.argmax(hit)]], int(c[np.argmax(hit)]), k)); break   # 실제로는 여기서 주행 중단 → 다음 경로
            else: since = None
            t += DTS
    return out


print('입력: BT 경로 %d 개(원경로 %d · 스무딩 %d), 지도 %d 장, 실제 막힘 중단 %d 번' % (len(paths), sum(p[2] for p in paths), sum(not p[2] for p in paths), len(GR), len(real)))
print('실제 로그의 막힘 중단:', ' · '.join(hm(t) for t in real))
for name, on in (('only_new=false(예전 · 재현 확인)', False), ('only_new=true(새 판)', True)):
    r = run(on); print('\n== %s → 막힘 중단 %d 번' % (name, len(r)))
    for t, pt, c, k in r:
        tp, P, israw = paths[k]; init = cost(at(GR, GRt, tp), P[None, :][0] if False else pt[None, :])[0]
        near = min((abs(t - x) for x in real), default=99)
        print('  %s  점 (%.2f, %.2f) 비용 %d · 경로 #%d(%s, 받은 %s, 받을 때 그 칸 %d) · 실제 중단과 차 %.2f s' % (hm(t), pt[0], pt[1], c, k, '원경로' if israw else '스무딩', hm(tp), init, near))
