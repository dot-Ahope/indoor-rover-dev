# 2026-10-22 — 유령 칸 대응: 깊이 프리셋 주행 f2pr1 · nvblox 최소 가중치

## §0 하루 시작 (사용자: "오늘 진행 뭘 해야 하는가." → 순서 0 점검 → 1 f2pr1 → 2 min_weight → "진행하라")
- 본 것(`outputs/chk_day_start_1022.txt`, 도구 `jobs/chk_day_start_1022.sh`):
  - PC 핑: 192.168.0.110 응답(TTL 63), 172.30.1.8 무응답 → Jetson 이 WEB_DEV_5G 로 돌아옴. 접속해 신원 `jetson-desktop` 확인.
  - **10:30:23 재부팅**(가동 47 분) → `/tmp` prep 5 개 없음. Isaac 컨테이너 · 시험 컨테이너 `Exited (255)`(nvblox_up.sh 가 docker start), 스택 없음, base active, 에이전트 컨테이너 떠 있음.
  - `camera.launch.py` = 어제 배포한 depth_preset 판(sha 95fe7b16a70f).
  - 디스크 여유 124 GB, 메모리 사용 881 MB.
- prep 스크립트 재전송(`jobs/up_prep_1022.sh` — 저장소 `Docs/tools` 판을 그대로): prep_fast.sh c636f4060d · prep_patrol.sh 6bdd126a30 · chk_prep.py d06751ab73, 저장소와 해시 일치. pad_relief.py · prep_patrol_pad.sh 는 지금 구성에서 안 씀(올리지 않음).
- 스크래치패드 `tools/` 폴더와 `job240 · 440 · 451 · 453 · 956` 원본이 또 사라짐(자동 삭제 추정). 주행 러너 묶음(run_f0 · run_f2c · put_one · job550 · job551 · job613 · rescued_jetson_tmp/)은 남아 있고 10-21 jobs 사본과 해시 일치(run_f0 은 사본이 비밀번호를 가려서 다름, run_f2c 는 어제 `home` 추가 판).

## §1 f2pr1 구성 prep — PREP_OK (`outputs/prep_pr_1022_1.txt`, 도구 `jobs/prep_pr_1022.sh`)
- 구성 = 10-21 §21.2 선언 그대로: 프로젝터 상시 끔 · vslam:=shadow · dds_shm:=true + `depth_preset:=3`.
- 위치 추정 검사 0.005 m · −0.1° 통과, `/wheel_odom 25.0 Hz`(재부팅 뒤에도 보드 세션 살아 있음 — 보드 리셋 불필요) · `/odometry/filtered 30.0` · `/tf 49.7` · 배터리 12.36 V, nvblox · cuVSLAM · vslam_twist · ekf_vslam 각 1. 64 s.
- 프리셋 적용 확인(`jobs/chk_preset_1022.sh`): 운용 카메라 `depth_module.visual_preset = 3`.
- 판정 기준은 10-21 §21.2(주행 전 선언). 주행은 사용자 "시작" 뒤.

## §2 f2pr1 주행 시작 (사용자: "1. 시험 상자 제자리에 있다. 2. 사람들이 돌아다니고 있다. 문제 발생시 여부 확인. 시작.")
- 러너 `run_f2c.sh f2pr1 … b910`(STAGE F2pr, LOAD_MAX 65, JETSON_HOST 192.168.0.110, GIT_HEAD 426a08c3). NOTE 에 '사람들이 돌아다님' 기록.
- **기준 3 해석(결과 보기 전, 주행 중 적음)**: 로버는 상자를 등지고(≈ −166°) 1.2 m 거리에서 출발하므로 '1.4 m 안에 들어온 뒤' 는 출발 즉시가 된다. → 시작 시각 t0 = 상자 중심 (1.25, −0.075) 이 **로버 1.4 m 안 그리고 진행 방향 ±40°(D455 깊이 수평 시야 ≈ 87° 의 안쪽)** 에 처음 든 시각. 판정: t0 + 2 s 안에 상자 영역 (1.15~1.35, −0.20~0.05) 로컬 LETHAL ≥ 8 칸. 같은 도구로 f2sm1(프리셋 없음) 도 잼(비교 기준). 도구 `jobs/anal_box_detect.py`.
- 사람 영향 확인: 문제(중단 · 긴 정지 · 유령 기준 미달)가 나오면 그 시각 라이다 점에 사람 크기 물체가 있었는지 bag 으로 확인.

## §3 f2pr1 결과 — 기준 1 · 2 통과, **기준 3(낮은 상자 2 s 안 ≥ 8 칸) 미달** (주행 11:34~11:38)
| 기준(10-21 §21.2 · §2 해석) | f2pr1(프리셋 3) | 비교: f2sm1(프리셋 없음) | 판정 |
|---|---|---|---|
| 1. 목표 | 3/3 (51.7 · 51.8 · 110.0 s, 총 213.7 s) | 3/3 | ✔ |
| 2. 유령 — 상자 너머 맨바닥 A · 문 사이 B (t 10~60 s) | **A 0 · B 0** | A 50 · B 0 (10-21 §15, 끔 주행 28~99 · 켬 0~3) | ✔ |
| 3. 낮은 상자 (t0 = 4.0 s, 출발 자세에서 이미 1.26 m · 방위 −4°) | 출발부터 **7 칸**, 처음 ≥ 8 은 t0 + 10.8 s | 출발부터 15~16 칸, t0 + 0.55 s | ✘ (7 < 8) |
| 4. 끝 상태 지도 · 라이다 근거 없는 LETHAL (기록) | 110 칸(그중 nvblox 슬라이스 77) | 253 칸(nvblox 244) | nvblox 몫 −68 % |

- 주행 전체 상자 칸(10 s 묶음, `outputs/anal_box_series_*.txt`):
  - 나가는 길(t 0~60, 로버-상자 최소 0.44 m): f2pr1 6~9 칸 · f2sm1 15~17 칸 — **절반**.
  - 돌아오는 길(t 170~220, 최소 0.35 m): f2pr1 **1~2 칸** · f2sm1 3~7 칸. 프리셋 없이도 복귀 쪽에선 상자가 작게 보임(반대편 면을 비스듬히 봄으로 추정), 프리셋 3 에선 거의 사라짐.
  - 그래도 로버는 상자 중심에서 0.35 m(차체 중심 기준) 밖으로 지나갔고 stuck 진단 0. 접촉 여부는 사용자 확인 필요.
- 기타: 누적 회전 휠 −79.5° vs EKF −161.7°(차 82.2°, f2sm1 11.3° · f2sm2 44.3°) — 미끄러짐이 컸다. 사람 통행(사용자)과 관련 있는지는 미분석.
- 읽기:
  1. 프리셋 3 은 **맨바닥 유령을 없앴다**(A 0, 끝 상태 nvblox 칸 −68 %). 정지 pr1 의 결과가 주행에서도 재현.
  2. 대가로 **라이다 아래 낮은 물체가 절반 이하로 보인다** — 나가는 길 7 칸은 여전히 LETHAL 이라 MPPI 가 피했지만, 복귀 쪽 1~2 칸은 '거의 못 봄'. 상자가 더 작거나 더 비스듬하면 놓칠 수 있다(추정).
  3. 따라서 프리셋 3 을 그대로 기본값으로 넣는 것은 선언 기준상 불합격. 남은 길(추정, 시험 전): (가) 중간 프리셋(5 Medium Density 등) 또는 고급 모드 개별 값(신뢰도 문턱)을 낮춰 절충점 찾기, (나) 프리셋 0 유지 + 2번(nvblox 최소 가중치)으로 깜빡이는 유령만 거르기, (다) 둘 조합.
- ⚠ 2번 준비 사항: 지금 러너 bag 에는 **깊이 영상이 없다**(nvblox 출력 슬라이스 · 코스트맵만) → 최소 가중치를 bag 재생으로 A/B 하려면 깊이(`/camera/camera/depth/image_rect_raw` + camera_info, 160×120 ≈ 38 kB × 15 Hz)를 함께 기록한 주행이 먼저 필요.
- 데이터: 러너 `outputs/run_f2pr1.txt` · bag `bags/bag_f2pr1.tgz`(PC 스크래치패드 `f0_f2pr1/` 에서 복사; /local_costmap/costmap · /global_costmap/costmap · /nvblox_node/static_map_slice · /map · /scan · /tf) · 유령 `outputs/anal_zone_ghosts_f2pr1.txt`(도구 `2026-10-21/jobs/anal_zone_ghosts.py`) · 상자 `outputs/anal_box_detect_f2pr1.txt` · `anal_box_detect_f2sm1.txt`(도구 `jobs/anal_box_detect.py`) · `outputs/anal_box_series_f2pr1.txt` · `anal_box_series_f2sm1.txt`(도구 `jobs/anal_box_series.py`) · 끝 상태 `outputs/anal_phantom_f2pr1_end.txt` · `anal_phantom_f2sm1_end_check.txt`(도구 `2026-10-21/jobs/anal_phantom_cells.py`, 그림 `figures/phantom_f2pr1_end.png`). f2sm1 입력 = `2026-10-21/bags/bag_f2sm1.tgz`.

## §4 사용자 관찰 확인: "사람 장애물 문제 없었음. 복귀 시 문을 넘으면서 멈칫. W3 에서 전선을 밟았는데 잘 작동했는지."
- 사람: 사용자 확인 — 이번 주행에 사람 장애물 문제 없음. f2pr1 은 비교용으로 유지.
- 로그 원본 보관: Jetson `/tmp/nav2.log` · `slam.log` · `sensors.log` 를 prep 이 덮기 전에 `bags/logs_f2pr1/` 로(nav2 는 `outputs/nav2_f2pr1.log` 에도). 사건 0.01 s 표 `outputs/nav_events_ms_f2pr1.txt`(도구 `jobs/anal_nav_ms.py` — 10-21 chk_nav_ms.sh 의 PC 판).
### §4.1 복귀 중 문 근처 멈칫 — 원인 두 가지, 둘 다 10-21 §12.2 에서 본 것과 같은 서명
| 시각 · 위치(map) | 길이 | 서명(0.01 s) | 원인 |
|---|---|---|---|
| 11:37:13.34 (2.23, −1.06) · 11:37:16.64 (2.21, −0.84) — 문 들어가기 직전 · 문 안 | 0.20 · 0.15 s | 0.0x s 전 `Exception in transformPose: Lookup would require extrapolation into the future` → `Unable to transform robot pose` → `follow_path Aborting` → 곧 `Received a goal`. 16.74 MonotoneEscape '최근접 19.2 cm, 성공'(아무것도 안 함) | TF 미래 외삽으로 컨트롤러 중단 → 재시작(10-21 §12.2 묶음 A). 직전 수 초 `Control loop missed` 반복 |
| 11:37:29~34 (1.94, −0.14) — 문 지난 뒤, 상자 쪽으로 돌며 | **4.9 s** | 27.02 `Smoothed path leads to a collision at (1.52, −0.03)` · `PathBlockedAhead: 앞 경로 (1.40, −0.02) 비용 99` → 29.05 '2.0 s 지속 → 주행 중단' → `Running wait` → 34.16 `wait completed` | 경로가 **출발점 낮은 상자(전면 x ≈ 1.15~1.35) 바로 옆** 칸(비용 99 = 내접)을 지남 → 막힘 검사가 주행을 끊고 복구 순서의 Wait 5 s 차례(10-21 §11.3 과 같은 기제) |
- 읽기: 사용자가 본 '문을 넘으며 멈칫' 은 문 안의 짧은 두 번(TF 외삽)과 문 지난 직후 4.9 s 정지(상자 옆 경로 막힘 → Wait)로 보인다. 문 자체(문턱 · 유령)가 원인이라는 근거는 없음 — 그 구간 문 사이 유령 칸 0(§3). TF 외삽이 왜 0.5 s 여유로 안 덮이는지, 경로가 왜 상자에 붙어 계획되는지는 10-21 과 같이 **미확인**.
### §4.2 W3 전선 — 위치 · 방향 추정은 정상, 휠 회전 수만 평소와 반대로 어긋남
- 도구 `jobs/anal_slip_segments.py`(10 s 묶음으로 휠 /wheel_odom 적분 · EKF /odometry/filtered · SLAM map→base 의 회전 · 이동), 결과 `outputs/anal_slip_segments_f2pr1.txt` · 비교 `anal_slip_segments_f2sm1.txt`.
  | W3 회전 구간(10 s 둘) | 휠 | EKF | SLAM(라이다) | 휠 − SLAM |
  |---|---|---|---|---|
  | f2pr1 11:36:11 · 11:36:21 | −90.2 · −54.9° | −104.3 · −69.1° | −104.3 · −70.2° | **+14.1 · +15.3°**(휠이 덜 셈) |
  | f2sm1 11:41:55 · 11:42:05 | −141.4 · −75.4° | −108.7 · −66.8° | −109.0 · −67.5° | −32.4 · −7.9°(휠이 더 셈 — 평소 미끄러짐) |
- 같은 W3 회전에서 평소(f2sm1)엔 휠이 실제보다 많이 돌았다고 세는데(트랙이 미끄러짐), 이번엔 **실제보다 적게** 셌다 → 전선이 한쪽 트랙 아래에 끼어 차체 회전 모양이 달라진 흔적으로 추정(기전 미확인). 주행 전체 휠−EKF 회전 차 82.2°(f2sm1 11.3°)의 약 1/3 이 이 두 묶음, 나머지는 B 회전(+24.5°) 등.
- 잘 작동했나: **EKF 방향은 SLAM 과 0~1.1° 안**(자이로가 회전을 맡아 휠 오차에 안 끌려감), 목표 2 SUCCEEDED(0.112 m), stuck 진단 0, 펌웨어 스톨 래치 없음, 주행 끝 map→odom 누적 보정 0.42 m · −4.9°(f2sm1 0.51 m · −4.2°)로 평소 범위. → 전선을 밟은 영향은 휠 적분에만 남고 위치 추정 · 주행에는 드러나지 않았다.
- 데이터: 위 결과 파일 · 입력 `bags/bag_f2pr1.tgz`(/wheel_odom · /odometry/filtered · /tf · /cmd_vel · /rover/stuck) · `2026-10-21/bags/bag_f2sm1.tgz` · 러너 요약 `outputs/run_f2pr1.txt`, `2026-10-21/outputs/run_f2sm1.txt` · 멈칫 `outputs/anal_stops_f2pr1.txt` · `anal_dip_events_f2pr1.txt`(도구 `2026-10-21/jobs/anal_stops.py` · `anal_dip_events.py`) · nav2 원본 `outputs/nav2_f2pr1.log`.

## §5 깊이 기록 주행 f2dr1 선언 (사용자: "(가) 시작") — 결과 보기 전
- 목적: nvblox 입력(깊이 160×120 · camera_info)을 담은 bag 을 지금 운용 구성(프로젝터 끔 · 그림자 cuVSLAM · SHM)으로 남겨, 2번(esdf_integrator_min_weight)과 프리셋 비교를 **같은 입력 재생**으로 한다. f2pr1 · f2sm1 bag 에는 깊이 영상이 없음(§3).
- 구성: prep `jobs/prep_dr_1022.sh`(= f2sm1 구성, depth_preset 지정 안 함 → visual_preset 0 확인), 러너 `run_f2c.sh f2dr1 … b910`, `BAG_DEPTH=1`(10-19 §3 옵션 — 깊이 best effort 구독, 끝나면 Jetson `~/bags/bag_f2dr1` 사본), STAGE `F2c-depthrec-p0`. 재생 도구 `2026-10-19/jobs/run_nvblox_replay.sh`(ROS_DOMAIN_ID 42 격리).
- 기록 성공 기준: 깊이 · camera_info 각 ≥ 14.5 Hz(주행 시간 × 15 의 97 % 이상), 목표 3/3 은 기준 아님(주행 비교용으로 기록).
- 프리셋 없음 기준선(실시간, f2sm1 재현 확인용): 맨바닥 영역 A(1.45~2.65, −0.35~0.45) · 문 영역 B(2.00~2.60, −0.85~−0.45) 유령 칸(`2026-10-21/jobs/anal_zone_ghosts.py`, t 10~60 s), 낮은 상자 `jobs/anal_box_detect.py`. f2sm1(A 50 · B 0, 상자 15~16 칸) 과 같은 범위면 입력 대표성 ✔.
- R0 재생 충실도(A/B 전에): 같은 설정 재생 조각 vs 실시간 조각(/nvblox_node/static_map_slice, 거리 ≤ 0 칸) — 영역 A 에서 한 번이라도 장애물이 된 칸 수 차 ≤ 20 % 이고 상자 영역 칸 수 중앙 차 ≤ 2 → 재생 신뢰.
- 2번 A/B(재생): min_weight 0.1(기준) · 1 · 2. **합격** = 영역 A 조각 유령 칸이 기준의 30 % 이하 **그리고** 상자 영역 칸 수 중앙(t0~t0+10 s)이 기준의 80 % 이상. 상자가 사라지면 불합격. 프리셋 3 과 견줄 수 있게 같은 지표로.

### §5.1 prep 1 회째 PREP_FAIL — 로버가 출발 자세가 아님 (`outputs/prep_dr_1022_1.txt`)
- 본 것: 위치 추정 검사(기대 0,0,0) 위치 차 0.160 m · yaw 차 +81.0° → 불합격. visual_preset 0(프리셋 없음 적용 ✔).
- 원인(기록으로 확인): f2pr1 은 목표 3 (0, 0, −170°) 로 끝나 로버가 **출발 방향의 반대(map −166.5°)** 로 서 있다(`outputs/run_f2pr1.txt` 끝 줄 '출발 대비 최종 map Δyaw −166.7°'). prep 은 SLAM 초기 자세를 출발 테이프 (0,0,0°) 로 주므로 180° 가까이 틀린 초기값에서 정합이 엉뚱한 곳(+81°)에 붙음. 10-21 의 '첫 실패 원인 미확인'(0.049 m · 2.5°)과는 크기가 달라 다른 경우.
- 조치: 사용자에게 출발 테이프 · 출발 방향으로 다시 놓아 달라고 요청 → 놓은 뒤 prep 재실행. 로버를 내가 돌리지 않음(움직임은 주행 "시작" 범위로만).

### §5.2 prep 2 회째 통과 → 러너 기동 실패(Jetson 연결 끊김, 로버 안 움직임)
- prep 2 회째(사용자가 출발 자세로 놓음): 위치 차 0.007 m · yaw 차 −0.0° → PREP_OK (`outputs/prep_dr_1022_2.txt`).
- 러너: 파일 전송 3 회 'lost connection' → `ssh: connect to host 192.168.0.110 port 22: No route to host` → 기동 실패 (`outputs/run_f2dr1.txt`). 주행 명령은 나가지 않음.
- PC 에서 본 것: 13:39:47 두 주소 무응답(`outputs/chk_ping_f2dr1.txt`), 13:40:05 잠깐 응답 뒤 13:40:35~13:41:53 다시 무응답, 13:42 부터 안정(`outputs/chk_ping_f2dr1_b.txt`).
- Jetson 에서 본 것(`jobs/chk_wifi_1022.sh` · `chk_wifi_1022b.sh` → `outputs/chk_wifi_1022.txt` · `chk_wifi_1022b.txt`): 신원 jetson-desktop, 가동 3 h 12 m(재부팅 없음), WEB_DEV_5G 유지, 13:30~13:45 끊김 사건 없음 · 13:32 DHCP 갱신(같은 주소)만, 스택 생존(controller 1 · nvblox 4).
- 추론: Jetson 무선 연결은 유지됐고 PC↔AP(또는 AP 안) 경로가 끊긴 것으로 추정(미확인 — PC 쪽 무선 기록 안 봄). 스택은 Jetson 안에서만 DDS 를 쓰므로 영향 없었을 것이나, 확실히 하려고 prep 3 회째 뒤 출발.

### §5.3 prep 3 회째 PREP_FAIL — Nav2 수명 주기 활성화가 멈춤 (`outputs/prep_dr_1022_3.txt` · `chk_prep_fail_1022.txt`, 도구 `jobs/chk_prep_fail_1022.sh`)
- 본 것: 150 s 기다린 뒤 controller · planner · behavior = inactive, bt_navigator = unconfigured(nav_map 만 active). 위치 추정은 됨(map→base (0.025, −0.006) · 1.2°). Jetson `/tmp/nav2.log`: planner_server · bt_navigator `failed to send response to /…/get_state (timeout)`(rmw_response.cpp:154), controller `Failed to get parameters: FollowPathMPPI.PreferForwardCritic.cost_weight` 반복. 네 서버 프로세스는 살아 있음.
- 추론: 수명 주기 관리자가 `get_state` 서비스 응답을 못 받아 다음 전이로 못 넘어감 — 서비스 응답(DDS) 전달 문제. 직전 Jetson↔PC 경로 끊김(§5.2)과 관계가 있는지 미확인(Jetson 무선은 유지됐었음). 10-21 이전에도 있던 일인지 기록 대조 안 함.
- 조치: prep 4 회째. 원본 nav2.log 는 prep 4 회째가 /tmp/logkeep 으로 옮김(필요하면 회수).

## §6 f2dr1 결과 — 목표 1 ABORTED 29 s (사용자: "진행하다 중간에 멈췄다. 확인 필요.")
- prep 4 회째 PREP_OK(0.007 m · +0.2°, `outputs/prep_dr_1022_4.txt`) → 러너 13:50:24 출발(`outputs/run_f2dr1_2.txt`; 1 회째 기동 실패 출력은 `run_f2dr1.txt`). 목표 1 (2.25, −1.60) **ABORTED 29.0 s**, 로버 map (0.73, 0.24, 19.6°) — 상자 북쪽, 출발에서 0.77 m. 러너는 중단 뒤 끝냄(로버 정지).
- 본 것 1 — nav2 사건(`outputs/nav_events_ms_f2dr1.txt`, 도구 `jobs/anal_nav_ms.py`, 원본 `outputs/nav2_f2dr1.log` · Jetson `~/bags/logs_f2dr1/`): 13:50:42.31 PathBlockedAhead 앞 경로 (1.85, 0.22) 비용 99 → 13:50:43.60 스무더 충돌 (1.82, −0.11) → **13:50:45.62 부터 계획기 `failed to create plan with tolerance 0.25` 매초 반복** → MonotoneEscape(최근접 22.4 cm, 할 일 없음) · Wait 5 s · 다시 MonotoneEscape · Wait → 중단.
- 본 것 2 — 전역 코스트맵 통과 가능 여부(`jobs/anal_door_pass.py` → `outputs/anal_door_pass_f2dr1.txt`; 값 < 99 칸만 4-이웃으로): 로버 → 목표 1 이 t 20 s(로버 (0.51, 0.18))까지 '닿음', **t 22 s 부터 '닿지 않음'**. 문 줄(y −0.60, x 1.80~2.85) 자체는 끝까지 통과 칸 있음(최소 62~75) → 막힌 곳은 문이 아니라 **로버(상자 북쪽)와 문 사이**.
- 본 것 3 — 막은 칸의 근거(`2026-10-21/jobs/anal_phantom_cells.py` → `outputs/anal_phantom_f2dr1_abort.txt`, 그림 `figures/phantom_f2dr1_abort.png`, t 40 s): 근거 없는(저장 지도 · 라이다 둘 다 아님) LETHAL 111 칸 — 전부 nvblox 조각이 점유로 봄. 북쪽 덩어리 51 칸 (1.14~2.24, 0.52~1.02) · 상자 14 칸(실물) · 상자 동쪽 맨바닥 (2.44~2.59, −0.38~−0.13) 8 칸 · (2.39, 0.24) 4 · (1.47, −0.42) 3 · (1.94, −0.46) 2 등. 로컬 기준 구간 합(`outputs/anal_zone_ghosts_f2dr1.txt`, t 0~42 s): 맨바닥 영역 A 21 칸(t 13~25 s 에 생김), 문 영역 B 0, 북쪽 (1.10~2.20, 0.45~1.15) 110 칸.
- 추론: 로버가 상자 **북쪽** 으로 돌았고(f2pr1 은 남쪽 — 미확인, 경로 비교 안 함), 그 길의 동쪽 출구(상자 동쪽 맨바닥 · 북쪽 덩어리 사이)에 카메라만 본 칸들이 전역 팽창(0.70 m)과 겹쳐 통과 칸이 끊겼다 → 계획 실패. 칸들이 유령(맨바닥)인지 사람 · 의자 같은 실물(라이다 높이 밖)인지는 영상 없이는 미확인 — 북쪽 덩어리는 라이다가 본 물체(초록) 옆이라 실물 가장자리일 수 있음. 맨바닥 영역 A 칸은 10-21 정의상 유령 후보.
- 의미: 프리셋 없음(f2sm1 구성)에서 **유령 후보 칸이 실제로 주행을 끊은 첫 사례**(f2sm1 은 A 50 칸에도 3/3). 프리셋 3 의 대가(상자 칸 절반)와 견줄 근거.
- 깊이 기록: 깊이 · camera_info 각 598 장(bag 41.9 s 전체 기준 14.28 Hz — 주행 구간만 따지면 15 Hz 근처로 추정, 미계산). bag `bags/bag_f2dr1.tgz`(PC), Jetson `~/bags/bag_f2dr1`. 출발 ~ 중단 29 s 의 상자 · 영역 A 를 담고 있어 **min_weight 재생 A/B 의 첫 입력으로 쓸 수 있음**(복귀 길은 없음).

## §7 bag 기록이 영향을 줬나 (사용자: "아무것도 없다. bag 기록이 영향을 끼친 것 아닌지 설명. 처음 위치로 되돌리겠다.")
- 사용자 관찰: 막은 칸 자리에 **실물 없음** → §6 의 '사람 · 의자 실물일 수 있음' 은 기각, 111 칸은 유령.
- 비교 1 — nvblox 입력 · 출력 시각(`jobs/anal_rec_effect.py` → `outputs/anal_rec_effect.txt`, 출발 뒤 40 s): 조각 주기 f2dr1 **8.60 Hz** vs f2sm1 8.95 · f2pr1 9.15 Hz(−4~6 %), 최대 간격 0.41 vs 0.21 · 0.30 s, 조각 지연 중앙 0.113 vs 0.114 · 0.113 s(p95 0.155 vs 0.152 · 0.151). 깊이(기록기가 받은 것) 14.25 Hz · 지연 중앙 0.064 s.
- 비교 2 — 같은 구간 유령 칸 수(`2026-10-21/jobs/anal_zone_ghosts.py`, t 0~42 s → `outputs/anal_zone_ghosts_f2dr1.txt` · `anal_zone_ghosts_f2sm1_0to42.txt` · `anal_zone_ghosts_f2pr1_0to42.txt`):
  | 주행 | 깊이 기록 | 맨바닥 A | 문 B | 문 앞 (1.90~2.80, −0.75~−0.30) | 북쪽 (1.10~2.20, 0.45~1.15) | 목표 1 통과 칸 연결(t 5~40 s 8 시점) |
  |---|---|---|---|---|---|---|
  | f2sm1(프리셋 없음) | 안 함 | 49 | 0 | 4 | **155** | 8/8 닿음 |
  | f2dr1(프리셋 없음) | 함 | 21 | 0 | 1 | 110 | **4/8**(t 22 s 부터 끊김) |
  | f2pr1(프리셋 3) | 안 함 | 0 | 0 | 4 | 55 | 8/8 |
  연결 도구 `jobs/anal_door_pass.py` → `outputs/anal_door_pass_f2sm1.txt` · `anal_door_pass_f2pr1.txt` · `anal_door_pass_f2dr1.txt`.
- 결론(측정): 깊이를 기록하지 않은 f2sm1 에 유령이 **더 많았다**(북쪽 155 · A 49 vs 110 · 21) → 유령은 기록 때문에 생긴 것이 아니다. 기록 중 조각 주기가 4~6 % 낮고 최대 간격이 조금 길었지만 지연 분포는 같음 → nvblox 입력은 사실상 같았다. 기록이 유령 수 · 위치를 바꿨다는 근거 없음(완전 배제는 못 함 — 같은 장면 반복 주행 없이 칸 위치 차이를 기록 탓/우연으로 가를 수 없음).
- 왜 f2dr1 만 막혔나(추론): 세 주행 모두 같은 길(상자 북쪽 → 동쪽, 출발 뒤 20 s 에 로버 (0.4~0.6, 0.13~0.19))로 갔다. 유령 수가 아니라 **놓인 자리** 차이 — f2dr1 은 t 19~25 s 에 (1.95~2.10, 0.00~0.35) 줄에 칸이 생겨 북쪽 덩어리와 상자 사이 출구를 메웠다(`outputs/anal_zone_ghosts_f2dr1.txt` 칸 목록). f2sm1 은 칸이 더 많아도 출구 줄이 비어 있었던 것으로 추정(칸 목록 대조는 미완).
- **§6 정정**: §6 의 '로버가 상자 북쪽으로 돌았고(f2pr1 은 남쪽 — 미확인)' 는 틀림.
  - 하려 한 것: 왜 이번만 막혔는지 경로 차이로 설명. 본 것: f2dr1 중단 위치 (0.73, 0.24) 가 상자 북쪽. 처음 추론: 평소와 다른 길. 의심한 이유: 사용자 질문으로 다른 주행을 같은 도구로 대조. 판별: `anal_door_pass` 로버 위치 — f2sm1 t 22 s (0.71, 0.21) · f2pr1 (0.61, 0.20), 같은 길. 결론: 길은 같고 유령 자리만 다름. 다음에 알아보는 법: '평소와 다르다' 는 말은 같은 도구로 기준 주행을 함께 돌린 뒤에만 쓴다.
- 의미: 프리셋 없음은 운에 따라 목표 1 출구가 닫힐 수 있음(3 회 중 1 회). 유령 대응(프리셋 · min_weight)의 필요가 실주행 중단으로 확인됨.
