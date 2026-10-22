# 10-22 하루 정리 페이지 생성기 — 본문 수치는 SUMMARY.md §0~§21 에서 옮김, 그림은 figures/ 의 PNG 를 그대로 넣음
#   스타일(CSS)은 10-21 생성기(2026-10-21/jobs/fig_day_summary_1021.py)의 <style> 을 그대로 읽어 씀 — 두 날 페이지가 같은 모양
#   사용: python fig_day_summary_1022.py <figures 폴더> <10-21 생성기 경로> <출력 html>
import base64, sys, re
F, OLD, OUT = sys.argv[1:4]
img = lambda p: 'data:image/png;base64,' + base64.b64encode(open('%s/%s' % (F, p), 'rb').read()).decode()
css = re.search(r'<style>.*?</style>', open(OLD, encoding='utf-8').read(), re.S).group(0)

page = '''<title>10-22 깊이 프리셋 결정</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
%%css%%
<div class="wrap">
<header>
  <p class="eyebrow">Indoor Rover · 2026-10-22 · Docs/debug_log/2026-10-22 §0–§21</p>
  <h1>10-22 깊이 프리셋 결정</h1>
  <p class="lead">어제 고른 유령 칸 대책(깊이 프리셋 3)을 주행으로 확인하고, nvblox 설정 대안과 견줬습니다. 프리셋 없이 달리면 맨바닥 유령이 출구를 막아 주행이 끊겼고, 프리셋 3 만 쓰면 복귀 때 낮은 상자를 못 봐서 쳤습니다. 둘을 함께 막는 구성으로 <b>깊이 프리셋 3 + nvblox 통합 거리 2.0 m</b> 를 골랐고, 검증 주행 두 번(f2pi1 · f2sm3)이 3/3 이었습니다. 상자 옆을 1~2 cm 로 붙어 지나는 이유는 nvblox 기억이 오도메트리 오차만큼 틀어지는 것으로 좁혔습니다.</p>
</header>

<section>
  <h2>오늘의 판정</h2>
  <div class="verdicts">
    <div class="v no"><b>프리셋 없음: 유령이 출구를 막아 주행 중단</b><span>f2dr1 목표 1 에서 29 s 만에 계획 실패. 그 자리엔 아무것도 없었음(사용자). 깊이 기록 탓은 아님 (§6 · §7)</span></div>
    <div class="v no"><b>nvblox 최소 가중치 1 · 2 기각</b><span>2.0 에서 맨바닥 유령 −74 % 지만 상자 칸도 −31 % — 같이 줄어듦 (§9)</span></div>
    <div class="v ok"><b>결정: 깊이 프리셋 3 기본값</b><span>camera.launch depth_preset 기본 −1 → 3, Jetson 배포 · visual_preset 3 확인 (§10)</span></div>
    <div class="v no"><b>프리셋 3 + 1.4 m: 복귀 때 상자를 못 보고 접촉</b><span>f2lp1 1 바퀴 복귀 t 194 s, 세 지도 모두 상자 0 칸. 상자 쪽 화소가 거의 전부 깊이 0 (§13)</span></div>
    <div class="v no"><b>중간 프리셋 5 정지 시험 불합격</b><span>깜빡 77 → 11 은 통과, 상자 안정 복셀 5 &lt; 8 (§14.1)</span></div>
    <div class="v ok"><b>결정: nvblox 통합 거리 1.4 → 2.0 m</b><span>f2lp1 재생에서 복귀 상자 0 → 9 칸(접촉 37 s 전부터), 유령 A 0 → 2 (§14.2 · §15)</span></div>
    <div class="v ok"><b>검증 f2pi1 3/3</b><span>복귀 상자 칸 t 160 s 부터, 유령 A 4. 단 실제 여유 최소 1.1 cm — 지도는 5.6 cm 로 봄 (§16 · §17)</span></div>
    <div class="v ok"><b>그림자 cuVSLAM f2sm3 판정 전부 통과</b><span>W3 회전 최대 창 30.7 → 18.0 cm(−41 %). f2sm1 −33 % 에 이어 두 번째 (§20)</span></div>
    <div class="v wait"><b>nav_guard CPU 24.8 → 19.5 %</b><span>피드백 기록 거르기를 줄였지만 목표 5 % 미달, 주원인 미확인 (§18 · §20)</span></div>
    <div class="v wait"><b>짧은 멈칫은 그대로</b><span>TF 외삽 중단 5 · 제어 주기 늦음 5 · 목표 바뀜 4. 0.5 s 넘는 정지는 0~1 번, CPU 75~76 % (§16 · §20)</span></div>
  </div>
</section>

<section>
  <h2>오늘 주행<span class="sec">§2 · §5 · §8 · §12 · §15 · §19</span></h2>
  <div class="tbl"><table>
    <tr><th>주행</th><th>깊이 프리셋 · 통합 거리</th><th>결과</th><th>무엇을 봤나</th></tr>
    <tr><td>f2pr1</td><td>3 · 1.4 m</td><td class="n">3/3</td><td>유령 A 0 · 출발 상자 7 칸(기준 8 미달) · 복귀 상자 1~2 칸</td></tr>
    <tr class="hl"><td>f2dr1</td><td>없음 · 1.4 m</td><td class="n">1 ABORTED</td><td>유령 칸이 목표 1 출구를 막아 29 s 에 계획 실패</td></tr>
    <tr><td>f2dr2</td><td>없음 · 1.4 m</td><td class="n">3/3</td><td>깊이 영상 3208 장 기록(재생 A/B 입력) · 유령 A 72</td></tr>
    <tr class="hl"><td>f2lp1</td><td>3 · 1.4 m</td><td class="n">사용자 정지</td><td>1 바퀴 복귀에 상자 접촉 → 2 바퀴째 상자가 밀려 바퀴 비교 무효</td></tr>
    <tr><td>f2pi1</td><td>3 · 2.0 m</td><td class="n">3/3</td><td>복귀 상자 칸 있음 · 유령 A 4 · 상자 옆 여유 1.1 cm</td></tr>
    <tr><td>f2sm3</td><td>3 · 2.0 m</td><td class="n">3/3</td><td>그림자 cuVSLAM W3 −41 % · nav_guard 19.5 % · 상자 옆 정지 1.1 s</td></tr>
  </table></div>
  <p class="note">모든 주행: 프로젝터 상시 끔 · 그림자 cuVSLAM · 공유메모리, 코스 b910(출발 → B → W3 → 출발). 판정 기준은 주행 전에 SUMMARY 에 적어 둠.</p>
</section>

<section>
  <h2>프리셋 없이 달리면 유령이 길을 막는다<span class="sec">§6 · §7</span></h2>
  <div class="pm"><div class="flow">
    <div class="k">본 것</div><div>f2dr1 이 상자 북쪽 (0.73, 0.24) 에서 멈추고 13:50:45 부터 매초 'failed to create plan'. 전역 코스트맵에서 지나갈 수 있는 칸만 밟아 목표 1 까지 닿는지 보면 t 20 s 까지 닿다가 22 s 부터 끊김 — 문 칸은 끝까지 열려 있음.</div>
    <div class="k">추론</div><div>막은 칸 111 개는 저장 지도에도 라이다에도 없고 nvblox(카메라)만 본 칸. 사용자 확인으로 그 자리엔 아무것도 없었음 → 유령. 같은 구성의 f2sm1 은 유령 50 칸에도 3/3 — 수가 아니라 놓인 자리(출구 줄)가 갈랐음.</div>
    <div class="k">기록 탓?</div><div>깊이를 기록하지 않은 f2sm1 이 유령이 더 많았음(북쪽 155 · 맨바닥 49 vs 110 · 21). 조각 주기 −4~6 %, 지연 분포는 같음 → 기록이 만든 것은 아님.</div>
    <div class="k">데이터</div><div class="mono">outputs/anal_door_pass_f2dr1.txt · anal_phantom_f2dr1_abort.txt · anal_rec_effect.txt · anal_zone_ghosts_*_0to42.txt · bags/bag_f2dr1.tgz</div>
  </div></div>
  <figure><img src="%%abort%%" alt="f2dr1 중단 순간 전역 코스트맵 칸의 근거"><figcaption>f2dr1 t 40 s: 빨강 = 지도 · 라이다 근거 없이 카메라만 본 칸. 로버(주황 사각) 동쪽 출구에 흩어져 전역 팽창(0.70 m)과 겹침.</figcaption></figure>
</section>

<section>
  <h2>nvblox 최소 가중치 — 유령과 상자가 같이 준다<span class="sec">§8 · §9</span></h2>
  <p>깊이 영상을 담은 f2dr2 를 컨테이너 nvblox 에 다시 넣어 설정만 바꿔 비교했습니다. 같은 설정 재생은 실시간과 같았습니다(R0).</p>
  <div class="tbl"><table>
    <tr><th>f2dr2 입력</th><th>맨바닥 유령</th><th>상자 칸 중앙</th><th>판정(유령 ≤ 30 % · 상자 ≥ 80 %)</th></tr>
    <tr><td>재생 0.1(기준)</td><td class="n">102</td><td class="n">13</td><td>—</td></tr>
    <tr><td>재생 1.0</td><td class="n">53 (52 %)</td><td class="n">11 (85 %)</td><td>✘</td></tr>
    <tr class="hl"><td>재생 2.0</td><td class="n">27 (26 %)</td><td class="n">9 (69 %)</td><td>✘</td></tr>
    <tr><td>참고: 프리셋 3 실시간(f2pr1)</td><td class="n">0</td><td class="n">7</td><td>다른 주행</td></tr>
  </table></div>
  <figure><img src="%%cells%%" alt="상자 둘레 nvblox 칸 비교"><figcaption>열 = 프리셋 없음 · 최소 가중치 2 재생(같은 입력) · 프리셋 3. 행 = 출발 · 출발 길(유령 구간) · 복귀. 색 = 그 시간 동안 장애물이었던 비율(초록 ≥ 80 % · 노랑 30~80 % · 주황 &lt; 30 %). 흰 테두리 = 실제 상자, 점선 = 맨바닥 영역.</figcaption></figure>
</section>

<section>
  <h2>상자 밖 칸은 상자 기억이 밀린 것<span class="sec">§11 ~ §11.4</span></h2>
  <div class="pm"><div class="flow">
    <div class="k">본 것</div><div>f2pr1 복귀 때 상자 북쪽 바깥 칸 (1.20, 0.00) 이 191.0 s, (1.20, 0.05) 쪽이 201.2 s 에 켜짐. 그 직전 172 s 에 문 쪽에서 상자를 봄.</div>
    <div class="k">추론</div><div>nvblox 는 odom 좌표로 기억하고 로버도 odom(EKF) 자세로 움직임. 172 s 기억을 map→odom 만 바꿔 옮기면 상자 중심이 190 s 에 북 +4.2 cm, 201.5 s 에 +5.0 cm — 켜진 시각과 맞음. SLAM 이 로버 쪽만 바로잡고 기억은 그대로라 차이가 드러난 것.</div>
    <div class="k">안 지워진 이유</div><div>복귀 때 그 방향 화소의 83~93 % 가 깊이 0(f2dr2 원시 깊이) — 다시 '본' 것이 아님. 칸을 지나 뒤에 닿는 광선(비울 재료)이 1.4 m 안에서 0 개 → 감쇠(약 78 s)로만 사라짐. site 거리 · 통합 거리 재생으로도 그대로.</div>
    <div class="k">주행 길이</div><div>오차는 '기억이 살아 있는 동안' 의 EKF 오차. 30 s 창 상위 5 % 가 23~34 cm, 뒤 절반이 큼 — 시간 탓인지 W3 회전 탓인지는 아직 못 가름.</div>
    <div class="k">데이터</div><div class="mono">outputs/anal_box_outside_f2pr1.txt · anal_memory_shift_f2pr1*.txt · anal_cell_timeline_*.txt · anal_carve_f2dr2_lowz.txt · anal_mo_window.txt</div>
  </div></div>
</section>

<section>
  <h2>f2lp1 접촉 — 프리셋 3 이 상자를 놓친 순간<span class="sec">§12 · §13 · §13.1</span></h2>
  <div class="pm"><div class="flow">
    <div class="k">본 것</div><div>차체가 상자와 겹친 첫 구간 15:48:14~24(1 바퀴 복귀). 그때 로컬 · 전역 · nvblox 모두 상자 0 칸, nav2 로그에도 막힘 · 복구 없음.</div>
    <div class="k">왜 못 봤나</div><div>출발 기억은 t ≈ 100 s 에 감쇠. 복귀 때 1.46~1.67 m 에서 정면으로 본 점 44 개는 통합 거리 1.4 m 밖이라 버려짐, 1.4 m 안에선 문 쪽으로 꺾는 중이라 시야 밖, 0.72 m 에서 시야에 들 때 상자 쪽 화소 100 % 깊이 0.</div>
    <div class="k">접근 각도</div><div>같은 프리셋 3 의 f2pr1 은 2.5 s 늦게 꺾어 상자가 정면(+10°) · 1.66 m 일 때 1 칸을 얻어 비켜 감 — 사용자 판단(접근 각도)과 맞음. 다만 프리셋 없음은 같은 각에서도 3~5 칸 → 프리셋 3 이 보이는 창을 좁힌 것.</div>
    <div class="k">데이터</div><div class="mono">outputs/anal_contact_f2lp1.txt · anal_box_maps_series_f2lp1.txt · anal_carve_f2lp1_approach.txt · anal_approach_cmp.txt</div>
  </div></div>
</section>

<section>
  <h2>중간 프리셋과 통합 거리 2.0 m<span class="sec">§14 · §15</span></h2>
  <div class="duo">
    <figure><img src="%%pr2%%" alt="정지 시험 프리셋 0 · 3 · 5"><figcaption>정지 시험(출발 자세, 상자 정면 1.2 m, 20 s): 프리셋 5 는 깜빡 복셀 11(P0 77)로 줄지만 상자 안정 복셀 5 — 기준 8 미달.</figcaption></figure>
    <div class="tbl" style="margin:0"><table>
      <tr><th>f2lp1 입력(프리셋 3)</th><th>유령 A</th><th>복귀 상자 칸</th></tr>
      <tr><td>실시간 1.4 m</td><td class="n">0</td><td class="n">0</td></tr>
      <tr><td>재생 1.4 m (R0)</td><td class="n">0</td><td class="n">0</td></tr>
      <tr class="hl"><td>재생 2.0 m</td><td class="n">2</td><td class="n">9</td></tr>
    </table></div>
  </div>
  <p>2.0 m 에선 상자 칸이 t 156.6 s(상자 2.2 m, 방위 −17~−23°)부터 생겨 접촉 시각보다 약 37 s 앞섰습니다. 1.4 m 로 줄였던 이유(먼 바닥 유령)는 프리셋 3 이 대부분 막아 줌. 남은 우려: 멀리서 처음 본 면이 두껍게 찍힘(10-14).</p>
</section>

<section>
  <h2>검증 f2pi1 — 상자를 봤지만 1.1 cm 로 지나감<span class="sec">§16 · §17</span></h2>
  <figure><img src="%%ret%%" alt="f2pi1 복귀 상자 옆 영상의 한 장면"><figcaption>영상 videos/f2pi1_return_box.mp4 의 한 장면. 왼쪽 = 로컬 코스트맵(MPPI 가 보는 값) · 자홍 = nvblox 칸 · 검정 사각 = 실제 상자, 오른쪽 위 = 그 순간 깊이 영상, 오른쪽 아래 = 실제 여유(검정) · 지도 여유(빨강) · 전진 명령.</figcaption></figure>
  <div class="pm"><div class="flow">
    <div class="k">본 것</div><div>실제 여유 최소 1.1 cm @ t 210.2 s, 그 순간 로컬 코스트맵 치명 칸까지 5.6 cm. 상자는 차체 옆이라 시야 밖, 지도의 상자 칸은 실제 북쪽 면보다 약 3 cm 남쪽.</div>
    <div class="k">결론</div><div>MPPI 는 4.5 cm 더 있다고 보고 지나감 = 기억 오차(이번엔 로버 반대쪽) + 칸 판정 반올림. 근본 대책은 오도메트리(기억이 덜 틀어지게).</div>
    <div class="k">멈칫 14 번</div><div>TF 외삽으로 컨트롤러 중단 5(0.05~0.3 s) · 제어 주기 늦음 → velocity_smoother 0.3 s 시간 제한 5(0~0.1 s) · 목표 바뀜 4. CPU 평균 76 %.</div>
    <div class="k">데이터</div><div class="mono">outputs/anal_contact_f2pi1.txt · anal_cell_timeline_f2pi1.txt · anal_dip_events_f2pi1.txt · nav_events_ms_f2pi1.txt · anal_cpu_f2pi1_cmp.txt</div>
  </div></div>
</section>

<section>
  <h2>그림자 cuVSLAM 반복 · CPU<span class="sec">§18 · §19 · §20</span></h2>
  <div class="tbl"><table>
    <tr><th>그림자 판정</th><th>f2sm3</th><th>f2sm1(10-21)</th></tr>
    <tr class="hl"><td>W3 회전 최대 창</td><td class="n">30.7 → 18.0 cm (−41 %)</td><td class="n">24.1 → 16.1 (−33 %)</td></tr>
    <tr><td>상자 옆 여유 변화</td><td class="n">+1.5 · +0.7 cm</td><td class="n">+0.9 · +0.6</td></tr>
    <tr><td>/vslam/odom · 끊김 · 버림</td><td class="n">14.9 Hz · 0 · 0</td><td class="n">15.0 · 2 · 0</td></tr>
    <tr><td>CPU</td><td class="n">75 %</td><td class="n">75.7 %</td></tr>
  </table></div>
  <figure><img src="%%shadow%%" alt="f2sm3 주 EKF 와 그림자 EKF"><figcaption>f2sm3: 주 EKF 와 그림자 EKF(+ cuVSLAM 이동 속도)의 SLAM 대비 오차. 한 번 더(f2sm4) 통과하면 주 EKF 에 넣는 시험으로.</figcaption></figure>
  <p>CPU 를 프로세스별로 나누면 Nav2 ≈ 100 %, 측정 · 러너 ≈ 60 %, 그림자 · rf2o ≈ 53 %, nav_guard 24.8 %(한 코어 = 100 %). nav_guard 는 목표 피드백마다 45 s 위치 기록 전체를 다시 걸러서, 기록을 0.2 s 간격으로 줄여 배포했으나 19.5 % 로 목표(5 %)에 못 미쳤습니다. 남은 원인은 미확인입니다.</p>
</section>

<section>
  <h2>바로잡은 내 오류</h2>
  <div class="pm"><h3>'이번엔 평소와 다른 길로 갔다' (§6 → §7)</h3><div class="flow">
    <div class="k">처음 추론</div><div>f2dr1 이 상자 북쪽에서 멈춘 것을 보고 경로가 평소와 달랐을 수 있다고 함.</div>
    <div class="k">의심한 이유</div><div>사용자가 기록 영향을 물어 다른 주행을 같은 도구로 대조.</div>
    <div class="k">판별</div><div>t 22 s 로버 위치 f2sm1 (0.71, 0.21) · f2pr1 (0.61, 0.20) — 같은 길.</div>
    <div class="k">다음에 알아보는 법</div><div>'평소와 다르다' 는 기준 주행을 같은 도구로 함께 돌린 뒤에만 쓴다.</div>
  </div></div>
  <div class="pm"><h3>'복귀 때 칸은 출발 기억' → '새로 본 것' → 둘 다 아님 (§11 → §11.2 → §11.3)</h3><div class="flow">
    <div class="k">처음 추론</div><div>처음 찍힌 시각만 보고 출발 기억이 밀린 것이라 함. 다음엔 시야 판정만 보고 복귀 중 새로 본 것이라 함.</div>
    <div class="k">의심한 이유</div><div>사용자 질문으로 칸의 시간 구간을 보니 출발 기억은 97 s 에 꺼짐. 원시 깊이를 세 보니 그 방향 화소 83~93 % 가 깊이 0.</div>
    <div class="k">결론</div><div>172 s 에 문 쪽에서 본 기억이 SLAM 보정으로 4~5 cm 밀려 칸 경계를 넘은 것.</div>
    <div class="k">다음에 알아보는 법</div><div>칸의 출처는 시간 구간부터, '보였다' 는 시야가 아니라 유효 깊이 화소 수로.</div>
  </div></div>
  <div class="pm"><h3>'전역 코스트맵도 같이 밀린다' (§17)</h3><div class="flow">
    <div class="k">처음 말</div><div>대화에서 계획기(전역, map)도 옮겨진 상자를 본다고 설명.</div>
    <div class="k">의심한 이유</div><div>10-21 §13.2 에서 전역 코스트맵 카메라 칸은 map→odom 변화만큼 움직이지 않았음(가장 잘 겹치는 이동 (0, 0)).</div>
    <div class="k">결론</div><div>오늘 잰 밀림은 nvblox 조각 · 로컬 코스트맵 기준으로만 유효. 전역 층의 갱신 방식은 미확인.</div>
  </div></div>
  <p class="note">그 밖(각 § 안에 기록): 광선 도구가 낮은 상자 위 공간까지 셈 · 광선을 1.0 m 까지만 봄 · 영상 생성기가 매 장 지도와 축을 다시 만들어 40 분 넘게 걸림 · 토픽 이름 환경 변수를 Git Bash 가 경로로 바꿈 · 영상(18 MB)을 git 제외 규약과 달리 커밋했다가 push 전에 뺌.</p>
</section>

<section>
  <h2>다음</h2>
  <div class="tbl"><table>
    <tr><th>순서</th><th>할 일</th><th>왜</th></tr>
    <tr><td class="n">1</td><td>f2sm4 그림자 반복 → 세 번 판정 → <span class="mono">vslam:=on</span> 주행 시험</td><td>상자 옆 기억 오차의 근본 대책(오도메트리)</td></tr>
    <tr><td class="n">2</td><td>상자 옆 여유: 경로가 주황(내접 근처)보다 노랑(낮은 비용) 쪽을 따르게 — 전역 감쇠 2.0 / 3.0 / 4.0 경로 거리 계산부터(사용자 제안, §22)</td><td>10-13 엔 상자 칸이 늦게 떠서 효과를 못 봤으나 지금은 37 s 앞서 보임</td></tr>
    <tr><td class="n">3</td><td>nav_guard 19.5 % · polkitd 15 % · lifecycle_manager 11 % 원인</td><td>CPU 75 % 가 멈칫 A · B 배경으로 의심</td></tr>
    <tr><td class="n">4</td><td>미뤄 둔 것: 사람 기억이 목표 칸을 막음 · prep 첫 불합격(10-21 건) · 시험 컨테이너 정리 · 깊이 해상도(decimation 2)</td><td>—</td></tr>
  </table></div>
</section>
</div>
'''
for k, v in (('css', css), ('abort', img('phantom_f2dr1_abort.png')), ('cells', img('box_cells_preset.png')), ('pr2', img('pr2/pr2_top.png')),
             ('ret', img('f2pi1_return_210.png')), ('shadow', img('shadow_f2sm3.png'))):
    page = page.replace('%%' + k + '%%', v)
open(OUT, 'w', encoding='utf-8').write(page)
print('페이지', OUT, '%.1f MB' % (len(page.encode()) / 1e6))
