# 10-21 하루 정리 페이지 생성기 — 본문 수치는 SUMMARY.md §0~§22 에서 옮김, 그림은 figures/ 의 PNG 를 그대로 넣음
#   사용: python fig_day_summary_1021.py <figures 폴더> <출력 html>
import base64, sys
F = sys.argv[1]; OUT = sys.argv[2]
img = lambda p: 'data:image/png;base64,' + base64.b64encode(open('%s/%s' % (F, p), 'rb').read()).decode()

page = '''<title>10-21 유령 셀과 프로젝터</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* 레이아웃: 하루 실험 노트 — 판정 카드 → 주제별 절(그림 · 표) → 바로잡은 내 오류(칸 형식) → 다음 */
:root{
  --bg:#f2f3f1; --panel:#ffffff; --ink:#1c2320; --ink2:#4b5651; --mute:#78827d; --rule:#d7dbd6;
  --ok:#2c7a4a; --no:#b0461f; --wait:#8a6a12; --hl:#b0461f; --chip:#eaece8;
  --sans:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#131715; --panel:#1b201e; --ink:#e3e8e5; --ink2:#b1bab5; --mute:#86908b; --rule:#2d3431;
  --ok:#6cc08b; --no:#e8895a; --wait:#d6b45a; --hl:#e8895a; --chip:#252b28; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#131715; --panel:#1b201e; --ink:#e3e8e5; --ink2:#b1bab5; --mute:#86908b; --rule:#2d3431;
  --ok:#6cc08b; --no:#e8895a; --wait:#d6b45a; --hl:#e8895a; --chip:#252b28; color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.68 var(--sans);margin:0}
.wrap{max-width:1040px;margin:0 auto;padding-block:28px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:40px}
h1{font-size:1.8rem;line-height:1.3;margin:0;text-wrap:balance}
h2{font-size:1.2rem;margin:0 0 10px;text-wrap:balance;display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline}
h3{font-size:1rem;margin:0 0 8px}
.sec{font:500 .74rem var(--mono);color:var(--mute)}
.eyebrow{font:500 .75rem var(--mono);letter-spacing:.05em;color:var(--mute);margin:0 0 6px}
.lead{color:var(--ink2);max-width:70ch;margin:10px 0 0}
p{max-width:72ch;margin:0 0 10px}
.note{color:var(--mute);font-size:.86rem}
.verdicts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}
.v{background:var(--panel);border:1px solid var(--rule);border-left:4px solid var(--mute);border-radius:4px;padding:11px 14px;display:grid;gap:3px;min-width:0}
.v.ok{border-left-color:var(--ok)}.v.no{border-left-color:var(--no)}.v.wait{border-left-color:var(--wait)}
.v b{font-size:.95rem}.v span{color:var(--ink2);font-size:.86rem}
.tbl{overflow-x:auto;background:var(--panel);border:1px solid var(--rule);border-radius:6px;margin:6px 0 12px}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums;font-size:.88rem}
th,td{padding:7px 11px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{font-weight:500;color:var(--mute);font-size:.78rem}
td.n{font-family:var(--mono);text-align:right;white-space:nowrap}
tr.hl td{background:color-mix(in srgb,var(--hl) 9%,transparent)}
tr:last-child td{border-bottom:0}
figure{margin:8px 0 14px}
figure img{width:100%;height:auto;display:block;border-radius:4px;border:1px solid var(--rule);background:#000}
figcaption{color:var(--mute);font-size:.82rem;margin-top:5px;max-width:80ch}
.duo{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.duo figure{margin:0;min-width:0}
.mono{font-family:var(--mono);font-size:.86em}
.pm{background:var(--panel);border:1px solid var(--rule);border-radius:6px;padding:14px 16px;margin-bottom:12px}
.flow{display:grid;grid-template-columns:118px minmax(0,1fr);gap:7px 14px}
.flow .k{font-size:.8rem;color:var(--mute);font-weight:500;padding-top:2px}
@media (max-width:560px){.flow{grid-template-columns:1fr}.flow .k{padding-top:6px}}
.pill{font:500 .72rem var(--mono);padding:1px 7px;border-radius:999px;background:var(--chip);color:var(--mute);margin-left:6px}
</style>
<div class="wrap">
<header>
  <p class="eyebrow">Indoor Rover · 2026-10-21 · Docs/debug_log/2026-10-21 §0–§22</p>
  <h1>10-21 유령 셀과 프로젝터</h1>
  <p class="lead">아침에는 출발 위치 검사를 prep 에 넣고 공유메모리 그림자 주행 f2sm1 을 마쳤습니다. 오후에는 사용자가 지목한 '없는데 찍히는 장애물 칸' 을 추적해 카메라(nvblox) 깊이, 그중에서도 프로젝터를 끈 뒤의 맨바닥이 출처임을 확인했습니다. 프로젝터를 다시 쓰는 길(NVIDIA 권장 구성, 번갈이 중 노출 고정)을 정지 시험으로 확인했지만 채택하지 않았고, 프로젝터를 끈 채로 깊이 프리셋을 바꾸는 대책이 정지 시험을 통과했습니다. 주행 확인은 내일입니다.</p>
</header>

<section>
  <h2>오늘의 판정</h2>
  <div class="verdicts">
    <div class="v ok"><b>prep 에 출발 위치 추정 검사 추가</b><span>위치 ±0.10 m · yaw ±2° 밖이면 PREP_FAIL. 오늘 한 번 실제로 걸렀고(0.049 m · 2.5°), 재실행에서 통과 (§1 · §21.1)</span></div>
    <div class="v ok"><b>f2sm1 공유메모리 그림자 주행 3/3</b><span>W3 회전 최대 창 24.1 → 16.1 cm(−33 %), cuVSLAM 프레임 간격 경고 4 분에 5 회 (§7)</span></div>
    <div class="v no"><b>f2sm2: 사람이 떠난 뒤에도 목표 칸이 막혀 W3 포기</b><span>라이다엔 없는데 전역 비용 99 칸 38~40 개가 끝까지 남음, 3 m 안은 안 지우는 복구 · 목표점까지 보는 막힘 검사가 겹침 (§10 · §12.1)</span></div>
    <div class="v wait"><b>복귀 중 멈칫 13 번의 원인 분류</b><span>TF 미래 외삽으로 컨트롤러 중단 6 · 제어 주기 지연 4 · 최적화 실패 2. 외삽이 0.5 s 여유로 안 덮이는 이유는 미확인 (§12.2)</span></div>
    <div class="v ok"><b>유령 칸의 출처는 nvblox(카메라)</b><span>끝 상태 지도 밖 LETHAL 의 97~100 %. 상자 너머 맨바닥 · 문 사이 점은 프로젝터 끔 주행에서만(28~99 칸 vs 켬 0~3) (§13 · §15)</span></div>
    <div class="v no"><b>NVIDIA 권장 RealSense 구성 불합격</b><span>드라이버를 4.51.1 로 바꿔도 켬/끔 표시가 뒤집힘(펌웨어 5.15 쪽으로 좁혀짐), 번갈이 중 끈 IR 은 평평 (§18)</span></div>
    <div class="v no"><b>번갈이 중 노출 고정: 절충점만</b><span>기동 파라미터로는 수락되지만 켠 깊이 78~83 %, 노출 ≥ 28 ms 면 점이 끈 프레임에 새어 듦 (§19)</span></div>
    <div class="v ok"><b>결정: 프로젝터 상시 끔 유지</b><span>사용자 결정. 유령 대응은 깊이 쪽에서 (§20)</span></div>
    <div class="v ok"><b>깊이 프리셋 High Accuracy 정지 시험 통과</b><span>깜빡 복셀 101 → 2, 앞 상자 유지. 대가: 깊이 채움률 0.317 → 0.045 (§21)</span></div>
    <div class="v wait"><b>주행 f2pr1 은 내일</b><span>유령 칸 · 낮은 상자 감지 기준을 미리 선언해 둠 (§21.2)</span></div>
  </div>
</section>

<section>
  <h2>공유메모리 그림자 주행 f2sm1<span class="sec">§7</span></h2>
  <p>어제 정지 시험으로 확인한 카메라 → cuVSLAM 공유메모리 전달을 실제 주행에서 확인했습니다. cuVSLAM 이동 속도를 넣은 그림자 EKF 는 주 EKF 와 나란히 돌 뿐 로버를 움직이지 않습니다.</p>
  <div class="tbl"><table>
    <tr><th>기준(10-20 §9.6)</th><th>f2sm1</th><th>f2v1(어제, UDP)</th></tr>
    <tr class="hl"><td>W3 회전 최대 창 감소</td><td class="n">24.1 → 16.1 cm (−33 %)</td><td class="n">27.5 → 22.1 (−20 %)</td></tr>
    <tr><td>상자 옆 여유 변화</td><td class="n">+0.9 · +0.6 cm</td><td class="n">+0.3 · −0.1</td></tr>
    <tr><td>정지 부하</td><td class="n">75.7 %</td><td class="n">75.0 %</td></tr>
  </table></div>
  <figure><img src="%%shadow%%" alt="f2sm1 주 EKF 와 그림자 EKF 의 SLAM 대비 오차"><figcaption>f2sm1: 주 EKF(휠 · 자이로)와 그림자 EKF(+ cuVSLAM 이동 속도)의 SLAM 대비 위치 오차. W3 회전 구간의 쌓임이 줄어듦. 주행 1 회 비교라 반복 확인(f2sm3 · f2sm4)이 남아 있습니다.</figcaption></figure>
</section>

<section>
  <h2>사람이 길을 막은 f2sm2 와 복귀 중 멈칫<span class="sec">§10 · §11 · §12</span></h2>
  <p>f2sm2 는 사람들이 일부러 길을 막아 반복 비교에서 뺐고(사용자), 동적 물체 대응의 근거로 씁니다. 사람이 W3 목표 자리에 섰다가 떠난 뒤에도 전역 코스트맵의 칸이 14 초 넘게 남았고, 목표 0.5 m 앞에서 막힘 검사가 매번 주행을 끊어 결국 목표를 포기했습니다. 칸을 들고 있던 층은 nvblox 로 추정합니다(층별 코스트맵이 bag 에 없어 미확인).</p>
  <div class="duo">
    <figure><img src="%%block%%" alt="f2sm2 W3 앞 장면"><figcaption>12:18:01 — 라이다 점(사람)은 사라졌는데 목표 둘레 빨간 칸은 그대로. 6 초 뒤 Goal failed.</figcaption></figure>
    <figure><img src="%%stops%%" alt="복귀 f2sm2h 의 멈춤과 멈칫"><figcaption>복귀 f2sm2h: 5.1 s 정지는 복구 순서의 Wait 차례, 짧은 멈칫 13 번은 0.01 s 시각으로 nav2 사건과 맞춰 분류.</figcaption></figure>
  </div>
</section>

<section>
  <h2>유령 칸은 카메라 깊이에서, 프로젝터를 끈 맨바닥에서<span class="sec">§13 · §14 · §15</span></h2>
  <p>지도에도 없고 그 순간 라이다도 보지 않는 LETHAL 칸을 근거별로 나누면 출발점 둘레 칸의 97~100 % 가 nvblox 슬라이스입니다. SLAM 보정으로 기억이 통째로 옮겨 찍힌다는 가설은 기각했습니다(가장 잘 겹치는 이동이 0). 새 칸이 생기는 거리를 보면 3 m 밖은 라이다, 1.5 m 안은 카메라입니다.</p>
  <div class="tbl"><table>
    <tr><th>t 10~60 s 동안 한 번이라도 LETHAL 이 된 칸(지도 · 라이다 0.10 m 밖)</th><th>프로젝터</th><th>상자 너머 맨바닥</th><th>문 사이</th></tr>
    <tr><td>f2u1 · f2u3 · f2v4 · f2w1 · f2x1</td><td>켬</td><td class="n">3 · 3 · 1 · 0 · 0</td><td class="n">3 · 0 · 0 · 0 · 0</td></tr>
    <tr class="hl"><td>f2z1 · f2z2 · f2sm1 · f2sm2</td><td>끔</td><td class="n">28~99 (흩어짐)</td><td class="n">0 · 6 · 0 · 2</td></tr>
  </table></div>
  <figure><img src="%%phantom%%" alt="f2sm2h 끝 상태의 근거 없는 LETHAL 칸"><figcaption>f2sm2h 끝 상태: 지도 · 라이다 근거 없는 LETHAL 칸(출발점 둘레). 기전(무늬 없는 바닥에서 스테레오 짝 찾기가 틀려 깊이가 튐)은 추정입니다.</figcaption></figure>
</section>

<section>
  <h2>프로젝터를 다시 쓸 수 있나 — NVIDIA 구성과 노출 고정<span class="sec">§16 ~ §19</span></h2>
  <p>프로젝터를 프레임마다 켰다 끄면(번갈이) 켠 프레임은 깊이에, 끈 프레임은 cuVSLAM 에 쓸 수 있습니다. 10-19 에는 두 문제로 실패했습니다: 켬/끔 표시가 뒤집혀 나오고, 자동 노출이 켠 프레임에 맞춰져 끈 IR 이 어둡습니다. NVIDIA 권장 드라이버(librealsense 2.55.1 · realsense-ros 4.51.1)를 시험 컨테이너에 따로 만들어 정지 상태로 다시 쟀습니다.</p>
  <div class="tbl"><table>
    <tr><th>시험</th><th>본 것</th><th>판정</th></tr>
    <tr><td>nv1 NVIDIA 구성 그대로</td><td>실제 켬 = 표시 0(깊이 유효 0.681 vs 0.182) — 우리 드라이버와 같은 방향으로 뒤집힘. 진짜 끈 프레임의 선명도 지표는 상시 끔의 10 %</td><td>불합격</td></tr>
    <tr><td>mx1 실행 중 노출 바꾸기</td><td>60 fps 는 수락되지만 자동 노출을 끄자 번갈이가 깨짐, 30 fps 는 USB 단에서 거부</td><td>후보 없음</td></tr>
    <tr class="hl"><td>mx2 기동 때 노출 고정</td><td>5/5 수락 · 번갈이 유지. 켠 깊이 78~83 %. 24 ms × 248: 끈 IR 밝기 87 %, 점 새어 듦 0</td><td>기준 미달, 절충점</td></tr>
  </table></div>
  <div class="duo">
    <figure><img src="%%mxA%%" alt="24 ms 끈 IR 프레임"><figcaption>A 24 ms × 248 의 끈 IR: 바닥에 점 없음.</figcaption></figure>
    <figure><img src="%%mxC%%" alt="32 ms 끈 IR 프레임"><figcaption>C 32 ms × 248 의 끈 IR: 아래 바닥에 켠 프레임의 점무늬가 새어 듦(가짜 특징). 설정별 그림은 별도 페이지 'mx2' 에.</figcaption></figure>
  </div>
  <p class="note">사용자 결정(§20): 프로젝터 상시 끔을 유지하고 유령은 깊이 쪽에서 대응. 시험 컨테이너와 이미지는 Jetson 에 남겨 두었습니다.</p>
</section>

<section>
  <h2>대응 1: 깊이 프리셋 High Accuracy<span class="sec">§20 · §21</span></h2>
  <p>지금 nvblox 는 드라이버 깊이를 필터 없이 받습니다. D455f 의 고급 모드 프리셋 3(High Accuracy)은 확신 낮은 짝 찾기 결과를 버립니다. 같은 자리에서 0 → 3 → 0 으로 바꿔, nvblox 와 같은 기준(1.4 m 안, 높이 0.06~0.30 m, 5 cm 복셀)으로 셌습니다.</p>
  <div class="tbl"><table>
    <tr><th></th><th>지금(0) · 두 번</th><th>High Accuracy(3)</th></tr>
    <tr class="hl"><td>깜빡 복셀(30 % 미만 프레임에만 찍힘, 유령 후보)</td><td class="n">108 · 95</td><td class="n">2</td></tr>
    <tr><td>앞 1.17 m 상자의 안정 복셀</td><td class="n">11 · 11</td><td class="n">4</td></tr>
    <tr><td>깊이 채움률</td><td class="n">0.317 · 0.317</td><td class="n">0.045</td></tr>
    <tr><td>바닥 점</td><td class="n">1116 · 1114</td><td class="n">85</td></tr>
  </table></div>
  <figure><img src="%%pr1%%" alt="IR 과 두 프리셋의 깊이 영상"><figcaption>왼쪽부터 IR(장면), 프리셋 0 깊이, 프리셋 3 깊이. 3 에서는 바닥 · 벽 · 의자 다리가 거의 사라지고 상자 앞면만 남습니다. 깊이는 가까울수록 밝게, 검정 = 깊이 없음.</figcaption></figure>
  <figure style="max-width:520px"><img src="%%top%%" alt="위에서 본 띠 복셀"><figcaption>위에서 본 띠 복셀(로버는 아래 가운데, 회색 호 = 1.4 m). 주황 = 깜빡, 노랑 = 중간, 초록 = 안정. 줄어든 깜빡 복셀 일부는 오른쪽 문틀 같은 실제 구조였을 수 있어 98 % 감소는 상한입니다.</figcaption></figure>
</section>

<section>
  <h2>바로잡은 내 오류 — 본 것 → 추론 → 결론 → 알아보는 법<span class="sec">§10 · §15 · §17.1 · §18.2 · §19.3</span></h2>
  <p class="note">같은 실수를 다시 했을 때 같은 순서로 따져 볼 수 있게 적습니다. 기전을 모르는 자리는 미확인으로 둡니다.</p>

  <div class="pm">
    <h3>'프로젝터 켬에서도 유령이 생긴다' <span class="pill">§14 → §15</span></h3>
    <div class="flow">
      <span class="k">하려 한 것</span><span>켬/끔 주행을 같은 영역(x 1.45~3.2 · y −0.55~0.6) · 주행 시각 세 점에서 비교.</span>
      <span class="k">본 것</span><span>켬 0~19 칸, 끔 6~40 칸 → "켬에서도 생기고 끔에서 약간 많다" 고 씀.</span>
      <span class="k">의심한 이유</span><span>사용자 직접 관찰("nvblox 만 쓸 때는 안 나왔다")과 맞지 않음. 다시 보니 창 오른쪽 끝 열이 x 2.75 벽 가장자리를 포함했고, 시각 세 점은 잠깐 생겼다 사라지는 칸을 놓침.</span>
      <span class="k">판별</span><span><span class="mono">anal_zone_ghosts.py</span>: t 10~60 s 전체에서 한 번이라도 LETHAL 이 된 칸을 위치 목록으로. 켬 주행의 칸은 거의 다 벽 옆 열, 맨바닥은 0~3.</span>
      <span class="k">결론</span><span>사용자가 맞음. 상자 너머 맨바닥 · 문 사이 점은 프로젝터를 끈 뒤에만 생김.</span>
      <span class="k">데이터</span><span>결과 <span class="mono">outputs/anal_zone_ghosts.txt</span>(처음 수치 <span class="mono">outputs/anal_phantom_local_cmp.txt</span>) · 도구 <span class="mono">jobs/anal_zone_ghosts.py</span> · 입력 <span class="mono">bags/bag_f2u1 · f2u3 · f2v4 · f2w1 · f2x1.tgz</span>(켬), <span class="mono">bag_f2z1 · f2z2 · f2sm1 · f2sm2.tgz</span>(끔) 의 /local_costmap/costmap · /map · /scan · /tf.</span>
      <span class="k">알아보는 법</span><span>켬/끔 같은 비교 창에 벽 · 상자 가장자리를 넣지 않는다. 칸 수가 아니라 위치 목록을 보고, 시각 몇 점이 아니라 구간 전체로 센다. 사용자 관찰과 어긋나면 내 창 설정부터 의심.</span>
    </div>
  </div>

  <div class="pm">
    <h3>노출을 늘리면 특징이 5 배 늘었다 <span class="pill">§19.3</span></h3>
    <div class="flow">
      <span class="k">하려 한 것</span><span>번갈이 중 노출 · 게인을 기동 파라미터로 고정하고 끈 IR 의 FAST 특징 수를 상시 끔 대조와 비교.</span>
      <span class="k">본 것</span><span>32 ms × 248: 밝기 47.6(대조 46.0), FAST20 233(대조 46).</span>
      <span class="k">처음 추론</span><span>대조보다 특징이 많은 좋은 결과.</span>
      <span class="k">의심한 이유</span><span>노출 · 게인 · 밝기가 대조와 같은데 특징만 5 배 — 장면이 안 바뀌었으니 늘 이유가 없음.</span>
      <span class="k">판별</span><span>저장한 끈 IR 프레임을 직접 봄 → 아래 바닥에 프로젝터 점무늬. 흰 점 수(아래 1/4): 24 ms 0 · 28 ms 74 · 32 ms 209~221 · 대조 0.</span>
      <span class="k">결론</span><span>노출이 프레임 주기(33.3 ms)에 가까워지면 켠 구간 빛이 섞임(기전 추정 · 미확인). 늘어난 특징은 카메라에 붙은 가짜.</span>
      <span class="k">데이터</span><span>지표 <span class="mono">outputs/run_mx2.txt</span>(메타 노출 · 게인, 밝기 · FAST) · 흰 점 수 <span class="mono">outputs/anal_mx2_leak.txt</span>(도구 <span class="mono">jobs/anal_mx2_leak.py</span>) · 판별에 본 프레임 <span class="mono">figures/mx2/C32k248_IR_m1.png</span> 등. 라이브 측정이라 bag 없음, 드라이버 로그는 Jetson <span class="mono">/tmp/mx2_*.log</span>(휘발).</span>
      <span class="k">알아보는 법</span><span>끈 IR 특징 수가 같은 노출의 대조보다 크면 먼저 프레임을 본다. 새어 듦은 가까운 바닥부터 나타난다.</span>
    </div>
  </div>

  <div class="pm">
    <h3>시험 컨테이너 첫 실행 무효 <span class="pill">§17.1 · §18.2</span></h3>
    <div class="flow">
      <span class="k">본 것</span><span>① <span class="mono">unable to find user admin</span> ② colcon 이 분리 노드를 못 찾음 ③ 새 이미지에 nvblox · cuVSLAM 없음 ④ cuVSLAM 'Invalid argument' + CUDA 메모리 풀 오류 ⑤ 원시 토픽까지 0 Hz.</span>
      <span class="k">처음 추론</span><span>옛 컨테이너와 '같은 옵션' 이면 같게 동작하고, 같은 판 패키지는 이미지에 들어 있다.</span>
      <span class="k">판별</span><span>① 옛 컨테이너는 실행 때 엔트리포인트로 사용자를 만듦 ② NVIDIA 배포본에 <span class="mono">COLCON_IGNORE</span> ③ <span class="mono">docker diff</span> — nvblox · cuVSLAM 은 옛 컨테이너 쓰기 층에 apt 로 설치된 것 ④ 실질 차이는 내가 넣은 <span class="mono">-v /dev:/dev</span> 하나, 빼니 정상 ⑤ <span class="mono">ros2 topic list</span> — 4.51.1 은 토픽에 노드 이름을 안 붙임.</span>
      <span class="k">결론</span><span>모두 내 설정 실수. 지금 운용 컨테이너는 이미지만으로 재현되지 않는다. /dev 마운트가 CUDA 를 막는 기전은 미확인.</span>
      <span class="k">데이터</span><span>① <span class="mono">outputs/up_rs_splitter_try1.txt</span> ② <span class="mono">chk_rs_ws.txt</span> ③ <span class="mono">chk_rs_ws2.txt</span> · <span class="mono">chk_rs_apt_sim.txt</span>(①~③ 은 원문 파일을 안 남겨 대화 기록에서 옮김) ④ <span class="mono">chk_nv_log.txt</span> · <span class="mono">chk_nv_cmp.txt</span> · <span class="mono">chk_nv_probe.txt</span> ⑤ <span class="mono">run_nv_static_try1.txt</span> · <span class="mono">chk_nv_probe.txt</span>(토픽 목록). 모두 <span class="mono">outputs/</span>.</span>
      <span class="k">알아보는 법</span><span>컨테이너를 다시 만들 땐 엔트리포인트까지 옮기고 <span class="mono">docker diff</span> 로 손 설치를 먼저 센다. GPU 노드가 'Invalid argument' 면 NitrosContext CUDA 오류부터. 드라이버 판을 바꾸면 기동 직후 토픽 이름부터 확인.</span>
    </div>
  </div>

  <div class="pm">
    <h3>그 밖의 정정(짧게)</h3>
    <div class="flow">
      <span class="k">§10</span><span><b>본 것</b> 막힘 분석 도구가 늘 'LETHAL 0' 인데 nav2 는 '비용 99' 를 말함 → <b>판별</b> 코스트맵 메시지 값은 0~100(100 = LETHAL)인데 ≥ 253 으로 셈 → <b>알아보기</b> 메시지 값 범위를 먼저 확인. <b>데이터</b> <span class="mono">outputs/anal_goal_block_f2sm2.txt</span> · <span class="mono">chk_abort_f2sm2.txt</span>, 입력 <span class="mono">bags/bag_f2sm2.tgz</span>.</span>
      <span class="k">§11.3 → §12.2</span><span><b>본 것</b> 1 s 해상도 사건 표에서 멈칫 4 번을 '새 경로 전달' 로 분류 → <b>판별</b> 0.01 s 로 맞추니 <span class="mono">Control loop missed</span> 와 0.01~0.09 s 안 → <b>알아보기</b> 멈칫은 0.01 s 시각으로, 주기 경고를 걸러내지 않는다. <b>데이터</b> <span class="mono">outputs/nav_events_ms.txt</span> · <span class="mono">anal_dip_events_f2sm2h.txt</span>, 입력 <span class="mono">bags/bag_f2sm2h.tgz</span>; 원천 nav2 로그(Jetson <span class="mono">/tmp/nav2.log</span>)는 그 뒤 prep 이 덮어 소실.</span>
    </div>
  </div>
</section>

<section>
  <h2>추론별 데이터 위치<span class="sec">§23</span></h2>
  <p class="note">경로는 모두 <span class="mono">Docs/debug_log/2026-10-21/</span> 아래. bag 은 git 에서 빠지는 <span class="mono">bags/</span> 에 로컬 보관(오늘 스크래치패드에서 옮김). 라이브 정지 시험(nv1 · mx · pr1)은 bag 없이 실시간으로 셌습니다 — 다른 지표로 다시 세려면 다음부터 짧은 bag 을 남깁니다.</p>
  <div class="tbl"><table>
    <tr><th>추론</th><th>결과 원문</th><th>입력 원천</th></tr>
    <tr><td>f2sm1 그림자 효과 §7</td><td class="mono">outputs/run_f2sm1.txt · anal_shadow_f2sm1.txt · gaps_f2sm1.txt</td><td class="mono">bags/bag_f2sm1.tgz</td></tr>
    <tr><td>W3 중단 · 사람 기억 §10 · §12.1</td><td class="mono">outputs/anal_goal_block_f2sm2.txt · chk_abort_f2sm2.txt · nav_events_ms.txt</td><td class="mono">bags/bag_f2sm2.tgz · nav2 로그(소실)</td></tr>
    <tr><td>복귀 멈칫 §11.3 · §12.2</td><td class="mono">outputs/anal_stops_f2sm2h.txt · anal_dip_events_f2sm2h.txt · chk_tf_extrap.txt</td><td class="mono">bags/bag_f2sm2h.tgz · nav2 로그(소실)</td></tr>
    <tr><td>유령 칸 출처 §13</td><td class="mono">outputs/anal_phantom_*.txt · anal_birth_vs_slice.txt · anal_cells_shift_xcorr_f2sm1.txt</td><td class="mono">bags/bag_f2sm1 · f2sm2h · f2u1 …</td></tr>
    <tr><td>켬/끔 맨바닥 §15</td><td class="mono">outputs/anal_zone_ghosts.txt</td><td class="mono">bags/bag_f2u1 … f2sm2 (9 개)</td></tr>
    <tr><td>시험 컨테이너 §17.1 · §18.2</td><td class="mono">outputs/up_rs_*.txt · chk_rs_*.txt · chk_nv_*.txt · run_nv_static_try1.txt</td><td>그 시점 Jetson 상태(docker inspect · diff · dpkg)</td></tr>
    <tr><td>NVIDIA 구성 §18.1</td><td class="mono">outputs/run_nv_static.txt</td><td>라이브 토픽 · Jetson /tmp/nv_static_*.log(휘발)</td></tr>
    <tr><td>노출 고정 §19</td><td class="mono">outputs/run_mx1.txt · run_mx2.txt · anal_mx2_leak.txt</td><td class="mono">figures/mx2/*.png · Jetson /tmp/mx2_*.log(휘발)</td></tr>
    <tr><td>깊이 프리셋 §21</td><td class="mono">outputs/run_pr1.txt</td><td class="mono">figures/pr1/*.npz · *.png · Jetson /tmp/pr1_cam_*.log(휘발)</td></tr>
  </table></div>
</section>

<section>
  <h2>다음</h2>
  <div class="flow">
    <span class="k">1</span><span>f2pr1 주행(§21.2 선언 그대로, "시작" 뒤): 프리셋 3 에서 맨바닥 유령 ≤ 10 칸 · 문 사이 ≤ 2 · 출발점 낮은 상자 ≥ 8 칸</span>
    <span class="k">2</span><span>대응 2: nvblox <span class="mono">esdf_integrator_min_weight</span> 0.1 → 1~2 — 주행 bag 재생으로 A/B</span>
    <span class="k">3</span><span>미뤄 둔 것: f2sm3 · f2sm4 그림자 반복, 사람 기억이 목표 칸을 막는 문제, 복귀 중 멈칫(TF 외삽 · 제어 주기), prep 위치 추정 첫 불합격 원인</span>
    <span class="k">4</span><span>Jetson 정리(사용자 결정): 시험 컨테이너 <span class="mono">isaac_rs_test</span> · 이미지 <span class="mono">isaac_ros_dev-aarch64-rs</span></span>
  </div>
  <p class="note">스택은 운용 구성(프로젝터 상시 끔 · cuVSLAM 그림자 · 공유메모리, 프리셋 지정 안 함)으로 떠 있고 로버는 출발점에 정지해 있습니다. Jetson 은 172.30.1.8(ALOPS). 기록은 커밋했고 push 는 하지 않았습니다.</p>
</section>
</div>
'''
for k, p in [('shadow', 'shadow_f2sm1.png'), ('block', 'f2sm2_frame_67.png'), ('stops', 'stops_f2sm2h.png'), ('phantom', 'phantom_f2sm2h.png'),
             ('mxA', 'mx2/A24k248_IR_m1.png'), ('mxC', 'mx2/C32k248_IR_m1.png'), ('pr1', 'pr1/pr1_imgs.png'), ('top', 'pr1/pr1_top.png')]:
    page = page.replace('%%' + k + '%%', img(p))
open(OUT, 'w', encoding='utf8').write(page)
print(len(page))
