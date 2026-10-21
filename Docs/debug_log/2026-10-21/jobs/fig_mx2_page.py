# 10-21 §19.3 mx2 결과 정리 페이지 생성기 — 수치는 outputs/run_mx2.txt · anal_mx2_leak.txt 에서 옮김, 그림은 mx_img/*.png 를 그대로 넣음
import base64, sys, html
D = sys.argv[1]; OUT = sys.argv[2]
img = lambda n: 'data:image/png;base64,' + base64.b64encode(open('%s/%s.png' % (D, n), 'rb').read()).decode()

# (키, 이름, 설명, 켠 깊이, 아래, 끈 밝기, FAST20, FAST5, lap, 새어 든 점 아래 1/4, 새어 든 점 전체, 켠 모드, 끈 모드)
R = [
    ('Auto', '자동 노출', '지금 NVIDIA 기본 · 노출 32.0 ms · 게인 16', 0.668, 0.531, 17.9, 1, 205, 0.65, 0, 3, 'm0', 'm1'),
    ('A24k248', 'A 24 ms × 248', '수동 고정 · 기동 파라미터', 0.533, 0.312, 39.9, 27, 378, 3.38, 0, 38, 'm0', 'm1'),
    ('B28k248', 'B 28 ms × 248', '수동 고정 · 기동 파라미터', 0.529, 0.308, 44.2, 92, 693, 3.77, 74, 114, 'm0', 'm1'),
    ('C32k248', 'C 32 ms × 248', '수동 고정 · 기동 파라미터', 0.526, 0.306, 47.6, 233, 1014, 4.15, 209, 260, 'm0', 'm1'),
    ('D32k128', 'D 32 ms × 128', '수동 고정 · 기동 파라미터', 0.562, 0.346, 32.5, 221, 498, 2.74, 221, 245, 'm0', 'm1'),
    ('Ctl', '대조 · 상시 끔', '지금 운용 방식 · 자동 노출 32.0 ms · 게인 246', 0.193, 0.141, 46.0, 46, 564, 3.70, 0, 50, None, 'm0'),
]


def bars(title, unit, idx, vmax, fmt, note, ref=None):
    # 가로 막대: 한 축(0 ~ vmax), 값 라벨은 막대 끝, ref = 세로 기준선(값, 이름)
    W, LW, RH, TOP = 520, 118, 30, 8
    H = TOP + RH * len(R) + 26
    x = lambda v: LW + (W - LW - 64) * v / vmax
    s = ['<svg viewBox="0 0 %d %d" role="img" aria-label="%s">' % (W, H, html.escape(title))]
    for t in [vmax * k / 4 for k in range(5)]:
        s.append('<line x1="%.1f" x2="%.1f" y1="%d" y2="%d" class="grid"/>' % (x(t), x(t), TOP, H - 20))
        s.append('<text x="%.1f" y="%d" class="tick" text-anchor="middle">%s</text>' % (x(t), H - 6, fmt(t)))
    for i, r in enumerate(R):
        v = r[idx]; y = TOP + i * RH
        cls = 'bar hl' if r[0] == 'A24k248' else ('bar ctl' if r[0] == 'Ctl' else 'bar')
        s.append('<text x="%d" y="%d" class="lab" text-anchor="end">%s</text>' % (LW - 10, y + 19, html.escape(r[1])))
        w = max(x(v) - LW, 2)
        s.append('<path class="%s" d="M%d %d h%.1f a4 4 0 0 1 4 4 v10 a4 4 0 0 1 -4 4 h-%.1f z"><title>%s: %s %s</title></path>' % (cls, LW, y + 6, w - 4, w - 4, html.escape(r[1]), fmt(v), unit))
        s.append('<text x="%.1f" y="%d" class="val">%s</text>' % (LW + w + 6, y + 19, fmt(v)))
    if ref:
        s.append('<line x1="%.1f" x2="%.1f" y1="%d" y2="%d" class="ref"/>' % (x(ref[0]), x(ref[0]), TOP - 4, H - 20))
    s.append('</svg>')
    return '<figure class="chart"><figcaption><b>%s</b><span>%s</span></figcaption>%s</figure>' % (title, note, ''.join(s))


rows = ''.join('<tr%s><th scope="row">%s<small>%s</small></th><td>%.3f</td><td>%.3f</td><td>%.1f</td><td>%d</td><td>%d</td><td>%.2f</td><td>%d</td></tr>' % (
    ' class="hl"' if r[0] == 'A24k248' else '', r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]) for r in R)

cards = []
for r in R:
    on_ir = '<img src="%s" alt="%s 켠 IR" loading="lazy">' % (img('%s_IR_%s' % (r[0], r[11])), r[1]) if r[11] else '<div class="none">프로젝터 켠 프레임 없음</div>'
    on_d = '<img src="%s" alt="%s 켠 깊이" loading="lazy">' % (img('%s_depth_%s' % (r[0], r[11] or r[12])), r[1])
    off_ir = '<img src="%s" alt="%s 끈 IR" class="ir" loading="lazy">' % (img('%s_IR_%s' % (r[0], r[12])), r[1])
    leak = '<span class="chip warn">점 새어 듦 %d</span>' % r[9] if r[9] else '<span class="chip ok">점 새어 듦 0</span>'
    cards.append('''<article class="set%s" id="set-%s"><header><h3>%s</h3><p>%s</p>%s</header>
<div class="trio"><figure><figcaption>끈 IR <em>→ cuVSLAM 입력</em></figcaption>%s</figure>
<figure><figcaption>켠 IR <em>점 무늬</em></figcaption>%s</figure>
<figure><figcaption>%s 깊이 <em>→ nvblox 입력</em></figcaption>%s</figure></div></article>''' % (
        ' hl' if r[0] == 'A24k248' else '', r[0], r[1], r[2], leak, off_ir, on_ir, '켠' if r[11] else '상시 끔', on_d))

page = '''<title>프로젝터 번갈이 노출 시험</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* 레이아웃: 실험 노트 한 장 — 결론 → 수치 표 · 막대 → 설정별 실제 프레임 → 추론 경로 */
:root{
  --bg:#f3f4f2; --panel:#ffffff; --ink:#1d2421; --ink2:#4f5954; --mute:#7c8580; --rule:#d9ddd8;
  --bar:#8f9c95; --hl:#b4561f; --ctl:#2f6f8f; --ok:#2d7a4b; --warn:#b4561f; --chipbg:#eceeea;
  --sans:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#141816; --panel:#1c211f; --ink:#e4e8e5; --ink2:#b3bbb6; --mute:#87908b; --rule:#2e3532;
  --bar:#6c7972; --hl:#e88a4f; --ctl:#6fb2d4; --ok:#6cc08b; --warn:#e88a4f; --chipbg:#262c29; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#141816; --panel:#1c211f; --ink:#e4e8e5; --ink2:#b3bbb6; --mute:#87908b; --rule:#2e3532;
  --bar:#6c7972; --hl:#e88a4f; --ctl:#6fb2d4; --ok:#6cc08b; --warn:#e88a4f; --chipbg:#262c29; color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.65 var(--sans);margin:0}
.wrap{max-width:1080px;margin:0 auto;padding-block:28px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:36px}
h1{font-size:1.75rem;line-height:1.3;margin:0;text-wrap:balance;font-weight:700}
h2{font-size:1.15rem;margin:0 0 12px;text-wrap:balance}
h3{font-size:1rem;margin:0}
.eyebrow{font:500 .75rem var(--mono);letter-spacing:.06em;color:var(--mute);margin:0 0 6px;text-transform:uppercase}
.lede{max-width:68ch;color:var(--ink2);margin:10px 0 0}
.verdict{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.verdict div{background:var(--panel);border:1px solid var(--rule);border-radius:6px;padding:14px 16px;min-width:0}
.verdict b{display:block;font-size:.8rem;color:var(--mute);font-weight:500}
.verdict p{margin:4px 0 0}
.fail{color:var(--warn);font-weight:700}.pass{color:var(--ok);font-weight:700}
.tbl{overflow-x:auto;background:var(--panel);border:1px solid var(--rule);border-radius:6px}
table{border-collapse:collapse;width:100%;min-width:720px;font-variant-numeric:tabular-nums}
th,td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-family:var(--mono);font-size:.86rem}
thead th{font:500 .74rem var(--sans);color:var(--mute);vertical-align:bottom}
tbody th{text-align:left;font:500 .9rem var(--sans)}
tbody th small{display:block;color:var(--mute);font-weight:400;font-size:.74rem}
tr.hl th,tr.hl td{background:color-mix(in srgb,var(--hl) 9%,transparent)}
tbody tr:last-child th,tbody tr:last-child td{border-bottom:0}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.chart{margin:0;background:var(--panel);border:1px solid var(--rule);border-radius:6px;padding:14px 14px 6px;min-width:0}
.chart figcaption{display:grid;gap:2px;margin-bottom:6px}.chart figcaption span{color:var(--mute);font-size:.8rem}
.chart svg{width:100%;height:auto;display:block}
.grid{stroke:var(--rule);stroke-width:1}.ref{stroke:var(--ink2);stroke-width:1.5;stroke-dasharray:3 3}
.tick{fill:var(--mute);font:11px var(--mono)}.lab{fill:var(--ink2);font:12px var(--sans)}.val{fill:var(--ink);font:12px var(--mono)}
.bar{fill:var(--bar)}.bar.hl{fill:var(--hl)}.bar.ctl{fill:var(--ctl)}.bar:hover{opacity:.8}
.tools{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}
.tools p{margin:0;color:var(--ink2);max-width:62ch}
.seg{display:inline-flex;border:1px solid var(--rule);border-radius:6px;overflow:hidden;background:var(--panel)}
.seg button{font:500 .85rem var(--sans);color:var(--ink2);background:none;border:0;padding:7px 14px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--ink);color:var(--bg)}
.seg button:focus-visible{outline:2px solid var(--hl);outline-offset:-2px}
.sets{display:grid;gap:18px}
.set{background:var(--panel);border:1px solid var(--rule);border-radius:6px;padding:14px}
.set.hl{border-color:var(--hl)}
.set header{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;margin-bottom:10px}
.set header p{margin:0;color:var(--mute);font-size:.84rem;flex:1 1 200px}
.chip{font:500 .76rem var(--mono);padding:2px 8px;border-radius:999px;background:var(--chipbg)}
.chip.ok{color:var(--ok)}.chip.warn{color:var(--warn)}
.trio{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.trio figure{margin:0;min-width:0}
.trio figcaption{font-size:.8rem;color:var(--ink2);margin-bottom:4px}.trio em{font-style:normal;color:var(--mute)}
.trio img,.none{width:100%;aspect-ratio:4/3;display:block;border-radius:3px;background:#000;image-rendering:auto}
.none{display:grid;place-items:center;color:#9aa;font-size:.8rem}
body.boost img.ir{filter:brightness(2.6)}
@media (max-width:640px){.trio{grid-template-columns:1fr 1fr}.trio figure:first-child{grid-column:1/-1}}
.flow{display:grid;gap:0;background:var(--panel);border:1px solid var(--rule);border-radius:6px}
.flow div{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:10px 14px;border-bottom:1px solid var(--rule)}
.flow div:last-child{border-bottom:0}.flow b{font-size:.82rem;color:var(--mute);font-weight:500}
.flow p{margin:0;max-width:72ch}
@media (max-width:520px){.flow div{grid-template-columns:1fr;gap:2px}}
code{font:.85em var(--mono)}
.src{color:var(--mute);font-size:.8rem}
</style>
<div class="wrap">
<header>
  <p class="eyebrow">2026-10-21 · SUMMARY §19.2–19.3 · 시험 mx2 · 로버 정지</p>
  <h1>프로젝터 번갈이 중 노출 · 게인을 고정하면 끈 IR 이 살아나는가</h1>
  <p class="lede">D455f 프로젝터를 30 fps 로 켰다 끄며(번갈이), 켠 프레임은 깊이(nvblox)에 끈 프레임은 IR 영상(cuVSLAM)에 쓰는 구성입니다. 자동 노출은 켠 프레임에 맞춰져 끈 IR 이 어둡습니다. 노출 · 게인을 카메라 기동 때 고정해 네 가지 값을 재고, 지금 운용 방식(프로젝터 상시 끔)과 비교했습니다. 장치: 드라이버 realsense-ros 4.51.1 · librealsense 2.55.1 · 펌웨어 5.15.0.2. 설정마다 6 초, 같은 자세.</p>
</header>

<section class="verdict" aria-label="판정">
  <div><b>설정 수락 · 번갈이 유지</b><p><span class="pass">5 / 5 통과</span> — 기동 파라미터로 넣으면 메타데이터가 요청값과 같고 번갈이도 유지. 실행 중에 바꾸면 거부되거나 번갈이가 깨졌음(mx1).</p></div>
  <div><b>선언 기준 3 · 켠 깊이 ≥ 자동의 90 %</b><p><span class="fail">전부 미달</span> — 78~83 %. 게인을 올리면 점 무늬가 과노출돼 깊이가 줄어듦(추정).</p></div>
  <div><b>새로 본 것 · 점 새어 듦</b><p>노출 28 ms 이상이면 끈 프레임 아래 바닥에 <span class="fail">켠 프레임의 점이 찍힘</span> — 카메라에 붙은 가짜 특징. 24 ms 는 0.</p></div>
  <div><b>절충점(판정과 별개)</b><p><b style="color:var(--hl);display:inline">A 24 ms × 248</b>: 상시 끔보다 켠 깊이 2.8 배, 끈 IR 밝기 87 %, 점 새어 듦 없음. 실제 주행에서 충분한지는 미확인.</p></div>
</section>

<section>
  <h2>수치</h2>
  <div class="tbl"><table>
    <thead><tr><th scope="col" style="text-align:left">설정 (P30 번갈이)</th><th scope="col">켠 깊이 유효</th><th scope="col">아래 절반</th><th scope="col">끈 IR 밝기</th><th scope="col">FAST20</th><th scope="col">FAST5</th><th scope="col">|라플라시안|</th><th scope="col">점 새어 듦<br>(아래 1/4)</th></tr></thead>
    <tbody>%ROWS%</tbody>
  </table></div>
  <p class="src">깊이 유효 = 0 이 아닌 화소 비율(중앙값). 밝기 · FAST · 라플라시안은 끈 IR1 프레임 중앙값. 점 새어 듦 = 저장된 끈 IR 한 장의 흰 점 수(top-hat 5×5 &gt; 20) — 설정당 한 장이라 참고값. 대조 행은 번갈이가 없어 "켠 깊이" 가 곧 상시 끔 깊이. 원문 <code>outputs/run_mx2.txt</code> · <code>anal_mx2_leak.txt</code>.</p>
</section>

<section class="charts" aria-label="막대 그림">
%CHARTS%
</section>

<section>
  <div class="tools">
    <h2 style="margin:0">설정별 실제 프레임</h2>
    <div class="seg" role="group" aria-label="끈 IR 밝기 보기">
      <button type="button" id="b-raw" aria-pressed="true">원본 밝기</button>
      <button type="button" id="b-boost" aria-pressed="false">끈 IR 2.6 배 밝게</button>
    </div>
  </div>
  <p class="src" style="margin:8px 0 14px">각 설정에서 저장한 한 장씩. 깊이는 가까울수록 밝게(0~4 m), 검정 = 깊이 없음. "끈 IR 2.6 배" 는 화면 표시만 바꿉니다 — 어두운 영상에서 바닥 점 새어 듦과 장면 질감을 보기 쉽게.</p>
  <div class="sets">%CARDS%</div>
</section>

<section>
  <h2>추론 경로</h2>
  <div class="flow">
    <div><b>하려 한 것</b><p>mx1 에서 실행 중 쓰기(<code>ros2 param</code>)로는 30 fps 번갈이의 긴 노출이 USB 단에서 거부됨(<code>RS2_USB_STATUS_PIPE</code>). 그래서 노출 · 게인을 카메라 기동 파라미터로 넣고 설정마다 다시 기동.</p></div>
    <div><b>본 것</b><p>다섯 설정 모두 메타데이터 노출 · 게인이 요청값 그대로, 드라이버 오류 0 건, 번갈이 유지. 노출을 늘릴수록 끈 IR 밝기 39.9 → 47.6, FAST20 27 → 233.</p></div>
    <div><b>처음 추론</b><p>32 ms × 248 이 대조(상시 끔, 31979 µs · 246)와 노출 · 게인이 같으니 끈 IR 도 같아야 하고, FAST20 233 은 대조(46)보다 특징이 많은 좋은 결과.</p></div>
    <div><b>의심한 이유</b><p>노출 · 게인 · 밝기가 대조와 같은데 특징 수만 5 배 — 장면이 바뀌지 않았으니 특징이 늘 이유가 없음.</p></div>
    <div><b>판별</b><p>저장한 끈 IR 프레임을 직접 봄 → 아래 바닥에 프로젝터 점 무늬. 흰 점 수(아래 1/4): 24 ms 0 · 28 ms 74 · 32 ms 209~221 · 대조 0.</p></div>
    <div><b>결론</b><p>노출이 프레임 주기(33.3 ms)에 가까워지면 켠 구간 빛이 끈 프레임에 섞임(기전 추정 · 미확인). FAST 증가는 가짜 특징이므로 28 ms 이상은 cuVSLAM 입력으로 부적합. 남는 것은 24 ms.</p></div>
    <div><b>다음에 알아보는 법</b><p>끈 IR 의 특징 수가 같은 노출의 대조보다 크면 먼저 프레임을 본다. 점 새어 듦은 아래 바닥(가까운 면)부터 나타난다.</p></div>
    <div><b>데이터</b><p>경로는 <code>Docs/debug_log/2026-10-21/</code> 아래. 지표 <code>outputs/run_mx2.txt</code>(메타 노출 · 게인, 밝기 · FAST, 깊이 유효) · 흰 점 수 <code>outputs/anal_mx2_leak.txt</code>(도구 <code>jobs/anal_mx2_leak.py</code>) · 측정 도구 <code>jobs/anal_mx1.py</code> · <code>run_mx2.sh</code> · 판별에 본 프레임 <code>figures/mx2/*.png</code>. 실행 중 쓰기 거부(mx1)는 <code>outputs/run_mx1.txt</code>. 라이브 측정이라 bag 없음, 드라이버 로그는 Jetson <code>/tmp/mx2_*.log</code>(휘발).</p></div>
  </div>
</section>

<section>
  <h2>남은 것</h2>
  <div class="flow">
    <div><b>판정</b><p>§19 선언 기준으로는 (나) 후보 없음 — 켠 깊이 기준(자동의 90 %)을 넘는 설정이 없음.</p></div>
    <div><b>함께 풀어야 할 것</b><p>메타데이터 켬/끔 표시가 이번에도 뒤집혀 있음(모드 0 = 켬). NVIDIA 분리 노드를 쓰려면 모드 판정을 반대로 해야 함.</p></div>
    <div><b>사용자 결정</b><p>A 24 ms × 248 절충(깊이 −20 % vs 자동 번갈이, 대신 끈 IR 확보)을 주행 기록으로 판별할지, 지금 운용(상시 끔)을 유지할지.</p></div>
  </div>
</section>
</div>
<script>
(function(){
  var raw=document.getElementById('b-raw'), boost=document.getElementById('b-boost');
  function set(on){document.body.classList.toggle('boost',on);raw.setAttribute('aria-pressed',String(!on));boost.setAttribute('aria-pressed',String(on));
    try{localStorage.setItem('mx2-boost',on?'1':'0')}catch(e){}}
  raw.addEventListener('click',function(){set(false)}); boost.addEventListener('click',function(){set(true)});
  try{if(localStorage.getItem('mx2-boost')==='1')set(true)}catch(e){}
})();
</script>
'''
charts = (bars('켠 깊이 유효 비율 → nvblox', '', 3, 0.8, lambda v: '%.2f' % v, '높을수록 좋음 · 점선 = 자동의 90 % (선언 기준)', ref=(0.668 * 0.9, '90 %'))
          + bars('끈 IR 밝기 → cuVSLAM', '', 5, 60, lambda v: '%.0f' % v, '높을수록 좋음 · 점선 = 대조의 80 % (선언 기준)', ref=(46.0 * 0.8, '80 %'))
          + bars('끈 프레임에 새어 든 점 (아래 1/4)', '개', 9, 240, lambda v: '%.0f' % v, '0 이어야 함 · 카메라에 붙은 가짜 특징'))
page = page.replace('%ROWS%', rows).replace('%CHARTS%', charts).replace('%CARDS%', '\n'.join(cards))
open(OUT, 'w', encoding='utf8').write(page)
print(len(page))
