#!/usr/bin/env python3
"""anal_ctrl_eval — MPPI 컨트롤러 틱마다 '그 틱에 컨트롤러가 따르던 경로' 대비 로버 옆 치우침 · 방향 오차 · 경로 곡률(2026-10-23, PC, 로버 안 움직임).
  왜: §20.9 · §21 — b910 복귀 때 경로 여유 8.9 cm 중 약 6 cm 를 추종에서 잃음(굽은 곳 모서리 깎기 + 상자 옆 차체 5° 기울어짐).
      anal_track_err.py 는 /plan_smoothed(map, 2 s 창) 대비 '방향 없는 거리' 라 안쪽/바깥쪽 · 장애물 쪽/반대쪽을 못 가름.
      여기서는 컨트롤러가 실제로 받은 경로(/transformed_global_plan)를 틱마다 써서 부호 있는 치우침을 잰다.
  경로 선택: /transformed_global_plan(odom, MPPI 가 매 틱 발행 = 로버 최근접점부터 prune_distance 1.0 m 앞까지).
      → 로버 자세도 odom→base_link 를 그 메시지 header.stamp 시각으로 보간해 같은 odom 좌표에서 비교(map→odom 변환 오차가 끼지 않음).
      상자 거리 · 상자 쪽 부호만 map 에서(map→odom ∘ odom→base_link, 같은 stamp, map→odom 은 같은 stamp 두 번 발행 → 마지막 값).
  지표(틱마다, 병진 중인 틱만 = /odometry/filtered |vx| ≥ 0.02 m/s — 제자리 회전 · 정지 틱은 방향 오차를 부풀리므로 빼고 수만 셈):
    (a) 옆 치우침 e = 경로 최근접점에서 왼쪽 법선 방향 로버 중심 거리(+ 왼쪽).
        부호 변환: e_in = e × sign(굽음 방향)(+ = 굽은 길 안쪽, 굽은 구간에서만 의미),
                  e_obs = e × (가장 가까운 로컬 코스트맵 치명 칸(값 100)이 경로 왼쪽이면 +1, 오른쪽이면 −1)(+ = 장애물 쪽, 1.0 m 안에 치명 칸 있을 때만).
    (b) 방향 오차 = 로버 yaw − 최근접점 경로 접선(접선 = 최근접점 앞뒤 0.05 m 현), 후진 주행(vx < −0.01)은 yaw + π 로 비교.
    (c) 곡률 = 최근접점에서 0.5 m 앞까지 순 방향 변화(°/0.5 m) = 시작 접선(0~0.1 m 현) ↔ 끝 접선(0.4~0.5 m 현) 차이, 부호 + = 왼쪽 굽음.
        ⚠ anal_track_err.py 의 '굽은 구간'(0.5 m 안 방향 최댓값 − 최솟값, 격자 지그재그 포함)과 정의가 다름 — 지그재그에 덜 민감.
        남은 경로 < 0.5 m 면 곡률 미정(목표 근처) → '짧음' 칸.
    분류: 직선 < 15° · 중간 15~30° · 굽음 ≥ 30°.
  상자 창: 로버 중심(map) ↔ 상자 사각형 거리 ≤ 0.6 m. 상자 = 2026-10-22/jobs/anal_contact.py 의 BOX(x 1.151~1.261, y −0.20~−0.02, 기록 위치).
      e_box = e × (상자 중심이 경로 왼쪽이면 +1) (+ = 상자 쪽), 방향 오차 부호도 상자 쪽 + . 차체 외곽(FP, 패딩 없음) ↔ 상자 최소 거리도 같이.
  출력: 주행별 분포(중앙 · 95 % · 최대, cm/°), 굽음에서 안쪽 비율, 상자 창 요약 + 상자 창 0.5 s 간격 시간열.
  인자: name=bag [name=bag ...]  (bag = 압축 푼 rosbag2 폴더)"""
import sys, math, bisect, datetime
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

TS = get_typestore(Stores.ROS2_HUMBLE)
BOX = (1.151, 1.261, -0.20, -0.02)                      # anal_contact.py 와 같은 상자(기록 위치, map)
BOXC = np.array([(BOX[0] + BOX[1]) / 2, (BOX[2] + BOX[3]) / 2])
FP = np.array([[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]])   # 차체 외곽(패딩 없음)
KST = datetime.timezone(datetime.timedelta(hours=9))
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
stamp = lambda h: h.stamp.sec + h.stamp.nanosec * 1e-9


def comp(a, b):
    c, s = math.cos(a[2]), math.sin(a[2])
    return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], a[2] + b[2])


def interp(L, Lt, t):
    """시각 t 의 (x, y, yaw) 선형 보간(양끝 밖이면 끝값)."""
    i = bisect.bisect_right(Lt, t)
    if i <= 0: return L[0][1]
    if i >= len(L): return L[-1][1]
    (t0, a), (t1, b) = L[i - 1], L[i]
    if t1 - t0 < 1e-6: return b
    u = (t - t0) / (t1 - t0)
    return (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]), a[2] + u * wrap(b[2] - a[2]))


def latest(L, Lt, t):
    """시각 t 이하 마지막 값(같은 stamp 가 여럿이면 마지막)."""
    return L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]


def project(P, q):
    """폴리라인 P 위 q 의 최근접점: (호 길이 s, 점, 세그먼트 번호)."""
    a, b = P[:-1], P[1:]; ab = b - a
    L2 = np.maximum(np.einsum('ij,ij->i', ab, ab), 1e-12)
    u = np.clip(np.einsum('ij,ij->i', q - a, ab) / L2, 0, 1)
    proj = a + u[:, None] * ab
    k = int(np.argmin(np.linalg.norm(proj - q, axis=1)))
    cum = np.r_[0, np.cumsum(np.sqrt(L2))]
    return cum[k] + u[k] * math.sqrt(L2[k]), proj[k], cum


def at_s(P, cum, s):
    """호 길이 s 의 점(범위 밖은 끝점)."""
    s = min(max(s, 0.0), cum[-1]); k = min(int(np.searchsorted(cum, s, side='right')) - 1, len(P) - 2)
    seg = cum[k + 1] - cum[k]; u = 0 if seg < 1e-12 else (s - cum[k]) / seg
    return P[k] + u * (P[k + 1] - P[k])


def chord_heading(P, cum, s0, s1):
    a, b = at_s(P, cum, s0), at_s(P, cum, s1)
    return math.atan2(b[1] - a[1], b[0] - a[0])


def rect_dist_poly(poly):
    """차체 다각형 ↔ 상자 사각형 최소 거리(변 표본, 겹치면 0)."""
    t = np.linspace(0, 1, 30)[:, None]; best = 9.0
    for i in range(4):
        p, q = poly[i], poly[(i + 1) % 4]; S = p + (q - p) * t
        dx = np.maximum(np.maximum(BOX[0] - S[:, 0], S[:, 0] - BOX[1]), 0); dy = np.maximum(np.maximum(BOX[2] - S[:, 1], S[:, 1] - BOX[3]), 0)
        best = min(best, float(np.min(np.hypot(dx, dy))))
    return best


def stat(v, scale=100.0):
    v = np.asarray(v, float)
    if not len(v): return '없음'
    return '중앙 %+5.1f · 95 %% %+5.1f · 최대 %+5.1f · 최소 %+5.1f (n %d)' % (scale * np.median(v), scale * np.percentile(v, 95), scale * v.max(), scale * v.min(), len(v))


def astat(v, scale=100.0):
    v = np.abs(np.asarray(v, float))
    if not len(v): return '없음'
    return '중앙 %5.1f · 95 %% %5.1f · 최대 %5.1f (n %d)' % (scale * np.median(v), scale * np.percentile(v, 95), scale * v.max(), len(v))


def run(name, bag):
    OB, MO, TGP, LC, OD = [], [], [], [], []
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        T0 = rd.start_time * 1e-9
        want = ('/tf', '/transformed_global_plan', '/local_costmap/costmap', '/odometry/filtered')
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in want]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((stamp(tr.header), v))
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((stamp(tr.header), v))
            elif c.topic == '/transformed_global_plan':
                if m.header.frame_id != 'odom': continue
                P = np.array([[p.pose.position.x, p.pose.position.y] for p in m.poses])
                TGP.append((stamp(m.header), t * 1e-9, P))
            elif c.topic == '/local_costmap/costmap':
                g = m.info; A = np.array(m.data, np.int16).reshape(g.height, g.width); ys, xs = np.nonzero(A >= 100)
                LC.append((t * 1e-9, m.header.frame_id, np.c_[g.origin.position.x + (xs + .5) * g.resolution, g.origin.position.y + (ys + .5) * g.resolution]))
            else:
                OD.append((t * 1e-9, m.twist.twist.linear.x, m.twist.twist.angular.z))
    for L in (OB, MO): L.sort(key=lambda q: q[0])
    OBt = [q[0] for q in OB]; MOt = [q[0] for q in MO]; LCt = [q[0] for q in LC]; ODt = [q[0] for q in OD]
    assert all(q[1] == 'odom' for q in LC), '로컬 코스트맵 frame 이 odom 이 아님'
    clock = lambda t: datetime.datetime.fromtimestamp(t, KST).strftime('%H:%M:%S.%f')[:10]
    rows = []                                           # 틱마다 결과
    n_rot = n_stop = 0
    for ts, tb, P in TGP:
        if len(P) < 3 or ts < OBt[0] or ts < MOt[0]: continue
        od = OD[max(bisect.bisect_right(ODt, tb) - 1, 0)]
        vx, wz = od[1], od[2]
        if abs(vx) < 0.02:                               # 병진 아닌 틱(제자리 회전 · 정지)은 수만 셈
            n_rot += abs(wz) > 0.05; n_stop += abs(wz) <= 0.05; continue
        r = interp(OB, OBt, ts)                          # odom 기준 로버
        q = np.array(r[:2]); s0, foot, cum = project(P, q)
        th = chord_heading(P, cum, s0 - 0.05, s0 + 0.05) if cum[-1] > 0.1 else math.atan2(P[-1, 1] - P[0, 1], P[-1, 0] - P[0, 0])
        nrm = np.array([-math.sin(th), math.cos(th)])   # 왼쪽 법선
        e = float(np.dot(q - foot, nrm))
        yaw = r[2] + (math.pi if vx < -0.01 else 0.0)
        he = wrap(yaw - th)                              # + = 로버 코가 경로보다 왼쪽
        if cum[-1] - s0 >= 0.5:
            turn = math.degrees(wrap(chord_heading(P, cum, s0 + 0.4, s0 + 0.5) - chord_heading(P, cum, s0, s0 + 0.1)))
        else:
            turn = None
        # 가장 가까운 로컬 치명 칸(odom, 1.0 m 안)
        lc = LC[max(bisect.bisect_right(LCt, tb) - 1, 0)][2] if LC else np.zeros((0, 2))
        obs_side = 0
        if len(lc):
            d = np.linalg.norm(lc - q, axis=1); j = int(np.argmin(d))
            if d[j] <= 1.0: obs_side = 1 if np.dot(lc[j] - foot, nrm) > 0 else -1
        # map 기준(상자)
        mo = latest(MO, MOt, ts); pm = comp(mo, r); pm = (pm[0], pm[1], wrap(pm[2]))
        qm = np.array(pm[:2])
        dx = max(BOX[0] - qm[0], qm[0] - BOX[1], 0); dy = max(BOX[2] - qm[1], qm[1] - BOX[3], 0); dbox = math.hypot(dx, dy)
        box_side = 0; fpd = None
        if dbox <= 0.6:
            # 상자 중심을 odom 으로 옮겨 경로 왼쪽/오른쪽 판단
            c, s_ = math.cos(mo[2]), math.sin(mo[2]); bx, by = BOXC[0] - mo[0], BOXC[1] - mo[1]
            bo = np.array([c * bx + s_ * by, -s_ * bx + c * by])
            box_side = 1 if np.dot(bo - foot, nrm) > 0 else -1
            cy, sy = math.cos(pm[2]), math.sin(pm[2]); poly = np.c_[pm[0] + cy * FP[:, 0] - sy * FP[:, 1], pm[1] + sy * FP[:, 0] + cy * FP[:, 1]]
            fpd = rect_dist_poly(poly)
        rows.append(dict(ts=ts, e=e, he=he, turn=turn, obs=obs_side, dbox=dbox, bside=box_side, fpd=fpd, pm=pm, vx=vx))

    print('=' * 100)
    print('%s · 틱(경로 메시지) %d · 병진 틱 %d · 제자리 회전 틱 %d · 정지 틱 %d · 경로 = /transformed_global_plan(odom)' % (name, len(TGP), len(rows), n_rot, n_stop))
    if not rows: return
    cls = {'직선(<15°)': [], '중간(15~30°)': [], '굽음(≥30°)': [], '짧음(남은 경로<0.5 m)': []}
    for r in rows:
        k = '짧음(남은 경로<0.5 m)' if r['turn'] is None else ('직선(<15°)' if abs(r['turn']) < 15 else ('중간(15~30°)' if abs(r['turn']) < 30 else '굽음(≥30°)'))
        cls[k].append(r)
    print(' 곡률 분포(°/0.5 m, 순 방향 변화 절댓값): %s' % astat([r['turn'] for r in rows if r['turn'] is not None], 1.0))
    print(' (a) 옆 치우침 |e| cm · (b) 방향 오차 |he| ° — 곡률 칸별')
    for k, L in cls.items():
        print('   %-18s |e| %s' % (k, astat([r['e'] for r in L])))
        print('   %-18s |he| %s' % ('', astat([math.degrees(r['he']) for r in L], 1.0)))
    B = cls['굽음(≥30°)']
    if B:
        ein = [r['e'] * (1 if r['turn'] > 0 else -1) for r in B]
        hin = [math.degrees(r['he']) * (1 if r['turn'] > 0 else -1) for r in B]
        frac = np.mean(np.array(ein) > 0); frac2 = np.mean(np.array(ein) > 0.02)
        print(' 굽음(≥30°): 안쪽(+) 부호 치우침 e_in cm %s' % stat(ein))
        print('            안쪽 비율 %.0f %% (e_in > 0) · 안쪽 2 cm 넘음 %.0f %% · 바깥 2 cm 넘음 %.0f %%' % (100 * frac, 100 * frac2, 100 * np.mean(np.array(ein) < -0.02)))
        print('            방향 오차 안쪽(+) ° %s' % stat(hin, 1.0))
    M = cls['중간(15~30°)']
    if M:
        ein = [r['e'] * (1 if r['turn'] > 0 else -1) for r in M]
        print(' 중간(15~30°): e_in cm %s · 안쪽 비율 %.0f %%' % (stat(ein), 100 * np.mean(np.array(ein) > 0)))
    O = [r for r in rows if r['obs'] != 0]
    if O:
        eo = [r['e'] * r['obs'] for r in O]
        print(' 1.0 m 안 치명 칸 있는 틱 %d: 장애물 쪽(+) e_obs cm %s · 장애물 쪽 비율 %.0f %%' % (len(O), stat(eo), 100 * np.mean(np.array(eo) > 0)))
        for k in ('직선(<15°)', '굽음(≥30°)'):
            eo2 = [r['e'] * r['obs'] for r in cls[k] if r['obs'] != 0]
            if eo2: print('   %-12s e_obs cm %s · 장애물 쪽 비율 %.0f %%' % (k, stat(eo2), 100 * np.mean(np.array(eo2) > 0)))
    W = [r for r in rows if r['bside'] != 0]
    print(' 상자 창(로버 중심 ↔ 상자 ≤ 0.6 m): 병진 틱 %d' % len(W))
    if W:
        eb = [r['e'] * r['bside'] for r in W]; hb = [math.degrees(r['he']) * r['bside'] for r in W]
        k = int(np.argmin([r['fpd'] for r in W])); rm = W[k]
        print('   상자 쪽(+) 치우침 e_box cm %s · 상자 쪽 비율 %.0f %%' % (stat(eb), 100 * np.mean(np.array(eb) > 0)))
        print('   상자 쪽(+) 방향 오차 ° %s' % stat(hb, 1.0))
        print('   차체 ↔ 상자 최소 %.3f m @ %s 로버 map (%.2f, %.2f, %.0f°) · 그 틱 e_box %+.1f cm · 방향 %+.1f° · 곡률 %s'
              % (rm['fpd'], clock(rm['ts']), rm['pm'][0], rm['pm'][1], math.degrees(rm['pm'][2]), 100 * eb[k], hb[k],
                 '-' if rm['turn'] is None else '%+.0f°' % rm['turn']))
        # 지나감별(2 s 넘게 끊기면 다른 지나감)
        segs = [[0]]
        for i in range(1, len(W)):
            (segs[-1].append(i) if W[i]['ts'] - W[i - 1]['ts'] <= 2.0 else segs.append([i]))
        for sg in segs:
            E = np.array([eb[i] for i in sg]); H = np.array([hb[i] for i in sg]); F = [W[i]['fpd'] for i in sg]; j = sg[int(np.argmin(F))]
            print('   지나감 %s~%s (yaw 중앙 %.0f°, 틱 %d): e_box 중앙 %+.1f · 최대 %+.1f · 최소 %+.1f cm · he_box 중앙 %+.1f · 최대 %+.1f° · 차체↔상자 최소 %.3f m @ %s (그 틱 e_box %+.1f cm · he %+.1f° · 곡률 %s)'
                  % (clock(W[sg[0]]['ts']), clock(W[sg[-1]]['ts']), math.degrees(np.median([W[i]['pm'][2] for i in sg])), len(sg), 100 * np.median(E), 100 * E.max(), 100 * E.min(),
                     np.median(H), H.max(), W[j]['fpd'], clock(W[j]['ts']), 100 * eb[j], hb[j], '-' if W[j]['turn'] is None else '%+.0f°' % W[j]['turn']))
        # 상자 창 시간열(창마다 0.5 s 간격)
        print('   시간열(0.5 s): 시각 · 로버 map x,y,yaw · 상자거리(중심) · 차체↔상자 · e_box cm · he_box ° · 곡률 °/0.5 m')
        last = -9
        for r, e1, h1 in zip(W, eb, hb):
            if r['ts'] - last < 0.5: continue
            last = r['ts']
            print('     %s (%5.2f, %5.2f, %5.0f°) %.2f %.3f %+5.1f %+5.1f %s' % (clock(r['ts']), r['pm'][0], r['pm'][1], math.degrees(r['pm'][2]), r['dbox'], r['fpd'], 100 * e1, h1,
                                                                            '-' if r['turn'] is None else '%+4.0f' % r['turn']))


if __name__ == '__main__':
    print('anal_ctrl_eval · 상자 = anal_contact.py BOX %s · 부호: e 왼쪽 + / e_in 굽은 길 안쪽 + / e_obs 가장 가까운 치명 칸 쪽 + / e_box 상자 쪽 +' % (BOX,))
    for a in sys.argv[1:]:
        n, b = a.split('=', 1); run(n, b)
