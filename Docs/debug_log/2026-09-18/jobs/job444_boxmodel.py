#!/usr/bin/env python3
"""러너 ① '실제 최근접' 이 dy3 에서 0.0 cm(접촉)로 나온 원인 재구성 (2026-09-18). 인자: NAME BAG_DIR GOAL_EPOCH CSV BOX_FX BOX_CY [...]
  job125_avoid3.py 의 상자 모델: 검출 순간 로버 자세(base_link)에서 전면 x=5 % 분위, 중심 y=중앙값을 잡고
  폭 0.18 × 깊이 0.11 사각형을 **그 순간 로버 방향으로** 세운다(make_peri). 로버가 돌아간 채 재고정하면 사각형도 같이 돈다.
  가정: 실물 상자는 prep 게이트가 잰 자리(BOX_FX 전면, BOX_CY 중심)에 map 축 정렬. 카메라에 보이는 면(전면·로버 쪽 옆면)을
  1 cm 간격으로 뽑아 FOV ±43° 안만 쓰는 근사(실제 깊이점 밀도는 거리·각에 따라 다름 — 근사).
  csv 의 box_age 가 0 으로 돌아간 마지막 시각 = 마지막 재고정. 그 자세로 모델을 다시 세워 csv clear_geo 와 비교.
"""
import sys, math, csv, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
HL, HW, BW, BD = 0.25, 0.165, 0.18, 0.11
CAM_X, HFOV = 0.23, math.radians(43.0)


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def poses(bag, G):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
    ob, mo = [], {}
    while r.has_next():
        topic, data, ts = r.read_next()
        if topic != '/tf':
            continue
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            v = (st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation))
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append(v)
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo[round(st, 4)] = v          # 같은 stamp 두 번 → 마지막 값(09-18 dedup 규칙)
    ob.sort(); mo = sorted(mo.values())
    obt = [o[0] for o in ob]; mot = [m[0] for m in mo]

    def at(t):
        _, ox, oy, oth = ob[min(max(bisect.bisect_left(obt, t), 0), len(ob) - 1)]
        _, ax, ay, ath = mo[min(max(bisect.bisect_right(mot, t) - 1, 0), len(mo) - 1)]
        return (ax + ox * math.cos(ath) - oy * math.sin(ath), ay + ox * math.sin(ath) + oy * math.cos(ath), ath + oth)
    return at


def peri(corners):
    P = []
    for i in range(4):
        (ax, ay), (bx, by) = corners[i], corners[(i + 1) % 4]
        for k in range(21):
            u = k / 20.0; P.append((ax + u * (bx - ax), ay + u * (by - ay)))
    return np.array(P)


def clear(P, px, py, yaw):
    c, s = math.cos(-yaw), math.sin(-yaw); dx = P[:, 0] - px; dy = P[:, 1] - py
    rx = dx * c - dy * s; ry = dx * s + dy * c
    return float(np.min(np.hypot(np.maximum(np.abs(rx) - HL, 0), np.maximum(np.abs(ry) - HW, 0))))


def model_from(p, fx0, cy0):
    """실물 상자 면을 로버 p 에서 보고 job125 방식으로 사각형을 세운다."""
    pts = [(fx0, y) for y in np.arange(cy0 - BW / 2, cy0 + BW / 2 + 1e-9, 0.01)]
    side_y = cy0 + BW / 2 if p[1] > cy0 + BW / 2 else (cy0 - BW / 2 if p[1] < cy0 - BW / 2 else None)
    if side_y is not None:
        pts += [(x, side_y) for x in np.arange(fx0, fx0 + BD + 1e-9, 0.01)]
    c, s = math.cos(-p[2]), math.sin(-p[2]); B = []
    for mx, my in pts:
        dx, dy = mx - p[0], my - p[1]; bx, by = dx * c - dy * s, dx * s + dy * c
        if abs(math.atan2(by, bx - CAM_X)) < HFOV and 0.5 < bx < 1.5 and abs(by) < 0.5:
            B.append((bx, by))
    if len(B) < 5:
        return None, 0
    B = np.array(B); fx = float(np.percentile(B[:, 0], 5)); cy = float(np.median(B[:, 1]))
    c2, s2 = math.cos(p[2]), math.sin(p[2]); cs = []
    for bx, by in ((fx, cy - BW / 2), (fx, cy + BW / 2), (fx + BD, cy + BW / 2), (fx + BD, cy - BW / 2)):
        cs.append((p[0] + bx * c2 - by * s2, p[1] + bx * s2 + by * c2))
    return peri(cs), len(B)


a = sys.argv[1:]
for k in range(0, len(a), 6):
    name, bag, G, cf, fx0, cy0 = a[k], a[k + 1], float(a[k + 2]), a[k + 3], float(a[k + 4]), float(a[k + 5])
    at = poses(bag, G); rows = list(csv.DictReader(open(cf)))
    T = [float(x['t']) for x in rows]; AGE = [float(x['box_age']) for x in rows]; CG = [float(x['clear_geo']) for x in rows]
    fixes = [T[i] - AGE[i] for i in range(len(T)) if AGE[i] < 0.11 and T[i] > 0.3]
    tf_last = fixes[-1] if fixes else 0.0
    p_fix = at(tf_last)
    TRUE = peri([(fx0, cy0 - BW / 2), (fx0, cy0 + BW / 2), (fx0 + BD, cy0 + BW / 2), (fx0 + BD, cy0 - BW / 2)])
    M, nb = model_from(p_fix, fx0, cy0)
    print('==== %s: 마지막 재고정 t=%.1f s, 그때 로버 map (%.3f, %+.3f) yaw %+.1f° → 모델 사각형이 %+.1f° 돌아감 (보이는 면 점 %d)' % (
        name, tf_last, p_fix[0], p_fix[1], math.degrees(p_fix[2]), math.degrees(p_fix[2]), nb))
    if M is not None:
        print('   모델 사각형 꼭짓점 y 최대(로버 쪽) %+.3f / 실물 %+.3f, x 범위 %.3f~%.3f / 실물 %.3f~%.3f' % (
            M[:, 1].max(), cy0 + BW / 2, M[:, 0].min(), M[:, 0].max(), fx0, fx0 + BD))
    print('   t     | csv ① clear_geo | 재구성: 모델 사각형 | 실물(prep 자리, 축 정렬)')
    res = []
    for i in range(len(T)):
        if T[i] < 12 or T[i] > 27:
            continue
        p = at(T[i]); cm = clear(M, *p) if M is not None else float('nan'); ct = clear(TRUE, *p)
        res.append((T[i], CG[i], cm, ct))
    for t, cg, cm, ct in res[::8]:
        print('  %5.1f | %.3f | %.3f | %.3f' % (t, cg, cm, ct))
    R = np.array(res)
    print('   최소: csv %.3f @%.1f | 모델 재구성 %.3f @%.1f | 실물 %.3f @%.1f | csv−모델 재구성 차 중앙 %+.3f (|차| 최대 %.3f)' % (
        R[:, 1].min(), R[np.argmin(R[:, 1]), 0], R[:, 2].min(), R[np.argmin(R[:, 2]), 0], R[:, 3].min(), R[np.argmin(R[:, 3]), 0],
        float(np.median(R[:, 1] - R[:, 2])), float(np.max(np.abs(R[:, 1] - R[:, 2])))))
