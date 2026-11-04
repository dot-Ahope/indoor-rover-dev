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

### 4 기 09-21 ~ 09-23 (Phase S 기준선 · Phase N nvblox · F0 시작) — 10-30 · 11-02 작성
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [Phase N 전반 N0~N4](nvblox-migration-n0-n4.md) | 완료 | 호스트 층 빌드 · 정지 A/B · 절단 거리 4 → 2 · 주행 A/B(STVL vs nvblox) |
| [nvblox 층 셀 인덱스 round → floor](nvblox-layer-round-floor.md) | 완료 | 호스트 nvblox_nav2 층이 칸 경계에서 반 칸 어긋남 → floor 수정(패치) |
| [Phase N 후반 N6 · 유령 셀](nvblox-n6-global-ghosts.md) | 완료 | bringup 통합 · 전역 이전 · 유령 셀(통합 거리 · 반사 테이프) · 최종 판정 |
| [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md) | 완료 | f0a1/f0a2 — SLAM 이 맞고 EKF 가 회전 중 옆 밀림을 못 봄 → 방향 D |
| [sensor_conditioner 역할](sensor-conditioner.md) | 완료 | 바이어스 · ZUPT · 공분산 — 빼면 안 되는 이유 |

| [주행 직전 DDS 참여자 금지 규칙](pre-drive-dds-participants.md) | 규칙(근거 약함) | cc1 루프 미달 18 = 주행 직전 메타 스냅숏 · 30 s 는 측정 근거 없음 |
| [Phase S 기준선](phase-s-baseline.md) | 완료 | S1~S6 · cc4/cc5 · BASELINE_STVL(여유 8~13 cm · CPU 320 % · 6.6 W)과 측정 방법 |

### 5 기 09-28 ~ 10-02 (회전 슬립 · SLAM 포크 · 컨디셔너 C++ · F0-b · F1 매핑 · F2 순회 · rf2o 시작) — 11-02 작성 · 앞 카드 8 장도 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [SLAM 포크 — 회전 중 스캔 처리](slam-fork-rotation.md) | 해결(지도 층) · 운용 | shouldProcessScan 을 '거리 또는 회전' 으로. ⚠ 위치 추정 모드 회전 문턱 0.15 rad(6.9°)에서의 효과는 미측정 |
| [회전축 보정 B2 · 회전 분산 B3](icr-b2-b3.md) | B2 보류 · B3 자동 켜짐 | B2 는 f0a7 map→odom 2.2 배로 기본 끔. B3 는 vslam/rf2o 때 σ 0.3 으로 자동 켜짐(ekf.launch.py 39~40) |
| [보드 OLED · base 자동 기동](board-oled-autostart.md) | 해결 | OLED 에 IP 표시 · rover-base 서비스 |
| [Isaac · cuVSLAM 평가](isaac-cuvslam-evaluation.md) | 결정(기능 완성 우선) | rf2o 야외 · 사람 마스크 · JetPack 6.2/NITROS · cuVSLAM 단독 · 프로젝터 충돌 → JetPack 7.2 뒤로 |
| [온보드 정지 수단 · nav_guard](onboard-stop-nav-guard.md) | 운용 | 목표 시간 · 무진행 한도로 Nav2 와 독립 취소. CPU 19.5 % 미해결 |
| [F0-b 코스 — 문 통과 7 m 왕복](f0b-course.md) | 완료 | f0b1 · f0b2 통과 · 실제 영상 나란히 |
| [F1 사무실 지도](f1-office-mapping.md) | 완료(office_v2) | 이어 그리기 오정합 2 회 → bag 재생 · 휜 구간 제거 → office_v2. 지금 지도는 office_v3 |
| [F2 순회 · 위치 점프](f2-patrol-loc-jump.md) | 점프 해결 | 1.33 m 점프 = 저장 지도의 빈 곳 → office_v3. 의자 옆 정체 · 복귀 상자 접촉 |
| [회전 중 장애물 번짐](rotation-obstacle-smear.md) | 조사 → rf2o | odom 좌표 코스트맵에 옛 표시가 남음 · 로컬 map 좌표 A/B |
| [rf2o 도입(5 기 부분)](rf2o-introduction.md) | 진행 → 이후 cuVSLAM | 라이다 정합 속도로 회전 미끄러짐을 EKF 에. 부호 반대 보정 · R2 오프라인 |

### 6 기 10-06 ~ 10-08 (rf2o 라이브 · 사람 시험 · 남서 정체 · 낮은 상자 기억 · 회전 방식 · TF 지연 · 저장소 공개) — 11-02 작성 · 앞 카드 9 장도 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [rf2o 게이트 G1~G4 · 사람 시험](rf2o-gates-people.md) | 보류(부분 해결) | 게이트 CPU 39 → 16 %. 정지 중 사람 · 다리 · 정지한 몸 통과, 크게 가린 채 움직이는 몸은 G4 로도 4.5~7.4 cm(목표 3). G3 기각, G4 판정량을 휠 잔차로 바꿔 곡선 오판 35 → 2 % |
| [남서 구석 방향 맞춤 정체](southwest-orient-stall.md) | 우회 | 도착 직전 '움찔' → nav_guard 취소 3/3 → 러너 '위치만(f)' 로 통과. 당시 해석('뒤 치명 칸')은 판별 없는 추정 — BT 가 끝 방향을 0° 로 덮어쓴 정황(10-14 CopyPath 로 고침), 일반 모드 재시험은 미실시 |
| [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md) | 우회(10-08) | 라이다 아래 상자를 계획기가 잊음: 라이다 소거가 카메라 표시를 지움(추정) + 재계획 0.01 Hz(측정). 전역 STVL 기각, 전역 nvblox(map) + 재계획 0.5 Hz 로 f2e2 3/3 · 미접촉. f2e1 접촉 = 층 프레임 기본값 odom(내 결함, 09-22 판에도 프레임 줄 없었음) |
| [회전 방식 · 트랙 비율 · 앞 회전 우선](rotation-method-track-ratio.md) | 보류 · 설정 반영(미검증) | 미끄러짐 방향 일정(뒤로) · 크기 불안정. 비율로 절반 이하 줄인 경우 없음(블록 설계라 확정 아님). PreferForward 5 → 15 — 지금 PathAlign · PathFollow(10-26 변경)에서의 효과는 미측정 |
| [W3 저속 떨림 · TF 지연](tf-lag-w3-wobble.md)(· 7 기 채움) | 조사 중 | ω 부호 6 s 에 21~34 번. TF 지연 가설 기각, t 235 중단은 map→odom stamp 1.49 s 멈춤 → MPPI transform_tolerance 0.5 로 우회. 떨림 원인 미확정 |
| [바닥 전선 · 케이블 가드 밟기](cable-step-over.md) | 보류 | 09-29 기울기 흔들림 2.6~3.3 배 · 10-01 가드 위 헛돎으로 SLAM 15 · 21 cm 되돌림. 10-06 영향 표는 대부분 원리 추정, 시험 미실시 |
| [저장소 공개 운영](repo-public-ops.md) | 해결(공개 이력) · 보류(비공개 이력 · GitHub 캐시) | 영상으로 첫 페이지 · 개인 계획 표현 정리 · 원본 → 공개 두 줄. 10-07 '이력 비밀번호 0' 점검이 놓친 옛 값은 11-02 게이트 강화 · 공개 이력 다시 쓰기로 0 |
| 이어 채움 | — | [rf2o 도입](rf2o-introduction.md)(라이브 줄자 B 1.5 cm · f2c 9/10) · [F2 순회 · 위치 점프](f2-patrol-loc-jump.md) · [nav_guard](onboard-stop-nav-guard.md) · [제자리 회전 미끄러짐](f0-rotation-side-slip.md)(10-06 단계별 90°) · [회전 중 번짐](rotation-obstacle-smear.md) · [트랙 비대칭](track-asymmetry.md) · [CPU 부하](cpu-load-stalls.md) |

### 7 기 10-12 ~ 10-15 (통신 포화 · 빠른 prep · 상자 옆 정지 · pad_relief · BT 끝 방향 · F2 기준선) — 11-03 작성 · 앞 카드 6 장도 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [통신 포화 — MPPI 궤적 발행 · reliable /tf 기록기](network-saturation-mppi-viz.md) | 우회 | 궤적 발행 206 kB + PreferForward 15 에서 6/6 포화. UDP 10 배, 그 79 % 가 /tf HEARTBEAT, 먼저 뒤처진 것은 bag 기록기(캡처 측정). 대책 lite(28 kB) + 기록기 /tf best effort. ⚠ 러너에서 /tf 재정의가 BAG_BE_TRAJ 조건 안에 있음. 5 대 15 차이는 미확정 |
| [빠른 prep](prep-fast-startup.md) | 해결(단축) · sed -i 우회 | ros2 조회 ≈ 25 회 → 확인 노드 1 개, 고정 대기 → 폴링: 4 분 41 초~5 분 17 초(PC) → Jetson 61 s, 이후 9 회 55~61 s. ⚠ prep_fast.sh 12 행 sed -i 가 설치본 링크를 끊는 결함 남음 |
| [상자 옆 정지 — 기전](box-side-stall-cause.md) | 조사 중(기전 확인 · 과장 원인 미확정) | MPPI 가 정확 여유 2.7~4.4 cm 까지 붙으면 Nav2 칸 검사가 서 있는 자세를 99 → 100 으로 뒤집어 후보 · 후진이 모두 막힘(실패 3 건 + 시뮬). 카메라 칸은 주행 중 +5~10 cm 나와 있고 정지하면 0~3 cm. '여유' 정의가 도구마다 셋 |
| [상자 옆 정지 — 시험한 대책](box-side-stall-remedies.md) | 조사 중 | 대책 19 개 중 17 개 효과 없음 · 부작용 · 기각 · 판정 없음. MonotoneEscape 켬(오프라인 5/5, 실제 미검증, 풋프린트 손 입력값), ClearanceBandCritic 띠 진입 0 · 2/2 지만 제어 주기 놓침으로 끔 |
| [갇힘 해제 pad_relief · 실행 중 패딩 변경 멈칫](pad-relief-runtime-padding.md) | 보류(쓰지 않음) | 시뮬 5/5 · 정지 4/4 · f2t1 실제 작동해 빠져나옴, 그 순간부터 좌우 틀기 지속, 정지 토글만으로 재현(10 · 9 → 98 · 64 → 15 · 20 /분). 토글은 잔떨림의 충분 조건이지 유일한 원인 아님(10-15 정정). 지금 표준 prep 은 노드를 띄우지 않음 |
| [BT 끝 방향 0° · CopyPath](bt-copypath-end-yaw.md) | 해결 | 스무딩 실패 때 TruncatePath 가 끝 방향을 0° 로 덮어씀 → 서쪽 통로 위치 2.9 cm 인데 정지(f2s1). 09-17 TODO 를 27 일 묵힘. CopyPath 뒤 f2t1 8/8 · 서쪽 통로 6/6. 남서 목표도 같은 결함이었음을 bag 재분석으로 직접 확인(11-03) |
| [F2 기준선 no5 · b910](f2-baseline-no5.md) | 완료(3/6) · 문서 · 태그 미작성 | 새 스택마다 6 회 중 3 회 합격, 실패 3 건 모두 상자 옆 기전. ⚠ 기준 ⑥ 은 결과를 본 뒤 재정의(옛 ⑥ 이면 2/6) |
| 이어 채움 | — | [W3 떨림 · TF 지연](tf-lag-w3-wobble.md)(10-07 stamp 정체 ≠ 10-12 수신 붕괴) · [DDS 공유메모리](dds-shm-incident.md)(10-12 검토만) · [회전 방식 · 앞 회전 우선](rotation-method-track-ratio.md)(PreferForward 15 검증 통과) · [낮은 상자 기억](low-box-global-memory.md)(전역 망각 = 지우기 반경 3.0) · [남서 구석 정체](southwest-orient-stall.md)(원인 해결 · f 우회 유지, p 재시험 없음) · [Jetson Wi-Fi](jetson-wifi-link.md)(10-14 IP 충돌 → .110 예약) |

### 8 기 10-19 ~ 10-23 (상자 칸 과장 · 프로젝터 · cuVSLAM · 공유메모리 · 유령 칸 · 경로 추종 · B0) — 11-03 작성 · 앞 카드 26 장도 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [카메라 상자 칸 과장의 근원](box-exaggeration-source.md) | 조사 중 | 출발점 상자 로버 쪽 면 +5.3 cm(f2x1)를 원시 깊이 점으로 나누면 관측 오차 3~5 + odom 기억 밀림 +2.7~6.1 + 칸 반올림(최대 5) cm. nvblox 설정 · 깊이 필터 · map 기억 · 깊이 해상도는 대책 아님(5 cm 척도 한계 주의) |
| [복귀 길 상자 칸](box-return-cells.md) | 우회(통합 거리 2.0, 1 회 검증) · 기억 밀림 남음 | 복귀 때 상자는 차체 옆 시야 밖이라 odom 기억이고 SLAM 보정마다 밀린다. 프리셋 3 · 프로젝터 끔에선 다시 봐도 깊이 0 → f2lp1 이 세 지도 0 칸인 채 접촉, 통합 2.0 뒤 f2pi1 실제 여유 1.1 cm |
| [프로젝터 번갈이 · IR](projector-ir-alternation.md) | 우회(10-21 §20 상시 끔 결정) | 번갈이는 우리 분리 노드 · NVIDIA 권장 구성 모두 자동 노출이 켠 프레임에 맞춰져 끈 IR 이 어두워 cuVSLAM 이 못 따라감(f2y1 469~483 cm). 상시 끔이면 따라감(f2z1 25.7 cm · yaw 0.8°) — 대가는 맨바닥 유령 칸 |
| [cuVSLAM 병진 속도 융합](cuvslam-velocity-fusion.md) | 부분 해결(운용 채택) | 오프라인(번갈이) 실패 → 상시 끔에서 따라감 → 같은 주행 그림자 비교 W3 회전 창 −20 %(UDP) · −31~−41 %(SHM) → 10-23 기본. 상자 옆 여유에는 효과 없음, yaw 는 휠 · 자이로가 정함 |
| [카메라 ↔ 컨테이너 공유메모리](camera-container-shm.md) | 해결(카메라 ↔ cuVSLAM 경로) | IR 307 kB 가 UDP 수신 버퍼 208 kB 를 넘어 정지 13 · 주행 9.5 Hz → 카메라 ↔ cuVSLAM 만 SHM+UDP 로 15.0 Hz(정지 A/B · 재기동 10/10 · f2sm1). 소켓 버림 감소의 직접 근거는 측정 결함으로 판정 불가 |
| [프로젝터 끔의 유령 칸 · 깊이 프리셋 3 · 통합 거리 2.0](ghost-cells-depth-preset.md) | 우회 | 상시 끔 뒤 맨바닥 유령 칸이 f2dr1 을 끊어 프리셋 3 기본(유령 0, 대가 낮은 상자 칸 절반 · min_weight · 프리셋 5 기각). 프리셋 3 + 1.4 m 는 f2lp1 접촉 → 2.0(f2pi1 3/3). 기전(무늬 없는 바닥 스테레오 오정합)은 추정 |
| [경로 추종 · 재계획 → B0](path-tracking-replan-b0.md) | 조사 중 | 상자 옆 근접은 계획기가 아니라 MPPI 굽은 곳 안쪽 깎기와 로버 자리 재계획 누적(경로 11~16 cm, 실제 0.3~6.7 cm). 재계획 0.01 Hz 도 b910 15.2 · 5.5 · 3.1 cm → B0 결함 기준선 고정. 10-23 Smac 오프라인 비교는 10-26 에 무효 |
| [PathBlockedAhead 99/100 · only_new](pathblocked-only-new.md) | 조사 중(조치 적용 · 실주행 효과 미확인) | 서쪽 통로 막힘 오판은 경로 받은 같은 틱에 99. 문턱 100 안은 상자 막힘도 끄는 내 오류 → '받을 때보다 커진 점만' 세는 only_new, bag 재생 9 사건 확인. ⚠ 표준 prep 0.5 Hz 와의 조합은 미시험 |
| [주행 전 검사 · 운용 사고(8 기)](drive-ops-1019-1023.md) | 우회 | 출발 위치 검사 PREP_POSE 가 prep 26 회 중 실제 오류 3 회를 주행 전에 거름, 게이트 P 65 % 완화는 판정을 바꾼 적 없음. prep 실패 3 유형 · 스크래치패드 소실 2 회 · 밤사이 재부팅 3 회의 원인은 미확인 |
| [기록 규칙의 진화](record-conventions-evolution.md) | 해결(규칙) · 보류(큰 bag 정리) | 큰 bag 수명 · 실수 칸 형식 · 추론별 데이터 위치 · 영상 기본 도구가 README §2.3 · §6 에 자리잡음. 남은 결함: TOOLS.md 3 일 누락 · 'git 제외' 라던 mp4 2 개가 실제로는 추적됨 |
| 이어 채움 | — | [상자 옆 정지 기전](box-side-stall-cause.md) · [대책](box-side-stall-remedies.md)(MonotoneEscape 실주행 첫 작동 f2sm2h) · [Isaac · cuVSLAM 평가](isaac-cuvslam-evaluation.md) · [DDS 공유메모리](dds-shm-incident.md)(10-20 재점검 표 검증) · [rf2o 도입](rf2o-introduction.md) · [rf2o 게이트 · 사람](rf2o-gates-people.md) · [제자리 회전 미끄러짐](f0-rotation-side-slip.md)(W3 창 9 주행) · [회전 중 번짐](rotation-obstacle-smear.md) · [N6 유령](nvblox-n6-global-ghosts.md) · [깊이 장애물](depth-obstacle-costmap.md) · [F2 기준선 no5](f2-baseline-no5.md) · [계획기](global-planner-choice.md) · [nav_guard](onboard-stop-nav-guard.md) · [CPU](cpu-load-stalls.md) · [MPPI 통로](mppi-passage-tuning.md) · [빠른 prep](prep-fast-startup.md) · [Wi-Fi](jetson-wifi-link.md) · [보드 연결](board-link-microros-session.md) · [전선](cable-step-over.md) · [보관](storage-housekeeping.md) · [DDS 참여자](pre-drive-dds-participants.md) |

### 9 기 10-26 ~ 10-29 (Smac 채택 · MPPI 굽은 곳 · nvblox 층 TF · SLAM stamp · 주행 전 검사 · F2.5 · 정지 드리프트) — 11-04 작성 · 시범 2 장 확장 · 앞 카드 약 25 장 이어 채움
| 카드 | 상태 | 한 줄 |
|---|---|---|
| [Smac Hybrid 채택](smac-hybrid-adoption.md) | 부분 해결(시험 구성 채택 · 기본 아님) | 오프라인 변형 비교는 1.1.20 Smac 의 static 설정 공유로 대부분 무효 → 변형마다 다시 재 RS + 해석 1.0 m. 실주행 b910 상자 옆 18.4 · 10.8 cm(MPPI 14 · 10, B0 15.2 · 5.5 · 3.1), 통로 남행은 tolerance 0.35 로 Smac 이 받아 0.8 → 4.1 cm. 북행 · 좁은 곳 출발은 출발 자세에 따라 NavFn 대체. launch 기본은 navfn |
| [MPPI 굽은 곳 안쪽 깎기 · PathAlign 28 / PathFollow 5](mppi-corner-cut-pathalign.md) | 우회(설정 채택 · 기전 미확인) | Smac 경로에서도 MPPI 가 굽은 곳 안쪽을 +10.7 · +15.7 cm 깎음(odom 좌표, 위치 보정 몫 ≤ 5 cm). 시뮬은 차를 못 가름, 실주행 A/B +4.6 · +1.6 cm 로 28 · 5 채택. ⚠ 기본 구성(NavFn · 0.5 Hz) + 28 · 5 조합은 달린 적 없음 |
| [nvblox 층 TF 조회 실패 처리](nvblox-layer-tf-drop.md) | 해결 | 전역 nvblox 층이 map→odom 조회 실패 순간 odom 슬라이스를 단위 변환으로 map 에 적어 0.55 m · 7.5° 틀어진 장(f2st1 3 장, 가짜 막힘 2). catch 에 return 뒤 f2tf1 틀어진 장 0, 방아쇠(SLAM stamp 정체)는 timeout 1.5 로 f2tt1 · f2tt2 경고 0. 영향 가능 기간 10-08 ~ 10-27 |
| [SLAM map→odom 시각 정체](slam-stamp-freeze.md) | 우회 | 위치 추정 정합(LinkNearChains 64 %) 동안 stamp 가 0.4~1.3 s 멈춰 nav2 TF 실패 → transform_timeout 1.5 로 f2tt1 · f2tt2 실패 0. 정체 자체(주행당 > 0.5 s 30 번 안팎)와 비용은 남음. 10-07 이후 위치 추정 순회 전부(회귀 아님) |
| [주행 전 검사 정리](drive-gate-consolidation.md) | 해결(정리) · 남은 결함 3 | 게이트 B · C · G2 를 한 노드(chk_drive_gate)로, P 를 30 s 대기 안으로 → 게이트 23.6 → 6.7 s, 출발까지 66 → 40 s(2 주행). 게이트 C 실제 관찰 창 1~5 s 흔들림 · timeout 1.5 뒤 C 문턱 1.0 s 의 뜻이 바뀜 · TEST_COURSE 게이트 표 낡음 |
| [F2.5 장소 이름 이동](f25-place-navigation.md) | 조사 중 | 등록부 좌표만 쓰는 place_server 로 실주행 5 회 — 앞 3 회는 설계대로 거절 · 멈춤(비스듬한 명목 자세 · 치우친 좌표 · 첫 메시지 유실), f2pl4 6/6(stop → /cmd_vel 0 0.29 s) · f2pl5 2/2. T1 미실행 · 모델 미실행 · launch 에 없음 · 휴대폰 창구는 휴대폰에서 미시험 |
| [세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md) | 조사 중 | 주행 뒤 정지에서만 odom yaw 가 돌고(43 분 +16.6°) SLAM 은 고치지 않아 경로 없음 · 7° 틀린 출발. 출발 전 검사 ⓐ 는 저장소에만(Jetson 판 미확인), d2 미실행. '정지 중 SLAM 이 안 고침' 은 위치 추정 문턱(0.15 rad)과 어긋나 기전 미확인 |
| 이어 채움 | — | [계획기](global-planner-choice.md) · [F2 기준선 no5](f2-baseline-no5.md)(9 기 no5 4 주행) · [BT CopyPath](bt-copypath-end-yaw.md) · [경로 추종 · B0](path-tracking-replan-b0.md) · [only_new](pathblocked-only-new.md)(f2sa3 첫 실작동) · [MPPI 통로](mppi-passage-tuning.md) · [MPPI 시뮬](mppi-offline-simulator.md) · [nvblox 층 반올림](nvblox-layer-round-floor.md) · [복귀 길 상자 칸](box-return-cells.md)(잊기 = 기능 · 시야 = 센서 한계, 사용자) · [상자 옆 정지 기전](box-side-stall-cause.md) · [낮은 상자 기억](low-box-global-memory.md) · [DDS 참여자](pre-drive-dds-participants.md) · [운용(8 기)](drive-ops-1019-1023.md) · [CPU](cpu-load-stalls.md) · [SLAM 포크](slam-fork-rotation.md) · [nav_guard](onboard-stop-nav-guard.md) · [휠 오도](wheel-odom-scale-slip.md)(반전 순간 FG 부호) · [트랙 비대칭](track-asymmetry.md) · [stuck_monitor](stuck-monitor.md)(자이로 우선 켜지 않음, 사용자) · [데크 yaw](sensor-deck-yaw.md)(xacro ↔ urdf) · [기록 규칙](record-conventions-evolution.md) |

### 10 월 (형식 시범)
10-29 시범 2 장(SLAM stamp 정체 · 정지 중 방향 드리프트)은 11-04 9 기에서 전체 형식으로 넓혀 위 9 기 표로 옮겼다.

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
