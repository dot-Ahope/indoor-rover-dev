#!/usr/bin/env python3
"""N4 주행 A/B 궤적 시각화 (09-22): 러너 csv(fwd, lat, clear_geo, lc_box)로 S 2 회·N2 3 회의 평면 궤적(base 출발 기준 전진 x·횡 y)과 코스트맵 여유 표를 한 페이지에.
  사용: python job512_trajviz.py <outputs_dir> <out.html>
  궤적 좌표: 출발 자세 기준(러너 csv fwd/lat). 상자: 게이트 검출 평균(전면 1.153, 중심 −0.09, 18×11 cm). 차체 0.50×0.33.
"""
import csv, sys, os, math
D, OUT = sys.argv[1], sys.argv[2]
RUNS = [('n4s1', 'S', 'STVL 1'), ('n4s2', 'S', 'STVL 2'), ('n4n1', 'N', 'nvblox 1'), ('n4n2', 'N', 'nvblox 2'), ('n4n3', 'N', 'nvblox 3')]
CLR = {'n4s1': 9.3, 'n4s2': 11.7, 'n4n1': 12.3, 'n4n2': 13.4, 'n4n3': 14.6}          # job416 코스트맵 상자 최소 여유 cm
RET = {'n4s1': 9.1, 'n4s2': 8.3, 'n4n1': 8.3, 'n4n2': 9.7, 'n4n3': 13.5}            # 복귀 회전 자리 실제 여유 cm (job446)
CPU = {'n4s1': 318, 'n4s2': 315, 'n4n1': 330, 'n4n2': 337, 'n4n3': 330}
T = {'n4s1': 31.6, 'n4s2': 30.9, 'n4n1': 31.6, 'n4n2': 31.4, 'n4n3': 32.2}
data = {}
for nm, _, _ in RUNS:
    rows = list(csv.DictReader(open(os.path.join(D, nm + '.csv'), encoding='utf-8')))
    data[nm] = [(float(r['fwd']), float(r['lat']), float(r['t'])) for r in rows]
    data[nm + '_lat'] = max(float(r['lat']) for r in rows if 1.0 < float(r['fwd']) < 1.4)
# SVG: x 전진 0~2.1 m (가로), y 횡 −0.3~+0.6 (세로, 위가 +y 왼쪽)
X0, X1, Y0, Y1 = -0.3, 2.2, -0.35, 0.65; PX = 300
W = (X1 - X0) * PX; H = (Y1 - Y0) * PX
def sx(x): return (x - X0) * PX
def sy(y): return (Y1 - y) * PX
def poly(nm):
    return ' '.join('%.1f,%.1f' % (sx(x), sy(y)) for x, y, _ in data[nm])
lines = []
for xv in (0, 0.5, 1.0, 1.5, 2.0):
    lines.append('<line x1="%.1f" y1="0" x2="%.1f" y2="%.1f" stroke="var(--grid)"/><text x="%.1f" y="%.1f" class="tick">%.1f m</text>' % (sx(xv), sx(xv), H, sx(xv) + 4, H - 6, xv))
for yv in (-0.2, 0, 0.2, 0.4, 0.6):
    lines.append('<line x1="0" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--grid)"/><text x="4" y="%.1f" class="tick">%+.1f</text>' % (sy(yv), W, sy(yv), sy(yv) - 4, yv))
box = '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="var(--boxfill)" stroke="var(--phys)" stroke-width="2"/>' % (sx(1.153), sy(-0.09 + 0.09), 0.11 * PX, 0.18 * PX)
furn = '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="var(--furn)"/>' % (sx(1.26), sy(0.67), 0.08 * PX, 0.09 * PX)
rover = '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="var(--rover)" stroke-width="1.5" stroke-dasharray="4 3"/>' % (sx(-0.25), sy(0.165), 0.5 * PX, 0.33 * PX)
goal = '<circle cx="%.1f" cy="%.1f" r="6" fill="none" stroke="var(--rover)" stroke-width="1.5"/>' % (sx(2.0), sy(0.0))
paths = ''.join('<polyline points="%s" fill="none" stroke="var(--%s)" stroke-width="2.2" opacity="0.9"/>' % (poly(nm), 's' if arm == 'S' else 'n') for nm, arm, _ in RUNS)
# 차체 오른쪽 변 궤적(횡 − 0.165)로 상자와의 실제 간격을 보이게
edges = ''.join('<polyline points="%s" fill="none" stroke="var(--%s)" stroke-width="1" stroke-dasharray="2 3" opacity="0.7"/>' % (' '.join('%.1f,%.1f' % (sx(x), sy(y - 0.165)) for x, y, _ in data[nm]), 's' if arm == 'S' else 'n') for nm, arm, _ in RUNS)
rows = ''.join('<tr><td>%s</td><td>%s</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.3f</td><td>%d</td></tr>' % (lab, 'STVL' if arm == 'S' else 'nvblox 2.0/0.99', T[nm], CLR[nm], RET[nm], data[nm + '_lat'], CPU[nm]) for nm, arm, lab in RUNS)
html = '''<title>N4 주행 궤적 A/B</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{color-scheme:light;--bg:#f6f5f1;--surface:#fcfcfb;--ink:#161613;--ink2:#52514e;--grid:#e3e1da;--rule:#d8d5cc;--s:#2a78d6;--n:#eb6834;--phys:#008300;--boxfill:#dfeedd;--furn:#d8d5cc;--rover:#0b0b0b}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--rule:#33322f;--s:#3987e5;--n:#d95926;--phys:#3ec13e;--boxfill:#1f3a1f;--furn:#33322f;--rover:#ffffff}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--rule:#33322f;--s:#3987e5;--n:#d95926;--phys:#3ec13e;--boxfill:#1f3a1f;--furn:#33322f;--rover:#ffffff}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR",system-ui,sans-serif;padding-block:28px;padding-inline:16px;max-width:1100px;margin:0 auto;line-height:1.5}
h1{font-size:1.4rem;margin:0 0 6px;text-wrap:balance}.lead{color:var(--ink2);margin:0 0 16px;max-width:75ch}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:.85rem;color:var(--ink2);margin:0 0 10px}.legend i{display:inline-block;width:22px;height:0;border-top:3px solid;vertical-align:3px;margin-right:6px}
.wrap{overflow-x:auto;border:1px solid var(--rule);background:var(--surface)}svg{display:block}.tick{font:11px "IBM Plex Mono",monospace;fill:var(--ink2)}
.tw{overflow-x:auto}table{border-collapse:collapse;font-size:.88rem;margin:14px 0 0;font-variant-numeric:tabular-nums}td,th{padding:5px 12px;border-bottom:1px solid var(--rule);text-align:right;white-space:nowrap}th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left}
.notes{margin:18px 0 0;padding:0 0 0 1.1em;color:var(--ink2);font-size:.9rem;max-width:80ch}.notes li{margin:4px 0}
</style>
<h1>N4 주행 A/B — STVL 층 vs nvblox 층, 같은 코스 5 회 (2026-09-22)</h1>
<p class="lead">출발 자세 기준 평면 궤적(러너 0.1 s 계측). 실선 = base_link 궤적, 점선 = 차체 오른쪽 변(횡 −0.165 m). 초록 상자 = 게이트가 잰 물리 상자(전면 1.153, 중심 −0.09), 회색 = 좌측 가구, 점선 사각형 = 출발 차체, 원 = 목표(2.0, 0).</p>
<div class="legend"><span><i style="border-color:var(--s)"></i>STVL (n4s1·n4s2)</span><span><i style="border-color:var(--n)"></i>nvblox 절단 2.0·감쇠 0.99 (n4n1~3)</span></div>
<div class="wrap"><svg viewBox="0 0 %(W).0f %(H).0f" width="%(W).0f" height="%(H).0f" role="img" aria-label="N4 궤적"><rect width="%(W).0f" height="%(H).0f" fill="var(--surface)"/>%(lines)s%(furn)s%(box)s%(rover)s%(goal)s%(edges)s%(paths)s</svg></div>
<div class="tw"><table><thead><tr><th>회차</th><th>층</th><th>소요 s</th><th>코스트맵 상자 최소 여유 cm</th><th>복귀 회전 자리 여유 cm</th><th>상자 옆 최대 횡변위 m</th><th>CPU 합 %%</th></tr></thead><tbody>%(rows)s</tbody></table></div>
<ul class="notes">
<li>다섯 회 모두 성공(중단·제어 미달 0). nvblox 층은 상자 옆 여유가 STVL 과 같거나 크고, 상자 뒤끝이 5 cm 뒤에 찍히는 만큼 복귀 회전이 조금 늦다. n4n3 은 원경로 자체가 넓었다.</li>
<li>CPU 는 nvblox 18~20 %%p 만큼 많다 — 전역 코스트맵이 아직 STVL(릴레이 포함)을 쓰기 때문이며, 전역까지 옮기면 릴레이·STVL 몫이 빠진다. GPU 3 %%, 전력 +0.2 W.</li>
<li>기준·원문: <code>Docs/debug_log/2026-09-22/SUMMARY.md §2~3.1</code>, 기준선 <code>Docs/debug_log/2026-09-21/BASELINE_STVL.md</code>.</li>
</ul>
'''
out = html % dict(W=W, H=H, lines=''.join(lines), furn=furn, box=box, rover=rover, goal=goal, edges=edges, paths=paths, rows=rows)
open(OUT, 'w', encoding='utf-8').write(out); print('html %d bytes → %s' % (len(out.encode('utf-8')), OUT))
