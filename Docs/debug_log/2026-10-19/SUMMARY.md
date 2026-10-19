# 2026-10-19 SUMMARY — 깊이 bag 기록 · nvblox 오프라인 재생 준비

## §0 오늘 방향 (사용자: "ClearanceBandCritic가 꼭 필요한가? 다른 스택이 하는 일을 중복하여 하게 되는거 아닌가 고민." → "깊이 bag 기록 준비부터 진행하라.")
- 판단(10-19 대화): 크리틱은 Humble MPPI 에 없는 '옆면 정확 거리' 벌점이라 완전 중복은 아니나, 상자 옆 문제에 대응 층이 이미 여럿(CostCritic · PathBlockedAhead · MonotoneEscape · stuck_monitor · nav_guard)이고 증상 회피다 → **보류**(코드 유지 · 꺼 둠). 근본 원인(주행 중 nvblox 옆면 과장 +5~10 cm, 10-15 §29.4)을 먼저 본다.
- 그 수단: 깊이 영상 · camera_info · tf 를 담은 bag 을 한 번 기록 → 컨테이너 nvblox 에 다시 넣어 설정만 바꾼 A/B(같은 입력, 배터리 불필요).
- 시작 상태: Jetson 09:38 재부팅(가동 1 h 21 m) → /tmp prep 5 개 재전송(저장소 판과 같음, `jobs/chk_day_start.sh`). 디스크 151 GB 여유. 러너 래퍼 run_jn.sh 가 scratchpad 에서 사라져 10-08 저장소 판으로 복구(주소 192.168.0.110).

## §1 깊이 토픽 실측 — nvblox 입력은 160×120 (주석 정정)
- 도구 `jobs/chk_depth_topic.sh`(prep 기동 뒤, 로버 안 움직임): /camera/camera/depth/image_rect_raw 발행 reliable · transient_local, nvblox 구독 best effort. camera_info **160×120** · plumb_bob · camera_depth_optical_frame, 14.99 Hz, **581 KB/s**(= 160 × 120 × 2 B × 15).
- 원인: `rover_bringup/launch/camera.launch.py` 의 decimation_filter ×4(09-08, 점군 CPU 용)가 깊이 이미지 자체에도 적용. `nvblox_local.yaml` 머리 주석 "dec 4 는 점군에만 — 깊이 이미지는 원해상도" 는 **틀림** → 주석 정정(값은 그대로).
- 함의(추정, 미검증): 4×4 묶음 평균이 물체 가장자리에서 앞 · 뒤 깊이를 섞어 가장자리를 넓힐 수 있음. 각도로는 1.3 m 에서 화소당 약 1.2 cm 라 +5~10 cm 과장 전부를 설명하긴 작음. 해상도 효과 시험은 decimation 을 끈 기록이 필요하고 실시간 점군 부하가 4 배가 되므로 별도 실험으로 미룸.
- 기록 부담: 정지 30 s 시험(`jobs/rec_depth_test.sh`, 깊이 · tf best effort 구독, `~/bags` 저장) → 깊이 427 장 / 28.5 s = 14.98 Hz(누락 0), 16.7 MiB, 기록기 CPU 무시할 수준.

## §2 nvblox 오프라인 재생 경로 — 동작 확인
- 도구 `jobs/run_nvblox_replay.sh <깊이bag> <꼬리표> [파라미터:=값 ...]`: 컨테이너에 두 번째 nvblox_node 를 **ROS_DOMAIN_ID=42**(실시간 스택 0 과 격리), use_sim_time · `bag play --clock`, 설치본 nvblox_local.yaml + 덮어쓰기. 출력 `~/bags/replay_<꼬리표>`(/nvblox_node/static_map_slice).
- 시험(정지 30 s bag): 재생 29 s, nvblox 깊이 콜백 15.2 Hz · 조각 270 개(약 9.5 Hz) — 경로 동작 ✔. 같은 설정 재생이 실시간과 같은 지도를 내는지는 아직 모름 → §5 R0 로 확인.

## §3 러너에 깊이 기록 옵션
- `job551_f0drive.sh`: `BAG_DEPTH=1` 이면 깊이 · camera_info 를 주행 bag 에 추가, 깊이는 best effort 구독(QoS 재정의), 끝나면 `~/bags/bag_<이름>` 사본(재부팅에도 남음). `run_f0.sh` 가 BAG_DEPTH 를 넘김. 사본 `jobs/`(run_f0.sh 비밀번호 가림).

## §4 분석 도구 · 기준선 — 과장은 nvblox 출력에서 이미 생김
- 도구 `jobs/anal_slice_box.py <주행bag> 이름=조각bag ...`: 로버가 상자 옆일 때 nvblox 조각(거리 ≤ 0) 의 상자 북쪽(로버 쪽) · 서쪽 면 vs 기록 상자. 남동쪽 창문틀 · 드론(y < −0.25) 제외.
- 기존 주행의 실시간 조각(`outputs/anal_slice_box_baseline.txt`): 북쪽 면 과장 중앙 f2w1 **+8.2** · f2u1 **+9.5** · f2u3 **+6.1** · f2v4 **+5.3** cm — 10-15 로컬 코스트맵 기준(+8.2 · +9.6 · +6.1 · +5.3)과 같음 → 과장은 Nav2 코스트맵 단계가 아니라 **nvblox 조각에서 이미 있음**(측정).

## §5 기록 주행 선언(주행 전)
- 주행: b910 1 회, `BAG_DEPTH=1`, 지금 구성 그대로(통합 거리 1.4 · ClearanceBandCritic 끔 · MonotoneEscape 켬), STAGE `F2c-depthrec`. 필요하면 no5 1 회 추가(서쪽 통로 상자).
- R0 재생 충실도(먼저): 같은 설정 재생 vs 그 주행의 실시간 조각 — 북쪽 면 과장 중앙 차 ≤ 1 cm 이고 칸 수 중앙 차 ≤ 2 → 재생 신뢰. 아니면 원인(시각 · tf · 큐 손실)부터.
- A/B(재생, R0 통과 뒤): ① 통합 거리 1.0 ② 복셀 0.025(절단 거리 cm 를 같게 vox 2 → 4 도 함께 따로) ③ esdf site 1.0(정면 정지에선 효과 없었음, 주행 중 재확인). 판정: 북쪽 면 과장 중앙이 같은 bag 재생 기준보다 **3 cm 이상** 줄면 실주행 후보, 상자 칸이 사라지거나(칸 수 중앙 < 3) 실제 면보다 안쪽이면 불합격.

## §6 기록 주행 f2x1(b910, BAG_DEPTH=1) · R0 · 설정 A/B (사용자: "시작")
- prep 재기동(출발 (0.003, −0.007, +0.3°)) → `run_f2c.sh f2x1 … b910`(STAGE F2c-depthrec, GIT aff3a47b) → `outputs/run_f2x1.txt`: 목표 1 · 2 · 3 **모두 성공**(52.8 · 48.0 · 102.6 s, 총 203.6 s). bag 102.6 MB, 깊이 · camera_info 각 3159(14.96 Hz), 실시간 조각 1994(9.45 Hz). 사본 Jetson `~/bags/bag_f2x1`.
- 재생 도구 수정: 첫 R0 출력 조각이 3997(2 배) — 주행 bag 에 든 실시간 조각까지 재생돼 섞임 → `bag play --topics`(깊이 · camera_info · tf · tf_static 만)로 고침.
- **R0 통과**: 실시간 vs 같은 설정 재생 — 북쪽 면 과장 중앙 +5.3 / +5.3 cm, 범위 +1.3~+6.8 같음, 칸 수 중앙 6 / 6(`outputs/anal_slice_box_f2x1_ab.txt`).
- 적용 확인: 재생 로그에 static_mapper 통합 거리 1 · site 1 찍힘(`jobs/chk_replay_params.sh`). 복셀 0.025 는 로그 줄로는 못 찾았으나 출력 크기 5 → 24 MB · 칸 수 6 → 19 로 적용 확인.
  | 재생 설정 | 북쪽(로버 쪽) 면 과장 중앙 · 범위 | 서쪽 면 | 칸 수 중앙 | 판정(§5: 3 cm 이상 감소) |
  |---|---|---|---|---|
  | 기준(= 실시간) | +5.3 · +1.3~+6.8 | −0.1 | 6 | — |
  | ① 통합 거리 1.0 | +5.3 · 같음 | **−3.1(덜 찍힘)** | 4 | ✘ |
  | ③ site 1.0 | +5.3 · 같음 | −0.1 | 6 | ✘ |
  | ② 복셀 0.025 | **+6.9** · +5.4~+9.6 | +2.3 | 19 | ✘(더 커짐) |
  | ②b 복셀 0.025 + 절단 4 vox | **+6.7** · +3.7~+7.2 | +10.8 | 34 | ✘ |

## §7 nvblox 깊이 전처리 — 3.2.5 에서 켜면 중단
- 근거: 통합 · site 를 바꿔도 과장이 같음 → 입력 깊이(가장자리 섞인 화소, 09-14 '실루엣 비산점' — depth_relay 는 점군에서만 거르고 nvblox 는 원 깊이를 받음)를 의심.
- `static_mapper.do_depth_preprocessing:=true`(팽창 4 · 2) 재생 → 조각 1 · 2 개. 로그(`jobs/chk_replay_log.sh`): `image_impl.h:248 Check failed: mask.rows() == image.rows() (0 vs. 120)` → abort. 이 버전에선 못 씀(소스 수정 필요).

## §8 bag 단계 가장자리 화소 거르기 — 효과 없음
- 규칙(시험 전 선언, `jobs/depth_edge_filter.py`, Jetson rosbag2_py): 유효 화소 중 3×3 이웃과 깊이 차 > max(5 cm, 4 % × 깊이) 인 것을 0 으로. 결과 유효 화소의 **22.26 %** 제거(비스듬한 바닥 등도 걸린 것으로 추정).
- 재생: 북쪽 면 과장 +5.3 · 범위 +1.3~+6.8 · 서쪽 −0.2 · 칸 7 — **기준과 같음** ✘.

## §9 읽기 — 과장은 nvblox 설정도 깊이 잡음도 아닌 '기하' 쪽일 가능성
- 측정: 통합 거리 · site · 가장자리 거르기 어느 것도 북쪽 면 과장의 중앙과 **범위까지** 바꾸지 않음. 복셀을 줄이면 오히려 커짐(칸 반올림이 줄면 남는 몫이 드러난 것으로 해석 가능).
- 추정(미검증): 남은 후보는 위치 쪽 — (a) 기록 상자 위치 자체(09-22 실측, 출발 배치 오차 1~2 cm) (b) 카메라 외부 보정 yaw(09-18 데크 −2.68° 보정; 1.3 m 에서 1° ≈ 2.3 cm) — 보는 방향마다 면이 다르게 밀림 (c) SLAM/오도메트리 — 비교를 지도 좌표로 하므로 그 순간 map→odom 오차가 그대로 섞임.
- 가르는 방법(다음, 오프라인): 상자 면 위치를 관측 순간의 카메라 방향 · 로버 자세별로 나눠 보기 — 방향에 따라 부호가 바뀌면 (b), 지도에서 늘 같으면 (a), 주행 따라 커지면 (c). 같은 bag 재생으로 가능.
