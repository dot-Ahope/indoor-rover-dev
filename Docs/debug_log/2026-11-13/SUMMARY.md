# 2026-11-13 — README 시각화용 bag 기록 준비: 컬러 5 fps · 추가 토픽 정지 시험

## §0 기록 토픽 검토 · 컬러 5 fps 정지 시험 선언 (사용자: "readme 페이지에, 각 스택별로 gif를 만들어서 … 우선 주행하여 bag를 기록하자. … 기존의 것에 더해 어떤 것까지 기록할 수 있을지부터 검토." → "컬러 원본 영상과 점군(depth/color/points)는 DDS 메모리 공유로 작업하기로 한 거 아니었나?" → "5 fps 로 정지 시험부터 해")
- 지금 기록(f2rr1, `2026-11-11/bags/f0_f2rr1/bag_f2rr1.tgz` 의 metadata): 18 토픽, 444.1 s, 압축 70 MB. `/tf` 49.8 Hz · `/imu/data` 199.0 · `/odometry/filtered` 29.9 · `/wheel_odom` 25.0 · `/cmd_vel` 19.5 · `/scan` 9.9 · `/trajectories` 9.7 · `/nvblox_node/static_map_slice` 9.4 · 로컬 코스트맵 1.7 · 전역 0.6 · `/map` 0.1 등.
- 사용자 질문(SHM)에 대한 사실: SHM 은 **카메라 프로세스 ↔ cuVSLAM 컨테이너** 에만 켬(10-20 §7.4 · §9, `camera.launch.py` 30 ~ 32 행 · `config/fastdds_shm_udp.xml` 머리말). 기록기는 UDP 전용(`job551_f0drive.sh` 7 행 `fastdds_udp_only.xml`) → 컬러 원본을 지금 기록기로 받으면 IR 때(307 kB 메시지가 소켓 버퍼 208 kB 초과)와 같은 손실이 날 수 있음(추정). 기록기만 SHM+UDP 프로파일로 띄우는 것은 해 본 적 없음 → 이 시험.
- 확인(`jobs/chk_color_ready_1113.sh` → `outputs/chk_color_ready_1113.txt`, 읽기만):
```
== 부팅 2026-11-13 14:29:17 · 지금 2026-11-13 15:05:29 · up 36 minutes
== rover-base(user) active
  realsense2_camera 0 … (스택 안 떠 있음)
== topic_tools(throttle)            ← 설치 안 됨(목록 비어 있음)
  ros-humble-compressed-image-transport 2.5.4-1jammy…
    Color        640x480       RGB8        @ 60/30/15/5 Hz
  /dev/nvme0n1p1  233G   99G  122G  45% /
```
- 5 fps 를 만드는 방법: throttle 노드가 없음(설치는 sudo → 안 함) → 카메라 컬러 프로파일을 640x480x5 로. `camera.launch.py` 에 `color_fps` 인자 추가(기본 15 = 그 전과 같음 → 표준 prep 은 바뀌지 않음), 이번만 `SENSORS_ADD="color_fps:=5"`. 컬러는 Nav2 · nvblox(`use_color: false`) 가 안 씀.
- 시험(로버 안 움직임): 표준 prep(`SENSORS_ADD="color_fps:=5" bash /tmp/prep_patrol.sh lite`) → `jobs/chk_rec_ab_1113.sh 60`:
  - A = f2rr1 과 같은 18 토픽, UDP 전용 기록기, 60 s
  - B = A + `/wheel_odom/conditioned /vslam/odom /visual_slam/tracking/odometry /visual_slam/status /pose /behavior_tree_log /local_costmap/published_footprint /rover/guard` + 컬러 · 깊이 영상과 camera_info, **SHM+UDP 기록기**, 60 s. 영상 두 줄은 best effort 로 구독(job551 깊이와 같은 이유).
- 판정(B, 주행 전 선언):
  - ① 컬러 ≥ 4.75 Hz(5 의 95 %) · 깊이 ≥ 14.25 Hz(15 의 95 %)
  - ② `/tf` ≥ 47.5 Hz 이고 A 보다 5 % 넘게 낮지 않음 · `/scan` · `/odometry/filtered` 도 A 대비 5 % 안
  - ③ `/visual_slam/tracking/odometry` ≥ 14.25 Hz(카메라 ↔ cuVSLAM SHM 경로가 안 나빠짐)
  - ④ CPU 전체 B − A ≤ 10 %p
  - 참고: 크기 계산값 컬러 4.6 MB/s + 깊이 ≈ 0.6 MB/s → 1 분 ≈ 310 MB(계산). 없는 토픽(`/pose` 등)은 기록 0 개로 나옴 — 목록에서 뺄 근거.
- 통과하면 B 목록으로 no5 주행(사용자 "시작" 뒤). 불합격이면 원인부터.

## §1 정지 시험 결과 — 통과(①은 계산 방법을 바꿔서 판정)
- prep(`jobs/prep_color_1113.sh 1` → `outputs/prep_color_1113_1.txt`): `PREP_OK` · 위치 차 0.010 m · yaw −0.2° · `BT RateController hz="0.01"` · Smac tol 0.35 — 인자 없이 띄운 표준 prep 이 새 기본값(11-11 §7)으로 뜬 첫 확인. 컬러 파라미터 `String value is: 640x480x5`.
- A/B(`jobs/chk_rec_ab_1113.sh 60` → `outputs/chk_rec_ab_1113.txt`, 로버 정지, 기록기 구독 8 s 뒤 60 s 측정):

| 지표 | A(18 토픽 · UDP) | B(30 토픽 · SHM+UDP) | A2(B 뒤 A 다시, `outputs/chk_rec_ab_1113_A2.txt`) |
|---|---|---|---|
| `/tf` | 48.64 Hz | 49.02 | 49.26 |
| `/scan` | 9.98 | 9.90 | 9.64 |
| `/odometry/filtered` | 29.46 | 29.37 | — |
| CPU 전체(6 코어 평균) | 47.3 % | 51.8 % | 47.3 % |
| 기록기 | 19 % | 41 % | 18 % |
| nvblox_node | 35 % | **58 %** | 35 % |
| realsense 프로세스 | 19 % | 20 % | 19 % |
| 크기 | 30 MB | 345 MB(66.2 s → 5.2 MB/s) | 30 MB |

- 판정(§0 선언):
  - ① 컬러: 선언한 계산(개수 ÷ bag 전체 길이)으로는 **4.73 Hz < 4.75 → 미달**. bag 전체 길이에는 기록기 시작 뒤 첫 컬러 전 구간이 들어가 낮게 나옴 → 메시지 stamp 간격으로 다시 봄(`jobs/anal_color_gaps_1113.py` → `outputs/anal_color_gaps_1113.txt`):
```
/camera/camera/color/image_raw: 313 개 · 수신 첫~끝 64.88 s → 4.809 Hz · stamp 간격 중앙 208.0 ms · 최소 207.6 · 최대 208.9 · 중앙의 1.5 배 넘는 간격 0 개
  컬러 640x480 rgb8 · 921600 B/장
/camera/camera/depth/image_rect_raw: 977 개 · 수신 첫~끝 64.90 s → 15.039 Hz · … 중앙의 1.5 배 넘는 간격 0 개
/visual_slam/tracking/odometry: 980 개 · 수신 첫~끝 65.11 s → 15.036 Hz · … 중앙의 1.5 배 넘는 간격 0 개
```
    → **손실 0, 카메라의 '5 fps' 는 실제 4.81 Hz(간격 208 ms)**. 결과를 본 뒤 계산 방법을 바꿔 통과로 판정했음을 적는다(§2 부터는 stamp 간격 방식으로 선언).
  - ② `/tf` 49.02 ≥ 47.5 · A 보다 높음 ✔, `/scan` −0.8 % · `/odometry/filtered` −0.3 % ✔
  - ③ cuVSLAM 15.04 Hz ✔(첫~끝 방식) — 카메라 ↔ cuVSLAM SHM 경로 영향 없음
  - ④ CPU 전체 +4.5 %p ≤ 10 ✔
- **설명 못 한 것**: B 에서 nvblox_node CPU 35 → 58 %(코어 1 기준 +23 %p). A2 에서 35 % 로 돌아와 시간 변동이 아니라 B 조건과 같이 움직임(재현 1 회). nvblox 는 기록기와 데이터를 주고받지 않는다 — 기전 미확인. 후보(추정): 기록기가 카메라 프로세스의 SHM 참가자가 되면서 카메라의 깊이 발행 경로가 바뀌어 nvblox(컨테이너) 쪽 수신 처리가 달라짐. 주행 중 nvblox 깊이 주기 · CPU 를 같이 본다.
- 목록 정리(B 기록기 로그): `/visual_slam/status` 는 호스트에 메시지 패키지가 없어 기록 불가(`unknown type 'isaac_ros_visual_slam_interfaces/msg/VisualSlamStatus'`), `/pose` 는 `has more than one type associated` → 둘 다 뺌. `/behavior_tree_log` · `/rover/guard` 는 정지 중 0 개(목표가 없음 — 주행 때 확인).
- 그 밖: `/dev/shm` fastrtps 세그먼트 22 개(기록기 B 가 끝난 뒤) — 다음 prep 의 `fastdds shm clean` 이 고아만 정리.
- 러너: `job551_f0drive.sh` 가 스크래치패드에서 사라져 있어(7 일 자동 삭제) 저장소 `2026-11-03/jobs/job551_f0drive.sh` 에서 복구 + `BAG_COLOR=1`(컬러 + camera_info + 깊이 · 홈 사본, 컬러 best effort, tgz 생략) · `BAG_SHM=1`(기록기만 SHM+UDP) → `jobs/job551_f0drive.sh`. `run_f0.sh` 가 두 변수를 Jetson 으로 넘기게 고침 → 가린 사본 `jobs/run_f0.sh`. f2rr1 이 실제로 쓴 job551 이 11-03 판과 같은지는 확인 못 함(Jetson /tmp 소실) — 11-03 뒤 저장소에 바뀐 판 없음.

## §2 README 시각화 기록 주행 f2rd1 선언 (결과 보기 전)
- 목적: 스택별 GIF 의 원천 bag. 구성 = 표준 prep(인자 없이 = smac · 0.01 Hz · vslam · lite) + `SENSORS_ADD="color_fps:=5"`. 표준과 다른 점 = 컬러 15 → 5 fps · 기록기 SHM+UDP · 기록 토픽 늘림(주행 스택 값은 같음). 출발 직전 prep 다시(정지 시험이 DDS 참가자를 만들고 지웠음).
- 러너: `run_f2c.sh f2rd1 "<NOTE>" <GIT_HEAD> no5`, 환경 `BAG_COLOR=1 BAG_SHM=1 STAGE=F2c-std-color5 EXTRA_TOPICS_ADD="/wheel_odom/conditioned /vslam/odom /visual_slam/tracking/odometry /behavior_tree_log /local_costmap/published_footprint /rover/guard"`. 코스 no5(8 목표, 속도 0.07) — f2tt1 · f2tt2 · f2rr1 과 같은 코스.
- 판정:
  - ① 8 목표 SUCCEEDED · ABORT 0 · nav_guard 0(러너 원문) ② 접촉 0(사용자) ③ 주행 중 nav2 TF 외삽 0 ④ 사람 개입 0(있으면 따로 적음)
  - ⑤ 기록: 컬러 stamp 간격 중앙 ≈ 208 ms · 1.5 배 넘는 간격이 전체의 ≤ 1 % · 깊이 · cuVSLAM 같은 방식 ≤ 1 % · `/tf` 개수 ÷ 첫~끝 ≥ 47.5 Hz · 홈 사본 `/home/jetson/bags/bag_f2rd1` 존재
  - 참고: 총 시간(f2rr1 434.4 s), 크기 계산 ≈ 450 s × 5.2 MB/s ≈ 2.3 GB(계산), nvblox 깊이 주기 · CPU(§1 미확인 항목).
- 표준 검증: ① ~ ④ 통과면 '인자 없이 띄운 표준 prep' 의 첫 성공 주행으로 CURRENT_STACK '검증 주행' 줄에 더할 후보(컬러 5 fps · 기록기 차이는 함께 적음 — 사용자 판단).

## §3 f2rd1 결과 · 서쪽 통로 이슈 분석 (사용자: "서쪽통로에서 주행하는데 이슈가 있었는데, 없는 상태로 다시 만들고 싶으니, 원인을 분석하고, 해결한 후 다시 기록하자.")
- prep(`jobs/prep_color_1113.sh rd1`): PC 쪽 출력이 필터(grep 이 이진으로 판단)에서 깨져 원문을 못 받음 → Jetson 원문을 `jobs/chk_prep_tail_1113.sh rd1` 로 다시 읽음 → `outputs/prep_color_1113_rd1.txt`: `PREP_OK` · 위치 차 0.010 m · yaw +0.1° · `BT RateController hz="0.01"`.
- 러너(`outputs/run_f2rd1.txt`, 원문 `outputs/f0_f2rd1.log`, 산출물 `bags/f0_f2rd1/` — csv · proc · tegra): 게이트 P 46 % · 기록기 `fastdds_shm_udp.xml · 토픽 31 개` → **8/8**, 51.8 · 54.5 · 53.3 · 50.5 · 48.2 · 34.7 · 97.1 · 98.1 s, **총 488.7 s**(f2rr1 434.4). stuck 진단 3(그림자). 컬러 bag `/home/jetson/bags/bag_f2rd1` 2.9 GB(PC 로 아직 안 옮김).
- §2 판정: ① ✔(8/8 · ABORT 0 · nav_guard 0) ② ④ 사용자 확인 대기 ③ nav2 TF 외삽은 아래 사건 파일에 없음(정식 집계 전) ⑤ 기록 미집계.
- 사건(`jobs/up_nav_events_1113.sh 15:45:50 16:10:00` → `outputs/nav_events_f2rd1_live.txt`, 347 줄) — f2rr1(`2026-11-11/outputs/nav_events_f2rr1.txt`)과 셈:

| | f2rr1 | f2rd1 |
|---|---|---|
| 컨트롤러 주기 놓침 | 43 | 127(15:48 38 · 15:49 42 · 15:50 39) |
| 막힘 정지(지속 → 중단 줄) | 4 | 10 |
| Smac `Starting point in lethal space` | 0 | 6 |
| MPPI `Optimizer fail to compute path` | 1 | 11 |
| 탈출 동작 · Wait | 1 · 0 | 3 · 3 |
| 목표 3 ~ 6 시간 | 119 s | 187 s |

- 가설 1 '기록 부하(컬러 · 깊이 SHM)로 CPU 가 밀렸다' → **약함**. `jobs/anal_proc_window_1113.py` → `outputs/anal_proc_window_1113.txt`: 서쪽 통로 창 전체 사용률 f2rd1 70.5 % · f2rr1 68.1 %, controller_server 44.2 · 43.2 %, nvblox_node 17.4 · 15.8 %, 기록기(`ros2`) 37.4 · 28.3 %. 복귀 창도 69.9 · 66.8 %. (§1 의 nvblox 35 → 58 % 는 pgrep -f 패턴 합계로 잰 값이라 이 표의 nvblox_node 와 같은 대상이 아님 — 미확인 그대로)
- 가설 2 '통로 안 코스트맵이 달랐다' → 그림 `figures/corridor_cmp_f2rr1_f2rd1.png`(`jobs/fig_corridor_cmp_1113.py`, f2rd1 코스트맵은 `jobs/anal_costmap_crop_1113.py` → `outputs/anal_costmap_crop_f2rd1.txt` 로 Jetson bag 에서 잘라 옴), 줄별 폭 `jobs/anal_corridor_width_1113.py` → `outputs/anal_corridor_width_1113.txt`:
```
y      | 저장지도 빈 폭(x 범위)  | f2rr1 14:55:44 (<99)  | f2rd1 15:48:03       | f2rd1 15:49:06
-4.40  | 0.95 (-2.05~-1.15) | 0.40 (-1.89~-1.54) | 0.35 (-1.89~-1.59) | 0.25 (-1.89~-1.69)
-4.00  | 0.80 (-2.05~-1.30) | 0.45 (-1.94~-1.54) | 0.45 (-1.94~-1.54) | 0.25 (-1.94~-1.74)
-2.70  | 1.05 (-2.15~-1.15) | 0.55 (-2.04~-1.54) | 0.00 (-1.74~-1.74) | 0.45 (-2.04~-1.64)
-2.60  | 1.10 (-2.20~-1.15) | 0.70 (-2.04~-1.39) | 0.00 (-1.74~-1.74) | 0.45 (-2.04~-1.64)
```
  - (→ §7 에서 정정: 안쪽 y −4.0 ~ −4.5 비교는 f2rr1 이 지나가기 전 시각이라 부적합, 실제 차이 5 ~ 10 cm)
  - 읽기: 저장 지도는 같고, **통로 동쪽 가장자리만** f2rd1 에서 0.1 ~ 0.25 m 안으로 들어옴(입구 y −2.6 ~ −2.8 은 15:48:03 에 x = −1.75 열까지 막힘). 서쪽 가장자리는 두 주행이 같음 → 위치 추정이 통째로 어긋난 것은 아님(추정). 그 칸이 라이다 · nvblox 중 어느 층에서 왔는지는 미확인.
  - 한계: 폭 계산은 x = −1.75 열을 포함하는 연속 구간이라, 통로가 서쪽으로 꺾이는 y −3.0 ~ −3.2 는 f2rr1 도 0 으로 나옴(그 줄은 읽지 않음).
- 컬러 장면(`jobs/anal_color_frames_1113.py` → `figures/f2rd1_color_154758 · 154802 · 154847 · 154852.jpg`, 15:50:28 장은 사람이 찍혀 `bags/f0_f2rd1/` 로 옮김 · base64 원문도 `bags/` 로 — §11): 15:48:02(로버 ≈ (−1.74, −2.26), yaw ≈ −114° — 러너 csv 시각을 첫 목표 시작에 맞춘 근사) 화면 왼쪽(= 통로 동쪽) 아래 가까이에 종이 상자. 11-11 엔 컬러 기록이 없어 그때 있었는지는 기록으로 못 가림 → 사용자 확인.

## §4 원인 결론 · 재기록 f2rd2 선언 (사용자: "통로 입구 및 안쪽 장애물 구성이 달랐을 것이다.")
- 결론: f2rd1 서쪽 통로의 막힘 · 후진 · 재계획 실패는 **11-11 과 다른 통로 장애물 배치**(입구 · 안쪽 동쪽 가장자리)로 통과 폭이 0.1 ~ 0.25 m 좁아진 탓 — §3 의 코스트맵 비교 + 사용자 확인. 기록 부하(가설 1)는 근거 약함(§3 CPU 표). 어느 물건이 얼마나 달랐는지는 사용자 기억 기준(측정 아님).
- f2rd1 의 처분: 앞 구간(목표 1 · 2 · 7 · 8)은 시각화 재료로 쓸 수 있음. bag 2.9 GB 는 README §6(GB 급: 시각화 → 사용자 확인 → 삭제) 대상 — 지금은 Jetson 홈에 둠.
- 해결: 사용자가 통로를 11-11 배치로 되돌림(입구 · 안쪽 동쪽 물건 치움). 로버 출발 위치 · 출발 상자는 그대로.
- f2rd2 선언(결과 보기 전): 구성 · 러너 · 기록은 §2 와 같음(이름만 f2rd2, NOTE '11-13 §4 통로 배치 복원 뒤 재기록'). 판정 = §2 ① ~ ⑤ + 서쪽 통로(목표 3 ~ 6):
  - ⑥ Smac `Starting point in lethal space` 0 · MPPI `Optimizer fail to compute path` ≤ 1 · 막힘 정지 ≤ 2 번(f2rr1 = 2 번, 통로 입구 1 · 복귀 상자 1) · 목표 3 ~ 6 합 ≤ 135 s(f2rr1 119 s + 약 15 %)
  - ⑦ 통로 폭 확인: 15:48 같은 위치(입구 y −2.6 ~ −2.8)의 비용 < 99 구간 동쪽 끝이 x ≥ −1.60(f2rr1 −1.54 ~ −1.39) — `jobs/anal_costmap_crop_1113.py` 로 다시 잼.
- (사용자: "통로 안쪽은 그런데, 아마 비슷할 것이다. 입구쪽만 문제. 우선 로버를 다시 놓았다.") — 안쪽(y −4.0 ~ −4.5, §3 에서 동쪽 15 cm 좁음)은 사용자 판단으로 11-11 과 비슷 → ⑥ 이 안쪽에서 걸리면 그 위치를 따로 적는다. prep `outputs/prep_color_1113_rd2.txt`: `PREP_OK` · 위치 차 0.008 m · yaw +0.5° · 배터리 12.15 V(f2rd1 전 12.37).

## §5 f2rd2 결과 — 입구는 해결, 안쪽(목표 5)에서 nav_guard 취소
- 러너 `outputs/run_f2rd2.txt`(원문 `outputs/f0_f2rd2.log`, 산출물 `bags/f0_f2rd2/`): 게이트 G2 0.220 m · P 48 % → 목표 1 53.0 · 2 55.1 · **3 27.0 · 4 33.2 s(SUCCEEDED_XY)** · **5 CANCELED 63.0 s**(도착 map (−1.498, −4.752, 92.5°), 목표 대비 1.063 m) → 6 ~ 8 시도 안 함. stuck 진단 6. 컬러 bag `/home/jetson/bags/bag_f2rd2` 1.4 GB.
- 읽기: 입구를 정리한 뒤 목표 3 · 4 는 f2rr1(31.0 · 28.7 s)과 비슷하거나 빠름 → **입구 배치가 f2rd1 이슈의 원인**이었다는 §4 결론과 맞음.
- 목표 5(남쪽 끝 → 통로 북쪽) 사건(`jobs/up_nav_events_1113.sh 16:07:40 16:13:00` → `outputs/nav_events_f2rd2.txt`):
```
16:10:47.66 bt_navigator Begin navigating from current location (-1.54, -5.37) to (-1.65, -3.70)
16:10:51.08 PathBlockedAhead: 앞 경로 (-1.61, -4.51) 비용 99 가 2.0 s 지속 → 주행 중단·재계획
16:10:52.08 planner_server SmacHybrid: failed to create plan, invalid use: Starting point in lethal space!
16:10:52.11 smoother_server Smoothed path leads to a collision at x: -1.510259, y: -4.742955
16:11:02.09 PathBlockedAhead: 앞 경로 (-1.54, -4.61) 비용 99 가 2.0 s 지속 → 주행 중단·재계획
16:11:02.14 [monotone_escape] 시작 최근접 13.9 cm · … → 성공: 최근접 13.9 cm
16:11:02.20 planner_server SmacHybrid: failed to create plan, no valid path found.
16:11:11.04 stuck_monitor STUCK: 지령 1.7cm/19° 인데 관측 2.0cm/1.7° (비율 0.09) [shadow — 조치 없음]   (16:11:49 까지 5 번)
16:11:32.69 controller_server Failed to make progress
16:11:50.49 nav_guard nav_guard 개입 — 무진행: 45 s 동안 최대 0.24 m 이동 < 0.25 m → 모든 목표 취소·정지
```
  - 막힌 자리 (−1.61, −4.51) · (−1.54, −4.61) = §3 에서 f2rd1 도 동쪽 가장자리가 15 cm 좁았던 y −4.0 ~ −4.6 구간. Smac 은 경로 없음 → NavFn 원경로(충돌 판정) → MPPI 는 제자리 회전을 지령(15 ~ 20°)했지만 관측 회전 0.1 ~ 3° — 회전이 안 됨(접촉 · 걸림인지는 미확인, 사용자 확인).
  - 컬러 장면: `figures/f2rd2_color_161049.jpg`(목표 5 시작, 오른쪽 가까이 검은 천 가방 · 회색 공구 상자), `bags/f0_f2rd2/f2rd2_color_161120.jpg`(git 제외 — 북쪽을 봄 — 오른쪽 = 동쪽 가까이 상자들 · 빨간 물건, 통로 끝에 사람 1 명). ⚠ 사람이 찍힌 사진은 공개 저장소로 나가면 안 됨 → 커밋 전 처리 결정 필요.
- §4 판정: ① ✘(목표 5 nav_guard 취소) — f2rd2 는 불합격. ⑥ 목표 3 · 4 는 lethal 0 · 막힘 정지 0(목표 3 · 4 구간 해당 줄 없음), 목표 5 에서 lethal 1 · 막힘 정지 2.
- 지금 로버: 통로 안 (−1.50, −4.75) 에 정지. 스택은 떠 있음.

## §6 f2rd2 bag 분석 — 왜 탈출 못 했나 · 큰 방향 전환이 있었나 (사용자: "아무것도 걸리지 않았다. 우선 bag분석부터 하자. 왜 탈출 못했는지, 그리고 서쪽 통로에서 목적지로 들어갈 때 한번 큰 방향전환이 있었는지 분석")
- 재료: `jobs/anal_series_1113.py <bag_f2rd2> 2026-11-13 16:09:20 16:11:55`(Jetson, bag 은 옮기지 않음) → `outputs/anal_series_f2rd2.csv`(59 662 줄: /cmd_vel · /wheel_odom · /odometry/filtered · /rover/status · /plan · /behavior_tree_log · map→odom). 1 s 칸 요약 `jobs/anal_series_bins_1113.py` → `outputs/anal_series_bins_f2rd2_goal5.txt` · `_goal34.txt`. 보드 상태 필드 = `tgt=목표 mm/s v=측정 mm/s d=duty %`(`firmware/rover_jupiter_fw/App/microros/microros_task.c` 111 행).
### §6.1 바퀴는 지령대로 돌았다(기계 문제 아님 — 사용자 관찰과 일치)
```
시각      지령v   지령w | L목표 L측정 L듀티 | R목표 R측정 R듀티 | EKFw  map yaw
16:10:49  -0.025  0.360 |   -85   -84   -86 |    47    41    62 |  0.38   -71.9     ← 목표 5 시작: 제자리 반바퀴
16:11:03   0.080  0.214 |    21    23    47 |    85    86    90 |  0.15    90.5     ← 약 200° 돌아 북쪽을 봄
16:11:10   0.005 -0.182 |    48    46    65 |   -32   -32   -45 | -0.19    92.3     ← 여기부터 v ≈ 0, w 가 ± 로 번갈아
16:11:24   0.002 -0.284 |    70    51    78 |   -67   -69   -76 | -0.33    94.2
16:11:25   0.013  0.286 |   -37   -24   -45 |    57    48    55 |  0.24    90.2
```
  - 목표 ≈ 측정(차이 대부분 ≤ 10 mm/s) · 스톨 메시지 없음. stuck_monitor 의 '지령 19° · 관측 1.7°' 는 **좌우로 번갈아 도는 지령의 절댓값 합 대 순 변화**라 '회전이 안 됨' 처럼 보인 것 — 코드 확인: `ros2_ws/src/rover_bringup/scripts/stuck_monitor.py` 10 행 '창(WINDOW s) 동안 지령 적산 ∫|v|dt, ∫|ω|dt', 145 행 `sum(abs(pts[i][idx]) * (pts[i][0] - pts[i-1][0]) …)` 대 172 행 관측 `rot_obs = abs(rot_scan)`(순 변화). 보드 `cmd_vel timeout — motors stopped` 는 지령 간격 0.85 s(16:10:14.61 → 15.46, 목표 3 → 4 넘어갈 때) · 0.75 s(16:10:51.41 → 52.16, 막힘 정지 때) 두 번(`outputs/anal_cmd_gaps_f2rd2.txt`).
### §6.2 탈출 못 한 기전 — 계획 · 탈출 · 컨트롤러가 서로 다른 기준으로 '괜찮다/안 된다' 를 판단한 교착
- 순서(`outputs/nav_events_f2rd2.txt` · 위 표): ① 남쪽 끝에서 제자리 반바퀴 도는 중(16:10:49) 카메라가 통로 동쪽 물건을 새로 봐 Smac 경로의 (−1.68, −4.31) · (−1.61, −4.51) 이 비용 99 → 막힘 정지 ② 재계획: Smac `Starting point in lethal space`(남쪽 끝에서 차체 중심이 치명 칸) → NavFn 대체 경로, 스무더는 (−1.51, −4.74) 충돌 판정 → 다듬지 않은 원경로(CopyPath) ③ 로버는 그 원경로를 따라 x ≈ −1.49 로 **곧게 북진**(heading 96°) ④ y ≈ −4.75 에서 통로가 서쪽으로 꺾이는 자리(통과 가능 구간 y −4.5: x −1.79 ~ −1.64)에 차체 중심이 동쪽으로 0.1 m 이상 벗어난 채 도착 → 앞 궤적 전부 비용 → MPPI v ≈ 0 · w ± 반복 ⑤ 막힘 정지 → `monotone_escape 시작 최근접 13.9 cm · 목표 5.0 cm … 성공` = 차체 외곽 여유 기준으론 '이미 괜찮음' 이라 안 움직임 → Smac `no valid path` → 다시 ④ ⑥ 45 s 무진행 → nav_guard 취소.
- f2rr1 과의 차이(`outputs/anal_goal5_turn_cmp.txt`): 남쪽 끝 반바퀴는 둘 다 같음(0 ~ 16 s, −107° → 93°). 그 뒤 f2rr1 은 y −4.88 ~ −4.82 에서 heading 102 ~ 107°(서쪽으로 비스듬히) 로 꺾이는 자리를 따라감, f2rd2 는 96° 그대로 곧게 가다 y −4.93 에서 멈춤. f2rr1 목표 5 엔 Smac 실패 · 막힘 정지가 없음 → Smac 경로(꺾임을 따라가는)를 그대로 따라감.
- 통로 폭(로버가 지나간 **뒤** 시각끼리, `jobs/anal_corridor_rows_1113.py --rr1t` → `outputs/anal_corridor_rows_f2rd2_after.txt`): y −4.5 통과 가능 구간 f2rr1 14:56:35 0.25 m(−1.79 ~ −1.59) · f2rd2 16:10:49 0.20 m(−1.79 ~ −1.64), y −4.3 0.35 · 0.25 m → f2rd2 가 동쪽에서 **5 ~ 10 cm** 좁음. → §7 정정.
- 결론: 기계 · 부하 문제 아님. **통로 남쪽의 동쪽 가장자리가 5 ~ 10 cm 좁아(배치 차이 추정 — 컬러 `figures/f2rd2_color_161049.jpg` 의 검은 천 가방 · 공구 상자, `bags/f0_f2rd2/f2rd2_color_161120.jpg`(사람이 찍혀 git 제외 폴더로 옮김) 의 동쪽 상자들) 반바퀴 도는 중 막힘 정지 → 남쪽 끝에서 Smac 실패 → NavFn 원경로가 꺾임을 따라가지 않음 → 꺾이는 자리에서 차체가 치명 칸에 걸린 채, 탈출 동작은 외곽 여유 13.9 cm 를 보고 '괜찮음' 이라 안 움직이는 교착.** 탈출 동작의 판정(외곽 여유 ≥ 5 cm)과 Smac 의 판정(중심 칸 비용)이 다른 것이 구조적 빈틈(f2rd1 의 `lethal space` 6 회도 같은 꼴).
### §6.3 큰 방향 전환
- 목표 3 진입(16:09:47 ~ 55): C 에서 서쪽 통로로 왼쪽 약 88° 회전(−180° → −92°) — 코스 모양대로.
- 목표 4(통로 남쪽으로, `outputs/anal_goal4_yaw_cmp.txt`): f2rd2 −79 → −113 → −61 → −97°, f2rr1 −61 → −98 → −68 → −101° — 같은 S 자(±30 ~ 35°). 통로가 남쪽으로 갈수록 동쪽으로 꺾이는 모양(통과 가능 구간 y −4.2 x −1.94 ~ −1.54 → y −5.1 x −1.64 ~ −1.34)을 따라간 것. f2rd1 만 −179° 까지 크게 돌았음(목표 4 16 ~ 22 s).
- 목표 5 시작(16:10:48 ~ 16:11:04): 남쪽 끝에서 **제자리 약 200° 회전** — f2rr1 도 같음(목표 4 가 남쪽을 보고 목표 5 가 북쪽이라 필요한 회전). 사용자가 본 '큰 방향 전환' 이 이것이면 정상 동작, 다른 장면이면 시각을 받아 다시 본다.

## §7 내 실수 — 통로 안쪽 비교에 '로버가 지나가기 전' 코스트맵을 씀(§3 정정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | §3 에서 f2rr1 과 f2rd1 의 서쪽 통로 통과 폭 비교(`jobs/fig_corridor_cmp_1113.py` · `jobs/anal_corridor_width_1113.py`) |
| 본 것 | f2rr1 14:55:44 대 f2rd1 15:49:06, y −4.0 ~ −4.5 동쪽 끝 −1.54 대 −1.69 |
| 처음 추론 | f2rd1 은 안쪽 동쪽 가장자리도 약 15 cm 좁다 → 안쪽 배치도 달랐을 것(§3 · §5 에서 사용자에게 그렇게 말함) |
| 의심한 이유 | f2rd2 16:09:00(로버가 안쪽에 가기 전) 코스트맵이 f2rr1 14:55:44 와 안쪽이 칸 단위로 같고, 지나간 뒤(16:10:49)에야 좁아짐 → 비교 시각이 '지나가기 전 대 지나간 뒤' 였음 |
| 판별 시험 | f2rr1 도 지나간 뒤(14:56:35 · 14:57:00)로 다시 비교(`jobs/anal_corridor_rows_1113.py --rr1t`) |
| 결론 | 안쪽 차이는 15 cm 가 아니라 **5 ~ 10 cm**(y −4.5: 0.25 대 0.20 m). 사용자의 "안쪽은 비슷할 것" 이 더 가까웠음. 차이 자체는 남아 §6.2 교착의 한 조건 |
| 다음에 알아보는 법 | 센서가 채우는 전역 코스트맵을 주행 간 비교할 때는 **같은 자리를 지나간 뒤 같은 상대 시점**끼리. 시각만 맞추지 않는다 |
| 스크립트 핵심 | `crop_from_bag(rr1, rr1t, '2026-11-11')` — 예전엔 `'14:55:44'` 고정 |
| 나온 결과 | `y −4.50 | f2rr1 14:56:35 0.25 (-1.79~-1.59) | 161049 0.20 (-1.79~-1.64)` |
| 데이터 | `outputs/anal_corridor_rows_f2rd2.txt`(지나가기 전 포함) · `outputs/anal_corridor_rows_f2rd2_after.txt` · f2rr1 bag(PC 스크래치패드 압축 해제본, 원본 `2026-11-11/bags/f0_f2rr1/bag_f2rr1.tgz`) · f2rd2 bag `/home/jetson/bags/bag_f2rd2` |

## §8 교착 기전 다시 보기 — 본체는 '충돌 판정된 원경로를 붙잡고 45 s' (사용자: "교착 문제부터 고치자")
- §6.2 를 BT 로그로 다시 맞춤(`outputs/nav_events_f2rd2.txt` · `outputs/anal_series_f2rd2.csv` 의 bt 줄, BT `ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml`):
  - 16:11:02.20 Smac `no valid path` → NavFn → 16:11:02.27 스무더 `collision at x: -1.521952, y: -4.742779` → CopyPath 원경로 → 16:11:02.29 컨트롤러가 받음.
  - 그 뒤 16:11:50 까지 **새 계획 0 개**(`/plan` 마지막 16:11:02.248). PathBlockedAhead 는 `only_new="true"`(받을 때 이미 99 인 점은 무시, 10-23 §20.2) 라 이 원경로에서 막힘을 안 셈.
  - MPPI 는 앞 궤적이 모두 비싸 v ≈ 0 · w ± 반복(§6.1 표). 진행 검사기 `PoseProgressChecker` 0.25 m 또는 0.5 rad / 25 s(`nav2_params.yaml` 96 ~ 99 행) → 16:11:32.69 `Failed to make progress` → 안쪽 `RecoveryNode FollowPath`(재시도 1) 가 로컬 정리만 하고 **같은 경로로 다시 FollowPath** → 다시 25 s 를 기다리는 중 16:11:50.49 nav_guard(0.25 m / 45 s, `nav_guard.py` 13 · 34 행)가 먼저 전체 취소.
  - 그래서 재계획 · 바깥 복구(정리 → 탈출 → 대기)는 한 번도 돌지 못함. 앞의 16:11:02 탈출 동작은 막힘 정지 경로였고, 최근접 13.9 cm ≥ 목표 5 cm 라 `이미 여유 있음 → 첫 주기에 성공`(`monotone_escape_behavior.cpp` 106 행) — 움직이지 않음.
- 전역 코스트맵 중심 칸(`outputs/anal_costmap_crop_f2rd2.txt`): 16:10:49 로버 (−1.535, −5.385) 76, 16:11:20 (−1.497, −4.858) 64 → 중심이 치명 칸인 순간은 16:10:52 한 번(그때 `Starting point in lethal space`). 교착의 대부분은 '치명 칸 안' 이 아니라 위 시간 구조.
- 정리(기전, 측정 기반): ① 충돌 판정된 원경로를 따름 ② 그 경로의 막힘은 only_new 로 안 셈 ③ 진행 실패 판정 25 s + 같은 경로 재시도 25 s = 50 s > nav_guard 45 s ④ 탈출 동작은 '여유 ≥ 5 cm' 면 움직이지 않음.

## §9 교착 수정 계획(구현 안 함 — 사용자: "우선 계획만 세워놓고, 오늘 일 마무리하자.")
- 목표: §8 의 교착(충돌 판정 원경로를 붙잡은 채 진행 실패 판정 25 s × 2 > nav_guard 45 s, 탈출 동작은 여유 ≥ 5 cm 면 안 움직임)을 없앤다. 구현 전에 아래 0 · 1 로 근거를 먼저 만든다.
- 0. 근거(PC, 로버 안 움직임): 성공 주행(f2tt1 · f2tt2 · f2rr1 · f2rd2 목표 1 ~ 4)의 러너 csv · bag 에서 '0.25 m 도 0.5 rad 도 못 움직인 구간'의 길이 분포를 센다 → 진행 검사 시간을 얼마로 줄여도 정상 주행이 걸리지 않는지(예: 최대 무진행 구간 + 여유). 지금 값 25 s 의 근거는 09-02 회전 오판 기록뿐.
- 1. 탈출 동작 오프라인 모의(PC): f2rd2 bag 의 `/local_costmap/costmap`(1.7 Hz) + 자세로 16:11:02 ~ 16:11:50 교착 자세에서 `monotone_escape_behavior.cpp` 의 `clearance()` 를 파이썬으로 옮겨, '여유가 줄지 않으면서 지금보다 δ(후보 2 · 3 · 5 cm) 넓히는' 앞 · 뒤 · 좌 · 우 움직임이 있는지 본다. 없으면 A2 는 이 교착에 무효 → 다른 수단(예: 막힌 경로 재계획 시 원경로 대신 실패 처리) 재검토.
- 2. 구현 후보(0 · 1 결과로 확정):
  - A1 `nav2_params.yaml` `progress_checker.movement_time_allowance` 25 → (0 의 결과) s — nav_guard(45 s) 안에 안쪽 재시도 + 바깥 복구(재계획 → 탈출 → 대기)가 들어가게. 안쪽 FollowPath 재시도는 그대로.
  - A2 `monotone_escape_behavior.cpp` 106 행: `c0 ≥ target` 이면 바로 성공하던 것을 `min_gain` 파라미터(기본 0 = 지금과 같음)로 '목표 = max(target, c0 + min_gain)' — 이미 여유가 있어도 자세를 바꾼 뒤 재계획되게. Jetson 에서 `colcon build --packages-select rover_navigation`.
  - 기각(§8 답변): 스무더 충돌 시 원경로 안 쓰기(11-10 f2dm2 사람 구간에서 원경로로 통과) · `only_new` 끄기(10-23 거짓 막힘 5 회).
- 3. 시험(주행 전 판정 선언, 사용자 "시작" 뒤): ① 재현 — 오늘 배치 그대로(통로 남쪽 동쪽 물건 유지) 로버를 (−1.50, −4.75) · 북쪽(≈ 92°)에 두고 목표 (−1.65, −3.70): nav_guard 개입 없이 60 s 안 도착 · 접촉 0. ② 회귀 — no5 1 회(정상 배치): 8/8 · 접촉 0 · TF 실패 0. ③ 표준 갱신은 같은 구성 연속 3 회 뒤(README §2.2 — 그 전엔 '미검증').
- 범위 밖으로 남김: 스무더가 충돌로 판정한 원경로를 따를 때 그 점들의 막힘을 다시 셀지(only_new 예외) — A1 · A2 결과를 보고.

## §10 bag 처리 방안(제안 — 아무것도 지우지 않음, 사용자: "오늘 기록한 bag 용량이 너무 큰데, 어떻게 처리할지만 생각.")
- 현황(`jobs/chk_bags_1113.sh` → `outputs/chk_bags_1113.txt`): 디스크 233 G 중 여유 113 G. 홈 `/home/jetson/bags/bag_f2rd1` 2.9 G · `bag_f2rd2` 1.4 G(재부팅에도 남음), **같은 내용이 `/tmp/bag_f2rd1` · `/tmp/bag_f2rd2` 에 또 있음**(job551 이 /tmp 에 쓰고 홈으로 복사 — `jobs/job551_f0drive.sh` 끝부분), 정지 시험 `/tmp/bag_rab_A · A2`(30 M) · `B`(345 M). 홈 bags 전체 21 G(옛 bag 포함).
- f2rd1 토픽별: 컬러 `2214.8 MB`(76 %) · 깊이 288.1 · nvblox 슬라이스 201.3 · `/trajectories` 129.9 · `/scan` 72.3 · `/imu/data` 33.7 MB. JPEG(품질 80) 한 장 ≈ 28 ~ 46 kB(`figures/*.jpg` 7 장) → 컬러를 JPEG 로 바꾸면 2403 장 ≈ 0.1 GB(계산), f2rd1 ≈ 0.8 GB · f2rd2 ≈ 0.4 GB(계산).
- 제안(순서):
  1. `/tmp` 중복(4.3 G + 정지 시험 0.4 G) — 홈 사본과 같은 내용 · 재부팅 때 어차피 지워짐. 지울지 사용자 확인.
  2. 경량판 만들기(Jetson): 원본을 읽어 컬러만 `sensor_msgs/CompressedImage`(JPEG 80) 로 바꾼 새 bag(나머지 토픽 그대로) → PC `bags/` 로 가져옴. 원본은 README §6 대로 '시각화 → 사용자 확인 → 삭제'.
  3. 다음 기록부터: 기록 때 압축(`…/color/image_raw/compressed` 구독 — 카메라 프로세스가 JPEG 를 만드는 CPU 를 정지 시험으로 먼저 잼) 또는 해상도 424×240 — 둘 다 미시험.
  - f2rd1(8/8, 통로 입구 막힘 장면) · f2rd2(교착 재현 원천)는 둘 다 분석 가치가 있어 경량판은 둘 다 남기는 것을 권함. 옛 홈 bags 21 G 정리는 별도 결정.

## §11 하루 정리 · 남은 것
- 커밋 안 함: `camera.launch.py`(color_fps) 와 오늘 기록. 사람이 찍힌 사진 2 장(`f2rd1_color_155028.jpg` · `f2rd2_color_161120.jpg`)과 컬러 base64 원문은 `bags/`(git 제외)로 옮김 — 커밋 · 공개 대상 아님.
- 로버: 서쪽 통로 안 (−1.50, −4.75) 에 정지, 스택 떠 있음(정지 시간이 길면 다음 주행 전 prep — CLAUDE.md 운용 주의).
- 다음: §9 0 · 1 → A1 · A2 구현 → §9 3 시험 → README GIF 기록 다시(f2rd3).
- 정리 페이지: 본문 `jobs/report_1113_body.html` + 조립 `jobs/fig_report_1113.py`(머리 = `2026-10-28/jobs/report_1028_head.html`, 제목만 바꿈) → `figures/day_summary_1113.html`(307 kB), 게시 https://claude.ai/artifact/B1zBmhPTdDjALKd1Y2Jeh9 (1 판). 쓴 그림 `figures/corridor_cmp_f2rr1_f2rd1.png` · `figures/f2rd1_color_154802.jpg` · `figures/f2rd2_color_161049.jpg`(사람 없는 장면만). 내용은 이 SUMMARY §0 ~ §11 만.
