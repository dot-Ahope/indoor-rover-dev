#!/usr/bin/env python3
"""anal_tffix_sig — §19 §15 서명(단위 변환으로 적힌 슬라이스)이 전역 코스트맵에 있었나, 주행 전체 (2026-10-27, PC).
  전역 메시지마다: 직전 대비 새로 생긴 치명 칸 A, 가장 가까운 슬라이스의 장애(≤0) 칸을
    (가) 단위 변환(odom 좌표 그대로) · (나) 실제 map→odom 으로 옮긴 칸과 A 의 겹침(5 cm 칸, ±1 칸 허용 없음 = §15 와 같은 floor 칸).
  서명 = A ≥ 50 칸 · (가) 겹침 ≥ 0.5·A · (가) > (나). nav2 로그 경고([NvbloxCostmapLayer] Can't transform) · 'Control loop missed' 수도.
  인자: bag폴더 nav2.log"""
import sys, re, time, math
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
ts_ = get_typestore(Stores.ROS2_HUMBLE)
ts_.register(get_types_from_msg('std_msgs/Header header\nfloat32 resolution\nuint32 width\nuint32 height\ngeometry_msgs/Point origin\nfloat32 unknown_value\nfloat32[] data\n', 'nvblox_msgs/msg/DistanceMapSlice'))
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
key = lambda P: set(map(tuple, np.floor(P / 0.05).astype(int)))
GM, SL, MO = [], [], []
with AnyReader([Path(sys.argv[1])], default_typestore=ts_) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/global_costmap/costmap', '/nvblox_node/static_map_slice', '/tf')]):
        ts = t * 1e-9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf':
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((ts, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
        elif c.topic == '/global_costmap/costmap':
            i = m.info; g = np.array(m.data, np.int16).reshape(i.height, i.width) == 100
            GM.append((ts, g, i.origin.position.x, i.origin.position.y, i.resolution))
        else:
            d = np.array(m.data, np.float32).reshape(m.height, m.width); J, I = np.nonzero((d <= 0) & (d != m.unknown_value))
            SL.append((ts, np.c_[m.origin.x + (I + .5) * m.resolution, m.origin.y + (J + .5) * m.resolution]))
st = np.array([s[0] for s in SL]); mt = np.array([x[0] for x in MO])
sig = []; n = 0
for k in range(1, len(GM)):
    ts, g, ox, oy, r = GM[k]; p = GM[k - 1][1]
    if p.shape != g.shape: continue
    J, I = np.nonzero(g & ~p)
    if len(I) < 50: continue
    n += 1
    A = set(zip((I + int(round(ox / r))).tolist(), (J + int(round(oy / r))).tolist()))
    S = SL[max(np.searchsorted(st, ts) - 1, 0)][1]; mo = MO[max(np.searchsorted(mt, ts) - 1, 0)]
    c, s = math.cos(mo[3]), math.sin(mo[3]); R = np.c_[mo[1] + c * S[:, 0] - s * S[:, 1], mo[2] + s * S[:, 0] + c * S[:, 1]]
    a, b = len(A & key(S)), len(A & key(R))
    if a >= 0.5 * len(A) and a > b: sig.append((ts, len(A), a, b))
    if a >= 0.3 * len(A): print('  후보 %s 새 칸 %d · 단위 겹침 %d · 실제 변환 겹침 %d' % (hs(ts), len(A), a, b))
print('전역 메시지 %d · 새 칸 ≥ 50 인 장 %d · **§15 서명 장 %d**' % (len(GM), n, len(sig)))
for x in sig: print('  서명 %s 새 칸 %d · 단위 겹침 %d · 실제 %d' % (hs(x[0]), x[1], x[2], x[3]))
t0, t1 = GM[0][0], GM[-1][0]; W, C = [], []
for l in open(sys.argv[2], encoding='utf-8', errors='replace'):
    m = re.search(r'\[(\d{10}\.\d+)\]', l)
    if not m: continue
    t = float(m[1])
    if not t0 <= t <= t1: continue
    if 'NvbloxCostmapLayer' in l and "Can't transform" in l: W.append(t)
    elif 'Control loop missed' in l: C.append(t)
print('bag 창 %s~%s: 층 경고 %d 번 · Control loop missed %d 번' % (hs(t0), hs(t1), len(W), len(C)))
for w in W:
    nx = next((x for x in GM if x[0] > w), None)
    print('  경고 %s → 다음 전역 장 %s' % (hs(w), hs(nx[0]) if nx else '-'))
