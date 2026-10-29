# 보드 연결 · micro-ROS 세션 (CH340 → udev → Docker agent → 세션 수립 · 재수립)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(운영 절차로 회피) · 펌웨어 재연결 로직 없음 — 이 시기 기준 | 08-26 ~ 09-03 (이후 09-07 · 09-09 · 09-11 계속) | [08-26 판단·결정 2](../debug_log/2026-08-26/SUMMARY.md) | `/etc/udev/rules.d/99-rover.rules`(Jetson, 08-26 `job0c.sh`) · `ros2_ws/src/rover_bringup/launch/base.launch.py`(Docker agent `-b 2000000` → 09-09 에 460800) | [자이로 소스 → D455f](gyro-source-d455f.md)(같은 날 시작) · micro-ROS 보드율 회귀(09-09, 카드 예정) |

**한 줄**: Jetson 은 CH340(USB-시리얼)으로 보드와 붙고, 장치 이름이 드라이버마다 달라 udev 로 `/dev/rover` 를 고정했다. micro-ROS agent 는 apt 패키지가 없어 Docker 로 띄웠다(2 Mbps). 펌웨어는 **부팅 직후 agent 가 나타날 때까지 ping 하다가 한 번만 세션을 맺고**, 그 뒤 agent 가 바뀌어도 다시 맺지 않는다. 그래서 '보드가 이미 세션을 맺은 상태에서 agent 를 다시 띄우면' 토픽이 사라지고 보드 RESET(물리 버튼 또는 ST-Link `-rst`)이 필요했다. 이 시기에는 펌웨어를 고치지 않고(사용자 규칙: 펌웨어 수정 금지 → 과제로만 기록) **agent 를 건드리지 않는 재시작 스크립트**로 피했다. 원인 기전의 정식 설명은 09-11 §5.7 에서 나온다(이 카드 범위 밖).

## 1. 증상
- agent(Docker 컨테이너)는 살아 있는데 `/wheel_odom` · `/battery` · `/rover/f5b_heartbeat` · `/imu/data_raw` 가 전부 `does not appear to be published yet`, 노드 목록에 `/rover_jupiter` 없음. [08-28 출력 `job7b_board_session.txt`](../debug_log/2026-08-28/outputs/job7b_board_session.txt) — agent `Up About an hour`.
- 보드 RESET 버튼 뒤 같은 스크립트로 `/wheel_odom` 48.599 Hz · 배터리 11.96 V · `/imu/data_raw` 50.001 Hz 로 돌아옴. [`job7b_after_reset.txt`](../debug_log/2026-08-28/outputs/job7b_after_reset.txt)
- 펌웨어 플래시 뒤에도 보드가 agent 에 붙지 않음(agent 가동 중이어도) → ST-Link `-rst` 로 해결. [09-03 '부수 발견 (운영)'](../debug_log/2026-09-03/SUMMARY.md)

## 2. 흐름 (시간순)
| 날짜 · 제목 | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 08-26 '한 일' Step 0 | L4T · USB · CH340 인식 점검, ttyUSB 로 안 잡히는 원인 조사(brltty 여부 · 드라이버 바인딩) | CH340 = `/dev/ttyCH341USB0`(WCH 벤더 드라이버 ch341 V1.9). L4T R36.5.0 | **장치명 하드코딩 금지**(사용자 지시) → udev `/dev/rover` | `jobs/job0.sh` · `job0b.sh` · `job0c.sh` — 출력 원문 없음(이 날은 출력 저장 규약 전, SUMMARY 머리말) |
| 08-26 Step 1 | agent 를 Docker 로 기동(`microros/micro-ros-agent:humble`, `--net host`, `-b 2000000`, `-v4`) | 세션 수립, 토픽 7 종. `/wheel_odom` 49.998 Hz · `/imu/data_raw` 49.999 Hz(σ ≤ 0.2 ms) · `/battery` 12.12 V | apt 패키지 없음 → Docker | `job1.sh` · `job1b.sh` · `job1c.sh` (출력 원문 없음) |
| 08-26 Step 2 | `base.launch.py`(agent + robot_state_publisher)로 전환 — 단독 agent 컨테이너를 지우고 launch 가 같은 이름으로 다시 띄움 | `job2d`(세션 재수립 확인) 뒤 `job2e`('리셋 후 재검증') — SUMMARY: **agent 재시작 시 보드 RESET 필요** | 펌웨어는 부팅 때 1 회만 세션 수립(`microros_task.c:183`), 60 s resync 는 엔티티를 다시 만들지 않음 → **펌웨어 과제**로 기록(수정 안 함) | `job2c.sh` · `job2d.sh` · `job2e.sh` (출력 원문 없음) |
| 08-26 Step 2 | 접지 저속 주행(사용자 승인) — 세션 통해 `/cmd_vel` 첫 사용 | 전진 0.05 m/s 3 s → 140 mm, 후진 복귀 오차 3 mm, 회전 0.3 rad/s → 휠 36° / 실 15° | 링크는 지령 · 발행 모두 정상 | `job2f.sh` |
| 08-26 판단 7 | 모터 구동 스크립트가 Claude Code 분류기에 차단 | — | 사용자가 `!` 접두어로 직접 실행하는 운영 패턴 | — |
| 08-27 '결과' 로버 줄 | Jetson 09:41 재부팅 뒤 bringup 복구(`job4i`), USB 재열거 뒤 복구(`job4k`) — 두 스크립트 모두 끝에 'NEXT: 보드 RESET' | `job4k` 끝: 노드 목록에 `/rover_jupiter` 있음(agent `Up 13 seconds`). `job4l`: `/wheel_odom` 50.002 Hz | RESET 을 실제로 했는지는 기록 없음(**미확인**) | [`outputs/job4k_rs_gate.txt`](../debug_log/2026-08-27/outputs/job4k_rs_gate.txt) · [`job4l_imu_lidar.txt`](../debug_log/2026-08-27/outputs/job4l_imu_lidar.txt) |
| 08-27 'W 트랙' | URDF 확정 반영 — `job5a` 가 agent 를 지우고 `base.launch` 재기동 | `/wheel_odom` 49.997 Hz 바로 나옴 | SUMMARY: '세션 유지, 별도 RESET 불요'. ⚠ 아래 §3 모순 1 | [`outputs/job5a_urdf_bringup.txt`](../debug_log/2026-08-27/outputs/job5a_urdf_bringup.txt) |
| 08-28 '한 일' | 아침 Jetson 재부팅(08:51) 뒤 `job6b` 로 스택 전체 재시작 | uptime 1 min, `/dev/rover -> ttyCH341USB0` 유지, agent 새로 띄운 뒤 `/wheel_odom` 50.016 Hz · 배터리 12.09 V | udev · 장치 이름 재부팅 뒤 유지 | [`2026-08-27/outputs/job6b_restart.txt`](../debug_log/2026-08-27/outputs/job6b_restart.txt)(⚠ 08-28 실행분이 08-27 폴더에 저장됨) |
| 08-28 (SUMMARY 에 없음) | LiDAR yaw 재적용하며 `job6m` 이 agent 포함 전체 재시작 | `/wheel_odom` 칸이 비어 있음(무발행) | — (기록 안 됨) | [`outputs/job6m_yaw_pi_fullrestart.txt`](../debug_log/2026-08-28/outputs/job6m_yaw_pi_fullrestart.txt) |
| 08-28 (SUMMARY 에 없음) | `job7b` 보드 세션 진단 → 사용자 RESET → 다시 `job7b` | 전: agent `Up About an hour`, 보드 토픽 전무 / 후: `/wheel_odom` 48.599 Hz | agent 재시작(job6m) 뒤 세션이 끊겼고 RESET 으로 복구 — 08-26 규칙과 일치 | `job7b_board_session.txt` · `job7b_after_reset.txt` |
| 08-28 (SUMMARY 에 없음) | `job7g` 재부팅 vs Wi-Fi 끊김 판별 | uptime 2:32, agent `Up 2 hours`, `/wheel_odom` 49.994 Hz, Wi-Fi −44 dBm. `last -x` 에 08-27 17:04 · 17:48 재부팅 기록 | 재부팅 아님 — 세션 · 스택 생존 | [`outputs/job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt) |
| 08-31 '한 일' | 충전 중 Jetson · 보드 모두 전원 사이클 → `job8d` 로 전체 재시작 | agent 새로 띄운 뒤 `/wheel_odom` 50.013 Hz | '보드 세션도 자동 재수립(충전 중 보드도 전원 사이클 → RESET 불필요)' | [`2026-08-31/outputs/job8d_restart.txt`](../debug_log/2026-08-31/outputs/job8d_restart.txt) |
| 08-31 (09-01 세션) | `job14a` 스택 재시작(기동 전 agent 없음, uptime 2:12) · `job16a` 세션 초기화(주석: '보드 RESET됨') · `job18b` 는 agent 를 **유지**하고 센서 · SLAM 만 재시작 | 14a: `/wheel_odom` 49.997 · 16a: 50.011 · 18b: 'agent 살아있음(보드 RESET 불필요)' | 'agent 를 안 건드리면 RESET 불필요' 운용이 자리 잡음 | `outputs/job14a_restart.txt` · `job16a_init.txt` · `job18b_restart.txt` |
| 09-02 '한 일' | 충전 뒤 Jetson 복귀 → `job20a_boot` | 09:41 agent 새로 띄운 뒤 `/wheel_odom` 49.992 Hz · 배터리 12.28 V | '보드는 전원 사이클로 자동 재연결(RESET 불필요)' | [`2026-08-31/outputs/job20a_boot.txt`](../debug_log/2026-08-31/outputs/job20a_boot.txt)(실행은 09-02) |
| 09-02 | 로버를 손으로 옮긴 뒤 원점 재설정: `job21a` · `job25a` — **agent 유지**, EKF · SLAM(· Nav2)만 재시작 | 'agent 유지됨(보드 RESET 불필요)' | 위치 초기화와 보드 세션을 분리 | [`2026-09-02/outputs/job21a_reset.txt`](../debug_log/2026-09-02/outputs/job21a_reset.txt) · `job25a_fullreset.txt` |
| 09-03 '한 일' 1~3 | 펌웨어 빌드 환경 복원(`stage_microros.sh` 로 libmicroros.a 재사용) · ST-LINK V3 플래시 | Device 0x413(F405) 검증 OK | — | `jobs/stage_microros.sh` · `cycle.sh` |
| 09-03 '부수 발견 (운영)' | 플래시 뒤 데드밴드 측정 | **플래시 후 보드가 agent 에 자동 재연결되지 않음**(agent 가동 중이어도) → ST-Link `-rst` 로 해결. 디버거 없으면 물리 RESET | 플래시 세션엔 디버거 연결 유지 | `job32c_min012.txt`('보드 재연결:' 칸이 빈 줄 — §5 참조) · `job32e_min016.txt`(agent `Up 5 minutes`, `/wheel_odom` 50.011, `/rover_jupiter` 있음) |
| 09-03 오후 | 스톨 래치 → 사용자 보드 RESET → 세션 재수립 · 새 펌웨어 플래시 · `-rst` | `-rst` 뒤 `/rover/status` level 0, `/wheel_odom` 50 Hz, 배터리 11.99 V | — | 09-03 '플래시 + Jetson Wi-Fi 간헐 무응답' |
| 09-03 '내일 할 일' | 다음 날 절차 확정 | — | agent 살아 있으면 `job33a_reset_noagent.sh`, 없으면 `job20a_boot.sh`(**보드 RESET 필요**) | `jobs/job33a_reset_noagent.sh` · [`outputs/job33a_reset.txt`](../debug_log/2026-09-03/outputs/job33a_reset.txt) |
| **이후(09-04 ~)** | 다음 시기에서 채움 | 지시만: 09-07 'agent 재생성 때문에 세션 미수립 → 물리 RESET'(09-07 SUMMARY) · **09-09 2 Mbps 에서 `/wheel_odom` 소실 → 460800 우회**(09-09 SUMMARY · CLAUDE.md) · **09-11 §5.7 '세션은 보드가 먼저 리셋되면 안 맺어진다' — agent 먼저, 보드 리셋 나중 + `job240_clean.sh` 보드 연결 게이트** | — | — |

## 3. 가설과 판별
| 가설 · 주장 | 판별 | 결과 | 판정 |
|---|---|---|---|
| CH340 이 `ttyUSB*` 로 잡히지 않는 것은 brltty 가 가로채서다 | `job0b`: dmesg · brltty 패키지 · 프로세스 · 인터페이스 드라이버 바인딩 | 결과는 장치 이름이 `ttyCH341USB0`(WCH 벤더 드라이버) — brltty 결과 원문은 없음 | 이름 차이의 원인 = 드라이버(SUMMARY 결과 표). brltty 여부 결과는 **미확인**(출력 원문 없음) |
| agent 를 다시 띄우면 보드 세션이 끊기고 RESET 이 필요하다 | 08-26 job2d → RESET → job2e · 08-28 job6m(agent 재시작) → job7b 무발행 → RESET → 회복 | 두 번 모두 RESET 으로 회복 | **지지**(기전 = 펌웨어 부팅 시 1 회 세션, `microros_task.c:183`) |
| 60 s 주기 time resync(`rmw_uros_sync_session`)가 agent 재연결을 복구한다 | 08-26 펌웨어 소스 읽기(주석 'agent 재연결 복구') | resync 는 시각만 맞추고 엔티티(노드 · 발행자)를 다시 만들지 않음 | **기각**(08-26 판단 2) — 주석이 기능을 과장 |
| 보드가 새로 부팅한 상태(전원 사이클)면 RESET 없이 붙는다 | 08-28 job6b · 08-31 job8d · 09-02 job20a · 09-01 job14a(부팅 뒤 agent 없음) | 모두 agent 기동 10~12 s 안에 `/wheel_odom` ≈ 50 Hz | **지지**(추정 기전: 보드가 부팅 직후 ping 루프에서 agent 를 기다리고 있었음. 각 경우 보드가 실제로 재부팅했는지는 08-31 · 09-02 만 SUMMARY 에 명시) |
| 모순 1: 08-27 job5a 는 세션 중 agent 를 다시 띄웠는데 RESET 없이 49.997 Hz | job5a 직전에 사용자가 `WHEEL_BASE_M` 0.245 펌웨어를 플래시(08-27 W 트랙) | 보드가 플래시 뒤 아직 세션을 맺지 않은(ping 대기) 상태였을 수 있음 | **미확인**(추정만). 이 한 번이 '규칙 예외'로 남는다 |
| 모순 2: 09-03 '플래시 후 자동 재연결 안 됨(agent 가동 중이어도)' — 위 '새로 부팅하면 붙는다' 와 반대 | 순서 기록: 플래시(`-rst` 포함) → `job32c` 가 **agent 를 지우고 다시 띄움** → '보드 재연결:' 빈칸 → 이후 `-rst` → `job32e` 에서 agent `Up 5 minutes` 와 함께 세션 정상 | 끊김이 플래시 때문인지, job32c 의 agent 재시작 때문인지(= 08-26 규칙) 구분 안 됨 | **미확인** — 09-11 §5.7 의 '보드 리셋 → agent 재시작 순서면 안 맺어짐' 이 같은 현상일 가능성(추정) |
| 09-03 오후 Jetson 재부팅 뒤 job34a 에서 RESET 없이 50.002 Hz | Jetson 재부팅이 보드도 재부팅시키는지 | 기록 없음 | **미확인** |

## 4. 조치와 효과
- **장치 이름 고정**: `/etc/udev/rules.d/99-rover.rules` — `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="rover", GROUP="dialout", MODE="0660"`. 08-28 · 08-31 재부팅 뒤에도 유지 확인(`job6b` 출력 `/dev/rover -> ttyCH341USB0`, 08-31 '한 일').
- **agent 기동 방식**: `base.launch.py` 가 `os.path.realpath('/dev/rover')` 로 실장치를 찾아 `docker run --rm --name microros_agent --net host --device <실장치>:/dev/rover microros/micro-ros-agent:humble serial --dev /dev/rover -b 2000000`. 컨테이너 이름을 고정해 이중 실행을 막는다(같은 이름이면 docker 가 거부). 심볼릭 링크를 그대로 `--device` 에 주지 않는 이유: 컨테이너 안에 링크 대상이 없으므로 실장치를 넘긴다(08-26 `job1.sh` 주석).
- **운영 절차**(이 시기 확정): ① 위치만 다시 잡을 때는 agent · `base.launch` 를 건드리지 않고 EKF · SLAM 만 재시작(`job18b` → `job21a` → `job25a` → `job33a`) ② agent 를 새로 띄워야 하면 보드 RESET 을 짝으로 ③ 플래시 뒤엔 ST-Link `-rst`(디버거 연결 유지).
- 효과: 09-01 ~ 09-03 의 위치 재설정 재시작에서 보드 세션 유지(`job18b` · `job21a` · `job33a` 출력: `/wheel_odom` 49.955 Hz 등).
- 한계: 펌웨어 재연결 로직이 없으므로 agent 가 죽으면(Jetson 재부팅 등) 사람 손이 필요. 원인 해결이 아니라 회피.

## 5. 내 실수 · 기록 결함
### 5.1 재시작 스크립트가 결과와 상관없이 'NEXT: 보드 RESET' 을 찍음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 스택 재시작 뒤 보드 세션 상태를 사람에게 알리기(`job4i` · `job4k` · `job8d` · `job14a`) |
| 본 것 | `job8d_restart.txt`: `wheel_odom: average rate: 50.013` 바로 다음 줄에 `NEXT: 보드 RESET 버튼 → 세션 재수립`. `job14a_restart.txt` 도 49.997 Hz 뒤 같은 줄 |
| 처음 추론 | (스크립트에 고정된 문구) 'agent 를 새로 띄웠으니 RESET 필요' |
| 의심한 이유 | 같은 출력의 직전 줄이 이미 50 Hz — 세션이 있다 |
| 판별 | 08-31 SUMMARY 는 '보드도 전원 사이클 → RESET 불필요' 로 바르게 적음. 스크립트만 고정 문구 |
| 결론 | 판정은 스크립트 문구가 아니라 측정 줄(`/wheel_odom` Hz)로 한다 |
| 다음에 알아보는 법 | 상태 판정 스크립트는 측정값으로 분기해 문구를 낸다. 이 개선은 09-03 `job33a`('무발행 ★RESET 필요' 를 실패 때만) → 09-11 `job240_clean.sh` 보드 연결 게이트로 이어짐 |
| 데이터 | `2026-08-31/outputs/job8d_restart.txt` · `job14a_restart.txt` · `2026-08-31/jobs/job8d.sh` |

### 5.2 `job32c` 의 '보드 재연결:' 빈칸 — 실패를 놓친 파이프
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 플래시 뒤 agent 를 다시 띄워 보드 재연결 → EKF 재시작 → MIN 0.012 데드밴드 측정 |
| 본 것 | `job32c_min012.txt` 첫 줄 `보드 재연결: ` 뒤가 비어 있고 같은 줄에 컨디셔너 로그가 붙음. 이어진 측정은 ω 0.05~0.20 모두 `-0.0도 ✗ 무반응` |
| 처음 추론 | 기록상 남은 추론 없음(**미확인**). SUMMARY 표의 MIN 0.012 줄은 다음 측정(`job32d`: 7.9 / 0.3 / 8.3 / 39.7 / 47.4°)을 썼고 job32c 는 언급되지 않음 |
| 의심한 이유 | 모든 지령에서 정확히 −0.0° — 데드밴드라면 0.20 rad/s 쯤에선 돌아야 함(같은 MIN 의 job32d 에서 39.7°) |
| 판별 | 스크립트 `timeout 6 ros2 topic hz /wheel_odom … \| grep … \| head -1 \|\| echo "실패!"` — 파이프의 종료 코드가 `head` 의 것(0)이라 무발행이어도 '실패!' 가 안 찍힌다 |
| 결론 | job32c 의 '무반응' 은 데드밴드가 아니라 **보드 세션 없음**(지령이 보드에 안 감)일 가능성이 높다(**추정** — 세션 부재를 직접 찍은 줄은 빈칸뿐) |
| 다음에 알아보는 법 | 서명: 모든 지령에서 정확히 0 의 변화 + 상태 줄 빈칸. 판정 줄은 `PIPESTATUS` 나 결과 문자열 검사로 실패를 명시적으로 찍는다 |
| 데이터 | [`2026-09-03/outputs/job32c_min012.txt`](../debug_log/2026-09-03/outputs/job32c_min012.txt) · `job32d_min012.txt` · `jobs/job32c_reagent.sh` |

## 6. 남은 것 (이 시기 기준)
- 펌웨어 재연결 로직(ping 실패 → 엔티티 재생성) — 08-26 펌웨어 과제 목록 1 번. 이후 시기에서 처리 여부 확인.
- 모순 1(08-27 job5a) · 모순 2(09-03 플래시 뒤) 의 기전 — 09-11 §5.7 의 순서 규칙으로 설명되는지 다음 시기 카드에서 대조.
- Jetson 재부팅이 보드를 재부팅시키는지(09-03 job34a) — 미확인.
- 2 Mbps 설정은 08-26 · 08-27 에 50 Hz 두 토픽을 안정적으로 실었음(`job4x` `/wheel_odom` 49.995 Hz). 09-09 회귀는 다음 시기.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| Step 0~2 | CH340 · udev · agent · base.launch · 첫 주행 | 08-26, `2026-08-26/jobs/job0*~job2*` (출력 원문 없음) |
| 세션 끊김 1 | agent 재시작 → RESET | 08-26 job2d → job2e |
| 세션 끊김 2 | job6m(agent 재시작) → job7b 무발행 → RESET → 회복 | 08-28 `outputs/job6m_*` · `job7b_*` |
| 전원 사이클 뒤 자동 수립 | job6b · job8d · job14a · job20a | 08-28 · 08-31 · 09-01 · 09-02 |
| 플래시 뒤 미연결 | cycle.sh · job32c · chk_board | 09-03 `jobs/` · `outputs/job32c_min012.txt` · `job32e_min016.txt` |
| agent 유지 재시작 | job18b · job21a · job25a · job33a | 08-31 · 09-02 · 09-03 |

## 8. 도구 해설
도구 계보: `job0 → job0b → job0c`(장치) · `job1 → job1b → job1c`(agent · 토픽 확인) · `job1 → base.launch.py(job2c)` · `job2d → job2e`(재검증) · `job6b → job8d → job14a → job16a_init → job20a_boot`(전체 기동) · `job18b → job21a → job25a → job33a_reset_noagent`(agent 유지 재시작) · `job7b · chk_board`(세션 확인) · `cycle.sh → job32c_reagent`(플래시 뒤). 공통 실행 형태: PC(Windows) → WSL `sshpass` → Jetson 에서 `bash /tmp/<job>.sh`(스크립트를 `/tmp` 로 올려 실행 — `job34a_boot.txt` 머리의 '스크립트 재전송' 줄). 예외: `cycle.sh` · `stage_microros.sh` 는 PC.

### 8.1 `job0.sh` — Step 0 장치 점검
- 실행: Jetson, 인자 없음.
- 왜: 보드를 처음 붙이며 L4T 버전과 CH340 인식 여부를 확인.
- 하는 일: `/etc/nv_tegra_release`, `dpkg -l | grep jetpack|nvidia-l4t-core`, `lsusb`, `ls -l /dev/ttyACM* /dev/ttyUSB*`, `lsmod | grep ch34` 와 `modinfo ch341`(모듈 존재), `dmesg | grep ch34|ttyUSB|1a86`(sudo 없이 — 거부될 수 있음).
- 출력: `===L4T===` 등 구역 머리 + 원문. 출력 원문 없음(대화에만). 결과는 SUMMARY '한 일' Step 0(L4T R36.5.0 · JetPack 6.2 계).
- 계보 · 결함: `ttyUSB*` 만 찾으므로 WCH 드라이버의 `ttyCH341USB*` 를 못 봄 → job0b 로 이어짐. 지금 다시 쓸 수 있음(진단용), 단 장치 이름 패턴 보완 필요.

### 8.2 `job0b.sh` — ttyUSB 로 안 잡히는 원인
- 실행: Jetson, sudo 비밀번호를 `echo '<PW>' | sudo -S` 로(커밋본은 가림).
- 왜: job0 에서 CH340 은 `lsusb` 에 있는데 `ttyUSB*` 가 없었음(SUMMARY 근거: 최종 장치명이 `ttyCH341USB0`).
- 하는 일: sudo dmesg 필터(ch34 · ttyUSB · 1a86 · brltty), brltty 패키지 · 프로세스 유무, `udevadm info` (경로 `1-2.2` 고정), `/sys/bus/usb/devices/*` 중 idVendor=1a86 을 찾아 각 인터페이스의 바인딩 드라이버 출력.
- 출력: 원문 없음. 결과가 쓰인 곳: SUMMARY 결과 표 'CH340 장치' 줄, `JETSON_SETUP_BRIEF.md` 장치명 정책.
- 결함: `udevadm` 경로가 `1-2.2` 고정(실제 위치는 `1-2.1` — 08-27 `job4v` 토폴로지). brltty 결론은 기록에 없음. 재사용: 드라이버 바인딩 루프 부분은 유효.

### 8.3 `job0c.sh` — udev 규칙 설치
- 실행: Jetson(sudo).
- 하는 일: `/etc/udev/rules.d/99-rover.rules` 작성(위 §4 원문) → `udevadm control --reload-rules && udevadm trigger --subsystem-match=tty` → `ls -l /dev/rover`.
- 출력: `/dev/rover -> ttyCH341USB0` 또는 `NO_ROVER_LINK`. 원문 없음. 이후 모든 스크립트 · launch 가 `/dev/rover` 만 참조.
- 계보: 같은 형식이 08-27 `job4e` 의 `/dev/rplidar`(CP210x 10c4:ea60) 규칙으로 복제. 지금도 유효(규칙은 Jetson 에 설치된 채).

### 8.4 `job1.sh` — agent 컨테이너 단독 기동
- 하는 일: `REAL_DEV=$(readlink -f /dev/rover)` → `docker rm -f microros_agent` → `docker run -d --name microros_agent --net host --device "$REAL_DEV:/dev/rover" microros/micro-ros-agent:humble serial --dev /dev/rover -b 2000000 -v4` → 8 s 뒤 `docker logs | tail -15`.
- 왜: Humble 용 agent 가 apt 에 없어서(SUMMARY Step 1). `--net host` = 컨테이너가 호스트 DDS 와 같은 네트워크를 써야 Jetson 노드가 토픽을 봄. `-v4` = 세션 로그를 보려는 상세 모드.
- 출력: agent 로그 15 줄(세션 수립 여부). 원문 없음.
- 계보: 08-26 Step 2 에서 `base.launch.py` 의 `ExecuteProcess` 로 옮김(`-d` 대신 launch 가 소유, `--rm`, `-v4` 제거). 지금: 보드율은 09-09 부터 460800 — 이 스크립트 그대로는 **못 씀**.

### 8.5 `job1b.sh` → `job1c.sh` — 토픽 · 주기 · 배터리 확인
- job1b: `ros2 topic list`, `ros2 topic hz /wheel_odom --qos-reliability best_effort`(12 s), 같은 식으로 `/imu/data_raw`, `/battery --once`.
- 결함: Humble 의 `ros2 topic hz` 에는 QoS 옵션이 없음 → job1c 주석 'Humble hz는 QoS 플래그 없음'.
- job1c: 플레인 `hz`(QoS 자동) 재시도 + 대체 측정 = `ros2 topic echo … --qos-reliability best_effort --field header.stamp.sec` 를 10 s 동안 받아 숫자 줄을 세고 `N/10` Hz(정수 나눗셈).
- 출력: `wheel_odom msgs in 10s: N (=> X Hz)`. 원문 없음. 결과: SUMMARY 결과 표 '토픽 주기' 49.998 / 49.999 Hz(σ ≤ 0.2 ms 는 hz 출력 쪽 값으로 보임 — 어느 줄인지 원문 없음).
- 재사용: 개념만. 지금은 `Docs/tools/` 의 확인 도구를 씀.

### 8.6 `job2a.sh` · `job2c.sh` — 워크스페이스 · base.launch 기동
- job2a: colcon · rosdep · 필요한 ROS 패키지(robot-state-publisher · xacro · tf2-tools 등) · `~/ros2_ws` 유무만 확인.
- job2c: `/tmp/rover_src/{rover_description,rover_bringup}` → `~/ros2_ws/src` 복사 → `colcon build --symlink-install` → **단독 agent 컨테이너 삭제**(launch 가 같은 이름으로 다시 띄우므로) → `setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log` → 18 s 뒤 로그 · `docker ps` · 노드 목록 · `/wheel_odom` hz · `robot_description` 파라미터 앞 120 자 · `/tf_static`(transient_local, reliable) 프레임 쌍.
- 결과가 쓰인 곳: 08-26 Step 2. 이 '단독 agent 삭제 → launch 가 재생성' 이 바로 세션을 끊은 첫 사건(→ job2d · job2e).
- 재사용: 아니오(배포 방식이 이후 바뀜).

### 8.7 `job2d.sh` → `job2e.sh` — 세션 재수립 확인
- job2d: `/tmp/bringup.log` 에서 `session established|create_client` grep(마지막 3 줄), 토픽 목록, `/wheel_odom` · `/imu/data_raw` hz(10 s), 노드 목록.
- job2e(주석 '리셋 후 재검증'): 같은 확인 + `/battery` voltage.
- 판정 기준: 로그에 `session established` 가 있고 `/wheel_odom` 이 ≈ 50 Hz 이면 세션 정상. 출력 원문 없음. 결과: SUMMARY 판단 2('agent 재시작 시 보드 RESET 필요').
- 결함: agent 로그 grep 은 `-v4` 가 빠진 launch 판에선 세션 줄이 안 나올 수 있음(launch 판 agent 는 `-v4` 없음 — 기본 상세도에서 해당 줄이 찍히는지 **미확인**).

### 8.8 `job2f.sh` — 접지 초저속 주행(링크로 첫 지령)
- 하는 일: `/wheel_odom` pose 스냅샷 → `ros2 topic pub -r 10 -t 30 /cmd_vel {angular.z: 0.3}`(3 s) 중간에 twist 1 회 → 정지(빈 Twist 5 회) → 전진 0.05 · 후진 0.05 각 3 s, 매번 pose 스냅샷.
- 한계 주석: linear ≤ 0.08, angular ≤ 0.8(지시서 §3).
- 출력 원문 없음. 결과: SUMMARY 결과 표 '주행 테스트'. 사용자 `!` 실행(분류기 차단).

### 8.9 `base.launch.py` (rover_bringup) — agent 를 소유하는 launch
- 위치: `ros2_ws/src/rover_bringup/launch/base.launch.py`(09-02 커밋 `76c08343` 판 기준; 08-26 원본은 저장소 이전 전이라 없음).
- 하는 일: §4 의 docker 명령 + `rover_description/launch/description.launch.py` 포함. launch 를 죽이면 `--rm` 컨테이너도 사라짐 → **launch 재시작 = agent 재시작 = 세션 끊김**.
- 지금: 09-09 부터 `-b 460800`(CLAUDE.md). 계속 쓰는 파일.

### 8.10 `job7b.sh` — 보드 세션 진단(08-28)
- 하는 일: agent 컨테이너 상태, `docker logs --tail 3` 중 session · Serial · error, 토픽 목록 중 `wheel_odom|battery|heartbeat|rover`, `/wheel_odom` 10 s hz, `/battery` 1 회, `/rover/f5b_heartbeat` 1 회(펌웨어 1 Hz 카운터), `/imu/data_raw` hz.
- 판정: 토픽 이름이 목록에 있어도 '발행 중' 은 아님(구독자 · 다른 노드가 이름을 남김) — `hz` 가 `does not appear to be published yet` 이면 무세션.
- 출력: `job7b_board_session.txt`(전) · `job7b_after_reset.txt`(후, heartbeat `data: 105`). 재사용: 형태는 `chk_board.sh` 로 축소 계승.

### 8.11 `job7g.sh` — 재부팅 vs Wi-Fi 끊김 판별
- 하는 일: `uptime`/`uptime -s`, sudo dmesg 끝 6 줄, `last -x` 재부팅 이력, ROS 프로세스 수 · 노드 목록, agent 컨테이너 uptime(재부팅이면 사라짐), `/wheel_odom` hz · 배터리, `lsmod | grep -c hid_sensor`(HID 모듈 자동 로드), `iwconfig wlP1p1s0` 신호.
- 판정: uptime 이 길고 agent 가 `Up 2 hours` 면 재부팅 아님 → 끊김은 PC↔Jetson 네트워크 쪽.
- 출력: `job7g_reboot_check.txt`. 재사용: Wi-Fi 진단은 이후 `/var/log/wifi_mon` 으로 대체(CLAUDE.md).

### 8.12 `cycle.sh` (09-03, PC Git Bash) — 펌웨어 값 바꿔 빌드 · 플래시 · 리셋
- 부른 형태: `bash cycle.sh <MIN>`(예 0.012 · 0.016 · 0.020).
- 하는 일: `sed -i` 로 `rover_platform.h` 의 `#define MIN_WHEEL_SPEED_MPS` 값 교체 → STM32CubeCLT gcc + GnuWin32 make 로 `make -j8`(크기 줄만) → `STM32_Programmer_CLI -c port=SWD reset=HWrst -w <elf> -v -rst`('Download verified' 줄만) → 3 s 뒤 **한 번 더** `-c port=SWD reset=HWrst -rst` → 12 s 대기.
- 왜 두 번째 `-rst`: 09-03 '부수 발견' — 플래시 뒤 자동 재연결이 안 돼서(주석에는 'ST-Link 리셋' 단계로만 적힘).
- 결함: 주석은 'EKF 재시작 → 데드밴드 측정' 까지 말하지만 스크립트는 리셋 뒤 12 s 대기로 끝남(측정은 별도 `job32b_deadband.sh`). `sed -i` 로 소스를 직접 바꾸므로 마지막 값이 소스에 남음(09-03 최종 0.020 은 별도 확정 플래시). 출력 원문 없음.
- 재사용: 경로(`C:\ST\STM32CubeCLT_1.21.0`)가 맞으면 가능. 지금 플래시 · 리셋 규약은 메모리 '플래시 후 -rst'.

### 8.13 `job32c_reagent.sh` — 플래시 뒤 agent 재연결
- 하는 일: `docker rm -f microros_agent`, `base.launch` 종료 → 다시 기동 → 12 s 뒤 `/wheel_odom` hz → EKF(컨디셔너) 재시작 → 바이어스 로그 · `/odometry/filtered` hz.
- 결함: §5.2 — `… | head -1 || echo "실패!"` 가 실패를 못 찍음. 또 '보드가 세션을 맺은 뒤 agent 를 다시 띄우면 끊긴다' 는 08-26 규칙과 반대 방향의 조치(agent 를 다시 띄움)라, 이 스크립트 자체가 끊김을 만들었을 수 있음(**추정**).
- 출력: `job32c_min012.txt` 앞부분. 후속: 다음 날 절차에서 `job33a_reset_noagent.sh`(agent 손대지 않음)로 대체.

### 8.14 `chk_board.sh` — 세 줄 세션 확인
- 하는 일: agent 컨테이너 이름 · 상태, `/wheel_odom` hz(6 s), 노드 목록 중 `rover_jupiter`.
- 출력 형태: `agent: microros_agent Up 5 minutes` / `/wheel_odom: average rate: 50.011` / `보드 노드: /rover_jupiter` — `job32e_min016.txt` 머리 3 줄이 이 형태(그 실행 결과로 **추정**).
- 결함: job32c 와 같은 `| head -1 || echo` 패턴 — '무발행' 문구가 안 찍힘. 재사용: 개념은 09-11 보드 연결 게이트로 계승.

### 8.15 `job33a_reset_noagent.sh` — agent 를 건드리지 않는 위치 초기화
- 주석: '손 이동 후 초기화 — agent 는 절대 건드리지 않음(디버거 없어 RESET 불가)'.
- 하는 일: agent · `/wheel_odom` · 배터리 확인(무발행이면 '★RESET 필요' 를 의도) → 컨디셔너 · EKF · SLAM 종료 → `ekf.launch`(16 s, 자이로 바이어스 10 s 동안 정지 필수) → `slam.launch` → `/odometry/filtered` · 원점 x · `/scan` 확인. 출력 파일 뒤쪽 '공간 판정'(방위별 최소거리, 스윕 반경 30 cm)은 저장된 스크립트에 없는 부분 — 같은 이름의 다른 판으로 **추정**(원문 미확인).
- 출력: `job33a_reset.txt`(`/wheel_odom` 49.955, 바이어스 (−0.00786, −0.00123, −0.00185)). 재사용: 역할은 이후 prep 스크립트(`Docs/tools/prep_patrol.sh` 계열)로 흡수.

### 8.16 전체 기동 · 재시작 스크립트 (간단 표)
| 도구 | 날짜 · 위치 | 하는 일 | agent | 출력 · 결과 |
|---|---|---|---|---|
| `job4i.sh` | 08-27 Jetson | 재부팅 뒤 HID 모듈 modprobe + `base` · `ekf` 기동, 끝에 'NEXT: 보드 RESET' | 새로 | 원문 없음. 번호상 다음인 `job4j` 출력에서 `AGENT_DOWN`(이유 **미확인**) |
| `job4k.sh` [3] | 08-27 | 카메라 게이트 뒤 bringup 복구(agent 삭제 → base → ekf) | 새로 | `job4k_rs_gate.txt` 끝: `/rover_jupiter` 있음 |
| `job5a.sh` | 08-27 | 확정 URDF 빌드 → slam · sensors · base 전부 종료 → base(agent) → sensors, TF 트리 · rates | 새로 | `job5a_urdf_bringup.txt`: `/wheel_odom` 49.997 — §3 모순 1 |
| `job6b.sh` | 08-28 | uptime · 장치 링크 · HID 모듈 수 · 잔여 정리 → base → sensors(35 s) → rates, 배터리로 세션 확인 | 새로 | `2026-08-27/outputs/job6b_restart.txt`(위치 주의) |
| `job6m.sh` | 08-28 | URDF yaw=π 재적용 + 전체 재시작(stale TF 제거 목적) | 새로 | `job6m_yaw_pi_fullrestart.txt`: `/wheel_odom` 빈칸 → 세션 끊김 |
| `job8d.sh` | 08-31 | 재부팅 뒤 base + sensors(lidar · scan_restamp · camera · ekf · foxglove) + slam | 새로 | `job8d_restart.txt` 50.013 Hz(§5.1) |
| `job10a.sh` → `job10b.sh` | 08-31 | RESET 전 상태(agent · 세션 · 노드, teleop 정리) → RESET 뒤 세션 · odom 원점 · slam 재시작 · 파이프라인 hz | 유지 | `job10a_prereset.txt`(agent `Up 7 hours`, 50.028) · `job10b_reset_slam.txt`(49.994, 12.20 V). 여기서 'RESET' 은 odom 원점 초기화 맥락 — 보드 RESET 여부 **미확인** |
| `job14a.sh` | 09-01 | 전체 재시작, 주석 'agent 재시작 → 보드 RESET 필요' | 새로(이전 NO_AGENT) | `job14a_restart.txt` 49.997 |
| `job16a_init.sh` | 09-01 | base + sensors + slam, 주석 '보드 RESET됨', 자이로 캘리브 정지 경고 | 새로 | `job16a_init.txt` 50.011 |
| `job18b_restart.sh` | 09-01 | **agent 유지** — sensors · slam 계열만 `pkill -9` 후 재기동, foxglove · deskew 개수 | 유지 | `job18b_restart.txt` |
| `job20a_boot.sh` | 08-31 폴더 = 09-02 폴더(동일 파일) | 부팅 뒤 base(12 s) → `/wheel_odom` · 배터리 → sensors(22 s) → slam → 노드 · VX_SCALE · 원점 · map→odom | 새로 | `2026-08-31/outputs/job20a_boot.txt`(09-02) · `2026-09-03/outputs/job32a_boot.txt` · `job34a_boot.txt`(09-03, 같은 출력 형식이라 이 스크립트로 **추정**) |
| `job21a_reset.sh` | 09-02 | agent 유지, EKF · SLAM 재시작 + 스캔으로 회전 여유 판정(스윕 반경 = hypot(0.25, 0.165)) | 유지 | `job21a_reset.txt`(+ `job21b_reset2` · `job21e_reset3` · `job22a_reset` 등 같은 형태 재실행으로 **추정**) |
| `job25a_fullreset.sh` | 09-02 | Nav2 종료 → EKF → SLAM → Nav2 재기동 · lifecycle · 방향별 여유 | 유지 | `job25a_fullreset.txt` |
| `stage_microros.sh` | 09-03 WSL | WSL `~/microros_build/firmware/build` 의 `libmicroros.a` · include 를 `/mnt/c/temp_microros` 로 복사, `include/X/X/*` 평탄화, 헤더 수 출력 | — | 원문 없음. SUMMARY: 7.4 MB · 헤더 1765 재사용으로 30 분+ 절감, WSL 이 F: 를 못 봐 C: 경유 |

## 9. 용어
- **CH340(N)**: USB↔UART 변환 칩(벤더 1a86, 제품 7523). USB Full-Speed(12 Mbps) 장치(`job4v` 토폴로지 `1-2.1 … speed=12M`).
- **ttyUSB vs ttyCH341USB**: 같은 칩이라도 커널 기본 `ch341` 드라이버면 `ttyUSB*`, WCH 벤더 드라이버면 `ttyCH341USB*` 로 이름이 달라진다.
- **udev 규칙 · 심볼릭 링크**: 리눅스가 장치를 붙일 때 규칙(벤더 · 제품 ID 일치)을 보고 `/dev/rover` 같은 고정 별칭을 만들어 준다. 포트 · 드라이버가 바뀌어도 스크립트는 별칭만 쓴다.
- **brltty**: 점자 단말 데몬. 일부 우분투에서 CH340 류를 점자기로 오인해 가로채는 것으로 알려져 있어 점검 대상이었다(이 장비에서 해당 여부는 기록 없음).
- **micro-ROS agent**: MCU(클라이언트)의 XRCE-DDS 메시지를 일반 ROS 2(DDS) 토픽으로 중계하는 Jetson 쪽 프로그램. 보드 노드 `/rover_jupiter` 는 agent 를 통해서만 보인다.
- **XRCE-DDS 세션**: 클라이언트가 `CREATE_SESSION` 으로 agent 와 맺는 연결 상태. 세션 위에 노드 · 발행자 · 구독자(엔티티)를 만든다. agent 가 새로 뜨면 옛 세션 · 엔티티를 모른다(09-11 §5.7 설명).
- **ping 루프(`rmw_uros_ping_agent`)**: 펌웨어가 부팅 직후 1 s 간격으로 agent 존재를 확인하는 반복(08-26 판 `microros_task.c` 183 행). 성공하면 지나가서 다시 돌아오지 않는다.
- **time resync(`rmw_uros_sync_session`)**: agent 시각과 보드 시각을 맞추는 호출. 60 s 마다 하지만 세션 · 엔티티 재생성은 하지 않는다.
- **`--net host` · `--device`**: Docker 옵션. 컨테이너가 호스트 네트워크를 그대로 쓰게 함(DDS 탐색용) · 호스트 장치 파일을 컨테이너 안으로 넘김.
- **보드율(baud) 2,000,000**: UART 속도. 이 시기 설정값. 09-09 에 460800 으로 낮춤(이후 시기).
- **ST-Link `-rst`**: STM32CubeProgrammer CLI 가 SWD 로 MCU 를 하드 리셋하는 옵션. 물리 RESET 버튼 대용.
- **`ros2 topic hz` 와 '토픽이 목록에 있음'**: 목록은 구독자만 있어도 이름이 남는다. 발행 여부는 `hz`/`echo` 로 본다.
