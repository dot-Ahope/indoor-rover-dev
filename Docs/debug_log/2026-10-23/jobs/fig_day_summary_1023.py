# 10-23 하루 정리 페이지 생성기 — 본문 수치는 SUMMARY.md §0~§23 · Docs/06_planner/SMAC_HYBRID_PLAN.md §8~§9 에서 옮김, 그림은 figures/ 의 PNG 를 그대로 넣음
#   스타일(CSS)은 10-21 생성기의 <style> 을 그대로 읽어 씀 — 10-21 · 10-22 · 10-23 페이지가 같은 모양
#   사용: python fig_day_summary_1023.py <figures 폴더> <10-21 생성기 경로> <출력 html>
import base64, sys, re
F, OLD, OUT = sys.argv[1:4]
img = lambda p: 'data:image/png;base64,' + base64.b64encode(open('%s/%s' % (F, p), 'rb').read()).decode()
css = re.search(r'<style>.*?</style>', open(OLD, encoding='utf-8').read(), re.S).group(0)

page = '''<title>10-23 상자 옆 여유와 계획기</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
%%css%%
<div class="wrap">
<header>
  <p class="eyebrow">Indoor Rover · 2026-10-23 · Docs/debug_log/2026-10-23 §0–§23 · 주행 9 번</p>
  <h1>10-23 상자 옆 여유와 계획기</h1>
  <p class="lead">복귀 길 상자 옆을 너무 가깝게 지나는 문제를 하루 종일 쫓았습니다. 오도메트리를 cuVSLAM 으로 바꿔 위치 추정은 확실히 좋아졌지만(<b>vslam:=on 기본 채택</b>) 상자 옆 여유는 그대로였고, 원인은 두 가지가 겹친 것으로 좁혀졌습니다: <b>계획 경로 자체가 꺾임 안쪽(상자 쪽)으로 짧게 돎</b> + <b>컨트롤러가 그 경로에서 안쪽을 더 깎음</b>. 주기 재계획을 끄고 막힘 판정을 고쳐 <b>NavFn 결함 기준선(B0)</b> 을 확정했고, Smac Hybrid-A* 를 실제 계획기로 오프라인 비교한 결과는 <b>기준 미달</b>이었습니다. 다음 후보는 차체 모양과 제자리 회전을 함께 다루는 Smac Lattice 입니다.</p>
</header>

<section>
  <h2>오늘의 판정</h2>
  <div class="verdicts">
    <div class="v no"><b>전역 감쇠 2 → 5: 경로 0~5 cm 만 이동</b><span>기준 ≥ 5 cm 미달. 단 시험한 방향은 '더 가파르게' 뿐 (§1.1 · §22.2)</span></div>
    <div class="v wait"><b>MPPI PathAlign 28 채택 보류</b><span>f2pa1 여유 12.3 cm 였으나 f2pa2 6.7 cm · 원인 모를 5.5 s 정지 → 14 로 되돌림 (§5 ~ §8)</span></div>
    <div class="v ok"><b>결정: vslam:=on 기본(오도메트리 = cuVSLAM)</b><span>W3 회전 창 13.2~16.8 cm(이전 21.5~30.7) · 멈칫 5(12~14) · CPU 70 %(75~76) (§10 · §11 · §16)</span></div>
    <div class="v ok"><b>결정: 재계획 = 목표당 1 회 + 막힘 때</b><span>0.5 Hz 재계획이 로버 자리부터 다시 그려 치우침을 쌓던 것을 끊음 (§14 · §17)</span></div>
    <div class="v ok"><b>막힘 판정 only_new</b><span>경로를 받을 때 이미 99 였던 칸은 세지 않음. 재생 시험에서 실제 막힘 9 개 재현(±0.03 s), 서쪽 통로 헛막힘 4 개만 빠짐 (§20.2 · §20.7)</span></div>
    <div class="v ok"><b>B0 = NavFn 결함 기준선 확정</b><span>태그 navfn-baseline-20261023. b910 상자 옆 15.4 · 5.5 · 3.1 cm (§21)</span></div>
    <div class="v no"><b>Smac Hybrid-A* 오프라인: 기준 미달</b><span>상자 여유 −7.1~+3.2 cm(기준 +5), 서쪽 통로 계획 실패 (§22.2)</span></div>
    <div class="v wait"><b>컨트롤러: 굽은 곳 안쪽 깎기</b><span>5 주행 모두 69~91 %, 복귀 상자 쪽 +7~11 cm. 제어 주기는 9.7~9.8 Hz 로 주원인 아님 (§22.3)</span></div>
  </div>
</section>

<section>
  <h2>오늘 주행<span class="sec">§5 · §6 · §10 · §11 · §17 · §18 · §20</span></h2>
  <div class="tbl"><table>
    <tr><th>주행</th><th>코스</th><th>바꾼 것</th><th>결과</th><th>상자 옆 실제 여유</th></tr>
    <tr><td>f2pa1</td><td>b910</td><td>PathAlign 14 → 28</td><td class="n">3/3</td><td class="n">12.3 cm</td></tr>
    <tr class="hl"><td>f2pa2</td><td>b910</td><td>같음(반복)</td><td class="n">3/3 · 5.5 s 정지</td><td class="n">6.7 cm</td></tr>
    <tr><td>f2von1</td><td>b910</td><td>PathAlign 14 · vslam:=on</td><td class="n">3/3</td><td class="n">3.3 cm</td></tr>
    <tr class="hl"><td>f2von2</td><td>b910</td><td>같음(반복)</td><td class="n">3/3</td><td class="n">0.3 cm</td></tr>
    <tr><td>f2rp1</td><td>b910</td><td>재계획 0.5 → 0.01 Hz + 막힘</td><td class="n">3/3</td><td class="n">15.4 cm</td></tr>
    <tr><td>f2rp2</td><td>b910</td><td>같음(반복)</td><td class="n">3/3</td><td class="n">5.5 cm</td></tr>
    <tr class="hl"><td>f2rp3</td><td>no5</td><td>같음, 좁은 통로 코스</td><td class="n">8/8 · 대기 2</td><td class="n">통로 4.0 cm</td></tr>
    <tr><td>f2rp4</td><td>no5</td><td>only_new</td><td class="n">8/8 · 대기 0</td><td class="n">통로 3.7~4.8 cm</td></tr>
    <tr class="hl"><td>f2rp5</td><td>b910</td><td>only_new (B0 확정 주행)</td><td class="n">3/3</td><td class="n">3.1 cm</td></tr>
  </table></div>
  <p class="note">실제 여유 = 차체 ↔ 기록된 상자 위치(x 1.151~1.261, y −0.20~−0.02). 판정 기준은 주행 전에 SUMMARY 에 적어 둠.</p>
</section>

<section>
  <h2>상자 옆이 가까운 두 가지 이유<span class="sec">§14 · §20.9 · §22</span></h2>
  <figure><img src="%%rp5%%" alt="f2rp5 복귀 상자 옆 영상의 한 장면"><figcaption>f2rp5 17:23:07.5 (영상 videos/f2rp5_return_box.mp4). 보라 = 막힘 뒤 다시 그린 경로(상자 내접 띠 바로 위), 청록 = 지나온 길 — 굽은 곳에서 경로 안쪽으로 깎인 뒤 상자 옆에서 차체가 상자 쪽으로 기울어짐. 실제 최소 여유 3.1 cm.</figcaption></figure>
  <div class="pm"><div class="flow">
    <div class="k">본 것</div><div>다시 그린 NavFn 경로의 상자 여유 8.9 cm(f2rp1 13.3 · f2rp2 10.2). 로버는 굽은 곳에서 경로보다 상자 쪽 +9~10 cm, 상자 옆에서 +3~9 cm, 차체 방향은 경로보다 5° 상자 쪽.</div>
    <div class="k">틈의 폭</div><div>상자 북쪽 치명 칸까지 0.70~0.90 m — 가운데로 가면 양옆 18~28 cm 가 남는 자리. 계획기는 9~16 cm 로 지나감.</div>
    <div class="k">추론</div><div>① 계획기는 길이와 비용을 맞바꿔 꺾임 안쪽(상자 쪽)으로 짧게 돎 — NavFn · Smac 공통. ② MPPI 는 굽은 곳에서 안쪽을 깎음(5 주행 69~91 %, 복귀 +7~11 cm, 갈 때는 반대 −4~5 cm).</div>
    <div class="k">결론</div><div>상자를 못 봐서가 아님(계획기는 상자를 보고 경로를 짬 — 사용자 판단과 같음). 경로를 틈 가운데로 미는 비용장 + 컨트롤러 추종 두 쪽을 따로 다뤄야 함.</div>
    <div class="k">데이터</div><div class="mono">outputs/anal_track_dev_f2rp5.txt · anal_contact_f2rp5.txt · anal_plan_series_f2rp5.txt · anal_ctrl_eval.txt · anal_ctrl_rate.txt · plan_offline/anal_box_gap.txt</div>
  </div></div>
</section>

<section>
  <h2>막힘 판정 only_new<span class="sec">§20.1 ~ §20.7</span></h2>
  <p>재계획을 목표당 1 번으로 줄이자, 앞 경로에 비용 99(내접) 칸이 2 초 이어지면 멈추고 다시 그리는 PathBlockedAhead 가 서쪽 통로에서 5 번 헛걸렸습니다. 0.5 Hz 재계획이 2 초마다 그 타이머를 리셋해 가려 왔던 것입니다.</p>
  <div class="tbl"><table>
    <tr><th>주행</th><th>실제 막힘 중단</th><th>예전 판정 재현</th><th>only_new</th><th>남은 것</th></tr>
    <tr><td>f2rp1</td><td class="n">1</td><td class="n">1 (0.02 s)</td><td class="n">1</td><td>상자 — 경로 받고 59 s 뒤 새로 99</td></tr>
    <tr><td>f2rp2</td><td class="n">1</td><td class="n">1 (0.02 s)</td><td class="n">1</td><td>상자</td></tr>
    <tr class="hl"><td>f2rp3</td><td class="n">6</td><td class="n">6 (≤ 0.03 s)</td><td class="n">2</td><td>서쪽 통로 4 개 빠짐(받는 순간 이미 99) · 새 99 1 · 상자 1</td></tr>
    <tr><td>f2rp4</td><td class="n">1</td><td class="n">1 (0.02 s)</td><td class="n">1</td><td>상자</td></tr>
  </table></div>
  <figure><img src="%%rp4%%" alt="f2rp4 서쪽 통로 영상의 한 장면"><figcaption>f2rp4 서쪽 통로(새 영상 도구 Docs/tools/fig_drive_video.py). 확대 판 · 미니맵 · 상태 수치 · 사건 시간줄. 이 주행에선 경로가 99 칸을 지나지 않아 only_new 가 쓰일 일이 없었음 — 그래서 bag 재생으로 따로 시험.</figcaption></figure>
</section>

<section>
  <h2>Smac Hybrid-A* 오프라인 비교<span class="sec">§22.1 · §22.2</span></h2>
  <p>Jetson 의 다른 ROS 도메인에 실제 planner_server 를 띄우고, 기록된 전역 코스트맵을 치명 칸에서 다시 부풀려 넣었습니다(재구성 일치 6 장면 모두 1.0000). 같은 지도 · 출발 · 목표로 NavFn 과 Smac 변형을 불렀습니다. 로버는 움직이지 않았습니다.</p>
  <div class="tbl"><table>
    <tr><th>장면</th><th>NavFn (B0)</th><th>Smac 기본형 6 변형</th><th>Smac 방향 144 칸</th></tr>
    <tr><td>f2rp1 재계획</td><td class="n">13.3</td><td class="n">6.2~13.5</td><td class="n">16.5</td></tr>
    <tr><td>f2rp2 재계획</td><td class="n">8.0</td><td class="n">4.0</td><td class="n">7.0</td></tr>
    <tr><td>f2rp5 재계획</td><td class="n">9.1</td><td class="n">9.6</td><td class="n">11.8</td></tr>
    <tr><td>f2rp5 복귀 전체</td><td class="n">9.0</td><td class="n">6.4</td><td class="n">12.2</td></tr>
    <tr class="hl"><td>서쪽 통로 남 · 북</td><td>성공 · 성공</td><td>실패 · 실패</td><td>실패 · 성공(고리)</td></tr>
  </table></div>
  <p class="note">값 = 경로를 정확히 따를 때 차체 ↔ 상자 여유(cm). 기준(계획 §4): NavFn + 5 cm 이상 · 서쪽 통로 실패 0 · 계획 ≤ 0.5 s(모두 0.001~0.04 s 로 통과).</p>
  <figure><img src="%%cmp%%" alt="f2rp5 복귀 전체 장면의 NavFn 과 Smac 경로"><figcaption>f2rp5 복귀 출발부터(상자 = 빨강). 주황 = NavFn 9.0 cm, 보라 = Smac 144 칸 12.2 cm. 두 경로 모두 상자 북쪽을 꺾임 안쪽으로 붙어 돎.</figcaption></figure>
  <div class="pm"><div class="flow">
    <div class="k">본 것</div><div>기본형은 cost_penalty 1.2 → 3.0 에도 경로가 거의 같음. '해석 확장'(목표까지 곡선을 바로 그어 차체만 안 닿으면 붙임) 길이를 줄이면 설치판 1.1.20 에서 즉시 실패 · 예외(vector::reserve).</div>
    <div class="k">서쪽 통로</div><div>북행 목표 자세는 전역 지도에서 차체가 치명 칸에 걸려 거부. 남행은 로버가 실제로 지난 자세도 2/175 가 치명에 걸리는 경계 통로 — 점 계획(NavFn)은 지나고 차체 계획은 못 이음.</div>
    <div class="k">결론</div><div>지금 설정 · 설치판으로는 Hybrid 로 바꿀 근거 없음(주행 시험으로 안 감). 원칙(직사각 차체 → 차체 계획기)은 맞으나 종류가 문제 — 아래 결정 항목.</div>
    <div class="k">데이터</div><div class="mono">outputs/plan_offline/anal_plan_compare_1~3.txt · run_planoff_1~3.txt · anal_fp_global_west_rp3_g4.txt · chk_smac_ver.txt · figures/plan_offline{,_2,_3}/</div>
  </div></div>
</section>

<section>
  <h2>Smac 계획기 — 결정 전에 볼 것<span class="sec">SMAC_HYBRID_PLAN §8 · §9</span></h2>
  <p>제자리 회전은 됩니다. 좌우를 반대로 돌리는 스키드스티어(우리 트랙 차체 포함)는 4 륜이든 트랙이든 제자리에서 돌 수 있고, 못 하는 것은 조향 바퀴로 도는 자동차형입니다. Hybrid-A* 의 DUBIN 모델은 자동차형 가정이라 우리에겐 불필요한 제약입니다. 다만 트랙은 제자리 회전 때 크게 미끄러집니다(10-02 회전 중 37 cm, 09-28 180° 당 10~27 cm). '할 수 있다' 와 '자주 해도 된다' 는 다릅니다.</p>
  <div class="tbl"><table>
    <tr><th>#</th><th>질문</th><th>왜</th><th>확인 방법 · 상태</th></tr>
    <tr class="hl"><td class="n">D1</td><td>어느 Smac — Hybrid / Lattice(diff) / 2D</td><td>차체 모양 + 스키드스티어엔 Lattice. Hybrid 는 '제자리에서 맞추고 들어가기' 를 못 그림(추정)</td><td>오프라인 도구에 Lattice 추가. 설치판에 diff 원형(5 cm · R 0.5 m) 있음 — 미시험</td></tr>
    <tr><td class="n">D2</td><td>Lattice 원형 회전반경 · 제자리 회전 벌점</td><td>기본 R 0.5 m 는 실내에 큼, 제자리 회전은 미끄러짐</td><td>기본 원형 먼저 → 필요하면 R 0.1~0.2 원형 생성</td></tr>
    <tr><td class="n">D3</td><td>경계 통로 정책</td><td>차체 계획기는 '지도상 겨우 걸리는' 통로를 막힌 길로 봄(로버는 실제로 지나감)</td><td>Smac 실패 → NavFn 한 번 더(BT 대체 경로) · 전역 패딩 0</td></tr>
    <tr><td class="n">D4</td><td>목표 자세 유효성</td><td>러너 자동 yaw 목표가 차체 충돌일 수 있음(서쪽 통로 북행)</td><td>보내기 전 차체 검사 · 가까운 유효 자세로</td></tr>
    <tr class="hl"><td class="n">D5</td><td>상자 쪽으로 붙는 성질</td><td>계획기보다 비용장 몫 — 틈 가운데 18~28 cm 가능, 실제 9~16</td><td>전역 cost_scaling_factor &lt; 2(완만)를 NavFn · Smac 둘 다로 오프라인 — 미시험 방향</td></tr>
    <tr><td class="n">D6</td><td>설치판 한계(Humble 1.1.20)</td><td>해석 확장 제한이 예외를 냄</td><td>판 올리기는 JetPack 7.2 이전 Phase 와 묶어 판단</td></tr>
    <tr><td class="n">D7</td><td>출발 차체 충돌 거부 · 재계획 주기</td><td>상자 옆 3~5 cm 자리에서 다시 그리면 거부 → 중단(09-15)</td><td>대체 경로 · 이어 그리기 후보</td></tr>
    <tr><td class="n">D8</td><td>컨트롤러와의 맞물림</td><td>경로 점 간격 · MPPI 경로 크리틱 offset · 스무더가 바뀜</td><td>컨트롤러 개선은 계획기 결정과 따로 진행 가능</td></tr>
    <tr><td class="n">D9</td><td>채택 기준</td><td>같은 지도 · 출발에서 비교</td><td>상자 옆 +5 cm · 서쪽 통로 실패 0 · 계획 ≤ 0.5 s</td></tr>
  </table></div>
</section>

<section>
  <h2>좁은 곳 방향 바꾸기와 바퀴 방향 부호<span class="sec">§24 · SMAC_HYBRID_PLAN D10</span></h2>
  <div class="tbl"><table>
    <tr><th>계획 모델</th><th>전진</th><th>후진</th><th>제자리 회전</th><th>좁은 곳 방향 바꾸기</th></tr>
    <tr><td>Hybrid DUBIN(지금 설정)</td><td>✔</td><td>✘</td><td>✘</td><td>크게 도는 고리(09-14 4.3 m · 오늘 서쪽 통로 201°)</td></tr>
    <tr><td>Hybrid REEDS_SHEPP</td><td>✔</td><td>✔</td><td>✘</td><td>전진 · 후진 반복(3 점 턴), 후진 · 전환 벌점으로 조절</td></tr>
    <tr class="hl"><td>Lattice 차동구동용</td><td>✔</td><td>설정 시 ✔</td><td>✔</td><td>제자리 회전(회전 벌점으로 조절)</td></tr>
  </table></div>
  <div class="pm"><h3>사용자 제안: 전진 · 후진 원호 반복이 미끄러짐을 줄일 것</h3><div class="flow">
    <div class="k">근거</div><div>스키드스티어는 회전이 급할수록 트랙이 옆으로 끌림 — 제자리(반경 0)가 가장 심함(물리 추정). 10-08 통제 시험 90° 당 중앙값: 제자리 6.2 · 반피벗 6.9 · 피벗(반경 ≈ 0.145 m) 4.0 cm. 반경 큰 쪽이 작았지만 순서 교란 · 변동 66~76 % 로 미확정.</div>
    <div class="k">대가</div><div>방향 바꿀 때마다 정지 · 반전(아래 부호 문제), 후진 중 카메라 시야 밖(라이다 아래 낮은 물체), 시간 증가.</div>
    <div class="k">시험</div><div>같은 자리 · ABAB 교대로 90° 방향 바꾸기: 제자리 / 피벗 / 원호 왕복 R 0.3 · 0.5. 지표 = 스캔 정합 미끄러짐 · EKF−SLAM 차 · 시간. 계획기 쪽은 REEDS_SHEPP · Lattice 경로 모양을 오프라인 도구로.</div>
  </div></div>
  <div class="pm"><h3>FG 펄스에는 방향이 없다 — 명령으로 보정할 수 있나</h3><div class="flow">
    <div class="k">지금</div><div>이미 명령 부호로 보정 중. 0 아닌 duty 를 낼 때 부호를 기록하고(integrated_bldc_driver.c:153), FG 펄스마다 그 부호를 붙임(fg_encoder_driver.c:151 · 170). 감속은 역 duty 제동 대신 동력을 끊고 굴림(speed_controller.c:202).</div>
    <div class="k">약점</div><div>반전 순간: 부호는 명령과 함께 바로 뒤집히지만 바퀴는 관성으로 옛 방향으로 더 돎 → 그 펄스가 반대로 세어짐(그 거리의 2 배 오차). 명령 0 에서 굴러감 · 밀림 · 구속 떨림도 직전 부호로 셈.</div>
    <div class="k">개선안</div><div>멈춘 뒤 방향 바꾸기: 0 명령 → FG 무펄스(예 50 ms) 확인 → 방향 · 부호 전환, 그 사이 펄스는 옛 부호로. 펌웨어에 이미 적어 둔 TODO. 대가는 반전마다 수십 ms 정지.</div>
    <div class="k">먼저 잴 것</div><div>오늘 bag 의 반전 순간(W3 출발 · 탈출 동작)에서 /wheel_odom 과 /vslam/odom 속도 부호가 어긋난 시간 · 거리. 반전당 mm 면 지금 방식으로 충분, cm 면 펌웨어 수정 근거. D10 시험 전에.</div>
  </div></div>
</section>

<section>
  <h2>주말 공부<span class="sec">다음 결정에 바로 쓰이는 것만</span></h2>
  <p>읽은 뒤 답해 볼 질문을 함께 적었습니다. 답이 우리 로그 수치로 확인되면 다음 주 결정(D1 · D2 · D5 · D10 · 컨트롤러)의 근거가 됩니다.</p>
  <div class="tbl"><table>
    <tr><th>주제</th><th>읽을 것</th><th>답해 볼 질문</th></tr>
    <tr class="hl"><td>Smac 계획기 전체</td><td>Macenski 외, "Open-Source, Cost-Aware Kinematically Feasible Planning for Mobile and Surface Robotics"(2024, Nav2 Smac 논문) · Nav2 Smac 문서(Hybrid · Lattice · 파라미터)</td><td>analytic expansion 은 비용을 무시하나? cost_penalty 는 어디에 곱해지나? Lattice 는 제자리 회전 · 후진을 어떻게 벌점 주나?</td></tr>
    <tr><td>Hybrid-A*</td><td>Dolgov 외, "Practical Search Techniques in Path Planning for Autonomous Driving"(2008)</td><td>연속 상태 + 격자 칸 묶음이 좁은 통로에서 길을 못 찾는 이유(서쪽 통로 실패)는?</td></tr>
    <tr><td>Dubins · Reeds-Shepp</td><td>Dubins(1957) · Reeds &amp; Shepp(1990) 최단 경로 — 교과서 요약(LaValle, <i>Planning Algorithms</i> 15 장)이면 충분</td><td>최소 회전반경이 고리 경로를 만드는 조건은? 3 점 턴이 최단이 되는 조건은?</td></tr>
    <tr><td>State Lattice</td><td>Pivtoraiko &amp; Kelly, 차동 제약 로봇의 state lattice 계획(2009 전후) · Nav2 lattice 원형 생성기 README</td><td>우리 R 0.1~0.2 m · 회전 허용 원형을 만들려면 무엇을 정해야 하나?</td></tr>
    <tr class="hl"><td>비용장 · 경로가 안쪽으로 붙는 이유</td><td>Nav2 costmap_2d inflation 비용식(내접 반경 · cost_scaling_factor) · NavFn 의 퍼텐셜 계획(Konolige, gradient method 2000)</td><td>cost_scaling_factor 를 2 → 1 로 낮추면 0.85 m 틈 가운데 비용이 어떻게 변하나? 길이 대 비용의 맞바꿈이 꺾임 안쪽을 택하게 하는 수식은?</td></tr>
    <tr><td>MPPI</td><td>Williams 외, "Information Theoretic MPC for Model-Based Reinforcement Learning"(ICRA 2017) · Nav2 MPPI 크리틱 문서(PathFollow · PathAlign · offset)</td><td>굽은 곳 안쪽 깎기(69~91 %)는 어떤 크리틱 · 지평 · 온도 조합에서 생기나? PathAlign 을 올렸을 때 '0.4 s 뒤 출발' 해가 되풀이된 기전은?</td></tr>
    <tr class="hl"><td>스키드스티어 · 트랙 미끄러짐</td><td>Martínez 외, "Approximating Kinematics for Tracked Mobile Robots"(IJRR 2005, ICR 모델) · Kozłowski &amp; Pazderski, 4 륜 스키드스티어 모델링 · 제어(2004)</td><td>회전 반경에 따라 트랙 미끄러짐(ICR 위치)이 어떻게 바뀌나? 10-08 의 '항상 뒤로 밀림' 을 ICR 이 뒤로 치우친 것으로 설명할 수 있나?</td></tr>
    <tr><td>단상 엔코더 · 반전</td><td>단상(1 채널) 타코 · 홀 신호 방향 추정, brake-before-reverse 모터 제어 자료</td><td>반전 순간 관성으로 도는 거리는 우리 모터(1:90, 542 펄스/회전)에서 얼마쯤일까 — bag 측정과 비교</td></tr>
    <tr><td>EKF · 운동 모델</td><td>Thrun 외, <i>Probabilistic Robotics</i> 5 장(운동 모델) · 7 장(EKF)</td><td>휠 부호가 잠깐 틀릴 때 cuVSLAM 속도가 얼마나 눌러 주나 — 공분산 설정으로 예측해 보고 bag 로 확인</td></tr>
  </table></div>
  <p class="note">문헌 제목 · 연도는 기억에 기댄 것 — 찾을 때 저자명으로 확인하세요. 우선순위는 강조한 세 줄(Smac 논문 · 비용장 · 미끄러짐).</p>
</section>

<section>
  <h2>바로잡은 내 오류</h2>
  <div class="pm"><h3>'막힘 기준 99 → 100 이 가장 단순하다' (§20.1 → §20.2)</h3><div class="flow">
    <div class="k">처음 추론</div><div>상자가 경로를 막으면 경로점이 상자 칸(100)에 들어가니 100 으로 올려도 잡힐 것 — '추정' 으로 적고 확인 안 함.</div>
    <div class="k">의심한 이유</div><div>바꾸기 전에 쓸모 있던 막힘들의 실제 값을 세어 봄.</div>
    <div class="k">판별</div><div>오늘 막힘은 상자 포함 전부 99. 둘을 가르는 것은 값이 아니라 '경로를 받고 몇 초 뒤' — 서쪽 통로 0.02 s, 상자 58~59 s.</div>
    <div class="k">다음에 알아보는 법</div><div>판정 문턱을 바꾸기 전에 그 판정이 쓸모 있게 걸린 사례들의 실제 값을 먼저 셈.</div>
  </div></div>
  <div class="pm"><h3>'f2rp5 상자 여유 기준 > 2.7 cm' (§20.8 → §20.9)</h3><div class="flow">
    <div class="k">본 것</div><div>3.1 cm 로 형식상 통과. 사용자: "상자에 너무 가까웠음".</div>
    <div class="k">결론</div><div>2.7 cm 는 칸 판정 뒤집힘 하한(측정 잡음 수준)이지 안전 여유가 아님. §17 의 '≥ 8 cm' 기준이면 f2rp2 · f2rp5 불합격.</div>
  </div></div>
  <div class="pm"><h3>'Smac 을 쓰면 상자 쪽으로 붙지 않을 것' (§21 대화 → §22.2)</h3><div class="flow">
    <div class="k">처음 말</div><div>차체 충돌 검사 · cost_penalty 로 여유가 커질 것으로 기대(일반 지식, 미측정이라고 함).</div>
    <div class="k">판별</div><div>오프라인 비교에서 −7.1~+3.2 cm. 꺾임 안쪽으로 붙는 성질은 계획기 종류와 무관.</div>
    <div class="k">다음에 알아보는 법</div><div>계획기 성질에 대한 기대는 같은 지도 · 출발로 먼저 재 보고 말함.</div>
  </div></div>
  <p class="note">그 밖(각 § 안에 기록): 재생 도구 0.1 s 간격 · 부동소수 비교로 f2rp4 상자 막힘 놓침 · 서쪽 통로 막힘 4 번을 목표 5 로 잘못 적음 · 영상 도구가 스무딩 실패 원경로를 빠뜨림 · 추종 오차 첫 판이 출발 0.15 m 를 빼 모든 주행 8.8 cm 로 나옴 · 18.1 의 중단 원인을 TF 외삽으로 잘못 적음.</p>
</section>

<section>
  <h2>다음</h2>
  <div class="tbl"><table>
    <tr><th>순서</th><th>할 일</th><th>왜</th></tr>
    <tr><td class="n">1</td><td>D5 — 전역 cost_scaling_factor 1.0 · 0.5 를 NavFn 으로 오프라인(장면 6 개)</td><td>경로를 틈 가운데로 미는 가장 직접적인 손잡이, 미시험 방향</td></tr>
    <tr><td class="n">2</td><td>D1 — Smac Lattice(diff) 를 같은 도구 · 기준으로</td><td>차체 모양 + 제자리 회전에 맞는 종류</td></tr>
    <tr><td class="n">3</td><td>컨트롤러 안쪽 깎기 — MPPI 오프라인 모의로 경로 추종 크리틱 조정</td><td>계획기와 별개로 +7~11 cm 를 잃음</td></tr>
    <tr><td class="n">4</td><td>반전 순간 휠 부호 오차 측정(bag) → D10 원호 왕복 통제 시험</td><td>사용자 제안(미끄러짐 줄이기)의 근거 · 대가 확인</td></tr>
    <tr><td class="n">5</td><td>미해결: TF 외삽 중단 · 제어 주기 늦음 · nav_guard CPU · 상자 기억 밀림(odom)</td><td>—</td></tr>
  </table></div>
</section>
</div>
'''
for k, v in (('css', css), ('rp5', img('f2rp5_return_box_frame.png')), ('rp4', img('f2rp4_west_corridor_frame.png')), ('cmp', img('plan_offline_2/plan_cmp_b910_rp5_full.png'))):
    page = page.replace('%%' + k + '%%', v)
open(OUT, 'w', encoding='utf-8').write(page)
print('페이지', OUT, '%.1f MB' % (len(page.encode()) / 1e6))
