#!/usr/bin/env python3
"""anal_box_history — 로버가 장애물 옆에서 멈췄을 때, 그 장애물 칸이 코스트맵에 '언제부터' 있었는지와 로버·경로가 '어떻게' 다가갔는지를 시간순으로 낸다. (2026-10-13)
  왜: f2o1 목표 3 정지(상자 옆 여유 4.8 cm). MPPI·경로가 상자 쪽으로 붙은 것인지, 상자 칸이 늦게 나타난 것인지 가린다.
  방법: 지정 시각(정지 때)의 로컬 코스트맵에서 차체에 가장 가까운 치명 칸이 속한 덩어리(연결된 칸)를 '상자'로 잡아 지도(map) 좌표로 고정한다.
        그 뒤 주행 전체의 로컬·전역 코스트맵마다 그 자리 칸 중 몇 개가 치명이었는지, 로버가 상자에서 얼마나 떨어져 있었는지,
        상자가 카메라 정면에서 몇 도였는지, 전역 경로(/plan)가 상자에 얼마나 가깝게 그려졌는지를 본다.
  한계: 상자 자리는 정지 순간의 코스트맵으로 정한 것이다(상자의 참 위치가 아님). map↔odom 보정이 그 사이 움직이면 자리도 그만큼 어긋난다.
  사용: anal_box_history.py bag HH:MM:SS(정지 시각) [시작 HH:MM:SS]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, hms = sys.argv[1], sys.argv[2]; hms0 = sys.argv[3] if len(sys.argv) > 3 else None
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])


def T2(tr):   # 평면 변환(x, y, yaw) → 3×3
    q = tr.rotation; yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)); c, s = math.cos(yaw), math.sin(yaw)
    return np.array([[c, -s, tr.translation.x], [s, c, tr.translation.y], [0, 0, 1]])


def load(bag, topics):
    D = {t: [] for t in topics}; ob = []; mo = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in topics or c.topic == '/tf']):
            ts = t / 1e9
            if c.topic == '/tf':
                for tr in rd.deserialize(raw, c.msgtype).transforms:
                    if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob.append((ts, T2(tr.transform)))
                    elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo.append((ts, T2(tr.transform)))
            else: D[c.topic].append((ts, rd.deserialize(raw, c.msgtype)))
    return D, ob, mo


def near(L, ts): return L[min(np.searchsorted([x[0] for x in L], ts), len(L) - 1)][1]
def grid(m): return m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)
def body_clear(pb):   # 차체 사각형 바깥 점들까지의 최소 거리
    dx = np.maximum.reduce([FP[:, 0].min() - pb[:, 0], np.zeros(len(pb)), pb[:, 0] - FP[:, 0].max()]); dy = np.maximum.reduce([FP[:, 1].min() - pb[:, 1], np.zeros(len(pb)), pb[:, 1] - FP[:, 1].max()])
    return np.hypot(dx, dy).min()


if __name__ == '__main__':
    D, ob, mo = load(bag, ['/local_costmap/costmap', '/global_costmap/costmap', '/plan'])
    obt = [x[0] for x in ob]; day = time.strftime('%Y-%m-%d ', time.localtime(ob[0][0])); ep = lambda s: time.mktime(time.strptime(day + s, '%Y-%m-%d %H:%M:%S'))
    tgt = ep(hms); tA = ep(hms0) if hms0 else ob[0][0]
    # 상자 = 정지 때 로컬 코스트맵의 치명 칸 중 차체에서 0.45 m 안에 있는 것
    ts, m = min(D['/local_costmap/costmap'], key=lambda x: abs(x[0] - tgt)); ox, oy, res, G = grid(m); Mob = near(ob, ts); Mmo = near(mo, ts)
    L = np.argwhere(G >= 100); Lo = np.c_[ox + (L[:, 1] + 0.5) * res, oy + (L[:, 0] + 0.5) * res, np.ones(len(L))]; Lb = (np.linalg.inv(Mob) @ Lo.T).T
    dx = np.maximum.reduce([FP[:, 0].min() - Lb[:, 0], np.zeros(len(Lb)), Lb[:, 0] - FP[:, 0].max()]); dy = np.maximum.reduce([FP[:, 1].min() - Lb[:, 1], np.zeros(len(Lb)), Lb[:, 1] - FP[:, 1].max()])
    from scipy import ndimage   # 차체에 가장 가까운 치명 칸이 속한 덩어리(8 방향 연결)만 '상자'로 — 반대편 벽 등 다른 물체를 섞지 않게
    lab, _ = ndimage.label(G >= 100, structure=np.ones((3, 3))); k = int(np.argmin(np.hypot(dx, dy))); sel = lab[L[:, 0], L[:, 1]] == lab[L[k, 0], L[k, 1]]
    BOX = (Mmo @ Lo[sel].T).T   # 지도 좌표의 상자 칸(중심)
    bc = BOX[:, :2].mean(0); print('상자(정지 %s 때 로컬 코스트맵 기준): 치명 칸 %d 개, 지도 좌표 중심 (%.2f, %.2f), 폭 x %.2f · y %.2f m' % (time.strftime('%H:%M:%S', time.localtime(ts)), len(BOX), bc[0], bc[1], np.ptp(BOX[:, 0]) + res, np.ptp(BOX[:, 1]) + res))

    def count(m, Tin):   # 코스트맵 m 에서 상자 자리 칸 중 치명 수(창 밖이면 None). Tin = map → 코스트맵 좌표
        ox, oy, res, G = grid(m); P = (Tin @ BOX.T).T; j = ((P[:, 0] - ox) / res).astype(int); i = ((P[:, 1] - oy) / res).astype(int); ok = (i >= 0) & (i < G.shape[0]) & (j >= 0) & (j < G.shape[1])
        if ok.sum() < len(BOX) * 0.8: return None
        v = G[i[ok], j[ok]]; return int((v >= 100).sum()), int((v >= 99).sum())
    print('\n시각      로버→상자 중심 거리  차체 여유  상자 방위(로버 앞 기준, +왼쪽)  로컬: 그 자리 치명/내접이상 칸  전역: 치명/내접이상  전역 경로가 상자 칸에 가장 가까운 거리')
    gl = D['/global_costmap/costmap']; pl = D['/plan']; last = -9
    for ts, m in D['/local_costmap/costmap']:
        if ts < tA or ts > tgt + 3 or ts - last < 1.9: continue
        last = ts; Mob = near(ob, ts); Mmo = near(mo, ts); Mmb = Mmo @ Mob; Pb = (np.linalg.inv(Mmb) @ BOX.T).T; cb = Pb[:, :2].mean(0)
        lc = count(m, np.linalg.inv(Mmo)); g = [x for x in gl if x[0] <= ts]; gc = count(g[-1][1], np.eye(3)) if g else None
        p = [x for x in pl if x[0] <= ts]; pd = float('nan')
        if p and len(p[-1][1].poses) > 1:
            xy = np.array([[q.pose.position.x, q.pose.position.y] for q in p[-1][1].poses]); pd = np.hypot(xy[:, None, 0] - BOX[None, :, 0], xy[:, None, 1] - BOX[None, :, 1]).min()
        f = lambda c: '창 밖' if c is None else '%2d / %2d' % c
        print('%s   %.2f m            %5.1f cm    %+5.0f°                         %-8s                   %-8s            %.2f m' % (time.strftime('%H:%M:%S', time.localtime(ts)), np.hypot(*cb), body_clear(Pb) * 100, math.degrees(math.atan2(cb[1], cb[0])), f(lc), f(gc), pd))
