#!/usr/bin/env python3
"""fig_place_run — 장소 이름 명령 주행(F2.5 place_server) 한 번을 그림 한 장으로 (2026-10-28 §14, PC).
  위 왼쪽: 지도(/map) 위 궤적 — 명령마다 색, 등록 장소 · 도착 · 정지 자리 표시.
  위 오른쪽: 명령 목록(보낸 명령 → 끝 상태 · 소요 · 서버가 붙인 설명).
  아래: 시간축 — 명령 막대(보낸 때 → 끝 상태) 위에 상태 사건(accepted · moving · arrived …), 그 밑에 지령 속도 /cmd_vel.
  입력은 bag 하나(/place/command · /place/status · /tf · /map · /cmd_vel) + 등록부(places.yaml).
  색: Okabe–Ito 순서(색각 이상 구분용으로 널리 쓰는 8 색) — 명령 순서대로 고정 배정.
  인자: bag폴더 places.yaml 출력.png [제목] [nav2.log — 막힘 재계획 · 주행 중단을 표시]"""
import sys, math, json, time
import numpy as np
import yaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False})
INK, INK2, MUTED, GRID = '#1d232b', '#4a5360', '#8a929c', '#e3e6ea'
PAL = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442', '#000000']
STATE_MK = {'accepted': ('o', 'none'), 'moving': ('>', None), 'arrived': ('*', None), 'checked': ('*', None), 'info': ('s', None),
            'canceled': ('X', None), 'failed': ('X', None), 'rejected': ('X', None)}

bag, reg_path, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
title = sys.argv[4] if len(sys.argv) > 4 else bag.name
reg = yaml.safe_load(open(reg_path, encoding='utf-8'))
yaw = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
CMD, ST, mo, ob, cv, MAP = [], [], [], [], [], None
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/place/command', '/place/status', '/tf', '/map', '/cmd_vel')]):
        ts = t * 1e-9; m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/place/command':
            rid, _, txt = m.data.partition('|'); CMD.append((ts, rid, txt))
        elif c.topic == '/place/status':
            try: ST.append((ts, json.loads(m.data)))
            except ValueError: pass
        elif c.topic == '/map': MAP = m
        elif c.topic == '/cmd_vel': cv.append((ts, m.linear.x, m.angular.z))
        else:
            for tr in m.transforms:
                p = (ts, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation))
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append(p)
                elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append(p)

# 명령 단위로 묶기: 보낸 명령(rid) → 그 rid 의 상태들. stop 은 앞 이동 명령에 딸린 사건으로 붙인다(@stop 시험).
END = ('arrived', 'checked', 'failed', 'canceled', 'rejected', 'info')
runs = []
for ts, rid, txt in CMD:
    ss = [(t, d) for t, d in ST if d.get('id') == rid]
    if txt.strip() == 'stop' and runs:
        runs[-1]['stop'] = ts; runs[-1]['events'] += [(t, d) for t, d in ss]; continue
    ends = [t for t, d in ss if d['state'] in END]
    runs.append({'t0': ts, 'txt': txt, 'events': ss, 't1': ends[0] if ends else (ss[-1][0] if ss else ts), 'stop': None})
# 같은 조회를 다시 보낸 경우(place_cmd 재전송) — 응답 없는 앞 것은 '응답 없음' 으로 남긴다
T0 = runs[0]['t0'] if runs else cv[0][0]
T1 = max([r['t1'] for r in runs] + [T0 + 1])

last = lambda L, t: L[max(np.searchsorted([x[0] for x in L], t, side='right') - 1, 0)]
def pose(t):
    _, mx, my, ma = last(mo, t); _, ox, oy, oa = last(ob, t); c, s = math.cos(ma), math.sin(ma)
    return mx + c * ox - s * oy, my + s * ox + c * oy, ma + oa

fig = plt.figure(figsize=(16, 10.8), facecolor='white')
gs = GridSpec(3, 2, figure=fig, width_ratios=[1.55, 1], height_ratios=[3.2, 1.25, 0.75], left=0.05, right=0.98, top=0.885, bottom=0.06, hspace=0.32, wspace=0.10)
fig.text(0.05, 0.965, title, fontsize=19, fontweight='bold', color=INK, va='center')
fig.text(0.05, 0.937, '%s ~ %s · 명령 %d 개 · 궤적 = SLAM map 좌표(map→odom × odom→base_link)' % (
    time.strftime('%H:%M:%S', time.localtime(T0)), time.strftime('%H:%M:%S', time.localtime(T1)), len(runs)), fontsize=11, color=INK2, va='center')

# ── 지도 · 궤적
am = fig.add_subplot(gs[0, 0])
if MAP is not None:
    i = MAP.info; g = np.array(MAP.data, np.int16).reshape(i.height, i.width)
    img = np.full(g.shape + (3,), 0.97); img[g < 0] = 0.90; img[g >= 65] = 0.35
    am.imshow(img, origin='lower', extent=[i.origin.position.x, i.origin.position.x + i.width * i.resolution,
                                          i.origin.position.y, i.origin.position.y + i.height * i.resolution], interpolation='nearest', zorder=0)
xs_all, ys_all = [], []
for k, r in enumerate(runs):
    col = PAL[k % len(PAL)]
    ts = np.arange(r['t0'], r['t1'] + 0.05, 0.1)
    if r['t1'] - r['t0'] > 1.0 and mo and ob:
        P = np.array([pose(t)[:2] for t in ts]); am.plot(P[:, 0], P[:, 1], color=col, lw=2.2, zorder=3, solid_capstyle='round')
        xs_all += list(P[:, 0]); ys_all += list(P[:, 1])
        ex, ey, ea = pose(r['t1']); st = [d['state'] for t, d in r['events'] if d['state'] in END]
        mk = '*' if st and st[0] in ('arrived', 'checked') else 'X'
        am.scatter([ex], [ey], marker=mk, s=230 if mk == '*' else 120, color=col, edgecolor='white', linewidth=1.2, zorder=6)
        am.annotate('', xy=(ex + 0.30 * math.cos(ea), ey + 0.30 * math.sin(ea)), xytext=(ex, ey), arrowprops=dict(arrowstyle='-|>', color=col, lw=1.6), zorder=6)
        if r['stop']:
            sx, sy, _ = pose(r['stop']); am.scatter([sx], [sy], marker='|', s=260, color=INK, linewidth=2.5, zorder=7)
            am.annotate('stop', (sx, sy), xytext=(6, 8), textcoords='offset points', fontsize=10, color=INK, fontweight='bold')
if mo and ob:
    sx, sy, _ = pose(T0); am.scatter([sx], [sy], marker='o', s=90, facecolor='white', edgecolor=INK, linewidth=1.8, zorder=7)
    am.annotate('출발', (sx, sy), xytext=(-8, -16), textcoords='offset points', fontsize=10, color=INK, ha='right')
used = {r['txt'].split(None, 1)[1].strip() for r in runs if r['txt'].startswith('go_to ') and len(r['txt'].split(None, 1)) > 1}
for p in reg['places']:
    names = {p['name'], *(p.get('aliases') or [])}; hit = bool(names & used) or (p['name'] == reg.get('home') and any(r['txt'].strip() == 'return' for r in runs))
    am.scatter([p['x']], [p['y']], marker='D', s=46 if hit else 26, facecolor='white' if hit else 'none', edgecolor=INK if hit else MUTED, linewidth=1.4, zorder=5)
    am.annotate(p['name'], (p['x'], p['y']), xytext=(7, -3), textcoords='offset points', fontsize=11 if hit else 9, color=INK if hit else MUTED, fontweight='bold' if hit else 'normal', zorder=8)
    xs_all.append(p['x']); ys_all.append(p['y'])
if xs_all:
    cx, cy = (min(xs_all) + max(xs_all)) / 2, (min(ys_all) + max(ys_all)) / 2; h = max(max(xs_all) - min(xs_all), (max(ys_all) - min(ys_all)) * 1.55) / 2 + 0.8
    am.set_xlim(cx - h, cx + h); am.set_ylim(cy - h / 1.55, cy + h / 1.55)
am.set_aspect('equal'); am.tick_params(colors=MUTED, labelsize=9); [s.set_color(GRID) for s in am.spines.values()]
am.set_xlabel('map x (m)', color=MUTED, fontsize=10); am.set_ylabel('map y (m)', color=MUTED, fontsize=10)
am.set_title('지도 위 궤적 — ◇ 등록 장소 · ★ 도착 · × 실패/취소 끝 · | stop 보낸 자리 · 화살표 = 끝 방향', fontsize=11, color=INK2, loc='left')

# ── 명령 목록
al = fig.add_subplot(gs[0, 1]); al.axis('off')
al.text(0, 1.0, '보낸 명령과 결과', fontsize=14, fontweight='bold', color=INK, va='top', transform=al.transAxes)
y = 0.93
for k, r in enumerate(runs):
    col = PAL[k % len(PAL)]; st = [d for t, d in r['events'] if d['state'] in END]; e = st[0] if st else None
    al.add_patch(plt.Rectangle((0, y - 0.028), 0.022, 0.03, color=col, transform=al.transAxes, clip_on=False))
    al.text(0.04, y, '%d. %s' % (k + 1, r['txt']), fontsize=13, color=INK, va='top', fontweight='bold', transform=al.transAxes)
    res = '%s · %.1f s' % (e['state'], r['t1'] - r['t0']) if e else '끝 상태 없음'
    if r['stop']: res += ' (stop: 이동 %.1f s 뒤)' % (r['stop'] - min([t for t, d in r['events'] if d['state'] == 'moving'] or [r['t0']]))
    al.text(0.98, y, res, fontsize=12, color=INK, va='top', ha='right', family='Malgun Gothic', transform=al.transAxes)
    det = ''
    for t, d in r['events']:
        if d['state'] in ('moving', 'accepted') and d.get('detail'): det = d['detail']
    if e and e.get('detail'): det = (det + ' │ ' if det else '') + e['detail']
    if det:
        import textwrap
        lines = textwrap.wrap(det, 52)[:4]
        for j, ln in enumerate(lines): al.text(0.04, y - 0.045 - j * 0.037, ln, fontsize=9.5, color=INK2, va='top', transform=al.transAxes)
        y -= 0.045 + len(lines) * 0.037 + 0.035
    else: y -= 0.08

# ── 시간축: 명령 막대 + 상태 사건
at = fig.add_subplot(gs[1, :]); n = max(len(runs), 1)
for k, r in enumerate(runs):
    col = PAL[k % len(PAL)]; yk = n - 1 - k
    at.barh(yk, max(r['t1'] - r['t0'], 0.4), left=r['t0'] - T0, height=0.36, color=col, alpha=0.28, edgecolor=col, linewidth=1.2)
    at.text(r['t0'] - T0, yk + 0.24, r['txt'], fontsize=9.5, color=INK, va='bottom')
    for t, d in r['events']:
        m_, fc = STATE_MK.get(d['state'], ('.', None))
        at.scatter([t - T0], [yk], marker=m_, s=70, facecolor=col if fc is None else fc, edgecolor=col, linewidth=1.4, zorder=4)
    if r['stop']: at.axvline(r['stop'] - T0, ymin=0, ymax=1, color=INK, lw=1.0, ls='--')
at.set_yticks([]); at.set_xlim(-2, T1 - T0 + 2); at.set_ylim(-0.5, n - 0.05)
at.tick_params(colors=MUTED, labelsize=9); [s.set_color(GRID) for s in at.spines.values()]
at.set_title('명령 흐름 — 막대 = 보낸 때 → 끝 상태 · ○ accepted · ▶ moving · ★ arrived · ■ info · × canceled/failed/rejected', fontsize=11, color=INK2, loc='left')

av = fig.add_subplot(gs[2, :], sharex=at)
if cv:
    C = np.array(cv); k = (C[:, 0] >= T0 - 2) & (C[:, 0] <= T1 + 2)
    av.plot(C[k, 0] - T0, C[k, 1], color=INK, lw=1.0, label='전진 지령 v (m/s)')
    av.plot(C[k, 0] - T0, C[k, 2] * 0.1, color=MUTED, lw=0.8, label='회전 지령 ω × 0.1 (rad/s)')
# nav2.log(선택, 다섯째 인자)의 BT 사건: 막힘 재계획(PathBlockedAhead '지속') · 주행 중단 — 지령 그래프 위 세로선 + 지도 위 표시
if len(sys.argv) > 5:
    import re
    seen = set()
    for ln in open(sys.argv[5], encoding='utf-8', errors='replace'):
        mt = re.search(r'\[(1\d{9}\.\d+)\]', ln)
        if not mt: continue
        t = float(mt.group(1))
        if not (T0 <= t <= T1): continue
        kind = '막힘 → 재계획' if ('PathBlockedAhead' in ln and '→' in ln) else '주행 중단' if 'Aborting' in ln or 'aborted' in ln.lower() else None
        if not kind or any(abs(t - s) < 1.0 for s in seen): continue
        seen.add(t); av.axvline(t - T0, color=PAL[5], lw=1.4); at.axvline(t - T0, color=PAL[5], lw=1.0, alpha=0.7)
        av.annotate(kind, (t - T0, av.get_ylim()[1] if cv else 0.08), xytext=(3, -12), textcoords='offset points', fontsize=9, color=PAL[5], fontweight='bold')
        if mo and ob:
            bx, by, _ = pose(t); am.scatter([bx], [by], marker='o', s=80, facecolor='none', edgecolor=PAL[5], linewidth=2.0, zorder=8)
            am.annotate(kind, (bx, by), xytext=(6, 6), textcoords='offset points', fontsize=9.5, color=PAL[5], fontweight='bold', zorder=8)
av.axhline(0, color=GRID, lw=0.8); av.grid(axis='y', color=GRID, lw=0.6)
av.tick_params(colors=MUTED, labelsize=9); [s.set_color(GRID) for s in av.spines.values()]
av.set_xlabel('첫 명령부터 초', color=MUTED, fontsize=10); av.legend(loc='lower right', bbox_to_anchor=(1.0, 1.0), frameon=False, fontsize=9, labelcolor=INK2, ncol=2)
av.set_title('/cmd_vel — 컨트롤러가 낸 지령', fontsize=11, color=INK2, loc='left')
fig.savefig(out, dpi=110); print('그림', out, '· 명령', len(runs), '· 궤적 점', len(xs_all))
