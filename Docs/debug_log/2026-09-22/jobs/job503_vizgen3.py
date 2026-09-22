#!/usr/bin/env python3
"""09-22 §1 절단 거리 A/B 시각화: STVL(stvl3) / nvblox 절단 4.0(t4) / 절단 2.0(t2) 로컬 코스트맵을 같은 배치에서 셀 단위로 비교하는 HTML.
  사용: python job503_vizgen3.py <dir> <out.html> [BX] [BY] [T4 감사 최소폭] [T2 감사 최소폭] [T5 요약]
  입력: dir/grid_stvl3_costmap.json, grid_t4_{costmap,slice}.json, grid_t2_{costmap,slice}.json (job489 덤프, base_link 좌표, 5 cm)
"""
import json, math, collections, sys, os
R = 0.05
A = sys.argv[1:]
D, OUT = A[0], A[1]
BX = float(A[2]) if len(A) > 2 else 1.153; BY = float(A[3]) if len(A) > 3 else -0.079
W4 = A[4] if len(A) > 4 else '(미회수)'; W2 = A[5] if len(A) > 5 else '(미회수)'; T5 = A[6] if len(A) > 6 else '(job474·tegrastats 출력 참조)'
BOX_D, BOX_W = 0.11, 0.18   # 물리 상자 깊이·폭(카메라 점군 기준, 09-21)
def snap(x): return int(math.floor(x / R))
def load(f): return {(snap(c[0]), snap(c[1])): c[2] for c in json.load(open(os.path.join(D, f), encoding='utf-8'))['cells']}
def cls(v): return 'L' if (v is not None and v >= 100) else ('I' if v == 99 else ('C' if (v is not None and v > 0) else 'F'))
def region(k):
    x, y = (k[0] + 0.5) * R, (k[1] + 0.5) * R
    if 0.9 < x < 1.5 and -0.35 < y < 0.15: return '상자'
    if y < -0.5: return '우측 벽'
    if y > 0.45: return '좌측 가구'
    if x < 0.3: return '뒤·옆'
    return '기타'
def ext(cells):
    if not cells: return '없음'
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    return 'x %.2f~%.2f, y %+.2f~%+.2f (%d)' % (min(xs) * R, (max(xs) + 1) * R, min(ys) * R, (max(ys) + 1) * R, len(cells))
S = load('grid_stvl3_costmap.json'); lethS = {k for k, v in S.items() if v >= 100}
V = {}
for nm in ('t4', 't2'):
    N = load('grid_%s_costmap.json' % nm); L = load('grid_%s_slice.json' % nm)
    lethN = {k for k, v in N.items() if v >= 100}; lethL = {k for k, v in L.items() if v is not None and v <= 0}
    diff = {}
    for k in set(S) | set(N):
        a, b = cls(S.get(k)), cls(N.get(k))
        diff[k] = 'B' if a == 'L' and b == 'L' else ('N' if b == 'L' else ('S' if a == 'L' else ('I' if 'I' in (a, b) else ('C' if 'C' in (a, b) else 'F'))))
    cnt = collections.Counter(diff.values()); regN = collections.Counter(region(k) for k, v in diff.items() if v == 'N')
    boxL = [k for k in lethL if region(k) == '상자']; boxN = [k for k in lethN if region(k) == '상자']
    xs = [k[0] for k in boxL]
    V[nm] = dict(N=N, L=L, lethN=lethN, lethL=lethL, diff=diff, cnt=cnt, regN=regN, boxL=boxL, boxN=boxN,
                 front=(min(xs) * R if xs else None), depth=((max(xs) - min(xs) + 1) * R if xs else None),
                 cols={r: len({k[0] for k in lethL if region(k) == r}) for r in ('우측 벽', '좌측 가구')})
t4, t2 = V['t4'], V['t2']
sbox = [k for k in lethS if region(k) == '상자']
# ---- SVG ----
X0, X1, Y0, Y1 = -0.5, 2.0, -1.0, 1.0; PX = 22
Wd = int((X1 - X0) / R) * PX; Hd = int((Y1 - Y0) / R) * PX
def sx(x): return (x - X0) / R * PX
def sy(y): return (Y1 - y) / R * PX
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
slice_color = lambda v: 'var(--unknown)' if v is None else ('var(--lethal)' if v <= 0 else ('var(--near)' if v < 0.175 else ('var(--cost)' if v < 0.40 else None)))
def overlay():
    o = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="var(--phys)" stroke-width="2" stroke-dasharray="4 3"/>' % (sx(BX), sy(BY + BOX_W / 2), BOX_D / R * PX, BOX_W / R * PX),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="var(--rover)" stroke-width="2"/>' % (sx(-0.25), sy(0.165), 0.5 / R * PX, 0.33 / R * PX),
         '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="var(--rover)" opacity="0.9"/>' % (sx(0.25), sy(0.0), sx(0.17), sy(0.05), sx(0.17), sy(-0.05))]
    for ang in (math.radians(43.5), -math.radians(43.5)):
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--fov)" stroke-width="1.5" stroke-dasharray="2 4"/>' % (sx(0.234), sy(0.044), sx(0.234 + 1.8 * math.cos(ang)), sy(0.044 + 1.8 * math.sin(ang))))
    for xv in (0, 0.5, 1.0, 1.5, 2.0):
        o.append('<line x1="%.1f" y1="0" x2="%.1f" y2="%d" stroke="var(--grid)" stroke-width="1"/><text x="%.1f" y="%d" class="tick">%.1f</text>' % (sx(xv), sx(xv), Hd, sx(xv) + 3, Hd - 4, xv))
    for yv in (-1.0, -0.5, 0, 0.5, 1.0):
        o.append('<line x1="0" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--grid)" stroke-width="1"/><text x="3" y="%.1f" class="tick">%+.1f</text>' % (sy(yv), Wd, sy(yv), sy(yv) - 3, yv))
    return ''.join(o)
def panel(title, sub, body):
    return ('<figure><figcaption><b>%s</b><span>%s</span></figcaption><div class="wrap"><svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">'
            '<rect width="%d" height="%d" fill="var(--surface)"/>%s%s</svg></div></figure>') % (title, sub, Wd, Hd, Wd, Hd, title, Wd, Hd, body, overlay())
def mark(ok): return '<b class="%s">%s</b>' % ('ok' if ok else 'ng', '통과' if ok else '불합격')
T1 = t4['front'] == t2['front'] and t2['front'] is not None and abs(t2['front'] - math.floor(BX / R) * R) < 1e-9
T2 = t2['depth'] is not None and t2['depth'] <= 0.15 + 1e-9
T3 = t2['cnt']['N'] <= 0.6 * t4['cnt']['N'] and t2['cnt']['S'] <= 10
T6 = all(t2['cols'][r] >= 0.9 * t4['cols'][r] for r in ('우측 벽', '좌측 가구'))
html = '''<title>절단 거리 A/B 코스트맵</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{color-scheme:light;--bg:#f6f5f1;--surface:#fcfcfb;--ink:#161613;--ink2:#52514e;--grid:#e3e1da;--lethal:#3a3937;--inscribed:#c9c6bd;--cost:#ebe9e2;--unknown:#f1efe9;--near:#d6d2c6;
--both:#4a3aa7;--nvonly:#eb6834;--stonly:#2a78d6;--phys:#008300;--rover:#0b0b0b;--fov:#eda100;--rule:#d8d5cc;--ok:#1d7a3a;--ng:#b3261e}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--lethal:#e8e6df;--inscribed:#4a4945;--cost:#2f2e2b;--unknown:#222220;--near:#3c3b37;
--both:#9085e9;--nvonly:#d95926;--stonly:#3987e5;--phys:#3ec13e;--rover:#ffffff;--fov:#c98500;--rule:#33322f;--ok:#57c46f;--ng:#f0705f}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#151514;--surface:#1a1a19;--ink:#f2f1ec;--ink2:#c3c2b7;--grid:#2b2b29;--lethal:#e8e6df;--inscribed:#4a4945;--cost:#2f2e2b;--unknown:#222220;--near:#3c3b37;
--both:#9085e9;--nvonly:#d95926;--stonly:#3987e5;--phys:#3ec13e;--rover:#ffffff;--fov:#c98500;--rule:#33322f;--ok:#57c46f;--ng:#f0705f}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR",system-ui,sans-serif;padding-block:28px;padding-inline:16px;max-width:1180px;margin:0 auto;line-height:1.5}
h1{font-size:1.45rem;margin:0 0 4px;text-wrap:balance}h2{font-size:1.05rem;margin:26px 0 8px}
.lead{color:var(--ink2);margin:0 0 20px;max-width:70ch}
.kpis{display:flex;flex-wrap:wrap;gap:10px 28px;margin:0 0 22px;padding:12px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
.kpi b{display:block;font-family:"IBM Plex Mono",monospace;font-size:1.35rem;font-variant-numeric:tabular-nums}.kpi span{color:var(--ink2);font-size:.85rem}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:.85rem;color:var(--ink2);margin:0 0 14px}
.legend i{display:inline-block;width:14px;height:14px;vertical-align:-2px;margin-right:6px;border-radius:2px}.legend i.line{height:0;border-top:2px dashed var(--phys);width:18px;vertical-align:2px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}
figure{margin:0}figcaption{display:flex;justify-content:space-between;gap:8px;align-items:baseline;margin:0 0 6px;font-size:.92rem}figcaption span{color:var(--ink2);font-size:.8rem;font-family:"IBM Plex Mono",monospace}
.wrap{overflow-x:auto;border:1px solid var(--rule);background:var(--surface)}svg{display:block}.tick{font:10px "IBM Plex Mono",monospace;fill:var(--ink2)}
.notes{margin:24px 0 0;padding:0 0 0 1.1em;color:var(--ink2);font-size:.9rem;max-width:80ch}.notes li{margin:4px 0}
.tw{overflow-x:auto}table{border-collapse:collapse;font-size:.88rem;margin:8px 0 0;font-variant-numeric:tabular-nums}td,th{padding:5px 12px;border-bottom:1px solid var(--rule);text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}
b.ok{color:var(--ok)}b.ng{color:var(--ng)}code{font-family:"IBM Plex Mono",monospace;font-size:.85em}
</style>
<h1>nvblox 절단 거리 4 → 2 복셀 — 로컬 코스트맵 정지 A/B (2026-09-22)</h1>
<p class="lead">같은 배치(로버: 출발 테이프, 상자 전면 x %(bx).3f·중심 y %(by).3f)에서 STVL 층, nvblox 층(절단 4.0 = 띠 0.20 m), nvblox 층(절단 2.0 = 띠 0.10 m)을 차례로 캡처했다. 층은 09-21 <code>floor</code> 수정본. 좌표는 base_link, +x 앞, +y 왼쪽(위). 초록 점선 = 물리 상자, 검은 사각형 = 차체, 노란 점선 = 카메라 화각.</p>
<div class="kpis">
 <div class="kpi"><b style="color:var(--nvonly)">%(n4)d → %(n2)d</b><span>nvblox 층에만 LETHAL (절단 4 → 2)</span></div>
 <div class="kpi"><b>%(d4).2f → %(d2).2f m</b><span>슬라이스 상자 깊이 (물리 %(bd).2f)</span></div>
 <div class="kpi"><b>%(f4).2f / %(f2).2f</b><span>상자 앞면 셀 t4 / t2 (물리 %(bx).3f)</span></div>
 <div class="kpi"><b>%(s4)d / %(s2)d</b><span>STVL 층에만 LETHAL t4 / t2</span></div>
</div>
<div class="legend"><span><i style="background:var(--lethal)"></i>LETHAL(100)</span><span><i style="background:var(--inscribed)"></i>내접 99</span><span><i style="background:var(--cost)"></i>비용 1~98</span><span><i style="background:var(--both)"></i>둘 다</span><span><i style="background:var(--nvonly)"></i>nvblox 만</span><span><i style="background:var(--stonly)"></i>STVL 만</span><span><i style="background:var(--unknown)"></i>슬라이스 미지</span><span><i class="line"></i>물리 상자</span></div>
<div class="grid2">
%(p1)s
%(p2)s
%(p3)s
%(p4)s
%(p5)s
%(p6)s
</div>
<h2>판정 (측정 전에 선언한 기준, SUMMARY §1)</h2>
<div class="tw"><table><thead><tr><th>기준</th><th>내용</th><th>측정</th><th>결과</th></tr></thead><tbody>
<tr><td>T1</td><td>상자 앞면 셀 두 조건 동일 = 물리 셀</td><td>t4 %(f4).2f · t2 %(f2).2f · 물리 %(bx).3f</td><td>%(T1)s</td></tr>
<tr><td>T2</td><td>슬라이스 상자 깊이 ≤ 0.15 m</td><td>%(d4).2f → %(d2).2f</td><td>%(T2)s</td></tr>
<tr><td>T3</td><td>nvblox 만 ≥ 40 %% 감소, STVL 만 ≤ 10</td><td>%(n4)d → %(n2)d, STVL 만 %(s2)d</td><td>%(T3)s</td></tr>
<tr><td>T4</td><td>감사 기준1 최소폭 0.40 유지</td><td>t4 %(w4)s · t2 %(w2)s</td><td>—</td></tr>
<tr><td>T5</td><td>N0 게이트(자취 0·주기·GPU·CPU)</td><td>%(t5)s</td><td>—</td></tr>
<tr><td>T6</td><td>표면 연속성: 벽·가구 LETHAL x 열 수 10 %% 이상 감소 금지</td><td>우측 벽 %(c4r)d → %(c2r)d · 좌측 가구 %(c4l)d → %(c2l)d</td><td>%(T6)s</td></tr>
</tbody></table></div>
<h2>선언 기준이 놓친 것 — 데이터를 본 뒤의 정정 (기준 강도는 선언보다 약함)</h2>
<div class="tw"><table><thead><tr><th>항목</th><th>절단 4.0</th><th>절단 2.0</th><th>읽기</th></tr></thead><tbody>
<tr><td>슬라이스 ≤0 셀 전체 / 그중 껍질 안쪽(띠)</td><td>173 / 73</td><td>110 / 25</td><td>띠 내부가 73 → 25 로 줄어 두께 감소는 확인됨</td></tr>
<tr><td>nvblox 만 — 띠가 자라는 구역(상자 + 우측 벽)</td><td>%(bn4)d</td><td>%(bn2)d</td><td>T3 의 의도(띠 감소)는 이 구역에서 %(bnpct).0f %% 감소로 충족</td></tr>
<tr><td>nvblox 만 — 좌측 가구</td><td>%(ln4)d</td><td>%(ln2)d</td><td>절단과 무관: base 거리 0.75~1.80 m(중앙 1.32)로 STVL 카메라 범위 <code>obstacle_range 1.2</code> 밖을 nvblox 만(통합 2.0 m) 본다</td></tr>
<tr><td>STVL 만(두 조건 공통 19)</td><td colspan="2">좌측 가구 9 · 뒤·옆 7 · 우측 벽 2 · 상자 1</td><td>절단과 무관: nvblox 슬라이스 높이 0.03~0.30 이 STVL 의 0.06~0.40 보다 낮아 가구 윗부분을 못 봄(후속 항목), 뒤·옆은 시야 밖</td></tr>
<tr><td>사라진 x 열의 위치(T6 의 의도 = 구멍)</td><td colspan="2">우측 벽: 2.05·2.10(끝, 통합 2.0 m 가장자리) → 구멍 0 · 좌측 가구: 1.55(안쪽 1 개)·1.65·1.90(끝)</td><td>구멍은 5 cm 1 개(거리 ≈1.7 m, 스침각). inflation 0.40 이 메우는 크기</td></tr>
<tr><td>상자 앞면 행별 x 셀</td><td>6 행, 1.25/1.15×4/1.20</td><td>5 행, 1.15×5</td><td>2.0 이 앞면을 더 고르게 찍음. 뒤끝 1.40 → 1.30(물리 1.26)</td></tr>
</tbody></table></div>
<h2>구역별 "nvblox 만" 셀</h2>
<div class="tw"><table><thead><tr><th>구역</th><th>절단 4.0</th><th>절단 2.0</th></tr></thead><tbody>%(rows)s</tbody></table></div>
<ul class="notes">
<li>절단 거리는 TSDF 가 표면 뒤로 음수 거리를 써 넣는 깊이다. 이진 층은 거리 ≤ 0 을 전부 치명으로 올리므로 띠 두께가 곧 치명 셀 두께가 된다(09-21 §10.3~10.5). 4 → 2 복셀은 그 두께를 0.20 → 0.10 m 로 줄이려는 것이고, 표면 앞(자유 공간) 쪽은 바뀌지 않아야 한다(T1).</li>
<li>절단이 작을수록 깊이 잡음(D455f, 1~2 m 에서 1~4 cm)에 대한 여유가 줄어 경사면·모서리에 구멍이 날 수 있다 — T6 가 그것을 감시한다. 벤더 예제는 전부 4.0 이며, 2.0 채택은 우리 복셀(0.05)·거리(≤2 m) 조건에서의 측정 결과에만 근거한다.</li>
<li>판정: T1·T2·T4·T5 통과, T3·T6 는 선언한 문구대로는 불합격. 다만 T3 는 "nvblox 만 = 띠" 라는 전제가 틀렸고(좌측 가구는 범위 차), T6 는 x 열 수가 띠의 x 방향 확장과 섞여 있었다. 띠가 자라는 구역만 보면 두께·개수 모두 줄었고 구멍은 5 cm 1 개다. 절단 2.0 채택 여부는 사용자 결정(SUMMARY 09-22 §1).</li>
</ul>
'''
rows = ''.join('<tr><td>%s</td><td>%d</td><td>%d</td></tr>' % (r, t4['regN'][r], t2['regN'][r]) for r in ('상자', '좌측 가구', '우측 벽', '뒤·옆', '기타'))
p1 = panel('A. STVL 층 (기준선 구성)', 'LETHAL %d' % len(lethS), rects(S, lambda v: cm_color[cls(v)]))
p2 = panel('B. nvblox 층 — 절단 4.0 (띠 0.20 m)', 'LETHAL %d · 상자 %s' % (len(t4['lethN']), ext(t4['boxN'])), rects(t4['N'], lambda v: cm_color[cls(v)]))
p3 = panel('C. nvblox 층 — 절단 2.0 (띠 0.10 m)', 'LETHAL %d · 상자 %s' % (len(t2['lethN']), ext(t2['boxN'])), rects(t2['N'], lambda v: cm_color[cls(v)]))
p4 = panel('D. 차이 STVL vs 절단 4.0', '둘 다 %d · nvblox 만 %d · STVL 만 %d' % (t4['cnt']['B'], t4['cnt']['N'], t4['cnt']['S']), rects(t4['diff'], lambda v: diff_color[v]))
p5 = panel('E. 차이 STVL vs 절단 2.0', '둘 다 %d · nvblox 만 %d · STVL 만 %d' % (t2['cnt']['B'], t2['cnt']['N'], t2['cnt']['S']), rects(t2['diff'], lambda v: diff_color[v]))
p6 = panel('F. 슬라이스 원자료 — 절단 2.0', '≤0 %d · 상자 %s' % (len(t2['lethL']), ext(t2['boxL'])), rects(t2['L'], slice_color))
out = html % dict(bx=BX, by=BY, bd=BOX_D, n4=t4['cnt']['N'], n2=t2['cnt']['N'], s4=t4['cnt']['S'], s2=t2['cnt']['S'], d4=t4['depth'] or 0, d2=t2['depth'] or 0, f4=t4['front'] or 0, f2=t2['front'] or 0,
                  p1=p1, p2=p2, p3=p3, p4=p4, p5=p5, p6=p6, T1=mark(T1), T2=mark(T2), T3=mark(T3), T6=mark(T6), w4=W4, w2=W2, t5=T5, rows=rows,
                  c4r=t4['cols']['우측 벽'], c2r=t2['cols']['우측 벽'], c4l=t4['cols']['좌측 가구'], c2l=t2['cols']['좌측 가구'],
                  bn4=t4['regN']['상자'] + t4['regN']['우측 벽'], bn2=t2['regN']['상자'] + t2['regN']['우측 벽'],
                  bnpct=100.0 * (1 - (t2['regN']['상자'] + t2['regN']['우측 벽']) / max(1, t4['regN']['상자'] + t4['regN']['우측 벽'])),
                  ln4=t4['regN']['좌측 가구'], ln2=t2['regN']['좌측 가구'])
open(OUT, 'w', encoding='utf-8').write(out); print('html %d bytes → %s | T1 %s T2 %s T3 %s T6 %s' % (len(out.encode('utf-8')), OUT, T1, T2, T3, T6))
