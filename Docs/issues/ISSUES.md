# 문제 대장 (2026-10-29 시작)

날짜별 기록(`Docs/debug_log/<날짜>/SUMMARY.md`)을 **문제별로 다시 묶은 길잡이**. 요약본이 아니라, 문제 하나가 여러 날에 흩어진 것을
'증상 → 가설 → 판별 실험 → 조치 → 남은 것' 순서로 따라가며 각 칸마다 원래 날짜의 § 와 데이터 파일로 들어가게 한다.

- 카드 한 장 = 문제 한 줄기. 형식은 아래 '카드 형식'. 주장마다 날짜 · § · 데이터(outputs · jobs · bag) 위치를 단다.
- 상태: **해결**(원인 확인 + 조치 + 재발 0 확인) · **우회**(증상 차단, 원인 남음) · **조사 중** · **보류**(사용자 결정 · 기능 한계).
- 자동 색인(손으로 고치지 않음, `python Docs/tools/anal_record_index.py` 로 다시 만듦): [§ 제목 색인](index/SECTIONS.md) · [실험 이름 대장](index/RUNS.md) · [도구 사전](index/JOBS.md).
- 작성 순서(10-29 사용자 결정): 최근 2 장으로 형식 시범 → 확인 뒤 **오래된 것부터** 시기별(08 월 펌웨어 · 통신 → 09 월 Nav2 · STVL · 데크 → Phase N → F0~F2 → 10 월). 뒤 카드가 앞 카드와 이어지면 링크만 덧붙인다.

## 카드 목록
시기 순(처음 본 날). 상태는 그 카드가 채워진 시기 기준 — '이후' 칸이 남은 카드는 뒤 시기를 읽으며 갱신한다.

### 1 기 08-26 ~ 09-03 (기동 · 센서 · 첫 지도 · Nav2 첫 구축) — 10-29 작성
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [보드 연결 · micro-ROS 세션](board-link-microros-session.md) | 우회 | CH340 → udev `/dev/rover`, Docker 에이전트. 세션은 보드 부팅 때만 맺어져 에이전트 재시작 · 플래시 뒤 보드 리셋 필요(예외 사례 있음 — 카드 참조) |
| [자이로 소스: 보드 IMU → D455f](gyro-source-d455f.md) | 해결 | 보드 ICM-20948 자이로 무반응(손 회전 ≤ 0.041 rad/s) → 카메라 IMU. HID 커널 모듈 빌드 · EKF 가 *_config 를 센서 프레임으로 읽는 함정 |
| [휠 오도 스케일 · 회전 슬립](wheel-odom-scale-slip.md) | 직진 해결 · 회전 보류(2 기) | 줄자 ×1.022 는 측정 실수, 실제는 휠 27.8 % 과대 → VX_SCALE 0.783(3 회 ±0.25 %). '슬립 0.46' 의 대부분이 스케일 오류 |
| [좌/우 트랙 비대칭(간헐)](track-asymmetry.md) | 보류 | 평소 0.1~0.4 °/m · 6 회 중 1 회 1.9 °/m. 휠별 텔레메트리가 없어 원인 판별 불가 |
| [스크립트 주행 안전 가드](script-drive-guards.md) | 부분 해결 | 전역 최소 여유 → 경로 밴드(직진) · 스윕 반경(회전) · 0.5 백분위로 진화 |
| [라이다 방향(yaw)](lidar-yaw-alignment.md) | 해결 | yaw = π. 오락가락의 원인은 Foxglove fixed frame = map(SLAM 없음). 카메라 y 부호는 보류 |
| [회전 중 스캔 끌림](scan-drag-deskew.md) | 해결(지연 성분) | 스윕 시작 stamp → restamp(−48 ms) → deskew(9 ms). '밀림 각' 은 지연 × 지령 속도 계산값(실측 아님) |
| [Foxglove 4 초 스냅](foxglove-snap-cpu.md) | 우회 | 로봇 위치 추정 문제가 아니라 foxglove_bridge 과부하로 /tf 표시 지연 → 재시작 + 화이트리스트 |
| [첫 SLAM 지도](first-slam-map.md) | 해결 | 360° 제자리 지도 · 조이스틱 주행 지도. '복귀 0.2 cm' 는 EKF 값이라 증명 못 됨(정정) |
| [조이스틱 조작](joystick-teleop.md) | 우회 | joy_node 불인식 → joy_linux, 버튼 없음 → 데드맨 없음, 안전 게이트 시행착오 |
| [Nav2 첫 구축](nav2-first-setup.md) | 해결(기동) | 진행 검사기가 회전을 못 봄 · inflation · 첫 벤치마크 RPP 0/1 · MPPI 0/2 |
| [기동 데드밴드](start-deadband.md) | 우회 → 기계적 층 소멸(2 기, 20 kHz) | RPP 각가속 클램프 × 정지마찰 데드락, 펌웨어 정지 문턱 0.010 도 원인 → 최소 휠 속도 0.020 승격 |
| [스톨 보호 래치](stall-latch.md) | 해결(2 기, 09-07 받침대) | 승격 0.020 이 스톨 판정에 걸려 로버 전체 잠김 → duty ≥ 0.60 판정 · 1.5 s 자동 복구 · 10 s 3 회 래치 |
| [라이다 근접 사각 · 벽 접촉](near-wall-blindspot.md) | 우회(완화) | 최소 거리 0.2 m + 장착 위치 → 앞 약 10 cm 사각, 회전 중 접촉 → padding 0.05 |
| [Jetson Wi-Fi](jetson-wifi-link.md) | 우회 | 회전 중 끊김 → 실행을 Jetson 안에서 분리(detach), 절전 끔. 원인 미확정(이후 재발) |
| [배터리 · 전원 운용](battery-power-ops.md) | 보류 | 방전으로 Jetson 다운 반복, 운용 규칙으로 대응 |

### 2 기 09-07 ~ 09-11 (모터 · 통신 · 첫 회피 주행 · 코스트맵) — 10-30 작성 · 1 기 카드 6 장도 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [모터 PWM 50 Hz 오적용](motor-pwm-50hz.md) | 해결 | 새 모터를 12 일 동안 구모터 주파수로 구동 — 회전자 떨림 펄스가 가짜 속도가 되어 스톨 감지 불가 → 20 kHz |
| [컨트롤러 선택 RPP vs MPPI](controller-rpp-vs-mppi.md) | 결정 → 이후 뒤집힘 | 09-07 RPP 채택(MPPI 벽 접촉) · RPP 조향 다듬기. 09-07 'MPPI 진동' 은 실제론 6~7 mm/s 지령이 펌웨어에서 버려진 것 |
| [정체 감시 stuck_monitor](stuck-monitor.md) | 작동 | 지령 대비 실제 이동. ⚠ 09-29 '자이로 우선' 수정은 use_gyro 기본 끔이라 실주행에서 꺼져 있음(10-29 §8) |
| [카메라 깊이 장애물](depth-obstacle-costmap.md) | 우회 | 수평 띠 → VoxelLayer → STVL. 상자 소실 = 거리에 따라 보이는 면 · mark_threshold · '소거' 가 아니라 '마킹 중단' |
| [inflation · padding · 충돌검사 지평](inflation-padding-roles.md) | 원리 정리 | padding = 통과 여부, inflation = 여유 선호. 상자 관통의 원인은 충돌검사 지평 0.12 m |
| [micro-ROS 보드율 회귀](microros-baud-regression.md) | 우회 | 2 Mbps 에서 /wheel_odom 이 수십 초씩 사라져 EKF 8.5 m 발산 → 460 800. 08-27 엔 같은 설정이 됐으므로 회귀(원인 미확정) |
| [DDS 공유메모리 사고](dds-shm-incident.md) | 우회 | 살아 있는 노드가 그래프에서 사라짐 → UDP 전용. 중첩 프로세스 |
| ['후진하고 멈췄다' — CPU · 위치 추정 정지](cpu-load-stalls.md) | 우회 | 위치 추정 정지와 CPU 부족, 원인 판정 두 번 정정 |
| [회피 주행 계측 결함](avoid-run-metrics.md) | 부분 해결 | 상자를 한 번만 고정 · 벽을 상자로 봄(클러스터링 없는 중앙값) 등 결함 6 건 |
| [코스트맵이 상자를 지움 — 클리어 · 감쇠](costmap-clear-recovery.md) | 해결 | 원인 = 복구 BT 의 ClearEntireCostmap → ClearCostmapExceptRegion. 09-10 감쇠 결정 취소 |
| [통과 폭 판단 도구와 '환각'](passage-width-analysis.md) | 조사 중 | 원형 근사 · 내접 반경 이중 계산 등 도구 결함 10 번까지. 통로는 1.2 m 가 아니라 0.6 m |
| [behavior_server BackUp](behavior-server-backup.md) | 해결 | BackUp 이 map 프레임으로 충돌 검사해 0.0 s 에 실패 · 첫 1 s 엇갈린 지령 |

### 3 기 09-14 ~ 09-18 (상자 옆 통로 · MPPI 복귀 · 데크 yaw) — 10-30 작성 · 앞 카드 13 장도 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [깊이 점군 아티팩트 · depth_relay](depth-relay-artifacts.md) | 해결 → 이후 대체 | 정면 바닥 근거리 · 상자 실루엣 비산점 · 25 % 프레임 바닥 한 점 → 릴레이 필터 · 시간 지속성. '전역 흔들림' 은 관찰자(사람) |
| [전역 계획기 NavFn vs Smac](global-planner-choice.md) | 보류 → 이후 채택(10-27) | 09-14 정지 A/B · sm1 — 계획기 교체로는 같은 자리 정체가 안 풀림 |
| [라이다 '고정점'](lidar-fixed-point.md) | 해결(없음) | 로버를 따라다니는 점은 bag 에 없음 |
| [MPPI 상자 옆 통로 튜닝 mp1~mp11](mppi-passage-tuning.md) | 해결(이 코스 3/3) | 지평 0.13 m 에서 경로 크리틱 안 켜짐 · 복셀 필터 · inflation 0.70 + SmoothPath · PathFollow 당근 · 목표 옆 정지 = 펌웨어 문턱 |
| [MPPI 조향 흔들림 · temperature](mppi-wobble-temperature.md) | 보류 | 'softmax 표본 부족' 가설로 0.3 을 냈으나 mp12 에서 안 줄어 0.15 복귀. 시뮬 구동계 모형이 틀렸을 가능성(바퀴 포화) |
| [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md) | 도구 카드 | job355 → 410 → 419(Humble 1.1.20 동작) → 452(CostCritic) — 무엇을 흉내 내고 어디까지 믿을 수 있나 |
| [ObstaclesCritic → CostCritic](obstacles-to-costcritic.md) | 해결(09-21 채택) | 상자를 크게 도는 이유 분해 · ObstaclesCritic 은 17.5 cm 안 여유를 구분 못 함 |
| [플래시 안전](flash-safety.md) | 우회(절차) | 리셋 없이 플래시 → MCU 정지 상태에서 로버가 스스로 회전 |
| [SLAM Fast DDS 데드락](slam-dds-deadlock.md) | 우회 + 수정판 | slam_toolbox 가 그래프에서 사라짐 — gdb 로 Fast DDS 2.6.11 락 순서 역전 → 2.6.12 |
| [로그 · 산출물 정리 보류](storage-housekeeping.md) | 보류 | 'GB 단위가 아니면 정리 미룸' (bags 는 지금 약 4.4 GiB) |
| [센서 데크 yaw −2.68°](sensor-deck-yaw.md) | 해결(라이다) | 로컬 코스트맵 상자가 다가오던 원인. 벽 옆면 정지 측정 → URDF 보정. 카메라 yaw 는 보정 뒤 미검증 |
| [간헐 중단 dy1~dy6](intermittent-abort-dy.md) | 부분 해결 | 보정 뒤 6 회 — 출발 자리 물체 · 게이트 수정 · 여유 ≥ 5 cm 불합격 |

### 10 월 (형식 시범)
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [SLAM map→odom 시각 정체](slam-stamp-freeze.md) | 우회 | 위치 추정 정합(LinkNearChains 64 %) 동안 stamp 가 멈춰 nav2 TF 실패 → timeout 1.5 로 실패 0, 정합 비용은 남음 |
| [세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md) | 조사 중 | 주행 뒤 정지에서만 odom yaw 가 돌고 SLAM 은 안 고침 → 경로 없음 · 7° 틀린 출발. 출발 전 검사 구현(미배포) |

## 카드 형식
1. 머리 표 — 상태 · 기간 · 처음 본 곳 · 바꾼 파일 · 관련 문제
2. 한 줄 — 무엇이 문제였고 지금 어디까지 왔나
3. 증상 — 사용자 · 기록이 처음 본 모습(수치 · 그림)
4. 흐름(시간순 표) — 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터
5. 가설과 판별 — 가설 | 판별 | 결과 | 판정(지지 · 기각 · 미확인)
6. 조치와 효과 — 무엇을 바꿨나, 전후 수치, 한계
7. 내 실수 — 실수 칸 형식 기록으로 가는 링크
8. 남은 것
9. 실험 · 도구 색인 — 이 문제에 쓴 주행 이름 · 도구 · 결과 파일
10. **도구 해설**(10-29 사용자: "할 수 있는 한 자세히 — 초창기일수록 매번 도구를 새로 만들어 도구 하나 파악하기도 힘들다") — 이 문제에 쓴 도구마다:
    - 실행 위치(Jetson · PC · WSL) · 부른 형태(인자)
    - 왜 만들었나(그때의 질문)
    - 하는 일 — 코드 기준 단계별(구독 토픽 · 계산식 · 판정 문턱 수치)
    - 출력(화면 줄 형태 · 저장 파일) · 그 출력이 남은 곳(`outputs/` 또는 '원천 소실')
    - 결과가 쓰인 § · 판정에 준 영향
    - 계보(앞판 → 뒤판의 차이, 대신한 후속 도구) · 알려진 결함 · 지금 다시 쓸 수 있는지
11. 용어 — 카드에 처음 나오는 개념(예: 데드밴드 · ZUPT · deskew)을 한두 줄로

시기 표시: 카드는 한 줄기 전체를 담지만 시기별로 채운다. 아직 안 읽은 시기는 '이후(09-07 ~): 다음 시기에서 채움' 으로 둔다.
