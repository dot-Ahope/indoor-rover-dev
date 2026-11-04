# 현재 구성 (CURRENT_STACK)

지금 로버 스택의 **값 · 그 값을 정하는 파일 · 결정한 날 · 근거 카드**를 한 표로 모은 안내다(2026-11-04 판, 값은 이날 저장소 코드에서 다시 읽음).
- **진실은 코드다.** 값이 이 문서와 다르면 코드가 맞다. 이 문서를 고치는 일은 구성을 바꾼 날의 일이다(그날 SUMMARY 와 함께).
- 경위(왜 이 값이 됐나, 무엇을 기각했나)는 문제 대장 카드 `Docs/issues/` 에 있다. 여기에는 한 줄 이유와 카드 이름만.
- 칸 'launch 기본' = launch 인자를 안 줬을 때, '표준 prep' = `Docs/tools/prep_patrol.sh`(→ `prep_fast.sh`)가 실제로 띄우는 구성. **주행은 표준 prep 기준**이다.
- 옛 판(CLAUDE.md §6 원문을 옮긴 것, 날짜별 서술)은 커밋 `29895107` 의 이 파일에 있다.

## 1. 기동 구성 — launch 기본 = 표준 prep (11-04 부터)
11-04 §17 에 launch 기본값을 표준 prep 구성과 같게 바꿨다 — 인자 없이 `ros2 launch` 해도 최신 스택이 뜬다(Jetson `--show-args` 확인 `Docs/debug_log/2026-11-04/outputs/up_launch_1104.txt`). 아래 '옛 launch 기본' 칸은 그 전 값(옛 기록을 읽을 때 참고).


| 항목 | 옛 launch 기본(~11-03) | 지금 기본(= 표준 prep) | 정하는 곳 | 결정 · 카드 |
|---|---|---|---|---|
| 계획기 | `planner:=navfn` | navfn(같음). Smac 시험은 `NAV_ADD="planner:=smac" REPLAN_HZ=0.01` | `navigation.launch.py` 203 · `prep_patrol.sh` 16~17 | 10-27 시험 구성 채택(기본 아님) · `smac-hybrid-adoption` |
| 주기 재계획 | `replan_hz:=`(BT 원본 0.01) | **0.5 Hz**(BT 원본 0.01 은 `replan_hz:=` 빈 값) | `prep_patrol.sh` 17 | 10-12 운용 · `path-tracking-replan-b0`(0.01 Hz 는 B0 시험) |
| 오도메트리(EKF 병진 속도) | `vslam:=off` · `rf2o:=false` | **cuVSLAM**(`vslam:=on` · `dds_shm:=true`). 옛 rf2o 구성은 `prep_patrol.sh` `ODOM=rf2o`(vslam off · 프로젝터 켬 · SHM 끔을 명시) | `ekf.launch.py` 98 · 109 · `prep_patrol.sh` 10~13 | 10-23 §16 · `cuvslam-velocity-fusion` |
| 카메라 프로젝터 | 켬(`emitter_off:=false`) | **상시 끔** | `camera.launch.py` 117 · `prep_patrol.sh` 11 | 10-21 §20 · `projector-ir-alternation` |
| 카메라 ↔ cuVSLAM 전송 | UDP(`dds_shm:=false`) | **SHM+UDP** | `camera.launch.py` 119 · `fastdds_shm_udp.xml` | 10-20 §9 · `camera-container-shm` |
| 전역 카메라 층 | `global_camera:=obstacle` | **nvblox**(map 프레임) | `navigation.launch.py` 207 · `prep_patrol.sh` 17 | 09-22 N6 · `nvblox-n6-global-ghosts` · `nvblox-layer-tf-drop` |
| MPPI 궤적 발행 | `mppi_viz:=false` | **lite**(28 kB) — `true`(206 kB) 금지 | `navigation.launch.py` 205 · `prep_patrol.sh` 8~9 | 10-12 · `network-saturation-mppi-viz` |
| 정체 감시 stuck_monitor | 작동(`stuck_shadow:=false`) | **관찰만**(`stuck_shadow:=true`), `use_gyro` 기본 끔 — 작동 모드는 10-01 f2a4 오판 · 10-29 사용자 '자이로 우선 켜지 마라' 로 쓰지 않음 | `navigation.launch.py` 219 · `prep_fast.sh` 63 | 10-29 §9 사용자(자이로 우선 켜지 않음) · `stuck-monitor` |
| 갇힘 해제 pad_relief | `off` | 띄우지 않음 — **켜지 않는다** | `navigation.launch.py` 231 · `pad_relief.py`(기본 off, 11-03) | 10-14 · `pad-relief-runtime-padding` |
| 지도 · SLAM | — | `office_v3`, slam_toolbox 포크 위치 추정 모드 | `prep_fast.sh` 9 · 61 · `slam.launch.py` 88(`slam_build:=fork`) | 10-02 · `f2-patrol-loc-jump` · `slam-fork-rotation` |

## 2. 고정 값 (launch · prep 과 무관)

### 2.1 SLAM · 위치 추정
| 값 | 정하는 곳 | 결정 · 카드 |
|---|---|---|
| 위치 추정 `transform_timeout 1.5` · 처리 문턱 0.30 m / 0.15 rad · 지도 갱신 10 s | `slam.launch.py` 75~77 | 10-27 §21 · `slam-stamp-freeze`(정체 자체는 남음) |
| map→odom 은 같은 stamp 를 두 번 발행 — 분석은 마지막 값만 | (slam_toolbox 동작) | 10-01 · `slam-stamp-freeze` |

### 2.2 코스트맵
| 값 | 정하는 곳 | 결정 · 카드 |
|---|---|---|
| 카메라 층 = nvblox(`camera_layer:=nvblox` · `global_camera:=nvblox` 기본, 컨테이너 nvblox 3.2.5 함께 기동). yaml 의 `plugins` 줄도 11-04 에 nvblox 판으로 맞춤 — launch 가 인자대로 늘 덮어씀 | `navigation.launch.py` 196 · `nav2_params.yaml` 328 · 563 | 09-22 N6-0 · `nvblox-migration-n0-n4` |
| nvblox 복셀 0.05 · 절단 2.0 칸 · 감쇠 0.99 · **통합 거리 2.0 m** · 슬라이스 z 0.06~0.30 · min_weight 0.1 · 지우기 반경 3.0 m · 깊이 전처리 끔 | `nvblox_local.yaml` 17 · 42 · 48 · 57 · 58 · 61 · 69~71 | 통합 2.0 = 10-22 §15 · `ghost-cells-depth-preset` · `box-return-cells` |
| 카메라 깊이 프리셋 **3 (High Accuracy)** · 데시메이션 ×4 | `camera.launch.py` 118 · 120 | 10-22 §10 · `ghost-cells-depth-preset`(데시메이션은 10-20 §8.3 대책 아님) |
| inflation 로컬 0.40 / 2.5 · 전역 0.70 / 2.0 · footprint_padding 0.01(둘 다) | `nav2_params.yaml` 527~528 · 722~723 · 323 · 558 | `inflation-padding-roles` |
| nvblox 층 TF 조회 실패 시 슬라이스 버림(호스트 `nvblox_nav2` 포크, round→floor 수정 포함) | `Docs/05_nvblox/nvblox_nav2_rover.patch` | 10-27 §17 · `nvblox-layer-tf-drop` · `nvblox-layer-round-floor` |

### 2.3 계획 · BT
| 값 | 정하는 곳 | 결정 · 카드 |
|---|---|---|
| NavFn(tolerance 0.25) + SimpleSmoother, 실패 시 원경로 — `CopyPath` 가 끝 방향까지 복사 | `nav2_params.yaml` 735~736 · 779 · BT `nav_to_pose_no_spin.xml` | 10-14 · `bt-copypath-end-yaw` |
| Smac Hybrid(시험 구성): REEDS_SHEPP · 최소 회전반경 0.10 · cost_penalty 3.0 · 해석 확장 1.0 m · tolerance 0.35, 실패 시 NavFn(BT `PlanSmacOrNavFn`) | `nav2_params.yaml` 740~763 | 10-26 §6.3 · 10-27 §8 · `smac-hybrid-adoption` |
| 막힘 판정 `PathBlockedAhead`(min_cost 99 · `only_new` 켬) | BT 108 · `path_blocked_ahead_condition.cpp` | 10-23 §20 · `pathblocked-only-new`(⚠ 0.5 Hz 와의 조합 미시험) |
| 복구: ClearCostmapExceptRegion · `monotone_escape`(풋프린트 손 입력값) | BT · `nav2_params.yaml` 791 | 09-11 · `costmap-clear-recovery` · `box-side-stall-remedies` |
| 러너 목표 방향은 NavFn 경로 끝에서 구함(`planner_id GridBased`) | `path_end_yaw.py` 22 | `smac-hybrid-adoption`(P2 미해결) |

### 2.4 컨트롤러 MPPI (BT `controller_id="FollowPathMPPI"`, `FollowPath`=RPP 는 남겨 둔 대조군)
| 값 | 정하는 곳 | 결정 · 카드 |
|---|---|---|
| 10 Hz · 32 step × 0.1 s · batch 1000 · temperature 0.15 | `nav2_params.yaml` 83 · 210~212 · 244 | `mppi-wobble-temperature`(0.3 시험 뒤 0.15 복귀) |
| 크리틱: Constraint · **Cost** · Goal · GoalAngle · **PathAlign 28** · **PathFollow 5** · PathAngle 2 · **PreferForward 15**. ClearanceBand(꺼짐) · ObstaclesCritic 은 블록만 보존(목록 밖, 11-04 정리) | `nav2_params.yaml` 255 · 264 · 269 · 276 · 283 · 287 · 290 | CostCritic 09-21 · `obstacles-to-costcritic` / PreferForward 10-12 · `rotation-method-track-ratio` / 28 · 5 10-26 · `mppi-corner-cut-pathalign` |

### 2.5 하드웨어 · 통신 운용 값
| 값 | 정하는 곳 | 결정 · 카드 |
|---|---|---|
| micro-ROS 460 800 bps(보드 · 에이전트 양쪽) — 2 Mbps 회귀 우회, 원인 미확정 | 보드 `usart.c` · `base.launch.py` 36 | 09-09 · `microros-baud-regression` |
| 데크 yaw −2.68° 보정(lidar π−0.04677 · camera/deck −0.04677) — 재조립 때 재측정, 함께 고칠 곳은 CLAUDE.md 하드웨어 요약 | `rover.urdf` · xacro · `stuck_monitor.py` · `rf2o_gate.py` | 09-18 · `sensor-deck-yaw` |
| 모터 PWM 20 kHz · 스톨 = duty ≥ 0.60 & 600 ms 무이동 → 1.5 s 자동 복구 · 10 s 3 회 래치 · `/cmd_vel` 500 ms 워치독 | 펌웨어 `safety_monitor.c` | 09-07 · `motor-pwm-50hz` · `stall-latch` |
| 보드 CH340 = WCH 벤더 드라이버(`ttyCH341USB0` → `/dev/rover`) — L4T R36.5 커널엔 기본 ch341 없음, 커널 갱신 때 재빌드 | Jetson `/lib/modules/…/ch341.ko` | 11-03 §11.1 · `board-link-microros-session` |

## 3. 운용 · 네트워크 · git

| 항목 | 지금 | 근거 · 카드 |
|---|---|---|
| Jetson 주소 | **<LAN-A>.8**(<WIFI-A>, 11-04) — 예약 주소 <LAN-B>.110(<WIFI-B>)은 끊긴 상태. <LAN-B>.101 은 다른 서버와 충돌 이력, 신원 확인 없이 붙지 않음 | 11-04 §10 · `jetson-wifi-link` |
| 재부팅 뒤 | `/tmp` 의 prep 도구가 지워짐 → `bash Docs/tools/up_tools.sh`(저장소 판 7 개) | 11-04 §1 · `prep-fast-startup` |
| 주행 전 검사 | 러너 게이트 `chk_drive_gate.py` 한 노드(B · C · G2) + 정지 부하 P(≤ 60 %) · 파라미터 확인 `chk_prep.py` · 출발 위치 검사 `PREP_POSE` | 10-27 §24 · `drive-gate-consolidation` · `drive-ops-1019-1023` |
| 장시간 정지 | 정지가 길었으면 출발 전 prep(odom yaw 드리프트). F2.5 는 출발 전 위치 검사 ⓐ(11-04 첫 배포) | 10-28 §16.1 · `stationary-yaw-drift` |
| F2.5 장소 이동 | 등록부 `places.yaml` → `place_server` · `place_cmd` · `place_web.py`(키는 저장소 밖) — **launch 에 없음**, job 스크립트로 띄우는 시험 단계. LLM 미실행 | 10-28 · `f25-place-navigation` |
| git | 원본 `feature/nvblox-migration` → 비공개 `personal` · 공개 `bash private/publish_public.sh` → public `dev`(CLAUDE.md · `private/` 제외). push 는 지시 때만, origin 금지 | README §8 · `repo-public-ops` |

## 4. 상태 (Phase)
- Phase S 종료(기준선 `Docs/debug_log/2026-09-21/BASELINE_STVL.md`) → Phase N(nvblox) 종료 09-23(`Docs/05_nvblox/PHASE_N_RESULTS.md`) → 기능 완성 우선(09-29): F0 · 정지 수단 · F1 지도 · F2 순회(기준선 no5 · B0 `navfn-baseline-20261023`) 완료 → **F2.5 장소 이름 이동(S1 완료, S2 LLM 부터)** → JetPack 7.2 이전 Phase. 순서 근거 `Docs/04_navigation/NAV2_EXPLORATION_PLAN.md` §7.4 · `Docs/06_planner/SMAC_HYBRID_PLAN.md`.
- 열린 큰 문제: 상자 옆 근접(`box-side-stall-cause` · `path-tracking-replan-b0`) · SLAM stamp 정체(`slam-stamp-freeze`) · 정지 yaw 드리프트(`stationary-yaw-drift`) · micro-ROS 2 Mbps 회귀(`microros-baud-regression`).
