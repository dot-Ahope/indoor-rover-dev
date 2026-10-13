#!/usr/bin/env python3
"""fig_report — 10-13 하루 기록을 한 장짜리 HTML 로 만든다(그림은 data URI 로 넣음). (2026-10-13, PC 에서 실행)
  모양은 10-12 보고서의 <style> 을 그대로 가져와 쓴다(같은 프로젝트의 같은 서식). 수치의 근거는 SUMMARY.md 의 절 번호로 단다.
  사용: fig_report.py (저장소 루트에서) → Docs/debug_log/2026-10-13/2026-10-13_report.html"""
import base64, io
from pathlib import Path
from PIL import Image
ROOT = Path('.'); FIG = ROOT / 'Docs/04_navigation/figures'; OUT = ROOT / 'Docs/debug_log/2026-10-13/2026-10-13_report.html'
prev = (ROOT / 'Docs/debug_log/2026-10-12/2026-10-12_report.html').read_text(encoding='utf-8')
head = prev[:prev.find('</style>') + len('</style>')]
head = head.replace('<title>로버 10-12 주행 기록</title>', '<title>로버 10-13 주행 기록</title>')
i = head.find('<meta name="description"'); j = head.find('>', i)
head = head[:i] + '<meta name="description" content="10-13 실내 로버 통신 포화의 정체 규명, 러너 수정 2 건, 상자 옆 정지 원인 분석과 대책 시험 기록">' + head[j + 1:]


def img(name, maxw=1500):
    im = Image.open(FIG / name).convert('RGB')
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=84, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def table(head_, rows, num=()):
    h = '<div class="tbl"><table><thead><tr>' + ''.join('<th>%s</th>' % c for c in head_) + '</tr></thead><tbody>'
    for r in rows: h += '<tr>' + ''.join('<td%s>%s</td>' % (' class="n"' if k in num else '', c) for k, c in enumerate(r)) + '</tr>'
    return h + '</tbody></table></div>'


P = lambda cls, t: '<span class="pill %s">%s</span>' % (cls, t)
OK, WARN, BAD, NA = (lambda t: P('p-ok', t)), (lambda t: P('p-warn', t)), (lambda t: P('p-bad', t)), (lambda t: P('p-n', t))
body = '''
<div class="wrap">
<header>
  <div class="eyebrow">Indoor Rover · debug_log/2026-10-13 · 원본 feature/nvblox-migration</div>
  <h1>10-13 기록: 통신 포화의 정체와 상자 옆 정지</h1>
  <div class="meta"><span>근거 <b class="mono">SUMMARY.md §0~§15</b></span><span>그림 <b class="mono">Docs/04_navigation/figures/2026-10-13_*</b></span><span>주행 <b>5 회</b></span><span>오프라인 시뮬 <b>280 회</b></span></div>
  <nav class="toc" aria-label="목차">
    <a href="#storm">통신 포화</a><a href="#runner">러너 수정</a><a href="#stall">상자 옆 정지</a><a href="#cause">원인 세 가지</a><a href="#tried">시험한 대책</a><a href="#eval">평가 세 건</a><a href="#fix">정정</a><a href="#next">다음</a>
  </nav>
</header>

<div class="status">
  <div class="st" style="--c:var(--ok)"><span class="k">통신 포화의 정체</span><span class="v">/tf HEARTBEAT 폭주</span><span class="d">bag 기록기가 /tf 를 못 따라가 시작. 기록기 /tf 를 best effort 로 바꿔 해소</span></div>
  <div class="st" style="--c:var(--ok)"><span class="k">목표 전환 때 소켓 손실</span><span class="v">1.2~2.5k /s → 0</span><span class="d">목표마다 띄우던 경로 조회기를 상주시킴</span></div>
  <div class="st" style="--c:var(--bad)"><span class="k">상자 옆 정지</span><span class="v">원인 규명, 미해결</span><span class="d">대책 4 가지를 시험했고 모두 기각 또는 되돌림</span></div>
  <div class="st" style="--c:var(--warn)"><span class="k">이 자리의 여유</span><span class="v">코스트맵 2~5 cm</span><span class="d">주행 9 회 모두. 통과와 정지가 1~2 cm 로 갈림. 실측은 11 cm</span></div>
</div>

<h2 id="storm">통신 포화의 정체 <span class="sec">§1~§3</span></h2>
<p class="prose">10-12 에 주행 중 UDP 통신량이 10 배로 뛰며 Nav2 가 중단되던 현상을, 포화를 일부러 재현하고(f2m1) 루프백 패킷을 캡처해 종류별로 셌습니다. 판정 기준은 주행 전에 적어 두었습니다.</p>
''' + table(['', '평상(4 s)', '포화(20 s)'], [
    ['전체 패킷', '4,794 /s', '56,350 /s (11.8 배)'], ['DATA', '3,745 (77 %)', '8,024 (14 %)'],
    ['HEARTBEAT', '450 (9 %)', '<b>44,739 (79 %)</b>'], ['ACKNACK', '594 (12 %)', '3,588 (6 %)']], num=(1, 2)) + '''
<div class="look">
  <div><h4>측정</h4><ul>
    <li>늘어난 HEARTBEAT 의 거의 전부가 <code>/tf</code> 를 쓰는 두 곳(위치 추정 노드 23.3k /s, EKF 20.8k /s)에서 나왔습니다.</li>
    <li>0.2 초 한 칸 안에 평상에서 폭주로 바뀌었습니다.</li>
    <li>그 순간 <code>/tf</code> 확인이 뒤처진 읽는 쪽은 bag 기록기 하나였습니다(70 → 92 개). 나머지 11 곳은 뒤처짐이 없었습니다.</li>
  </ul></div>
  <div><h4>확인 주행 f2n1</h4><ul>
    <li>기록기의 <code>/tf</code> 구독만 best effort 로 바꾸고 같은 조건으로 달렸습니다.</li>
    <li>포화 없음, 3 목표 성공. <code>/tf</code> HEARTBEAT 은 6~7 /s 였습니다.</li>
    <li>bag 의 <code>/tf</code> 는 49~50 Hz 로 빠진 것이 없었습니다.</li>
  </ul></div>
</div>
<figure>
  <div class="img"><img src="''' + img('2026-10-13_bag_reception_f2m1_f2n1.png') + '''" alt="포화 주행과 확인 주행의 토픽별 수신 부족률"></div>
  <figcaption>위: 포화 주행(f2m1). 아래: 기록기 <code>/tf</code> 를 best effort 로 바꾼 주행(f2n1). 줄은 토픽, 색은 2 초 칸마다 평상 대비 못 받은 비율입니다. 위쪽은 포화 시작 뒤 <code>/tf</code> 가 끝까지 빨갛고, 아래쪽은 목표 전·전환 구간만 빨갛습니다.</figcaption>
</figure>
<div class="warnbox prose"><b>남은 것.</b> 앞 회전 우선 가중이 5 일 때는 왜 포화가 안 생기는지는 가리지 못했습니다. 발행량, 발행 간격, 기록기 CPU 를 견줬으나 5 와 15 가 같았습니다. 대책이 듣는 상황이라 미확정으로 닫았습니다.</div>

<h2 id="runner">러너 수정 2 건 <span class="sec">§4</span></h2>
''' + table(['고친 것', '전', '후(f2o1)'], [
    ['기록기 <code>/tf</code> 구독', 'reliable — 포화의 시작점', 'best effort 기본. bag <code>/tf</code> 49~51 Hz'],
    ['경로 끝 방향 조회기', '목표마다 새 프로세스 → 전환 때 손실 1,208~2,510 /s', '주행 시작 때 한 번만 띄움 → 전 구간 손실 0 /s']]) + '''

<h2 id="stall">상자 옆 정지 <span class="sec">§4.4~§6</span></h2>
<p class="prose">러너를 고친 뒤의 주행 3 회가 모두 복귀 길의 같은 상자 앞에서 끝났습니다. 통신은 정상이었습니다. Nav2 는 "후보 궤적 전부 충돌"을 반복했고 후진 복구도 "앞에 충돌"로 거부됐습니다. 그런데 실제로는 닿지 않았고, 줄자로 잰 여유는 11 cm 였습니다.</p>
<figure>
  <div class="img"><img src="''' + img('2026-10-13_f2o1_stop_at_box.png', 1280) + '''" alt="f2o1 정지 순간의 전역 코스트맵과 차체"></div>
  <figcaption>f2o1 정지 순간. 초록 = 차체, 보라 = 전역 경로, 빨간 네모 = MPPI 가 보는 치명 칸, 노랑 = 카메라 시야, 검은 십자 = 상자 끝. 로버 중심은 경로 위에 있고 오른쪽(북쪽)은 비어 있습니다 — 통로가 좁아서 멈춘 것이 아닙니다.</figcaption>
</figure>
<figure>
  <div class="img"><img src="''' + img('2026-10-13_f2o1_plan_through_box.png', 1280) + '''" alt="목표 3 출발 직후 전역 경로가 상자 자리를 지나감"></div>
  <figcaption>같은 주행의 목표 3 출발 5 초 뒤. 전역 지도에 상자 끝이 없어 경로가 그 자리를 지나가게 그려졌습니다. 로버가 3 m 넘게 멀어지면 카메라 지도가 지워지도록 설정돼 있기 때문입니다. 상자는 1.5 m 까지 다가왔을 때 다시 보였습니다.</figcaption>
</figure>

<h2 id="cause">원인 세 가지 <span class="sec">§5.4, §6.2, §8</span></h2>
''' + table(['', '무엇', '크기', '근거'], [
    ['1', '전역 경로가 상자 끝에 가깝게 그려진다', '0.22~0.29 m (차체 반폭 0.165 m)', '측정. 다듬기 전후 차이는 0.2~0.6 cm 라 스무더 탓이 아님'],
    ['2', '기억된 상자가 로버 쪽으로 밀린다', '4~5 cm', '카메라 지도는 odom 좌표. 상자는 1.5 m 에서 한 번 보이고 시야(±43°) 밖으로 나감. 그 뒤의 오도메트리 어긋남만큼 밀림. 실측 11 cm 대 코스트맵 5.4 cm 와 크기·방향 일치'],
    ['3', 'Nav2 충돌 검사가 칸 단위다', '약 5 cm', '시뮬에 같은 방식을 넣자 실제 정지 자세에서 5 / 5 가 갇힘. Nav2 소스와 한 줄씩 대조하지는 않음']], num=(0,)) + '''
<p class="prose">더하면 실제 11 cm 에서 약 5 cm 와 약 5 cm 가 빠져 거의 남지 않습니다. 그래서 Nav2 는 현재 자세부터 충돌로 보고, 어느 방향 후보도 받아들이지 않습니다.</p>
<h3>이 자리는 원래부터 아슬아슬했습니다 <span class="tag">§10</span></h3>
''' + table(['주행', '구성(벌점 · 궤적 발행)', '통신 포화', '상자 구역 최소 여유', '결과'], [
    ['f2f1', '15 · 전체', '있음', '3.8 cm', OK('통과') + ' 4.8 초 멈칫'], ['f2g1', '5 · 전체', '없음', '2.8 cm', OK('통과')],
    ['f2h1', '15 · 끔', '없음', '3.3 cm', OK('통과')], ['f2l1', '15 · lite', '없음', '2.9 cm', OK('통과')],
    ['f2l2', '15 · lite', '없음', '4.7 cm', OK('통과')], ['f2n1', '15 · 전체', '없음', '4.4 cm', OK('통과')],
    ['f2o1', '15 · lite', '없음', '2.2 cm', BAD('정지')], ['f2p1', '15 · lite, 전역 감쇠 3.0', '없음', '1.8 cm', BAD('정지')],
    ['f2q1', '15 · lite, 옆 여유 가중 3 배', '없음', '4.3 cm', BAD('취소')]], num=(3,)) + '''
<p class="prose">통과한 주행과 정지한 주행의 차이가 1~2 cm 입니다. 통신 포화가 상자를 피하게 도운 것도 아니었습니다 — 통과 6 회 중 포화가 있던 것은 한 번뿐입니다.</p>

<h2 id="tried">시험한 대책 <span class="sec">§5~§12</span></h2>
''' + table(['대책', '방법', '결과', '판단'], [
    ['전역 inflation 감쇠 2.0 → 3.0', '오프라인 재계획 + 주행 f2p1', '재계획으로는 +5 cm, 주행에서는 같은 자리 재정지', WARN('되돌림')],
    ['막혔을 때 후진 추가', '정지 자세에서 움직여 본 계산', '후진·오른쪽 회전은 기하로는 가능했으나 같은 검사에 걸림', NA('안 함')],
    ['풋프린트 패딩 0.01 → 0', '시뮬 40 회', '멈춤 1/10 → 0/10. 대신 1 cm 더 붙어 지나감', BAD('기각') + ' 더 붙는 방향'],
    ['MPPI 옆 여유 가중 3 배', '시뮬 150 회 + 주행 f2q1', '시뮬은 최악 여유 7~8 cm, 실제는 4.3 cm 에 머뭇거림(목표 1 +17 초)', WARN('되돌림')],
    ['전역 지도가 상자를 오래 기억', '—', '지나간 사람 같은 동적 물체도 남음', NA('보류')]]) + '''
<div class="fix prose">대책의 방향은 "갇히는 문턱을 낮춘다"가 아니라 "더 멀리 돌아간다"로 정했습니다. 다만 너무 돌아가려 하면 좁은 곳 통과가 어려워진다는 것도 주행에서 확인했습니다.</div>
<div class="warnbox prose"><b>시뮬의 한계.</b> 오프라인 MPPI 시뮬은 이 자리에서 실제보다 5 cm 쯤 넉넉하게 지나갑니다(실제는 9 회 모두 5 cm 미만, 시뮬은 10 씨앗 중 9 개가 5~11 cm). 설정 간 방향만 보고, 절대값으로 설정을 정하면 안 됩니다. 옆 여유 가중 3 배에서 그대로 드러났습니다.</div>

<h2 id="eval">평가 세 건 <span class="sec">§13~§14</span></h2>
<div class="look">
  <div><h4>다시 봤을 때 갱신</h4><ul>
    <li>이미 그렇게 동작합니다. 상자는 1.5 m 에서 다시 보이고 경로도 2 초 안에 비켜 그려집니다.</li>
    <li>정지를 만드는 밀림은 상자가 시야 밖으로 나간 뒤, 옆을 지나는 동안 생깁니다. 그 구간에는 다시 볼 수단이 없습니다.</li>
    <li>카메라 통합 거리는 1.4 → 2.0 m 로 되돌렸습니다(다음 기동부터). 유령 칸이 돌아오는지 확인이 필요합니다.</li>
  </ul></div>
  <div><h4>갇혔을 때만 패딩 0</h4><ul>
    <li>실제 정지 자세 두 곳에서 시뮬: 지금 값은 5 / 5 가 15 초 내내 전진 0.</li>
    <li>패딩 0 은 5 / 5 가 1 m 넘게 전진, 차체가 치명 칸에 겹치지 않음(여유 1.9~2.5 cm).</li>
    <li>구현 전 확인할 것: 실행 중 패딩 변경이 실제로 반영되는지. 결정 전입니다.</li>
  </ul></div>
</div>
<h3>EKF 는 미끄러짐을 보고 있나 <span class="tag">§14.3</span></h3>
<p class="prose">라이다 스캔 정합 속도(rf2o)가 이미 차체 vx·vy 로 EKF 에 들어가고 있고, 상자 접근 구간에서 게이트가 거부한 것도 없습니다. 그런데 효과는 거의 없습니다. 25 초 구간을 밀어 가며 SLAM 이동과 견준 어긋남의 중앙값입니다.</p>
''' + table(['주행', 'EKF(지금)', '휠만', 'rf2o 만', '휠 앞 + rf2o 옆'], [
    ['f2o1', '5.4 cm', '5.7', '10.4', '7.6'], ['f2p1', '4.8', '4.9', '12.7', '5.5'], ['f2n1', '4.5', '5.0', '12.5', '7.8'], ['f2q1', '6.6', '6.4', '11.7', '8.7']], num=(1, 2, 3, 4)) + '''
<p class="prose">rf2o 가 고쳐 주는 양은 0~2 cm 이고, 더 믿게 하면 오히려 나빠집니다(앞 방향을 약 10 % 적게 잼). 지금 가진 재료의 가중을 바꿔서는 4~5 cm 밀림을 없앨 수 없습니다. 기준이 SLAM 이라 참값은 아닙니다.</p>

<h2 id="fix">정정한 것 <span class="sec">SUMMARY 에 정정으로 남김</span></h2>
<ul class="prose">
  <li>"상자 칸이 늦게 떴다"고 읽은 것은 칸을 지도 좌표에 고정해 놓고 봐서 생긴 착시였습니다. 카메라 지도(odom 좌표)가 보정만큼 미끄러진 것입니다.</li>
  <li>전역 감쇠를 "완만하게" 하자는 후보는 방향이 반대였습니다. 완만하면 더 붙습니다.</li>
  <li>"시뮬이 옛 크리틱 기준이라 고쳐야 한다"는 확인 없이 한 말이었습니다. 09-18·10-01 판에 이미 들어 있었습니다.</li>
  <li>서쪽 통로 장면을 "실제로 지나간 곳"이라고 선언에 적었으나 그 주행은 통로를 못 지났습니다. 실행 전에 고쳤습니다.</li>
  <li>검증 주행 선언에 탐색 통신 급증을 구분해 두지 않아 엄격히 읽으면 '중간' 판정인 것을 그대로 적었습니다.</li>
  <li>rf2o 원본 속도를 차체 좌표로 그냥 적분해 3 m 어긋난 값을 냈다가 뺐습니다(라이다 좌표의 속도).</li>
</ul>

<h2 id="next">다음 <span class="sec">§15</span></h2>
<ol class="prose">
  <li>카메라 통합 거리 2.0 m 로 주행 1 회 — 상자를 다시 보는 거리와 유령 칸 확인.</li>
  <li>"갇혔을 때만 패딩 0" 을 할지 결정. 한다면 정지 상태에서 실행 중 변경이 반영되는지부터.</li>
  <li>미뤄 둔 10 개 목표 순회 기준선.</li>
  <li>정체 감시 노드를 작동 모드로 되돌리기 전에 오늘 찍힌 STUCK 기록(f2p1 1 회, f2q1 11 회) 확인.</li>
  <li>옆을 지나는 동안의 오도메트리 어긋남을 줄일 다른 관측(시각 오도메트리)은 다음 단계 과제입니다.</li>
</ol>

<footer>현재 구성은 아침과 같고(전역 감쇠 2.0 · 패딩 0.01 · 옆 여유 가중 3.81), 바뀐 것은 러너 2 건과 카메라 통합 거리 2.0 m 입니다. 수치의 출처는 Docs/debug_log/2026-10-13/SUMMARY.md 와 outputs/ 입니다.</footer>
</div>
'''
OUT.write_text(head + body, encoding='utf-8', newline='\n'); print('저장', OUT, round(OUT.stat().st_size / 1024), 'kB')
