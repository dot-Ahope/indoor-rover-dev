# ② 온보드 정지 수단 · nav_guard (5 시기: 09-29 §13 ~ §13.6)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| 09-29 시점 **종결(일부 미검증)** — L2 nav_guard 시간 한도는 G1 실동작 통과, 무진행 한도는 **기동만 확인**(G2 사용자 보류), L3 stuck_monitor 는 '작동' 으로 전환. 이후: 10-01 nav_guard 한도 계산 결함 수정 · 무진행 첫 실개입(정상) · **stuck_monitor 는 사용자 결정으로 다시 관찰 모드**(지금 순회 prep 기본) · 자이로 우선 수정은 실주행에서 꺼져 있었음 · 10-22 nav_guard CPU 19.5 % 미해결(아래 '이후') | 09-29 (이 카드는 09-29 를 채움) | [09-29 §13](../debug_log/2026-09-29/SUMMARY.md) — F2 진입 조건(로드맵 §7.3-1 · §7.4) | [`nav_guard.py`](../../ros2_ws/src/rover_bringup/scripts/nav_guard.py)(신규) · [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 225~228 행(`nav_guard:=true` 기본) · `stuck_monitor.py`(자이로 우선, 09-29) · prep `job240` 의 `stuck_shadow:=${STUCK_SHADOW:-false}`(09-29) | [정체 감시 stuck_monitor](stuck-monitor.md)(L3 의 본체) · [스톨 보호 래치](stall-latch.md)(L0) · [보드 OLED · base 자동 기동](board-oled-autostart.md)(L1 복구 절차) · [Jetson Wi-Fi](jetson-wifi-link.md)(PC 쪽 한도가 사라지는 이유) · [스크립트 주행 안전 가드](script-drive-guards.md) · [F0-b 코스](f0b-course.md)(오판 1 건이 나온 주행) |

**한 줄**: F2(저장 지도 순회) 전에 'PC · Wi-Fi 없이도 잘못 가면 스스로 멈추고, 사람이 언제든 멈출 수 있게' 하려고 층별로 정리했다. 목표 시간 한도가 **PC 러너에만** 있어 Wi-Fi 가 끊기면 사라진다는 빈틈을 Jetson 노드 `nav_guard`(목표별 시간 한도 + 45 s 무진행 → 모든 목표 취소 + `/cmd_vel` 0)로 메웠고, 시간 한도는 G1 에서 15.12 s 진단 · 15.18 s 취소 · 0.38 s 뒤 정지로 통과했다. stuck_monitor 는 성공 주행 bag 20 개를 오프라인 재생해 오판 1 건의 기전(스캔 상관 회전 과대)을 찾고 '자이로 우선' 으로 고쳐 오판 0 · 받침대 참 정체 0.8~0.9 s 검출을 확인한 뒤 작동으로 바꿨다 — 그러나 이 수정은 **실주행에선 꺼져 있었다**(10-01 발견, 아래 실수 2).

## 1. 증상 · 빈틈
09-29 §13 '현재 있는 것'(코드 확인):
- 펌웨어 `safety_monitor.c`: `/cmd_vel` 500 ms 워치독, 스톨(|duty| ≥ 0.60 & 600 ms 동안 3 mm 미만 → 1.5 s 정지 · 자동 재무장, 10 s 3 회 래치). **E-stop 은 설계 문서(FIRMWARE_DEV_PLAN tSafety)에만 있고 미구현**.
- `stuck_monitor.py`: launch 기본은 작동이지만 prep(`job240`)은 그림자 모드. 09-16 오판 이력, **09-29 f0b1(성공 주행)에서도 진단 1 회**.
- 목표 시간 한도: PC 러너(`job550`)에만. 원격 정지(`job156`)도 Wi-Fi 필요.
빠진 경우: ⓐ Nav2 가 살아서 엉뚱하게 계속 감 ⓑ Wi-Fi 끊김으로 PC 쪽 한도 · 원격 정지 상실 ⓒ 사람이 즉시 멈추고 싶을 때.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 09-29 §13 | 층별 구체안 L0~L4 + **주행 전 판정 선언** G1(한도 15 s → +1 s 안 취소 · 1 s 안 정지) · G2(막힌 목표 → 무진행 한도 + 2 s) · G3(성공 bag 오판 0 + 벽 밀기 검출 ≥ 1) · G4(스위치 정지 ≤ 5 cm) · (선택) G5 심장박동 | — | 순서 G3 → L2 · G1 · G2 → G4 | — |
| 09-29 §13.1 | G3 전수 조사 — bag 20 개(F0 9 · 회전 9 · 직진 2, 지령 ≈ 1,570 s) | 판정 **1 건**: f0b1 t 36.9 s 문 통과 중, "지령 15.6 cm/10° 인데 관측 2.0 cm/21.0°(비율 0.13)", 같은 2 s SLAM 15.0 cm · −12.5° | **오판** | `job668` · `job669` → [`j669_stuck_all.txt`](../debug_log/2026-09-29/outputs/j669_stuck_all.txt) |
| 09-29 §13.1 | 원인 분석 + 오프라인 재생기 OLD/NEW | 회전 지령 10° < 회전 문턱 11.5° → 병진 비율만 판정. roll 에 쓴 스캔 상관 회전이 문틀에서 −17~−18°(자이로 −6~−10°) → 병진 1~2 cm 과소. OLD 2 건(f0b1 37.4 s 재현 · f0b2 37.3 s 같은 문) / **NEW(자이로 우선) 0 건** | 수정: 창 안 자이로 표본 > 10 이면 roll = 자이로 적분 · 회전 관측 = 자이로. 자체시험 통과 | `job670` · `job671` → [`j671_stuck_offline.txt`](../debug_log/2026-09-29/outputs/j671_stuck_offline.txt) · `job672`(출력 원문 없음) |
| 09-29 §13.1 | 09-07 벽 밀기 bag 은 소실 → 대체 G3b 선언 | — | 받침대(트랙 공중) 직진 · 회전 각 ≤ 3 s 검출 | — |
| 09-29 §13.2 | G3b 받침대 | 직진 0.07 m/s: 휠 0.070 · 자이로 0.004 rad/s → **0.8 s** 판정; 회전 0.3 rad/s: **0.9 s** | G3 종결 → prep 을 `stuck_shadow:=${STUCK_SHADOW:-false}`(**기본 작동**) | `job673` · `job674` → [`j674_stand.txt`](../debug_log/2026-09-29/outputs/j674_stand.txt) |
| 09-29 §13.3 | 사용자 결정 2 건 · nav_guard 구현 | L1 = **보드 전원 차단**(Jetson 도 재부팅 → 복구 = 전원 → rover-base → prep). 심장박동 정지 = 나중. nav_guard 기동 8 s 개입 0, 첫 시도 SIGINT Traceback → 예외 처리 | — | `job675`(출력 원문 없음) |
| 09-29 §13.4 | 시험 범위 조정(사용자) | G2 보류("상황이 발생했을 때"), 발로 막기 기각(발목 · 정강이는 라이다 0.185 m 에 보임 · 끼임 위험). 안 보이는 장애물 = L3 · L0 영역(받침대가 같은 물리 상황) | 무진행 경로 **실동작 미검증** 으로 운용 | — |
| 09-29 §13.5 | G1(`time_limit_override 15`, W3 목표) | 진단 **15.12 s** "시간 한도 초과: 15 s > 15 s (남은 거리 시작 7.15 m)" · CANCELED **15.18 s** · 휠 정지 취소 뒤 **0.38 s** · 기본 한도였다면 234 s | **G1 통과**. 취소 직후 늦은 피드백이 같은 목표를 재등록(로그 "6.09 m → 204 s") → `tripped` 로 무시하게 수정 | `job676` · `job677` · `job678` → [`j678_g1.txt`](../debug_log/2026-09-29/outputs/j678_g1.txt) · `job679` |
| 09-29 §13.6 | G4 생략(사용자: "전원을 끄는 것이기 때문") | 정지 거리 미측정(1:90 기어드라 짧을 것 — 추정) | **② 종결** | — |
| 10-07 §2.2(6 기) | f2c1 목표 4(남서 구석) — 실주행에서 한도 계산 · 무진행 개입 | 목표 시작 11:00:57 첫 피드백 '남은 거리 0.11 m → 시간 한도 33 s'(직전 목표 경로 값) → 같은 0.0 s 에 '2.06 m → 89 s' 로 갱신 = 10-01 §8.13 d0 수정(시작 10 s 안 최대값)이 작동. 11:01:57 Nav2 진행 검사 실패(PoseProgressChecker 0.25 m · 0.5 rad / 25 s) → BT 가 로컬 정리 뒤 FollowPath 만 재시도(스무더 수신 줄 없음 = 재계획 없음) → **11:02:08(시작 71 s, 한도 89 s 전) '무진행: 45 s 동안 최대 0.24 m 이동 < 0.25 m'** → 모든 목표 취소 → 러너 CANCELED 71.2 s. 그 45 s 의 EKF B(odom) 1 s 표본 이동은 보간하면 기준점(+33.2 s)에서 최대 ≈ 0.26~0.28 m(+41~+45 s 표본) — nav_guard 는 피드백 `current_pose`(map) 기준이라 창 안의 map→odom 보정(≈ 11:01:27 14.4 cm)만큼 달라질 수 있음(추정) | 설계대로 개입(진행 검사 재시도가 다시 25 s 를 채우기 전에 끊음). 다만 판정이 0.25 m 경계에서 갈림 — 좁은 곳에서 돌며 조금씩 움직이는 정체는 문턱 근처에 머무를 수 있다. 같은 자리 f2d1(69.4 s)도 nav_guard 취소로 서술됐으나 로그는 원천 소실 → [남서 구석 방향 맞춤 정체](southwest-orient-stall.md) | [`j908_g4log.txt`](../debug_log/2026-10-07/outputs/j908_g4log.txt) · [`f0_f2c1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c1_runner.log) · [`j910_g4cost.txt`](../debug_log/2026-10-07/outputs/j910_g4cost.txt) · [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) · 그때 코드 = 커밋 `273ddc7f` 판(다음 변경은 10-22 `0c0523de` 기록 간격뿐) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| f0b1 t 36.9 s 판정은 참 정체 | 같은 2 s SLAM 이동 | 15.0 cm · −12.5° 움직임 | 기각 — 오판(측정) |
| 오판 = 스캔 상관 회전 과대 → 병진 과소 | 재생기 OLD vs NEW | OLD 2 · NEW 0 | 지지(오프라인 재생). **실주행에서 NEW 가 켜졌는지는 확인 안 함**(실수 2) |
| 수정 뒤에도 참 정체를 잡는다 | 받침대 G3b | 0.8 · 0.9 s | 지지(측정) — 자이로가 0 이고 스캔도 안 변하는 상황이라 OLD · NEW 어느 쪽이든 잡히는 시험(코드 읽기 — 이 시험은 NEW 를 판별하지 않음) |
| nav_guard 시간 한도가 PC 와 무관하게 멈춘다 | G1 | 15.12 · 15.18 · +0.38 s | 지지(측정, 단일 목표) |
| nav_guard 무진행 한도가 작동한다 | G2 | 보류 | 미확인(09-29) → 10-01 §8.27 실개입으로 확인(이후) |

## 4. 조치와 효과 (09-29 종결 때의 층별 상태)
| 층 | 내용 | 09-29 상태 |
|---|---|---|
| L0 펌웨어 | 워치독 500 ms · 스톨 정지 · 래치 | 기존(09-07 받침대 검증 — [스톨 보호 래치](stall-latch.md)) |
| L1 보드 전원 스위치 | 모터 구동 전원까지 끊는 최후 수단 | 있음, **정지 거리 미측정** |
| **L2 nav_guard** | 목표별 시간 한도 · 45 s 무진행 → 전부 취소 + 정지 | 시간 한도 **G1 통과**, 무진행 **미검증** |
| L3 stuck_monitor | 휠은 도는데 몸이 안 감 | 작동 전환(G3 오판 0 · G3b 0.8~0.9 s) — ⚠ 아래 실수 2 · 이후 |
| L4 원격 정지 | PC `job156` | 기존(Wi-Fi 있을 때) |
| (선택) 심장박동 | PC 1 Hz 신호 5 s 끊기면 정지 | 사용자: 나중(F2 전 재검토) |
남는 빈틈(§13.4): **가볍고 안 보이는 물체는 밀고 간다**(몸이 움직여 어떤 층도 이상으로 안 봄) → 운용 규칙(바닥 정리)으로만.

## 5. 내 실수
**실수 1 — nav_guard 한도를 첫 피드백의 남은 거리로 고정(09-29 구현 → 10-01 §8.13 정정)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 목표별 시간 한도 = 처음 남은 거리 / 0.07 × 2 + 30 s(러너와 같은 식) — `nav_guard.py` 09-29 판 |
| 본 것 | f2a5: B 도착 뒤 C(3.87 m) 목표가 34.3 s 에 취소, 로버는 정상 주행 중. 로그 "목표 ed99afdb: 남은 거리 **0.15 m** → 시간 한도 **34 s**". f2a4 에도 "0.14 m → 34 s" |
| 처음 추론 | (09-29) 첫 피드백 = 새 목표 경로의 남은 거리라고 가정 — G1 은 단일 목표라 드러나지 않음 |
| 의심한 이유 | 34 s = 0.15/0.07 × 2 + 30 — 남은 거리 0.15 는 직전 목표 B 의 xy 허용(0.15) 근처 값 |
| 판별 | 같은 계산이 두 회차에 반복 · 값이 B 도착 직전과 일치(로그) |
| 결론 | 새 목표 직후 bt_navigator 피드백은 새 경로가 나오기 전의 **직전 목표 남은 거리**(추정 — 내부 순서는 코드로 확인 안 함). 수정: d0 = 시작 뒤 10 s 안의 남은 거리 **최대값**(`d0_window`), f2a6 에서 "0.14 m → 34 s" 직후 "4.00 m → 144 s" 로 덮임 확인 |
| 다음에 알아보는 법 | 액션 피드백의 '첫 값' 을 기준으로 삼지 않는다 — 연속 목표 시험(목표 2 개 이상)으로 검증하고, 한도가 바뀔 때 로그를 남긴다 |
| 데이터 | `2026-10-01/outputs/j751_cancel2.txt` · `f0_f2a5_runner.log` · `j754_d_why.txt` · `jobs/job752_deploy_guard.sh` · 지금 코드 `nav_guard.py` `cb_fb` 의 2026-10-01 주석 |

**실수 2 — '자이로 우선' 수정을 오프라인으로만 검증하고 L3 를 작동으로 바꿈(09-29 §13.1~§13.2 → 10-01 §8.11 · 10-29 §8)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | stuck_monitor 오판 기전 수정 후 작동 전환 |
| 본 것 | 재생기 `job670` NEW 0 건, 자체시험 통과(`job672`), 받침대 0.8~0.9 s |
| 처음 추론 | 설치본에 수정이 들어갔으니 실주행도 NEW 로 판정한다 |
| 의심한 이유 | 10-01 f2a4 오판 취소를 조사하다 실행 중 파라미터를 보니 `use_gyro = False` |
| 판별 | `stuck_monitor.py` 85 행 `('use_gyro', False)`(09-08: 200 Hz IMU 구독 rclpy 역직렬화 CPU ~25 % 로 기본 끔) · 102 행 `if use_gyro:` 일 때만 `/imu/data` 구독 → 창 안 자이로 표본 0 → 스캔 상관(OLD 경로)으로 대체. launch 는 `shadow_mode` 만 넘김(지금 코드에서도 같음) |
| 결론 | 재생기는 bag 의 `/imu/data` 를 직접 읽어 NEW 를 흉내 냈을 뿐, 실주행 노드는 자이로를 받지 않았다. 받침대 시험은 자이로 · 스캔 둘 다 0 이라 이 차이를 가르지 못한다. f2a4 오판의 직접 원인인지는 재현(`job748`)으로는 아님 |
| 다음에 알아보는 법 | 오프라인 재생기로 고친 판정은 **실행 중 노드의 파라미터 · 구독 목록**(`ros2 param get` · `ros2 node info`)으로 같은 경로가 켜졌는지 확인한 뒤에 '검증' 이라고 쓴다. 판별 시험은 두 경로가 **다른 답**을 내는 상황(문 통과 회전)으로 고른다 |
| 데이터 | `2026-10-01/SUMMARY.md` §8.11 · `outputs/j747_stuckchk.txt` · `j748_sector.txt` · `2026-10-29/SUMMARY.md` §8 · [정체 감시 stuck_monitor](stuck-monitor.md) |

**실수 3 — nav_guard CPU 원인을 '기록 거르기' 로 단정(10-22 §18 → §20)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2pi1 노드별 CPU 에서 nav_guard 24.8 % 의 원인 제거 |
| 본 것 | `anal_cpu_nodes_f2pi1.txt` nav_guard 24.8 % |
| 처음 추론 | 피드백(BT 주기 최대 100 Hz)마다 45 s 기록 전체를 파이썬 리스트로 다시 거르는 비용(코드 읽기 — 피드백 주기 실측 안 함) |
| 의심한 이유 | 수정(0.2 s 간격 기록 · 앞에서 버림) 뒤 확인 기준 '< 5 %' 를 선언해 둠 |
| 판별 | f2sm3 `anal_cpu_nodes_f2sm3.txt`: **24.8 → 19.5 %** |
| 결론 | 거르기는 일부일 뿐 주원인이 아님. 남은 후보 = 고주파 피드백을 rclpy 가 역직렬화하는 비용 자체(미확인 — stuck_monitor 의 200 Hz IMU 구독 25 % 와 같은 모양) |
| 다음에 알아보는 법 | rclpy 노드 CPU 는 먼저 **구독 주기 × 메시지 크기**를 재고(`ros2 topic hz` · `bw`) 콜백 안 계산을 의심한다 |
| 데이터 | `2026-10-22/outputs/anal_cpu_nodes_f2pi1.txt` · `anal_cpu_nodes_f2sm3.txt` · `jobs/up_navguard_1022.sh` → `outputs/up_navguard_1022.txt` · 러너 `rss_f2pi1.txt`(PC 스크래치패드 — **원천 소실**) |

**기록 · 원문 대조**: §13.5 '남은 거리 7.15 → 6.09 m(≈ 1.06 m 전진 뒤 정지)' — `j678_g1.txt` 의 `출발 map None`(시험 스크립트가 출발 자세를 못 받음) → 1.06 m 는 map 이동이 아니라 **nav_guard 로그의 남은 경로 길이 차**다(측정 경로 다름, 이동 거리 자체는 미측정).

## 6. 남은 것 (09-29 시점)
- G2(무진행 실동작) · G4(전원 스위치 정지 거리) · G3c(안 보이는 낮은 물체) · G5(심장박동) — 미실행.
- E-stop(펌웨어) 미구현.
- 가볍고 안 보이는 물체 밀기 — 운용 규칙만.

## 7. 이후 (09-30 ~) — 포인터
- **10-01 §8.7**: prep 이 nav_guard 를 정리 목록에서 빠뜨려 2 개가 동시에 떠 있었음(55 분 전 것) → `job240` 정리 목록에 추가(지금 `Docs/tools/prep_fast.sh` 17 행 `PATS` 에도 있음 — 코드 확인). §8.11: f2a4 stuck_monitor 오판 취소 · `use_gyro=False` 발견(실수 2). **§8.12 사용자 결정: F2 순회 동안 stuck_monitor 관찰만** — 안전은 nav_guard · 펌웨어 · 전원 스위치. §8.13~§8.14 d0 결함 수정 · 확인(실수 1). **§8.27 f2a10: 무진행 첫 실개입** — 목표 2 59.5 s, "45 s 동안 최대 0.24 m"(SUMMARY '정상 개입') → 09-29 미검증이던 무진행 경로가 실주행에서 동작 — [10-01 SUMMARY](../debug_log/2026-10-01/SUMMARY.md).
- 10-02 §6.4 · 10-07 §2.2 · §6.2 · §7.1: 남서 목표 방향 맞추기 정체 · 상자 앞 정지를 nav_guard 가 취소(무진행 또는 시간) — 각 SUMMARY. 10-12 §3.2 f2f2: 지도 서버 unconfigured 로 경로가 없어 45 s 뒤 무진행(0.00 m) 취소 — 코드상 d0 가 안 잡히면 시간 한도 없이 무진행만 판정하는 경로가 실제로 작동한 예.
- 10-14 §13.1 f2s1: 목표 위치 2.9 cm 안인데 끝 방향 문제로 멈춤 → Nav2 진행 검사기(25 s) 뒤 nav_guard 무진행(0.24 m) 취소 — 원인은 경로 끝 방향(`CopyPath` 로 해결, CLAUDE.md §6).
- 10-22 §18 · §20: nav_guard CPU 24.8 → 19.5 %(실수 3), 미해결 — 10-23 SUMMARY 끝 '미해결 그대로' 목록에도 있음.
- 10-23 ~ 10-28 순회 판정 ① 에 'nav_guard 취소 0' 이 들어가 매 회 기록(10-27 · 10-28 모두 0).
- **지금 운용(코드 확인)**: `navigation.launch.py` 기본 `nav_guard:=true` · `stuck_shadow:=false`(작동) 이지만, 순회 prep `Docs/tools/prep_patrol.sh` 17 행이 `STUCK_SHADOW=true` 를 강제하고 `prep_fast.sh` 기본도 `${STUCK_SHADOW:-true}` → **stuck_monitor 는 관찰 모드**, `use_gyro` 는 여전히 기본 False. 09-29 §13.2 의 'prep 기본 = 작동' 은 10-01 §8.12 부터 맞지 않는다. CLAUDE.md §6 의 'stuck_monitor(09-29 자이로 우선 수정 뒤 **작동 모드** — prep `STUCK_SHADOW=true` 면 관찰만)' 문구는 지금 prep 이 늘 true 라는 점과 자이로 경로가 꺼져 있다는 점을 빠뜨림(10-29 §8 지적과 같음).
- F2.5 `place_server.py` 도 취소를 같은 방식(빈 `CancelGoal` = 모든 목표)으로 하고, 시간 · 무진행은 nav_guard 에 맡긴다(코드 18 · 261 행). `place_web.py` 의 휴대폰 정지는 Wi-Fi 의존 '보조'(코드 12 행).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job668` · `job669` | bag 20 개 `/rover/stuck` 전수 조사 | → `j669_stuck_all.txt` |
| `job670` · `job671` | stuck_monitor 오프라인 재생 OLD/NEW | → `j671_stuck_offline.txt` |
| `job672` | stuck_monitor 빌드 · 자체시험 | 출력 원문 없음 |
| `job673` · `job674` | G3b 받침대 | → `j674_stand.txt` |
| `job675` | nav_guard 빌드 · 기동 8 s | 출력 원문 없음 |
| `job676` | G1 prep(stuck ACTIVE · nav_guard) | 출력 원문 없음(j678 앞 확인값은 SUMMARY) |
| `job677` · `job678` | G1 시간 한도 | → `j678_g1.txt` |
| `job679` | `tripped` 수정 빌드 | 출력 원문 없음 |
| `nav_guard.py` | L2 노드 | `ros2_ws/src/rover_bringup/scripts/` |
| (10-01) `job752_deploy_guard.sh` · (10-22) `up_navguard_1022.sh` · `chk_navguard_inst.sh` | d0 수정 · CPU 수정 배포 | 각 날짜 `jobs/` |

## 9. 도구 해설
공통: Jetson 에서 `run_jn.sh` 로 실행. bag 은 `/tmp/bag_<이름>`(PC 로컬 tgz 를 다시 올려 풂, 09-29 §0).
도구 계보: (정체 판정) `stuck_monitor.py` 09-08 → 09-18 → **09-29 자이로 우선**(use_gyro 꺼짐) / 평가 `job668`(기록된 판정 읽기) → `job670`(판정식 재생, 설치본 함수 import) → 10-01 `job747` · `job748`(섹터 재현). (목표 한도) PC 러너 `job550` 한도 식 → **`nav_guard.py`**(같은 식, Jetson) → 10-01 d0 창 → 10-22 기록 간격.

### nav_guard.py — 온보드 목표 한도 (Jetson, Python rclpy, 지금 코드 기준)
- 실행 위치 · 부른 형태: `navigation.launch.py` 가 `Node(package='rover_bringup', executable='nav_guard.py', name='nav_guard')`, 조건 `nav_guard:=true`(기본). 파라미터 `enable True` · `v_nominal 0.07` · `time_factor 2.0` · `time_margin 30` · `time_limit_override 0` · `no_progress_s 45` · `no_progress_m 0.25` · `rate 5` · `d0_window 10` — **매 틱 다시 읽어** `ros2 param set /nav_guard …` 로 실행 중 변경 가능(G1 이 이것을 씀).
- 왜: 시간 한도가 PC 러너에만 있어 Wi-Fi 가 끊기면 사라짐 · Nav2 엔 전체 시간 한도가 없고 진행 검사기(0.25 m/25 s)는 Nav2 가 건강할 때만(머리 주석).
- 하는 일: ① `/navigate_to_pose/_action/feedback` 구독 — 목표 id 별로 `t0`(첫 피드백 벽시계), `d0` = 시작 뒤 10 s 안 `distance_remaining` 최대값(0 초과, 이전보다 5 cm 넘게 클 때만 갱신 · 로그), `limit = d0/0.07 × 2 + 30`; 위치 기록은 0.2 s 간격으로만, `no_progress_s + 2` s 넘은 것은 앞에서 버림. `tripped` 에 든 목표는 무시 ② `/navigate_to_pose/_action/status` — ACCEPTED · EXECUTING · CANCELING 이 아닌 목표는 지움 ③ 5 Hz `tick`: 경과 > (override > 0 ? override : limit) 이면 시간 위반; 경과 > 45 s 이고 45 s 전 기준점 `a` 이후 기록 중 `a` 에서 가장 먼 거리 < 0.25 m 이면 무진행 위반 ④ `trip`: ERROR 로그 · `/rover/guard` DiagnosticArray(ERROR, 목표 id 앞 8 자) → `cancel_goal` 서비스에 **빈 요청 = 모든 목표 취소**(서비스 없으면 정지 지령만) → 1 s 동안 20 Hz 로 `/cmd_vel` 0 → 지금 목표들을 `tripped` 에 넣고 비움.
- 출력: nav2 로그 `/tmp/nav2.log`(prep 마다 덮음 — 날짜별 `outputs/` 에 발췌: `j678_g1.txt` · 10-01 `j751_cancel2.txt` 등), `/rover/guard` 토픽.
- 쓰인 곳: §13.5 G1 · 10-01 이후 모든 순회 판정의 'nav_guard 취소' 칸.
- 알려진 결함 · 한계: d0 가 한 번도 안 잡히면(남은 거리 0 만 옴) 시간 한도 없음 → 무진행만(10-12 §3.2 가 그 예). 시간은 벽시계(`time.time()`) — sim 시간 미지원. 한 목표 위반이 **모든 목표**를 취소(place_server 목표 포함 — 의도된 설계). CPU 19.5 %(실수 3, 미해결). `/cmd_vel` 에 직접 0 을 내므로 velocity_smoother 출력과 1 s 동안 섞임(펌웨어는 마지막 수신값 사용 — 실제 정지는 G1 에서 0.38 s 로 측정됨).
- 지금 다시: 운용 중.

### job668_stuckscan.py · job669_stuck_all.sh — 기록된 정체 판정 전수 조사 (Jetson, Python)
- 부른 형태: `python3 job668_stuckscan.py BAG [BAG …]`(`job669` 가 f0a1~f0b2 · s1 · s2 · r1 · r1b · r2 · r2b · r3 · l1 · l2 · s_fb1 · s_fb2 를 풀어 넘김).
- 하는 일: bag 의 `/rover/stuck`(판정 때만 발행) 마다 첫 지령 기준 시각 · 메시지 · map 위치(map→odom∘odom→base_link) · 직전 2 s 지령 평균 v · ω · **같은 2 s 실제 map 이동 cm · 회전 °**(SLAM 자세 = 스캔 정합 기반 — 독립 기준).
- 출력: `j669_stuck_all.txt`.
- 전제: 'stuck_monitor 코드는 09-18 이후 그대로 → bag 판정 = 현재 코드 판정'(머리 주석) — 09-29 수정 전까지만 성립.

### job670_stuck_offline.py · job671 — 판정 재생 OLD/NEW (Jetson, Python)
- 하는 일: 설치본 `stuck_monitor.py` 를 `importlib` 로 읽어 `profile` · `rot_shift_deg` · `sector_delta` 를 그대로 쓰고, `tick()` 판정식을 옮김(5 Hz · 창 2 s · v_thr 0.015 · w_thr 0.10 · ratio 0.25 · confirm 2 · cooldown 5 s). bag 시간으로 재생. OLD = roll 스캔 상관 · 회전 관측 max(|스캔|, 자이로), NEW = 창 안 자이로 있으면 roll = 자이로 누적 · 관측 = |자이로|. 복구 행동 보류는 상태 토픽이 없어 생략.
- 출력: `j671_stuck_offline.txt`(OLD 2 · NEW 0).
- 결함: **bag 의 `/imu/data` 를 직접 읽으므로** 실행 중 노드의 `use_gyro` 설정과 무관하게 NEW 가 '켜진' 상태를 흉내 냄(실수 2).
- 계보: 10-01 `job748_sector.py`(섹터 계산만 재현).

### job673_stand.py · job674 — 받침대 G3b (Jetson, Python)
- 하는 일: `/cmd_vel` 20 Hz 로 정지 3 s → 직진 0.07 m/s 6 s → 정지 7 s(쿨다운 5 s 넘김) → 회전 0.3 rad/s 6 s → 정지 3 s. `/rover/stuck` 판정 시각(구간 시작 기준) · `/wheel_odom` 휠 속도 · 자이로 yaw 기록. 판정 = 직진 · 회전 각 시작 ≤ 3 s 에 ≥ 1. `job674` 는 앞에 `job657` prep(그림자 모드).
- 출력: `j674_stand.txt`.
- 한계: 몸이 안 움직여 OLD · NEW 가 같은 답을 내는 시험(§3).

### job677_g1.py · job678 — nav_guard G1 (Jetson, Python)
- 하는 일: `ros2 param set /nav_guard time_limit_override 15` → W3 (5.5, −2.2) `NavigateToPose` → 목표 수락 기준 `/rover/guard` 진단 시각 · 목표 상태 CANCELED 시각 · 휠 정지 시각(|v| < 0.005 · |ω| < 0.02 가 0.5 s 지속) · 이동 거리(map, TF) → 판정 → override 0 원복. `job678` 은 끝에 nav2.log 의 nav_guard 줄 4 개.
- 출력: `j678_g1.txt`.
- 결함: 출발 map 자세를 못 받아 `출발 map None` → 이동 거리 미측정(§5 끝).

### job675 · job679 · job672 — 배포 · 빌드 (Jetson, bash)
- `job675`: `colcon build rover_bringup rover_navigation` → 설치본 확인 → `navigation.launch.py --show-args` 에 `nav_guard` 인자 → `timeout -s INT 8 ros2 run … nav_guard.py`(rc 124 = 정상). `job679`: 빌드 뒤 `grep -c tripped`. `job672`: stuck_monitor 빌드 · `--selftest`(회전 15.0° · 병진 0.050 m 기대값). 셋 다 출력 원문 없음.

## 10. 용어
- **그림자(관찰) 모드**: 판정 · 진단은 내되 목표 취소 · 정지 지령은 내지 않는 모드(`shadow_mode`).
- **무진행 한도**: 일정 시간 동안 위치가 일정 거리 넘게 안 바뀌면 진행 없음으로 보는 규칙 — Nav2 진행 검사기(0.25 m/25 s)와 nav_guard(0.25 m/45 s).
- **빈 CancelGoal 요청**: goal_info 가 비면 액션 서버의 모든 목표 취소(ROS 2 액션 규약).
- **받침대 시험**: 트랙을 공중에 띄워 '휠은 돌고 몸은 정지' 를 만드는 정체 재현.
