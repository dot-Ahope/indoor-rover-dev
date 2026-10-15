#!/usr/bin/env python3
"""anal_box_true_vs_map — 출발점 시험 상자의 기록 위치(고정)와 로컬 코스트맵이 찍은 상자 칸을 지도 좌표에서 비교. (2026-10-15 §29.4, 오늘만)
  왜: 사용자 "상자 옆 여유 상당히 많았고, 그리고도 또 더 회피해서 움직이는 모습을 보였다(복귀시) 상자 위치는 항상 동일하므로, 기록된 상자 위치와 센서가 인식한 상자 위치 비교."
  기록 상자(TEST_COURSE_AND_GATES §1 · 10-15 §23): 앞면 x 1.151, 깊이 0.11 → x 1.151~1.261, 폭 0.18 · 중심 y −0.11 → y −0.20~−0.02 (지도, 출발 자세 = 원점).
    ⚠ 출발 자세는 prep 마다 (0, 0, 0°) 로 잡히므로 테이프에 놓은 오차(1~2 cm · 1° ≈ 1.2 m 에서 2 cm)가 그대로 섞인다.
  프레임마다(지도 좌표 = map→odom ∘ 코스트맵): 상자 구역(x 0.95~1.50, y −0.45~+0.25) 치명 칸, 칸 가장자리 기준 북 · 남 · 서 · 동 면,
    실제 여유 = 차체(패딩 포함 · 패딩 없는 몸체) ↔ 기록 상자 직사각형 최소 거리, 지도 여유 = 차체(패딩 포함) ↔ 그 칸 중심 최소 거리.
  출력: 로버가 상자 옆(지도 x 0.9~1.7, |y| < 0.6)에 있는 프레임 표 + 요약. 인자: 이름=bag ...  [--fig 그림경로]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

BOX = (1.151, 1.261, -0.20, -0.02)   # x0, x1, y0, y1 (지도)
REG = (0.95, 1.50, -0.45, 0.25)
PAD = (0.272, -0.258, 0.175)          # 패딩 포함 풋프린트
BODY = (0.262, -0.248, 0.165)         # 패딩 없는 몸체
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
hms = lambda ts: time.strftime('%H:%M:%S', time.localtime(ts)) + '.%d' % (int(ts * 10) % 10)
compose = lambda A, B: (A[0] + math.cos(A[2]) * B[0] - math.sin(A[2]) * B[1], A[1] + math.sin(A[2]) * B[0] + math.cos(A[2]) * B[1], A[2] + B[2])


def rect_pts_dist(P, F, px, py):
    """차체 직사각형 F(앞, 뒤, 반폭) at P 와 점들 사이 최소 거리"""
    c, s = math.cos(P[2]), math.sin(P[2]); dx, dy = px - P[0], py - P[1]; bx = c * dx + s * dy; by = -s * dx + c * dy
    return np.hypot(np.maximum(np.maximum(F[1] - bx, bx - F[0]), 0), np.maximum(np.abs(by) - F[2], 0))


def rect_box_dist(P, F):
    """차체 직사각형 ↔ 기록 상자 직사각형 최소 거리(두 볼록 다각형: 꼭짓점 · 변 표본으로 1 mm 정밀)"""
    x0, x1, y0, y1 = BOX; t = np.linspace(0, 1, 120)
    bx = np.concatenate([x0 + (x1 - x0) * t, np.full_like(t, x1), x1 - (x1 - x0) * t, np.full_like(t, x0)])
    by = np.concatenate([np.full_like(t, y0), y0 + (y1 - y0) * t, np.full_like(t, y1), y1 - (y1 - y0) * t])
    d1 = rect_pts_dist(P, F, bx, by).min()
    # 차체 변 표본 → 상자까지(상자가 차체보다 작아 꼭짓점만으론 부족할 때 대비)
    c, s = math.cos(P[2]), math.sin(P[2]); f, r, h = F
    ex = np.concatenate([f + 0 * t, r + (f - r) * t, r + 0 * t, r + (f - r) * t]); ey = np.concatenate([-h + 2 * h * t, np.full_like(t, h), -h + 2 * h * t, np.full_like(t, -h)])
    wx = P[0] + c * ex - s * ey; wy = P[1] + s * ex + c * ey
    d2 = np.hypot(np.maximum(np.maximum(x0 - wx, wx - x1), 0), np.maximum(np.maximum(y0 - wy, wy - y1), 0)).min()
    return min(d1, d2)


args = [a for a in sys.argv[1:] if not a.startswith('--')]; fig = None
if '--fig' in sys.argv: fig = sys.argv[sys.argv.index('--fig') + 1]; args = [a for a in args if a != fig]
RES = {}
for arg in args:
    nm, bag = arg.split('=')
    mo = None; ob = None; rows = []; cells_all = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                    if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo = v
                    elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob = v
                continue
            if mo is None or ob is None: continue
            P = compose(mo, ob)
            if not (0.9 <= P[0] <= 1.7 and abs(P[1]) < 0.6): continue
            a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100); r = m.info.resolution
            ox_, oy_ = m.info.origin.position.x + (ix + 0.5) * r, m.info.origin.position.y + (iy + 0.5) * r   # odom
            gx = mo[0] + math.cos(mo[2]) * ox_ - math.sin(mo[2]) * oy_; gy = mo[1] + math.sin(mo[2]) * ox_ + math.cos(mo[2]) * oy_
            k = (gx > REG[0]) & (gx < REG[1]) & (gy > REG[2]) & (gy < REG[3]); gx, gy = gx[k], gy[k]
            real_pad = rect_box_dist(P, PAD); real_body = rect_box_dist(P, BODY)
            if len(gx):
                mapd = float(rect_pts_dist(P, PAD, gx, gy).min())
                faces = (gy.max() + r / 2, gy.min() - r / 2, gx.min() - r / 2, gx.max() + r / 2)   # 북 · 남 · 서 · 동 (칸 가장자리)
                cells_all.append(np.stack([gx, gy], 1))
            else:
                mapd = float('nan'); faces = (float('nan'),) * 4
            rows.append((t / 1e9, P, real_pad, real_body, mapd, len(gx), faces))
    RES[nm] = (rows, np.concatenate(cells_all) if cells_all else np.zeros((0, 2)))
    print('\n== %s · 상자 옆 프레임 %d · 기록 상자 x %.3f~%.3f · y %.2f~%.2f' % (nm, len(rows), *BOX))
    print('  시각        | 로버 지도 (x, y, yaw)        | 실제 여유 패딩 · 몸체 cm | 지도 여유 cm | 칸 | 면 북(실제 −0.020) 남(−0.200) 서(1.151) 동(1.261)')
    for st, P, rp, rb, md, nc, f in rows:
        print('  %s | (%+.3f, %+.3f, %+6.1f°) | %6.1f · %6.1f | %6.1f | %2d | %+.3f %+.3f %.3f %.3f' % (hms(st), P[0], P[1], math.degrees(P[2]), 100 * rp, 100 * rb, 100 * md, nc, *f))
    if rows:
        R = np.array([(r[2], r[4], r[6][0], r[6][2]) for r in rows], float); ok = ~np.isnan(R[:, 1])
        print('  요약: 실제 여유(패딩 포함) 최소 %.1f cm · 지도 여유 최소 %.1f cm · 같은 프레임 (실제 − 지도) 중앙 %.1f cm(범위 %.1f~%.1f) · 북쪽 면 중앙 %+.3f(실제보다 %+.1f cm 로버 쪽) · 서쪽 면 중앙 %.3f(%+.1f cm)'
              % (100 * R[:, 0].min(), 100 * np.nanmin(R[:, 1]), 100 * np.median(R[ok, 0] - R[ok, 1]), 100 * (R[ok, 0] - R[ok, 1]).min(), 100 * (R[ok, 0] - R[ok, 1]).max(),
                 np.nanmedian(R[:, 2]), 100 * (np.nanmedian(R[:, 2]) - BOX[3]), np.nanmedian(R[:, 3]), 100 * (BOX[0] - np.nanmedian(R[:, 3]))))

if fig:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']; plt.rcParams['axes.unicode_minus'] = False
    n = len(RES); f_, axs = plt.subplots(1, n, figsize=(4.6 * n, 4.8), squeeze=False)
    for ax, (nm, (rows, C)) in zip(axs[0], RES.items()):
        if len(C):
            u, cnt = np.unique(np.round(C / 0.01) * 0.01, axis=0, return_counts=True); fr = cnt / max(len(rows), 1)
            for (x, y), q in zip(u, fr): ax.add_patch(Rectangle((x - 0.025, y - 0.025), 0.05, 0.05, fc=(0.85, 0.35, 0.1, 0.15 + 0.6 * min(q, 1)), ec='none'))
        ax.add_patch(Rectangle((BOX[0], BOX[2]), BOX[1] - BOX[0], BOX[3] - BOX[2], fill=False, ec='k', lw=2, label='기록 상자'))
        P = np.array([r[1] for r in rows])
        if len(P): ax.plot(P[:, 0], P[:, 1], '.', ms=3, color='tab:blue', label='로버 중심(상자 옆 프레임)')
        if rows:
            k = int(np.argmin([r[2] for r in rows])); Pk = rows[k][1]; c, s = math.cos(Pk[2]), math.sin(Pk[2])
            cx = [PAD[0], PAD[0], PAD[1], PAD[1], PAD[0]]; cy = [PAD[2], -PAD[2], -PAD[2], PAD[2], PAD[2]]
            ax.plot([Pk[0] + c * a - s * b for a, b in zip(cx, cy)], [Pk[1] + s * a + c * b for a, b in zip(cx, cy)], color='tab:blue', lw=1.2,
                    label='실제 여유 최소 자세 %.1f cm' % (100 * rows[k][2]))
        ax.set_xlim(0.8, 1.8); ax.set_ylim(-0.5, 0.6); ax.set_aspect('equal'); ax.grid(alpha=0.3); ax.set_title(nm); ax.set_xlabel('지도 x (m)'); ax.set_ylabel('지도 y (m)')
        ax.legend(fontsize=7, loc='upper right')
    f_.suptitle('출발점 시험 상자: 기록 위치(검은 테) vs 로컬 코스트맵 치명 칸(주황, 진할수록 오래 찍힘)', fontsize=10)
    f_.tight_layout(); f_.savefig(fig, dpi=130); print('그림', fig)
