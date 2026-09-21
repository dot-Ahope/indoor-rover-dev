#!/usr/bin/env python3
"""STVL vs nvblox 로컬 코스트맵 시각화 v2 (2026-09-21 §10.5) — 층 결함(round→floor) 수정 후 재캡처용. job491 을 인자화하고 "층 vs 슬라이스" 판(E)과 V1~V4 판정, v1(수정 전) 대비 표를 더했다.
  사용: python job494_vizgen2.py <stvl.json> <nvblox.json> <slice.json> <out.html> [감사 최소폭 문자열]
  입력 JSON 은 job489 덤프(base_link 좌표, 5 cm 셀). 공통 5 cm 격자(floor(x/0.05))에 스냅해 비교.
"""
import json, math, collections, sys
R = 0.05
A = sys.argv[1:]
F_S, F_N, F_L, OUT = A[0], A[1], A[2], A[3]
V4_TXT = A[4] if len(A) > 4 else '(감사 미회수)'
def snap(x): return int(math.floor(x / R))          # 셀 인덱스(셀 [i*R, (i+1)*R))
def load(f):
    d = json.load(open(f, encoding='utf-8')); return {(snap(c[0]), snap(c[1])): c[2] for c in d['cells']}
S = load(F_S); N = load(F_N); L = load(F_L)
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
# 층(N) vs 슬라이스(L): 층 LETHAL ↔ 슬라이스 ≤0
lethalN = {k for k, v in N.items() if v >= 100}; lethalL = {k for k, v in L.items() if v is not None and v <= 0}
LS = {}
for k in lethalN | lethalL:
    LS[k] = 'B' if (k in lethalN and k in lethalL) else ('Y' if k in lethalN else 'Z')
lcnt = collections.Counter(LS.values())
# V2 정정(재캡처 뒤): 전체 창 비교는 (a) 코스트맵에 라이다 층 셀이 섞이고 (b) 슬라이스가 3×3 m 창 밖까지 이어져 평가 불가 →
#   공통 영역 = 슬라이스 기지(known) ∩ base_link 반경 1.45 m(코스트맵 창 내접원) 로 한정하고, 층만 중 STVL 모드 캡처에서도 LETHAL 인 셀(공유하는 라이다 층)은 제외한다.
lethalS = {k for k, v in S.items() if v >= 100}
inside = lambda k: math.hypot((k[0] + 0.5) * R, (k[1] + 0.5) * R) < 1.45
dom = {k for k, v in L.items() if v is not None and inside(k)}
c_both = lethalN & lethalL & dom; c_layer = (lethalN - lethalL) & dom; c_layer_pure = c_layer - lethalS; c_slice = (lethalL - lethalN) & dom
inbox = lambda k: 0.9 < (k[0] + 0.5) * R < 1.5 and -0.35 < (k[1] + 0.5) * R < 0.15
slice_box = sorted(k for k in lethalL if inbox(k))
def ext(cells):
    if not cells: return '없음'
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    return 'x %.2f~%.2f, y %+.2f~%+.2f (%d 셀)' % (min(xs) * R, (max(xs) + 1) * R, min(ys) * R, (max(ys) + 1) * R, len(cells))
def rng(cells):
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    return (min(xs), max(xs), min(ys), max(ys)) if cells else None
sbox = [k for k, v in S.items() if v >= 100 and region(k) == '상자']; nbox = [k for k, v in N.items() if v >= 100 and region(k) == '상자']
# ---- 판정 V1~V3 ----
v1_ok = rng(nbox) == rng(slice_box)
v2_ok = len(c_layer_pure) <= 5 and len(c_slice) <= 5
left_edge = ((max(c[1] for c in nbox) + 1) * R) if nbox else None
v3_ok = left_edge is not None and abs(left_edge - 0.011) <= 0.025 + 1e-9
print('LETHAL 공통 %d / nvblox 만 %d / STVL 만 %d' % (cnt['B'], cnt['N'], cnt['S']))
print('nvblox 만:', dict(reg['N'])); print('STVL 만:', dict(reg['S'])); print('공통:', dict(reg['B']))
print('층 vs 슬라이스: 둘 다 %d / 층만 %d / 슬라이스만 %d' % (lcnt['B'], lcnt['Y'], lcnt['Z']))
print('상자 LETHAL 외곽 — STVL:', ext(sbox), '| nvblox 층:', ext(nbox), '| nvblox 슬라이스(≤0):', ext(slice_box), '| 물리: x 1.153~1.263, y −0.169~+0.011')
print('공통 영역(슬라이스 기지 ∩ 반경 1.45 m) %d 셀: 둘 다 %d / 층만 %d(라이다 귀속 %d, 순수 %d) / 슬라이스만 %d' % (len(dom), len(c_both), len(c_layer), len(c_layer & lethalS), len(c_layer_pure), len(c_slice)))
print('V1 층=슬라이스 외곽: %s | V2(정정) 공통 영역 순수 층만·슬라이스만 ≤5: %s (%d, %d) | V3 통과측 가장자리 %s (물리 +0.011): %s | V4 %s' % (v1_ok, v2_ok, len(c_layer_pure), len(c_slice), ('%+.2f' % left_edge) if left_edge is not None else '?', v3_ok, V4_TXT))

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
ls_color = {'B': 'var(--both)', 'Y': 'var(--nvonly)', 'Z': 'var(--stonly)'}
def overlay():
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
def mark(ok): return '<b class="%s">%s</b>' % ('ok' if ok else 'ng', '통과' if ok else '불합격')
html = '''<title>STVL vs nvblox 코스트맵</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{color-scheme:light;--bg:#f6f5f1;--surface:#fcfcfb;--ink:#161613;--ink2:#52514e;--grid:#e3e1da;--lethal:#3a3937;--inscribed:#c9c6bd;--cost:#ebe9e2;--unknown:#f1efe9;--near:#d6d2c6;
--both:#4a3aa7;--nvonly:#eb6834;--stonly:#2a78d6;--phys:#008300;--rover:#0b0b0b;--fov:#eda100;--rule:#d8d5cc;--ok:#1d7a3a;--ng:#b3261e}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--lethal:#e8e6df;--inscribed:#4a4945;--cost:#2f2e2b;--unknown:#222220;--near:#3c3b37;
--both:#9085e9;--nvonly:#d95926;--stonly:#3987e5;--phys:#3ec13e;--rover:#ffffff;--fov:#c98500;--rule:#33322f;--ok:#57c46f;--ng:#f0705f}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--lethal:#e8e6df;--inscribed:#4a4945;--cost:#2f2e2b;--unknown:#222220;--near:#3c3b37;
--both:#9085e9;--nvonly:#d95926;--stonly:#3987e5;--phys:#3ec13e;--rover:#ffffff;--fov:#c98500;--rule:#33322f;--ok:#57c46f;--ng:#f0705f}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR",system-ui,sans-serif;padding-block:28px;padding-inline:16px;max-width:1180px;margin:0 auto;line-height:1.5}
h1{font-size:1.45rem;margin:0 0 4px;text-wrap:balance}
h2{font-size:1.05rem;margin:26px 0 8px}
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
.tw{overflow-x:auto}table{border-collapse:collapse;font-size:.88rem;margin:8px 0 0;font-variant-numeric:tabular-nums}td,th{padding:5px 12px;border-bottom:1px solid var(--rule);text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}
b.ok{color:var(--ok)}b.ng{color:var(--ng)}code{font-family:"IBM Plex Mono",monospace;font-size:.85em}
</style>
<h1>로컬 코스트맵 정지 비교 — STVL 층 vs nvblox 층 (2026-09-21, v2 결함 수정 후)</h1>
<p class="lead">같은 배치(로버: 출발 테이프, 상자: 앞단 +0.90 m·우측 0.08 m)에서 로컬 코스트맵(3×3 m, 5 cm)의 카메라 층만 바꿔 캡처했다. v2 는 <code>nvblox_nav2</code> 층의 슬라이스 조회 결함(<code>round</code> → <code>floor</code>)을 고친 뒤 재캡처한 것. 좌표는 base_link, +x 앞, +y 왼쪽(위). 초록 점선 = 카메라 점군으로 잰 물리 상자(전면 x 1.153, 중심 y −0.079), 검은 사각형 = 차체 0.50×0.33, 노란 점선 = 카메라 수평 화각 87°.</p>
<div class="kpis">
 <div class="kpi"><b>%(B)d</b><span>둘 다 LETHAL</span></div>
 <div class="kpi"><b style="color:var(--nvonly)">%(N)d</b><span>nvblox 층에만 LETHAL</span></div>
 <div class="kpi"><b style="color:var(--stonly)">%(S)d</b><span>STVL 층에만 LETHAL</span></div>
 <div class="kpi"><b>%(sb)s</b><span>상자 LETHAL 셀 STVL / nvblox 층 / nvblox 슬라이스</span></div>
 <div class="kpi"><b>%(lsb)s</b><span>층 vs 슬라이스(공통 영역): 둘 다 / 층만(라이다 제외) / 슬라이스만</span></div>
</div>
<div class="legend"><span><i style="background:var(--lethal)"></i>LETHAL(100)</span><span><i style="background:var(--inscribed)"></i>내접 99</span><span><i style="background:var(--cost)"></i>비용 1~98</span><span><i style="background:var(--both)"></i>둘 다</span><span><i style="background:var(--nvonly)"></i>nvblox(층) 만</span><span><i style="background:var(--stonly)"></i>STVL(슬라이스) 만</span><span><i style="background:var(--unknown)"></i>슬라이스 미지</span><span><i class="line"></i>물리 상자</span></div>
<div class="grid2">
%(p1)s
%(p2)s
%(p3)s
%(p4)s
%(p5)s
</div>
<h2>판정 (캡처 전에 선언한 기준)</h2>
<div class="tw"><table><thead><tr><th>기준</th><th>내용</th><th>측정</th><th>결과</th></tr></thead><tbody>
<tr><td>V1</td><td>층의 상자 LETHAL 외곽 = 슬라이스 ≤0 외곽</td><td>층 %(nboxext)s / 슬라이스 %(lboxext)s</td><td>%(v1)s</td></tr>
<tr><td>V2 (정정)</td><td>공통 영역(슬라이스 기지 ∩ 반경 1.45 m) 안에서 층만(라이다 층 제외)·슬라이스만 각 ≤ 5 셀</td><td>%(dom)d 셀 중 둘 다 %(cb)d · 층만 %(ly)d(라이다 귀속 %(ll)d) · 슬라이스만 %(lz)d</td><td>%(v2)s</td></tr>
<tr><td>V3</td><td>상자 통과 측(왼쪽) 가장자리 = 물리 +0.011 ± 2.5 cm</td><td>%(ledge)s</td><td>%(v3)s</td></tr>
<tr><td>V4</td><td>감사 기준1 최소폭 0.40 m 유지</td><td>%(v4txt)s</td><td>—</td></tr>
</tbody></table></div>
<h2>v1(수정 전, 같은 배치·다른 캡처) 대비</h2>
<div class="tw"><table><thead><tr><th></th><th>v1 수정 전</th><th>v2 수정 후</th></tr></thead><tbody>
<tr><td>둘 다 / nvblox 만 / STVL 만</td><td>189 / 89 / 12</td><td>%(B)d / %(N)d / %(S)d</td></tr>
<tr><td>상자 — STVL 층</td><td>x 1.10~1.25, y −0.20~0.00</td><td>%(sboxext)s</td></tr>
<tr><td>상자 — nvblox 층</td><td>x 1.10~1.35, y −0.30~−0.05 (슬라이스보다 −1 셀)</td><td>%(nboxext)s</td></tr>
<tr><td>상자 — nvblox 슬라이스</td><td>x 1.15~1.40, y −0.25~0.00</td><td>%(lboxext)s</td></tr>
<tr><td>구역별 nvblox 만 (상자/좌측 가구/우측 벽)</td><td>12 / 26 / 51</td><td>%(rn)s</td></tr>
</tbody></table></div>
<ul class="notes">
<li><b>수정한 결함</b>: <code>lookupInSlice()</code> 가 슬라이스 인덱스를 <code>round((pos − origin)/res)</code> 로 구했다. 슬라이스 메시지의 origin 은 첫 픽셀의 모서리(<code>origin = aabb.min()</code>)이므로 올바른 인덱스는 <code>floor</code> 이고, <code>round</code> 는 소수부 ≥ 0.5 일 때 옆 픽셀을 읽어 층 그림 전체가 한 셀(5 cm) 평행이동했다. v1 에서 상자의 통과 측 가장자리가 물리보다 6 cm 안쪽에 찍힌 원인이다.</li>
<li>수정 뒤에도 남는 차이는 <b>표면 뒤 두께</b>뿐이다. nvblox 층은 <code>distance ≤ 0 → LETHAL</code> 이 이진/기울기 모드와 무관하게 적용되고, TSDF 절단 거리(4 복셀 = 0.20 m)만큼 표면 뒤로 음수가 이어지므로 관측된 모든 표면이 4 셀 두께의 판이 된다. STVL 은 점이 떨어진 복셀만 올려 1 셀 껍질이다. 띠는 광선이 표면에 닿은 뒤 이어지는 구간이라 언제나 카메라가 못 보는 쪽에 놓이고, 자유 공간 쪽으로는 나오지 않는다.</li>
<li>슬라이스(D)의 미지 영역(로버 뒤·근거리)은 코스트맵에서 FREE 로 취급되고(track_unknown_space false) 라이다 층이 보완한다.</li>
<li><b>V2 정정</b>: 처음 선언한 "전체 창에서 층만·슬라이스만 각 ≤ 5" 는 평가할 수 없었다 — 코스트맵에는 라이다 층 셀이 섞이고(판 E 의 "층만" 대부분), 슬라이스는 3×3 m 창 밖까지 이어진다(판 E 의 "슬라이스만"). 그래서 공통 영역(슬라이스 기지 ∩ 반경 1.45 m)으로 한정하고 STVL 모드 캡처에서도 LETHAL 인 셀(공유 라이다 층)을 제외해 다시 셌다. 판 E 는 정정 전 전체 창 그림 그대로다.</li>
<li>다음: 절단 거리 <code>projective_integrator_truncation_distance_vox</code> 4 → 2 로 띠를 0.10 m 로 줄이는 정지 A/B(앞면 위치·근거리 자취를 다시 잼) → N4 주행 A/B(<code>BAG_PROFILE=nvblox</code>)를 기준선 지표로 판정. 기울기 모드(A/B-2)는 표면 앞쪽 비용만 바꾸므로 띠의 해법이 아니다.</li>
</ul>
'''
rows_n = '%d / %d / %d' % (reg['N']['상자'], reg['N']['좌측 가구'], reg['N']['우측 벽'])
p1 = panel('A. STVL 층 (기준선 구성)', 'LETHAL %d' % sum(1 for v in S.values() if v >= 100), rects(S, lambda v: cm_color[cls(v)]))
p2 = panel('B. nvblox 층 (이진, floor 수정)', 'LETHAL %d' % len(lethalN), rects(N, lambda v: cm_color[cls(v)]))
p3 = panel('C. 차이 STVL vs nvblox 층', '둘 다 %d · nvblox 만 %d · STVL 만 %d' % (cnt['B'], cnt['N'], cnt['S']), rects(diff, lambda v: diff_color[v]))
p4 = panel('D. nvblox ESDF 슬라이스 원자료', '≤0 %d · 미지 %d' % (len(lethalL), sum(1 for v in L.values() if v is None)), rects(L, slice_color))
p5 = panel('E. 층 vs 슬라이스 (정렬 검증)', '둘 다 %d · 층만 %d · 슬라이스만 %d' % (lcnt['B'], lcnt['Y'], lcnt['Z']), rects(LS, lambda v: ls_color[v]))
out = html % dict(B=cnt['B'], N=cnt['N'], S=cnt['S'], sb='%d / %d / %d' % (len(sbox), len(nbox), len(slice_box)), lsb='%d / %d / %d' % (len(c_both), len(c_layer_pure), len(c_slice)),
                  p1=p1, p2=p2, p3=p3, p4=p4, p5=p5, nboxext=ext(nbox), lboxext=ext(slice_box), sboxext=ext(sbox), v1=mark(v1_ok), v2=mark(v2_ok), v3=mark(v3_ok),
                  ly=len(c_layer), lz=len(c_slice), ll=len(c_layer & lethalS), cb=len(c_both), dom=len(dom), ledge=('%+.2f m' % left_edge) if left_edge is not None else '?', v4txt=V4_TXT, rn=rows_n)
open(OUT, 'w', encoding='utf-8').write(out); print('html %d bytes → %s' % (len(out.encode('utf-8')), OUT))
