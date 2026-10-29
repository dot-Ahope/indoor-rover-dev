# 스톨 보호 래치 × 데드밴드 승격 충돌 — 접촉 없이 로버 전체가 잠김

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **조치 완료 · 09-03 시점 주행 미검증** → 09-07 받침대에서 검증(다음 시기) | 08-26(전조) · 09-03 (이 카드), 이후 09-07 ~ | [09-03 「오후 세션 — 스톨 보호 래치 × 데드밴드 승격 충돌」(L37)](../debug_log/2026-09-03/SUMMARY.md) | `firmware/rover_jupiter_fw/App/app/safety_monitor.c` · `safety_monitor.h` · `App/microros/microros_task.c`(상태 메시지) — 커밋 `42ea9579`. 문서 전체의 출처 불명 '3A' 삭제 | [기동 데드밴드](start-deadband.md)(원인 쪽) · [Nav2 첫 구축](nav2-first-setup.md)(벤치마크가 막힘) |

**한 줄**: 데드밴드 보상으로 작은 바퀴 명령을 0.020 m/s 로 올렸더니, 그 값이 펌웨어 스톨 감지 문턱(지령 > 0.015 m/s) 바로 위라, 부하 때문에 잠깐 못 움직인 바퀴가 '600 ms 동안 3 mm 미만' 조건에 걸려 **스톨 fault 가 래치**됐다. 래치는 UART5 CLI 의 'c' 나 리셋으로만 풀리는데 ROS 쪽 해제 수단이 없어 Nav2 는 회복할 수 없었다(MPPI · RPP 각 1 회, 물리 접촉 없음). 09-03 저녁에 판정을 '지령 속도' 에서 '실제로 넣은 duty ≥ 0.60' 기준으로 바꾸고, 래치를 '1.5 s 정지 후 자동 재무장, 10 s 안에 3 번이면 하드 래치' 로 바꿨다. 처음 낸 안(지령 문턱 0.015 → 0.040)은 근거가 '드라이버 내장 3A 차단' 이었는데 그 사양의 출처가 없어 철회했다. 09-07 에 'UART5 CLI 경로는 배선이 없어 애초에 동작하지 않았다' 는 정정이 붙었다.

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

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| MPPI Run 1 무반응 = 벽에 끼임(물리 접촉) | 사용자 육안 · `job21c_where` 거리 | 벽과 14 cm(좌90 중심 기준 28 cm), 접촉 없음 | **기각** |
| = Nav2 가 명령을 안 냄 | `job30_goalabs` 의 `/cmd_vel` 표시 | v −0.02 · w −0.20 을 계속 냄 | **기각** |
| = 펌웨어가 명령을 막음(fault) | `/rover/status` | level 2 `STALL fault — reset required` | **확인**(조회 출력은 원천 소실, Run 2 는 `job35d_diag.txt` 에 남음) |
| 래치를 건 바퀴는 '승격된' 바퀴 | 지령으로 바퀴 목표 계산(아래) · 휠별 텔레메트리 | 계산상 MPPI Run 1 정지 지령에서 좌측이 승격 +0.020, RPP Run 2 는 안쪽 바퀴 0.0245(승격 아님, 문턱 바로 위). 어느 바퀴가 실제로 섰는지는 텔레메트리가 없어 모름 | **부분 지지** — 정확히는 '승격값 또는 그 근처의 저속 명령 + 부하' |
| 지령 문턱만 올리면(0.040) 된다 | 근거 검토 | 그 아래 지령의 진짜 구속을 무한 방치 — 드라이버 과전류 보호 사양 미확인 | **기각(철회)** |
| duty 기준이면 '마찰 못 이김' 과 '진짜 구속' 을 가른다 | 설계 논리(정지한 휠은 적분이 쌓여 duty 상승, 그래도 안 움직이면 구속) | 09-03 은 빌드 · 플래시만 | **미확인**(09-07 받침대 검증, 다음 시기) |

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
| 남은 흔적 | 이 카드 작성 중 확인: **`safety_monitor.c` 18 행 주석 "진짜 구속 시엔 드라이버 내장 3A 차단이 1차 방어 → 600ms 지연 허용 가능."** 이 지금도 남아 있다(`git grep -n "3A 차단"` → 이 한 곳). 같은 파일 28 행은 "출처 불명 '3A' 삭제" 라고 적어 서로 모순. 수정은 사용자 결정 대기(이 카드는 기록만) |
| 데이터 | [09-03 「펌웨어 수정 — 스톨 정책」 L69~L71](../debug_log/2026-09-03/SUMMARY.md) · `git show 1cefd2c8`(3A 첫 기재) · `git show 42ea9579`(삭제 · 새 정책) · [`../../firmware/rover_jupiter_fw/App/app/safety_monitor.c`](../../firmware/rover_jupiter_fw/App/app/safety_monitor.c) |

## 6. 남은 것 (09-03 시점)
- 받침대에서 손으로 바퀴를 잡아 level 1 → 1.5 s 재개 → 3 회째 level 2 확인(「내일 할 일」 2), duty 0.60 이 너무 낮 · 높은지.
- ROS 쪽 fault 해제 서비스(`/rover/clear_fault`) — 제안만.
- 휠별 duty · 목표 · 엔코더 텔레메트리 — 스톨 순간의 근거(어느 바퀴가 섰나)를 남기려면 필요(「내일 할 일」 5).
- 문서 불일치(수정 안 함, 보고만): `safety_monitor.c` 18 행의 '3A' 주석(§5). CLAUDE.md §2 '안전 메커니즘' 의 하위 줄 "스톨 감지 (200ms 윈도우, 지령 vs 엔코더 변화)" 는 08-26 이전 구현이고 바로 위 줄(duty ≥ 0.60 AND 600 ms)과 어긋난다.
- **이후(09-04 ~): 다음 시기에서 채움** — 09-07 받침대 검증(`job40a_stalltest.py`)에서 'FG 기반 스톨 감지 무력' → 원인 = 모터 PWM 50 Hz(회전자 떨림 펄스가 15~33 mm/s 가짜 속도) → 20 kHz 정정 뒤 600 ms 감지 · 1.5 s 자동복구 · 3 회 래치 전 경로 정상(CLAUDE.md §2). 휠별 텔레메트리(`/rover/status` `values[]`)도 09-07 에 추가. Jetson 쪽 '휠은 도는데 안 나아감' 감시(`stuck_monitor`)는 별도 줄기.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| MPPI Run 1(09-03) | 첫 래치 | 09-03 L39, `job34d_mppi_run1.txt` · `job34e_stuckdiag.txt` |
| RPP Run 1 · 2(09-03) | 성공 · 두 번째 래치 | 09-03 L61, `job35b_rpp_run1.txt` · `job35c_rpp_run2.txt` · `job35d_diag.txt` |
| 새 정책 플래시 | level 0 확인, 주행 없음 | 09-03 L76(출력 원문 없음) |
| 도구 | `job30_goalabs.sh`(09-02) · `job34e_stuckdiag.sh` · `job35a_prep.sh` · `chk_board.sh`(09-03) · (원본 없음) `job35d_diag` · 09-02 `job23a_topics` | 아래 §8 |
| 펌웨어 | `safety_monitor_update()` · `safety_monitor_clear()` · `safety_monitor_is_latched()` · `speed_controller_get_duty()` · `microros_task.c` 상태 발행 | 아래 §8.5 |

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

## 9. 용어
- **스톨(stall)**: 모터에 구동 명령 · 전력이 들어가는데 회전자가 돌지 못하는 상태. 전류가 커져 모터 · 드라이버가 과열될 수 있어 보호가 필요하다. 이 펌웨어는 전류를 못 재므로 '구동 중인데 이동 없음' 으로 간접 판정.
- **latch(래치)**: 한 번 켜지면 원인이 사라져도 명시적으로 지울 때까지 유지되는 상태. 09-03 이전 스톨 fault 는 무조건 래치, 이후는 '3 회 / 10 s' 일 때만 하드 래치.
- **re-arm(재무장)**: 보호 동작 뒤 감시를 초기화하고 다시 구동을 허용하는 것. 여기선 1.5 s 정지 뒤 자동.
- **duty 기준 판정**: '얼마나 빠르게 하라고 했나(지령)' 가 아니라 '실제로 얼마나 세게 밀고 있나(duty)' 로 구속을 판단. 정지마찰 때문에 잠깐 못 움직인 바퀴는 적분이 쌓이면서 곧 움직이므로 duty 가 0.60 에 가기 전에 풀리고, 0.60 이상으로 밀어도 600 ms 동안 3 mm 도 못 가면 진짜 구속으로 본다.
- **watchdog(cmd_vel)**: 마지막 명령 뒤 500 ms 안에 새 명령이 없으면 모터를 멈추는 펌웨어 감시. 통신이 끊겨도 로버가 계속 달리지 않게 하는 1 차 안전장치(CLAUDE.md §2).
- **DiagnosticStatus level**: 0 OK · 1 WARN · 2 ERROR · 3 STALE(byte 값).
- **데드밴드 · 승격 · 정지마찰 · duty**: [데드밴드 카드 §9](start-deadband.md).
