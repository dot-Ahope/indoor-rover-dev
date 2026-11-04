# F2.5 장소 이름 이동 — 등록부 · place_server · 명령 창구 · 휴대폰 창구 (9 기: 10-28 §6 ~ §17, 10-29 §2 · §4 코드만)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **조사 중** — S1 기능(이름 → 등록부 좌표 → 목표 검사 → NavigateToPose · stop · return)은 실주행으로 확인(f2pl4 명령 6/6 · f2pl5 2/2, 접촉 0 — 사용자 관찰). 그러나 ① 설계의 S1 종료 조건 T1(장소마다 9/10)은 **안 돌렸다** ② 온디바이스 모델(S2 ~ S5)은 **한 번도 실행 안 함**(10-28 §15) ③ `place_server` · `place_web` 은 **어떤 launch 에도 없다** — 10-28 러너가 src 에서 직접 띄운 시험 단계(11-03 §7 ③, 이 카드 작성 중 다시 확인) ④ 휴대폰에서 실제로 열어 본 적 없음 | 10-28 ~ (09-30 §9 목표 제시) | [09-30 §9](../debug_log/2026-09-30/SUMMARY.md) 사용자 최종 목표 → [10-28 §6](../debug_log/2026-10-28/SUMMARY.md) 설계 착수 | 설계 [`F25_PLACE_LLM_DESIGN.md`](../07_language/F25_PLACE_LLM_DESIGN.md) v0.1 → v0.2 · 등록부 [`places.yaml`](../../ros2_ws/src/rover_navigation/config/places.yaml)(신규) · [`place_server.py`](../../ros2_ws/src/rover_navigation/scripts/place_server.py) · [`place_cmd.py`](../../ros2_ws/src/rover_navigation/scripts/place_cmd.py) · [`path_end_yaw.py`](../../ros2_ws/src/rover_navigation/scripts/path_end_yaw.py)(러너 job613 사본) · [`place_web.py`](../../ros2_ws/src/rover_navigation/scripts/place_web.py) · `CMakeLists.txt` 46~47 행(설치 줄) · 그림 도구 [`fig_place_run.py`](../tools/fig_place_run.py) · 커밋 `f56a619d`(§7) → `a79247e8`(§8) → `b343b5aa`(§9) → `e0bcbcce`(§10) → `f3286e49`(§13) → `be17666e`(§16) → `b359fbc7`(10-29 출발 전 위치 검사) | [F2 기준선 no5](f2-baseline-no5.md)(등록 좌표의 출처) · [남서 구석 정체](southwest-orient-stall.md)(`f` 위치만 규칙) · [BT 끝 방향 · CopyPath](bt-copypath-end-yaw.md)(경로 끝 방향) · [온보드 정지 · nav_guard](onboard-stop-nav-guard.md)(stop · 한도) · [세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md)(§13.1 · §16.1 경로 없음의 원인, 출발 전 위치 검사) · [PathBlockedAhead](pathblocked-only-new.md) · [상자 옆 정지 기전](box-side-stall-cause.md)(칸 경계 흔들림) · [Smac 채택](smac-hybrid-adoption.md)(이 주행들의 스택 구성) · [주행 전 검사 정리](drive-gate-consolidation.md)(러너 게이트) · [주행 직전 DDS 참여자 금지](pre-drive-dds-participants.md) · [Jetson Wi-Fi](jetson-wifi-link.md)(휴대폰 · AP 격리) |

**한 줄**: '장소 이름을 말하면 그 자리로, 돌아와 하면 출발점으로' 의 첫 두 단계(S0 등록부 · S1 LLM 없는 장소 실행 노드)를 하루에 만들어 실주행했다. 원칙은 **좌표는 사람이 쓴 `places.yaml` 에서만** 나오고, 모르는 이름 · 여유 부족 · 연결 이상은 모두 '움직이지 않음' 으로 끝나게 하는 것. 실주행 5 번 중 앞의 3 번은 전부 그 원칙대로 '거절 · 멈춤' 으로 끝났다 — f2pl1 은 경로 끝 방향(−51°)으로 비스듬히 선 명목 자세를 검사해 통로 북쪽 거절(→ ±45° 방향 고침), f2pl2 는 등록 좌표가 통로 동쪽 물체 쪽으로 13 cm 치우쳐 남쪽에서 다시 거절(→ x −1.65 → −1.78), f2pl3 은 창구의 첫 'where' 가 서버에 닿지 않아 로버가 아예 안 움직임(→ 양방향 연결 확인). 네 번째 f2pl4 에서 명령 6 개가 전부 기대대로 끝났고 stop → `/cmd_vel` 0 까지 0.29 s, 다섯 번째 f2pl5(W3 왕복) 2/2. 'C 와 위 복도를 한 자리로 합친' 내 결정 때문에 한 구간이 no5 보다 7.5 s 느렸고(경로가 좁은 통로에서 4 cm 동쪽), 되돌린 뒤의 판별 시험(upB)은 보류됐다. 같은 날 휴대폰 웹 창구 `place_web.py` 도 만들었지만 PC 에서만 확인했다. 모델은 아직 안 돌았다.

## 1. 출발점 · 목표
- 09-30 §9 사용자 최종 목표: "특정 구역에 이름을 붙이고, 온디바이스 LLM 에 '그 지역으로 이동해' 라고 하면 이동, '돌아와' 하면 출발 위치로 복귀". 제안 구조 = LLM 은 고정 형식(`{"action": "go_to", "place": <등록 이름>}`)만 내고, 좌표는 등록부, 실행은 NavigateToPose. 선행 = 위치 추정 모드(세션 간 같은 좌표계) → F2 순회 → '서비스 호출로 장소 이동(LLM 없이)' → LLM 앞단. [09-30 SUMMARY](../debug_log/2026-09-30/SUMMARY.md) 194~197 행.
- 10-28 §6 설계 v0.1 의 전제 표(측정 근거): prep 위치 검사 0.3~1.6 cm · no5 8 목표 4 회 연속 8/8 · 도착 오차 0.09~0.23 m · 주행 중 RAM 3.2 / 7.6 GB. 남은 약점으로 '주행 중 PC 연결이 끊기면 PC 에서 멈출 수 없음(10-28 §3.1)' 을 적어 정지를 Jetson 안에서 처리하게 함. [설계 문서](../07_language/F25_PLACE_LLM_DESIGN.md) §2.
- 이 카드의 '증상' 은 고장이 아니라 **기능 개발 중 만난 거절 · 멈춤 · 느림**이다.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-30 §9 | 최종 목표 · 구조 제안 | — | 입력 = 텍스트(결정), LLM 은 좌표를 만들지 않음 | [09-30 SUMMARY](../debug_log/2026-09-30/SUMMARY.md) |
| 10-28 §6 | 설계 v0.1 | 구조 · 안전 · 자원 예산(추정) · 시험 T1~T5 · 단계 S0~S5 · 결정 6 개 | 다음 = §8 결정 → S0 → S1 | [설계](../07_language/F25_PLACE_LLM_DESIGN.md) · `Docs/INDEX.md` · `NAV2_EXPLORATION_PLAN.md` §7.4 |
| 10-28 §7 | S0 이름 결정(사용자 "우선 우리가 부르던 이름으로") · S1 코드 · dry_run 1 차 | 장소 6 곳(출발점 · B · C(별칭 '위 복도') · 통로 북쪽 · 남서(`f`) · W3), '돌아와' = 출발점. 1 차: **남서 거절 여유 0.000 m**, dry_run 의 accepted 가 끝 상태가 아니라 창구가 25 s 기다림 | 남서 `min_clear 0.0`(근거를 등록부에) · dry_run 끝 상태 'checked' · stop 때 진행 중 명령에도 canceled | [`chk_place_dry_1028.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028.txt) · 도구 [`chk_place_dry_1028.sh`](../debug_log/2026-10-28/jobs/chk_place_dry_1028.sh) |
| 10-28 §7 | dry_run 2 차 | checked 5(B · C · 남서 · W3 · 출발점), 거절 2(화장실 · 빈 이름) · stop 정상. 출발점에서 남서로 바로 가면 경로 끝 방향 154°(431 점) | "이동 명령 5 개 모두 checked" → 실주행 준비 끝(**✘ 통로 북쪽을 안 봄**, §5.1) | [`chk_place_dry_1028b.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028b.txt) |
| 10-28 §7.1 · §8 | **f2pl1**(full: no5 순서 + W3 @stop20 + return) | where 1.0 s → B arrived 54.6 s → 위 복도(→ C) arrived 53.9 s → **통로 북쪽 rejected '목표 여유 0.000 m < 0.10'** → 창구가 뒤 명령을 안 보내고 rc 1. 로버 C 에서 정지. nav_guard 취소 0 | 판정 ① 불합격. 거절은 설계대로의 안전 동작 | [`drives/f2pl1/place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl1/place_s1.log) · [`place_server_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl1/place_server_s1.log) · bag `bags/bag_f2pl1.tgz`(14 MB) |
| 10-28 §8.2 | 거절 순간 전역 판으로 방향별 여유 재계산 · C 에서 dry_run 재현 | −90° 0.110 · −60° 0.029 · −45° 0.002 · −30~−15° 0.000, 가장 가까운 치명 칸 늘 x −1.365(/map 0 = 정적 지도에 없는 물체). C 에서 재현 3/3 '방향 −51°' | 거절 = 경로 끝 0.3 m 가 통로로 비스듬히 들어가는 방향의 **명목 자세**. no5 러너는 같은 목표를 −55~−64° 로 보내 로버가 −74~−87° 로 서서 끝냈음 | [`place_clear_f2pl1.txt`](../debug_log/2026-10-28/outputs/place_clear_f2pl1.txt) · [`chk_place_dry_1028c1.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028c1.txt) · `drives/f2tt2/f0_f2tt2/f0_f2tt2.log` |
| 10-28 §8.3 | place_server: 여유 미달이면 ±45° 안 5° 간격으로 가장 가까운 기준 넘는 방향으로 고침 | C 에서 dry_run 3/3 '−35° 고침(원래 0.000) · 방향 −86° · **여유 0.10 m**' | 통과 — 기준에 딱 걸침(§8.4 에 '한 칸 더 찍히면 거절될 수 있음' 선언) | [`chk_place_dry_1028c2.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028c2.txt) |
| 10-28 §9 | **f2pl2**(fromC) | 통로 북쪽 arrived 31.0 s(고침 −35° → −86°) → 남서 arrived 26.6 s → **두 번째 통로 북쪽(남쪽에서) rejected '0.000 m · 방향 74°'**. 로버 남서 구석 정지 | 선언한 위험이 그대로 일어남 | [`drives/f2pl2/place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl2/place_s1.log) · bag `bags/bag_f2pl2.tgz` |
| 10-28 §9 | 그 칸 출처 · 좌표 옮김 재계산 | 칸 (−1.465, −3.735) 전역 99 ↔ 100, 라이다 점 5 cm 안 27~184 개 · nvblox 0.21~0.28(장애물 아님) → 실재 물체 가장자리. x −1.78 이면 두 판 모두 ±75~90° 0.10~0.16 m | 등록부 통로 북쪽 **x −1.65 → −1.78**(내 판단, 미검증 자리) | [`place_clear_f2pl2.txt`](../debug_log/2026-10-28/outputs/place_clear_f2pl2.txt) · [`cell_src_f2pl2.txt`](../debug_log/2026-10-28/outputs/cell_src_f2pl2.txt) · [`place_clear_center.txt`](../debug_log/2026-10-28/outputs/place_clear_center.txt) |
| 10-28 §9 | §5.1 교훈 적용: 6 곳 전부 + 실주행과 같은 출발 자리(남서)에서 dry_run | 6 곳 checked — 통로 북쪽 99° 여유 0.13 · 0.18 m(고침 없이) | 실주행 준비 | [`chk_place_dry_1028c3.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028c3.txt) |
| 10-28 §10 | **f2pl3**(fromSW) | `>> where` → 5.0 s 끝 상태 없음 → rc 1, **이동 명령 0 개 · 로버 안 움직임**. bag `/place/command` 1 · `/place/status` 0, 서버 로그에 수신 흔적 없음 | 첫 메시지 연결 경쟁(어느 쪽인지 미확인) → place_cmd 양방향 확인 + 1 s + 조회만 재전송 | [`drives/f2pl3/place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl3/place_s1.log) · [`chk_place_dry_1028c4.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028c4.txt)(9/9) |
| 10-28 §11 | **f2pl4**(fromSW) | 명령 6 개 rc 0: where 0.0 s · 통로 북쪽(−1.78) 34.1 s · 위 복도(→ C) **31.3 s** · W3 @stop20 canceled 20.1 s · W3 81.4 s · return 105.0 s. **stop → `/cmd_vel` 0 +0.29 s · EKF 정지 +0.47 s** | S1 기능 확인. 위 복도 구간만 no5(22.6~23.9 s)보다 +31~38 % — 원인 미확인 | [`drives/f2pl4/place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl4/place_s1.log) · [`stop_cmdvel_f2pl4.txt`](../debug_log/2026-10-28/outputs/stop_cmdvel_f2pl4.txt) · bag `bags/bag_f2pl4.tgz`(34 MB) |
| 10-28 §12 | 위 복도 구간 vs no5 목표 6(사용자 "접촉 없었다 … 뭐가 달랐기에") | 컨트롤러 주기 20/s · BT 사건 0 같음. 다름: 목표 10 cm 북쪽(내 합침) · 경로 x 4 cm 동쪽 · 동쪽 가장자리 한 칸 안쪽 · 오른쪽 라이다 여유 0.06~0.07(no5 0.11~0.15) · 평균 전진 0.060 m/s | MPPI 가 스스로 감속(측정). 앞쪽 감속은 설명 안 됨(미확인). §5.2 실수 | [`leg_compare_C.txt`](../debug_log/2026-10-28/outputs/leg_compare_C.txt) · [`leg_env_C.txt`](../debug_log/2026-10-28/outputs/leg_env_C.txt) · [`plan_x_C.txt`](../debug_log/2026-10-28/outputs/plan_x_C.txt) · [`east_edge_history.txt`](../debug_log/2026-10-28/outputs/east_edge_history.txt) |
| 10-28 §13 | 판별 시험 선언(upB): 위 복도를 (−1.60, −2.10) 별도 장소로 · 같은 구간 2 번 · 판정 ② ≤ 25.0 s 둘 다 → 원인 = 좌표 | 사전 여유 40~55° 0.124~0.111 m(기준 위 1.8 cm) | 선언(결과 보기 전) | [`place_clear_upB_f2pl4.txt`](../debug_log/2026-10-28/outputs/place_clear_upB_f2pl4.txt)(한글 깨짐, §6-7) |
| 10-28 §13.1 | 주행 전 dry_run | 출발점 말고 **모든 목표 경로 조회 실패(상태 6) → 직선 방향**, C · 위 복도 직선 −128° 로 여유 0 거절 | f2pl5(upB) 시작 안 함. 원인은 [드리프트 카드](stationary-yaw-drift.md) 몫(처음 해석 'nvblox 기억' 은 §16.2 에서 틀림) | [`chk_place_dry_1028c5.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028c5.txt) |
| 10-28 §14 · §14.1 | prep #2 → dry_run 8/8 → **f2pl5**(사용자 "W3 만 찍고 오는 것으로", upB 보류) | W3 arrived 91.7 s · return 100.2 s, TF 실패 0 · 중단 0 · PathBlockedAhead 재계획 1(복귀 +154 s). 접촉 0(사용자) | 기준 ①~④ 통과. 명령 · 결과 그림 도구 신설 | [`drives/f2pl5/place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl5/place_s1.log) · [`chk_place_dry_1028c6.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028c6.txt) · [`fig_place_run_f2pl5.png`](../debug_log/2026-10-28/outputs/fig_place_run_f2pl5.png) |
| 10-28 §15 | 사용자 "온디바이스 모델이 어떤 출력을 냈는지" | 명령 문자열은 러너 PLAN 에 내가 적은 고정 문자열, 문장 해석 단계 없음 | **모델은 아직 돌지 않았다** — S1 까지만 | [10-28 §15](../debug_log/2026-10-28/SUMMARY.md) · [`run_place_s1_1028.sh`](../debug_log/2026-10-28/jobs/run_place_s1_1028.sh) 22~28 행 |
| 10-28 §16 | 휴대폰 웹 창구(사용자 "휴대폰 웹 페이지도 만들자" — 설계 §8-3 결정) | dry_run 서버와 함께: 키 없이 403 · 키 있으면 200(5 693 B) · 장소 7 곳 · POST 5/5 응답 · 배터리 12.20 V · **PC(ALOPS) → Jetson:8080 200, 15 ms** | 동작(PC 에서). 휴대폰 미확인 · 종료 예외 처리는 다음 실행에서 확인 | [`place_web_chk1.txt`](../debug_log/2026-10-28/outputs/place_web_chk1.txt) · 도구 [`up_place_web_1028.sh`](../debug_log/2026-10-28/jobs/up_place_web_1028.sh) · [`chk_place_web_1028.sh`](../debug_log/2026-10-28/jobs/chk_place_web_1028.sh) |
| 10-28 §16.1 | 같은 dry_run 에서 경로 조회 다시 전부 실패 | odom yaw 정지 중 +16.6° · 스캔 맞춤 −32.5° | 포인터만 — [드리프트 카드](stationary-yaw-drift.md) | `place_web_chk1.txt` state 2 · 3 |
| 10-28 §17 | 마무리 | 결정 대기: §16.3 드리프트 대책 · 설계 §8-4~6 · place_web 상주 기동 방식 | `place_web.py` 는 소스 · CMakeLists 에만, Jetson colcon 설치 안 함 | [10-28 §17](../debug_log/2026-10-28/SUMMARY.md) |
| 10-29 §2 | 출발 전 위치 추정 검사(ⓐ)를 `place_server` 에 추가 | 문턱 0.40 · 4° · 0.03(근거 570 판) | **Jetson 배포 · 실동작 안 함**(10-29 §5) — 본체는 [드리프트 카드](stationary-yaw-drift.md) | 커밋 `b359fbc7`, 코드 146~180 · 191 · 204~205 행 |
| 10-29 §4 · §5 | d2 선언(`run_place_s1_1028.sh d2 w3` = f2pl5 와 같은 명령) | 실행 안 함 | — | [`run_d2_1029.sh`](../debug_log/2026-10-29/jobs/run_d2_1029.sh) |
| 11-03 §7 ③ | CLAUDE.md 지적 대조 | `ros2_ws/src/*/launch/` 검색 0 | 시험 단계라고 CLAUDE.md F2.5 줄에 적음 | [11-03 SUMMARY](../debug_log/2026-11-03/SUMMARY.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| f2pl1 통로 북쪽 거절 = 여유 검사가 실제로 서지 않을 명목 자세(경로 끝 방향)를 판정 | 거절 순간 전역 판 방향별 여유 · C 에서 dry_run 재현 · no5 같은 목표의 보낸/도착 방향 | 비스듬(−45~−15°) 0.000~0.002, 통로 축(−90°) 0.110. 재현 3/3 −51°. no5 는 −55~−64° 로 보내 −74~−87° 도착(4/4 SUCCEEDED) | **지지(측정)** — no5 러너엔 여유 검사가 없어 같은 자세를 Nav2 가 받았고 로버가 축 쪽으로 섰다 |
| 방향 고침(±45°)만으로 충분 | f2pl2 같은 목표를 남쪽에서 | 74° 거절, +90° 도 0.010 | **기각** — 방향이 아니라 좌표(물체 쪽 13 cm 치우침) 문제 |
| 거절을 만든 칸은 유령 · 기억 | 그 칸 판마다 라이다 점 · nvblox 거리 | 라이다 5 cm 안 27~184 점 내내, nvblox 0.21~0.28 | **기각** — 라이다가 보는 실재 물체 가장자리, 99 ↔ 100 은 칸 경계 흔들림(10-28 §5 와 같은 꼴). 물체 정체(쇼핑백 · 상자)는 **미확인**(사용자 확인 필요로 남음) |
| x −1.78 이면 남북 어느 쪽 진입이든 기준을 넘는다 | 두 bag 판으로 오프라인 재계산 → f2pl4 실주행 | 오프라인 0.10~0.16 m · f2pl4 '102°, 여유 0.17(고침 없음)' arrived 34.1 s | **지지(1 회)** |
| f2pl3 'where' 유실 = 서버 쪽 수신 전(명령 경로) | 서버 로그 · bag 의 /place/command · /place/status 수 | 서버 로그 수신 흔적 0 · status 0 | f2pl3 은 **명령 쪽에서 빠짐(측정)**. 그런데 13:16 dry_run c1 에선 서버가 info 로 답했는데 창구가 25.1 s 동안 못 받음 → **응답 쪽 유실도 한 번 있었다**(이 카드 작성 중 발견, §6-2). 기전(DDS 매칭 완료 전 발행)은 **추정** |
| 위 복도 구간 느림 = C 로 합친 목표 좌표(10 cm 북쪽) | upB 판별 시험(§13 선언, 기준 ≤ 25.0 s / ≥ 28.0 s) | 실행 안 함(§13.1 경로 없음 → §14 사용자 지시로 W3 왕복으로 바꿈) | **미확인** — 다른 후보: 동쪽 가장자리 2~4 cm 안쪽(추정) · 끝 방향 50° vs 88°. 구간 앞쪽 감속은 여유가 no5 와 같은 자리에서도 일어나 좌표만으로 설명 안 됨 |
| 명령 → 이동 시작 지연은 작다(설계 T3 의 장소 실행 부분) | place_s1.log accepted · moving 시각 | 0.0~0.2 s(경로 방향 조회 포함) | **지지(측정, 4 주행)** — 문장 해석 지연(T3 본체)은 모델이 없어 미측정 |

## 4. 조치와 효과
- **구조(설계 §3 → 실제 구현)**: 문자열 명령 토픽 `/place/command`(`'<id>|<명령>'`) → `place_server`(등록부 · 위치 · 목표 검사 · NavigateToPose) → `/place/status`(JSON 한 줄, `accepted · rejected · moving · arrived · failed · canceled · info · checked`). 창구는 `place_cmd.py`(여러 명령을 한 프로세스 · 참여자 1 개로) · `place_web.py`(휴대폰). 경로 끝 방향은 별도 상주 프로세스 `path_end_yaw.py --serve`(같은 노드에서 compute_path_to_pose 뒤 navigate_to_pose 응답이 오지 않던 09-28 §20 사고 때문).
- **거절 규칙(움직이지 않는 경우)**: 모르는 이름 · 모르는 명령 · 이동 중 새 go_to('먼저 stop', 설계 §8-4 결정 전 기본값) · TF 없음 · 전역 코스트맵 없음 · 목표 여유 < 기준(장소별 `min_clear`, 기본 0.10 m; ±45° 방향 고침 뒤에도) · navigate_to_pose 서버 없음 · (10-29 ~) 출발 전 위치 추정 검사 불합격.
- **효과(측정)**:

  | | f2pl1 | f2pl2 | f2pl3 | f2pl4 | f2pl5 |
  |---|---|---|---|---|---|
  | 보낸 명령(where 포함) → 기대대로 | 3/4(통로 북쪽 거절) | 3/4(통로 북쪽 거절) | 0/1(where 무응답) | **6/6** | **3/3** |
  | 로버 상태 끝 | C 에서 정지 | 남서에서 정지 | 안 움직임 | 출발점 | 출발점 |
  | 명령 → moving | 0.0~0.1 s | 0.1 s | — | 0.0~0.1 s | 0.1 s |
  | stop → /cmd_vel 0 | — | — | — | **+0.29 s**(감속 램프 +0.09 s 부터) | — |
  | nav_guard 취소 | 0 | 0 | — | 0 | 0 |

  출처: 각 `outputs/drives/f2pl*/place_s1.log` · `nav2.log`(nav_guard 줄은 시간 한도 계산 로그만, 취소 줄 0 — 이 카드 작성 중 셈) · [`stop_cmdvel_f2pl4.txt`](../debug_log/2026-10-28/outputs/stop_cmdvel_f2pl4.txt).
- 한계:
  - 3 번의 '거절 · 멈춤' 은 위험 동작이 아니었지만, 곧 **좁은 곳 장소 하나(통로 북쪽)가 여유 0.10 m 경계에 걸려 있다**는 뜻이다. 물체 가장자리가 한 칸 더 들어오면 다시 거절된다(−1.78 의 여유 0.13~0.18 m 는 한두 칸 몫).
  - 구간 시간 판정 ④ 은 '위 복도' 한 구간에서 ✘ 로 남았고 원인 미확인.
  - 장소마다 9/10(T1) 는 시험 안 함 — 각 장소 도착은 1~3 회뿐.

### 4.1 지금 코드 영향 (11-04 저장소 기준)
- **아무 launch · prep 도 F2.5 노드를 띄우지 않는다.** `ros2_ws/src/*/launch/` · `Docs/tools/*.sh` 에서 `place_server|place_web|place_cmd|path_end_yaw` 검색 0(이 카드 작성 중 다시 확인, 11-03 §7 ③ 과 같음). 띄우는 곳은 10-28 러너 [`run_place_s1_1028.sh`](../debug_log/2026-10-28/jobs/run_place_s1_1028.sh) 12 행(`setsid nohup python3 $SRC/scripts/place_server.py --ros-args -p places_file:=$SRC/config/places.yaml` — Jetson **src** 에서 직접, UDP 전용 프로파일 6 행) · 30 행(`place_cmd.py "$CMDS"`)뿐. 그 러너는 PC 쪽 [`up_place_s1_1028.sh`](../debug_log/2026-10-28/jobs/up_place_s1_1028.sh) 5~6 행이 **스크래치패드의 `f25_*` 사본**을 Jetson src 에 올린 뒤 부른다 — 이 카드 작성 중 스크래치패드 사본 5 개(server · cmd · path_end_yaw · web · places)가 저장소 판과 같음(CR 빼고 md5)을 확인했으나, 스크래치패드는 자동 삭제 대상이다.
- [`CMakeLists.txt`](../../ros2_ws/src/rover_navigation/CMakeLists.txt) 46~47 행이 네 스크립트를 설치 목록에 넣지만, Jetson colcon 설치는 10-28 §17 기준 안 함 — 지금 Jetson 설치본 여부는 **미확인**(11-04 §1 src 비교 8 파일에 place_* 는 없음).
- Jetson src 의 `place_server.py` 판: f2pl4 · f2pl5 서버 로그 traceback 의 `line 230, in <module>` 은 230 행 판(커밋 `a79247e8` ~ `be17666e`)과 맞는다. 10-29 ⓐ 판(281 행, `b359fbc7`)은 배포 안 함(10-29 §5) → Jetson src 는 **ⓐ 없는 판일 가능성이 큼(추정, 확인 안 함)**.
- 저장소 판 [`place_server.py`](../../ros2_ws/src/rover_navigation/scripts/place_server.py) 동작 요점(행):
  - 41 행 `HL, HW = 0.26, 0.175`(job377 과 같은 차체 반길이 · 반폭) · 56~57 행 파라미터(`min_clear 0.10 · xy_done 0.15 · dry_run False · loc_check True · loc_min_score 0.40 · loc_max_yaw 4.0 · loc_min_gain 0.03`).
  - 136~143 행 `clearance` — 전역 코스트맵 **≥ 100(치명)** 칸만 · 차체 직사각형 바깥까지 거리 최소. 99(내접)는 안 셈.
  - 195~196 행 이동 중 새 go_to 거절 · 197~198 행 모르는 이름 거절 · 204~205 행 출발 전 위치 추정 검사(10-29) · 207~208 행 xy 0.15 m 안이면 '이미 그 자리' arrived · 209 행 `p`/`f` 면 경로 끝 방향 · 212 행 장소별 `min_clear` · 214~223 행 ±45° · 5° 방향 고침(`TODO(improve)` 218 행) · 224 행 거절 메시지에 방향 · 226 행 dry_run 'checked'.
  - 249~256 행 `f` 모드: xy < 0.15 m 이면 `cancel_goal_async` → arrived(러너 `f` 와 같은 규칙, [남서 카드](southwest-orient-stall.md)).
  - 258~266 행 stop = 빈 `CancelGoal`(Nav2 **모든** 목표) + 자기 목표 핸들 취소 + 진행 중 명령에 canceled 알림.
  - ⚠ 76 행은 등록부 `map:` 이름을 **찍기만** 한다 — [`places.yaml`](../../ros2_ws/src/rover_navigation/config/places.yaml) 8 행 `TODO(improve): 지도 이름 확인 연결`. 설계 §4-2 '등록부 무효(지도 바뀜) → 움직이지 않음' 은 미구현.
  - ⚠ 경로 조회 실패(`FAIL 경로 없음(상태 6)`)면 직선 방향으로 대체하고 그대로 검사 · 송신한다(119 행) — §13.1 · §16 에서 거절은 직선 방향의 여유 0 때문이었고, 직선 방향으로도 여유가 있으면 'checked' 가 나왔다(c5 의 B · W3 · 통로 북쪽). 실주행이었다면 Nav2 에 목표가 갔을 것(그 뒤는 계획 실패로 끝났을 것으로 추정).
- [`places.yaml`](../../ros2_ws/src/rover_navigation/config/places.yaml): 7 곳 — 출발점 (0, 0) · B (2.25, −1.6) · C (−1.6, −2.0) · 위 복도 (−1.6, −2.1)(32 행, §13 분리) · 통로 북쪽 **(−1.78, −3.7)**(37~41 행, §9) · 남서 (−1.6, −5.5) `f` · `min_clear 0.0`(46~47 행) · W3 (5.5, −2.2). `home: 출발점`(9 행).
- [`place_cmd.py`](../../ros2_ws/src/rover_navigation/scripts/place_cmd.py) 27~30 행 양방향 확인(`pub.get_subscription_count()` 와 `n.count_publishers('/place/status')`) + 1 s · 52~53 행 조회(where · list)만 2 s 무응답이면 한 번 재전송 · 46 행 기다림 go_to 300 s · 나머지 5 s · 66 행 기대와 다르면 뒤 명령을 안 보내고 rc 1.
- [`place_web.py`](../../ros2_ws/src/rover_navigation/scripts/place_web.py) 9 행 `0.0.0.0:8080` · 11 행 `TODO(improve)` 평문 HTTP · 키 하나 · 12 행 휴대폰 정지는 '보조' · 13 행 주행 30 s 전 새로 띄우지 않음 · 27 행 키 파일 위치(저장소 밖) · 30~35 행 없으면 만들고 0600 · 135~137 행 키 비교(`secrets.compare_digest`, 헤더 `X-Rover-Key` 또는 주소 `?k=`) · 109 행 장소 버튼 4 s 안 두 번 눌러야 송신 · 119 행 정지는 한 번에 'stop'.
- 그림 도구 [`fig_place_run.py`](../tools/fig_place_run.py) — 상시 도구(§9.9).

## 5. 내 실수
### 5.1 10-28 §8.1 — dry_run 에서 '통로 북쪽' 을 시험하지 않고 "이동 명령 5 개 모두 통과" 로 보고
| 칸 | 내용 |
|---|---|
| 하려 한 것 | §7 dry_run 으로 등록부 장소 전부의 목표 검사(경로 끝 방향 · 여유)를 실주행 전에 확인 |
| 본 것 | `chk_place_dry_1028b.txt`: checked 5 = B · C · 남서 · W3 · 출발점. 명령 목록에 통로 북쪽이 없음 |
| 처음 추론 | "이동 명령 5 개 모두 checked" = 등록부 전부 통과(사용자에게도 그렇게 보고) |
| 의심한 이유 | f2pl1 이 바로 그 장소에서 거절 |
| 판별 | 스크립트 명령 목록 대조 — 6 곳 중 5 곳. 수가 '5 개' 로 맞아 보였음 |
| 결론 | 통로 북쪽은 실주행 전 한 번도 검사 안 됨. 게다가 dry_run 은 출발점에서만 해서 실주행과 다른 출발 자리(C → 통로 북쪽)의 경로 끝 방향은 볼 수 없었음 |
| 다음에 알아보는 법 | dry_run 은 **등록부를 읽어 모든 장소**를 돌고 결과 수 = 장소 수 확인. 출발 자리가 바뀌는 검사는 그 자리에서 다시 보거나 bag 으로 재계산 |
| 스크립트 핵심 | [`chk_place_dry_1028.sh`](../debug_log/2026-10-28/jobs/chk_place_dry_1028.sh) 9 행 — 손으로 쓴 목록 |
| 나온 결과 | 아래 |
| 데이터 | [`chk_place_dry_1028b.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028b.txt) · [`drives/f2pl1/place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl1/place_s1.log) |

```bash
# jobs/chk_place_dry_1028.sh 9 행 — 장소를 등록부에서 읽지 않고 손으로 적음(통로 북쪽 없음)
for c in "list" "where" "go_to B" "go_to 위 복도" "go_to 남서" "go_to W3" "return" "go_to 화장실" "go_to" "stop"; do echo "## $c"; $C $c --wait 25; echo "  rc $?"; done
```
```
# outputs/chk_place_dry_1028b.txt(발췌) → outputs/drives/f2pl1/place_s1.log
0.1 s  checked  B  [dry_run — 보내지 않음] 목표 (2.25, -1.60, -80°) 경로 끝 방향(157 점) · 여유 0.44 m · 거리 2.88 m
0.1 s  checked  남서  [dry_run — 보내지 않음] 목표 (-1.60, -5.50, 154°) 경로 끝 방향(431 점) · 여유 0.00 m · 거리 5.63 m
   0.0 s  rejected  통로 북쪽  목표 여유 0.000 m < 0.10
```
- 이후의 판(`chk_place_dry_1028c.sh` 9 행)도 여전히 손 목록이다 — 다만 9 행에 7 곳을 모두 적었다(c5 · c6). '등록부에서 읽어 전부' 는 코드로 바뀌지 않음.

### 5.2 10-28 §12.3 — 위 복도를 C 로 합친 것
| 칸 | 내용 |
|---|---|
| 하려 한 것 | §7 등록부에서 위 복도 (−1.6, −2.1) 와 C (−1.6, −2.0) 를 '10 cm 차' 라 한 장소로 |
| 본 것 | f2pl4 위 복도 구간 31.3 s(no5 22.6~23.9 s), Smac 경로 4 cm 동쪽 |
| 처음 추론 | 10 cm 는 도착 허용(0.15 m) 안이라 같은 자리 |
| 의심한 이유 | 도착점은 같아도 **좁은 통로 안 경로 선**이 목표 위치에 따라 바뀜 — 여유가 몇 cm 인 곳에서는 의미 있는 차 |
| 판별 | §13 upB(선언만, 실행 안 함) |
| 결론 | 원인 후보 중 하나일 뿐 — **미확인**. 등록부는 §13 에서 되돌림(위 복도 별도 장소) |
| 다음에 알아보는 법 | 검증된 목표를 '가까워서' 합치거나 옮길 때는 그 목표로 가는 경로가 좁은 곳을 지나는지 보고, 지나면 합치지 않거나 오프라인 계획으로 경로 차를 먼저 잰다 |
| 스크립트 핵심 · 나온 결과 | 아래 |
| 데이터 | [`plan_x_C.txt`](../debug_log/2026-10-28/outputs/plan_x_C.txt) · [`leg_compare_C.txt`](../debug_log/2026-10-28/outputs/leg_compare_C.txt) · 도구 [`anal_plan_x.py`](../debug_log/2026-10-28/jobs/anal_plan_x.py) · [`anal_leg_compare.py`](../debug_log/2026-10-28/jobs/anal_leg_compare.py) |

```
# outputs/plan_x_C.txt — 같은 시각 /plan 두 개씩(§6-6 참고)
## f2pl4 C
    +0.0 s   77 점 1.94 m  … | y -3.2: x -1.891 · y -2.9: x -1.921 · y -2.6: x -1.898 · …
    +0.0 s   26 점 1.87 m  … | y -3.2: x -1.796 · y -2.9: x -1.793 · y -2.6: x -1.742 · …
## f2tt2 g6
    -0.0 s   75 점 1.90 m  … | y -3.2: x -1.915 · y -2.9: x -1.941 · y -2.6: x -1.894 · …
    +0.0 s   25 점 1.79 m  … | y -3.2: x -1.836 · y -2.9: x -1.837 · y -2.6: x -1.780 · …
# outputs/leg_compare_C.txt
== f2pl4_C : 소요 31.3 s · 이동 1.78 m · 출발 (-1.73, -3.81, 102°) → 끝 (-1.65, -2.13, 68°) · 목표 (-1.60, -2.00) 끝 거리 0.136 m
   국면: 전진 29.5 s · 제자리 회전 1.3 s · 정지 0.5 s | 평균 전진 속도 0.060 m/s
```

### 5.3 10-28 §16.2 — '§13.1 남쪽 띠는 13:44 이후 생긴 칸'
- F2.5 dry_run 에서 드러났지만 원인 쪽 실수라 칸 형식 원본과 해설은 [세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md) 카드. 이 카드에 남길 것은 하나: **경로 조회 실패(상태 6)가 나면 place_server 는 직선 방향으로 대체할 뿐 원인을 말해 주지 않는다** — §13.1 처럼 '좌표 문제' 로 오해하기 쉽다.

## 6. 기록 어긋남 (원문 대조, 카드 작성 중)
1. **'이동 N 개 arrived · @stop canceled' 의 N 에 @stop 명령이 들어 있다**: §7.1 '이동 명령 9 개 arrived(…), @stop 은 canceled' · §8.4 '이동 7 개' · §9.1 '이동 5 개'. 각 명령 묶음([`run_place_s1_1028.sh`](../debug_log/2026-10-28/jobs/run_place_s1_1028.sh) 23~27 행)의 이동 명령은 @stop 포함 9 · 7 · 5 개라 기대 arrived 는 8 · 6 · 4. §11 판정 '① ✔(이동 5 arrived · @stop canceled)' 도 f2pl4 원문은 **arrived 4 · canceled 1**([`place_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl4/place_s1.log)). 판정 결과(통과)는 그대로.
2. **첫 메시지 유실은 f2pl3 이 처음이 아니다**: §10 은 f2pl3(13:31)을 첫 사례로 적지만, 그 전 13:16 dry_run c1 에서 첫 `where` 가 '끝 상태 없음 25.1 s' 였다([`chk_place_dry_1028c1.txt`](../debug_log/2026-10-28/outputs/chk_place_dry_1028c1.txt) 5 행). 같은 파일 끝 서버 로그엔 `[2a7a6624] info  map (-1.50, -2.00, -176°)` 가 있어 **서버는 받고 답했는데 창구가 못 받은** 경우다. §8.2 는 c1 을 −51° 재현 근거로만 인용. §10 의 '둘 중 어느 쪽인지 미확인' 에 대해 c1 = 응답 쪽, f2pl3 = 명령 쪽으로 **두 방향 다 한 번씩 있었다**(측정).
3. **게이트 C '최대 stamp 지연' 음수**: §10 은 f2pl3 의 '−0.84 s(음수)는 처음 보는 값' 이라 했지만 f2pl2 게이트(13:21:55)에 이미 `최대 stamp 지연 -1.33 s`, f2pl4 −0.92 · f2pl5 −1.19 s 도 음수(각 `place_s1.log` 3 행). 게이트 도구 쪽 해석은 [주행 전 검사 정리](drive-gate-consolidation.md) 몫.
4. **`places.yaml` 41 행 '미검증 자리 — f2pl3 에서 첫 도착'**: f2pl3 은 움직이지 않았다. −1.78 첫 도착은 f2pl4(34.1 s).
5. **설계 v0.2 와 구현의 차이**(설계 문서는 v0.2 뒤 안 고침): §3.2 '서비스 `/place/go_to` · `/place/return` · `/place/stop` · `/place/list` · `/place/register`' → 실제는 토픽 `/place/command` 하나 + `/place/status`, `register` 없음. §3.2 '러너와 겹치는 코드는 공용 모듈로' → `path_end_yaw.py` 는 job613 사본(머리 주석 2 행). §3.4 1 차 창구 `rover_say` → 없음(`place_cmd.py`). §3.2 절차 순서 '여유 검사 → 경로 끝 방향' → 코드는 방향을 먼저 정하고 그 방향으로 여유를 잰다(209 · 211 행 — 이 순서라야 §8.2 의 비스듬 자세 문제가 보였다). §4-2 '지도 바뀜 → 움직이지 않음' → 미구현(§4.1).
6. **§12.1 '경로 가로 위치 4 cm 동쪽' 은 두 /plan 중 한쪽만**: [`plan_x_C.txt`](../debug_log/2026-10-28/outputs/plan_x_C.txt) 엔 같은 시각 /plan 이 두 개(77 · 75 점, 26 · 25 점). SUMMARY 는 25~26 점 판(−1.796/−1.793/−1.742 vs −1.836/−1.837/−1.780 → 4 cm 동쪽)만 적었다. 75~77 점 판은 −1.891/−1.921/−1.898 vs −1.915/−1.941/−1.894 → 2.4 · 2.0 cm 동쪽 · 0.4 cm 서쪽. 어느 쪽을 MPPI 가 따랐는지 기록 없음. 두 /plan 중 하나는 경로 끝 방향 조회기(`path_end_yaw.py` 22 행 `planner_id = 'GridBased'`, 두 러너 모두 목표 직전에 부름)의 응답일 가능성 — **추정**.
7. **[`place_clear_upB_f2pl4.txt`](../debug_log/2026-10-28/outputs/place_clear_upB_f2pl4.txt) 한글 손상**: 파일은 UTF-8(BOM) 이지만 한글 자리가 전부 U+FFFD 로 저장돼 숫자만 남았다(이 카드 작성 중 바이트 확인). SUMMARY §13 이 인용한 '40~55° 0.124~0.111 · 가장 가까운 치명 칸 (−1.415, −2.335)' 은 숫자로는 맞음. 원문 글자는 **원천 소실**.
8. **종료 예외**: §7 '종료 예외 처리' · §16 'ExternalShutdownException 흔적 → 처리 추가' 뒤에도 f2pl4 · f2pl5 서버 로그 끝에 `rclpy._rclpy_pybind11.RCLError: failed to initialize wait set: the given context is not valid …` traceback 이 남았다([`drives/f2pl5/place_server_s1.log`](../debug_log/2026-10-28/outputs/drives/f2pl5/place_server_s1.log)). 지금 코드 272 행도 `KeyboardInterrupt` · `ExternalShutdownException` 둘만 잡는다. 러너가 `kill -INT` 뒤 3 s 에 `-9` 하는 종료 경로(33 행)에서 나는 것으로 보이며 주행 결과엔 영향 없음(추정).
9. **TOOLS.md 늦게 만듦**: [10-28 TOOLS.md](../debug_log/2026-10-28/TOOLS.md) 2 행이 스스로 '§8 시점에 늦게 만들었다' 고 적음 — §0~§7 줄은 SUMMARY 에서 옮긴 것.

## 7. 남은 것
- **T1(장소마다 go_to → return 9/10 · 도착 오차 ≤ 0.25 m · 접촉 0)** — 설계상 S1 종료 조건, 안 함.
- 판별 시험 upB(위 복도 좌표 vs 환경, §13) — 보류. 등록부엔 분리된 채 남음.
- 통로 북쪽이 여유 0.10 경계 근처(0.13~0.18 m) — 통로 안 물체(정적 지도에 없음, 정체 미확인)가 움직이면 다시 거절될 수 있다. 물체를 치우거나 정적 지도에 넣는 것은 결정 안 함(10-28 §5 후보 ②).
- 설계 §8-4(이동 중 새 명령) · §8-5(여러 단계 명령) · §8-6(모델 라이선스) — 사용자 결정 대기.
- S2(문장 세트 + 규칙 기준선) ~ S5 — 미착수. 문장 → 이동 지연(T3) · 모델 상주 자원(T4) 미측정.
- 휴대폰 실제 접속 — 미확인. 휴대폰이 WEB_DEV_5G 에 붙으면 무선 클라이언트 간 통신이 막힐 수 있다(09-23 AP 격리 추정, [Wi-Fi 카드](jetson-wifi-link.md)) — ALOPS 권장(추정).
- `place_web` 상주 기동 방식(prep 뒤 · 주행 30 s 전 금지) — 결정 대기. 또 `place_web` 의 정지 버튼은 `place_server` 가 떠 있어야만 듣는다(웹은 `/place/command` 를 낼 뿐 — 코드 60~63 행, 추론).
- 창구 `place_cmd.py` 는 명령 묶음마다 **새 DDS 참여자**를 만들고 약 1~2 s 뒤 첫 이동 명령을 보낸다(27~30 행) — '주행 30 s 전 참여자 생성 금지'([DDS 참여자 카드](pre-drive-dds-participants.md))와 어긋나는 형태. 러너는 서버 · 기록기 생성 뒤 30 s 를 기다리지만(`run_place_s1_1028.sh` 18 행) 창구 자체는 예외. f2pl4 · f2pl5 영향은 **미측정**(관찰만, 이 카드 작성 중).
- 출발 전 위치 추정 검사(10-29 ⓐ) — Jetson 배포 · 실동작 확인 안 함([드리프트 카드](stationary-yaw-drift.md)).
- 등록부 지도 이름 검사 · 경로 조회 실패 때 직선 방향 대체(§4.1 ⚠ 두 줄) — 그대로.
- 종료 때 `RCLError`(§6-8) — 고침 안 함.
- launch 통합 · colcon 설치 — 안 함. 지금 다시 돌리려면 `up_place_s1_1028.sh` 가 스크래치패드 사본을 쓰는 점(§4.1)을 먼저 저장소 판으로 바꿔야 한다.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| dry_run 1 차 · 2 차 | 출발점에서 등록부 검사(통로 북쪽 빠짐) | `jobs/up_place_dry_1028.sh` → `jobs/chk_place_dry_1028.sh` → `outputs/chk_place_dry_1028{,b}.txt` |
| dry_run c1 ~ c6 | C 에서 재현(c1) · 방향 고침(c2) · 남서에서 6 곳(c3) · 창구 수정(c4) · 출발점 경로 없음(c5) · prep 뒤(c6) | `jobs/up_place_dry_1028c.sh` → `jobs/chk_place_dry_1028c.sh` → `outputs/chk_place_dry_1028c{1..6}.txt` |
| f2pl1 | full — 통로 북쪽 거절(비스듬 자세) | `outputs/drives/f2pl1/*` · `bags/bag_f2pl1.tgz` |
| f2pl2 | fromC — 남쪽에서 통로 북쪽 거절(좌표) | `outputs/drives/f2pl2/*` · `bags/bag_f2pl2.tgz` |
| f2pl3 | fromSW — 첫 where 유실, 안 움직임 | `outputs/drives/f2pl3/*` · `bags/bag_f2pl3.tgz` |
| f2pl4 | fromSW — 명령 6/6 · 정지 시험 | `outputs/drives/f2pl4/*` · `outputs/stop_cmdvel_f2pl4.txt` · `bags/bag_f2pl4.tgz` |
| (upB) | 위 복도 판별 — 선언만, 실행 안 함 | `jobs/run_place_s1_1028.sh` 25 행 |
| f2pl5 | w3 — W3 왕복 2/2 | `outputs/drives/f2pl5/*` · `outputs/fig_place_run_f2pl5.png` · `bags/bag_f2pl5.tgz` |
| (d2) | 10-29 같은 명령 — 실행 안 함 | `2026-10-29/jobs/run_d2_1029.sh` |
| 목표 여유 재계산 | 방향별 여유 · 격자 | `jobs/anal_place_clear.py` → `outputs/place_clear_{f2pl1,f2pl2,center,upB_f2pl4}.txt` · `east_edge_history.txt` · `corridor_grid_y29.txt` |
| 칸 출처 | 라이다 · nvblox | `jobs/anal_cell_src.py` → `outputs/cell_src_f2pl2.txt` |
| 구간 비교 | 위 복도 구간 no5 대비 | `jobs/anal_leg_compare.py` · `anal_leg_env.py` · `anal_plan_x.py` → `outputs/leg_compare_{C,other}.txt` · `leg_env_C.txt` · `plan_x_C.txt` |
| 휴대폰 창구 확인 | 403/200 · POST 5/5 · PC 200 | `jobs/up_place_web_1028.sh` → `jobs/chk_place_web_1028.sh` → `outputs/place_web_chk1.txt` |
| 명령 · 결과 그림 | 지도 궤적 + 명령 표 + 시간축 | `Docs/tools/fig_place_run.py` → `outputs/fig_place_run_f2pl5.png` |

(경로는 따로 적지 않으면 `Docs/debug_log/2026-10-28/` 기준.)

## 9. 도구 해설
공통: Jetson 쪽 F2.5 도구는 PC(WSL)의 `up_*.sh` 가 스크래치패드 사본을 Jetson `~/ros2_ws/src/rover_navigation` 에 올리고(비밀번호는 `run_jn.sh` 에서 읽어 출력 안 함) Jetson 쪽 `run_*` · `chk_*` 를 부른다. 모두 **src 에서 직접** `python3 …/scripts/*.py` 로 실행(설치본 아님). dry_run = `place_server` 파라미터 `dry_run:=true` — 목표를 Nav2 에 보내지 않아 로버 안 움직임.

### 9.1 `place_server.py` — 장소 실행 노드 (Jetson, rclpy) · §7 ~ §11, 10-29 §2
- 부른 형태: `python3 $SRC/scripts/place_server.py --ros-args -p places_file:=$SRC/config/places.yaml [-p dry_run:=true]`.
- 왜: LLM 앞단 없이도 '이름 → 등록 좌표 → 이동 · 정지 · 복귀' 가 실주행에서 되는지(S1) — 모델을 붙이기 전에 실행부를 검증.
- 하는 일(저장소 판):
  1. 기동: 등록부를 읽어 이름 · 별칭을 공백 빼고 소문자로 맞춘 키로(95 행) 사전에 넣고, 겹치면 기동 실패(88~89 행). `path_end_yaw.py --serve` 를 자식 프로세스로 띄워 15 s 안 'READY' 를 기다림(101~109 행).
  2. 구독: `/global_costmap/costmap`(transient local) · `/scan` · `/map` · `/place/command`. 발행: `/place/status`.
  3. go_to: 위치(TF map→base_link) → (10-29) 위치 추정 검사 → 이미 0.15 m 안이면 arrived → 경로 끝 방향(조회기에 'GX GY 직선방향' 한 줄, 20 s 안 'YAW …' 또는 'FAIL …', 실패 · 시간 초과면 직선 방향) → 그 방향의 차체 ↔ 치명 칸 여유 → 미달이면 ±5°…±45° 중 여유 큰 쪽 먼저 비교해 기준을 넘는 첫 각 → 그래도 미달이면 rejected → NavigateToPose(frame map) → accepted · moving · arrived/failed/canceled(상태 4 · 5 · 6).
  4. `f` 모드: 0.2 s 타이머(`tick`)가 xy < 0.15 m 에서 목표 취소 → arrived(위치 도착).
  5. stop: 빈 CancelGoal → Nav2 모든 목표 취소.
  ```python
  # place_server.py 214~224 행(발췌) — §8.3 방향 고침
  if c < mc and mode != 'f' and not mode.lstrip('-').replace('.', '').isdigit():
      for k in range(1, 10):
          cand = [(self.clearance(gx, gy, gth + s * math.radians(5 * k)), gth + s * math.radians(5 * k)) for s in (-1, 1)]
          cc, ct = max(cand)
          if cc >= mc:
              why += ' → 여유 위해 %+.0f° 고침(원래 여유 %.3f)' % (math.degrees(ct - gth), c); c, gth = cc, math.atan2(math.sin(ct), math.cos(ct)); break
  if c < mc: return self.say(rid, 'rejected', pl['name'], '목표 여유 %.3f m < %.2f · 방향 %.0f° %s' % (c, mc, math.degrees(gth), why))
  ```
  ```
  # outputs/drives/f2pl2/place_s1.log
     0.1 s  accepted  통로 북쪽  목표 (-1.65, -3.70, -86°) 경로 끝 방향(77 점) → 여유 위해 -35° 고침(원래 여유 0.000) · 여유 0.10 m · 거리 1.70 m
     0.1 s  rejected  통로 북쪽  목표 여유 0.000 m < 0.10 · 방향 74° 경로 끝 방향(69 점)
  ```
- 출력: 노드 로그(러너가 `/tmp/place_server_s1.log` → 날짜 `outputs/drives/<이름>/place_server_s1.log`), `/place/status`(bag 에 기록).
- 계보: 러너 `job550` 의 목표 방향(`p`/`f`) · `job377` 목표 여유 기준을 노드로 옮김 → §8 방향 고침 · 거절 메시지 방향 → §9 장소별 `min_clear` 는 §7 부터 → 10-29 위치 추정 검사.
- 알려진 결함 · 한계: 지도 이름 검사 없음 · 경로 조회 실패 때 직선 방향으로 계속 · 여유 검사는 100 칸만(99 무시) · 이동 중 새 명령은 무조건 거절 · 종료 RCLError(§6-8) · launch 없음. ±45° · 5° 는 한 사례로 정한 값(`TODO(improve)`).
- 지금 다시: 가능(src 에서). Jetson 판은 확인 필요(§4.1).

### 9.2 `path_end_yaw.py` — 경로 끝 방향 조회기 (Jetson, rclpy, 상주) · §7
- 원본 러너 도구 `job613_pathyaw.py`(09-28 §20 · 10-13 §4)의 사본. `--serve` 면 'READY' 뒤 표준입력 한 줄마다 `compute_path_to_pose`(planner_id `GridBased`, `use_start False`) → 경로 끝에서 0.30 m 이상 떨어진 앞 점과의 방향. 출력 `YAW <rad> <점 수> <구간 m>` 또는 `FAIL <이유>`.
- 왜 따로: 같은 노드에서 경로 조회 뒤 navigate_to_pose 응답이 오지 않던 사고(f0a5 1 차) · 목표마다 새 프로세스를 띄우면 2~14 s 탐색 통신 급증(10-13 §2.1).
- 결함: 조회 자체가 planner_server 의 `/plan` 발행을 한 번 더 만든다(§6-6 의 두 /plan 후보 — 추정).

### 9.3 `place_cmd.py` — 명령 창구 (Jetson, rclpy) · §7 · §10
- 부른 형태: `place_cmd.py "where; go_to B; go_to W3 @stop20; wait 5; return" [--wait 초] [--no-wait]`.
- 하는 일: 명령마다 `'<uuid8>|<명령>'` 발행 → 같은 id 의 상태만 읽음 → 끝 상태(arrived · checked · failed · canceled · rejected · info)에서 다음 명령. 기대 상태(go_to · return → arrived/checked, @stop · stop → canceled, list · where → info)와 다르면 **뒤 명령을 보내지 않고 rc 1**. `@stopN` = moving 뒤 N 초에 stop.
  ```python
  # place_cmd.py 27 · 52~53 행 — §10 수정
  while (pub.get_subscription_count() == 0 or n.count_publishers('/place/status') == 0) and time.time() - T0 < 10: rclpy.spin_once(n, timeout_sec=0.1)
  if head in ('where', 'list') and last is None and time.time() - t0 > 2.0 and not stop_sent:
      rid = send(c); stop_sent = True   # 조회는 되풀이해도 무해(이동 명령은 되풀이하지 않음 — 두 번 가는 일 방지)
  ```
  ```
  # outputs/drives/f2pl3/place_s1.log(수정 전) → f2pl4(수정 뒤)
  >> where
  << where → 끝 상태 없음 (기대 info) 5.0 s
  >> where
     0.0 s  info    map (-1.44, -5.36, -114°)
  ```
- 계보: 첫 판 61 행(`f56a619d`) → 67 행(`e0bcbcce`, 양방향 확인). 첫 수정판은 Humble 에 없는 `Subscription.get_publisher_count()` 를 써서 dry_run 에서 예외 → `node.count_publishers()`(§10).
- 결함: 이동 명령의 첫 메시지 유실은 여전히 되보내지 않는다(설계 의도 — 대신 5 s · 300 s 기다림 뒤 rc 1). 새 참여자 문제(§7).

### 9.4 `run_place_s1_1028.sh` · `up_place_s1_1028.sh` — S1 실주행 러너 (Jetson · PC) · §7.1 ~ §14
- PC: `bash up_place_s1_1028.sh <이름> <PLAN>` — 스크래치패드 `f25_place_server.py` · `f25_place_cmd.py` · `f25_path_end_yaw.py` · `f25_places.yaml` 을 Jetson src 에 올리고, `git hash-object` 10 자리를 찍고, Jetson 러너를 `setsid nohup` 으로(PC 끊겨도 계속, 10-28 §3.1) 띄운 뒤 3 s 마다 로그를 따라보고 끝나면 로그 · bag · nav2/slam/sensors 로그 회수.
- Jetson: 게이트(`/tmp/chk_drive_gate.py`, B · C OK 그리고 G2 ≥ 0.10 m 아니면 '주행하지 않음') → place_server · bag 기록기(`/tf` best effort 재정의, `/place/status` · `/place/command` 포함) · tegrastats → **30 s** → PLAN 명령 묶음 → 정리(`kill -INT` → 3 s → `-9`).
- PLAN(22~28 행): `full` · `fromC` · `fromSW` · `upB` · `w3`.
- 출력: `/tmp/place_s1.log` 등 → `outputs/drives/<이름>/`. 결함: 스크래치패드 사본 의존(§4.1), 창구 참여자(§7).

### 9.5 `chk_place_dry_1028.sh` · `chk_place_dry_1028c.sh` (+ `up_place_dry_1028*.sh`) — dry_run 검사 (Jetson) · §7 ~ §14
- dry_run 서버를 띄우고 12 s 뒤 명령마다 **새 `place_cmd.py` 프로세스**로(`--wait 25`) 보냄. `c` 판은 9 행 목록을 날마다 바꿈(c3 남서에서 6 곳, c5 · c6 위 복도 포함 7 곳). 결과 = 창구 출력 + 서버 로그 끝 25 줄.
- 결함: 손 목록(§5.1) · 명령마다 새 참여자(c1 의 첫 where 유실도 이 형태에서, §6-2) · 실행 자리 = 그때 로버 자리라 실주행 출발 자리와 다를 수 있음.

### 9.6 `anal_place_clear.py` — 목표 여유 오프라인 재계산 (PC, rosbags) · §8 · §9 · §12 · §13
- 부른 형태: `anal_place_clear.py bag폴더 날짜 시각 gx gy [방향들]`.
- 하는 일: 시각 직전의 `/global_costmap/costmap` 판에서 ≥ 100 칸까지의 차체 직사각형 바깥 거리(place_server `clearance` 와 같은 식, 0.26 × 0.175) · 가장 가까운 칸 · 그 칸의 `/map` 값(≥ 65 점유) · 차체 안 치명 칸 수 → 방향별 한 줄. 목표 둘레 ±0.5 m 문자 격자(`#` 치명 · `+` 99 · `:` 1~98 · `.` 0 · `?` 미지 · `@` 목표).
- 출력 발췌는 §2 · §5.2. 결함: 격자 범위 ±0.5 m 고정 — §16.2 의 '범위 다른 두 격자 비교' 실수가 이 도구 출력에서 나옴([드리프트 카드](stationary-yaw-drift.md)). `place_clear_upB_f2pl4.txt` 는 저장 과정에서 한글 손상(§6-7).

### 9.7 `anal_cell_src.py` — 한 칸의 출처 (PC, rosbags) · §9
- 한 칸 (x, y) 의 전역 값을 판마다 + 그때 nvblox 슬라이스 거리(odom) · 직전 1 s 라이다 점 중 5 cm 안 개수(map→odom→base_link→센서 변환은 10-28 §5 `anal_corridor_cell.py` 와 같음).
  ```
  # outputs/cell_src_f2pl2.txt 머리
  칸 (-1.465, -3.735) — 판 시각 | 전역 값 | 로버 map | nvblox 거리(odom 슬라이스) | 라이다 점 5 cm 안(직전 1 s)
    13:22:06.02 |  99 | (-1.50, -2.01) | nan | 0
  ```
  (로버가 통로를 지나는 동안 라이다 27~184 점 — SUMMARY §9 표.)

### 9.8 `anal_leg_compare.py` · `anal_leg_env.py` · `anal_plan_x.py` — 구간 비교 (PC) · §12
- `anal_leg_compare.py --bag 폴더 시작 끝 gx gy 이름` / `--csv job550csv 목표번호 gx gy 이름`: 10 Hz 로 맞춘 map 자세 · 지령으로 소요 · 이동 · 국면(전진 |v| ≥ 0.02 · 제자리 회전 |v| < 0.02 & |ω| ≥ 0.05 · 정지) · 목표 0.30 / 0.15 m 안 처음 시각.
- `anal_leg_env.py bag 시작epoch 길이 이름`: 0.5 s 마다 지령 v · 직전 1 s `/cmd_vel` 수 · 로컬 치명(≥ 99) ↔ 차체 · 라이다 ↔ 차체(odom). 주의: 출력의 '로컬 치명 0.000' 은 ≥ 99 를 세어 내접 띠가 차체에 닿는 값이라 장애물 거리로 읽으면 안 됨(이 카드 작성 중 출력 보고 판단, 추정).
- `anal_plan_x.py bag 시작 끝 y1,y2,…`: 창 안 `/plan` 마다 y 값별 x. 같은 시각 두 /plan 을 둘 다 찍는다(§6-6).

### 9.9 `Docs/tools/fig_place_run.py` — 명령 · 결과 그림 (PC, 상시 도구) · §14.1
- 부른 형태: `fig_place_run.py bag폴더 places.yaml 출력.png [제목] [nav2.log]`.
- 하는 일: bag 의 `/place/command` · `/place/status` · `/tf` · `/map` · `/cmd_vel` + 등록부 → 위 왼쪽 지도 위 명령별 궤적(Okabe–Ito 8 색 순서 고정) · 위 오른쪽 명령 표(끝 상태 · 소요 · 서버 설명) · 아래 시간축(명령 막대 · 상태 사건 · `/cmd_vel`). nav2.log 를 주면 'PathBlockedAhead … →'(막힘 재계획) · 'Aborting'(중단) 줄의 epoch 를 세로선 · 지도 표시로.
- 출력: [`fig_place_run_f2pl5.png`](../debug_log/2026-10-28/outputs/fig_place_run_f2pl5.png). f2pl4 bag 으로도 그려짐(§14.1, 출력 파일은 저장 안 함).
- 지금 다시: 가능. 결함: 글꼴 `Malgun Gothic` 고정(Windows PC 전제).

### 9.10 `place_web.py` · `up_place_web_1028.sh` · `chk_place_web_1028.sh` — 휴대폰 창구 (Jetson, rclpy + 표준 라이브러리 HTTP) · §16
- 하는 일: `ThreadingHTTPServer` 0.0.0.0:8080. `GET /` 페이지 · `/api/places` · `/api/state?after=`(상태 기록 40 개 · 배터리 · 구독자 수), `POST /api/cmd {"text": …}` → `/place/command` 에 `'w<7자리>|<text>'`. 모든 요청은 키 비교(불일치 403). 페이지: 장소 버튼(4 s 안 두 번), 아래 고정 정지(한 번), 직접 입력, 1 s 마다 상태 조회 · 끊기면 빨간 띠.
- 키: Jetson `~/.config/rover_web/key`(저장소 밖, 0600, 없으면 노드가 만듦). **키 값은 어떤 기록에도 없다** — 확인 도구는 `K=$(cat …)` 변수로만 쓰고 출력엔 '권한 600 · 길이 N' 만 찍음(`chk_place_web_1028.sh` 10 행), 서버 기동 로그도 키 자리를 `<키 — 파일경로>` 로 찍는다(코드 165 행). `outputs/place_web_chk1.txt` 에 키 · 키 붙은 주소 없음(이 카드 작성 중 확인).
- 확인 결과 발췌:
  ```
  # outputs/place_web_chk1.txt
  키 없이 / → 403
  키 있음 / → 200 · 5693 B · title <title>로버 명령
  places → {"places": ["출발점", "B", "C", "위 복도", "통로 북쪽", "남서", "W3"], "home": "출발점"}
    4 rejected 없는곳 등록되지 않은 장소
    5 canceled None 정지 요청 — Nav2 목표 전부 취소
  == PC(WSL)→Jetson:8080 키 있음 → 200 0.015355s
  ```
- 한계: 평문 HTTP · 키 하나(주소에 키를 붙이면 브라우저 기록에 남음) · Wi-Fi 의존 보조 정지 · 휴대폰 미시험 · 종료 예외 처리 미확인 · 상주 기동 방식 미정.

## 10. 용어
- **장소 등록부(places.yaml)**: 이름 · 별칭 → map 좌표 · 방향 방식의 표. 좌표의 유일한 출처 — LLM · 창구는 이름만 고른다.
- **dry_run**: place_server 가 검사(경로 끝 방향 · 여유)까지만 하고 목표를 보내지 않는 모드, 끝 상태 'checked'.
- **경로 끝 방향(`p`)**: 목표 직전 계획 경로 끝 0.3 m 구간의 방향을 목표 방향으로 쓰는 규칙(09-28 §16). `f` = 같되 0.15 m 안이면 방향 맞춤 없이 끝.
- **명목 자세**: 보낸 목표의 (x, y, 방향) 그대로의 자세. 실제 로버는 방향 허용 안에서 다르게 설 수 있다(§3 첫 줄).
- **목표 여유**: 목표 자세의 차체 직사각형(0.52 × 0.35 m)과 전역 코스트맵 치명(100) 칸 사이 최소 거리.
- **S0 ~ S5 · T1 ~ T5**: 설계 §7 단계 · §6 시험(T1 장소 이동 9/10, T2 문장 세트, T3 지연, T4 자원, T5 통합).
