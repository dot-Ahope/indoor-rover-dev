# nvblox 이전 전반부 N0~N4 — 컨테이너 nvblox · 호스트 층 · 정지 A/B · 절단 · 감쇠 · 주행 A/B

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **결정(로컬 층 채택, 09-22 N5 (a))** — N4 주행 S 2 · N2 3 회 5/5 성공, 코스트맵 상자 여유 N2 12.3~14.6 cm(S 9.3~11.7), 기억 유지 3/3. **CPU 기준(< 320 %)만 불합격**(330~337 %, 구조적 — 전역 STVL · 릴레이 잔존). 이전 명분이던 'CPU 절감' 은 이 시기에 확인되지 않았고 N6 에서도 동등에 그침(→ `nvblox-n6-global-ghosts.md`) | 09-09 계획 → 09-11 보류 → 09-14 재개 판단 → **09-21 §9~§10 · 09-22 §0~§3.1**(이 카드) → 09-22 §4~ · 09-23(N6, 다른 카드) | [`NVBLOX_MIGRATION_PLAN.md`](../05_nvblox/NVBLOX_MIGRATION_PLAN.md) §0 · 09-14 재검토 · [09-21 §9](../debug_log/2026-09-21/SUMMARY.md) | Jetson: `~/workspaces/isaac_ros-dev`(isaac_ros_common · isaac_ros_nvblox release-3.2), 컨테이너 `isaac_ros_dev-aarch64-container`(apt `ros-humble-isaac-ros-nvblox 3.2.5`), 호스트 `~/ros2_ws/src/{isaac_ros_common_stub, nvblox_msgs→, nvblox_nav2→}`. 저장소: [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml)(`nvblox_layer` 블록, 09-21 md5 7632b6e393dc), 채택 설정 [`nvblox_local.yaml`](../../ros2_ws/src/rover_navigation/config/nvblox_local.yaml)(09-22, 절단 2.0 · 감쇠 0.99), `job231_drive.sh` `BAG_PROFILE=nvblox`, 절차 [`TEST_COURSE_AND_GATES.md`](../04_navigation/TEST_COURSE_AND_GATES.md) v2.0(게이트 J · K · L) | [층 셀 인덱스 결함 round→floor](nvblox-layer-round-floor.md)(정지 A/B 중 발견) · `nvblox-n6-global-ghosts.md`(N6-0 bringup · 전역 이전 · 유령 셀) · [카메라 깊이 장애물](depth-obstacle-costmap.md)(STVL 이 오게 된 경위) · [깊이 점군 아티팩트 · depth_relay](depth-relay-artifacts.md)(nvblox 가 대체하려던 릴레이) · [ObstaclesCritic → CostCritic](obstacles-to-costcritic.md)(기준선 cc2~cc5) · [회피 주행 계측 결함](avoid-run-metrics.md)(러너 ①~⑥ · job416) · [통과 폭 판단 도구](passage-width-analysis.md)(job248 감사 기준1) · ['후진하고 멈췄다' — CPU](cpu-load-stalls.md) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(10-27 같은 층 파일 두 번째 수정) |

**한 줄**: Phase S(STVL) 기준선을 고정한 날(09-21) 저녁부터 다음 날까지, Isaac ROS 3.2 개발 컨테이너 안에 nvblox 를 띄우고(호스트 ROS 무손상) 호스트 Nav2 에 nvblox 코스트맵 층을 소스 빌드해 붙인 뒤, **정지 셀 대조 → 층 결함 수정 → 절단 거리 4→2 → 감쇠 0.95→0.99 → 주행 A/B** 순서로 진행했다. 정지 단계에서 nvblox 가 STVL 보다 '부정확해 보인' 이유는 (A) 층의 반 셀 인덱스 결함(수정)과 (B) 표면 뒤 TSDF 절단 띠(절단 2.0 으로 0.20 → 0.10 m)였고, 주행 단계에서 벤더 기본 감쇠(0.95)가 이 코스에 필요한 기억 시간(≥ 60 s)의 1/4 밖에 안 된다는 것을 사용자 질의로 발견해 0.99 로 바꿨다. 주행 지표는 기준선 이상이었지만 CPU 는 늘었다(+12~22 %p).

> ⚠ 읽을 때 주의
> - 이 시기 nvblox 입력 깊이는 **160×120**(디시메이션 4 가 깊이 이미지 자체를 줄임). `nvblox_n0.yaml` 머리 주석 "dec 4 는 점군에만 적용 — 깊이 이미지는 원해상도" 는 **틀렸다**(09-21 §9 정정, §6.1).
> - 이 시기 nvblox 는 **로컬 코스트맵 카메라 층만** 맡았다. 전역 코스트맵은 STVL + depth_relay 그대로(N6-1 에서 이전, 다른 카드).
> - 판정의 '여유' 는 세 종류가 섞인다: 코스트맵 상자 최소 여유(job416, 셀 양자화 ±2.5 cm), 복귀 회전 자리 여유(job446), 러너 ① 실제 최근접(카메라 점군 기하). 서로 다른 값이다(§9 용어).

---

## 1. 출발점 — 왜 옮기려 했나(계획의 근거 vs 그때까지 잰 것)
| 날짜 | 계획서가 든 근거 | 측정으로 확인됐나 |
|---|---|---|
| 09-09 §0 | "Jetson GPU 를 놀리는 것은 낭비, TSDF/ESDF 를 GPU 에서 만드는 nvblox 가 이 하드웨어에 맞다. 목적은 성능 향상, 기준선 A/B 로 판정" | 원칙 — 판정 방식만 정함 |
| 09-09 → 09-10 정정 | 처음 전제 "카메라가 근접 시 깊이점을 못 만든다" 는 계측 아티팩트(벽을 상자로 잡음, [회피 계측 결함](avoid-run-metrics.md)). 진짜 원인은 **STVL 절두체 clearing 이 가림 · 화각을 모르는 것** → "nvblox TSDF 는 관측된 것만 갱신하므로 이 실패 모드가 구조적으로 없다" | 원인 쪽은 09-10 §9 · §11 측정. nvblox 쪽은 **설계상 주장**(이 시기엔 미측정) |
| 09-11 판정 | **지금은 이전하지 않는다** — 이틀간 실패 원인은 BT · RPP · 절차 · 도구, STVL 은 CPU 상위 8 개 밖. 트리거 (c 필수 + a/b) | 측정(09-11 §5.13) |
| 09-14 재검토 | 목표가 '청소기형 자유 이동' 이면 지도 계층 요구가 바뀜. 그날 한 땜질 3 개(릴레이 비산점 · 근거리 제거, 감쇠 연장)가 nvblox 의 구조적 기능. 트리거 (a) 충족, (b) "nvblox(GPU)가 릴레이와 STVL 을 함께 대체하면 CPU 는 오히려 준다", Orin Nano 통합 · ESDF 시간 "15~25 ms 추정" | (b) 와 시간은 **추정**. 이 카드의 측정: 통합 0.37 ms · ESDF 2.5 ms/프레임(160×120, §2 N0) — 추정보다 훨씬 쌈. CPU 는 로컬만 바꾼 N4 에서 **+12~22 %p 늘었다**(§2 n4) |
| 09-21 BASELINE §4 | 채택 = 3 회 중단 0 · 미달 ≤ 1, 코스트맵 상자 여유 ≥ 8 cm(평균 ≥ 11), ①·④ 동등 이상, **CPU 합 < 320 %(릴레이 + STVL 분 ≥ 30 %p 감소 기대)**, GPU · 전력(6.6/7.9 W) · 온도(48.8 °C) 한계 안 | 기준선 수치는 측정(cc2~cc5: 여유 8.4~12.9, CPU ≈ 320, GPU 0) — [CostCritic 카드](obstacles-to-costcritic.md) |

- 기준선이 적어 둔 STVL 한계(BASELINE §3): ① 릴레이 min_range 0.45 → 앞단 0.43 m 안 물체가 코스트맵에 없음 ② 상자 옆 통과 중 25~30 s 는 STVL 기억(decay 120 s)으로 주행, 절두체 근평면 안쪽은 감쇠로만 지움 ③ 상자 셀이 실물보다 넓음(코스트맵 여유 8~13 vs 기하 9~18 cm).
- 정리: 이전의 근거 중 **측정된 것은 'STVL 쪽 실패 모드'** 였고, nvblox 가 그것을 푼다는 것 · CPU 가 준다는 것은 이 Phase 에서 재야 할 가설이었다. 이 카드의 결과로 보면 기억(③ 100/100)과 여유는 확인, CPU 절감은 기각(로컬만 바꾼 단계에서는 오히려 증가 — 구조적 이유가 있어 N6 로 넘김).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-21 §9 사전 조사 | 읽기 전용 probe(job464 · 465) | L4T R36.5.0(JetPack 6.2 계열), NVMe 233 GB 중 193 여유, docker 29.3 + nvidia 기본 런타임 + toolkit 1.16.2, 호스트 CUDA 없음, git-lfs 없음, NGC 익명 풀 OK, 15 W | **Isaac ROS 3.2 Dev 컨테이너 방식**(호스트 ROS 무손상). `realsense_splitter`(에미터 교대)는 미사용, cuVSLAM 은 이 Phase 제외 | `2026-09-21/outputs/j464_n0probe.txt` · `j465_n0probe2.txt` |
| 09-21 §9 1 단계 | 사용자 승인 sudo(git-lfs), isaac_ros_common release-3.2(fcf4d9e) 클론, 이미지 빌드 백그라운드(job468) | 첫 빌드는 TERM 미설정으로 즉시 종료(job470 진단) → TERM=xterm 재시작(job471) | — | `j468_n0_setup.txt` · `j470_builddiag.txt` · `j471_buildstart.txt` |
| 09-21 §9 2 단계 | 상주 컨테이너 기동 + 컨테이너 안 apt nvblox(job472) | 이미지 = NGC 프리빌드 40.3 GB(풀 ≈ 25 분, 재태그), CDI 지정 실패("Found 0 CDI devices") → 레거시 `NVIDIA_VISIBLE_DEVICES=all`, CUDA 12.6, `ros-humble-isaac-ros-nvblox 3.2.5` | 컨테이너 쪽 완료(호스트 무변경) | `j472_container.txt` · `j476_cdi.txt` |
| 09-21 §9 3 단계 | 호스트 센서 + SLAM(Nav2 없음, job475) 위에서 nvblox_node 깊이 전용(job473, `nvblox_n0.yaml`) | 깊이 통합 15.1 Hz · ESDF 9.6 Hz · 슬라이스 9.5 Hz, 지연 깊이 0.065 s · ESDF 0.10 s, tsdf 0.37 ms · esdf 2.5 ms, **GPU 0~10 % · nvblox CPU ≈ 16 %** | N0 (iii) 통과 | `j473_start.txt` · `j475_sensors.txt` · `j477_nvblox_info.txt` |
| 09-21 §9 N0 (i)(ii)(iv) | 정지 측정(job474 + job478), 변형 2 차(job483) | 앞면 +0.4 셀(0.05) · +0.1 셀(0.03), 근거리 자취 0/311, 4 조건 표(§4.1) | **N0 4 게이트 통과**. 절차 사고 2 건(§6.2) | `j474_n0a.txt` · `j480_hostchk.txt` · `j481_n0_variants.txt`(실패판) · `j482_state.txt` · `j483_n0_variants2.txt` |
| 09-21 §10.1 | 호스트에 `nvblox_msgs` · `nvblox_nav2` 소스 빌드(job484 실패 → job485 성공) | job484: `isaac_ros_common` cmake extras 의 `FindCUDA REQUIRED` 로 2.9 s 만에 실패. job485: 빈 스텁 `isaac_ros_common` 으로 70 s, 플러그인 `nvblox::nav2::NvbloxCostmapLayer` 등록 | CUDA 없이 호스트 층 확보 | `j484_hostbuild.txt` · `j485_hostbuild2.txt` · `j486_pluginchk.txt` |
| 09-21 §10.1 | `nav2_params.yaml` 에 `nvblox_layer` 블록(이진) + 주석 `plugins` 줄 배포 | md5 7632b6e393dc(src · install · /tmp 동일) | A/B-1 = '치명 셀 출처' 하나만 바꿈 | `j487_deploy_nv.txt` |
| 09-21 §10.2 | 정지 A/B(job488 · job489) | LETHAL 207 → 308, 앞 0.3~1.6 m 62 → 114, 감사 기준1 0.40 → **0.10** | "nvblox 는 관측된 모든 표면을 치명으로 올려 통로 창이 좁아졌다" ✘ — 0.10 은 클리어 직후 과도 상태(§10.3 정정) | `j488_layer_ab.txt` · `j489_{stvl,nvblox}_mode.txt` |
| 09-21 §10.3 | 셀 단위 JSON · 시각화(run_j490 · job491) | 두 번째 표본 기준1 **0.40** · RPP 0.25, nvblox 만 89 셀은 **모두 관측면 뒤쪽** | 통과 폭 · 앞면은 같고 차이는 '표면 뒤 두께'. 기전 = TSDF 절단 0.20 m(**추정**, 방향 · 두께 일치) | `j490_griddump.txt` · `grid_*.json` · `j491_costmap_ab.html` |
| 09-21 §10.4 | 사용자 "STVL 이 더 정확해 보인다. 어떻게 해결할 것인가" → 소스 읽기 | (A) `lookupInSlice` round 결함 (B) `distance <= 0 → LETHAL` 이 이진/기울기 분기 **앞** | §10.3 의 "A/B-2(기울기)로 띠 다루기" **정정** — 띠 손잡이는 절단 거리뿐 | `j492_layersrc.txt` |
| 09-21 §10.5 | round → floor 수정 · 재캡처(V1~V4 선언) | 층 = 슬라이스, 통과 측 0.00 vs 물리 +0.011 | (A) 확정 → [별도 카드](nvblox-layer-round-floor.md) | `j493_*` · `j494_viz2.txt` |
| 09-22 §0 | 09:36 재부팅 복구(job498 · job499) | `/tmp` 스크립트 · 스택 전부 없음, 컨테이너 Exited → `docker start`(apt 8 패키지 보존), 포크 diff 유지 | 복구 절차 = 재전송 → `docker start` → base → 보드 리셋(사용자) → prep | `2026-09-22/outputs/j498_state.txt` · `j499_container.txt` · `j500_prep1.txt` |
| 09-22 §1 · §1.1 | 절단 4.0 vs 2.0 정지 A/B, T1~T6 선언 → job501 · job502 | 띠 셀 73 → 25, 상자 깊이 0.25 → 0.15, nvblox 만 98 → 70(−29 %), 좌측 가구 x 열 11 → 8 | 선언대로면 T3 · T6 불합격 → 전제 오류 정정 뒤 2.0 지지(근거 약함 표기), **사용자 "제안대로"** | `j501a_t4.txt` · `j501b_t2.txt` · `j502_eval.txt` · `j502b_shell.txt` · `j502c_holes.txt` · `j503_trunc_ab.html` |
| 09-22 §2 | N4 주행 A/B 설계 · 판정 기준 선언(주행 전) | 사전 가설(계산): 감쇠 0.95 면 관측 끊김 ≈ 15 s 뒤 ESDF 소실 → t ≈ 20 s 상자 소실 가능 | 첫 N2 회차를 이 가설 측정으로 삼을 계획 | SUMMARY 만 |
| 09-22 §2.1 | 사용자 "감쇠값은 로버 속도에 맞춰 계산한 것인가" → **아니다, 벤더 기본값** → 필요 기억 시간 계산 · 정지 측정(job506) | 0.95: 관측 끊김 후 17 s 에 상자 셀 0 · 36 s 블록 해제. 0.99: 81 s | 0.99 채택(필요 ≥ 60 s) | `j506_d95.txt` · `j506_d99.txt` |
| 09-22 §3 | 주행 n4s1(S) · n4n1(N2) · n4s2(S) · n4n2(N2) · n4n3(N2) | §5 표 | 게이트 L 문턱 10 → 8 정정(n4n2 전, 사용자 승인), n4n3 러너 ①② 무효(재고정 결함) | `j507_*` · `j508_*` · `j509_*` · `j510_*` · `j511_*` · `n4*.csv` · `nav2_n4*.log` · `top_n4*.log` · `tegra_n4*.log` · `meta_n4*.txt` · `params_n4*.txt` · bag `2026-09-22/bags/bag_n4*.tgz`(로컬) |
| 09-22 §3.1 | N4 판정(BASELINE §4) | CPU 만 불합격(구조적) | 권고 (a) 로컬 채택 → **사용자 결정 (a)**(PHASE_N_RESULTS 머리) | SUMMARY · `j512_n4_traj.html` |
| 이후 09-22 §4~ · 09-23 | N6-0 bringup · N6-1 전역 · 유령 셀 · N6 판정 | | | `nvblox-n6-global-ghosts.md` |

## 3. 시스템 구조 — 무엇이 어디서 도는가(이 시기)
```
[호스트 Jetson, 네이티브 ROS 2 Humble]                         [컨테이너 isaac_ros_dev-aarch64-container]
 realsense-ros 4.58.3 ─ /camera/camera/depth/image_rect_raw ──┐   (docker run -d --network host --ipc=host --pid=host
   (640×480×15 → 디시메이션 4 → 160×120 16UC1, 15 Hz)          │    --runtime nvidia, /tmp 공유, 같은 Fast DDS UDP 전용 프로파일)
   + depth/camera_info                                         ├──▶ nvblox_node (apt nvblox 3.2.5, CUDA 12.6, GPU)
 EKF odom→base_link · URDF /tf_static ─────────────────────────┘      TSDF 복셀 0.05 (odom 프레임, 통합 2.0 m, 절단 4→2 복셀)
                                                                         → ESDF 2D (z 0.03~0.30 사이 최소 거리)
 Nav2 controller_server / local_costmap  ◀── /nvblox_node/static_map_slice (DistanceMapSlice 9.5 Hz) ──┘
   plugins: [nvblox_layer | stvl_layer, obstacle_layer(라이다), inflation_layer]
   nvblox_layer = 호스트에서 소스 빌드한 nvblox::nav2::NvbloxCostmapLayer (isaac_ros_common 빈 스텁)
     셀마다 lookupInSlice → 거리 ≤ 0 → LETHAL, 그 밖 FREE(이진) → inflation_layer 가 0.40/2.5 로 번짐
 Nav2 planner_server / global_costmap: static + STVL(+depth_relay) + 라이다 — 이 시기 변경 없음
```
- 왜 컨테이너인가: Isaac ROS 3.2 는 JetPack 6.x 용이고 설치 경로가 개발 컨테이너 또는 apt(저장소 등록 · sudo). 컨테이너면 호스트 Humble · 카메라 드라이버 · micro-ROS 에이전트를 안 건드린다(계획서 N1 게이트 "현재 스택을 건드리지 않고 nvblox 만 추가할 수 있는가"). 대가: 재부팅 뒤 컨테이너 복구(`docker start`) · `docker exec` 는 신호를 안 넘겨 노드 정리가 수동(N6-0 의 `nvblox_up.sh` 가 자동화, 다른 카드).
- 왜 층만 호스트 빌드인가: 층은 `DistanceMapSlice` 구독 + nav2_costmap_2d 만 쓰므로 CUDA 가 필요 없다. Nav2 가 호스트에 있으니 플러그인도 호스트에 있어야 로드된다.
- 왜 odom 프레임인가: 계획서 09-14 §3 — slam_toolbox map→odom 점프(18~36 cm 관측)가 map 프레임 TSDF 를 번지게 하므로 로컬 지도로. 대가: odom 이 틀어지면 기억된 장애물이 같이 밀린다(이후 10-13 상자 옆 4~5 cm, CLAUDE.md §6).

## 4. 가설과 판별
### 4.1 N0 — nvblox 단독 정지 측정(09-21 §9, 계획서 09-14 §5 의 4 게이트)
| 조건(입력 / 복셀) | 상자 띠 장애물 셀 최소 x(중앙) → 물리 1.153 대비 | 카메라 0.45 m 안 장애물 셀 | 깊이 / ESDF Hz | 지연 깊이 / ESDF s | GPU % | nvblox CPU % | tsdf / esdf ms |
|---|---|---|---|---|---|---|---|
| 160×120 / 0.05 (30 s) | 1.175 → **+0.4 셀**(0.022 m), 변동 0 | **0 / 311** | 15.1 / 9.5 | 0.064 / 0.10 | 0~10 | 16~21 | 0.36 / 2.4 |
| 160×120 / **0.03** | 1.157 → +0.1 셀(0.004 m) | 0 / 209 | 15.1 / 9.6 | 0.065 / 0.10 | 0~6 | 21 | 0.61 / 3.2 |
| 320×240 / 0.05 | +0.4 셀 | 0 / 207 | 15.1 / 9.6 | 0.068 / 0.10 | 2~4 | 18 | 0.39 / 2.2 |
| 640×480 / 0.05 | +0.4 셀 | 0 / 191 | 14.8 / 9.5 | 0.072 / 0.11 | 0~7 | 18 | 0.36 / 2.2 |
- 판정: (i) ≤ 1 셀 ✓ (ii) 0/450 급 ✓(0/311) (iii) 15 Hz · 한 코어 미만 ✓ (iv) 0.03 가능 ✓. 640×480 에서는 호스트 코어 하나 77~91 %(realsense 쪽)와 측정 노드 TF 실패 17 회 — 해상도를 올리면 호스트 비용이 먼저 온다. 15 W 모드 그대로.
- 측정 vs 추정: '+0.4 셀' 은 슬라이스 셀 **중심**(모서리 규약 가정)과 물리 전면의 차다. 규약 반 칸 문제는 [round→floor 카드](nvblox-layer-round-floor.md) §6.3. STVL 쪽 비교값(코스트맵 상자 앞 가장자리 1.125~1.15, 릴레이 없을 때 근거리 아티팩트 17 %/4 % 프레임)은 다른 도구(job248 감사 · 09-14 job311/312)로 잰 것이라 같은 자로 잰 대조가 아니다.

### 4.2 정지 A/B — '치명 셀이 2 배' 의 정체(09-21 §10.2~§10.4)
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| nvblox 가 통로 창을 좁힌다(기준1 0.40 → 0.10) | 같은 배치 재캡처(§10.3) | 두 번째 표본 0.40 · RPP 0.25(3 표본 동일) — 0.10/0.00 은 Nav2 재기동 · 클리어 직후 층이 재적분 중인 과도 상태 | 기각(§6.3). 같은 현상이 09-22 n4n2 러너 게이트에서 재현 |
| nvblox 만 LETHAL(89 셀)은 STVL 이 놓친 실제 장애물(안전 이득) | 셀 위치를 센서 표면과 대조 | 89 셀 **모두 관측면 뒤쪽**(상자 뒤 +x · 우측 −y, 벽 · 가구 뒤), 자유 공간 쪽으로 나온 것 0 | 기각 — 이득도 손실도 통과 폭엔 없음 |
| 그 89 셀은 TSDF 절단 띠(4 복셀 = 0.20 m) | 방향(카메라가 보는 면의 뒤로) · 두께 일치(§10.3) → 소스(§10.4) → 절단 4→2 A/B(09-22 §1) | 띠 셀 73 → 25, 상자 깊이 0.25 → 0.15 | 지지 |
| 띠는 기울기 모드(A/B-2, `inflation_distance`)로 다룰 수 있다 | `updateCosts()` L186~188 | `distance <= 0 → LETHAL` 이 `convert_to_binary_costmap_` 분기 **앞** → 기울기 모드는 표면 **앞쪽** 비용만 바꿈 | 기각(§10.3 의 제안 정정) |
| 층 그림이 슬라이스와 다르다(−1 셀) | 소스 · 재캡처 | round 결함 | 지지 → [별도 카드](nvblox-layer-round-floor.md) |
- 09-21 §10.4 의 "정확도 재정의": 관측면(앞면 · 왼쪽 가장자리) 위치는 슬라이스 기준 STVL 과 같다(≤ 1 셀). 비관측 영역(상자 뒤 · 오른쪽)은 STVL "모르면 비어 있음" vs nvblox "표면 뒤 0.20 m 는 막힘" 의 **가정 차이**이지 측정 정확도 차이가 아니다 — 폭 0.18 상자에서는 STVL 가정이 맞고, 깊은 가구에서는 반대.
- 해결 순서(09-21 §10.4 제안, 이후 그대로 진행): ① floor 수정 ② 절단 4→2 ③ N4 주행 ④ 띠가 주행 지표를 해칠 때만 포크 규칙 변경(표면 셀만 LETHAL) — "안 보인 내부는 막힘" 이라는 nvblox 의도를 버리는 설계 변경이라 마지막 순위. ④ 는 하지 않았다.

### 4.3 절단 거리 4.0 vs 2.0(09-22 §1, 기준 측정 전 선언)
| | STVL(stvl3) | 절단 4.0 (t4) | 절단 2.0 (t2) |
|---|---|---|---|
| 로컬 LETHAL / 슬라이스 ≤0 | 201 / — | 275 / 173 | 248 / 110 |
| 상자 외곽(층 = 슬라이스) | x 1.10~1.25, y −0.20~+0.05 (10) | x 1.15~1.40, y −0.25~+0.05 (23) | **x 1.15~1.30, y −0.20~+0.05 (12)** |
| 상자 앞면 셀 / 깊이 | 1.10 / 0.15 | 1.15 / 0.25 | 1.15 / **0.15**(물리 전면 1.151, 뒤끝 1.26) |
| 5 cm 스냅 둘 다 / nvblox 만 / STVL 만 | — | 177 / 98 / 24 | 178 / 70 / 23 |
| nvblox 만: 상자 / 우측 벽 / 좌측 가구 | — | 15 / 37 / 45 | **3 / 21** / 46 |
| 감사 기준1 / RPP (3 표본) | 0.35(prep) | 0.35 / 0.15 | 0.35 / 0.15 |
| job474 (i) / (ii) | — | +0.024 m / 0/210 | +0.024 m / 0/212 |
| 깊이 / ESDF / esdf 지연 · GPU / nvblox CPU | — | 15.1 / 9.6 / 0.101 · 0~4 % / 18.3 % | 15.1 / 9.6 / 0.102 · 0~4 % / 17.8 % |
| 표면 x 열(슬라이스) 우측 벽 / 좌측 가구 | — | 23 / 11 | 21 / 8 |
- 선언 기준: T1 앞면 동일 ✓ · T2 깊이 ≤ 0.15 ✓ · **T3 nvblox 만 ≥ 40 % 감소 · STVL 만 ≤ 10 ✘**(−29 %, 23) · T4 기준1 유지 ✓ · T5 N0 게이트 유지 ✓ · **T6 표면 연속성(x 열 −10 % 이내) ✘**(좌측 가구 11 → 8 = −27 %).
- 데이터를 본 뒤의 정정(선언보다 약한 근거, 09-22 §1.1): T3 의 전제 "nvblox 만 = 절단 띠" 가 틀렸다 — 좌측 가구 nvblox 만 46 셀은 base 거리 0.75~1.80 m(중앙 1.32)로 **STVL 카메라 `obstacle_range 1.2` 밖**을 nvblox(통합 2.0 m)만 보는 것(`j502b_shell.txt`). 띠가 자라는 구역(상자 + 우측 벽)만 보면 52 → 24(−54 %). 껍질 안쪽(띠) 셀 73 → 25. STVL 만 19 셀(공통)은 좌측 가구 9 · 뒤 · 옆 7 — nvblox 슬라이스 0.03~0.30 이 STVL 0.06~0.40 보다 낮아 가구 윗부분을 못 봄 + 시야 밖. T6 의 사라진 열은 우측 벽 2 열(2.05 · 2.10, 통합 2.0 m 끝) · 좌측 가구 3 열 중 2 열(1.65 · 1.90, 끝), **안쪽 구멍은 x 1.55 의 5 cm 1 개**(거리 ≈ 1.7 m, 스침각, `j502c_holes.txt`).
- 결정: 선언 규칙대로면 "T6 실패 → 4.0 유지". 정정 분석은 2.0 지지 → 제안 "N4 를 S / N(2.0) 로, 나쁘면 N(4.0) 을 세 번째 팔로" → 사용자 "제안대로". 벤더 기본(4.0)을 벗어나는 근거는 이 표뿐(09-22 §1.1 스스로 기록).
- 같은 정지 A/B 의 다른 결과: 상자 앞면 행별 셀이 t2 는 1.15 × 5, t4 는 1.25 / 1.15 × 4 / 1.20(`j502c_holes.txt`) — 2.0 이 더 고르다. 감사 기준1 이 어제 0.40 이 아니라 0.35 인 것은 배치 · 시각 차(같은 날 STVL 도 0.35).

### 4.4 감쇠 — 벤더 기본값이었나(09-22 §2 · §2.1)
- 출처 확인: `nvblox_n0.yaml` 의 `decay_tsdf_rate_hz 5.0 / tsdf_decay_factor 0.95 / tsdf_decayed_weight_threshold 0.001 / tsdf_decayed_free_distance_vox 4.0` 은 isaac_ros_nvblox release-3.2 `nvblox_base.yaml` 값 그대로(job506 이 벤더 파일 L21 · L102~106 을 같이 찍음, `j506_d95.txt` 앞머리). 벤더 파일의 `exclude_last_view_from_decay: true` 는 우리 yaml 에 없음(시야 안 복셀은 15 Hz 로 재적분되므로 이 코스에는 영향 없음 — 판단, 측정 아님). STVL 의 로컬 120 s 도 속도식이 아니라 09-14~16 코스 실험으로 정한 값.
- 계산(측정 아님): 가중 w_n = w_max · f^n, n = 감쇠 주기 × 시간. w_max 5.0 → ESDF 최소 가중 0.1 까지 n = ln(0.02)/ln f, 자유 판정 0.001 까지 n = ln(0.0002)/ln f. f 0.95 @5 Hz → 76 회 = **15.3 s**, 166 회 = 33 s. f 0.99 → 389 회 = **78 s**, 847 회 = 170 s.
- 필요 기억 시간(계산): 상자가 화각을 벗어나는 전진 0.31~0.35 m(BASELINE ⑥)부터 로버 뒤끝이 상자 뒤끝(1.26)을 지나 복귀 회전을 마치는 전진 ≈ 1.6~1.8 m 까지 1.3~1.5 m. 평균 0.07 m/s(2.2 m/31 s) → 19~21 s, 상자 옆 최저 0.05 m/s → 26~30 s, 안전계수 2 → **≥ 60 s**.
- 정지 측정(job506, 절단 2.0): 32 s 적분 뒤 t = 5 s 에 `enable_depth false`(IMU · odom 유지).

  | 감쇠 | 상자 구역 ≤0 셀(시각) | 0 이 된 시각 → 관측 끊김 후 | 그 뒤 | 깊이 복구 뒤 |
  |---|---|---|---|---|
  | 0.95 | 13(t 0~10) → 12(11~17) → 10~11(18~21) | **t = 22 s → 17 s** | 구역 120 셀 전부 미지, t = 41 s 슬라이스 범위 밖(블록 해제 ≈ 36 s) | 깊이 14.9 Hz · 점군 15.1 · odom 30.8 |
  | 0.99 | 11~12(t 0~85) | **t = 86 s → 81 s** | (100 s 창 안에서 해제 미관측) | 14.95 · 15.3 · 30.6 |

  계산 15 s / 78 s 와 일치. '자유가 되는 시각' 은 두 조건 모두 관측 안 됨(셀이 자유가 되기 전에 미지 · 범위 밖으로 빠짐). 층은 미지 · 범위 밖을 NO_INFORMATION → 자유로 다루므로 0.95 였다면 주행 t ≈ 22 s 에 상자가 로컬 코스트맵에서 사라졌을 것(추정 — 0.95 로 주행하지 않아 확인 안 함).
- 결정: N2 팔 = `nvblox_n0_t2d99.yaml`(절단 2.0 + 감쇠 0.99). '감쇠 끔(rate 0)' 은 옮겨진 물체가 재관측 전까지 영원히 남아 STVL 120 s 보다 보수적 → 기각, 같은 이유로 0.995 이상도 불필요. 0.99 는 STVL 120 s 보다 짧아 '기억 의존 감소' 명분 유지.

### 4.5 N4 주행 A/B 설계(09-22 §2, 주행 전 선언)
- 비교 대상: 로컬 코스트맵 카메라 층만(전역 · NavFn · SimpleSmoother · MPPI CostCritic · 러너 동일). 정지 계획 비교는 전역이 같아 무의미 → 하지 않음.
- 회차: 같은 배치(출발 테이프, 상자 1.15 / −0.07~−0.10)에서 S → N2 → S → N2 → N2. 회차마다 손 배치 → `run_mp9prep.sh`(게이트 A~D) → (N) `job508_modeN.sh`(nvblox 시작 → 32 s → Nav2 를 nvblox 층으로 → 클리어 8 s → 게이트 J · K · L, 주행 30 s 전) / (S) `job511_modeS.sh` → 사용자 "시작" → `STAGE='N4-<S|N2>' NOTE=… GIT_HEAD=… [BAG_PROFILE=nvblox] run_drive_nohup.sh n4<s|n>k 2.0 <BX> <BY> 0.06 0` → `run_post3.sh` → `run_j509_analyze.sh`.
- 판정 = BASELINE §4 그대로 + N 전용 지표: ③ 상자 자리 비용(0 이면 기억 소실), ⑥ 미관측 구간 동안 상자 셀 유지, 근거리 자취, nvblox CPU · GPU · ESDF 주기.

## 5. 조치와 효과 — N4 결과(09-22 §3 · §3.1)
| 지표 | n4s1 (S, 11:29) | n4n1 (N2, 11:48) | n4s2 (S, 12:03) | n4n2 (N2, 13:13) | n4n3 (N2, 13:47) | 기준선 cc2~cc5 |
|---|---|---|---|---|---|---|
| 결과 · 소요 · 거리 | 성공 31.6 s · 2.15 m | 성공 31.6 · 2.17 | 성공 30.9 · 2.17 | 성공 31.4 · 2.16 | 성공 32.2 · 2.24 | 4/4, 31.5 s |
| 중단 / 제어 미달 / EKF 위반(게이트 누적) | 0 / 0 / 64 | 0 / 0 / 44 | 0 / 0 / 35 | 0 / 0 / 41 | 0 / 0 / 34 | 0 / 0 / 19~39 |
| 코스트맵 상자 최소 여유(job416) cm | 9.3 @17.1 s | 12.3 @18.9 | 11.7 @16.8 | 13.4 @19.1 | **14.6** @18.6 | 8.4~12.9 |
| 복귀 회전 자리 원경로 → 실제(job446 L=3) cm | 9.4 → 9.1 | 8.3 → 8.3 | 7.2 → 8.3 | 8.1 → 9.7 | 10.2 → 13.5 | ≥ 8.1 |
| 뒤 모서리 컨트롤러 Δ L=3 / L=2 | +1.2 / −0.7 | +2.5 / −0.1 | +1.8 / +1.2 | +3.0 / +2.5 | +2.4 / −0.2 | 안으로 안 붙음 |
| 러너 ① 실제 최근접 / ② 계획 여유 cm | 13.3 / 12.3 | 10.3 / 9.1 | 13.3 / 8.9 | 12.8 / 8.6 | (27.6 / 13.6 **무효**) bag ≈ 17.5 | ① 9.4~18.0 |
| ③ 상자 자리 비용 로컬/전역 | 100/100 | 100/100 | 100/100 | 100/100 | 99/100 | 기억 소실 0 |
| ④ 좌우 전환 / 계획 접촉 | 0 / 0 % | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 |
| ⑥ 미관측 최대 s | 31.1 | 31.1 | 30.4 | 30.9 | 31.1 | 30.8~31.4 |
| 조향 부호반전 /m · 고주파 \|ω\| | 4.75 · 0.087 | 5.78 · 0.087 | 4.21 · 0.074 | 5.27 · 0.080 | 3.54 · 0.092 | 1~5.6 · 0.079~0.090 |
| nvblox 깊이 / ESDF / 지연 | — | 15.0 / 9.6 / 0.103 | — | 15.1 / 9.5 / 0.103 | 15.2 / 9.5 / 0.102 | — |
| **CPU 합**(top 전 프로세스 평균 합) · nvblox | 318 | **330** · 18.0 | 315 | **337** · 20.3 | **330** · 18.4 | ≈ 320 |
| tegra GPU 평균/최대 · tj · VDD_IN 평균/최대 | 0/0 · 49.1 · — | 2.8/10 · 50.2 · 6.80/7.98 W | 0 · 49.2 · 6.57/7.62 | 2.8/14 · 50.9 · 6.86/8.06 | 3.6/18 · 49.6 · 6.80/8.06 | 0 · 48.8 · 6.6/7.9 |
| bag 크기(tgz) | 2.7 MB | 14.6 MB | 2.7 | 14.5 | 15.2(`j507_n4n3_post.txt` 15 180 697 B) | — |

| BASELINE §4 기준 | N2 결과 | 판정 |
|---|---|---|
| 3 회 중단 0 · 미달 ≤ 1 | 0 · 0 (3/3) | 통과 |
| 코스트맵 상자 여유 ≥ 8(평균 ≥ 11) | 12.3 · 13.4 · 14.6(평균 13.4) — S 오늘 9.3 · 11.7 | 통과 |
| ①·④ 동등 이상 | ① 10.3 · 12.8 · (≈ 17.5) vs S 13.3 · 13.3, ④ 0 | 통과(n4n1 만 S 보다 3 cm 작음, 기준선 하한 9.4 안) |
| CPU 합 < 320 % | 330 · 337 · 330 vs S 318 · 315 | **불합격 — 구조적**(nvblox 18~20 % 가 더해지고 릴레이 19 · 전역 STVL 은 그대로) |
| GPU · 전력 · 온도 | GPU 평균 2.8~3.6 %(최대 18), +0.2~0.3 W, tj +1~2 °C | 통과 |
| (추가) ③ 기억 | 100 · 100 · 99 | 통과(감쇠 0.99 결정) |
| (추가) 근거리 자취 | 게이트 L 0/86~104 프레임(정지). 주행 중 지표 없음 | 정지 기준 통과 |

- 읽기(09-22 §3.1): 지도 품질 · 주행 안전 지표는 모두 기준선 이상, 실패는 CPU 하나이고 원인은 nvblox 가 아니라 "STVL + 릴레이를 아직 못 뺐다" 는 구조. 권고 (a) 로컬 nvblox 채택 + 전역 이전 계획(CPU −40 %p 기대: 릴레이 19 + STVL 갱신분 — **기대치**), (b) CPU 기준을 문자 그대로 적용해 STVL 유지 → **사용자 결정 (a)**. 이 '−40 %p 기대' 는 N6 에서 확인되지 않았다(CPU 320~325, STVL 과 동등 — `nvblox-n6-global-ghosts.md`).
- 채택 구성: 컨테이너 `ros2 run nvblox_ros nvblox_node --params-file /tmp/nvblox_n0_t2d99.yaml` → 저장소 [`nvblox_local.yaml`](../../ros2_ws/src/rover_navigation/config/nvblox_local.yaml), 층 이진 + inflation 0.40/2.5, 절차 v2.0(게이트 J · K · L · `BAG_PROFILE=nvblox`). 구성 전환(launch 기본값)은 N6-0.
- **지금 저장소와 대조(10-30, 이 카드 작성 때)**: `nvblox_local.yaml` 은 지금도 `projective_integrator_truncation_distance_vox: 2.0`(L58) · `tsdf_decay_factor: 0.99`(L70) · `tsdf_decayed_weight_threshold 0.001` · `decay_tsdf_rate_hz 5.0` · `esdf_integrator_min_weight 0.1` · `global_frame odom` · 복셀 0.05 · 통합 2.0 m(L57, 중간에 1.4 였다가 10-22 에 2.0 복귀) · 슬라이스 z **0.06**~0.30(L68, 09-22 N6-1 에 0.03 → 0.06). `nav2_params.yaml` `nvblox_layer` 는 로컬 L331~338 · 전역 L564~571 모두 `convert_to_binary_costmap: true` · `max_obstacle_distance 0.40` · `inflation_distance 0.175`. 즉 이 카드의 절단 · 감쇠 결정은 **그대로 운용 중**이고, 기억 시간 81 s 는 당시 코스(0.07 m/s, 1.3~1.5 m 미관측 구간)로 계산한 값이다 — 10 월 순회 코스의 미관측 구간에 맞는지는 다시 계산한 기록이 없다(§7). ⚠ 같은 파일 머리 주석 중 L6 "아직 bringup(launch)에 통합되지 않음: … 로컬 plugins 기본값은 STVL" 과 L12 "슬라이스 … 최소 0.03" 은 09-22 채택 시점 문장이 남은 것으로, 지금 값(launch 기본 nvblox, 하한 0.06)과 다르다(값은 맞고 주석만 낡음 — 이 카드에서 고치지 않음).

## 6. 내 실수
### 6.1 디시메이션이 점군에만 걸린다고 적은 설정 주석 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | nvblox 입력(깊이 이미지)의 해상도를 정해 `nvblox_n0.yaml` 을 쓰기 |
| 본 것 | 09-21 §5(S2)의 표현 "디시메이션 4 … 점군에" 를 그대로 믿고 yaml 머리에 "dec 4 는 점군에만 적용 — 깊이 이미지는 원해상도" |
| 처음 추론 | 깊이 이미지는 640×480 그대로일 것 |
| 의심한 이유 | job475 가 깊이 이미지 폭 · 높이를 찍어 보니 **160×120 16UC1**(`j475_sensors.txt`) |
| 판별 | job481/483 에서 `decimation_filter.filter_magnitude` 를 4 · 2 · 1 로 바꿔 160×120 · 320×240 · 640×480 확인(`j483_n0_variants2.txt` "깊이 이미지: …") |
| 결론 | realsense-ros 의 디시메이션은 깊이 스트림 자체를 줄인다. S2 §5 의 문구도 틀림(09-21 §9 굵은 글씨 정정). N0 표의 '160×120' 이 기본 운용 조건 |
| 다음에 알아보는 법 | 입력 해상도는 문서 · 기억이 아니라 `ros2 topic echo <img> --once --field width/height` 로 먼저 잰다. 정정은 SUMMARY 에만 적지 말고 **틀린 문장이 있는 설정 파일 주석도 같이 고친다** — 09-21 에는 SUMMARY 만 고쳐서, 운용본 `nvblox_local.yaml` 머리에 같은 틀린 주석이 복사돼 남았고 **10-19 §1 에 같은 사실을 처음 발견처럼 다시 재서**(`chk_depth_topic.sh`, 160×120 · 581 KB/s) 주석을 고쳤다(지금 L9~10 "⚠ 2026-10-19 정정(실측)"). `2026-09-21/jobs/nvblox_n0.yaml` · `2026-09-22/jobs/nvblox_n0_t2*.yaml` 기록 사본은 틀린 문장 그대로 |
| 데이터 | `2026-09-21/outputs/j475_sensors.txt` · `j483_n0_variants2.txt` · 도구 `jobs/job475_sensors.sh` · `job483_n0_variants2.sh` |

### 6.2 N0 변형 측정 1 차의 두 절차 사고 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 복셀 0.03 · 입력 해상도 3 조건을 차례로(job481) |
| 본 것 | 재시작한 노드가 깊이 1 프레임 뒤 멈춰 슬라이스 0 프레임(`j481_n0_variants.txt` "슬라이스 0 프레임 … ros/update_esdf 1 0.0") |
| 처음 추론 | (재시작 실패) |
| 의심한 이유 | `pkill -f nvblox_node` 패턴이 `docker exec … bash -lc '…nvblox_node…'` 라는 **자기 셸 명령줄**에도 맞아 먼저 자기를 죽이고 옛 노드가 남음(`j482_state.txt` 로 프로세스 확인). 2 차 첫 판에선 통계 로그의 Rates 블록 뒤 Delays 블록의 같은 이름 줄(0.064 s)을 rate 로 읽어 '깊이를 안 받음' 으로 오판 |
| 판별 | 실행 파일 경로 `^/opt/ros/humble/lib/nvblox_ros/nvblox_node` 로 PID 를 찾아 INT → KILL, 사라짐 확인 뒤 시작, 30 s 뒤 `grep -A7 "NVBlox Rates"` 의 `ros/depth_image_callback` ≥ 10 Hz 확인 후에만 측정(job483) |
| 결론 | 2 차에서 4 조건 측정 완료. 이 정지 · 시작 · 확인 패턴은 job501 · job506 · job508 · job511 · 게이트 J(절차 v2.0 표 J "Rates 헤더 뒤 7 줄만")로 이어졌고 N6-0 `nvblox_up.sh` 로 자동화 |
| 다음에 알아보는 법 | `pkill -f <이름>` 은 그 이름을 인자로 가진 셸 · ssh · docker exec 명령줄까지 죽인다 — 실행 파일 절대 경로 앵커(`^/…/bin`)로. 통계 로그는 블록 머리로 잘라 읽는다. 같은 이유로 `job497_endstate.sh` 는 `grep 'nvblox_nod[e]'` 를 쓰고 Jetson 측 파일로 만들었다 |
| 데이터 | `2026-09-21/outputs/j481_n0_variants.txt` · `j482_state.txt` · `j483_n0_variants2.txt` · 도구 `jobs/job481_n0_variants.sh` · `job483_n0_variants2.sh`(머리 주석에 두 사고 기록) |

### 6.3 '통로 창이 0.10 으로 좁아졌다' — 과도 상태를 결과로 읽음 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 정지 A/B(§10.2)에서 nvblox 층의 통과 폭 판정 |
| 본 것 | job248 감사 기준1 0.10 m(@1.20) · RPP 0.00, 3 표본 동일(`j488_layer_ab.txt` B 절) |
| 처음 추론 | "nvblox 이진 층은 관측된 모든 표면을 치명으로 올려 통로 창이 좁아졌다" — 안전 이득인지 과다 마킹인지 셀 대조가 필요하다고까지 적음 |
| 의심한 이유 | 같은 표본의 10 cm ASCII 로는 x 1.2 의 자유 띠가 STVL 0.4 · nvblox 0.3 으로 1 셀 차이뿐 — 감사 0.10 과 맞지 않음(§10.2 스스로 "불일치는 job248 기준식을 다시 읽어 해소할 것") |
| 판별 | 같은 배치 재캡처(§10.3 `run_j490.sh`) |
| 결론 | 두 번째 표본 0.40 · 0.25 → 0.10/0.00 은 **Nav2 재기동 · 클리어 직후 층이 재적분 중인 과도 상태**(§10.3 정정). 기전(왜 3 표본 연속 같은 0.10 인지)은 미확인 |
| 다음에 알아보는 법 | 층을 바꾸거나 클리어한 직후의 감사는 ≥ 20 s 두고 잰다(절차 v2.0 §4-10). 09-22 n4n2 러너 게이트에서 같은 '기준1 0.10' 이 재현됐지만 러너는 그 값을 게이트로 쓰지 않아 영향 없음(09-22 §3) |
| 데이터 | `2026-09-21/outputs/j488_layer_ab.txt` · `j489_nvblox_mode.txt` · `j490_griddump.txt` · `2026-09-22/outputs/j507_n4n2_drive.txt` |

### 6.4 '기울기 모드로 띠를 다룬다' — 코드 안 보고 제안 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 절단 띠를 줄이는 방법 제시(§10.3 결론) |
| 본 것 | 층 파라미터에 `inflation_distance` · `max_obstacle_distance`(기울기 모드) 가 있음 |
| 처음 추론 | "N4 전에 절단 4 → 2 또는 A/B-2(거리 → 비용 기울기) 중 하나" — 기울기 모드가 띠 비용을 바꿀 수 있다고 봄 |
| 의심한 이유 | 사용자 질의("어떻게 해결할 것인가")에 답하려고 코드를 읽음 |
| 판별 | `updateCosts()` L186~188(`j492_layersrc.txt`) |
| 결론 | `distance <= 0 → LETHAL` 이 `convert_to_binary_costmap_` 분기 **앞**이라 기울기 모드는 표면 앞쪽(거리 > 0)만 바꾼다. 띠 손잡이는 nvblox 쪽 절단 거리뿐(§10.4 정정) |
| 다음에 알아보는 법 | 파라미터 이름으로 효과를 추정하지 말고 그 파라미터가 쓰이는 분기를 먼저 읽는다(층 소스는 300 줄) |
| 데이터 | `2026-09-21/outputs/j492_layersrc.txt` · 도구 `jobs/run_j492.sh` |

### 6.5 절단 A/B 선언 기준의 전제 오류(T3 · T6) — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 절단 4 → 2 를 측정 전 선언한 T1~T6 로 판정 |
| 본 것 | T3(nvblox 만 −40 %) · T6(표면 x 열 −10 % 이내) 불합격(`j502_eval.txt`) |
| 처음 추론 | (선언 규칙대로면 4.0 유지) |
| 의심한 이유 | 'nvblox 만' 의 절반이 좌측 가구였고 두 조건에서 45 · 46 으로 같았다 — 절단과 무관한 셀이 섞임. T6 의 x 열은 띠가 x 방향으로 자라는 것과 섞임 |
| 판별 | 구역 · 거리 · 껍질/안쪽 분해(`j502b_shell.txt`), 사라진 열의 위치(`j502c_holes.txt`) |
| 결론 | 좌측 가구 = STVL 카메라 범위 1.2 m 밖 · 사라진 열 = 통합 2.0 m 끝, 안쪽 구멍 1 개(x 1.55, 5 cm). 2.0 채택 — **데이터를 본 뒤의 정정이라 선언보다 약함**(SUMMARY 스스로 기록) |
| 다음에 알아보는 법 | 셀 수 기준은 '그 변수가 바꿀 수 있는 구역' 으로 먼저 한정해 선언한다(두 지도의 관측 범위 · 높이 범위가 다르면 차이 셀의 대부분이 범위 차이다). 연속성 기준은 '끝(범위 경계)' 과 '안쪽 구멍' 을 나눠 선언 |
| 데이터 | `2026-09-22/outputs/j502_eval.txt` · `j502b_shell.txt` · `j502c_holes.txt` · `grid_{stvl3,t4,t2}_*.json` · 도구 `jobs/job502_trunc_eval.py`(b · c 는 도구 원문 없음 — §6.9) |

### 6.6 감쇠를 벤더 기본값으로 복사 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | N0 정지 측정용 yaml(09-21)을 만들고 그대로 N4 주행에 쓰려 함 |
| 본 것 | 사용자 질의 "감쇠값은 로버 속도에 맞춰 계산한 것인가" |
| 처음 추론 | (질의 전에는 검토 안 함 — 09-22 §2 사전 가설에서 0.95 → 소실 가능성을 '첫 N2 회차로 측정' 하려 했음) |
| 의심한 이유 | 출처를 보니 벤더 `nvblox_base.yaml` 값 그대로 — 정지 측정용으로 옮길 때 속도 · 코스와 무관하게 복사 |
| 판별 | 필요 기억 시간 계산(≥ 60 s) + 정지 깊이 차단 측정(job506: 0.95 → 17 s, 0.99 → 81 s) |
| 결론 | 0.95 로 첫 N2 를 돌았다면 t ≈ 22 s 에 상자가 사라져 복귀 회전에서 뒤 모서리를 스칠 수 있었다(추정 — 안 돌았으므로 미확인). 주행 전에 0.99 로 바꿈 → N4 ③ 100/100 |
| 다음에 알아보는 법 | 상류 예제 값을 옮길 때는 **시간 상수가 있는 파라미터**(감쇠 · 지속 · 시간 초과)마다 '이 코스에서 필요한 시간' 을 계산해 옆에 적는다. 주행으로 확인하려던 가설은 주행 전에 정지 측정(입력 차단)으로 잴 수 있으면 먼저 잰다 |
| 데이터 | `2026-09-22/outputs/j506_d95.txt` · `j506_d99.txt` · 도구 `jobs/job506_decay.sh` · `job506_decay.py` · 설정 `jobs/nvblox_n0_t2d99.yaml` |

### 6.7 게이트 L 문턱 10 → 8(데이터를 본 뒤) — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | n4n2 전 모드 N 게이트(J · K · L) |
| 본 것 | 배치 1.155 / −0.099 에서 슬라이스 상자 띠 셀 9/프레임, 두 번 동일 → 문턱 10 불합격(`j508_n4n2_prepN.txt`). 앞면 +0.4 셀 · 근거리 0/86 · J · K 통과 |
| 처음 추론 | (게이트 불합격 → 주행 안 함) |
| 의심한 이유 | 문턱 10 은 절단 4.0 시절(20 셀) · n4n1(12)을 보고 정한 값. 절단 2.0 의 기하 기대값은 폭 4 셀 × 띠 2~3 셀 = 8~12 |
| 판별 | 기하 계산만(측정 추가 없음) |
| 결론 | ≥ 8 로 정정(사용자 승인 12:18, job505 · 절차 v2.0 §3 L). 근거 강도는 선언보다 약함 |
| 다음에 알아보는 법 | 셀 수 문턱은 그 셀을 만드는 설정(절단 · 복셀 · 슬라이스 높이)이 바뀌면 다시 계산한다. ⚠ 저장소 `2026-09-22/jobs/job505_modeN_gate.sh` 는 **정정 뒤 판(≥ 8)** 이고, `j508_n4n2_prepN.txt` 의 '불합격' 은 정정 전 판(≥ 10)의 출력이다 — 같은 출력을 지금 판으로 다시 판정하면 통과 |
| 데이터 | `2026-09-22/outputs/j508_n4n2_prepN.txt` · 도구 `jobs/job505_modeN_gate.sh` |

### 6.8 그 밖의 작은 실수 · 결함(표)
| 무엇 | 본 것 | 영향 · 처리 | 데이터 |
|---|---|---|---|
| n4n3 러너 ①② 무효 | t = 1.1 s 재고정이 상자 모델을 전면 1.096 · 중심 **−0.200**(게이트 −0.089 에서 11 cm 우측)으로 옮김, 깊이점 최대 173(다른 회차 263~352) — yaw ±5° 조건만 보고 위치 이탈을 안 봄 | ① 27.6 → bag 기준 ≈ 17.5 로 대체. TODO(러너 job125) → N6-2 에서 `REFIX_MAX 0.06` 으로 수정(PHASE_N_RESULTS §1 N6-2) | `2026-09-22/outputs/n4n3_refix.csv` · `j507_n4n3_drive.txt` |
| run_j509 를 post 와 한 셸에서 이어 부름 | nav2 로그 파일이 아직 없어 epoch 추출이 비어 D · E · A 실패. 처음 적을 때 heredoc 백틱이 명령 치환돼 파일명이 빈 칸 | 따로 불러 재실행(`j509_n4n1_analysis.txt` 는 재실행분) | `2026-09-22/outputs/j509_n4n1_analysis.txt` |
| run_drive_nohup.sh 의 옛 scratchpad 경로 | n4s1 에서 `job315_boxcells.py` 를 못 찾는 경고 — 러너가 09-17 세션의 scratchpad(`82ce61d4…`)에서 파일을 올림. Jetson `/tmp` 에 파일이 있어 게이트는 정상 | 옛 scratchpad 에 복사해 해소. 그 scratchpad 는 09-28 자동 소실 — 지금 이 러너는 그대로 못 씀 | 09-22 §3 n4s1 읽기 |
| n4s2 prep 직후 모드 | prep 이 Nav2 를 설치 YAML(그때 nvblox 층 상태)로 띄워 옛 odom 지도를 가진 nvblox 가 상자 셀 최대 y −0.025 · 창 0.330 을 냄 | 절차 v2.0 §4-9(prep 뒤 nvblox 재시작)의 근거가 실제로 재현. job511 로 STVL 복귀 · 클리어 뒤 정상(0.023 · 0.282) | `2026-09-22/outputs/j511_n4s2_prepS.txt` · `j510_prep_n4s2.txt` |
| job315 가 job488 안에서 인자 없이 불림 | 09-21 job488 실행 4 회 모두 `IndexError: list index out of range` | '센서 점 8 cm 근거' 수치는 job248 감사 줄에서 나온 것. STVL 쪽은 감사 줄도 없어 '(감사 출력 누락)' | `2026-09-21/outputs/j488_layer_ab.txt` · `j493_ab_nvfix.txt` |
| job485 의 플러그인 등록 확인 | "pluginlib 등록: (package.xml export 없음)" — grep 패턴을 `nav2_costmap_2d plugin=` 으로 찾았는데 실제 export 는 `<costmap_2d plugin="${prefix}/nvblox_costmap_layer.xml" />` | job486 으로 export · ament_index 리소스 · 클래스 이름 확인(등록 정상) | `j485_hostbuild2.txt` · `j486_pluginchk.txt` |

### 6.9 SUMMARY · PHASE_N_RESULTS 와 원문이 다른 곳(이 카드 작성 때 대조)
1. **`2026-09-21/jobs/job489_gridcmp.py` 는 JSON 덤프 없는 앞 판**이다. §10.3 이 "job489_gridcmp.py(JSON 덤프 추가)" 라고 쓴 판은 `2026-09-22/jobs/job489_gridcmp.py` 에만 있다(diff: JSON 2 줄 + TOPIC 인자). 09-21 의 `grid_*.json` 을 다시 만들려면 09-22 판을 써야 한다.
2. **`j502b_shell.txt` · `j502c_holes.txt` 를 만든 도구가 저장되지 않았다.** 09-22 §1.1 머리는 "평가 `jobs/job502_trunc_eval.py` → `j502_eval.txt` · `j502b_shell.txt` · `j502c_holes.txt`" 라고 쓰지만 job502 는 `j502_eval.txt` 내용만 찍는다(껍질 · 구멍 분석 코드 없음). 이 두 파일(정정 분석의 핵심 근거)의 도구는 **원문 없음** — PC 에서 즉석으로 돌린 것으로 보인다(추정).
3. **§10.2 표의 STVL 값 출처**: "LETHAL 207 / 62" · "기준1 0.40 / RPP 0.25" 는 `j488_layer_ab.txt` 의 STVL 절이 아니라 `j489_stvl_mode.txt` 에 있다(j488 STVL 절은 감사의 '상자:' 줄만 3 개, 최소폭 · 로컬 줄 없음). 값은 맞다.
4. **'CPU +18~20 %p' 표현**: 09-22 §3.1 표는 "330 · 337 · 330 vs S 318 · 315 (nvblox +18~20 %p …)" — 18~20 은 nvblox **프로세스** CPU 이고, CPU **합**의 차는 같은 날 S 대비 +12~22 %p(330 − 318 = 12, 337 − 315 = 22). 계획서 09-22 절의 "CPU +12~19 %p" 도 상한이 다르다. CPU 합을 계산한 도구는 jobs 에 없다(top 로그 `top_n4*.log` 에서 즉석 계산 — 원문 없음). `job512_trajviz.py` 는 이 값들을 상수(`CPU = {...}`)로 박아 그린다.
5. **'뒤 모서리 Δ +2.5~3.0 은 상자 뒤끝 1.30 vs 1.25 때문' 의 크기**: PHASE_N_RESULTS §2 · 09-22 §3 은 정지 절단 A/B 의 뒤끝(t2 1.30, STVL 1.25)으로 설명하지만, **주행 중** job416 이 본 로컬 코스트맵 상자 LETHAL 셀 중심 범위는 N2 가 x 1.175~1.375(n4n2 · n4n3, 셀 뒤 가장자리 1.40), n4n1 은 1.175~**1.575**, S 는 1.075~1.225(n4s1) · 1.125~1.275(n4s2)였다(`j509_n4*_analysis.txt` D 절). 즉 주행 중 N2 상자는 정지 t2(1.30)보다 10~30 cm 더 깊었다. 설명의 방향(N2 상자가 뒤로 더 깊다)은 맞지만 크기는 다르고, 왜 주행 중 더 깊어지는지(지나가며 다른 각도에서 본 면의 띠가 쌓임? 같은 구역 안 다른 물체?)는 **미확인**.
6. **PHASE_N_RESULTS §1 N0 행 "GPU ≤10 % · CPU 16~21 %"** 와 SUMMARY §9 는 일치. §4 "슬라이스 z 0.03~0.30 · 통합 2.0 m" 는 N4 당시 값(지금 슬라이스 하한은 0.06 — §5 대조).
7. **`job473_nvblox_run.sh` 09-22 판의 `start [yaml]` 인자는 동작하지 않는다(코드 읽기).** `--params-file /tmp/${2:-nvblox_n0.yaml}` 이 호스트 쪽 작은따옴표 안에 있어 호스트는 `$2` 를 펼치지 않고, 컨테이너 안 `bash -lc` 에는 위치 인자가 없으므로 언제나 `nvblox_n0.yaml`(절단 4.0 · 감쇠 0.95)을 읽는다. 09-22 §1.1 · §2 는 이 인자를 절차로 적었지만 실제 측정 · 주행은 각자 nv_start 를 가진 job501 · job506 · job508 이 했고(실효값 `ros2 param get` 2.0 · 0.99 확인, `j501b_t2.txt` · `j508_*`), 이 인자가 실제로 쓰였는지는 **미확인**. N6-0 이후 `nvblox_up.sh`(큰따옴표)로 대체.
8. **`run_deploy_nv.sh` 머리 주석**은 "CostCritic 교체 (09-18 §17)" · 백업 폴더 `.bak_20260918` — 09-18 배포 스크립트를 복사해 내용만 바꾼 흔적. 실제로 배포한 것은 `nav2_params_0921nv.yaml`(nvblox_layer 블록 추가, `j487_deploy_nv.txt` diff).

## 7. 남은 것
1. **CPU**: 로컬만 바꾼 이 단계의 +12~22 %p 는 '구조적' 으로 처리됐고 N6 에서도 절감은 없었다(→ `nvblox-n6-global-ghosts.md`). nvblox 채택 근거는 CPU 가 아니라 여유 · 기억 · 3D/GPU 경로로 바뀌었다(계획서 N6 판정).
2. **기억 시간의 코스 의존**: 0.99(81 s)는 09-22 코스(평균 0.07 m/s, 미관측 1.3~1.5 m)로 계산한 값. 10 월 순회(F2) 코스에서 '상자를 화각에서 놓친 뒤 다시 지날 때까지' 시간과 대조한 기록은 이 카드 범위에서 못 찾음.
3. **이진 모드만 사용**: 계획서 09-14 §1 · §4 가 꼽은 nvblox 장점 '연속 거리장(ESDF)을 비용으로' 는 쓰지 않았다(`convert_to_binary_costmap: true` 지금도). 기울기 모드 A/B(A/B-2)는 하지 않음.
4. **절단 띠의 비관측 가정**: '표면 뒤 0.10 m 는 막힘' 은 얇은 물체(상자)에선 과대, 깊은 가구에선 과소. 포크 규칙 변경(④)은 미시행.
5. **슬라이스 높이**: 0.30 → 0.40(가구 윗부분, STVL 과 맞춤)은 N6-2 후보로 넘김(PHASE_N_RESULTS §5-3).
6. **주행 중 근거리 자취 지표 없음**: 정지 게이트 L 만. bag 에 슬라이스가 있어(`BAG_PROFILE=nvblox`) 사후 계산 가능.
7. **§6.9-5 주행 중 상자 깊이**의 원인 미확인 — bag `2026-09-22/bags/bag_n4n*.tgz` 의 슬라이스로 시간별 상자 띠 범위를 그려 보면 판별 가능.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 데이터 |
|---|---|---|
| n0a · n0a_pess | N0 정지 160×120 / 0.05, 30 s · pessimistic 10 s | `2026-09-21/outputs/j474_n0a.txt` |
| v03_dec4 · v05_dec2 · v05_dec1 · v05_dec4 | N0 변형(복셀 0.03, 입력 320×240 · 640×480, 복귀) | `j481_n0_variants.txt`(실패판) · `j483_n0_variants2.txt` |
| stvl_mode · nvblox_mode | 정지 A/B 1 차 | `j488_layer_ab.txt` · `j489_{stvl,nvblox}_mode.txt` |
| stvl · nvblox | 정지 A/B 2 차(JSON) | `j490_griddump.txt` · `grid_{stvl,nvblox}_costmap.json` · `grid_nvblox_slice.json` |
| stvl2 · nvfix | floor 수정 후 | [round→floor 카드](nvblox-layer-round-floor.md) |
| stvl3 · t4 · t2 | 절단 A/B | `2026-09-22/outputs/j501a_t4.txt` · `j501b_t2.txt` · `j501_ab_t{4,2}.txt` · `grid_{stvl3,t4,t2}_*.json` · `nvblox_t{4,2}.log` · `j502*.txt` |
| d95 · d99 | 감쇠 정지(깊이 차단) | `j506_d95.txt` · `j506_d99.txt` |
| n4s1 · n4s2 (S) / n4n1 · n4n2 · n4n3 (N2) | N4 주행 | `j507_<이름>_drive.txt` · `_post.txt` · `j508_<이름>_prepN.txt` · `j509_<이름>_analysis.txt` · `j510_prep_<이름>.txt` · `j511_n4s2_prepS.txt` · `<이름>.csv` · `_refix.csv` · `nav2_` · `top_` · `tegra_` · `rss_` · `meta_` · `params_` · `nvblox_n4n*.log` · `drive_<이름>_remote.log` · bag `2026-09-22/bags/bag_<이름>.tgz`(로컬, git 제외) |
| 그림 | v1 · v2 층 비교, 절단 A/B, N4 궤적 | [`figures/`](../05_nvblox/figures/) 의 `2026-09-21_costmap_*` · `2026-09-22_truncation_4_vs_2.html` · `2026-09-22_n4_trajectories_stvl_vs_nvblox.html`(= `j503_trunc_ab.html` · `j512_n4_traj.html`) |

## 9. 도구 해설
**공통**: `run_*.sh` 는 PC(WSL) 래퍼 — 그날 PC scratchpad(`…/21d4aa9f…/scratchpad` 또는 09-17 세션 `…/82ce61d4…/scratchpad`)의 파일을 `tr -d '\r'` 로 CRLF 를 빼 `/tmp` 에 쓴 뒤 `sshpass -p <PW> scp` 로 Jetson(그때 `JETSON_HOST` 기본 192.168.0.101 — 지금은 192.168.0.110)의 `/tmp` 에 올리고 `ssh … "bash /tmp/jobNNN …"` 로 실행. scratchpad 는 자동 삭제돼 **지금은 래퍼가 원본을 못 찾는다** — 저장소 `jobs/` 사본이 유일. 컨테이너 안 실행은 모두 `docker exec -u admin --workdir /workspaces/isaac_ros-dev isaac_ros_dev-aarch64-container bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; …"`(호스트와 같은 UDP 전용 프로파일을 `/tmp` 공유로).

**도구 계보**
- 컨테이너 · nvblox 기동: `job468`(작업 공간 · 이미지 빌드) → `job470`/`job471`(TERM 문제) → `job472`(상주 컨테이너 · apt) → `job473`(노드 start/stop) → `job481` ✘ → `job483`(실행 파일 PID 방식) → `job499`(재부팅 복구 `docker start`) → `job501` · `job506` · `job508`(각자 nv_start) → N6-0 `ros2_ws/src/rover_navigation/scripts/nvblox_up.sh`(다른 카드).
- 측정: `job474_n0_measure.py`(슬라이스 (i)(ii)(iii)) → 게이트 L(`job505` 가 8 s 로 부름) · 절단 A/B(`job501` measure). 물리 상자: `job478_boxphys.py`(카메라 점군) ↔ 기존 `job248_audit.py`(감사, BOX_HINT).
- 층 A/B: `job488_layer_ab.sh`(09-21 sed 판 → 09-22 launch 인자 판) + `job489_gridcmp.py`(ASCII → JSON) → `job491`/`job494`/`job503`(그림) · `job502`(절단 판정).
- 주행: `run_drive_nohup.sh`(PC) → Jetson `job254_s4run.sh`(게이트) → `job231_drive.sh`(bag · top · tegrastats · rss · 러너 `job125_avoid3.py` · 메타 `job453_runmeta.sh`) → `run_post3.sh`(회수, 내부 `job379_navevents.sh`) → `run_j509_analyze.sh`(job416 · job446 · job462 · job431b) → `job512_trajviz.py`.

### 9.1 사전 조사 · 설치 · 빌드 확인(작은 도구 묶음)
| 도구 | 실행 · 인자 | 하는 일 | 출력 | 비고 |
|---|---|---|---|---|
| `job464_n0probe.sh` | Jetson, 없음(읽기 전용, sudo 없음) | L4T · JetPack · CUDA · docker · nvidia 런타임 · 이미지 · 디스크 · 메모리 · nvpmodel · nvcr.io/github/isaac apt/문서 사이트 curl 응답 · 기존 isaac 흔적 · realsense 패키지 · 커널 | `j464_n0probe.txt`: R36 REVISION 5.0, JetPack 패키지 미설치(none), 호스트 CUDA 없음, Default Runtime nvidia, 193G/233G | 계획서 09-14 N1(job316)과 같은 질문을 설치 직전에 다시 |
| `job465_n0probe2.sh` | Jetson, 없음 | 루트 디스크 · NVMe 모델, git-lfs 유무, `ISAAC_ROS_WS`, `/dev/shm`, daemon.json, nvcr.io 작은 이미지 익명 풀 시험(60 s) 후 삭제, 깊이 토픽 존재, 온도 | `j465_n0probe2.txt` | 익명 풀 OK 가 '컨테이너 방식 가능' 근거 |
| `job468_n0_setup.sh` | Jetson, 없음 — **사용자 승인 sudo**(파일 안 비밀번호는 `<PW>` 로 가려짐) | 센서 · SLAM · Nav2 내림(에이전트 · RSP 유지) → `apt-get install git-lfs` → `~/workspaces/isaac_ros-dev/src` 에 isaac_ros_common release-3.2 클론 · `ISAAC_ROS_WS` 를 ~/.bashrc 에 → `build_image_layers.sh --image_key aarch64.ros2_humble --image_name isaac_ros_dev-aarch64` 백그라운드(`/tmp/isaac_build.log`) 45 s 꼬리 | `j468_n0_setup.txt` | 되돌리기 방법이 머리 주석에 |
| `job469_buildchk.sh` | Jetson, 없음 | 빌드 프로세스 · 로그 꼬리 · 이미지 · 컨테이너 · 디스크 · Wi-Fi 수신량 | (출력 원문 없음) | 진행 확인용 |
| `job470_builddiag.sh` | Jetson, 없음 | `TERM=xterm` 으로 빌드 스크립트를 `bash -x` 60 s 전경 실행해 첫 40 줄 | `j470_builddiag.txt` | 첫 빌드가 `tput`(TERM 미설정) 실패로 `set -e` 아래 즉시 종료한 원인 확인 |
| `job471_buildstart.sh` | Jetson, 없음 | TERM=xterm 으로 빌드 재시작 · 90 s 뒤 pull 진행 grep | `j471_buildstart.txt` | 실제로는 NGC 프리빌드 층 풀(≈ 25 분) |
| `job476_cdi.sh` | Jetson, 없음 | CDI 지정(`nvidia.com/gpu=all,nvidia.com/pva=all`) 그대로 `docker run` 오류 · `/etc/cdi` · `nvidia-ctk cdi list` · 레거시 `NVIDIA_VISIBLE_DEVICES=all` 시험(장치 · libcuda 확인) | `j476_cdi.txt`: "Found 0 CDI devices" | CDI 생성(`sudo nvidia-ctk cdi generate`)은 필요할 때만으로 미룸 |
| `job475_sensors.sh` | Jetson, 없음 | N0 용 호스트 스택: sensors.launch(28 s) → slam.launch(15 s), 프로세스 수 · 깊이 이미지 Hz · frame_id · **인코딩 · 폭 × 높이** · odom→base_link · odom→camera_depth_optical_frame · EKF 위반 | `j475_sensors.txt` | 160×120 발견(§6.1) |
| `job477_nvblox_info.sh` | Jetson, 없음 | 컨테이너 안 `ros2 node info /nvblox_node` 발행 토픽, 슬라이스 토픽 Hz · 해상도, 로그의 마지막 `NVBlox Rates` 블록, tegrastats 8 s(GR3D · CPU), 컨테이너 nvblox CPU(top) | `j477_nvblox_info.txt`: 발행 토픽 12 개, pessimistic 슬라이스 9.504 Hz · 0.05, Rates 15.1/15.1/9.6/tick 101 | N0 (iii) 근거 |
| `job479_auditdbg.sh` | Jetson | `BOX_HINT='1.15 -0.10' job248_audit.py` 꼬리 12 줄 | (출력 원문 없음) | 감사가 Nav2 없이 도는지 디버그 |
| `job480_hostchk.sh` | Jetson | 프로세스 수 · `/scan` · 원시 점군 · 릴레이 점군 · 깊이 이미지 Hz · sensors.log 끝 · `job478 10` | `j480_hostchk.txt` | 물리 상자 1.153 / −0.079 출처 |
| `job482_nvblox_state.sh` | Jetson | 컨테이너 안 nvblox 프로세스 표(pid · ppid · etimes · args), 변형 로그 오류, 슬라이스 Hz, 호스트 깊이 폭 · dec 실효값 | `j482_state.txt` | job481 실패 진단(§6.2) |
| `job484_hostbuild.sh` | Jetson, 없음 | isaac_ros_nvblox release-3.2 `--depth 1` 클론(7908a18 2025-10-08) → 의존(tf2_eigen · nav2_costmap_2d · pluginlib) 확인 → `~/ros2_ws/src` 에 `isaac_ros_common` · `nvblox_msgs` · `nvblox_nav2` 심볼릭 → `colcon build --symlink-install --packages-select` 3 개 | `j484_hostbuild.txt`: `FindCUDA.cmake:859` 오류, isaac_ros_common 2.88 s 실패 | 기존 패키지 무손상 확인 줄 포함 |
| `job485_hostbuild2.sh` ★ | Jetson, 없음 | `isaac_ros_common` 심볼릭 · 빌드물 제거 → `~/ros2_ws/src/isaac_ros_common_stub/` 에 package.xml(name `isaac_ros_common`, version 3.2.5, ament_cmake) + CMakeLists(`find_package(ament_cmake)` · `ament_package()`)만 → 같은 3 개 빌드 | `j485_hostbuild2.txt`: 1.87 + 29.3 + 37.4 s = 70 s, `libnvblox_nav2.so`, msg 9 개 | 근거: nvblox_nav2 는 `ament_auto_find_build_dependencies()` 로 존재만 확인, nvblox_msgs 는 CMake 에서 isaac_ros_common 을 안 씀. 결함: 등록 확인 grep 패턴 오류(§6.8). **지금도 이 스텁 구조로 운용**(호스트 `~/ros2_ws/src`, 저장소에는 없음 — 재구성 시 이 스크립트가 유일한 기록) |
| `job486_pluginchk.sh` | Jetson | 설치된 package.xml 의 export 줄, ament_index `nav2_costmap_2d__pluginlib__plugin/nvblox_nav2` 내용, `nvblox_costmap_layer.xml` 의 name · type · base_class_type, 호스트 메시지 인식 | `j486_pluginchk.txt`: `nvblox::nav2::NvbloxCostmapLayer` / `nav2_costmap_2d::Layer` | |
| `job497_endstate.sh` 등 마감 확인 | | | | [round→floor 카드](nvblox-layer-round-floor.md) §10 |

### 9.2 job472_container.sh ★ 상주 컨테이너 · apt nvblox
- 실행: Jetson, 인자 없음(PC 래퍼 `run_j472.sh`). 호스트 변경 없음, 되돌리기 `docker rm -f isaac_ros_dev-aarch64-container`.
- 왜: Isaac ROS 의 `run_dev.sh` 는 `-it`(TTY) 전제라 ssh 비대화식에서 못 씀. 같은 인자로 `-d … sleep infinity` 상주형을 만들어 이후 `docker exec` 로 노드를 띄운다.
- 하는 일: 이미지 `isaac_ros_dev-aarch64` 확인(없으면 빌드 로그 꼬리 후 종료) → 실행 중이 아니면 `docker run -d --privileged --network host --ipc=host --pid=host --runtime nvidia -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all -e ROS_DOMAIN_ID … -v /tmp/:/tmp/ -v /usr/lib/aarch64-linux-gnu/tegra:… -v $ISAAC_ROS_WS:/workspaces/isaac_ros-dev … --entrypoint /usr/local/bin/scripts/workspace-entrypoint.sh … sleep infinity`(엔트리포인트가 NOPASSWD sudo 의 admin 사용자를 만든다) → 안에서 lsb · ROS_DISTRO · nvcc · `apt-cache policy ros-humble-isaac-ros-nvblox` → `sudo apt-get install -y ros-humble-isaac-ros-nvblox` → `ros2 pkg list | grep ^nvblox` → `DistanceMapSlice` 정의 → 호스트 `fastdds_udp_only.xml` 을 `/tmp` 로 복사(컨테이너와 공유) → `docker system df`.
- 출력: `j472_container.txt`(이미지 40.3 GB, Ubuntu 22.04.4 · humble · CUDA 12.6 · Candidate 3.2.5-0jammy, 패키지 8 개, docker 이미지 41.51 GB, 여유 155 G).
- 쓰인 곳: 09-21 §9 2 단계, 09-22 §0 복구(`job499` 가 컨테이너가 없을 때만 이것을 부름).
- 결함: `--network host --ipc=host` 라 DDS 공유메모리 경로가 열려 있음 — 같은 UDP 전용 프로파일을 공유해 SHM 을 끈 상태로 맞춤([DDS 공유메모리 사고](dds-shm-incident.md)). 컨테이너 안 apt 는 재생성하면 다시 받아야 함(그래서 09-22 는 `docker start`).
- 다시 쓸 수 있나: 예(컨테이너가 없을 때). 평소 복구는 N6-0 `nvblox_up.sh` 가 `docker start` 로.

### 9.3 job473_nvblox_run.sh ★ nvblox 노드 start / stop / status / log
- 실행: Jetson, `bash job473_nvblox_run.sh start|stop|status|log [N]`(09-22 판 `start [yaml]`).
- 하는 일: start = 컨테이너 안 `pkill -f nvblox_node`(⚠ §6.2 의 자기 셸 함정) → `docker exec -d … exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/nvblox_n0.yaml -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > /tmp/nvblox_n0.log` → 12 s 뒤 프로세스 수 · 로그 꼬리. stop = INT → 2 s → KILL. log = rate · Hz · ms · delay · drop · error 줄. status = 프로세스 수 · nvblox 토픽 목록.
- 리매핑 근거: 벤더 예제 `get_realsense_remappings` 와 같음(splitter 없음).
- 출력: `j473_start.txt`(N0 (iii)), 이후 다른 스크립트 안에서 조용히(`>/dev/null`).
- 쓰인 곳: 09-21 §9 · run_j490 · run_j493 · run_j496.
- 결함: (1) `pkill -f` 자기 셸(§6.2). (2) 09-22 판 `start [yaml]` 은 따옴표 때문에 인자가 무시됨(§6.9-7, 코드 읽기). (3) `docker exec` 가 신호를 안 넘겨 호스트 쪽에서 끝내도 노드가 남음(N6-0 에서 해결).
- 다시 쓸 수 있나: 비권장 — N6-0 이후 `navigation.launch.py camera_layer:=nvblox` → `nvblox.launch.py` → `nvblox_up.sh`. 절차 표 J 에 아직 `job473 status` 가 확인 도구로 남아 있다(`TEST_COURSE_AND_GATES.md` L61).

### 9.4 job474_n0_measure.py ★ 슬라이스 정지 측정 (i)(ii)(iii)
- 실행: **컨테이너 안** python3(`nvblox_msgs` 필요 — 이 시점엔 호스트에 없었음), `python3 /tmp/job474_n0_measure.py NAME SEC [BX BY] [TOPIC]`. PC 래퍼 `run_j474.sh NAME [SEC]`(호스트 job248 로 물리 상자를 먼저 재고 그 값을 넘김, pessimistic 슬라이스도 10 s) · `run_j474b.sh NAME SEC BX BY [TOPIC]`.
- 왜: 계획서 09-14 §5 N0 게이트 (i) 상자 가장자리 ≤ 1 셀 (ii) 근거리 자취 0/450 급 (iii) 주기 · 지연.
- 하는 일: `DistanceMapSlice`(sensor_data QoS)를 SEC + 3 s 받는다. 프레임마다 TF(슬라이스 프레임 ← base_link, 최신)로 로버 자세 → 기지 셀의 중심 `origin + (k + 0.5)·res` 를 base_link 좌표로. 거리 ≤ 0 = 장애물. (i) 상자 띠: |y − BY| < 0.14 · 0.5 < x < 2.0 의 장애물 셀 최소 x(프레임별) → 중앙 · 최소 · 최대, 물리 BX 와 차(m · 셀). (ii) 근거리: 카메라(x 0.234) 반경 0.45 m 안 · x > 0.25(앞단) · |y| < 0.5 의 장애물 셀 수 → 0 아닌 프레임 수. (iii) 수신 Hz · 간격 중앙 · 최대 · stamp 지연(수신 − header). TF 실패 프레임 수.
- 출력: `==== NAME: 슬라이스 n 프레임 (SEC s, TF 실패 n) 토픽 …` + (iii)(i)(ii) 세 줄 → `j474_n0a.txt` · `j483_n0_variants2.txt` · `2026-09-22/outputs/j501a_t4.txt` · `j501b_t2.txt` · `j508_*` (게이트 L).
- 쓰인 곳: 09-21 §9 N0 표, 09-22 §1.1 T5, 게이트 L(09-22 §2 · §3).
- 결함: 셀 중심 모서리 규약 가정([round→floor 카드](nvblox-layer-round-floor.md) §6.3). 상자 띠 폭 ±0.14 · 범위 상수가 이 코스 전용. '최소 x' 는 셀 중심이라 앞면 오차가 +0.5 셀 근처로 양자화됨(실제 +0.022~0.024 m 가 늘 '+0.4~0.5 셀').
- 다시 쓸 수 있나: 컨테이너 또는 호스트(지금은 호스트에도 `nvblox_msgs` 가 빌드돼 있음)에서 그대로. 상시 도구로는 안 옮겨짐.

### 9.5 job478_boxphys.py ★ 물리 상자(카메라 원시 점군, Nav2 불필요)
- 실행: Jetson 호스트, `python3 job478_boxphys.py [NFR=10]`. 마지막 줄 `BX BY N`.
- 왜: N0 는 Nav2 없이 돌았으므로 감사(job248)가 기대는 코스트맵 없이 물리 상자를 잴 도구가 필요. 러너 job125 의 `detect_box` 와 같은 규칙.
- 하는 일: `/camera/camera/depth/color/points` 를 base_link 로(TF 는 frame_id 별 1 회 캐시) → z 0.05~0.30 · x 0.5~1.5 · |y| < 0.5 → y 방향 1D 군집(간격 0.08, ≥ 25 점) 중 z 중앙 < 0.20 이고 진행축(|y 중앙|)에 가장 가까운 것 → x 로 정렬해 0.10 m 넘는 틈에서 쪼개 가장 큰 조각(≥ 40 점) → 전면 x = 5 백분위, 중심 y = 중앙값. 10 프레임 중앙값 · 범위.
- 출력: `상자(카메라 점군, base_link): 전면 x … 중심 y … 점 … 프레임` → `j480_hostchk.txt`.
- 결함: 군집 규칙이 '진행축에 가장 가까운 낮은 물체' 라 다른 낮은 물체가 더 가까우면 그것을 잡는다(09-10 '벽을 상자로' 사건의 교훈은 반영 — 군집을 먼저 함). 상자 높이 · 위치 상수.
- 다시 쓸 수 있나: 예(같은 점군 토픽이 있을 때 — 지금 모드 N 운용은 `camera_pointcloud:=keep` 이 기본이라 있음).

### 9.6 job481_n0_variants.sh(✘) → job483_n0_variants2.sh ★ 복셀 · 해상도 변형
- 실행: Jetson, `bash job483_n0_variants2.sh BX BY`(`run_j483.sh`).
- 하는 일(483): 조건마다 `ros2 param set /camera/camera decimation_filter.filter_magnitude DEC` → 깊이 이미지 폭 × 높이 · Hz → nvblox 정지(실행 파일 경로 `^/opt/ros/humble/lib/nvblox_ros/nvblox_node` PID 에 INT → 3 s → KILL, 남은 PID 출력) → 시작(`--params-file /tmp/<yaml>`, 로그 `/tmp/nvblox_<NM>.log`) → 32 s → `grep -aA7 "NVBlox Rates"` 의 `ros/depth_image_callback` ≥ 10 이 아니면 로그 꼬리 남기고 다음 조건 → job474(20 s, 컨테이너) 백그라운드 + tegrastats 6 s(GR3D · CPU) + top(nvblox CPU) → Rates(depth · update_esdf · depth_image_callback) · Delays(esdf_integration · depth_image_callback) · Timings(`tsdf/integrate` · `ros/esdf/integrate` 평균 ms = 합 × 1000 / 횟수). 조건: v03_dec4(`nvblox_n0_v03.yaml` 복셀 0.03) · v05_dec2 · v05_dec1 · 복귀 v05_dec4.
- 출력: `j483_n0_variants2.txt`(§4.1 표).
- 계보: 481 은 `pkill -f` · 확인 없는 측정 → 0 프레임(§6.2). 483 의 nv_stop/nv_start/depth_rate 함수가 job501 · job506 · job508 · job511 에 그대로 복사됨.
- 다시 쓸 수 있나: 예(조건 yaml 이 `/tmp` 에 있으면). 디시메이션을 바꾸므로 끝의 복귀 조건을 꼭 돌릴 것.

### 9.7 설정 파일 — nvblox_n0*.yaml
| 파일 | 내용 | 쓰인 곳 |
|---|---|---|
| `2026-09-21/jobs/nvblox_n0.yaml` | 벤더 `nvblox_base.yaml` + `nvblox_realsense.yaml` 기반. `global_frame odom` · 복셀 0.05 · `mapping_type static_tsdf` · 깊이만(색 · 라이다 없음) · 깊이 통합 40 Hz 상한 · ESDF 10 Hz · 감쇠 5 Hz · base_link 반경 3 m 밖 소거 1 Hz · 통계 출력 10 s · `esdf_mode 2d` · 슬라이스 z 0.03~0.30(odom z 는 base_link 원점 = 바닥 + 0.026 이라 바닥 제외로 0.03) · 통합 2.0 m · **절단 4.0** · 가중 `inverse_square_tsdf_distance_penalty` · 최대 가중 5.0 · ESDF 최소 가중 0.1 · max_site 2.0 · **감쇠 0.95** · 감쇠 문턱 0.001 · 자유 4.0 | N0 · 정지 A/B · 절단 t4. ⚠ 머리 주석의 '깊이 이미지는 원해상도' 는 틀림(§6.1) |
| `nvblox_n0_v03.yaml` | 위와 복셀 0.03 만 다름 | N0 (iv) |
| `2026-09-22/jobs/nvblox_n0_t2.yaml` | 절단 2.0 만 다름 | 절단 t2 · 감쇠 d95 |
| `nvblox_n0_t2d99.yaml` | t2 + 감쇠 0.99 | 감쇠 d99 · N4 팔 N2 → 저장소 `nvblox_local.yaml` 의 출발점 |

### 9.8 run_deploy_nv.sh + nav2_params_0921nv.yaml — 층 블록 배포
- 실행: PC, 인자 없음. scratchpad 의 `nav2_params_0921nv.yaml` 을 CRLF 제거 · CostCritic 포함 확인 → Jetson `/tmp` → python yaml 로 critics 목록 확인 → 설치본 대비 주석 뺀 diff → 설치본 백업(`~/ros2_ws/.bak_20260918/install_nav2_params_before_nv.yaml`) → src · install 둘 다에 복사 → md5 3 개.
- 출력: `j487_deploy_nv.txt`(diff = `nvblox_layer` 블록 8 줄, md5 7632b6e393dc × 3). Nav2 재기동 없음(다음 prep).
- 결함: 머리 주석 · 백업 폴더 이름이 09-18 판 그대로(§6.9-8). install 이 src 로의 심볼릭이면 cp 가 src 를 두 번 쓰는 셈이고, 일반 파일이면 링크가 이미 끊긴 상태 — 설치본을 직접 쓰는 이 방식은 뒤에 prep 의 `sed -i` 가 설치본 심볼릭을 일반 파일로 바꾼 문제와 같은 계열이다.
- 다시 쓸 수 있나: 아니오(파일 이름 고정). 지금은 저장소 src 가 진실이고 prep 이 배포.

### 9.9 job488_layer_ab.sh ★ 로컬 카메라 층 전환 + 정지 감사
- 실행: Jetson, `[QUICK=1] bash job488_layer_ab.sh stvl|nvblox [BX=1.15] [BY=0.10]`(`run_j488.sh` 는 job248 · job315 도 09-17 scratchpad 에서 올림).
- 하는 일(09-21 판): 설치본 `nav2_params.yaml` 의 두 줄 `plugins: ["stvl_layer", …]` / `# plugins: ["nvblox_layer", …]` 을 sed 로 맞바꿈(재빌드 없음) → 활성 줄 번호 출력 → Nav2 프로세스 TERM 6 s → KILL → `navigation.launch.py stuck_shadow:=true` 재기동 35 s → 프로세스 수 · 로그의 nvblox · plugin · error 줄 · `ros2 param get /local_costmap/local_costmap plugins` → (QUICK 이면 끝) → 로컬 클리어 10 s → job248 감사 3 표본(`^상자|로컬\[|최소폭`) → job315(⚠ 인자 없이 → IndexError) → top 20 s(controller · planner · depth_relay · nvblox · python3) → `/local_costmap/costmap` Hz.
- 09-22 판: sed 를 버리고 `navigation.launch.py … camera_layer:=$MODE`(N6-0, `/tmp/nav2_params_active.yaml` 생성), `nvblox_up.sh` 도 정지 목록에, plugins 줄에 컨테이너 nvblox 수 · 활성 yaml 머리.
- 출력: `j488_layer_ab.txt` · `j489_*_mode.txt` 앞부분 · `j493_ab_nvfix.txt` · 09-22 `j508_*` · `j511_*` 안.
- 결함: 기본 BY 0.10(양수 — 상자는 −0.09)인데 BOX_HINT 로만 쓰여 감사는 상자를 제대로 잡았다. 설치본 sed 는 설치본이 src 로의 심볼릭이면 src 를 바꾼다. Nav2 재기동마다 롤링 창 원점이 바뀌어 셀 정렬이 캡처마다 다르다.
- 다시 쓸 수 있나: 09-22 판만(절차 v2.1 §2-2N 이 '모드 S 대조군 또는 전환만 할 때' 로 남김).

### 9.10 job501_trunc_ab.sh ★ 절단 A/B 묶음 + run_j501.sh
- 실행: Jetson, `bash job501_trunc_ab.sh BX BY a|b`(ssh 10 분 한도 때문에 a: STVL + t4, b: t2 + 복귀로 나눔). PC `run_j501.sh BX BY PHASE` 가 job501 · job488 · job489 를 올리고 JSON · 감사 · nvblox 로그 회수.
- 하는 일: (a) 현재 plugins 확인 → 로컬 클리어 12 s → `job489 stvl3 0` → nv_stop · nv_start `nvblox_n0.yaml` t4 → 32 s → 깊이 콜백 ≥ 10 확인(아니면 중단) → `QUICK=1 job488 nvblox` → 클리어 → 감사 3 표본(`tee /tmp/j501_ab_t4.txt`) → `job489 t4 1` → measure(job474 20 s + tegrastats 6 s + top + Rates/Delays). (b) nv_stop · nv_start `nvblox_n0_t2.yaml` t2 → 32 s → 확인 → **절단 실효값 `ros2 param get /nvblox_node static_mapper.projective_integrator_truncation_distance_vox`** → 클리어 → 감사 → `job489 t2 1` → measure → `QUICK=1 job488 stvl` · nv_stop.
- 출력: `j501a_t4.txt` · `j501b_t2.txt` · `j501_ab_t{4,2}.txt` · `grid_{stvl3,t4,t2}_*.json` · `nvblox_t{4,2}.log`.
- 결함: t4 와 t2 사이 Nav2 를 재기동하지 않고 nvblox 만 바꿨으므로 두 조건의 코스트맵 격자 정렬은 같다(좋음). STVL 캡처는 a 단계 처음 한 번뿐.
- 다시 쓸 수 있나: yaml 두 개가 `/tmp` 에 있고 job488 이 09-22 판이면 예.

### 9.11 job502_trunc_eval.py ★ 절단 A/B 판정
- 실행: PC python, `python job502_trunc_eval.py <dir> [BX=1.153]`.
- 하는 일: 세 JSON 을 floor 5 cm 스냅 → LETHAL 집합(코스트맵 ≥ 100, 슬라이스 ≤ 0). 구역 규칙(job491 과 같음). 조건별: 층 LETHAL 수 · 슬라이스 ≤0 수 · STVL 대비 둘 다 / nvblox 만(구역별) / STVL 만 · 상자 외곽(층 · 슬라이스) · 앞면 셀 · 깊이(외곽 x 범위) · 표면 연속성 = 우측 벽 · 좌측 가구 구역의 슬라이스 LETHAL 이 있는 x 열 수 · y 행 수. T1 = 앞면 t4 == t2 == floor(BX/0.05)·0.05, T2 = t2 깊이 ≤ 0.15, T3 = t2 nvblox 만 ≤ 0.6 × t4 이고 STVL 만 ≤ 10, T6 = 두 구역 x 열 수가 t4 의 90 % 이상. T4 · T5 는 다른 출력에서 읽음.
- 출력: `j502_eval.txt`(9 줄).
- 결함: §6.5 의 전제 오류가 코드에 그대로(구역 · 범위 구분 없음). `j502b_shell.txt`(껍질/안쪽 · 구역별 · 좌측 가구 거리)와 `j502c_holes.txt`(사라진 열 위치 · 공통 열 면 위치 · 상자 행별 앞면)를 만든 코드는 **없음**(§6.9-2).
- 다시 쓸 수 있나: 같은 이름의 JSON 이면 예. 정정 분석까지 하려면 b · c 를 다시 짜야 한다.

### 9.12 job503_vizgen3.py — 절단 A/B 그림
- 실행: PC python, `python job503_vizgen3.py <dir> <out.html> [BX] [BY] [T4 감사] [T2 감사] [T5 요약]`.
- 하는 일: STVL / t4 / t2 층, 차이 2 장, t2 슬라이스 판 + T1~T6 판정과 정정표(정정 내용은 코드 안 문자열 — '껍질' 단어가 들어 있는 것은 이 때문).
- 출력: `j503_trunc_ab.html` = 그림 3(`figures/2026-09-22_truncation_4_vs_2.html`). 화면 출력 원문 없음.

### 9.13 job505_modeN_gate.sh ★ 게이트 J · K · L
- 실행: Jetson, `bash job505_modeN_gate.sh LOGNAME BX BY`(LOGNAME = nvblox 시작 때의 로그 이름, `/tmp/nvblox_<LOGNAME>.log`). 주행 30 s 전에 끝낼 것(DDS 참여자 생성).
- 하는 일: J = 컨테이너 안 실행 파일 경로 PID 수 == 1 · 로그 Rates 블록 `ros/depth_image_callback` ≥ 10 · `ros/update_esdf` ≥ 9 · Delays `esdf_integration` ≤ 0.15 s. K = `ros2 param get /local_costmap/local_costmap plugins` 에 `nvblox_layer`. L = 컨테이너 안 job474 8 s → '프레임당 셀'(상자 띠) ≥ **8**(저장본, 정정 전 10) · 근거리 자취 0 프레임 · 슬라이스 ≥ 30 프레임. 셋 다 통과가 아니면 exit 1 "주행하지 않음".
- 출력: `j508_n4n{1,2,3}_prepN.txt` 끝.
- 계보: 절차 v2.0 §3 J · K · L 의 실행본. 이후 09-23 에 게이트 M · N(`job522_goalprobe.py`, job315 · job248)이 이 스크립트에 붙음(절차 표 M · N 행) — 저장소 09-22 사본은 그 전 판.
- 다시 쓸 수 있나: 로그 이름 · 컨테이너 이름이 같으면 예. N6-0 이후 J 는 `job254` 안에서 `/tmp/nvblox_node.log` 로 자동.

### 9.14 job506_decay.sh + job506_decay.py ★ 감쇠 정지 측정
- 실행: Jetson, `bash job506_decay.sh YAML NAME BX BY [SEC=80]`(`run_j506.sh` 가 sh · py · t2d99 yaml 을 올림).
- 하는 일(sh): 벤더 `nvblox_base.yaml` 의 감쇠 관련 줄(L21 rate · L102 factor · L103 threshold · L104 exclude_last_view · L106 free) 과 이번 yaml 의 factor 를 나란히 → nvblox 재시작 → 32 s → 깊이 콜백 Hz → py 백그라운드 → 6 s 뒤(py 의 t = 5 s) `ros2 param set /camera/camera enable_depth false` → 4 s 뒤 깊이 Hz(빈 값 = 끊김) → py 끝 → `enable_depth true` → 6 s → 깊이 · 릴레이 점군 · EKF odom Hz → nvblox 정지.
- 하는 일(py, 호스트 — 호스트 `nvblox_msgs`): 슬라이스 첫 메시지의 프레임으로 TF 한 번(로버 정지 가정) → 1 초마다 상자 구역(base x 0.9~1.5, y −0.35~+0.15)의 ≤0 셀 · 최소 거리 · 미지 · 자유 셀 수 → ≤0 이 처음 0 이 된 시각 · 자유가 기준보다 5 셀 넘게 는 시각.
- 출력: `j506_d95.txt` · `j506_d99.txt`(§4.4 표).
- 결함: '자유가 늘기 시작한 시각' 은 두 번 모두 None — 셀이 자유가 되기 전에 미지 · 범위 밖으로 빠져서. '블록 해제 ≈ 36 s' 는 구역이 슬라이스 범위 밖으로 나간 시각(t = 41)에서 읽은 것. 0.99 는 100 s 창이라 해제를 못 봄.
- 다시 쓸 수 있나: 예. 감쇠 · 통합 거리를 바꿀 때 기억 시간을 주행 없이 재는 도구 — 상시 도구로는 안 옮겨짐.

### 9.15 job508_modeN.sh · job511_modeS.sh ★ 회차 팔 준비
| 도구 | 하는 일 | 출력 |
|---|---|---|
| `job508_modeN.sh NAME BX BY [YAML=nvblox_n0_t2d99.yaml]`(`run_j508.sh` 가 508 · 505 · 488 · 442 · 474 · yaml 을 올림) | 실행 파일 PID 로 nvblox 정지 → 시작(로그 `/tmp/nvblox_<NAME>.log`) → 32 s → 깊이 콜백 · **감쇠 · 절단 실효값**(`ros2 param get /nvblox_node static_mapper.tsdf_decay_factor` · `…truncation_distance_vox`) → `QUICK=1 job488 nvblox` → `job442_clearwait.sh`(로컬 · 전역 클리어 + 8 s, [간헐 중단 카드](intermittent-abort-dy.md)) → `job505` | `j508_n4n{1,2,3}_prepN.txt`(n4n2 는 L 불합격 2 회 — §6.7) |
| `job511_modeS.sh BX BY` | 현재 plugins → `QUICK=1 job488 stvl` → nvblox 정지 → job442 → job248 감사 1 표본(상자 · 최소폭) | `j511_n4s2_prepS.txt` |
- 둘 다 prep(`run_mp9prep.sh` → job240) **뒤에** 부른다 — prep 이 Nav2 를 설치 YAML 상태로 다시 띄우기 때문(n4s2 의 실제 사례, §6.8).

### 9.16 주행 묶음 — run_drive_nohup.sh ★ · job254 · job231_drive.sh · job453 · run_post3.sh
- `run_drive_nohup.sh NAME D BX BY TOL GL`(PC, 환경변수 `STAGE` · `NOTE` · `GIT_HEAD` · `BAG_EXTRA` · `BAG_PROFILE`): 09-17 scratchpad 에서 job254 · job231 · job125 · job248 · job315 · job386 · job451 · job453 을 올림 → **사전 게이트**(한 ssh 씩): job248 감사(최소폭 줄이 없으면 1 회 재시도) → 통로 띠 근거 없는 셀 ≤ 1 → job315 상자 셀 최대 y 3 표본 중앙 → 창 = 좌측 경계 − (상자 셀 최대 y + 0.195) ≥ 0.20 → job377 목표 풋프린트 ↔ LETHAL ≥ 0.20 → job440 출발 자세 차체 외곽 여유 ≥ 0.10(nan 이면 1 회 재시도) → Jetson 에서 `nohup bash job254_s4run.sh` → 5 s 마다 로그 폴링(최대 8 분, ssh 실패는 재시도) → '결과 ' · '게이트 실패' 에서 끝. ssh 가 끊겨도 주행은 Jetson 에서 계속된다(09-15 교훈).
- `job254_s4run.sh`(Jetson): 프로세스 중복 · 보드 `/wheel_odom` 25 Hz · SLAM map→odom 개수 · 출발 자세 · 상자 기준선 대비 dx · dy ±TOL → `job231_drive.sh`. 저장소 09-22 사본에는 N6-0 게이트 J(활성 yaml 이 nvblox 층이면 `/tmp/nvblox_node.log` 검사)가 들어 있다 — N4 회차 때 판에는 없었음(N4 는 job508 의 J 로 대신).
- `job231_drive.sh`(Jetson): bag 기록(기본 17 토픽 + `BAG_EXTRA`, **`BAG_PROFILE=nvblox` 면 `/nvblox_node/static_map_slice` · `/nvblox_node/combined_occupancy_grid` · 깊이 이미지 160×120 · camera_info 추가 ≈ 0.6 MB/s** — 09-21 §10.1) + top 2 s + tegrastats 1 s + 노드별 RSS → 러너 `job125_avoid3.py D 90 NAME` → 기록 종료 → `job453_runmeta.sh`(주행 **뒤**에 메타 · 파라미터 — cc1 의 디스커버리 부하 교훈) → nav2 로그 신규분 패턴 수 · EKF 위반 · slam 폐기. 09-21 사본은 09-21 판(BAG_PROFILE 추가).
- `run_post3.sh NAME`(PC): job379 로 nav2 이벤트 표 · bag tgz 를 만들고 bag · drive 로그 · csv · nav2 구간 로그 · top · meta · params · refix csv · tegrastats · rss 를 회수 → `j507_<이름>_post.txt` 와 각 파일. 09-17 scratchpad 경로 고정.
- 메타 예(`meta_n4n1.txt`): stage `N4-N2`, note "nvblox 층 이진, floor 수정, 절단 2.0, 감쇠 0.99 = nvblox_n0_t2d99.yaml 1회차 — 배치 1.151/-0.089, 게이트 J·K·L 통과", git_head_pc `9a9fb34`, nav2-mppi 1.1.20, 15 W.
- 계보 · 지금: 09-28 에 09-17 scratchpad 가 자동 소실돼 이 러너는 그대로는 못 씀 → 이후 `run_jn.sh` · 10-27 `chk_drive_gate.py` 체계(CLAUDE.md §6). 러너 지표 ①~⑥ 의 정의 · 결함은 [회피 계측 결함](avoid-run-metrics.md).

### 9.17 run_j509_analyze.sh ★ 회차 bag 분석
- 실행: PC, `run_j509_analyze.sh NAME EPOCH`(EPOCH = nav2 로그의 `bt_navigator: Begin navigating` 시각). Jetson `/tmp/bag_<NAME>` 에 대해: D `job416_boxclear.py`(로컬 코스트맵 상자 LETHAL ↔ 차체 외곽 거리 − 반셀 0.025, 0.6 s 간격 표 · 최소 — [회피 계측 결함](avoid-run-metrics.md)) · E `job446_pathdecomp.py`(원경로 → 스무딩 → 실제 경로의 상자 여유 분해, 복귀 회전 자리 x 1.10~1.25 · 뒤 모서리 x 1.35~1.55, 예측 L = 2 · 3 s — [CostCritic 카드](obstacles-to-costcritic.md)) · F `job462_baghz.py`(bag 토픽별 개수 · Hz · 간격 중앙 · 최대) · A `job431b_crab.py`(SLAM 게걸음 각 — [센서 데크 yaw](sensor-deck-yaw.md)).
- 출력: `j509_<이름>_analysis.txt`(§5 표의 job416 · job446 · bag Hz 열).
- 결함: EPOCH 를 nav2 로그에서 뽑는 일은 래퍼 밖(대화 쪽)에서 했고, post 와 한 셸에서 이어 부르면 로그가 아직 없어 빈 값(§6.8). tegrastats 요약(job463) · CPU 합은 이 래퍼에 없음(§6.9-4).
- 다시 쓸 수 있나: 원본 scratchpad 소실로 래퍼는 불가, 개별 도구는 각 날짜 jobs 사본으로 가능.

### 9.18 job512_trajviz.py — N4 궤적 그림
- 실행: PC python, `python job512_trajviz.py <outputs_dir> <out.html>`.
- 하는 일: 러너 csv(fwd · lat · clear_geo · lc_box)로 5 회의 평면 궤적(출발 자세 기준), 상자(게이트 평균 전면 1.153 · 중심 −0.09 · 18×11 cm) · 차체 0.50×0.33, 회차별 소요 · 코스트맵 여유 · 복귀 자리 · 최대 횡변위 · **CPU 합(코드 상수 `{n4s1: 318, n4s2: 315, n4n1: 330, n4n2: 337, n4n3: 330}`)** 표.
- 출력: `j512_n4_traj.html` = 그림 4.
- 결함: CPU · 여유 일부가 상수(측정 도구의 출력을 읽지 않음). n4n3 의 러너 ① 무효를 그림이 어떻게 다루는지는 이 카드에서 확인 안 함.

### 9.19 09-22 복구 · 확인 도구(작은 것)
| 도구 | 하는 일 | 출력 |
|---|---|---|
| `job498_state.sh`(`run_j498.sh` 는 ping 실패 시 ALOPS 172.30.1.8 도 확인) | uptime · 부팅 시각, `/tmp` 스크립트 잔존, 스택 프로세스 수, 컨테이너 · nvblox 프로세스, **포크 diff `--stat`**, 로컬 plugins, scan · depth · wheel_odom Hz, 로드 · 온도 · 디스크 | `j498_state.txt`(56 분 전 재부팅, 전부 없음, 포크 diff 유지, 155 G) |
| `job499_container_up.sh`(`run_j499.sh` 가 09-21 세트 13 파일 + t2 yaml 재전송) | 컨테이너가 남아 있으면 `docker start`, 없으면 job472 → DDS 프로파일 `/tmp` 복사 → 안 nvblox 패키지 수 · GPU(`nvidia-smi -L`) → `/tmp` 파일 수 | `j499_container.txt`(Exited (255) → Up, 8 개, GPU 0: Orin (nvgpu)) |
| `job504_quick.sh` | 보드 리셋 직후: 스택 프로세스 수, 진행 중 `/tmp/job*`, wheel_odom · scan · odometry/filtered Hz, 에이전트 로그 끝 3 줄 | (출력 원문 없음 — SUMMARY §0 에 25.0 Hz) |
| `run_jx.sh 파일 [인자…]` | 범용 래퍼(09-22): 파일 하나를 CRLF 제거 · 전송 · 실행(.py 면 python3), `JX_TIMEOUT` 기본 300 s | — (이후 `run_jn.sh` 로 이어짐, 메모리 '실행 투명성') |

## 10. 용어
- **nvblox**: NVIDIA 의 GPU 3D 지도 라이브러리. 깊이 이미지를 **TSDF** 복셀에 통합하고 거기서 **ESDF** 를 만든다. 여기서는 Isaac ROS 3.2 의 `nvblox_ros`(apt 3.2.5)를 컨테이너 안에서 `nvblox_node` 로 띄웠다.
- **TSDF(절단 부호 거리장)**: 복셀마다 '가장 가까운 관측 표면까지의 부호 있는 거리' 를 표면 앞뒤 **절단 거리** 안에서만 저장(앞 +, 뒤 −). 광선을 따라 '여기는 비었다' 도 같이 기록되므로 STVL 의 절두체 소거와 달리 가림 · 화각을 안다.
- **절단 거리(`projective_integrator_truncation_distance_vox`)**: TSDF 를 저장하는 표면 앞뒤 폭(복셀 수). 4.0 × 0.05 = 0.20 m, 2.0 = 0.10 m. 표면 **뒤** 음수 구간이 ESDF ≤ 0 이 되어 이진 층에서 치명 '띠' 가 된다.
- **ESDF(유클리드 부호 거리장)**: 모든 칸에 '가장 가까운 장애물까지 거리'. `esdf_mode 2d` 면 슬라이스 높이 구간(z 0.03~0.30, 지금 0.06~0.30)의 복셀을 모아 2D 로. 최소 가중(0.1) 미만 복셀은 ESDF 에서 빠진다.
- **슬라이스(`DistanceMapSlice`)**: ESDF 2D 를 영상처럼 낸 메시지(0.05 m 픽셀, 미관측 = `unknown_value`). `static_map_slice` 와 `pessimistic_static_map_slice`(미지를 장애물 쪽으로 보는 판, N0 에서 같은 값).
- **통합 거리(`projective_integrator_max_integration_distance_m`)**: 이보다 먼 깊이는 TSDF 에 안 넣음. 2.0 m(지금도) — STVL 카메라 `obstacle_range 1.2` 보다 멀어 nvblox 만 보는 구역이 생긴다(§4.3 좌측 가구).
- **감쇠(`tsdf_decay_factor` @ `decay_tsdf_rate_hz`)**: 관측이 끊긴 복셀의 가중을 주기마다 곱으로 줄임. 가중이 ESDF 최소 가중 아래로 가면 ESDF 에서 빠지고(상자가 코스트맵에서 사라짐), 감쇠 문턱 아래면 자유/미지 처리. 0.95 @5 Hz → 15 s, 0.99 → 78 s(계산), 측정 17 s · 81 s.
- **nvblox 코스트맵 층(`nvblox::nav2::NvbloxCostmapLayer`)**: Nav2 코스트맵 플러그인. 슬라이스를 구독해 셀마다 거리를 읽고 이진 모드(`convert_to_binary_costmap: true`)면 거리 ≤ 0 → LETHAL, 그 밖 FREE. 기울기 모드면 `inflation_distance` 안 INSCRIBED, `max_obstacle_distance` 까지 선형 비용 — 그래도 ≤ 0 은 LETHAL(분기 순서, §4.2).
- **빈 스텁 패키지**: 이름 · 버전만 맞춘 빈 ament 패키지. 의존 선언만 만족시켜 CUDA 를 끌어오는 진짜 `isaac_ros_common` 없이 층을 호스트에서 빌드.
- **상주 컨테이너**: `docker run -d … sleep infinity` 로 띄워 두고 `docker exec` 로 명령을 넣는 방식. TTY 전제인 `run_dev.sh` 대신.
- **CDI(Container Device Interface)**: 장치를 이름(`nvidia.com/gpu=all`)으로 컨테이너에 넘기는 방식. 호스트에 스펙(/etc/cdi)이 없어 레거시 `NVIDIA_VISIBLE_DEVICES=all` 로.
- **모드 S / 모드 N**: 로컬 코스트맵 카메라 층이 STVL(대조군) / nvblox. 이 시기엔 설치 YAML 의 `plugins` 줄 sed 로, N6-0 부터 launch 인자 `camera_layer:=stvl|nvblox`.
- **게이트 J · K · L**(절차 v2.0): J nvblox 노드 1 개 · 깊이 ≥ 10 · ESDF ≥ 9 Hz · 지연 ≤ 0.15 s, K 로컬 plugins 실효값 = nvblox_layer, L 슬라이스 상자 띠 셀 ≥ 8(정정 전 10) · 근거리 자취 0.
- **`BAG_PROFILE=nvblox`**: bag 에 슬라이스 · 점유 격자 · 깊이 이미지 160×120 · camera_info 를 더 담는 설정(≈ 0.6 MB/s, bag 2.7 → 14.5 MB). 오프라인 nvblox 재생 · 비교용.
- **과도 상태(층 전환 직후)**: Nav2 재기동 · 클리어 직후 층이 슬라이스를 다시 받아 채우는 동안의 코스트맵. 이때의 감사(기준1 0.10)는 결과가 아니다.
- **코스트맵 상자 최소 여유(job416) / 복귀 회전 자리 여유(job446) / 러너 ① 실제 최근접**: 각각 로컬 코스트맵 LETHAL 셀 ↔ 차체 외곽(셀 양자화 ±2.5 cm), 경로 분해의 특정 구간 여유, 카메라 점군 상자 모델 ↔ 차체 외곽 기하 거리. 같은 주행에서 서로 다른 값이 정상.
