#!/usr/bin/env python3
"""STVL vs nvblox 로컬 코스트맵 시각화 HTML 생성 (2026-09-21 §10). 입력: grid_stvl_costmap.json, grid_nvblox_costmap.json, grid_nvblox_slice.json (base_link 좌표, 5 cm 셀)
  두 코스트맵은 각각 캡처 순간의 base_link 자세로 변환돼 격자가 수 mm 어긋나므로 공통 5 cm 격자(인덱스 = round(x/0.05))에 스냅해 비교한다.
  출력: costmap_ab.html (SVG 4 판: STVL / nvblox / 차이 / nvblox 슬라이스) + 요약 수치. 물리 상자 외곽·차체·카메라 화각선을 겹친다.
"""
import json, math, collections, os
R = 0.05
def snap(x): return int(math.floor(x / R))          # 셀 인덱스(셀 [i*R, (i+1)*R))
def load(f):
    d = json.load(open(f)); return {(snap(c[0]), snap(c[1])): c[2] for c in d['cells']}
S = load('grid_stvl_costmap.json'); N = load('grid_nvblox_costmap.json'); L = load('grid_nvblox_slice.json')
def cls(v): return 'L' if (v is not None and v >= 100) else ('I' if v == 99 else ('C' if (v is not None and v > 0) else 'F'))
keys = set(S) | set(N)
diff = {}
for k in keys:
    a, b = cls(S.get(k)), cls(N.get(k))
    diff[k] = 'B' if a == 'L' and b == 'L' else ('N' if b == 'L' else ('S' if a == 'L' else ('I' if 'I' in (a, b) else ('C' if 'C' in (a, b) else 'F'))))
cnt = collections.Counter(diff.values())
def region(k):
    x, y = (k[0] + 0.5) * R, (k[1] + 0.5) * R
    if 0.9 < x < 1.5 and -0.35 < y < 0.15: return '상자'
    if y < -0.5: return '우측 벽'
    if y > 0.45: return '좌측 가구'
    if x < 0.3: return '뒤·옆'
    return '기타'
reg = {c: collections.Counter(region(k) for k, v in diff.items() if v == c) for c in 'BNS'}
# 슬라이스 상자 셀
slice_box = sorted(k for k, v in L.items() if v is not None and v <= 0 and 0.9 < (k[0] + 0.5) * R < 1.5 and -0.35 < (k[1] + 0.5) * R < 0.15)
def ext(cells):
    if not cells: return '없음'
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    return 'x %.2f~%.2f, y %+.2f~%+.2f (%d 셀)' % (min(xs) * R, (max(xs) + 1) * R, min(ys) * R, (max(ys) + 1) * R, len(cells))
sbox = [k for k, v in S.items() if v >= 100 and region(k) == '상자']; nbox = [k for k, v in N.items() if v >= 100 and region(k) == '상자']
print('LETHAL 공통 %d / nvblox 만 %d / STVL 만 %d' % (cnt['B'], cnt['N'], cnt['S']))
print('nvblox 만:', dict(reg['N'])); print('STVL 만:', dict(reg['S'])); print('공통:', dict(reg['B']))
print('상자 LETHAL 외곽 — STVL:', ext(sbox), '| nvblox 층:', ext(nbox), '| nvblox 슬라이스(≤0):', ext(slice_box), '| 물리: x 1.153~1.263, y −0.169~+0.011')
# 슬라이스 거리 분포(상자 앞 x 0.9~1.15 자유 셀의 거리 최소)
front = [v for k, v in L.items() if v is not None and 0.95 < (k[0] + 0.5) * R < 1.15 and -0.2 < (k[1] + 0.5) * R < 0.0]
print('슬라이스: 상자 앞 0.95~1.15 m 셀 거리 %s' % (['%.2f' % v for v in sorted(front)[:6]]))

# ---- HTML ----
X0, X1, Y0, Y1 = -0.5, 2.0, -1.0, 1.0      # base_link 표시 범위(m)
PX = 22                                     # 셀당 px
W = int((X1 - X0) / R) * PX; H = int((Y1 - Y0) / R) * PX
def sx(x): return (x - X0) / R * PX
def sy(y): return (Y1 - y) / R * PX          # 위가 +y(왼쪽)
def rects(cellmap, colorfn):
    out = []
    for (i, j), v in cellmap.items():
        x, y = i * R, j * R
        if not (X0 <= x < X1 and Y0 <= y < Y1): continue
        c = colorfn(v)
        if c: out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s"/>' % (sx(x), sy(y + R), PX, PX, c))
    return ''.join(out)
cm_color = {'L': 'var(--lethal)', 'I': 'var(--inscribed)', 'C': 'var(--cost)', 'F': None}
diff_color = {'B': 'var(--both)', 'N': 'var(--nvonly)', 'S': 'var(--stonly)', 'I': 'var(--inscribed)', 'C': 'var(--cost)', 'F': None}
def overlay():
    # 물리 상자, 차체(0.50×0.33), 카메라 화각(87°) 선, 축
    o = []
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="var(--phys)" stroke-width="2" stroke-dasharray="4 3"/>' % (sx(1.153), sy(0.011), 0.11 / R * PX, 0.18 / R * PX))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="var(--rover)" stroke-width="2"/>' % (sx(-0.25), sy(0.165), 0.5 / R * PX, 0.33 / R * PX))
    o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="var(--rover)" opacity="0.9"/>' % (sx(0.25), sy(0.0), sx(0.17), sy(0.05), sx(0.17), sy(-0.05)))
    for ang in (math.radians(43.5), -math.radians(43.5)):
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--fov)" stroke-width="1.5" stroke-dasharray="2 4"/>' % (sx(0.234), sy(0.044), sx(0.234 + 1.8 * math.cos(ang)), sy(0.044 + 1.8 * math.sin(ang))))
    for xv in (0, 0.5, 1.0, 1.5, 2.0):
        o.append('<line x1="%.1f" y1="0" x2="%.1f" y2="%d" stroke="var(--grid)" stroke-width="1"/><text x="%.1f" y="%d" class="tick">%.1f</text>' % (sx(xv), sx(xv), H, sx(xv) + 3, H - 4, xv))
    for yv in (-1.0, -0.5, 0, 0.5, 1.0):
        o.append('<line x1="0" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--grid)" stroke-width="1"/><text x="3" y="%.1f" class="tick">%+.1f</text>' % (sy(yv), W, sy(yv), sy(yv) - 3, yv))
    return ''.join(o)
def panel(title, sub, body):
    return ('<figure><figcaption><b>%s</b><span>%s</span></figcaption><div class="wrap"><svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">'
            '<rect width="%d" height="%d" fill="var(--surface)"/>%s%s</svg></div></figure>') % (title, sub, W, H, W, H, title, W, H, body, overlay())
slice_color = lambda v: 'var(--unknown)' if v is None else ('var(--lethal)' if v <= 0 else ('var(--near)' if v < 0.175 else ('var(--cost)' if v < 0.40 else None)))
html = '''<title>STVL vs nvblox 코스트맵</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{color-scheme:light;--bg:#f6f5f1;--surface:#fcfcfb;--ink:#161613;--ink2:#52514e;--grid:#e3e1da;--lethal:#3a3937;--inscribed:#c9c6bd;--cost:#ebe9e2;--unknown:#f1efe9;--near:#d6d2c6;
--both:#4a3aa7;--nvonly:#eb6834;--stonly:#2a78d6;--phys:#008300;--rover:#0b0b0b;--fov:#eda100;--rule:#d8d5cc}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--lethal:#e8e6df;--inscribed:#4a4945;--cost:#2f2e2b;--unknown:#222220;--near:#3c3b37;
--both:#9085e9;--nvonly:#d95926;--stonly:#3987e5;--phys:#3ec13e;--rover:#ffffff;--fov:#c98500;--rule:#33322f}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--lethal:#e8e6df;--inscribed:#4a4945;--cost:#2f2e2b;--unknown:#222220;--near:#3c3b37;
--both:#9085e9;--nvonly:#d95926;--stonly:#3987e5;--phys:#3ec13e;--rover:#ffffff;--fov:#c98500;--rule:#33322f}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR",system-ui,sans-serif;padding-block:28px;padding-inline:16px;max-width:1180px;margin:0 auto;line-height:1.5}
h1{font-size:1.45rem;margin:0 0 4px;text-wrap:balance}
.lead{color:var(--ink2);margin:0 0 20px;max-width:70ch}
.kpis{display:flex;flex-wrap:wrap;gap:10px 28px;margin:0 0 22px;padding:12px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.kpi b{display:block;font-family:"IBM Plex Mono",monospace;font-size:1.35rem;font-variant-numeric:tabular-nums}
.kpi span{color:var(--ink2);font-size:.85rem}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:.85rem;color:var(--ink2);margin:0 0 14px}
.legend i{display:inline-block;width:14px;height:14px;vertical-align:-2px;margin-right:6px;border-radius:2px}
.legend i.line{height:0;border-top:2px dashed var(--phys);width:18px;vertical-align:2px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}
figure{margin:0}figcaption{display:flex;justify-content:space-between;gap:8px;align-items:baseline;margin:0 0 6px;font-size:.92rem}
figcaption span{color:var(--ink2);font-size:.8rem;font-family:"IBM Plex Mono",monospace}
.wrap{overflow-x:auto;border:1px solid var(--rule);background:var(--surface)}
svg{display:block}.tick{font:10px "IBM Plex Mono",monospace;fill:var(--ink2)}
.notes{margin:24px 0 0;padding:0 0 0 1.1em;color:var(--ink2);font-size:.9rem;max-width:80ch}.notes li{margin:4px 0}
table{border-collapse:collapse;font-size:.88rem;margin:14px 0 0;font-variant-numeric:tabular-nums}td,th{padding:5px 12px;border-bottom:1px solid var(--rule);text-align:right}th:first-child,td:first-child{text-align:left}
</style>
<h1>로컬 코스트맵 정지 비교 — STVL 층 vs nvblox 층 (2026-09-21)</h1>
<p class="lead">같은 배치(로버: 출발 테이프, 상자: 앞단 +0.90 m·우측 0.08 m)에서 로컬 코스트맵(3×3 m, 5 cm)의 카메라 층만 바꿔 캡처했다. 좌표는 base_link, +x 앞, +y 왼쪽(위). 초록 점선 = 카메라 점군으로 잰 물리 상자(전면 x 1.153, 중심 y −0.079), 검은 사각형 = 차체 0.50×0.33, 노란 점선 = 카메라 수평 화각 87°.</p>
<div class="kpis">
 <div class="kpi"><b>%(B)d</b><span>둘 다 LETHAL</span></div>
 <div class="kpi"><b style="color:var(--nvonly)">%(N)d</b><span>nvblox 층에만 LETHAL</span></div>
 <div class="kpi"><b style="color:var(--stonly)">%(S)d</b><span>STVL 층에만 LETHAL</span></div>
 <div class="kpi"><b>%(sb)s</b><span>상자 LETHAL 셀 STVL / nvblox 층 / nvblox 슬라이스</span></div>
</div>
<div class="legend"><span><i style="background:var(--lethal)"></i>LETHAL(100)</span><span><i style="background:var(--inscribed)"></i>내접 99</span><span><i style="background:var(--cost)"></i>비용 1~98</span><span><i style="background:var(--both)"></i>둘 다</span><span><i style="background:var(--nvonly)"></i>nvblox 만</span><span><i style="background:var(--stonly)"></i>STVL 만</span><span><i style="background:var(--unknown)"></i>슬라이스 미지</span><span><i class="line"></i>물리 상자</span></div>
<div class="grid2">
%(p1)s
%(p2)s
%(p3)s
%(p4)s
</div>
<table><thead><tr><th>구역</th><th>둘 다</th><th>nvblox 만</th><th>STVL 만</th></tr></thead><tbody>%(rows)s</tbody></table>
<ul class="notes">
<li>nvblox 층(이진: ESDF ≤ 0 → LETHAL)은 표면 <b>뒤쪽</b>으로 TSDF 절단 거리(4 복셀 = 0.20 m)만큼 음수 거리가 이어져 치명 셀이 두껍다 — 상자가 %(nbox_depth)s 깊이로 찍힌 이유이고, 우측 벽·좌측 가구의 "nvblox 만" 셀 대부분이 표면 뒤 띠다. 표면 앞(자유 공간)으로 나온 것은 아니므로 통과 폭 자체는 STVL 과 같게 측정됐다(감사 기준1 0.40 m).</li>
<li>STVL 층은 릴레이(0.45 m 컷·복셀 3점·5중3 지속)와 감쇠 뒤에 남은 점만 셀로 올려 얇고 성기다. 두 층이 겹치는 셀(둘 다)이 적은 것은 이 두께 차이 + 캡처 사이 몇 mm 자세 차이의 5 cm 격자 스냅 때문이다.</li>
<li>nvblox 슬라이스(우하)는 층이 읽는 원자료: 미지(관측 없음) 영역이 로버 뒤·근거리에 넓다 — 카메라 시야 밖은 nvblox 가 모르며, 코스트맵에서는 FREE 로 취급된다(track_unknown_space false). 라이다 층이 그 자리를 보완한다.</li>
<li>상자의 nvblox 셀이 물리보다 뒤(+x)와 우측(−y)으로 늘어난 것(슬라이스 y %(sly)s vs 물리 −0.17~+0.01)도 같은 기전이다: 카메라(y +0.04)는 상자의 <b>앞면과 왼쪽 면</b>만 보므로, 그 두 면의 뒤쪽 — 앞면 뒤(+x)와 왼쪽 면 뒤(−y) — 로 절단 띠가 이어진다. 보이는 면(앞·왼쪽 가장자리)은 물리와 한 셀 안에서 맞는다. 즉 보정 오차가 아니라 이진 변환이 TSDF 띠를 통째로 치명으로 올리는 규칙의 결과다.</li>
<li>다음 후보: 절단 거리(`projective_integrator_truncation_distance_vox` 4 → 2)로 띠를 0.10 m 로 줄이거나, A/B-2(ESDF 거리 → 비용 기울기)에서 `inflation_distance` 로 다루기. 어느 쪽이든 통과 폭·CostCritic 여유 지표로 다시 잰다.</li>
</ul>
'''
rows = ''.join('<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (r, reg['B'][r], reg['N'][r], reg['S'][r]) for r in ('상자', '좌측 가구', '우측 벽', '뒤·옆', '기타'))
p1 = panel('A. STVL 층 (기준선 구성)', 'LETHAL %d' % sum(1 for v in S.values() if v >= 100), rects(S, lambda v: cm_color[cls(v)]))
p2 = panel('B. nvblox 층 (이진 A/B-1)', 'LETHAL %d' % sum(1 for v in N.values() if v >= 100), rects(N, lambda v: cm_color[cls(v)]))
p3 = panel('C. 차이 (LETHAL 기준)', '둘 다 %d · nvblox 만 %d · STVL 만 %d' % (cnt['B'], cnt['N'], cnt['S']), rects(diff, lambda v: diff_color[v]))
p4 = panel('D. nvblox ESDF 슬라이스 원자료', '≤0 %d · 미지 %d' % (sum(1 for v in L.values() if v is not None and v <= 0), sum(1 for v in L.values() if v is None)), rects(L, slice_color))
sly = ('%+.2f~%+.2f' % (min(c[1] for c in slice_box) * R, (max(c[1] for c in slice_box) + 1) * R)) if slice_box else '없음'
nbd = ('%.2f m' % ((max(c[0] for c in nbox) - min(c[0] for c in nbox) + 1) * R)) if nbox else '?'
out = html % dict(B=cnt['B'], N=cnt['N'], S=cnt['S'], sb='%d / %d / %d' % (len(sbox), len(nbox), len(slice_box)), p1=p1, p2=p2, p3=p3, p4=p4, rows=rows, nbox_depth=nbd, sly=sly)
open('costmap_ab.html', 'w', encoding='utf-8').write(out); print('html %d bytes' % len(out.encode('utf-8')))
