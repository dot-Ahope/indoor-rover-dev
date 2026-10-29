# 도구 사전 (자동 — `Docs/tools/anal_record_index.py`)

설명 = 파일 첫 설명 줄(docstring · 주석). 언급 = SUMMARY 에서 파일 이름이 나온 날짜 · §. 옛 번호 이름(job4xx)은 Docs/tools/README.md 의 대응표도 함께 본다.

## 상시 도구 Docs/tools/ (37)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_bag_rates.py`](../../tools/anal_bag_rates.py) | anal_bag_rates — bag 여러 개의 토픽별 '기록기가 받은' 메시지 수·주기·크기를 나란히 비교한다. (2026-10-13) | 10-13 §3 |
| [`anal_box_history.py`](../../tools/anal_box_history.py) | anal_box_history — 로버가 장애물 옆에서 멈췄을 때, 그 장애물 칸이 코스트맵에 '언제부터' 있었는지와 로버·경로가 '어떻게' 다가갔는지를 시간순으로 낸다. (2026-10-13) | 10-13 §4.6 · 10-13 §5 |
| [`anal_box_layers.py`](../../tools/anal_box_layers.py) | anal_box_layers — 정지 때 차체 옆에 있던 치명 칸(상자 끝)을 '어느 층이 언제' 채웠는지 시간순으로 본다. (2026-10-13) | 10-13 §6 |
| [`anal_box_pass.py`](../../tools/anal_box_pass.py) | anal_box_pass — 여러 주행에서 '같은 구역을 지날 때' 차체와 로컬 코스트맵 치명 칸 사이 여유가 얼마였는지 나란히 본다. (2026-10-13) | 10-13 §10 · 10-13 §12 · 10-13 §12.1 · … +4 |
| [`anal_mppi_sim.py`](../../tools/anal_mppi_sim.py) | anal_mppi_sim — MPPI 오프라인 시뮬(Humble 1.1.20 동작 흉내, bag 의 경로·로컬 코스트맵 재생). Jetson 에서 실행(rosbag2_py). (2026-10-13 고정 이름, 원본 job776) | 10-13 §8 · 10-13 §9 · 10-13 §11 · … +2 |
| [`anal_navlog.py`](../../tools/anal_navlog.py) | 10-12 §3.3: Nav2 로그(PC 로 회수한 사본) 요약 — 종류별 횟수(주행 창), 10 s 칸 히스토그램, 반복 아닌 경고·오류 원문. 인자: nav2.log HH:MM:SS HH:MM:SS [원문 최대 줄] | — |
| [`anal_odom_drift.py`](../../tools/anal_odom_drift.py) | anal_odom_drift — 구간마다 '어느 오도메트리 재료가 SLAM 과 얼마나 어긋났나'를 견준다. (2026-10-13) | 10-13 §14 |
| [`anal_plan_keepout.py`](../../tools/anal_plan_keepout.py) | anal_plan_keepout — 전역 지도에서 '카메라(nvblox)가 본 장애물' 둘레만 통과 금지 띠로 두껍게 했을 때 전역 경로가 어떻게 달라지는지 기록된 bag 으로 본다. (2026-10-14) | 10-14 §1 |
| [`anal_proc_cpu.py`](../../tools/anal_proc_cpu.py) | 10-12 §3.3: 프로세스별 CPU(전 프로세스 틱 기록) 구간 비교. 인자: 이름=proc.log@시작epoch@끝epoch ...  (코어 1 개 = 100) | — |
| [`anal_record_index.py`](../../tools/anal_record_index.py) | anal_record_index — 실험 기록 자동 색인 3 종 (2026-10-29, PC). 기록이 늘면 다시 돌려 덮어쓴다(손으로 고치지 않는다). | — |
| [`anal_recorder_cpu.py`](../../tools/anal_recorder_cpu.py) | anal_recorder_cpu — 주행별 bag 기록기(ros2 bag record)의 CPU 사용을 시간순으로, 다른 주요 프로세스·전체 부하와 함께 본다. (2026-10-13) | 10-13 §3 |
| [`anal_reverse.py`](../../tools/anal_reverse.py) | 10-12 §1.2: 러너 csv 로 목표별 후진·제자리 회전 집계. 후진 거리 = 지령 v < −0.005 인 표본 사이 odom 이동 길이(EKF, 미끄러짐은 못 봄). | — |
| [`anal_rtps_acklag.py`](../../tools/anal_rtps_acklag.py) | anal_rtps_acklag — 한 토픽의 쓰는 쪽이 보낸 HEARTBEAT(가진 표본 번호 범위)와 읽는 쪽들이 보낸 ACKNACK(어디까지 받았나)을 시간순으로 맞춰, | 10-13 §1.2 |
| [`anal_rtps_onset.py`](../../tools/anal_rtps_onset.py) | anal_rtps_onset — 포화가 시작되는 몇 초를 잘게(기본 0.2 s) 나눠, 어느 읽는 쪽이 먼저 뒤처졌는지 본다. (2026-10-13) | 10-13 §1.2 · 10-13 §2.1 |
| [`anal_rtps_pcap.py`](../../tools/anal_rtps_pcap.py) | anal_rtps_pcap — 루프백 캡처(pcap)에서 DDS(RTPS) 패킷을 종류·보낸 쪽·받는 쪽별로 센다. (2026-10-13) | 10-13 §0 · 10-13 §1 · 10-13 §1.2 |
| [`anal_tf_rate.py`](../../tools/anal_tf_rate.py) | 10-12 §3.3: bag 의 /tf 발행량 추이 — 10 s 칸마다 프레임 쌍별 변환 수(Hz)와 /tf 메시지 수. 인자: bag | 10-13 §2.1 |
| [`anal_top.py`](../../tools/anal_top.py) | 10-12 §2: top 기록(2 s 간격)에서 구간별 부하 — load average, 유휴 %, 프로세스별 CPU 평균. 인자: top.log HH:MM:SS HH:MM:SS [..구간 더] | — |
| [`anal_traj_size.py`](../../tools/anal_traj_size.py) | 10-12 §7.3: /trajectories(MPPI 궤적 발행) 메시지의 크기·주기 추이 — 10 s 칸마다 메시지 수, 직렬화 크기(kB), 마커 수. 인자: bag... | — |
| [`anal_udp_drops.py`](../../tools/anal_udp_drops.py) | 10-12 §9.2: UDP 손실 시간순 분석. 인자: net_<이름>.log 포화시작(HH:MM:SS) | 10-13 §1.2 · 10-13 §4.4 |
| [`chk_drive_gate.py`](../../tools/chk_drive_gate.py) | chk_drive_gate — 주행 직전 게이트 B · C · G2 를 한 노드(DDS 참여자 1 개)로 (2026-10-27 §24, Jetson, 로버 안 움직임). | 10-27 §24 · 10-27 §31 |
| [`chk_jetson_state.sh`](../../tools/chk_jetson_state.sh) | 상태 확인(로버 안 움직임): 재부팅 여부·IP·스택·/tmp 스크립트·캡처 도구 권한. 10-13 세션 시작용 | 10-13 §0 |
| [`chk_padding_dynamic.py`](../../tools/chk_padding_dynamic.py) | chk_padding_dynamic — 실행 중에 코스트맵 footprint_padding 을 바꾸면 실제로 반영되는지 본다. 로버는 움직이지 않는다(명령을 내지 않음). (2026-10-14) | 10-14 §7 · 10-14 §7.1 |
| [`chk_prep.py`](../../tools/chk_prep.py) | prep 확인을 한 프로세스(DDS 참여자 1 개)로 (2026-10-12 §13). | 10-15 §1 · 10-15 §1.1 · 10-21 §1 · … +4 |
| [`fig_bag_reception.py`](../../tools/fig_bag_reception.py) | fig_bag_reception — bag 기록기가 토픽별로 '제때 받았는지'를 시간축으로 그린다. (2026-10-13) | 10-13 §3 |
| [`fig_box_approach_video.py`](../../tools/fig_box_approach_video.py) | fig_box_approach_video — 로버가 장애물(상자)에 다가가 멈추기까지를 지도 좌표 영상으로 만든다. (2026-10-13) | 10-13 §4.6 |
| [`fig_drive_video.py`](../../tools/fig_drive_video.py) | fig_drive_video — 주행 한 구간을 영상으로(1920 × 1080). fig_run_video · 10-23 fig_replan_video 의 화면 재설계판 (2026-10-23 §20.5). | 10-23 §20.5 · 10-23 §20.6 · 10-23 §20.7 · … +2 |
| [`fig_patrol_goals.py`](../../tools/fig_patrol_goals.py) | fig_patrol_goals — 순회 코스의 목표 지점을 저장 지도(office_v3) 위에 순서대로 그린다. (2026-10-14) | 10-14 §12 · 10-14 27.2 · 10-14 27.3 |
| [`fig_place_run.py`](../../tools/fig_place_run.py) | fig_place_run — 장소 이름 명령 주행(F2.5 place_server) 한 번을 그림 한 장으로 (2026-10-28 §14, PC). | 10-28 §14.1 · 10-28 §17 |
| [`fig_run_video.py`](../../tools/fig_run_video.py) | fig_run_video — 주행 한 구간을 지도 좌표 영상으로 만든다(특정 장애물 없이 주행 전체를 보는 일반판). (2026-10-14) | 10-14 §10 · 10-14 §13.4 · 10-14 19.3 · … +2 |
| [`fig_rviz_video.py`](../../tools/fig_rviz_video.py) | fig_rviz_video — 주행 구간을 RViz 스타일(어두운 바탕 · 1 m 격자 · costmap 색표 · 초록 경로 · 빨간 라이다 · 차체 외곽 · 좌표축)로 정사각 영상 (2026-10-26 §17). | 10-26 §17 · 10-26 §18.1 · 10-27 §12 · … +3 |
| [`fig_stop_costmap.py`](../../tools/fig_stop_costmap.py) | fig_stop_costmap — 로버가 멈춘 순간의 로컬 코스트맵·차체 풋프린트·라이다 점을 겹쳐 그리고, 풋프린트에 걸린 비용과 실제 여유(라이다)를 수치로 낸다. (2026-10-13) | 10-13 §4.5 · 10-14 §9.2 |
| [`prep_fast.sh`](../../tools/prep_fast.sh) | prep_fast — 순회용 빠른 기동(정리 → 센서 → SLAM 위치 추정 → Nav2 → 준비 확인). 로버 안 움직임. 옛 이름 job972_prep_fast.sh(10-12 §13) | 10-14 §25 · 10-15 §1.1 · 10-20 §6 · … +6 |
| [`prep_patrol.sh`](../../tools/prep_patrol.sh) | prep_patrol — 순회 구성으로 빠른 prep. 로버 안 움직임. 인자: VIZ(lite\|true\|off, 기본 lite) [FWD=15.0] | 10-13 §1 · 10-13 §1.1 · 10-15 §1.1 · … +9 |
| [`README.md`](../../tools/README.md) | Docs/tools — 계속 쓰는 도구 (2026-10-13~) | 08-27 한 일 · 08-28 코드 위치 이전 (사용자 요청) · 10-07 §9 · … +3 |
| [`run_slam_replay.sh`](../../tools/run_slam_replay.sh) | run_slam_replay — 위치 추정 SLAM 을 주행 bag 입력으로 다시 돌려 map→odom stamp 정체를 잰다 (2026-10-27 §26, Jetson, 로버 안 움직임). | 10-27 §26.2 · 10-27 §29 |
| [`slam_replay_feed.py`](../../tools/slam_replay_feed.py) | slam_replay_feed — 주행 bag 의 /scan · /tf(map→odom 뺌) · /tf_static 을 실시간 1 배로 다시 내보내고(/clock 포함), | 10-27 §26.2 |
| [`up_tools.sh`](../../tools/up_tools.sh) | up_tools — Jetson /tmp 로 도구 전송(실행 안 함). 비밀번호는 run_jn.sh 에서 읽는다. 재부팅 뒤 한 번. | 10-14 §7.1 |

## 2026-08-26 (28)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job0.sh`](../../debug_log/2026-08-26/jobs/job0.sh) | Step 0 추가 점검: L4T/JetPack 버전, USB 장치, CH340 인식 여부 | — |
| [`job0b.sh`](../../debug_log/2026-08-26/jobs/job0b.sh) | CH340이 ttyUSB로 안 잡히는 원인 조사: 커널 로그 + brltty 여부 | — |
| [`job0c.sh`](../../debug_log/2026-08-26/jobs/job0c.sh) | udev 규칙: CH340(1a86:7523) -> /dev/rover 심볼릭 링크 고정 | — |
| [`job1.sh`](../../debug_log/2026-08-26/jobs/job1.sh) | Step 1: micro-ros-agent 컨테이너 실행 (심볼릭 링크 resolve 후 전달) | — |
| [`job1b.sh`](../../debug_log/2026-08-26/jobs/job1b.sh) | Step 1 검증: 토픽 목록, 발행 주기, 배터리 전압 | — |
| [`job1c.sh`](../../debug_log/2026-08-26/jobs/job1c.sh) | Step 1 검증(계속): Humble hz는 QoS 플래그 없음 → 플레인 hz 시도, 실패 시 echo 카운트로 측정 | — |
| [`job2a.sh`](../../debug_log/2026-08-26/jobs/job2a.sh) | Step 2 사전 점검: colcon, 필요한 ROS 패키지, 기존 워크스페이스 | — |
| [`job2c.sh`](../../debug_log/2026-08-26/jobs/job2c.sh) | Step 2: 워크스페이스 구성 → colcon 빌드 → base.launch.py 기동 → 검증 | — |
| [`job2d.sh`](../../debug_log/2026-08-26/jobs/job2d.sh) | Step 2 재검증: agent 세션 재수립 확인 + 토픽 주기 | — |
| [`job2e.sh`](../../debug_log/2026-08-26/jobs/job2e.sh) | 리셋 후 재검증: 세션 로그, 토픽, 주기 | — |
| [`job2f.sh`](../../debug_log/2026-08-26/jobs/job2f.sh) | 접지 상태 초저속 주행 테스트 (사용자 승인, 2026-08-26) | — |
| [`job3a.sh`](../../debug_log/2026-08-26/jobs/job3a.sh) | Step 3 사전: robot_localization 설치 확인 (없으면 apt 설치) | — |
| [`job3b.sh`](../../debug_log/2026-08-26/jobs/job3b.sh) | Step 3: EKF 구성 반영 → 빌드 → static TF(imu_link) + ekf_node 기동 → 정적 검증 | — |
| [`job3c.sh`](../../debug_log/2026-08-26/jobs/job3c.sh) | 누락 의존성 설치 후 EKF 재기동·검증 | — |
| [`job3d.sh`](../../debug_log/2026-08-26/jobs/job3d.sh) | EKF 진단: 구독 QoS 정합, 정지 시 자이로 바이어스, 30초 yaw 드리프트 | — |
| [`job3e.sh`](../../debug_log/2026-08-26/jobs/job3e.sh) | 센서 컨디셔너 반영 → 재빌드 → EKF 재기동 → 정적 재검증 (바이어스 제거 확인) | — |
| [`job3g.sh`](../../debug_log/2026-08-26/jobs/job3g.sh) | IMU 실물 여부 판정: 정지 시 중력벡터(≈9.8) + 샘플 간 변동(실센서 노이즈) 확인 | — |
| [`job3h.sh`](../../debug_log/2026-08-26/jobs/job3h.sh) | 진단: 컨디셔너/EKF 중복 실행 여부 + /imu/data 발행자 수 + mag 상태 | — |
| [`job3i.sh`](../../debug_log/2026-08-26/jobs/job3i.sh) | 컨디셔너 10s 캘리브레이션 반영 → EKF 재기동 → 60초 정적 드리프트 정량 측정 | — |
| [`job3j.sh`](../../debug_log/2026-08-26/jobs/job3j.sh) | 휠 단독 EKF 반영 → 재기동 → 정적 검증 (yaw 완전 고정 기대) | — |
| [`job3m.sh`](../../debug_log/2026-08-26/jobs/job3m.sh) | Step 3 주행 검증: 회전·직진 시 /odometry/filtered 발산 없음 확인 | — |
| [`job3n.sh`](../../debug_log/2026-08-26/jobs/job3n.sh) | Step 3 최종 주행 검증 (휠 단독 EKF): 회전·직진 시 filtered가 wheel_odom을 추종하는지 | — |
| [`job3o.sh`](../../debug_log/2026-08-26/jobs/job3o.sh) | 슬립 보정 반영 → 재빌드 → EKF 재기동 → 정적 확인 | — |
| [`job3p.sh`](../../debug_log/2026-08-26/jobs/job3p.sh) | 슬립 보정 검증: 회전 3초 → filtered Δyaw ≈ 실회전(~15°) 확인 (wheel은 ~35° 주장 예상) | — |
| [`job3q.sh`](../../debug_log/2026-08-26/jobs/job3q.sh) | 고속 회전 슬립 테스트: 0.6 rad/s × 3s — 계수 0.43의 속도 의존성 확인 | — |
| [`job3r.sh`](../../debug_log/2026-08-26/jobs/job3r.sh) | 자이로 생사 판정 녹화: 90초간 gyro z 50Hz 연속 기록 (사용자가 손으로 로버 회전) | — |
| [`job3r2.sh`](../../debug_log/2026-08-26/jobs/job3r2.sh) | 자이로 판정 재녹화: 180초간 gyro z 50Hz 연속 기록 (사용자 손 회전 대기) | — |
| [`job3s.sh`](../../debug_log/2026-08-26/jobs/job3s.sh) | 손 회전 녹화 분석: gyro z 통계 + 파형 요약 | — |

## 2026-08-27 (31)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job4a.sh`](../../debug_log/2026-08-27/jobs/job4a.sh) | Step 4 사전: 필요 패키지 apt 가용성 + 현재 USB 장치 | — |
| [`job4b.sh`](../../debug_log/2026-08-27/jobs/job4b.sh) | D455 camera_link 오프셋 (Intel realsense2_description xacro) | — |
| [`job4c.sh`](../../debug_log/2026-08-27/jobs/job4c.sh) |  | — |
| [`job4d.sh`](../../debug_log/2026-08-27/jobs/job4d.sh) | 현재 Jetson의 RealSense 준비 상태 진단 (JETSON_REALSENSE_INSTALL.md 게이트 기준) | — |
| [`job4e.sh`](../../debug_log/2026-08-27/jobs/job4e.sh) | Step 4 준비 (저리스크): rplidar_ros 설치, RealSense 패키지 업그레이드, udev 규칙 2종 | — |
| [`job4f.sh`](../../debug_log/2026-08-27/jobs/job4f.sh) | JetsonHacks 저장소 2종 클론 + 빌드 스크립트 원문 확인 | — |
| [`job4g.sh`](../../debug_log/2026-08-27/jobs/job4g.sh) | RealSense IMU용 HID 센서 커널 모듈 소스 빌드 (root로 실행, 백그라운드, 로그 /tmp/hid_build.log) | — |
| [`job4g_diag.sh`](../../debug_log/2026-08-27/jobs/job4g_diag.sh) |  | — |
| [`job4g_launch.sh`](../../debug_log/2026-08-27/jobs/job4g_launch.sh) |  | — |
| [`job4h.sh`](../../debug_log/2026-08-27/jobs/job4h.sh) | ws 배포: rover_description(xacro+mesh+launch) + rover_bringup(lidar/camera/slam/foxglove launch, slam.yaml) → colcon → xacro 검증 | — |
| [`job4i.sh`](../../debug_log/2026-08-27/jobs/job4i.sh) | 재부팅 후 복구·검증: HID 모듈 로드 확인 → bringup(base+ekf+static TF) 복구 | — |
| [`job4j.sh`](../../debug_log/2026-08-27/jobs/job4j.sh) | 빌드된 HID 모듈·패치 uvcvideo 라이브 로드 검증 (재부팅 없이) | — |
| [`job4k.sh`](../../debug_log/2026-08-27/jobs/job4k.sh) | (1) 패치 uvcvideo 교체 + USB 재열거 → HID 재바인딩·iio 확인 (2) RealSense 게이트 (3) bringup 복구 | — |
| [`job4l.sh`](../../debug_log/2026-08-27/jobs/job4l.sh) | IMU 정밀 검증(accel/gyro 모두, iio 권한, 15s hz) + LiDAR 게이트 + 로버 토픽 확인 | — |
| [`job4m.sh`](../../debug_log/2026-08-27/jobs/job4m.sh) | D455f 자이로 → EKF 복원 배포·검증 | — |
| [`job4n.sh`](../../debug_log/2026-08-27/jobs/job4n.sh) | job4m 검증부 재실행 (텍스트 안전) | — |
| [`job4o.sh`](../../debug_log/2026-08-27/jobs/job4o.sh) | EKF가 /imu/data 를 실제로 융합하는지 진단: 타임스탬프 정합, 구독 QoS, 값 분포 | — |
| [`job4p.sh`](../../debug_log/2026-08-27/jobs/job4p.sh) | 토픽별 수신 지연(now - header.stamp) 측정 — EKF 무음 폐기(old measurement) 가설 검증 | — |
| [`job4q.sh`](../../debug_log/2026-08-27/jobs/job4q.sh) | EKF debug 모드 15s: imu0 측정이 처리되는지 / TF 변환 실패 여부 직접 확인 | — |
| [`job4r.sh`](../../debug_log/2026-08-27/jobs/job4r.sh) | imu0_config 축 수정 배포 → EKF 재시작 → filtered vyaw에 자이로 반영 확인 + 30s 정적 드리프트 | — |
| [`job4s.sh`](../../debug_log/2026-08-27/jobs/job4s.sh) |  | — |
| [`job4t.sh`](../../debug_log/2026-08-27/jobs/job4t.sh) | 손 회전 동적 검증 녹화 150s: 광학 y(=로봇 yaw축) 자이로 + EKF yaw 각속도 | — |
| [`job4u.sh`](../../debug_log/2026-08-27/jobs/job4u.sh) | 손 회전 녹화 분석: D455f 자이로(광학 y) vs EKF vyaw | — |
| [`job4v.sh`](../../debug_log/2026-08-27/jobs/job4v.sh) | USB 대역폭 테스트: 토폴로지 + (A) 카메라 풀스트림+LiDAR 동시 vs (B) 카메라 단독 비교 | — |
| [`job4w.sh`](../../debug_log/2026-08-27/jobs/job4w.sh) | 동시 부하 재측정: LiDAR 발행 확인 후 scan/depth/color/imu/odom 5개 동시 15s (window 100) | — |
| [`job4x.sh`](../../debug_log/2026-08-27/jobs/job4x.sh) | 센서 통합 launch로 전환 + slam_toolbox 스모크 테스트 + foxglove | — |
| [`job4y.sh`](../../debug_log/2026-08-27/jobs/job4y.sh) | LiDAR yaw 정렬 측정: 로버 정면(카메라 방향) 0.3m에 손/책을 5초간 두고 실행 → lidar_yaw 산출 | — |
| [`job4z.sh`](../../debug_log/2026-08-27/jobs/job4z.sh) | 회전 슬립 계수 정밀 캘리브레이션 (자이로 기준). 인자: 각속도 지령(기본 0.3), 지속 초(기본 4) | — |
| [`job5a.sh`](../../debug_log/2026-08-27/jobs/job5a.sh) | W3: 확정 URDF 반영 → colcon → base.launch 재시작(agent 포함) → sensors.launch 재시작(컨디셔너 1.0) | — |
| [`job5b.sh`](../../debug_log/2026-08-27/jobs/job5b.sh) | W4 슬립 재캘리브레이션 (자이로 기준, WT-600 게이지 0.245 반영 펌웨어). 접지 상태·사용자 입회. | — |
| [`job5c.sh`](../../debug_log/2026-08-27/jobs/job5c.sh) | 슬립 계수 0.46 배포 → 컨디셔너/EKF 재시작 → 정적 확인 + conditioned vs gyro 정합 스팟체크 | — |

## 2026-08-28 (31)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job6a.sh`](../../debug_log/2026-08-28/jobs/job6a.sh) | 스택 상태 확인 + LiDAR yaw 정렬 사전 점검(현재 스캔 섹터별 거리 스냅샷) | — |
| [`job6b.sh`](../../debug_log/2026-08-28/jobs/job6b.sh) | 재부팅 여부 확인 + 스택 전체 재시작 (base → sensors), 세션 검증 | — |
| [`job6c.sh`](../../debug_log/2026-08-28/jobs/job6c.sh) | LiDAR yaw 정렬 v2: 개별 최근접 빔 각도 + 근거리(<0.8m) 세밀(10deg) 히스토그램 | — |
| [`job6d.sh`](../../debug_log/2026-08-28/jobs/job6d.sh) | 종이 흔들기 추적: 15초간 근거리(<0.7m) 변동이 큰 섹터를 검출 → 종이 방향(lidar 프레임) 판정 | — |
| [`job6e.sh`](../../debug_log/2026-08-28/jobs/job6e.sh) | lidar_yaw=π 반영 → RSP 재빌드·재시작 → TF 확인 | — |
| [`job6f.sh`](../../debug_log/2026-08-28/jobs/job6f.sh) | 검증: 종이를 base_link 프레임에서 추적 (LaserScan→base_link 변환). 정면이면 0deg, 좌 +90, 우 -90. | — |
| [`job6g.sh`](../../debug_log/2026-08-28/jobs/job6g.sh) | 정밀 검증: base_link 프레임에서 (a)정지 기준선 3s → (b)흔들기 15s. 차이(변동)가 큰 상위 구간 + 최대변동 빔 각도 | — |
| [`job6h.sh`](../../debug_log/2026-08-28/jobs/job6h.sh) | 벽 마주보기 검증: 정지 스캔, base_link 프레임 최근접 방향 = 벽 = 정면이어야 함 | — |
| [`job6i.sh`](../../debug_log/2026-08-28/jobs/job6i.sh) | 원시 lidar 각도(θ_lidar, TF 무관) 분석 — 코너(정면+좌측 벽) ground truth와 대조해 회전 vs 반전 판정 | — |
| [`job6j.sh`](../../debug_log/2026-08-28/jobs/job6j.sh) |  | — |
| [`job6k.sh`](../../debug_log/2026-08-28/jobs/job6k.sh) | 트인 공간 + 정면 단일 물체: 유일 최근접 반사의 원시 θ_lidar = 로버 정면 하드웨어 각도 | — |
| [`job6l.sh`](../../debug_log/2026-08-28/jobs/job6l.sh) | 현재 실제 상태 사실확인: 배포 URDF yaw, RSP 노드 수, TF, robot_description 파라미터 | — |
| [`job6m.sh`](../../debug_log/2026-08-28/jobs/job6m.sh) | yaw=π 재적용 + 전체 스택 완전 재시작(base+sensors+foxglove) — stale TF 제거 | — |
| [`job6n.sh`](../../debug_log/2026-08-28/jobs/job6n.sh) | 왼손/오른손 판정: 좌측벽(~325mm)·정면벽(~800mm)의 순수 원시 각도(θ_msg) 측정 → 방향성 판정 | — |
| [`job6o.sh`](../../debug_log/2026-08-28/jobs/job6o.sh) | 현재 배포 TF(yaw=π)로 스캔을 base_link 프레임 변환 → 정면벽(800mm) base~0°, 좌측벽(325mm) base~+90° 확인 | — |
| [`job7a.sh`](../../debug_log/2026-08-28/jobs/job7a.sh) | SLAM 준비: slam_toolbox 기동 확인/시작 → /map·map→odom TF·현재 pose | — |
| [`job7b.sh`](../../debug_log/2026-08-28/jobs/job7b.sh) | 보드 세션 진단: agent 상태, wheel_odom 실측, battery, heartbeat | — |
| [`job7c.sh`](../../debug_log/2026-08-28/jobs/job7c.sh) | SLAM 맵핑용 제자리 360° 회전 + 실시간 충돌 가드. 접지·사방 확보 상태, 사용자 입회. | — |
| [`job7d.sh`](../../debug_log/2026-08-28/jobs/job7d.sh) | 제자리 360° 회전 + 풋프린트 인식 충돌 가드(로버 외곽 0.50×0.33 vs 벽 실거리). 접지·사용자 입회. | — |
| [`job7d1.sh`](../../debug_log/2026-08-28/jobs/job7d1.sh) | 세션 확인 + slam_toolbox 재시작(깨끗한 맵) | — |
| [`job7e.sh`](../../debug_log/2026-08-28/jobs/job7e.sh) | 리셋 후 세션 확인 + slam 재시작(깨끗한 맵) + 회전 전 시작 여유(풋프린트 실거리) 측정 | — |
| [`job7f.sh`](../../debug_log/2026-08-28/jobs/job7f.sh) | 제자리 360° 회전 + 풋프린트 인식 충돌 가드(로버 외곽 0.50×0.33 vs 벽 실거리). 접지·사용자 입회. | — |
| [`job7g.sh`](../../debug_log/2026-08-28/jobs/job7g.sh) | 재부팅 vs WiFi 단절 판별 + 스택/세션 생존 확인 | — |
| [`job7h.sh`](../../debug_log/2026-08-28/jobs/job7h.sh) | 안전: 잔존 회전 프로세스 정리 + 정지 지령 + 현재 회전율 확인 | — |
| [`job7i_launch.sh`](../../debug_log/2026-08-28/jobs/job7i_launch.sh) | 회전을 detach 실행: WiFi 끊겨도 Jetson에서 독립 완주. 스크립트 자체 안전장치(가드/360°/타임아웃). | — |
| [`job7j.sh`](../../debug_log/2026-08-28/jobs/job7j.sh) | 회전 로그 확인 + 프로세스 생존 여부 + 현재 상태 | — |
| [`job7k.sh`](../../debug_log/2026-08-28/jobs/job7k.sh) | 견고한 detach 회전 코어 — 로그에 진행상황 실시간 flush 기록. WiFi 무관하게 완주. | — |
| [`job7k_launch.sh`](../../debug_log/2026-08-28/jobs/job7k_launch.sh) | 견고한 detach 실행 + 즉시 초기 확인 | — |
| [`job7l.sh`](../../debug_log/2026-08-28/jobs/job7l.sh) | 맵 저장 + 통계 + PNG 렌더 + 현재 pose(360° 후 시작 부근 복귀 확인) | — |
| [`job8a.sh`](../../debug_log/2026-08-28/jobs/job8a.sh) | 스캔/오도 타이밍 정합 정적 분석 (주행 불필요) — "포인트 끌림" 원인 특정 | — |
| [`job8b.sh`](../../debug_log/2026-08-28/jobs/job8b.sh) | 재스탬프+slam튜닝 배포 → lidar/slam 재시작 → 스캔 지연 재측정(개선 확인) | — |

## 2026-08-31 (70)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job10a.sh`](../../debug_log/2026-08-31/jobs/job10a.sh) |  | — |
| [`job10b.sh`](../../debug_log/2026-08-31/jobs/job10b.sh) |  | — |
| [`job10c.sh`](../../debug_log/2026-08-31/jobs/job10c.sh) | 깨끗한 odom: EKF 재시작(odom→0, 자이로 캘리브 10s, 로버 정지 유지) → slam 재시작 | — |
| [`job10d.sh`](../../debug_log/2026-08-31/jobs/job10d.sh) |  | — |
| [`job10e.sh`](../../debug_log/2026-08-31/jobs/job10e.sh) |  | — |
| [`job10stop.sh`](../../debug_log/2026-08-31/jobs/job10stop.sh) |  | — |
| [`job11.sh`](../../debug_log/2026-08-31/jobs/job11.sh) | teleop 정지 + 맵 저장 + 통계/PNG + 주행 궤적 정보 | — |
| [`job14a.sh`](../../debug_log/2026-08-31/jobs/job14a.sh) | 스택 재시작: base(agent+RSP) + sensors(camera+lidar+ekf+foxglove). agent 재시작 → 보드 RESET 필요. | — |
| [`job14b_straight.sh`](../../debug_log/2026-08-31/jobs/job14b_straight.sh) | 직진 캘리브레이션: 각속도 0으로 전진, 오도 유클리드 거리 TARGET 도달 시 정지. 풋프린트 가드. | — |
| [`job14c_square.sh`](../../debug_log/2026-08-31/jobs/job14c_square.sh) | 사각형 루프 드리프트 정량화 (좁은공간). 인자: 변길이(기본0.35), 회전방향(기본 L=CCW) | — |
| [`job14d_square.sh`](../../debug_log/2026-08-31/jobs/job14d_square.sh) | 사각형 루프 드리프트 정량화 v2: 방향별 여유 출력 + 시작가드 제거 + 가드임계 인자화. | — |
| [`job14e_framecheck.sh`](../../debug_log/2026-08-31/jobs/job14e_framecheck.sh) | 라이다 프레임 결정: /scan_raw 원시각도로 가까운 장애물 위치 → yaw=0/π 매핑 대조. | — |
| [`job14g_health.sh`](../../debug_log/2026-08-31/jobs/job14g_health.sh) | 무동작 헬스체크: 노드·토픽 라이브 + 배터리 + 새 위치 사방여유(회전공간 확인). | — |
| [`job14h_square_gt.sh`](../../debug_log/2026-08-31/jobs/job14h_square_gt.sh) | 사각형 루프 + 벽기반 지면검증(ground truth). 인자: 변(0.40) 방향(L) 가드(0.03) | — |
| [`job14i_slamstart.sh`](../../debug_log/2026-08-31/jobs/job14i_slamstart.sh) | SLAM 기동·검증 (무동작). map->odom TF + /map 확인. | — |
| [`job14j_slamdrift.sh`](../../debug_log/2026-08-31/jobs/job14j_slamdrift.sh) | SLAM 지면검증 드리프트: 사각형 주행 중 map->odom 변화 추적 = slam이 보정한 드리프트. | — |
| [`job14k_slamdrift2.sh`](../../debug_log/2026-08-31/jobs/job14k_slamdrift2.sh) | SLAM 지면검증 드리프트 v2: 시작 여유 게이트 추가(사용자 근처면 중단). | — |
| [`job15a_apply.sh`](../../debug_log/2026-08-31/jobs/job15a_apply.sh) | conditioner vx보정 반영: 소스갱신 → 재빌드 → EKF+SLAM 새로 재시작. 로버 정지 유지! | — |
| [`job15b_joy.sh`](../../debug_log/2026-08-31/jobs/job15b_joy.sh) | 조이스틱 teleop 기동 + 검증. 모션은 스틱 움직일 때만 발생. | — |
| [`job15c_shutdown.sh`](../../debug_log/2026-08-31/jobs/job15c_shutdown.sh) | 안전 종료: 모터 정지 → Jetson 노드/agent 종료. (펌웨어/보드 무관) | — |
| [`job16a_init.sh`](../../debug_log/2026-08-31/jobs/job16a_init.sh) | 세션 초기화: base(agent+rsp)+sensors(camera+lidar+ekf+foxglove)+slam. 보드 RESET됨. 로버 정지! | — |
| [`job16b_tfdiag.sh`](../../debug_log/2026-08-31/jobs/job16b_tfdiag.sh) | 검증(자이로/scan/imu) + TF 진단(odom->base, map->odom 브로드캐스트율) + 조이스틱 기동. | — |
| [`job16c_tfmon.sh`](../../debug_log/2026-08-31/jobs/job16c_tfmon.sh) |  | — |
| [`job16d_tsverify.sh`](../../debug_log/2026-08-31/jobs/job16d_tsverify.sh) |  | — |
| [`job16e_stamps.sh`](../../debug_log/2026-08-31/jobs/job16e_stamps.sh) |  | — |
| [`job16f_latency.sh`](../../debug_log/2026-08-31/jobs/job16f_latency.sh) |  | — |
| [`job16g_tfcadence.sh`](../../debug_log/2026-08-31/jobs/job16g_tfcadence.sh) | odom->base 와 map->odom 값 변화 주기 측정 (20초, 회전 중). /odometry/filtered 토픽도 병행. | — |
| [`job16h_rotlog.sh`](../../debug_log/2026-08-31/jobs/job16h_rotlog.sh) | 스크립트가 직접 제자리 회전(0.6rad/s, 15s) + 동시 TF주기 로깅. 넓은공간·가드. | — |
| [`job16i_slamdiag.sh`](../../debug_log/2026-08-31/jobs/job16i_slamdiag.sh) |  | — |
| [`job16j_cpu.sh`](../../debug_log/2026-08-31/jobs/job16j_cpu.sh) |  | — |
| [`job16k_fgtest.sh`](../../debug_log/2026-08-31/jobs/job16k_fgtest.sh) | foxglove 끄고 CPU 확보 후, 스크립트 회전 중 map->odom 갱신되는지 확인. | — |
| [`job16l_fgrestart.sh`](../../debug_log/2026-08-31/jobs/job16l_fgrestart.sh) |  | — |
| [`job16m_joy.sh`](../../debug_log/2026-08-31/jobs/job16m_joy.sh) |  | — |
| [`job17a_camcheck.sh`](../../debug_log/2026-08-31/jobs/job17a_camcheck.sh) |  | — |
| [`job17b_optapply.sh`](../../debug_log/2026-08-31/jobs/job17b_optapply.sh) |  | — |
| [`job17c_validate.sh`](../../debug_log/2026-08-31/jobs/job17c_validate.sh) |  | — |
| [`job17d_clean.sh`](../../debug_log/2026-08-31/jobs/job17d_clean.sh) |  | — |
| [`job17e_identify.sh`](../../debug_log/2026-08-31/jobs/job17e_identify.sh) |  | — |
| [`job18a_precheck.sh`](../../debug_log/2026-08-31/jobs/job18a_precheck.sh) | 무동작 사전점검: joy 정리 + 전압 + 방향별 여유 + 노드/TF 상태 | — |
| [`job18b_restart.sh`](../../debug_log/2026-08-31/jobs/job18b_restart.sh) | sensors+slam 깨끗이 재시작 (base/agent 유지 → 보드 RESET 불필요). 로버 정지 유지! | — |
| [`job18c_vxverify.sh`](../../debug_log/2026-08-31/jobs/job18c_vxverify.sh) | vx×1.022 검증: 최대속도 직진, odom vs slam(지면검증) 이동거리 비율. | — |
| [`job18d_slamhealth.sh`](../../debug_log/2026-08-31/jobs/job18d_slamhealth.sh) |  | — |
| [`job18f_drive.sh`](../../debug_log/2026-08-31/jobs/job18f_drive.sh) | 직진 스케일 재검증: 방향 인자 F(전진)/B(후진). 최대속도 0.10. odom·slam·raw휠 모두 기록. | — |
| [`job18g_speed.sh`](../../debug_log/2026-08-31/jobs/job18g_speed.sh) | 직진 스케일 vs 속도: 인자 방향(F/B) 속도(m/s). odom·slam·휠원시 기록. | — |
| [`job19a_apply783.sh`](../../debug_log/2026-08-31/jobs/job19a_apply783.sh) | VX_SCALE 0.783 반영: 재빌드 → conditioner/EKF/slam 재시작 → 검증. 로버 정지! | — |
| [`job20a_boot.sh`](../../debug_log/2026-08-31/jobs/job20a_boot.sh) | 부팅 후 full 스택 기동: base(agent+RSP) → sensors(camera/lidar/ekf/foxglove) → slam. 로버 정지! | 09-03 내일 할 일 (순서) · 09-09 1 · 09-09 내가 만든 오염 (기록 보존) |
| [`job8c.sh`](../../debug_log/2026-08-31/jobs/job8c.sh) | 수정 배포 상태 + 배터리 확인 (회전 테스트 가능 여부) | — |
| [`job8d.sh`](../../debug_log/2026-08-31/jobs/job8d.sh) | 재부팅 후 전체 스택 재시작: base(agent+RSP) + sensors(lidar+scan_restamp+camera+ekf+foxglove) + slam | — |
| [`job8e.sh`](../../debug_log/2026-08-31/jobs/job8e.sh) |  | — |
| [`job8f.sh`](../../debug_log/2026-08-31/jobs/job8f.sh) |  | — |
| [`job8f_launch.sh`](../../debug_log/2026-08-31/jobs/job8f_launch.sh) |  | — |
| [`job8g.sh`](../../debug_log/2026-08-31/jobs/job8g.sh) | 회전 완료 대기 후 로그 읽기 | — |
| [`job8h.sh`](../../debug_log/2026-08-31/jobs/job8h.sh) | scan_deskew 배포 → lidar 재시작 → 정지 시 무결성(스캔 왜곡 없음) 확인 | — |
| [`job8i.sh`](../../debug_log/2026-08-31/jobs/job8i.sh) | 중복 정리 → 단일 lidar 파이프라인 재시작 → 정지 무결성 재확인 | — |
| [`job8j.sh`](../../debug_log/2026-08-31/jobs/job8j.sh) |  | — |
| [`job8k.sh`](../../debug_log/2026-08-31/jobs/job8k.sh) |  | — |
| [`job9b.sh`](../../debug_log/2026-08-31/jobs/job9b.sh) | 조이스틱 장치 인식 + joy_node 패키지 확인 | — |
| [`job9c.sh`](../../debug_log/2026-08-31/jobs/job9c.sh) | joy_node 기동 + /joy 12초 캡처 (사용자가 스틱·버튼 조작) → 축/버튼 활동 확인 | — |
| [`job9e.sh`](../../debug_log/2026-08-31/jobs/job9e.sh) | joy_linux 설치 + joy_linux_node로 /dev/input/js0 읽기 → /joy 12초 캡처 | — |
| [`job9i.sh`](../../debug_log/2026-08-31/jobs/job9i.sh) |  | — |
| [`job9j.sh`](../../debug_log/2026-08-31/jobs/job9j.sh) |  | — |
| [`job9k.sh`](../../debug_log/2026-08-31/jobs/job9k.sh) |  | — |
| [`job9m.sh`](../../debug_log/2026-08-31/jobs/job9m.sh) |  | — |
| [`job9n.sh`](../../debug_log/2026-08-31/jobs/job9n.sh) |  | — |
| [`job9o.sh`](../../debug_log/2026-08-31/jobs/job9o.sh) |  | — |
| [`job9p.sh`](../../debug_log/2026-08-31/jobs/job9p.sh) |  | — |
| [`job9q.sh`](../../debug_log/2026-08-31/jobs/job9q.sh) |  | — |
| [`job9r_drive.sh`](../../debug_log/2026-08-31/jobs/job9r_drive.sh) | 조이스틱 주행 v4: "중립 안정 대기"(스틱 움직이다 놓으면 자동 감지) → teleop → cmd_vel 게이트 | — |
| [`job9s.sh`](../../debug_log/2026-08-31/jobs/job9s.sh) | deadzone 0.25 재배포 → 단일 인스턴스 → 중립 cmd_vel=0 검증(/cmd_vel_test, 보드 무영향) | — |
| [`job9stop.sh`](../../debug_log/2026-08-31/jobs/job9stop.sh) | 안전 정지: 모든 teleop/joy 종료 → /cmd_vel 중단 → watchdog 정지. 원인 진단. | — |

## 2026-09-02 (18)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job20a_boot.sh`](../../debug_log/2026-09-02/jobs/job20a_boot.sh) | 부팅 후 full 스택 기동: base(agent+RSP) → sensors(camera/lidar/ekf/foxglove) → slam. 로버 정지! | 09-03 내일 할 일 (순서) · 09-09 1 · 09-09 내가 만든 오염 (기록 보존) |
| [`job20c_pathdrive.sh`](../../debug_log/2026-09-02/jobs/job20c_pathdrive.sh) | 직진 검증 v2 — 경로방향 가드(로버 폭 밴드 내 진행방향 장애물만) + 전역 비상정지(3cm). | 09-02 개선: 주행 가드를 경로방향 방식으로 변경 |
| [`job21a_reset.sh`](../../debug_log/2026-09-02/jobs/job21a_reset.sh) | 세션 초기화(손 이동 후): EKF+slam 재시작(base/agent 유지) + 회전공간 판정. 로버 정지! | — |
| [`job21c_where.sh`](../../debug_log/2026-09-02/jobs/job21c_where.sh) | 회전 방해물 방위 진단 (무동작): 30도 섹터별 중심기준 최소거리 | — |
| [`job21d_loop.sh`](../../debug_log/2026-09-02/jobs/job21d_loop.sh) | 회전 포함 드리프트 재측정 (올바른 스케일 0.783 적용 후). | — |
| [`job21d_loop_v2.sh`](../../debug_log/2026-09-02/jobs/job21d_loop_v2.sh) | 회전 포함 드리프트 재측정 (올바른 스케일 0.783 적용 후). | — |
| [`job22b_asym.sh`](../../debug_log/2026-09-02/jobs/job22b_asym.sh) | 좌/우 트랙 비대칭 정량화: 순수 직진(angular=0) 지령 시 실제 휨 측정. | — |
| [`job23b_turnstraight.sh`](../../debug_log/2026-09-02/jobs/job23b_turnstraight.sh) | 관측조건 재현: "90도 회전 → 직진"을 N회 반복, 회전 직후 직진 구간의 휨 측정. | — |
| [`job24a_nav2up.sh`](../../debug_log/2026-09-02/jobs/job24a_nav2up.sh) | Nav2 기동 + 검증 (주행 없음) | — |
| [`job24b_goal.sh`](../../debug_log/2026-09-02/jobs/job24b_goal.sh) | Nav2 첫 자율주행: 현재 위치 기준 정면 D미터 목표 전송 + 모니터링 | — |
| [`job25a_fullreset.sh`](../../debug_log/2026-09-02/jobs/job25a_fullreset.sh) | 손 이동 후 전체 재초기화: Nav2 종료 → EKF → slam → Nav2 순. base/agent 유지. | — |
| [`job25b_goaldir.sh`](../../debug_log/2026-09-02/jobs/job25b_goaldir.sh) | Nav2 방향 지정 목표: 현재 heading 기준 ANG도 방향으로 D미터, 목표자세=진행방향 | — |
| [`job25e_nav2start.sh`](../../debug_log/2026-09-02/jobs/job25e_nav2start.sh) |  | 09-03 내일 할 일 (순서) · 09-08 부수 수정 |
| [`job25g_diag2.sh`](../../debug_log/2026-09-02/jobs/job25g_diag2.sh) |  | — |
| [`job26a_goalmon.sh`](../../debug_log/2026-09-02/jobs/job26a_goalmon.sh) | 목표 전송 + cmd_vel 체인 모니터 (controller→/cmd_vel_nav→smoother→/cmd_vel) | — |
| [`job27b_profile.sh`](../../debug_log/2026-09-02/jobs/job27b_profile.sh) |  | — |
| [`job30_goalabs.sh`](../../debug_log/2026-09-02/jobs/job30_goalabs.sh) | 절대좌표(map) 목표: x y yaw_deg timeout | 09-03 내일 할 일 (순서) |
| [`job31_shutdown.sh`](../../debug_log/2026-09-02/jobs/job31_shutdown.sh) | 안전 종료: 모터 정지 → Jetson 노드 → agent. (펌웨어/보드 무관) | — |

## 2026-09-03 (13)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`chk_board.sh`](../../debug_log/2026-09-03/jobs/chk_board.sh) |  | — |
| [`cycle.sh`](../../debug_log/2026-09-03/jobs/cycle.sh) | 펌웨어 MIN 값 변경 → 빌드 → 플래시 → ST-Link 리셋 → EKF 재시작 → 데드밴드 측정 | — |
| [`job32b_deadband.sh`](../../debug_log/2026-09-03/jobs/job32b_deadband.sh) | 데드밴드 보상 검증: 미세 각속도 지령에 실제 회전하는지 (자이로 측정). | — |
| [`job32c_reagent.sh`](../../debug_log/2026-09-03/jobs/job32c_reagent.sh) | 보드 재부팅(플래시) 후 agent 재연결 + 데드밴드 재측정 | — |
| [`job32d_ekfrestart.sh`](../../debug_log/2026-09-03/jobs/job32d_ekfrestart.sh) |  | — |
| [`job33a_reset_noagent.sh`](../../debug_log/2026-09-03/jobs/job33a_reset_noagent.sh) | 손 이동 후 초기화 — agent 는 절대 건드리지 않음(디버거 없어 RESET 불가) | 09-03 내일 할 일 (순서) |
| [`job34c_verify.sh`](../../debug_log/2026-09-03/jobs/job34c_verify.sh) |  | — |
| [`job34e_stuckdiag.sh`](../../debug_log/2026-09-03/jobs/job34e_stuckdiag.sh) |  | — |
| [`job35a_prep.sh`](../../debug_log/2026-09-03/jobs/job35a_prep.sh) |  | — |
| [`stage_microros.sh`](../../debug_log/2026-09-03/jobs/stage_microros.sh) |  | — |
| [`wifi_diag.sh`](../../debug_log/2026-09-03/jobs/wifi_diag.sh) | Jetson Wi-Fi 끊김 진단 (읽기 전용) | — |
| [`wifi_diag2.sh`](../../debug_log/2026-09-03/jobs/wifi_diag2.sh) |  | — |
| [`wifi_fix.sh`](../../debug_log/2026-09-03/jobs/wifi_fix.sh) | Jetson: Wi-Fi power save OFF (런타임 + NM 영구), 근거: 절약모드 ON + NM 끊김 로그 없음 + 간헐 무응답 | — |

## 2026-09-07 (9)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job40a_stalltest.py`](../../debug_log/2026-09-07/jobs/job40a_stalltest.py) | 스톨 정책 검증 (받침대): /cmd_vel 을 20Hz 로 DUR 초 발행하며 /rover/status 전이·휠별 텔레메트리·휠 속도를 기록. | 09-07 받침대 스톨 검증 (`jobs/job40a_stalltest.py`, 결 · 09-07 다음 세션 할 일 (순서) |
| [`job43_mon.py`](../../debug_log/2026-09-07/jobs/job43_mon.py) | 텔레메트리 모니터 (구독 전용 — /cmd_vel 을 발행하지 않음). | — |
| [`job44_deadband.py`](../../debug_log/2026-09-07/jobs/job44_deadband.py) | 바닥 데드밴드 스윕 (2026-09-07, PWM 20kHz 이후 재실측). | — |
| [`job45_tape.py`](../../debug_log/2026-09-07/jobs/job45_tape.py) | 직진 스케일 캘리브레이션 (2026-09-07, PWM 20kHz 이후 VX_SCALE 재측정). | — |
| [`job46_rot.py`](../../debug_log/2026-09-07/jobs/job46_rot.py) | 제자리 회전 캘리브레이션 — 라이다 스캔 정합을 GT 로 사용 (2026-09-07). | — |
| [`job53_bench.py`](../../debug_log/2026-09-07/jobs/job53_bench.py) | Nav2 컨트롤러 벤치마크 (2026-09-07, 스케일 교정 후 재측정). | — |
| [`rover_cli.ps1`](../../debug_log/2026-09-07/jobs/rover_cli.ps1) |  | 09-07 UART5 디버그 콘솔 — 현재 배선에서 동작하지 않음 (신규 확인) |
| [`run_sig.sh`](../../debug_log/2026-09-07/jobs/run_sig.sh) | 사용: run_sig.sh <출력이름> <DUR> <VX> | — |
| [`stuck_monitor.py`](../../debug_log/2026-09-07/jobs/stuck_monitor.py) | stuck_monitor — rover-level 정체/접촉 감시 (2026-09-07). | 09-07 구현 (1·2번) · 09-18 9.3 · 09-29 §13 · … +1 |

## 2026-09-08 (42)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job25e_nav2start.sh`](../../debug_log/2026-09-08/jobs/job25e_nav2start.sh) |  | 09-03 내일 할 일 (순서) · 09-08 부수 수정 |
| [`job56_osc.py`](../../debug_log/2026-09-08/jobs/job56_osc.py) | RPP 조향 진동 측정 (2026-09-08, 계획 §5.y). job53_bench 와 같은 목표 주행 + 20 Hz 트레이스. | 09-08 RPP 조향 진동 측정·튜닝 `job58` (계획 §5.y) — 20 H · 09-08 다음 세션 절차 (충전 후) |
| [`job59_sensors_restart.sh`](../../debug_log/2026-09-08/jobs/job59_sensors_restart.sh) | Jetson 측: 센서(camera/lidar/foxglove/EKF)+slam 재시작, agent 유지. 로버 정지 필수(자이로 캘리브 10s). | 09-08 부수 수정 |
| [`job59b_depthchk.sh`](../../debug_log/2026-09-08/jobs/job59b_depthchk.sh) |  | — |
| [`job59c_navchk.sh`](../../debug_log/2026-09-08/jobs/job59c_navchk.sh) |  | — |
| [`job59d_smfix.sh`](../../debug_log/2026-09-08/jobs/job59d_smfix.sh) | stale stuck_monitor 정리(최신 1개만 유지) + 현재 CPU 측정(top 기준) | — |
| [`job59e_cpu.sh`](../../debug_log/2026-09-08/jobs/job59e_cpu.sh) |  | — |
| [`job59f_depthcmp.py`](../../debug_log/2026-09-08/jobs/job59f_depthcmp.py) | depth 가상스캔 vs 라이다 각도별 비교 (로버 기준각). 카메라는 라이다보다 x +0.080m 앞. | — |
| [`job59g_costchk.py`](../../debug_log/2026-09-08/jobs/job59g_costchk.py) | local costmap 에서 depth 전용 관측점(−20°, 1.46m)이 마킹됐는지 확인 (정적, 주행 없음). | — |
| [`job60b_depthrows.py`](../../debug_log/2026-09-08/jobs/job60b_depthrows.py) | 깊이 이미지 행 띠별 최소 거리 (정면 열 ±40px). 상자가 어느 행(=높이)에 나타나는지 확인. | — |
| [`job60c_voxchk.sh`](../../debug_log/2026-09-08/jobs/job60c_voxchk.sh) |  | — |
| [`job60d_pcdiag.sh`](../../debug_log/2026-09-08/jobs/job60d_pcdiag.sh) |  | — |
| [`job60e_pcon.sh`](../../debug_log/2026-09-08/jobs/job60e_pcon.sh) |  | — |
| [`job60f_pcbox.py`](../../debug_log/2026-09-08/jobs/job60f_pcbox.py) | 포인트클라우드에서 base_link 기준 낮은 물체 탐색: z 0.06~0.40, \|y\|<0.6, x 0.2~2.0 의 점을 x 10cm 구간별로 집계. | — |
| [`job60h_clear.sh`](../../debug_log/2026-09-08/jobs/job60h_clear.sh) |  | — |
| [`job60i_zchk.py`](../../debug_log/2026-09-08/jobs/job60i_zchk.py) |  | — |
| [`job60j_minh.sh`](../../debug_log/2026-09-08/jobs/job60j_minh.sh) |  | — |
| [`job61b_state.sh`](../../debug_log/2026-09-08/jobs/job61b_state.sh) |  | — |
| [`job62_infl.sh`](../../debug_log/2026-09-08/jobs/job62_infl.sh) |  | — |
| [`job62b_fan.py`](../../debug_log/2026-09-08/jobs/job62b_fan.py) | 로컬 코스트맵을 부채꼴로 훑어 x=0.9~1.3m 구간에서 로버 중심이 지날 수 있는 y 슬롯을 찾는다. | — |
| [`job62c_boxdim.py`](../../debug_log/2026-09-08/jobs/job62c_boxdim.py) | 포인트클라우드를 point_step 스트라이드로 정확히 읽어 base_link 기준 장애물 점의 경계상자를 낸다. | — |
| [`job63_planquery.py`](../../debug_log/2026-09-08/jobs/job63_planquery.py) | 무주행 경로 질의 — 로버를 움직이지 않고 '경로가 존재하는가' 를 Nav2 플래너에 직접 묻는다. | 09-08 다음 세션 절차 (충전 후) |
| [`job64c_globaldiag.py`](../../debug_log/2026-09-08/jobs/job64c_globaldiag.py) | 전역 코스트맵 진단: 목표 주변 비용/미지영역, 로버→목표 직선의 셀 상태. | — |
| [`job64d_cleartest.sh`](../../debug_log/2026-09-08/jobs/job64d_cleartest.sh) |  | — |
| [`job64e_map.py`](../../debug_log/2026-09-08/jobs/job64e_map.py) | 전역 코스트맵·slam map 을 로버 기준 ASCII 로 출력 (전방 위쪽, 좌측 왼쪽). | 09-08 전역 플래너가 경로를 못 내던 문제 `job64` |
| [`job67_foxglove.sh`](../../debug_log/2026-09-08/jobs/job67_foxglove.sh) |  | — |
| [`job68_memory.sh`](../../debug_log/2026-09-08/jobs/job68_memory.sh) |  | — |
| [`job71_watchbox.py`](../../debug_log/2026-09-08/jobs/job71_watchbox.py) | 상자 셀 추적 실험 — 접근하는 동안 코스트맵의 '상자 칸'이 언제·왜 사라지는지 직접 본다. | 09-08 다음: 원인 확정 실험 `job71_watchbox.py` (Nav2 미 |
| [`job72_globalmark.sh`](../../debug_log/2026-09-08/jobs/job72_globalmark.sh) |  | — |
| [`job73_probe.py`](../../debug_log/2026-09-08/jobs/job73_probe.py) | 상자를 검출해 map 좌표로 바꾸고 로컬·전역 코스트맵 비용과 깊이점 z 분포를 한 번 출력(주행 없음). | 09-08 정정 A: "전역에 depth 가 마킹되지 않는다"는 **내 좌표 처리  |
| [`job73_run.sh`](../../debug_log/2026-09-08/jobs/job73_run.sh) |  | 09-08 다음 후보 (전역에 깊이를 반영시키는 법) |
| [`job74_layers.sh`](../../debug_log/2026-09-08/jobs/job74_layers.sh) | 전역에 depth 가 안 찍히는 원인 후보를 런타임으로 하나씩 배제한다. 주행 없음. | — |
| [`job75_forward.py`](../../debug_log/2026-09-08/jobs/job75_forward.py) | 전방 장애물 추적 (프레임 정정판) — 접근 중 코스트맵의 '앞쪽 장애물'이 유지되는지 본다. | 09-08 다음 검증 (상자 재배치 후) |
| [`job78_killnav.sh`](../../debug_log/2026-09-08/jobs/job78_killnav.sh) | Nav2 만 강제 종료 (센서·slam·agent 유지). ssh 인라인 금지 — 파일로 실행할 것. | — |
| [`job80_apply.sh`](../../debug_log/2026-09-08/jobs/job80_apply.sh) |  | — |
| [`job82_apply.sh`](../../debug_log/2026-09-08/jobs/job82_apply.sh) |  | — |
| [`job88_pad.sh`](../../debug_log/2026-09-08/jobs/job88_pad.sh) |  | — |
| [`job90_infl.sh`](../../debug_log/2026-09-08/jobs/job90_infl.sh) |  | — |
| [`run_osc.sh`](../../debug_log/2026-09-08/jobs/run_osc.sh) | 사용: run_osc.sh <csv이름> <x> <y> <yaw> <timeout> | — |
| [`run_param.sh`](../../debug_log/2026-09-08/jobs/run_param.sh) | 사용: run_param.sh <node> <param=value> ...  (런타임 파라미터 변경 + 확인) | — |
| [`run_smpos.sh`](../../debug_log/2026-09-08/jobs/run_smpos.sh) | stuck_monitor 정탐 검증 — /cmd_vel 을 /cmd_vel_test 로 리매핑해 로버는 정지한 채 "지령만" 흘림 | — |
| [`stuck_monitor.py`](../../debug_log/2026-09-08/jobs/stuck_monitor.py) | stuck_monitor — rover-level 정체/접촉 감시 (2026-09-07). | 09-07 구현 (1·2번) · 09-18 9.3 · 09-29 §13 · … +1 |

## 2026-09-09 (78)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job100_cmdvel.sh`](../../debug_log/2026-09-09/jobs/job100_cmdvel.sh) | 가설: 보드로 들어가는 /cmd_vel 수신 트래픽이 스핀 루프를 붕괴시킨다. | — |
| [`job101_load.sh`](../../debug_log/2026-09-09/jobs/job101_load.sh) | 부하 단계별 보드 토픽 주기 측정 — micro-ROS 링크 붕괴가 CPU 경합 때문인지 가른다. | — |
| [`job102_clean.sh`](../../debug_log/2026-09-09/jobs/job102_clean.sh) | 중복 프로세스 완전 정리 후, base 만 남긴 상태에서 /wheel_odom 을 60초 연속 관측. | — |
| [`job103_obs.sh`](../../debug_log/2026-09-09/jobs/job103_obs.sh) | 깨끗한 상태(base+sensors+slam, 중복 없음)에서 보드 링크 60초 연속 관측. 아무것도 죽이지 않는다. | — |
| [`job104_obs2.sh`](../../debug_log/2026-09-09/jobs/job104_obs2.sh) | 고아 Nav2 프로세스 제거(에이전트·보드 세션은 건드리지 않음) 후 링크 재관측. | — |
| [`job105_bytes.sh`](../../debug_log/2026-09-09/jobs/job105_bytes.sh) | 결정적 측정: 보드->젯슨 UART 실바이트 유입량과 토픽 수신량을 같은 5초 버킷으로 동시 기록. | — |
| [`job106_baud.sh`](../../debug_log/2026-09-09/jobs/job106_baud.sh) |  | — |
| [`job107_port.sh`](../../debug_log/2026-09-09/jobs/job107_port.sh) |  | — |
| [`job108_rchar.sh`](../../debug_log/2026-09-09/jobs/job108_rchar.sh) | 결정적 측정: agent 가 시리얼에서 실제로 읽어들이는 바이트 수(rchar)를 토픽 수신량과 같은 버킷으로 기록. | — |
| [`job109_inside.sh`](../../debug_log/2026-09-09/jobs/job109_inside.sh) | 문제 위치 판별: 컨테이너 내부(agent 와 같은 DDS 참가자 호스트)에서 본 주기 vs 젯슨 호스트에서 본 주기 | — |
| [`job110_v6.sh`](../../debug_log/2026-09-09/jobs/job110_v6.sh) | agent 를 -v6(DEBUG) 로 띄워 보드가 실제로 어떤 datawriter 로 몇 개를 보내는지 센다. | — |
| [`job111_v6read.sh`](../../debug_log/2026-09-09/jobs/job111_v6read.sh) | -v6 로그 60초 수집 후 집계: 보드가 어떤 datawriter 로 몇 프레임 보냈는가 / agent 가 뭘 버렸는가 | — |
| [`job112_txdiag.sh`](../../debug_log/2026-09-09/jobs/job112_txdiag.sh) | 보드가 /rover/status 로 보고하는 발행 시도/실패 카운터를 5초 간격 차분으로 본다. | — |
| [`job113_txlayer.sh`](../../debug_log/2026-09-09/jobs/job113_txlayer.sh) | 전송 계층 계측: wc=write 호출, wb=gState busy 로 버림, wh=HAL 오류, wt=세마포어 타임아웃, wl=최대 len | — |
| [`job114_lenhist.sh`](../../debug_log/2026-09-09/jobs/job114_lenhist.sh) | agent -v6 로그에서 '수신된 프레임 길이' 분포를 낸다. | — |
| [`job115_normalagent.sh`](../../debug_log/2026-09-09/jobs/job115_normalagent.sh) | -v6 진단 에이전트를 정상 에이전트로 되돌린다 (base.launch 경유). | — |
| [`job116_chk.sh`](../../debug_log/2026-09-09/jobs/job116_chk.sh) |  | — |
| [`job117_baud.sh`](../../debug_log/2026-09-09/jobs/job117_baud.sh) |  | — |
| [`job118_verify.sh`](../../debug_log/2026-09-09/jobs/job118_verify.sh) |  | — |
| [`job120_why.sh`](../../debug_log/2026-09-09/jobs/job120_why.sh) |  | — |
| [`job121_deploy.sh`](../../debug_log/2026-09-09/jobs/job121_deploy.sh) |  | — |
| [`job122_fix.sh`](../../debug_log/2026-09-09/jobs/job122_fix.sh) |  | — |
| [`job123_reinit.sh`](../../debug_log/2026-09-09/jobs/job123_reinit.sh) | 손으로 옮긴 뒤 좌표계 초기화: sensors(EKF) + slam + nav2 재기동. agent/base 는 건드리지 않는다. | — |
| [`job125_avoid3.py`](../../debug_log/2026-09-09/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job127_pad.sh`](../../debug_log/2026-09-09/jobs/job127_pad.sh) |  | — |
| [`job129_layers.sh`](../../debug_log/2026-09-09/jobs/job129_layers.sh) |  | — |
| [`job130_stvl.sh`](../../debug_log/2026-09-09/jobs/job130_stvl.sh) |  | — |
| [`job131_probe.py`](../../debug_log/2026-09-09/jobs/job131_probe.py) | 경로 생성 실패 진단 — 전역/로컬 코스트맵을 로버 전방 부채꼴로 훑어 어디가 막혔는지 본다. | — |
| [`job132_stop.sh`](../../debug_log/2026-09-09/jobs/job132_stop.sh) |  | — |
| [`job133_verify.sh`](../../debug_log/2026-09-09/jobs/job133_verify.sh) |  | — |
| [`job135_live.sh`](../../debug_log/2026-09-09/jobs/job135_live.sh) |  | — |
| [`job137_det.py`](../../debug_log/2026-09-09/jobs/job137_det.py) | job125 의 상자 검출이 왜 실패하는지 — 같은 필터를 단계별로 풀어서 점 수를 센다. | — |
| [`job139_sys.sh`](../../debug_log/2026-09-09/jobs/job139_sys.sh) |  | — |
| [`job142_stall.sh`](../../debug_log/2026-09-09/jobs/job142_stall.sh) |  | — |
| [`job143_estop.sh`](../../debug_log/2026-09-09/jobs/job143_estop.sh) | 즉시 정지: 지령 발행 주체부터 죽이고 0 지령을 반복 발행 | — |
| [`job144_slam.sh`](../../debug_log/2026-09-09/jobs/job144_slam.sh) |  | — |
| [`job145_alive.sh`](../../debug_log/2026-09-09/jobs/job145_alive.sh) |  | — |
| [`job146_ekfin.sh`](../../debug_log/2026-09-09/jobs/job146_ekfin.sh) |  | — |
| [`job147_stamp.py`](../../debug_log/2026-09-09/jobs/job147_stamp.py) | EKF 가 입력은 받는데 출력을 안 하는 원인 추적 — 헤더 타임스탬프와 시스템 시각을 비교한다. | — |
| [`job148_shm.sh`](../../debug_log/2026-09-09/jobs/job148_shm.sh) |  | — |
| [`job149_hardstop.sh`](../../debug_log/2026-09-09/jobs/job149_hardstop.sh) |  | — |
| [`job150_recover.sh`](../../debug_log/2026-09-09/jobs/job150_recover.sh) | DDS 공유메모리 잔재 복구. 핵심: SIGKILL 금지 — SIGTERM 으로 정상 종료시켜야 | — |
| [`job151_check.sh`](../../debug_log/2026-09-09/jobs/job151_check.sh) |  | — |
| [`job153_rt.sh`](../../debug_log/2026-09-09/jobs/job153_rt.sh) |  | — |
| [`job154_reinit.sh`](../../debug_log/2026-09-09/jobs/job154_reinit.sh) | 손 이동 후 좌표계 초기화 + 설정 반영. SIGTERM 우선 (SIGKILL 은 FastDDS 공유메모리 잔재를 | 09-09 8.9 |
| [`job156_stop.sh`](../../debug_log/2026-09-09/jobs/job156_stop.sh) |  | 09-09 8.9 · 09-16 1.6 · 09-16 1.13 |
| [`job157_fg.sh`](../../debug_log/2026-09-09/jobs/job157_fg.sh) |  | — |
| [`job158_alt.sh`](../../debug_log/2026-09-09/jobs/job158_alt.sh) |  | — |
| [`job159_fgdeploy.sh`](../../debug_log/2026-09-09/jobs/job159_fgdeploy.sh) |  | — |
| [`job160_stvlinst.sh`](../../debug_log/2026-09-09/jobs/job160_stvlinst.sh) |  | — |
| [`job161_stvlparam.sh`](../../debug_log/2026-09-09/jobs/job161_stvlparam.sh) |  | — |
| [`job162_p2.sh`](../../debug_log/2026-09-09/jobs/job162_p2.sh) |  | — |
| [`job163_ex.sh`](../../debug_log/2026-09-09/jobs/job163_ex.sh) |  | — |
| [`job164_stvlup.sh`](../../debug_log/2026-09-09/jobs/job164_stvlup.sh) |  | — |
| [`job165_err.sh`](../../debug_log/2026-09-09/jobs/job165_err.sh) |  | — |
| [`job166_nav2only.sh`](../../debug_log/2026-09-09/jobs/job166_nav2only.sh) |  | — |
| [`job168_pre.sh`](../../debug_log/2026-09-09/jobs/job168_pre.sh) |  | — |
| [`job171_chk.sh`](../../debug_log/2026-09-09/jobs/job171_chk.sh) |  | — |
| [`job172_freeze.sh`](../../debug_log/2026-09-09/jobs/job172_freeze.sh) | job170 의 TF 정지(t≈4.0, 절대시각 ≈1788943244) 전후 로그 조사 | — |
| [`job173_slam.sh`](../../debug_log/2026-09-09/jobs/job173_slam.sh) |  | — |
| [`job174_dds.sh`](../../debug_log/2026-09-09/jobs/job174_dds.sh) |  | — |
| [`job176_who.sh`](../../debug_log/2026-09-09/jobs/job176_who.sh) |  | — |
| [`job177_env.sh`](../../debug_log/2026-09-09/jobs/job177_env.sh) |  | — |
| [`job178_imu.sh`](../../debug_log/2026-09-09/jobs/job178_imu.sh) |  | — |
| [`job179_clean.sh`](../../debug_log/2026-09-09/jobs/job179_clean.sh) |  | — |
| [`job180_imuparam.sh`](../../debug_log/2026-09-09/jobs/job180_imuparam.sh) |  | — |
| [`job181_dedup.sh`](../../debug_log/2026-09-09/jobs/job181_dedup.sh) |  | — |
| [`job91_query.py`](../../debug_log/2026-09-09/jobs/job91_query.py) | 현재 자세 기준 전방 D m 목표에 대한 무주행 경로 질의. | 09-09 2 |
| [`job92_avoid.py`](../../debug_log/2026-09-09/jobs/job92_avoid.py) | 회피 주행 검증 (2026-09-09) — inflation 0.40/패딩 0.02 배포 후 첫 실주행. | 09-09 3 |
| [`job93_jump.sh`](../../debug_log/2026-09-09/jobs/job93_jump.sh) |  | — |
| [`job94_clock.sh`](../../debug_log/2026-09-09/jobs/job94_clock.sh) |  | — |
| [`job95_wodom.sh`](../../debug_log/2026-09-09/jobs/job95_wodom.sh) |  | — |
| [`job96_session.sh`](../../debug_log/2026-09-09/jobs/job96_session.sh) |  | — |
| [`job97_recover.sh`](../../debug_log/2026-09-09/jobs/job97_recover.sh) | 보드 RESET 후 복구: ① 보드 토픽 규정 주기 확인(실패 시 중단) ② EKF/SLAM/Nav2 재기동 | — |
| [`job98_entities.sh`](../../debug_log/2026-09-09/jobs/job98_entities.sh) |  | — |
| [`job99_bytes.sh`](../../debug_log/2026-09-09/jobs/job99_bytes.sh) | 보드가 UART 로 실제 몇 바이트를 보내는지 측정 → 펌웨어 발행 실패 vs agent 드롭 을 가른다. | — |
| [`run_j.sh`](../../debug_log/2026-09-09/jobs/run_j.sh) | 범용 러너: $1 = 스크립트 파일명 (스크래치패드 기준), 나머지 = 인자 | 09-10 부수적으로 고친 것 · 09-22 0 · 09-28 3.3 |
| [`run_xfer_all.sh`](../../debug_log/2026-09-09/jobs/run_xfer_all.sh) | 재부팅 후 /tmp 작업 스크립트 일괄 재전송 | 09-10 부수적으로 고친 것 · 09-22 0 · 09-23 0 · … +1 |

## 2026-09-10 (14)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job125_avoid3.py`](../../debug_log/2026-09-10/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job182_s6base.sh`](../../debug_log/2026-09-10/jobs/job182_s6base.sh) | S6 기준선: Nav2 포함 상태에서 EKF 주기 위반 / slam 스캔 폐기 / 노드별 CPU 를 30초 창으로 잰다. | — |
| [`job185_why.sh`](../../debug_log/2026-09-10/jobs/job185_why.sh) |  | — |
| [`job186_stuck.sh`](../../debug_log/2026-09-10/jobs/job186_stuck.sh) |  | — |
| [`job187_src.sh`](../../debug_log/2026-09-10/jobs/job187_src.sh) |  | — |
| [`job188_sm.sh`](../../debug_log/2026-09-10/jobs/job188_sm.sh) |  | — |
| [`job189_wait.sh`](../../debug_log/2026-09-10/jobs/job189_wait.sh) |  | — |
| [`job190_err.sh`](../../debug_log/2026-09-10/jobs/job190_err.sh) |  | — |
| [`job191_nofg.sh`](../../debug_log/2026-09-10/jobs/job191_nofg.sh) |  | — |
| [`job194_bagdrive.sh`](../../debug_log/2026-09-10/jobs/job194_bagdrive.sh) | 주행 + rosbag 기록 (2026-09-10). | 09-10 6 · 09-10 겪은 오류 (기록) |
| [`job197_drift.sh`](../../debug_log/2026-09-10/jobs/job197_drift.sh) |  | — |
| [`job209_static.py`](../../debug_log/2026-09-10/jobs/job209_static.py) | 정지 상태 깊이 지속성 측정 (2026-09-10). | — |
| [`job210_cluster.py`](../../debug_log/2026-09-10/jobs/job210_cluster.py) | 상자 검출을 클러스터링으로 고치고, 그 자리의 코스트맵 비용을 직접 읽는다 (2026-09-10). | — |
| [`job213_axis.py`](../../debug_log/2026-09-10/jobs/job213_axis.py) | 정지 상태 yaw 드리프트의 원천 — 축을 바로잡아 다시 잰다 (2026-09-10). | — |

## 2026-09-11 (63)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job125_avoid3.py`](../../debug_log/2026-09-11/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job218_approach.py`](../../debug_log/2026-09-11/jobs/job218_approach.py) | 접근 실험 — 로컬 코스트맵이 상자를 버리는 지점을 통제된 조건에서 잡는다 (2026-09-11). | 09-11 1 |
| [`job218_back.py`](../../debug_log/2026-09-11/jobs/job218_back.py) | 접근 실험 후 같은 거리만큼 후진 복귀 — 다음 시행을 같은 조건에서 시작하기 위함. | 09-11 6 |
| [`job220_rotate.py`](../../debug_log/2026-09-11/jobs/job220_rotate.py) | 회전 실험 — 로컬 코스트맵이 상자를 버리는 '방위'를 잡는다 (2026-09-11). | 09-11 1 |
| [`job225_face.py`](../../debug_log/2026-09-11/jobs/job225_face.py) | 제자리 회전으로 map 기준 heading 을 맞춘다 (2026-09-11). | 09-11 6 · 09-14 2.6 · 09-14 2.8 · … +2 |
| [`job228_why.py`](../../debug_log/2026-09-11/jobs/job228_why.py) | RPP 가 무엇과 충돌한다고 보는지 찾는다 (2026-09-11). | — |
| [`job230_map.py`](../../debug_log/2026-09-11/jobs/job230_map.py) | 로버 주변 로컬 코스트맵을 격자로 찍고, 같은 영역의 라이다·깊이 점을 겹쳐 본다 (2026-09-11). | 09-11 5 |
| [`job233_pass.py`](../../debug_log/2026-09-11/jobs/job233_pass.py) | 통과 가능성 판정 — 이 배치에서 로버가 지나갈 틈이 있는가 (2026-09-11). | 09-11 5.1 · 09-11 5.6 · 09-11 7 |
| [`job240_clean.sh`](../../debug_log/2026-09-11/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job243_spin.py`](../../debug_log/2026-09-11/jobs/job243_spin.py) | 제자리 회전 중 병진 드리프트 실측 (2026-09-11). | — |
| [`job248_audit.py`](../../debug_log/2026-09-11/jobs/job248_audit.py) | 구성 전면 점검 — 물리 공간 vs 코스트맵 vs 컨트롤러 판정 기준 (2026-09-11). | — |
| [`job249_nav2only.sh`](../../debug_log/2026-09-11/jobs/job249_nav2only.sh) | nav2 만 재기동 — 중복 프로세스 없이. base/sensors/slam 은 건드리지 않는다(보드 세션 유지). | 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · 09-14 0 · 09-16 1.8 |
| [`job250_rsp_then_drive.sh`](../../debug_log/2026-09-11/jobs/job250_rsp_then_drive.sh) | robot_state_publisher 중복 판정 → 프로세스가 정확히 1개일 때만 주행. | — |
| [`job252_fix_then_drive.sh`](../../debug_log/2026-09-11/jobs/job252_fix_then_drive.sh) |  | — |
| [`job254_s4run.sh`](../../debug_log/2026-09-11/jobs/job254_s4run.sh) | S4 1회차 절차: 게이트(중복·보드·통과폭) → 주행 D=1.8 (bag+로그분석) | 09-11 배운 것 · 09-11 절차 (확정) · 09-14 2 · … +3 |
| [`job259_cycle.sh`](../../debug_log/2026-09-11/jobs/job259_cycle.sh) | 복귀 → heading 정렬 → 위치 확인 → S4 다음 회차 | — |
| [`job263_snap_restart_run.sh`](../../debug_log/2026-09-11/jobs/job263_snap_restart_run.sh) |  | — |
| [`job264_cycle3.sh`](../../debug_log/2026-09-11/jobs/job264_cycle3.sh) | S4 3/3: Nav2 복귀 → heading 정렬 → 재기동(base 유지, 새 원점) → 상자 게이트 → 주행 | — |
| [`job266_nudge.py`](../../debug_log/2026-09-11/jobs/job266_nudge.py) | 직선 미세 이동 — 상자 상대 게이트의 dx 를 맞추기 위해. 양수 전진 / 음수 후진. v=0.04. | — |
| [`job267_cycle.sh`](../../debug_log/2026-09-11/jobs/job267_cycle.sh) | 손 이동 후 S4 회차: 재기동 → 상자 측정 → dy 벗어나면 중단 / dx 만 벗어나면 직진 보정 → 게이트 → 주행 | — |
| [`job268_run3.sh`](../../debug_log/2026-09-11/jobs/job268_run3.sh) | S4 3/3 — 사용자 판단: 좌우 17cm 오프셋은 동등 처리. dx 만 직진 보정. 재기동 생략(6분 전 완료, 이후 주행 없음). | — |
| [`job269_return.sh`](../../debug_log/2026-09-11/jobs/job269_return.sh) |  | — |
| [`job270_stuckwhy.sh`](../../debug_log/2026-09-11/jobs/job270_stuckwhy.sh) |  | — |
| [`job271_manual_return.sh`](../../debug_log/2026-09-11/jobs/job271_manual_return.sh) | Nav2 복귀 실패 후 수동 직진 복귀 — 전진 투영(RPP 기준 100) + 라이다 정면 게이트 | — |
| [`job272_back_home.sh`](../../debug_log/2026-09-11/jobs/job272_back_home.sh) | 후진으로 원점 복귀 — 후방 투영(100) + 라이다 후방 게이트. 파서는 tf2_echo 의 대괄호 안만 읽는다. | — |
| [`job273_left.sh`](../../debug_log/2026-09-11/jobs/job273_left.sh) |  | — |
| [`job274_clear_back.sh`](../../debug_log/2026-09-11/jobs/job274_clear_back.sh) | 유령(센서 근거 없는 LETHAL) 제거 → 감사 → 게이트 후진 복귀 | — |
| [`job275_ghost_then_back.py`](../../debug_log/2026-09-11/jobs/job275_ghost_then_back.py) | (1) 유령 띠 다중 프레임 감사: 30 프레임 동안 차체 좌측 띠(x -0.5~0.5, y +0.20~+0.35, z 0.06~0.40)에 | — |
| [`job277_cmdvel.py`](../../debug_log/2026-09-11/jobs/job277_cmdvel.py) | /cmd_vel 명령 충돌 검증 (2026-09-11 저녁, 사용자 질문). | — |
| [`job278_pubs_jp.py`](../../debug_log/2026-09-11/jobs/job278_pubs_jp.py) |  | — |
| [`job279_interleave.py`](../../debug_log/2026-09-11/jobs/job279_interleave.py) |  | — |
| [`job282_ab_timeout.py`](../../debug_log/2026-09-11/jobs/job282_ab_timeout.py) | velocity_smoother.velocity_timeout A/B 검증 (2026-09-11). | — |
| [`job284_raw.py`](../../debug_log/2026-09-11/jobs/job284_raw.py) | 로컬 costmap_raw(0~255)로 footprint 둘레 값을 본다 — behavior_server 의 충돌 검사와 같은 데이터. | — |
| [`job285_behavior.py`](../../debug_log/2026-09-11/jobs/job285_behavior.py) | behavior_server 의 'Collision Ahead' 즉시 실패 원인 (2026-09-11). | — |
| [`job287_course_return.sh`](../../debug_log/2026-09-11/jobs/job287_course_return.sh) | 코스 주행 + Nav2 복귀 — 복구 동작(BackUp)이 살아난 뒤 첫 시험 | — |
| [`job288_return_bag.sh`](../../debug_log/2026-09-11/jobs/job288_return_bag.sh) | Nav2 복귀 + bag + 로그 분석 (복귀에도 사후 분석 근거를 남긴다) | 09-11 5.15 · 09-14 2.8 |
| [`job289_stuck.sh`](../../debug_log/2026-09-11/jobs/job289_stuck.sh) |  | — |
| [`job291_full.sh`](../../debug_log/2026-09-11/jobs/job291_full.sh) | 손 이동 후 전체 검증: 재기동 → 코스 주행 → 복귀(출발 pose+180°) → face 0 | — |
| [`job292_wall.sh`](../../debug_log/2026-09-11/jobs/job292_wall.sh) |  | — |
| [`job293_v2.sh`](../../debug_log/2026-09-11/jobs/job293_v2.sh) | v2: 목표를 벽 앞 창 안에 둔다. 상자 뒷면(map≈1.51)+0.45 ≤ 목표 ≤ 벽 inscribed 직전(map≈2.04) → 현재 x 0.139 기준 D=1.85. | — |
| [`job294_v3.sh`](../../debug_log/2026-09-11/jobs/job294_v3.sh) | v2: 목표를 벽 앞 창 안에 둔다. 상자 뒷면(map≈1.51)+0.45 ≤ 목표 ≤ 벽 inscribed 직전(map≈2.04) → 현재 x 0.139 기준 D=1.85. | — |
| [`job295_v4.sh`](../../debug_log/2026-09-11/jobs/job295_v4.sh) | v2: 목표를 벽 앞 창 안에 둔다. 상자 뒷면(map≈1.51)+0.45 ≤ 목표 ≤ 벽 inscribed 직전(map≈2.04) → 현재 x 0.139 기준 D=1.85. | — |
| [`job296_v5.sh`](../../debug_log/2026-09-11/jobs/job296_v5.sh) | v5: 재기동 → 패딩 readback 게이트 → face 0 → 상자 게이트 → 코스 D=1.85 (복귀는 별도 판단) | — |
| [`job297_v5b.sh`](../../debug_log/2026-09-11/jobs/job297_v5b.sh) |  | — |
| [`job298_v5c.sh`](../../debug_log/2026-09-11/jobs/job298_v5c.sh) |  | — |
| [`job299_redetect.py`](../../debug_log/2026-09-11/jobs/job299_redetect.py) | 상자 재탐지 — 넓은 범위(x 0.3~2.0, 10점 이상)로 모든 낮은 클러스터를 나열하고, x 구간별 y-히스토그램을 찍는다. | — |
| [`job300_v5d.sh`](../../debug_log/2026-09-11/jobs/job300_v5d.sh) | v5: 전진 0.39 (상자 1.27 m 복원) → 힌트 게이트 → 목표 지점 RPP 폭 게이트 → 코스 D=1.85 | — |
| [`job301_back.py`](../../debug_log/2026-09-11/jobs/job301_back.py) | 원시 센서 스윕 게이트 후 현재 heading 그대로 직선 후진 D m, 그 뒤 face 0 는 별도. | — |
| [`job302_home.sh`](../../debug_log/2026-09-11/jobs/job302_home.sh) |  | — |
| [`job303_bagstall.py`](../../debug_log/2026-09-11/jobs/job303_bagstall.py) | bag 정체 순간 분석 (2026-09-11, v5 실패 원인). | 09-11 5.19 |
| [`job304_lethal_audit.py`](../../debug_log/2026-09-11/jobs/job304_lethal_audit.py) | bag 의 특정 시각에 로컬 코스트맵 LETHAL 군집이 무엇인지 감사한다 (2026-09-11). | 09-11 5.19 |
| [`job305_ghost_stats.py`](../../debug_log/2026-09-11/jobs/job305_ghost_stats.py) | 주행 중 새로 생기는 LETHAL 셀의 통계 (2026-09-11) — '유령 셀' 이 어디서 생기는가. | 09-11 5.19 |
| [`job306_depth_live.py`](../../debug_log/2026-09-11/jobs/job306_depth_live.py) | 정지 상태에서 깊이 점군을 8 s 표본해 '단독 셀' 의 출처를 본다 (2026-09-11). 로버는 움직이지 않는다. | 09-11 5.19 |
| [`job307_scene.py`](../../debug_log/2026-09-11/jobs/job307_scene.py) | 정지 상태 현장 지도: 깊이(z 0.06~0.40) 와 라이다를 base_link 5 cm 격자에 겹쳐 그린다 (2026-09-11). 로버는 움직이지 않는다. | 09-11 5.19 |
| [`job308_plan_ab.py`](../../debug_log/2026-09-11/jobs/job308_plan_ab.py) | 정지 상태 계획 A/B — inflation_radius 가 '상자 옆 틈' 에서 계획을 어디에 놓는가 (2026-09-11). 로버는 움직이지 않는다. | 09-11 5.19 |
| [`run_j303.sh`](../../debug_log/2026-09-11/jobs/run_j303.sh) |  | — |
| [`run_j304.sh`](../../debug_log/2026-09-11/jobs/run_j304.sh) |  | — |
| [`run_j305.sh`](../../debug_log/2026-09-11/jobs/run_j305.sh) |  | — |
| [`run_j306.sh`](../../debug_log/2026-09-11/jobs/run_j306.sh) |  | — |
| [`run_j307.sh`](../../debug_log/2026-09-11/jobs/run_j307.sh) |  | — |
| [`run_j308.sh`](../../debug_log/2026-09-11/jobs/run_j308.sh) |  | — |
| [`run_state.sh`](../../debug_log/2026-09-11/jobs/run_state.sh) |  | — |
| [`run_xfer_all2.sh`](../../debug_log/2026-09-11/jobs/run_xfer_all2.sh) | 재부팅 후 /tmp 작업 스크립트 일괄 재전송 (2026-09-14: job* 전체) | 09-14 0 · 09-15 0 |

## 2026-09-14 (50)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job125_avoid3.py`](../../debug_log/2026-09-14/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job225_face.py`](../../debug_log/2026-09-14/jobs/job225_face.py) | 제자리 회전으로 map 기준 heading 을 맞춘다 (2026-09-11). | 09-11 6 · 09-14 2.6 · 09-14 2.8 · … +2 |
| [`job240_clean.sh`](../../debug_log/2026-09-14/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job249_nav2only.sh`](../../debug_log/2026-09-14/jobs/job249_nav2only.sh) | nav2 만 재기동 — 중복 프로세스 없이. base/sensors/slam 은 건드리지 않는다(보드 세션 유지). | 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · 09-14 0 · 09-16 1.8 |
| [`job254_s4run.sh`](../../debug_log/2026-09-14/jobs/job254_s4run.sh) | S4 1회차 절차: 게이트(중복·보드·통과폭) → 주행 D=1.8 (bag+로그분석) | 09-11 배운 것 · 09-11 절차 (확정) · 09-14 2 · … +3 |
| [`job308_plan_ab.py`](../../debug_log/2026-09-14/jobs/job308_plan_ab.py) | 정지 상태 계획 A/B — inflation_radius 가 '상자 옆 틈' 에서 계획을 어디에 놓는가 (2026-09-11). 로버는 움직이지 않는다. | 09-11 5.19 |
| [`job309_lidar_fixed.py`](../../debug_log/2026-09-14/jobs/job309_lidar_fixed.py) | 라이다 '고정점' 판정 (2026-09-14, 사용자 관찰: 우측 전방에 로버 중심에서 항상 같은 거리에 찍히는 점 하나). | — |
| [`job310_bodyfixed.py`](../../debug_log/2026-09-14/jobs/job310_bodyfixed.py) | 주행 bag 에서 '차체 고정점' 을 찾는다 (2026-09-14, 사용자 관찰: 우측 전방에 로버 이동과 무관하게 같은 거리에 찍히는 점). | — |
| [`job311_floor_noise.py`](../../debug_log/2026-09-14/jobs/job311_floor_noise.py) | 정지 상태 30 s: 로버 정면 바닥(전방 0.45~1.0, \|횡\| < 0.3, 물체 없음)에 z ≥ 0.06 깊이점이 생기는가 (2026-09-14). | — |
| [`job312_box_edge.py`](../../debug_log/2026-09-14/jobs/job312_box_edge.py) | 상자 좌측 가장자리 '연장 셀' 의 출처 (2026-09-14). 로버는 움직이지 않는다. | 09-16 1.8 |
| [`job313_relay_dedup.sh`](../../debug_log/2026-09-14/jobs/job313_relay_dedup.sh) | depth_relay 중복 정리: job240 이 sensors(camera.launch)를 재기동하면 launch 가 릴레이를 띄우는데, | 09-14 2.11 |
| [`job314_relay_orphan.sh`](../../debug_log/2026-09-14/jobs/job314_relay_orphan.sh) | depth_relay 고아 정리: sensors.launch 를 죽였을 때 자식 릴레이가 살아남아(robot_state_publisher 와 같은 부류) | — |
| [`job315_boxcells.py`](../../debug_log/2026-09-14/jobs/job315_boxcells.py) | 로컬 코스트맵에서 상자 LETHAL 셀의 최대 y (차체좌표) — 창 게이트용 (2026-09-14 §2.16). 인자: BX BY | 09-22 3 |
| [`job316_env.sh`](../../debug_log/2026-09-14/jobs/job316_env.sh) | N1/N0 환경 조사 (읽기 전용, sudo 없음) + 계획·컨트롤러 A/B 에 필요한 패키지 확인 | — |
| [`job317_plan_ab2.py`](../../debug_log/2026-09-14/jobs/job317_plan_ab2.py) | 계획기 A/B — NavFn(GridBased) vs Smac Hybrid-A*(SmacHybrid), 정지 상태, 주행 없음 (2026-09-14, NVBLOX 계획서 §5-3). | — |
| [`job318_gwobble.py`](../../debug_log/2026-09-14/jobs/job318_gwobble.py) | 전역 코스트맵 흔들림 정량 (2026-09-14 §2.19 후속). 로버 정지, 주행 없음. | — |
| [`job319_gwobble2.py`](../../debug_log/2026-09-14/jobs/job319_gwobble2.py) | 전역 코스트맵 흔들림 정량 (2026-09-14 §2.19 후속). 로버 정지, 주행 없음. | — |
| [`job320_boxfront.py`](../../debug_log/2026-09-14/jobs/job320_boxfront.py) | 상자 앞 0.03~0.35 m, 상자 y 폭 안, z 0.06~0.25 의 깊이점 — '상자 앞 유령 셀' 출처 (2026-09-14). 정지, 주행 없음. | — |
| [`run_ab317.sh`](../../debug_log/2026-09-14/jobs/run_ab317.sh) | 정지 계획 A/B: 재기동(새 YAML: SmacHybrid 등록) → 릴레이 정리 → 계획기 목록 확인 → 상자 감사 → job317 (GridBased vs SmacHybrid), 주행 없음 | — |
| [`run_ab317b.sh`](../../debug_log/2026-09-14/jobs/run_ab317b.sh) | Smac 파라미터 2안 (R 0.10, cost_penalty 1.2, non_straight 1.05) 라이브 적용 → 두 목표(정면 1.8,0 / 통로선 1.8,+0.35)로 정지 A/B, 주행 없음 | — |
| [`run_ab317c.sh`](../../debug_log/2026-09-14/jobs/run_ab317c.sh) | Smac cost_penalty 스윕(정지, use_start=(0,0,0), 목표 1.8/+0.35, 주행 없음) — 라이브 코스트맵(상자 있음) 기준 | — |
| [`run_boxgrow.sh`](../../debug_log/2026-09-14/jobs/run_boxgrow.sh) | 주행 중 코스트맵 상자 군집의 시간 변화: bag 의 여러 시각에 job304 를 돌려 상자 행(전진 0.9~1.6, 횡 -0.4~+0.4 중심)만 뽑는다 | — |
| [`run_edge2.sh`](../../debug_log/2026-09-14/jobs/run_edge2.sh) |  | — |
| [`run_epi.sh`](../../debug_log/2026-09-14/jobs/run_epi.sh) | 주행 bag 에피소드 분석: NAME LOGT(이 시각 이후의 nav2.log 충돌만) [START x y yaw_deg] | 09-14 4 |
| [`run_inf1.sh`](../../debug_log/2026-09-14/jobs/run_inf1.sh) | inflation 0.55/2.0 검증 주행: 재감사(상자 위치·창) 게이트 → job254 (중복·보드·클리어·상자 게이트 → bag 주행 → 로그 분석) | 09-14 2 · 09-14 2.10 · 09-14 2.13 · … +4 |
| [`run_inf1a.sh`](../../debug_log/2026-09-14/jobs/run_inf1a.sh) |  | — |
| [`run_inf2.sh`](../../debug_log/2026-09-14/jobs/run_inf2.sh) |  | — |
| [`run_inf4.sh`](../../debug_log/2026-09-14/jobs/run_inf4.sh) |  | — |
| [`run_j249b.sh`](../../debug_log/2026-09-14/jobs/run_j249b.sh) |  | — |
| [`run_j308.sh`](../../debug_log/2026-09-14/jobs/run_j308.sh) |  | — |
| [`run_j309.sh`](../../debug_log/2026-09-14/jobs/run_j309.sh) |  | — |
| [`run_j312.sh`](../../debug_log/2026-09-14/jobs/run_j312.sh) |  | — |
| [`run_j318.sh`](../../debug_log/2026-09-14/jobs/run_j318.sh) |  | — |
| [`run_j319.sh`](../../debug_log/2026-09-14/jobs/run_j319.sh) |  | — |
| [`run_j320.sh`](../../debug_log/2026-09-14/jobs/run_j320.sh) |  | — |
| [`run_moh.sh`](../../debug_log/2026-09-14/jobs/run_moh.sh) | min_obstacle_height 0.08 배포 → nav2 재기동(job249) → readback → 정지 검증(job312: 코스트맵 상자 범위) → 회전 게이트 → 정렬 → 상자 재검출 | — |
| [`run_pd1.sh`](../../debug_log/2026-09-14/jobs/run_pd1.sh) |  | — |
| [`run_post.sh`](../../debug_log/2026-09-14/jobs/run_post.sh) | 주행 직후: bag·csv 회수(재부팅 전 필수) + 차체 고정점 판정(job310) | 09-14 0 · 09-14 4 |
| [`run_prep2.sh`](../../debug_log/2026-09-14/jobs/run_prep2.sh) |  | — |
| [`run_relay.sh`](../../debug_log/2026-09-14/jobs/run_relay.sh) |  | — |
| [`run_relay2.sh`](../../debug_log/2026-09-14/jobs/run_relay2.sh) |  | — |
| [`run_ret.sh`](../../debug_log/2026-09-14/jobs/run_ret.sh) | Nav2 복귀(bag) → 출발 heading 정렬 → 자세·상자 재검출.  인자: NAME X Y YAW_deg FACE_deg | — |
| [`run_spd1_align.sh`](../../debug_log/2026-09-14/jobs/run_spd1_align.sh) |  | — |
| [`run_spd1_post.sh`](../../debug_log/2026-09-14/jobs/run_spd1_post.sh) |  | — |
| [`run_spd1_prep.sh`](../../debug_log/2026-09-14/jobs/run_spd1_prep.sh) | 손 배치 후: 재기동(job240) → 릴레이 중복 정리(job313) → readback 게이트(RPP 감속·decay·inflation) | — |
| [`run_tc1.sh`](../../debug_log/2026-09-14/jobs/run_tc1.sh) |  | — |
| [`run_tc2_prep.sh`](../../debug_log/2026-09-14/jobs/run_tc2_prep.sh) |  | — |
| [`run_tc3.sh`](../../debug_log/2026-09-14/jobs/run_tc3.sh) |  | — |
| [`run_xfer_all2.sh`](../../debug_log/2026-09-14/jobs/run_xfer_all2.sh) | 재부팅 후 /tmp 작업 스크립트 일괄 재전송 (2026-09-14: job* 전체) | 09-14 0 · 09-15 0 |
| [`run_yaml_deploy.sh`](../../debug_log/2026-09-14/jobs/run_yaml_deploy.sh) |  | — |

## 2026-09-15 (15)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job321_drift.py`](../../debug_log/2026-09-15/jobs/job321_drift.py) | 세션 누적 오차 점검 (2026-09-15, 사용자 우려: 시간이 지나 ROS 세션에 오차가 쌓였는가). 정지 30 s, 주행 없음. | — |
| [`job322_snap.py`](../../debug_log/2026-09-15/jobs/job322_snap.py) | 컬러 카메라 한 프레임을 /tmp/snap.jpg 로 저장 (현장 확인용). 로버는 움직이지 않는다. | 09-22 5.2 |
| [`job323_state.sh`](../../debug_log/2026-09-15/jobs/job323_state.sh) |  | — |
| [`job324_diag.sh`](../../debug_log/2026-09-15/jobs/job324_diag.sh) |  | — |
| [`job325_post_incident.sh`](../../debug_log/2026-09-15/jobs/job325_post_incident.sh) |  | — |
| [`job326_net_fix.sh`](../../debug_log/2026-09-15/jobs/job326_net_fix.sh) | (sudo, 사용자 승인 09-16) 1) mavlink-router 비활성  2) Wi-Fi 자동접속 우선순위: WEB_DEV_5G(192.168.0.x) > ALOPS_ROBOTICS_5G  3) WEB_DEV_5G 로 전환 (nohup — 세션이 | — |
| [`run_ab_bk.sh`](../../debug_log/2026-09-15/jobs/run_ab_bk.sh) | 상자 뒤 목표(1.8, 0) 정지 A/B: Smac cost_penalty × minimum_turning_radius 스윕 (상자 살아 있는 상태, 주행 없음). 인자: BX BY | — |
| [`run_chk15.sh`](../../debug_log/2026-09-15/jobs/run_chk15.sh) |  | — |
| [`run_front2.sh`](../../debug_log/2026-09-15/jobs/run_front2.sh) |  | — |
| [`run_inf1.sh`](../../debug_log/2026-09-15/jobs/run_inf1.sh) | inflation 0.55/2.0 검증 주행: 재감사(상자 위치·창) 게이트 → job254 (중복·보드·클리어·상자 게이트 → bag 주행 → 로그 분석) | 09-14 2 · 09-14 2.10 · 09-14 2.13 · … +4 |
| [`run_j321.sh`](../../debug_log/2026-09-15/jobs/run_j321.sh) |  | — |
| [`run_lan.sh`](../../debug_log/2026-09-15/jobs/run_lan.sh) | Jetson LAN(172.30.1.8) 연결 확인 + 스크립트 실행 러너: $1 = 실행할 원격 스크립트(스크래치패드 파일명) | 09-15 3.1 |
| [`run_pd1.sh`](../../debug_log/2026-09-15/jobs/run_pd1.sh) |  | — |
| [`run_recon.sh`](../../debug_log/2026-09-15/jobs/run_recon.sh) |  | — |
| [`run_usb.sh`](../../debug_log/2026-09-15/jobs/run_usb.sh) | USB 가상 IP(192.168.55.1) 링크 진단 — 핑, TCP 22 배너, ssh 3회(stderr 포함), norc 진단 스크립트 실행 | — |

## 2026-09-16 (71)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`edits_0916.py`](../../debug_log/2026-09-16/jobs/edits_0916.py) | 2026-09-16 일괄 편집: 릴레이 CPU 수정·max_range, decay 120/180, 컨트롤러 10 Hz·MPPI model_dt·visualize, BT MPPI 유지, bag 토픽 | — |
| [`edits_0916b.py`](../../debug_log/2026-09-16/jobs/edits_0916b.py) |  | — |
| [`edits_0916c.py`](../../debug_log/2026-09-16/jobs/edits_0916c.py) |  | — |
| [`edits_0916d.py`](../../debug_log/2026-09-16/jobs/edits_0916d.py) | 2026-09-16 저녁: DDS 를 루프백에 고정(IP 변경 면역) + 러너/잡에 프로파일 export + stuck_shadow | — |
| [`job156_stop.sh`](../../debug_log/2026-09-16/jobs/job156_stop.sh) |  | 09-09 8.9 · 09-16 1.6 · 09-16 1.13 |
| [`job231_drive.sh`](../../debug_log/2026-09-16/jobs/job231_drive.sh) | 검증 주행 — BT 수정(ClearCostmapExceptRegion) + 감쇠 복원(로컬 30초 선형) 상태. | 09-18 17.3 · 09-21 2 · 09-21 6 · … +1 |
| [`job240_clean.sh`](../../debug_log/2026-09-16/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job249_nav2only.sh`](../../debug_log/2026-09-16/jobs/job249_nav2only.sh) | nav2 만 재기동 — 중복 프로세스 없이. base/sensors/slam 은 건드리지 않는다(보드 세션 유지). | 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · 09-14 0 · 09-16 1.8 |
| [`job323_state.sh`](../../debug_log/2026-09-16/jobs/job323_state.sh) |  | — |
| [`job327_mp2why.py`](../../debug_log/2026-09-16/jobs/job327_mp2why.py) | mp2(NavFn+MPPI) 왼쪽 쏠림·정지 원인 분석 (2026-09-16). | 09-16 (머리) |
| [`job328_navlog.sh`](../../debug_log/2026-09-16/jobs/job328_navlog.sh) | nav2.log 에서 LOGT 이후의 컨트롤러/복구/오류 줄만 추출 + drive 로그 앞부분 | 09-16 (머리) |
| [`job329_plancorner.py`](../../debug_log/2026-09-16/jobs/job329_plancorner.py) | /plan 의 헤딩 프로파일: 지정 bag 시각의 최신 계획을 로버 최근접점부터 0.05 m 마다 (x, y, 진행방향°, 로버 yaw 대비 상대각) 출력 | 09-16 (머리) |
| [`job331_boxflicker.sh`](../../debug_log/2026-09-16/jobs/job331_boxflicker.sh) | 상자 셀 최대 y 의 시간 변동(게이트 창 0.186 vs 0.235 오락가락 원인): job315 를 N회 반복 | — |
| [`job333_voxstat.py`](../../debug_log/2026-09-16/jobs/job333_voxstat.py) | 상자 왼쪽 가장자리 셀 깜빡임의 출처 — 필터된 깊이 구름을 odom(코스트맵 격자, 0.05 m, 원점 정렬)으로 옮겨 | 09-16 1.8 |
| [`job334_rate.sh`](../../debug_log/2026-09-16/jobs/job334_rate.sh) | mp3 nav2.log: 제어 루프 지연 경고 수·시각 분포, 진행 실패, MPPI 메시지 | — |
| [`job337_pkgs2.sh`](../../debug_log/2026-09-16/jobs/job337_pkgs2.sh) |  | — |
| [`job338_ghost_decay.py`](../../debug_log/2026-09-16/jobs/job338_ghost_decay.py) | voxel_decay 를 60→120 s(로컬)·90→180 s(전역) 로 늘리면 잡음 셀이 누적돼 통로를 막는가 — 주행 bag 실데이터로 검토 (2026-09-16 §C). | 09-16 1.11 |
| [`job339_relay_prof.sh`](../../debug_log/2026-09-16/jobs/job339_relay_prof.sh) | depth_relay CPU 프로파일: 두 번째 인스턴스를 cProfile 로 12 s 돌려 단계별 시간 (원 릴레이는 그대로) | 09-16 1.11 |
| [`job340_smooth_ab.py`](../../debug_log/2026-09-16/jobs/job340_smooth_ab.py) | 계획 A/B (정지, 주행 없음) — A 계획: 격자 모서리를 입구에서 멀리·완만하게 (2026-09-16 분석 문서 §4 A1/A2). | 09-16 1.11 |
| [`job341_relay_cpu.sh`](../../debug_log/2026-09-16/jobs/job341_relay_cpu.sh) | 새 릴레이 코드(array.array)의 CPU: 두 번째 인스턴스를 20 s 띄우고 top 으로 %CPU 표본 (원 릴레이는 그대로) | — |
| [`job342_readback.sh`](../../debug_log/2026-09-16/jobs/job342_readback.sh) |  | — |
| [`job343_chk.sh`](../../debug_log/2026-09-16/jobs/job343_chk.sh) |  | — |
| [`job345_traj.py`](../../debug_log/2026-09-16/jobs/job345_traj.py) | MPPI 후보 궤적(/trajectories, visualize=true) 분석 — 정체 순간 최적화기가 무엇을 보고 있었나 (2026-09-16 mp4). | — |
| [`job346_mp4state.sh`](../../debug_log/2026-09-16/jobs/job346_mp4state.sh) |  | — |
| [`job347_cancel.sh`](../../debug_log/2026-09-16/jobs/job347_cancel.sh) |  | — |
| [`job348_readback2.sh`](../../debug_log/2026-09-16/jobs/job348_readback2.sh) |  | — |
| [`job349_health.sh`](../../debug_log/2026-09-16/jobs/job349_health.sh) |  | — |
| [`job350_disc.sh`](../../debug_log/2026-09-16/jobs/job350_disc.sh) |  | — |
| [`job351_now.sh`](../../debug_log/2026-09-16/jobs/job351_now.sh) |  | — |
| [`job352_unblock.sh`](../../debug_log/2026-09-16/jobs/job352_unblock.sh) | job156 이 'ros2 topic pub -1 /cmd_vel' 에서 무한 대기(옛 참가자와 매칭 불가) → 죽이고 데몬 재시작 | — |
| [`job353_stop2.sh`](../../debug_log/2026-09-16/jobs/job353_stop2.sh) | 전체 정지(타임아웃 있는 판): 옛 참가자 매칭 대기(ros2 topic pub -1) 를 쓰지 않는다. 로버는 정지 상태(펌웨어 watchdog 500 ms). | 09-16 2 |
| [`job354_critics.py`](../../debug_log/2026-09-16/jobs/job354_critics.py) | MPPI 크리틱 비용 재구성 — "상자 회피" 와 "경로 추종" 이 입구에서 어떻게 충돌하는가 (2026-09-16, mp4 bag). | 09-16 1.14 |
| [`job355_mppi_sim.py`](../../debug_log/2026-09-16/jobs/job355_mppi_sim.py) | MPPI 오프라인 시뮬레이터 — bag 의 정지 장면(로컬 코스트맵·변환 경로·자세)에서 Humble MPPI 의 배치·크리틱·softmax 갱신을 | 09-16 1.14 · 09-17 12.3 |
| [`job356_variants.sh`](../../debug_log/2026-09-16/jobs/job356_variants.sh) | job355 변형 일괄 실행 (bag_mp4 t=17 정체 시작 장면) | — |
| [`job357_variants2.sh`](../../debug_log/2026-09-16/jobs/job357_variants2.sh) |  | — |
| [`job358_variants3.sh`](../../debug_log/2026-09-16/jobs/job358_variants3.sh) |  | — |
| [`job359_agentchk.sh`](../../debug_log/2026-09-16/jobs/job359_agentchk.sh) | 에이전트 컨테이너가 루프백 프로파일을 받았는지 + 세션/토픽 가시성 (루프백 CLI vs 전체 인터페이스 CLI) | — |
| [`job360_wl_test.sh`](../../debug_log/2026-09-16/jobs/job360_wl_test.sh) | 화이트리스트별 /wheel_odom 가시성 (에이전트가 어떤 주소를 광고하는지 간접 확인) | — |
| [`job361_fix.sh`](../../debug_log/2026-09-16/jobs/job361_fix.sh) |  | — |
| [`job362_slamdiag.sh`](../../debug_log/2026-09-16/jobs/job362_slamdiag.sh) |  | — |
| [`job363_rsp.sh`](../../debug_log/2026-09-16/jobs/job363_rsp.sh) |  | — |
| [`job364_mp5state.sh`](../../debug_log/2026-09-16/jobs/job364_mp5state.sh) |  | — |
| [`job365_mp5ana.sh`](../../debug_log/2026-09-16/jobs/job365_mp5ana.sh) |  | — |
| [`job366_mp5sim.sh`](../../debug_log/2026-09-16/jobs/job366_mp5sim.sh) |  | — |
| [`run_alt.sh`](../../debug_log/2026-09-16/jobs/run_alt.sh) | 대체 호스트(172.30.1.8)로 스크립트 실행 + bag/csv 회수 | — |
| [`run_alt2.sh`](../../debug_log/2026-09-16/jobs/run_alt2.sh) |  | — |
| [`run_alt3.sh`](../../debug_log/2026-09-16/jobs/run_alt3.sh) |  | — |
| [`run_dds_deploy.sh`](../../debug_log/2026-09-16/jobs/run_dds_deploy.sh) | fastdds_udp_only.xml + base.launch.py 배포(src+install) → 전체 정지(job156) → 깨끗한 기동(job240, base 부터) | — |
| [`run_drive_nohup.sh`](../../debug_log/2026-09-16/jobs/run_drive_nohup.sh) | 주행 러너 v2 (09-15 교훈): 원격에서 nohup 으로 게이트+주행을 띄우고 로그 파일을 폴링한다 — ssh 가 끊겨도 주행은 기록되고, 재접속 후 이어 읽는다. | 09-18 13.3 · 09-18 17.3 · 09-21 10.1 · … +2 |
| [`run_fix3.sh`](../../debug_log/2026-09-16/jobs/run_fix3.sh) |  | — |
| [`run_gate.sh`](../../debug_log/2026-09-16/jobs/run_gate.sh) | 게이트만 (재기동·주행 없음): 상자 감사 + 통로 띠 + 창(3 표본 중앙값) | 09-18 13.3 |
| [`run_j312.sh`](../../debug_log/2026-09-16/jobs/run_j312.sh) |  | — |
| [`run_j327.sh`](../../debug_log/2026-09-16/jobs/run_j327.sh) |  | — |
| [`run_j327b.sh`](../../debug_log/2026-09-16/jobs/run_j327b.sh) |  | — |
| [`run_j329.sh`](../../debug_log/2026-09-16/jobs/run_j329.sh) |  | — |
| [`run_j333.sh`](../../debug_log/2026-09-16/jobs/run_j333.sh) |  | — |
| [`run_j333b.sh`](../../debug_log/2026-09-16/jobs/run_j333b.sh) | job333 을 raw(백그라운드)·filtered(전경) 두 토픽으로 동시에 DUR 초 실행, 사건(y ≥ EVENT_Y) 기록 | — |
| [`run_j338.sh`](../../debug_log/2026-09-16/jobs/run_j338.sh) |  | — |
| [`run_j338b.sh`](../../debug_log/2026-09-16/jobs/run_j338b.sh) | job338 재실행: mp2 + (있으면) bk1 업로드 후 분석 | — |
| [`run_j340.sh`](../../debug_log/2026-09-16/jobs/run_j340.sh) |  | — |
| [`run_j354.sh`](../../debug_log/2026-09-16/jobs/run_j354.sh) |  | — |
| [`run_j356.sh`](../../debug_log/2026-09-16/jobs/run_j356.sh) |  | — |
| [`run_j366.sh`](../../debug_log/2026-09-16/jobs/run_j366.sh) |  | — |
| [`run_j_alt.sh`](../../debug_log/2026-09-16/jobs/run_j_alt.sh) | 범용 러너: $1 = 스크립트 파일명 (스크래치패드 기준), 나머지 = 인자 | — |
| [`run_prep.sh`](../../debug_log/2026-09-16/jobs/run_prep.sh) | 주행 준비만(주행 없음): 재기동(job240, 에이전트 유지) → 릴레이 고아 정리 → 파라미터 readback → 상자 감사 → 게이트 수치 | — |
| [`run_prep_alt.sh`](../../debug_log/2026-09-16/jobs/run_prep_alt.sh) | 주행 준비만(주행 없음): 재기동(job240, 에이전트 유지) → 릴레이 고아 정리 → 파라미터 readback → 상자 감사 → 게이트 수치 | — |
| [`run_relay_deploy.sh`](../../debug_log/2026-09-16/jobs/run_relay_deploy.sh) | depth_relay.py + camera.launch.py 를 src·install 에 배포 (반영은 다음 sensors 재기동) | — |
| [`run_restart2.sh`](../../debug_log/2026-09-16/jobs/run_restart2.sh) |  | — |
| [`run_snap.sh`](../../debug_log/2026-09-16/jobs/run_snap.sh) |  | — |
| [`run_xml_check.sh`](../../debug_log/2026-09-16/jobs/run_xml_check.sh) |  | — |
| [`run_xml_revert.sh`](../../debug_log/2026-09-16/jobs/run_xml_revert.sh) |  | — |

## 2026-09-17 (129)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`edits_0917.py`](../../debug_log/2026-09-17/jobs/edits_0917.py) |  | — |
| [`edits_0917b.py`](../../debug_log/2026-09-17/jobs/edits_0917b.py) |  | — |
| [`edits_0917c.py`](../../debug_log/2026-09-17/jobs/edits_0917c.py) |  | — |
| [`edits_0917d.py`](../../debug_log/2026-09-17/jobs/edits_0917d.py) |  | — |
| [`edits_sim_db.py`](../../debug_log/2026-09-17/jobs/edits_sim_db.py) |  | — |
| [`fw_build.sh`](../../debug_log/2026-09-17/jobs/fw_build.sh) |  | — |
| [`fw_thresh_edit.py`](../../debug_log/2026-09-17/jobs/fw_thresh_edit.py) |  | — |
| [`fw_verify.sh`](../../debug_log/2026-09-17/jobs/fw_verify.sh) |  | — |
| [`job125_avoid3.py`](../../debug_log/2026-09-17/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job231_drive.sh`](../../debug_log/2026-09-17/jobs/job231_drive.sh) | 검증 주행 — BT 수정(ClearCostmapExceptRegion) + 감쇠 복원(로컬 30초 선형) 상태. | 09-18 17.3 · 09-21 2 · 09-21 6 · … +1 |
| [`job248_audit.py`](../../debug_log/2026-09-17/jobs/job248_audit.py) | 구성 전면 점검 — 물리 공간 vs 코스트맵 vs 컨트롤러 판정 기준 (2026-09-11). | — |
| [`job254_s4run.sh`](../../debug_log/2026-09-17/jobs/job254_s4run.sh) | S4 1회차 절차: 게이트(중복·보드·통과폭) → 주행 D=1.8 (bag+로그분석) | 09-11 배운 것 · 09-11 절차 (확정) · 09-14 2 · … +3 |
| [`job355_mppi_sim.py`](../../debug_log/2026-09-17/jobs/job355_mppi_sim.py) | MPPI 오프라인 시뮬레이터 — bag 의 정지 장면(로컬 코스트맵·변환 경로·자세)에서 Humble MPPI 의 배치·크리틱·softmax 갱신을 | 09-16 1.14 · 09-17 12.3 |
| [`job367_boot.sh`](../../debug_log/2026-09-17/jobs/job367_boot.sh) |  | — |
| [`job368_clusters.sh`](../../debug_log/2026-09-17/jobs/job368_clusters.sh) |  | — |
| [`job369_boxrange.py`](../../debug_log/2026-09-17/jobs/job369_boxrange.py) | 상자 거리 교차검증 (2026-09-17): 깊이 클러스터 0.96 m vs 컬러 영상 추정 1.38 m 불일치. 로버는 움직이지 않는다. | 09-17 13.1 |
| [`job370_scanmatch.py`](../../debug_log/2026-09-17/jobs/job370_scanmatch.py) | 오늘 출발 자세 vs 어제 mp5 출발 자세 — 라이다 스캔 정합(ICP)으로 로버 변위를 구해, 어제 상자 위치(깊이 1.174/−0.013)가 | — |
| [`job371_costbox.py`](../../debug_log/2026-09-17/jobs/job371_costbox.py) | 코스트맵 상자 위치 비교(감사 스크립트 우회): 오늘 로컬 코스트맵 vs 어제 mp5 bag 출발 시 로컬 코스트맵. | — |
| [`job372_cells.py`](../../debug_log/2026-09-17/jobs/job372_cells.py) | 로컬·전역 코스트맵 상자 영역(x 0.5~1.8, \|y\|<0.4) LETHAL 셀 목록 + 3 회(10 s 간격) 반복 — 앞쪽 셀이 잡음인지 지속인지 | — |
| [`job373_mp6post.sh`](../../debug_log/2026-09-17/jobs/job373_mp6post.sh) |  | — |
| [`job374_mp6ana.sh`](../../debug_log/2026-09-17/jobs/job374_mp6ana.sh) |  | — |
| [`job375_goalsim.sh`](../../debug_log/2026-09-17/jobs/job375_goalsim.sh) |  | — |
| [`job376_goalview.sh`](../../debug_log/2026-09-17/jobs/job376_goalview.sh) |  | — |
| [`job377_goalclear.py`](../../debug_log/2026-09-17/jobs/job377_goalclear.py) | 목표 여유 게이트 (2026-09-17, mp6 교훈): 목표 자리에 로버 풋프린트를 놓았을 때 전역 코스트맵 LETHAL 셀까지 최소거리. | 09-17 3 |
| [`job378_goalcands.sh`](../../debug_log/2026-09-17/jobs/job378_goalcands.sh) |  | — |
| [`job379_navevents.sh`](../../debug_log/2026-09-17/jobs/job379_navevents.sh) | 마지막 "Begin navigating" 이후 nav2.log 이벤트(경로 전달·반복 제외) + 드라이브 로그 표 + bag 압축 | 09-18 12.2 |
| [`job380_health.sh`](../../debug_log/2026-09-17/jobs/job380_health.sh) |  | — |
| [`job381_slam.sh`](../../debug_log/2026-09-17/jobs/job381_slam.sh) |  | — |
| [`job382_slamgraph.sh`](../../debug_log/2026-09-17/jobs/job382_slamgraph.sh) |  | — |
| [`job383_slamlast.sh`](../../debug_log/2026-09-17/jobs/job383_slamlast.sh) |  | — |
| [`job384_power.sh`](../../debug_log/2026-09-17/jobs/job384_power.sh) |  | — |
| [`job385_pmhist.sh`](../../debug_log/2026-09-17/jobs/job385_pmhist.sh) |  | — |
| [`job386_slamalive.py`](../../debug_log/2026-09-17/jobs/job386_slamalive.py) | SLAM 생존 게이트 (2026-09-17 mp7): slam_toolbox 프로세스가 살아 있어도 그래프에서 사라지거나 map->odom 이 끊길 수 있다. | 09-17 5 · 10-21 §9 · 10-27 §24 |
| [`job387_slambt.sh`](../../debug_log/2026-09-17/jobs/job387_slambt.sh) | 사용자 승인(09-17): 정지한 slam_toolbox 의 전 스레드 역추적 (읽기 전용 attach, 끝나면 detach) | — |
| [`job388_pm25.sh`](../../debug_log/2026-09-17/jobs/job388_pm25.sh) | 사용자 승인(09-17): 전력 모드 15W(0) → 25W(1). 전후 확인. | — |
| [`job389_pmconf.sh`](../../debug_log/2026-09-17/jobs/job389_pmconf.sh) |  | — |
| [`job390_pmrevert.sh`](../../debug_log/2026-09-17/jobs/job390_pmrevert.sh) | 25W 가 CPU 상한을 1344 MHz 로 낮춤(15W 는 1497) → 사용자 승인 범위의 원복: 15W(0) | — |
| [`job391_fastdds.sh`](../../debug_log/2026-09-17/jobs/job391_fastdds.sh) | 사용자 승인(09-17): ros-humble-fastrtps 2.6.11 → 2.6.12 (StatefulWriter 락 순서 역전 수정 #6463) | — |
| [`job392_rsp_start.sh`](../../debug_log/2026-09-17/jobs/job392_rsp_start.sh) |  | — |
| [`job393_churn.sh`](../../debug_log/2026-09-17/jobs/job393_churn.sh) | Fast DDS 2.6.12 확인: /tf·/map 구독자를 반복 생성·해체하면서 SLAM map->odom 생존 확인 (로버 정지) | 09-17 6.3 |
| [`job394_cmdtrace.py`](../../debug_log/2026-09-17/jobs/job394_cmdtrace.py) | mp8 목표 앞 정지 구간: /cmd_vel 발행 간격·값 분포, /wheel_odom 속도, /rover/status, /odometry/filtered 속도 (goal 기준 초) | — |
| [`job395_status.py`](../../debug_log/2026-09-17/jobs/job395_status.py) | mp8: /rover/status 키-값 전체를 시간순으로(값이 바뀔 때만) + 같은 시각 cmd/wheel 속도 | — |
| [`job396_goalsim8.sh`](../../debug_log/2026-09-17/jobs/job396_goalsim8.sh) | mp8 목표 앞 정지 재현·대안 시뮬레이션 (t=33 s: 상자 통과 직후, 목표까지 약 0.5 m) | — |
| [`job397_lowspeed.py`](../../debug_log/2026-09-17/jobs/job397_lowspeed.py) | 저속 정지 출발 실측 (2026-09-17, 펌웨어 STOP 0.010→0.005 플래시 후) — 로버가 움직인다: 사용자 출발 지시 필수. | 09-17 8.4 |
| [`job398_cmdsrc.sh`](../../debug_log/2026-09-17/jobs/job398_cmdsrc.sh) |  | 09-17 8.6 |
| [`job399_afterflash.sh`](../../debug_log/2026-09-17/jobs/job399_afterflash.sh) |  | 09-17 8.6 |
| [`job400_rotclear.py`](../../debug_log/2026-09-17/jobs/job400_rotclear.py) | 제자리 회전 스윕 여유 (2026-09-17 저속 실측 전): 로컬 코스트맵 LETHAL 셀과 base 중심 거리 최소값. | — |
| [`job401_whydrop.sh`](../../debug_log/2026-09-17/jobs/job401_whydrop.sh) |  | — |
| [`job402_ddssplit.sh`](../../debug_log/2026-09-17/jobs/job402_ddssplit.sh) |  | 09-17 8.7 |
| [`job403_critics_rb.sh`](../../debug_log/2026-09-17/jobs/job403_critics_rb.sh) |  | — |
| [`job404_lowtgt.py`](../../debug_log/2026-09-17/jobs/job404_lowtgt.py) | mp9: 휠 목표가 1~9 mm/s(옛 펌웨어라면 버려졌을 구간)였던 순간 수와 그때 실제 휠 속도, /cmd_vel 최소 크기 | — |
| [`job405_recheck.sh`](../../debug_log/2026-09-17/jobs/job405_recheck.sh) |  | 09-17 10 |
| [`job406_bandcells.sh`](../../debug_log/2026-09-17/jobs/job406_bandcells.sh) |  | 09-17 11 |
| [`job407_wobble.py`](../../debug_log/2026-09-17/jobs/job407_wobble.py) | 조향 흔들림 분석 (2026-09-17, mp9·mp10·mp11 bag). 로버는 움직이지 않는다. | 09-17 12.1 |
| [`job408_wobblesim.sh`](../../debug_log/2026-09-17/jobs/job408_wobblesim.sh) | 흔들림 A/B 시뮬레이션 (백그라운드): 통로 장면 bag_mp11 t=10, 입구 장면 bag_mp4 t=17, 목표 근처 장면 bag_mp8 t=33 | 09-17 12.3 |
| [`job409_lag.py`](../../debug_log/2026-09-17/jobs/job409_lag.py) | 명령 ω → 실제 yaw rate 지연·이득 (mp9·mp10·mp11): /cmd_vel ω 와 /odometry/filtered ω(카메라 자이로 융합) 를 20 ms 격자로 맞춘 뒤 | 09-17 12.2 |
| [`job410_mppi_sim_lag.py`](../../debug_log/2026-09-17/jobs/job410_mppi_sim_lag.py) | MPPI 오프라인 시뮬레이터 — bag 의 정지 장면(로컬 코스트맵·변환 경로·자세)에서 Humble MPPI 의 배치·크리틱·softmax 갱신을 | 09-17 12.3 |
| [`job411_tempsim.sh`](../../debug_log/2026-09-17/jobs/job411_tempsim.sh) | 온도 A/B — 구동계 모델(지연 1 주기·ω 이득 0.7·ω 가속 1.2) 포함. 통로(mp11 bag t=19), 입구(mp4 t=17), 목표 근처(mp8 t=33) | 09-17 12.3 |
| [`job412_tempsim2.sh`](../../debug_log/2026-09-17/jobs/job412_tempsim2.sh) | 조향 흔들림 원인·대책 (2026-09-17): 이상 구동계 vs 실측 구동계(지연 1 주기·ω 이득 0.7·smoother ω 가속 1.2), temperature 0.15/0.22/0.3, wz_std 0.3 | 09-17 12.5 |
| [`job413_wobblecause.sh`](../../debug_log/2026-09-17/jobs/job413_wobblecause.sh) | 조향 흔들림 기제 분리 (2026-09-17): 구동계 요소(smoother ω 가속 제한 / 지연·이득)를 하나씩 + softmax 유효 표본 수(ESS) | 09-17 12.4 |
| [`job415_sectors.py`](../../debug_log/2026-09-17/jobs/job415_sectors.py) | 출발 자세 비교(빠른 판정, 2026-09-17): 현재 스캔 vs bag 출발 스캔의 전/후/좌/우 좁은 복도(폭 ±4 cm) 최근접 거리. | 09-17 13.1 |
| [`job416_boxclear.py`](../../debug_log/2026-09-17/jobs/job416_boxclear.py) | 주행 스크립트 '실여유 0' 검증 (2026-09-17 mp12): bag 의 로컬 코스트맵 LETHAL 셀 ↔ 차체 외곽 사각형 거리. 로버는 움직이지 않는다. | 09-17 13.4 |
| [`job417_compare.sh`](../../debug_log/2026-09-17/jobs/job417_compare.sh) | mp12(temperature 0.3) vs mp9~11(0.15): 흔들림(job407) + 코스트맵 상자 여유(job416), 같은 지표 | 09-17 13.3 |
| [`job418_mppisrc.sh`](../../debug_log/2026-09-17/jobs/job418_mppisrc.sh) | 설치된 nav2_mppi_controller(Humble 1.1.20) 헤더에서 시뮬레이터 충실도 관련 동작 확인 (읽기 전용) | — |
| [`job419_mppi_sim_humble.py`](../../debug_log/2026-09-17/jobs/job419_mppi_sim_humble.py) | [job419, 2026-09-17 §14] humble=1 이면 nav2_mppi_controller 1.1.20 소스 대조로 확인한 동작을 따른다: | 09-17 14.1 |
| [`job420_humblesim.sh`](../../debug_log/2026-09-17/jobs/job420_humblesim.sh) | Humble 1.1.20 동작 모드 시뮬레이터 검증 (2026-09-17 §14): 실측(T0.15 mp9~11 반전 10.3~14.8 /m·RMS 0.058~0.076, T0.3 mp12 8.8 /m·0.059) 재현 여부 | 09-17 14.2 |
| [`job421_dynsim.sh`](../../debug_log/2026-09-17/jobs/job421_dynsim.sh) | 동적 입력 재생 (2026-09-17 §14): 재가지치기만 / +/plan·map->odom 시간 재생 / +코스트맵 시간 재생 — 흔들림이 실측 수준·온도 무관으로 되는지 | 09-17 14.3 |
| [`job421b_dynsim.sh`](../../debug_log/2026-09-17/jobs/job421b_dynsim.sh) | job421 재실행 (2026-09-17 §14): job421 의 run() 이 전역 T 를 덮어써 경로재생·코스트맵재생 변형이 temperature=19 로 돌았다 → local 로 고침, 두 변형만 | 09-17 14.3 |
| [`job422_sensnoise.py`](../../debug_log/2026-09-17/jobs/job422_sensnoise.py) | EKF 상태 잡음 실측 (2026-09-17 §14): 컨트롤러가 받는 /odometry/filtered twist·odom->base_link 자세의 잡음. | 09-17 14.4 |
| [`job423_regensim.sh`](../../debug_log/2026-09-17/jobs/job423_regensim.sh) | regenerate_noises A/B (2026-09-17 §14): 고정 잡음(현재 기본) vs 매 반복 새 잡음, temperature 0.15/0.3, seed 여러 개(잡음 뽑기 편차) | 09-17 14.5 |
| [`job424_latwobble.py`](../../debug_log/2026-09-17/jobs/job424_latwobble.py) | 조향 흔들림이 위치에 주는 영향 (2026-09-17 §14): 통로 구간(odom x 0.6~1.45) odom->base_link 궤적에서 | 09-17 14.6 |
| [`job425_detour.py`](../../debug_log/2026-09-17/jobs/job425_detour.py) | 상자를 크게 돌아간다' 분석 (2026-09-17 §15, 사용자 질문). 로버는 움직이지 않는다. 인자: BAG GOAL_EPOCH [variants=1] | 09-17 15 |
| [`job426_boxframes.py`](../../debug_log/2026-09-17/jobs/job426_boxframes.py) | 로컬(odom) vs 전역(map) 코스트맵의 상자 위치 비교 (2026-09-17 §15). 로버는 움직이지 않는다. 인자: BAG GOAL_EPOCH | 09-17 15 |
| [`job427_wifi.sh`](../../debug_log/2026-09-17/jobs/job427_wifi.sh) | Wi-Fi 끊김·IP 전환 진단 (2026-09-17, 사용자 요청). 읽기 전용 — 설정 변경 없음, sudo 없음, 비밀번호 출력 금지. | 09-17 17 |
| [`job427b_wifi.sh`](../../debug_log/2026-09-17/jobs/job427b_wifi.sh) | Wi-Fi 진단 2 (2026-09-17): 9월 syslog 이벤트 타임라인 + 새 스캔. 읽기 전용, sudo 없음, 비밀 출력 없음. | 09-17 17 |
| [`job427c_wifi.sh`](../../debug_log/2026-09-17/jobs/job427c_wifi.sh) | Wi-Fi 진단 3 (2026-09-17): 전체 기간 AP 별 끊김 집계 + AP 강제 끊김(reason=2) 전후 ±90 s 의 다른 syslog 사건. 읽기 전용. | 09-17 17 |
| [`job427d_wifi.sh`](../../debug_log/2026-09-17/jobs/job427d_wifi.sh) | Wi-Fi 진단 4 (2026-09-17): SSH 세션 빈도(러너 폴링) vs AP 강제 끊김 시각. 읽기 전용. | 09-17 17 |
| [`run_bt_files.sh`](../../debug_log/2026-09-17/jobs/run_bt_files.sh) | BT XML 파일만 배포(src+install), nav2 재기동 없음 + 목표 여유 게이트를 현재 자세에서 시험(mp6 목표 2.2/0 과 후보) | — |
| [`run_deploy_temp.sh`](../../debug_log/2026-09-17/jobs/run_deploy_temp.sh) | nav2_params.yaml 배포(src+install), nav2 재기동 없음 — 기존 설치본과 diff 로 temperature 만 바뀌는지 확인 | — |
| [`run_drive_nohup.sh`](../../debug_log/2026-09-17/jobs/run_drive_nohup.sh) | 주행 러너 v2 (09-15 교훈): 원격에서 nohup 으로 게이트+주행을 띄우고 로그 파일을 폴링한다 — ssh 가 끊겨도 주행은 기록되고, 재접속 후 이어 읽는다. | 09-18 13.3 · 09-18 17.3 · 09-21 10.1 · … +2 |
| [`run_fastdds.sh`](../../debug_log/2026-09-17/jobs/run_fastdds.sh) |  | — |
| [`run_gate2.sh`](../../debug_log/2026-09-17/jobs/run_gate2.sh) | 재부팅 뒤 /tmp 소실 대비: 감사 도구 전송 → 릴레이 고아 → readback → 게이트 (재기동 없음) | 09-28 3.3 |
| [`run_getlogs.sh`](../../debug_log/2026-09-17/jobs/run_getlogs.sh) | Jetson /tmp 로그를 스크래치패드로 회수: 인자 PREFIX | — |
| [`run_j369.sh`](../../debug_log/2026-09-17/jobs/run_j369.sh) |  | — |
| [`run_j371.sh`](../../debug_log/2026-09-17/jobs/run_j371.sh) |  | — |
| [`run_j394.sh`](../../debug_log/2026-09-17/jobs/run_j394.sh) |  | — |
| [`run_j395.sh`](../../debug_log/2026-09-17/jobs/run_j395.sh) |  | — |
| [`run_j396.sh`](../../debug_log/2026-09-17/jobs/run_j396.sh) |  | — |
| [`run_j404.sh`](../../debug_log/2026-09-17/jobs/run_j404.sh) |  | — |
| [`run_j407.sh`](../../debug_log/2026-09-17/jobs/run_j407.sh) |  | — |
| [`run_j408.sh`](../../debug_log/2026-09-17/jobs/run_j408.sh) |  | — |
| [`run_j409.sh`](../../debug_log/2026-09-17/jobs/run_j409.sh) |  | — |
| [`run_j411.sh`](../../debug_log/2026-09-17/jobs/run_j411.sh) |  | — |
| [`run_j412.sh`](../../debug_log/2026-09-17/jobs/run_j412.sh) |  | — |
| [`run_j413.sh`](../../debug_log/2026-09-17/jobs/run_j413.sh) |  | — |
| [`run_j414.sh`](../../debug_log/2026-09-17/jobs/run_j414.sh) | 출발 자세 교차검증 (주행 없음): 원시 깊이 상자 거리(job369) + 현재 스캔 ↔ mp10·mp11 bag 출발 스캔 ICP(job370) | — |
| [`run_j414b.sh`](../../debug_log/2026-09-17/jobs/run_j414b.sh) |  | — |
| [`run_j415.sh`](../../debug_log/2026-09-17/jobs/run_j415.sh) |  | — |
| [`run_j416.sh`](../../debug_log/2026-09-17/jobs/run_j416.sh) |  | — |
| [`run_j417.sh`](../../debug_log/2026-09-17/jobs/run_j417.sh) |  | — |
| [`run_j418.sh`](../../debug_log/2026-09-17/jobs/run_j418.sh) |  | — |
| [`run_j418b.sh`](../../debug_log/2026-09-17/jobs/run_j418b.sh) |  | — |
| [`run_j418c.sh`](../../debug_log/2026-09-17/jobs/run_j418c.sh) |  | — |
| [`run_j420.sh`](../../debug_log/2026-09-17/jobs/run_j420.sh) |  | — |
| [`run_j421.sh`](../../debug_log/2026-09-17/jobs/run_j421.sh) |  | — |
| [`run_j421b.sh`](../../debug_log/2026-09-17/jobs/run_j421b.sh) |  | — |
| [`run_j422.sh`](../../debug_log/2026-09-17/jobs/run_j422.sh) |  | — |
| [`run_j423.sh`](../../debug_log/2026-09-17/jobs/run_j423.sh) |  | — |
| [`run_j424.sh`](../../debug_log/2026-09-17/jobs/run_j424.sh) |  | — |
| [`run_j425.sh`](../../debug_log/2026-09-17/jobs/run_j425.sh) |  | — |
| [`run_j426.sh`](../../debug_log/2026-09-17/jobs/run_j426.sh) |  | — |
| [`run_j427.sh`](../../debug_log/2026-09-17/jobs/run_j427.sh) |  | — |
| [`run_j427b.sh`](../../debug_log/2026-09-17/jobs/run_j427b.sh) |  | — |
| [`run_j427c.sh`](../../debug_log/2026-09-17/jobs/run_j427c.sh) |  | — |
| [`run_j427d.sh`](../../debug_log/2026-09-17/jobs/run_j427d.sh) |  | — |
| [`run_lowprep.sh`](../../debug_log/2026-09-17/jobs/run_lowprep.sh) |  | — |
| [`run_lowspeed.sh`](../../debug_log/2026-09-17/jobs/run_lowspeed.sh) |  | — |
| [`run_mp6ana.sh`](../../debug_log/2026-09-17/jobs/run_mp6ana.sh) |  | — |
| [`run_mp6post.sh`](../../debug_log/2026-09-17/jobs/run_mp6post.sh) |  | — |
| [`run_mp7prep.sh`](../../debug_log/2026-09-17/jobs/run_mp7prep.sh) |  | — |
| [`run_mp8prep.sh`](../../debug_log/2026-09-17/jobs/run_mp8prep.sh) |  | — |
| [`run_mp9prep.sh`](../../debug_log/2026-09-17/jobs/run_mp9prep.sh) |  | 09-22 0 · 09-22 2 · 09-22 4 · … +3 |
| [`run_pm25.sh`](../../debug_log/2026-09-17/jobs/run_pm25.sh) |  | — |
| [`run_pmrevert.sh`](../../debug_log/2026-09-17/jobs/run_pmrevert.sh) |  | — |
| [`run_post3.sh`](../../debug_log/2026-09-17/jobs/run_post3.sh) |  | 09-18 12.2 · 09-18 17.3 · 09-21 6 · … +2 |
| [`run_slambt.sh`](../../debug_log/2026-09-17/jobs/run_slambt.sh) |  | — |
| [`run_verify2612.sh`](../../debug_log/2026-09-17/jobs/run_verify2612.sh) |  | — |
| [`run_wait423.sh`](../../debug_log/2026-09-17/jobs/run_wait423.sh) |  | — |
| [`run_waitsim.sh`](../../debug_log/2026-09-17/jobs/run_waitsim.sh) | 원격 시뮬 로그에 끝 표시가 나올 때까지 대기(최대 N 초) 후 출력 | — |

## 2026-09-18 (100)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job125_avoid3.py`](../../debug_log/2026-09-18/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job231_drive.sh`](../../debug_log/2026-09-18/jobs/job231_drive.sh) | 검증 주행 — BT 수정(ClearCostmapExceptRegion) + 감쇠 복원(로컬 30초 선형) 상태. | 09-18 17.3 · 09-21 2 · 09-21 6 · … +1 |
| [`job254_s4run.sh`](../../debug_log/2026-09-18/jobs/job254_s4run.sh) | S4 1회차 절차: 게이트(중복·보드·통과폭) → 주행 D=1.8 (bag+로그분석) | 09-11 배운 것 · 09-11 절차 (확정) · 09-14 2 · … +3 |
| [`job379_navevents.sh`](../../debug_log/2026-09-18/jobs/job379_navevents.sh) | 마지막 "Begin navigating" 이후 nav2.log 이벤트(경로 전달·반복 제외) + 드라이브 로그 표 + bag 압축 | 09-18 12.2 |
| [`job428_wifi_dfs.sh`](../../debug_log/2026-09-18/jobs/job428_wifi_dfs.sh) | WEB_DEV_5G(ipTIME AX3000R, 5 GHz ch36·160 MHz = DFS 52~64 포함) 끊김이 DFS/채널 전환과 관련되는지 (2026-09-18). 읽기 전용. | 09-18 4 |
| [`job428b_now.sh`](../../debug_log/2026-09-18/jobs/job428b_now.sh) |  | — |
| [`job428c_bss.sh`](../../debug_log/2026-09-18/jobs/job428c_bss.sh) |  | — |
| [`job428d_pmf.sh`](../../debug_log/2026-09-18/jobs/job428d_pmf.sh) |  | — |
| [`job429_probe.sh`](../../debug_log/2026-09-18/jobs/job429_probe.sh) | A안 사전 점검 (2026-09-18): 디스크, wpa_supplicant 실행 인자, wpa_cli 모니터가 debug 메시지를 받는지 20 s 시험, 단일 채널 스캔 가능 여부. | 09-18 7.1 |
| [`job429b_montest.sh`](../../debug_log/2026-09-18/jobs/job429b_montest.sh) | wpa_cli 모니터 재시험: 줄 버퍼(stdbuf -oL) + level 2. 5 s 뒤 scan 1 회. 설정 변경 없음. | 09-18 7.1 |
| [`job429c_dbgrate.sh`](../../debug_log/2026-09-18/jobs/job429c_dbgrate.sh) | wpa_supplicant debug 로그 양 측정 60 s 후 원래 수준 복귀. 핸드셰이크 줄이 나오는지 보려고 중간에 scan 1 회. | 09-18 7.1 |
| [`job429d_install.sh`](../../debug_log/2026-09-18/jobs/job429d_install.sh) | A안 설치 (2026-09-18, 사용자 승인): wifi-mon 서비스 + rsyslog 규칙. 네트워크 설정은 바꾸지 않는다. SPW 환경변수로 sudo. | 09-18 7.2 |
| [`job429e_check.sh`](../../debug_log/2026-09-18/jobs/job429e_check.sh) |  | — |
| [`job429f_trace.sh`](../../debug_log/2026-09-18/jobs/job429f_trace.sh) |  | — |
| [`job429g_tail.sh`](../../debug_log/2026-09-18/jobs/job429g_tail.sh) |  | — |
| [`job429h_redeploy.sh`](../../debug_log/2026-09-18/jobs/job429h_redeploy.sh) |  | 09-18 7.2 |
| [`job429i_snaptest.sh`](../../debug_log/2026-09-18/jobs/job429i_snaptest.sh) | 사건 스냅샷 함수 단독 시험(네트워크 변경 없음). 결과 파일은 확인 후 test_ 접두로 남긴다. | — |
| [`job429j_secret.sh`](../../debug_log/2026-09-18/jobs/job429j_secret.sh) |  | — |
| [`job430_disk.sh`](../../debug_log/2026-09-18/jobs/job430_disk.sh) | 로그·산출물 누적 조사 (2026-09-18, 읽기 전용 — 삭제 없음). sudo 는 크기 읽기에만. | 09-18 8 |
| [`job430b_logs.sh`](../../debug_log/2026-09-18/jobs/job430b_logs.sh) | logrotate 설치·예약 여부, ~/.ros/log 구성 (읽기 전용) | 09-18 8 |
| [`job430c_talkers.sh`](../../debug_log/2026-09-18/jobs/job430c_talkers.sh) | syslog 를 채우는 프로그램 (읽기 전용): 최근 7 일 날짜별 크기, 9/17 하루 프로그램별 줄 수·바이트 | 09-18 8 |
| [`job431_odomdrift.py`](../../debug_log/2026-09-18/jobs/job431_odomdrift.py) | odom 이 옆 이동을 덜 세는 원인 (2026-09-18). 로버는 움직이지 않는다. 인자: BAG GOAL_EPOCH [T_END] ... (T_END: 목표 도착 s — 주면 그 뒤 정지 구간 보정을 뺀다; 09-18 §11 에서 추가) | 09-18 9.1 · 09-18 11.2 |
| [`job431b_crab.py`](../../debug_log/2026-09-18/jobs/job431b_crab.py) | SLAM(map) 자세로 본 '진행 방향 − 몸체 방향'(게걸음 각) 통계 (2026-09-18). 인자: BAG GOAL_EPOCH [...] | 09-18 9.1 · 09-18 11.2 |
| [`job431c_bigcorr.py`](../../debug_log/2026-09-18/jobs/job431c_bigcorr.py) | [job431c] 큰 옆 보정(\|δl\|>1 cm)의 시각·당시 운동 목록 + 시간대별 누적. 원판 job431: | — |
| [`job431d_morows.py`](../../debug_log/2026-09-18/jobs/job431d_morows.py) | map->odom 원시 기록 점검(2026-09-18): 한 보정이 두 번 세어지는지. 인자: BAG GOAL_EPOCH T0 T1 | 09-18 11.2 |
| [`job432_run.sh`](../../debug_log/2026-09-18/jobs/job432_run.sh) | 장착 yaw 측정 실행 (정지, 모터 경로 없음): 라이다 노드 단독 + 카메라(IMU·컬러 끔) → 측정 → 두 노드 종료 | 09-18 9.2 |
| [`job432_wallyaw.py`](../../debug_log/2026-09-18/jobs/job432_wallyaw.py) | 라이다·카메라 장착 yaw 측정 (2026-09-18). 로버 옆면(트랙 앞뒤 모두)을 곧은 벽에 붙여 두고 정지 상태에서 실행. | 09-18 9.2 |
| [`job432c_run.sh`](../../debug_log/2026-09-18/jobs/job432c_run.sh) | 장착 yaw 측정 실행 (정지, 모터 경로 없음): 라이다 노드 단독 + 카메라(IMU·컬러 끔) → 측정 → 두 노드 종료 | — |
| [`job432c_wallyaw_tf.py`](../../debug_log/2026-09-18/jobs/job432c_wallyaw_tf.py) | [job432c] 보정 URDF 검증판 — 공칭값 대신 robot_state_publisher 의 TF(base_link←lidar_link, base_link←카메라 구름 프레임)를 쓴다. 기대: 옆벽 ≈ 0°. | 09-18 9.3 |
| [`job433_deploy.sh`](../../debug_log/2026-09-18/jobs/job433_deploy.sh) | 데크 yaw 보정 배포 (2026-09-18): rover.urdf·rover.urdf.xacro·stuck_monitor.py 를 src+install 에. 기존본은 ~/ros2_ws/.bak_20260918/ 에 백업. | 09-18 9.3 |
| [`job434_base.sh`](../../debug_log/2026-09-18/jobs/job434_base.sh) | base(micro-ROS 에이전트 + robot_state_publisher)만 기동 — 이후 사용자 보드 리셋 | — |
| [`job434b_rspdedup.sh`](../../debug_log/2026-09-18/jobs/job434b_rspdedup.sh) | robot_state_publisher 중복 정리: base.launch 의 자식이 아닌 것(벽 측정 때 description.launch 로 띄운 것)만 종료 | 09-18 10 |
| [`job434c_temp.sh`](../../debug_log/2026-09-18/jobs/job434c_temp.sh) |  | — |
| [`job438_tfgaps.py`](../../debug_log/2026-09-18/jobs/job438_tfgaps.py) | TF 발행 공백·시각 어긋남 점검 (2026-09-18, 간헐 중단 원인). 인자: BAG GOAL_EPOCH T_END [EVENT_T ...] 반복은 '--' 로 구분 | 09-18 12.2 |
| [`job439_startcells.py`](../../debug_log/2026-09-18/jobs/job439_startcells.py) | 출발 순간 로버 근처 장애물 셀 (2026-09-18 dy3: 출발 0.04 s 스무더 충돌·0.88 s Optimizer fail). 인자: BAG GOAL_EPOCH [BAG GOAL_EPOCH ...] | 09-18 13.2 |
| [`job440_startclear.py`](../../debug_log/2026-09-18/jobs/job440_startclear.py) | 출발 자세 여유 게이트 (2026-09-18 dy3 교훈): 로버 뒤 ≈5 cm 의 물체(관찰자 발 추정)로 출발 자세가 내접 셀 안에 들어가 | 09-18 13.3 · 10-27 §24 |
| [`job441_rearscan.py`](../../debug_log/2026-09-18/jobs/job441_rearscan.py) | 출발 직전 로버 뒤쪽 라이다 점 비교 (2026-09-18 dy3 '뒤 5 cm 물체' 검증). 인자: BAG GOAL_EPOCH [...] | 09-18 13.2 |
| [`job441b_rearobj.py`](../../debug_log/2026-09-18/jobs/job441b_rearobj.py) | dy3 출발 때 로버 뒤 물체 추적 (2026-09-18). 인자: BAG GOAL_EPOCH | 09-18 13.2 |
| [`job441c_rearshape.py`](../../debug_log/2026-09-18/jobs/job441c_rearshape.py) | dy3 출발 때 로버 뒤 물체 추적 (2026-09-18). 인자: BAG GOAL_EPOCH | 09-18 13.2 |
| [`job442_clearwait.sh`](../../debug_log/2026-09-18/jobs/job442_clearwait.sh) | 사람 흔적 셀 제거(09-18): 로컬·전역 코스트맵을 비우고 8 s 동안 현재 센서로 다시 채운다(상자는 카메라 앞이라 곧바로 재마킹) | 09-18 13.3 |
| [`job444_boxmodel.py`](../../debug_log/2026-09-18/jobs/job444_boxmodel.py) | 러너 ① '실제 최근접' 이 dy3 에서 0.0 cm(접촉)로 나온 원인 재구성 (2026-09-18). 인자: NAME BAG_DIR GOAL_EPOCH CSV BOX_FX BOX_CY [...] | 09-18 13.4 |
| [`job445_lidarbox.py`](../../debug_log/2026-09-18/jobs/job445_lidarbox.py) | 라이다가 상자를 보는가 (2026-09-18, 사용자 질의). 인자: BAG GOAL_EPOCH BOX_FX BOX_CY | 09-18 14 |
| [`job446_pathdecomp.py`](../../debug_log/2026-09-18/jobs/job446_pathdecomp.py) | 상자 옆 여유가 어디서 줄어드는가 — 원경로(NavFn) → 스무딩(SimpleSmoother 재현) → 실제(MPPI) 분해 (2026-09-18 §15). | 09-18 15.1 · 09-18 16 |
| [`job448_leftwall.py`](../../debug_log/2026-09-18/jobs/job448_leftwall.py) | 원경로 옆 위치가 회차마다 다른 이유 (2026-09-18 §15). 인자: NAME BAG GOAL_EPOCH [...] | 09-18 15.2 |
| [`job449_criticcurve.py`](../../debug_log/2026-09-18/jobs/job449_criticcurve.py) | 상자 옆 통과 중 '옆 여유 c' 에 따른 장애물 크리틱 비용 곡선 — 1.1.20 소스(obstacles_critic.cpp, cost_critic.cpp) 그대로 (2026-09-18 §15). | 09-18 15.3 · 09-18 16 |
| [`job450_envchk.sh`](../../debug_log/2026-09-18/jobs/job450_envchk.sh) |  | — |
| [`job450b_bw.sh`](../../debug_log/2026-09-18/jobs/job450b_bw.sh) |  | — |
| [`job451_paramsnap.py`](../../debug_log/2026-09-18/jobs/job451_paramsnap.py) | 주행 재현용 파라미터 스냅샷 (2026-09-18 §17). 노드 하나로 여러 노드의 list/get_parameters 서비스를 직접 불러 | 09-18 17.3 |
| [`job452_mppi_sim_cc.py`](../../debug_log/2026-09-18/jobs/job452_mppi_sim_cc.py) | [job452, 2026-09-18 §17] job419(09-17 §14, Humble 1.1.20 동작 모드) 에 **CostCritic** 을 추가한 판. 원본 동작은 obst=0 으로 유지. | 09-18 17.2 |
| [`job452_run.sh`](../../debug_log/2026-09-18/jobs/job452_run.sh) | CostCritic 사전 검증 (2026-09-18 §17): dy2·dy4·dy6 bag 의 세 장면(입구 차선변경 goal+8 s, 복귀 회전 시작 goal+16.5 s, 상자 뒤 모서리 goal+20 s) | 09-18 17.2 |
| [`job453_runmeta.sh`](../../debug_log/2026-09-18/jobs/job453_runmeta.sh) | 주행 재현 메타 (2026-09-18 §17): "무엇으로 달렸는지" 를 bag 옆에 남긴다 — 실행 중 노드의 실제 파라미터(job451), 배포 파일 해시, 단계·메모, 기록 토픽. | 09-18 17.3 |
| [`run_deploy_cc.sh`](../../debug_log/2026-09-18/jobs/run_deploy_cc.sh) | nav2_params.yaml 배포(src+install) — CostCritic 교체 (09-18 §17). nav2 재기동 없음(다음 run_mp9prep 이 재기동). 설치본과 diff 로 바뀐 줄만 확인, 기존본 백업. | 09-18 17.5 |
| [`run_drive_gateonly.sh`](../../debug_log/2026-09-18/jobs/run_drive_gateonly.sh) | 주행 러너 v2 (09-15 교훈): 원격에서 nohup 으로 게이트+주행을 띄우고 로그 파일을 폴링한다 — ssh 가 끊겨도 주행은 기록되고, 재접속 후 이어 읽는다. | — |
| [`run_drive_nohup.sh`](../../debug_log/2026-09-18/jobs/run_drive_nohup.sh) | 주행 러너 v2 (09-15 교훈): 원격에서 nohup 으로 게이트+주행을 띄우고 로그 파일을 폴링한다 — ssh 가 끊겨도 주행은 기록되고, 재접속 후 이어 읽는다. | 09-18 13.3 · 09-18 17.3 · 09-21 10.1 · … +2 |
| [`run_gate.sh`](../../debug_log/2026-09-18/jobs/run_gate.sh) | 게이트만 (재기동·주행 없음): 상자 감사 + 통로 띠 + 창(3 표본 중앙값) | 09-18 13.3 |
| [`run_j428b.sh`](../../debug_log/2026-09-18/jobs/run_j428b.sh) |  | — |
| [`run_j428c.sh`](../../debug_log/2026-09-18/jobs/run_j428c.sh) |  | — |
| [`run_j428d.sh`](../../debug_log/2026-09-18/jobs/run_j428d.sh) |  | — |
| [`run_j429.sh`](../../debug_log/2026-09-18/jobs/run_j429.sh) |  | — |
| [`run_j429d.sh`](../../debug_log/2026-09-18/jobs/run_j429d.sh) |  | — |
| [`run_j429h.sh`](../../debug_log/2026-09-18/jobs/run_j429h.sh) |  | — |
| [`run_j431.sh`](../../debug_log/2026-09-18/jobs/run_j431.sh) |  | — |
| [`run_j431b.sh`](../../debug_log/2026-09-18/jobs/run_j431b.sh) |  | — |
| [`run_j432.sh`](../../debug_log/2026-09-18/jobs/run_j432.sh) |  | — |
| [`run_j432c.sh`](../../debug_log/2026-09-18/jobs/run_j432c.sh) |  | — |
| [`run_j433.sh`](../../debug_log/2026-09-18/jobs/run_j433.sh) |  | — |
| [`run_j434.sh`](../../debug_log/2026-09-18/jobs/run_j434.sh) |  | — |
| [`run_j435.sh`](../../debug_log/2026-09-18/jobs/run_j435.sh) |  | 09-18 10 |
| [`run_j435b.sh`](../../debug_log/2026-09-18/jobs/run_j435b.sh) |  | — |
| [`run_j435c.sh`](../../debug_log/2026-09-18/jobs/run_j435c.sh) |  | — |
| [`run_j435d.sh`](../../debug_log/2026-09-18/jobs/run_j435d.sh) |  | — |
| [`run_j435e.sh`](../../debug_log/2026-09-18/jobs/run_j435e.sh) |  | — |
| [`run_j435f.sh`](../../debug_log/2026-09-18/jobs/run_j435f.sh) |  | — |
| [`run_j436.sh`](../../debug_log/2026-09-18/jobs/run_j436.sh) |  | — |
| [`run_j436b.sh`](../../debug_log/2026-09-18/jobs/run_j436b.sh) |  | — |
| [`run_j436c.sh`](../../debug_log/2026-09-18/jobs/run_j436c.sh) |  | — |
| [`run_j437.sh`](../../debug_log/2026-09-18/jobs/run_j437.sh) |  | — |
| [`run_j438.sh`](../../debug_log/2026-09-18/jobs/run_j438.sh) |  | — |
| [`run_j439.sh`](../../debug_log/2026-09-18/jobs/run_j439.sh) |  | — |
| [`run_j440.sh`](../../debug_log/2026-09-18/jobs/run_j440.sh) |  | — |
| [`run_j441.sh`](../../debug_log/2026-09-18/jobs/run_j441.sh) |  | — |
| [`run_j441b.sh`](../../debug_log/2026-09-18/jobs/run_j441b.sh) |  | — |
| [`run_j441c.sh`](../../debug_log/2026-09-18/jobs/run_j441c.sh) |  | — |
| [`run_j442.sh`](../../debug_log/2026-09-18/jobs/run_j442.sh) |  | — |
| [`run_j443.sh`](../../debug_log/2026-09-18/jobs/run_j443.sh) |  | — |
| [`run_j444.sh`](../../debug_log/2026-09-18/jobs/run_j444.sh) |  | 09-18 13.4 |
| [`run_j445.sh`](../../debug_log/2026-09-18/jobs/run_j445.sh) |  | — |
| [`run_j446.sh`](../../debug_log/2026-09-18/jobs/run_j446.sh) |  | — |
| [`run_j447.sh`](../../debug_log/2026-09-18/jobs/run_j447.sh) |  | — |
| [`run_j448.sh`](../../debug_log/2026-09-18/jobs/run_j448.sh) |  | — |
| [`run_j450.sh`](../../debug_log/2026-09-18/jobs/run_j450.sh) |  | — |
| [`run_j450b.sh`](../../debug_log/2026-09-18/jobs/run_j450b.sh) |  | — |
| [`run_j451.sh`](../../debug_log/2026-09-18/jobs/run_j451.sh) |  | — |
| [`run_j452.sh`](../../debug_log/2026-09-18/jobs/run_j452.sh) |  | — |
| [`run_j452chk.sh`](../../debug_log/2026-09-18/jobs/run_j452chk.sh) |  | — |
| [`run_j452get.sh`](../../debug_log/2026-09-18/jobs/run_j452get.sh) |  | — |
| [`run_j453.sh`](../../debug_log/2026-09-18/jobs/run_j453.sh) |  | — |
| [`run_post3.sh`](../../debug_log/2026-09-18/jobs/run_post3.sh) |  | 09-18 12.2 · 09-18 17.3 · 09-21 6 · … +2 |
| [`run_xfer_exist.sh`](../../debug_log/2026-09-18/jobs/run_xfer_exist.sh) |  | — |
| [`wifi_mon.sh`](../../debug_log/2026-09-18/jobs/wifi_mon.sh) | Wi-Fi 계측 (2026-09-18 A안: WEB_DEV_5G 가 끊고 재인증을 거부하는 원인 — DFS(160 MHz) vs PMF/드라이버). | 09-18 7.2 · 09-23 5 |

## 2026-09-21 (94)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job125_avoid3.py`](../../debug_log/2026-09-21/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job231_drive.sh`](../../debug_log/2026-09-21/jobs/job231_drive.sh) | 검증 주행 — BT 수정(ClearCostmapExceptRegion) + 감쇠 복원(로컬 30초 선형) 상태. | 09-18 17.3 · 09-21 2 · 09-21 6 · … +1 |
| [`job457_cpustate.sh`](../../debug_log/2026-09-21/jobs/job457_cpustate.sh) |  | — |
| [`job458_nearrange.py`](../../debug_log/2026-09-21/jobs/job458_nearrange.py) | S2 근거리 측정 (2026-09-21 §5). 인자: NAME D_FRONT DEC [SEC=10] [W=0.18] [H=0.14] [DEPTH=0.11] | 09-21 5 |
| [`job459_setdec.sh`](../../debug_log/2026-09-21/jobs/job459_setdec.sh) | 디시메이션 런타임 변경 시험 (S2): realsense-ros 4.x 는 필터 파라미터가 동적이라 재기동 없이 바뀌는지 본다. 인자: DEC | 09-21 5 |
| [`job460_artifact.py`](../../debug_log/2026-09-21/jobs/job460_artifact.py) | 근거리 아티팩트 재확인 (2026-09-21 §5, 09-14 job311/312 의 '0.36~0.38 m 에 17 % 프레임' 근거를 데크 보정 뒤 다시 본다). 인자: [SEC=30] [DEC] | 09-21 5 |
| [`job461_tegratest.sh`](../../debug_log/2026-09-21/jobs/job461_tegratest.sh) |  | — |
| [`job462_baghz.py`](../../debug_log/2026-09-21/jobs/job462_baghz.py) | S5 기준선: bag 에서 토픽별 실측 발행 주기 (2026-09-21 §7). 인자: BAG [BAG ...] | — |
| [`job463_tegra.py`](../../debug_log/2026-09-21/jobs/job463_tegra.py) | S5 기준선: tegrastats 로그 요약 (2026-09-21 §7). 인자: tegra_<이름>.log [...] | — |
| [`job464_n0probe.sh`](../../debug_log/2026-09-21/jobs/job464_n0probe.sh) | N0 사전 조사(읽기 전용, sudo 없음): docker/nvidia 런타임, 이미지, 디스크, 네트워크(nvcr.io·github·apt 저장소), JetPack, 전원 모드, 기존 isaac 흔적 | 09-21 9 |
| [`job465_n0probe2.sh`](../../debug_log/2026-09-21/jobs/job465_n0probe2.sh) |  | 09-21 9 |
| [`job466_docs_relink.py`](../../debug_log/2026-09-21/jobs/job466_docs_relink.py) | Docs 폴더 재구성(2026-09-21)에 따른 링크·경로 수정. 인자: REPO_ROOT [MEMORY_DIR] | — |
| [`job467_linkcheck.py`](../../debug_log/2026-09-21/jobs/job467_linkcheck.py) | 리포의 md 상대 링크 존재 검사 (debug_log·로컬 전용 폴더 제외). 인자: REPO_ROOT | — |
| [`job468_n0_setup.sh`](../../debug_log/2026-09-21/jobs/job468_n0_setup.sh) | Phase N0 1단계 (2026-09-21, 사용자 승인): 센서·SLAM·Nav2 내림(base 유지) → git-lfs(sudo) → ~/workspaces/isaac_ros-dev + isaac_ros_common(release-3.2) → I | 09-21 9 |
| [`job469_buildchk.sh`](../../debug_log/2026-09-21/jobs/job469_buildchk.sh) |  | — |
| [`job470_builddiag.sh`](../../debug_log/2026-09-21/jobs/job470_builddiag.sh) |  | — |
| [`job471_buildstart.sh`](../../debug_log/2026-09-21/jobs/job471_buildstart.sh) | 09-21: 첫 시도는 TERM 미설정 → print_color 의 tput 이 set -e 아래서 실패해 즉시 종료. TERM=xterm 으로 재시작. | — |
| [`job472_container.sh`](../../debug_log/2026-09-21/jobs/job472_container.sh) | Phase N0 2단계 (2026-09-21): Isaac ROS Dev 컨테이너를 **상주형**으로 띄우고(run_dev.sh 의 docker run 인자 그대로, -it 대신 -d + sleep) 안에서 nvblox 를 apt 로 설치. | 09-21 9 |
| [`job473_nvblox_run.sh`](../../debug_log/2026-09-21/jobs/job473_nvblox_run.sh) | Phase N0 3단계 (2026-09-21): 호스트 센서 스택(카메라·라이다·EKF·SLAM, Nav2 없음) 위에서 컨테이너의 nvblox_node 를 깊이 전용으로 띄운다. 인자: start\|stop\|status\|log | 09-21 9 · 09-22 1.1 |
| [`job474_n0_measure.py`](../../debug_log/2026-09-21/jobs/job474_n0_measure.py) | N0 정지 측정 (2026-09-21, 계획서 §5.1). 컨테이너 안에서 실행(nvblox_msgs 필요). 인자: NAME SEC [BOX_FRONT_X BOX_CY]  (base_link 기준 상자 전면 x·중심 y, 게이트 감사값) | 09-21 9 |
| [`job475_sensors.sh`](../../debug_log/2026-09-21/jobs/job475_sensors.sh) | N0 용 호스트 스택: 센서(카메라·라이다·컨디셔너·EKF·릴레이) + SLAM 만 (Nav2 없음). job240 과 같은 기동 명령. | 09-21 9 |
| [`job476_cdi.sh`](../../debug_log/2026-09-21/jobs/job476_cdi.sh) |  | — |
| [`job477_nvblox_info.sh`](../../debug_log/2026-09-21/jobs/job477_nvblox_info.sh) |  | — |
| [`job478_boxphys.py`](../../debug_log/2026-09-21/jobs/job478_boxphys.py) | 물리 상자 위치(카메라 원시 점군, Nav2 불필요) — job125 detect_box 와 같은 규칙 (2026-09-21 N0 용). 출력 마지막 줄: 'BX BY N | 09-21 9 |
| [`job479_auditdbg.sh`](../../debug_log/2026-09-21/jobs/job479_auditdbg.sh) |  | — |
| [`job480_hostchk.sh`](../../debug_log/2026-09-21/jobs/job480_hostchk.sh) |  | — |
| [`job481_n0_variants.sh`](../../debug_log/2026-09-21/jobs/job481_n0_variants.sh) | N0 (iv) 복셀 0.03 + 입력 해상도 변형(디시메이션 2 → 320x240, 1 → 640x480). 각 조건: nvblox 재시작 → 15 s 대기 → 슬라이스 20 s 측정 → 통계 블록·tegrastats 5 s. 끝에 dec 4·복셀 0 | — |
| [`job482_nvblox_state.sh`](../../debug_log/2026-09-21/jobs/job482_nvblox_state.sh) |  | — |
| [`job483_n0_variants2.sh`](../../debug_log/2026-09-21/jobs/job483_n0_variants2.sh) | N0 (iv)+입력 해상도 변형, 2 차 (2026-09-21): 1 차(job481)는 재시작한 노드가 깊이 1 프레임 뒤 멈추고 죽어 0 프레임. 원인 후보: pkill -f 가 자기 bash 를 먼저 죽여 옛 노드가 남음·확인 없이 측정. | 09-21 9 |
| [`job484_hostbuild.sh`](../../debug_log/2026-09-21/jobs/job484_hostbuild.sh) | N2~N3 1단계 (2026-09-21): 호스트 ros2_ws 에 nvblox_msgs + nvblox_nav2(+ isaac_ros_common cmake 패키지) 만 소스 빌드 — CUDA 불필요. 호스트 Nav2 가 nvblox 코스트맵 층을  | 09-21 10.1 |
| [`job485_hostbuild2.sh`](../../debug_log/2026-09-21/jobs/job485_hostbuild2.sh) | N2~N3 1단계 2차 (2026-09-21): isaac_ros_common 의 cmake extras 가 CUDA 를 강제(FindCUDA REQUIRED)해 호스트 빌드 실패 → | 09-21 10.1 |
| [`job486_pluginchk.sh`](../../debug_log/2026-09-21/jobs/job486_pluginchk.sh) |  | — |
| [`job488_layer_ab.sh`](../../debug_log/2026-09-21/jobs/job488_layer_ab.sh) | N3 정지 A/B (2026-09-21): 로컬 코스트맵 카메라 층을 stvl\|nvblox 로 바꿔 Nav2 만 재기동 → 로컬 코스트맵의 상자 셀·근거 없는 셀·창·CPU 를 같은 자세에서 비교. 인자: stvl\|nvblox [BX BY] | 09-21 10.2 · 09-21 10.5 |
| [`job489_gridcmp.py`](../../debug_log/2026-09-21/jobs/job489_gridcmp.py) | N3 정지 A/B 보조 (2026-09-21): 로컬 코스트맵(OccupancyGrid)과 nvblox 슬라이스를 base_link 기준 10 cm ASCII 지도로 찍어 어디가 LETHAL/미지인지 본다. 인자: NAME [SLICE=1] | 09-21 10.2 · 09-21 10.3 |
| [`job491_vizgen.py`](../../debug_log/2026-09-21/jobs/job491_vizgen.py) | STVL vs nvblox 로컬 코스트맵 시각화 HTML 생성 (2026-09-21 §10). 입력: grid_stvl_costmap.json, grid_nvblox_costmap.json, grid_nvblox_slice.json (base_link | 09-21 10.3 |
| [`job493_fixfloor.sh`](../../debug_log/2026-09-21/jobs/job493_fixfloor.sh) | N3 결함 수정 (2026-09-21 §10.4~10.5): nvblox_nav2 층 lookupInSlice() 의 슬라이스 인덱스 round → floor. | 09-21 10.5 |
| [`job494_vizgen2.py`](../../debug_log/2026-09-21/jobs/job494_vizgen2.py) | STVL vs nvblox 로컬 코스트맵 시각화 v2 (2026-09-21 §10.5) — 층 결함(round→floor) 수정 후 재캡처용. job491 을 인자화하고 "층 vs 슬라이스" 판(E)과 V1~V4 판정, v1(수정 전) 대비 표를 더했 | 09-21 10.5 |
| [`job497_endstate.sh`](../../debug_log/2026-09-21/jobs/job497_endstate.sh) | Jetson 측 파일(ssh 인라인에 프로세스 이름을 두지 않기 위해): 마감 상태 읽기 전용 확인 | — |
| [`nav2_params_0921nv.yaml`](../../debug_log/2026-09-21/jobs/nav2_params_0921nv.yaml) | Nav2 파라미터 — WT-600 스키드스티어 로버 (dev 플랫폼) | — |
| [`nvblox_n0.yaml`](../../debug_log/2026-09-21/jobs/nvblox_n0.yaml) | nvblox N0 정지 측정용 파라미터 (2026-09-21). 기준: isaac_ros_nvblox release-3.2 nvblox_base.yaml + nvblox_realsense.yaml 을 우리 로버에 맞게. | 09-21 9 · 09-22 2.1 |
| [`nvblox_n0_v03.yaml`](../../debug_log/2026-09-21/jobs/nvblox_n0_v03.yaml) | nvblox N0 정지 측정용 파라미터 (2026-09-21). 기준: isaac_ros_nvblox release-3.2 nvblox_base.yaml + nvblox_realsense.yaml 을 우리 로버에 맞게. | — |
| [`run_deploy_nv.sh`](../../debug_log/2026-09-21/jobs/run_deploy_nv.sh) | nav2_params.yaml 배포(src+install) — CostCritic 교체 (09-18 §17). nav2 재기동 없음(다음 run_mp9prep 이 재기동). 설치본과 diff 로 바뀐 줄만 확인, 기존본 백업. | 09-21 10.1 |
| [`run_drive_nohup.sh`](../../debug_log/2026-09-21/jobs/run_drive_nohup.sh) | 주행 러너 v2 (09-15 교훈): 원격에서 nohup 으로 게이트+주행을 띄우고 로그 파일을 폴링한다 — ssh 가 끊겨도 주행은 기록되고, 재접속 후 이어 읽는다. | 09-18 13.3 · 09-18 17.3 · 09-21 10.1 · … +2 |
| [`run_j434.sh`](../../debug_log/2026-09-21/jobs/run_j434.sh) |  | — |
| [`run_j435g.sh`](../../debug_log/2026-09-21/jobs/run_j435g.sh) |  | — |
| [`run_j435h.sh`](../../debug_log/2026-09-21/jobs/run_j435h.sh) |  | — |
| [`run_j435i.sh`](../../debug_log/2026-09-21/jobs/run_j435i.sh) |  | — |
| [`run_j435j.sh`](../../debug_log/2026-09-21/jobs/run_j435j.sh) |  | — |
| [`run_j435k.sh`](../../debug_log/2026-09-21/jobs/run_j435k.sh) |  | — |
| [`run_j446b.sh`](../../debug_log/2026-09-21/jobs/run_j446b.sh) |  | — |
| [`run_j446c.sh`](../../debug_log/2026-09-21/jobs/run_j446c.sh) |  | — |
| [`run_j446d.sh`](../../debug_log/2026-09-21/jobs/run_j446d.sh) |  | — |
| [`run_j446e.sh`](../../debug_log/2026-09-21/jobs/run_j446e.sh) |  | — |
| [`run_j446f.sh`](../../debug_log/2026-09-21/jobs/run_j446f.sh) |  | — |
| [`run_j451b.sh`](../../debug_log/2026-09-21/jobs/run_j451b.sh) |  | — |
| [`run_j455_probe.sh`](../../debug_log/2026-09-21/jobs/run_j455_probe.sh) | 09-21 시작 점검: Jetson 도달 IP, 가동 시간, Wi-Fi 상태, wifi-mon 이벤트(주말 끊김?), CostCritic YAML 유지, /tmp 러너·bag 잔존, 디스크 | — |
| [`run_j456_wifievent.sh`](../../debug_log/2026-09-21/jobs/run_j456_wifievent.sh) |  | — |
| [`run_j457.sh`](../../debug_log/2026-09-21/jobs/run_j457.sh) |  | — |
| [`run_j458.sh`](../../debug_log/2026-09-21/jobs/run_j458.sh) | 인자: NAME D_FRONT DEC [SEC]. 측정 앞뒤로 realsense·depth_relay CPU 와 EKF 위반 증분도 함께. | 09-21 5 |
| [`run_j459.sh`](../../debug_log/2026-09-21/jobs/run_j459.sh) |  | — |
| [`run_j460.sh`](../../debug_log/2026-09-21/jobs/run_j460.sh) |  | — |
| [`run_j461.sh`](../../debug_log/2026-09-21/jobs/run_j461.sh) |  | — |
| [`run_j462.sh`](../../debug_log/2026-09-21/jobs/run_j462.sh) |  | — |
| [`run_j462b.sh`](../../debug_log/2026-09-21/jobs/run_j462b.sh) |  | — |
| [`run_j464.sh`](../../debug_log/2026-09-21/jobs/run_j464.sh) |  | — |
| [`run_j465.sh`](../../debug_log/2026-09-21/jobs/run_j465.sh) |  | — |
| [`run_j468.sh`](../../debug_log/2026-09-21/jobs/run_j468.sh) |  | — |
| [`run_j469.sh`](../../debug_log/2026-09-21/jobs/run_j469.sh) |  | — |
| [`run_j470.sh`](../../debug_log/2026-09-21/jobs/run_j470.sh) |  | — |
| [`run_j471.sh`](../../debug_log/2026-09-21/jobs/run_j471.sh) |  | — |
| [`run_j472.sh`](../../debug_log/2026-09-21/jobs/run_j472.sh) |  | — |
| [`run_j473.sh`](../../debug_log/2026-09-21/jobs/run_j473.sh) |  | — |
| [`run_j474.sh`](../../debug_log/2026-09-21/jobs/run_j474.sh) | N0 (i)(ii) 측정: 호스트 상자 감사(카메라 점군 → 물리 전면 x·중심 y) → 컨테이너 안 job474 로 ESDF 슬라이스 SEC 초. 인자: NAME [SEC=30] | — |
| [`run_j474b.sh`](../../debug_log/2026-09-21/jobs/run_j474b.sh) | N0 (i)(ii): 컨테이너 안 job474 로 ESDF 슬라이스 측정. 인자: NAME SEC BX BY [TOPIC] | — |
| [`run_j475.sh`](../../debug_log/2026-09-21/jobs/run_j475.sh) |  | — |
| [`run_j476.sh`](../../debug_log/2026-09-21/jobs/run_j476.sh) |  | — |
| [`run_j477.sh`](../../debug_log/2026-09-21/jobs/run_j477.sh) |  | — |
| [`run_j480.sh`](../../debug_log/2026-09-21/jobs/run_j480.sh) |  | — |
| [`run_j481.sh`](../../debug_log/2026-09-21/jobs/run_j481.sh) |  | — |
| [`run_j483.sh`](../../debug_log/2026-09-21/jobs/run_j483.sh) |  | — |
| [`run_j484.sh`](../../debug_log/2026-09-21/jobs/run_j484.sh) |  | — |
| [`run_j485.sh`](../../debug_log/2026-09-21/jobs/run_j485.sh) |  | — |
| [`run_j486.sh`](../../debug_log/2026-09-21/jobs/run_j486.sh) |  | — |
| [`run_j488.sh`](../../debug_log/2026-09-21/jobs/run_j488.sh) | 인자: stvl\|nvblox BX BY | 09-22 2 |
| [`run_j489.sh`](../../debug_log/2026-09-21/jobs/run_j489.sh) |  | — |
| [`run_j490.sh`](../../debug_log/2026-09-21/jobs/run_j490.sh) | 시각화용 원자료: STVL 모드 코스트맵 JSON → nvblox 모드로 전환(+nvblox 기동) → 코스트맵·슬라이스 JSON → STVL 복귀·nvblox 정지 → JSON 회수 | 09-21 10.3 |
| [`run_j492.sh`](../../debug_log/2026-09-21/jobs/run_j492.sh) | 읽기 전용: nvblox_nav2 층의 거리→비용 변환·격자 조회 코드와 슬라이스 origin 규약 확인 (DDS 참여 없음) | — |
| [`run_j492b.sh`](../../debug_log/2026-09-21/jobs/run_j492b.sh) | 읽기 전용: lookupInSlice 구현·슬라이스 origin 계산·절단 기본값 | — |
| [`run_j492c.sh`](../../debug_log/2026-09-21/jobs/run_j492c.sh) | 읽기 전용: 슬라이스 origin 이 픽셀 모서리인지 중심인지 (esdf_slice_conversions.cu) | — |
| [`run_j493.sh`](../../debug_log/2026-09-21/jobs/run_j493.sh) | §10.5: 층 결함(round→floor) 수정·재빌드 → 같은 배치에서 STVL(stvl2) / 수정 nvblox 층(nvfix) 코스트맵·슬라이스 JSON 재캡처 → STVL 복귀·nvblox 정지 → JSON·감사 출력 회수 | 09-21 10.5 |
| [`run_j495.sh`](../../debug_log/2026-09-21/jobs/run_j495.sh) | 읽기 전용: 재빌드된 nvblox_nav2 .so 의 실제 경로·시각과 Nav2 가 로드한 라이브러리 확인 | — |
| [`run_j496.sh`](../../debug_log/2026-09-21/jobs/run_j496.sh) | 마감 상태 확인·정리: 설치 .so 가 build 로의 심볼릭인지, 컨테이너에 nvblox 프로세스가 남았는지(남았으면 job473 stop 으로 정지) | — |
| [`run_j497.sh`](../../debug_log/2026-09-21/jobs/run_j497.sh) |  | — |
| [`run_post3.sh`](../../debug_log/2026-09-21/jobs/run_post3.sh) |  | 09-18 12.2 · 09-18 17.3 · 09-21 6 · … +2 |

## 2026-09-22 (42)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job240_clean.sh`](../../debug_log/2026-09-22/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job254_s4run.sh`](../../debug_log/2026-09-22/jobs/job254_s4run.sh) | S4 1회차 절차: 게이트(중복·보드·통과폭) → 주행 D=1.8 (bag+로그분석) | 09-11 배운 것 · 09-11 절차 (확정) · 09-14 2 · … +3 |
| [`job442_clearwait.sh`](../../debug_log/2026-09-22/jobs/job442_clearwait.sh) | 사람 흔적 셀 제거(09-18): 로컬·전역 코스트맵을 비우고 8 s 동안 현재 센서로 다시 채운다(상자는 카메라 앞이라 곧바로 재마킹) | 09-18 13.3 |
| [`job453_runmeta.sh`](../../debug_log/2026-09-22/jobs/job453_runmeta.sh) | 주행 재현 메타 (2026-09-18 §17): "무엇으로 달렸는지" 를 bag 옆에 남긴다 — 실행 중 노드의 실제 파라미터(job451), 배포 파일 해시, 단계·메모, 기록 토픽. | 09-18 17.3 |
| [`job473_nvblox_run.sh`](../../debug_log/2026-09-22/jobs/job473_nvblox_run.sh) | Phase N0 3단계 (2026-09-21): 호스트 센서 스택(카메라·라이다·EKF·SLAM, Nav2 없음) 위에서 컨테이너의 nvblox_node 를 깊이 전용으로 띄운다. 인자: start [yaml]\|stop\|status\|log | 09-21 9 · 09-22 1.1 |
| [`job488_layer_ab.sh`](../../debug_log/2026-09-22/jobs/job488_layer_ab.sh) | N3 정지 A/B (2026-09-21): 로컬 코스트맵 카메라 층을 stvl\|nvblox 로 바꿔 Nav2 만 재기동 → 로컬 코스트맵의 상자 셀·근거 없는 셀·창·CPU 를 같은 자세에서 비교. 인자: stvl\|nvblox [BX BY] | 09-21 10.2 · 09-21 10.5 |
| [`job489_gridcmp.py`](../../debug_log/2026-09-22/jobs/job489_gridcmp.py) | N3 정지 A/B 보조 (2026-09-21): 로컬 코스트맵(OccupancyGrid)과 nvblox 슬라이스를 base_link 기준 10 cm ASCII 지도로 찍어 어디가 LETHAL/미지인지 본다. 인자: NAME [SLICE=1] | 09-21 10.2 · 09-21 10.3 |
| [`job498_state.sh`](../../debug_log/2026-09-22/jobs/job498_state.sh) | 09-22 시작 상태(읽기 전용): 재부팅 여부, /tmp 스크립트 잔존, 스택 프로세스, 컨테이너, 로컬 plugins, nvblox 포크 diff | 09-22 0 |
| [`job499_container_up.sh`](../../debug_log/2026-09-22/jobs/job499_container_up.sh) | 09-22 재부팅 후 isaac 컨테이너 복구: 정지된 컨테이너가 남아 있으면 docker start(안의 apt nvblox 보존), 없으면 job472 로 재생성(apt 재설치, 수 분) | 09-22 0 |
| [`job501_trunc_ab.sh`](../../debug_log/2026-09-22/jobs/job501_trunc_ab.sh) | 09-22 §1 절단 거리 A/B (Jetson 측): 같은 배치에서 STVL 캡처 → nvblox 절단 4.0(t4) → 절단 2.0(t2) 순으로 로컬 코스트맵·슬라이스 JSON(job489)·감사(job248)·N0 계측(job474, 컨테이너) | 09-22 1.1 |
| [`job502_trunc_eval.py`](../../debug_log/2026-09-22/jobs/job502_trunc_eval.py) | 09-22 §1 절단 A/B 평가: STVL(stvl3) / t4 / t2 의 job489 JSON(base_link, 5 cm)을 공통 격자에 스냅해 T1~T4·T6 를 센다(T5 는 job474·tegrastats 출력에서 읽음). | 09-22 1.1 |
| [`job503_vizgen3.py`](../../debug_log/2026-09-22/jobs/job503_vizgen3.py) | 09-22 §1 절단 거리 A/B 시각화: STVL(stvl3) / nvblox 절단 4.0(t4) / 절단 2.0(t2) 로컬 코스트맵을 같은 배치에서 셀 단위로 비교하는 HTML. | — |
| [`job504_quick.sh`](../../debug_log/2026-09-22/jobs/job504_quick.sh) | 보드 리셋 직후 빠른 확인(읽기 전용): 에이전트 세션·wheel_odom·스택 프로세스·prep 진행 중인 job 들 | — |
| [`job505_modeN_gate.sh`](../../debug_log/2026-09-22/jobs/job505_modeN_gate.sh) | 절차 v2.0 게이트 J·K·L (모드 N 전용, 09-22): nvblox 노드 1 개·깊이 ≥10 Hz·ESDF ≥9 Hz·지연 ≤0.15 s, 로컬 plugins 실효값 = nvblox_layer, 슬라이스 상자 커버(≥0 셀 ≥8 — 09-22 | 09-22 2 |
| [`job506_decay.py`](../../debug_log/2026-09-22/jobs/job506_decay.py) | nvblox 감쇠 정지 측정 (09-22 §2): 슬라이스에서 상자 구역(base x 0.9~1.5, y −0.35~+0.15)의 ≤0 셀 수·최소 거리·미지/자유 셀 수를 1 초마다 찍는다. | 09-22 2.1 |
| [`job506_decay.sh`](../../debug_log/2026-09-22/jobs/job506_decay.sh) | 09-22 감쇠 정지 측정: nvblox(YAML) 시작 → 32 s 적분 → 깊이 스트림 차단(enable_depth false) → 상자 셀 소실 시각 기록(job506_decay.py, 호스트) → 깊이 복구 → nvblox 정지. 인자: YAM | 09-22 2.1 |
| [`job508_modeN.sh`](../../debug_log/2026-09-22/jobs/job508_modeN.sh) | 09-22 N4 팔 N2 준비(Jetson 측, prep 뒤에 실행): nvblox(절단 2.0·감쇠 0.99) 시작 → 로컬 코스트맵을 nvblox 층으로 전환(Nav2 만 재기동) → 클리어·8 s 재관측 → 게이트 J·K·L. 인자: NAME B | — |
| [`job511_modeS.sh`](../../debug_log/2026-09-22/jobs/job511_modeS.sh) | 09-22 N4 팔 S 준비(Jetson 측, prep 뒤): 로컬 코스트맵을 STVL 층으로 복귀(Nav2 만 재기동) → nvblox 정지 → 클리어·8 s 재관측 → plugins 실효값 확인. 인자: BX BY | 09-22 3 |
| [`job512_trajviz.py`](../../debug_log/2026-09-22/jobs/job512_trajviz.py) | N4 주행 A/B 궤적 시각화 (09-22): 러너 csv(fwd, lat, clear_geo, lc_box)로 S 2 회·N2 3 회의 평면 궤적(base 출발 기준 전진 x·횡 y)과 코스트맵 여유 표를 한 페이지에. | — |
| [`job513_verify.sh`](../../debug_log/2026-09-22/jobs/job513_verify.sh) | N6-0 검증(Jetson 측, 2026-09-22): rover_navigation 재빌드 → V1 nvblox 기본 기동·게이트 J·K·L → V2 launch 종료 시 노드 정리 → V3 camera_layer:=stvl → V4 컨테이너 정지  | 09-22 4.1 |
| [`job514_trapdiag.sh`](../../debug_log/2026-09-22/jobs/job514_trapdiag.sh) | N6-0 V2 진단: 래퍼(nvblox_up.sh)가 TERM/INT 에 반응하는지 — launch 아래서 뜬 래퍼와 수동 실행 래퍼를 대조 | 09-22 4.1 |
| [`job516_v5chk.sh`](../../debug_log/2026-09-22/jobs/job516_v5chk.sh) |  | — |
| [`job517_wrapchk.sh`](../../debug_log/2026-09-22/jobs/job517_wrapchk.sh) |  | — |
| [`job518_g1g2.sh`](../../debug_log/2026-09-22/jobs/job518_g1g2.sh) | N6-1 정지 검증(Jetson, 2026-09-22): 현재 모드에서 G1(전역·로컬 코스트맵 상자 셀, 감사)·G2(CPU: depth_relay·nvblox·controller·planner, STVL 갱신 유무)를 잰다. 인자: NAME BX  | 09-22 5.1 |
| [`job522_goalprobe.py`](../../debug_log/2026-09-22/jobs/job522_goalprobe.py) | 목표 부근(base x 1.5~2.3, \|y\|<0.45) 에 무엇이 있나: 라이다 점·카메라 깊이 점·nvblox 슬라이스·전역/로컬 코스트맵을 한 번에 (2026-09-22 N6-1 G3 게이트 G1 실패 진단). 로버 정지 가정. | 09-22 5.1 |
| [`job526_parmchk.sh`](../../debug_log/2026-09-22/jobs/job526_parmchk.sh) |  | 09-22 5.2 |
| [`job528_dynchk.sh`](../../debug_log/2026-09-22/jobs/job528_dynchk.sh) | 읽기 전용: nvblox 3.2 의 동적/사람 분리 모드 설정과 필요 입력·토픽 확인 | — |
| [`nvblox_n0_t2.yaml`](../../debug_log/2026-09-22/jobs/nvblox_n0_t2.yaml) | 09-22 절단 거리 A/B 변형: nvblox_n0.yaml 과 truncation 4.0 → 2.0 만 다름 | 09-22 0 · 09-22 2 |
| [`nvblox_n0_t2d99.yaml`](../../debug_log/2026-09-22/jobs/nvblox_n0_t2d99.yaml) | 09-22 절단 거리 A/B 변형: nvblox_n0.yaml 과 truncation 4.0 → 2.0 만 다름 | 09-22 2.1 |
| [`run_j498.sh`](../../debug_log/2026-09-22/jobs/run_j498.sh) |  | — |
| [`run_j499.sh`](../../debug_log/2026-09-22/jobs/run_j499.sh) | 09-22: 09-21 세트 + 절단 A/B 파일 재전송 → 컨테이너 복구 | 09-28 §0 |
| [`run_j501.sh`](../../debug_log/2026-09-22/jobs/run_j501.sh) | 09-22 §1 절단 A/B 러너(PC): job501 전송·실행 → JSON·감사 출력 회수. 인자: BX BY | 09-22 1.1 |
| [`run_j504.sh`](../../debug_log/2026-09-22/jobs/run_j504.sh) |  | — |
| [`run_j506.sh`](../../debug_log/2026-09-22/jobs/run_j506.sh) |  | — |
| [`run_j508.sh`](../../debug_log/2026-09-22/jobs/run_j508.sh) | PC 러너: N2 준비(job508) — 인자: NAME BX BY [YAML] | — |
| [`run_j509_analyze.sh`](../../debug_log/2026-09-22/jobs/run_j509_analyze.sh) | 09-22 N4 회차 bag 분석 러너(PC): 인자 NAME EPOCH(bt_navigator 'Begin navigating' 시각). Jetson /tmp/bag_<NAME> 에 대해 job416(코스트맵 여유)·job446(경로 분해)·job4 | 09-22 3 |
| [`run_j513_deploy.sh`](../../debug_log/2026-09-22/jobs/run_j513_deploy.sh) | N6-0 배포·검증 러너(PC, 2026-09-22): rover_navigation 의 launch/·scripts/·config/nvblox_local.yaml·CMakeLists 를 Jetson 소스에 넣고 colcon 빌드 → 검증 시나리오 V | 09-22 4.1 |
| [`run_j518.sh`](../../debug_log/2026-09-22/jobs/run_j518.sh) | N6-1 정지 검증 러너(PC): 현재(모드 N, prep 직후) → G1·G2 측정 → 모드 S 로 전환(job488 stvl, Nav2 만) → 같은 측정 → 모드 N 복귀. JSON 회수. 인자: BX BY | 09-22 5.1 |
| [`run_j519_deploy2.sh`](../../debug_log/2026-09-22/jobs/run_j519_deploy2.sh) | N6-1 배포(PC, 2026-09-22): nav2_params.yaml(전역 nvblox_layer 블록)·navigation.launch.py(전역 plugins 전환)·depth_relay.py(구독자 없으면 생략) → Jetson 소스 → c | 09-22 5.1 |
| [`run_j523.sh`](../../debug_log/2026-09-22/jobs/run_j523.sh) | N6-1 nvblox yaml 재배포 → Nav2(nvblox) 재기동(래퍼가 새 yaml 로 노드 재시작) → 목표 부근 탐침(job522)·게이트 J·K·L·목표 여유(job377 2.0 0.0). 인자: BX BY [확인할 yaml 문자열] | 09-22 5.2 |
| [`run_j524.sh`](../../debug_log/2026-09-22/jobs/run_j524.sh) | 재탐침만: job522(목표 부근) + 게이트 J·K·L + 목표 여유(job377 D LAT). 인자: BX BY | — |
| [`run_jx.sh`](../../debug_log/2026-09-22/jobs/run_jx.sh) | 범용 러너(09-22): 새 scratchpad 의 Jetson 측 파일 하나를 CRLF 제거 후 전송·실행. 인자: <job파일> [인자…] | 09-23 5 |

## 2026-09-23 (32)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job125_avoid3.py`](../../debug_log/2026-09-23/jobs/job125_avoid3.py) | 회피 주행 계측판 (2026-09-09) — job92 의 여유 측정이 틀렸던 것을 고친다. | 09-09 순서를 하나 앞에 둬야 하는 이유 — 미해결 모순 · 09-10 원인 — 클러스터링 없는 median (job125_avoid3.py d · 09-11 지표 오염 — 관찰이 맞았다 · … +5 |
| [`job505_modeN_gate.sh`](../../debug_log/2026-09-23/jobs/job505_modeN_gate.sh) | 절차 v2.0 게이트 J·K·L (모드 N 전용, 09-22): nvblox 노드 1 개·깊이 ≥10 Hz·ESDF ≥9 Hz·지연 ≤0.15 s, 로컬 plugins 실효값 = nvblox_layer, 슬라이스 상자 커버(≥0 셀 ≥8 — 09-22 | 09-22 2 |
| [`job529_wifi_collect.sh`](../../debug_log/2026-09-23/jobs/job529_wifi_collect.sh) | 읽기 전용: 09-18 설치한 wifi-mon 기록과 syslog 의 무선 이벤트 회수 (2026-09-23 끊김 분석) | 09-23 0.1 |
| [`job530_wifi_boot.sh`](../../debug_log/2026-09-23/jobs/job530_wifi_boot.sh) | 읽기 전용: 오늘 부팅 직후(NTP 전, 1970 타임스탬프) 구간의 무선 이벤트 — mon.log·wpa_debug·syslog, 그리고 AP 재스캔 | 09-23 0.1 |
| [`job531_pcl_toggle.sh`](../../debug_log/2026-09-23/jobs/job531_pcl_toggle.sh) | N6-2 C1 정지 A/B: 모드 N 에서 realsense 점군 생성 끄기 — CPU(realsense·릴레이·nvblox)·점군/깊이 Hz·nvblox 깊이 콜백 비교, 끝에 복구 | 09-23 3 |
| [`job532_slice_h.sh`](../../debug_log/2026-09-23/jobs/job532_slice_h.sh) | N6-2 H1 정지 측정(Jetson): 슬라이스 최소 높이 0.03 vs 0.06(통합 1.4 고정). 변형 yaml 을 설치본 위에 잠시 덮고 Nav2(nvblox) 재기동 → 3 표본(게이트 L 상자 셀·목표 부근 유령·상자 왼쪽 가장자리 차)  | 09-23 4 |
| [`job534_netprep.sh`](../../debug_log/2026-09-23/jobs/job534_netprep.sh) | 읽기 전용: 고정 IP(DHCP 예약) 복귀·충돌 감지 설정 전 확인 — wifi_mon.sh 내용, arping/tcpdump 유무, NM 프로파일의 ipv4 설정, 현재 점군 파라미터 | — |
| [`job535_net_fixed.sh`](../../debug_log/2026-09-23/jobs/job535_net_fixed.sh) | 2026-09-23 사용자 지시: 고정 IP(공유기 DHCP 예약) 방식으로 WEB_DEV_5G 로 되돌리고, IP 충돌을 잡도록 설정. sudo 사용(비밀번호는 표준입력). | 09-23 5 |
| [`job536_moncheck.sh`](../../debug_log/2026-09-23/jobs/job536_moncheck.sh) | wifi-mon ARP 중복 검사 패치가 실제 적용됐는지 확인·미적용이면 적용(sudo) | — |
| [`job539_dropchk.sh`](../../debug_log/2026-09-23/jobs/job539_dropchk.sh) |  | — |
| [`job540_trace.sh`](../../debug_log/2026-09-23/jobs/job540_trace.sh) | 끊김 중 온보드 기록(읽기 전용): 1) 끊김 시각대 로그 요약(job539) 2) 2 s 마다 IP·링크·게이트웨이 핑·ARP 테이블 게이트웨이 MAC 을 30 분간 | 09-23 11 |
| [`job541_fetch.sh`](../../debug_log/2026-09-23/jobs/job541_fetch.sh) |  | — |
| [`job542_dropwin.sh`](../../debug_log/2026-09-23/jobs/job542_dropwin.sh) | 11:55~12:07 끊김 창 전체: mon.log LINK/EVENT/ARP_DUP, wpa CTRL-EVENT·reason, NM 상태 변화 이유, 커널 | — |
| [`job543_mon.sh`](../../debug_log/2026-09-23/jobs/job543_mon.sh) |  | — |
| [`job544_drop2.sh`](../../debug_log/2026-09-23/jobs/job544_drop2.sh) |  | — |
| [`job545_slipyaw.py`](../../debug_log/2026-09-23/jobs/job545_slipyaw.py) | 목표 도착 뒤 제자리 회전 중 트랙 미끄러짐 검증 (09-23 n62b, 사용자 관찰): bag 에서 1 s 구간별로 | 09-23 12.1 |
| [`job546_scanrot.py`](../../debug_log/2026-09-23/jobs/job546_scanrot.py) | 미끄러짐 검증 2 (09-23 n62b): 라이다 스캔만으로 실제 몸체 회전을 잰다(휠·IMU·SLAM 과 독립). | 09-23 12.1 |
| [`job547_cpuidle.sh`](../../debug_log/2026-09-23/jobs/job547_cpuidle.sh) |  | — |
| [`job549_cond.sh`](../../debug_log/2026-09-23/jobs/job549_cond.sh) |  | 09-23 15 |
| [`job550_f0run.py`](../../debug_log/2026-09-23/jobs/job550_f0run.py) | F0 코스 확장 러너 (2026-09-23): 상자 코스와 무관한 연속 목표 주행 + 왕복 복귀 오차 계측. | 09-23 16 · 09-28 §12 · 09-28 §16 · … +5 |
| [`job551_f0drive.sh`](../../debug_log/2026-09-23/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`job552_goalyaw.py`](../../debug_log/2026-09-23/jobs/job552_goalyaw.py) | 목표 도착 뒤 최종 heading 확인 (09-23): bag 끝(목표 도달 시점)의 map yaw·EKF(odom) yaw 와 출발 yaw 의 차, 그리고 라이다 스캔 상관으로 잰 출발→도착 실제 회전. | 09-23 §17 |
| [`job553_yawseries.py`](../../debug_log/2026-09-23/jobs/job553_yawseries.py) | 목표 도달 전후 yaw 시계열 (09-23): map yaw·EKF yaw·지령 ω 를 'Reached the goal' 전 6 s ~ 후 3 s, 0.5 s 간격으로. | 09-23 §17 |
| [`job556_abortmap.py`](../../debug_log/2026-09-23/jobs/job556_abortmap.py) | F0-a 복귀 중단 분석 (09-23): 지정 시각들에서 로컬 코스트맵(odom) 치명 셀(OccupancyGrid 100 = LETHAL, 99 = 내접)과 차체 풋프린트(0.5×0.33) 최소 거리·위치, | 09-23 §18 |
| [`job557_boxdrift.py`](../../debug_log/2026-09-23/jobs/job557_boxdrift.py) | F0-a 상자 이동 검증 (09-23): 3 s 간격으로 로컬(odom)·전역(map) 코스트맵의 상자 LETHAL(100) 셀 범위를 map 좌표로, 그리고 map→odom. | 09-23 §18.1 |
| [`job558_cause.py`](../../debug_log/2026-09-23/jobs/job558_cause.py) | F0-a 중단 원인 분석 (09-23) — bag_f0a1 만으로. | 09-23 §19 |
| [`job559_fpframes.py`](../../debug_log/2026-09-23/jobs/job559_fpframes.py) | F0-a 원인 2 보강 (09-23): 복귀 구간 로컬 코스트맵 **매 프레임**에서 그 순간 자세의 풋프린트(패딩 0.01) 최대 비용과 | 09-23 §19 |
| [`run_f0.sh`](../../debug_log/2026-09-23/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_j535.sh`](../../debug_log/2026-09-23/jobs/run_j535.sh) | PC: 네트워크 전환 실행 → 90 s 동안 두 IP 핑 → 붙은 쪽에서 상태·NM 로그 확인 | 09-23 5 |
| [`run_j540.sh`](../../debug_log/2026-09-23/jobs/run_j540.sh) |  | — |
| [`run_jx.sh`](../../debug_log/2026-09-23/jobs/run_jx.sh) | 범용 러너(09-22): 새 scratchpad 의 Jetson 측 파일 하나를 CRLF 제거 후 전송·실행. 인자: <job파일> [인자…] | 09-23 5 |
| [`run_xfer_all_h.sh`](../../debug_log/2026-09-23/jobs/run_xfer_all_h.sh) | 재부팅 후 /tmp 작업 스크립트 일괄 재전송 (2026-09-10 갱신) | 09-23 0 · 09-23 2 · 09-28 §0 |

## 2026-09-28 (24)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job550_f0run.py`](../../debug_log/2026-09-28/jobs/job550_f0run.py) | F0 코스 확장 러너 (2026-09-23): 상자 코스와 무관한 연속 목표 주행 + 왕복 복귀 오차 계측. | 09-23 16 · 09-28 §12 · 09-28 §16 · … +5 |
| [`job562_spin.py`](../../debug_log/2026-09-28/jobs/job562_spin.py) | 제자리 180° 회전 시험 (2026-09-28, 09-23 §20.3): 스키드스티어 제자리 회전 중 차체 중심이 옆으로 밀리는 양을 잰다. | 09-28 §1 · 09-29 §3 |
| [`job564_spinclear.py`](../../debug_log/2026-09-28/jobs/job564_spinclear.py) | 회전 시험 전 주변 여유 확인: 라이다 스캔을 차체 좌표로 바꿔 8 방위별 최근접 거리(차체 중심 기준)와 회전 반경(0.30 m) 밖 여유. | 09-28 §2 |
| [`job565_spindrive.sh`](../../debug_log/2026-09-28/jobs/job565_spindrive.sh) | 제자리 회전 시험 래퍼(Jetson, 2026-09-28): 게이트 A(프로세스)·B(보드)·C(SLAM) → bag → job562 → 메타(job453). | — |
| [`job567_scanmatch.py`](../../debug_log/2026-09-28/jobs/job567_scanmatch.py) | 제자리 회전 시험 분석 (2026-09-28): SLAM 없이 **정지 구간 스캔끼리 직접 정합(ICP)** 해서 회전별 차체 중심 이동을 잰다. | 09-28 3.2 · 09-29 §3 |
| [`job580_slamreplay.py`](../../debug_log/2026-09-28/jobs/job580_slamreplay.py) | B1 오프라인 검증 재생기 (2026-09-28 §7): 회전 시험 bag 을 **별도 ROS 도메인**에서 sim time 으로 재생해 새로 띄운 slam_toolbox 에 먹이고, | 09-28 §8 |
| [`job581_b1.sh`](../../debug_log/2026-09-28/jobs/job581_b1.sh) | B1 오프라인 검증 래퍼(Jetson, 2026-09-28): 도메인 42 에서 slam_toolbox(use_sim_time) 를 설정별로 띄우고 job580 으로 bag 재생. | 09-28 §8 |
| [`job594_condab.py`](../../debug_log/2026-09-28/jobs/job594_condab.py) | 컨디셔너 V1 출력 동일성 (2026-09-28 §11): 원시 입력 bag(/camera/camera/imu, /wheel_odom)을 **도메인 42** 에서 1 배속 재생해 | — |
| [`job595_condab.sh`](../../debug_log/2026-09-28/jobs/job595_condab.sh) | 컨디셔너 V1 래퍼(Jetson, 2026-09-28 §11). 모드: | — |
| [`job598_conddet.py`](../../debug_log/2026-09-28/jobs/job598_conddet.py) | 컨디셔너 V1 결정적 대조 (2026-09-28 §11): Python 판 노드를 **DDS 없이** 콜백 직접 호출로 bag 전체(누락 0)에 돌려 출력을 만들고, | 09-28 §11 |
| [`job603_f0a3.py`](../../debug_log/2026-09-28/jobs/job603_f0a3.py) | f0a3 판정 보조 (2026-09-28 §14): bag 에서 | — |
| [`job606_rearclear.py`](../../debug_log/2026-09-28/jobs/job606_rearclear.py) | f0a3 관찰 1 확인 (2026-09-28 §15): 목표 2 초반 후진·좌회전 동안 차체(패딩 없는 0.25×0.165)와 상자 사이 거리. | 09-28 §15 |
| [`job610_pathtest.py`](../../debug_log/2026-09-28/jobs/job610_pathtest.py) | f0a4 'p' 실패 진단(09-28): compute_path_to_pose 를 직접 불러 상태·경로 길이·오류를 출력(로버는 움직이지 않음). | 09-28 §18 |
| [`job613_pathyaw.py`](../../debug_log/2026-09-28/jobs/job613_pathyaw.py) | 경로 끝 방향 조회(단독 프로세스, 2026-09-28 §20): 현재 위치 → (GX, GY) 경로를 planner(GridBased)에서 받아 끝 0.3 m 구간 방향(rad)을 출력. | 09-28 §20 · 10-13 §4 · 10-21 §3 |
| [`job618_straight.py`](../../debug_log/2026-09-28/jobs/job618_straight.py) | 직진 전·후진 시험 (2026-09-28 §23, A2·A3): 같은 거리를 앞으로 갔다가 뒤로 돌아오며 | 09-28 §23 |
| [`job619_straightdrive.sh`](../../debug_log/2026-09-28/jobs/job619_straightdrive.sh) | 직진 전·후진 시험 래퍼(Jetson, 2026-09-28 §23): 게이트 A·B·C → bag → job618 → 메타(job453). | — |
| [`job620_straightscan.py`](../../debug_log/2026-09-28/jobs/job620_straightscan.py) | [job620 = job567 의 직진판, 09-28 §23: 구간 = \|v\| 또는 \|ω\| 지령, 휠 적분 거리 추가] | 09-28 §23 |
| [`job623_straightbag.py`](../../debug_log/2026-09-28/jobs/job623_straightbag.py) | 직진 전·후진 분석 (2026-09-28 §23, bag 만으로): | — |
| [`job626_icrfit.py`](../../debug_log/2026-09-28/jobs/job626_icrfit.py) | B2 ICR 식별 (2026-09-28 §26, PC 에서 실행): 회전 시험 스캔 정합 출력에서 회전별 (중심 이동 d, 회전각 θ)를 읽어 | 09-28 §26 |
| [`run_f0.sh`](../../debug_log/2026-09-28/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_jn.sh`](../../debug_log/2026-09-28/jobs/run_jn.sh) | 범용 러너(09-28, 현재 스크래치패드 기준 — 옛 82ce61d4 폴더 소실 대체): $1 = 스크립트 파일명, 나머지 = 인자. 환경 JETSON_HOST, JX_TIMEOUT | 09-28 3.3 · 10-07 §1.0 · 10-08 §5 · … +3 |
| [`run_spin.sh`](../../debug_log/2026-09-28/jobs/run_spin.sh) | 회전 시험 PC 러너(09-28): 전송(재시도 3) → job565 를 setsid nohup 으로 기동 → 로그 폴링 → 산출물 회수 | 09-29 §3 |
| [`run_straight.sh`](../../debug_log/2026-09-28/jobs/run_straight.sh) | 회전 시험 PC 러너(09-28): 전송(재시도 3) → job565 를 setsid nohup 으로 기동 → 로그 폴링 → 산출물 회수 | 09-28 §23 |
| [`slam_toolbox_rover_fork.patch`](../../debug_log/2026-09-28/jobs/slam_toolbox_rover_fork.patch) |  | 09-28 §9 |

## 2026-09-29 (49)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job240_clean.sh`](../../debug_log/2026-09-29/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job627_ekfreplay.py`](../../debug_log/2026-09-29/jobs/job627_ekfreplay.py) | B2·B3 오프라인 검증 재생기 (2026-09-28 §27): 회전 시험 bag 의 /wheel_odom·/imu/data·/tf_static 을 **도메인 42** 에서 sim time 으로 재생, | 09-28 §27 · 09-29 §1 |
| [`job628_b2ab.sh`](../../debug_log/2026-09-29/jobs/job628_b2ab.sh) | (EKF 노드 이름은 ekf.yaml 키와 같게 ekf_filter_node 유지 — 도메인 42 라 라이브와 안 섞임) | 09-28 §27 · 09-29 §1 |
| [`job630_b2ab_all.sh`](../../debug_log/2026-09-29/jobs/job630_b2ab_all.sh) | B2·B3 오프라인 A/B 일괄(Jetson, 09-28 §27): 네트워크가 끊겨도 계속 돌도록 setsid nohup 으로 띄워 /tmp/b2ab_all.txt 에 쓴다. | 09-28 §27 · 09-29 §1 |
| [`job631_bagprep.sh`](../../debug_log/2026-09-29/jobs/job631_bagprep.sh) | 09-29: 재부팅으로 사라진 회전 bag 을 /tmp 에 다시 풀기. 인자 없음(/tmp/bag_*.tgz 를 푼다) | — |
| [`job632_b2ab_eval.py`](../../debug_log/2026-09-29/jobs/job632_b2ab_eval.py) | B2·B3 오프라인 A/B 판정 (2026-09-29 §1): job630 출력(b2ab_all.txt)을 읽어 회전마다 | 09-29 §1.1 |
| [`job635_build_b23.sh`](../../debug_log/2026-09-29/jobs/job635_build_b23.sh) | 09-29 §3: ekf.launch.py(icr·rot_cov 인자) 배포 후 rover_bringup 빌드·확인 | — |
| [`job637_scan_l12.sh`](../../debug_log/2026-09-29/jobs/job637_scan_l12.sh) | 09-29 §3: L1·L2 bag 을 정지 스캔 직접 정합(job567)으로 분석 — 정답(실제 중심 이동) | — |
| [`job638_l_eval.py`](../../debug_log/2026-09-29/jobs/job638_l_eval.py) | 09-29 §3 판정: L1·L2 회전별 EKF(B2·B3 켬)·SLAM 이동 vs 스캔 직접 정합(정답). 값은 j636(러너 출력)·j637(스캔 정합) 원문에서 옮김(cm). | — |
| [`job639_nearest.py`](../../debug_log/2026-09-29/jobs/job639_nearest.py) | 09-29 §3.2: L2 회전 2 안전 정지 때 가장 가까운 라이다 점이 **바닥(map) 어디**였는지, 그리고 시작 때 여유 측정의 | 09-29 §3.2 |
| [`job640_f0csv.py`](../../debug_log/2026-09-29/jobs/job640_f0csv.py) | F0-a 절차 v2.3 §7 판정 계산 (2026-09-29, 09-28 j617 계산을 파일로 남김): 러너 csv → 목표별 xy 진입→끝 시간·ω 부호 바뀜, | 09-29 §4.1 |
| [`job642_b2_vs_slam.py`](../../debug_log/2026-09-29/jobs/job642_b2_vs_slam.py) | 09-29 §5: f0a7 에서 map→odom 누적 보정이 f0a6 의 2.2 배가 된 원인 — B2 가 odom 에 더한 이동과 SLAM 보정(map→odom 변화)을 구간별로 대조. | 09-29 §5 |
| [`job643_b2slam_run.sh`](../../debug_log/2026-09-29/jobs/job643_b2slam_run.sh) | 09-29 §5: f0a6(로컬에서 올린 사본)·f0a7 bag 으로 B2 추가량 vs SLAM 보정 대조(job642) | — |
| [`job644_platform.sh`](../../debug_log/2026-09-29/jobs/job644_platform.sh) | 09-29 §8: JetPack·L4T·CUDA·TensorRT 버전, 컨테이너 Isaac ROS 패키지 버전, 영상 경로(누가 어디서 도나) 확인 | 09-29 §8 |
| [`job645_vslam_pre.sh`](../../debug_log/2026-09-29/jobs/job645_vslam_pre.sh) | 09-29 §9 준비: 컨테이너 cuVSLAM 노드·파라미터, realsense_splitter 유무, 호스트 realsense 드라이버 버전 | — |
| [`job646_vslam_up.sh`](../../debug_log/2026-09-29/jobs/job646_vslam_up.sh) | 09-29 §9: 주행 스택을 내리고(base 유지) 카메라를 cuVSLAM 설정(IR 스테레오·프로젝터 끔)으로 띄운 뒤 컨테이너에서 cuVSLAM 3.2 기동 | — |
| [`job647_vslam_measure.py`](../../debug_log/2026-09-29/jobs/job647_vslam_measure.py) | 09-29 §9 V1: cuVSLAM 출력 측정 (컨테이너 안에서 실행 — VisualSlamStatus 메시지 정의가 거기 있음). | — |
| [`job648_vslam_down.sh`](../../debug_log/2026-09-29/jobs/job648_vslam_down.sh) | 09-29 §9: 단독 확인 정리 — cuVSLAM·전용 카메라 종료(원래 스택은 다음 prep 으로 복귀) | — |
| [`job649_vslam_v1.sh`](../../debug_log/2026-09-29/jobs/job649_vslam_v1.sh) | 09-29 §9 V1: 컨테이너에서 job647 측정(DUR·LABEL) + 같은 시간 부하(top·tegrastats) 기록 | — |
| [`job650_vostate.sh`](../../debug_log/2026-09-29/jobs/job650_vostate.sh) | 09-29 §9: VisualSlamStatus 의 vo_state 정의 확인 | — |
| [`job651_splitter_chk.sh`](../../debug_log/2026-09-29/jobs/job651_splitter_chk.sh) | 09-29 §10: 프로젝터 번갈이(emitter_on_off) 경로 준비물 확인 — 컨테이너의 splitter 노드, nvblox 예제의 realsense 설정, 드라이버 파라미터 | — |
| [`job652_splitter_apt.sh`](../../debug_log/2026-09-29/jobs/job652_splitter_apt.sh) | 09-29 §10: realsense_splitter 설치 가능 여부, emitter_flashing 예제 설정 원문 | — |
| [`job653_depth_emit.py`](../../debug_log/2026-09-29/jobs/job653_depth_emit.py) | 09-29 §10 M1: 프로젝터 켬/끔 깊이 비교. /camera/camera/depth/image_rect_raw(16UC1 mm) + camera_info 를 N 프레임 모아 | 09-29 §10.1 |
| [`job654_emit_m12.sh`](../../debug_log/2026-09-29/jobs/job654_emit_m12.sh) | 09-29 §10: M1(프로젝터 켬/끔 깊이) → M2(번갈이 60 fps 실현성). cuVSLAM·전용 카메라를 먼저 내린다. | 09-29 §10.1 |
| [`job655_mapdump.py`](../../debug_log/2026-09-29/jobs/job655_mapdump.py) | 09-29 §12: F0 나머지 코스 계획용 — bag 의 마지막 /map(OccupancyGrid)을 npz 로 저장(해상도·원점·격자). | 09-29 §12 |
| [`job656_mapdump_run.sh`](../../debug_log/2026-09-29/jobs/job656_mapdump_run.sh) | 09-29 §12: f0a7 bag 의 마지막 지도 추출 | — |
| [`job657_prep_f0b.sh`](../../debug_log/2026-09-29/jobs/job657_prep_f0b.sh) | 09-29 §12.1 F0-b prep: nvblox 컨테이너 확인 → job240(기본 스택, B2·B3 끔) → 컨디셔너 파라미터 확인 | — |
| [`job658_pathcheck.py`](../../debug_log/2026-09-29/jobs/job658_pathcheck.py) | 09-29 §12.1 F0-b 출발 전 점검: GridBased(NavFn)에게 (0,0)→(5.5,−2.2) 경로를 물어 길이·문 통과 여부를 본다(주행 없음). | — |
| [`job659_prestart.sh`](../../debug_log/2026-09-29/jobs/job659_prestart.sh) | 09-29 §12.1 출발 전: 컨디셔너 파라미터(긴 대기) + 경로 점검 | — |
| [`job660_clearance.py`](../../debug_log/2026-09-29/jobs/job660_clearance.py) | 09-29 §12.2 B-b 여유: 주행 중(목표 진행 구간) 라이다 점 ↔ 차체 외곽(0.50 × 0.33 m 직사각, base_link 중심) 최소 거리. | 09-29 §12.2 |
| [`job661_clear_run.sh`](../../debug_log/2026-09-29/jobs/job661_clear_run.sh) | 09-29 §12.2 f0b1 여유 계산 | — |
| [`job663_cable.py`](../../debug_log/2026-09-29/jobs/job663_cable.py) | 09-29 §12.3 W3 부근 전선 밟기 영향 (사용자 관찰: "W3 목적지 위치에 긴 전선이 있어 밟으면서 흔들림·오차"). | 09-29 §12.3 |
| [`job664_cable_run.sh`](../../debug_log/2026-09-29/jobs/job664_cable_run.sh) | 09-29 §12.3 전선 밟기 영향 분석 | — |
| [`job665_prestart2.sh`](../../debug_log/2026-09-29/jobs/job665_prestart2.sh) |  | — |
| [`job667_f0b2_anal.sh`](../../debug_log/2026-09-29/jobs/job667_f0b2_anal.sh) | 09-29 §12.5 f0b2 여유·전선 분석 | — |
| [`job668_stuckscan.py`](../../debug_log/2026-09-29/jobs/job668_stuckscan.py) | 09-29 §13 G3: bag 에 남은 stuck_monitor 판정(/rover/stuck, 판정 때만 발행) 전수 조사. | 09-29 §13.1 |
| [`job669_stuck_all.sh`](../../debug_log/2026-09-29/jobs/job669_stuck_all.sh) | 09-29 §13 G3: bag 풀기 후 stuck 판정 전수 조사 | — |
| [`job670_stuck_offline.py`](../../debug_log/2026-09-29/jobs/job670_stuck_offline.py) | 09-29 §13 G3: stuck_monitor 판정 로직을 bag 시간으로 재생하는 오프라인 평가기(기존 OLD / 수정 NEW 비교). | 09-29 §13.1 |
| [`job671_stuck_offline_run.sh`](../../debug_log/2026-09-29/jobs/job671_stuck_offline_run.sh) | 09-29 §13 G3: stuck_monitor 오프라인 재생 OLD/NEW | — |
| [`job672_stuck_deploy.sh`](../../debug_log/2026-09-29/jobs/job672_stuck_deploy.sh) | 09-29 §13.1: stuck_monitor(자이로 우선) 빌드·자체시험 → 설치본 로직으로 20 bag 오판 재확인(OLD=설치본 판정식 재현 경로 아님, 참고) | — |
| [`job673_stand.py`](../../debug_log/2026-09-29/jobs/job673_stand.py) | 09-29 §13 G3b 받침대 시험: 트랙이 공중에서 도는 상태(몸 정지)에서 stuck_monitor(그림자 모드)가 정체를 잡는지. | 09-29 §13.2 |
| [`job674_stand_run.sh`](../../debug_log/2026-09-29/jobs/job674_stand_run.sh) | 09-29 §13 G3b: prep(새 stuck_monitor, 그림자) → 받침대 시험 | — |
| [`job675_guard_deploy.sh`](../../debug_log/2026-09-29/jobs/job675_guard_deploy.sh) | 09-29 §13 L2: nav_guard 배포·빌드·기동 확인(목표 없이 8 s — 개입 0 이어야) | — |
| [`job676_prep_g.sh`](../../debug_log/2026-09-29/jobs/job676_prep_g.sh) | 09-29 §13 G1 준비: prep(stuck_monitor 작동·nav_guard) → 두 노드 모드 확인 | — |
| [`job677_g1.py`](../../debug_log/2026-09-29/jobs/job677_g1.py) | 09-29 §13 G1: nav_guard 시간 한도 실동작. nav_guard time_limit_override=15 로 두고 W3 (5.5, −2.2) 목표를 보낸다. | 09-29 §13.5 |
| [`job678_g1_run.sh`](../../debug_log/2026-09-29/jobs/job678_g1_run.sh) | 09-29 §13 G1 실행 | — |
| [`job679_guard_fix.sh`](../../debug_log/2026-09-29/jobs/job679_guard_fix.sh) | 09-29 §13.5 nav_guard 재개입 방지 수정 빌드(다음 prep 부터 적용) | — |
| [`run_spin.sh`](../../debug_log/2026-09-29/jobs/run_spin.sh) | 회전 시험 PC 러너(09-28): 전송(재시도 3) → job565 를 setsid nohup 으로 기동 → 로그 폴링 → 산출물 회수 | 09-29 §3 |
| [`vslam_standalone.launch.py`](../../debug_log/2026-09-29/jobs/vslam_standalone.launch.py) | 09-29 §9 cuVSLAM 3.2 단독 확인용 (컨테이너 안에서 실행). Isaac 예제 isaac_ros_visual_slam_realsense.launch.py 의 노드 파라미터를 | — |

## 2026-09-30 (46)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job240_clean.sh`](../../debug_log/2026-09-30/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job680_slambias.py`](../../debug_log/2026-09-30/jobs/job680_slambias.py) | 09-30 §3 SLAM 앞뒤 치우침 시험: 출발 테이프에서 직진 DIST m(EKF 기준) 뒤 정지, SLAM 이동 vs 사용자 줄자. | 09-30 §3 · 09-30 §3.2 |
| [`job681_fp_build.sh`](../../debug_log/2026-09-30/jobs/job681_fp_build.sh) | 09-30 §3: footprint 실측 반영 빌드 | — |
| [`job682_slambias_run.sh`](../../debug_log/2026-09-30/jobs/job682_slambias_run.sh) | 09-30 §3: prep(새 footprint) → footprint 적용 확인 → 0.70 m 직진 SLAM 치우침 시험 | — |
| [`job683_slambias_rev.sh`](../../debug_log/2026-09-30/jobs/job683_slambias_rev.sh) | 09-30 §3 2 회차: 같은 자리에서 0.70 m 후진(0.06 m/s) | — |
| [`job684_map_save.sh`](../../debug_log/2026-09-30/jobs/job684_map_save.sh) | 09-30 F1: SLAM 지도 저장 — 포즈 그래프(이어 그리기용 .posegraph/.data) + 격자(pgm/yaml, Nav2·편집용). 인자: 이름 | 09-30 §4 |
| [`job685_f1_teleop.sh`](../../debug_log/2026-09-30/jobs/job685_f1_teleop.sh) | 09-30 F1: USB 패드 매핑 조종 기동(profile mapping = 0.07 m/s·0.3 rad/s) + 확인 | 09-30 §4 |
| [`job686_f1_deploy.sh`](../../debug_log/2026-09-30/jobs/job686_f1_deploy.sh) | 09-30 §4: slam·joy launch 인자 배포 확인 | — |
| [`job687_f1_prep.sh`](../../debug_log/2026-09-30/jobs/job687_f1_prep.sh) | 09-30 §4 F1: prep(새 지도) → 패드 장치 확인 → 끊김 시험용 조종(출력 /cmd_vel_test, 로버 비구동) | — |
| [`job688_nav2chk.sh`](../../debug_log/2026-09-30/jobs/job688_nav2chk.sh) | 09-30: Nav2 inactive 원인 확인 | — |
| [`job689_nav2_startup.sh`](../../debug_log/2026-09-30/jobs/job689_nav2_startup.sh) | 09-30: Nav2 lifecycle 재기동(STARTUP) — 첫 기동이 behavior_server get_state 실패로 중단됨 | — |
| [`job690_joydrop.py`](../../debug_log/2026-09-30/jobs/job690_joydrop.py) | 09-30 §4 F1-0 무선 끊김 시험: 30 s 동안 /joy 와 /cmd_vel_test(조종 출력, 로버 비구동)를 기록. | — |
| [`job691_joydrop_run.sh`](../../debug_log/2026-09-30/jobs/job691_joydrop_run.sh) |  | — |
| [`job692_posenow.py`](../../debug_log/2026-09-30/jobs/job692_posenow.py) | 09-30 §4 F1-1a: 지금 로버 map 자세(5 s 평균)와 오른쪽 앞 모서리의 출발 표시 대비 예측(출발 = map 원점, 출발 yaw 는 원점 자세). | — |
| [`job693_f1_save.sh`](../../debug_log/2026-09-30/jobs/job693_f1_save.sh) | 09-30 F1: 현재 자세 → 지도 저장(office_v1) → 매핑 통계 | — |
| [`job694_lagchk.sh`](../../debug_log/2026-09-30/jobs/job694_lagchk.sh) | 09-30: 매핑 중 Foxglove 에서 로버 위치가 멈췄다 점프한 원인 — 브리지·SLAM·EKF 로그와 현재 부하 | 09-30 §5 |
| [`job695_loadab.sh`](../../debug_log/2026-09-30/jobs/job695_loadab.sh) | 09-30: Foxglove 연결 유무 부하 A/B — 30 s 동안 EKF 주기 미달·SLAM 스캔 버림 증가, 부하, 주요 프로세스 CPU. 인자: 라벨 | 09-30 §5 |
| [`job696_bridge_map.sh`](../../debug_log/2026-09-30/jobs/job696_bridge_map.sh) | 09-30 §5: 브리지를 viz:=map 으로 교체(다른 스택 유지) — 빌드 → 기존 브리지 종료 → 새로 기동 → 설정 확인 | 09-30 §5.1 |
| [`job697_restore_chk.py`](../../debug_log/2026-09-30/jobs/job697_restore_chk.py) | 09-30 §4 F1-2 복원 확인: 불러온 /map 크기·원점(저장본 office_v1 = 301×213, 원점 (−5.09, −6.96))과 | 10-01 §6 |
| [`job698_f1_restore.sh`](../../debug_log/2026-09-30/jobs/job698_f1_restore.sh) | 09-30 §4 F1-2: office_v1 불러와 prep(viz:=map) → 복원 확인 | — |
| [`job699_bag2frames.py`](../../debug_log/2026-09-30/jobs/job699_bag2frames.py) | 09-30 §7 주행 영상화용 추출: F0 bag → 10 Hz 프레임 데이터(npz). PC 에서 그림·ffmpeg 로 영상화. | 09-30 §7 · 09-30 §7.2 |
| [`job700_vid_extract.sh`](../../debug_log/2026-09-30/jobs/job700_vid_extract.sh) | 09-30 §7: f0b1·f0b2 bag → 영상 프레임 데이터 | — |
| [`job701_vx_jitter.py`](../../debug_log/2026-09-30/jobs/job701_vx_jitter.py) | 09-30 §7.4 EKF 직진 속도 흔들림의 출처(v2): 전진 주행 전체(명령 v ≥ 0.075)에서 신호마다 1 s 이동평균을 뺀 **빠른 흔들림**의 | 09-30 §7.4 |
| [`job702_vx_jitter_run.sh`](../../debug_log/2026-09-30/jobs/job702_vx_jitter_run.sh) | 09-30 §7.4 EKF 직진 속도 흔들림 출처 | — |
| [`job703_map_spans.py`](../../debug_log/2026-09-30/jobs/job703_map_spans.py) | 09-30 §8 F1-3: 저장 지도(office_v1.pgm/yaml)에서 구간 길이 측정 — 한 점에서 한 방향으로 빈 셀을 따라가 양쪽 벽(점유 셀) 사이 거리. | 09-30 §8 |
| [`job704_f1v2_prep.sh`](../../debug_log/2026-09-30/jobs/job704_f1v2_prep.sh) | 09-30 §10: office_v1 불러와 prep(viz:=map) → F1-2 재확인(테이프 재정렬) → 매핑 조종 기동 | 09-30 §10 |
| [`job705_jumpchk.sh`](../../debug_log/2026-09-30/jobs/job705_jumpchk.sh) | 09-30 §11: 이어 그리기 중 Foxglove 에서 로버가 멈췄다 점프 — 메모리·부하·TF 지연·SLAM/EKF 로그 | 09-30 §11 |
| [`job706_cputop.sh`](../../debug_log/2026-09-30/jobs/job706_cputop.sh) | 09-30 §11: CPU 소비 상위(top 5 회 평균) + 브리지 설정 + 부하 | 09-30 §11 |
| [`job707_mapmode_prep.sh`](../../debug_log/2026-09-30/jobs/job707_mapmode_prep.sh) | 09-30 §11: 매핑 전용 모드 prep(office_v1 불러오기, Nav2·nvblox 없음) → 복원 확인 → 조종 → 30 s 부하·EKF 미달 확인 | 09-30 §11 |
| [`job708_mapmode_chk.sh`](../../debug_log/2026-09-30/jobs/job708_mapmode_chk.sh) | 09-30 §11: 매핑 모드 prep 상태 확인 | — |
| [`job709_mapmode_prep_full.sh`](../../debug_log/2026-09-30/jobs/job709_mapmode_prep_full.sh) | 09-30 §11: 매핑 모드 prep 전체 출력(원인 확인) | — |
| [`job710_mapmode_teleop.sh`](../../debug_log/2026-09-30/jobs/job710_mapmode_teleop.sh) |  | — |
| [`job711_rotchk.py`](../../debug_log/2026-09-30/jobs/job711_rotchk.py) | 09-30 §12: 회전 중 지도 위 로버가 안 도는 현상 — 15 s 동안 1 s 간격으로 | 09-30 §12 |
| [`job712_rotchk_run.sh`](../../debug_log/2026-09-30/jobs/job712_rotchk_run.sh) |  | — |
| [`job713_jump2.sh`](../../debug_log/2026-09-30/jobs/job713_jump2.sh) | 09-30 §13: 매핑 중 로버가 지도 위에서 갑자기 점프 — 사후 조사(주행 없음, 읽기만). | 09-30 §13 |
| [`job714_jump2b.sh`](../../debug_log/2026-09-30/jobs/job714_jump2b.sh) | 09-30 §13 보충: Ceres 최적화(루프 클로저) 흔적 횟수·시각, slam 시작 시각, 카메라 IMU 실제 수신률(기동 때 Motion Module failure 경고 확인) | 09-30 §13 |
| [`job715_slamcfg_deploy.sh`](../../debug_log/2026-09-30/jobs/job715_slamcfg_deploy.sh) | 09-30 §14: slam.yaml(loop_search_space_dimension 8→3) 를 src·install 양쪽에 배포 — 지금 도는 SLAM 은 건드리지 않음(다음 prep 에서 반영) | 09-30 §14 |
| [`job716_joymax_deploy.sh`](../../debug_log/2026-09-30/jobs/job716_joymax_deploy.sh) | 09-30 §15: 조이스틱 mapping 프로필을 펌웨어 상한(0.085 m/s·0.38 rad/s)으로 — src 배포·빌드, 실행 중 teleop 파라미터도 즉시 변경 | 09-30 §15 |
| [`job717_map2_prep.sh`](../../debug_log/2026-09-30/jobs/job717_map2_prep.sh) | 09-30 §16: 매핑 재시작 — office_v1 불러오기(출발 테이프 = 0,0,0), 매핑 전용 모드, 루프 창 3 m, bag 자동, stuck 관찰, Foxglove map 세트 | 09-30 §16 |
| [`job718_ana.py`](../../debug_log/2026-09-30/jobs/job718_ana.py) | 09-30 §16: 매핑 bag 에서 map→odom(SLAM 보정) 시계열의 점프 찾기 + 그 시각의 로버 운동. | 09-30 §16 |
| [`job718_map2_break.sh`](../../debug_log/2026-09-30/jobs/job718_map2_break.sh) | 09-30 §16: 두 번째 매핑도 지도 깨짐(사용자) — 지도 저장 안 함. bag 을 닫고(SIGINT) 사후 분석. | — |
| [`job719_cut.sh`](../../debug_log/2026-09-30/jobs/job719_cut.sh) | 09-30 §17: 점프 전(bag +699 s, 17:36:15)까지만 지도 되살리기 — 도메인 42 에서 office_v1 이어 그리기 slam(현 slam.yaml)을 sim time 으로 띄우고 | 09-30 §17 |
| [`job719_cutreplay.py`](../../debug_log/2026-09-30/jobs/job719_cutreplay.py) | 09-30 §17: 점프 전까지만 지도 되살리기 — 매핑 bag 을 **도메인 42**·sim time 으로 CUT 초까지만 재생해 | 09-30 §17 |
| [`job720_stop_replay.sh`](../../debug_log/2026-09-30/jobs/job720_stop_replay.sh) | 09-30 §17: 사용자 "멈추고 마무리" — 점프 전 재생(job719) 중단, 도메인 42 재생 slam 정리. 라이브 센서·에이전트는 그대로. | — |
| [`render_f0b.py`](../../debug_log/2026-09-30/jobs/render_f0b.py) | 09-30 §7.2: F0-b 주행 영상 v2(1280×720, 10 fps = 실제 속도). 인자: vid_XXX.npz out.mp4 제목 [상자 전면 x] [상자 중심 y] | 09-30 §7 · 09-30 §7.2 · 09-30 §7.5 |
| [`sidebyside.sh`](../../debug_log/2026-09-30/jobs/sidebyside.sh) | 09-30 §7: 실제 촬영(세로) + 데이터 영상(가로) 좌우 결합. 동기 = 문 통과 순간(영상에서 읽음 ↔ bag 계산). | 09-30 §7.1 |

## 2026-10-01 (87)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`attrib_blocks.py`](../../debug_log/2026-10-01/jobs/attrib_blocks.py) | 10-01 §8.23: 센서가 새로 막은 칸(자홍)을 원인별로 — 그 칸에서 0.20 m(≈ 내접 0.175 + 셀) 안에 | 10-01 §8.23 |
| [`edit_south.py`](../../debug_log/2026-10-01/jobs/edit_south.py) | 10-01 §3: 사용자 지시 — 후보(루프 클로저 끔)의 책상 구역 남쪽 벽을 x ≥ 0 에서 office_v1 값에 맞춰 보정(격자 pgm 편집). | 10-01 §3 |
| [`f2_candidates.py`](../../debug_log/2026-10-01/jobs/f2_candidates.py) | 10-01 §8: F2 웨이포인트 후보 — office_v2 격자에서 각 후보의 벽까지 여유(가장 가까운 점유 셀 거리)와 미지 비율, 그림 | 10-01 §8 |
| [`fit_scan.py`](../../debug_log/2026-10-01/jobs/fit_scan.py) | 10-01 §8.40: 기록된 로버 자세가 맞는지 — 라이다 스캔(그 자세로 map 에 놓은 것)을 저장 지도 벽에 맞추는 데 필요한 보정(dx, dy, dθ) | 10-01 §8.39 · 10-01 §8.41 |
| [`fit_scan2.py`](../../debug_log/2026-10-01/jobs/fit_scan2.py) | 10-01 §8.40: 국소(±0.3 m, ±4°) 격자 탐색 — 책상 반복 구조 때문에 Powell 이 1.3~2.7 m 옆 칸으로 빠지는 것(fit_scan.py) 방지 | 10-01 §8.40 |
| [`job240_clean.sh`](../../debug_log/2026-10-01/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job550_f0run.py`](../../debug_log/2026-10-01/jobs/job550_f0run.py) | F0 코스 확장 러너 (2026-09-23): 상자 코스와 무관한 연속 목표 주행 + 왕복 복귀 오차 계측. | 09-23 16 · 09-28 §12 · 09-28 §16 · … +5 |
| [`job551_f0drive.sh`](../../debug_log/2026-10-01/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`job697_restore_chk.py`](../../debug_log/2026-10-01/jobs/job697_restore_chk.py) | 09-30 §4 F1-2 복원 확인: 불러온 /map 크기·원점(저장본 office_v1 = 301×213, 원점 (−5.09, −6.96))과 | 10-01 §6 |
| [`job719_cut.sh`](../../debug_log/2026-10-01/jobs/job719_cut.sh) | 09-30 §17: 점프 전(bag +699 s, 17:36:15)까지만 지도 되살리기 — 도메인 42 에서 office_v1 이어 그리기 slam(현 slam.yaml)을 sim time 으로 띄우고 | 09-30 §17 |
| [`job719_cutreplay.py`](../../debug_log/2026-10-01/jobs/job719_cutreplay.py) | 09-30 §17: 점프 전까지만 지도 되살리기 — 매핑 bag 을 **도메인 42**·sim time 으로 CUT 초까지만 재생해 | 09-30 §17 |
| [`job722_cand_grid.sh`](../../debug_log/2026-10-01/jobs/job722_cand_grid.sh) | 10-01 §1: 후보 포즈 그래프(cand_0930_cut699)에서 격자 지도(pgm/yaml) 만들기 — job719 의 save_map 이 255 로 실패(sim time 재생 뒤, 원인 미확정) | 10-01 §1.1 |
| [`job725_save_v2.sh`](../../debug_log/2026-10-01/jobs/job725_save_v2.sh) | 10-01 §5: 사용자 승인 — cand_0930_cut590_nolc 를 office_v2 로 저장(복사, 원본·office_v1 유지). 같은 이름 있으면 중단. | 10-01 §5 |
| [`job726_prep_map.sh`](../../debug_log/2026-10-01/jobs/job726_prep_map.sh) | 10-01 §5·§7: 지도 불러오기 prep — 기본 office_v2(출발 테이프 = 0,0,0). 인자/환경: | 10-01 §5 · 10-01 §7 · 10-02 §4 · … +1 |
| [`job727_f12_v2.sh`](../../debug_log/2026-10-01/jobs/job727_f12_v2.sh) | 10-01 §6 F1-2(office_v2): 출발 테이프에서 office_v2 불러오기 → 복원 확인. 판정(선언): 원점에서 ≤ 5 cm, 5 s 안 안정(연속 변화 ≤ 1 cm), /map 333×227·원점 (−5.29, −6.96). | 10-01 §6 |
| [`job728_nav2state.sh`](../../debug_log/2026-10-01/jobs/job728_nav2state.sh) | 10-01 §6: Nav2 lifecycle 상태·부하·EKF 확인(prep 에서 controller_server "?" — 조회 시간 초과인지 기동 실패인지) | — |
| [`job730_f14_deploy.sh`](../../debug_log/2026-10-01/jobs/job730_f14_deploy.sh) | 10-01 §7 F1-4 준비: 위치 추정 후보 코드 배포·빌드 → 정지 상태에서 후보별 기동 확인(로버 출발 테이프, 움직이지 않음) | 10-01 §7.1 |
| [`job731_f2_prep.sh`](../../debug_log/2026-10-01/jobs/job731_f2_prep.sh) | 10-01 §8.1 F2 첫 주행 prep: office_v2 + slam_toolbox 위치 추정 모드(LOC=slamloc), 전체 스택 → 시작 자세 확인(L-d) | 10-01 §8.1 · 10-02 §4 |
| [`job732_abort_why.sh`](../../debug_log/2026-10-01/jobs/job732_abort_why.sh) | 10-01 §8.2: f2a1 목표 1 ABORTED(36 s, map (0.55, 0.12)) — 원인 로그(읽기만). 11:05:30~11:06:30 구간. | 10-01 §8.2 |
| [`job733_tfstamp.py`](../../debug_log/2026-10-01/jobs/job733_tfstamp.py) | 10-01 §8.2: /tf 의 map→odom(slam_toolbox)과 odom→base_link(EKF) 발행 주기·스탬프 지연(수신 시각 − 스탬프) 10 s. | 10-01 §8.2 |
| [`job734_tflag_bag.py`](../../debug_log/2026-10-01/jobs/job734_tflag_bag.py) | 10-01 §8.2: bag 의 /tf 로 map→odom(slam) 스탬프가 odom→base_link(EKF) 최신 스탬프보다 뒤처진 시간 — 컨트롤러는 로봇 자세(EKF 최신 스탬프)를 | 10-01 §8.2 · 10-01 §8.3 |
| [`job736_locreplay.py`](../../debug_log/2026-10-01/jobs/job736_locreplay.py) | 10-01 §9: 위치 추정 모드 부하 재현 — 09-30 매핑 bag 을 도메인 42·sim time 으로 재생해 localization_slam_toolbox_node(office_v2)에 먹이고, | — |
| [`job736_locreplay.sh`](../../debug_log/2026-10-01/jobs/job736_locreplay.sh) | 10-01 §9: 위치 추정 모드 부하 A/B — 도메인 42 에서 localization_slam_toolbox_node(office_v2, sim time)를 변형별로 띄우고 job736 재생. | 10-01 §9 |
| [`job738_deploy_slamloc.sh`](../../debug_log/2026-10-01/jobs/job738_deploy_slamloc.sh) | 10-01 §8.5: slam.launch.py(transform_timeout 0.5) 배포·빌드 | — |
| [`job739_slamparams.sh`](../../debug_log/2026-10-01/jobs/job739_slamparams.sh) |  | — |
| [`job740_f2a2_anal.sh`](../../debug_log/2026-10-01/jobs/job740_f2a2_anal.sh) | 10-01 §8.4: f2a2 분석 — 실주행 map→odom 결손(job734), 주행 구간 Nav2 경고·오류(job732 형식), 위치 추정 노드 CPU(top) | 10-01 §8.5 |
| [`job741_f2a3_anal.sh`](../../debug_log/2026-10-01/jobs/job741_f2a3_anal.sh) | 10-01 §8.4: f2a3 분석 — 실주행 map→odom 결손(job734), 주행 구간 Nav2 경고·오류(job732 형식), 위치 추정 노드 CPU(top) | — |
| [`job742_who.sh`](../../debug_log/2026-10-01/jobs/job742_who.sh) | 10-01 §8.7: CPU 포화(sy 30~40 %) 원인 찾기 — 지금(로버 정지, 스택 기동 상태) 상위 프로세스·python 명령줄·polkitd 호출자 | — |
| [`job743_polkit.sh`](../../debug_log/2026-10-01/jobs/job743_polkit.sh) | 10-01 §8.7: ① 고아 nav_guard 정리(55 분 전 것) ② polkitd CPU 가 nmcli(OLED 정보 노드 3 s 마다) 때문인지 — polkitd 누적 CPU 를 20 s 그냥 vs nmcli 20 회 호출하며 비교 | — |
| [`job744_fgclients.sh`](../../debug_log/2026-10-01/jobs/job744_fgclients.sh) | 10-01 §8.8: foxglove_bridge 클라이언트 접속 기록 — 주행(f2a2 12:58·f2a3 13:41) 중 연결된 클라이언트가 있었나, 지금 연결은 누구인가 | 10-01 §8.8 |
| [`job745_idleload.sh`](../../debug_log/2026-10-01/jobs/job745_idleload.sh) | 10-01 §8.9: 정지 상태(전체 스택 기동, Foxglove 닫음) 30 s 부하 기준선 — 코어 평균·us/sy, 프로세스별 CPU(전체 목록, 누적 틱 차), | — |
| [`job746_cancel_why.sh`](../../debug_log/2026-10-01/jobs/job746_cancel_why.sh) | 10-01 §8.11: f2a4 목표 2 CANCELED(12.9 s) — 누가 취소했나(stuck_monitor·nav_guard·러너), 같은 구간 Nav2 로그 | — |
| [`job747_stuckchk.py`](../../debug_log/2026-10-01/jobs/job747_stuckchk.py) | 10-01 §8.11: f2a4 STUCK(14:02:52) 앞 8 s — 0.5 s 마다 명령 v·ω, 휠 v·ω, EKF v, 자이로 ω, map 위치 변화(SLAM), 최근접 라이다 점 거리(차체 외곽 기준 아님, 라이다 중심). | 10-01 §8.11 |
| [`job748_sector.py`](../../debug_log/2026-10-01/jobs/job748_sector.py) | 10-01 §8.11: STUCK 판정(14:02:52.67) 때 stuck_monitor 와 같은 방식으로 앞(0°)·뒤(180°) ±20° 섹터를 재현 — 2 s 전 스캔 A vs 마지막 B. | 10-01 §8.11 |
| [`job749_usegyro.sh`](../../debug_log/2026-10-01/jobs/job749_usegyro.sh) |  | — |
| [`job750_f2_prep_shadow.sh`](../../debug_log/2026-10-01/jobs/job750_f2_prep_shadow.sh) | 10-01 §8.12: F2 순회 prep — stuck_monitor 관찰 모드(사용자 결정, §8.11 오판). 나머지는 job731 과 같음 | 10-01 §8.12 |
| [`job751_cancel2.sh`](../../debug_log/2026-10-01/jobs/job751_cancel2.sh) | 10-01 §8.13: f2a5 목표 2 CANCELED(34.3 s) — 누가 취소했나 | — |
| [`job752_deploy_guard.sh`](../../debug_log/2026-10-01/jobs/job752_deploy_guard.sh) | 10-01 §8.13: nav_guard d0 수정 배포·빌드 | 10-01 §8.13 |
| [`job753_chk.sh`](../../debug_log/2026-10-01/jobs/job753_chk.sh) |  | — |
| [`job754_d_why.sh`](../../debug_log/2026-10-01/jobs/job754_d_why.sh) | 10-01 §8.15: f2a6 목표 3(D) CANCELED 166.6 s — 원인 | — |
| [`job755_traj.py`](../../debug_log/2026-10-01/jobs/job755_traj.py) | 10-01 §8.15: f2a6 bag → map 위 로버 궤적(0.5 s), /plan 들(10 s 마다 1 개), 명령·휠 속도 → CSV 3 개(/tmp/f2a6_*.csv). | 10-01 §8.15 |
| [`job756_routes.py`](../../debug_log/2026-10-01/jobs/job756_routes.py) | 10-01 §8.16: f2a6 목표 3(C→D) 동안 경로가 왜 바뀌었나. | 10-01 §8.16 |
| [`job757_events.sh`](../../debug_log/2026-10-01/jobs/job757_events.sh) |  | — |
| [`job758_btcheck.sh`](../../debug_log/2026-10-01/jobs/job758_btcheck.sh) |  | 10-01 §8.17 |
| [`job759_deploy_bt.sh`](../../debug_log/2026-10-01/jobs/job759_deploy_bt.sh) | 10-01 §8.17: BT(경로 무효 시만 재계획) 배포·빌드 | 10-01 §8.17 |
| [`job760_nav2_restart.sh`](../../debug_log/2026-10-01/jobs/job760_nav2_restart.sh) | 10-01 §8.18: Nav2 만 재시작(새 BT 적용) — 센서·EKF·위치 추정(slam_toolbox)·에이전트는 그대로(로버가 손으로 옮겨지지 않아 위치 추정 유효). | 10-01 §8.18 · 10-02 §4 |
| [`job761_events.sh`](../../debug_log/2026-10-01/jobs/job761_events.sh) |  | — |
| [`job762_plans.py`](../../debug_log/2026-10-01/jobs/job762_plans.py) | 10-01 §8.19: f2a7 bag 의 /plan 시각·시작점·끝점·길이·경유(최소 y·최대 y) — 경로가 어디로 향했나 | 10-01 §8.19 |
| [`job766_preempt.sh`](../../debug_log/2026-10-01/jobs/job766_preempt.sh) |  | — |
| [`job767_sensviz.py`](../../debug_log/2026-10-01/jobs/job767_sensviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-01 §8.22 |
| [`job768_deploy_a1.sh`](../../debug_log/2026-10-01/jobs/job768_deploy_a1.sh) | 10-01 §8.24: BT(재계획 = 목표 변경·주행 실패 때만)·전역 nvblox 층 제거 배포 → Nav2 만 재시작(위치 추정 유지) | 10-01 §8.24 |
| [`job770_slip.py`](../../debug_log/2026-10-01/jobs/job770_slip.py) | 10-01 §8.26: f2a9 케이블 가드 통과 — 0.5 s 마다 명령 v, 휠 v(트랙이 돈 속도), SLAM(map) 실제 속도, 자이로 피치·롤 각속도(IMU x·z), | 10-01 §8.26 |
| [`job771_duty.py`](../../debug_log/2026-10-01/jobs/job771_duty.py) | 10-01 §8.26: f2a9 28~42 s — 펌웨어 /rover/status 의 좌우 트랙 tgt·v·d(듀티)·pps 와 map→odom 보정 변화(SLAM 이 휠 이동을 되돌린 양). | 10-01 §8.26 |
| [`job772_g.sh`](../../debug_log/2026-10-01/jobs/job772_g.sh) |  | — |
| [`job774_lviz.py`](../../debug_log/2026-10-01/jobs/job774_lviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-01 §8.31 |
| [`job775_vxmin.sh`](../../debug_log/2026-10-01/jobs/job775_vxmin.sh) | 10-01 §8.28: MPPI vx_min 0 배포 → Nav2 만 재시작(위치 추정 유지) | 10-01 §8.28 |
| [`job776_mppi_sim_ack.py`](../../debug_log/2026-10-01/jobs/job776_mppi_sim_ack.py) | [job776, 2026-10-01 §8.29] job452 + Ackermann 최소 회전 반경(ack_r>0 이면 \|ω\| ≤ \|v\|/ack_r — Nav2 1.1.x AckermannMotionModel::applyConstraints 와 같은 규 | 10-01 §8.29 · 10-13 §7 |
| [`job776_run.sh`](../../debug_log/2026-10-01/jobs/job776_run.sh) | 10-01 §8.29: 회전 방식 시뮬 — 두 장면 × 세 설정. 공통 = job452 의 실측 구동계 모델(COM) + 경로·로컬 코스트맵 시간 재생. | 10-01 §8.29 |
| [`job778_gviz.py`](../../debug_log/2026-10-01/jobs/job778_gviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-01 §8.31 |
| [`job779_mapdiff.py`](../../debug_log/2026-10-01/jobs/job779_mapdiff.py) | 10-01 §8.32: 주행 중 위치 추정 노드가 낸 /map(전역 정적 층의 입력)이 저장 지도 office_v2.pgm 과 같은가 — 특히 서쪽 통로. | 10-01 §8.32 |
| [`job780_prep_navmap.sh`](../../debug_log/2026-10-01/jobs/job780_prep_navmap.sh) | 10-01 §8.33: 저장 지도 전역 정적 층 + 위치 추정(slamloc) prep — stuck 관찰 모드. 확인: /map_nav 발행·static_layer map_topic·전역 plugins | 10-01 §8.33 |
| [`job781_chk.sh`](../../debug_log/2026-10-01/jobs/job781_chk.sh) |  | 10-01 §8.33 |
| [`job784_camglobal.sh`](../../debug_log/2026-10-01/jobs/job784_camglobal.sh) | 10-01 §8.35: 전역 obstacle_layer 에 카메라 점군 소스 추가 배포 → Nav2 만 재시작(위치 추정 유지, NAV_ARGS 저장 지도 유지) → 상자 표시 확인 | 10-01 §8.35 |
| [`job785_boxchk.sh`](../../debug_log/2026-10-01/jobs/job785_boxchk.sh) | 10-01 §8.36: prep 뒤 정지 상태에서 전역·로컬 코스트맵의 상자 자리 비용 확인 | — |
| [`job787_lviz.py`](../../debug_log/2026-10-01/jobs/job787_lviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-01 §8.37 |
| [`job788_cmd.py`](../../debug_log/2026-10-01/jobs/job788_cmd.py) | 10-01 §8.37: f2a12 목표 7 — 바퀴 명령(/cmd_vel 류)·경로(/plan) 시계열. 인자: BAG T_START T_END(epoch) | 10-01 §8.37 |
| [`job789_g34.py`](../../debug_log/2026-10-01/jobs/job789_g34.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-01 §8.37 |
| [`job790_btlibs.sh`](../../debug_log/2026-10-01/jobs/job790_btlibs.sh) | 10-01 §8.39: 기본 plugin_lib_names 목록이 박힌 라이브러리 찾기 | 10-01 §8.39 |
| [`job791_deploy_pba.sh`](../../debug_log/2026-10-01/jobs/job791_deploy_pba.sh) | 10-01 §8.39: PathBlockedAhead BT 조건 노드 배포 — 소스·CMake·package.xml·nav2_params·BT XML 복사 → 빌드 → Nav2 만 재시작(위치 추정 유지) → 플러그인 적재 확인 | 10-01 §8.39 |
| [`job792_full.py`](../../debug_log/2026-10-01/jobs/job792_full.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-01 §8.40 |
| [`job793_slamlog.sh`](../../debug_log/2026-10-01/jobs/job793_slamlog.sh) | 10-01 §8.41: f2a12 +283.5 s(epoch ≈ 1790841826) map→odom 1.37 m 점프 — slam_toolbox 로그에 루프 클로저/매칭 기록이 있나 | — |
| [`proc_anal.py`](../../debug_log/2026-10-01/jobs/proc_anal.py) | 10-01 §8.9: 러너 proc_<NAME>.log(2 s 마다 전체 프로세스 CPU 틱) → 구간별 프로세스 CPU·코어 평균. 인자: LOG [시작 epoch] [끝 epoch] | 10-01 §8.9 |
| [`render_cand.py`](../../debug_log/2026-10-01/jobs/render_cand.py) | 10-01 §1: office_v1 과 후보(cand_0930_cut699) 격자를 월드 좌표로 맞춰 겹쳐 그림 — 이중 벽(R2) 확인용 | 10-01 §1.1 |
| [`render_f2a12.py`](../../debug_log/2026-10-01/jobs/render_f2a12.py) | 10-01 §8.40: f2a12 전체 bag 시각화(1 s 간격) — 왼쪽 = 지도 전체·궤적, 오른쪽 = 로버 주변 3 × 3 m 확대. | 10-01 §8.40 |
| [`render_g7.py`](../../debug_log/2026-10-01/jobs/render_g7.py) | 10-01 §8.37: f2a12 목표 7(서쪽 통로 북행) — 출발 직후 왜 제자리에서 떨기만 했나. 왼쪽 전역, 오른쪽 로컬(+nvblox·라이다), 아래 바퀴 명령. | 10-01 §8.37 |
| [`render_jumphole.py`](../../debug_log/2026-10-01/jobs/render_jumphole.py) | 10-01 §8.42: 점프 지점 주변 지도 구멍(미지 칸)과 점프 전·후 추정 자세 | 10-01 §8.42 |
| [`render_sensviz.py`](../../debug_log/2026-10-01/jobs/render_sensviz.py) | 10-01 §8.22: f2a8 D 구간 — 센서가 통로를 어떻게 '막힘'으로 만들었나(1 s 프레임 → mp4 + 핵심 장면 그림) | 10-01 §8.22 |
| [`render_westcorr.py`](../../debug_log/2026-10-01/jobs/render_westcorr.py) | 10-01 §8.31: f2a10 목표 2(서쪽 통로 중간) — 왜 통로를 못 지났나. 같은 시각의 두 판: | 10-01 §8.31 |
| [`run_f0.sh`](../../debug_log/2026-10-01/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_x723.sh`](../../debug_log/2026-10-01/jobs/run_x723.sh) | 10-01 §2: 루프 클로저 끔(nolc) 변형으로 점프 전 재생 → 격자 생성 | — |
| [`run_x724.sh`](../../debug_log/2026-10-01/jobs/run_x724.sh) | 10-01 §4: 남쪽 통로 구간(+590 s 이후) 스캔을 빼고(=+590 s 에서 자름) 루프 클로저 끔으로 재생 → 격자 | 10-01 §4 |
| [`run_x730.sh`](../../debug_log/2026-10-01/jobs/run_x730.sh) |  | — |
| [`shift_cand.py`](../../debug_log/2026-10-01/jobs/shift_cand.py) | 10-01 §1: 영역별로 후보를 office_v1 에 가장 잘 겹치는 평행 이동(±0.30 m, 5 cm 단위) — 두 지도가 어디서 얼마나 어긋났나 | 10-01 §1.1 |
| [`southwall.py`](../../debug_log/2026-10-01/jobs/southwall.py) | 10-01 §2: 남쪽 벽 위치 — 출발 방 남쪽 벽(y≈−0.6, 문 쪽 벽 바깥 면)에서 남쪽 벽까지 거리를 x 별로(빈 셀 따라 아래로 첫 점유) | 10-01 §2.1 |
| [`straight.py`](../../debug_log/2026-10-01/jobs/straight.py) | 10-01 §2.2: 책상 구역 남쪽 벽은 실제로 일직선(사용자) — 각 지도에서 벽 점(열마다 y −5.9 아래 첫 점유)을 x −2.0~6.0 에서 모아 | 10-01 §2.2 |
| [`wall_cand.py`](../../debug_log/2026-10-01/jobs/wall_cand.py) | 10-01 §1: 두 방 사이 벽(줄자 ≈ 0.20 m) 두께와 출발 방 폭(줄자 1.97 m)을 후보·office_v1 에서 같은 방법(빈 셀→점유 셀 경계)으로 | 10-01 §1.1 |
| [`zoom_cand.py`](../../debug_log/2026-10-01/jobs/zoom_cand.py) |  | 10-01 §1.1 |

## 2026-10-02 (63)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`box_fov.py`](../../debug_log/2026-10-02/jobs/box_fov.py) | 10-02 §9.1: f2b4 복귀 때 상자가 카메라(D455 깊이 수평 화각 87° = ±43.5°) 안에 있었나 — 기하 계산만 | 10-02 §9.1 |
| [`clear_cand.py`](../../debug_log/2026-10-02/jobs/clear_cand.py) | 10-02 §5: 경로 계획용 격자에서 지울 후보(움직이는 물체) 찾기 — office_v3 점유 칸 중 이후 주행에서 "비어 있음" 증거가 쌓인 칸 | 10-02 §5 |
| [`cmp_maps.py`](../../debug_log/2026-10-02/jobs/cmp_maps.py) | 10-02 §1: 후보 지도 판정 H-1(구멍)·H-3(옛 지도 보존)·H-4(남쪽 벽) — 기준 office_v2(·v1) | 10-02 §1.1 |
| [`get803.sh`](../../debug_log/2026-10-02/jobs/get803.sh) |  | — |
| [`job551_f0drive.sh`](../../debug_log/2026-10-02/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`job726_prep_map.sh`](../../debug_log/2026-10-02/jobs/job726_prep_map.sh) | 10-01 §5·§7: 지도 불러오기 prep — 기본 office_v3(10-02 §4, 이전 office_v2)(출발 테이프 = 0,0,0). 인자/환경: | 10-01 §5 · 10-01 §7 · 10-02 §4 · … +1 |
| [`job731_f2_prep.sh`](../../debug_log/2026-10-02/jobs/job731_f2_prep.sh) | 10-01 §8.1 F2 첫 주행 prep: office_v3(10-02 §4, MAP= 로 바꿈) + slam_toolbox 위치 추정 모드(LOC=slamloc), 전체 스택 → 시작 자세 확인(L-d) | 10-01 §8.1 · 10-02 §4 |
| [`job760_nav2_restart.sh`](../../debug_log/2026-10-02/jobs/job760_nav2_restart.sh) | 10-01 §8.18: Nav2 만 재시작(새 BT 적용) — 센서·EKF·위치 추정(slam_toolbox)·에이전트는 그대로(로버가 손으로 옮겨지지 않아 위치 추정 유효). | 10-01 §8.18 · 10-02 §4 |
| [`job800_chk.sh`](../../debug_log/2026-10-02/jobs/job800_chk.sh) | 10-02 §1: 지도 보완 전 확인 — bag 유무·시작 시각·토픽, 지도 파일, 가동 상태 | — |
| [`job801_bagup.sh`](../../debug_log/2026-10-02/jobs/job801_bagup.sh) | 10-02 §1: f2a12 bag 을 재부팅에 안전한 ~/bags 로 풀고 정보 확인 | — |
| [`job802_extend.sh`](../../debug_log/2026-10-02/jobs/job802_extend.sh) | 10-02 §1: office_v2 이어 그리기(루프 클로저 끔)로 f2a12 bag +CUT 초까지 재생 → 후보 포즈 그래프·격자. 도메인 42·sim time. | 10-02 §1.1 |
| [`job803_locjump.py`](../../debug_log/2026-10-02/jobs/job803_locjump.py) | 10-02 §2: f2a12 bag 을 도메인 42·sim time·1 배속으로 통째 재생해 localization_slam_toolbox_node 에 먹이고, | 10-02 §2 |
| [`job803_locjump.sh`](../../debug_log/2026-10-02/jobs/job803_locjump.sh) | 10-02 §2: 위치 추정 재생 3 조합 — 인자 "지도:탐색창" 목록. 운용과 같은 위치 추정 설정(slam.launch 의 0.30·0.15·갱신 10·tt 0.5). | 10-02 §2 |
| [`job804_save_v3.sh`](../../debug_log/2026-10-02/jobs/job804_save_v3.sh) | 10-02 §4: 후보 cand_1002_f2a12_c276_nolc → office_v3 (사용자 승인). office_v1·v2 는 보존. | 10-02 §4 |
| [`job805_evid.py`](../../debug_log/2026-10-02/jobs/job805_evid.py) | 10-02 §5: 지우기 증거 추출 — bag 하나에서 (1) 라이다 스캔(5 Hz)과 그 시각 로버 map 자세 (2) nvblox 슬라이스(1 Hz)와 그 시각 map→odom. | 10-02 §5 |
| [`job805_evid.sh`](../../debug_log/2026-10-02/jobs/job805_evid.sh) | 10-02 §5: 10-01 F2 bag 12 개 풀기(~/bags/f2) → 증거 추출(/tmp/evid/*.npz) | — |
| [`job812_navchk.sh`](../../debug_log/2026-10-02/jobs/job812_navchk.sh) | 10-02 §6: prep 뒤 Nav2 상태·BT 플러그인·/map_nav 크기 확인 | — |
| [`job814_nearcells.py`](../../debug_log/2026-10-02/jobs/job814_nearcells.py) | 10-02 §6.3: G2 불합격(여유 0.067 m) 원인 — 로컬 코스트맵 99/100 칸 중 차체 외곽 0.25 m 안의 것을 로버 기준 좌표로 나열 | — |
| [`job816_g5log.sh`](../../debug_log/2026-10-02/jobs/job816_g5log.sh) | 10-02 §6.4: f2b3 목표 5(전체 6) 정지·취소 원인 — nav2 로그(13:24:55 이후) | — |
| [`job817_lviz.py`](../../debug_log/2026-10-02/jobs/job817_lviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-02 §7 |
| [`job820_gviz.py`](../../debug_log/2026-10-02/jobs/job820_gviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-02 §9 |
| [`job820_lviz.py`](../../debug_log/2026-10-02/jobs/job820_lviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-02 §9 |
| [`job821_lviz.py`](../../debug_log/2026-10-02/jobs/job821_lviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | 10-02 §10 |
| [`job823_wallgap.py`](../../debug_log/2026-10-02/jobs/job823_wallgap.py) | 10-02 §11: 통제 회전 시험 전 — 벽까지 거리(라이다, 차체 기준)와 제자리 회전 여유 계산(모서리 반경 0.31 m) | 10-02 §11 |
| [`job825.sh`](../../debug_log/2026-10-02/jobs/job825.sh) |  | — |
| [`job825_rot.py`](../../debug_log/2026-10-02/jobs/job825_rot.py) | 10-02 §11: 통제 회전 시험 — bag 기록하며 /cmd_vel 로 제자리 ±90° × 3. 라이다 외곽 0.08 m 안이면 정지·중단. 인자: BAG_NAME | 10-02 §11 · 10-02 §12 |
| [`job827_gapchk.py`](../../debug_log/2026-10-02/jobs/job827_gapchk.py) |  | — |
| [`job828_lviz.py`](../../debug_log/2026-10-02/jobs/job828_lviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | — |
| [`job830_localmap.sh`](../../debug_log/2026-10-02/jobs/job830_localmap.sh) | 10-02 §12: navigation.launch.py(local_frame 인자) 배포·빌드 → Nav2 만 재시작(local_frame:=map) → 확인 | — |
| [`job831_lviz.py`](../../debug_log/2026-10-02/jobs/job831_lviz.py) | 10-01 §8.22: f2a8 D 구간(목표 1) — 센서가 통로를 어떻게 막힌 것으로 만들었나 시각화용 추출(1 s 간격). | — |
| [`job832_revert.sh`](../../debug_log/2026-10-02/jobs/job832_revert.sh) | 10-02 §12.1: A/B 끝 — Nav2 를 기본(local_frame odom)으로 재시작 | 10-02 §12.1 |
| [`job833_rf2o_src.sh`](../../debug_log/2026-10-02/jobs/job833_rf2o_src.sh) | 10-02 §13 R0: rf2o 소스 확인 — 인터넷·브랜치·메시지(공분산 채우는지) | — |
| [`job834_rf2o_build.sh`](../../debug_log/2026-10-02/jobs/job834_rf2o_build.sh) | 10-02 §13 R0: rf2o(MAPIRlab ros2 브랜치) 별도 작업공간 ~/rf2o_ws 에 소스 빌드(slam_ws 와 같은 방식) | 10-02 §13 |
| [`job835_rf2o_rec.py`](../../debug_log/2026-10-02/jobs/job835_rf2o_rec.py) | 10-02 §13 R1: rf2o 재생 시험 기록기 — /odom_rf2o 와 /tf(map→odom, odom→base) 를 받아 npz 로. 인자: OUT SEC | — |
| [`job835_rf2o_replay.sh`](../../debug_log/2026-10-02/jobs/job835_rf2o_replay.sh) | 10-02 §13 R1: 도메인 42·sim time — rf2o(publish_tf false) + bag 재생(--clock) + 기록기. 인자: BAG OUT | 10-02 §13.1 |
| [`job837.sh`](../../debug_log/2026-10-02/jobs/job837.sh) |  | — |
| [`job841_imuaxis.py`](../../debug_log/2026-10-02/jobs/job841_imuaxis.py) |  | — |
| [`job842_stamp.py`](../../debug_log/2026-10-02/jobs/job842_stamp.py) |  | — |
| [`job843_dbg.sh`](../../debug_log/2026-10-02/jobs/job843_dbg.sh) | EKF A 가 휠을 융합하지 않는 이유 확인 — f2b4 30 s 재생, /r2/wheel_A 와 /r2/ekfA 비교 | — |
| [`r2_eval.py`](../../debug_log/2026-10-02/jobs/r2_eval.py) | 10-02 §14 R2 판정 계산 — EKF A/B(+ 라이브 EKF) 를 줄자·SLAM·구석 벽 일관성으로 비교 | — |
| [`r2_gate.py`](../../debug_log/2026-10-02/jobs/r2_gate.py) | 10-02 §14 R2(오프라인 원형): 휠 공분산 중계 + rf2o 게이트 — bag 재생에서 EKF A/B 를 같은 입력으로 돌리기 위한 노드. | 10-02 §14 · 10-02 §14.1 · 10-06 §1 |
| [`r2_rec.py`](../../debug_log/2026-10-02/jobs/r2_rec.py) | 10-02 §14 R2: 기록기 — EKF A/B 출력, 라이브 TF(map→odom·odom→base), 스캔(2 Hz). 인자: OUT SEC | 10-02 §14 |
| [`r2_run.sh`](../../debug_log/2026-10-02/jobs/r2_run.sh) | 10-02 §14 R2: 도메인 42·sim time — rf2o + 게이트 + EKF A/B + 기록기, bag 재생(/scan /tf /tf_static /wheel_odom /imu/data). 인자: BAG OUT | 10-02 §14 |
| [`render_box.py`](../../debug_log/2026-10-02/jobs/render_box.py) | 10-02 §9: f2b4 출발 방 복귀 — 상자를 봤나(로컬 코스트맵·nvblox·라이다·전역, 6 장면) | 10-02 §9 |
| [`render_cand_clear.py`](../../debug_log/2026-10-02/jobs/render_cand_clear.py) | 10-02 §5: 지울 후보 그림 — 회색 = 지도 점유(증거 부족), 검정 = 확인된 벽(라이다 hit ≥ 3), 주황 = 후보 B(라이다만), 초록 = A(라이다+nvblox) | — |
| [`render_cand_label.py`](../../debug_log/2026-10-02/jobs/render_cand_label.py) | 10-02 §5: 지울 후보 묶음 번호 그림(3 칸 이상) + 병목 세 곳(점선 원) | — |
| [`render_corner.py`](../../debug_log/2026-10-02/jobs/render_corner.py) | 10-02 §7: f2b3 남서 구석 정체 — 4 장면(로컬 코스트맵(odom→map 변환)·라이다·차체·경로) | 10-02 §7 |
| [`render_day1002.py`](../../debug_log/2026-10-02/jobs/render_day1002.py) | 10-02 하루 실험 시각화 — rf2o·회전 미끄러짐·번짐·R2 A/B | 10-02 §15 |
| [`render_ekfB_slip.py`](../../debug_log/2026-10-02/jobs/render_ekfB_slip.py) | 10-02 §16: rf2o 로 vx·vy 를 보정한 EKF B 가 회전 미끄러짐을 실제로 따라갔나 — rot3(줄자 있음)·rot2 | 10-02 §16 |
| [`render_hole_fill.py`](../../debug_log/2026-10-02/jobs/render_hole_fill.py) | 10-02 §1: office_v2 vs 후보(cand_1002_f2a12_c276_nolc) — 남쪽 통로 구멍이 메워졌나, 옛 벽이 움직였나 | — |
| [`render_locjump.py`](../../debug_log/2026-10-02/jobs/render_locjump.py) | 10-02 §2: f2a12 위치 추정 재생 — map→odom x 시계열(라이브 기록 vs 재생 3 조합) | 10-02 §2.1 |
| [`rf2o_cmp.py`](../../debug_log/2026-10-02/jobs/rf2o_cmp.py) | 10-02 §13 R1: rf2o 재생 결과 vs SLAM(map 자세) vs EKF(odom 자세) — 회전 시험 동안 위치 변화·회전 추적 | 10-02 §13.1 |
| [`rf2o_fix.py`](../../debug_log/2026-10-02/jobs/rf2o_fix.py) | 10-02 §13 R1b: rf2o 속도의 좌표 보정 검증 — v_base = R(라이다 yaw)·v_rf2o − ω × r_lidar, 자이로(EKF) yaw 로 적분 | 10-02 §13.2 |
| [`rf2o_lever.py`](../../debug_log/2026-10-02/jobs/rf2o_lever.py) | 10-02 §18: rf2o 단독 자세의 출렁임이 실제 차체 움직임인지, 라이다 위치(중심 앞 0.152 m)의 원운동인지 확인 | 10-02 §18 |
| [`rot_models.py`](../../debug_log/2026-10-02/jobs/rot_models.py) | 10-02 §8: 제자리 회전 구간에서 주행계 이동 모델 비교 — 기준 = SLAM(map) 이동 D (09-29 §3.1: 회전 중 SLAM 오차 1~2 cm) | 10-02 §8.2 |
| [`run_f0.sh`](../../debug_log/2026-10-02/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_f2b2.sh`](../../debug_log/2026-10-02/jobs/run_f2b2.sh) | 10-02 §6.2: 목표 문자열을 파일 안에 적어 wsl 인자 분리 문제를 피함(f2b1 실수). 인자: NAME GOALS_KEY(rest\|full) | 10-02 §6.3 · 10-02 §7.2 |
| [`run_x805.sh`](../../debug_log/2026-10-02/jobs/run_x805.sh) |  | — |
| [`run_x810.sh`](../../debug_log/2026-10-02/jobs/run_x810.sh) | 10-02 §6: 재부팅 뒤 보조 스크립트 재전송(실행 안 함) | 10-02 §6 |
| [`run_x840.sh`](../../debug_log/2026-10-02/jobs/run_x840.sh) |  | — |
| [`smear_layers.py`](../../debug_log/2026-10-02/jobs/smear_layers.py) | 10-02 §10: 회전 중 번짐 층 분리 — 서쪽 구조물(y −5.95~−5.35, x −2.1~−1.6)의 안쪽 면(가장 큰 x)을 층별로 | 10-02 §10 |
| [`smear_rot.py`](../../debug_log/2026-10-02/jobs/smear_rot.py) | 10-02 §11: 통제 회전 시험 번짐 — 차체 기준 좌표로 라이다(진실)·로컬 치명·nvblox 장애의 외곽 최근접 거리, 옛 칸 수 | 10-02 §11.1 · 10-02 §12 |
| [`wait819.sh`](../../debug_log/2026-10-02/jobs/wait819.sh) |  | 10-02 §8.1 |

## 2026-10-06 (36)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`job240_clean.sh`](../../debug_log/2026-10-06/jobs/job240_clean.sh) | ── 깨끗한 기동 절차 (2026-09-11 제정) ─────────────────────────────────────── | 09-11 5.4 · 09-11 5.7 · 09-11 중복 프로세스 (사용자 지적 "중첩된 프로세스가 있어 충돌이 일어나지 않 · … +10 |
| [`job726_prep_map.sh`](../../debug_log/2026-10-06/jobs/job726_prep_map.sh) | 10-01 §5·§7: 지도 불러오기 prep — 기본 office_v3(10-02 §4, 이전 office_v2)(출발 테이프 = 0,0,0). 인자/환경: | 10-01 §5 · 10-01 §7 · 10-02 §4 · … +1 |
| [`job850_deploy.sh`](../../debug_log/2026-10-06/jobs/job850_deploy.sh) | 10-06 R3: rover_bringup(rf2o_gate.py·rf2o.yaml·ekf.launch.py·CMakeLists) 배포·빌드, 재생용 bag 풀기 | — |
| [`job851_r3chk.sh`](../../debug_log/2026-10-06/jobs/job851_r3chk.sh) | 10-06 R3 정지 기동 확인: rf2o·게이트·그림자 EKF 동작, 발행률, 게이트 판정, CPU(10 s) | — |
| [`job852_prep_rf2o.sh`](../../debug_log/2026-10-06/jobs/job852_prep_rf2o.sh) | 10-06 R3: rf2o·그림자 EKF 켠 prep | 10-06 §3 |
| [`job853_step_init.sh`](../../debug_log/2026-10-06/jobs/job853_step_init.sh) | 10-06 §4: 단계별 회전 실측 — bag 기록 시작(/imu/data 포함) + init | — |
| [`job854_step.sh`](../../debug_log/2026-10-06/jobs/job854_step.sh) |  | — |
| [`job856_end.sh`](../../debug_log/2026-10-06/jobs/job856_end.sh) |  | — |
| [`job860_t1.sh`](../../debug_log/2026-10-06/jobs/job860_t1.sh) | 10-06 §9 T1: bag 기록 + 정지 관찰 60 s(사람이 움직임) + 게이트 판정 변화 | 10-06 §9 |
| [`job861_t1scan.py`](../../debug_log/2026-10-06/jobs/job861_t1scan.py) | 10-06 §9 T1 확인: 사람 움직임이 라이다에 실제로 보였나 — 2 m 안 점 중 첫 스캔과 5 cm 넘게 다른 점 수(스캔별)·각도 범위 | 10-06 §9.1 |
| [`job862_t1b_start.sh`](../../debug_log/2026-10-06/jobs/job862_t1b_start.sh) | 10-06 §9.2 T1b: 정지 + 사용자가 몸으로 라이다 시야 약 70 % 를 가림 — 백그라운드로 90 s 기록·관찰(시작 알림 뒤 사용자가 가림) | — |
| [`job863_t1bscan.py`](../../debug_log/2026-10-06/jobs/job863_t1bscan.py) | 10-06 §9 T1 확인: 사람 움직임이 라이다에 실제로 보였나 — 2 m 안 점 중 첫 스캔과 5 cm 넘게 다른 점 수(스캔별)·각도 범위 | — |
| [`job864_occ.sh`](../../debug_log/2026-10-06/jobs/job864_occ.sh) | 10-06 §10: 가림 0·0.15·0.3·0.5·0.7 를 도메인 51~55 에서 동시에(각자 /clock), bag_step1(2021 s) | 10-06 §10 |
| [`job870_occmove.sh`](../../debug_log/2026-10-06/jobs/job870_occmove.sh) | 10-06 §11: 움직이는 몸 5 조건(도메인 61~65) — 인자: 이름 coverage center_deg rho '추가 매개' | 10-06 §11 |
| [`job871_qcal.sh`](../../debug_log/2026-10-06/jobs/job871_qcal.sh) | 10-06 §12 G3 보정: q 를 기록만(log) — 깨끗(0 %)·정적 몸 50 %·움직이는 C·E·다리 A, 도메인 71~75 | 10-06 §12 |
| [`job876_g4.sh`](../../debug_log/2026-10-06/jobs/job876_g4.sh) | 10-06 §12.1: G4(회전 중 병진 타당성) 켜고 5 조건, 도메인 81~85 — 1 분마다 진행 줄(current.log 에 보이게) | 10-06 §12 · 10-06 §13 · 10-07 §1 |
| [`occ_eval.py`](../../debug_log/2026-10-06/jobs/occ_eval.py) | 10-06 §10: 합성 가림 결과 — 단계 정지 시점마다 오른쪽 앞끝 예측 대각 거리 − 줄자 | — |
| [`occ_kill.sh`](../../debug_log/2026-10-06/jobs/occ_kill.sh) | 합성 가림 재생 정리 — PID 로만(이름 pkill 은 자기 자신·라이브 스택을 죽일 수 있음) | 10-06 §10.1 |
| [`occ_rec.py`](../../debug_log/2026-10-06/jobs/occ_rec.py) | 10-06 §10: 합성 가림 재생 기록 — 시험 EKF B(/odometry/filtered), 진실 대용(/truth_odom), /cmd_vel. 인자: OUT SEC | 10-06 §10 |
| [`occ_run.sh`](../../debug_log/2026-10-06/jobs/occ_run.sh) | 10-06 §10: 합성 가림 1 조건 — 인자 DOMAIN COVERAGE OUT [CENTER_DEG RHO] | 10-06 §10 |
| [`occ_scan.py`](../../debug_log/2026-10-06/jobs/occ_scan.py) | 10-06 §10 T2 합성: bag 스캔(/scan_in)에 '바닥에 고정된 사람 몸'을 그려 /scan 으로 — 회전 중 가림이 rf2o·EKF 를 흔드는가. | 10-06 §10 · 10-06 §11 |
| [`occm_eval.py`](../../debug_log/2026-10-06/jobs/occm_eval.py) | 10-06 §10: 합성 가림 결과 — 단계 정지 시점마다 오른쪽 앞끝 예측 대각 거리 − 줄자 | — |
| [`r3_eval.py`](../../debug_log/2026-10-06/jobs/r3_eval.py) | 10-02 §14 R2 판정 계산 — EKF A/B(+ 라이브 EKF) 를 줄자·SLAM·구석 벽 일관성으로 비교 | 10-06 §2 |
| [`r3_rec.py`](../../debug_log/2026-10-06/jobs/r3_rec.py) | 10-06 R3: 정식 ekf.launch(rf2o:=true shadow:=true) 재생 검증 기록기 — /odometry/filtered(B), /odometry/ekf_a(A). 인자: OUT SEC | 10-06 §2 |
| [`r3_replay.sh`](../../debug_log/2026-10-06/jobs/r3_replay.sh) | 10-06 R3: 정식 ekf.launch.py(rf2o:=true shadow:=true use_sim_time:=true)를 도메인 42 에서 bag 재생으로 검증. 인자: BAG OUT | 10-06 §2 · 10-06 §5.1 |
| [`render_day1006.py`](../../debug_log/2026-10-06/jobs/render_day1006.py) | 10-06 하루 시각화: ① 합성 가림 조건별 EKF B 오차(정적·움직이는 몸) ② 원위치 단계 오차 누적 ③ 회전 중 rf2o 병진 속도 분포(G4 근거) ④ G3 q 분포(기각 근거) | 10-06 §13 |
| [`render_step1.py`](../../debug_log/2026-10-06/jobs/render_step1.py) | 10-06 §4: 단계별 회전 실측 결과 — 각 단계에서 오른쪽 앞끝의 예측 위치(EKF B·A·SLAM)와 줄자 대각 거리(원) | 10-06 §4.1 |
| [`run_step.sh`](../../debug_log/2026-10-06/jobs/run_step.sh) | 사용: run_step.sh init \| +90 \| -90 | — |
| [`run_step2.sh`](../../debug_log/2026-10-06/jobs/run_step2.sh) |  | — |
| [`run_x850.sh`](../../debug_log/2026-10-06/jobs/run_x850.sh) |  | — |
| [`run_x851.sh`](../../debug_log/2026-10-06/jobs/run_x851.sh) |  | — |
| [`run_x856.sh`](../../debug_log/2026-10-06/jobs/run_x856.sh) |  | — |
| [`run_x864.sh`](../../debug_log/2026-10-06/jobs/run_x864.sh) |  | — |
| [`run_x870.sh`](../../debug_log/2026-10-06/jobs/run_x870.sh) |  | — |
| [`step_rot.py`](../../debug_log/2026-10-06/jobs/step_rot.py) | 10-06 §4 단계별 회전 실측(10-02 §17 사용자 제안): 한 번 실행 = 제자리 90° 한 단계(또는 init). | 10-06 §4 |
| [`t1_still.py`](../../debug_log/2026-10-06/jobs/t1_still.py) | 10-06 §9 T1: 로버 정지 + 사람 이동 — SEC 초 동안 EKF B·A·rf2o 원 자세·게이트 판정 변화. 인자: SEC | 10-06 §9 |

## 2026-10-07 (74)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`box_step.py`](../../debug_log/2026-10-07/jobs/box_step.py) | 10-07 §8.3 전역 카메라 STVL 층 실측 — 한 번 실행 = 한 단계. 상자 ②(map x 1.1~1.3, y −0.1~+0.1)·상자 ①(1.3~1.6, −0.45~−0.3) 칸 수를 | 10-07 §8.3 |
| [`box_vis.py`](../../debug_log/2026-10-07/jobs/box_vis.py) | 10-07 §8: 상자 ②(map x 1.1~1.3, y −0.1~+0.1) 가 전역 코스트맵에 언제 있고 언제 사라지나 — 로버 거리·카메라 화각 안 여부와 함께 | 10-07 §8.1 |
| [`cap_box.json`](../../debug_log/2026-10-07/jobs/cap_box.json) |  | — |
| [`cap_corner.json`](../../debug_log/2026-10-07/jobs/cap_corner.json) |  | — |
| [`cap_corridor.json`](../../debug_log/2026-10-07/jobs/cap_corridor.json) |  | — |
| [`compose_sc.sh`](../../debug_log/2026-10-07/jobs/compose_sc.sh) | 10-07 §9: 실제 영상(세로 4K) 구간 → 406×720·30 fps, 데이터 영상(720×720·10 fps) 과 좌우 결합. (Git Bash ffmpeg 의 drawtext 는 fontconfig 로 죽어 라벨은 PNG 오버레이) | 10-07 §9 |
| [`f2c2_boxgap.py`](../../debug_log/2026-10-07/jobs/f2c2_boxgap.py) | 10-07 §2.5: 상자(카메라만 본 치명 칸 묶음, map x 1.25~1.75 · y −0.55~−0.2) ↔ 차체 외곽 거리, 그리고 계획 경로 대비 옆 벗어남·방향 차(1 s 마다) | 10-07 §2.6 |
| [`f2c2_w3ahead.py`](../../debug_log/2026-10-07/jobs/f2c2_w3ahead.py) | 10-07 §3.3: W3 통로 — 진행 방향 앞 띠(차체 폭 ±0.27 m, 앞 0~1.2 m)의 치명·고비용 칸: 정리(t≈235) 전후, 라이다 근거 유무 | — |
| [`f2c2_w3cost.py`](../../debug_log/2026-10-07/jobs/f2c2_w3cost.py) | 10-07 §3.3: f2c2 W3 통로 구간 — 로컬 코스트맵 치명 칸이 통로를 좁혔나(정리 11:12:09 = 러너 t≈235 전후 비교), 라이다 근거 유무 | — |
| [`f2c2_w3lat.py`](../../debug_log/2026-10-07/jobs/f2c2_w3lat.py) | 10-07 §5: W3 떨림 구간 — 계획 경로 대비 옆 벗어남·방향 차(4 s 마다), 쓰인 계획 시각 | 10-07 §5 |
| [`f2c_anal.py`](../../debug_log/2026-10-07/jobs/f2c_anal.py) | 10-07 §3: f2c1·f2c2 — ③-b 회전 구간 번짐(EKF B·그림자 A 대 SLAM), ③-c 게이트 비용, rf2o 발행률, map→odom 보정이 어디서 쌓였나 | — |
| [`f2c_g4arc.py`](../../debug_log/2026-10-07/jobs/f2c_g4arc.py) | 10-07 §3: G4 가 주행 중 곡선(전진하며 회전)에서 정상 전진 속도를 오염으로 보는가 — 회전 표본을 EKF B 전진 속도로 나눠 σ 키움·버림 비율 | — |
| [`fuse_all.sh`](../../debug_log/2026-10-07/jobs/fuse_all.sh) | 10-07 §9.2: 영상 6 개 전부 — 실제 영상(4K 세로) → 406×720·30 fps 로 먼저 줄이고(한 그래프로 하면 hstack 입력 높이 0 오류), RViz 풍 데이터(720×720) 와 좌우 결합 | 10-07 §9.2 |
| [`g4_eval.py`](../../debug_log/2026-10-07/jobs/g4_eval.py) | 10-07 §1: G4 켠 합성 가림 결과(occm_eval.py 와 같은 계산, 입력만 g4/) | — |
| [`g4_why.py`](../../debug_log/2026-10-07/jobs/g4_why.py) | 10-07 §1: G4 켠 뒤 남은 오차의 성격 — 회전 구간마다 진실 대용(T) 이동 vs 시험 B 이동(시작 자세 기준, cm). | 10-07 §1.1 |
| [`g4ref_offline.py`](../../debug_log/2026-10-07/jobs/g4ref_offline.py) | 10-07 §4 A(오프라인): 10-06 보정 재생 csv(합성 5 조건, bag_step1 = 제자리 회전 시험)에서 G4 판정량 abs vs wheel — 판정(통과·σ 배수·버림)이 바뀌는 회전 표본 수 | 10-07 §4.1 |
| [`get901.sh`](../../debug_log/2026-10-07/jobs/get901.sh) |  | — |
| [`get915.sh`](../../debug_log/2026-10-07/jobs/get915.sh) | 10-07 §4: 재생 결과 회수(인자 = 파일 이름들) | — |
| [`job550_f0run.py`](../../debug_log/2026-10-07/jobs/job550_f0run.py) | F0 코스 확장 러너 (2026-09-23): 상자 코스와 무관한 연속 목표 주행 + 왕복 복귀 오차 계측. | 09-23 16 · 09-28 §12 · 09-28 §16 · … +5 |
| [`job551_f0drive.sh`](../../debug_log/2026-10-07/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`job726_prep_map.sh`](../../debug_log/2026-10-07/jobs/job726_prep_map.sh) | 10-01 §5·§7: 지도 불러오기 prep — 기본 office_v3(10-02 §4, 이전 office_v2)(출발 테이프 = 0,0,0). 인자/환경: | 10-01 §5 · 10-01 §7 · 10-02 §4 · … +1 |
| [`job876_g4.sh`](../../debug_log/2026-10-07/jobs/job876_g4.sh) | 10-06 §12.1: G4(회전 중 병진 타당성) 켜고 5 조건, 도메인 81~85 — 1 분마다 진행 줄(current.log 에 보이게) | 10-06 §12 · 10-06 §13 · 10-07 §1 |
| [`job900_chk.sh`](../../debug_log/2026-10-07/jobs/job900_chk.sh) | 10-07 시작 점검: 가동 시간, 스택 프로세스, 재생에 필요한 파일 | — |
| [`job902_load.sh`](../../debug_log/2026-10-07/jobs/job902_load.sh) | 10-07: G4 재생 5 개 동시 중 Jetson 부하(배속 가능 여부 판단용, 읽기만) | 10-07 §1.0 |
| [`job903_prep_rf2o_g4.sh`](../../debug_log/2026-10-07/jobs/job903_prep_rf2o_g4.sh) | 10-07 §2: rf2o + G4 + 그림자 EKF A 켠 prep(위치 추정 office_v3·Nav2) — 로버 안 움직임 | 10-07 §2 |
| [`job905_peek.sh`](../../debug_log/2026-10-07/jobs/job905_peek.sh) | 10-07: prep 진행 확인(읽기만) | — |
| [`job906_net.sh`](../../debug_log/2026-10-07/jobs/job906_net.sh) | 10-07: 연결 끊김 진단(읽기만) — 가동 시간, 현재 Wi-Fi, 끊김 기록 | 10-07 §2.1 |
| [`job907_postchk.sh`](../../debug_log/2026-10-07/jobs/job907_postchk.sh) | 10-07 §2: prep 뒤 확인(읽기만) — Nav2 상태, rf2o·게이트 발행률, 정지 중 CPU | 10-07 §2.1 |
| [`job908_g4log.sh`](../../debug_log/2026-10-07/jobs/job908_g4log.sh) | 10-07 §2: f2c1 목표 4(남서) 취소 원인 — nav2 로그(11:00:30 이후, 읽기만) | — |
| [`job909_cmdnow.sh`](../../debug_log/2026-10-07/jobs/job909_cmdnow.sh) | 10-07: 지금 움찔댐 — /cmd_vel 발행자·현재 값·Nav2 활성 목표 확인(읽기만) | 10-07 §2.3 |
| [`job910_g4cost.py`](../../debug_log/2026-10-07/jobs/job910_g4cost.py) | 10-07 §2.3: f2c1 목표 4(남서) 정체 — 로컬 코스트맵이 차체를 가뒀나. 1 s 마다: | 10-07 §2.3 |
| [`job910_run.sh`](../../debug_log/2026-10-07/jobs/job910_run.sh) | 10-07 §2.3: f2c1 bag 에서 목표 4 구간(11:00:50~11:02:15) 로컬 코스트맵·라이다·cmd_vel 추출(읽기만) | — |
| [`job911_navtail.sh`](../../debug_log/2026-10-07/jobs/job911_navtail.sh) | 10-07 §2.4: 주행 중 관찰(사용자: 전진하며 이상하게 움직임) — 로그만 읽음(DDS 참여자 만들지 않음) | 10-07 §2.4 |
| [`job912_extract.py`](../../debug_log/2026-10-07/jobs/job912_extract.py) | 10-07 §2.5: f2c2 bag 추출(시각화용) — 지도 자세 궤적(map→odom∘odom→base_link, EKF B), 그림자 A(odom), /plan 전부, 전역 코스트맵(2 s 간격), | 10-07 §2.6 |
| [`job912_run.sh`](../../debug_log/2026-10-07/jobs/job912_run.sh) | 10-07 §2.5: f2c2 목표 5·6 구간 추출(읽기만, 1~2 분) | — |
| [`job913_extract.py`](../../debug_log/2026-10-07/jobs/job913_extract.py) | 10-07 §3: f2c 주행 bag 전체 추출(③-b 번짐·③-c 게이트·보정량) — map→odom, odom→base(EKF B), 그림자 A, EKF B 속도, rf2o 원·게이트 출력(+공분산), cmd_vel, /plan 시각. | — |
| [`job913_run.sh`](../../debug_log/2026-10-07/jobs/job913_run.sh) | 10-07 §3: f2c1·f2c2 bag 추출(읽기만, 2~4 분) | — |
| [`job914_w3log.sh`](../../debug_log/2026-10-07/jobs/job914_w3log.sh) | 10-07 §3.3: f2c2 W3 구간(러너 t 176~240 ≈ epoch 1791339070~1791339135) nav2 로그 전부(Message Filter 제외, 읽기만) | — |
| [`job915_rp.sh`](../../debug_log/2026-10-07/jobs/job915_rp.sh) | 10-07 §4 B: f2c2 bag(430 s) 재생 — G4 abs(라이브 재현 확인) vs wheel(잔차) 동시, 도메인 91·92, 약 8 분, 로버 안 움직임. 1 분마다 진행 줄 | 10-07 §4.1 |
| [`job917_run.sh`](../../debug_log/2026-10-07/jobs/job917_run.sh) | 10-07 §5: W3 떨림 TF 지연 — bag 분석 + 11:12:09 외삽 오류 원문(읽기만, 1~2 분) | 10-07 §5 |
| [`job917_tflag.py`](../../debug_log/2026-10-07/jobs/job917_tflag.py) | 10-07 §5: f2c2 W3 떨림(러너 t 188~236) — TF·토픽 stamp 지연(bag 수신 시각 − header stamp)과 stamp 간격을 6 s 창별로. | 10-07 §5 |
| [`job918_prep.sh`](../../debug_log/2026-10-07/jobs/job918_prep.sh) | 10-07 §6: rf2o + G4(휠 잔차) + 그림자 A + MPPI transform_tolerance 0.5 prep — 로버 안 움직임 | 10-07 §11 |
| [`job919_chk.sh`](../../debug_log/2026-10-07/jobs/job919_chk.sh) | 10-07 §6: 실행 중 노드가 새 설정을 쓰는가(읽기만) | 10-07 §6.1 |
| [`job920_chk.sh`](../../debug_log/2026-10-07/jobs/job920_chk.sh) | 10-07 §6: 어느 컨트롤러 플러그인이 FollowPath 인가(읽기만) | 10-07 §6.1 |
| [`job921_run.sh`](../../debug_log/2026-10-07/jobs/job921_run.sh) | 10-07 §7: f2d2 목표 10(출발 복귀) 상자 앞 정지 — nav2 로그 + bag 추출(읽기만, 1~2 분) | — |
| [`job922_prep.sh`](../../debug_log/2026-10-07/jobs/job922_prep.sh) | 10-07 §8.2: 전역 카메라 STVL 층(global_camera:=stvl) prep — rf2o·G4 잔차 그대로. 로버 안 움직임 | 10-07 §8.2 |
| [`job923_rec.sh`](../../debug_log/2026-10-07/jobs/job923_rec.sh) | 10-07 §8.3: 상자 시험 녹화 시작\|끝 — 카메라 점군 포함(오프라인 A/B: 옛 구성 vs STVL 을 같은 입력으로 다시 계산하려고) | 10-07 §8.3 |
| [`job925_chk.sh`](../../debug_log/2026-10-07/jobs/job925_chk.sh) | 10-07 §8.3: 전역 STVL 이 상자를 왜 안 표시하나(읽기만) — 점군 발행률·상자 근처 점 수·로컬 코스트맵·STVL 로그 | 10-07 §8.4 |
| [`job926_gc.py`](../../debug_log/2026-10-07/jobs/job926_gc.py) | 10-07 §8.3: 전역 코스트맵 상자 근처 값과 발행 간격(읽기만) — 두 구독 방식(최초 래치 vs 이후 갱신) 비교 | 10-07 §8.4 |
| [`job927_csv.sh`](../../debug_log/2026-10-07/jobs/job927_csv.sh) | 10-07 §8.4: 단계 4 csv 최근 값(읽기만) — 2 s 간격으로 줄임 | — |
| [`job928_pts.py`](../../debug_log/2026-10-07/jobs/job928_pts.py) | 10-07 §8.4: 상자 ② 자리(map x 1.05~1.35, y −0.30~+0.10)에 지금 카메라 점(z 0.06~0.40)이 있나 — 5 s 동안 프레임별 점 수(읽기만) | — |
| [`job929_bagpts.py`](../../debug_log/2026-10-07/jobs/job929_bagpts.py) | 10-07 §8.4: 상자 ② 자리(map x 1.05~1.35, y −0.30~+0.10)의 카메라 점 수를 bag_box1 에서 2 s 마다 — 치우기 전후. | 10-07 §8.5 |
| [`job930_extract.py`](../../debug_log/2026-10-07/jobs/job930_extract.py) | 10-07 §9 쇼케이스 영상용 추출(job912 변형: 스캔 0.2 s·로컬 0.5 s 간격) — 지도 자세 궤적(map→odom∘odom→base_link, EKF B), 그림자 A(odom), /plan 전부, 전역 코스트맵(2 s 간격), | 10-07 §9 |
| [`job930_run.sh`](../../debug_log/2026-10-07/jobs/job930_run.sh) | 10-07 §9: 쇼케이스 영상용 bag 구간 추출(읽기만) — 시각은 Jetson epoch(13:11:37 KST = 1791346297) | 10-07 §9 |
| [`job931_run.sh`](../../debug_log/2026-10-07/jobs/job931_run.sh) | 10-07 §9.2: 영상 6 개 전체 구간 bag 추출(읽기만) — f2d1 13:02:50~13:06:30, f2d2 13:11:35~13:19:00 | 10-07 §9.2 |
| [`job932_topics.sh`](../../debug_log/2026-10-07/jobs/job932_topics.sh) | 10-07 §11: 컨트롤러가 내는 시각화 토픽 확인(읽기만) | 10-07 §11 |
| [`job933_nvslice.py`](../../debug_log/2026-10-07/jobs/job933_nvslice.py) | 10-07 §16: 상자 시험 bag(bag_box1)의 nvblox 슬라이스로 — 같은 장면에서 nvblox 가 '가까이서 기억(C1)'·'치운 뒤 갱신(C2)' 을 만족했나(읽기만). | 10-07 §16 · 10-08 §1 |
| [`occ_run.sh`](../../debug_log/2026-10-07/jobs/occ_run.sh) | 10-06 §10: 합성 가림 1 조건 — 인자 DOMAIN COVERAGE OUT [CENTER_DEG RHO] | 10-06 §10 |
| [`plan_vs_box.py`](../../debug_log/2026-10-07/jobs/plan_vs_box.py) | 10-07 §10: fused_131646 구간 — 로컬(nvblox) 은 상자를 보는데 계획 경로가 그 위를 지나는가, 그때 전역 코스트맵(계획기가 보는 것)의 상자 칸 값은 | 10-07 §10.1 |
| [`render_f2c2_box.py`](../../debug_log/2026-10-07/jobs/render_f2c2_box.py) | 10-07 §2.5: f2c2 복귀 마지막 구간 — 라이다 점(지도 좌표)으로 상자 위치, 차체 외곽(2 s 마다), 계획 경로, 외곽 ↔ 라이다 최근접 시계열 | — |
| [`render_f2c2_box2.py`](../../debug_log/2026-10-07/jobs/render_f2c2_box2.py) | 10-07 §2.5: 복귀 마지막 60 s — 로컬 코스트맵 치명 칸(라이다+nvblox, map 좌표로)을 라이다 점과 겹침 → 라이다에 없는 치명 칸 = 카메라만 본 낮은 물체(상자 후보) | 10-07 §2.6 |
| [`render_f2c2_g6.py`](../../debug_log/2026-10-07/jobs/render_f2c2_g6.py) | 10-07 §2.5: f2c2 마지막 목표(출발 복귀) — 계획 경로(시각별)와 실제 궤적, 전역 코스트맵 위 상자. 사용자 관찰 "상자를 피하는 경로였는데 다시 상자 쪽으로 틀어 돌아옴" 확인 | — |
| [`render_f2d2_box2.py`](../../debug_log/2026-10-07/jobs/render_f2d2_box2.py) | 10-07 §2.5: 복귀 마지막 60 s — 로컬 코스트맵 치명 칸(라이다+nvblox, map 좌표로)을 라이다 점과 겹침 → 라이다에 없는 치명 칸 = 카메라만 본 낮은 물체(상자 후보) | 10-07 §7.1 |
| [`render_rviz.py`](../../debug_log/2026-10-07/jobs/render_rviz.py) | 10-07 §9.2 RViz 풍 bag 시각화(사용자 지정 스타일) — 720×720, 10 fps(실제 속도), 로버 진행 방향이 위(RViz 고정 프레임 base_link 처럼). | 10-07 §9.2 · 10-07 §10.2 · 10-07 §11 · … +1 |
| [`render_sc.py`](../../debug_log/2026-10-07/jobs/render_sc.py) | 10-07 §9 쇼케이스: bag 구간(job930_extract npz) → 위에서 본 데이터 영상(720×720, 10 fps = 실제 속도). | 10-07 §9 |
| [`rp_eval.py`](../../debug_log/2026-10-07/jobs/rp_eval.py) | 10-07 §4 B: f2c2 재생 abs vs wheel — 게이트 csv 로 회전 표본(제자리·곡선)의 G4 σ 키움·버림 비율, 재생 EKF B 와 라이브 B 궤적 차 | 10-07 §4.1 |
| [`rp_run.sh`](../../debug_log/2026-10-07/jobs/rp_run.sh) | 10-07 §4: 주행 bag 재생(가림 합성 없음) — 인자 DOMAIN BAG OUT. 환경 GV(gate_v) GVREF(gate_vref). 라이브 EKF B 는 /truth_odom 으로 기록 | 10-07 §4.1 |
| [`run_f0.sh`](../../debug_log/2026-10-07/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_f2c.sh`](../../debug_log/2026-10-07/jobs/run_f2c.sh) | 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5] | 10-07 §2.1 · 10-07 §2.2 · 10-07 §2.4 · … +31 |
| [`run_jn.sh`](../../debug_log/2026-10-07/jobs/run_jn.sh) | 범용 러너(10-07 재작성 — 스크래치패드 사본 소실, 09-28 판 + JX_WHY 실시간 로그): $1 = 스크립트, 나머지 = 인자. 환경 JETSON_HOST, JX_TIMEOUT, JX_WHY | 09-28 3.3 · 10-07 §1.0 · 10-08 §5 · … +3 |
| [`up901.sh`](../../debug_log/2026-10-07/jobs/up901.sh) | 10-07: 재부팅 뒤 G4 재생 준비 — bag_step1·합성 스크립트·게이트 소스 업로드, 빌드, bag 풀기 | 10-07 §1.0 |
| [`up904.sh`](../../debug_log/2026-10-07/jobs/up904.sh) | 10-07 §2: 재부팅 뒤 보조 스크립트 재전송(실행 안 함) | 10-07 §2 · 10-07 §2.1 |
| [`up916.sh`](../../debug_log/2026-10-07/jobs/up916.sh) | 10-07 §4: 재부팅 뒤 재생 준비(호스트 인자) — bag_step1·합성·주행 재생 스크립트·게이트 소스 업로드, 빌드 | — |
| [`up918.sh`](../../debug_log/2026-10-07/jobs/up918.sh) | 10-07 §6: nav2_params(transform_tolerance 0.5) 배포·빌드 | — |

## 2026-10-08 (29)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`box_align.py`](../../debug_log/2026-10-08/jobs/box_align.py) | 10-08 §3.7: 복귀 구간 상자 ② — 로컬(MPPI)·전역(계획기) 지도의 상자 칸 위치 비교, 경로 ↔ 상자, 차체 ↔ 상자. 인자: npz 시작HH:MM:SS 끝HH:MM:SS | 10-08 §3.7 |
| [`contact_eval.py`](../../debug_log/2026-10-08/jobs/contact_eval.py) | 10-08 §3.5: f2e1 상자 ② 접촉 — 복귀 구간 0.5 s 마다 로컬 코스트맵(MPPI 가 보는 지도)의 상자 자리 치명·내접 칸, 차체 외곽 안 칸, 로버 자세·지령, MPPI 최적 궤적이 상자 칸과 겹치나 | 10-08 §3.5 |
| [`extract_pc.py`](../../debug_log/2026-10-08/jobs/extract_pc.py) | 10-08 §3.4: PC 판 bag 추출(rosbags) — render_rviz.py 와 같은 키 + MPPI 후보·최적 궤적(/trajectories, odom). 인자: bag 출력.npz | 10-08 §3.4 |
| [`f2e_eval.py`](../../debug_log/2026-10-08/jobs/f2e_eval.py) | 10-08 §3.3: f2e1(B: 전역 nvblox + 재계획 0.5 Hz) — 상자 ②: nvblox 첫 표시 → 상자를 피하는 새 경로까지 시간, 경로 ↔ 상자 칸 거리; 재계획 수·경로 옆 변화 | 10-08 §3.3 |
| [`f2e_gcm.py`](../../debug_log/2026-10-08/jobs/f2e_gcm.py) | 10-08 §3.3: 복귀 구간 전역 코스트맵(계획기)과 로컬 코스트맵에 상자 ② 가 들어갔나 — x 0.9~1.6 · y −0.4~0.4 단면 | 10-08 §3.3 |
| [`job934_prep.sh`](../../debug_log/2026-10-08/jobs/job934_prep.sh) | 10-08 §3: 전역 nvblox + 주기 재계획 0.5 Hz prep(B) — rf2o·G4 잔차·그림자 A, 순회라 MPPI 궤적 발행. 로버 안 움직임 | 10-08 §3 |
| [`job936_chk.sh`](../../debug_log/2026-10-08/jobs/job936_chk.sh) | 10-08 §3: B 구성 확인(읽기만) — MPPI visualize·/trajectories 발행·Nav2 상태 | 10-08 §3.2 |
| [`job937_src.sh`](../../debug_log/2026-10-08/jobs/job937_src.sh) | 10-08 §3.3: nvblox_nav2 층의 프레임 파라미터 기본값·사용처(읽기만) | 10-08 §3.3 |
| [`job940_ratio.py`](../../debug_log/2026-10-08/jobs/job940_ratio.py) | 트랙 속도 비율 통제 시험 (2026-10-08 §5): 회전 방식(느린/빠른 트랙 비 r)에 따라 회전 미끄러짐이 어떻게 달라지는지 잰다. | 10-08 §5 · 10-08 §5.1 |
| [`job941_ratiodrive.sh`](../../debug_log/2026-10-08/jobs/job941_ratiodrive.sh) | 트랙 비율 통제 시험 래퍼(Jetson, 10-08 §5): 게이트 A(프로세스)·B(보드)·C(SLAM) → 30 s(DDS 규칙) → bag → job940 → 메타(job453). | 10-08 §5 · 10-08 §5.6 |
| [`job942_chk.sh`](../../debug_log/2026-10-08/jobs/job942_chk.sh) | 10-08 §5 시험 전 확인(로버 안 움직임): 프로세스·정체 감시 모드·보드·로버 위치(map)·차체 중심 기준 라이다 최근접·방향별 최근접 | 10-08 §5.1 |
| [`job943_shadow.sh`](../../debug_log/2026-10-08/jobs/job943_shadow.sh) |  | — |
| [`job944_fwdsim.sh`](../../debug_log/2026-10-08/jobs/job944_fwdsim.sh) | 10-08 §6: 앞 회전 우선 — MPPI 오프라인 시뮬(job776 = 실측 구동계 모델 + 경로·로컬 코스트맵 bag 재생). 로버 안 움직임. | 10-08 §6 · 10-13 §7 |
| [`job946_fwdseed.sh`](../../debug_log/2026-10-08/jobs/job946_fwdseed.sh) | 10-08 §6: job944 의 F5·F15 를 seed 2·3 으로 반복(표본 잡음 확인). 로버 안 움직임. | 10-08 §6 |
| [`nv_global_whatif.py`](../../debug_log/2026-10-08/jobs/nv_global_whatif.py) | 10-08 §2: '전역에 nvblox 를 넣었다면' — 순회 bag 에서 카메라만 본 장애물 칸(유령 후보)과 상자 ② 첫 표시 시각. | 10-08 §2.1 |
| [`nvslice_pc.py`](../../debug_log/2026-10-08/jobs/nvslice_pc.py) | 10-08 §1: bag_box1 의 nvblox 슬라이스로 상자 ② 자리 장애물 칸 수(2 s 마다) — PC 에서 rosbags 로 읽음(Jetson 무응답). | 10-08 §1 |
| [`ratio_anal.py`](../../debug_log/2026-10-08/jobs/ratio_anal.py) | 10-08 §5 비율 시험 분석(PC): 회전마다 정지 스캔끼리 직접 정합(실제 이동) − 휠 추측항법 = 미끄러짐. rot2.py 와 같은 잣대. | 10-08 §5 |
| [`ratio_pool.py`](../../debug_log/2026-10-08/jobs/ratio_pool.py) | 10-08 §5.6: 실행 1·2 회전을 합쳐 §5·§5.1·§5.5 판정(V·Q0·Q1·Q2·Q3) — ratio_anal.py 의 csv 를 읽음 | 10-08 §5.6 |
| [`render_goals.py`](../../debug_log/2026-10-08/jobs/render_goals.py) | 10-08 §3: 이번 순회 목표 10 개(저장 지도 office_v3 위) — 순서·이름·판정 방식, 지난 순회(10-07 f2c1+f2c2) 실제 궤적, 상자 위치 | — |
| [`render_rviz.py`](../../debug_log/2026-10-08/jobs/render_rviz.py) | 10-07 §9.2 RViz 풍 bag 시각화(사용자 지정 스타일) — 720×720, 10 fps(실제 속도), 로버 진행 방향이 위(RViz 고정 프레임 base_link 처럼). | 10-07 §9.2 · 10-07 §10.2 · 10-07 §11 · … +1 |
| [`render_whatif.py`](../../debug_log/2026-10-08/jobs/render_whatif.py) | 10-08 §2: 카메라만 본 장애물 묶음(전역 nvblox 였다면 계획기에 들어갔을 칸)을 저장 지도 위에 번호로 — 사용자가 실제 물체인지 확인 | 10-08 §2.1 |
| [`rot2.py`](../../debug_log/2026-10-08/jobs/rot2.py) | 10-08 §4: 주행 중 '도는' 구간 전부(제자리·피벗·호) — 회전축 위치, 트랙 속도, 미끄러짐을 같은 잣대로 비교. | 10-08 §4 · 10-08 §5 · 10-08 §5.4 |
| [`rot2_stats.py`](../../debug_log/2026-10-08/jobs/rot2_stats.py) | 10-08 §4: rot2.py 결과(≥45° 회전)를 회전 종류별로 묶음. 종류는 트랙 속도로 정함(회전축 추정과 독립): | 10-08 §4 |
| [`rot_fig.py`](../../debug_log/2026-10-08/jobs/rot_fig.py) | 10-08 §4 그림: 회전축 위치(차체 좌표)와 90°당 미끄러짐, 회전 종류별 | — |
| [`run_f2c.sh`](../../debug_log/2026-10-08/jobs/run_f2c.sh) | 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5] | 10-07 §2.1 · 10-07 §2.2 · 10-07 §2.4 · … +31 |
| [`run_jn.sh`](../../debug_log/2026-10-08/jobs/run_jn.sh) | 범용 러너(10-07 재작성 — 스크래치패드 사본 소실, 09-28 판 + JX_WHY 실시간 로그): $1 = 스크립트, 나머지 = 인자. 환경 JETSON_HOST, JX_TIMEOUT, JX_WHY | 09-28 3.3 · 10-07 §1.0 · 10-08 §5 · … +3 |
| [`run_ratio.sh`](../../debug_log/2026-10-08/jobs/run_ratio.sh) | 비율 시험 PC 러너(10-08 §5, 09-28 run_spin.sh 기반): 전송(재시도 3) → job941 을 setsid nohup 으로 기동 → 로그 폴링 → 산출물 회수 | 10-08 §5 |
| [`slip_model.py`](../../debug_log/2026-10-08/jobs/slip_model.py) | 10-08 §5.11: 회전 중 '뒤로 밀림' 보정 모델 오프라인 적합(실행 1·2 40 회, 한 개 빼고 검증 LOO) | 10-08 §5.11 |
| [`up944.sh`](../../debug_log/2026-10-08/jobs/up944.sh) | 10-08 §6 시뮬 파일 전송(비밀번호는 run_jn.sh 에서 읽음) | — |

## 2026-10-12 (42)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`box_smooth.py`](../../debug_log/2026-10-12/jobs/box_smooth.py) | 10-12 §2: 복귀 때 상자 ② 주변(map x 2.6 → 0.4)에서 '매끄럽지 못한' 구간 분석. 인자: 이름=npz ... | 10-12 §2 · 10-12 §3 |
| [`extract_pc.py`](../../debug_log/2026-10-12/jobs/extract_pc.py) | 10-08 §3.4: PC 판 bag 추출(rosbags) — render_rviz.py 와 같은 키 + MPPI 후보·최적 궤적(/trajectories, odom). 인자: bag 출력.npz | 10-08 §3.4 |
| [`fig_1012.py`](../../debug_log/2026-10-12/jobs/fig_1012.py) | 10-12 §15 그림 4 장: (1) 주행 10 회의 /tf 수신 추이 (2) 계측 4 회의 UDP 수신·손실 (3) 포화 전후 프로세스 부하 (4) W3 출발 후진 거리·prep 시간 | 10-12 §15 |
| [`fig_f2f1.py`](../../debug_log/2026-10-12/jobs/fig_f2f1.py) | 10-12 §2 그림: f2f1 복귀 상자 구간 — 위 = 그 순간의 로컬 코스트맵(RViz 색)·차체·경로·MPPI 최적 궤적 4 장면, 아래 = 시간축(지령 속도, TF 끊김·사건, CPU) | 10-12 §2 |
| [`gap_eval.py`](../../debug_log/2026-10-12/jobs/gap_eval.py) | 10-12 §2: 토픽·TF 끊김 찾기 — bag 기록 시각(수신) 간격과 메시지 stamp 간격. 인자: bag [최소 간격 s=0.5] | 10-12 §2 · 10-12 §3 |
| [`get960.sh`](../../debug_log/2026-10-12/jobs/get960.sh) | 10-12 §3.3: Nav2·센서 로그 통째 회수(재부팅 전에) | — |
| [`job551_f0drive.sh`](../../debug_log/2026-10-12/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`job947_state.sh`](../../debug_log/2026-10-12/jobs/job947_state.sh) |  | 10-12 §1 |
| [`job951_chk.sh`](../../debug_log/2026-10-12/jobs/job951_chk.sh) | 10-12 §1: prep 뒤 확인(로버 안 움직임) — Nav2 수명 주기, 실행 중 PreferForward 가중, 원점, nvblox | 10-12 §1.1 |
| [`job952_navlog.sh`](../../debug_log/2026-10-12/jobs/job952_navlog.sh) | 10-12 §2: f2f1 주행 중 Nav2·EKF·SLAM 로그의 경고·오류(10:32~10:36) — 로버 안 움직임 | — |
| [`job953_navlog2.py`](../../debug_log/2026-10-12/jobs/job953_navlog2.py) | 10-12 §2: f2f1 복귀 상자 구간(10:35:00~10:35:45) Nav2 로그 — 반복 경고는 초당 횟수로, 나머지는 원문. + 주행 전체의 종류별 횟수 | — |
| [`job954_why.py`](../../debug_log/2026-10-12/jobs/job954_why.py) | 10-12 §3.2: f2f2 목표 1 취소 원인 — 주행 창(11:16:35~11:17:35)의 Nav2·guard·stuck 로그. 로버 안 움직임 | — |
| [`job955_nav2re.sh`](../../debug_log/2026-10-12/jobs/job955_nav2re.sh) | 10-12 §3.2: 전역 정적 층이 지도를 못 받음(no map received) → Nav2 만 재시작(B 구성 인자 그대로) + 전역 코스트맵에 지도가 들어왔는지 확인. 로버 안 움직임 | 10-12 §7.2 |
| [`job956_gcmchk.py`](../../debug_log/2026-10-12/jobs/job956_gcmchk.py) | 10-12 §3.2 게이트 후보: 전역 코스트맵에 정적 지도가 들어왔는가 — /global_costmap/costmap 한 장의 치명(≥99) 칸 수와 크기 | 10-12 §3.2 |
| [`job957_mapdiag.sh`](../../debug_log/2026-10-12/jobs/job957_mapdiag.sh) | 10-12 §3.2: 전역 정적 층이 지도를 못 받는 원인 — map_server 상태·/map_nav 발행·로그. 로버 안 움직임 | 10-12 §3.2 |
| [`job959_mapdiag2.sh`](../../debug_log/2026-10-12/jobs/job959_mapdiag2.sh) | 10-12 §3.2: 지연 적용 뒤에도 unconfigured — 관리 노드 로그와 수동 전이 시도. 로버 안 움직임 | 10-12 §3.2 |
| [`job961_dup.sh`](../../debug_log/2026-10-12/jobs/job961_dup.sh) | 10-12 §3.4: 중복·잔류 프로세스 확인(사용자 요청). 로버 안 움직임 | 10-12 §3.4 |
| [`job962_dup2.sh`](../../debug_log/2026-10-12/jobs/job962_dup2.sh) | 10-12 §3.4: 중복 확인 보강 — nvblox 실행 파일 수, 데몬 없이 본 노드 목록, 주행 러너 잔류물. 로버 안 움직임 | 10-12 §3.4 |
| [`job963_prep5.sh`](../../debug_log/2026-10-12/jobs/job963_prep5.sh) | 10-12 §4: PreferForward 5 로 임시 되돌려 prep(B 구성) + 지도 서버·전역 지도·실행 값 확인. 로버 안 움직임 | 10-12 §4.1 · 10-12 §5 |
| [`job964_prep15.sh`](../../debug_log/2026-10-12/jobs/job964_prep15.sh) | 10-12 §5: PreferForward 15 로 prep (job963 에 W=15.0). 로버 안 움직임 | 10-12 §5.1 |
| [`job965_state.sh`](../../debug_log/2026-10-12/jobs/job965_state.sh) | 10-12 §5.3: 주행 중단 뒤 정지 상태에서 포화가 남아 있는가 — /tf 주기, 프로세스 CPU, 루프백 패킷. 로버 안 움직임 | 10-12 §5.2 |
| [`job966_prep_lean.sh`](../../debug_log/2026-10-12/jobs/job966_prep_lean.sh) | 10-12 §6: 부하 여유 구성 prep — 그림자 EKF A 끔·MPPI 궤적 발행 끔, PreferForward 15. 로버 안 움직임 | 10-12 §6.1 · 10-12 §7 |
| [`job967_net.sh`](../../debug_log/2026-10-12/jobs/job967_net.sh) | 10-12 §8: 궤적 발행과 다른 프로세스의 충돌 여부 — UDP 버퍼 설정·누적 손실·구독자·DDS 전송 설정. 로버 안 움직임 | 10-12 §8.2 |
| [`job968_shm.sh`](../../debug_log/2026-10-12/jobs/job968_shm.sh) | 10-12 §8.3: 공유메모리 전송 재사용 검토용 사실 확인(로버 안 움직임) | 10-12 §8.3 |
| [`job969_prep_j.sh`](../../debug_log/2026-10-12/jobs/job969_prep_j.sh) | 10-12 §9: 계측 재현 prep — 그림자 EKF 끔 + MPPI 궤적 발행 원래대로 + PreferForward 15(f2i1 구성). 로버 안 움직임 | 10-12 §9.1 |
| [`job970_prep_lite.sh`](../../debug_log/2026-10-12/jobs/job970_prep_lite.sh) | 10-12 §12: lite prep — 그림자 EKF 끔 + MPPI 궤적 발행 lite(후보 10 × 8 점 + 최적 32 점) + PreferForward 15. 로버 안 움직임 | 10-12 §12.1 |
| [`job971_prepchk.py`](../../debug_log/2026-10-12/jobs/job971_prepchk.py) | prep 확인을 한 프로세스(DDS 참여자 1 개)로 (2026-10-12 §13). | 10-12 §13 |
| [`job972_prep_fast.sh`](../../debug_log/2026-10-12/jobs/job972_prep_fast.sh) | 빠른 prep (2026-10-12 §13, 사용자: "prep 단축은 앞 2 가지 적용") — job240(09-11)·job726·job731·job780 의 F2 순회 경로를 한 파일로, | 10-12 §13 · 10-12 §14 |
| [`job973_prep_lite_fast.sh`](../../debug_log/2026-10-12/jobs/job973_prep_lite_fast.sh) | 10-12 §13: 빠른 prep 으로 운용 후보 구성(그림자 EKF 끔 + mppi_viz lite + PreferForward 15, B 구성). 로버 안 움직임 | 10-12 §13 |
| [`navlog_pc.py`](../../debug_log/2026-10-12/jobs/navlog_pc.py) | 10-12 §3.3: Nav2 로그(PC 로 회수한 사본) 요약 — 종류별 횟수(주행 창), 10 s 칸 히스토그램, 반복 아닌 경고·오류 원문. 인자: nav2.log HH:MM:SS HH:MM:SS [원문 최대 줄] | 10-12 §4 |
| [`net_anal.py`](../../debug_log/2026-10-12/jobs/net_anal.py) | 10-12 §9.2: UDP 손실 시간순 분석. 인자: net_<이름>.log 포화시작(HH:MM:SS) | 10-12 §9.2 |
| [`onset_ctx.py`](../../debug_log/2026-10-12/jobs/onset_ctx.py) | 10-12 §8: (1) 포화 시작 직전 20 s 의 주행 상태 (2) 포화 없는 구간에서 '도는 정도'와 프로세스 부하의 관계 | 10-12 §8.1 |
| [`proc_cmp2.py`](../../debug_log/2026-10-12/jobs/proc_cmp2.py) | 10-12 §3.3: 프로세스별 CPU(전 프로세스 틱 기록) 구간 비교. 인자: 이름=proc.log@시작epoch@끝epoch ...  (코어 1 개 = 100) | 10-12 §3.3 · 10-12 §4 |
| [`rev_eval.py`](../../debug_log/2026-10-12/jobs/rev_eval.py) | 10-12 §1.2: 러너 csv 로 목표별 후진·제자리 회전 집계. 후진 거리 = 지령 v < −0.005 인 표본 사이 odom 이동 길이(EKF, 미끄러짐은 못 봄). | 10-12 §1.2 |
| [`run_f0.sh`](../../debug_log/2026-10-12/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`tf_rate.py`](../../debug_log/2026-10-12/jobs/tf_rate.py) | 10-12 §3.3: bag 의 /tf 발행량 추이 — 10 s 칸마다 프레임 쌍별 변환 수(Hz)와 /tf 메시지 수. 인자: bag | 10-12 §3.3 · 10-12 §4 |
| [`top_eval.py`](../../debug_log/2026-10-12/jobs/top_eval.py) | 10-12 §2: top 기록(2 s 간격)에서 구간별 부하 — load average, 유휴 %, 프로세스별 CPU 평균. 인자: top.log HH:MM:SS HH:MM:SS [..구간 더] | 10-12 §2 · 10-12 §3 |
| [`traj_size.py`](../../debug_log/2026-10-12/jobs/traj_size.py) | 10-12 §7.3: /trajectories(MPPI 궤적 발행) 메시지의 크기·주기 추이 — 10 s 칸마다 메시지 수, 직렬화 크기(kB), 마커 수. 인자: bag... | 10-12 §7.3 |
| [`up950.sh`](../../debug_log/2026-10-12/jobs/up950.sh) | 10-12 §1: 재부팅 뒤 스크립트 재전송 + nav2_params(PreferForward 15) 배포·빌드. 실행은 안 함. 비밀번호는 run_jn.sh 에서 읽음. | 10-12 §1 |
| [`up958.sh`](../../debug_log/2026-10-12/jobs/up958.sh) | 10-12 §3.2: navigation.launch(지도 서버 관리 노드 3 s 지연) 배포·빌드 + 확인 스크립트 전송 | — |
| [`up963.sh`](../../debug_log/2026-10-12/jobs/up963.sh) |  | — |
| [`up972.sh`](../../debug_log/2026-10-12/jobs/up972.sh) |  | — |

## 2026-10-13 (34)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_cap_f2m1.sh`](../../debug_log/2026-10-13/jobs/anal_cap_f2m1.sh) | (오늘만) f2m1 캡처를 Jetson 에서 분석 — 로버 안 움직임 | — |
| [`anal_cap_f2m1b.sh`](../../debug_log/2026-10-13/jobs/anal_cap_f2m1b.sh) | (오늘만) f2m1 캡처 재분석: 평상 창 10:19:36 부터 4 s, 포화 시작 10:19:40 — 로버 안 움직임 | — |
| [`anal_cap_f2m1c.sh`](../../debug_log/2026-10-13/jobs/anal_cap_f2m1c.sh) | (오늘만) f2m1 포화 시작 구간(10:19:38 부터 4 s)을 0.2 s 칸으로 — 로버 안 움직임 | — |
| [`anal_cap_f2m1d.sh`](../../debug_log/2026-10-13/jobs/anal_cap_f2m1d.sh) | (오늘만) f2m1 포화 직전 15 s 의 /tf HEARTBEAT·ACKNACK 맞춰 보기 — 로버 안 움직임 | — |
| [`anal_cap_f2n1.sh`](../../debug_log/2026-10-13/jobs/anal_cap_f2n1.sh) | (오늘만) f2n1 캡처: 10 s 칸으로 전체 패킷·/tf DATA·HEARTBEAT, 그리고 주행 중간 20 s 창의 종류별 집계 — 로버 안 움직임 | — |
| [`anal_f2o1_options.py`](../../debug_log/2026-10-13/jobs/anal_f2o1_options.py) | anal_f2o1_options — f2o1 정지(상자 옆 4.8 cm)에 대한 대책 후보의 사전 평가 3 가지. (2026-10-13 §5, 오늘만 쓰는 분석 — 로버 안 움직임) | 10-13 §5 |
| [`anal_pad0_summary.py`](../../debug_log/2026-10-13/jobs/anal_pad0_summary.py) | (10-13 §11) 패딩 0 시뮬(/tmp/sweep_pad0) 대 현재 패딩 0.01(/tmp/sweep 의 cost_w 3.81) 요약표 — 계산만. | 10-13 §11.1 |
| [`anal_sweep_summary.py`](../../debug_log/2026-10-13/jobs/anal_sweep_summary.py) | (10-13 §9) /tmp/sweep 의 시뮬 결과 요약표 — 계산만. 내용 없는 파일은 끝부분을 보여 준다. | 10-13 §9.1 |
| [`anal_unstuck_summary.py`](../../debug_log/2026-10-13/jobs/anal_unstuck_summary.py) | (10-13 §14.2) /tmp/unstuck 의 탈출 시뮬 결과 요약 — 계산만. | 10-13 §14 |
| [`chk_costw.sh`](../../debug_log/2026-10-13/jobs/chk_costw.sh) | (10-13 §12) 실행 중 MPPI CostCritic 값 확인 — 로버 안 움직임 | 10-13 §12.1 |
| [`chk_navlog_f2o1.sh`](../../debug_log/2026-10-13/jobs/chk_navlog_f2o1.sh) | (오늘만) f2o1 목표 3 중단 전후(13:33:05~13:33:50)의 Nav2 로그 원문 — 로버 안 움직임 | — |
| [`chk_pad0.sh`](../../debug_log/2026-10-13/jobs/chk_pad0.sh) | (10-13 §11) 패딩 0 시뮬 진행 확인 — 로버 안 움직임 | — |
| [`chk_pathyaw_serve.sh`](../../debug_log/2026-10-13/jobs/chk_pathyaw_serve.sh) | (10-13 §4) 상주 경로 조회기 정지 시험: 경로 계산만 요청(로버 안 움직임). 목표 3 개를 한 프로세스로 연달아 조회한다. | 10-13 §4 |
| [`chk_sweep.sh`](../../debug_log/2026-10-13/jobs/chk_sweep.sh) | (10-13 §9) 시뮬 묶음 진행 확인 — 로버 안 움직임 | — |
| [`fetch_one.sh`](../../debug_log/2026-10-13/jobs/fetch_one.sh) | (PC·WSL) Jetson /tmp 의 파일 하나를 PC 로 회수. 인자: 원격 파일명, 받을 폴더(/mnt/...). 비밀번호는 run_jn.sh 에서 읽는다(여기에 적지 않음). | — |
| [`fig_report.py`](../../debug_log/2026-10-13/jobs/fig_report.py) | fig_report — 10-13 하루 기록을 한 장짜리 HTML 로 만든다(그림은 data URI 로 넣음). (2026-10-13, PC 에서 실행) | 10-13 §15 |
| [`job550_f0run.py`](../../debug_log/2026-10-13/jobs/job550_f0run.py) | F0 코스 확장 러너 (2026-09-23): 상자 코스와 무관한 연속 목표 주행 + 왕복 복귀 오차 계측. | 09-23 16 · 09-28 §12 · 09-28 §16 · … +5 |
| [`job551_f0drive.sh`](../../debug_log/2026-10-13/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`job613_pathyaw.py`](../../debug_log/2026-10-13/jobs/job613_pathyaw.py) | 경로 끝 방향 조회(단독 프로세스, 2026-09-28 §20): 현재 위치 → (GX, GY) 경로를 planner(GridBased)에서 받아 끝 0.3 m 구간 방향(rad)을 출력. | 09-28 §20 · 10-13 §4 · 10-21 §3 |
| [`prep_deploy_costw.sh`](../../debug_log/2026-10-13/jobs/prep_deploy_costw.sh) | (10-13 §12) MPPI CostCritic cost_weight 를 Jetson 의 nav2_params.yaml(소스·설치본)에 반영 → 순회 prep(lite, 15) → 실행 중 값 확인. 인자: 값(기본 11.43). 로버 안 움직임 | 10-13 §12.1 |
| [`prep_deploy_ginfl.sh`](../../debug_log/2026-10-13/jobs/prep_deploy_ginfl.sh) | (10-13 §5.3) 전역 inflation 감쇠 계수를 Jetson 의 nav2_params.yaml(소스·설치본)에 반영 → 순회 prep → 실행 중 값 확인. 인자: 값(기본 3.0). 로버 안 움직임 | 10-13 §5.6 |
| [`prep_patrol_run.sh`](../../debug_log/2026-10-13/jobs/prep_patrol_run.sh) | (오늘만) run_jn.sh 는 인자를 넘기지만 여기서는 f2m1 용으로 고정: 캡처 권한 확인 + 순회 prep(궤적 발행 원래대로, 벌점 15). 로버 안 움직임 | — |
| [`put_bin.sh`](../../debug_log/2026-10-13/jobs/put_bin.sh) | (PC·WSL) 스크래치패드의 이진 파일을 그대로 Jetson /tmp 로 전송(put_one.sh 는 CR 을 지우므로 이진 파일엔 쓰면 안 됨). 비밀번호는 run_jn.sh 에서 읽는다. | — |
| [`put_one.sh`](../../debug_log/2026-10-13/jobs/put_one.sh) | (PC·WSL) 스크래치패드의 파일을 Jetson /tmp 로 전송(CR 제거). 인자: 파일명 ... 비밀번호는 run_jn.sh 에서 읽는다(여기에 적지 않음). | 10-20 §2.1 · 10-21 §3 |
| [`run_f0.sh`](../../debug_log/2026-10-13/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_sim_box.sh`](../../debug_log/2026-10-13/jobs/run_sim_box.sh) | (10-13 §7) MPPI 오프라인 시뮬(job776)로 f2o1·f2p1 상자 옆 정지를 재현해 본다 — 계산만, 로버 안 움직임. 인자: 추가 key=val(없으면 현재 값), 환경 SEEDS·LABEL | 10-13 §7.1 |
| [`run_sim_box2.sh`](../../debug_log/2026-10-13/jobs/run_sim_box2.sh) | (10-13 §8) MPPI 오프라인 시뮬(anal_mppi_sim, EXTRA 로 fpchk=1 등 추가 인자)로 f2o1·f2p1 상자 옆 정지를 재현해 본다 — 계산만, 로버 안 움직임. 인자: 추가 key=val(없으면 현재 값), 환경 SEE | 10-13 §8.1 |
| [`run_sim_box3.sh`](../../debug_log/2026-10-13/jobs/run_sim_box3.sh) | (10-13 §8) MPPI 오프라인 시뮬(anal_mppi_sim, EXTRA 로 fpchk=1 등 추가 인자)로 f2o1·f2p1 상자 옆 정지를 재현해 본다 — 계산만, 로버 안 움직임. 인자: 추가 key=val(없으면 현재 값), 환경 SEE | 10-13 §8.1 |
| [`run_sim_pad0.sh`](../../debug_log/2026-10-13/jobs/run_sim_pad0.sh) | (10-13 §11) MPPI 시뮬 묶음: 장면 4 개 × 씨앗 10 개, fpchk=1 pad=0(풋프린트 패딩 없앰), 3 개씩 병렬 — 계산만, 로버 안 움직임. 결과 /tmp/sweep_pad0/*.txt, 끝에 요약표. | — |
| [`run_sim_sweep.sh`](../../debug_log/2026-10-13/jobs/run_sim_sweep.sh) | (10-13 §9) MPPI 시뮬 묶음: 장면 5 개 × cost_w 3 개 × 씨앗 10 개, fpchk=1, 3 개씩 병렬 — 계산만, 로버 안 움직임. 결과 /tmp/sweep/*.txt, 끝에 요약표. | 10-13 §9 |
| [`run_sim_unstuck.sh`](../../debug_log/2026-10-13/jobs/run_sim_unstuck.sh) | (10-13 §14.2) 실제 정지 자세 3 곳에서 시뮬 시작: pad=0.01 대 pad=0, 씨앗 1~5, 150 주기, fpchk=1 — 계산만, 로버 안 움직임 | 10-13 §14 |
| [`up_costw_only.sh`](../../debug_log/2026-10-13/jobs/up_costw_only.sh) | (10-13 §12) MPPI CostCritic cost_weight 만 Jetson yaml(소스·설치본)에 반영하고, 실행 중인 컨트롤러 값도 같이 바꾼다(재기동 없음). 인자: 값. 로버 안 움직임 | 10-13 §12.1 |
| [`up_ginfl_only.sh`](../../debug_log/2026-10-13/jobs/up_ginfl_only.sh) | (10-13 §6) 전역 inflation 감쇠 계수만 Jetson yaml(소스·설치본)에 반영 — 재기동 없음(실행 중인 Nav2 는 다음 prep 때 바뀜). 인자: 값. 로버 안 움직임 | 10-13 §6 |
| [`up_nvblox_integ.sh`](../../debug_log/2026-10-13/jobs/up_nvblox_integ.sh) | (10-13 §14) nvblox 통합 거리(projective_integrator_max_integration_distance_m)를 Jetson 의 nvblox_local.yaml(소스·설치본)에 반영 — 재기동 없음(다음 prep 때 적용). 인 | 10-13 §14 · 10-14 §6 |

## 2026-10-14 (47)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_blob_src.py`](../../debug_log/2026-10-14/jobs/anal_blob_src.py) | anal_blob_src — 지도 좌표의 한 작은 구역에 로컬 코스트맵 치명 칸이 언제부터 있었고, 라이다 점이 그 구역에 있었는지 시간순으로. (2026-10-14 §22, 오늘만) | 10-14 §22 |
| [`anal_box_edge_growth.py`](../../debug_log/2026-10-14/jobs/anal_box_edge_growth.py) | anal_box_edge_growth — 사용자 지적 2 가지를 bag 과 계산으로 본다. (2026-10-14, 오늘만) | 10-14 §5 |
| [`anal_box_edge_map.py`](../../debug_log/2026-10-14/jobs/anal_box_edge_map.py) | anal_box_edge_map — 출발점 근처 상자(복귀 길 상자 끝, 10-13 §12)의 북쪽 가장자리를 지도 좌표로: 로컬 코스트맵(odom)과 전역 코스트맵(map) 각각. (2026-10-14 §22, 오늘만) | 10-14 §22 |
| [`anal_box_shift_angle.py`](../../debug_log/2026-10-14/jobs/anal_box_shift_angle.py) | anal_box_shift_angle — 기억된 상자가 밀린 양(10-13 §6.2) 가운데 '각도(yaw) 몫'과 '위치 몫'을 가른다. (2026-10-14, 오늘만 — 사용자 지적: "1 칸 두꺼워지는 이유에 각도 문제도 있다고 본다") | 10-14 §4 |
| [`anal_ctrl_timing.py`](../../debug_log/2026-10-14/jobs/anal_ctrl_timing.py) | anal_ctrl_timing — 패딩 토글 뒤 컨트롤러가 '느려졌는지·흔들리는 입력을 받았는지'를 bag · top 기록으로 견준다. (2026-10-14 §23, 오늘만) | 10-14 §23 |
| [`anal_free_wobble.py`](../../debug_log/2026-10-14/jobs/anal_free_wobble.py) | anal_free_wobble — 로버 둘레가 완전히 빈 칸(비용 0)일 때만 골라 좌우 틀기(\|ω\|>0.05 부호 바뀜)를 센다. (2026-10-14 §23, 오늘만) | 10-14 §23 |
| [`anal_hesitation.py`](../../debug_log/2026-10-14/jobs/anal_hesitation.py) | anal_hesitation — '멈칫거리며 움직임'(사용자 영상)을 수치로: 구간별 명령 속도가 순항(≥0.06)에서 0.03 아래로 떨어졌다 돌아오는 횟수, | 10-14 §18 · 10-14 21.1 |
| [`anal_lc_hist.py`](../../debug_log/2026-10-14/jobs/anal_lc_hist.py) | anal_lc_hist — 로컬 코스트맵(/local_costmap/costmap) 값 분포를 구간별로 견준다. (2026-10-14 §21, 오늘만) | 10-14 21.3 |
| [`anal_navfn_replay.py`](../../debug_log/2026-10-14/jobs/anal_navfn_replay.py) | anal_navfn_replay — 발행된 전역 코스트맵 위에서 NavFn 과 같은 비용 변환으로 다익스트라 최단 경로를 다시 구해, bag 의 /plan 과 견준다. (2026-10-14 §24, 오늘만) | 10-14 §24 |
| [`anal_path_endyaw.py`](../../debug_log/2026-10-14/jobs/anal_path_endyaw.py) | anal_path_endyaw — 계획기 경로(/plan)와 컨트롤러가 받은 경로(/transformed_global_plan)의 끝 방향을 시간순으로 견준다. (2026-10-14, 오늘만) | 10-14 §16 · 10-14 §17 |
| [`anal_person_event.py`](../../debug_log/2026-10-14/jobs/anal_person_event.py) | anal_person_event — 주행 중 로버 앞에 무엇이 나타났다 사라졌는지와 그때 속도·전역 경로가 어떻게 변했는지 시간순으로 낸다. (2026-10-14, 오늘만 — f2r2 에서 사람이 지나갔다는 사용자 관찰 확인) | — |
| [`anal_slice_blob.py`](../../debug_log/2026-10-14/jobs/anal_slice_blob.py) | anal_slice_blob — nvblox 거리 지도 조각(/nvblox_node/static_map_slice)에서 상자 끝 덩어리 구역이 시간에 따라 어땠는지. (2026-10-14 §24, 오늘만) | 10-14 §24 |
| [`anal_sw_turn.py`](../../debug_log/2026-10-14/jobs/anal_sw_turn.py) | anal_sw_turn — 남서 통로(f2t1 목표 4·5)에서 로버가 왜 상자 쪽으로 머리를 돌렸는지. (2026-10-14 §20, 오늘만) | 10-14 §20 · 10-14 §22 |
| [`anal_sw_yawsweep.py`](../../debug_log/2026-10-14/jobs/anal_sw_yawsweep.py) | anal_sw_yawsweep — 그 시각 그 자리에서 로버 방향만 바꿔 놓았다면 차체(패딩 포함 직사각형)가 로컬 코스트맵에서 얼마나 여유·비용을 갖는지. (2026-10-14 §20, 오늘만) | 10-14 §20 |
| [`anal_unstuck2_summary.py`](../../debug_log/2026-10-14/jobs/anal_unstuck2_summary.py) | (10-14 §2) /tmp/unstuck2 의 갇힘 해제 되돌림 시뮬 요약 — 계산만. | 10-14 §2.1 |
| [`anal_video_sync.py`](../../debug_log/2026-10-14/jobs/anal_video_sync.py) | anal_video_sync — 휴대폰 영상(촬영 시각 정보 없음)을 bag 시각에 맞춘다. (2026-10-14, 오늘만) | 10-14 19.2 |
| [`anal_westpass_cells.py`](../../debug_log/2026-10-14/jobs/anal_westpass_cells.py) | anal_westpass_cells — 서쪽 통로 정지 자리에서 로버 오른쪽 치명 칸이 두 주행에서 왜 달랐나(사용자 관찰). 오늘만. (2026-10-14) | 10-14 §13.5 |
| [`chk_after_f2r1.sh`](../../debug_log/2026-10-14/jobs/chk_after_f2r1.sh) | (10-14 §9) f2r1 뒤: pad_relief 기록·컨트롤러 실패 로그·현재 패딩 확인 — 로버 안 움직임 | — |
| [`chk_after_f2r2.sh`](../../debug_log/2026-10-14/jobs/chk_after_f2r2.sh) | (10-14 §9) f2r2 뒤: pad_relief 기록·컨트롤러 실패 로그·현재 패딩 확인 — 로버 안 움직임 | — |
| [`chk_after_f2s1.sh`](../../debug_log/2026-10-14/jobs/chk_after_f2s1.sh) | (10-14 §9) f2s1 뒤: pad_relief 기록·컨트롤러 실패 로그·현재 패딩 확인 — 로버 안 움직임 | — |
| [`chk_after_f2s2.sh`](../../debug_log/2026-10-14/jobs/chk_after_f2s2.sh) | (10-14 §9) f2s2 뒤: pad_relief 기록·컨트롤러 실패 로그·현재 패딩 확인 — 로버 안 움직임 | — |
| [`chk_after_relief.sh`](../../debug_log/2026-10-14/jobs/chk_after_relief.sh) | (10-14 §18) pad_relief 가 한 번 내렸다 올린 뒤의 로컬 코스트맵 상태(스택 그대로) — 로버 안 움직임 | 10-14 §18 |
| [`chk_bt_load.sh`](../../debug_log/2026-10-14/jobs/chk_bt_load.sh) | (10-14 §14) 스택 재기동(prep) 뒤 bt_navigator 가 CopyPath 를 읽었는지·BT 오류가 없는지 확인 — 로버 안 움직임 | 10-14 §14 |
| [`chk_jetson_navsrc.sh`](../../debug_log/2026-10-14/jobs/chk_jetson_navsrc.sh) | (10-14 §14) Jetson 소스의 rover_navigation 파일 3 개를 /tmp 로 복사(PC 에서 저장소와 비교하려고) — 로버 안 움직임 | 10-14 §14 |
| [`chk_live2_f2t1.sh`](../../debug_log/2026-10-14/jobs/chk_live2_f2t1.sh) | (10-14 §17) 주행 중: 러너 기록·최근 위치/속도(러너 csv)·CPU — 명령 없음 | — |
| [`chk_live3_f2t1.sh`](../../debug_log/2026-10-14/jobs/chk_live3_f2t1.sh) | (10-14 §17) 주행 중: 목표 시작·성공·실패 시각(Nav2 로그), 최근 컨트롤러 실패 — 명령 없음 | — |
| [`chk_live_f2t1.sh`](../../debug_log/2026-10-14/jobs/chk_live_f2t1.sh) | (10-14 §17) 주행 중 실시간 확인: 최근 60 s Nav2 경고·오류, pad_relief 기록 — 로버에 명령 안 보냄(DDS 참여자도 안 만듦) | — |
| [`chk_logkeep.sh`](../../debug_log/2026-10-14/jobs/chk_logkeep.sh) | (10-14 §25) prep_fast 의 기록 보관 부분만 실행해 시험 — 기록을 비우지 않음, 로버 안 움직임 | 10-14 §25 |
| [`chk_nav2_window.sh`](../../debug_log/2026-10-14/jobs/chk_nav2_window.sh) | (10-14 §24) Nav2 기록의 한 시각 구간을 거르지 않고 출력 — 로버 안 움직임. 인자: 시작HH:MM:SS 끝HH:MM:SS | 10-14 §24 |
| [`chk_navlog_f2r1.sh`](../../debug_log/2026-10-14/jobs/chk_navlog_f2r1.sh) | (10-14 §9.2) f2r1 상자 옆 11:26:34~11:26:50 의 Nav2 로그 원문 — 로버 안 움직임 | 10-14 §9.2 |
| [`chk_navlog_f2s1.sh`](../../debug_log/2026-10-14/jobs/chk_navlog_f2s1.sh) | (10-14 §13.1) f2s1 목표 3 취소 전후 Nav2·nav_guard 로그 — 로버 안 움직임 | — |
| [`chk_navlog_f2t1.sh`](../../debug_log/2026-10-14/jobs/chk_navlog_f2t1.sh) | (10-14 §17) f2t1 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임 | — |
| [`chk_navlog_f2u2.sh`](../../debug_log/2026-10-14/jobs/chk_navlog_f2u2.sh) | (10-14 §22) f2u2 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임 | 10-14 §22 |
| [`chk_nvblox_integ.sh`](../../debug_log/2026-10-14/jobs/chk_nvblox_integ.sh) | (10-14 §7) 실행 중 nvblox 가 읽은 통합 거리 확인 — 로버 안 움직임 | — |
| [`chk_pad_relief.sh`](../../debug_log/2026-10-14/jobs/chk_pad_relief.sh) | (10-14 §8.2) pad_relief 정지 시험: 가짜 컨트롤러 실패 로그로 켜짐·시간 한도 복귀·종료 때 복귀를 확인 — 로버 안 움직임(주행 명령 없음) | 10-14 §8 · 10-14 §8.6 |
| [`chk_prep_md5.sh`](../../debug_log/2026-10-14/jobs/chk_prep_md5.sh) | (10-14 §25) Jetson /tmp 의 prep 스크립트 md5 확인 — 로버 안 움직임 | 10-14 §25 |
| [`chk_rate_f2t1.sh`](../../debug_log/2026-10-14/jobs/chk_rate_f2t1.sh) | (10-14 §18) f2t1 동안 30 s 칸별: 컨트롤러 주기 미달·좌표 변환 미래 요청 경고 수, PathBlocked/follow 중단 — 로버 안 움직임 | — |
| [`fig_box_end_plans.py`](../../debug_log/2026-10-14/jobs/fig_box_end_plans.py) | fig_box_end_plans — 복귀 길 상자 끝(출발점 동쪽)에서 계획기 경로가 '곧게' 나온 주행과 '상자 끝을 감아 돌게' 나온 주행을 나란히. (2026-10-14 §24, 오늘만) | 10-14 §24 |
| [`fig_no5_route.py`](../../debug_log/2026-10-14/jobs/fig_no5_route.py) | fig_no5_route — 8 목표 순회 코스(no5)를 저장 지도(office_v3) 위에: 목표 번호 + 실제로 달린 궤적(목표 구간마다 색). (2026-10-14 §27, 오늘만) | 10-14 §27 · 10-14 27.2 · 10-14 27.3 |
| [`prep_pad_only.sh`](../../debug_log/2026-10-14/jobs/prep_pad_only.sh) | (10-14 §9) pad_relief 만 다시 띄우고 상태 확인 — 로버 안 움직임 | 10-14 §9.1 |
| [`prep_patrol_pad.sh`](../../debug_log/2026-10-14/jobs/prep_patrol_pad.sh) | (10-14 §9) 순회 prep(viz, 벌점) 뒤 pad_relief 노드를 접속과 분리해 띄운다(mode 인자: on\|shadow, 기본 shadow — 10-14 §19: 실행 중 패딩 변경 뒤 멈칫거림 의심). 로버 안 움직임 | 10-14 19.1 · 10-15 §0 · 10-15 §1.1 · … +2 |
| [`run_detached.sh`](../../debug_log/2026-10-14/jobs/run_detached.sh) | (PC·WSL) 연결이 불안정할 때: 파일을 재시도하며 보내고, Jetson 에서 setsid nohup 으로 스크립트를 띄운 뒤(접속이 끊겨도 계속 돎) 결과 파일을 재시도하며 읽어 온다. | 10-14 §8.5 · 10-14 §8.6 |
| [`run_f2c.sh`](../../debug_log/2026-10-14/jobs/run_f2c.sh) | 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5] | 10-07 §2.1 · 10-07 §2.2 · 10-07 §2.4 · … +31 |
| [`run_sim_unstuck2.sh`](../../debug_log/2026-10-14/jobs/run_sim_unstuck2.sh) | (10-14 §2) '갇혔을 때만 패딩 0' 되돌림 시뮬: 정지 자세 2 곳 × us_d 3 개 × 씨앗 5, 300 주기, fpchk=1 unstuck=1 — 계산만, 로버 안 움직임 | 10-14 §2.1 |
| [`up_bt_copypath.sh`](../../debug_log/2026-10-14/jobs/up_bt_copypath.sh) | (10-14 §14) CopyPath BT 노드 배포: 저장소 파일 4 개를 Jetson 소스에 두고 rover_navigation 만 빌드 — 로버 안 움직임(실행 중 스택은 다음 prep 때 새 노드를 읽음) | 10-14 §14 |
| [`up_pad_shadow.sh`](../../debug_log/2026-10-14/jobs/up_pad_shadow.sh) | (10-14 §19) 실행 중인 pad_relief 를 관찰 모드(shadow)로 다시 띄움 — 패딩은 바꾸지 않고 판정·기록만. 로버 안 움직임 | 10-14 19.1 |
| [`up_pad_toggle.sh`](../../debug_log/2026-10-14/jobs/up_pad_toggle.sh) | (10-14 §21 A/B 시험 B 조건) 로버가 서 있는 상태에서 로컬 코스트맵 footprint_padding 을 pad_relief 가 f2t1 에서 한 것과 같은 값·간격으로 바꿨다 되돌린다. | 10-14 21.1 · 10-14 21.3 |

## 2026-10-15 (61)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_ahead_cells.py`](../../debug_log/2026-10-15/jobs/anal_ahead_cells.py) | anal_ahead_cells — 로컬 코스트맵 프레임마다 차체 둘레(앞으로 늘린 직사각형) 안 치명 칸 수와 위치를 차체 좌표로. (2026-10-15 §3, 오늘만) | 10-15 §3 |
| [`anal_band_run.py`](../../debug_log/2026-10-15/jobs/anal_band_run.py) | anal_band_run — 주행 전체에서 차체(패딩 포함) ↔ 로컬 치명 칸 정확 여유와 Nav2 식 풋프린트 판정. (2026-10-15 §29.2, 오늘만) | 10-15 §29.2 · 10-15 §29.6 · 10-23 §20 · … +2 |
| [`anal_box_true_vs_map.py`](../../debug_log/2026-10-15/jobs/anal_box_true_vs_map.py) | anal_box_true_vs_map — 출발점 시험 상자의 기록 위치(고정)와 로컬 코스트맵이 찍은 상자 칸을 지도 좌표에서 비교. (2026-10-15 §29.4, 오늘만) | 10-15 §29.4 · 10-15 §29.7 · 10-15 §30 · … +1 |
| [`anal_cam_vs_lidar.py`](../../debug_log/2026-10-15/jobs/anal_cam_vs_lidar.py) | anal_cam_vs_lidar — 카메라(nvblox 거리 지도 조각)가 라이다로 확인되는 면을 실제보다 앞에(과대) / 같게 / 뒤에(과소) 찍는지, 아예 못 찍는지(누락). (2026-10-15 §9, 오늘만) | 10-15 9.2 |
| [`anal_cell_first_seen.py`](../../debug_log/2026-10-15/jobs/anal_cell_first_seen.py) | anal_cell_first_seen — 기준 순간의 카메라만 치명 칸들이 '처음 치명이 된 순간' 카메라에서 본 방위각 · 거리, 그리고 그 전에 시야 안에 있었는데 안 찍혔던 순간. (2026-10-15 §7, 오늘만) | 10-15 §7 |
| [`anal_cell_ratio_odom.py`](../../debug_log/2026-10-15/jobs/anal_cell_ratio_odom.py) | anal_cell_ratio_odom — §7 재검: 칸을 odom 격자에 고정해, 시야 안 프레임마다 로컬 코스트맵 치명 여부와 nvblox 조각 점유 여부를 함께 셈. (2026-10-15 §12, 오늘만) | 10-15 §12 |
| [`anal_cmd_timeline.py`](../../debug_log/2026-10-15/jobs/anal_cmd_timeline.py) | anal_cmd_timeline — 한 구간의 0.5 s 칸마다 로버 자세 · 명령 · 명령 끊김 · 지도 여유. (2026-10-15 §32, 오늘만) | 10-15 §32 |
| [`anal_flicker_filter.py`](../../debug_log/2026-10-15/jobs/anal_flicker_filter.py) | anal_flicker_filter — 후보 3 오프라인 검증: 카메라만 본 칸 중 '시야 안에서 자주 빠지는(깜빡이는)' 칸만 낮춘다면, 실제 면은 남고 과장 칸만 지워지는가. (2026-10-15 §12, 오늘만) | 10-15 §12 |
| [`anal_grid_phase.py`](../../debug_log/2026-10-15/jobs/anal_grid_phase.py) | anal_grid_phase — nvblox 거리 지도 조각과 로컬 코스트맵의 격자 원점이 0.05 m 칸에 대해 어디에 놓였는지(위상)를 시간순으로. (2026-10-15 §12, 오늘만) | 10-15 §12 |
| [`anal_intdist_proxy.py`](../../debug_log/2026-10-15/jobs/anal_intdist_proxy.py) | anal_intdist_proxy — nvblox 최대 통합 거리 1.4 → 1.0 의 효과를 기록 bag 으로 어림(실주행 대체, 배터리 부족). (2026-10-15 §30.1, 오늘만) | 10-15 §30.1 |
| [`anal_intdist_slice.py`](../../debug_log/2026-10-15/jobs/anal_intdist_slice.py) | anal_intdist_slice — nvblox 거리 지도 조각(/nvblox_node/static_map_slice)에서 상자 구역 칸이 '표면(거리 ≤ 0)이 되는 순간'의 카메라 거리. (2026-10-15 §30.1, 오늘만) | 10-15 §30.1 |
| [`anal_lidar_strip.py`](../../debug_log/2026-10-15/jobs/anal_lidar_strip.py) | anal_lidar_strip — 지도 좌표의 좁은 띠(x 범위 · y 범위) 안에 라이다 점이 언제 · 몇 개 · 라이다에서 어느 방위 · 거리로 찍혔는지 시간순. (2026-10-15 §12, 오늘만) | 10-15 §12 |
| [`anal_map_vs_lidar.py`](../../debug_log/2026-10-15/jobs/anal_map_vs_lidar.py) | anal_map_vs_lidar — 그 순간의 라이다 점(지도 좌표)을 저장 지도(office_v3) 점유 칸과 겹쳐, 서쪽 벽 · 동쪽 면이 각각 얼마나 어긋나는지. (2026-10-15 §10, 오늘만) | 10-15 §10 |
| [`anal_mapfix_replan.py`](../../debug_log/2026-10-15/jobs/anal_mapfix_replan.py) | anal_mapfix_replan — 저장 지도 서쪽 벽(서쪽 통로 y −3.85~−4.45)을 오늘 라이다 위치로 고쳤다면 계획 경로가 상자 옆을 얼마나 띄워 지나는지. (2026-10-15 §11, 오늘만 — 실제 지도는 안 바꿈) | 10-15 §11 |
| [`anal_memory_shift.py`](../../debug_log/2026-10-15/jobs/anal_memory_shift.py) | anal_memory_shift — odom 에 기억된 칸이 '처음 찍힌 순간'과 '나중 순간' 사이 map→odom 변화 때문에 지도(실제 세계) 위에서 얼마나 밀렸는지. (2026-10-15 §24, 오늘만) | 10-15 24.1 · 10-22 §11 · 10-22 §11.3 · … +1 |
| [`anal_monotone_escape.py`](../../debug_log/2026-10-15/jobs/anal_monotone_escape.py) | anal_monotone_escape — '여유가 줄지 않는 곧은 이동'으로 멈춘 자세에서 빠져나갈 수 있는지, 기록된 실패 순간의 로컬 코스트맵으로 시뮬레이션. (2026-10-15 §25, 오늘만) | 10-15 25.1 |
| [`anal_motion_probe.py`](../../debug_log/2026-10-15/jobs/anal_motion_probe.py) | anal_motion_probe — 한 순간의 로컬 코스트맵 위에 차체(패딩 포함 직사각형)를 기본 움직임대로 옮겨 놓고, 치명 칸(100)에 닿는지 · 가장 가까운 치명 칸까지 거리. (2026-10-15 §5, 오늘만) | 10-15 §5 · 10-15 18.1 · 10-15 18.3 · … +1 |
| [`anal_near_cells_src.py`](../../debug_log/2026-10-15/jobs/anal_near_cells_src.py) | anal_near_cells_src — 기준 순간에 차체에서 R 안에 있던 로컬 치명 칸들을 지도 좌표로 뽑고, 칸마다 (1) 그 순간 라이다 점이 3.5 cm 안에 있었나 (2) 다른 순간들에도 그 칸이 치명이었나. (2026-10-15 §5, 오늘 | 10-15 §5 · 10-15 18.1 · 10-15 20.1 |
| [`anal_passage_gap.py`](../../debug_log/2026-10-15/jobs/anal_passage_gap.py) | anal_passage_gap — 서쪽 통로(map x ≈ −1.7)를 남북으로 지날 때, y 띠(5 cm)마다 로컬 코스트맵 치명 칸의 왼쪽(서) · 오른쪽(동) 경계와 그 사이 폭. (2026-10-15 §3, 오늘만) | 10-15 §3 |
| [`anal_path_center.py`](../../debug_log/2026-10-15/jobs/anal_path_center.py) | anal_path_center — 서쪽 통로 목표(출발점) x 를 바꾸면 남서로 가는 계획 경로가 상자 옆을 얼마나 띄워 지나는지, 기록된 전역 코스트맵으로 다시 계산. (2026-10-15 §9, 오늘만) | 10-15 9.1 |
| [`anal_replan_trace.py`](../../debug_log/2026-10-15/jobs/anal_replan_trace.py) | anal_replan_trace — 한 구간 동안 (1) 계획기 경로(/plan)가 나올 때마다 처음 0.6 m 방향과 상자 구역에 가장 가까이 가는 거리, (2) 상자 구역의 카메라만 치명 칸 수(로컬), | 10-15 §19 |
| [`anal_stall_entry.py`](../../debug_log/2026-10-15/jobs/anal_stall_entry.py) | anal_stall_entry — 멈춤 직전 몇 초, 로버가 어떻게 'Nav2 칸 검사로 서 있는 자세부터 닿음' 상태에 들어갔는지. (2026-10-15 §28, 오늘만) | 10-15 §28 · 10-15 §29.1 |
| [`anal_wiggle_amp.py`](../../debug_log/2026-10-15/jobs/anal_wiggle_amp.py) | anal_wiggle_amp — 좌우 틀기의 '크기': 명령 각속도 부호 바뀜을 문턱 0.05 · 0.10 · 0.20 rad/s 로 각각 세고, 명령 ω 와 실제 차체 각속도(EKF)의 흔들림 크기(RMS, 1 s 이동평균을 뺀 고주파 성분). (2 | 10-15 §16 |
| [`cat_nvyaml.sh`](../../debug_log/2026-10-15/jobs/cat_nvyaml.sh) | (10-15 §22) Jetson nvblox_local.yaml 내용 출력 — 읽기만 | — |
| [`chk_after_reboot.sh`](../../debug_log/2026-10-15/jobs/chk_after_reboot.sh) | (10-15 §2) 재부팅 뒤 상태 확인 — 신원(호스트 이름·Jetson 릴리스·작업 폴더) · /tmp 기동 스크립트 · 컨테이너 · 망. 로버 안 움직임 | 10-15 §1.1 |
| [`chk_band_loaded.sh`](../../debug_log/2026-10-15/jobs/chk_band_loaded.sh) | (10-15 §29) ClearanceBandCritic 적재 · 오류 · 제어 주기 경고 — 로버 안 움직임 | — |
| [`chk_band_time.sh`](../../debug_log/2026-10-15/jobs/chk_band_time.sh) | (10-15 §29.6) 크리틱 계산 시간 기록 · 놓침 수 — 로버 안 움직임 | 10-15 §29.6 |
| [`chk_box_dump.py`](../../debug_log/2026-10-15/jobs/chk_box_dump.py) | chk_box_dump — 정지 상태에서 시험 상자 둘레의 세 층을 지도 좌표로 저장(Jetson 에서 실행, 로버 안 움직임). (2026-10-15 §23) | 10-15 §23 · 10-15 §24 |
| [`chk_box_face.py`](../../debug_log/2026-10-15/jobs/chk_box_face.py) | chk_box_face — 로버가 서 있는 동안 로컬 코스트맵에 찍힌 출발점 시험 상자의 서쪽 면(로버 쪽 면) x 를 프레임마다 기록. (2026-10-15 §22, Jetson 에서 실행, 로버 안 움직임) | 10-15 §22 |
| [`chk_cfg30.sh`](../../debug_log/2026-10-15/jobs/chk_cfg30.sh) | (10-15 §30) 배포 확인 — 로버 안 움직임 | — |
| [`chk_esc_context.sh`](../../debug_log/2026-10-15/jobs/chk_esc_context.sh) | (10-15 §29.6) 탈출 실행 전후 nav2.log 문맥 — 로버 안 움직임 | 10-15 §29.6 |
| [`chk_esc_log.sh`](../../debug_log/2026-10-15/jobs/chk_esc_log.sh) | (10-15 §27) nav2 로그의 탈출 · 복구 · 컨트롤러 실패 줄 — 로버 안 움직임 | 10-15 §27.5 |
| [`chk_escape_loaded.sh`](../../debug_log/2026-10-15/jobs/chk_escape_loaded.sh) | (10-15 §26) MonotoneEscape 가 behavior_server 에 올라왔는지 · BT 가 새 xml 을 읽었는지 — 로버 안 움직임 | 10-15 §26 |
| [`chk_logkeep_missed.sh`](../../debug_log/2026-10-15/jobs/chk_logkeep_missed.sh) | (10-15 §29.2) /tmp/logkeep 의 지난 nav2 로그마다 제어 주기 놓침 · 목표 성공 수 — 로버 안 움직임 | 10-15 §29.2 |
| [`chk_missed_hist.sh`](../../debug_log/2026-10-15/jobs/chk_missed_hist.sh) | (10-15 §29.2) 제어 주기 놓침 경고의 10 s 단위 분포 + 목표 시작/끝 시각 — 로버 안 움직임 | 10-15 §29.2 |
| [`chk_missed_sec.sh`](../../debug_log/2026-10-15/jobs/chk_missed_sec.sh) | (10-15 §32) 17:36:00~17:37:20 초별 제어 주기 놓침 수 + 이벤트(재계획 · 취소 · 탈출 · 크리틱 시간) — 로버 안 움직임 | 10-15 §32 |
| [`chk_nav2_behavior_src.sh`](../../debug_log/2026-10-15/jobs/chk_nav2_behavior_src.sh) | (10-15 §26) Nav2 humble behavior 플러그인 구조 확인 — 헤더 읽기만, 로버 안 움직임 | 10-15 §26 |
| [`chk_navlog_f2v1.sh`](../../debug_log/2026-10-15/jobs/chk_navlog_f2v1.sh) | (10-14 10-15 §3) f2v1 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임 | — |
| [`chk_navlog_f2v1r.sh`](../../debug_log/2026-10-15/jobs/chk_navlog_f2v1r.sh) | (10-14 §22) f2v1r 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임 | — |
| [`chk_navlog_f2v2.sh`](../../debug_log/2026-10-15/jobs/chk_navlog_f2v2.sh) | (10-14 §22) f2v2 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임 | — |
| [`chk_navlog_f2v3.sh`](../../debug_log/2026-10-15/jobs/chk_navlog_f2v3.sh) | (10-14 §22) f2v3 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임 | — |
| [`chk_navlog_f2v4.sh`](../../debug_log/2026-10-15/jobs/chk_navlog_f2v4.sh) | (10-14 §22) f2v4 뒤: 스무딩 실패 시각, 목표 시작/끝, 복구 동작, pad_relief 기록 — 로버 안 움직임 | — |
| [`chk_nvblox_site.sh`](../../debug_log/2026-10-15/jobs/chk_nvblox_site.sh) | (10-15 §13) nvblox 컨테이너 안에서 ESDF 'site' 판정 소스·기본값 찾기 — 읽기만, 로버 안 움직임 | 10-15 §13 |
| [`chk_nvyaml.sh`](../../debug_log/2026-10-15/jobs/chk_nvyaml.sh) | (10-15 §22) nvblox_local.yaml 배포 경로 확인 — 읽기만, 로버 안 움직임 | 10-15 §22 |
| [`chk_pose_map.py`](../../debug_log/2026-10-15/jobs/chk_pose_map.py) | chk_pose_map — 로버 지도 자세(map→base_link). 로버 안 움직임. | — |
| [`chk_run_nav2.sh`](../../debug_log/2026-10-15/jobs/chk_run_nav2.sh) | (10-15 §29.2) 주행 뒤 nav2.log 요약: 제어 주기 놓침 · 컨트롤러 실패 · 복구 · 탈출 · 목표 결과 — 로버 안 움직임 | — |
| [`chk_scan_near.py`](../../debug_log/2026-10-15/jobs/chk_scan_near.py) | chk_scan_near — 라이다 점 중 차체 직사각형(0.25/-0.25/±0.165)에 가장 가까운 10 개(몸체 좌표, 여유 cm). 로버 안 움직임. | 10-15 §27.1 |
| [`chk_src_md5.sh`](../../debug_log/2026-10-15/jobs/chk_src_md5.sh) | (10-15 §26) 배포 전 Jetson src 파일 md5 — 읽기만 | 10-15 §26 |
| [`fig_box_dump.py`](../../debug_log/2026-10-15/jobs/fig_box_dump.py) | fig_box_dump — 시험 상자 둘레 세 층(카메라 깊이 점군 · nvblox 거리 지도 · 로컬 코스트맵)을 site 2.0 / 1.0 두 조건 나란히, 실제 상자 위치와 함께. (2026-10-15 §23, 오늘만) | 10-15 §23 |
| [`fig_passage_f2w2.py`](../../debug_log/2026-10-15/jobs/fig_passage_f2w2.py) | fig_passage_f2w2 — 마지막 주행 f2w2(no5, ClearanceBandCritic 켬)의 서쪽 통로 남행 구간: 움직임 · 장애물 · 명령 · 놓침 한 장. (2026-10-15 §33, 오늘만) | 10-15 §33 |
| [`fig_stall_cells.py`](../../debug_log/2026-10-15/jobs/fig_stall_cells.py) | fig_stall_cells — 서쪽 통로 남쪽 정지 자리: 멈추기 전 · 멈춘 순간 · 복귀 출발의 로컬 치명 칸(라이다 확인 / 카메라만)과 차체, 그리고 차체 옆 여유의 시간 변화. (2026-10-15 §6, 오늘만) | 10-15 §6 |
| [`fig_stall_view.py`](../../debug_log/2026-10-15/jobs/fig_stall_view.py) | fig_stall_view — 정지 순간 로버 주변: 전역 코스트맵 바탕 + 로컬 치명 칸 + 라이다 + 계획기 경로 + 차체. (2026-10-15 §3, 10-14 fig_box_end_plans.py 를 창 위치만 인자로 바꿔 복사) | 10-15 §3 |
| [`run_escape_test.py`](../../debug_log/2026-10-15/jobs/run_escape_test.py) | run_escape_test — MonotoneEscape 실제 시험 단계별 도구(Jetson 에서 실행). (2026-10-15 §27) | 10-15 §27 · 10-15 §27.3 · 10-15 §27.4 |
| [`run_f2c.sh`](../../debug_log/2026-10-15/jobs/run_f2c.sh) | 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5] | 10-07 §2.1 · 10-07 §2.2 · 10-07 §2.4 · … +31 |
| [`up_band_critic.sh`](../../debug_log/2026-10-15/jobs/up_band_critic.sh) | (10-15 §29) ClearanceBandCritic 배포 + 빌드 — /tmp/cbc.tar 를 src 에 풀고(바뀌는 원본은 날짜 붙여 백업) colcon 빌드. 로버 안 움직임 | 10-15 §29 |
| [`up_cfg_intdist.sh`](../../debug_log/2026-10-15/jobs/up_cfg_intdist.sh) | (10-15 §30) nvblox 통합 거리 1.0 · ClearanceBandCritic 끔 설정 배포 — /tmp 의 두 yaml 을 Jetson src 로(원본 백업). 설치본은 src 링크라 다음 기동부터. 로버 안 움직임 | 10-15 §30 · 10-15 §30.1 |
| [`up_escape.sh`](../../debug_log/2026-10-15/jobs/up_escape.sh) | (10-15 §26) MonotoneEscape 배포 + 빌드 — /tmp/esc.tar 를 src 에 풀고(바뀌는 원본은 날짜 붙여 백업) colcon 빌드. 로버 안 움직임 | 10-15 §26 |
| [`up_escape2.sh`](../../debug_log/2026-10-15/jobs/up_escape2.sh) | (10-15 §26) package.xml 중복 의존 고친 판만 다시 배포 + 빌드. 로버 안 움직임 | 10-15 §26 |
| [`up_escape_xml.sh`](../../debug_log/2026-10-15/jobs/up_escape_xml.sh) | (10-15 §26) 플러그인 xml(name 속성 추가) 배포 — 설치본은 src 링크. 로버 안 움직임 | 10-15 §26 |
| [`up_nvyaml.sh`](../../debug_log/2026-10-15/jobs/up_nvyaml.sh) | (10-15 §22) /tmp/nvblox_local.yaml(PC 저장소 판)을 Jetson src 로 배포 — 원본은 날짜 붙여 백업. 설치본은 src 링크라 다음 기동부터 적용. 로버 안 움직임 | 10-15 22.1 |
| [`up_nvyaml_restore.sh`](../../debug_log/2026-10-15/jobs/up_nvyaml_restore.sh) | (10-15 §23) Jetson src nvblox_local.yaml 을 가장 최근 백업(site 2.0)으로 되돌림 — 지금 판은 날짜 붙여 따로 보관. 로버 안 움직임 | 10-15 §23 |

## 2026-10-19 (45)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_box_cells_in.py`](../../debug_log/2026-10-19/jobs/anal_box_cells_in.py) | anal_box_cells_in — nvblox 조각에서 '실제 상자 안' 칸 수와 상자 주변 칸 무리의 위치를 시간에 따라. (2026-10-19 §22) | 10-19 §22 · 10-20 §3 |
| [`anal_box_memory.py`](../../debug_log/2026-10-19/jobs/anal_box_memory.py) | anal_box_memory — 복귀 길 상자 옆 통과 때 지도의 상자 칸은 언제 · 어디서 본 기억인가, 그 기억이 통과 순간까지 얼마나 밀렸나. (2026-10-19 §11) | 10-19 §11 |
| [`anal_box_points.py`](../../debug_log/2026-10-19/jobs/anal_box_points.py) | anal_box_points — 깊이 영상 화소를 그 순간의 tf 로 지도 좌표 점으로 바꿔, 출발점 시험 상자의 면이 관측마다 어디에 찍히는지. (2026-10-19 §10) | 10-19 §10 · 10-19 §14 · 10-19 §22 |
| [`anal_slice_box.py`](../../debug_log/2026-10-19/jobs/anal_slice_box.py) | anal_slice_box — nvblox 거리 지도 조각(실시간 또는 재생)이 출발점 시험 상자를 실제보다 얼마나 크게 찍는지. (2026-10-19 §4) | 10-19 §4 · 10-19 §21 |
| [`anal_split_s1.py`](../../debug_log/2026-10-19/jobs/anal_split_s1.py) | anal_split_s1 — 분리 노드 S1 판정 측정(10-19 §15). 로버 안 움직임. | 10-19 §15.1 |
| [`anal_vslam_cmp.py`](../../debug_log/2026-10-19/jobs/anal_vslam_cmp.py) | anal_vslam_cmp — 오프라인 cuVSLAM(프로젝터 끔 · 켬 × IMU 융합 켬 · 끔)과 EKF 를 SLAM 자세(기준) 대비 비교. (2026-10-19 §23, PC) | 10-19 §23.1 · 10-20 §1 · 10-20 §3.1 |
| [`chk_day_start.sh`](../../debug_log/2026-10-19/jobs/chk_day_start.sh) | (10-19) 하루 시작 상태: 가동 시간 · /tmp prep 스크립트 · 디스크 · 실행 중 스택 · 배터리 — 로버 안 움직임 | 10-19 §0 |
| [`chk_depth_topic.sh`](../../debug_log/2026-10-19/jobs/chk_depth_topic.sh) | (10-19 §1) 깊이 토픽 실측: QoS · 해상도 · 주기 · 대역폭, bag 저장 형식 플러그인 — 로버 안 움직임 | 10-19 §1 |
| [`chk_eoff.sh`](../../debug_log/2026-10-19/jobs/chk_eoff.sh) | 10-19 §25: 프로젝터 끔 구성 정지 점검(읽기만) — 프로젝터 상태, 원시 IR · 깊이 주기, IR 밝기 | 10-19 §25 |
| [`chk_f2y1.sh`](../../debug_log/2026-10-19/jobs/chk_f2y1.sh) | 10-19 §19: f2y1 결과 — 러너 로그 요약, IR bag 토픽 수, 부하 지표(읽기만) | 10-19 §19.1 |
| [`chk_flash_s2.sh`](../../debug_log/2026-10-19/jobs/chk_flash_s2.sh) | (10-19 §16 S2) 정지 상태에서 지금 스택의 부하 · 흐름 측정 30 s — 번갈이 구성 판정용. 로버 안 움직임 | 10-19 §16.1 |
| [`chk_ir_exposure.py`](../../debug_log/2026-10-19/jobs/chk_ir_exposure.py) | chk_ir_exposure — 번갈이 카메라에서 IR 노출 · 게인을 실행 중에 바꿔 가며, 끈 IR 의 밝기 · 특징 수와 켠 깊이 유효 비율을 잰다. (2026-10-19 §24, Jetson, 로버 정지) | — |
| [`chk_ir_exposure_diag.sh`](../../debug_log/2026-10-19/jobs/chk_ir_exposure_diag.sh) | (10-19 §24.1) 노출 · 게인 설정 거부와 '자동 노출 끄면 끈 프레임에 점 무늬' 확인 — 파라미터 정의, CLI 설정 결과, 메타데이터 교대 · 레이저 출력, 영상 저장. 로버 안 움직임 | — |
| [`chk_ir_gain_off.sh`](../../debug_log/2026-10-19/jobs/chk_ir_gain_off.sh) | (10-19 §24.2) 번갈이 없이 프로젝터 끔에서 수동 게인 · 노출이 되는지, 되면 IR 이 얼마나 밝아지고 특징이 생기는지. 로버 안 움직임(스택은 앞 시험에서 이미 내림) | — |
| [`chk_nvblox_preproc.sh`](../../debug_log/2026-10-19/jobs/chk_nvblox_preproc.sh) | (10-19 §7) nvblox 깊이 전처리 관련 파라미터 이름 · 기본값(컨테이너 헤더 · 실행 로그) — 로버 안 움직임 | — |
| [`chk_replay_log.sh`](../../debug_log/2026-10-19/jobs/chk_replay_log.sh) | (10-19 §7) 재생 nvblox 로그의 오류 · 마지막 줄 — 인자: 꼬리표. 로버 안 움직임 | 10-19 §7 |
| [`chk_replay_params.sh`](../../debug_log/2026-10-19/jobs/chk_replay_params.sh) | (10-19 §6) 재생 nvblox 로그에서 실제 적용된 파라미터 확인 — 인자: 꼬리표 ... 로버 안 움직임 | 10-19 §6 |
| [`chk_replay_vox.sh`](../../debug_log/2026-10-19/jobs/chk_replay_vox.sh) | (10-19 §6) 재생 로그의 복셀 크기 줄 — 인자: 꼬리표 ... 로버 안 움직임 | — |
| [`depth_edge_filter.py`](../../debug_log/2026-10-19/jobs/depth_edge_filter.py) | depth_edge_filter — 깊이 bag 의 깊이 영상에서 가장자리(깊이 불연속) 화소를 지운 새 bag 을 만든다. (2026-10-19 §8, Jetson 에서 실행) | 10-19 §8 |
| [`depth_turn_filter.py`](../../debug_log/2026-10-19/jobs/depth_turn_filter.py) | depth_turn_filter — 깊이 bag 에서 로버가 빨리 돌던 순간의 깊이 프레임을 뺀 새 bag. (2026-10-19 §13, Jetson 에서 실행) | 10-19 §13 |
| [`export_vslam.py`](../../debug_log/2026-10-19/jobs/export_vslam.py) | export_vslam — 오프라인 cuVSLAM 출력 bag → 변형별 오도메트리 csv + vo_state 요약. (2026-10-19 §23, 컨테이너 안 — VisualSlamStatus 메시지 정의가 거기 있음) | 10-19 §23.1 |
| [`fig_box_zoom_cmp.py`](../../debug_log/2026-10-19/jobs/fig_box_zoom_cmp.py) | fig_box_zoom_cmp — 두 주행의 출발점 시험 상자 확대: nvblox 조각의 표면 안 칸(지도 좌표)을 출발 길 · 복귀 길 통과 순간마다 나란히. (2026-10-19 §21) | 10-19 §21 |
| [`fig_ir_drive_video.py`](../../debug_log/2026-10-19/jobs/fig_ir_drive_video.py) | fig_ir_drive_video — IR 기록 주행 영상: 위 = IR1 프로젝터 끔(cuVSLAM 입력) \| 켬(점 무늬), 아래 = 지도 위 로버 · 지나온 길 · 카메라 시야 \| 시간축(회전 속도 · 특징 수). (2026-10-19 §20,  | 10-19 §20 |
| [`fig_ir_extract.py`](../../debug_log/2026-10-19/jobs/fig_ir_extract.py) | fig_ir_extract — IR bag(프로세스 안 기록, §17)에서 IR1 의 프로젝터 끔 · 켬 프레임을 짝지어 나란히 놓은 작은 영상 + 프레임별 지표 csv. (2026-10-19 §20, Jetson 에서 실행) | 10-19 §20 |
| [`get_f2z1.sh`](../../debug_log/2026-10-19/jobs/get_f2z1.sh) |  | — |
| [`get_replays.sh`](../../debug_log/2026-10-19/jobs/get_replays.sh) | (PC·WSL, 10-19 §6) 재생 출력 tgz 회수 — 인자: 꼬리표 ... | — |
| [`get_vso.sh`](../../debug_log/2026-10-19/jobs/get_vso.sh) |  | — |
| [`job551_f0drive.sh`](../../debug_log/2026-10-19/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`mk_vslam_bag.py`](../../debug_log/2026-10-19/jobs/mk_vslam_bag.py) | mk_vslam_bag — IR bag(§17 프로세스 안 기록)을 cuVSLAM 오프라인 입력 bag 으로: 프로젝터 끔 / 켬 프레임을 다른 토픽으로 나누고 IMU · tf_static 을 붙인다. (2026-10-19 §23, Jetson 호스트 | — |
| [`pack_replay.sh`](../../debug_log/2026-10-19/jobs/pack_replay.sh) | (10-19 §6) ~/bags 의 재생 출력을 /tmp 에 tgz 로 묶음(PC 회수용) — 인자: 꼬리표 ... 로버 안 움직임 | — |
| [`prep_eoff.sh`](../../debug_log/2026-10-19/jobs/prep_eoff.sh) | 10-19 §25: 프로젝터 상시 끔 구성 prep(로버 정지) | — |
| [`prep_flash.sh`](../../debug_log/2026-10-19/jobs/prep_flash.sh) | 10-19 §16: 번갈이 구성 prep(로버 안 움직임) | 10-19 §16.1 |
| [`rec_depth_test.sh`](../../debug_log/2026-10-19/jobs/rec_depth_test.sh) | (10-19 §1) 정지 30 s 깊이 bag 시험 기록 — 깊이 · camera_info · tf · tf_static, 깊이 · tf 는 best effort 구독. 저장은 재부팅에도 남는 ~/bags. 로버 안 움직임 | 10-19 §1 |
| [`rm_s2_flash.sh`](../../debug_log/2026-10-19/jobs/rm_s2_flash.sh) | 10-19 §18: 큰 bag 정리 — s2_flash30rec(§16 ③ IR 8 Hz, 수치는 §16.1 기록) 삭제. 삭제 전 대상 확인 | 10-19 §18 |
| [`run_f0.sh`](../../debug_log/2026-10-19/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_ir_exposure.sh`](../../debug_log/2026-10-19/jobs/run_ir_exposure.sh) | (10-19 §24) IR 노출 · 게인 정지 시험 — 스택 내리고(base 유지) 카메라 단독(번갈이 30, 지금 설정) → chk_ir_exposure.py → 카메라 종료. 로버 안 움직임 | — |
| [`run_nvblox_replay.sh`](../../debug_log/2026-10-19/jobs/run_nvblox_replay.sh) | (10-19 §2) 기록한 깊이 bag 을 컨테이너 nvblox 에 다시 넣어 거리 지도 조각을 얻는다 — 설정만 바꾼 오프라인 A/B 용. 로버 안 움직임 | 10-19 §2 · 10-19 §15.1 · 10-22 §5 · … +1 |
| [`run_split_s1.sh`](../../debug_log/2026-10-19/jobs/run_split_s1.sh) | (10-19 §15 S1) 분리 노드 정지 시험 — 주행 스택 내리고(base 유지) 카메라를 스택 설정 + 깊이 · IR 640×480×60 + emitter_on_off 로 띄워 | 10-19 §15.1 |
| [`run_vslam_offline.sh`](../../debug_log/2026-10-19/jobs/run_vslam_offline.sh) | (10-19 §23) 오프라인 cuVSLAM 켬/끔 비교 — 실시간 스택 내림(base 유지, 로버 정지) → 입력 bag 만들기(호스트) → 컨테이너에서 IMU 융합 켬 · 끔 두 판. | 10-19 §23.1 |
| [`run_vso.sh`](../../debug_log/2026-10-19/jobs/run_vso.sh) |  | — |
| [`up_splitter.sh`](../../debug_log/2026-10-19/jobs/up_splitter.sh) | (10-19 §15) emitter_splitter 배포 + 빌드 — /tmp/spl.tar 를 rover_bringup src 에 풀고(바뀌는 원본은 날짜 붙여 백업) colcon 빌드. | 10-19 §15.1 |
| [`vslam_offline.launch.py`](../../debug_log/2026-10-19/jobs/vslam_offline.launch.py) | 10-19 §23 오프라인 cuVSLAM — 컨테이너 안, 도메인 42, use_sim_time. 끔(/off) · 켬(/on) 프레임용 cuVSLAM 두 개를 각자 컨테이너에. | — |
| [`vslam_run_in.sh`](../../debug_log/2026-10-19/jobs/vslam_run_in.sh) | (10-19 §23) 컨테이너 안에서 실행: 오프라인 cuVSLAM 한 판 — 런치(끔 · 켬 두 개) → 출력 기록 → 입력 bag 재생(1 배속, --clock) → 정리 → csv 로 내보내기. | 10-19 §23.1 |
| [`vso_export.sh`](../../debug_log/2026-10-19/jobs/vso_export.sh) | 10-19 §23: IMU 켬 판 내보내기 재실행 + 두 판 요약 출력(읽기 위주) | — |
| [`watch_f0.sh`](../../debug_log/2026-10-19/jobs/watch_f0.sh) | 주행 로그 원격 감시(읽기만, DDS 없음): 인자 NAME | — |

## 2026-10-20 (35)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_box_face_points.py`](../../debug_log/2026-10-20/jobs/anal_box_face_points.py) | anal_box_face_points — 정지 bag 에서 깊이 '점' 자체가 상자 면 밖으로 얼마나 나오나(센서 몫) vs nvblox 칸 면(지도 몫). (2026-10-20 §8, PC) | 10-20 §8.1 · 10-20 §8.2 |
| [`anal_box_static.py`](../../debug_log/2026-10-20/jobs/anal_box_static.py) | anal_box_static — 정지 상태 짧은 bag 에서 깊이 품질과 nvblox 조각의 시험 상자 · 빈 바닥 표현을 잰다. (2026-10-20 §2, PC) | 10-20 §2.1 · 10-20 §7.4 · 10-20 §8.2 · … +1 |
| [`anal_ekf_replay.py`](../../debug_log/2026-10-20/jobs/anal_ekf_replay.py) | anal_ekf_replay — EKF 오프라인 재실행 변형(V0~V3)을 주행 때 EKF · cuVSLAM 과 함께 SLAM 기준으로 비교. (2026-10-20 §5, PC) | 10-20 §5.1 · 10-20 §6.3 · 10-21 §7 · … +5 |
| [`anal_vslam_rpe.py`](../../debug_log/2026-10-20/jobs/anal_vslam_rpe.py) | anal_vslam_rpe — 짧은 창(Δ s) 상대 오차: cuVSLAM · EKF 가 Δ 초 동안 움직인 양이 SLAM 이 본 움직임과 얼마나 다른가. (2026-10-20 §4, PC) | 10-20 §4 |
| [`chk_day_start_1020.sh`](../../debug_log/2026-10-20/jobs/chk_day_start_1020.sh) | 10-20: 하루 시작 상태 + f2z1 cuVSLAM 결과 유무(읽기만) | 10-20 §0 |
| [`chk_gateb.sh`](../../debug_log/2026-10-20/jobs/chk_gateb.sh) |  | 10-20 §9.7 |
| [`chk_hz_time.sh`](../../debug_log/2026-10-20/jobs/chk_hz_time.sh) |  | 10-20 §9.7 |
| [`chk_mem.sh`](../../debug_log/2026-10-20/jobs/chk_mem.sh) |  | — |
| [`chk_udp.sh`](../../debug_log/2026-10-20/jobs/chk_udp.sh) |  | 10-20 §7.1 |
| [`chk_udp_drops.sh`](../../debug_log/2026-10-20/jobs/chk_udp_drops.sh) | 소켓별 UDP 버림(drops) 10 s 증가 → inode → 프로세스. 읽기만 | — |
| [`chk_udp_drops2.sh`](../../debug_log/2026-10-20/jobs/chk_udp_drops2.sh) |  | 10-20 §9.3 · 10-20 §11.2 |
| [`chk_udp_rate.sh`](../../debug_log/2026-10-20/jobs/chk_udp_rate.sh) | UDP 수신 버퍼 오류 증가율 — 그림자 구성(정지) 그대로 20 s, cuVSLAM 만 잠시 멈춘 20 s 비교 | 10-20 §7.1 |
| [`chk_uid.sh`](../../debug_log/2026-10-20/jobs/chk_uid.sh) |  | — |
| [`chk_vslam_live.py`](../../debug_log/2026-10-20/jobs/chk_vslam_live.py) | chk_vslam_live — (10-20 §6.1) 정지 중 cuVSLAM 그림자 구성 측정. 노드 1 개 + /proc. 인자: 초(기본 60) | 10-20 §6.1 · 10-20 §9.2 · 10-20 §11.2 |
| [`fig_box_static.py`](../../debug_log/2026-10-20/jobs/fig_box_static.py) | fig_box_static — B 시험(10-20 §2) 그림: 구성별 깊이 영상 한 장(160×120) + 마지막 nvblox 조각의 상자 근처 칸. 인자: 출력.png 이름=bag ... | 10-20 §2.1 |
| [`fig_shm_day.py`](../../debug_log/2026-10-20/jobs/fig_shm_day.py) | fig_shm_day — 10-20 §7.5 · §9.3 · §9.5 수치(출력 원문에서 옮김)를 한 그림으로. 인자: 출력.png | 10-20 §10 |
| [`fill_report_1020.py`](../../debug_log/2026-10-20/jobs/fill_report_1020.py) | 10-20 정리 페이지: 머리(10-19 스타일) + 본문 + 그림(data URI) → report_1020.html | 10-20 §10 |
| [`get_bt.sh`](../../debug_log/2026-10-20/jobs/get_bt.sh) |  | — |
| [`get_dc.sh`](../../debug_log/2026-10-20/jobs/get_dc.sh) |  | 10-20 §8.3 |
| [`get_sh.sh`](../../debug_log/2026-10-20/jobs/get_sh.sh) |  | 10-20 §9.3 |
| [`get_vso_f2z1.sh`](../../debug_log/2026-10-20/jobs/get_vso_f2z1.sh) |  | — |
| [`job551_f0drive_1020.sh`](../../debug_log/2026-10-20/jobs/job551_f0drive_1020.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | — |
| [`mk_ekf_replay_bag.py`](../../debug_log/2026-10-20/jobs/mk_ekf_replay_bag.py) | mk_ekf_replay_bag — EKF 오프라인 재실행용 입력 bag 을 만든다. (2026-10-20 §5, PC) | 10-20 §5 · 10-20 §5.1 · 10-20 §5.2 |
| [`mk_ekf_replay_params.py`](../../debug_log/2026-10-20/jobs/mk_ekf_replay_params.py) | mk_ekf_replay_params — ekf.yaml(주행 구성)에서 재실행 변형 V0~V3 파라미터 파일을 만든다. (2026-10-20 §5) | 10-20 §5.1 · 10-20 §5.2 |
| [`report_1020_body.html`](../../debug_log/2026-10-20/jobs/report_1020_body.html) |  | — |
| [`report_1020_head.html`](../../debug_log/2026-10-20/jobs/report_1020_head.html) |  | — |
| [`run_box_depth_ab.sh`](../../debug_log/2026-10-20/jobs/run_box_depth_ab.sh) | (10-20 §2) B 시험: 프로젝터 켬(지금) vs 상시 끔 — 각 구성 prep → 20 s 안정 → 20 s 기록 → 마지막에 지금 구성으로 복귀. 로버 안 움직임 | 10-20 §2.1 |
| [`run_decim_ab.sh`](../../debug_log/2026-10-20/jobs/run_decim_ab.sh) | (10-20 §8.2) 데시메이션 정지 A/B — D4 → D2 → D1 → D4. 각 prep → 20 s → 25 s 기록 + CPU · nvblox 깊이 Hz. 끝나면 D4 복귀. 로버 안 움직임 | 10-20 §8.2 · 10-20 §8.3 |
| [`run_ekf_replay.sh`](../../debug_log/2026-10-20/jobs/run_ekf_replay.sh) | (10-20 §5) EKF 오프라인 재실행 — WSL(ROS Humble) 에서 입력 bag 재생 + EKF 변형 4 개 동시, 출력 bag 기록. Jetson · 로버 안 씀. | 10-20 §5.1 |
| [`run_f2c.sh`](../../debug_log/2026-10-20/jobs/run_f2c.sh) | 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5] | 10-07 §2.1 · 10-07 §2.2 · 10-07 §2.4 · … +31 |
| [`run_shm_restart.sh`](../../debug_log/2026-10-20/jobs/run_shm_restart.sh) | (10-20 §9.4) N-SHM S3 — S 구성 prep 10 회 + 사고 모사(-9). 건강은 로그로만. 마지막 회 구성 그대로 둠. 로버 안 움직임 | 10-20 §9.5 |
| [`run_shm_static.sh`](../../debug_log/2026-10-20/jobs/run_shm_static.sh) | (10-20 §9.2) N-SHM S2 정지 A/B — U(UDP) → S(dds_shm) → U. 각 prep → 20 s → 60 s 측정 → 25 s 기록. 마지막은 S 로 둔다(다음 단계용). 로버 안 움직임 | 10-20 §9.3 · 10-20 §11.2 |
| [`run_vslam_static.sh`](../../debug_log/2026-10-20/jobs/run_vslam_static.sh) | (10-20 §6.1) L0 정지 시험 — A: 프로젝터 상시 끔 / B: + vslam:=shadow. 각 prep → 20 s → 60 s 측정. B 상태로 둔다. 로버 안 움직임 | 10-20 §6.1 |
| [`up_shm.sh`](../../debug_log/2026-10-20/jobs/up_shm.sh) | (10-20 §9.1) N-SHM S1 배포 + 빌드 — /tmp/vs_* 를 rover_bringup src 에(원본 날짜 백업), 새 config 파일이라 colcon 빌드. 로버 안 움직임 | — |
| [`up_vslam.sh`](../../debug_log/2026-10-20/jobs/up_vslam.sh) | (10-20 §6) cuVSLAM 실시간 그림자 구성 배포 + 빌드 — /tmp/vs_* 를 rover_bringup src 에(바뀌는 원본은 날짜 붙여 백업), prep_fast 는 /tmp 판 교체. 로버 안 움직임 | — |

## 2026-10-21 (47)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_birth_vs_slice.py`](../../debug_log/2026-10-21/jobs/anal_birth_vs_slice.py) | anal_birth_vs_slice — 전역 LETHAL 칸(저장 지도 밖)이 처음 생긴 그 순간, nvblox 슬라이스(바로 그때 받은 판)도 그 자리를 점유로 갖고 있었나. (2026-10-21 §13, PC) | 10-21 §13 · 10-21 §23 |
| [`anal_cells_shift_xcorr.py`](../../debug_log/2026-10-21/jobs/anal_cells_shift_xcorr.py) | anal_cells_shift_xcorr — 두 시각의 전역 LETHAL 칸(저장 지도 칸 제외) 집합을 겹쳐, 가장 잘 겹치는 이동량을 찾는다. (2026-10-21 §13, PC) | 10-21 §13 · 10-21 §23 |
| [`anal_cmd_dips.py`](../../debug_log/2026-10-21/jobs/anal_cmd_dips.py) | anal_cmd_dips — 주행 중 /cmd_vel 전진 명령이 0 근처(< 0.01 m/s)로 떨어진 '짧은 멈칫'을 묶어 세고, 바로 앞(≤ 1.5 s) nav2 사건과 맞춘다. (2026-10-21 §11, PC) | 10-21 §11.3 · 10-21 §23 |
| [`anal_dip_events.py`](../../debug_log/2026-10-21/jobs/anal_dip_events.py) | anal_dip_events — /cmd_vel 전진 명령이 0 근처(< 0.01)로 떨어진 묶음마다, 0.01 s 시각 nav2 사건(앞 2 s ~ 뒤 0.5 s)과 명령값 흐름을 나란히. (2026-10-21 §12, PC) | 10-21 §12 · 10-21 §23 · 10-22 §4.2 · … +2 |
| [`anal_goal_block.py`](../../debug_log/2026-10-21/jobs/anal_goal_block.py) | anal_goal_block — 목표 주변이 왜 막혔나: 목표점 둘레의 전역 코스트맵 칸 · 라이다 점을 시각별로. (2026-10-21 §10, PC) | 10-21 §10 · 10-21 §23 |
| [`anal_mx1.py`](../../debug_log/2026-10-21/jobs/anal_mx1.py) | anal_mx1 — 10-21 §19 번갈이 중 수동 노출 · 게인 시험(시험 컨테이너 안, 로버 안 움직임). | 10-21 §19 · 10-21 §23 |
| [`anal_mx2_leak.py`](../../debug_log/2026-10-21/jobs/anal_mx2_leak.py) | 10-21 §19.3 끈 프레임 점 새어 듦 — 저장된 한 장씩(설정당 1 장, 참고값): 흰 점(top-hat 5×5 > 20) 연결 성분 수, 전체 · 아래 1/4 | 10-21 §23 |
| [`anal_nv_static.py`](../../debug_log/2026-10-21/jobs/anal_nv_static.py) | anal_nv_static — 10-21 §18 3번 정지 시험 nv1 측정(새 이미지 컨테이너 안에서, 로버 안 움직임). | 10-21 §18 · 10-21 §18.2 · 10-21 §23 |
| [`anal_phantom_birth.py`](../../debug_log/2026-10-21/jobs/anal_phantom_birth.py) | anal_phantom_birth — '카메라 층만' LETHAL 덩어리가 언제 생겼나: 상자 영역 안 칸이 처음 100 이 된 시각과 그때 로버 자세(거리 · 카메라 기준 방위). (2026-10-21 §13, PC) | 10-21 §13 · 10-21 §23 |
| [`anal_phantom_cells.py`](../../debug_log/2026-10-21/jobs/anal_phantom_cells.py) | anal_phantom_cells — 전역 코스트맵의 LETHAL(값 100) 칸을 근거별로 나눈다: 저장 지도(/map 점유)에 있음 · 지금 라이다 점 근처 · 둘 다 아님(= 카메라 층만, '유령' 후보). (2026-10-21 §13, PC) | 10-21 §13 · 10-21 §14 · 10-21 §15 · … +3 |
| [`anal_phantom_shift.py`](../../debug_log/2026-10-21/jobs/anal_phantom_shift.py) | anal_phantom_shift — 가설 검사: '카메라 층만' LETHAL 칸은 nvblox 가 odom 좌표로 기억한 진짜 벽 · 상자가, 그 뒤 SLAM 의 map→odom 보정이 바뀌면서 | 10-21 §13 · 10-21 §23 |
| [`anal_pr1.py`](../../debug_log/2026-10-21/jobs/anal_pr1.py) | anal_pr1 — 10-21 §21 깊이 프리셋 정지 시험(호스트, 로버 안 움직임). | 10-21 §21 · 10-21 §23 · 10-22 §14 |
| [`anal_stops.py`](../../debug_log/2026-10-21/jobs/anal_stops.py) | anal_stops — 주행 중 '멈춤' 구간 찾기: EKF 속도(\|v\| < 0.01 m/s 이고 \|ω\| < 0.05 rad/s)가 1 s 넘게 이어진 구간. (2026-10-21 §11, PC) | 10-21 §11.3 · 10-21 §23 · 10-22 §4.2 · … +3 |
| [`anal_topic_gaps.py`](../../debug_log/2026-10-21/jobs/anal_topic_gaps.py) | anal_topic_gaps — bag 안 토픽별 수신 시각(기록 시각) 기준 평균 Hz · 0.5 s 넘는 끊김 수 · 최대 간격. (2026-10-21 §7, PC) | 10-21 §7 · 10-21 §23 · 10-22 §20 |
| [`anal_zone_ghosts.py`](../../debug_log/2026-10-21/jobs/anal_zone_ghosts.py) | anal_zone_ghosts — 지정 영역에서 주행 한 구간 동안 로컬 코스트맵 LETHAL 이 한 번이라도 된 칸(저장 지도 0.10 m 밖 · 그 순간 라이다 점 0.10 m 밖)을 모두 센다. (2026-10-21 §15, PC) | 10-21 §15 · 10-21 §21 · 10-21 §21.2 · … +5 |
| [`chk_isaac_rs_prereq.sh`](../../debug_log/2026-10-21/jobs/chk_isaac_rs_prereq.sh) | 2번(컨테이너 RealSense 층 + realsense_splitter) 사전 조사 — 읽기만 (10-21 §17) | — |
| [`chk_isaac_rs_prereq2.sh`](../../debug_log/2026-10-21/jobs/chk_isaac_rs_prereq2.sh) |  | — |
| [`chk_isaac_rs_prereq3.sh`](../../debug_log/2026-10-21/jobs/chk_isaac_rs_prereq3.sh) |  | — |
| [`chk_isaac_rs_prereq4.sh`](../../debug_log/2026-10-21/jobs/chk_isaac_rs_prereq4.sh) |  | — |
| [`chk_nav_f2sm2h.sh`](../../debug_log/2026-10-21/jobs/chk_nav_f2sm2h.sh) |  | — |
| [`chk_nav_ms.sh`](../../debug_log/2026-10-21/jobs/chk_nav_ms.sh) | nav2.log 사건을 0.01 s 시각으로 — 인자: 시작HH:MM:SS 끝HH:MM:SS | 10-21 §12 · 10-21 §23 · 10-22 §4 |
| [`chk_nv_cmp.sh`](../../debug_log/2026-10-21/jobs/chk_nv_cmp.sh) | 옛 컨테이너 vs 시험 컨테이너 설정 차이 · 옛 cuVSLAM 기동 로그에도 NitrosContext 오류가 있나 | — |
| [`chk_nv_log.sh`](../../debug_log/2026-10-21/jobs/chk_nv_log.sh) | nv1 0 Hz 원인: 기동 로그 · 오류 앞뒤 · 환경 | — |
| [`chk_nv_probe.sh`](../../debug_log/2026-10-21/jobs/chk_nv_probe.sh) | nv1 실패 판별: (1) 시험 컨테이너 쓰기 층(apt 설치)을 이미지로 보존 (2) /dev 전체 마운트 빼고 옛 컨테이너와 같은 옵션으로 재생성 | — |
| [`chk_rs_apt_sim.sh`](../../debug_log/2026-10-21/jobs/chk_rs_apt_sim.sh) | 시험 컨테이너 안 apt 모의 설치(-s, 실제 설치 안 함): 옛 컨테이너와 같은 판의 nvblox·cuVSLAM 을 넣으면 realsense 4.51.1 이 바뀌는가 | 10-21 §17.1 · 10-21 §23 |
| [`chk_rs_build.sh`](../../debug_log/2026-10-21/jobs/chk_rs_build.sh) |  | — |
| [`chk_rs_ws.sh`](../../debug_log/2026-10-21/jobs/chk_rs_ws.sh) | 왜 colcon 이 realsense_splitter 를 못 찾나 · nvblox_ros/cuVSLAM 은 어디 설치돼 있나 | 10-21 §17.1 |
| [`chk_rs_ws2.sh`](../../debug_log/2026-10-21/jobs/chk_rs_ws2.sh) | 옛 컨테이너의 nvblox/cuVSLAM 출처(apt?) · 새 이미지에 있나 · 분리 노드 의존성 | 10-21 §17.1 |
| [`chk_splitter_src.sh`](../../debug_log/2026-10-21/jobs/chk_splitter_src.sh) |  | — |
| [`fig_day_summary_1021.py`](../../debug_log/2026-10-21/jobs/fig_day_summary_1021.py) | 10-21 하루 정리 페이지 생성기 — 본문 수치는 SUMMARY.md §0~§22 에서 옮김, 그림은 figures/ 의 PNG 를 그대로 넣음 | 10-21 §22 |
| [`fig_mx2_page.py`](../../debug_log/2026-10-21/jobs/fig_mx2_page.py) | 10-21 §19.3 mx2 결과 정리 페이지 생성기 — 수치는 outputs/run_mx2.txt · anal_mx2_leak.txt 에서 옮김, 그림은 mx_img/*.png 를 그대로 넣음 | 10-21 §19.3 |
| [`job550_f0run.py`](../../debug_log/2026-10-21/jobs/job550_f0run.py) | F0 코스 확장 러너 (2026-09-23): 상자 코스와 무관한 연속 목표 주행 + 왕복 복귀 오차 계측. | 09-23 16 · 09-28 §12 · 09-28 §16 · … +5 |
| [`job551_f0drive.sh`](../../debug_log/2026-10-21/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`job613_pathyaw.py`](../../debug_log/2026-10-21/jobs/job613_pathyaw.py) | 경로 끝 방향 조회(단독 프로세스, 2026-09-28 §20): 현재 위치 → (GX, GY) 경로를 planner(GridBased)에서 받아 끝 0.3 m 구간 방향(rad)을 출력. | 09-28 §20 · 10-13 §4 · 10-21 §3 |
| [`mx_cam.launch.py`](../../debug_log/2026-10-21/jobs/mx_cam.launch.py) | 10-21 §19 mx1 — 시험 컨테이너(isaac_rs_test, 드라이버 4.51.1 · librealsense 2.55.1 RSUSB) 안 카메라만. | 10-21 §19 · 10-21 §23 |
| [`nv_static.launch.py`](../../debug_log/2026-10-21/jobs/nv_static.launch.py) | 10-21 §18 3번 정지 시험 nv1 — NVIDIA 권장 구성 그대로: RealSense 드라이버(4.51.1-isaac) + realsense_splitter + cuVSLAM 을 한 component container 에. | 10-21 §18 · 10-21 §18.2 · 10-21 §23 |
| [`prep_back_1021.sh`](../../debug_log/2026-10-21/jobs/prep_back_1021.sh) | 시험 컨테이너 잔여 프로세스 정리 뒤 운용 구성 복귀 | — |
| [`put_one.sh`](../../debug_log/2026-10-21/jobs/put_one.sh) | (PC·WSL) 스크래치패드의 파일을 Jetson /tmp 로 전송(CR 제거). 인자: 파일명 ... 비밀번호는 run_jn.sh 에서 읽는다(여기에 적지 않음). | 10-20 §2.1 · 10-21 §3 |
| [`run_f0.sh`](../../debug_log/2026-10-21/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_f2c.sh`](../../debug_log/2026-10-21/jobs/run_f2c.sh) | 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5] | 10-07 §2.1 · 10-07 §2.2 · 10-07 §2.4 · … +31 |
| [`run_mx1.sh`](../../debug_log/2026-10-21/jobs/run_mx1.sh) | 10-21 §19 mx1 — 로버 안 움직임. 주행 스택 내리고(base 유지) 시험 컨테이너 isaac_rs_test 에서 카메라만 띄워 | 10-21 §19 · 10-21 §23 |
| [`run_mx2.sh`](../../debug_log/2026-10-21/jobs/run_mx2.sh) | 10-21 §19.2 mx2 — 로버 안 움직임. 주행 스택 내리고(base 유지) 시험 컨테이너에서 카메라만, P30 번갈이. | 10-21 §19.2 · 10-21 §23 |
| [`run_nv_static.sh`](../../debug_log/2026-10-21/jobs/run_nv_static.sh) | 10-21 §18 3번 정지 시험 nv1 — 로버 안 움직임. 주행 스택을 내리고(base 유지) 새 이미지 컨테이너 isaac_rs_test 안에서 | 10-21 §18 · 10-21 §23 |
| [`run_pr1.sh`](../../debug_log/2026-10-21/jobs/run_pr1.sh) | 10-21 §21 pr1 — 로버 안 움직임. (1) camera.launch.py 에 depth_preset 인자 배포(Jetson 사본이 저장소 HEAD 와 같을 때만) | 10-21 §21 · 10-21 §23 |
| [`up_rs_apt.sh`](../../debug_log/2026-10-21/jobs/up_rs_apt.sh) | 10-21 §17.1 2번 마무리(재): 시험 컨테이너에만 옛 컨테이너와 같은 판 nvblox 3.2.5 · cuVSLAM 3.2.6 · bringup 3.2.13 apt 설치(모의 결과 Inst 46 · Remv 0 · realsense 변경 없음) | 10-21 §23 |
| [`up_rs_image_build.sh`](../../debug_log/2026-10-21/jobs/up_rs_image_build.sh) | 10-21 §17 — 새 이미지 isaac_ros_dev-aarch64-rs 빌드(지금 이미지 + NVIDIA Dockerfile.realsense). 백그라운드, 로그 ~/rs_build/build.log | — |
| [`up_rs_splitter.sh`](../../debug_log/2026-10-21/jobs/up_rs_splitter.sh) | 10-21 §17 2번 마무리 — 새 이미지로 시험 컨테이너 isaac_rs_test 생성(지금 컨테이너와 같은 옵션 + /dev 마운트: 카메라 재열거 대비), | 10-21 §17.1 · 10-21 §18.2 · 10-21 §23 |

## 2026-10-22 (48)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_box_detect.py`](../../debug_log/2026-10-22/jobs/anal_box_detect.py) | anal_box_detect — 출발점 낮은 상자 감지 시각(2026-10-22 §2, PC). | 10-22 §2 · 10-22 §3 · 10-22 §5 |
| [`anal_box_maps_series.py`](../../debug_log/2026-10-22/jobs/anal_box_maps_series.py) | anal_box_maps_series — 상자 영역(기록 상자 ±0.05 m) 칸 수를 세 지도에서 시간 묶음별로: nvblox 조각 · 로컬 코스트맵 LETHAL · 전역 코스트맵 LETHAL, 로버 위치 · 상자까지 거리 · 방위(2026-10-2 | 10-22 §13 · 10-22 §13.1 · 10-22 §15 |
| [`anal_box_outside.py`](../../debug_log/2026-10-22/jobs/anal_box_outside.py) | anal_box_outside — 복귀 때 상자 칸 밖(테두리 밖)에 찍힌 nvblox 칸이 언제 · 어디서 본 것인지(2026-10-22 §11, PC). | 10-22 §11 · 10-22 §12 |
| [`anal_box_series.py`](../../debug_log/2026-10-22/jobs/anal_box_series.py) | anal_box_series — 출발점 낮은 상자 영역(1.15~1.35, -0.20~0.05) 로컬 LETHAL 칸 수와 로버-상자 거리를 10 s 묶음으로(주행 전체). (2026-10-22 §3, PC) | 10-22 §3 |
| [`anal_carve.py`](../../debug_log/2026-10-22/jobs/anal_carve.py) | anal_carve — 깊이 원시 화소로, 지정 칸 기둥(지도 x0~x1 · y0~y1 · 높이 z 0.06~0.30 = 조각 띠)에 대해 프레임마다 | 10-22 §11.3 · 10-22 §13 |
| [`anal_cell_timeline.py`](../../debug_log/2026-10-22/jobs/anal_cell_timeline.py) | anal_cell_timeline — 지정 칸들이 nvblox 조각에서 장애물이었던 시간 구간과, 그 구간에 상자가 카메라에 보였는지(2026-10-22 §11.2, PC). | 10-22 §11.2 · 10-22 §14.2 · 10-22 §16 |
| [`anal_contact.py`](../../debug_log/2026-10-22/jobs/anal_contact.py) | anal_contact — 차체 외곽(footprint)과 출발점 낮은 상자(기록 위치) 사이 최소 거리를 시간순으로, 가까울 때 그 순간 지도들이 상자를 갖고 있었는지(2026-10-22 §13, PC). | 10-22 §13 · 10-22 §15 · 10-23 §5 · … +4 |
| [`anal_cpu_nodes.py`](../../debug_log/2026-10-22/jobs/anal_cpu_nodes.py) | anal_cpu_nodes — 러너 proc 로그(시각 · pid · 누적 CPU 틱 · (comm))로 주행 동안 프로세스별 평균 CPU %(한 코어 = 100 %) (2026-10-22 §18, PC). | 10-22 §18 |
| [`anal_door_pass.py`](../../debug_log/2026-10-22/jobs/anal_door_pass.py) | anal_door_pass — 전역 코스트맵에서 로버 → 목표로 '통과 가능한 칸'(값 < 99, 99 = INSCRIBED · 100 = LETHAL)만 밟아 닿는지(4-이웃 BFS), 문 줄(y 고정) 의 칸 값(2026-10-22 §6, PC). | 10-22 §6 · 10-22 §7 |
| [`anal_memory_shift.py`](../../debug_log/2026-10-22/jobs/anal_memory_shift.py) | anal_memory_shift — 출발 때 본 상자를 nvblox 가 odom 좌표로 기억한다고 할 때, 그 뒤 map→odom 보정만으로 지도에서 얼마나 옮겨 보이는지(2026-10-22 §11, PC). | 10-15 24.1 · 10-22 §11 · 10-22 §11.3 · … +1 |
| [`anal_mo_window.py`](../../debug_log/2026-10-22/jobs/anal_mo_window.py) | anal_mo_window — map→odom 이 W 초 창 안에서 얼마나 바뀌는지(= 그 창 동안 기억된 물체가 로버 기준으로 틀어지는 양)를 주행 앞 · 뒤 절반으로 나눠 (2026-10-22 §11.4, PC). | 10-22 §11.4 · 10-22 §12 |
| [`anal_nav_ms.py`](../../debug_log/2026-10-22/jobs/anal_nav_ms.py) | anal_nav_ms — nav2.log(PC 사본) 사건을 0.01 s 시각(KST)으로 — 10-21 chk_nav_ms.sh 의 PC 판(2026-10-22 §4). | 10-22 §4 · 10-22 §6 · 10-22 §16 · … +1 |
| [`anal_rec_effect.py`](../../debug_log/2026-10-22/jobs/anal_rec_effect.py) | anal_rec_effect — 깊이 기록이 nvblox 에 영향을 줬나(2026-10-22 §7, PC): 출발 뒤 T 초 동안 nvblox 조각 · 로컬 코스트맵 주기, 조각 지연(bag 수신 − header.stamp) 분포. | 10-22 §7 |
| [`anal_slice_zones.py`](../../debug_log/2026-10-22/jobs/anal_slice_zones.py) | anal_slice_zones — nvblox 조각(실시간 또는 재생)으로 유령 · 상자 지표(2026-10-22 §9, PC). 기준 §5. | 10-22 §9.1 · 10-22 §14.2 |
| [`anal_slip_segments.py`](../../debug_log/2026-10-22/jobs/anal_slip_segments.py) | anal_slip_segments — 주행을 시간 묶음으로 나눠 휠 · EKF · SLAM 의 회전 · 이동을 나란히(2026-10-22 §4, PC). | 10-22 §4.2 · 10-22 §12 |
| [`chk_abort_f2dr1.sh`](../../debug_log/2026-10-22/jobs/chk_abort_f2dr1.sh) | 10-22 §6 f2dr1 목표 1 ABORTED(29 s) — 13:50:20~13:51:00 nav2 사건(시각 KST) + 로그 원본을 ~/bags/logs_f2dr1 로 보관 | — |
| [`chk_day_start_1022.sh`](../../debug_log/2026-10-22/jobs/chk_day_start_1022.sh) | 10-22 하루 시작 점검(읽기만): 신원 · 재부팅 · 주소 · prep 파일 · camera.launch 판 · 컨테이너 · 스택 · 디스크 · Wi-Fi 기록 | 10-22 §0 |
| [`chk_f2sm3_logs.sh`](../../debug_log/2026-10-22/jobs/chk_f2sm3_logs.sh) | 10-22 §19 f2sm3 그림자 판정 보조: vslam_twist 10 s 통계(버림) · cuVSLAM 프레임 간격 경고 · nav_guard 로그 이상 — 로버 안 움직임 | 10-22 §20 |
| [`chk_live_cfg.sh`](../../debug_log/2026-10-22/jobs/chk_live_cfg.sh) | 10-22 §15 주행 전 실행 중 설정 확인: 카메라 프리셋 · 실시간 nvblox 통합 거리 — 로버 안 움직임(DDS 참여자 생성 — 주행 30 s 전엔 쓰지 않음) | — |
| [`chk_navguard_inst.sh`](../../debug_log/2026-10-22/jobs/chk_navguard_inst.sh) | 10-22 §18 nav_guard 설치 형태 확인(설치본이 src 링크인지) · Jetson src 판 sha — 로버 안 움직임 | 10-22 §18 |
| [`chk_prep_fail_1022.sh`](../../debug_log/2026-10-22/jobs/chk_prep_fail_1022.sh) | 10-22 §5.3 prep 3 회째 PREP_FAIL — 기다림 끝 이유 · nav2 기동 오류 | 10-22 §5.3 |
| [`chk_preset_1022.sh`](../../debug_log/2026-10-22/jobs/chk_preset_1022.sh) |  | 10-22 §1 |
| [`chk_rp_int2.sh`](../../debug_log/2026-10-22/jobs/chk_rp_int2.sh) | 10-22 §14 재생 출력 확인(러너 출력 스트림이 첫 재생 머리말 뒤 끊김 — 작업은 계속됨): 적용 파라미터 · 재생 시간 · 조각 수 | 10-22 §14.2 |
| [`chk_stop.sh`](../../debug_log/2026-10-22/jobs/chk_stop.sh) | 10-22 §12 정지 확인: 휠 속도 · 남은 bag 기록기 정상 종료(SIGINT) · bag 크기 | 10-22 §12.1 |
| [`chk_wifi_1022.sh`](../../debug_log/2026-10-22/jobs/chk_wifi_1022.sh) | 10-22 §5.2 f2dr1 러너 기동 실패(No route) 뒤: 신원 · 가동 시간 · Wi-Fi 끊김 기록 · 스택 생존 — 로버 안 움직임 | 10-22 §5.2 |
| [`chk_wifi_1022b.sh`](../../debug_log/2026-10-22/jobs/chk_wifi_1022b.sh) | 10-22 §5.2 13:30~13:45 Wi-Fi 끊김 · 재연결 사건만 | 10-22 §5.2 |
| [`fig_box_cells.py`](../../debug_log/2026-10-22/jobs/fig_box_cells.py) | fig_box_cells — 출발점 낮은 상자 둘레의 nvblox 장애물 칸을 위에서 본 그림(10-21 pr1_top.png 의 주행판, 2026-10-22 §10, PC). | 10-22 §10 |
| [`fig_day_summary_1022.py`](../../debug_log/2026-10-22/jobs/fig_day_summary_1022.py) | 10-22 하루 정리 페이지 생성기 — 본문 수치는 SUMMARY.md §0~§21 에서 옮김, 그림은 figures/ 의 PNG 를 그대로 넣음 | 10-22 §21 |
| [`fig_pr2_top.py`](../../debug_log/2026-10-22/jobs/fig_pr2_top.py) | fig_pr2_top — 정지 프리셋 시험 복셀(base_link 기준 5 cm, 띠 0.06~0.30 m 를 위에서 합침)을 10-21 pr1_top.png 처럼 나란히(2026-10-22 §14, PC). | 10-22 §14.1 |
| [`fig_preset_video.py`](../../debug_log/2026-10-22/jobs/fig_preset_video.py) | fig_preset_video — 두 주행을 나란히 같은 경과 시간으로 재생하는 지도 영상(2026-10-22 §10, PC). | 10-22 §10 |
| [`fig_return_video.py`](../../debug_log/2026-10-22/jobs/fig_return_video.py) | fig_return_video — 복귀 때 상자를 어떤 값으로 알고 있었고 왜 붙어 지나갔는지 보는 영상(2026-10-22 §17, PC). | 10-22 §17 |
| [`get_bag_f2lp1.sh`](../../debug_log/2026-10-22/jobs/get_bag_f2lp1.sh) | (PC·WSL) 10-22 §13 f2lp1 bag 회수(러너가 정지로 끝 처리를 못 함) — Jetson ~/bags 사본도 만듦. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-22 §13 |
| [`get_logs_f2pi1.sh`](../../debug_log/2026-10-22/jobs/get_logs_f2pi1.sh) | (PC·WSL) 10-22 §16 f2pi1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | 10-22 §16 |
| [`get_logs_f2sm3.sh`](../../debug_log/2026-10-22/jobs/get_logs_f2sm3.sh) | (PC·WSL) 10-22 §16 f2sm3 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | 10-22 §20 |
| [`get_rp_1022.sh`](../../debug_log/2026-10-22/jobs/get_rp_1022.sh) | (PC·WSL) 10-22 §9 재생 출력 회수 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-22 §9.1 |
| [`prep_dr_1022.sh`](../../debug_log/2026-10-22/jobs/prep_dr_1022.sh) | 10-22 §5 f2dr1 구성 prep: 운용(프로젝터 상시 끔 · 그림자 · SHM), 깊이 프리셋 지정 안 함(= f2sm1 과 같은 구성) | 10-22 §5 |
| [`prep_op_1022.sh`](../../debug_log/2026-10-22/jobs/prep_op_1022.sh) | 10-22 §5 §10 운용 prep(인자에 depth_preset 없음) — camera.launch 기본값 3 이 적용되는지 확인 | 10-22 §10 · 10-22 §12 · 10-22 §15 · … +1 |
| [`prep_pr_1022.sh`](../../debug_log/2026-10-22/jobs/prep_pr_1022.sh) | 10-22 f2pr1 구성 prep: 운용(프로젝터 상시 끔 · 그림자 · SHM) + 깊이 프리셋 3 | 10-22 §1 |
| [`rp_clr_1022.sh`](../../debug_log/2026-10-22/jobs/rp_clr_1022.sh) | 10-22 §11.3 상자 밖 칸이 안 지워지는 이유 재생 시험: f2dr2 깊이 bag → site 거리 1.0 vox · 통합 거리 2.0 m (기준 = mw01 재생). 로버 안 움직임 | 10-22 §11.3 |
| [`rp_int2_1022.sh`](../../debug_log/2026-10-22/jobs/rp_int2_1022.sh) | 10-22 §14 단계 3: f2lp1 깊이 bag(프리셋 3) → 통합 거리 1.4(R0 기준) · 2.0 재생. 로버 안 움직임 | 10-22 §14.1 · 10-22 §14.2 |
| [`rp_mw_1022.sh`](../../debug_log/2026-10-22/jobs/rp_mw_1022.sh) | 10-22 §9 min_weight 재생 A/B: f2dr2 깊이 bag → 컨테이너 두 번째 nvblox(ROS_DOMAIN_ID 42) — R0(기준 0.1) · mw1 · mw2. 로버 안 움직임 | 10-22 §9 |
| [`run_f2c.sh`](../../debug_log/2026-10-22/jobs/run_f2c.sh) | 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5] | 10-07 §2.1 · 10-07 §2.2 · 10-07 §2.4 · … +31 |
| [`run_pr2.sh`](../../debug_log/2026-10-22/jobs/run_pr2.sh) | 10-22 §14 pr2 — 로버 안 움직임. 깊이 프리셋 0 · 3 · 5(Medium Density) 정지 비교(10-21 pr1 과 같은 도구 anal_pr1.py, 같은 자리 · 같은 측정 20 s). | 10-22 §14 |
| [`stop_now.sh`](../../debug_log/2026-10-22/jobs/stop_now.sh) | 10-22 §12 사용자 "그만 멈춰라" — 러너 · Nav2 주행 노드 종료 → 펌웨어 watchdog(cmd_vel 500 ms 무수신 정지) + 0 속도 발행 | 10-22 §12.1 |
| [`up_cam_1022.sh`](../../debug_log/2026-10-22/jobs/up_cam_1022.sh) | 10-22 §10 camera.launch.py 배포: depth_preset 기본 -1 → 3 (사용자 결정). 이전 판 sha 확인 → /tmp 사본 → 교체 → sha 확인. 로버 안 움직임 | 10-22 §10 |
| [`up_navguard_1022.sh`](../../debug_log/2026-10-22/jobs/up_navguard_1022.sh) | 10-22 §18 nav_guard.py 배포: 피드백 기록 0.2 s 간격 · 앞에서부터 버림(CPU 25 % 대책). 이전 sha 6b7381c5d260 확인 → /tmp 사본 → 교체(실행 권한 유지). 다음 prep 부터 적용. 로버 안 움직임 | 10-22 §18 |
| [`up_nvy_1022.sh`](../../debug_log/2026-10-22/jobs/up_nvy_1022.sh) | 10-22 §15 nvblox_local.yaml 배포: 통합 거리 1.4 → 2.0 (사용자 결정). 이전 sha 확인(e86434bd8921 = Jetson 판 — 저장소 HEAD 와 머리 주석 3 줄(10-19 정정)만 다름, 값 같음) → /t | 10-22 §15 |
| [`up_prep_1022.sh`](../../debug_log/2026-10-22/jobs/up_prep_1022.sh) | 10-22 재부팅 뒤 prep 스크립트 재전송 — 저장소 Docs/tools 의 prep_fast.sh · prep_patrol.sh · chk_prep.py 를 base64 로 붙여 /tmp 에 씀(생성은 PC, 본문 생략) | 10-22 §0 · 10-23 §5.1 · 10-23 §16 |

## 2026-10-23 (39)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_cost_section.py`](../../debug_log/2026-10-23/jobs/anal_cost_section.py) | anal_cost_section — 상자 옆 단면(지도 x 고정)에서 로컬 코스트맵 비용을 y 따라(2026-10-23 §12, PC). | 10-23 §12 |
| [`anal_ctrl_eval.py`](../../debug_log/2026-10-23/jobs/anal_ctrl_eval.py) | anal_ctrl_eval — MPPI 컨트롤러 틱마다 '그 틱에 컨트롤러가 따르던 경로' 대비 로버 옆 치우침 · 방향 오차 · 경로 곡률(2026-10-23, PC, 로버 안 움직임). | 10-23 §22.3 |
| [`anal_ctrl_rate.py`](../../debug_log/2026-10-23/jobs/anal_ctrl_rate.py) | anal_ctrl_rate — MPPI 컨트롤러가 10 Hz 를 실제로 내는가: nav2 로그 경고 수 + bag 의 지령 · 컨트롤러 발행 간격(2026-10-23, PC, 로버 안 움직임). | 10-23 §22.3 |
| [`anal_ginfl_path.py`](../../debug_log/2026-10-23/jobs/anal_ginfl_path.py) | anal_ginfl_path — 전역 inflation 감쇠(cost_scaling_factor)를 바꾸면 복귀 경로가 실제 상자에서 얼마나 떨어지나(2026-10-23 §1, PC, 로버 안 움직임). | 10-23 §1.1 |
| [`anal_motion_window.py`](../../debug_log/2026-10-23/jobs/anal_motion_window.py) | anal_motion_window — 지정 시각 앞 W 초 동안 이동량을 소스별로: 명령(/cmd_vel 적분) · 휠(/wheel_odom 적분) · 주 EKF(/odometry/filtered 자세 차) · | 10-23 §10.1 |
| [`anal_mppi_stop.py`](../../debug_log/2026-10-23/jobs/anal_mppi_stop.py) | anal_mppi_stop — MPPI 가 스스로 0 근처를 고른 구간에서 무엇과 무엇이 맞섰나(2026-10-23 §7, PC, 로버 안 움직임). | 10-23 §7 · 10-23 §12 |
| [`anal_pathalign_occ.py`](../../debug_log/2026-10-23/jobs/anal_pathalign_occ.py) | anal_pathalign_occ — 상자 옆에서 MPPI PathAlignCritic 이 꺼졌을까: 컨트롤러가 받은 경로(/transformed_global_plan)의 점 중 | 10-23 §3 |
| [`anal_pba_replay.py`](../../debug_log/2026-10-23/jobs/anal_pba_replay.py) | anal_pba_replay — PathBlockedAhead 판정을 bag 으로 다시 돌려 only_new 전후를 비교(2026-10-23 §20.7, PC, 로버 안 움직임). | 10-23 §20.7 |
| [`anal_pba_replay_extend.py`](../../debug_log/2026-10-23/jobs/anal_pba_replay_extend.py) | anal_pba_replay_extend — (10-23 §20.7) only_new 로 막힘을 안 셌다면 그 경로를 목표 도착까지 계속 썼을 것: f2rp3 경로 #3(14:47:09 서쪽 통로)을 | 10-23 §20.7 |
| [`anal_pba_timing.sh`](../../debug_log/2026-10-23/jobs/anal_pba_timing.sh) | 10-23 §20.2 PathBlockedAhead '처음 막힘' 이 경로를 받은 뒤 몇 초에 나왔나(PC, 로버 안 움직임). | 10-23 §20.2 |
| [`anal_plan_series.py`](../../debug_log/2026-10-23/jobs/anal_plan_series.py) | anal_plan_series — 복귀 중 다시 그려진 전역 경로(/plan · /plan_smoothed)마다 실제 상자까지의 여유를, 출발점(로버 자리) 근처를 빼고 (2026-10-23 §4, PC). | 10-23 §4 · 10-23 §5 |
| [`anal_pose_at.py`](../../debug_log/2026-10-23/jobs/anal_pose_at.py) | anal_pose_at — 지정 시각(현지 HH:MM:SS.ss)들의 로버 지도 자세(map→odom ∘ odom→base_link) 출력(10-23 §20.3, PC). 인자: bag 시각... | 10-23 §20.3 |
| [`anal_track_dev.py`](../../debug_log/2026-10-23/jobs/anal_track_dev.py) | anal_track_dev — 상자 옆을 지날 때 '계획 경로의 여유' 와 '실제로 지나간 여유' 의 차이: 로버가 경로에서 상자 쪽으로 얼마나 벗어났나(2026-10-23 §2, PC). | 10-23 §2 · 10-23 §5 · 10-23 §10 |
| [`anal_track_err.py`](../../debug_log/2026-10-23/jobs/anal_track_err.py) | anal_track_err — 컨트롤러 경로 추종 오차: 각 전역 경로(/plan_smoothed)가 쓰이는 동안(다음 경로가 올 때까지) 로버 중심이 그 경로 선에서 옆으로 얼마나 떨어졌나 | 10-23 §14 · 10-23 §17 |
| [`chk_ctrl_gap.py`](../../debug_log/2026-10-23/jobs/chk_ctrl_gap.py) | chk_ctrl_gap — 컨트롤러 출력 토픽(/trajectories · /transformed_global_plan)이 정지 구간에 실제로 나왔나: 수신 간격 · header 시각(2026-10-23 §7, PC). | 10-23 §7 |
| [`chk_day_start_1023.sh`](../../debug_log/2026-10-23/jobs/chk_day_start_1023.sh) | 10-23 하루 시작 점검(prep 무출력 뒤): 신원 · 가동 시간 · /tmp prep 파일 · 스택 프로세스 · 배터리 — 로버 안 움직임 | 10-23 §5.1 |
| [`chk_mppi_params.py`](../../debug_log/2026-10-23/jobs/chk_mppi_params.py) | chk_mppi_params — nav2_params.yaml 의 controller_server(FollowPathMPPI 포함) 블록을 원문 그대로 남기고, 주행 bag 의 params.txt(실행 중 노드 파라미터)와 값 비교(2026-10-23 | 10-23 §22.3 |
| [`chk_opt_traj.py`](../../debug_log/2026-10-23/jobs/chk_opt_traj.py) | chk_opt_traj — MPPI 최적 궤적(32 점, 0.1 s 간격)의 점간 이동 거리 = 단계별 속도를 시각별로(2026-10-23 §7, PC). | 10-23 §7 |
| [`chk_rp_cfg.sh`](../../debug_log/2026-10-23/jobs/chk_rp_cfg.sh) | 10-23 §17 f2rp1 prep 뒤 설정 확인(출력 끊김 대비 따로) — 로버 안 움직임 | 10-23 §17.1 |
| [`chk_scan_window.py`](../../debug_log/2026-10-23/jobs/chk_scan_window.py) | chk_scan_window — 정지 구간 앞뒤로 라이다 앞쪽(±60°) 가장 가까운 점 · 방위를 1 s 마다, 로버 자세와 함께(2026-10-23 §6.2, PC). | 10-23 §6.2 |
| [`fig_day_summary_1023.py`](../../debug_log/2026-10-23/jobs/fig_day_summary_1023.py) | 10-23 하루 정리 페이지 생성기 — 본문 수치는 SUMMARY.md §0~§23 · Docs/06_planner/SMAC_HYBRID_PLAN.md §8~§9 에서 옮김, 그림은 figures/ 의 PNG 를 그대로 넣음 | 10-23 §23 |
| [`fig_mppi_stop.py`](../../debug_log/2026-10-23/jobs/fig_mppi_stop.py) | fig_mppi_stop — f2pa2 5.5 s 정지를 한 장으로(2026-10-23 §8, PC, 로버 안 움직임). | 10-23 §8 |
| [`fig_replan_video.py`](../../debug_log/2026-10-23/jobs/fig_replan_video.py) | fig_replan_video — Docs/tools/fig_run_video.py 사본 + 경로 위 막힘 표시 · nav2 사건 줄 (2026-10-23 §19). | 10-23 §19 · 10-23 §20.1 · 10-23 §20.6 |
| [`fig_return_video2.py`](../../debug_log/2026-10-23/jobs/fig_return_video2.py) | fig_return_video2 — 10-22 fig_return_video 에 MPPI 최적 궤적(/trajectories, 단계 속도 색 · 첫 단계 굵은 원)을 더한 판(2026-10-23 §12, PC). | 10-23 §12 |
| [`get_logs_f2pa1.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2pa1.sh) | (PC·WSL) 10-22 §16 f2pa1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2pa2.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2pa2.sh) | (PC·WSL) 10-22 §16 f2pa2 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2rp1.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2rp1.sh) | (PC·WSL) 10-22 §16 f2rp1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2rp2.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2rp2.sh) | (PC·WSL) 10-22 §16 f2rp2 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2rp3.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2rp3.sh) | (PC·WSL) 10-22 §16 f2rp3 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2rp4.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2rp4.sh) | (PC·WSL) 10-22 §16 f2rp4 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2rp5.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2rp5.sh) | (PC·WSL) 10-22 §16 f2rp5 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2von1.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2von1.sh) | (PC·WSL) 10-22 §16 f2von1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2von2.sh`](../../debug_log/2026-10-23/jobs/get_logs_f2von2.sh) | (PC·WSL) 10-22 §16 f2von2 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`prep_op_1022.sh`](../../debug_log/2026-10-23/jobs/prep_op_1022.sh) | 10-22 §5 §10 운용 prep(인자에 depth_preset 없음) — camera.launch 기본값 3 이 적용되는지 확인 | 10-22 §10 · 10-22 §12 · 10-22 §15 · … +1 |
| [`prep_rp_1023.sh`](../../debug_log/2026-10-23/jobs/prep_rp_1023.sh) | 10-23 §17 A 시험 prep — 운용 기본(prep_patrol: vslam on · 프로젝터 끔 · SHM) + 주기 재계획 끔(REPLAN_HZ 0.01 = 목표당 1 회, 막힘 · 목표 변경 때만 재계획) | 10-23 §17 · 10-23 §20 · 10-23 §20.4 · … +1 |
| [`prep_von_1023.sh`](../../debug_log/2026-10-23/jobs/prep_von_1023.sh) | 10-23 §10 vslam:=on prep — 운용(프로젝터 상시 끔 · SHM · 프리셋 3 기본 · 통합 2.0)에서 주 EKF 의 odom1 을 rf2o 대신 cuVSLAM 병진 속도로(ekf.launch vslam:=on) | 10-23 §10 |
| [`up_palign_1023.sh`](../../debug_log/2026-10-23/jobs/up_palign_1023.sh) | 10-23 §5 MPPI PathAlignCritic cost_weight 만 Jetson yaml(소스 · 설치본)에 반영(인자: 값, 기본 28). 실행 중 값은 안 바꿈 — 다음 prep 으로 적용(10-14 실행 중 변경 멈칫 교훈). 로버 안 | 10-23 §5 · 10-23 §10 |
| [`up_pba_onlynew_1023.sh`](../../debug_log/2026-10-23/jobs/up_pba_onlynew_1023.sh) | 10-23 §20.2 PathBlockedAhead only_new 배포: 저장소 cpp · BT xml 을 Jetson 소스에 두고 rover_navigation 만 빌드. 로버 안 움직임(실행 중 스택은 다음 prep 때 새 노드 · xml 을 읽 | 10-23 §20.2 |
| [`up_prep_patrol_1023.sh`](../../debug_log/2026-10-23/jobs/up_prep_patrol_1023.sh) | 10-23 §16 /tmp/prep_patrol.sh 를 저장소 Docs/tools 판(vslam 기본 · REPLAN_HZ 환경)으로 교체. 로버 안 움직임 | 10-23 §16 |

## 2026-10-26 (39)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_bend_dev_odom.py`](../../debug_log/2026-10-26/jobs/anal_bend_dev_odom.py) | anal_bend_dev_odom — 복귀 상자 둘레(map x 0.5~2.4, y −0.8~0.8, 마지막 통과)에서 컨트롤러 자기 좌표(odom) 기준 경로 이탈, '굽은 곳 안쪽 +' 부호 (2026-10-26 §11, PC). | 10-26 §11.1 |
| [`anal_corridor_gap.py`](../../debug_log/2026-10-26/jobs/anal_corridor_gap.py) | anal_corridor_gap — 서쪽 통로 단면(y −4.4 ~ −5.0, 0.1 m 간격)에서 전역 코스트맵 치명 칸 사이 틈 폭 · 내접(99) 아닌 칸 폭, 주행별 비교 (2026-10-26 §16, PC). | 10-26 §16 |
| [`anal_corridor_track.py`](../../debug_log/2026-10-26/jobs/anal_corridor_track.py) | anal_corridor_track — 서쪽 통로(map x −2.3~−0.9, y −5.7~−3.4)에서 로버가 컨트롤러 경로(/transformed_global_plan, odom)를 얼마나 바짝 따랐나 · 그 경로가 지나는 전역 코스트 (2026 | 10-26 §15 |
| [`anal_goal_yaw.py`](../../debug_log/2026-10-26/jobs/anal_goal_yaw.py) | anal_goal_yaw — §20 목표 방향 시험 결과 표 (2026-10-26, PC, 로버 안 움직임). | 10-26 §20.1 |
| [`anal_rev_sign.py`](../../debug_log/2026-10-26/jobs/anal_rev_sign.py) | anal_rev_sign — 바퀴 지령 방향이 뒤집히는 순간, FG 휠 속도(부호 = 마지막 지령 방향)가 실제 움직임과 어긋나는 시간 · 거리 (2026-10-26 §2, PC, 로버 안 움직임). | 10-26 §2 |
| [`anal_sim_corner_summary.py`](../../debug_log/2026-10-26/jobs/anal_sim_corner_summary.py) | anal_sim_corner_summary — §10.4 시뮬 70 판 요약(PC). 병렬 출력이 한 줄에 섞여도 '라벨 s씨앗 \|' 경계로 나눠 셈(첫 판은 섞인 줄 1 개를 놓쳐 base n 9).  인자: 원문 txt 출력 txt | 10-26 §10.5 |
| [`chk_cmd_vs_motion_f2sh2.py`](../../debug_log/2026-10-26/jobs/chk_cmd_vs_motion_f2sh2.py) | chk_cmd_vs_motion_f2sh2 — f2sh2 굽은 곳(13:18:22~38) 명령(/cmd_vel) 대 실제 움직임(EKF /odometry/filtered · /vslam/odom · 자이로 /imu/data 를 base_link 로)  | 10-26 §10.1 |
| [`chk_corr_paths.py`](../../debug_log/2026-10-26/jobs/chk_corr_paths.py) | 통로 창(16:11:45~16:13:35)에 받은 경로 메시지 목록: 토픽 · 점 수 · 점 간격 중앙(출처 판별) · 시작 · 끝 | 10-26 §19 · 10-27 §13 |
| [`chk_dev_frame_f2sh2.py`](../../debug_log/2026-10-26/jobs/chk_dev_frame_f2sh2.py) | chk_dev_frame_f2sh2 — f2sh2 복귀 굽은 곳(13:18:25~13:18:38) 경로 이탈이 컨트롤러 탓인지 위치 보정(map→odom) 탓인지 가름 (2026-10-26 §9, PC). | 10-26 §9 |
| [`chk_smac_fail_cells.py`](../../debug_log/2026-10-26/jobs/chk_smac_fail_cells.py) | Smac 실패 · 성공 순간의 출발(로버) · 목표 자세가 전역 코스트맵에서 어떤 칸인가: 중심 칸 비용, 차체 직사각형(+패딩 0.01) 안 최대 비용 · 치명(100 = 비용 254) · 내접(99 = 253) 칸 수(OccupancyGrid 0~ | 10-26 §19 |
| [`chk_w3_turn.py`](../../debug_log/2026-10-26/jobs/chk_w3_turn.py) | chk_w3_turn — W3 출발 직후 '전진 명령 0 근처' 구간에 회전 명령 · 실제 회전(EKF)이 있었나 (2026-10-26 §13, PC). 인자: bag 시작HH:MM:SS.s 끝HH:MM:SS.s | 10-26 §13 |
| [`fig_box_compare.py`](../../debug_log/2026-10-26/jobs/fig_box_compare.py) | fig_box_compare — 복귀 길 상자 옆을 B0(NavFn) 주행과 Smac 주행으로 나란히: 지나간 길 · 차체 자국 · 그때 따른 전역 경로 · 실제 최소 여유 (2026-10-26 §8, PC). | 10-26 §8 · 10-26 §12 |
| [`fig_goal_yaw.py`](../../debug_log/2026-10-26/jobs/fig_goal_yaw.py) | fig_goal_yaw — §20.1 목표 방향 시험 결과를 한 장으로: 순간(행) × 목표 방향 더하기(열), 칸 색 = Smac 성공 · 실패, 오른쪽 = 출발 자세 (2026-10-26, PC). | 10-26 §21 |
| [`fig_real_tiles.py`](../../debug_log/2026-10-26/jobs/fig_real_tiles.py) | fig_real_tiles — 실제 촬영 작업본에서 지정 시각 장면을 뽑아 시각 글씨를 붙여 격자 한 장으로(토큰 절약: 6 장 = 그림 1 장) (2026-10-26 §16, PC). | 10-26 §16 |
| [`fig_smac_expansion.py`](../../debug_log/2026-10-26/jobs/fig_smac_expansion.py) | fig_smac_expansion — Smac Hybrid 가 경로를 찾으며 '어디까지 뻗어 봤나'(방문 노드)를 그림 · 영상으로 (2026-10-26 §22, PC, 로버 안 움직임). | 10-26 §22 · 10-27 §2.1 |
| [`fill_report_1026.py`](../../debug_log/2026-10-26/jobs/fill_report_1026.py) | 10-26 정리 페이지: 머리(10-20 틀) + 본문 + 그림(data URI, figures/report/*.jpg) → figures/day_summary_1026.html (로컬 사본 = 게시 원본) | 10-26 §21 |
| [`get_logs_f2sa1.sh`](../../debug_log/2026-10-26/jobs/get_logs_f2sa1.sh) | (PC·WSL) 10-22 §16 f2sa1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2sa2.sh`](../../debug_log/2026-10-26/jobs/get_logs_f2sa2.sh) | (PC·WSL) 10-22 §16 f2sa2 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2sa3.sh`](../../debug_log/2026-10-26/jobs/get_logs_f2sa3.sh) | (PC·WSL) 10-22 §16 f2sa3 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2sh1.sh`](../../debug_log/2026-10-26/jobs/get_logs_f2sh1.sh) | (PC·WSL) 10-22 §16 f2sh1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`get_logs_f2sh2.sh`](../../debug_log/2026-10-26/jobs/get_logs_f2sh2.sh) | (PC·WSL) 10-22 §16 f2sh2 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음 | — |
| [`prep_smac_1026.sh`](../../debug_log/2026-10-26/jobs/prep_smac_1026.sh) | 10-26 §7 Smac 주행 prep — 운용 기본(prep_patrol: vslam on · 프로젝터 끔 · SHM) + 재계획 0.01 + planner:=smac(Smac Hybrid RS → 실패 시 NavFn). 로버 안 움직임 | 10-26 §7 · 10-26 §7.2 |
| [`report_1026_body.html`](../../debug_log/2026-10-26/jobs/report_1026_body.html) |  | 10-26 §21 |
| [`report_1026_head.html`](../../debug_log/2026-10-26/jobs/report_1026_head.html) |  | 10-26 §21 |
| [`run_expdbg_1026.sh`](../../debug_log/2026-10-26/jobs/run_expdbg_1026.sh) | run_expdbg_1026 — (PC) §22 Smac 탐색 기록: 진단 빌드(~/smac_dbg_ws) 오버레이로 f2sa3 통로 6 순간(목표 방향 원래 그대로)을 재질의하고 방문 노드 기록을 받아 옴. 로버 안 움직임(도메인 42). | 10-26 §22 |
| [`run_goal_yaw_1026.sh`](../../debug_log/2026-10-26/jobs/run_goal_yaw_1026.sh) | run_goal_yaw_1026 — (PC) §20 목표 방향 시험: 실주행 SmacHybrid 값(시간 상한 2.0 s) 하나 + NavFn 을 오프라인 planner_server(도메인 42)에 올려 장면 78 개 질의. 로버 안 움직임. | 10-26 §20.1 |
| [`run_sim_corner_1026.sh`](../../debug_log/2026-10-26/jobs/run_sim_corner_1026.sh) | 10-26 §10 MPPI 굽은 곳 안쪽 깎기 — 오프라인 시뮬(Docs/tools/anal_mppi_sim.py, Jetson, 로버 안 움직임). | 10-26 §10 |
| [`run_sim_corner_1026b.sh`](../../debug_log/2026-10-26/jobs/run_sim_corner_1026b.sh) | 10-26 §10.2 재현 시험: 시뮬 구동계를 펌웨어 바퀴 포화(비례 축소, wheel_max 0.085)로 — w_gain 0.7(회전만 줄임)은 곡률을 바꿔 깎기를 가렸음. 로버 안 움직임 | — |
| [`run_sim_corner_1026c.sh`](../../debug_log/2026-10-26/jobs/run_sim_corner_1026c.sh) | 10-26 §10.3 굽은 곳 깎기 변형 × 씨앗 1~6(바퀴 포화 구동계). 로버 안 움직임 | 10-26 §10.3 |
| [`run_sim_corner_1026d.sh`](../../debug_log/2026-10-26/jobs/run_sim_corner_1026d.sh) | 10-26 §10.4 굽은 곳 깎기 — 재계획 직후 13:18:10 부터 26 s, 변형 7 × 씨앗 10, 4 개씩 병렬. 로버 안 움직임 | — |
| [`run_sim_stall_1026.sh`](../../debug_log/2026-10-26/jobs/run_sim_stall_1026.sh) | 10-26 §10.6 f2pa2 정지 장면 — A14 · A28 · A28Fw5 × 씨앗 10, 4 병렬. 로버 안 움직임 | — |
| [`scenes_expdbg_1026.json`](../../debug_log/2026-10-26/jobs/scenes_expdbg_1026.json) |  | — |
| [`scenes_goal_yaw_1026.json`](../../debug_log/2026-10-26/jobs/scenes_goal_yaw_1026.json) |  | 10-26 §20.1 |
| [`up_mppi_path_1026.sh`](../../debug_log/2026-10-26/jobs/up_mppi_path_1026.sh) | 10-26 §11 MPPI PathAlign · PathFollow cost_weight 를 Jetson yaml(소스 · 설치본)에만 반영. 인자: PathAlign PathFollow(기본 28 5, 되돌리기 14 10). | 10-26 §11 |
| [`up_params_1026.sh`](../../debug_log/2026-10-26/jobs/up_params_1026.sh) | 10-26 §14 저장소 nav2_params.yaml(28 · 5 채택판)을 Jetson src · 설치본에 — 로버 안 움직임. 실행본 = 이 머리 + 스크래치패드가 붙인 base64(/tmp/up_nav2_params.yaml) | 10-26 §14 |
| [`up_prep_1026.sh`](../../debug_log/2026-10-26/jobs/up_prep_1026.sh) | 10-26 재부팅 뒤 prep 스크립트 재전송 — 저장소 Docs/tools 판(prep_fast · prep_patrol(vslam 기본) · chk_prep). 실제 실행본은 이 머리 + PC 가 붙인 base64 본문(스크래치패드 up_prep_ | 10-26 §0 · 10-26 §7.2 |
| [`up_smac_expdbg_1026.sh`](../../debug_log/2026-10-26/jobs/up_smac_expdbg_1026.sh) | 10-26 §22 Smac 탐색 기록 진단 빌드(Jetson ~/smac_dbg_ws 오버레이, 로버 안 움직임): nav2_smac_planner 1.1.20 원본(설치판과 같은 태그) + Docs/06_planner/smac_fork/nav2_sm | 10-26 §22 |
| [`up_smac_fork_1026.sh`](../../debug_log/2026-10-26/jobs/up_smac_fork_1026.sh) | 10-26 §5 Smac 포크 빌드(Jetson ~/smac_ws 오버레이, 로버 안 움직임): nav2_smac_planner 1.1.20(= apt 판과 같은 태그) + Docs/06_planner/smac_fork/nav2_smac_planner | 10-26 §5 |
| [`up_smac_nav_1026.sh`](../../debug_log/2026-10-26/jobs/up_smac_nav_1026.sh) | 10-26 §7 planner:=smac 배포(로버 안 움직임): navigation.launch.py · nav2_params.yaml · copy_path_action.cpp → ~/ros2_ws/src/rover_navigation, prep_p | 10-26 §7 |

## 2026-10-27 (73)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_block_cell.py`](../../debug_log/2026-10-27/jobs/anal_block_cell.py) | anal_block_cell — f2st1 복귀 길 막힘 판정 칸 (1.13, 0.14) 을 원자료와 대조 (2026-10-27 §14, PC, 로버 안 움직임). | 10-27 §14 · 10-27 §19 |
| [`anal_load_f2tf1.py`](../../debug_log/2026-10-27/jobs/anal_load_f2tf1.py) | anal_load_f2tf1 — §21 부하(§16 ③) 원인: 주행 중 CPU 포화 정도 · 프로세스별 몫 · TF 지연 순간과의 관계 (2026-10-27, PC). | 10-27 §21.2 |
| [`anal_parent_chain.py`](../../debug_log/2026-10-27/jobs/anal_parent_chain.py) | anal_parent_chain — Smac 탐색 기록에서 '통로 남쪽 노드가 어디를 거쳐 왔나' 를 부모 사슬로 (2026-10-27 §1 ②, PC, 로버 안 움직임). | 10-27 §2 |
| [`anal_slam_freeze.py`](../../debug_log/2026-10-27/jobs/anal_slam_freeze.py) | anal_slam_freeze — §21 SLAM map→odom stamp 멈춤 분석 (2026-10-27, PC). | 10-27 §21.2 |
| [`anal_slam_freeze_cause.py`](../../debug_log/2026-10-27/jobs/anal_slam_freeze_cause.py) | anal_slam_freeze_cause — §22 SLAM map→odom stamp 정체가 통신(UDP) 탓인가 처리 탓인가 (2026-10-27, PC). | 10-27 §22 |
| [`anal_slam_freeze_hist.py`](../../debug_log/2026-10-27/jobs/anal_slam_freeze_hist.py) | anal_slam_freeze_hist — §23 SLAM map→odom stamp 정체가 예전부터 있었나 (2026-10-27, PC, 로버 안 움직임). | 10-27 §23 |
| [`anal_slam_freeze_trigger.py`](../../debug_log/2026-10-27/jobs/anal_slam_freeze_trigger.py) | anal_slam_freeze_trigger — §26 SLAM map→odom stamp 정체가 무엇에 맞춰 나나 (2026-10-27, PC). | 10-27 §26.1 |
| [`anal_slam_replay.py`](../../debug_log/2026-10-27/jobs/anal_slam_replay.py) | anal_slam_replay — §26 SLAM 재생 변형별: map→odom stamp 정체 · 미래 여유 · SLAM CPU · 원래 주행 SLAM 과의 위치 차 (2026-10-27, PC). | 10-27 §26.2 · 10-27 §26.3 |
| [`anal_slam_timing.py`](../../debug_log/2026-10-27/jobs/anal_slam_timing.py) | anal_slam_timing — §29 계측판 SLAM 로그('[ROVER_T]')에서 처리 스캔마다 단계별 시간(ms) 분포 (2026-10-27, PC). | 10-27 §29.1 |
| [`anal_sys_perf.py`](../../debug_log/2026-10-27/jobs/anal_sys_perf.py) | anal_sys_perf — §30 현재 시스템 성능 요약용 수치: tegrastats(CPU · GPU · RAM · 전력 · 온도) 주행 구간 통계 (2026-10-27, PC). | 10-27 §30 |
| [`anal_tffix_sig.py`](../../debug_log/2026-10-27/jobs/anal_tffix_sig.py) | anal_tffix_sig — §19 §15 서명(단위 변환으로 적힌 슬라이스)이 전역 코스트맵에 있었나, 주행 전체 (2026-10-27, PC). | 10-27 §19 |
| [`anal_tolcp.py`](../../debug_log/2026-10-27/jobs/anal_tolcp.py) | anal_tolcp — §5 허용치 · cost_penalty 재질의 표 (2026-10-27, PC, 로버 안 움직임). | 10-27 §5.1 |
| [`apply_slam_tt15_1027.sh`](../../debug_log/2026-10-27/jobs/apply_slam_tt15_1027.sh) | §21 Jetson: slam.launch.py(transform_timeout 1.5) 를 src · 설치본에. 로버 안 움직임. 해시는 git blob(PC HEAD 와 대조) | 10-27 §21.3 |
| [`chk_cam_fov.py`](../../debug_log/2026-10-27/jobs/chk_cam_fov.py) | chk_cam_fov — §21 복귀 때 카메라(nvblox)가 상자만 못 봤나, 아무것도 못 봤나 (2026-10-27, PC). | 10-27 §21.1 |
| [`chk_day_start_1027.sh`](../../debug_log/2026-10-27/jobs/chk_day_start_1027.sh) |  | — |
| [`chk_gcm_fit.py`](../../debug_log/2026-10-27/jobs/chk_gcm_fit.py) | chk_gcm_fit — §15 틀어진 전역 프레임의 '새로 생긴 치명 칸' 을 만들 수 있는 slice→map 변환 찾기 (2026-10-27, PC). | 10-27 §15 · 10-27 §17 |
| [`chk_gcm_msgs.py`](../../debug_log/2026-10-27/jobs/chk_gcm_msgs.py) | chk_gcm_msgs — 전역 코스트맵 메시지를 하나씩: 연결(발행자) 수 · 수신 시각 · header stamp · 원점 · 크기 · 직전 메시지와 다른 칸 수 · | 10-27 §15 |
| [`chk_gcm_odd.py`](../../debug_log/2026-10-27/jobs/chk_gcm_odd.py) | chk_gcm_odd — §15 앞뒤와 크게 다른 전역 코스트맵 프레임이 무엇과 겹치나 (2026-10-27, PC). | — |
| [`chk_gcm_rot.py`](../../debug_log/2026-10-27/jobs/chk_gcm_rot.py) | chk_gcm_rot — §15 틀어진 코스트맵 프레임이 정상 프레임을 얼마나 돌리고 옮긴 것인가 (2026-10-27, PC). | 10-27 §15 |
| [`chk_gcm_static.py`](../../debug_log/2026-10-27/jobs/chk_gcm_static.py) | chk_gcm_static — §15 틀어진 전역 프레임에서 새로 생긴 치명 칸이 SLAM 정적 지도(/map) 점유 칸인가 (2026-10-27, PC). | 10-27 §15 |
| [`chk_mapodom_window.py`](../../debug_log/2026-10-27/jobs/chk_mapodom_window.py) | chk_mapodom_window — §21 컨트롤러 TF 중단 순간 앞뒤의 map→odom(/tf) 수신 시각 · stamp (2026-10-27, PC). 인자: bag폴더 epoch초…(중단 로그 시각) | 10-27 §21.2 |
| [`chk_nvlayer_so.sh`](../../debug_log/2026-10-27/jobs/chk_nvlayer_so.sh) | 읽기 전용: nvblox_nav2 설치 라이브러리 위치 · 갱신 시각 · 새 문자열(10-27 §17) | 10-27 §17 |
| [`chk_nvlayer_tffix_1027.py`](../../debug_log/2026-10-27/jobs/chk_nvlayer_tffix_1027.py) | chk_nvlayer_tffix_1027 — §17 수정 층 정지 확인 (2026-10-27, Jetson, 로버 안 움직임). | 10-27 §17 |
| [`chk_replan_maps.py`](../../debug_log/2026-10-27/jobs/chk_replan_maps.py) | chk_replan_maps — §28 f2tt1 15:58:11.40 북행 재계획: 실주행 Smac 은 성공, 오프라인 재질의는 실패 — 지도 판마다 무엇이 다른가 (2026-10-27, PC). | 10-27 §28 |
| [`chk_replay_prereq_1027.sh`](../../debug_log/2026-10-27/jobs/chk_replay_prereq_1027.sh) | §26 재생 준비 확인(읽기만) | — |
| [`chk_slam_idle_1027.sh`](../../debug_log/2026-10-27/jobs/chk_slam_idle_1027.sh) | §24 정지 상태 SLAM stamp 지연 20 s 관찰(새 게이트 SEC=20) + slam 로그 최근 줄. 로버 안 움직임 | 10-27 §24 |
| [`chk_slice_health.py`](../../debug_log/2026-10-27/jobs/chk_slice_health.py) | chk_slice_health — §19 nvblox 슬라이스가 계속 갱신됐나 (2026-10-27, PC). 2 s 마다: 슬라이스 수 · stamp 지연 · 원점 · 크기 · | 10-27 §19 |
| [`chk_slice_tf.py`](../../debug_log/2026-10-27/jobs/chk_slice_tf.py) | chk_slice_tf — §15 틀어진 전역 프레임 앞뒤로 nvblox 슬라이스 원본과 TF 를 메시지마다 (2026-10-27, PC). | 10-27 §15 |
| [`chk_tf_lag.py`](../../debug_log/2026-10-27/jobs/chk_tf_lag.py) | chk_tf_lag — §16 nvblox 전역 층 TF 실패가 부하 탓인가 (2026-10-27, PC). | 10-27 §16 |
| [`cmp_gate_1027.sh`](../../debug_log/2026-10-27/jobs/cmp_gate_1027.sh) | §24 옛 게이트(B · C · G2 따로) vs 새 게이트(chk_drive_gate 한 노드) — 같은 정지 상태에서 값 · 소요 시간. 로버 안 움직임 | 10-27 §24 |
| [`fig_block_cell.py`](../../debug_log/2026-10-27/jobs/fig_block_cell.py) | fig_block_cell — §14 막힘 판정 칸 (1.13, 0.14) 원자료 대조 그림 (2026-10-27, PC). | 10-27 §14 |
| [`fig_f2st1_summary.py`](../../debug_log/2026-10-27/jobs/fig_f2st1_summary.py) | fig_f2st1_summary — §11 f2st1 결과를 f2sa3(10-26, tol 0.25) · f2rp4(10-23, B0 NavFn)와 한 장으로 (2026-10-27 §12, PC). | 10-27 §12 |
| [`fig_f2tt1_summary.py`](../../debug_log/2026-10-27/jobs/fig_f2tt1_summary.py) | fig_f2tt1_summary — §27 f2tt1(transform_timeout 1.5) 결과를 f2st1 · f2tf1 과 한 장으로 (2026-10-27, PC). | 10-27 §27 |
| [`fig_gcm_diff.py`](../../debug_log/2026-10-27/jobs/fig_gcm_diff.py) | fig_gcm_diff — §15 틀어진 전역 프레임에서 새로 생긴 · 사라진 치명 칸과, 그 사이 라이다 스캔(map 으로 옮김)을 겹쳐 그림 (2026-10-27, PC). | 10-27 §15 |
| [`fig_gcm_frames.py`](../../debug_log/2026-10-27/jobs/fig_gcm_frames.py) | fig_gcm_frames — §15 전역 코스트맵 메시지 연속 몇 장을 같은 창으로 나란히(밝은 색표 = fig_rviz_video light) + 같은 시각 로컬 코스트맵 (2026-10-27, PC). | 10-27 §15 |
| [`fig_smac_expansion_tol.py`](../../debug_log/2026-10-27/jobs/fig_smac_expansion_tol.py) | fig_smac_expansion_tol — (v2 에서 갈라짐, 2026-10-27 §7) 같은 순간 16:11:56.85 남행을 허용 · cp 만 바꾼 세 판으로: 기준 tol 0.25 · cp 3.0 실패 / tol 0.35 · cp 3.0 성공 | 10-27 §7 |
| [`fig_smac_expansion_tt1.py`](../../debug_log/2026-10-27/jobs/fig_smac_expansion_tt1.py) | fig_smac_expansion_tt1 — f2tt1 통로 세 순간의 Smac 탐색이 자라는 영상(fig_smac_expansion_v2 의 3 칸 구성, 장면 목록만 바꿈) (2026-10-27 §27, PC). | 10-27 §27 · 10-27 §28 |
| [`fig_smac_expansion_v2.py`](../../debug_log/2026-10-27/jobs/fig_smac_expansion_v2.py) | fig_smac_expansion_v2 — Smac 탐색이 자라는 영상, 같은 일끼리 비교하도록 다시 짬 (2026-10-27 §3, PC, 로버 안 움직임). | 10-27 §3 |
| [`fig_tolcp_paths.py`](../../debug_log/2026-10-27/jobs/fig_tolcp_paths.py) | fig_tolcp_paths — §5 허용치 · cost_penalty 재질의에서 새로 성공한 경로 모양 (2026-10-27, PC). 인자: tolcp폴더 장면.npz 그림.png | 10-27 §5.1 |
| [`fill_report_1027.py`](../../debug_log/2026-10-27/jobs/fill_report_1027.py) | 10-27 정리 페이지: 머리(10-26 틀, 제목만) + 본문 + 그림(data URI, figures/report/*.jpg) → figures/day_summary_1027.html (로컬 사본 = 게시 원본) | 10-27 §31 |
| [`get_logs_f2st1.sh`](../../debug_log/2026-10-27/jobs/get_logs_f2st1.sh) | (PC·WSL) 10-27 f2st1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음(값 출력 안 함) | 10-27 §11 |
| [`get_logs_f2tf1.sh`](../../debug_log/2026-10-27/jobs/get_logs_f2tf1.sh) | (PC·WSL) 10-27 f2tf1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음(값 출력 안 함) | 10-27 §19 |
| [`get_logs_f2tt1.sh`](../../debug_log/2026-10-27/jobs/get_logs_f2tt1.sh) | (PC·WSL) 10-27 f2tt1 nav2 · slam · sensors 로그 회수(prep 이 덮기 전) — 비밀번호는 run_jn.sh 에서 읽음(값 출력 안 함) | 10-27 §25 |
| [`job551_f0drive.sh`](../../debug_log/2026-10-27/jobs/job551_f0drive.sh) | F0 주행 래퍼(Jetson, 2026-09-23): 일반 게이트(A 프로세스·B 보드·J nvblox·C SLAM·G2 출발 자세) → bag·tegrastats·top·RSS → job550 → 메타(job453). | 09-23 16 · 10-07 §2.2 · 10-12 §3.4 · … +8 |
| [`prep_nvlayer_tffix_1027.sh`](../../debug_log/2026-10-27/jobs/prep_nvlayer_tffix_1027.sh) | §17 결함 수정 (2026-10-27 §15~16): nvblox_nav2 층 slice 콜백 — lookupTransform 예외 때 경고만 찍고 계속 진행해 | 10-27 §17 |
| [`prep_slam_dbg_1027.sh`](../../debug_log/2026-10-27/jobs/prep_slam_dbg_1027.sh) | §29 SLAM 포크 단계별 시간 계측 판(기록만, 동작 불변) — 운용 ~/slam_ws 는 건드리지 않고 사본 ~/slam_dbg_ws 에 넣어 빌드. 로버 안 움직임. | 10-27 §29 |
| [`prep_smac_1027.sh`](../../debug_log/2026-10-27/jobs/prep_smac_1027.sh) | 10-27 §10 f2st1 prep(10-26 prep_smac_1026.sh + tolerance 확인) — 운용 기본(prep_patrol: vslam on · 프로젝터 끔 · SHM) + 재계획 0.01 + planner:=smac(Smac H | 10-27 §10 · 10-27 §24 |
| [`prep_smac_1027b.sh`](../../debug_log/2026-10-27/jobs/prep_smac_1027b.sh) | 10-27 §24 prep — prep_smac_1027.sh 에서 `ros2 param get` 약 11 번을 뺀 판(같은 값은 chk_prep.py 가 한 노드로 조회해 출력). 구성은 그대로: | 10-27 §24 |
| [`report_1027_body.html`](../../debug_log/2026-10-27/jobs/report_1027_body.html) |  | 10-27 §31 |
| [`report_1027_head.html`](../../debug_log/2026-10-27/jobs/report_1027_head.html) |  | 10-27 §31 |
| [`run_f0.sh`](../../debug_log/2026-10-27/jobs/run_f0.sh) | F0 PC 러너: Jetson 에 파일 전송(재시도 3) → job551 을 setsid nohup 으로 기동 → 로그 폴링(끊겨도 주행은 계속) → 끝나면 산출물 회수 | 09-23 16 · 09-23 §19 · 10-01 §7.2 · … +11 |
| [`run_prep_full_1027.sh`](../../debug_log/2026-10-27/jobs/run_prep_full_1027.sh) | §24 prep 본체를 필터 없이(원인 확인). 로버 안 움직임 | 10-27 §24 |
| [`run_prep_tt15_1027.sh`](../../debug_log/2026-10-27/jobs/run_prep_tt15_1027.sh) | §21 transform_timeout 1.5 반영 prep(f2tf1 과 같은 구성) + SLAM 파라미터 확인. 로버 안 움직임 | 10-27 §21.3 |
| [`run_slamrep_batch_1027.sh`](../../debug_log/2026-10-27/jobs/run_slamrep_batch_1027.sh) | §26 SLAM 재생 A/B 묶음(Jetson, 도메인 42, 로버 안 움직임): f2tt1 첫 210 s, 변형마다 같은 입력. 본 스택 SLAM 생존을 앞뒤로 확인. | 10-27 §26.3 |
| [`run_swap_1027.sh`](../../debug_log/2026-10-27/jobs/run_swap_1027.sh) | run_swap_1027 — (PC) §1 ③ 출발 ↔ 지도 바꿔 끼우기: 진단 빌드(~/smac_dbg_ws, 설치판과 같은 동작 · 탐색 기록)로 장면 16 개 질의. 로버 안 움직임(도메인 42). | 10-27 §2 |
| [`run_tffix_chk_1027.sh`](../../debug_log/2026-10-27/jobs/run_tffix_chk_1027.sh) | §17: 수정 층으로 prep 재기동(f2st1 과 같은 구성) → 정지 120 s 확인. 로버 안 움직임 | 10-27 §17 |
| [`run_tol_box_1027.sh`](../../debug_log/2026-10-27/jobs/run_tol_box_1027.sh) | run_tol_box_1027 — (PC) §8 허용 0.25 대 0.35 를 10-23 상자 · 통로 6 장면에서: 변형마다 오프라인 planner_server(설치판, 도메인 42) 따로. 로버 안 움직임. | 10-27 §8.1 |
| [`run_tolcp_1027.sh`](../../debug_log/2026-10-27/jobs/run_tolcp_1027.sh) | run_tolcp_1027 — (PC) §5 허용치 · cost_penalty 재질의: 변형마다 오프라인 planner_server(설치판 .so, 도메인 42)를 따로 띄워 f2sa3 통로 6 순간 질의. 로버 안 움직임. | 10-27 §5.1 |
| [`run_tolcp_exp_1027.sh`](../../debug_log/2026-10-27/jobs/run_tolcp_exp_1027.sh) | run_tolcp_exp_1027 — (PC) §7 16:11:56.85 남행 한 순간을 진단 빌드(~/smac_dbg_ws, 탐색 기록)로 V1(tol 0.35 · cp 3.0) · V3(tol 0.25 · cp 1.5) 재질의. 변형마다 프로세스  | 10-27 §7 |
| [`run_top_f2tf1.sh`](../../debug_log/2026-10-27/jobs/run_top_f2tf1.sh) | §18 f2tf1 동안 프로세스별 CPU 1 s 간격 기록(약 11 분, DDS 참여자 아님). 끝나면 /tmp/top_f2tf1.txt | — |
| [`run_tt1_exp_1027.sh`](../../debug_log/2026-10-27/jobs/run_tt1_exp_1027.sh) | run_tt1_exp_1027 — (PC) §27 f2tt1 통로 세 순간(남행 15:57:41 · 북행 15:58:05.80 · 북행 재계획 15:58:11.40)을 진단 빌드(~/smac_dbg_ws, 탐색 기록)로 재질의. | 10-27 §27 |
| [`scenes_swap_1027.json`](../../debug_log/2026-10-27/jobs/scenes_swap_1027.json) |  | 10-27 §2 |
| [`scenes_tolcp_exp_1027.json`](../../debug_log/2026-10-27/jobs/scenes_tolcp_exp_1027.json) |  | 10-27 §7 |
| [`scenes_tt1_exp_1027.json`](../../debug_log/2026-10-27/jobs/scenes_tt1_exp_1027.json) |  | 10-27 §27 |
| [`up_cmp_gate_1027.sh`](../../debug_log/2026-10-27/jobs/up_cmp_gate_1027.sh) | (PC·WSL) §24 게이트 비교 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-27 §24 |
| [`up_prep_1027b.sh`](../../debug_log/2026-10-27/jobs/up_prep_1027b.sh) | (PC·WSL) §24 chk_prep(파라미터 조회 확장) · prep_smac_1027b 전송 후 prep — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임 | — |
| [`up_prep_params_1027.sh`](../../debug_log/2026-10-27/jobs/up_prep_params_1027.sh) | 10-27 §9 재부팅 뒤 prep 재전송(Docs/tools: prep_fast · prep_patrol · chk_prep) + 저장소 nav2_params.yaml(tolerance 0.35) 을 Jetson src · 설치본에. 로버 안 움직임 | 10-27 §9 |
| [`up_slam_replay_1027.sh`](../../debug_log/2026-10-27/jobs/up_slam_replay_1027.sh) | (PC·WSL) §26 SLAM 재생 도구 전송 후 실행 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 인자: 변형 bag 오프셋 길이 ["SLAM_EXTRA"] | — |
| [`up_slam_tt15_1027.sh`](../../debug_log/2026-10-27/jobs/up_slam_tt15_1027.sh) | (PC·WSL) §21 slam.launch.py 전송 · 적용 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-27 §21.3 |
| [`up_slamrep_batch_1027.sh`](../../debug_log/2026-10-27/jobs/up_slamrep_batch_1027.sh) | (PC·WSL) §26 재생 A/B 묶음 전송 · 실행 · 결과 회수 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-27 §26.3 |
| [`up_slamrep_dbg_1027.sh`](../../debug_log/2026-10-27/jobs/up_slamrep_dbg_1027.sh) | (PC·WSL) §29 계측판 SLAM 재생(f2tt1 첫 210 s) — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임, 도메인 42 | 10-27 §29.1 |
| [`up_slamrep_link_1027.sh`](../../debug_log/2026-10-27/jobs/up_slamrep_link_1027.sh) | (PC·WSL) §29.2 link_scan_maximum_distance A/B(계측판) 한 변형 — 인자: 변형이름(L10\|L075). 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-27 §29.2 |
| [`up_tffix_chk_1027.sh`](../../debug_log/2026-10-27/jobs/up_tffix_chk_1027.sh) | (PC·WSL) §17 확인 스크립트 전송 후 실행 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-27 §17 |

## 2026-10-28 (30)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_cell_src.py`](../../debug_log/2026-10-28/jobs/anal_cell_src.py) | anal_cell_src — 한 칸(x, y)의 전역 코스트맵 값을 판마다, 그리고 그때 출처 후보(nvblox 슬라이스 거리 · 직전 1 s 라이다 점 5 cm 안 개수)를 본다 (2026-10-28 §9, PC). | 10-28 §9 |
| [`anal_corridor_cell.py`](../../debug_log/2026-10-28/jobs/anal_corridor_cell.py) | anal_corridor_cell — §5 통로 남쪽 좁은 곳에 북행 출발 직후 잠깐 생기는 내접 칸(막힘 판정)의 출처 (2026-10-28, PC, 로버 안 움직임). | 10-28 §5 |
| [`anal_gcm_vs_static.py`](../../debug_log/2026-10-28/jobs/anal_gcm_vs_static.py) | anal_gcm_vs_static — 전역 코스트맵 덤프의 치명(100) 칸을 정적 /map 점유(≥65)와 비교해 문자 격자로(10-28 §16, PC). | 10-28 §16.1 |
| [`anal_leg_compare.py`](../../debug_log/2026-10-28/jobs/anal_leg_compare.py) | anal_leg_compare — 같은 구간(통로 북쪽 → 위 복도/C)을 place_server 주행(bag)과 no5 러너 주행(job550 csv)에서 비교 (2026-10-28 §12, PC). | 10-28 §12 · 10-28 판정 기준(주행 전 선언) |
| [`anal_leg_env.py`](../../debug_log/2026-10-28/jobs/anal_leg_env.py) | anal_leg_env — 한 구간 동안 0.5 s 마다: 지령 v · 직전 1 s /cmd_vel 수(컨트롤러 주기) · 차체(0.52 × 0.35 직사각형)와 | 10-28 §12 · 10-28 판정 기준(주행 전 선언) |
| [`anal_place_clear.py`](../../debug_log/2026-10-28/jobs/anal_place_clear.py) | anal_place_clear — place_server 목표 여유 검사가 왜 0 이 나왔나 (2026-10-28 §8, PC, 로버 안 움직임). | 10-28 §8.2 · 10-28 §9 · 10-28 §12 · … +3 |
| [`anal_plan_x.py`](../../debug_log/2026-10-28/jobs/anal_plan_x.py) | anal_plan_x — 시간 창 안의 /plan 마다 y 값 몇 곳에서 경로의 x(통로 안 가로 위치)와 점 수 · 길이 (2026-10-28 §12, PC). | 10-28 §12 · 10-28 판정 기준(주행 전 선언) |
| [`chk_clear_global_1028.sh`](../../debug_log/2026-10-28/jobs/chk_clear_global_1028.sh) | §13 전역 코스트맵 비우기 → 5 s · 20 s 뒤 로버 둘레 다시 보기(치명 띠가 nvblox 기억에서 되살아나는지). 로버 안 움직임 | 10-28 §13.1 |
| [`chk_costmap_dump.py`](../../debug_log/2026-10-28/jobs/chk_costmap_dump.py) | chk_costmap_dump — 전역 코스트맵 · 정적 /map 한 판과 로버 자세를 /tmp/gcm_dump.npz 로 (10-28 §16, 로버 안 움직임) | 10-28 §16.1 |
| [`chk_costmap_robot.py`](../../debug_log/2026-10-28/jobs/chk_costmap_robot.py) | chk_costmap_robot — 전역 코스트맵 한 판에서 로버 자리 둘레 ±1.2 m 를 문자 격자로(10-28 §13, 로버 안 움직임). | 10-28 §13.1 |
| [`chk_costmap_robot_1028.sh`](../../debug_log/2026-10-28/jobs/chk_costmap_robot_1028.sh) |  | — |
| [`chk_day_start_1028.sh`](../../debug_log/2026-10-28/jobs/chk_day_start_1028.sh) | 10-28 하루 시작 점검(읽기만): 가동 시간 · Wi-Fi · /tmp prep 스크립트 · 스택 프로세스 · SLAM transform_timeout · 수정 nvblox 층 · 디스크 | 10-28 §0 |
| [`chk_nav_alive_1028.sh`](../../debug_log/2026-10-28/jobs/chk_nav_alive_1028.sh) | §13 dry_run 에서 경로 조회가 전부 '경로 없음(상태 6)' — 계획기 상태 확인(로버 안 움직임) | 10-28 §13.1 |
| [`chk_place_dry_1028.sh`](../../debug_log/2026-10-28/jobs/chk_place_dry_1028.sh) | §7 F2.5 S1 정지 시험(dry_run — 목표를 Nav2 에 보내지 않음, 로버 안 움직임): src 에 올린 place_server 를 띄우고 명령 창구로 검사 | 10-28 §7 · 10-28 §8.1 |
| [`chk_place_dry_1028c.sh`](../../debug_log/2026-10-28/jobs/chk_place_dry_1028c.sh) | §8 f2pl1 통로 북쪽 거절 재현 · §9 장소 6 곳 전부(dry_run(dry_run — 목표를 Nav2 에 보내지 않음, 로버 안 움직임): src 에 올린 place_server 를 띄우고 명령 창구로 검사 | 10-28 §8.2 · 10-28 §13.1 |
| [`chk_place_web_1028.sh`](../../debug_log/2026-10-28/jobs/chk_place_web_1028.sh) | §16 place_web 확인(dry_run place_server 와 함께 — 목표를 Nav2 에 보내지 않음, 로버 안 움직임). 키는 출력하지 않는다 | 10-28 §16 |
| [`chk_scan_align.py`](../../debug_log/2026-10-28/jobs/chk_scan_align.py) | chk_scan_align — 지금 라이다 한 판을 정적 /map 에 맞춰 보고 yaw 를 얼마나 돌려야 가장 잘 맞는지(10-28 §16, 로버 안 움직임). | 10-28 §16.1 · 10-29 §2 |
| [`chk_scan_band.py`](../../debug_log/2026-10-28/jobs/chk_scan_band.py) | chk_scan_band — 라이다 한 판을 map 으로 옮겨 로버 둘레 ±1.2 m 에 점을 찍는다(10-28 §13, 로버 안 움직임). | 10-28 §13.1 |
| [`fig_gcm_reach.py`](../../debug_log/2026-10-28/jobs/fig_gcm_reach.py) | fig_gcm_reach — 전역 코스트맵 덤프(chk_costmap_dump.py)에서 로버 칸부터 지나갈 수 있는 칸(값 ≤ 98, 미지 포함)을 넓이 우선으로 칠해 | 10-28 §16.1 |
| [`fill_report_1028.py`](../../debug_log/2026-10-28/jobs/fill_report_1028.py) | 10-28 정리 페이지: 머리(10-27 틀, 제목만) + 본문 + 그림(data URI, outputs/*.png) → figures/day_summary_1028.html (로컬 사본 = 게시 원본) | 10-28 §17 |
| [`get_f2tt2.sh`](../../debug_log/2026-10-28/jobs/get_f2tt2.sh) | (PC·WSL) 10-28 f2tt2 산출물 · 로그 회수(PC 쪽 러너 폴링이 끊겨 자동 회수 안 됨) — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-28 §4 |
| [`prep_smac_1028.sh`](../../debug_log/2026-10-28/jobs/prep_smac_1028.sh) | 10-28 prep — f2tt1 과 같은 구성(prep_patrol: vslam · 프로젝터 끔 · SHM + 재계획 0.01 + planner:=smac). 원문은 /tmp/prep_full_<n>.txt 로 남기고 요약만 출력(10-27 §24) | 10-28 §2 · 10-28 §14 |
| [`report_1028_body.html`](../../debug_log/2026-10-28/jobs/report_1028_body.html) |  | 10-28 §17 |
| [`report_1028_head.html`](../../debug_log/2026-10-28/jobs/report_1028_head.html) |  | 10-28 §17 |
| [`run_place_s1_1028.sh`](../../debug_log/2026-10-28/jobs/run_place_s1_1028.sh) | §7 F2.5 S1 실주행: 장소 이름 명령으로 no5 와 같은 순서 + W3 구간 정지 시험 + 돌아와. Jetson 에서 setsid nohup 으로 독립 실행(PC 끊겨도 계속, 10-28 §3.1). | 10-28 §7.1 · 10-28 §8.3 · 10-28 §13 · … +2 |
| [`up_place_dry_1028.sh`](../../debug_log/2026-10-28/jobs/up_place_dry_1028.sh) | (PC·WSL) §7 F2.5 파일을 Jetson src 에 올리고 dry_run 정지 시험 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임 | 10-28 §7 |
| [`up_place_dry_1028c.sh`](../../debug_log/2026-10-28/jobs/up_place_dry_1028c.sh) | (PC·WSL) §8 수정한 place_server(거절에 방향 기록)를 Jetson src 에 올리고 dry_run 정지 시험 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임 | 10-28 §8.2 |
| [`up_place_s1_1028.sh`](../../debug_log/2026-10-28/jobs/up_place_s1_1028.sh) | (PC·WSL) §7 S1 파일 전송 · Jetson 에서 독립 실행 시작 · 끝날 때까지 로그 따라보기 · 회수. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-28 §7.1 |
| [`up_place_web_1028.sh`](../../debug_log/2026-10-28/jobs/up_place_web_1028.sh) | (PC·WSL) §16 place_web 올리기 + Jetson 확인 실행 + PC(ALOPS)에서 8080 접속 확인. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) · 키도 출력 안 함. 로버 안 움직임 | 10-28 §16 |
| [`up_prep_1028.sh`](../../debug_log/2026-10-28/jobs/up_prep_1028.sh) | (PC·WSL) 10-28 재부팅 뒤 prep 재전송 + prep. 인자: 회차번호. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임 | 10-28 §2 · 10-28 §14 · 10-29 §2 |

## 2026-10-29 (9)

| 파일 | 설명 | 언급 |
|---|---|---|
| [`anal_drift_bag.py`](../../debug_log/2026-10-29/jobs/anal_drift_bag.py) | anal_drift_bag — 정지 기록 bag 에서 방향 드리프트 원천 가르기 (10-29 §1 판정 ①~④, PC). | 10-29 §3 · 10-29 §4 |
| [`anal_scan_align_bag.py`](../../debug_log/2026-10-29/jobs/anal_scan_align_bag.py) | anal_scan_align_bag — bag 의 라이다 판마다 정적 /map 과 맞춤 점수(10-29 §2, PC). | 10-29 §2 |
| [`anal_scan_align_sum.py`](../../debug_log/2026-10-29/jobs/anal_scan_align_sum.py) | anal_scan_align_sum — outputs/scan_align/*.txt(anal_scan_align_bag 출력) 분포 요약 (10-29 §2, PC) | 10-29 §2 |
| [`chk_day_start_1029.sh`](../../debug_log/2026-10-29/jobs/chk_day_start_1029.sh) | 10-29 하루 시작 점검(읽기만): 가동 시간 · Wi-Fi · 스택 프로세스 · 컨디셔너 ZUPT 로그 | 10-29 §0 |
| [`chk_drift_rec_1029.sh`](../../debug_log/2026-10-29/jobs/chk_drift_rec_1029.sh) | 10-29 정지 방향 드리프트 기록(Jetson, 로버 안 움직임 · 명령 없음). 인자: 이름 길이s(기본 1800) | 10-29 §1 · 10-29 §2 · 10-29 §4 |
| [`chk_yaw_drift.py`](../../debug_log/2026-10-29/jobs/chk_yaw_drift.py) | chk_yaw_drift — 정지 중 방향 드리프트 원천 측정 (2026-10-29, Jetson, 로버 안 움직임). | 10-29 §2 |
| [`run_d2_1029.sh`](../../debug_log/2026-10-29/jobs/run_d2_1029.sh) | (PC·WSL) §4 d2: 주행(10-28 S1 러너 w3, 새 place_server 배포 포함) → 끝나자마자 d2s 정지 기록 40 분 시작. 로버는 주행 구간만 움직임 | — |
| [`up_drift_rec_1029.sh`](../../debug_log/2026-10-29/jobs/up_drift_rec_1029.sh) | (PC·WSL) 10-29 정지 기록 스크립트 전송 + 시작. 인자: 이름 길이s. 비밀번호는 run_jn.sh 에서 읽음(출력 안 함) | 10-29 §2 |
| [`up_fetch_drift.sh`](../../debug_log/2026-10-29/jobs/up_fetch_drift.sh) | (PC·WSL) 정지 기록 회수: Jetson /tmp/bag_<이름> 를 묶어 scratchpad/drift_<이름>/ 로 + 로그. 인자: 이름 | 10-29 §3 |
