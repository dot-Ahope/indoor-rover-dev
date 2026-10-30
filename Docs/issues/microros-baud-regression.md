# micro-ROS 링크에서 `/wheel_odom` 이 사라진 문제 — 2 Mbps 회귀, 460 800 bps 우회

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(보드율을 낮춰 증상 0) · **근본 원인 미확정**(08-27 엔 같은 2 Mbps 가 정상 → 회귀, 후보 셋 미판별) | 09-09 하루(이후 재시험 기록 없음 — 10-14 구성표에도 '2 Mbps 회귀 미해결') | [09-09 §3](../debug_log/2026-09-09/SUMMARY.md) — `job92` 주행 중 EKF 8.5 m 발산 | `firmware/.../Core/Src/usart.c`(USER CODE 2 의 override `huart1.Init.BaudRate = 460800`) · `ros2_ws/src/rover_bringup/launch/base.launch.py`(agent `-b 460800`) · `App/microros/microros_task.c`(발행 게이트 · TX 진단 카운터) · `App/microros/microros_transport.c`(링 버퍼 재작성) — 커밋 `7cc12d6`(USB 결론, 틀림) → `f1a76d86`(우회 · 정정) | [보드 연결 · micro-ROS 세션](board-link-microros-session.md)(세션 재수립 · RESET 규칙) · [DDS 공유메모리 사고](dds-shm-incident.md)(같은 날, 내가 만든 다른 고장) · [CPU 부족 정지](cpu-load-stalls.md)(같은 날 오후) · [모터 PWM 20 kHz 정정(09-07)](stall-latch.md)(회귀 후보 2) |

**한 줄**: 09-09 아침 첫 주행(`job92`)에서 로버는 거의 안 움직였는데 좌표가 1 초에 8.5 m 튀었다. EKF 가 유일한 속도 관측인 `/wheel_odom` 을 잃고 카메라 가속도만 적분한 결과였다. 하루 동안 시계 · 크기 · `/cmd_vel` · CPU 를 기각했고(그 사이 `pkill "a\|b"` 로 측정을 오염시킴), 링크를 5 초 버킷으로 보니 odom 과 보드 IMU 가 50 Hz 를 번갈아 차지했다. 그것을 'USB Full-Speed 32 B 엔드포인트 상한(32~40 kB/s)' 으로 설명하고 커밋까지 했으나(**틀림**), 발행량을 22 kB/s 로 줄여도 odom 이 0 이었다. agent · rcl · 전송 계층을 계측으로 차례로 지우자 남은 구간은 'STM32 UART → CH340 → USB' 뿐이었고, 보드율을 2 000 000 → 460 800 으로 낮추자 70 s 연속 100 % 전달로 돌아왔다. 그 뒤 사용자 질문("어제까지 되던 게 왜?")으로 08-27 의 같은 2 Mbps 60 kB/s 기록을 찾아 '용량 한계가 아니라 회귀' 로 정정했다. 회귀 원인(배선 · 09-07 PWM 20 kHz · CH340/드라이버)은 지금도 판별되지 않았다.

## 1. 증상
- `job92_avoid.py 1.80 90` 주행 t = 2 → 3 s 에 전진 +0.000 → **+8.543 m**, 횡 −1.209 m, 상자 거리 1.004 → 7.644 m. 깊이 여유는 0.625 → 0.574 m 로 연속 — **로버는 물리적으로 거의 그대로, 좌표만 튐**. 결과 ABORTED(`GridBased: failed to create plan` 반복 → `Goal failed`). [09-09 §3](../debug_log/2026-09-09/SUMMARY.md)
- `job93` TF: `map→odom` [1.119, −0.066] · `odom→base` **[5.725, 0.618]** → SLAM 점프가 아니라 **EKF 오도메트리 발산**(§3).
- 그 뒤 관측: `/wheel_odom` 이 수십 초 단위로 0 Hz, 작은 토픽(`/rover/status` 5 Hz · `/battery` 1 Hz)은 그동안 정확한 주기 유지(§5).
- 출력 원문: **09-09 는 `outputs/` 가 비어 있다** — 이 날 모든 수치는 SUMMARY 서술(과 커밋 메시지)뿐이다(10-20 §7.2 도 같은 사실을 적음). CSV(`/tmp/job92.csv` 등)도 Jetson `/tmp` 에만 있었고 **원천 소실**.

## 2. 흐름 (시간순)
jobs 는 전부 [2026-09-09/jobs/](../debug_log/2026-09-09/jobs/). 출력은 전부 '원문 없음'(위 §1). 순서는 job 번호 = 실행 순서로 본다(같은 날 연속 번호, SUMMARY 서술 순서와 일치).

| 곳 | 한 일 | 본 것(수치, SUMMARY 기준) | 그때 결론(틀렸으면 표시) | 도구 |
|---|---|---|---|---|
| §1 | Jetson 재부팅 뒤 `/tmp` 스크립트 재전송 → `job20a_boot.sh` 스택 기동 | — | 09-08 배포한 inflation 0.40 / padding 0.02 검증이 목표 | `run_xfer_all.sh` · (08-31) `job20a_boot.sh` |
| §2 | 무주행 경로 질의 | 경로 2.75 m, 최대 횡 +0.488 m, 비용 최대 71 → 최근접 0.294 m | 설정은 의도대로(이 카드 범위 밖) | `job91_query.py` |
| §3 | 회피 주행 | t = 3 s 에 +8.543 m 점프, ABORTED, 최소 여유 34.3 cm | — | `job92_avoid.py` |
| §3 | 점프 위치 특정 | map→odom 1.1 m · odom→base 5.7 m | **EKF 발산**, 원인 = `/wheel_odom` 소실 | `job93_jump.sh` |
| §4 가설 1 | 시계 스텝 | `journalctl`: NTP 초기 동기 09:43:18, 스택 09:49:50, 주행 09:56 · stamp − host **−0.010 s** | 기각 | `job94_clock.sh` |
| | QoS · 퍼블리셔 · BEST_EFFORT 수신 | (수치 SUMMARY 미기록) | — | `job95_wodom.sh` |
| | 보드 토픽 생존 · agent 로그 | (수치 미기록) | — | `job96_session.sh` |
| | 보드 RESET 뒤 복구 시도(①에서 `/wheel_odom` · `/imu/data_raw` > 20 Hz 아니면 중단) | (미기록) — 정리 단계 `pkill` 의 백슬래시+세로줄 패턴(§5.2) 가 **아무것도 안 죽임** | (그때는 몰랐음 → §5.2 실수) | `job97_recover.sh` |
| | agent 의 client_key 별 엔티티 수 · 오류 | (미기록) | — | `job98_entities.sh` |
| | agent 프로세스 rchar/wchar(호스트 `pgrep`) + 30 s 동시 수신 | (미기록) | 호스트에서 컨테이너 프로세스 `/proc/<pid>/io` 를 못 읽었을 것(**추정** — 후속 job105 가 `docker exec` 로 바꿈) | `job99_bytes.sh` |
| §4 가설 3 | `/cmd_vel` 이 보드 스핀 루프를 무너뜨리나 | `/cmd_vel` 은 **무발행** | 기각 | `job100_cmdvel.sh`(정리 단계는 같은 ERE 패턴 결함, §5.2) |
| §4 가설 4 | 부하 단계(base → +sensors → +slam → +nav2)별 보드 토픽 Hz · idle | idle **56.6 %** 에서 odom **0.00 Hz**, idle **14.6 %** 에서 **24.91 Hz** — 부하와 역상관 | 기각 | `job101_load.sh`(⚠ 단계 (1) 의 정리가 ERE 패턴 결함으로 실패 — §3 표 주석) |
| §4 '내가 만든 오염' | 프로세스 수 세기 → `for p in …; do pkill -9 -f "$p"` 로 고침 → base 만 60 s | `ekf_node` 2 개 등 중복 스택, load **16.8**, SSH 'No route to host' 3 회 | job97 · 100 · 101 의 정리 실패 = 원인. 그 구간 측정 **폐기** | `job102_clean.sh` |
| §5 | 깨끗한 상태(중복 없음, 아무것도 안 죽임) 60 s, 5 초 버킷 | 0–5 s odom 38.34, 5–25 s ≈49, 25–30 s 4.00, 30–60 s **0.00**; imu 0 → ≈1.0; status ≈5; battery 1.00 | 'odom 이 50 Hz 를 독점하다 소멸' | `job103_obs.sh`(표의 4 칸 구성과 맞음 — SUMMARY 는 job104 로 적음, §6 모순 3) |
| §5 | 고아 Nav2 제거 → 60 s (conditioned 칸 추가) | (위 표와 함께 인용) | — | `job104_obs2.sh` |
| §5 | 90 s 관측 + agent rchar/wchar(컨테이너 안 `/proc`) | 40–50 s odom **50.9** / imu 0.0 · 60–70 s odom 0.0 / imu **50.9** · 25–40 s odom ≈40 / imu ≈35 / status 0 / battery 0 | **교대 점유 = 용량 경쟁**(무작위 손실이 아님 — 작은 토픽은 정확) | `job105_bytes.sh`(B/s 칸 결과는 SUMMARY 에 없음) |
| §6 | agent 인자 · termios · USB · io 재시도 | agent Cmd `serial --dev /dev/rover -b 2000000` | — | `job106_baud.sh`(⚠ `stty -F /dev/ttyUSB0` = **라이다** 장치를 봄, §9 결함) |
| §6 | 시리얼 장치 전체 · CH340 엔드포인트 크기 | `/dev/rover → ttyCH341USB0`(1a86:7523), `/dev/rplidar → ttyUSB0`(CP2102N, cp210x). `1-2.1` speed 12 Mbps, ep_02 / ep_82 **wMaxPacketSize 0x20(32 B) Bulk**, ep_81 0x08 Interrupt 1 ms | '**USB FS 32 B 엔드포인트가 상한 32~40 kB/s**' — odom 단독 50.9 Hz × 720 B = 36.6 kB/s 와 '맞아떨어져' 확신 → **틀림(§10)** | `job107_port.sh` |
| 커밋 `7cc12d6`(10:40) | 위 결론 + 펌웨어 발행 게이트(odom 매 cycle → 30 Hz 의도, imu · mag 5 Hz) | 커밋 메시지: '합계 25.4 kB/s ≈ 상한의 65 %' | (상한 개념이 틀렸으므로 '65 %' 도 무의미) | `microros_task.c` |
| §6.5 | agent rchar 를 토픽 수신과 같은 버킷으로(실행 파일 = `micro_ros_agent` 인 pid) | (미기록) | — | `job108_rchar.sh` |
| | 컨테이너 안에서 본 Hz vs 호스트에서 본 Hz | (미기록) | — | `job109_inside.sh` |
| §6.5 | agent 를 `-v6` 로 다시 띄움 → 사용자 보드 RESET → 60 s 수집 · 집계 | **`recv_message` 1020 = DDS `write` 1020** | agent 는 받은 것을 버리지 않음 | `job110_v6.sh` → `job111_v6read.sh` · `job114_lenhist.sh` |
| §6.5 | 펌웨어에 TX 카운터(`/rover/status` 의 `TX` 값) 넣고 5 초 차분 | odom 발행 시도 **25/s**, 실패 **0**, rc **0** | rcl · 버퍼 · MTU 아님 | `job112_txdiag.sh` |
| §6.5 | 전송 계층 카운터 | (저장본 job113 은 `wc/wb/wh/wt/wl` — 옛 세마포어 전송판) → 링 버퍼판에서 **wb / wh / wf 전부 0, 링 최대 점유 1559 / 8192 B** | 보드는 모든 바이트를 정상 송신 | `job113_txlayer.sh`(+ 저장 안 된 후속판 — §9) |
| §6.5 | 남는 구간 = UART → CH340 → USB, `HwFlowCtl = NONE`. agent 를 정상 판으로 되돌림 → 확인 → `-b 460800` 배포 + 펌웨어 460800 | 2 Mbps: odom 시도 25/s → 수신 **0~13 Hz, 30 s 단위 전멸 반복** / 460 800: **25.0 Hz, 70 s 연속 100 %, 드롭 0** | 해소 | `job115_normalagent.sh` → `job116_chk.sh` → `job117_baud.sh` → (70 s = 14 버킷 × 5 s 라 job112 또는 job113 의 재실행으로 **추정**) |
| §6.5 | 전 토픽 주기 · dmesg | odom 25.005 / imu 5.000 / mag 5.000 / status 5.000 / battery 1.000 / conditioned 25.018 / filtered 30.003. `dmesg` ch341 오류 **없음** | '커널이 못 보는 CH340 칩 내부 유실과 일관'(**추정**) | `job118_verify.sh` |
| §7 · 커밋 `f1a76d86`(11:38) | 대역 예산 확정(odom 33 ms 게이트 → 실효 25 Hz, imu · mag 5 Hz) + 링 버퍼 전송 + 보드율 460800(양쪽) | 수지 '22.4 kB/s = 460 800 의 49 %'. 빌드 text 132 920 / data 5 032 / bss 108 744 | 게이트는 원인과 무관하게 유지 | 펌웨어 · `base.launch.py` |
| §10 | 사용자 질의 "어제까지 잘 되던 데이터 크기가 왜?" → `git log -S"BaudRate = 2000000"` · 과거 로그 | 2 Mbps 는 **2026-05-28(`a72b369`)부터 불변**. 08-26 `/wheel_odom` 49.998 · `/imu/data_raw` 49.999 Hz, [08-27 `job4x_sensors_slam.txt`](../debug_log/2026-08-27/outputs/job4x_sensors_slam.txt) `/wheel_odom` **49.995** | **'용량 상한' 폐기 → 08-27 ~ 09-09 사이의 회귀** | (대화 중 명령, 스크립트 없음) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| SLAM 점프 | job93 TF 분해 | map→odom 1.1 m, odom→base 5.7 m | **기각** — EKF 쪽 |
| 시계 스텝(NTP) | job94 journalctl · stamp 오프셋 | 동기 완료가 주행 13 분 전, 오프셋 −0.010 s | **기각** |
| 메시지 크기 | 보드 리셋 뒤 토픽별 Hz | `/rover/status`('큰 메시지') 4.6 Hz 회복, odom 만 0 | SUMMARY: **기각**('크기 단조성이 깨짐'). ⚠ 근거가 같은 문서 수지표와 안 맞음 — status 는 ~280 B 로 odom(~720 B)보다 작고 imu(~330 B)보다도 작다. 280 B 가 살고 720 B 가 죽은 것은 오히려 크기 순서와 **맞다**. §9 교훈 4 도 '부분 실패는 크기 순으로 온다' 고 쓴다 → 이 기각은 근거가 약함(원문 없어 그때 무엇을 '큰 메시지' 로 봤는지 **미확인**) |
| `/cmd_vel` 수신 트래픽 | job100 | `/cmd_vel` 무발행 | **기각** |
| CPU 경합 | job101 부하 단계별 idle · Hz | idle 56.6 % → 0 Hz, 14.6 % → 24.91 Hz | **기각**(역상관). ⚠ job101 은 정리 단계가 ERE 패턴 결함으로 실패한 스크립트 중 하나 — '단계' 이름(base 만 등)은 실제와 달랐을 것. 다만 같은 창의 idle · Hz 쌍이므로 역상관 관찰 자체는 단계 이름과 무관(원문 없음) |
| 컨테이너 ↔ 호스트 DDS 전달 | job109 안 · 밖 Hz 비교 | SUMMARY 에 결과 없음 | **미기록** — 뒤의 `-v6`(agent 가 DDS 로 1020 건 write)로 간접 배제 |
| USB FS 32 B 벌크 엔드포인트 상한 32~40 kB/s | job107 엔드포인트 크기 × '1 ms 프레임당 패킷 1 개' 가정 | 36.6 kB/s 와 일치해 확신 → 08-27 60 kB/s 로 반증 | **기각**(§10). 덧붙여 '1 ms 프레임에 벌크 패킷 1 개' 가정 자체가 USB FS 사양과 다르다(한 프레임에 여러 벌크 패킷 가능 — 일반 사양 기준 **추정**, 이 장비에서 재지 않음) |
| 수요 > 용량(경쟁) — 보드 IMU `s_si.valid` 가 간헐이라 살아날 때 수요 1.5 배 | 09:52 첫 측정 imu 0.98 Hz 때 odom 26.2 Hz 정상 → imu 50 Hz 되자 odom 0 · 교대 점유 | 게이트로 수요 22.4 kB/s, 심지어 **2 kB/s 구간에서도 odom 0** | **기각**(§6.5 '대역 가설의 붕괴'). 교대 점유는 실재 관찰이지만 원인 설명은 아님 — 방아쇠 역할은 **미확인** |
| agent 가 받은 것을 버림 | `-v6` recv vs write | 1020 = 1020 | **기각** |
| `rcl_publish` 실패 · 버퍼 · MTU | TX 카운터 | 시도 25/s · 실패 0 · rc 0 | **기각** — 단 best-effort 는 실패를 rc 로 안 올린다(§9 교훈 3) → 아래 두 줄로 이어짐 |
| 보드 전송 계층이 바이트를 버림 | `wb`(busy 버림) · `wh`(HAL 오류) · `wf`(링 가득) · `hw`(링 최대 점유) | 0 · 0 · 0 · 1559/8192 | **기각** |
| 청크 전송 지연 → agent 프레임 타임아웃(`microros_transport.c` 머리 주석의 '왜 바꿨나') | 주석: 42 B 청크 × 18 회, 매번 세마포어 대기 → 프레임이 수십 ms 에 걸쳐 도착 · 'agent 수신은 그 7 % 뿐' | SUMMARY 에는 이 기전이 없다. 링 버퍼판(hw 1559)에서도 2 Mbps 손실이 이어졌고 보드율을 낮춰서야 해소 | **미확인** — 같은 커밋에 둘 다 들어가 효과를 나눌 수 없음(§6 모순 1) |
| UART → CH340 → USB 구간이 2 Mbps 에서 잃음 | 보드율만 460 800 으로 | 0~13 Hz → 25.0 Hz · 70 s 100 % | **지지**(증상 소거 확인). 기전('흐름제어 없는 CH340 FIFO 오버런', `base.launch.py` 주석)은 **추정** — dmesg 오류 0, 칩 안을 볼 수단 없음 |
| 용량 한계 vs 회귀 | 과거 로그 · git | 2 Mbps 는 05-28 부터 같고 08-26 · 08-27 에 ≈60 kB/s 안정 | **회귀**로 판정(§10) |
| 회귀 원인: ① 물리 배선 · 커넥터(WT-600 이관으로 바뀜) ② 09-07 모터 PWM 50 Hz → 20 kHz ③ CH340 모듈 · ch341(WCH 벤더 V1.9) 드라이버 | 좁히는 절차: ① dmesg(완료, 오류 없음) ② USB 포트 · 케이블 교체 뒤 2 Mbps ③ 모터 구동 vs 정지 손실률 ④ 09-06 펌웨어 A/B | ②~④ **미실행**. ②에 대한 반대 근거 하나: 장애는 모터 정지 중에도 났다(단순 EMI 로 다 설명 안 됨, §10) | **미확인**(이후 시기에도 재시험 기록 없음) |

## 4. 조치와 효과
- **보드율 2 000 000 → 460 800 bps**, 양쪽 일치 필수:
  - 보드: `Core/Src/usart.c` 의 CubeMX 생성값(`huart1.Init.BaudRate = 921600`)을 `USER CODE BEGIN USART1_Init 2` 안에서 덮어쓰고 `HAL_UART_Init` 을 한 번 더 부른다(CubeMX 재생성에도 살아남게). 주석에 '2 Mbps 는 CH340N datasheet 최대치' · '우회' · 후보 셋.
  - Jetson: `base.launch.py` 의 docker 인자 `-b 460800`.
  - 효과: odom 25.0 Hz 70 s 연속 100 % · 드롭 0, 전 토픽 규정 주기(§2 job118 줄).
- **발행 대역 예산**(`microros_task.c` 스핀 루프, 20 ms 주기): odom `now − last ≥ 33 ms` 게이트 → 20 ms 루프에서 2 주기마다 = **실효 25 Hz**(실측 25.005); imu · mag `≥ 200 ms` → 5 Hz; status 5 Hz · battery 1 Hz 는 원래대로. 근거: EKF 30 Hz, 보드 IMU 는 EKF 미사용(CLAUDE.md §4). IMU 를 지우지 않고 5 Hz 로 둔 이유: 자이로 원인 규명 시 관측 가능성(기각한 대안 = 삭제).
  - 수지(SUMMARY): 18.3 + 1.7 + 0.7 + 1.4 + 0.1 = '22.4 kB/s', 460 800(8N1 → 46 080 B/s)의 49 %. ⚠ 적힌 항의 합은 **22.2**, 크기 × 주기로 다시 곱하면 25×732 + 5×330 + 5×130 + 5×280 + 1×100 = **22.1 kB/s**(48 %). 결론에 영향 없는 산술 차이.
- **전송 계층 재작성**(`microros_transport.c`): 쓰기를 8 kB TX 링에 복사하고 즉시 반환, DMA 완료 인터럽트가 남은 구간을 이어 건다(프레임 사이 공백 제거, 호출자 버퍼를 DMA 소스로 쓰던 위험 제거). 링이 50 ms 넘게 가득하면 그 바이트를 버리고 `g_tx_full` 에 센다. 효과는 보드율 변경과 분리 측정 안 됨(§6 모순 1).
- **진단 카운터 유지**: `/rover/status` 의 `values[2]` key `TX` = `ot=… wc=… wb=… wh=… wf=… hw=…`(누적). UART5 콘솔이 배선돼 있지 않아 printf 대신 도달이 확인된 토픽에 실었다(주석).
- 한계: 우회일 뿐. 2 Mbps 설계값의 여유(200 kB/s)는 지금 못 쓴다. 회귀 원인이 링크에 남아 있다면 460 800 에서도 언젠가 드러날 수 있다(**추정**). 소급 영향 — 09-08 의 미해결 이상(1.40 m 목표에 5.79 m 경로 · SLAM map yaw 점프 · 여유 있는데 상자에 붙는 경로)이 odom 간헐 소실의 약한 증상이었을 가능성을 §10 이 인정했고 재검증을 남겼다.

## 5. 내 실수
### 5.1 'USB FS 32 B 엔드포인트가 상한' — 맞아떨어지는 숫자 하나로 인과를 단정
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 교대 점유(§5)의 '용량' 이 어디서 오는지 찾기 — `job106_baud.sh` · `job107_port.sh` 로 장치 · USB 정보 수집 |
| 본 것 | CH340 이 USB Full-Speed(12 Mbps), 벌크 엔드포인트 `wMaxPacketSize = 0x20`(32 B). 관측 최대 odom 단독 50.9 Hz × 720 B = 36.6 kB/s |
| 처음 추론 | 'FS 벌크는 1 ms 프레임 단위, 패킷 32 B → 실효 32~40 kB/s' 가 36.6 과 맞음 → **병목은 UART 가 아니라 USB**, 2 Mbps 는 선로 속도일 뿐 200 kB/s 여유는 못 씀. 29 Hz 운용도 '상한의 95 %' 였다고 적음. 커밋 `7cc12d6` · CLAUDE.md 까지 반영 |
| 의심한 이유 | ① 발행 게이트로 수요를 22.4 kB/s(상한의 ~60 %)까지 내렸는데 odom 이 계속 0, 수요 2 kB/s 구간도 0(§6.5) ② 사용자 질문 "어제까지 잘 되던 데이터 크기가 왜 오늘 이렇게 됐는가"(§10) |
| 판별 | `git log -S"BaudRate = 2000000"` → 05-28 부터 불변. 08-27 `job4x_sensors_slam.txt` `/wheel_odom` 49.995 Hz + imu 50 Hz(≈60 kB/s) 안정 |
| 결론 | 상한 결론 폐기. 36.6 kB/s 는 그 시점의 우연한 값. '1 ms 프레임당 32 B' 가정도 검증 안 한 것이었다 |
| 다음에 알아보는 법 | **새 이론은 세운 즉시 과거 측정치와 대조한다**(§9 교훈 1 — '5 분이면 반증됐다'). '어제까지 됐다' 가 있으면 한계보다 **회귀**부터 가른다(교훈 2). 상한을 주장할 땐 그 상한을 넘는 과거 관측이 하나라도 있는지 먼저 찾는다 |
| 데이터 | SUMMARY §6 · §10 · §9, 커밋 `7cc12d6` · `f1a76d86` 메시지, [`2026-08-27/outputs/job4x_sensors_slam.txt`](../debug_log/2026-08-27/outputs/job4x_sensors_slam.txt), 도구 `job106_baud.sh` · `job107_port.sh`. 09-09 출력 원문은 **원천 소실** |

### 5.2 `pkill -f "a\|b"` — 정리가 조용히 실패해 중복 스택을 쌓음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 복구 · 가설 시험 전에 Nav2 · SLAM · 센서 노드를 한 줄로 정리(`job97_recover.sh` · `job100_cmdvel.sh` · `job101_load.sh`) |
| 본 것 | (job102 의 '정리 전 프로세스 수') `ekf_node` 2 개 등 중복, load **16.8**, Jetson SSH 'No route to host' 3 회 |
| 처음 추론 | 그 전까지는 정리가 됐다고 믿고 '부하 단계별 측정' 등을 해석 |
| 의심한 이유 | 프로세스 수가 줄지 않고 load 가 폭증 |
| 판별 | `pkill` 은 POSIX **ERE** 로 패턴을 해석한다 — ERE 에서 '백슬래시 + 세로줄' 은 교대(or)가 아니라 **세로줄 글자 그 자체**. 이름에 세로줄이 든 프로세스는 없으니 아무것도 안 죽고, 스크립트는 그 위에 launch 를 또 띄웠다 |
| 결론 | 해당 구간 측정 폐기. `job102_clean.sh` 부터 `for p in "a" "b"; do pkill -9 -f "$p"; done` 형태 |
| 다음에 알아보는 법 | 정리 직후 **반드시 세어서 찍는다**(job102 부터 '정리 후 프로세스 수'). grep 의 BRE(백슬래시 + 세로줄 = or)와 pgrep/pkill 의 ERE(세로줄만 = or)를 섞지 않는다. job97 의 '잔여 프로세스' 줄은 `pgrep -fc` 에 세로줄만 쓴 패턴이라 **세는 쪽은 맞고 죽이는 쪽만 틀렸다** — 세어 본 값을 읽었으면 그 자리에서 잡혔을 결함 |
| 데이터 | SUMMARY §4 '내가 만든 오염' · §9 교훈 5, 도구 `job97_recover.sh` · `job100_cmdvel.sh` · `job101_load.sh` · `job102_clean.sh`. 출력 원문 없음 |

### 5.3 `job106` 이 라이다 포트의 termios 를 읽음 — 기록되지 않은 도구 결함
| 칸 | 내용 |
|---|---|
| 하려 한 것 | agent 가 연 시리얼의 실제 보드율(termios) 확인 |
| 본 것 | 스크립트가 `stty -F /dev/ttyUSB0` · `/sys/class/tty/ttyUSB0/device/driver` · `udevadm info -n /dev/ttyUSB0` 를 본다 |
| 처음 추론 | (SUMMARY 에 이 출력의 해석은 없음) |
| 의심한 이유 | 같은 날 job107 결과 `/dev/rover → ttyCH341USB0`, `/dev/rplidar → ttyUSB0`(cp210x). 즉 job106 의 장치 줄은 **라이다** 것 |
| 판별 | job107 이 `/dev/ttyUSB*` 전부 · `/dev/rover` · by-id 를 나열하고 1a86 장치를 `/sys` 에서 직접 찾도록 다시 짬 |
| 결론 | job106 의 termios · 드라이버 줄은 이 문제와 무관한 장치 값. 결론에 쓰이지 않아 피해는 없었다(**추정** — 원문 없음) |
| 다음에 알아보는 법 | 장치는 별칭(`/dev/rover`)이나 `readlink -f /dev/rover` 로만 지정. 커널 이름을 하드코딩하지 않는다(08-26 사용자 규칙과 같은 원리) |
| 데이터 | `jobs/job106_baud.sh` · `jobs/job107_port.sh`, SUMMARY §6 장치 표 |

(같은 날의 다른 실수 — DDS 공유메모리 · CPU · 배터리 오판 — 은 [DDS 공유메모리 사고](dds-shm-incident.md) · [CPU 부족 정지](cpu-load-stalls.md).)

## 6. 기록 사이 모순 (원문 대조)
1. **무엇이 고쳤나 — 보드율인가 링 버퍼인가.** `microros_transport.c` 머리 주석은 '이전 구현(청크마다 세마포어 대기) 때문에 미완성 프레임이 버려졌다 · 실측 증거: 보드 25 회/s 성공인데 agent 수신 7 %' 라고 원인을 단정한다. SUMMARY §6.5 는 이 기전을 쓰지 않고 '링 최대 점유 1559/8192' 를 든 뒤(= 링 버퍼판이 이미 돌고 있었음) 보드율을 낮춰 해소했다고 쓴다. 커밋 `f1a76d86` 은 둘을 함께 넣었다. → 링 버퍼만으로는 안 고쳐졌다는 것이 SUMMARY 서술에서 읽히지만, 옛 전송 + 460 800 조합은 시험하지 않아 **기여 분리 불가**. 주석의 'agent 수신 7 %' 는 SUMMARY · outputs 어디에도 없는 수치(원천 소실).
2. **'FIFO 오버런'.** `base.launch.py` 주석은 '흐름제어 없는 CH340 이 2 Mbps 유입을 USB 로 못 빼내 FIFO 오버런' 으로 적는다. SUMMARY 는 '커널이 관측할 수 없는 CH340 칩 내부 유실과 일관' 까지만. 오버런은 측정이 아니라 **추정**이다. 또 '용량 회귀' 정정(§10) 뒤에도 이 주석은 '못 빼내' 라는 용량식 표현을 남기고 있다.
3. **§5 첫 표의 출처.** SUMMARY 는 '(job104, job105)' 라 쓰지만 첫 표의 칸(odom · imu · status · battery 4 개)은 `job103_obs.sh` 의 출력 형식과 같다(job104 는 conditioned 칸이 더 있다). 원문 없어 **미확인**.
4. **메시지 크기 720 B vs 732 B.** SUMMARY 수지표 · 커밋 `7cc12d6` 은 ~720 B(CDR 계산), §0 · `usart.c` · `microros_task.c` 주석 · CLAUDE.md 는 732 B. 732 는 `-v6` 프레임 길이 분포(job114)에서 온 값으로 보이나(**추정**) 기록은 없다.
5. **'30 Hz 게이트' 이름.** 코드 안 주석 `/* /wheel_odom 30Hz 게이트 */` 와 커밋 `7cc12d6`(30 Hz · 25.4 kB/s)는 의도값이고, 33 ms 게이트가 20 ms 루프에서 실제로는 40 ms 마다 걸려 25 Hz 가 된다(같은 파일 위쪽 주석 · 실측 25.005). 숫자 두 개가 한 파일에 공존.
6. **수지 합계 22.4 vs 22.1~22.2**(위 §4).

## 7. 남은 것
- 회귀 원인 판별(§3 마지막 줄의 ②~④). 지금 운용엔 영향 없으나 2 Mbps 의 여유를 다시 쓰려면 필요. 시험 설계는 09-09 §10 '좁히는 절차' 그대로 쓸 수 있다: (a) 같은 펌웨어 · 2 Mbps 로 USB 포트 · 케이블만 바꿔 손실률 (b) 모터 구동 · 정지 각 60 s 손실률 (c) 09-06 펌웨어(PWM 50 Hz 판) 플래시 A/B.
- 링 버퍼 전송의 기여(옛 전송 + 460 800 조합) — 분리 측정 없음.
- 09-08 의 미해결 이상들 재검증(§10 '소급 영향') — 이후 시기 카드에서 확인.
- 펌웨어 세션 재수립 로직 부재는 별도 — [보드 연결 카드](board-link-microros-session.md).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job92 | 첫 회피 주행 — 8.5 m 발산 | `jobs/job92_avoid.py`, CSV 원천 소실 |
| job93 · 94 · 95 · 96 · 98 | 발산 위치 · 시계 · odom QoS · 보드 토픽 생존 · agent 엔티티 | `jobs/` 같은 이름 |
| job97 · 100 · 101 | 복구 · `/cmd_vel` · 부하 단계 — 정리 결함(ERE 패턴, §5.2) 포함 | 같은 곳 |
| job102 · 103 · 104 · 105 | 정리 고침 · 깨끗한 60 s · 고아 제거 60 s · 90 s + io | 같은 곳 |
| job106 · 107 | agent 인자 · USB 엔드포인트(틀린 결론의 재료) | 같은 곳 |
| job108 · 109 | rchar 버킷 · 컨테이너 안팎 Hz | 같은 곳 |
| job110 · 111 · 114 · 115 | agent `-v6` 기동 · 집계 · 길이 분포 · 정상 복귀 | 같은 곳 |
| job112 · 113 | 펌웨어 TX 카운터 차분 · 전송 계층 카운터 | 같은 곳 |
| job116 · 117 · 118 | 상태 확인 · 460800 배포 · 전 토픽 검증 | 같은 곳 |
| 커밋 `7cc12d6` → `f1a76d86` | 틀린 결론 + 게이트 → 우회 + 링 버퍼 + 정정 | git |

## 9. 도구 해설
**공통**: 전부 **Jetson** 에서 실행. PC(WSL)의 `run_j.sh <파일> [인자]` 가 스크래치패드의 스크립트를 `scp` 로 `/tmp/` 에 올리고 `ssh … "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; bash|python3 /tmp/<파일> 2>&1 | tail -60"`(300 s 제한)로 부른다 — 화면에는 **마지막 60 줄만** 남는다. 비밀번호는 `<PW>`, 주소는 그날 `192.168.0.101`. 출력은 대화에만 있었고 `outputs/` 에 저장되지 않았다(**원천 소실**). 토픽 Hz 는 대부분 직접 짠 파이썬 구독자(`qos_profile_sensor_data` = BEST_EFFORT, 깊이 5)로 콜백 수를 세서 `건수 / 경과 초` 로 낸다 — `ros2 topic hz` 보다 가볍고 5 초 버킷으로 시간 변화를 본다. 기대치 '29 Hz'(odom · imu)는 게이트 전 펌웨어의 운용값(05-28 커밋 '31Hz' 계열)이다.

**도구 계보**
- 러너: `run_j.sh`(범용 업로드 + 실행) · `run_xfer_all.sh`(재부팅 뒤 `/tmp` 일괄 재전송 — 그날 20 개 job, 3 회 재시도, `py_compile` 검사). 이후 `run_jn.sh`(09-29, 실행 투명성) · `Docs/tools/` 로 대체.
- 링크 관측: job95(10 s 한 토픽) → job99(30 s 세 토픽 + 호스트 io) → job100 · 101(같은 측정 함수, 정리 결함) → job102(5 초 버킷 60 s, 정리 고침) → job103(+battery, 아무것도 안 죽임) → job104(+conditioned) → job105(90 s + 컨테이너 안 `/proc/<pid>/io`) → job108(pid 를 실행 파일로 고름 + '기대 B/s' 칸) → job111(`-v6` 로그와 동시)
- 계층 계측: job98(agent 엔티티) → job110 · 111 · 114(`-v6`) → job112(펌웨어 rcl 카운터) → job113(전송 계층 카운터, 옛 필드)
- 장치: job96(ttyUSB 만 봄) → job106(ttyUSB0 = 라이다) → job107(전체 · 1a86 직접)
- 복귀 · 배포: job115 → job116 → job117 → job118

### 9.1 `job92_avoid.py` — 회피 주행(발산이 처음 보인 도구)
- 부른 형태: `python3 job92_avoid.py [D=1.80] [timeout=90] [csv이름=job92]`.
- 왜: 09-08 의 inflation 0.40 / padding 0.02 를 '계획이 아니라 실제로 얼마나 붙었나' 로 검증.
- 하는 일: TF 버퍼로 `map→base_link`, `/cmd_vel` · `/plan` · `/camera/camera/depth/color/points` 구독. 깊이점을 `base_link` 로 변환해 z 0.03~0.35 m · x −0.1~1.5 · |y| < 0.9 만 골라, 차체 외곽(반길이 0.25, 반폭 0.165 + 패딩 0.02 = 0.185)에서 최근접 거리 = '최소 여유'. NavigateToPose 로 정면 D m 목표를 보내고 1 초마다 t · 전진 · 횡변위 · 최소 여유 · 상자 거리 · v · ω 출력, CSV `/tmp/<이름>.csv`.
- 출력: §1 의 표(SUMMARY 인용). CSV 원천 소실.
- 쓰인 곳: §3 증상. 이 날 오후 '최소 여유' 지표 자체가 틀렸음이 드러나 `job125_avoid3.py` 로 대체(§8.6 — 상자가 화각을 벗어나면 다른 물체를 잼).
- 지금: 못 씀(지표 결함). 후속은 `job125_avoid3.py` → 이후 러너들.

### 9.2 `job93_jump.sh` — 점프 위치 특정
- 하는 일: `tf2_echo` 로 map→odom · odom→base_link · map→base_link 의 Translation · RPY 각 5 s, `/odometry/filtered` · `/wheel_odom` x · y 1 회, `/tmp/slam.log`(warn|error|loop|match|jump|reset|serial 마지막 15 줄), `/tmp/nav2.log`(abort|fail|…|stuck 12 줄), `/rover/stuck`, `/map` info.
- 판정: 점프가 어느 변환에 있나 — map→odom 이면 SLAM, odom→base 면 EKF.
- 출력: §1 의 두 줄. 원문 없음. 재사용 가능(형태는 이후 `chk_` 계열).

### 9.3 `job94_clock.sh` — 시계 스텝
- 하는 일: `timedatectl`, `journalctl -b` 에서 time sync · timesyncd · chronyd · clock step 줄, `/wheel_odom` · `/odometry/filtered` hz, 10 s 구독으로 수신 수 · x/y 변화 · |v|,|ω| 최대 · 헤더 stamp 경과 vs 실경과 · 'host 대비 오프셋'(마지막 stamp − 마지막 수신 시각).
- 출력: NTP 09:43:18 · 오프셋 −0.010 s(§3 가설 1). 원문 없음.
- 결함: 오프셋은 같은 기계 시계 기준이라 보드 time sync(60 s resync)가 튀는 순간을 10 s 창 하나로는 못 잡을 수 있다.

### 9.4 `job95_wodom.sh` · `job96_session.sh` · `job98_entities.sh` — 링크 상태 보기
- job95: `ros2 topic info /wheel_odom --verbose`(Reliability · Durability), BEST_EFFORT 10 s 수신(정지 상태라 |v|,|ω| 가 0 이어야), ekf.yaml 의 odom0 · imu0 줄, sensors.log 의 ekf/conditioner 경고.
- job96: `/wheel_odom` · `/battery` · `/rover/status` · `/imu/data_raw` · `/imu/mag` hz 각 8 s, `rover_jupiter` 노드, agent 컨테이너, `docker logs` 에서 delete|session|timeout|error|heartbeat|disconnect 25 줄, `ls /dev/ttyUSB*`(⚠ 보드는 `ttyCH341USB0` 라 안 나옴).
- job98: agent 로그에서 `establish_session` · `create_client`(client_key 별) → 최근 client_key 의 `create_datawriter` 수 · 목록 → 오류 줄 → `ros2 node info /rover_jupiter` 발행 목록 → 토픽별 퍼블리셔 수 → dmesg.
- 왜: '세션이 반쪽인가(일부 엔티티만 생성)' 를 보려고. 결과는 SUMMARY 에 없음(원문 없음).
- 재사용: 개념만 — agent 로그는 launch 판 agent 가 `-v4` 이하라 `create_datawriter` 줄이 안 나올 수 있다([보드 카드 §8.7](board-link-microros-session.md) 와 같은 한계).

### 9.5 `job97_recover.sh` — 보드 RESET 뒤 복구(정리 결함판)
- 주석: 'agent 컨테이너와 base.launch 는 건드리지 않는다(건드리면 또 RESET 이 필요해짐)'.
- 하는 일: ① `ros2 topic hz` 10 s 로 odom · imu · status · battery 주기 → `float(odom) > 20 and float(imu) > 20` 아니면 '세션이 반쪽' 출력 후 exit 2(게이트) ② `pkill -f "navigation_launch\|controller_server\|…"` 세 줄 ③ sensors(24 s, 자이로 캘리브 동안 정지) → slam(12 s) → nav2(25 s) ④ 토픽 · TF · lifecycle · nav2 오류 · 배터리.
- 결함: ②가 ERE 리터럴이라 아무것도 안 죽임(§5.2). 게이트 기준 'imu > 20' 은 보드 IMU 가 간헐(`s_si.valid`)이라 세션이 정상이어도 걸릴 수 있다.
- 후속: job102 의 for-루프 정리 → job123 · job154(SIGTERM판).

### 9.6 `job99_bytes.sh` — UART 바이트 수(첫 시도)
- 하는 일: 호스트 `pgrep -f micro_ros_agent | head -1` 의 `/proc/<pid>/io` rchar · wchar 를 10 s 차분 → 'UART 수신 B/s'; 30 s 동안 odom · imu · status 수신 Hz, 마지막 status 의 level · 값.
- 기대치 주석: odom 720 B × 29 + imu 330 B × 29 ≈ 30 kB/s, 작은 것만이면 ≈ 2 kB/s.
- 결함: 컨테이너 프로세스는 root 소유라 jetson 사용자가 `/proc/<pid>/io` 를 못 읽었을 것(**추정** — job105 · 106 이 docker exec · `docker inspect .State.Pid` 로 바꾼 것이 그 흔적). rchar 는 '읽기 시스템 호출로 받은 바이트' 라 시리얼 외 다른 fd 읽기도 섞인다.

### 9.7 `job100_cmdvel.sh` · `job101_load.sh` — `/cmd_vel` · CPU 가설(정리 결함판)
- job100: `/cmd_vel` 발행 주체 · 주기 → Nav2 노드 목록 → Nav2 종료(`\|` 결함) → 종료 후 `/cmd_vel` → 20 s 보드 토픽 Hz. 주석의 가설 근거: '세션 1: Nav2 기동(= cmd_vel 시작) 직후 odom 사망'.
- job101: `/tmp/_meas.py`(15 s 동안 세 토픽 수신 Hz)를 만들어 두고, 단계 (1) slam · sensors 종료(`\|` 결함) → (2) sensors(26 s) → (3) slam(14 s) → (4) nav2(28 s) 마다 load · idle(`top -bn2 -d1` 의 `%Cpu` 줄 8 번째 칸) + 측정. 끝에 상위 CPU 8 개 · `nproc` · `nvpmodel -q`.
- 출력: 가설 3 · 4 의 수치(§3). `nvpmodel -q` 결과는 기록 없음(전력 모드는 09-17 에 처음 기록 — 15 W).
- 결함: 정리 실패로 단계 이름이 실제 상태와 다름 + 단계마다 launch 를 또 띄워 중복을 키움(§5.2 의 load 16.8 원인 중 하나).

### 9.8 `job102_clean.sh` · `job103_obs.sh` · `job104_obs2.sh` — 깨끗한 상태 관측 ★
- job102: 13 개 이름별 `pgrep -fc` 로 '정리 전' 개수 → 19 개 패턴을 하나씩 `pkill -9 -f` → 6 s → '정리 후' (잔존 표시) · agent · 노드 · load → **base 만 남긴 상태**에서 60 s(5 초 버킷 12 개) odom · imu · status Hz.
- job103: 아무것도 안 죽이고 중복 점검(8 개 이름 개수 · load · `rover_jupiter`) → 60 s 버킷 4 토픽(+battery, 기대 29/29/5/1) → conditioned · filtered hz · odom→base.
- job104: 고아 Nav2 10 패턴 `pkill -9` → 12 개 이름 개수 → 60 s 버킷 5 토픽(+`/wheel_odom/conditioned`) → agent 로그 6 줄.
- 판정 읽는 법: 작은 토픽(status 5 · battery 1)이 정확한데 큰 토픽만 0 → 링크 '용량 경쟁'(그때 해석). status 마저 0 이 되는 버킷(25–40 s)은 '둘이 동시에 밀면 작은 것도 밀려남'.
- 결함: `pkill -9` — 같은 날 저녁 SHM 사고의 원인 계열([DDS 카드](dds-shm-incident.md)). `pgrep -fc "$p" || echo 0` 은 0 개일 때 '0' 과 '0' 두 줄을 내지만 여기선 `[ "$c" != "0" ]` 비교라 표시만 이상하고 판정은 맞다(**추정** — 다중 줄은 같은 날 job179 에서 산술 오류로 터짐, [CPU 카드](cpu-load-stalls.md)).
- 지금: 5 초 버킷 관측 방식은 유효. 고정 도구는 이후 `Docs/tools/chk_*` 계열.

### 9.9 `job105_bytes.sh` · `job108_rchar.sh` — 바이트 유입 vs 토픽 수신 ★(의도)
- 질문(주석): 붕괴 후에도 바이트가 계속 들어오면 → 보드는 보내는데 agent 가 못 살림 / 바이트도 줄면 → 보드가 발행 포기.
- job105: `docker exec microros_agent` 로 컨테이너 안 `/proc/*/cmdline` 에 `micro_ros_agent` 가 든 첫 pid → 5 초마다 그 `/proc/<pid>/io` rchar · wchar 차분 → 18 버킷(90 s) odom · imu · status · bat Hz 와 나란히.
- job108: pid 를 `readlink /proc/$p/exe` 가 `*micro_ros_agent` 인 것으로 고름(job105 의 cmdline 방식은 entrypoint 셸을 고를 수 있다는 주석), fd 중 tty 확인, 16 버킷(80 s), '기대(메시지합) B/s' = odom × 720 + imu × 330 + status × 280 + bat × 100 칸 추가.
- 출력: job105 의 Hz 칸은 §5 교대 점유 표의 출처(90 s). **B/s 칸 결과는 SUMMARY 어디에도 없다** — 측정됐는지조차 **미확인**. 판정은 뒤의 `-v6` · TX 카운터가 대신했다.
- 지금: 같은 질문은 09-11 job240 의 '시리얼 3 초 수신 바이트'(직접 `cat /dev/rover`)로 단순화돼 계승([보드 카드](board-link-microros-session.md)).

### 9.10 `job106_baud.sh` · `job107_port.sh` — 장치 · USB(틀린 결론의 재료)
- job106: `docker inspect` 의 Cmd · Entrypoint, `stty -F /dev/ttyUSB0`, `docker exec … cat /proc/1/io`, `docker top`, `lsusb`, ttyUSB0 드라이버, `udevadm info -a -n /dev/ttyUSB0` 의 MaxPacketSize · speed, `docker inspect .State.Pid` 로 호스트 pid 의 io 10 s.
- job107: `/dev/ttyUSB*` · `/dev/ttyACM*` · `/dev/rover` · `/dev/rplidar`, `/dev/serial/by-id`, ttyUSB 마다 드라이버 · vid:pid · `fuser` 보유 프로세스, `/sys/bus/usb/devices/*` 중 idVendor 1a86 의 speed · 각 `ep_*` 의 wMaxPacketSize · type · interval, 컨테이너 안 agent 의 tty fd.
- 출력: §2 의 장치 블록(SUMMARY §6 인용). 원문 없음.
- 결함: job106 의 ttyUSB0 = 라이다(§5.3). job107 의 엔드포인트 크기는 사실이지만 '그래서 32~40 kB/s' 는 도구가 아니라 해석의 결함(§5.1).
- 지금: job107 은 장치 점검으로 재사용 가능.

### 9.11 `job109_inside.sh` — 컨테이너 안 vs 호스트
- 하는 일: 컨테이너 NetworkMode · IpcMode · PidMode · 마운트 · ROS/RMW/FASTRTPS/DDS 환경변수(여기서 `MICROROS_DISABLE_SHM=1` 이 보였을 것 — 같은 날 저녁 SHM 사고에서 '보드 토픽만 멀쩡' 의 근거로 다시 쓰임, **추정**), 호스트 · 컨테이너 `/dev/shm` → 컨테이너 안 `ros2 topic hz` 3 토픽 각 14 s → 같은 3 토픽을 호스트에서.
- 판정(주석): 안 정상 · 밖 0 → 컨테이너↔호스트 DDS 문제 / 안도 0 → 보드 쪽.
- 출력: SUMMARY 에 결과 없음. 컨테이너 이미지에 `ros2` CLI 가 있는지도 기록 없음(**미확인**).

### 9.12 `job110_v6.sh` → `job111_v6read.sh` · `job114_lenhist.sh` → `job115_normalagent.sh` — agent 상세 로그 ★
- job110: agent 컨테이너 삭제 · `base.launch` 종료(→ robot_state_publisher 도 죽으므로 `description.launch.py` 를 따로 기동) → `docker run --rm --name microros_agent --net host --device <실장치>:/dev/rover … -b 2000000 -v6 > /tmp/agent_v6.log` → '보드 RESET 버튼을 눌러 주세요'(agent 를 새로 띄웠으니 세션 재수립 필요 — [보드 카드](board-link-microros-session.md) 규칙).
- job111: 로그 줄 수 기록 → 백그라운드로 60 s(12 버킷) 4 토픽 Hz → ANSI 색 코드 제거 → 로그 함수명(`| name |`)별 건수 상위 15 · datawriter_id 별 전송 건수 · 오류 흔적(error|wrong|invalid|discard|drop|crc|overflow…) · 세션/스트림/heartbeat/acknack/fragment 줄 · 원시 10 줄.
- job114: 전체 로그에서 `recv_message`(보드 → agent) 의 `len:` 분포 상위 20 · `DataWriter.cpp`(agent → DDS) 길이 분포 · 최대 수신 길이 · `send_message`(agent → 보드) 분포 · 함수명.
- job115: `-v6` 로그 크기 → 컨테이너 · `base.launch` · RSP 정리 → **로그 삭제**(`rm -f /tmp/agent_v6.log`) → `base.launch` 정상 기동 → '이제 보드 리셋 필요'.
- 출력: `recv_message` 1020 = DDS write 1020(§6.5). 길이 분포 결과(odom 프레임이 들어왔는지)는 SUMMARY 에 없다 — 732 B 의 출처일 가능성(**추정**, §6 모순 4). `-v6` 원본 로그는 job115 가 지움 → **원천 소실**.
- 쓰인 곳: 'agent 는 안 버린다'. 한계: agent 가 프레임을 '받았다' 고 로그하기 전에(프레이밍 단계에서) 버린 것은 이 집계에 안 잡힌다 — 그래서 transport 주석의 '미완성 프레임 버림' 가설과 모순되지 않는다(§3).
- 지금: `-v6` 집계 형태는 링크 진단에 재사용 가능(로그를 지우기 전에 `outputs/` 로 옮길 것).

### 9.13 `job112_txdiag.sh` · `job113_txlayer.sh` — 펌웨어 카운터 차분 ★
- 전제: 펌웨어가 `/rover/status` 의 KeyValue `TX` 에 누적 카운터를 싣는다(UART5 콘솔 미배선이라 printf 대신).
- job112: `TX` 값을 정규식 `(\w+)=(-?\d+)` 로 파싱, 15 s 안에 첫 값이 없으면 '펌웨어 반영 확인 필요' 로 중단 → 14 버킷(70 s) 동안 c(루프 사이클) · ot/of(odom 시도/실패) · it/if(imu 시도/실패)의 초당 증가량과 실제 수신 Hz, 마지막 rc(`orc`). 판정 문구: 시도 > 0 & 실패 ≈ 시도 → rcl 거부 / 시도 > 0 & 실패 ≈ 0 → 전송 계층 · 링크 / 시도 ≈ 0 → 게이트 · 루프.
- job113: 같은 방식으로 ot · wc(write 호출) · wb(gState busy 로 버림) · wh(HAL 오류) · wt(세마포어 타임아웃)의 초당 증가 + 최대 len `wl`.
- 출력: 시도 25/s · 실패 0 · rc 0(§6.5). 2 Mbps 0~13 Hz 와 460 800 '70 s 연속 100 %' 도 14 버킷 = 70 s 라 이 둘 중 하나의 출력으로 **추정**.
- ⚠ 판 불일치: 저장된 job113 은 옛 전송(세마포어 대기)판 필드 `wt` · `wl` 을 읽는다(전송 주석의 '실측 wl=42' 가 이 도구 값). SUMMARY 의 '`wb/wh/wf` 0 · 링 최대 1559/8192' 는 링 버퍼판 필드(`wf` = 링 가득 버린 바이트, `hw` = 링 최대 점유 — 지금 펌웨어의 `TX` 형식 `ot= wc= wb= wh= wf= hw=`)라 **저장 안 된 후속판**으로 읽은 값이다. 지금 펌웨어에는 `of` · `it` · `if` 도 `TX` 문자열에 없다 → job112 · 113 을 지금 돌리면 일부 칸이 0 으로 나온다.
- 지금: 지금 펌웨어 필드에 맞춰 고치면 재사용 가능. 이 '도달이 확인된 토픽에 계측을 싣는다' 가 이 문제를 푼 핵심 수단.

### 9.14 `job116_chk.sh` · `job117_baud.sh` · `job118_verify.sh` — 배포와 검증
- job116: 노드 목록 · 토픽 수 · 보드 4 토픽 hz(각 8 s) · agent 의 마지막 `establish_session` 2 줄 · ROS 프로세스 수.
- job117: PC 에서 올린 `/tmp/base.launch.py` 를 src · install 둘 다에 복사(빌드 없이 — 설치본이 심볼릭 링크가 아닐 때 필요) → `'-b', '<숫자>'` 확인 → agent · base · RSP 정리 → base 기동 → agent Cmd 확인. 이어서 보드는 460800 펌웨어 플래시(리셋 포함)가 필요 — 순서는 agent 먼저(09-11 §5.7 규칙과 같은 방향).
- job118: 10 개 토픽 hz(보드 5 · conditioned · filtered · scan · map · 점군) · map→odom · odom→base · 배터리 · `dmesg | grep ch341|ch34x|usb 1-2|overrun|frame error|parity` · `1-2.1` speed/product · `/sys/kernel/debug/usb/devices`(보통 접근 불가).
- 출력: §2 의 전 토픽 줄 · dmesg 무오류. 원문 없음.
- 지금: job118 의 '전 토픽 한 번에' 는 이후 `chk_prep.py` · `chk_drive_gate.py`(10-27)로 대체.

### 9.15 `run_j.sh` · `run_xfer_all.sh` — 실행 · 재전송(PC, WSL)
- `run_j.sh <파일> [인자…]`: 스크래치패드(그날 세션 `82ce61d4…`, 09-28 자동 소실)의 파일을 `/tmp` 로 올려 `.py` 면 python3, 아니면 bash 로 실행. `tail -60` 이라 긴 출력의 앞부분은 잘린다 — 60 s · 90 s 버킷 관측(12~18 줄 + 머리)은 들어오지만 job111 처럼 여러 구역을 찍는 도구는 앞 구역이 잘렸을 수 있다(**추정**).
- `run_xfer_all.sh`: 재부팅으로 `/tmp` 가 지워졌을 때 20 개 job 을 한 번에 올리고 `chmod` · `py_compile`.
- 지금: 못 씀(스크래치패드 경로 소실). 같은 역할 = `run_jn.sh` → `Docs/tools/`.

## 10. 용어
- **XRCE-DDS · micro-ROS agent**: MCU 같은 작은 장치용 DDS 변형(eProsima Micro XRCE-DDS). 보드(클라이언트)는 시리얼로 agent 에 메시지를 보내고, Jetson 의 agent 가 그것을 일반 DDS(ROS 2 토픽)로 다시 쓴다. 보드 쪽 `rcl_publish` 는 XRCE 스트림에 넣는 데까지만 책임진다.
- **best-effort 스트림**: 재전송 없는 스트림. 바이트가 링크에서 사라져도 보드 `rcl_publish` 는 rc 0(성공)을 돌려준다 — 이 문제에서 '시도 25/s · 실패 0 인데 수신 0' 이 가능했던 이유.
- **보드율(baud) · 8N1**: UART 선로 속도(초당 비트). 8N1 은 한 바이트에 시작 · 정지 비트 포함 10 비트 → 460 800 bps = 46 080 B/s, 2 000 000 bps = 200 000 B/s.
- **CH340(N) · ch341 드라이버**: USB↔UART 변환 칩(1a86:7523, USB Full-Speed 12 Mbps). 이 Jetson 은 WCH 벤더 드라이버 ch341(V1.9)로 `/dev/ttyCH341USB0` 이 된다(커널 기본 드라이버면 `ttyUSB*`). 하드웨어 흐름제어(RTS/CTS)를 안 쓰므로(`HwFlowCtl = NONE`) 칩 버퍼가 차도 보드를 멈출 신호가 없다.
- **USB Full-Speed · 벌크 엔드포인트 · wMaxPacketSize**: FS 는 12 Mbps, 1 ms 프레임 단위로 시간을 나눈다. 벌크는 대역이 남을 때 쓰는 전송 방식, wMaxPacketSize 는 패킷 하나의 최대 바이트(CH340 은 32 B). 패킷 크기는 처리량의 상한을 바로 정하지 않는다(§5.1).
- **CDR 직렬화 · Odometry 크기**: ROS 메시지를 바이트로 만드는 규칙. `nav_msgs/Odometry` 는 pose 7 double + 공분산 36 double + twist 6 double + 공분산 36 double = 680 B + 헤더 · 프레임 이름 ≈ 720 B. 공분산 576 B(80 %)는 우리가 상수로만 채우지만 타입상 생략 불가.
- **교대 점유**: 두 큰 토픽(odom · 보드 IMU)이 번갈아 거의 50 Hz 를 받고 다른 하나는 0 이 되는 패턴(§5). 작은 토픽은 그동안 정확.
- **링 버퍼 · DMA · high-water**: 원형 버퍼에 쓰고 DMA(CPU 없이 메모리 → UART 전송) 완료 인터럽트가 다음 구간을 이어 거는 방식. high-water = 관측된 최대 점유.
- **`-v6`(agent 상세도)**: agent 로그 수준. 6 은 메시지 단위(`recv_message` · `write`) 로그까지 찍는다. 운용 판은 상세도 옵션 없음.
- **ERE vs BRE**: 정규식 방언. `grep`(BRE)에서 `\|` 는 or, `pgrep`/`pkill`(ERE)에서 `\|` 는 글자 `|`(or 는 그냥 `|`).
- **회귀(regression)**: 전에 되던 것이 어떤 변화 뒤에 안 되는 것. '원래 한계' 와 달리 '그 사이에 바뀐 것' 을 찾는 문제가 된다.
