# 배터리 · 전원 운용 — 방전으로 Jetson 이 같이 꺼짐 (1 시기: 08-26 ~ 09-03, 3 시기 메모: 09-15 ~ 09-18)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 규칙 | 관련 문제 |
|---|---|---|---|---|
| **보류**(운용 규칙으로 대응 · 하드웨어 대책 없음) · '12.0 V 아래에서 데드밴드 증가' 는 측정 없는 추정 | 08-26 ~ (이 카드는 09-03 까지) | [08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md) "배터리 11.71V — 충전 필요" | 저장소 코드 변경 없음. 기동 · 점검 스크립트에 `/battery` 전압 출력 줄(`job20a_boot` · `job18a_precheck` 등). 계획 문서 [`NAV2_EXPLORATION_PLAN.md`](../04_navigation/NAV2_EXPLORATION_PLAN.md) P5 · §6.2 '테스트 전 배터리 ≥ 12.0 V 체크리스트' · '전압 연동 하한'(미구현) | [첫 SLAM 지도](first-slam-map.md)(08-31 밤 진단이 방전으로 무산) · 휠 오도 스케일(09-01 검증 직전 다운, 카드 예정) · 기동 데드밴드 · 스톨 래치(09-02~03, 카드 예정) |

**한 줄**: 로버 배터리가 Jetson 까지 먹인다(제어보드의 12 V Orin 라인 — [`PROJECT_OVERVIEW.md` §3.4](../../PROJECT_OVERVIEW.md)). 그래서 주행 중 전압이 떨어지면 모터만 약해지는 게 아니라 **Jetson 이 꺼져 스택 전체가 내려가고 그날 실험이 끊긴다**. 이 시기에 그런 중단이 두 번(08-31 밤, 09-01 세션 3) 있었고, 그 전 08-28 에도 11.71 V 에서 '충전 필요' 로 멈췄다. 대응은 운용 규칙(작업 전 충전 확인 · 스크립트마다 전압 출력 · 테스트 전 ≥ 12.0 V)뿐이고, 09-03 에 적은 '12.0 V 아래로 가면 데드밴드가 커질 수 있다' 는 **측정 없이 한 추정**이다.

> 읽는 법: 08 월 기록은 § 번호가 없어 '날짜 + 제목 글자' 로 인용. 전압은 보드가 내는 `/battery`(`sensor_msgs/BatteryState`, 1 Hz — PROJECT_OVERVIEW 토픽 표) 한 번 읽은 값. 부하 상태(주행 중)인지 정지 상태인지 대부분 기록 안 됨 — 표에 아는 만큼 적었다. 배터리 화학 · 용량 · 방전 차단 전압은 **미확인**(PROJECT_OVERVIEW §3.6 '정확한 셀 화학, 용량 미확인' — 그 절은 대형 플랫폼 기준이라 이 소형 로버의 배터리 사양은 기록이 없다).

## 1. 증상
- 08-28: 회전 지도 직후 11.71 V → "충전 필요"(같은 날 아침 12.09 V).
- 08-31 저녁: "배터리 방전 말기(정지 12.17V이나 부하 시 전압 처짐 → 모터 약함). 충전 필요." → 이어서 "⚠ 배터리 완전방전 → Jetson 재부팅·스택 다운. 라이브 진단은 충전 후."([08-31 '조이스틱 속도 상향' · '루프클로저/드리프트 재확인'](../debug_log/2026-08-31/SUMMARY.md)). 그 직전 진단 `job13` 은 지도 · 파라미터 전부 빈 값.
- 09-01 세션 3: VX_SCALE 0.783 을 적용 · 재시작까지 해 놓고 "**검증 주행 직전 배터리 방전으로 Jetson 다운 → 검증 미완**"([08-31 파일 '★★ 중대 정정' 조치](../debug_log/2026-08-31/SUMMARY.md)). 09-02 첫 줄 "어제 검증 직전 배터리 방전으로 중단됐던 항목".
- 09-02 '다음 단계' 6: "배터리 운용: 방전으로 Jetson 다운이 반복됨 → 작업 전 충전 확인, 장시간 테스트 시 전원 대책 필요."

## 2. 흐름 — 전압 기록 (시간순)
| 날짜 · 때 | 전압 | 상태(아는 만큼) | 무엇에 이어졌나 | 데이터 |
|---|---|---|---|---|
| 08-26 | 12.12 V | Step 1~3 중 | — | [08-26 '결과 (수치)'](../debug_log/2026-08-26/SUMMARY.md) |
| 08-28 아침(재부팅 뒤) | 12.09 V | 정지 | — | [08-28 '결과 (수치)'](../debug_log/2026-08-28/SUMMARY.md) |
| 08-28 보드 리셋 뒤 | 11.96 V | 정지 | — | [`job7b_after_reset.txt`](../debug_log/2026-08-28/outputs/job7b_after_reset.txt) |
| 08-28 | 11.90 V | 정지(회전 시도 사이) | — | [`job7d1_session_slam.txt`](../debug_log/2026-08-28/outputs/job7d1_session_slam.txt) |
| 08-28 | 11.84 V | 정지 | — | [`job7e_reset_clearance.txt`](../debug_log/2026-08-28/outputs/job7e_reset_clearance.txt) |
| 08-28 11:23 | 11.80 V | 정지 | — | [`job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt) |
| 08-28 11:42 직전 | **11.71 V** | 정지 | 360° 회전 1 회 뒤 '충전 필요' → 3 일 충전(그동안 Jetson 전원 사이클) | [`job7e2_reset_slam.txt`](../debug_log/2026-08-28/outputs/job7e2_reset_slam.txt) |
| 08-31 시작 | 12.18 V('완충') | 정지 | — | [`job8e_prep.txt`](../debug_log/2026-08-31/outputs/job8e_prep.txt)(12.177) · [08-31 '결과 (수치)'](../debug_log/2026-08-31/SUMMARY.md) "11.7V(방전) → 12.18V(완충)" |
| 08-31 16:55 | 12.20 V | 정지(보드 리셋 뒤) | — | [`job10b_reset_slam.txt`](../debug_log/2026-08-31/outputs/job10b_reset_slam.txt) |
| 08-31 마무리 | 12.17 V | 정지. 부하 때 처짐 · 모터 약함(관찰, 부하 전압 기록 없음) | '충전 필요' | [`job12_speed_change.txt`](../debug_log/2026-08-31/outputs/job12_speed_change.txt) |
| 08-31 밤 | — | **Jetson 다운** | 라이브 드리프트 진단 무산 | [`job13_drift_diag.txt`](../debug_log/2026-08-31/outputs/job13_drift_diag.txt)(전부 빈 값 · NO_MAP) |
| 09-01 | 12.07 V | 정지(직진 2 m 사전 점검) | — | [`job18a_precheck.txt`](../debug_log/2026-08-31/outputs/job18a_precheck.txt) |
| 09-01 세션 3 | — | **Jetson 다운** | VX_SCALE 0.783 검증 미완 → 09-02 로 | 출력 원문 없음(SUMMARY 문장) |
| 09-02 09:41 | 12.28 V | 정지(충전 뒤 부팅) | — | [`job20a_boot.txt`](../debug_log/2026-08-31/outputs/job20a_boot.txt)(09-02 실행이지만 08-31 폴더에 저장됨) |
| 09-02 마감 | 측정 안 함 | — | 종료 스크립트가 '측정불가' 를 고정 문구로 출력 | [`job31_shutdown.txt`](../debug_log/2026-09-02/outputs/job31_shutdown.txt) |
| 09-03 09:31 | 12.33 V | 정지(부팅) | — | [`job32a_boot.txt`](../debug_log/2026-09-03/outputs/job32a_boot.txt) |
| 09-03 | 12.09 V | 정지(데드밴드 스윕 뒤 손으로 옮김) | — | [`job33a_reset.txt`](../debug_log/2026-09-03/outputs/job33a_reset.txt) |
| 09-03 오후 | 12.28 · 12.12 V | 정지 | — | [`job34a_boot.txt`](../debug_log/2026-09-03/outputs/job34a_boot.txt) · [`job34e_stuckdiag.txt`](../debug_log/2026-09-03/outputs/job34e_stuckdiag.txt) |
| 09-03 18:30 무렵 | 11.99 V | 정지(새 펌웨어 플래시 뒤) | — | [09-03 '플래시 + Jetson Wi-Fi'](../debug_log/2026-09-03/SUMMARY.md)(원문 출력 없음) |
| 09-03 '부수 발견 (운영)' | 12.09~12.33 V | — | "어제 관찰대로 12.0V 아래로 가면 데드밴드가 커질 수 있음" | [09-03 SUMMARY](../debug_log/2026-09-03/SUMMARY.md) |

**같은 날 안에서 본 하강 (10-29 계산)**: 08-28 아침 12.09 → 11:42 직전 11.71 V(약 3 시간, 회전 시도 몇 번 · 대부분 정지 대기). 08-31 은 12.18 → 12.17 V 로 정지 전압이 거의 그대로인데 '부하 때 처짐 · 모터 약함' 이 보였고 몇 시간 뒤 다운 — **정지 전압은 남은 용량의 지표로 약했다**(같은 12.17 V 에서 몇 시간 안에 다운). 부하 전압 · 전류 기록이 없어 정량은 미확인.

**3 시기(09-15 ~ 09-18) 메모 — 방전 다운 기록 없음, 전압은 게이트 줄에 한 번씩만**
| 날짜 · § | 전압 | 상태 | 무엇에 이어졌나 | 데이터 |
|---|---|---|---|---|
| 09-15 §0 | 기록 없음 | '충전 후 재부팅' → 러너 242 개 재전송 · `job240_clean` 기동 | 충전이 하루 시작 절차로 굳음(전압 값은 안 남김) | [09-15 §0](../debug_log/2026-09-15/SUMMARY.md) |
| 09-17 §6.2 | 12.12 V | 전력 모드 25 W 전환 · 15 W 원복 중(온도 47 °C) | 25 W 제안 때 '로버 배터리 · Jetson 전원 회로 허용 전력 확인 필요' 라고 적었으나 확인 전에 원복(CPU 가 오히려 느려서) | [09-17 §6](../debug_log/2026-09-17/SUMMARY.md) |
| 09-17 §8.7 · §8.8 | 12.10 V | 재부팅 뒤 기동 · 저속 실측 | — | [`prep_lowspeed.txt`](../debug_log/2026-09-17/outputs/prep_lowspeed.txt) · [09-17 §8.8](../debug_log/2026-09-17/SUMMARY.md) |
| 09-17 §9 · §10 · §13.1 | 12.10 · 12.07 · 11.92 V | mp9 · mp10 · mp12 게이트 | 11.92 V(12.0 V 아래)에서 mp12 주행 · 성공 — 'NAV2 계획의 ≥ 12.0 V' 는 지켜지지 않았고 문제도 기록되지 않음 | [09-17 §9 · §10 · §13.1](../debug_log/2026-09-17/SUMMARY.md) |
| 09-18 §10 · §11.1 | 12.20 · 12.17 V | dy1 · dy2 게이트(아침 재부팅 뒤) | — | [`prep_dy1.txt`](../debug_log/2026-09-18/outputs/prep_dy1.txt) · [`prep_dy2.txt`](../debug_log/2026-09-18/outputs/prep_dy2.txt) |
- 이 시기의 Jetson 재부팅(09-15 · 09-17 · 09-18)은 배터리가 아니라 충전 절차 · Wi-Fi 사고 · 사용자 판단 때문이다([Jetson Wi-Fi](jetson-wifi-link.md)). 방전으로 꺼진 기록은 없다.

이후(09-04 ~ 09-14 와 09-21 ~): 다음 시기에서 채움 — 게이트 표의 배터리 항목은 '전압 기록(문턱 없음, 12.1~12.2 V 에서 주행해 옴)'([`TEST_COURSE_AND_GATES.md`](../04_navigation/TEST_COURSE_AND_GATES.md) 게이트 I), F0 코스 확장 조건 '배터리 ≥ 12.0 V'(NAV2_EXPLORATION_PLAN §7 표), 보드 전원을 끄면 Jetson 이 재부팅되는 구성(보드 OLED 작업 기록, 다음 시기).

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| Jetson 다운 = 배터리 방전 | 다운 직전 · 직후 전압 | 다운 순간 전압 기록 없음. 08-31 은 '방전 말기' 관찰 · 09-01 은 문장만 | 정황상 **지지**(사용자 관찰 · 충전 뒤 정상 복귀), 측정은 **미확인** |
| 정지 전압(12.1~12.2 V)으로 남은 시간을 알 수 있다 | 08-31 12.17 V → 몇 시간 뒤 다운 | 같은 정지 전압에서 다운 | 이 배터리에서는 **약함**(부하 전압 · 누적 사용 시간이 더 나을 것 — 추정) |
| 전압이 낮으면 기동 데드밴드가 커진다(12.0 V 문턱) | 전압별 데드밴드 측정 | **하지 않음**. 09-03 스윕은 12.09~12.33 V 에서만 | **미확인** — 09-03 의 '어제 관찰대로' 가 가리키는 09-02 기록에는 전압 · 데드밴드 관계 측정이 없다(09-02 는 '전압 강하 시 한쪽 모터 약화' 를 좌우 비대칭의 '후보 원인' 으로만 적음 — [09-02 '새 발견 — 간헐적 좌/우 트랙 속도 비대칭'](../debug_log/2026-09-02/SUMMARY.md)) |
| 부하 때 전압 처짐으로 모터가 약해진다 | 부하 전압 · duty 기록 | 없음(08-31 사용자 관찰 '모터 약함') | **미확인**. 같은 시기 08-26 '50 mm/s 유지에 duty 92~93 %(여유 거의 없음)' 이 있어 전압이 조금만 떨어져도 최고속을 못 낼 여지는 있다(**추정**) |

## 4. 조치와 효과
- **운용 규칙**(이 시기에 생긴 것):
  1. 작업 전 충전 확인 · 장시간 시험 시 전원 대책(09-02 '다음 단계' 6).
  2. 기동 · 점검 스크립트에 `/battery` 한 줄 출력(아래 §8 도구들) — 값이 기록에 남게.
  3. '테스트 전 배터리 ≥ 12.0 V 체크리스트'(NAV2_EXPLORATION_PLAN §6.2 '전기' 줄, 우선 ★0, 비용 0) · '배터리 게이트: 전압 임계 미만 시 탐사 중단 · 복귀'(같은 문서 P5 대응).
  4. 충전 전 종료 순서: 모터 0 → Jetson 노드 → agent(`job15c_shutdown` · `job31_shutdown`) — '로버 손으로 옮겨 충전 가능'.
- **계획만 하고 안 한 것**: 펌웨어 '전압 연동 하한' `MIN_eff = MIN × V_ref / V_batt`(NAV2_EXPLORATION_PLAN §6.2, ★1 묶음) — 이 시기 구현 기록 없음. 대용량 · 예비 배터리 검토(같은 문서 '배터리(P5)').
- 효과: 09-02 · 09-03 은 충전 뒤 시작해 세션 끝까지 다운 없음(12.09~12.33 V). 규칙의 효과라기보다 '충전하고 시작했다' 는 사실.
- 한계: 다운 순간을 잡는 장치가 없다(전압 기록이 스크립트 실행 때 한 점씩). 정지 전압이 남은 용량을 잘 말해 주지 않는다(§2).

## 5. 내 실수
- **'어제 관찰대로 12.0V 아래로 가면 데드밴드가 커질 수 있음'(09-03)** — 관찰로 적었지만 그런 측정은 09-02 · 09-03 기록 어디에도 없다.

| 칸 | 내용 |
|---|---|
| 하려 한 것 | 데드밴드 보상값(0.020 m/s)의 한계를 적으며 전압 영향을 함께 경고 |
| 본 것 | 09-03 스윕 수치(12.09~12.33 V 범위에서만), 09-02 의 '전압 강하 시 한쪽 모터 약화'(좌우 비대칭 후보 목록 중 하나) |
| 처음 추론 | '어제 관찰' → 12.0 V 아래 데드밴드 증가 |
| 의심한 이유(이 카드를 쓰며) | 09-02 SUMMARY 에서 전압 · 데드밴드 수치를 찾으면 없다(전압 줄은 12.28 V 하나 · 후보 목록 한 줄). 문턱 12.0 의 출처도 없음 |
| 판별 | 기록 검색만(이 카드) — 실험 없음 |
| 결론 | '12.0 V' 는 근거 없는 경계값이고 전압 → 데드밴드 관계는 **미확인**. 운용 규칙(≥ 12.0 V)은 안전 쪽 습관으로는 무해하지만 '측정된 문턱' 처럼 읽으면 안 된다 |
| 다음에 알아보는 법 | 문서에 숫자 문턱을 쓸 때 그 숫자를 낸 출력 파일을 같이 적는다(CLAUDE.md '사양 수치 출처' 원칙과 같은 것). 측정이 없으면 '가정' 이라 쓴다 |

## 6. 남은 것
- 배터리 사양(화학 · 용량 · 차단 전압 · Jetson 이 꺼지는 전압) — 미확인.
- 다운 순간 기록 수단(전압 · 시각을 계속 남기는 로거) — 없음(이 시기).
- 전압 → 데드밴드 · 최고속 관계 측정 — 없음.
- Jetson 전원 12 V 가 정격(9~19 V) 하한 근처라는 점(PROJECT_OVERVIEW §4.2 (4)) — 대책 미정.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job7b` · `job7d1` · `job7e` · `job7g` | 세션 확인 중 전압 1 점 | 08-28 — 해설 [첫 SLAM 지도 §8](first-slam-map.md#8-도구-해설) |
| `job8c` · `job8e` | 재부팅 뒤 상태 + 전압 | 08-31 시작 |
| `job10b` | 보드 리셋 뒤 세션 + 전압 | 08-31 — 해설 [첫 SLAM 지도 §8](first-slam-map.md#8-도구-해설) |
| `job12`(소실) · `job13`(소실) | 마무리 전압 · 다운 뒤 빈 진단 | 08-31 |
| `job14g_health` · `job18a_precheck` | 무동작 헬스체크 · 사전 점검 | 09-01 |
| `job15c_shutdown` · `job31_shutdown` | 충전 전 종료 | 09-01 · 09-02 |
| `job20a_boot` · `job33a_reset_noagent` · `job34e_stuckdiag` | 기동 · 재초기화 · 진단에 전압 줄 | 09-02 · 09-03 |

## 8. 도구 해설
공통: Jetson 에서 실행(PC → WSL → sshpass 러너, 원본 소실 — [첫 SLAM 지도 §8 공통](first-slam-map.md#8-도구-해설)). 전압 읽기는 거의 전부 `timeout 5 ros2 topic echo /battery --once`(전체 또는 `--field voltage`) 한 번. `/battery` 는 보드 micro-ROS 토픽이라 **보드 세션이 없으면 'does not appear' → NONE** 이 된다 — 'NONE' 은 '배터리 0' 이 아니라 '보드가 안 보임'.

### job8c — 재스탬프 배포 상태 + 배터리 (스크립트는 08-31 jobs, 출력은 08-28 outputs)
- 왜: 08-28 에 배포한 scan_restamp · slam 튜닝이 살아 있는지와, 회전 시험을 할 만큼 배터리가 있는지.
- 하는 일: scan_restamp · slam · rplidar 노드, `/scan_raw` · `/scan` hz 4 s, 5 s 동안 두 토픽의 now−stamp 평균(재스탬프 효과), slam `minimum_travel_heading` · `minimum_time_interval`, `/battery` voltage, `/wheel_odom` hz.
- 출력: [`2026-08-28/outputs/job8c_status.txt`](../debug_log/2026-08-28/outputs/job8c_status.txt) — **전 항목 빈 값, battery NONE**. 스택이 안 떠 있을 때 실행된 것(08-31 아침, 충전 중 재부팅 뒤 — **추정**: 다음 도구 `job8d` 가 '재부팅 후 전체 스택 재시작'). 출력 파일이 08-28 폴더에 있는 것은 날짜 배치 어긋남.
- 결함: 스택 · 보드 유무를 먼저 보지 않아 '빈 값' 의 이유가 출력에 안 나온다.
- 계보: → `job8e`(재기동 뒤 같은 확인).

### job8e — 재기동 뒤 배터리 · 스캔 지연 · 시작 여유 (08-31)
- 하는 일: `/battery` voltage → 5 s 동안 `/scan_raw` · `/scan` now−stamp 평균 → `/scan` 한 장으로 차체 외곽 최소 여유(공통 `clearances`).
- 출력: [`job8e_prep.txt`](../debug_log/2026-08-31/outputs/job8e_prep.txt) — 12.177 V, 100 → 52 ms, 70 cm.
- 쓰인 곳: 08-31 '배터리 12.18V(완충)' 의 출처.

### job14g_health — 무동작 헬스체크 (09-01)
- 왜: 사각형 루프 시험 전 '노드 · 토픽이 살아 있고, 배터리 있고, 새 자리에서 돌 공간이 있나' 를 로버를 안 움직이고 확인.
- 하는 일: ① 노드(rover_jupiter · ekf · scan_deskew · camera · rplidar) ② `/wheel_odom` · `/odometry/filtered` · `/scan` hz 4 s(없으면 '무발행!') ③ `/battery` 의 voltage · percentage, 없으면 `/rover/status` 에서 volt|batt 줄, 그것도 없으면 '(배터리 토픽 없음)' ④ `/scan` 한 장 → 차체 외곽 여유를 base_link 각도로 4 구역 — 앞 −45~45° · 좌 45~135° · 뒤 135~−135° · 우 −135~−45° — 각 최소(cm)와 전체 최소 ⑤ 회전 판정: 네 방향 모두 ≥ 15 cm 면 '✅ 충분', 아니면 부족한 방향.
- 출력: 원문 없음(대화에만).
- 결함: percentage 는 보드가 실제 값을 채우는지 확인 안 됨. 회전 판정 15 cm 는 제자리 회전의 모서리 궤적을 고려한 값이 아니라 현재 자세의 여유 — 회전하며 모서리가 다가가는 것은 안 봄(08-28 `job7k` 에서 시작 88.7 cm → 회전 중 16.4 cm).
- 계보: `job7e` 의 최소 여유 → 4 구역 → `job18a_precheck`(직진 판정) → 09-02 `job21c_where`(다음 카드) → 9 월 게이트.

### job18a_precheck — 직진 2 m 사전 점검 (09-01)
- 하는 일: ① joy 정리(`pkill -f joy_linux · teleop_twist_joy`, '/cmd_vel 단독화' — [조이스틱 카드](joystick-teleop.md)) ② `/battery` voltage ③ 노드 · `/odometry/filtered` hz · `map→base_link` ④ `job14g` 와 같은 4 구역 여유 ⑤ '직진 2m 판정: 앞 ≥ 230 cm'.
- 출력: [`job18a_precheck.txt`](../debug_log/2026-08-31/outputs/job18a_precheck.txt) — 12.07 V, 앞 157 · 뒤 152 · 좌 86 · 우 136 cm → '전방 부족'. `map->base_link` 칸이 비어 있음(그때 tf2_echo 가 4 s 안에 값을 못 냄 — slam 은 노드 목록에 있음, 이유 **미확인**).
- 결함: `grep -aE "voltage"` 가 BatteryState 의 `voltage` 줄과 다른 필드(예: `cell_voltage`)를 함께 잡을 수 있음 — `head -1` 로 첫 줄만(이번엔 정상).

### job12 · job13 — (스크립트 원천 소실)
- `job12` 출력의 마지막 줄 'battery(소진 확인): 12.17' — '소진 확인' 이라는 이름대로 마무리 때 남은 전압을 보려던 것.
- `job13` 은 Jetson 다운 뒤라 전부 빈 값 — [첫 SLAM 지도 §8](first-slam-map.md#8-도구-해설).

### job15c_shutdown — 충전 전 안전 종료 (09-01)
- 하는 일: `ros2 topic pub -1 /cmd_vel '{}'` 15 회 → joy_teleop · joy_linux · teleop · slam · ekf · conditioner · deskew · rplidar · realsense · base.launch · sensors.launch `pkill -f` → 2 s → `docker rm -f microros_agent` → 2 s → `ros2 node list` 로 남은 노드 → '로버 손으로 옮겨 충전 가능'.
- 출력: [`job15c_shutdown.txt`](../debug_log/2026-08-31/outputs/job15c_shutdown.txt) — '남은 노드: /camera/camera /foxglove_bridge /joy_node /robot_state_publisher /rover_jupiter /rplidar_node'.
- 결함: ① 종료 목록에 foxglove · robot_state_publisher 가 없음(출력에 그대로 남음) ② 남은 노드 확인이 2 s 뒤 그래프 조회라 '실제 생존' 과 '그래프 캐시' 를 못 가름 — `/rover_jupiter` 는 agent 를 지운 뒤에도 나와 캐시일 가능성이 큼(**추정**) ③ 배터리를 종료 **전에** 읽지 않음.
- 계보: → `job31_shutdown`(09-02, Nav2 노드까지).

### job20a_boot — 부팅 뒤 전체 기동 (08-31 jobs · 09-02 jobs 에 같은 파일)
- 하는 일: 날짜 → 잔여 프로세스 `pkill -9`(base · sensors · slam launch, 센서 노드, joy · teleop 포함) · `docker rm -f microros_agent` → base.launch(agent + robot_state_publisher) detach → 12 s → agent Up · 보드 `/wheel_odom` hz(없으면 '보드 미연결') · **`/battery` voltage** → sensors.launch(자이로 바이어스 ≈ 10 s, '정지!') → 22 s → bias 로그 → slam.launch → 10 s → 노드 · `/odometry/filtered` · `/scan` hz · conditioner 의 `VX_SCALE` 줄(grep) · odom 원점 · map→odom.
- 출력: 09-02 실행 [`2026-08-31/outputs/job20a_boot.txt`](../debug_log/2026-08-31/outputs/job20a_boot.txt)(12.28 V) · 09-03 실행 [`job32a_boot.txt`](../debug_log/2026-09-03/outputs/job32a_boot.txt)(12.33 V) · [`job34a_boot.txt`](../debug_log/2026-09-03/outputs/job34a_boot.txt)(12.28 V).
- 의의(이 카드): 매 세션 첫 전압이 이 출력에 자동으로 남게 된 것.
- 결함: 전압 문턱 판정 없음(출력만). agent 를 새로 띄우므로 보드 리셋이 따라야 하는데, '보드 미연결' 문구만 내고 리셋 안내는 없다(이 규칙은 09-11 에 정식화 — 다음 시기).
- 계보: `job8d`(08-31) → 이것 → 10 월 `prep_fast.sh` · `chk_prep.py`(배터리 항목 = 게이트 I '전압 기록').

### job31_shutdown — 충전 전 전체 종료 (09-02)
- `job15c` 와 같은 순서에 Nav2 노드(controller · planner · bt_navigator · behavior · velocity_smoother · smoother · waypoint_follower · lifecycle_manager · component_container)와 `ros2 launch` 전부를 `pkill -9` 로 추가.
- 출력: [`job31_shutdown.txt`](../debug_log/2026-09-02/outputs/job31_shutdown.txt) — 남은 노드에 Nav2 · 센서 노드가 길게 남음(2 s 뒤 조회 — 그래프 캐시일 가능성, **미확인**).
- 알려진 결함: '배터리(마지막): 측정불가(agent 종료됨)' 를 **측정 없이 고정 문구로** 출력한다 — agent 를 지우기 전에 읽었어야 했다. 그래서 09-02 마감 전압이 없다.

### job33a_reset_noagent · job34e_stuckdiag — 전압 줄이 들어간 09-03 도구 (요점)
- `job33a_reset_noagent`: 로버를 손으로 옮긴 뒤 agent 는 건드리지 않고(디버거 없어 보드 RESET 불가) EKF · slam 만 재시작. 앞머리에 agent · `/wheel_odom` · **배터리**. 출력 [`job33a_reset.txt`](../debug_log/2026-09-03/outputs/job33a_reset.txt) 12.09 V. 상세는 데드밴드 카드(예정).
- `job34e_stuckdiag`: 스톨 래치 진단 묶음 안에 '=== 배터리 ===' 한 줄. 출력 [`job34e_stuckdiag.txt`](../debug_log/2026-09-03/outputs/job34e_stuckdiag.txt) 12.12 V. 상세는 스톨 래치 카드(예정).

## 9. 용어
- **`/battery`(sensor_msgs/BatteryState)**: 보드(F405)가 micro-ROS 로 내는 배터리 상태(설계 1 Hz). 여기서는 `voltage` 만 썼다. 보드 세션이 없으면 토픽이 없다.
- **정지 전압 vs 부하 전압**: 배터리는 전류를 많이 뽑을수록 내부 저항 때문에 단자 전압이 내려간다. 서 있을 때 12.17 V 여도 모터가 돌 때 더 낮아져 모터 · Jetson 이 문턱 아래로 갈 수 있다. 이 시기 기록은 거의 정지 전압.
- **12 V Orin 라인**: Jetson 은 제어보드의 12 V 출력에서 전원을 받는다. Jetson Orin Nano 의 입력 정격은 9~19 V(PROJECT_OVERVIEW §3.4 · §4.2) — 12 V 는 하한 쪽. 배터리가 떨어지면 Jetson 이 꺼지거나 재부팅되어 ROS 스택 · `/tmp` 의 스크립트 · bag 이 함께 사라진다.
- **기동 데드밴드**: 모터가 정지 마찰을 이기고 움직이기 시작하는 최소 지령. 이보다 작은 지령은 아무 반응이 없다(09-02~03 카드 예정). 전압이 낮으면 같은 duty 에서 모터 힘이 줄어 이 문턱이 올라갈 '수 있다' — 이 시기엔 측정 없음.
- **그래프 캐시(`ros2 node list`)**: ROS2 노드 목록은 DDS 발견 정보로 만든다. 프로세스를 죽인 직후에는 목록에서 바로 안 빠질 수 있어, 종료 직후 '남은 노드' 는 실제 생존과 다를 수 있다.
