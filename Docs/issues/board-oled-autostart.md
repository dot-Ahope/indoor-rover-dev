# 보드 OLED 상태 표시 · base 부팅 자동 기동 (5 시기: 09-28 §28 · 09-29 §2)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **해결**(기능) — OLED 표시는 새 모듈로 화면 확인(사용자 눈), base 자동 기동은 재부팅 뒤 사람 개입 없이 IP 표시(사용자 확인). 남은 한계 2 개(아래 §6) | 09-28 ~ 09-29 | [09-28 §28](../debug_log/2026-09-28/SUMMARY.md) (사용자 요청) · [09-29 §2](../debug_log/2026-09-29/SUMMARY.md) ("OLED 에 IP 가 안 나옴") | 펌웨어 `App/drivers/ssd1306_driver.[ch]` · `App/drivers/battery_adc.[ch]` · `App/app/display_info.[ch]` · `App/app/display_task.[ch]` · `App/microros/microros_task.c`(구독 추가) / Jetson [`display_info_pub.py`](../../ros2_ws/src/rover_bringup/scripts/display_info_pub.py) · [`base.launch.py`](../../ros2_ws/src/rover_bringup/launch/base.launch.py) 45~49 행 · [`systemd/rover-base.service`](../../ros2_ws/src/rover_bringup/systemd/rover-base.service) · [`install_rover_base_service.sh`](../../ros2_ws/src/rover_bringup/scripts/install_rover_base_service.sh) · prep `job240_clean.sh` 2 단계 | [보드 연결 · micro-ROS 세션](board-link-microros-session.md)(세션은 보드 부팅 때만 맺어짐) · [Jetson Wi-Fi](jetson-wifi-link.md)(IP 가 바뀌는 이유) · [배터리 · 전원 운용](battery-power-ops.md)(보드 전원 = Jetson 전원) · [온보드 정지 수단 · nav_guard](onboard-stop-nav-guard.md)(L1 = 보드 전원 스위치 복구 절차가 이 서비스에 기댐) |

**한 줄**: Jetson 은 무선 IP 가 WEB_DEV ↔ ALOPS 로 바뀌고 재부팅도 잦은데, SSH 주소를 알 길이 없었다. 보드 J8 헤더에 0.91" SSD1306 OLED 를 달고, Jetson 이 쓰는 IP · SSID 를 micro-ROS 토픽으로 보내 보드가 그리게 했다(09-28). 첫 모듈은 명령에 ACK 하면서도 점등하지 않는 **패널 불량**이었고 교체로 해결. 다음 날 아침 '재부팅 뒤 IP 가 안 보인다' 는 것은 **구조 문제**(IP 가 micro-ROS 로만 가므로 사람이 base 를 띄우기 전엔 표시가 없음)여서 base 를 systemd 사용자 서비스로 부팅 때 자동 기동했다(09-29).

## 1. 증상
- 09-28: 요구 — 재부팅 · 망 전환 뒤 Jetson 주소를 보드에서 바로 읽고 싶다(사용자 요청, §28).
- 09-28 §28.2: 보드 쪽은 정상(구독 1, 전송 성공)인데 화면이 꺼져 있음.
- 09-29 §2: Jetson 이 밤사이 재부팅(uptime 1 h 8 min) → 에이전트 · base · `display_info_pub` 모두 없음 → OLED 줄 1 이 비어 있음(펌웨어는 정보가 한 번도 안 오면 `IP (no Jetson info)`).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 09-28 §28 | 회로도로 J8 = SDA · SCL · **5.0 V** · GND → I2C2(PB10/PB11, 100 kHz 이미 초기화) 확인. 펌웨어 4 모듈 + micro-ROS 구독 추가, Jetson 발행 노드 | 빌드 경고 0, text 131,280 B · data 5,164 · bss 118,624(data+bss 123.8 KB / RAM 128 KB) | 계층 유지(Driver · App · Comm) | 회로도 `Docs/01_firmware/STM32BD/ROVER_MECURY_R10.20260106.pdf` 2 쪽. 출력 원문 없음(SUMMARY 수치만) |
| 09-28 §28.1 | 백업(`fw_backup_20260928_before_oled.bin`, 로컬 스크래치패드 — **원천 소실 가능**) 뒤 `STM32_Programmer_CLI … -w build/rover_jupiter_fw.elf -v -rst` | `/wheel_odom` 25.001 Hz(전과 같음), `/battery` 12.20 V, status OK, `/rover/display_info` **구독 수 1**, 발행값 `IP=192.168.0.101;SSID=WEB_DEV_5G` | 보드 수신까지는 **측정**으로 확인, 화면은 사용자 확인 대기 | 출력 원문 없음 |
| 09-28 §28.2 | 화면 안 나옴 → SWD 로 드라이버 상태 읽기 | `s_ok`=1, 초기화 명령 16 개 ACK, 1 Hz 513 B 전송 계속 성공, 프레임 버퍼에 "IP 192.168…" 글리프 정상 | 펌웨어는 끝까지 동작 | 출력 원문 없음 |
| 09-28 §28.2 | 가설 '5 V 미공급(풀업 기생 전원으로 논리부만 ACK)' | 사용자 측정 J8 3–4 번 **5.21 V** | **기각** | 사용자 측정(구두) |
| 09-28 §28.2 | 진단 펌웨어(임시 `TODO(improve)` 훅: 부팅 I2C2 스캔 + SWD 명령 1 바이트 전송) | I2C2 ACK 는 **0x3C 하나뿐**, **0xA5(RAM 무시 전체 점등)도 ACK 인데 무점등** | 패널 불량 의심 | 진단 훅은 제거 — 코드 남지 않음 |
| 09-28 §28.2 | 전원 끄고 새 모듈로 교체 | 화면 정상(사용자) | 원인 = 첫 모듈 패널 불량 | 재플래시(커밋 0075277 과 같은 펌웨어, text 131,280 B) 뒤 `/wheel_odom` 25.000 Hz · 12.21 V · 구독 1 |
| 09-29 §2 | 재부팅 뒤 IP 공백 원인 조사 | uptime 1 h 8 min, base 프로세스 없음 | **구조 문제**: IP 경로가 micro-ROS 뿐 | — |
| 09-29 §2 | 대안 3 개 비교 → systemd 사용자 서비스 + linger | 설치 10:28: Linger=yes, enabled, active 15 s 뒤 `/wheel_odom` 24.997 Hz · display_info 구독 1 · 세션 1 건 — **보드 리셋 없이 연결**(보드가 에이전트 대기 중이었음) | 채택 | 출력 원문 없음 |
| 09-29 §2 | 전원 끄고 켜기 확인 | 재부팅 뒤 사람 개입 없이 OLED 에 IP(사용자) | §2 종결 | 사용자 확인 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 펌웨어 · I2C 전송이 실패한다 | SWD 로 `s_ok` · 전송 결과 · 프레임 버퍼 읽기 | 전부 정상 | 기각(측정) |
| 5 V 가 안 와서 패널만 꺼져 있다 | J8 3–4 번 전압 | 5.21 V | 기각(측정) |
| 주소 0x3C 에 다른 부품이 답한다 | 부팅 I2C2 스캔 | ACK 0x3C 하나 | 기각(측정) |
| 패널 자체 불량 | 0xA5(전체 점등) 전송 → 무점등, 새 모듈 → 정상 | 교체로 해결 | **지지**(교체 1 회 — 첫 모듈을 다른 보드에서 시험하진 않음) |
| 재부팅 뒤 공백 = 구조 문제(base 를 사람이 띄워야 함) | uptime · 프로세스 확인, 서비스 설치 뒤 전원 재투입 | 사람 개입 없이 IP 표시 | 지지 |

대안 비교(09-29 §2): ① 매번 수동 기동(현상 유지) ② **systemd 로 base 자동 기동(채택)** ③ 부팅 스크립트가 시리얼로 IP 직접 송신 — micro-ROS 와 같은 UART 라 충돌, 기각.
사용자 서비스로 한 이유: prep 가 `sudo` 없이 `systemctl --user restart rover-base` 로 다시 띄울 수 있게(서비스 파일 머리 주석). 부팅 기동은 linger 로. base 만 띄우는 이유: 센서 · SLAM · Nav2 는 카메라 IMU 캘리브에 로버 정지가 필요해 prep 몫.

## 4. 조치와 효과
- 표시 화면(코드 `display_task.c` 기준 — 지금 저장소): 1 Hz · 우선순위 Low · 스택 384 워드. 줄 1 `IP <주소>`(마지막 수신 15 s 초과면 끝에 `?`, 한 번도 안 왔으면 `IP (no Jetson info)`) / 줄 2 SSID / 줄 3 `BAT 12.05V ROS OK|WAIT|ERR` / 줄 4 `RUN|CMD-TO|STALL|LATCH UP hh:mm:ss`(safety_monitor 상태 우선순위 LATCH > STALL > CMD-TO).
- 효과: 재부팅 · 망 전환 뒤 SSH 주소를 보드에서 읽음(09-29 §2 사용자 확인). 펌웨어 안전 상태(STALL · LATCH · cmd_vel 시간 초과)도 눈으로 보게 됨 — 이 효과를 쓴 기록은 이 시기에 없음.
- 한계: 측정은 '보드가 받았다' 까지(구독 수 · SWD), 화면은 사용자 눈. OLED 갱신이 주행 성능에 주는 영향은 미측정(블로킹 I2C ≈ 50 ms/프레임을 Low 우선순위 태스크에서 — 영향 없을 것으로 추정).

## 5. 내 실수
기록상 틀린 추론은 없다(가설 2 개는 판별로 기각, 정정 § 없음). 운용상 알아 둔 것 2 건(§28.2 끝):
- 전원이 켜진 채 모듈을 바꾸면, 새 모듈이 ACK 하는 한 드라이버가 초기화를 다시 보내지 않아 화면이 안 나온다(재초기화는 전송 실패 때만 — 지금 `display_task.c` 도 `if (!ssd1306_ok())` 일 때만 5 s 마다 `ssd1306_init`). → **모듈 교체는 전원 끄고**.
- 보드 전원을 끄면 Jetson 도 재부팅된다(같은 배터리) → base 재기동 뒤 보드 리셋이 필요할 수 있다(09-29 §2 서비스로 '함께 켜질 때' 는 리셋 불필요가 됨).

## 6. 남은 것
- 주기적 재초기화(전원 켠 채 모듈 교체 대응) — 미구현(09-28 §28.2 '필요하면').
- **Jetson 만** 재부팅되고 보드가 옛 세션을 믿는 경우엔 여전히 보드 리셋 필요(서비스 파일 주석 · 09-11 job240 주석과 같은 이유) — [보드 연결 · micro-ROS 세션](board-link-microros-session.md).
- `display_info_pub.py` 머리 주석의 예시 IP `192.168.0.101` 은 10-15 이후 실제 주소(192.168.0.110)와 다르다 — 예시일 뿐 동작 영향 없음(코드는 `ip route get` 결과를 그대로 보냄).
- 지금 순회 prep(`Docs/tools/prep_fast.sh` 44~48 행)은 base 를 **띄우지 않는다** — 에이전트가 없으면 "job240(전체 절차)으로 기동할 것" 이라며 끝낸다. 서비스 재시작 분기는 dated `job240_clean.sh`(09-29 · 09-30 판) 에만 있다(지금 코드 확인).

## 7. 이후 (09-30 ~) — 포인터
- 09-30 §6: 충전으로 전원이 꺼지면 "Jetson 재부팅 → rover-base 자동 기동 → PC 에서 prep 스크립트 재전송" 이 다음 세션 시작 절차로 굳음 — [09-30 SUMMARY](../debug_log/2026-09-30/SUMMARY.md). 09-30 §3.1 prep 에서 "base 서비스 자동 기동 상태(에이전트 17 h)" 확인.
- 10-01 §8.7: 주행 중 polkitd 평균 ~20 %(최대 69 %)가 OLED 노드의 `nmcli` 탓인지 시험 — 정지 상태 0.1 %, nmcli 20 회 추가해도 0.1 % → **OLED 노드 탓 아님**(측정, `2026-10-01/outputs/j743_polkit.txt`). polkitd 원인은 10-22 §18 에서도 미확인(15.3 %) — [10-01 SUMMARY](../debug_log/2026-10-01/SUMMARY.md).
- 09-29 §13.3: 보드 전원 스위치 = 최후 정지 수단(L1), 복구 = 전원 켬 → 이 서비스 자동 기동 → prep — [온보드 정지 수단 · nav_guard](onboard-stop-nav-guard.md).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| OLED 펌웨어 | Driver 2 · App 2 · micro-ROS 구독 | `firmware/rover_jupiter_fw/App/{drivers,app,microros}/` |
| `display_info_pub.py` | Jetson → 보드 IP · SSID 발행 | `ros2_ws/src/rover_bringup/scripts/` |
| `rover-base.service` · `install_rover_base_service.sh` | base 부팅 자동 기동 | `ros2_ws/src/rover_bringup/{systemd,scripts}/` |
| `job240_clean.sh`(09-29 판) | prep — 서비스가 있으면 재시작 | [`2026-09-29/jobs/`](../debug_log/2026-09-29/jobs/) |
| 진단 펌웨어 | I2C2 스캔 · SWD 명령 1 바이트 | 제거됨(코드 없음) |

## 9. 도구 해설
도구 계보: (없음 — 처음 만든 기능) 09-28 수동 `ros2 launch rover_bringup base.launch.py`(display_info_pub 포함) → 09-29 `rover-base.service`(같은 launch 를 systemd 가 부름) → prep `job240` 이 서비스 재시작으로 분기 → 10 월 `prep_fast.sh` 는 base 를 건드리지 않고 '에이전트 있음' 만 확인.

### display_info_pub.py — 보드 OLED 용 IP · SSID 발행 (Jetson, Python rclpy)
- 실행 위치 · 부른 형태: `base.launch.py` 가 `Node(package='rover_bringup', executable='display_info_pub.py', output='log')` 로 띄움(에이전트 · robot_state_publisher 와 함께). 인자 없음.
- 왜: 무선은 Jetson 에만 있어 보드는 IP 를 모른다(§28).
- 하는 일: 3 s 마다 ① `ip -4 route get 1.1.1.1` 출력에서 `src` 다음 낱말 = 실제로 쓰는 출발 주소, `dev` 다음 = 장치 ② `nmcli -t -f DEVICE,TYPE,CONNECTION device` 에서 그 장치 줄을 찾아 wifi 면 연결 이름, 아니면 장치 이름 ③ `std_msgs/String "IP=<ip>;SSID=<앞 23 자>"` 를 `rover/display_info`(QoS 깊이 1)로 발행. 각 명령은 시간 한도 2 s, 실패하면 빈 문자열. 시작 때 한 번 즉시 발행.
- 출력: 토픽만(로그 없음). 09-28 §28.1 에서 발행값 `IP=192.168.0.101;SSID=WEB_DEV_5G` · 보드 구독 1 확인 — 출력 원문 없음.
- 쓰인 곳: §28.1 · §2 확인. 10-01 §8.7 polkitd 의심 대상(기각).
- 결함: 종료 처리(KeyboardInterrupt) 없음 — launch 종료 때 Traceback 가 날 수 있음(코드 읽기, 관찰 기록 없음). 펌웨어 버퍼(IP 19 · SSID 23 자)에 맞춰 SSID 만 자름.
- 지금 다시: 그대로 운용 중(base 의 일부).

### rover-base.service — base 부팅 자동 기동 (Jetson, systemd 사용자 서비스)
- 실행 위치 · 부른 형태: `~/.config/systemd/user/rover-base.service`, `WantedBy=default.target` + linger 로 로그인 없이 부팅 때 기동. 수동은 `systemctl --user restart rover-base`.
- 왜: §2 — IP 가 가장 필요한 순간(재부팅 직후)에 표시가 비는 구조.
- 하는 일: `FASTRTPS_DEFAULT_PROFILES_FILE` = 설치본 `fastdds_udp_only.xml`([DDS 공유메모리 사고](dds-shm-incident.md)) → `ExecStartPre` ① 최대 90 s 동안 1 s 마다 `/dev/rover` 존재 **그리고** `docker info` 성공을 기다림(사용자 서비스는 시스템 docker.service · udev 에 순서를 걸 수 없어서) — 못 기다리면 실패 ② 남은 `microros_agent` 컨테이너 강제 삭제(이름 충돌 방지) → `ExecStart` = humble · ws setup 뒤 `ros2 launch rover_bringup base.launch.py` → 종료 때 컨테이너 삭제, `KillSignal=SIGINT` · `TimeoutStopSec=20`, `Restart=on-failure` · 5 s. 표준 출력 · 오류를 `/tmp/base.log` 에 덧붙임(prep 가 'session established' 를 세는 파일).
- 출력: `/tmp/base.log`(재부팅마다 사라짐 — 원천 소실). 설치 결과(Linger=yes · enabled · active)는 SUMMARY 수치만.
- 결함 · 한계: `Restart=on-failure` 이므로 수동 `ros2 launch base.launch.py` 를 따로 띄우면 둘이 겹쳐 컨테이너 이름 충돌(→ job240 분기의 이유). 보드 세션 문제(Jetson 만 재부팅)는 못 고침. `/tmp/base.log` 를 append 로 쓰므로 prep 가 먼저 비움(`: > /tmp/base.log`).
- 지금 다시: 운용 중.

### install_rover_base_service.sh — 서비스 설치 (Jetson, bash, 한 번)
- 부른 형태: `bash install_rover_base_service.sh`(설치본 `lib/rover_bringup/` 또는 src).
- 하는 일: `ros2 pkg prefix rover_bringup` 의 `share/rover_bringup/systemd/rover-base.service`(없으면 스크립트 옆 `../systemd/`)를 `~/.config/systemd/user/` 로 복사 → Linger 가 yes 가 아니면 `sudo loginctl enable-linger $USER`(유일한 sudo) → `daemon-reload` · `enable` → `linger: … | enabled: …` 한 줄.
- 출력: 그 한 줄(09-29 10:28 — 원문 없음, SUMMARY 에 결과만).
- 결함: `enable` 만 하고 `start` 는 안 함(설치 직후 기동은 따로 — 09-29 기록은 'active 15 s 뒤' 이므로 별도로 시작한 것으로 추정). 서비스 파일을 고치면 이 스크립트를 다시 돌려야 복사본이 바뀐다(링크가 아니라 복사).
- 지금 다시: 재플래시 · 새 Jetson 때 그대로.

### job240_clean.sh 2 단계(09-29 판) — prep 의 base 처리 (Jetson, bash)
- 하는 일(이 카드 관련 부분, 40~56 행): 에이전트 컨테이너 1 개이고 `/wheel_odom` hz 가 나오거나 'session established' 기록이 있으면 base 재기동 생략(09-16 — 재기동 = 보드 리셋 재요구). 아니면 `systemctl --user is-enabled rover-base` 이면 `/tmp/base.log` 비우고 **서비스 재시작**, 아니면 옛 방식(pkill → `docker rm -f` → `setsid nohup ros2 launch …`) 뒤 12 s 대기.
- 쓰인 곳: 09-29 이후 prep 전부(F0-b · ② 시험 — [F0-b 코스](f0b-course.md)).
- 계보: 10 월 `Docs/tools/prep_fast.sh` 는 이 분기를 빼고 '에이전트 없으면 중단' 으로 바꿈(§6).

### OLED 펌웨어 모듈 (F405, C)
- `ssd1306_driver.[ch]`(Driver): 텍스트 전용 5×7 글꼴 21 자 × 4 줄, 블로킹 `HAL_I2C_Master_Transmit`(프레임 512 B ≈ 50 ms, 시간 한도 200 ms). 실패하면 `s_ok=false` → 태스크가 5 s 마다 재초기화.
- `battery_adc.[ch]`(Driver): ADC1 배터리 전압(분압 4.05)을 microros_task 에서 옮기고 **뮤텍스 보호**(두 태스크가 같은 ADC 사용).
- `display_info.[ch]`(App): 표시 정보 공유 상태(크리티컬 섹션 복사) — IP · SSID · 수신 시각 · micro-ROS 상태(WAIT/OK/ERR).
- `display_task.[ch]`(App): 위 §4 화면. 부팅 500 ms 지연(f1_sanity 의 부팅 I2C 스캔과 안 겹치게).
- `microros_task.c`: `rover/display_info` 구독(best effort, 정적 버퍼 96 B) — 구독 한도 5 중 2 번째라 라이브러리 재빌드 불필요, executor 핸들 1 → 2.
- 빌드(PC, STM32CubeCLT GCC + GnuWin32 make — 메모리 '보드 OLED') · 플래시 `STM32_Programmer_CLI -w … -v -rst`([플래시 안전](flash-safety.md)).

## 10. 용어
- **SSD1306**: 128×32(또는 64) 단색 OLED 컨트롤러. I2C 주소 0x3C, 0xA5 = 'RAM 무시 전체 점등' 시험 명령.
- **linger**(systemd-logind): 사용자가 로그인하지 않아도 그 사용자의 systemd 서비스가 부팅 때 뜨게 하는 설정.
- **micro-ROS 세션**: 보드(클라이언트)가 에이전트와 맺는 연결 — 보드 부팅 때만 맺으므로 에이전트만 재시작하면 보드 리셋이 필요할 수 있다.
