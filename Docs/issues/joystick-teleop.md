# 조이스틱 teleop — DragonRise 패드, 데드맨 없는 안전 모델

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(운용 가능 · 데드맨 버튼 없음 · 패드 신호 끊김 원인 미확인) | 08-31 15:08 ~ 09-01 (이 카드는 09-03 까지만) | [08-31 '조이스틱 teleop + 병진 주행 맵핑 (저녁)'](../debug_log/2026-08-31/SUMMARY.md) | [`config/joy_teleop.yaml`](../../ros2_ws/src/rover_bringup/config/joy_teleop.yaml)(deadzone 0.25 · scale 0.08 → 0.10 / 0.4 → 0.8) · [`launch/joy_teleop.launch.py`](../../ros2_ws/src/rover_bringup/launch/joy_teleop.launch.py) · 설치 `ros-humble-joy-linux` · jetson 사용자 `input` 그룹 | [첫 SLAM 지도](first-slam-map.md)(병진 지도를 이 조종으로 그림) · [배터리 · 전원 운용](battery-power-ops.md)(속도 상향 직후 '모터 약함') · 이후 F1 매핑 프로필(09-30) |

**한 줄**: 지도를 그리려고 USB 게임패드(DragonRise 0079:181c)로 로버를 조종하려 했다. ROS2 기본 `joy_node`(SDL2)로는 메시지 0 → 레거시 조이스틱 장치 `/dev/input/js0` 를 읽는 `joy_linux` 로 바꿔 축은 받았지만, **버튼은 js0 로 아예 들어오지 않아 데드맨(누르고 있어야 움직임) 을 못 쓴다**. 그래서 '스틱 중립(데드존 안) = 정지 + 펌웨어 500 ms watchdog' 를 안전 모델로 삼았고, 그 모델을 무너뜨린 사건 셋(트리거 축 −1.0 로 인한 검사 오탐 · 중복 노드의 묵은 값 · 시작 때 기울인 값)을 고치며 기동 스크립트를 v4 까지 바꿨다. 중립 오프셋(axis1 ≈ −0.18)은 데드존 0.25 로 흡수, 최대 속도는 0.10 m/s · 0.8 rad/s 로 올렸다.

> 읽는 법: 08 월 기록은 § 번호가 없어 '날짜 + 제목 글자' 로 인용. 시각은 `outputs/` 파일의 저장 시각(사용자가 대화에서 옮긴 시각 — 실행 직후로 **추정**). **(10-29 확인)** 은 이 카드를 쓰며 코드 · 파일로 다시 확인한 것.

## 1. 증상
- `joy_node` 를 띄우고 12 s 동안 스틱 · 버튼을 조작했는데 `/joy` 수신 0 개(`job9c`).
- `joy_linux` 로 바꾼 뒤에도 축이 전부 0 이거나(`job9e` · `9f`), 한동안 정상이다가 원시 장치 이벤트까지 0 이 되는 구간이 있었다(`job9n` · `9o`, USB 다시 꽂아 회복).
- 버튼: js0 원시 읽기에서 버튼 INIT 15 개는 오지만 눌림 이벤트 0(`job9k`).
- 안전: 스틱을 놓아도 로버가 움직이는 사건 2 회(16:39 `job9stop`, 17:00 `job10stop` 으로 긴급 정지). SUMMARY 의 '안전 시행착오 ①②③' 으로 정리됨.
- 저녁: 스크립트 주행 때 조이스틱 teleop 이 같이 떠 있으면 `/cmd_vel` 을 두 곳에서 냄(09-01 '부수 발견').

## 2. 흐름 (시간순)
| 시각(08-31) | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 15:22 | 장치 · 패키지 확인 | `/dev/input/js0`(root:input, rw-rw-r--+), event6 'Controller' · event7 'System Control' · event8 'Consumer Control', lsusb `0079:181c DragonRise`, `joy` 설치 · `joy-linux` 없음 · `teleop-twist-joy` 설치 | 장치 인식 OK | [`job9b.sh`](../debug_log/2026-08-31/jobs/job9b.sh) · [`job9b_joystick_check.txt`](../debug_log/2026-08-31/outputs/job9b_joystick_check.txt) |
| 15:23 | `joy_node`(SDL2) 12 s 캡처 | `/joy` hz 없음, 수신 0 | joy_node/장치 점검 | [`job9c.sh`](../debug_log/2026-08-31/jobs/job9c.sh) · [`job9c_joy_data.txt`](../debug_log/2026-08-31/outputs/job9c_joy_data.txt) |
| 15:24 | 진단(스크립트 소실) | joy_node 로그 비어 있음, js0 `crw-rw-r--+`, jetson 은 `input` 그룹 **아님**, js0 직접 2 s 읽기 = 축 INIT 바이트(타입 0x81 · 0x82…) 나옴, `device_id 0` · `device_name ''` | SUMMARY: "joy_node(SDL2)는 인식 못 함" — 원인은 **미확인**(§3 가설 표) | [`job9d_joy_diag.txt`](../debug_log/2026-08-31/outputs/job9d_joy_diag.txt) |
| 15:26 | `joy_linux` 설치 · jetson 을 input 그룹에 추가(다음 로그인부터) · 12 s 캡처 | 'Opened joystick: /dev/input/js0. deadzone 0.05', 19.8 Hz, 수신 238 · 축 8 · 버튼 15, **축 변화 0 · 버튼 0** | 출력 문구는 '입력 정상'(코드가 수신 수만 봄 — §8 결함) | [`job9e.sh`](../debug_log/2026-08-31/jobs/job9e.sh) · [`job9e_joy_linux.txt`](../debug_log/2026-08-31/outputs/job9e_joy_linux.txt) |
| 15:26~15:28 | 재캡처 · 원시 읽기(스크립트 소실) | 9f: 수신 296, 변화 0 / 9g: 출력 머리만 / 9h: 원시 INIT 23 · 조작 264 · 축 0 = 32767, 1 = 7094 | 9h: "장치 정상(joy_linux 설정문제)" — **틀림**(15:29 같은 설정으로 정상, §5 실수 1) | [`job9f_joy_capture2.txt`](../debug_log/2026-08-31/outputs/job9f_joy_capture2.txt) · [`job9g_js0_raw.txt`](../debug_log/2026-08-31/outputs/job9g_js0_raw.txt) · [`job9h_js0_raw2.txt`](../debug_log/2026-08-31/outputs/job9h_js0_raw2.txt) |
| 15:29 | 같은 joy_linux 설정으로 12 s | 수신 636, **축 0~3 −1.00..+1.00**, 4~7 변화 0, 버튼 없음 | 축 정상 | [`job9i.sh`](../debug_log/2026-08-31/jobs/job9i.sh) · [`job9i_joy_final.txt`](../debug_log/2026-08-31/outputs/job9i_joy_final.txt) |
| 15:35 · 15:36 | 데드맨 후보 버튼 찾기 → js0 원시 버튼 | `/joy` 버튼 감지 0 → 원시: 버튼 INIT 15, 눌림 이벤트 **없음** | 이 패드는 버튼이 js0 로 안 옴 → **데드맨 불가** | [`job9j.sh`](../debug_log/2026-08-31/jobs/job9j.sh) · [`job9j_deadman.txt`](../debug_log/2026-08-31/outputs/job9j_deadman.txt) · [`job9k.sh`](../debug_log/2026-08-31/jobs/job9k.sh) · [`job9k_button_raw.txt`](../debug_log/2026-08-31/outputs/job9k_button_raw.txt) |
| 15:38 · 15:39 | teleop 부호 확인(`/cmd_vel_test` 로 돌려 로버 안 움직임) | 9l(소실): linear · angular 전부 0 / 9m: `/joy` 297 · `/cmd_vel_test` 295, axis1 · axis2 변화 0 | '/joy 자체가 안 움직임' | [`job9l_teleop_signcheck.txt`](../debug_log/2026-08-31/outputs/job9l_teleop_signcheck.txt) · [`job9m.sh`](../debug_log/2026-08-31/jobs/job9m.sh) · [`job9m_joy_cmd_trace.txt`](../debug_log/2026-08-31/outputs/job9m_joy_cmd_trace.txt) |
| 15:40 · 15:41 | 원시 js0 와 `/joy` 동시 20 s → 모든 joy 종료 뒤 원시만 8 s | joy PID 2 개(21155 · 21157), 원시 조작 0 · `/joy` 0 → 정리 뒤에도 원시 INIT 23 · 조작 **0** | '장치/케이블/모드 — USB 재연결 권장' | [`job9n.sh`](../debug_log/2026-08-31/jobs/job9n.sh) · [`job9n_raw_vs_joy.txt`](../debug_log/2026-08-31/outputs/job9n_raw_vs_joy.txt) · [`job9o.sh`](../debug_log/2026-08-31/jobs/job9o.sh) · [`job9o_clean_device.txt`](../debug_log/2026-08-31/outputs/job9o_clean_device.txt) |
| 16:12 → 16:36 | 사용자 USB 재연결 → 원시 8 s | js0 생성 16:12:07, Device 007 → 008, 조작 516, 축 1 = 32767 · 2 = −32767 | 장치 정상 → teleop 진행 | [`job9p.sh`](../debug_log/2026-08-31/jobs/job9p.sh) · [`job9p_reconnect.txt`](../debug_log/2026-08-31/outputs/job9p_reconnect.txt) |
| 16:37 | joy_linux(deadzone **0.12**) + teleop → `/cmd_vel_test` 15 s | 'joy_node 2개, teleop 2개', axis1 ±1 → linear.x **±0.080**, axis2 ±1 → angular.z **±0.400**, 4 방향 ✓ | 매핑 · 부호 정상(사용자 실측: axis1 = 전후 양수 전진, axis2 = 좌우 양수 좌회전) | [`job9q.sh`](../debug_log/2026-08-31/jobs/job9q.sh) · [`job9q_sign_verify.txt`](../debug_log/2026-08-31/outputs/job9q_sign_verify.txt) |
| ≈16:38 | 실제 주행(기동 스크립트 판 원문 없음) | 스틱을 놓아도 움직임(**추정** — 바로 뒤 긴급 정지와 원인 진단 문구로 미루어) | — | — |
| 16:39 | **긴급 정지 1** + 중립 값 측정 | 잔존 0, 정지 발행, 실제 속도 ≈ 0, **중립 axis1 = −0.180**(deadzone 0.12) | 좌스틱 중립이 −0.18 로 치우침 → 데드존 0.12 를 넘어 크리프 | [`job9stop.sh`](../debug_log/2026-08-31/jobs/job9stop.sh) · [`job9stop_safety.txt`](../debug_log/2026-08-31/outputs/job9stop_safety.txt) |
| 16:42 | yaml deadzone **0.25** 배포 · 중립 6 s | 잔존 0 → 노드 각 1, 중립 axis1 평균 +0.000, `/cmd_vel_test` 최대 0.0000 | 크리프 없음 | [`job9s.sh`](../debug_log/2026-08-31/jobs/job9s.sh) · [`job9s_neutral_verify.txt`](../debug_log/2026-08-31/outputs/job9s_neutral_verify.txt) |
| 16:46~16:56 | 지도용 깨끗한 출발(보드 리셋 · EKF · slam 재시작) | — | → [첫 SLAM 지도](first-slam-map.md) `job10a~10c` | — |
| 17:00 | **긴급 정지 2** | 잔존 teleop 0 · joy 0 · launch 0, 실제 vx −1.2e−5, `/cmd_vel` 무발행 | 원인 원문 없음. SUMMARY ②: '중복 joy_node 스테일 풀값 사건'(**대응 관계는 추정**) | [`job10stop.sh`](../debug_log/2026-08-31/jobs/job10stop.sh) · [`job10stop.txt`](../debug_log/2026-08-31/outputs/job10stop.txt) |
| 17:03 | 장치 latch 의심 → 원시 js0 중립 5 s | 축 0~3 = 0.0, **축 4 · 5 = −1.0**, 비INIT 이벤트 1 | 출력 문구 '장치가 풀값 latch(패드 문제)' — **틀린 판정**: 4 · 5 는 트리거 축의 쉬는 값. SUMMARY ①: '트리거축(4,5)이 −1.0 라 전체축 체크가 오탐 → 제어축(1,2)만 체크' | [`job10d.sh`](../debug_log/2026-08-31/jobs/job10d.sh) · [`job10d_neutral_latch.txt`](../debug_log/2026-08-31/outputs/job10d_neutral_latch.txt) |
| 17:08 | 제어축 정밀 측정 6 s(yaml 설정의 joy_linux) | axis1 · axis2 평균 · 범위 0.000, '권장 데드존 0.1' | 중립 0 — 단 이 값은 데드존 **적용 뒤** 값이라 오프셋을 못 봄(§8 결함) | [`job10e.sh`](../debug_log/2026-08-31/jobs/job10e.sh) · [`job10e_neutral_precise.txt`](../debug_log/2026-08-31/outputs/job10e_neutral_precise.txt) |
| ≈17:08~17:22 | `job9r_drive` v4 로 기동 → 병진 지도 주행 | (중립 안정 2 s → teleop → `/cmd_vel` 0 게이트 3 s) | 안전 게이트 매번 정상(SUMMARY) | [`job9r_drive.sh`](../debug_log/2026-08-31/jobs/job9r_drive.sh)(실행 출력 원문 없음) |
| 17:22 | teleop 종료 + 지도 저장 | — | — | [`job11.sh`](../debug_log/2026-08-31/jobs/job11.sh)(→ 지도 카드) |
| 마무리 | scale 0.08 → **0.10**, 0.4 → **0.8**(사용자 '최대 기울기 = 최대속도') 배포 | 배포 yaml 확인, 배터리 12.17 V | 다음 세션 적용 | [`job12_speed_change.txt`](../debug_log/2026-08-31/outputs/job12_speed_change.txt)(스크립트 소실) |
| 09-01 12:58 | launch 로 기동(`joy_teleop.launch.py`) | js0 시각 'Jan 1 1970'(재부팅 직후), 노드 2 개, `/joy` 축 0 · `/cmd_vel` 0, map→odom 0 | 주행 가능 | [`job15b_joy.sh`](../debug_log/2026-08-31/jobs/job15b_joy.sh) · [`job15b_joy.txt`](../debug_log/2026-08-31/outputs/job15b_joy.txt) |
| 09-01 '4초 스냅' 조사 | 조이스틱으로 돌려 보며 TF 관찰 | — | 부수: '스크립트 주행 시 joy teleop 이 `/cmd_vel` 이중발행 → 주행 전 joy 종료 필요' | [`job16b_tfdiag.sh`](../debug_log/2026-08-31/jobs/job16b_tfdiag.sh) · [`job16j_cpu.sh`](../debug_log/2026-08-31/jobs/job16j_cpu.sh) |
| 09-01 14:48 | 재기동 | 노드 2 개, 축 0, `/cmd_vel` 0, load 2.62 | 주행 가능 | [`job16m_joy.sh`](../debug_log/2026-08-31/jobs/job16m_joy.sh) · [`job16m_joy.txt`](../debug_log/2026-08-31/outputs/job16m_joy.txt) |
| 09-01 이후 | 스크립트 주행 전 'joy 정리(cmd_vel 단독화)' 를 앞머리에 | — | — | `job17c_validate.sh` · [`job18a_precheck.sh`](../debug_log/2026-08-31/jobs/job18a_precheck.sh) · 09-02 `job20a_boot` · `job31_shutdown` |

이후(09-04 ~): 다음 시기에서 채움 — 펌웨어 최대 직진 0.085 m/s(09-07, yaml 주석에 반영), `profile:=mapping`(09-30 F1, 0.07 · 0.3 → §15 에서 0.085 · 0.38, launch 주석), 온보드 정지 수단(09-29 F0 '정지 수단').

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| `joy_node`(SDL2)가 이 패드를 인식 못 함 | joy_linux 로 바꿔 js0 로 읽기 | joy_linux 는 축을 받음 | 'js0 로는 된다' 는 **확인**. SDL2 가 '인식 못 함' 인지 **권한**(SDL2 는 evdev `/dev/input/event*` 를 열고, event6 은 `crw-rw----+ root input` 인데 jetson 은 input 그룹 아님 — `job9d`) 인지는 **미확인**(input 그룹 추가 뒤 joy_node 재시험 기록 없음) |
| 15:26 축 0 = joy_linux 설정 문제 | 15:29 같은 인자로 다시 | 정상 | **기각** — 사용자 조작 타이밍 또는 패드 상태(§5 실수 1) |
| 패드가 간헐적으로 이벤트를 멈춤 | joy 프로세스 전부 죽이고 원시 8 s(`job9o`) → USB 재연결(`job9p`) | 재연결 전 0, 뒤 516 | 장치 쪽 상태 문제 **지지**. 무엇(패드 모드 · 케이블 · 절전)인지는 **미확인** |
| 버튼은 js0 가 아닌 다른 장치로 옴 | event7 · event8('System Control' · 'Consumer Control')을 읽어 보기 | 안 함 | **미확인** — 데드맨 불가 결론은 'js0 기준' 에서만 확인 |
| 중립인데 움직임 = 스틱 오프셋 | 중립 값(`job9stop`, deadzone 0.12) | axis1 −0.180 | **지지** → deadzone 0.25(16:42 크리프 0) |
| 중립인데 움직임 = 장치 latch | 원시 중립 값(`job10d`) | 제어축 0, 트리거 축만 −1 | **기각**(장치는 정상). 트리거 −1 이 우리 검사를 오탐시킨 것(SUMMARY ①) |
| 중립인데 움직임 = 묵은 노드가 옛 값을 냄 | 노드 · 프로세스 수 세기 | `job9q` '2 개' — 그러나 `pgrep -f` 는 `ros2 run` 래퍼(python)와 실제 노드를 둘 다 센다(`job10d` 주석) | 실제로 중복 노드가 있었는지는 **미확인**. 대응(단일 인스턴스 강제 = `ros2 node list` 로 `/joy_node` 정확히 1 개)은 들어감 |

## 4. 조치와 효과
- **joy_linux + teleop_twist_joy**: `joy_linux_node` 를 `joy_node` 라는 이름으로(`-r __node:=joy_node`, launch 에선 `name='joy_node'`) 띄워 yaml 의 `joy_node:` 블록을 그대로 받게 함. 지금 파일([`joy_teleop.yaml`](../../ros2_ws/src/rover_bringup/config/joy_teleop.yaml)): `dev /dev/input/js0`, `deadzone 0.25`, `autorepeat_rate 20.0`, `coalesce_interval_ms 20`, `axis_linear.x 1` · `scale_linear.x 0.10`, `axis_angular.yaw 2` · `scale_angular.yaw 0.8`, `require_enable_button false`, `enable_turbo_button −1`. 처음 git 반영 `76c08343`(09-02), 이후 주석 한 줄(09-07 펌웨어 최대 0.085)과 launch 의 `profile` 인자(09-30)만 바뀜 **(10-29 확인)**.
- **안전 모델**: 데드맨 버튼 대신 '스틱 놓음 → 데드존 안 → 0 → 정지' + 펌웨어 `/cmd_vel` 500 ms watchdog(CLAUDE.md 안전 원칙) + 기동 게이트(`job9r_drive` v4: 노드 1 개 · 중립 2 s 안정 · teleop 뒤 `/cmd_vel` 3 s 동안 |값| < 0.005).
- **효과**: 16:42 크리프 0, 병진 지도 주행 ≈ 14 분 무사고, 09-01 두 번 기동 정상.
- **한계**:
  - 데드맨 없음 — 조이스틱이 USB 에서 빠지거나 joy_linux 가 마지막 값을 붙잡으면 teleop 은 그 값을 계속 낼 수 있다(teleop_twist_joy 는 /joy 가 끊긴 걸 모름, **추정**). 이 경우 펌웨어 watchdog 은 `/cmd_vel` 이 계속 오므로 안 걸린다.
  - 데드존 0.25 → 스틱 앞 1/4 은 반응 없음(joy_linux 는 데드존 바깥을 다시 0~1 로 늘림 — **추정**, 소스 확인 안 함).
  - 기동 게이트는 `job9r_drive` 에만 있고, 09-01 부터 쓴 `joy_teleop.launch.py`(job15b · job16m)에는 없다 — launch 직후 `/joy` · `/cmd_vel` 1 회 값을 '눈으로' 볼 뿐.
  - 스크립트 · Nav2 주행과 동시에 켜 두면 `/cmd_vel` 이중 발행. 09-01 부터 주행 스크립트 앞머리에서 joy 를 죽이는 것으로 대응(멀티플렉서 `twist_mux` 는 '없음' — `job9a_nav2_check.txt`).
- 권고(08-31 '미해결·다음'): 버튼이 되는 컨트롤러(Xbox/PS)로 데드맨 확보 — 이후 교체 기록은 다음 시기에서 확인.

## 5. 내 실수
### 실수 1 — 축 0 을 'joy_linux 설정 문제' 로 판정
| 칸 | 내용 |
|---|---|
| 하려 한 것 | joy_linux 로 바꾼 뒤 축 입력 확인(`job9e.sh` · 소실된 9f · 9g · 9h) |
| 본 것 | [`job9e_joy_linux.txt`](../debug_log/2026-08-31/outputs/job9e_joy_linux.txt) 수신 238 · 축 변화 0, [`job9f`](../debug_log/2026-08-31/outputs/job9f_joy_capture2.txt) 296 · 0, [`job9h`](../debug_log/2026-08-31/outputs/job9h_js0_raw2.txt) 원시 조작 264 |
| 처음 추론 | 원시는 움직이는데 /joy 는 0 → "장치 정상(joy_linux 설정문제)"(9h 출력 문구) |
| 의심한 이유 | 15:29 `job9i` 가 **같은 인자**(`dev /dev/input/js0 deadzone 0.05 autorepeat 20`)로 축 0~3 전부 ±1 을 받음 — 설정은 바뀌지 않았다 |
| 판별 | `job9i`(설정 그대로 재시험) |
| 결론 | 설정 문제 아님. 9e · 9f 의 0 은 캡처 창 12~15 s 와 사용자 조작이 어긋났거나(9n 의 출력 문구 '이전 0 은 타이밍' 과 같은 해석) 패드가 이벤트를 멈춘 상태(뒤 9o 와 같은 현상)였을 것 — 어느 쪽인지 **미확인** |
| 다음에 알아보는 법 | 사람이 조작해야 하는 캡처는 '같은 창에서 원시 장치 + ROS 토픽' 을 함께 기록(`job9n` 방식)해야 '설정 · 장치 · 타이밍' 을 가를 수 있다. 원시 0 · 토픽 0 이면 장치/타이밍, 원시 ≠ 0 · 토픽 0 이면 노드 문제 |

### 실수 2 — 트리거 축 −1.0 을 '장치 latch' 로 판정 (그리고 그 앞의 '전체 축 중립 검사')
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 시작 때 스틱이 중립인지 검사하고 아니면 기동 중단(기동 스크립트 v1~v3 — 원문 없음, SUMMARY ①), 이어 '풀값 latch' 의심 판별(`job10d.sh`) |
| 본 것 | [`job10d_neutral_latch.txt`](../debug_log/2026-08-31/outputs/job10d_neutral_latch.txt) 축 4 · 5 = −1.0, 나머지 0.0 |
| 처음 추론 | 전체 축 |값| < 문턱을 '중립' 으로 봄 → 4 · 5 때문에 항상 실패. `job10d` 의 판정 문구도 '|값| > 0.5 인 축 = 장치가 풀값 latch(패드 문제)' |
| 의심한 이유 | 4 · 5 는 15:29 `job9i` 에서 조작 중에도 움직이지 않은 축이고, 0 이 아닌 −1 에 고정 — 아날로그 트리거의 '안 누름' 값과 같은 모양 |
| 판별 | 제어에 쓰는 축(1 · 2)만 보도록 바꿈 → `job9r_drive` v4 의 중립 검사(`abs(a1) < 0.15 and abs(a2) < 0.15`) |
| 결론 | 장치 이상 아님 · 검사 범위 오류(SUMMARY ①). 트리거 축이라는 것은 이름(DragonRise 축 배치)으로 확인하지 않았다 — '쉬는 값이 −1 인 축' 이라는 관찰까지만 |
| 다음에 알아보는 법 | 중립 검사 · 안전 게이트는 '쓰는 축만', 쉬는 값은 장치마다 다를 수 있음(트리거 −1). 판정 문구에 결론(latch)을 미리 박아 두지 말고 관찰(값)만 출력 |

### 실수 3 — 데드존 적용 뒤 값으로 '오프셋 0' 을 측정
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 중립 오프셋을 정밀 측정해 필요한 데드존을 계산(`job10e.sh`, 마지막 줄 '관측 최대 오프셋 → 안전 데드존 권장') |
| 본 것 | [`job10e_neutral_precise.txt`](../debug_log/2026-08-31/outputs/job10e_neutral_precise.txt) axis1 · axis2 0.000, '권장 0.1' |
| 의심한 이유(이 카드를 쓰며) | `job10e` 는 joy_linux 를 yaml(`deadzone 0.25`)로 띄우고 `/joy` 를 읽는다. joy_linux 는 데드존을 노드 안에서 적용하므로 `/joy` 에는 이미 0 이 나온다. 같은 패드의 원시 중립은 16:39 에 −0.18(deadzone 0.12 로 읽은 값) |
| 판별 | 코드 읽기 **(10-29 확인)** — 실험으로 다시 잰 것은 없음 |
| 결론 | '권장 데드존 0.1' 은 틀린 권고(따랐다면 −0.18 오프셋으로 크리프 재발). 실제로는 따르지 않고 0.25 유지 — 다행히 결과는 맞았다 |
| 다음에 알아보는 법 | 오프셋 · 잡음 측정은 필터 · 데드존 **앞** 단계(원시 js0 또는 deadzone 0 으로 띄운 노드)에서. 측정 도구가 어떤 파라미터로 노드를 띄웠는지 출력에 함께 적기 |

## 6. 남은 것
- 데드맨 버튼 — 이 패드로는 불가(js0 기준). event7 · 8 확인 또는 다른 컨트롤러.
- SDL2 `joy_node` 실패 원인(권한인지 장치인지) — 미확인. 지금은 joy_linux 로 충분.
- 패드가 이벤트를 멈추는 현상(15:38~16:12) — 원인 미확인, 재발 기록은 다음 시기에서 확인.
- `/joy` 끊김(USB 분리) 때 teleop 이 마지막 값을 계속 내는지 — 미확인(시험 없음). 데드맨이 없으니 확인 가치가 있다.
- `joy_teleop.launch.py` 에 기동 게이트(중립 안정 · `/cmd_vel` 0) 없음.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job9b` · `9c` · (`9d`) · `9e` · (`9f` · `9g` · `9h`) · `9i` | 장치 인식 → joy_node → joy_linux 축 | 08-31 15:22~15:29 |
| `job9j` · `9k` | 데드맨 버튼 찾기 → 버튼 미작동 | 15:35~15:36 |
| (`9l`) · `9m` · `9n` · `9o` · `9p` · `9q` | 부호 · 매핑 · 장치 멈춤 · 재연결 | 15:38~16:37 |
| `9stop` · `9s` | 긴급 정지 1 · 데드존 0.25 | 16:39 · 16:42 |
| `10stop` · `10d` · `10e` | 긴급 정지 2 · latch 의심 · 오프셋 | 17:00~17:08 |
| `9r_drive` (v4) | 지도 주행 기동 게이트 | ≈17:08 |
| (`job12`) · `job15b_joy` · `job16m_joy` | 속도 상향 · launch 기동 | 08-31 마무리 · 09-01 |
| `job16j_cpu` · `job17c_validate` · `job18a_precheck` · `job15c_shutdown` | joy 정리(이중 발행 방지) · 종료 | 09-01 |
| 괄호 = 스크립트 원천 소실(출력만) | | |

## 8. 도구 해설
공통: 전부 Jetson 의 bash(+ python3 heredoc), PC → WSL → sshpass 러너로 `/tmp` 에 올려 실행(러너 원본 소실 — [첫 SLAM 지도 §8 공통](first-slam-map.md#8-도구-해설)). 사람이 스틱을 움직여야 하는 캡처는 화면의 '지금부터 N초!' 안내에 맞춰 사용자가 조작했다. 인자 없음(값은 스크립트 안). 원시 js0 읽기 도구(9k · 9n · 9o · 9p · 10d)는 공통으로 리눅스 joystick API 이벤트 8 바이트 `struct js_event { u32 time; s16 value; u8 type; u8 number; }` 를 `struct.unpack('<IhBB')` 로 풀고, `type & 0x80` = INIT(장치를 열 때 현재 상태를 한 번씩 알려 주는 이벤트), `type & 0x7f` = 1 버튼 · 2 축, 값 범위 −32767 ~ +32767.

### job9b — 장치 · 패키지 확인
- 하는 일: `ls -l /dev/input/js*` · `event*` 마지막 5, `lsusb` 에서 허브 · RealSense · CH340 등 알려진 장치를 빼고 남은 것, 각 event 의 `/sys/class/input/<ev>/device/name` 에서 joy|game|pad|… 이름, `dpkg -l` 로 `ros-humble-joy` · `joy-linux` · `teleop-twist-joy`, `jstest` 유무.
- 출력: [`job9b_joystick_check.txt`](../debug_log/2026-08-31/outputs/job9b_joystick_check.txt).
- 쓰인 곳: 장치 경로 · 패키지 상태(joy-linux 없음 → 9e 에서 설치).
- 지금 다시: 그대로 쓸 수 있음(읽기 전용).

### job9c — joy_node(SDL2) 캡처
- 하는 일: `pkill -f joy_node` → `ros2 run joy joy_node -p device_id:=0 -p deadzone:=0.05 -p autorepeat_rate:=20.0` detach → 4 s → 로그 'opened|error|fail' → `/joy` hz 4 s → 12 s 동안 `/joy` 를 받아 축별 min/max · 눌린 버튼 집합. 축 폭 > 0.1 이면 '← 움직임'.
- 출력: [`job9c_joy_data.txt`](../debug_log/2026-08-31/outputs/job9c_joy_data.txt) — 수신 0.
- 결함: joy_node 가 장치를 못 열어도 '실행중' 으로 나옴(프로세스 생존만 봄).
- 계보: 캡처 골격 → 9e · 9i(joy_linux 판).

### job9d — 진단 (스크립트 원천 소실)
- 출력 [`job9d_joy_diag.txt`](../debug_log/2026-08-31/outputs/job9d_joy_diag.txt) 로 본 내용: joy_node 로그 전체(빈 값), js0 권한 · jetson 그룹(input 없음), `xxd` 로 js0 2 s 직접 읽기(INIT 바이트), `ros2 param list/get /joy_node`.
- 의의: 'js0 는 읽힌다 · jetson 은 input 그룹이 아니다' 두 사실의 출처. 이것으로 joy_linux 전환을 정했다.

### job9e — joy_linux 설치 + 캡처
- 하는 일: `sudo apt-get install -y ros-humble-joy-linux`(비밀번호 `<PW>`), `sudo usermod -aG input jetson`, 기존 joy 종료, `ros2 run joy_linux joy_linux_node -p dev:=/dev/input/js0 -p deadzone:=0.05 -p autorepeat_rate:=20.0` detach → 4 s → 로그 · hz → 12 s 캡처(9c 와 같은 집계).
- 출력: [`job9e_joy_linux.txt`](../debug_log/2026-08-31/outputs/job9e_joy_linux.txt) — 3.3.0 설치, 'Opened joystick', force feedback 경고(무해), 19.77 Hz, 축 변화 0.
- 결함: 마지막 판정 줄이 `n.cnt` (수신 수)만 보고 '입력 정상' 을 출력 — 축이 하나도 안 움직였는데도. 9i 에서 '폭 > 0.2 인 축 또는 버튼이 있어야 ✅' 로 고침.
- 시스템 변경: input 그룹 추가는 영구(되돌린 기록 없음).

### job9f · job9g · job9h — 재캡처 · 원시 읽기 (스크립트 원천 소실)
- 9f: 15 s 캡처 판, 수신 296 · 변화 0, 판정 '❌ … 장치/드라이버 재점검'.
- 9g: 'js0 grab 여부(다른 프로세스 점유?)' 머리 줄과 안내만 남음 — 결과 줄 없음(중간에 멈췄거나 출력이 잘림, **미확인**).
- 9h: 원시 7 s, INIT 23(축 8 + 버튼 15), 조작 264, 축 0 = 32767 · 1 = 7094, 판정 '장치 정상(joy_linux 설정문제)' — §5 실수 1.

### job9i — joy_linux 최종 캡처
- 9e 와 같은 노드 인자, 캡처 12 s, '움직임' 문턱 0.2, 판정이 '움직인 축 또는 버튼' 기준으로 바뀜.
- 출력: [`job9i_joy_final.txt`](../debug_log/2026-08-31/outputs/job9i_joy_final.txt) — 축 0~3 움직임, 버튼 없음.
- 쓰인 곳: '축은 된다' 확정, 축 번호(좌스틱 0 · 1, 우스틱 2 · 3 — **추정**: 안내 문구 '좌스틱 상하→좌우' 순서와 9q 매핑으로).

### job9j — 데드맨 버튼 후보 (ROS 단)
- 하는 일: joy_linux 없으면 띄우고, 10 s 동안 `/joy` 의 버튼별 눌림 횟수, 가장 많이 눌린 버튼 = 데드맨 후보.
- 출력: [`job9j_deadman.txt`](../debug_log/2026-08-31/outputs/job9j_deadman.txt) — '버튼 감지 안됨'.

### job9k — 버튼 원시 읽기
- 하는 일: joy_linux 를 죽이고(원시를 독점하려고) js0 비차단 모드로 10 s, INIT 중 버튼 수, 비INIT 버튼 이벤트 횟수, 참고로 움직인 축 마지막 값.
- 출력: [`job9k_button_raw.txt`](../debug_log/2026-08-31/outputs/job9k_button_raw.txt) — 버튼 INIT 15, 눌림 없음.
- 쓰인 곳: '버튼은 js0 로 안 들어옴(데드맨 불가)' 의 근거 — yaml · launch 주석에 그대로.
- 결함: event7 · event8 은 안 봄(§3).

### job9l — teleop 부호 검증 (스크립트 원천 소실)
- 출력 [`job9l_teleop_signcheck.txt`](../debug_log/2026-08-31/outputs/job9l_teleop_signcheck.txt): 빌드 1 줄 → 노드 `/joy_node` `/teleop_twist_joy_node` → 4 방향 조작 안내 → 수신 271, linear · angular 0. '보드로 안 감' 문구로 보아 teleop 출력을 `/cmd_vel` 이 아닌 곳으로 돌린 판(9m · 9q 와 같이 `/cmd_vel_test`, **추정**).

### job9m — joy → cmd_vel 추적
- 하는 일: 노드 목록, `/joy` 구독자 수, 15 s 동안 `/joy` 의 axes[1] · axes[2] 와 `/cmd_vel_test` 의 linear.x · angular.z 범위. 판정: /joy 가 0.2 넘게 안 변함 → '/joy 자체가 안 움직임', /joy 는 변하는데 cmd 는 0.01 미만 → 'teleop 설정 문제', 둘 다 → '정상 매핑'.
- 출력: [`job9m_joy_cmd_trace.txt`](../debug_log/2026-08-31/outputs/job9m_joy_cmd_trace.txt).
- 의의: '어느 단계에서 끊겼나' 를 가르는 첫 2 단 비교. 다음 9n 에서 원시까지 3 단.

### job9n — 원시 js0 vs /joy 동시 20 s
- 하는 일: joy_linux PID 출력('여럿이면 충돌'), 별도 스레드로 js0 원시 비INIT 축 이벤트 수, 동시에 `/joy` 에서 |값| > 0.2 축. 판정 셋: 원시 > 0 · /joy 0 → 'joy_node 가 못 읽음', 원시 0 → '조작 안됨(타이밍) 또는 장치', 둘 다 → 정상.
- 출력: [`job9n_raw_vs_joy.txt`](../debug_log/2026-08-31/outputs/job9n_raw_vs_joy.txt) — PID 21155 · 21157, 원시 0 · /joy 385 개(값 0).
- 결함: PID 둘을 '충돌' 로 읽게 하는 문구 — `ros2 run` 은 파이썬 래퍼 프로세스와 실제 노드 프로세스 둘을 만들고, 둘 다 명령줄에 `joy_linux` 가 있다(PID 가 붙어 있는 것도 부모 · 자식으로 보임, **추정**). 정확한 수는 `ros2 node list` 로(9r v4 가 그렇게 함).
- 계보: 3 단 비교(원시 · /joy · cmd) 방식 — §5 실수 1 의 '다음에 알아보는 법'.

### job9o — 깨끗한 원시 읽기
- 하는 일: joy_linux · joy_node · teleop `pkill -9` → 남은 수 → `lsusb | grep 0079:181c` · js0 권한 · `sudo fuser -v /dev/input/js0`(점유 프로세스) → 8 s 원시.
- 출력: [`job9o_clean_device.txt`](../debug_log/2026-08-31/outputs/job9o_clean_device.txt) — 남은 0, 연결됨, INIT 23, 조작 0 → 'USB 재연결 권장'.
- 쓰인 곳: '소프트웨어를 다 치워도 장치가 안 보낸다' → 사용자 재연결.

### job9p — 재연결 확인
- 9o 와 같은 원시 읽기 + `stat -c %y /dev/input/js0`(재연결하면 장치 노드가 새로 생겨 시각이 갱신됨).
- 출력: [`job9p_reconnect.txt`](../debug_log/2026-08-31/outputs/job9p_reconnect.txt) — Device 008, 16:12:07, 조작 516.

### job9q — 매핑 · 부호 검증
- 하는 일: 전부 `pkill -9` → joy_linux(deadzone **0.12**) → teleop_node(`--params-file …/joy_teleop.yaml`, `-r /cmd_vel:=/cmd_vel_test`) → 프로세스 수 → 15 s 동안 /joy axes[1] · [2] 와 `/cmd_vel_test` 최소 · 최대, 4 방향(|값| > 0.02) 체크.
- 출력: [`job9q_sign_verify.txt`](../debug_log/2026-08-31/outputs/job9q_sign_verify.txt) — ±0.080 · ±0.400, 4 방향 ✓, '2개 · 2개'.
- 쓰인 곳: yaml 의 axis 번호 · scale(0.08 · 0.4) 확정, '사용자 실측 매핑'.
- 결함: '각 1 이어야' 의 2 개는 래퍼 포함 수(job9n 결함과 같음). joy_linux 를 yaml 이 아닌 명령줄 deadzone 0.12 로 띄움 — yaml 과 실제 값이 갈린 상태였다(16:39 크리프의 배경).

### job9r_drive — 지도 주행 기동 게이트 (v4) ★
- 왜: 데드맨이 없으니 '기동 순간' 이 가장 위험하다 — 시작 때 스틱이 기울어 있거나, 묵은 노드가 옛 값을 내거나, 검사가 오탐해 주행을 못 하는 사건을 겪은 뒤.
- 하는 일(단계 번호는 스크립트 그대로):
  1. 스테일 제거: `pkill -9 -f teleop` · `joy_linux` 를 최대 5 회, `pgrep -f 'teleop_node|joy_linux_node'` 가 0 이 될 때까지 → 2 s.
  2. joy_linux 단일 기동: `--params-file joy_teleop.yaml -r __node:=joy_node` → 4 s → `ros2 node list | grep -c '^/joy_node$'` 가 정확히 1 이 아니면 joy 를 죽이고 종료(exit 1).
  3. **중립 안정 대기**: 최대 25 s 동안 `/joy` 를 받아 `|axes[1]| < 0.15 and |axes[2]| < 0.15` 가 **2.0 s 연속**이면 OK. 아니면 'TIMEOUT a1 · a2' 출력 · joy 종료 · exit 1.
  4. teleop 기동(`--params-file`, `/cmd_vel` 그대로 = 보드로 감) → 3 s.
  5. **`/cmd_vel` = 0 게이트**: 3 s 동안 `/cmd_vel` 의 max(|linear.x|, |angular.z|) < 0.005 이면 OK, 아니면 teleop · joy 강제 종료 · exit 1.
  6. '주행 시작 가능!' 출력. 이후 사람이 조종.
- 출력: 실행 출력 원문 없음(대화에만).
- 계보(SUMMARY '안전 시행착오' 로 재구성, v1~v3 원문 없음 — **추정**):
  - v1: 기동 뒤 '전체 축' 중립 검사 → 트리거 4 · 5 = −1 로 늘 실패(①).
  - v2: (단일 인스턴스 강제 + 게이트 실패 시 강제 종료 추가 — ②, 묵은 노드가 풀값을 낸 사건 뒤).
  - v3: 시작 때 '지금 값' 한 번 검사 → 사용자가 스틱을 잡고 있던 순간이 걸림(③ '시작 시 스틱 조작값 latch').
  - **v4(이것)**: 제어축(1 · 2)만, '2 s 연속 중립' 을 기다림 + 노드 수는 `ros2 node list` 로.
  - 후속: 09-01 부터는 `joy_teleop.launch.py`(게이트 없음, §4 한계). 10 월엔 조이스틱 대신 웹 · 장소 명령(F2.5) 쪽으로 감(다음 시기).
- 결함: 중립 문턱 0.15 는 joy_linux 데드존(0.25) 적용 뒤 값이라 거의 항상 0 → 사실상 '스틱을 놓았나' 만 본다(그게 목적이긴 함). 게이트 3 s 는 teleop 이 /joy 를 받기 전이면 `/cmd_vel` 을 하나도 안 받아 `mx = 0` → OK 가 된다(무발행도 통과).
- 지금 다시: 조이스틱을 쓸 때 launch 대신 이걸 쓰는 편이 안전. 토픽 · 파일 경로는 지금도 같다.

### job9s — 데드존 0.25 배포 · 중립 검증
- 하는 일: `/tmp/rover_src` 복사 · 빌드 → 전부 `pkill -9` → 남은 수 → joy_linux(yaml) · teleop(→ `/cmd_vel_test`) → 노드 목록 → '손 떼주세요' 6 s 동안 /joy axis1 평균 · `/cmd_vel_test` 최대 |값|, 둘 다 0.005 미만이면 '✅ 크리프 없음'.
- 출력: [`job9s_neutral_verify.txt`](../debug_log/2026-08-31/outputs/job9s_neutral_verify.txt).
- 결함: 실수 3 과 같은 구조(데드존 뒤 값) — 다만 여기 질문은 '최종 cmd 가 0 인가' 라서 목적에는 맞다.

### job9stop — 긴급 정지 1 + 중립 원인 진단
- 하는 일: teleop · joy 전부 `pkill -9` → 남은 수 → `ros2 topic pub -t 10 -r 10 -w 1 /cmd_vel '{}'` → `/odometry/filtered` twist(x · z) → joy_linux 를 **deadzone 0.12** 로 다시 띄워 4 s 동안 마지막 /joy 축 전부 → 'axis1 · axis2 (0 근처여야)' → joy 종료.
- 출력: [`job9stop_safety.txt`](../debug_log/2026-08-31/outputs/job9stop_safety.txt) — axis1 −0.180.
- 쓰인 곳: yaml 주석 '좌스틱 중립이 axis1 ≈ −0.18 로 치우침(실측 2026-08-31). 데드존 0.25'. TODO 'jscal 캘리브레이션 또는 중립 정상인 조이스틱'.
- 결함: '마지막 메시지 1 개' 값이라 중립 흔들림 범위는 모름.

### job10stop — 긴급 정지 2
- 하는 일: teleop · joy_linux · joy_node · joy_teleop(launch) `pkill -9` → 남은 수 3 종 → 빈 `/cmd_vel` 15 회 → 실제 속도 → `/cmd_vel` 현재값(무발행이면 빈 칸).
- 출력: [`job10stop.txt`](../debug_log/2026-08-31/outputs/job10stop.txt) — 모두 0.
- 결함: '정지 발행됨' 줄이 출력에 없다 — `timeout 3` 이 `-t 15 -r 10`(1.5 s + 연결 대기 `-w 1`)보다 먼저 끝나 `&&` 뒤가 안 찍힌 것(**추정**). 정지 지령이 실제로 몇 번 나갔는지 모름. 실제 속도 ≈ 0 은 확인됨.

### job10d — '풀값 latch' 의심 판별
- 하는 일: joy/teleop `pkill -9` → ros2 node 에 joy 몇 개 · 프로세스(래퍼 포함) → 원시 js0 5 s, 축별 마지막 값(INIT 포함)을 32767 로 나눠 출력, 비INIT 이벤트 수, |원시| > 16000(0.5) 인 축 목록 → '장치가 풀값 latch' 경고.
- 출력: [`job10d_neutral_latch.txt`](../debug_log/2026-08-31/outputs/job10d_neutral_latch.txt).
- 결함: §5 실수 2(판정 문구). INIT 값까지 '마지막 값' 에 넣어 '장치를 연 순간의 상태' 를 그대로 보여 준 점은 좋다.

### job10e — 제어축 정밀 측정
- 하는 일: joy/teleop 종료 → 직전 `/tmp/teleop.log` 마지막 3 줄(scale 확인 — 'Linear axis x on 1 at scale 0.08', 'Angular axis yaw on 2 at scale 0.4') → joy_linux(yaml, deadzone 0.25) → 6 s 동안 axis1 · axis2 평균 · 범위 → 데드존 0.25 를 한 번 더 적용한 최대 → '관측 최대 오프셋 + 0.1 = 권장 데드존(최대 0.4)'.
- 출력: [`job10e_neutral_precise.txt`](../debug_log/2026-08-31/outputs/job10e_neutral_precise.txt).
- 결함: §5 실수 3 — 이미 데드존을 지난 값으로 오프셋을 잼.
- 지금 다시: 원시 js0 값으로 바꾸면 쓸 만함.

### job12 — 속도 상향 (스크립트 원천 소실)
- 출력 [`job12_speed_change.txt`](../debug_log/2026-08-31/outputs/job12_speed_change.txt): 빌드 → 배포된 yaml 의 `x: 0.10 # 로버 최대 = 펌웨어 MAX_LINEAR_SPEED_MPS 0.100` · `yaw: 0.8 # §3 상한. ⚠ 고속 회전은 슬립↑·맵품질↓` → teleop/joy 정리 → 배터리 12.17 V.
- 근거: 09-01 펌웨어 소스 확인 — V_MAX 0.100 m/s, 각속도 명시 상한 없음 → 암묵 0.816 rad/s(= 0.100 / 반 게이지 0.1225)([08-31 파일 09-01 '결과 (수치)'](../debug_log/2026-08-31/SUMMARY.md)). '§3 상한' 은 당시 문서의 0.8 rad/s 를 가리킴(어느 문서 §3 인지 원문 확인 못 함 — **미확인**).
- 이후: 09-07 펌웨어 최대 0.085 m/s 로 바뀜 → yaml 0.10 은 펌웨어가 잘라 실효 0.085(지금 yaml 주석).

### job15b_joy — launch 기동 (09-01)
- 하는 일: js0 존재 → joy_linux · teleop_twist_joy · joy_teleop `pkill -f` → `ros2 launch rover_bringup joy_teleop.launch.py` detach → 6 s → 노드 · `/odometry/filtered` hz → `/joy` 1 회 axes 앞부분 → `/cmd_vel` 1 회 → map→odom.
- 출력: [`job15b_joy.txt`](../debug_log/2026-08-31/outputs/job15b_joy.txt).
- 차이(9r v4 대비): 게이트 없음 — 값을 보여 주기만. `/cmd_vel` 1 회 수신에 0 이 나온 것은 teleop 이 중립에서도 0 을 계속 낸다는 뜻(autorepeat 20 Hz).
- 결함: `pkill -f` 가 SIGTERM 이라 9 계열(`-9`)보다 약함, 남은 수 확인 없음.

### job16m_joy — launch 재기동 (09-01 14:48)
- job15b 의 축약판 + `/proc/loadavg`(foxglove 부하 조사 중이라).
- 출력: [`job16m_joy.txt`](../debug_log/2026-08-31/outputs/job16m_joy.txt) — 첫 줄 'wsl: …' 은 PC 쪽 WSL 경고가 깨진 글자로 섞인 것(무관).

### joy 정리가 들어간 도구 (09-01 '이중 발행' 대응)
- [`job16b_tfdiag.sh`](../debug_log/2026-08-31/jobs/job16b_tfdiag.sh): TF 진단 중 조이스틱으로 돌려 보려고 joy_teleop.launch 를 다시 띄움(18~21 행).
- [`job16j_cpu.sh`](../debug_log/2026-08-31/jobs/job16j_cpu.sh) · `job17c_validate.sh` · [`job18a_precheck.sh`](../debug_log/2026-08-31/jobs/job18a_precheck.sh): 앞머리 `pkill -f joy_linux; pkill -f teleop_twist_joy` — 주석 '(cmd_vel 이중발행 제거)' · '(cmd_vel 단독화)'. 이 규칙의 근거 원문(두 발행자가 동시에 있던 측정)은 남아 있지 않다 — SUMMARY 09-01 '부수 발견' 한 줄뿐.
- [`job15c_shutdown.sh`](../debug_log/2026-08-31/jobs/job15c_shutdown.sh): 종료 목록 맨 앞에 joy_teleop · joy_linux · teleop. 출력 [`job15c_shutdown.txt`](../debug_log/2026-08-31/outputs/job15c_shutdown.txt) 의 '남은 노드' 에 `/joy_node` 가 남음 — 2 s 만에 `ros2 node list` 를 읽어 그래프 캐시(데몬)가 아직 안 지운 것인지 실제로 살아 있었는지 **미확인**.

### 설정 · launch
- [`config/joy_teleop.yaml`](../../ros2_ws/src/rover_bringup/config/joy_teleop.yaml) — §4 의 값. 주석에 매핑 · 데드존 근거(−0.18) · 데드맨 불가 · TODO(production) jscal.
- [`launch/joy_teleop.launch.py`](../../ros2_ws/src/rover_bringup/launch/joy_teleop.launch.py) — `joy_linux_node`(name `joy_node`) + `teleop_node`(name `teleop_twist_joy_node`), 둘 다 같은 yaml. 09-30 에 `profile:=normal|mapping` 추가(mapping = 0.085 · 0.38, 다음 시기).

## 9. 용어
- **joy_linux / js0**: 리눅스에는 게임패드를 읽는 길이 둘 있다. 오래된 joystick API(`/dev/input/js0`, 8 바이트 이벤트 — 축 · 버튼만)와 evdev(`/dev/input/eventN`, 모든 입력 장치 공통). ROS2 Humble 의 `joy` 패키지(`joy_node`)는 SDL2 로 evdev 쪽을, `joy_linux` 패키지(`joy_linux_node`)는 js0 를 읽는다. 둘 다 `sensor_msgs/Joy`(`axes[]` −1~1, `buttons[]` 0/1)를 `/joy` 로 낸다.
- **teleop_twist_joy**: `/joy` → `/cmd_vel`(Twist) 변환 노드. `linear.x = scale_linear.x × axes[axis_linear.x]`, `angular.z = scale_angular.yaw × axes[axis_angular.yaw]`. `require_enable_button: true` 면 지정 버튼을 누르고 있을 때만 낸다(= 데드맨).
- **deadzone(데드존)**: 스틱 중심 근처 이 크기 이하의 값을 0 으로 보는 범위. 스틱은 놓아도 정확히 0 으로 안 돌아오므로(이 패드 −0.18) 데드존이 그보다 커야 '놓으면 정지' 가 된다. joy_linux 는 노드 안에서 적용 — `/joy` 에는 이미 적용된 값이 나온다.
- **deadman(데드맨)**: 조종자가 버튼을 '누르고 있는 동안만' 움직이는 안전 방식. 손을 떼거나 쓰러지면 즉시 멈춘다. 이 패드는 버튼이 안 와서 못 씀 → '스틱 놓음 = 0' 으로 대신했고, 이것은 USB 분리 · 노드 멈춤에 약하다.
- **INIT 이벤트**: js0 를 열 때 장치가 축 · 버튼마다 현재 상태를 한 번씩 보내는 이벤트(`type & 0x80`). 버튼 INIT 15 = 버튼 15 개가 '있다' 는 뜻일 뿐 눌림과는 무관.
- **트리거 축**: 아날로그 트리거(L2/R2 류)는 축으로 오고 안 눌렀을 때 −1(또는 +1)이 쉬는 값인 경우가 많다. 이 패드 축 4 · 5 가 −1.0 이었다(트리거라는 것은 **추정**).
- **`ros2 run` 래퍼**: `ros2 run pkg exe` 는 파이썬 프로세스가 실제 실행 파일을 자식으로 띄운다. `pgrep -f <이름>` 은 둘 다 세므로 노드 하나가 '2 개' 로 보인다. 노드 수는 `ros2 node list` 로 센다.
- **`/cmd_vel` 이중 발행**: 두 노드가 같은 토픽에 Twist 를 내면 보드는 마지막에 온 것을 따른다 — 스크립트가 0 을 내도 조이스틱 teleop 의 값(또는 그 반대)이 섞인다. 멀티플렉서(`twist_mux`)가 우선순위로 고르지만 이 시기엔 설치 안 됨.
- **펌웨어 watchdog**: 보드가 `/cmd_vel` 을 500 ms 못 받으면 모터를 세운다(CLAUDE.md 안전 원칙). 발행이 '멈췄을 때' 만 작동 — 잘못된 값이 계속 오면 못 막는다.
