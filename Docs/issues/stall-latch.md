# 스톨 보호 래치 × 데드밴드 승격 충돌 — 접촉 없이 로버 전체가 잠김

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결(펌웨어 경로, 09-07 받침대)** — 모터 PWM 20 kHz 정정 뒤 구속 → 600 ms 판정 · 1.5 s 자동 복구 · 3 회 하드 래치 전 경로 확인. 바퀴가 도는 갇힘(벽 긁힘 · 트랙 헛돎)은 펌웨어 범위 밖 → Jetson `stuck_monitor`(별도 줄기). 09-03 Nav2 래치의 20 kHz 재현 여부는 미확인 | 08-26(전조) · 09-03 · 09-07 (09-08 ~ 09-11 은 텔레메트리로 '래치 아님' 판정에만 쓰임), 이후 09-14 ~ | [09-03 「오후 세션 — 스톨 보호 래치 × 데드밴드 승격 충돌」(L37)](../debug_log/2026-09-03/SUMMARY.md) | `firmware/rover_jupiter_fw/App/app/safety_monitor.c` · `safety_monitor.h` · `App/microros/microros_task.c`(상태 메시지) — 커밋 `42ea9579`. 문서 전체의 출처 불명 '3A' 삭제. **09-07**: `App/drivers/fg_encoder_driver.c`(`encoder_get_pulse_stats()`, CH2 하강에지 폭 계측) · `App/hal/i_encoder.h` · `App/drivers/stm32_encoder_driver.c` · `microros_task.c`(`values[]` L/R) · `safety_monitor.c/.h`(`safety_monitor_get_stall_counter()`) — 커밋 `bdbb9a8f`; `App/drivers/integrated_bldc_driver.c`(PWM 20 kHz) — `8fd76182`. 10-29 `595eec44` 주석 정정('3A' · CLAUDE.md §2) | [기동 데드밴드](start-deadband.md)(원인 쪽) · [Nav2 첫 구축](nav2-first-setup.md)(벤치마크가 막힘) · [모터 PWM 50 Hz 오적용](motor-pwm-50hz.md)(09-07 감지 무력의 원인) |

**한 줄**: 데드밴드 보상으로 작은 바퀴 명령을 0.020 m/s 로 올렸더니, 그 값이 펌웨어 스톨 감지 문턱(지령 > 0.015 m/s) 바로 위라, 부하 때문에 잠깐 못 움직인 바퀴가 '600 ms 동안 3 mm 미만' 조건에 걸려 **스톨 fault 가 래치**됐다. 래치는 UART5 CLI 의 'c' 나 리셋으로만 풀리는데 ROS 쪽 해제 수단이 없어 Nav2 는 회복할 수 없었다(MPPI · RPP 각 1 회, 물리 접촉 없음). 09-03 저녁에 판정을 '지령 속도' 에서 '실제로 넣은 duty ≥ 0.60' 기준으로 바꾸고, 래치를 '1.5 s 정지 후 자동 재무장, 10 s 안에 3 번이면 하드 래치' 로 바꿨다. 처음 낸 안(지령 문턱 0.015 → 0.040)은 근거가 '드라이버 내장 3A 차단' 이었는데 그 사양의 출처가 없어 철회했다. 09-07 에 'UART5 CLI 경로는 배선이 없어 애초에 동작하지 않았다' 는 정정이 붙었다. **09-07 받침대 검증**: 처음엔 트랙을 나무토막으로 고정해도 감지가 안 됐다(바퀴 속도 14~28 mm/s 로 보고). 휠별 텔레메트리(`/rover/status values[]`)를 넣어 보니 서 있는 바퀴의 FG 펄스 주기가 20.0 / 10.0 ms 로 PWM 50 Hz 에 묶여 있었고, 오전엔 'FG 기반 감지의 근본 한계' 로 결론 냈다가, 원인이 **모터 PWM 50 Hz 오적용**임을 찾아 20 kHz 로 바꾸자(Run J) 구속 바퀴 펄스 0 → 판정 3 회 → 하드 래치까지 처음으로 설계대로 동작했다([PWM 카드](motor-pwm-50hz.md)). 같은 날 MPPI 벽 긁힘 사고에선 바퀴가 계속 돌아 펌웨어 감지가 안 걸렸고(정상), 이 몫은 Jetson `stuck_monitor` 로 넘어갔다. 09-09 에는 텔레메트리 `sc=0` 으로 '로버 무이동 = 래치 아님' 을 바로 판정했다.

---

## 1. 증상
- 09-03 MPPI Run 1(복도, 정면 1.6 m): t≈48 s 부터 (1.14, 0.38) 에서 `v = −0.02, w = −0.20` 명령을 100 초 동안 반복했는데 로버 무반응. 사용자 확인: 벽과 14 cm, **물리 접촉 없음**. `/rover/status` = level 2 `STALL fault — reset required`. [09-03 「경과」 L39](../debug_log/2026-09-03/SUMMARY.md) · `2026-09-03/outputs/job34d_mppi_run1.txt` · `job34e_stuckdiag.txt`
- 보드 리셋 뒤 RPP Run 2(복귀 180° + 1.46 m): 180° 회전은 성공, 주행 중 선회에서 멈춤 → BackUp 복구는 `Collision Ahead` 로 거부 → TIMEOUT, 남은 122 cm. 사방 ≥ 55 cm, 접촉 없음. `/rover/status` level 2. [09-03 「벤치마크 재개 결과」 L61](../debug_log/2026-09-03/SUMMARY.md) · `job35c_rpp_run2.txt` · `job35d_diag.txt`

## 2. 흐름 (시간순)
| 날짜 · 제목 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-26 (펌웨어 주석 · 커밋 `1cefd2c8`) | 1:90 모터 교체 뒤 스톨 감지 재조정 | 기동이 느려(정지 → 20 mm/s 에 300 ms+) 200 ms 창에서 고속 지령 오탐 → 창 600 ms. FG 속도 추정이 펄스 하나에도 ~30 mm/s 튀어 '연속 저속' 카운터가 리셋 → **누적 이동거리 판정**(600 ms 에 < 3 mm)으로 변경. 옛 문턱 50 mm/s 는 V_MAX 보다 커서 감지가 영영 안 켜졌음 → 15 mm/s | 600 ms 지연 허용 근거 = "진짜 구속 시엔 **드라이버 내장 3A 차단**이 1차 방어"(출처 없음 — §5) | `safety_monitor.c` 주석(`76c08343` 판) · 같은 커밋이 CLAUDE.md 에 '차단 3A' 기재 |
| 09-02 「N1 벤치마크」 | (래치 없음) | 0.015 이하 바퀴 명령은 속도 제어기가 정지로 처리(`TARGET_THRESH 0.01`)해 스톨 판정 대상 밖 | — | 코드(`speed_controller.c` · `safety_monitor.c`, `76c08343` 판) |
| 09-03 오전 | 승격 0.020 플래시 · 무부하 제자리 회전 스윕 | 스톨 0 회 | — | [데드밴드 카드](start-deadband.md) |
| 09-03 「경과」 L39 | MPPI Run 1 `job30_goalabs.sh 1.6 0 0 150` | 위 증상 ① · `job34e_stuckdiag.sh` 는 좌측 28~30 cm(중심 기준)로 '회전 방해' 와 nav2 의 `Failed to make progress` 약 25 s 간격만 보여 줌 | 사용자 확인(접촉 없음) 뒤 `/rover/status` 조회로 **원인 확정: 펌웨어 스톨 래치**(조회 출력은 파일에 없음 — 대화에만) | `job34d_mppi_run1.txt` · `job34e_stuckdiag.txt` |
| 09-03 「메커니즘(설계 충돌)」 L46 | 코드 대조 | 승격값 0.020 > 문턱 0.015 → 부하(한쪽 휠 역회전 선회 · 근접 기동)에서 승격된 휠이 정지마찰을 못 이기면 600 ms / 3 mm 충족 → **로버 전체 잠김**. 해제는 UART5 CLI 'c' 뿐, ROS 경유 없음 | 자율운용과 양립 불가한 정책 | 커밋 `42ea9579` 메시지 · `safety_monitor.c`(`76c08343` 판) |
| 09-03 「조치 · 계획」 L53 | 사용자 보드 리셋 → 재배치 → `job35a_prep.sh`(이번엔 `/rover/status` 확인 포함) | fault 상태 `message: OK` | RPP + Spin 제거 BT 로 A/B 재개. 펌웨어 묶음에 ① 스톨 하한을 승격값 위로(예 0.025) ② 비래치화 / 자동 해제 / `/rover/clear_fault` ③ 기동 보조 | `job35a_prep.txt` |
| 09-03 「벤치마크 재개 결과」 L61 | RPP Run 1 · Run 2 | Run 1 성공(20 s) · Run 2 증상 ② | 선회 안쪽 휠 0.0245 m/s 가 부하로 정지 → 600 ms / 3 mm → 래치. **결론: 스톨 래치 정책이 자율주행의 차단 항목** | `job35b_rpp_run1.txt` · `job35c_rpp_run2.txt` · `job35d_diag.txt` |
| 09-03 「펌웨어 수정 — 스톨 정책」 L69 | 처음 안: 지령 문턱 0.015 → **0.040** | 근거였던 '드라이버 내장 3A 차단' 을 사용자가 확인 — 판매 페이지 · 문서 어디에도 없음. 08-26 커밋에서 출처 없이 기재된 값 | **❌ 철회**. '3A' 를 문서 전체에서 삭제, 모델명 CHR-GM37-BLDC3650 기재(§5 실수) | 커밋 `42ea9579`(CLAUDE.md · PROJECT_OVERVIEW 등) |
| 09-03 같은 곳 | 채택 안: **duty 기준 판정**(비정지 지령 AND \|duty\| ≥ 0.60 AND 600 ms 무이동) + **1.5 s 자동 재무장, 10 s 안 3 회면 하드 래치** + `safety_monitor_is_latched()` + 상태 메시지 2 단 | 빌드 완료 | 승격값 0.020 의 초기 duty ≈ 0.37 은 판정 밖. 기대: 선회 중 순간 정체는 1.5 s 뒤 재개(Nav2 progress checker 25 s 안), 진짜 끼임은 ~5 s 안 래치(**추정**) | 커밋 `42ea9579` `safety_monitor.c` · `.h` · `microros_task.c` |
| 09-03 「플래시 + Wi-Fi」 L76 | 새 펌웨어 플래시(ST-Link V3) · `-rst` | `/rover/status` level 0 `OK`, `/wheel_odom` 50 Hz, 배터리 11.99 V | **주행 검증 안 함**(「마무리」 L84) | 출력 원문 없음(대화에만) |
| 09-03 「메커니즘」 정정 줄(09-07 추가) | — | ST-Link VCP 가 UART5(PC12/PD2)에 배선돼 있지 않아 콘솔 수신 0 바이트 | **'CLI 'c' 로 해제' 경로조차 물리적으로 없었음** — 해제 수단은 보드 리셋뿐(09-07 자동복구 정책으로 문제 자체는 해소) | [09-07 「UART5 디버그 콘솔 — 현재 배선에서 동작하지 않음」](../debug_log/2026-09-07/SUMMARY.md) |
| 09-07 「준비」 L3 | Jetson 재부팅(업타임 4 분) → `/tmp` 스크립트 14 개 재전송, `job20a` 전체 기동, 보드 리셋 없이 접속 | `/wheel_odom` 50 Hz, 배터리 12.22 V. 사용자가 로버를 받침대에 올림 | — | 출력 원문 없음 |
| 09-07 「받침대 스톨 검증」 L7 | `job40a_stalltest.py` Run 1(0.05, 안 잡음) · Run 2(0.02, 손으로 누름) · Run 3(0.02, **좌 트랙 나무토막 고정**), 각 30 s | Run 1 v 0.047~0.057(시작 2 s 제외). Run 2 v 0.011~0.031, 사용자 "모터 진동, 트랙 정지, 힘이 점점 세져 손으로 못 막음". Run 3 좌 0.0049~0.0292(대부분 0.014~0.028), 우 0.0031~0.0238. **세 회차 모두 status `OK` 만** | 「판단」: 서 있어도 ~0.02 m/s 보고 → 600 ms 에 ~12 mm → 3 mm 판정 불가. 원인(코드): FG 는 방향이 없어 `bldc_last_dir_sign()` 으로 부호 주입 → 진동 펄스도 전진 누적. "**FG 이동거리 기반 스톨 감지는 하드 구속을 못 잡는다**" — **❌ 50 Hz 에 한정(같은 날 정정)** | [`job40a_run1.txt`](../debug_log/2026-09-07/outputs/job40a_run1.txt) · [`run2`](../debug_log/2026-09-07/outputs/job40a_run2.txt) · [`run3`](../debug_log/2026-09-07/outputs/job40a_run3.txt) |
| 09-07 「판단」 L18 | 전류로 잴 수 있나 확인 | `/battery.current = NAN`, 션트 없음 — 모터 전류 측정 경로 없음 | 펌웨어가 쓸 수 있는 신호는 FG 뿐 | — |
| 09-07 「텔레메트리 펌웨어 + 서명 수집」 L25 | **플래시 2 회**: ① `values[]` L/R `tgt v d pps T cv sc` ② High 폭 `w` 추가. Run A~F(`job41a`~`f`) | A 자유 0.02: duty 43 → 57 %, pps 29 → 59. B 자유 0.05: duty 81 → 93 %, pps 90 → 179. **C 좌 구속 0.02 30 s: duty 42 → 67 %, pps 15~80, T 20.0 ms 근처 고정 구간 다수 — 감지 0**. D 구속 불확실(무효). E 이름은 `blockL005` 지만 '구속 안 함' 으로 취급. **F 좌 구속 0.05 10 s: 3.1~4.1 s duty 97~98 % · pps 125~180(트랙이 토막을 밀며 이동) → 4.57 s pps 0 → 4.80 s level 1 `STALL — auto-recovering` → 6.20 s `OK`** | 스톨 자동 복구 **첫 관측** — 판정 · 복구 · 메시지는 설계대로, 단 '펄스가 완전히 끊긴 경우에만'. 「설계 결정」: 펌웨어 정책 유지 + Jetson rover-level 정체 감지(지령 vs EKF/스캔 변위, 2 s)를 **N1 전제조건으로 격상**(CLAUDE.md 원칙 예외로 명시 — **❌ 40 분 뒤 '보조' 로 격하**) | `job41a`~`job41f`(아래 §8.6 이름 규칙) · 커밋 `bdbb9a8f` 09:34 |
| 09-07 「Run G」 L53 | 좌 구속 0.05 10 s, 0.2 s 간격 기록(사용자: 문제 시 전원 차단 대기) | 좌 2.86~3.66 s duty 78 → 92 %, pps 45~70(가짜 v 14~23) → 3.86 s 98 % · pps 29 → 4.26 s pps 0 → **4.51 s STALL level 1** → 5.91 s OK → 6.86~7.66 s 94 → 98 % 펄스 소실 → **7.71 s STALL(10 s 안 2 회째)** → 9.31 s OK. 우(자유) 같은 duty 에서 pps 100~138 | 「확정」: **하드 구속 시 duty 94~98 % 에서 FG 펄스가 끊긴다**(F 1 + G 2 재현). 감지 체인 = 적분 와인드업 → duty ≥ 94 % → 펄스 소실 → 600 ms. 저duty 한계의 원인 = 승격 0.020 이 기저 펄스 속도 0.015 와 가까워 적분이 안 쌓임 → MIN 0.030 개선안([데드밴드 카드](start-deadband.md)) | [`job41g_blockL005_10s.txt`](../debug_log/2026-09-07/outputs/job41g_blockL005_10s.txt) |
| 09-07 「Run H」 L76 | MIN 0.030 플래시 시도 → ST-Link "No STM32 target found" **실패**, 구 MIN 0.020 상태로 좌 구속 · 지령 0.03 10 s | 좌 duty 56~58 % 고정, pps 85~100, **T 10.0 ms 고정**, v 33 → 가짜 속도가 목표 30 을 채워 적분 정지. 10 s 감지 0. 우(자유) duty 53 → 75 % | 기저 펄스 **100 Hz 모드** 발견 → 0.030 철회, ≥ 0.04 권고. 근본 후보 = PWM 위상 게이팅(PWM 주파수 변경은 '사양 미확인' 으로 기각 — [PWM 카드 실수 ②](motor-pwm-50hz.md)) | [`job41h_blockL003_min030.txt`](../debug_log/2026-09-07/outputs/job41h_blockL003_min030.txt) |
| 09-07 (출력만, SUMMARY 에 절 없음) | MIN 0.040 판 플래시(커밋 없음) → 좌 구속 지령 0.02 12 s = **Run I** | 목표 40(승격). 좌 duty 64 → 98 %, 2.91 s 98 % → **3.39 s STALL** → 4.99 s OK → 7.91 s 98 % → **7.99 s STALL** → 9.39 s OK. 12 s 에 2 회(하드 래치 없음). 스톨 직후 정지 중(`tgt=0 d=0`)에도 좌 `pps 20~30 · v 7~9` 가 찍힘(3.71~4.90 s) — 해석 기록 없음(**미확인**) | Run J 비교표의 '50 Hz (Run I)' 칸 | [`job41i_blockL_min040.txt`](../debug_log/2026-09-07/outputs/job41i_blockL_min040.txt) |
| 09-07 「★ 근본 원인」 L88 · 「Run J」 L92 | PWM 50 Hz → 20 kHz 플래시(MIN 은 아직 0.040), 좌 구속 · 지령 0.02 10 s | 구속 좌 pps 0(간헐 4~10), 자유 우 duty 57~61 % · pps 150~184 · cv 0~1. 첫 status 1.81 s → **2.41 s STALL** → 4.01 OK → **5.21 s STALL** → 6.61 OK → **7.81 s `STALL latched — reset required`**(level 2). 판정 순간 좌 duty 73 · 88 · 84 % | **정책 전 경로 첫 검증.** '오전 결론' 정정: FG 감지 무력은 50 Hz 아티팩트에 한정, Jetson 감지는 '필수 전제' → '보조(트랙 슬립 · 벽 밀림)' | [`job42a_20k_blockL.txt`](../debug_log/2026-09-07/outputs/job42a_20k_blockL.txt) · 커밋 `8fd76182` 10:12 · [PWM 카드](motor-pwm-50hz.md) |
| 09-07 「UART5 디버그 콘솔」 L119 | 사용자 재현을 CLI 로 하려다 발견. COM5(STLink VCP 2) · COM6 열고 `-rst` | **수신 0 바이트**(부팅 시 `[cli] 시리얼 모터 제어 준비` + 도움말이 반드시 나가야 함). 펌웨어 설정은 정상(`__io_putchar` → `huart5` 115200, PC12 TX5 / PD2 RX5 AF8, CLI 태스크 `freertos.c:180`). 저장소 debug_log 전체에 `[cli]` 출력 기록 0 | **한 번도 검증된 적 없는 경로.** 원인(추정): ST-Link 를 SWD 4 선만 연결, VCP UART 2 선 미배선. 사용자 재현은 ROS 경유로 진행 | `jobs/rover_cli.ps1`(출력 원문 없음) |
| 09-07 「사고: MPPI 주행 중 벽 접촉 (54e)」 L331 | Nav2 벤치마크 중 MPPI 가 벽을 긁음 | 횡 −0.32 m 드리프트, 사고 후 좌 여유 30 cm. 휠은 계속 돎 | "**펌웨어 스톨 감지는 작동하지 않았고, 작동하는 것이 맞다**"(구속 아님) → 휠이 도는 갇힘은 Jetson rover-level 감시 필요 → `stuck_monitor.py`(shadow) 신설 | `outputs/job54e_mppi2.txt` · [Nav2 쪽 줄기 — 다음 시기 카드] |
| 09-07 「오늘 최종 상태」 L299 | — | 스톨 정책 'duty ≥ 0.60 · 600 ms → 1.5 s 자동복구, 10 s 내 3 회 래치 — 받침대 3 회 재현' | — | — |
| 09-08 「원인 확정 — 근접 시 깊이 소거」 L199 | 상자를 밀고 목표 도착 | 바퀴가 돌고 로버도 실제 전진 | "안전장치 무반응은 정상 — 펌웨어 스톨 · stuck_monitor 모두 감지 대상이 아님" | [09-08 SUMMARY](../debug_log/2026-09-08/SUMMARY.md) |
| 09-09 §8.13 「남은 문제 — 로버가 움직이지 않음」 L708 · §8.14 L724 | job170 무이동 TIMEOUT 진단 | 보드 `cmd_vel timeout — motors stopped`, **스톨 카운터 `sc=0`(래치 아님)**, 배터리 11.96 → 11.94 V | 텔레메트리로 래치를 **즉시 배제**(09-03 처럼 한참 다른 데를 보지 않음). 원인은 §8.14 에서 `map→odom` 갱신 정지로 정정(배터리 가설 철회) | [09-09 SUMMARY](../debug_log/2026-09-09/SUMMARY.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| MPPI Run 1 무반응 = 벽에 끼임(물리 접촉) | 사용자 육안 · `job21c_where` 거리 | 벽과 14 cm(좌90 중심 기준 28 cm), 접촉 없음 | **기각** |
| = Nav2 가 명령을 안 냄 | `job30_goalabs` 의 `/cmd_vel` 표시 | v −0.02 · w −0.20 을 계속 냄 | **기각** |
| = 펌웨어가 명령을 막음(fault) | `/rover/status` | level 2 `STALL fault — reset required` | **확인**(조회 출력은 원천 소실, Run 2 는 `job35d_diag.txt` 에 남음) |
| 래치를 건 바퀴는 '승격된' 바퀴 | 지령으로 바퀴 목표 계산(아래) · 휠별 텔레메트리 | 계산상 MPPI Run 1 정지 지령에서 좌측이 승격 +0.020, RPP Run 2 는 안쪽 바퀴 0.0245(승격 아님, 문턱 바로 위). 어느 바퀴가 실제로 섰는지는 텔레메트리가 없어 모름 | **부분 지지** — 정확히는 '승격값 또는 그 근처의 저속 명령 + 부하' |
| 지령 문턱만 올리면(0.040) 된다 | 근거 검토 | 그 아래 지령의 진짜 구속을 무한 방치 — 드라이버 과전류 보호 사양 미확인 | **기각(철회)** |
| duty 기준이면 '마찰 못 이김' 과 '진짜 구속' 을 가른다 | 설계 논리(정지한 휠은 적분이 쌓여 duty 상승, 그래도 안 움직이면 구속) | 09-03 은 빌드 · 플래시만 | **미확인**(09-07 받침대 검증, 다음 시기) |
| (09-07) 구속 바퀴를 손 · 토막으로 세우면 600 ms 안에 잡힌다 | Run 2 · 3 · C(50 Hz, 지령 0.02, 30 s) | 이벤트 0 — 서 있는 바퀴가 14~28 mm/s 로 보고 | **50 Hz 에서 기각** → 20 kHz 에서 지지(Run J) |
| (09-07) FG 이동거리 방식 자체가 구속을 못 잡는다(오전 결론) | 20 kHz 로 바꾼 뒤 같은 구속(Run J) | 구속 pps 0 → 3 회 판정 → 하드 래치 | **기각** — 방식이 아니라 50 Hz 기저 펄스 탓([PWM 카드](motor-pwm-50hz.md)) |
| (09-07) 승격값을 기저 펄스 속도보다 충분히 올리면(0.030 · 0.040) 50 Hz 에서도 체인이 시작된다 | Run H(목표 30) · Run I(목표 40) | 30 은 100 Hz 모드(≈30 mm/s)와 겹쳐 적분 정지 · 감지 0. 40 은 duty 98 % 까지 올라 2 회 감지 | **부분 지지** — 0.040 에서만, 그것도 펄스 소실을 기다리는 느린 체인. 20 kHz 정정으로 불필요 |
| (09-07) 판정 · 자동 복구 · 3 회 래치 로직 자체는 맞게 짜였다 | Run F · G(50 Hz, 펄스 0 순간) · Run J(20 kHz) | level 1 → 약 1.4~1.6 s 뒤 `OK`(status 5 Hz), Run J 3 회째 level 2 | **확인** |
| (09-07) 휠이 도는 갇힘(벽 긁힘)도 펌웨어가 잡아야 한다 | 54e 사고 | 휠은 돌았음 → 정의상 스톨 아님 | **기각(설계 범위 밖)** — Jetson `stuck_monitor` 로 |
| (09-09) job170 무이동 = 스톨 래치 | `/rover/status values[]` | `sc=0`, 메시지 `cmd_vel timeout` | **기각**(텔레메트리로 즉시) |

계산(코드와 로그 지령으로, 측정 아님): 바퀴 목표 `v_l = v − ω·0.1225`, `v_r = v + ω·0.1225`.
- MPPI Run 1 정지 지령 `v −0.02, w −0.20` → `v_l = +0.0045 → 승격 +0.020`, `v_r = −0.0445`. 옛 판정(지령 > 0.015)으로 두 바퀴 모두 감시 대상.
- RPP Run 2 선회 지령 `v 0.06, w 0.29` → `v_l = 0.0245`(안쪽), `v_r = 0.0955`. SUMMARY 의 '0.0245' 와 일치.
- RPP Run 2 래치 직전(t≈39~75 s): 지령 v 0.06~0.10 · w +0.03~+0.29(반시계)인데 위치는 약 9 cm, heading 은 +176.6 → +157.7°(시계 방향) — 지령과 반대로 돎. 해석 기록 없음(**미확인**).

## 4. 조치와 효과
### 4.1 옛 정책 → 새 정책 (코드 기준 비교)
| 항목 | 09-03 이전(`76c08343` 판) | 09-03 저녁(`42ea9579` 판) |
|---|---|---|
| 감시 대상 바퀴 | `|목표| > V_TARGET_THRESH 0.015` | `|목표| > 0.010`(속도 제어기 정지 문턱과 같게) **그리고** `|last_duty| ≥ STALL_DUTY_THRESH 0.60` |
| 판정 창 | 조건이 이어지는 동안 60 샘플(100 Hz × 0.6 s), 창 시작 누적거리 대비 < 3 mm 면 스톨 · ≥ 3 mm 면 창 재시작 | 같음 |
| 스톨 때 동작 | 양쪽 목표 0 · PID 리셋 · `motor_driver_stop_all()`, `s_fault = true` **영구** | 같은 정지 + 시각 기록(크기 3 링버퍼) |
| 해제 | `safety_monitor_clear()`(CLI 'c', `cli_task.c:100`) 또는 리셋 — **CLI 는 배선 없음(09-07)** | `STALL_HOLD_MS 1500` 뒤 자동 재무장(창 카운터 · 플래그 초기화). 단 가장 오래된 기록이 10 s(`STALL_LATCH_WINDOW_MS`) 안이면서 3 회째면 `s_latched = true`(하드 래치, clear · 리셋 필요) |
| `/rover/status`(5 Hz) | fault → level 2 `STALL fault — reset required` / cmd_vel 시간초과 → level 1 / 그 밖 0 `OK` | 하드 래치 → level 2 `STALL latched — reset required` / 일시 정지 → level 1 `STALL — auto-recovering` / cmd_vel 시간초과 → level 1 / 0 `OK` |

### 4.2 새 정책의 시간 감각 (코드로 계산, 측정 아님)
구속된 바퀴는 측정 속도 0 → 오차 = 목표. 적분은 매 tick `Ki 6.0 × 목표 × 0.01 s` 씩 쌓인다.
- 목표 0.020: 초기 duty ≈ 0.13 + 12×0.020 + 0.7×0.020 = 0.384 → 0.60 까지 적분 0.216 필요, 초당 0.12 → **약 1.8 s** + 창 0.6 s ⇒ 첫 스톨 ≈ 2.4 s. 재무장 때 PID 가 리셋되므로 매번 처음부터 → 스톨 ≈ 2.4 · 6.3 · 10.2 s → 3 번째가 첫 번째로부터 7.8 s(≤ 10 s) ⇒ **하드 래치 ≈ 10 s**.
- 목표 0.05: 초기 duty ≈ 0.765(이미 ≥ 0.60) → 스톨 0.6 · 2.7 · 4.8 s ⇒ 하드 래치 ≈ 4.8 s. SUMMARY 의 '진짜 끼임은 ~5 s 내 래치' 는 이쪽에 해당.
- 승격값 근처의 '정지마찰 순간 정체' 는 적분이 0.60 에 가기 전(≈1.8 s 안)에 움직이기 시작하면 판정조차 안 된다 — 이것이 duty 기준의 의도.

### 4.3 한계 (09-03 시점)
- 0.60 은 '튜닝 가능값'. 08-26 duty-속도 곡선(30 mm/s → 72 %)대로라면 정상 주행 중에도 duty 가 0.60 을 넘으므로, 판정은 사실상 '600 ms 무이동' 이 가른다(설계상 의도와 같음, 실측 확인은 다음 시기).
- 주행으로는 검증 안 함. FG 펄스로 이동을 재는 방식 자체의 한계(PWM 50 Hz 에서 회전자 떨림 펄스가 가짜 이동으로 잡힘)는 09-07 에야 드러남.
- 600 ms 창의 원래 근거('3A 차단이 1 차 방어')는 철회됐는데 창 길이는 다시 따지지 않았다.
- fault 중에도 `/cmd_vel` 콜백은 목표를 다시 쓴다. 같은 제어 tick 안에서 `speed_controller_update()` 가 duty 를 내고 바로 뒤 `safety_monitor_update()` 가 멈추는 순서라 실효 펄스는 아주 짧을 것으로 **추정**(코드 읽기, 미측정).

### 4.4 09-07 측정으로 본 새 정책 (계산 §4.2 와 대조)
| 조건 | §4.2 계산(09-03, 50 Hz FF) | 측정 | 차이의 이유(코드 · 출력 대조) |
|---|---|---|---|
| 목표 0.05 구속, 50 Hz(Run F · G) | 첫 스톨 0.6 s | 구속 후 ≈ 1.5~2 s(「확정」) — duty 가 94~98 % 에 가서 **펄스가 끊긴 뒤**에야 창이 찬다 | 계산은 '구속 = 이동 0' 을 가정했으나 50 Hz 에선 기저 펄스가 이동으로 잡힘 |
| 목표 0.02~0.03 구속, 50 Hz(Run 2 · 3 · C · H) | 목표 0.020: ≈ 2.4 s 첫 스톨, ≈ 10 s 하드 래치 | 10~30 s 동안 **0 회** | 가짜 속도(15 · 30 mm/s)가 목표를 거의 채워 적분이 안 쌓임(duty 55~70 % 정체) |
| 목표 0.04 구속, 20 kHz, 구 FF(Run J) | 목표 0.05 류: 0.6 · 2.7 · 4.8 s | 첫 status 기준 **0.6 · 3.4 · 6.0 s**(스크립트 시각 2.41 · 5.21 · 7.81), 3 회째 하드 래치 | 초기 duty 0.64(≥ 0.60)라 첫 판정은 계산대로 0.6 s. 재무장 뒤엔 1.2 s 걸림 — 재개 직후 좌에 펄스가 조금 있어(`4.07 s pps=74 v=35`) 창이 한 번 다시 시작된 것으로 보임(**추정**). 정지 유지는 status 상 1.4~1.6 s(설정 1.5 s, 5 Hz 표본) |

- **현 펌웨어 최저 속도에서의 감각(계산, 미측정)**: 지금 FF(`DEADZONE 0.34`, `KV 5.8`)와 MIN 0.008 이면 구속 시 초기 duty ≈ 0.34 + 5.8×0.008 + 0.7×0.008 ≈ 0.39 → 0.60 까지 적분 0.21, 초당 Ki 6.0×0.008 = 0.048 → 약 4.4 s + 창 0.6 s ⇒ 첫 스톨 ≈ 5.0 s. 재무장마다 PID 리셋이라 다음은 +1.5 + 5.0 → 5.0 · 11.5 · 18.0 s — 3 회가 10 s 안에 안 들어와 **하드 래치 없이 1.5 s 정지 · 재개가 반복**될 수 있다. 의도(진짜 구속은 결국 래치)와 어긋날 수 있는 지점 — 받침대에서 확인한 적 없음.

## 5. 내 실수 — 출처 없는 '드라이버 3A 차단' 에 기댄 설계
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 승격(0.020)과 스톨 감지 충돌을 없애기 |
| 본 것 | 래치 2 회(`job34d` · `job35c`), 둘 다 접촉 없음 |
| 처음 추론 | 스톨 지령 문턱을 0.015 → **0.040** 으로 올리면 승격 구간 명령은 감시 밖이 된다. 그 아래 지령에서 진짜로 끼이면? → '드라이버 내장 3A 차단' 이 1 차로 막아 준다(08-26 에 쓴 `safety_monitor.c` 주석과 CLAUDE.md 의 '차단 3A' 를 그대로 믿음) |
| 의심한 이유 | 사용자 확인: 판매 페이지 · 문서 어디에도 3A 사양이 없음. 추적하니 08-26 커밋(`1cefd2c8`)에서 출처 없이 적힌 값 |
| 판별 | 문서 근거 확인(사용자) — 모터 모델 CHR-GM37-BLDC3650, 과전류 보호 사양 **미확인** |
| 결론 | 0.040 안 철회 → 펌웨어가 저속 지령의 진짜 구속도 잡아야 함 → duty 기준 판정. '3A' 문구를 문서 전체에서 삭제(커밋 `42ea9579`) |
| 다음에 알아보는 법 | 안전 설계의 전제가 되는 사양 수치는 **출처(데이터시트 · 판매 페이지 · 실측)를 옆에 적는다.** 출처 없는 수치를 근거로 보호 기능을 약하게 하는 변경은 하지 않는다. 지울 때는 `git grep` 으로 **코드 주석까지** 찾는다 |
| 남은 흔적 | 이 카드 작성 중 확인: **`safety_monitor.c` 18 행 주석 "진짜 구속 시엔 드라이버 내장 3A 차단이 1차 방어 → 600ms 지연 허용 가능."** 이 지금도 남아 있다(`git grep -n "3A 차단"` → 이 한 곳). 같은 파일 28 행은 "출처 불명 '3A' 삭제" 라고 적어 서로 모순. 수정은 사용자 결정 대기(이 카드는 기록만). → **10-29 커밋 `595eec44` 에서 정정됨**(18 행은 "당시 '…3A 차단…' 이라 적었으나 3A 는 출처 없는 값 — 2026-09-03 삭제 … 2026-10-29 주석 정정" 으로 바뀜, 동작 불변) |
| 데이터 | [09-03 「펌웨어 수정 — 스톨 정책」 L69~L71](../debug_log/2026-09-03/SUMMARY.md) · `git show 1cefd2c8`(3A 첫 기재) · `git show 42ea9579`(삭제 · 새 정책) · [`../../firmware/rover_jupiter_fw/App/app/safety_monitor.c`](../../firmware/rover_jupiter_fw/App/app/safety_monitor.c) |

## 5.2 내 실수 ② 받침대 결과로 '펌웨어는 저duty 구속을 못 잡는다' 고 안전 원칙까지 고침 (09-07 오전)
전체 추론 경로(서명 · 판별 · 사양 대조)는 [PWM 카드 §6 실수 ① · ②](motor-pwm-50hz.md). 여기선 스톨 설계에 남긴 영향만.
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 09-03 정책을 받침대에서 검증하고 부족하면 보완 |
| 본 것 | Run 2 · 3 · C: 구속해도 감지 0. Run F: 펄스 0 순간에만 감지 |
| 처음 추론 | 「설계 결정」: 펌웨어 정책은 유지하되 "저duty 구속은 펌웨어 단독으로 불가 → **Jetson 측 rover-level 정체 감지를 N1 전제조건으로 격상**. CLAUDE.md 원칙('안전은 펌웨어')의 예외로 근거와 함께 명시". CLAUDE.md §2 에 "⚠ 한계 … 저duty 구속은 펌웨어가 감지 불가 … Jetson 측 … 예외적으로 병행" 을 넣고 커밋(`bdbb9a8f` 09:34). 승격값 0.030 · 위상 게이팅 같은 우회책을 이어서 설계 |
| 의심한 이유 | 구속 펄스 주기가 PWM 주기(20.0 ms)와 그 절반(10.0 ms)에 정확히 묶임 |
| 판별 | PWM 20 kHz → Run J: 구속 pps 0, 3 회 판정 → 하드 래치 |
| 결론 | 펌웨어 1 차 보호 원칙은 그대로 유효. CLAUDE.md 문구를 '20 kHz 뒤 전 경로 정상 · Jetson 감지는 휠이 도는 갇힘용 **보조**' 로 되돌림(`8fd76182` 10:12). 오전에 설계한 0.030 승격 · 위상 게이팅은 폐기 |
| 다음에 알아보는 법 | 안전 원칙(CLAUDE.md)을 바꾸는 결론은 **하드웨어 설정이 사양대로라는 확인 뒤**에만 커밋한다. 받침대 한 세션의 결과로 원칙의 예외를 만들지 않는다 |
| 데이터 | [09-07 「설계 결정」 L48 · 「정정 (오늘 오전 결론)」 L114](../debug_log/2026-09-07/SUMMARY.md) · `git show bdbb9a8f -- CLAUDE.md` · `git show 8fd76182 -- CLAUDE.md` · `outputs/job41*.txt` · `job42a_20k_blockL.txt` |

## 5.3 기록 사이 어긋남 (09-07, SUMMARY ↔ 원문 출력)
- Run 2 "보고 속도 0.011~0.018 유지" ↔ `job40a_run2.txt` 의 `v` 0.0113~0.0312(10 s 이후 0.016~0.031). Run 1 "양 휠 0.047~0.057" ↔ 그 회차 도구판은 좌우를 따로 찍지 않고 `/wheel_odom` 의 `v` · `w` 만 찍었다(0.0475~0.0572, 시작 2 s 의 0.030~0.036 제외) — '양 휠' 은 v 로부터의 추정.
- Run 1~3 출력 형식이 셋 다 다르고 저장된 `job40a_stalltest.py` 의 형식(`L=… R=… | L[…] R[…]`)과도 다르다 — 도구를 그 자리에서 고쳐 가며 썼고 **앞판들은 원천 소실**(§8.6).
- `job41e_blockL005`: 이름은 '좌 구속' 이지만 SUMMARY 는 '(구속 안 함) … 자유 회전 데이터로 취급'. 출력도 자유 회전(Run B)과 같은 모양(duty 79 → 93 %, pps 95 → 180).
- Run I(`job41i`)는 SUMMARY 에 절이 없고 Run J 비교표에만 나온다. 그 표의 "duty 98 % 도달 후 ~3 s" 는 출력과 다르다(98 % → 0.5 s · < 0.1 s 뒤 판정, '~3 s' 는 출발 · 재무장 뒤 시간) — [PWM 카드 §6.5 ①](motor-pwm-50hz.md).
- 「Run J」 표의 '2.4 s → 5.2 s → 7.8 s' 는 **스크립트 시작 기준** 시각이다. 첫 status 가 1.81 s 에 왔으므로 구속 후 시간으로는 0.6 · 3.4 · 6.0 s(§4.4).

## 6. 남은 것 (09-03 시점)
- 받침대에서 손으로 바퀴를 잡아 level 1 → 1.5 s 재개 → 3 회째 level 2 확인(「내일 할 일」 2), duty 0.60 이 너무 낮 · 높은지.
- ROS 쪽 fault 해제 서비스(`/rover/clear_fault`) — 제안만.
- 휠별 duty · 목표 · 엔코더 텔레메트리 — 스톨 순간의 근거(어느 바퀴가 섰나)를 남기려면 필요(「내일 할 일」 5).
- 문서 불일치(수정 안 함, 보고만): `safety_monitor.c` 18 행의 '3A' 주석(§5). CLAUDE.md §2 '안전 메커니즘' 의 하위 줄 "스톨 감지 (200ms 윈도우, 지령 vs 엔코더 변화)" 는 08-26 이전 구현이고 바로 위 줄(duty ≥ 0.60 AND 600 ms)과 어긋난다. → 두 곳 모두 **10-29 `595eec44` 에서 정정됨**(CLAUDE.md 줄은 "스톨 감지 창 600 ms … 판정 기준은 위 duty 규칙").

### 6.1 09-07 ~ 09-11 에서 채운 것 · 남은 것
- 받침대 검증 완료(09-07): 위 '손으로 바퀴를 잡아 level 1 → 1.5 s 재개 → 3 회째 level 2' 는 Run J 에서 확인. 단 **Nav2 실주행에서 승격 바퀴 래치(09-03 증상)가 20 kHz 에서도 나는지는 이 시기에 확인 안 함**.
- 휠별 텔레메트리 — 완료(`values[]`, 09-07). 09-09 에 '래치 아님' 판정으로 바로 쓰임. 09-09 §7 대역 예산 조정에도 `/rover/status` 는 5 Hz 그대로(카드 범위 밖, [보드율 회귀 카드](microros-baud-regression.md)).
- ROS 쪽 fault 해제 서비스 — 여전히 없음. 하드 래치 해제는 보드 리셋뿐(UART5 CLI 는 배선 부재). 자동 복구 때문에 하드 래치까지 가는 경우가 드물어 실질 영향은 줄었음(**추정**).
- duty 0.60 · 600 ms · 3 mm · 1.5 s · 3 회/10 s — 20 kHz 에서 전 경로는 확인했지만 **값 자체는 50 Hz 시기 근거 그대로**(재튜닝 없음). 현 FF 에서 최저 승격 속도 구속 시 하드 래치에 안 갈 수 있다는 계산(§4.4) 미확인.
- 0.60 의 의미 변화(계산): 20 kHz · 현 FF 에서 duty ≥ 0.60 은 무부하 정상 주행 약 0.045 m/s 이상(0.34 + 5.8·v = 0.60 → v ≈ 0.045)에서 이미 충족 → 그 위에선 사실상 '600 ms 무이동' 이 판정을 가른다(설계 의도와 같음).
- 전류 측정 경로 없음(`/battery.current = NAN`) — 하드웨어 한계로 남음.
- UART5 CLI: 배선(VCP TX → PD2, RX → PC12, GND) 또는 USB-TTL 연결 시 사용 가능(선택). `rover_cli.ps1` 준비됨.
- **이후(09-14 ~): 다음 시기에서 채움** — 09-17 정지 · 스톨 문턱 0.010 → 0.005(`STALL_TARGET_THRESH = STOP`, `rover_platform.h` 한 곳으로 — [`2026-09-17/SUMMARY.md`](../debug_log/2026-09-17/SUMMARY.md) §8) · job397 저속 정지 출발 '스톨 이벤트 0(duty < 0.60)'. Jetson `stuck_monitor`(09-07 신설 → 09-08 정탐 · 활성, 09-29 자이로 우선)는 별도 줄기.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| MPPI Run 1(09-03) | 첫 래치 | 09-03 L39, `job34d_mppi_run1.txt` · `job34e_stuckdiag.txt` |
| RPP Run 1 · 2(09-03) | 성공 · 두 번째 래치 | 09-03 L61, `job35b_rpp_run1.txt` · `job35c_rpp_run2.txt` · `job35d_diag.txt` |
| 새 정책 플래시 | level 0 확인, 주행 없음 | 09-03 L76(출력 원문 없음) |
| 도구 | `job30_goalabs.sh`(09-02) · `job34e_stuckdiag.sh` · `job35a_prep.sh` · `chk_board.sh`(09-03) · (원본 없음) `job35d_diag` · 09-02 `job23a_topics` | 아래 §8 |
| 펌웨어 | `safety_monitor_update()` · `safety_monitor_clear()` · `safety_monitor_is_latched()` · `speed_controller_get_duty()` · `microros_task.c` 상태 발행 | 아래 §8.5 |
| 받침대 Run 1~3(09-07) | 텔레메트리 전, 구속해도 감지 0 | 09-07 L7, `job40a_run{1,2,3}.txt` |
| Run A~F(09-07) | 휠별 텔레메트리 첫 서명, Run F 자동 복구 첫 관측 | 09-07 L25, `job41a_free002` · `job41b_free005` · `job41c_blockL002` · `job41d_blockL002_w` · `job41e_blockL005` · `job41f_blockL005` |
| Run G · H · I(09-07) | 50 Hz 구속: 2 회 자동 복구 · 100 Hz 모드 · MIN 0.040 | 09-07 L53 · L76, `job41g_blockL005_10s` · `job41h_blockL003_min030` · `job41i_blockL_min040` |
| Run J(09-07) | 20 kHz: 3 회 → 하드 래치 | 09-07 L92, `job42a_20k_blockL.txt` |
| 54e 사고(09-07) | 벽 긁힘, 휠 회전 → 스톨 아님 | 09-07 L331, `job54e_mppi2.txt` |
| job170 진단(09-09) | `sc=0` 으로 래치 배제 | 09-09 §8.13(출력은 SUMMARY 인용만) |
| 도구(09-07) | `job40a_stalltest.py` · `run_sig.sh` · `job43_mon.py` · `rover_cli.ps1` · 텔레메트리 펌웨어(`encoder_get_pulse_stats()` · `values[]`) | 아래 §8.6~§8.10 |

---

## 8. 도구 해설
공통 사항(Jetson `/tmp` 실행 · PC→WSL→ssh 감싸개 원천 소실 · 빈칸 = 무발행 · 노드 생성 직후 주행)은 [Nav2 카드 §8.0](nav2-first-setup.md).

### 8.1 `job30_goalabs.sh` — 래치를 만난 주행 도구
상세는 [Nav2 카드 §8.10](nav2-first-setup.md). 이 문제와 관련된 점: `/cmd_vel` 의 마지막 (v, w) 만 3 s 마다 찍고 **보드 상태(`/rover/status`)를 보지 않는다** → MPPI Run 1 의 100 초 '무반응' 이 화면상으론 '명령은 나오는데 안 움직이는 배회' 로만 보였다. 위치 · heading 이 3 s 마다 그대로인 줄이 연속되면 펌웨어 쪽 차단을 의심하는 서명.

### 8.2 `job34e_stuckdiag.sh` — 정체 진단(상태 확인 빠짐)
- 위치 · 형태: Jetson, 인자 없음. [`../debug_log/2026-09-03/jobs/job34e_stuckdiag.sh`](../debug_log/2026-09-03/jobs/job34e_stuckdiag.sh)
- 왜: MPPI Run 1 타임아웃 직후, 로버가 왜 안 움직였는지 — 공간 · 컨트롤러 쪽을 먼저 의심.
- 하는 일: `/tmp/job21c_where.sh` 의 3~20 줄(전 방위 여유) → nav2.log 에서 `mppi|collision|critic|trajector|Failed|abort|recovery|spin|backup`(서비스 타임아웃 줄 제외) 마지막 12 → `/battery` 전압 → `/cmd_vel` 한 장(3 s).
- 출력: `job34e_stuckdiag.txt` — 좌60 30 · 좌90 28 · 좌후120 30 cm '회전 방해', `Failed to make progress` 4 번(약 25 s 간격) · spin 시작 → 5 s 뒤 취소(스크립트 타임아웃의 목표 취소), 12.12 V, `/cmd_vel` 빈칸(=정지).
- 결함: **`/rover/status` 를 안 봄** — 원인(래치)이 이 출력에 없다. 확정에 쓴 상태 조회 출력은 저장 안 됨(원천 소실).
- 계보: 이 빈틈 → 다음 도구 `job35a_prep.sh` 가 '보드 세션 + fault 상태' 를 첫 단계로 넣음. 지금 다시 쓰기: 안 씀.

### 8.3 `job35a_prep.sh` — 리셋 뒤 재벤치마크 준비(상태 확인 첫 등장)
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job35a_prep.sh`](../debug_log/2026-09-03/jobs/job35a_prep.sh)
- 하는 일(이 문제 관련): 1) `/tmp/chk_board.sh` + `ros2 topic echo /rover/status --once` 의 `message:` 줄 → `message: OK` 여야 진행. 나머지(EKF · SLAM 초기화, Nav2 기동, 파라미터, 공간)는 [Nav2 카드 §8.13](nav2-first-setup.md).
- 출력: `job35a_prep.txt` — agent Up 24 minutes · 49.990 Hz · `/rover_jupiter` · `message: OK`.
- 결함: 상태는 기동 전에 한 번만 본다(주행 중 감시 아님). 공통 결함 ①.
- 계보: → 이후 러너 · 게이트가 `/rover/status` 를 주행 중 기록(09-07 이후). 10-27 `chk_drive_gate.py` 의 '주행 전 검사' 로 이어짐.

### 8.4 원본 없는 출력: `job35d_diag.txt` · 09-02 `job23a_topics.txt`
- `job35d_diag.txt`(09-03, 도구 원본 없음 — 대화에서 즉석): `/rover/status` 의 `level: "\x02"` · `message: STALL fault — reset required`, nav2.log 의 `Running backup` → `Collision Ahead - Exiting DriveOnHeading` → `Running wait` → `Failed to make progress` 2 회, 전 방위 최근접 55 cm. `level` 은 `diagnostic_msgs/DiagnosticStatus` 의 byte 라 `ros2 topic echo` 가 `"\x02"` 처럼 이스케이프로 찍는다(0 OK · 1 WARN · 2 ERROR).
- `job23a_topics.txt`(09-02 오전, 원본 없음): 보드가 내는 토픽 6 종과 `/rover/status` 한 장 — `level "\x01"`, `cmd_vel timeout — motors stopped`, **`values: []`**(휠별 값 없음). 이 시기 '어느 바퀴가 섰나' 를 알 수 없었던 근거.

### 8.5 펌웨어 코드 해설
- **`safety_monitor_update()`**(`App/app/safety_monitor.c`, 100 Hz, 제어 태스크에서 `speed_controller_update()` 바로 뒤):
  1. cmd_vel watchdog: 한 번이라도 받은 뒤 500 ms(`CMDVEL_TIMEOUT_MS`) 넘게 없으면 진입 순간 목표 0 · PID 리셋 · 모터 정지, `s_cmdvel_timeout = true`(래치 아님, 다음 명령에 해제).
  2. fault 중이면: 매 tick PID 리셋 + 모터 정지. (09-03 판) 하드 래치가 아니고 1.5 s 지났으면 바퀴별 창 카운터 · 스톨 플래그를 지우고 `s_fault = false`(재무장) — 다음 `/cmd_vel` 부터 구동. 그리고 return.
  3. 바퀴마다: `tgt = speed_controller_get_target()`, `duty = speed_controller_get_duty()`(직전 tick 에 실제로 넣은 duty), `dist = encoder_read_distance_m()`(FG 누적거리). 감시 조건(위 표)을 만족하면 카운터 0 일 때 창 시작 거리 저장, 60 이 되면 이동 < 3 mm → 스톨, 아니면 창 재시작. 조건이 깨지면 카운터 0.
  4. 한 바퀴라도 스톨이면: `s_fault = true`, 시각 링버퍼(3 칸)에 기록, 3 칸이 다 찼고 가장 오래된 기록이 10 s 안이면 `s_latched = true`. 양쪽 목표 0 · PID 리셋 · 모터 정지.
- **`safety_monitor_clear()`**: `safety_monitor_init()`(모든 상태 초기화) + PID 리셋. 부르는 곳은 CLI 'c'(`cli_task.c`) 하나 — 그 CLI 는 UART5 배선 부재로 실제로는 못 씀(09-07). 즉 하드 래치 해제 = 보드 리셋.
- **`speed_controller_get_duty()`**: `last_duty` 반환. 정지 목표면 0. duty 식은 [데드밴드 카드 §8.8](start-deadband.md).
- **`microros_task.c` 상태 발행**: 200 ms 마다 `is_latched()` → `has_fault()` → `cmdvel_timeout()` 순으로 level · message 를 정해 `/rover/status`(DiagnosticArray, 항목 1 개) 발행. 09-03 판까지 `values[]` 는 빈 배열.
- **창 판정 상수의 출처**: 600 ms · 3 mm(08-26, '정상 최저속 15 mm/s → 창당 9 mm ≫ 3 mm'), duty 0.60(09-03, 승격 초기 duty 0.37 보다 충분히 위), 1.5 s · 3 회 · 10 s(09-03, Nav2 progress checker 25 s 안에 회복되도록) — 모두 PWM 50 Hz 시기 값.

### 8.6 `job40a_stalltest.py` — 받침대 스톨 시험기 ★ 09-07 의 거의 모든 출력을 만든 도구
- 위치 · 형태: **Jetson** `/tmp/job40a_stalltest.py`, `python3 job40a_stalltest.py DUR VX [WZ] [LOG_DT]`(REPORT 「명령어 · 스크립트」). PC 에선 `run_sig.sh` 또는 직접 ssh 로 부름(§8.7). [`../debug_log/2026-09-07/jobs/job40a_stalltest.py`](../debug_log/2026-09-07/jobs/job40a_stalltest.py)
- 왜: 09-03 새 스톨 정책을 '손 · 나무토막으로 바퀴를 세운 상태' 에서 검증하려고. 처음엔 상태 전이만 볼 계획이었으나, 감지가 안 되자 같은 도구로 휠별 텔레메트리 서명을 모으는 데 계속 씀.
- 하는 일:
  1. 노드 `stalltest`. `/cmd_vel` 퍼블리셔(depth 10), `/rover/status`(DiagnosticArray, `qos_profile_sensor_data`) · `/wheel_odom`(Odometry, sensor QoS) 구독.
  2. `/rover/status` 콜백: 모든 `values[]` 의 key → value 를 사전 `kv` 에 덮어씀(펌웨어는 key `L` · `R` 두 개). `(level, message)` 가 직전과 다르면 `[t s] status level=… '…'` 줄을 즉시 찍고 이벤트 목록에 저장. `level` 은 byte 라 `bytes` 면 `x[0]` 으로 정수화.
  3. 주 루프(DUR 초): `spin_once(0.01)`, **0.05 s 마다 같은 `Twist(vx, wz)` 발행(20 Hz)** — 펌웨어 watchdog 500 ms 보다 충분히 촘촘. `LOG_DT`(기본 0.5, `8fd76182` 에서 인자 추가 — status 가 5 Hz 라 0.2 가 하한) 마다 한 줄: `/wheel_odom` 의 v · w 로 **B = 0.245 고정**의 차동 역산 `L = v − w·B/2`, `R = v + w·B/2` 와 `kv['L']` · `kv['R']` 문자열 그대로.
  4. 끝나면 영 Twist 10 번(0.05 s 간격) → '이벤트 요약' · '최종 status'.
- 출력: 09-07 `outputs/job40a_run{1,2,3}.txt` · `job41a`~`job41i` · `job42a` · `job42b_*` · `job42c_*`(이름 규칙은 [PWM 카드 §9.1](motor-pwm-50hz.md)). 시각은 **스크립트 시작 기준** — 첫 1~2.5 s 의 `wheel_odom 없음` 은 DDS 구독 연결 지연이라, 모터가 실제로 언제 움직이기 시작했는지는 이 시각으로 정확히 알 수 없다(첫 status 줄이 대략의 기준).
- 읽는 법: 앞의 `L=` · `R=` 는 `/wheel_odom` 에서 **도구가 역산한 값**, 괄호 안 `v` 는 **펌웨어가 FG 로 잰 휠 속도(mm/s)**. 둘은 다를 수 있다(예 Run F 4.57 s `L=0.0002` vs `v=0`). 판정에는 괄호 안 값을 본다.
- 결과가 쓰인 곳: 09-07 「받침대 스톨 검증」 · 「텔레메트리」 표 · Run F · G 타임라인 · Run H · Run J · 「20kHz 정착점」 표 → 오전 결론, PWM 원인 확정 뒤 검증, FF 재튜닝(`DEADZONE 0.34` · `KV 4.5`).
- 계보: 09-02 권고('values[] 에 휠별 값') → 이 도구 + 텔레메트리 펌웨어 → 텔레메트리 없이 지령 vs 응답만 보던 09-03 `job32b` 와 달리 '어느 바퀴가 무엇을 하나' 를 처음 직접 봄. 같은 기능의 구독 전용판 = `job43_mon.py`(§8.8). 09-07 「다음 세션 할 일」 1 은 이 도구로 stuck_monitor 정탐을 시험하자고 했으나 09-08 정탐은 다른 형식의 출력(`2026-09-08/outputs/job57_stuck_positive.txt`)으로 남았다 — 이 도구를 썼는지 **미확인**.
- 알려진 결함: ① **저장본은 마지막 판** — Run 1 · 2 출력은 `wheel_odom v=… w=…`, Run 3 은 `v=… w=… → L=… R=…` 형식이라 그 앞판들은 원천 소실(같은 파일을 덮어쓰며 고침). ② B = 0.245 고정 — 09-07 오후 펌웨어가 유효 게이지 0.409 → 0.443 으로 바뀐 뒤엔 `L=` · `R=` 역산이 틀린다(이 카드의 출력은 모두 그 전). ③ 회차마다 새 노드 → 공통 결함(노드 생성 직후 발행)과 같은 구독 지연. ④ 이벤트는 '바뀔 때만' 기록 — status 가 5 Hz 라 1.5 s 정지는 1.4~1.6 s 로 찍힌다.
- 지금 다시 쓰기: 받침대 단일 시험으로는 개념 유효. 단 `values[]` 형식이 그대로인지, B 를 현 `WHEEL_BASE_M`(0.443)으로 바꿀지 확인 필요.

### 8.7 `run_sig.sh` — PC 쪽 재시도 감싸개
- 위치 · 형태: **PC**(sshpass 사용 — 이 시기 WSL 감싸개, `Docs/tools` 이전). `run_sig.sh <출력이름> <DUR> <VX>`. [`jobs/run_sig.sh`](../debug_log/2026-09-07/jobs/run_sig.sh)
- 왜: 09-07 에도 Wi-Fi `banner exchange timeout` 이 재발(「부수 관찰」) — 한 번 끊기면 회차를 잃으므로.
- 하는 일: `sshpass -p <PW> ssh … jetson@192.168.0.101`(당시 주소, ConnectTimeout 5) 로 `source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job40a_stalltest.py $2 $3 | tee /tmp/$1.txt` 를 `timeout 90` 으로 최대 **3 번**(실패 시 2 s 대기) 시도.
- 출력: Jetson `/tmp/<이름>.txt`(재부팅 · 덮어쓰기로 휘발) + PC 화면. 저장소의 `outputs/` 는 PC 쪽에서 화면 출력을 받은 것으로 보인다 — `job42b_20k_free_004.txt` 첫 줄이 PC 쪽 오류 `ssh: connect to host 192.168.0.101 port 22: Connection timed out`(첫 시도 실패 → 재시도 성공의 흔적).
- 결함: ① 인자 두 개만 넘김 — `WZ` · `LOG_DT` 를 쓴 0.2 s 간격 회차(`job41g` 이후)는 이 감싸개가 아닌 다른 호출(원천 소실). ② `timeout 90` 이 시험 시간을 넘으면 중간에 끊긴다(30 s 회차까지는 문제없음). ③ 재시도 때 앞 시도의 부분 출력이 섞일 수 있음.
- 지금 다시 쓰기: 안 씀 — 주소가 바뀌었고(현 192.168.0.110) 실행은 `run_jn.sh` · `Docs/tools/` 체계로 바뀜.

### 8.8 `job43_mon.py` — 구독 전용 텔레메트리 모니터
- 위치 · 형태: Jetson, `python3 job43_mon.py [DUR=60] [간격=0.5]`. [`jobs/job43_mon.py`](../debug_log/2026-09-07/jobs/job43_mon.py)
- 왜: **UART5 CLI** 로 모터를 직접 돌리면서(ROS 지령 없이) 휠별 duty · pps · 주기를 보려고 — 사용자가 손으로 재현할 때 쓰려던 도구.
- 하는 일: `/rover/status` 만 구독, `values[]` 의 L · R 문자열을 간격마다 찍고, level 이 바뀌면 `>>> status …`. `/cmd_vel` 은 **한 번도 발행하지 않음** → 보드 watchdog 이 무장되지 않아(첫 명령 전엔 timeout 판정 안 함) CLI 로 돌리는 모터를 멈추지 않는다.
- 출력: 대응하는 `outputs/` 파일 없음. CLI 가 배선 부재로 안 됐으므로 의도대로 쓰이지 못한 것으로 보인다(**미확인**).
- 계보: `job40a` 에서 발행 부분을 뺀 판. 지금 다시 쓰기: CLI 배선 뒤엔 유효.

### 8.9 `rover_cli.ps1` — UART5 디버그 콘솔(Windows)
- 위치 · 형태: **PC Windows PowerShell**, `powershell -ExecutionPolicy Bypass -File rover_cli.ps1 [COM5]`. [`jobs/rover_cli.ps1`](../debug_log/2026-09-07/jobs/rover_cli.ps1)
- 하는 일: `SerialPort(COM, 115200, 8N1)` 열기 → `?` 를 보내 1.5 s 동안 받은 바이트 수를 셈 — **0 이면 "[warn] board sent 0 bytes - UART5 TX may not be wired to this VCP"**. 이후 한 줄씩 보내고 1.2 s 동안 응답, `q` 면 `s`(정지)를 보내고 닫음. 보드 명령: `b/r/l <mm/s>` 구동 · `s` 정지 · `c` fault 해제 · `e` FG 카운트 · `z` 리셋 · `?`.
- 출력: 원문 저장 없음. SUMMARY 「UART5 디버그 콘솔」 에 'COM5 · COM6 양쪽 수신 0 바이트' 로 옮겨 적음.
- 결과가 쓰인 곳: 09-03 '해제는 CLI c 뿐' 서술의 정정, 스톨 해제 경로 = 리셋뿐 확정.
- 지금 다시 쓰기: 배선만 되면 유효(도구 자체는 경고 기능까지 갖춤).

### 8.10 휠별 텔레메트리 펌웨어 — `encoder_get_pulse_stats()` · `/rover/status values[]` (커밋 `bdbb9a8f`)
- 위치: [`../../firmware/rover_jupiter_fw/App/drivers/fg_encoder_driver.c`](../../firmware/rover_jupiter_fw/App/drivers/fg_encoder_driver.c) · `App/hal/i_encoder.h` · `App/microros/microros_task.c` · `App/app/safety_monitor.c`. 플래시 2 회: ① `tgt v d pps T cv sc` ② `w`(High 폭) 추가 — `job41a`~`c` 엔 `w` 가 없고 `job41d` 부터 있다.
- 왜: 09-02 권고 · 09-03 남은 것('어느 바퀴가 섰나') + 09-07 오전 '서 있는 바퀴가 움직인다고 보고' 의 정체를 보려고.
- 하는 일(FG 캡처 ISR): TI1 상승에지(CH1) 마다 직전 캡처와의 차 = 주기 `s_period` 를 크기 8 링에 넣고, 부호 없는 총 펄스 수 `s_pulse_total` 증가. 같은 입력을 간접 매핑한 CH2 **하강에지**에서 '직전 상승에지 → 지금' = High 폭을 다른 8 링에. 입력 필터 `ICFilter 0x0F`(≈ 3 µs). 누적 카운트 `s_count` 는 여전히 `bldc_last_dir_sign()` 부호로 ±1.
- `encoder_get_pulse_stats()`(호출 = status 발행 5 Hz → **창 200 ms**): `pps = 직전 호출 이후 펄스 증가분 × 1000 / 경과 ms`(→ 200 ms 창이라 **5 pps 단위로 양자화**: 45 · 50 · 55 …). 창 안 펄스가 8 개 미만이면 `T` = 마지막 주기 1 개(펄스 없으면 0), **`cv` 는 0 으로 강제**. 8 개 이상이면 링 8 개 평균 = `T`, 표준편차/평균 × 100 = `cv`. `w` = 폭 링 8 개 평균(창에 펄스가 1 개 이상이면, 옛 값 섞임 허용 — '진단용').
- `values[]` 문자열(정수, nano printf 가 float 미지원): `tgt`(목표 mm/s, `speed_controller_get_target`) · `v`(FG 속도 mm/s, `encoder_read_velocity_mps`) · `d`(`speed_controller_get_duty` %) · `pps` · `T`(µs) · `cv`(%) · `w`(µs) · `sc`(`safety_monitor_get_stall_counter` = 현재 창 샘플 수 0~60). key `L` · `R`, 정적 버퍼 72 바이트.
- 읽는 법 · 함정: ① `sc` 는 감시 조건(목표 > 문턱 AND duty ≥ 0.60)이 이어지는 동안 0 → 60 으로 오르고, 이동 ≥ 3 mm 면 0 으로 돌아가 다시 센다(예 `job42b_006` 의 18 → 38 → 58). **스톨 중엔 60 고정**. 좌우가 같은 값으로 찍히는 건 두 바퀴가 같은 tick 에 같은 조건을 만족해서다(카운터는 바퀴별). ② `cv=0` 이 '규칙적' 이 아니라 '펄스 부족' 일 수 있다(① 의 강제). ③ `T` 가 수억 µs(예 `T=286071631`)면 긴 정지 뒤 첫 주기 — 의미 없음. 링에 그런 값이 섞이면 `cv` 가 수백 %(예 `job41g` 우 `T=56721260 cv=264`). ④ `pps` 는 호출 간격 기준이라 status 가 늦게 나가면 창이 길어진다.
- 결과가 쓰인 곳: 50 Hz 기저 펄스 서명(20.0 / 10.0 ms), Run F · G 의 펄스 소실 순간, 20 kHz 정착점 표, 09-09 '래치 아님(sc=0)', 09-17 mp8 '0.009 m/s 지령에 tgt 0 · duty 0'([데드밴드 카드](start-deadband.md) §5).
- 계보 · 지금: 이후 bag 에 `/rover/status` 를 기록하는 근거 자료가 됨. 지금도 같은 형식으로 발행(필드 변경 여부는 이후 시기에서 확인).

## 9. 용어
- **스톨(stall)**: 모터에 구동 명령 · 전력이 들어가는데 회전자가 돌지 못하는 상태. 전류가 커져 모터 · 드라이버가 과열될 수 있어 보호가 필요하다. 이 펌웨어는 전류를 못 재므로 '구동 중인데 이동 없음' 으로 간접 판정.
- **latch(래치)**: 한 번 켜지면 원인이 사라져도 명시적으로 지울 때까지 유지되는 상태. 09-03 이전 스톨 fault 는 무조건 래치, 이후는 '3 회 / 10 s' 일 때만 하드 래치.
- **re-arm(재무장)**: 보호 동작 뒤 감시를 초기화하고 다시 구동을 허용하는 것. 여기선 1.5 s 정지 뒤 자동.
- **duty 기준 판정**: '얼마나 빠르게 하라고 했나(지령)' 가 아니라 '실제로 얼마나 세게 밀고 있나(duty)' 로 구속을 판단. 정지마찰 때문에 잠깐 못 움직인 바퀴는 적분이 쌓이면서 곧 움직이므로 duty 가 0.60 에 가기 전에 풀리고, 0.60 이상으로 밀어도 600 ms 동안 3 mm 도 못 가면 진짜 구속으로 본다.
- **watchdog(cmd_vel)**: 마지막 명령 뒤 500 ms 안에 새 명령이 없으면 모터를 멈추는 펌웨어 감시. 통신이 끊겨도 로버가 계속 달리지 않게 하는 1 차 안전장치(CLAUDE.md §2).
- **DiagnosticStatus level**: 0 OK · 1 WARN · 2 ERROR · 3 STALE(byte 값).
- **데드밴드 · 승격 · 정지마찰 · duty**: [데드밴드 카드 §9](start-deadband.md).
- **FG 펄스 · 기저 펄스 · 하드 잼 · PWM 주파수**: [PWM 카드 §10](motor-pwm-50hz.md).
- **pps · T · cv · w**: 초당 펄스 수 · 펄스 주기 평균(µs) · 주기 변동계수(표준편차 ÷ 평균, %) · 펄스 High 폭(µs). 진짜 회전이면 `T` 가 속도에 반비례해 연속적으로 변하고, 50 Hz 기저 펄스면 20.0 / 10.0 ms 에 붙는다.
- **텔레메트리(`values[]`)**: `/rover/status`(DiagnosticArray)의 key–value 칸에 휠별 내부 상태를 문자열로 실어 보내는 것. 09-07 전에는 빈 배열이었다.
- **적분 와인드업 체인(09-07 의 말)**: 구속 → 오차 = 목표 → 적분이 쌓여 duty 상승 → (50 Hz 에선 duty 94~98 % 에서야 펄스 소실) → 600 ms 무이동 판정. 가짜 속도가 목표를 채우면 적분이 안 쌓여 체인이 시작되지 않는다.
- **rover-level 정체 감지**: 바퀴가 아니라 로버 전체가 실제로 움직였는지를 라이다 · 자이로 등으로 보는 Jetson 쪽 감시(`stuck_monitor`). 바퀴가 도는데 안 나아가는 경우(트랙 헛돎 · 벽 밀림)를 맡는다.
