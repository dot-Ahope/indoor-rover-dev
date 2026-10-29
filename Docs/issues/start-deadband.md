# 기동 데드밴드 — 작은 속도 명령이 실행되지 않음

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(09-03 시점: 고정 하한 승격 0.020) · 원인 층 일부는 이후 시기에 다시 밝혀짐 | 08-26(전조) · 09-02 ~ 09-03 (이 카드), 이후 09-07 · 09-17 | [09-02 「B-1 원인 ②(핵심)」(L182)](../debug_log/2026-09-02/SUMMARY.md) | `firmware/rover_jupiter_fw/App/app/rover_platform.h`(`MIN_WHEEL_SPEED_MPS` · `WHEEL_SPEED_EPS_MPS` 신설) · `App/microros/microros_task.c`(`apply_min_wheel_speed()`) · `nav2_params.yaml`(RPP `max_angular_accel` 1 → 4, `xy_goal_tolerance` 0.15 ↔ 0.25) | [Nav2 첫 구축](nav2-first-setup.md) · [스톨 래치 × 승격](stall-latch.md)(이 조치의 부작용) · [라이다 근접 사각](near-wall-blindspot.md)(데드밴드 배회가 벽 근접을 부름) |

**한 줄**: Nav2 컨트롤러가 내는 작은 명령(바퀴 속도로 수 mm/s ~ 1 cm/s)에 로버가 아예 반응하지 않아, 컨트롤러는 '측정 속도 0' 을 보고 같은 작은 명령을 끝없이 반복했다(RPP 회전 시작 데드락 · MPPI 목표 앞 정체 · 장애물 옆 배회). 09-02 에 RPP 쪽은 가속 제한을 풀어 우회하고, 근본 보상으로 펌웨어에 '최소 기동 바퀴 속도 승격'(0.003 ≤ |v| < MIN → MIN)을 넣었다. 09-03 에 빌드 환경을 되살려 플래시하고 MIN 을 0.012 · 0.016 · 0.020 으로 바꿔 가며 쟀더니 기동 문턱은 0.012~0.016 m/s(당시 펌웨어 단위)였고, 여유를 둔 **0.020** 으로 확정했다. 다만 ① 이 측정은 모터 PWM 이 잘못 50 Hz 로 걸려 있던 조건이었고(09-07 발견), ② 09-02 데드락의 직접 원인 일부는 기계 마찰이 아니라 **펌웨어 속도 제어기의 정지 문턱(0.01 m/s)이 그 명령을 '정지' 로 버린 것**이었다(이 카드 작성 중 코드 읽기로 확인, 09-17 실측과 일치). 그리고 승격된 0.020 이 스톨 감지 문턱(0.015) 바로 위라 [스톨 래치](stall-latch.md)를 불렀다.

---

## 1. 증상
- RPP 가 180° 회전 목표에서 `w = +0.050 rad/s` 를 68 초 동안 20 Hz 로 냈는데 heading 이 176.9 → 176.4° 로 0.5° 만 변함. 바퀴로 환산하면 ±6 mm/s. [09-02 L182](../debug_log/2026-09-02/SUMMARY.md) · `2026-09-02/outputs/job26a_goalmon.txt`
- MPPI 복귀 주행이 목표 23 cm 앞에서 `v = −0.01` 을 약 54 초(t≈93~147 s) 반복하며 그 자리. `job30a_mppi_return.txt`
- MPPI 전진 주행이 장애물 근처에서 ±0.01~0.05 명령으로 같은 자리를 맴돔(t≈45~147 s), 그 사이 앞 벽에 붙어 회전 · 헛돎(사용자). `job30b_mppi_fwd.txt` · [09-02 「N1 벤치마크 1차」 L279](../debug_log/2026-09-02/SUMMARY.md)

## 2. 흐름 (시간순)
| 날짜 · 제목 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-26 「결과」 · 펌웨어 주석 | 1:90 모터로 교체 뒤 속도 제어기 튜닝 | 최소 기동 duty ≈ 15 %(좌우 대칭) → feedforward `DEADZONE 0.13`. duty-속도: 30 mm/s → 72 %, 50 → 92 %, 98 % → 115 ± 5 mm/s. 회전 0.3 rad/s 지령 → 휠 36° · 실제 15° | 기동 duty 와 속도 곡선을 feedforward 로 넣음(`KV_DUTY_PER_MPS 12`) | [08-26 SUMMARY](../debug_log/2026-08-26/SUMMARY.md)(출력 캡처 없음, '사후 작성') · `speed_controller.c` 주석(커밋 `42ea9579` 판) |
| 09-02 「원인 ②」 L182 | `job26a_goalmon.sh` 로 명령 체인 감시 | RPP · 스무더 출력 모두 0.05 rad/s, 로버 무반응 | RPP `rotateToHeading` 각가속 클램프(첫 명령 = `1.0 × 0.05 s` = 0.05) × '정지마찰 · PWM 데드밴드' = 데드락. **기전 설명은 불완전**(§5 실수 ①: 펌웨어가 6 mm/s 를 정지로 버림) | `job26a_goalmon.txt` |
| 09-02 「수정 후 결과」 L197 | `max_angular_accel` 1.0 → 4.0 | 첫 명령 0.243 rad/s → 회전 시작, 180° 성공 | RPP 회전 시작은 해결 | `job26b_goal180_fixed.txt` |
| 09-02 계획 §5 | 컨트롤러 판단에 '시스템 특성 ② 기동 데드밴드(ω < ~0.15 rad/s 무반응)' 기재 | 측정한 점은 0.05(무반응)와 0.3(반응) 뿐 | 0.15 는 **추정**(측정 아님) | 계획 문서 커밋 `76c08343` 판 §5 |
| 09-02 「N1 벤치마크 1차」 L279 | RPP · MPPI 같은 코스 | MPPI 목표 23 cm 앞 정체 · 중간 배회 | 임시로 `xy_goal_tolerance` 0.15 → 0.25 — 근접 정체만 완화, 배회는 그대로. **컨트롤러 튜닝으로 해결 불가 → 펌웨어 보상이 차단 항목** | `job29c` · `job30a` · `job30b` |
| 09-02 「펌웨어 수정 완료」 L298 | `rover_platform.h` 에 `MIN_WHEEL_SPEED_MPS 0.020f` · `WHEEL_SPEED_EPS_MPS 0.003f`, `microros_task.c` 에 `apply_min_wheel_speed()` | (소스만, 플래시 대기) | 탐색 범위 0.015~0.030 으로 실측 조정 예정 | 커밋 `76c08343` |
| 09-03 「한 일」 1~3 L4 | **빌드 환경 복원** — `micro_ros_stm32cubemx_utils` 가 `.gitignore` 라 저장소에 없음 → humble 브랜치 clone, `libmicroros.a` 는 WSL `~/microros_build` 의 이전 산출물(7.4 MB, 헤더 1765) 재사용, WSL 이 F: 를 못 봐 C: 경유(`stage_microros.sh`). Windows 도구(STM32CubeCLT arm-none-eabi-gcc 14.3 + GnuWin32 make)로 빌드, ST-LINK V3SET 로 플래시 | text 124,536 / data 5,020 / bss 108,696 · Device 0x413(F405) 검증 OK · 승격 코드 심볼 확인 | 처음부터 라이브러리를 만드는 30 분+ 절약 | `jobs/stage_microros.sh`(빌드 · 플래시 출력 원문은 없음 — 대화에만) |
| 09-03 오전 | `job20a_boot.sh`(09:31) → `job32b_deadband.sh`(MIN 0.020) | 배터리 12.33 V · ω 0.05/0.08/0.12/0.20/0.30 → **20.0 / 18.5 / 21.9 / 28.6 / 46.9°**(8 s) — 전 구간 반응 | **ω 0.05 데드락 해소** | `job32a_boot.txt` · `job32b_deadband.txt` |
| 09-03 같은 날 | `cycle.sh 0.012` → `job32c_reagent.sh` → 측정 | **다섯 지령 전부 −0.0~−0.1°**, '보드 재연결:' 칸 빈칸 | SUMMARY 에 이 회차 언급 없음. 보드가 agent 에 다시 안 붙어 명령이 안 들어간 것으로 **추정**(근거: 같은 날 「부수 발견」 "플래시 후 보드가 agent 에 자동 재연결되지 않음, `-rst` 로 해결" · 이 회차 전후 회전 여유 47 → 46 cm 로 로버가 안 움직임) | `job32c_min012.txt` |
| 09-03 같은 날 | `job32d_ekfrestart.sh` → 측정(MIN 0.012 재측정) | **7.9 / 0.3 / 8.3 / 39.7 / 47.4°** — ω 0.08 무반응, 나머지 미약 · 불규칙 | 0.012 = 문턱 경계 | `job32d_min012.txt` |
| 09-03 같은 날 | `cycle.sh 0.016` → `chk_board.sh` · `job32d_ekfrestart.sh` → 측정 | 시작 회전 여유 36 cm(필요 30) · 17.3 / 13.6 / 9.6 / 6.6 / **0.0°** — 갈수록 줄다 마지막 0 | **무효** — 반복 회전으로 로버가 좌측 벽 32 cm 까지 밀려 가드(중심 기준 < 33 cm)가 조기 중단(SUMMARY 각주) | `job32e_min016.txt` |
| 09-03 같은 날 | 로버 재배치 → `job33a_reset_noagent.sh` → 측정(MIN 0.016) | 배터리 12.09 V · 회전 여유 60 cm · **23.8 / 18.6 / 15.0 / 28.9 / 49.4°** — 전 구간 반응 | 0.016 = 문턱 위 | `job33a_reset.txt` · `job33b_min016_clean.txt` |
| 09-03 「판단」 L19 | `cycle.sh 0.020`(최종 플래시, 측정 없음) · 헤더 주석에 실측 근거 · 한계 · `TODO(improve)` | — | **기동 문턱 ≈ 0.012~0.016 m/s, 마진 둔 0.020 채택.** 0.016 의 분해능 이득은 승격 구간에선 없음 | 커밋 `42ea9579` `rover_platform.h` |
| 09-03 「부수 발견」 L25 | (운영) | 제자리 회전을 반복하면 로버가 밀림(수 회전에 10 cm+) · 배터리 12.09~12.33 V | 회전 시험은 사방 55 cm+. 12.0 V 아래면 데드밴드가 커질 수 있음(**추정**, 측정 없음) | — |
| 09-03 계획 §6 | 0.020 평가와 추가 작업 표 | 마진 = 문턱 상한 대비 +25 %, 하한 대비 +67%. 순수 회전 환산 |ω| < 0.163 rad/s 는 전부 0.163 으로 실행 | 적절. 한계 = 고정값(전압 · 바닥 · 장력 변화)과 '움직인 뒤' 저속 능력 미사용. ★1 = 기동 보조(적응형) · 전압 연동 하한 · 휠별 텔레메트리 | 계획 문서 `42ea9579` 판 §6.1~6.3 |
| 09-03 「경과」 L39 · 「메커니즘」 L46 | Nav2 실주행 재개 | 승격된 휠이 부하 상태에서 못 움직이면 스톨 조건(지령 > 0.015, 600 ms · 3 mm)에 정확히 걸려 **로버 전체 래치** | 승격 × 스톨 감지 설계 충돌 → [스톨 카드](stall-latch.md) | `2026-09-03/outputs/job34d_mppi_run1.txt` · `job35c_rpp_run2.txt` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| RPP 가 명령을 0 으로 낸다 | `/cmd_vel_nav` 감시 | 0.05 를 냄 | **기각**(`job26a`) |
| 스무더가 명령을 깎는다 | `/cmd_vel` 감시 | 같은 0.05 | **기각**(`job26a`) |
| 첫 명령이 너무 작다(RPP 각가속 클램프) | accel 1 → 4 | 0.243 으로 즉시 회전 | **확인**(`job26b`) |
| 작은 바퀴 명령은 펌웨어 속도 제어기에서 '정지' 로 처리된다 | 09-02 당시 `speed_controller.c`: `TARGET_THRESH 0.01f` — `set_target(|v| < 0.01)` 이면 `stop_ramp` 로 들어가 duty 0 | ω 0.05 → 바퀴 ±0.0061 m/s < 0.01 → **duty 0**(코드). 09-17 mp8 에서 '0.009 m/s 지령에 양 휠 tgt 0 · duty 0' 이 실측으로 드러남 | **지지(코드 읽기 + 이후 실측)** — 09-02 · 09-03 기록엔 없음, §5 실수 ① |
| 기계적 기동 문턱(정지마찰 · 저속 제어 한계)이 있다 | 승격값 0.012 / 0.016 / 0.020 스윕(모두 정지 문턱 0.01 위) | 0.012 불규칙(0.08 에서 0.3°), 0.016 · 0.020 전 구간 반응 | **지지** — 문턱 ≈ 0.012~0.016(당시 단위, PWM 50 Hz 조건) |
| 문턱은 전압에 따라 커진다 | — | 측정 없음(배터리 12.09~12.33 V 범위만) | **미확인** |
| 승격으로 Nav2 좁은 곳 문제가 풀린다 | 재벤치마크 | 스톨 래치로 중단 | **미확인**(이후 시기) |

## 4. 조치와 효과
| 바꾼 것 | 전 → 후 | 효과(측정) | 한계 |
|---|---|---|---|
| RPP `max_angular_accel` | 1.0 → 4.0 | 회전 시작 0.05 → 0.243 rad/s, 180° 성공 | RPP 회전 시작에만 해당 |
| 펌웨어 바퀴 속도 승격 | 없음 → 0.003 ≤ |v| < 0.020 이면 ±0.020 | ω 0.05 에서 8 s 에 20°(무반응 → 반응) | ① 승격 구간은 지령 크기와 무관하게 같은 속도(분해능 상실) ② 고정값 ③ 스톨 감지 문턱(0.015) 바로 위 → 래치 ④ PWM 50 Hz 조건의 값 |
| `xy_goal_tolerance` | 0.15 → 0.25(09-02) → 0.15(09-03) | 근접 정체 완화 → 승격 뒤 원복 | — |

계산으로 보는 승격의 크기(코드 · 기록 수치로 계산, 측정 아님):
- 09-03 펌웨어의 반 게이지 `HALF_WHEEL_BASE = 0.1225 m` → 승격 0.020 은 순수 회전으로 `0.020 / 0.1225 = 0.163 rad/s`. 8 s 면 75° 가 돼야 하지만 측정은 18~22° (약 25~30 %). 이 차이는 당시 펌웨어 바퀴 속도 단위가 실제보다 약 1.28 배 컸던 것(09-02 VX_SCALE 0.783 · 09-07 휠 둘레 0.16130 → 0.12533)과 트랙 회전 미끄러짐이 겹친 것 — 어느 쪽이 얼마인지는 이 시기 기록으로 나눌 수 없다.
- 같은 이유로 '0.012~0.016 m/s' 는 당시 펌웨어 단위다. 현 헤더의 환산 계수 0.777 을 쓰면 실제 약 0.0093~0.0124 m/s(계산).
- 승격 0.020 의 초기 duty ≈ `DEADZONE 0.13 + KV 12 × 0.020 + Kp 0.7 × 0.020` ≈ 0.384(헤더 주석은 Kp 항을 빼고 0.37).

## 5. 내 실수
### 실수 ① 데드락을 '정지마찰' 로만 설명하고 펌웨어 정지 문턱을 안 봄 (09-02 「원인 ②」 L182)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 회전 목표에서 로버가 안 움직이는 이유를 밝혀 고치기 |
| 본 것 | `job26a_goalmon.txt`: RPP · 스무더 모두 0.05 rad/s(= 바퀴 ±6 mm/s), heading 불변 |
| 처음 추론 | "0.05 rad/s = 휠 ±6 mm/s → **정지마찰 · PWM 데드밴드 이하**라 로버가 안 움직임"(SUMMARY 원문). 펌웨어 보상도 같은 그림으로 설계(`rover_platform.h` 주석: "모터가 반응하지 않음(정지마찰 · 저속 제어한계)") |
| 의심한 이유 | (이 카드 작성 중) 같은 펌웨어의 `speed_controller.c:35 TARGET_THRESH 0.01f` — 0.01 m/s 미만 목표는 '정지 명령' 으로 처리된다. 6 mm/s 는 이 아래 |
| 판별 | 코드 읽기: 09-02 판(`76c08343` 이전과 같음) `speed_controller_set_target()` 은 `|v| < TARGET_THRESH` 면 `stop_ramp = true` 만 하고 목표를 바꾸지 않음 → 정지 상태에서 시작했으면 목표 0 · duty 0. 이후 시기 실측: 09-17 mp8 bag 의 `/rover/status` 에서 0.009 m/s 지령에 양 휠 tgt 0 · duty 0 (09-17 SUMMARY §7), 09-17 에 정지 문턱을 10 → 5 mm/s 로 낮추고 'MIN < 정지 문턱' 이면 컴파일 오류(`#error`)를 넣음 |
| 결론 | 09-02 데드락의 **직접 원인은 펌웨어가 6 mm/s 명령을 버린 것**. 기계적 기동 문턱(09-03 스윕 0.012~0.016)은 그 위에 있는 두 번째 층. 승격(0.020 > 0.01)은 두 층을 한꺼번에 넘겨서 효과가 있었다 — 결론(승격)은 맞았지만 이유 설명이 반쪽 |
| 다음에 알아보는 법 | '명령은 나가는데 안 움직임' 이면 기계를 탓하기 전에 **명령 경로의 모든 문턱**(펌웨어의 EPS · 정지 문턱 · 승격 · 포화, 스무더 deadband)을 표로 늘어놓고 지령값과 견준다. 보드가 휠 목표 · duty 를 내보내야(09-07 휠별 텔레메트리) 이 구별이 측정으로 가능 |
| 데이터 | `2026-09-02/outputs/job26a_goalmon.txt` · 펌웨어 `git show 76c08343:firmware/rover_jupiter_fw/App/app/speed_controller.c`(35 · 126 행 부근) · [`../debug_log/2026-09-17/SUMMARY.md`](../debug_log/2026-09-17/SUMMARY.md) §7(mp8) · §8.8 |

### 실수 ② 무효 측정을 기록에서 빠뜨림 (09-03 MIN 0.012 1 차)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | MIN 0.012 스윕 |
| 본 것 | `job32c_min012.txt`: 다섯 지령 전부 0°, 재연결 확인 칸 빈칸 |
| 처음 추론 | (기록 없음) — SUMMARY 표는 재측정(`job32d`)만 실었고 1 차 회차의 '전부 0' 과 그 이유는 안 적음 |
| 의심한 이유 | 0.012 재측정에선 0.05 에서 7.9° 가 돌았다 — 같은 펌웨어로 '전부 0' 은 측정 조건 문제 |
| 판별 | 같은 날 「부수 발견」(플래시 뒤 보드가 agent 에 자동 재연결 안 됨), 공통 결함 ①(빈칸 = 무발행), 회전 여유 47 → 46 cm(안 움직임) |
| 결론 | 1 차 회차는 보드 미연결로 명령이 안 들어간 것으로 **추정**(직접 확인한 출력 없음) |
| 다음에 알아보는 법 | 스윕 전에 `/wheel_odom` Hz 와 `/rover/status` 를 **값으로** 확인(빈칸 금지), 무효 회차도 SUMMARY 에 '무효 · 이유' 로 남긴다(09-03 `job32e` 무효는 각주로 남겼음 — 같은 방식) |
| 데이터 | `2026-09-03/outputs/job32c_min012.txt` · `job32d_min012.txt`, 도구 `jobs/job32c_reagent.sh` · `cycle.sh` |

## 6. 남은 것 (09-03 시점)
- 승격값과 스톨 감지의 충돌 → [스톨 래치 카드](stall-latch.md)(09-03 오후 duty 기준 스톨로 조치).
- 적응형 기동 보조 · 전압 연동 하한 · 휠별 텔레메트리(계획 §6.2 ★1) — 미구현.
- 문턱 측정은 EKF yaw 로만 했고 바퀴별 기동 여부는 못 봄.
- **이후(09-04 ~): 다음 시기에서 채움** — 09-07 모터 PWM 50 Hz → 20 kHz 정정으로 09-03 문턱 측정은 폐기(현 `rover_platform.h` 이력 주석: "※ PWM 50 Hz 조건 측정 — 09-07 에 폐기"), 0.010 임시 하향 · 바닥 스윕 `job44a` · 휠 둘레 교정으로 0.008(환산) → 09-17 정지 출발 8 mm/s 직접 확인 · 정지 문턱 10 → 5 mm/s. 현 값: `MIN_WHEEL_SPEED_UMPS 8000` · `SPEED_CTRL_STOP_THRESH_UMPS 5000` · `WHEEL_SPEED_EPS_UMPS 3000`.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| B-1 감시 · 수정 | 0.05 rad/s 데드락 → accel 4.0 | 09-02 L182~L212, `job26a_goalmon.txt` · `job26b_goal180_fixed.txt` |
| N1 Run 2 · 3 | MPPI 미세 명령 정체 · 배회 | 09-02 L279, `job30a_mppi_return.txt` · `job30b_mppi_fwd.txt` |
| MIN 스윕 | 0.020 / 0.012(무효 · 재) / 0.016(무효 · 재) | 09-03 L7~L15, `job32b_deadband.txt` · `job32c_min012.txt` · `job32d_min012.txt` · `job32e_min016.txt` · `job33b_min016_clean.txt` |
| 도구 | `cycle.sh` · `stage_microros.sh` · `chk_board.sh` · `job32b_deadband.sh` · `job32c_reagent.sh` · `job32d_ekfrestart.sh` · `job33a_reset_noagent.sh`(09-03 `jobs/`), `job26a_goalmon.sh` · `job20a_boot.sh`(09-02 `jobs/`) | 아래 §8 |
| 펌웨어 | `apply_min_wheel_speed()` · `cmdvel_callback()` · `speed_controller_set_target()/update()` · 상수 | 아래 §8.8 |

---

## 8. 도구 해설
실행 경로 · 출력 저장 방식 · 공통 결함(빈칸 = 무발행, 라이다 상수, 노드 생성 직후 주행)은 [Nav2 첫 구축 카드 §8.0](nav2-first-setup.md) 과 같다. `job26a_goalmon.sh` · `job20a_boot.sh` · `job33a_reset_noagent.sh` 의 상세도 그 카드 §8.7 · §8.12 · §8.13.

### 8.1 `cycle.sh` — MIN 값 바꿔 빌드 · 플래시 · 리셋 한 번에
- 위치 · 형태: **PC 의 Git Bash**(경로 `/f/6_Indoor_Rover/Rover`, Windows 도구 사용). `bash cycle.sh 0.012` 처럼 MIN 값 하나. [`../debug_log/2026-09-03/jobs/cycle.sh`](../debug_log/2026-09-03/jobs/cycle.sh)
- 왜: MIN 을 세 번 바꿔 재야 했고, 매번 '헤더 수정 → 빌드 → 플래시 → 리셋' 을 손으로 하면 실수 여지가 큼.
- 하는 일: ① `sed -i "s|^#define MIN_WHEEL_SPEED_MPS       [0-9.]*f|… ${MIN}f|"` 로 `rover_platform.h` 를 **직접 수정**(공백 7 칸까지 정확히 맞춰야 매칭) → 바뀐 줄 출력 ② `PATH` 에 STM32CubeCLT 1.21.0 의 GNU 도구 + GnuWin32 make → `make -C firmware/rover_jupiter_fw -j8`, 크기 줄(text/data/bss) 또는 error 마지막 1 줄 ③ `STM32_Programmer_CLI -c port=SWD reset=HWrst -w …/build/rover_jupiter_fw.elf -v -rst` → 'Download verified' 줄 ④ 3 s 뒤 `-c port=SWD reset=HWrst -rst` 로 **한 번 더 리셋**('MCU Reset' 줄) ⑤ 12 s 대기(보드가 agent 와 세션을 맺을 시간).
- 출력: 화면에만(원문 저장 없음, 대화에만).
- 쓰인 곳: 09-03 스윕 세 회차와 최종 0.020 플래시. 09-09 §7 에서도 언급(JOBS 색인).
- 알려진 결함: ① 머리 주석은 'EKF 재시작 → 데드밴드 측정' 까지 한다고 적었지만 코드는 리셋 + 12 s 대기에서 끝남 — EKF 재시작 · 측정은 Jetson 쪽 도구(`job32d` · `job32b`)를 따로 불렀다. ② 소스 파일을 `sed -i` 로 고치므로 마지막에 부른 값이 저장소에 남는다(최종 0.020 회차로 되돌림). ③ 두 번째 `-rst` 는 '플래시 뒤 보드가 agent 에 안 붙음' 대응으로 보이지만 넣은 시점이 기록에 없다(**미확인** — 0.012 1 차 회차가 무효였던 것과 관련 추정).
- 지금 다시 쓰기: 상수가 정수 µm/s(`MIN_WHEEL_SPEED_UMPS`)로 바뀌어 sed 패턴이 더는 안 맞음 → 그대로는 안 됨. 빌드 · 플래시 절차는 `Docs/01_firmware/BUILD_AND_FLASH_GUIDE.md` 참조.

### 8.2 `stage_microros.sh` — micro-ROS 라이브러리 옮겨 싣기
- 위치 · 형태: **WSL**(`$HOME/microros_build`, `/mnt/c`), 인자 없음, `set -e`. [`jobs/stage_microros.sh`](../debug_log/2026-09-03/jobs/stage_microros.sh)
- 왜: 펌웨어 빌드에 필요한 `micro_ros_stm32cubemx_utils/libmicroros/`(`libmicroros.a` + `include/`)가 `.gitignore` 라 저장소에 없었다. 처음부터 만들면 30 분+ → WSL 에 남아 있던 이전 산출물을 재사용. 그런데 WSL 에서 F: 가 안 보여 C: 를 중간 정거장으로 씀.
- 하는 일: `B=$HOME/microros_build/firmware/build`, `S=/mnt/c/temp_microros`. `libmicroros.a` 크기 출력 · `include` 유무 → `S` 지우고 새로 만듦 → `.a` 복사 → **원본 `$B/include` 에서 `*.c` 파일 삭제**(`find … -delete`) → include 전체 복사 → `include/X/X/*` 이중 폴더를 `include/X/` 로 평탄화(Makefile 이 `-I…/libmicroros/include` 하나만 보므로) → 크기 · 헤더 수 · 앞 5 개 폴더 이름.
- 출력: 대화에만. SUMMARY 에 7.4 MB · 헤더 1765 로 옮겨 적음.
- 쓰인 곳: 09-03 「한 일」 1. C: → 펌웨어 트리(`Middlewares/Third_Party/micro_ros_stm32cubemx_utils/libmicroros/`)로 옮긴 단계는 도구 · 출력이 없다(원천 소실).
- 결함: 복사 **원본** 쪽 include 의 `.c` 를 지운다(복사본만 지우는 게 안전). 산출물이 언제 · 어떤 설정으로 만들어졌는지(이전 F5a 단계 추정)는 이 도구가 확인하지 않음 — `Docs/01_firmware/F5a_MICROROS_LIB.md` 참조.
- 지금 다시 쓰기: 같은 상황(라이브러리 소실)이면 개념은 유효, 경로는 확인 필요.

### 8.3 `chk_board.sh` — 보드 세션 3 줄 확인
- 위치 · 형태: Jetson, 인자 없음. [`jobs/chk_board.sh`](../debug_log/2026-09-03/jobs/chk_board.sh)
- 하는 일: `docker ps` 에서 microros 컨테이너 이름 · 상태, `/wheel_odom` hz(6 s), `ros2 node list` 에 `rover_jupiter`.
- 출력: `job32e_min016.txt` 첫 3 줄(agent Up 5 minutes · 50.011 Hz · `/rover_jupiter`), `job35a_prep.txt` 의 1).
- 결함: 공통 결함 ① — 'agent 없음' · '무발행' 문구가 안 찍힐 수 있음(빈칸으로 판단). 펌웨어 상태(`/rover/status`)는 안 봄 → 09-03 오후 `job35a_prep.sh` 가 따로 추가.
- 계보: → 이후 prep · 게이트 도구의 '보드 세션' 단계. 지금 다시 쓰기: 개념 유효(빈칸 해석 주의).

### 8.4 `job32b_deadband.sh` — 미세 각속도 지령에 실제로 도는가 ★ 스윕 측정 도구
- 위치 · 형태: Jetson, 인자 없음(지령 목록이 코드에 고정). [`jobs/job32b_deadband.sh`](../debug_log/2026-09-03/jobs/job32b_deadband.sh)
- 왜: 플래시 전 데드락 지점(ω 0.05)이 풀렸는지, 그리고 MIN 을 바꿔 가며 '어디부터 도는가' 를 같은 절차로 재기.
- 하는 일:
  1. `/odometry/filtered` 구독 → yaw(쿼터니언 z · w 로 `atan2(2wz, 1−2z²)`), `/scan` 구독 → 중심 기준 거리의 **0.5 백분위수**(튀는 점 몇 개 무시, 09-02 회전 루프 도구에서 온 방식).
  2. 시작 여유 `cen > SWEEP + 0.05 = 0.35 m` 아니면 중단.
  3. ω = 0.05, 0.08, 0.12, 0.20, 0.30 rad/s 마다: 영 명령 10 번(0.02 s 간격) + 0.6 s 정착 → 시작 yaw `h0` → **8.0 s 동안** `Twist(angular.z = ω)` 를 루프마다 발행(약 50 Hz) — 단 `cen < SWEEP + 0.03 = 0.33 m` 이면 즉시 중단 → 영 10 번 + 0.8 s → 회전량 `d = wrap(yaw − h0)`(°), 평균 실 ω = `rad(d) / 8.0`, 판정 `|d| > 2°` 면 '✓ 회전함'.
  4. 판정 줄: ω 0.05 결과(✅ 보상 성공 / ❌), 무반응 지령 목록, '실ω/지령ω 비율'.
- 출력: `job32b_deadband.txt`(0.020) · `job32c_min012.txt`(0.012 무효) · `job32d_min012.txt`(0.012) · `job32e_min016.txt`(0.016 무효) · `job33b_min016_clean.txt`(0.016). 표는 '지령ω · 8초간 실회전 · 평균실ω · 판정'.
- 읽는 법: 승격 때문에 ω 0.05 · 0.08 · 0.12 는 바퀴 지령이 0.0061 · 0.0098 · 0.0147 m/s 로 **모두 MIN 미만 → 같은 MIN 으로 실행**된다(MIN 0.012 면 0.12 는 0.0147 이라 그대로). 그래서 이 세 칸은 '같은 지령을 세 번 준 반복 측정' 으로 읽어야 한다 — 0.016 에서 23.8 / 18.6 / 15.0° 로 같은 지령에 ±25 % 안팎의 흩어짐. '실ω/지령ω 비율' 은 승격 구간에서 의미가 없다(분모가 실제 실행값이 아님).
- 쓰인 곳: 09-03 「한 일」 4 의 표 · 「판단」 · 헤더 주석 실측 근거.
- 알려진 결함: ① **가드 조기 중단을 출력에 표시하지 않음** — 중단돼도 8 s 로 나눠 '0.0° ✗ 무반응' 으로 찍힌다(`job32e` 의 0.30 칸이 그 예. SUMMARY 각주로만 무효 처리). ② yaw 는 **EKF 출력**(`/odometry/filtered`, 자이로는 D455f 카메라 IMU)이지 자이로 원신호 적분이 아님 — SUMMARY 표의 '자이로 회전량' 은 근사 표현. ③ 회전을 연달아 하므로 로버가 밀려 다음 회차 여유가 줄어듦(회전 여유 61 → 47, 46 → 36 cm — 회전 반복 밀림의 간접 증거, 09-03 「부수 발견」). ④ 바퀴별 기동 여부는 못 봄.
- 계보: 09-02 회전 루프 도구의 '백분위 여유 + 감속' 방식 → 이것 → 09-07 `job44a_deadband`(PWM 20 kHz 뒤 바닥 스윕: 직진 지령 5~30 mm/s, 3 s 유지, 휠별 텔레메트리로 FG · duty 직접 확인 — 다음 시기) → 09-17 `job397`(정지 출발 실측). 지금 다시 쓰기: 안 씀(바퀴별 값을 보는 후속 도구가 나음).

### 8.5 `job32c_reagent.sh` — 플래시 뒤 agent 재연결 + EKF 재시작
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job32c_reagent.sh`](../debug_log/2026-09-03/jobs/job32c_reagent.sh)
- 왜: 플래시로 보드가 재부팅되면 세션이 끊기므로 agent 를 새로 띄워 다시 붙이려 함(08-26 이후 알려진 '세션 1 회 수립' 펌웨어 성질).
- 하는 일: `docker rm -f microros_agent` · `pkill -f base.launch` → `base.launch.py` 12 s → `/wheel_odom` hz(6 s) → conditioner · EKF 종료 → `ekf.launch.py` 15 s → `gyro bias` 줄 → `/odometry/filtered` hz.
- 출력: `job32c_min012.txt` 앞부분 — '보드 재연결:' 뒤가 빈칸이고 곧바로 자이로 바이어스 줄이 이어짐(= hz 측정 실패, 공통 결함 ① 로 '실패!' 미출력). 그 뒤 측정 전부 0°.
- 결함: 재연결 실패를 알리지 못해 측정을 그대로 진행함. 플래시 뒤엔 agent 재기동이 아니라 **보드 리셋(`-rst`)** 이 필요했다(「부수 발견」) — 이 도구의 접근 자체가 그날의 해법과 다름.
- 계보: 이후 플래시 절차는 `cycle.sh` 의 두 번째 `-rst` + `job32d_ekfrestart.sh` 로 바뀐 것으로 보임(추정). 지금 다시 쓰기: 안 씀.

### 8.6 `job32d_ekfrestart.sh` — EKF 만 재시작
- 위치 · 형태: Jetson, 인자 없음. [`jobs/job32d_ekfrestart.sh`](../debug_log/2026-09-03/jobs/job32d_ekfrestart.sh)
- 왜: 스윕 회차마다 yaw 기준을 새로 잡고 자이로 바이어스를 다시 캘리브(정지 상태 10 s)하려고. agent · SLAM 은 그대로.
- 하는 일: `sensor_conditioner` · `ekf_node` 종료 2 s → `ekf.launch.py` 15 s → 로그의 `gyro bias` 또는 `not stationary` 마지막 줄 → `/odometry/filtered` hz.
- 출력: `job32d_min012.txt` · `job32e_min016.txt` 의 앞부분(예: bias (−0.00692, −0.00124, −0.00176) rad/s, 29.992 Hz).
- 결함: 캘리브 중 로버가 움직이면 `not stationary` 가 찍히는데, 그 경우에도 다음 측정으로 넘어감(감싸개 쪽에서 사람이 봐야 함). 지금 다시 쓰기: 안 씀(EKF 구성 변경).

### 8.7 `job33a_reset_noagent.sh` — agent 유지 초기화
상세는 [Nav2 카드 §8.13](nav2-first-setup.md). 이 카드에서는 MIN 0.016 재측정 전 재배치 · 초기화에 썼다(`job33a_reset.txt`: 배터리 12.09 V, 회전 여유 최근접 60 cm).

### 8.8 펌웨어 코드 해설 (09-03 커밋 `42ea9579` 판)
- **명령 경로**(`App/microros/microros_task.c` `cmdvel_callback()`): `/cmd_vel` 의 `linear.x` 를 ±`V_MAX_MPS`(= `MAX_LINEAR_SPEED_MPS` 0.100) 로 자름 → 차동 역기구학 `v_l = v − ω·0.1225`, `v_r = v + ω·0.1225`(`HALF_WHEEL_BASE = WHEEL_BASE_M 0.245 / 2`) → 한쪽이 0.100 을 넘으면 두 바퀴를 같은 비율로 줄여 회전 방향 보존 → **`apply_min_wheel_speed()`** 를 좌 · 우 각각 → `speed_controller_set_target()` → `safety_monitor_cmdvel_received()`(watchdog 시각 갱신).
- **`apply_min_wheel_speed(v)`**: `|v| < WHEEL_SPEED_EPS_MPS(0.003)` → 0(정지 의도 유지), `|v| < MIN_WHEEL_SPEED_MPS(0.020)` → `copysignf(0.020, v)`(부호 보존 승격), 그 밖은 그대로. 승격은 **포화 축소 뒤**에 하므로 축소로 작아진 바퀴도 승격된다. 부작용: 한쪽만 승격되면 곡률이 지령과 달라짐(주석: '상위 피드백 루프가 흡수').
- **`speed_controller_set_target()`**(`App/app/speed_controller.c`): `|target| < TARGET_THRESH(0.01)` 이면 목표를 바꾸지 않고 `stop_ramp` 모드(4.0 m/s² 로 0 까지 감속 후 duty 0). 승격 전에는 바로 여기서 6 mm/s 가 '정지' 가 됐다(§5 실수 ①).
- **`speed_controller_update()`**(100 Hz, `freertos.c` 의 제어 태스크에서 `encoder_update_velocity → speed_controller_update → safety_monitor_update → odometry_update` 순): 목표 < 0.01 이면 적분 · duty 0. 아니면 `integral += Ki(6.0) · err · 0.01`(±`I_MAX 0.85` 클램프), `duty = sign(tgt) · DEADZONE(0.13) + KV(12.0) · tgt + Kp(0.7) · err + integral`, ±`OUT_MAX 0.98` 로 자르고, 통합 BLDC 는 목표와 반대 부호 duty(제동)를 0 으로(방향선 thrash 방지). `last_duty` 에 저장 — 이 값이 [스톨 카드](stall-latch.md)의 duty 기준 판정에 쓰인다.
- **상수의 출처**: `DEADZONE 0.13`(최소 기동 duty 실측 ~15 % 의 살짝 아래), `KV 12`(08-26 duty-속도 곡선 절충), `I_MAX 0.85`(50 mm/s 에 70 % 포화 관측 뒤 상향) — 전부 08-26 · PWM 50 Hz 조건. `MAX_LINEAR_SPEED_MPS 0.100`(duty 98 % 에서 0.115 m/s 실측에 여유).

## 9. 용어
- **데드밴드(기동 데드밴드)**: 명령이 0 이 아닌데도 출력(바퀴 회전)이 0 인 입력 구간. 여기선 두 층 — ① 펌웨어가 의도적으로 '정지' 로 보는 구간(`TARGET_THRESH 0.01`, `EPS 0.003`) ② 모터 · 트랙이 실제로 못 움직이는 구간(정지마찰 · 저속 제어 한계, 09-03 실측 0.012~0.016).
- **정지마찰(static friction)**: 멈춰 있는 물체를 움직이기 시작하는 데 드는 힘이 이미 움직이는 물체를 계속 움직이는 힘(운동마찰)보다 큰 성질. 그래서 '움직이기 시작할 때만' 큰 힘이 필요하고, 계획 §6.1 의 '움직인 뒤 저속 능력을 못 씀' 한계가 여기서 나온다.
- **승격(promotion)**: 문턱 아래의 0 이 아닌 명령을 문턱 값으로 올려 실행(부호 보존). 대가는 분해능 — 승격 구간 안의 명령은 크기와 무관하게 같은 속도.
- **기동 보조(kick-start, 계획의 '적응형')**: 멈춰 있을 때만 잠깐 문턱 이상으로 밀고 움직이기 시작하면 원래 작은 목표로 돌아가는 방식. 이 시기엔 제안만 됨.
- **duty**: PWM 한 주기 중 켜져 있는 비율(0~1). 이 모터는 '내장 속도 제어' 로 추정돼(08-26) duty 가 곧 전압이 아니라 속도 지령처럼 동작한다. 이 시기 PWM 주파수는 잘못 50 Hz 였다(09-07 에 20 kHz 로 정정).
- **feedforward(DEADZONE · KV)**: 오차를 보기 전에 '이 속도면 대략 이 duty' 를 미리 더하는 항. PID 는 그 위에서 잔차만 보정.
- **RPP 각가속 클램프**: [Nav2 카드 §9](nav2-first-setup.md) RPP 항목.
- **스톨 · latch · re-arm**: [스톨 카드 §9](stall-latch.md).
