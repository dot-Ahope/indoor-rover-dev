# Foxglove 화면의 '4초 스냅' — 시각화 브리지 과부하, 그리고 CPU 소비자 오인

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회**(브리지 재시작 + 토픽 화이트리스트로 증상 해소, 사용자 확인) · 기전('브리지가 /tf 를 늦게 · 뭉쳐 전달')은 **추정**으로 남음 · 2 기(09-09 ~ 09-10): 브리지 상시 88~95 % → `viz:=lean` 3 단계 · 스레드 · 큐 · 기능 축소, 그러나 **클라이언트가 붙으면 lean 이어도 69.6 %** → 운용 규칙 '측정 주행 중 Foxglove 끄기' · 이후 09-30 재발 | 09-01(08-31 폴더의 연속 세션) ~ 09-10(이후 09-30) | [08-31 SUMMARY '(2026-09-01 연속 세션)' → '다음 (★최우선 = 새 관찰)'](../debug_log/2026-08-31/SUMMARY.md) | `ros2_ws/src/rover_bringup/launch/foxglove.launch.py`(topic_whitelist 신설) · `scripts/scan_deskew.py`(벡터화, 부수) | [회전 중 스캔 끌림](scan-drag-deskew.md) · [라이다 yaw](lidar-yaw-alignment.md)(fixed frame 혼선) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(stamp 의 뜻) · [CPU 부족 정지](cpu-load-stalls.md)(09-09 ~ 09-10, 클라이언트 연결이 EKF 를 굶김) · 회전 미끄러짐 · SLAM 포크(09-28, 카드 예정) |

**한 줄**: Foxglove 에서 로버 모델은 멈춰 있고 스캔만 실시간으로 움직이다가 '약 4 초마다' 로버가 제자리로 점프하는 것을 사용자가 봤다. TF 주기 · stamp · 클럭 · SLAM 을 차례로 재서 ROS 안쪽은 건강함을 확인했고, 프로세스별 CPU 에서 foxglove_bridge 가 66 % 로 가장 큰 소비자였으며 브리지를 재시작하자 사용자가 '매끄러워졌다' 고 확인했다 → 시각화 아티팩트로 결론, 카메라 토픽을 빼는 화이트리스트로 브리지 8.8 %. 같은 조사에서 'deskew 가 CPU 35~45 %' 라고 적었던 것은 오인이었고 실제 최대 소비자는 `sensor_conditioner`(44 %)였다. conditioner 는 '없앨 임시 코드' 라는 이유로 최적화하지 않기로 했다(이후 09-28 C++ 이식).

## 1. 증상
- 09-01(사용자): 회전 · 이동 중 로봇 description 은 정지, scan 만 실시간 → **~4 초 뒤** description 이 실제 방향 · 위치로 점프하며 scan 이 map 에 정합. 이동량 · 방향(전진/회전) · 크기와 무관하게 '항상 ~4 초'. [08-31 SUMMARY '다음 (★최우선 = 새 관찰)'](../debug_log/2026-08-31/SUMMARY.md)
- '4 초' 는 사용자 육안 값이다. 주기를 잰 출력은 없다.
- 사용자 가설: "odom 이 절대위치(루프클로저/slam)로만 갱신되고 상대위치(dead-reckoning)로는 안 되는 것 아닌지". → 계산(토픽) 수준은 상대운동 정상(사각형 루프에서 `/odometry/filtered` 연속 이동)이라고 부분 정정, 표시 수준에서는 맞을 수 있다고 남김(같은 절).

## 2. 흐름 (시간순)
모든 job 은 [2026-08-31/jobs/](../debug_log/2026-08-31/jobs/), 출력은 [2026-08-31/outputs/](../debug_log/2026-08-31/outputs/). 'SUMMARY 단계 n' = [08-31 '★ Foxglove 4초 스냅 — 원인 규명·해결 (2026-09-01 세션2, job16*)'](../debug_log/2026-08-31/SUMMARY.md) 의 진단 경로 번호.

| 곳 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| '다음' 절 | 조사 순서 계획: ① slam 정합 주기 · transform_publish_period ② odom→base TF 발행률 ③ stamp · 클럭 ④ Foxglove fixed frame · TF 버퍼. '결정적 시험' = fixed frame map → odom | — | 고정 4 초 = 누적 드리프트가 아니라 **TF/표시 갱신 주기 문제** 강력 의심 | SUMMARY 문장 |
| 세션 2 시작 | `job16a` 전체 재기동(보드 RESET 뒤) | filtered 29.948 Hz, map→odom (0,0,0), VX_SCALE 1.022 | Foxglove fixed frame = odom 으로 관찰 준비 | job16a_init.txt |
| | `job16b` 센서 · TF 주기 + 조이스틱 기동 | `/imu/data` 199.989 · 카메라 imu **140.243** · scan 9.976 · `/tf` **30.998 Hz**. tf2_monitor 줄은 빈 출력 | (tf2_monitor 는 grep 이 못 잡아 16c 로 재시도) | job16b_tfdiag.txt |
| SUMMARY 단계 1 | 사용자 Foxglove fixed frame 변경 | 바꿔도 로봇 정지 + scan 실시간 | **표시층 문제**로 좁힘 | 사용자 관찰(파일 없음) |
| | `job16c` tf2_monitor odom→base_link · map→odom 8 s | odom→base net delay 평균 3.3 ms · 최대 20.2 ms. '<no authority>' 50.27 Hz, Average Delay 0.80 s · Max 249.7 s | net delay 정상. 50 Hz · 249 s 의 뜻은 해석 안 함(**미확인**) | job16c_tfmon.txt |
| | `job16d` 재측정 + stamp(파이썬 실패) | net delay 평균 6.1 · 최대 35.6 ms; 파이썬 블록 `rclpy.init() has not been called` | 도구 결함 → 16e | job16d_tsverify.txt |
| | `job16e` 토픽별 첫 메시지 stamp vs now | wheel_odom +0.014 s · 카메라 imu +0.012 s · filtered +0.683 · scan_raw +0.674 · scan +0.675 s; **보드 − 카메라 stamp −0.002 s** | 클럭 동기 정상. 0.68 s 는 측정법 결함(§8 job16e) | job16e_stamps.txt |
| SUMMARY 단계 2 | `job16f` use_sim_time · 콜백 안 지연 | use_sim_time 4 노드 False. 지연 평균 wheel_odom 16.8 · 카메라 imu 1.6 · filtered 13.5 · scan_raw 102.7 · scan(deskew) **3.1 ms** | 전부 fresh → **타임스탬프/클럭 기각** | job16f_latency.txt |
| | `job16g` 사용자 회전 20 s 동안 TF 값 변화 주기 | 출력 원문 없음 | (16h 로 대체 — 스크립트가 직접 회전) | job16g_tfcadence.sh |
| SUMMARY 단계 3 | `job16h` 스크립트 제자리 회전 0.6 rad/s · 15 s + TF 로깅 | yaw 총 **202°**, odom→base 값 변화 **448 회 · 간격 평균 33 ms · 최대 66 ms**, map→odom **변화 없음** | odom TF 건강(30 Hz 매끄러움) | job16h_rotlog.txt |
| SUMMARY 단계 4 | map→odom 해석 | 순수 회전 중 고정, 병진 시 변함(job14k) | '순수회전 시 고정 = 정상(보정할 것 없음, heading 자이로 정확)' — **이유 틀림**(이후 09-28: apt slam_toolbox 는 제자리 회전 중 스캔을 버림, §3) | SUMMARY |
| | `job16i` slam 로그 · map→odom stamp · 파라미터 · 부하 | 'queue is full' 드롭 2 줄, 4 s 동안 서로 다른 map→odom stamp **12 개**, min_time 0.1 · distance 0.05 · heading 0.03 · transform_timeout 0.2 · mode mapping, load **6.21** 5.08 3.64(6 코어), slam CPU 칸 빈 값 | 발행은 됨(값만 고정) | job16i_slamdiag.txt |
| SUMMARY 단계 6 | `job16j` joy 종료 + 프로세스별 CPU | load 4.97. **foxglove 65.7 %**(누적 CPU 시간 16:19) · ekf 37.3 · python3(pid 14964) **35.3** · slam 31.4 · realsense 23.5 · rplidar 15.7 · python3(pid 14782) 7.8 · agent 4.9 | 'foxglove 66 % 최대, deskew(py) 35 %' — **pid 14964 는 conditioner 였음(오인, §5.1)** | job16j_cpu.txt |
| SUMMARY 단계 5 | `job16k` foxglove 끄고 회전 12 s | load 4.24 → 회전 뒤 3.73, 회전 157°, map→odom **여전히 고정** | CPU 가 slam 정지의 원인 아님 | job16k_fgtest.txt |
| | `job16l` transform_publish_period · 정지 stamp 수 · foxglove 재시작(`ros2 run`, 화이트리스트 없음) | period 0.05, 4 s 동안 서로 다른 stamp **36 개(~9 Hz)**, 재시작 뒤 load **1.90** | '20 Hz 설정인데 ~9 Hz(CPU 눌림)' — **지표 해석 틀림**(§5.4) | job16l_fgrestart.txt |
| SUMMARY 단계 7 | `job16m` 조이스틱 재기동 → 사용자 주행 | joy 축 0 · cmd_vel 0, load 2.62 | 사용자 "매끄러워졌다" → **확정**: 브리지 과부하로 /tf 가 클라이언트에 늦게 전달(**기전 추정**) | job16m_joy.txt · 사용자 관찰 |
| '부수 발견' | — | slam 'queue full' 간헐, 스크립트 회전 때 joy teleop 이 `/cmd_vel` 이중 발행 | 주행 스크립트 전 joy 종료 필요 | SUMMARY |
| [CPU 최적화 절](../debug_log/2026-08-31/SUMMARY.md) | `job17a` 카메라 토픽 · enable 파라미터 · CPU | color/depth/gyro/accel 켜짐, infra 꺼짐, unite_imu 1, color 15.005 Hz. CPU python3 **45.5** · realsense 30.7 · rplidar 18.8 · **foxglove 18.8**(재시작 뒤, 화이트리스트 전) · ekf 11.9 · python3 7.9 | 'deskew 45 %' 로 읽음(**오인**) | job17a_camcheck.txt |
| | `job17b` deskew 벡터화 + foxglove 화이트리스트 배포 | 전: deskew(pid 14782) **9.0 %**, load 6.42. 후: `/foxglove_bridge` **2 개**(55.9 · 51.0 %), 화이트리스트 `/scan` 확인, deskew(pid 19811) 0.0 % | 이중 기동 사고 | job17b_optapply.txt |
| | `job17c` foxglove 1 개로 · 회전 중 deskew CPU | foxglove 1, deskew(19811) 회전 중 평균 **0.0 %**(10 샘플). python3 43.6 · rplidar 16.8 · realsense 11.9 · ekf 11.9 · foxglove 11.9 · python3 8.9 | — (0.0 % 는 **측정 대상 오류**, §5.2) | job17c_validate.txt |
| | `job17d` pid 식별 + 가벼운 회전 | deskew pid 19811 · conditioner pid **14964**. deskew 0.0 % × 8. 회전 뒤 python3 42.2 · foxglove 10.8, load 2.61 | 큰 python3 = conditioner | job17d_clean.txt |
| | `job17e` cmdline 으로 정체 확인 | deskew pid 19811 · **19814**(2 개), conditioner 14964. **14964 sensor_conditioner.py 44.1 %**, rplidar 18.6, realsense 11.8, ekf 11.8, slam 8.8, **foxglove 8.8**, **19814 scan_deskew.py 7.8 %** | **'deskew 45 %' 정정 → conditioner 44 %, deskew ~8 %**. foxglove **66 → 8.8 %** | job17e_identify.txt |
| 'conditioner 결정' | 최적화 여부 | — | **안 함**: 펌웨어가 대체할 임시 shim · 카메라 IMU 는 Jetson USB 라 펌웨어가 못 맡음 · 200 → 100 Hz 하향은 VIO(cuVSLAM)에 반대 · Isaac 도입 시 재작업. 트리거 = 특정 시험이 CPU 벽에 닿을 때 | SUMMARY |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| odom→base_link TF 가 안 나가거나 드묾 | `/tf` hz(16b), tf2_monitor(16c · 16d), 회전 중 값 변화 간격(16h) | `/tf` 31 Hz, 회전 중 448 회 · 평균 33 ms · 최대 66 ms | **기각** |
| stamp · 클럭 어긋남(use_sim_time, 보드 micro-ROS 시각, deskew now − 9 ms) | 16e · 16f | use_sim_time False, 보드 − 카메라 −0.002 s, 지연 1.6~17 ms(스캔 원본 103 ms 는 스윕 시작 stamp 탓) | **기각** |
| fixed frame(map)과 SLAM 갱신 주기 탓 | 사용자 fixed frame 변경(단계 1) | 바꿔도 같은 증상 | **기각**(표시층으로 좁힘) |
| SLAM 이 CPU 에 눌려 map→odom 을 못 고침 | 16k foxglove 끄고 회전 | 그래도 회전 중 고정 | **기각** — 단, '고정이 정상' 이라는 이유는 틀림: 이후 09-28 에 apt slam_toolbox 가 제자리 회전 중 스캔을 전부 버린다는 것이 확인됨(`Docs/04_navigation/SLAM_FORK_ROTATION.md` §2, 회전 11 회 중 0 회 포착). 그때 실제 차체는 180° 당 10~27 cm 옆으로 밀리고 있었다 |
| foxglove_bridge 과부하로 클라이언트에 /tf 가 늦게 · 뭉쳐 감 | 16j CPU(66 %), 16l 재시작 → 16m 사용자 주행 | '매끄러워졌다'(사용자) | **지지**(증상 해소는 확인) · **기전은 추정**: 클라이언트 쪽 /tf 도착 시각을 잰 적 없음. 재시작은 부하뿐 아니라 클라이언트 구독 상태 · 큐도 새로 만든다 |
| deskew(Python)가 CPU 35~45 % | 17d · 17e pid → cmdline | 그 python3 는 conditioner(44.1 %), deskew 7.8 % | **기각**(오인 정정) |
| 화이트리스트가 브리지 부하를 줄임 | 17a(재시작 뒤 · 화이트리스트 전) vs 17c · 17d · 17e(뒤) | 18.8 % → 11.9 · 10.8 · 8.8 %(각 1 초 표본 1 개) | **지지(약함)** — '66 → 8.8 %' 에는 재시작 효과(66 → 18.8)가 대부분 섞여 있다. 클라이언트 접속 · 패널 상태는 기록 없음 |

## 4. 조치와 효과
- **foxglove_bridge 재시작**(16l) → 사용자 확인 '매끄러움'. 운영 대책: 재발 시 재시작, Foxglove 레이아웃에서 포인트클라우드 · 이미지 구독 최소화.
- **topic_whitelist**(17b, `foxglove.launch.py`, 09-02 커밋판): `/scan` `/scan_raw` `/map` `/map_metadata` `/tf` `/tf_static` `/robot_description` `/odometry/filtered` `/wheel_odom` `/imu/data` `/imu/data_raw` `/rover/status` `/battery` `/cmd_vel` `/joy` — `/camera/*` 제외. 브리지 CPU 8.8~11.9 %(17c~17e).
- 부수 관찰(해석 **미확인**): 같은 전후로 ekf_node 37.3 → 11.8 %, realsense 23.5 → 11.8 %. realsense 감소는 브리지가 영상(압축 전송 포함)을 구독하지 않게 된 효과일 수 있다(**추정**). EKF 감소의 기전은 모름.
- **deskew 벡터화**: 9.0 → 7.8 %(조건 다른 두 1 초 표본) — 효과 미미, '대폭 절감' 은 측정 근거 없음.
- **conditioner 최적화 안 함**(위 표 마지막 줄의 네 근거). 이후 09-02 Nav2 기동 시 conditioner 47 % · foxglove 27 %, foxglove 를 끄면 load 6.9 → 3.4([09-02 SUMMARY 'B-1' 부수 조치 · 첫 자율주행 '관찰·다음 튜닝 후보' 2](../debug_log/2026-09-02/SUMMARY.md)) → '자율주행 중에는 foxglove 끄기' 운영.
- 이후(09-09 ~ 09-10): 아래 §4b 에서 채움 — 브리지 상시 88~95 % → `viz:=lean`(기본) / `full` / `cam` 3 단계 · `num_threads 2` · `max_qos_depth 1` · `capabilities` 축소(09-09 §8.10), lean 뒤 top 에서 브리지 사라짐(§8.12, 클라이언트 연결 상태 미기록), 09-10 §4 **클라이언트가 붙자 lean 이어도 69.6 %** · 끊자 EKF 위반 86 → 0 → '측정 주행 중 Foxglove 끄기'.
- 이후(09-28 ~, 다음 시기에서 채움): conditioner C++ 이식(CPU 42.2 → 7.1 %, 커밋 9c2984b4), 09-30 §5 매핑 중 lean 연결로 EKF 위반 12 회 / 30 s → `viz:=map` 세트, 09-30 §12 **같은 증상**('스캔만 돌고 로버는 멈췄다 점프', Jetson TF 정상, j712) → 브리지 `max_qos_depth 1` 이 /tf 를 버린다는 다른 기전 추정 → map 세트 10.

## 4b. 2 기(09-09 ~ 09-10) — 경량화, 그리고 '클라이언트가 붙는 것' 이 병목
### 흐름
jobs 는 [2026-09-09/jobs/](../debug_log/2026-09-09/jobs/) · [2026-09-10/jobs/](../debug_log/2026-09-10/jobs/). 이 두 날의 해당 출력 원문은 없다(09-09 `outputs/` 비어 있음, 09-10 은 CSV 2 개뿐) — 수치는 SUMMARY 서술.

| 곳 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 도구 |
|---|---|---|---|---|
| 09-08(참고) | 코스트맵 · 경로 시각화를 위해 화이트리스트에 `/local_costmap/costmap(_updates)` · `/global_costmap/costmap(_updates)` · `/plan` · `/local_plan` 추가(커밋 `fe79f1c4`) | 주석: 로컬 60×60 = 3.6 k 칸 @ 2 Hz, 전역 167×98 = 16 k 칸 @ 1 Hz 로 '가볍다' | 사용자가 회피 실패를 직접 보려고 | `foxglove.launch.py` |
| 09-09 §8.10 | 브리지가 상시 CPU **88~95 %**(≈ 1 코어)로 최대 소비자, 같은 시기 ekf_node `Failed to meet update rate! Took 0.14s` 반복 | 어느 도구의 top 인지 SUMMARY 미표기(job139 · 146 계열로 **추정**) | '비용은 코어 수가 아니라 **메시지 건수 × 직렬화**' | — |
| §8.10 | 설치된 브리지의 선언 파라미터 이름을 바이너리 문자열에서 추출 · 버전 · sensors.launch 의 imu 리매핑 | `num_threads` · `max_qos_depth` · `send_buffer_limit` · `use_compression` · `capabilities` · `topic_whitelist` 전부 존재, **3.2.4** | 파라미터 이름을 추측하지 않고 설치본에서 확인 | `job157_fg.sh` |
| §8.10 | 브리지 기본 capabilities 문자열 · (같은 job 에서 Nav2 · realsense 대안 확인) | `clientPublish` · `parameters` · `parametersSubscribe` · `services` · `connectionGraph` · `assets` | 폴링이 비싼 `connectionGraph` · `parametersSubscribe` · `assets` 를 뺄 수 있음 | `job158_alt.sh` B) |
| §8.10 · 커밋 `585df0ea` | `foxglove.launch.py` 3 단계 화이트리스트 + 부하 억제 파라미터 + `sensors.launch.py` 에 `viz` 인자 전달 → 배포 · 단독 기동 시험 | 파라미터 거부 없음, 포트 8765, **유휴 0.7 %**. lean 합산 **약 60 msg/s** | 효과는 '다음 기동 때 부하 상태에서 측정' | `job159_fgdeploy.sh` |
| 09-09 §8.12 | lean 적용 뒤 CPU 상위 | 이전: `foxglov+` **88.2 %** / ekf_node 41.2 / `async_s+` 38.2 / `bt_navi+` 31.4 → 이후: python3 **39.2** / `rplidar+` 19.6 / `control+` 15.7 / `realsen+` 14.7 / `planner+` 12.7 — **브리지가 상위에서 사라짐** | '경량화 효과 확인' — ⚠ 클라이언트 연결 여부 미기록(§5.6) | 도구 미표기(job176 의 top 상위 5 와 형식이 같음 — **추정**) |
| 09-09 §8.16 | 같은 날 저녁 job175 정지 — EKF 위반 91 회 · load 9.01 | (Foxglove 언급 없음) | CPU 부족 → [CPU 카드](cpu-load-stalls.md) | `job177_env.sh` |
| 09-10 §4 | stuck_monitor 수정 뒤 Nav2 재기동 실패(`planner_server/get_state service client: async_send_request failed`) | load **6.35**, EKF 위반 **86**, slam 폐기 **28**, **`foxglove_bridge` 69.6 %**('부팅 직후엔 상위권에 없던 것') | 설정 오류가 아니라 부하로 서비스 응답 타임아웃 | `job189_wait.sh` · `job190_err.sh` |
| 09-10 §4 | 8765 포트 연결 → 브리지 TERM → 30 s 재측정 | `ESTAB 192.168.0.101:8765 ← 192.168.0.6:65351`(사용자 PC Foxglove Studio). 정지 뒤 EKF 위반 **0** · slam 폐기 **0** · Nav2 전 노드 active | **★ 진짜 병목 = 클라이언트 연결** — `viz:=lean` 으로 토픽을 줄여도 **붙으면** 1 코어 가까이. '관측 도구가 관측 대상을 망가뜨리고 있었다'(§0 1) | `job191_nofg.sh` |
| 09-10 §0 · §6 | 운용 규칙 | — | 측정 주행 중 Foxglove Studio 창을 닫거나 브리지를 내린다. 경로 · 코스트맵은 rosbag 으로 남겨 **사후에** 본다(09-10 §6 job195 기록 주행부터) | `job194_bagdrive.sh`(이 카드 범위 밖) |

### 가설과 판별(2 기)
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 브리지 비용은 토픽 건수 × 직렬화 — 고주파 토픽을 빼면 준다 | lean(약 60 msg/s: `/imu/data` 200 Hz · `/scan_raw` · `/wheel_odom` · `*_updates` 제외) 배포 뒤 top | 유휴 0.7 %(job159, 클라이언트 없음), §8.12 상위에서 사라짐 | **지지(약함)** — 두 측정 모두 클라이언트 연결 상태를 적지 않았다 |
| `*_updates` 토픽이 비용 | 코드 · 설정 | `always_send_full_costmap: true` 라 **애초에 발행되지 않음** | 비용원 아님(목록 정리만) |
| 브리지 CPU 는 '광고하는 토픽 수' 로 정해진다 | 09-10 §4: lean 그대로, 클라이언트 연결 유무만 다름 | 연결 69.6 % · 끊으면 위반 0 | **기각** — 비용은 클라이언트가 **구독한** 토픽 · 패널에서 생긴다(**추정**: 어떤 패널 · 토픽을 열었는지는 기록 없음) |
| 클라이언트 연결이 EKF 를 굶겨 TF · Nav2 를 망친다 | 같은 세션에서 브리지 정지 전후 | 86 → 0 · 28 → 0 · 기동 실패 → active | **지지**(09-10 당일). 09-09 주행 실패와의 인과는 **추정**(그날 연결 기록 없음 — [CPU 카드 §6 모순 2](cpu-load-stalls.md)) |

### 조치와 효과(2 기)
- **`foxglove.launch.py` 09-09 판**(커밋 `585df0ea`, `viz` 인자):
  - `LEAN`(기본, 15 개): `/tf` · `/tf_static` · `/robot_description` · `/map` · `/map_metadata` · `/scan` · `/odometry/filtered` · `/rover/status` · `/battery` · `/rover/stuck` · `/cmd_vel` · `/local_costmap/costmap` · `/global_costmap/costmap` · `/plan` · `/local_plan`.
  - `FULL` = LEAN + `/imu/data`(200 Hz — 'LEAN 에서 뺀 가장 큰 이유') · `/imu/data_raw` · `/imu/mag` · `/wheel_odom` · `/scan_raw` · `/joy`.
  - `CAM` = FULL + color 영상 · camera_info · 깊이 영상 · 점군.
  - 파라미터: `num_threads 2`(기본 0 = 코어 수 6, 다른 노드 몫을 남김) · `max_qos_depth 1`(밀리면 쌓지 말고 버림 — 시각화는 최신만 의미) · `send_buffer_limit 2000000` · `use_compression False`(압축은 CPU 를 더 씀) · `capabilities ['clientPublish','parameters','services']`.
  - 효과: 유휴 0.7 %, §8.12 상위에서 사라짐. 그러나 클라이언트가 붙으면 69.6 %(09-10) — **경량화로는 부족**.
- **운용 규칙**(09-10 §4): 측정 주행 중 Foxglove 를 닫는다(또는 브리지를 내린다). 이후 계획서 S6 에도 '클라이언트 접속 시 다시 오른다 — 측정 주행 중 끄기 검토' 로 반영.
- 한계 · 이후: `max_qos_depth 1` 이 09-30 §12 에서 `/tf` 를 버리는 원인으로 다시 의심됨(map 세트만 10). 09-09 의 '1(버림)' 은 부하 억제용 선택이었고 `/tf` 처럼 여러 발행자가 한 토픽에 섞이는 경우의 영향은 그때 검토하지 않았다.

## 5. 내 실수
### 5.1 CPU 35~45 % 를 deskew 로 오인 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 프로세스별 CPU 로 과부하 원인 찾기(16j), 최적화 대상 고르기(17a) |
| 본 것 | `top` 의 COMMAND 칸이 `python3` 인 줄 두 개: pid 14964 35.3 %(16j) · 45.5 %(17a), pid 14782 7.8 % |
| 처음 추론 | 큰 python3 = 방금 만든 scan_deskew(Python, 10 Hz × 1800 점, 재배치 루프) → SUMMARY 단계 6 'deskew(py) 35 %', 최적화 대상 'deskew 45 %' → 벡터화 |
| 의심한 이유 | 벡터화 뒤에도 큰 python3(43.6 · 42.2 %)가 그대로였고, deskew 로 잡은 pid 는 0.0 % 였다(17c · 17d) |
| 판별 | `pgrep -f` 로 이름별 pid(17d), `/proc/<pid>/cmdline` 으로 python3 의 실제 스크립트(17e) |
| 결론 | 14964 = `sensor_conditioner.py`(200 Hz 카메라 IMU 처리) 44.1 %, deskew = 19814 · 7.8 %. 벡터화 전 deskew 는 14782 · 7.8~9.0 % 였다 — 처음부터 deskew 는 큰 소비자가 아니었다 |
| 다음에 알아보는 법 | `top` 에서 `python3` · `ros2` 같은 해석기 이름은 **반드시 pid → cmdline** 으로 풀어 적는다(`top -c` 또는 `ps -o pid,pcpu,args`). 08-27 SUMMARY 에 이미 'conditioner CPU 41 %' 가 있었다 — 같은 크기의 python 소비자를 보면 그 기록부터 대조 |
| 데이터 | `2026-08-31/outputs/job16j_cpu.txt` · `job17a_camcheck.txt` · `job17d_clean.txt` · `job17e_identify.txt`; 08-27 '판단·결정' 8 |

### 5.2 deskew CPU 0.0 % — 감싸개(wrapper) 프로세스를 잼 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 벡터화 뒤 deskew CPU(17b AFTER · 17c 회전 중 · 17d 회전 중) |
| 본 것 | pid 19811, 0.0 % 가 10 · 8 샘플 내내 |
| 처음 추론 | SUMMARY 에는 0.0 % 를 쓰지 않고 'deskew ~8 %' 로 기록(17e 값). 코드 주석에는 '초당 ~1.6 만 Python 반복 제거 → deskew CPU 대폭 절감' |
| 의심한 이유 | 17e 에서 `pgrep -f scan_deskew` 가 19811 · 19814 두 개 — `ros2 run` 으로 띄우면 `ros2` 감싸개 프로세스와 실제 python 프로세스가 둘 다 이름에 scan_deskew 를 가진다. 스크립트들은 `pgrep … \| head -1` 로 첫 번째(감싸개)를 골랐다 |
| 판별 | 17e 의 cmdline: 19814 = `…/scan_deskew.py` 7.8 % |
| 결론 | 17b~17d 의 deskew 0.0 % 는 무효. 벡터화 전후 비교는 9.0 %(14782, launch 로 띄운 실제 python) vs 7.8 %(19814) 뿐이고 조건(정지/회전 · 부하)이 달라 '대폭 절감' 은 근거 없음. 17e 의 '중복 인스턴스 2 개' 도 중복이 아니라 감싸개 + 본체(**추정**, 감싸개 cmdline 은 안 봄) |
| 다음에 알아보는 법 | `pgrep -f` 결과가 2 개 이상이면 cmdline 확인. 0.0 % 가 계속 나오면 '아무 일도 안 하는 프로세스를 재고 있다' 를 먼저 의심 |
| 데이터 | `job17b_optapply.txt` · `job17c_validate.txt` · `job17d_clean.txt` · `job17e_identify.txt`, 소스 `ros2_ws/src/rover_bringup/scripts/scan_deskew.py` 의 `np.minimum.at` 주석 |

### 5.3 '순수 회전 중 map→odom 고정 = 정상'
- 그때 근거 '보정할 것 없음(heading 자이로 정확)' 은 heading 만 봤다. 제자리 회전 중 차체 옆 밀림(위치)이 있었고, map→odom 이 안 변한 진짜 이유는 apt slam_toolbox 가 이동 거리 문턱만 보고 회전 중 스캔을 버렸기 때문(09-28). 칸 형식 기록은 이후 시기 카드(회전 미끄러짐 · SLAM 포크)에서 — 이후(09-28 ~): 다음 시기에서 채움(09-04 ~ 09-10 기록에는 이 주제 없음).

### 5.4 'transform_publish_period 20 Hz 인데 실측 ~9 Hz(CPU 눌림)'
- 16i · 16l 은 '버퍼에서 본 map→odom stamp 의 서로 다른 값 개수' 를 셌다. slam_toolbox 는 map→odom stamp 를 '마지막 스캔 시각 + transform_timeout' 으로 찍는다(10-01 §8.5 포크 소스 확인, [SLAM 시각 정체 카드](slam-stamp-freeze.md)). 그러면 서로 다른 stamp 수는 발행 주기(20 Hz)가 아니라 **스캔 수신 주기(최대 10 Hz)** 에 묶이므로 9 Hz 는 정상 쪽이다. 'CPU 눌림' 해석은 근거가 없다(**추정** — 이 시기 apt 판의 해당 코드는 직접 안 봄). 대신 16i(부하 6.2, foxglove 켬)의 **3 Hz** 는 스캔 처리 쪽이 밀렸다는 신호였을 수 있는데 그때는 읽지 않았다(**추정**).

### 5.5 기전을 '확정' 으로 적음
- SUMMARY '결론' 은 'foxglove_bridge 가 /tf 를 클라이언트로 늦게(뭉쳐) 전달' 을 확정처럼 쓴다. 측정된 것은 (a) ROS 안쪽 TF 정상 (b) 브리지 CPU 66 % (c) 재시작 뒤 사용자 육안 해소 뿐이다. 클라이언트 쪽 도착 간격은 재지 않았고, 09-30 에는 같은 증상이 '브리지 큐 깊이 1 이 /tf 를 버림' 으로 다시 설명된다. 증상 해소 = 확인, 기전 = 추정으로 읽어야 한다.

### 5.6 '경량화 효과 확인' — 클라이언트가 안 붙은 상태에서 잼 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `viz:=lean` 등 09-09 경량화의 효과 확인(09-09 §8.12, job159 단독 기동 시험) |
| 본 것 | job159: 단독 기동 유휴 0.7 %. §8.12: 상위 목록에서 브리지가 사라짐(이전 1 위 88.2 %) |
| 처음 추론 | 토픽 집합 · 스레드 · 큐 · 기능을 줄여 브리지 부하가 해결됐다 — '경량화 효과 확인' |
| 의심한 이유 | 다음 날(09-10 §4) lean 그대로인데 브리지 69.6 % · EKF 위반 86 · Nav2 기동 실패 |
| 판별 | `ss -tn \| grep :8765` → 사용자 PC 의 Foxglove Studio 연결(ESTAB) → 브리지를 내리자 위반 0 · active |
| 결론 | 브리지 비용의 주인은 '광고한 토픽 수' 가 아니라 **연결된 클라이언트가 구독하는 것**. job159 · §8.12 는 연결이 없거나 가벼운 상태를 쟀을 가능성이 크다(연결 상태 미기록이라 **추정**). '효과 확인' 은 클라이언트 없음 조건에서만 유효 |
| 다음에 알아보는 법 | 시각화 · 브리지 부하를 잴 때는 **클라이언트 연결 수(`ss -tn \| grep :8765`) · 열린 패널** 을 같은 줄에 적는다. 전후 비교는 같은 클라이언트 조건으로(09-30 의 '연결 vs 끊김' 측정이 그 형태) |
| 데이터 | 09-09 SUMMARY §8.10 · §8.12, 09-10 SUMMARY §4, 도구 `2026-09-09/jobs/job159_fgdeploy.sh` · `2026-09-10/jobs/job191_nofg.sh`. 출력 원문 없음 |

## 6. 남은 것
- 브리지 쪽 기전(늦게 전달 vs 큐에서 버림)을 가르는 측정: Foxglove 클라이언트가 받은 /tf 메시지 간격 기록 — 이후(09-30 ~): 09-30 §12 에서 채움.
- 클라이언트 쪽 무엇이 브리지 1 코어를 만드는가(열린 패널 · 구독 토픽별 비용) — 09-10 은 '연결 유무' 만 갈랐다. 09-30 §5 에서 map 세트로 다시 측정(다음 시기).
- job16c 의 '<no authority> 50.27 Hz' 와 'Max Delay 249 s' 의 뜻(정적 TF stamp 가 섞인 것으로 보임 — **추정**).
- job16b 의 카메라 imu 140.243 Hz(같은 세션 conditioner 출력 `/imu/data` 는 199.989) — `ros2 topic hz` 가 부하 아래서 덜 센 것인지 실제 누락인지 미확인.
- conditioner CPU: 09-09 ~ 09-10 의 경과(35~37 %, 자이로 100 Hz 시도 실패, S6 신설 · 하향)는 [CPU 부족 정지 카드](cpu-load-stalls.md). 이후(09-28 ~): 다음 시기에서 채움(C++ 이식 42.2 → 7.1 %).

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job16a · 16m | 세션 초기화 · 조이스틱 재기동 | `2026-08-31/jobs/` · `outputs/` 같은 이름 |
| job16b · 16c · 16d | TF 발행률 · tf2_monitor | 같은 곳 |
| job16e · 16f | stamp · 클럭 · 콜백 안 지연 | 같은 곳 |
| job16g · 16h | 회전 중 TF 값 변화 주기(사용자 회전 / 스크립트 회전) | 같은 곳(16g 출력 없음) |
| job16i · 16l | slam 로그 · map→odom stamp 수 · 파라미터 | 같은 곳 |
| job16j · 16k | 프로세스별 CPU · foxglove 끄고 회전 | 같은 곳 |
| job17a ~ 17e | 카메라 토픽 · 최적화 배포 · 회전 중 CPU · pid 식별 | 같은 곳 |
| job157 · 158 · 159 | 브리지 파라미터 · capabilities 확인 · lean 배포 · 단독 기동(09-09) | `2026-09-09/jobs/`, 출력 원문 없음 |
| job189 · 190 · 191 | Nav2 기동 실패 · lifecycle 오류 · 클라이언트 연결 확인 후 브리지 끄고 30 s(09-10) | `2026-09-10/jobs/`, 출력 원문 없음 |
| `foxglove.launch.py` | topic_whitelist(09-01) → 코스트맵 · 경로 추가(09-08) → viz 단계(09-09) → map 세트(09-30) | `ros2_ws/src/rover_bringup/launch/` |

## 8. 도구 해설
공통: 전부 **Jetson** 에서 실행(PC → WSL → ssh, 비밀번호 `<PW>`; 출력 첫 줄의 깨진 `wsl:` 경고 = WSL 의 localhostForwarding 안내문이 한글 코드페이지로 깨진 것). 인자 없음. CPU 수치는 `top -b -n 2 -d 1` 의 **두 번째 화면**(1 초 구간), 단위는 코어 1 개 = 100 %(6 코어 = 600 %). 1 초 표본 하나라 ±수 % 흔들린다. `top` 은 이름을 15 자로 자르고(`foxglov+` · `async_s+` · `realsen+`), Python 노드는 전부 `python3` 으로 보인다(§5.1).

**도구 계보**
- 기동: job16a(전체) → job16m(조이스틱만). 이전 판 = 08-31 job8d · 08-28 job6m.
- TF 주기: job16b(`ros2 topic hz /tf` + tf2_monitor, grep 실패) → job16c(tf2_monitor tail) → job16d(+ net delay 재측정) → job16g(사용자 회전, TF 값 변화 간격) → job16h(스크립트 회전 + 가드) → job16k(foxglove 끄고 같은 시험, map→odom 만)
- 시각: job16d(파이썬 결함) → job16e(첫 메시지 stamp, 결함) → job16f(콜백 안 40 개 평균) — 08-28 job8a 의 측정식과 같음
- SLAM: job16i(로그 · stamp 수 · 파라미터 · 부하) → job16l(period · stamp 수 재측정)
- CPU: job16j(top) → job17a(+ 카메라 파라미터) → job17b(전후, pgrep 첫 pid) → job17c(회전 중 10 샘플) → job17d(이름별 pid) → job17e(cmdline 으로 정체) — 이후 `Docs/tools/anal_top.py` · `anal_proc_cpu.py`(10-12)로 고정 도구화
- 2 기(09-09 ~ 09-10): job157(파라미터 이름) · job158 B)(capabilities) → job159(lean 배포 · 무클라이언트 기동 시험) → (09-10) job189 · 190(기동 실패 · 부하) → job191(클라이언트 연결 확인 → 브리지 끄고 30 s 차분). 09-10 의 30 s 창 CPU 는 이름별 평균 집계라 python3 가 희석된다([CPU 카드 §6 모순 1](cpu-load-stalls.md))

### job16a_init.sh — 세션 초기화
- 하는 일: base · sensors · slam · joy_teleop launch, realsense · rplidar · scan_deskew · ekf · conditioner · foxglove · RSP · slam · joy_linux · teleop `pkill -9` → agent 컨테이너 제거 → base.launch(10 s) → `/wheel_odom` hz → sensors.launch(16 s, 자이로 바이어스 보정 동안 로버 정지) → 'gyro bias' 로그 → slam.launch(10 s) → 노드 목록 · filtered · scan hz · `tf2_echo map odom` · conditioner 소스의 `VX_SCALE =` 줄.
- 출력: [job16a_init.txt](../debug_log/2026-08-31/outputs/job16a_init.txt) — wheel_odom 50.011, filtered 29.948, `/scan` 칸 빈 값, map→odom (0,0,0), VX_SCALE 1.022(같은 날 세션 3 에서 무효로 판명된 값).

### job16b_tfdiag.sh — 센서 · TF 진단 + 조이스틱
- 하는 일: 바이어스 로그 → `/imu/data` · `/camera/camera/imu` · `/scan` hz → `/tf` hz → `tf2_monitor odom base_link` · `map odom` 각 9 s 를 `Average rate|Average delay|Buffer` 로 grep → joy_teleop.launch 재기동.
- 출력: [job16b_tfdiag.txt](../debug_log/2026-08-31/outputs/job16b_tfdiag.txt) — /tf 30.998 Hz, tf2_monitor 두 칸 **빈 값**(출력 형식이 'Average Delay' 대문자 등이라 grep 불일치로 보임 — **추정**).
- 결함: grep 패턴. 조이스틱을 켜 둔 채 이후 스크립트 회전을 하면 `/cmd_vel` 이 이중 발행된다(SUMMARY '부수 발견').

### job16c_tfmon.sh — tf2_monitor 원문
- 하는 일: `tf2_monitor odom base_link` · `map odom` 각 8 s, 마지막 20 줄.
- 출력: [job16c_tfmon.txt](../debug_log/2026-08-31/outputs/job16c_tfmon.txt) — 'Net delay avg 0.0033 · max 0.0202'(odom→base), map→odom 은 −0.0094 · 0; 발행자 '<no authority available>' 50.27 · 50.35 Hz, Average Delay 0.80 · 0.91 s, Max Delay 249.7 · 261.8 s.
- 읽는 법: net delay = 변환 stamp 와 수신 시각 차(체인 전체). '<no authority>' 줄은 /tf 전체에 대한 집계로 보이며 큰 Max Delay 는 기동 때 stamp 가 찍힌 정적 변환이 섞인 것일 수 있다(**추정**). 결론에는 net delay 만 썼다.

### job16d_tsverify.sh — 재측정 + stamp(실패)
- 하는 일: `tf2_monitor odom base_link` 13 s 의 Net delay · Node · Max Delay 줄 → 파이썬: 토픽 4 개(`/wheel_odom` · `/odometry/filtered` · `/camera/camera/imu` · `/scan`) 첫 메시지 stamp.
- 출력: [job16d_tsverify.txt](../debug_log/2026-08-31/outputs/job16d_tsverify.txt) — net delay 평균 6.1 ms · 최대 35.6 ms; 파이썬은 `rclpy.init()` 을 안 불러 `NotInitializedException`.
- 계보: 16e 에서 init 추가.

### job16e_stamps.sh — 토픽별 첫 stamp vs now
- 하는 일: 토픽 5 개(위 4 개 + `/scan_raw`)를 구독해 **각 토픽 첫 메시지의 stamp** 만 저장 → 5 개가 다 오거나 6 s 가 지나면 그때 `now` 를 한 번 읽어 `now − stamp` → 보드(wheel_odom) − 카메라(imu) stamp 차.
- 출력: [job16e_stamps.txt](../debug_log/2026-08-31/outputs/job16e_stamps.txt) — 보드 − 카메라 **−0.002 s**(클럭 동기 근거). filtered · scan 류 0.67~0.68 s.
- 결함: `now` 를 마지막 토픽이 도착한 뒤에 읽으므로 먼저 받은 토픽일수록 '대기 시간' 이 지연으로 더해진다(0.68 s 는 지연이 아님). 보드 − 카메라 차는 둘 다 빨리 오는 토픽(50 · 200 Hz)이라 쓸 만하다. 계보: 16f 에서 콜백 안 측정으로 고침.

### job16f_latency.sh — 콜백 안 지연 ★
- 하는 일: `ros2 param get <노드> use_sim_time`(EKF · rplidar · slam · deskew) → 토픽 5 개 구독, **콜백 안에서** `now − stamp` 를 토픽당 40 개까지 5 s → 평균 · 최대 · 최소 ms.
- 출력: [job16f_latency.txt](../debug_log/2026-08-31/outputs/job16f_latency.txt) — §2 의 값(scan_raw 102.7 · scan 3.1 ms 등).
- 쓰인 곳: SUMMARY 단계 2('타임스탬프/클럭 기각'). [스캔 끌림 카드](scan-drag-deskew.md) 의 deskew 정지 지연 표에도 쓰임.
- 다시 쓸 수 있음(측정식이 옳다). 단 '지연' 은 stamp 를 어디 찍느냐에 따라 달라지는 값이라 작다고 정합이 맞는 것은 아니다.

### job16g_tfcadence.sh — 사용자 회전 중 TF 값 변화 주기
- 하는 일: 20 s 동안 0.02 s 마다 TF 버퍼에서 `odom→base_link` · `map→odom` 의 (x, y, yaw) 를 소수 4 자리로 반올림해 조회, **값이 바뀐 순간 사이 간격**을 모음 → 횟수 · 평균 · 최대 · 최소; `/odometry/filtered` yaw 범위.
- 출력 원문 없음(대화에만, 실행 여부도 기록 없음). 같은 측정을 16h 가 스크립트 회전으로 대신했다.
- 주의: 값 반올림 4 자리라 아주 느린 움직임은 '변화 없음' 으로 셀 수 있다. yaw 식이 `atan2(2wz, 1 − 2z²)` 로 롤 · 피치 0 을 가정.

### job16h_rotlog.sh — 스크립트 회전 + TF 로깅 ★
- 하는 일: `/cmd_vel` 0.6 rad/s 를 15 s 발행하면서 16g 와 같은 값 변화 간격 측정, `/scan` 으로 차체 사각형까지 여유(라이다 0.152 m · yaw π, 차체 x ±0.25 · y ±0.165) 계산 — **5 cm 미만이면 정지**, 끝나면 0 Twist 15 회; `/odometry/filtered` yaw 를 unwrap 해 총 회전량.
- 출력: [job16h_rotlog.txt](../debug_log/2026-08-31/outputs/job16h_rotlog.txt) — 202°, odom→base 448 회 · 33 ms · 66 ms, map→odom 고정.
- 쓰인 곳: 단계 3(odom TF 건강), 단계 4(map→odom 고정 — 해석은 §5.3).
- 결함: 측정은 Jetson 안 TF 버퍼 — Foxglove 클라이언트가 받는 것과는 다르다(그래서 '표시층' 결론의 간접 근거만 됨). 회전 명령 0.6 rad/s 와 실제 회전(202°/15 s ≈ 0.235 rad/s)의 차이는 기록 안 됨.

### job16i_slamdiag.sh — SLAM 진단
- 하는 일: `/tmp/slam.log` 에서 drop · transform · timeout · warn · error · queue 등 마지막 15 줄 + 마지막 10 줄 → 4 s 동안 0.05 s 마다 `map→odom` 조회해 **서로 다른 stamp 집합** → slam 파라미터 7 개 → `uptime` load · `top` 에서 `sync_slam_toolbox_node` 줄의 CPU.
- 출력: [job16i_slamdiag.txt](../debug_log/2026-08-31/outputs/job16i_slamdiag.txt) — 'minimum laser range setting (0.0 m) exceeds … (0.2 m)' 경고(08-27 에도 '무해'), 'queue is full' 2 줄, stamp 12 개, load 6.21, slam CPU 빈 값.
- 결함: top 은 이름이 `async_s+` 로 잘려 `sync_slam_toolbox_node` 와 안 맞음. stamp 수의 뜻은 §5.4.

### job16j_cpu.sh — 프로세스별 CPU
- 하는 일: joy_linux · teleop 종료(`/cmd_vel` 이중 발행 제거) → `nproc` · `/proc/loadavg` → `top -b -n 2 -d 1 -o %CPU` 두 번째 화면 상위 16 줄(머리 포함).
- 출력: [job16j_cpu.txt](../debug_log/2026-08-31/outputs/job16j_cpu.txt) — §2 값. TIME+ 칸(foxglove 16:19.72 = 누적 CPU 16 분)이 SUMMARY '16 분 누적' 의 출처.
- 결함: python3 정체 미식별(§5.1).

### job16k_fgtest.sh — foxglove 끄고 회전
- 하는 일: `pkill -f foxglove` → 4 s 뒤 load → 16h 와 같은 회전(0.6 rad/s · 12 s · 5 cm 가드)에서 `map→odom` 값 변화만 → 회전량 · 변화 횟수 · load.
- 출력: [job16k_fgtest.txt](../debug_log/2026-08-31/outputs/job16k_fgtest.txt) — load 4.24 → 3.73, 157°, map→odom 고정.
- 쓰인 곳: 단계 5('CPU 가 slam-stall 원인 아님').

### job16l_fgrestart.sh — period 확인 · foxglove 재시작
- 하는 일: `ros2 param get /slam_toolbox transform_publish_period` → 정지 상태 4 s 동안 0.02 s 마다 map→odom stamp 집합 → `ros2 run foxglove_bridge foxglove_bridge`(launch 아님 → **화이트리스트 없이** 기본 설정) → 노드 존재 · load.
- 출력: [job16l_fgrestart.txt](../debug_log/2026-08-31/outputs/job16l_fgrestart.txt) — 0.05, stamp 36 개(~9 Hz), load 1.90.
- 쓰인 곳: '부수 발견'(재발행 ~9 Hz), 단계 7 의 재시작.
- 결함: 이렇게 `ros2 run` 으로 띄운 브리지가 17b 에서 launch 판과 겹쳐 '이중 기동 사고' 의 씨앗이 됐다(**추정** — 17b 의 `pkill -f foxglove` 뒤에도 2 개가 보인 이유는 미확인).

### job16m_joy.sh — 조이스틱 재기동
- 하는 일: `/dev/input/js0` 확인 → joy_linux · teleop 종료 → joy_teleop.launch(6 s) → 노드 · `/joy` 축 · `/cmd_vel` 1 회 · load.
- 출력: [job16m_joy.txt](../debug_log/2026-08-31/outputs/job16m_joy.txt) — 축 0 · 0, cmd_vel 0, load 2.62.
- 쓰인 곳: 사용자 주행 → '매끄러워졌다' 확인의 준비.

### job17a_camcheck.sh — 카메라 토픽 · 파라미터 · CPU
- 하는 일: `ros2 topic list | grep camera` → `/camera/camera` 의 enable_color · depth · gyro · accel · infra1 · infra2 · pointcloud.enable · enable_sync · unite_imu_method → color · depth · infra1 영상 hz 3 s → top 상위 6(COMMAND · %CPU 만).
- 출력: [job17a_camcheck.txt](../debug_log/2026-08-31/outputs/job17a_camcheck.txt) — 압축 전송 토픽(compressed · compressedDepth · theora)까지 광고됨, color 15.005 Hz(depth 칸 빈 값), pointcloud.enable 빈 값, CPU 표.
- 쓰인 곳: '카메라 토픽을 화이트리스트에서 빼자' 의 근거. CPU 표는 §5.1 오인의 재료.

### job17b_optapply.sh — 벡터화 deskew + 화이트리스트 배포
- 하는 일: BEFORE — `pgrep -f scan_deskew | head -1` 의 CPU(`top -p`) · load → PC 에서 올린 `/tmp/scan_deskew.py` · `/tmp/foxglove.launch.py` 를 소스로 복사 → `colcon build --packages-select rover_bringup` → deskew 종료 후 **`ros2 run rover_bringup scan_deskew.py --ros-args -p ref:=end -p omega_deadband:=0.02`** → foxglove 종료 후 `foxglove.launch.py` → `/scan` hz · 노드 · `topic_whitelist` 파라미터 → AFTER(같은 방식) · 상위 6 · load.
- 출력: [job17b_optapply.txt](../debug_log/2026-08-31/outputs/job17b_optapply.txt) — 전 14782 · 9.0 %, 후 19811 · 0.0 %(감싸개), foxglove 노드 2 개 55.9 · 51.0 %.
- 결함: §5.2(pgrep 첫 pid). `--symlink-install` 없이 빌드(앞선 job 들과 다름 — 영향은 미확인). deskew 가 launch 밖에서 돌게 돼 '다음 full 재시작 때 lidar.launch 로 복귀' 메모가 필요해졌다(SUMMARY).

### job17c_validate.sh — foxglove 정리 + 회전 중 deskew CPU
- 하는 일: `pkill -9 -f foxglove_bridge` → launch 로 하나만 → 개수 → joy 종료 → `/tmp/rot.py`(0.6 rad/s · 15 s · 5 cm 가드, 16h 의 축소판)를 백그라운드로 → 2 s 뒤 `top -b -n 10 -d 1 -p <deskew pid>` 평균 → 상위 6 · load · `/scan` hz.
- 출력: [job17c_validate.txt](../debug_log/2026-08-31/outputs/job17c_validate.txt) — foxglove 1, deskew 0.0 %(19811, 무효), foxglove 11.9 %.
- 결함: 회전이 실제로 일어났는지 출력에 증거 없음(각속도 · 회전량 미기록).

### job17d_clean.sh — pid 식별 + 가벼운 회전
- 하는 일: rot.py 종료 → `pgrep -f` 로 deskew · conditioner 첫 pid → `timeout 12 ros2 topic pub /cmd_vel … '{angular: {z: 0.6}}' -r 20` 백그라운드 → `/odometry/filtered` 의 twist z 1 회 → deskew pid 8 샘플 → 0 Twist 10 회 → 상위 6 · load.
- 출력: [job17d_clean.txt](../debug_log/2026-08-31/outputs/job17d_clean.txt) — deskew 19811 · conditioner 14964, 각속도 칸 빈 값, deskew 0.0 % × 8.
- 쓰인 곳: '큰 python3 = 14964 = conditioner' 의 첫 단서.

### job17e_identify.sh — cmdline 으로 정체 확인 ★
- 하는 일: `pgrep -f` 로 scan_deskew · sensor_conditioner 의 pid 전부와 개수, foxglove 개수 → top 상위 9 줄을 파일로 → python3 인 pid 마다 `/proc/<pid>/cmdline` 에서 `.py` 경로.
- 출력: [job17e_identify.txt](../debug_log/2026-08-31/outputs/job17e_identify.txt) — 14964 `sensor_conditioner.py` 44.1 %, 19814 `scan_deskew.py` 7.8 %, foxglove 8.8 %.
- 쓰인 곳: SUMMARY '결과' 의 정정 · 'foxglove 66 → 8.8 %'.
- 다시 쓸 수 있음 — 이 'pid → cmdline' 단계가 이후 CPU 도구의 기본이 됐어야 할 부분(10-12 `anal_proc_cpu.py` 는 전 프로세스 틱 기록 방식).

### foxglove.launch.py — topic_whitelist(09-01 판)
- 실행: Jetson, `sensors.launch.py` 가 포함(17b 에서 단독 launch 로도).
- 하는 일: `foxglove_bridge` 노드(port 8765, address 0.0.0.0)에 `topic_whitelist` = 위 §4 의 15 개 이름. 브리지는 각 항목을 **정규식 full-match** 로 토픽 이름과 맞춰 맞는 것만 클라이언트에 광고 · 서빙한다(주석). `/camera/*` 가 빠져 영상 · 깊이 · 압축 전송이 안 나간다.
- 계보: 09-08 코스트맵 · 경로 6 개 추가(커밋 `fe79f1c4`, 합계 22 개 — 09-09 SUMMARY 는 '고정 21개' 로 적음, 하나 차이) → 09-09 viz 3 단계(LEAN 은 `/imu/data` 200 Hz · `/scan_raw` · `/wheel_odom` · `*_updates` 도 뺌 — 이 09-01 판에는 앞 셋이 들어 있었다), num_threads 2, max_qos_depth 1, capabilities 축소 → 09-30 map 세트(max_qos_depth 10). 09-09 판 상세는 아래 'foxglove.launch.py — 09-09 판'.

### job157_fg.sh — 브리지 파라미터 이름 확인(09-09)
- 실행: Jetson, 인자 없음.
- 왜: 경량화 파라미터를 '추측하지 않고' 설치본에서 확인(09-09 §8.10 '확인된 가용 수단').
- 하는 일: `/opt/ros/humble/lib/foxglove_bridge/` 목록 → 실행 파일 · `.so` 에 `strings` 를 걸어 port · address · tls · topic_whitelist · param_whitelist · service_whitelist · client_topic_whitelist · min/max_qos_depth · num_threads · send_buffer_limit · use_compression · capabilities · asset_uri_allowlist · include_hidden · disable_load_message · ignore_unresponsive_param_nodes 와 **정확히 같은 줄**만 → `package.xml` 버전 → 설치본 sensors.launch 의 imu · remap 줄.
- 출력: 6 개 파라미터 존재 · 3.2.4(SUMMARY §8.10 블록). 원문 없음.
- 결함: 문자열이 바이너리에 있다고 '선언된 파라미터' 라는 보장은 없다(로그 문구 등일 수 있음) — 실제 수용은 job159 의 기동 시험이 확인.
- 지금: 같은 방법(설치본 문자열 · 예제 확인)은 STVL 파라미터 확인(§8.11)에도 쓰였다. 재사용 가능.

### job158_alt.sh — 대안 가용성 확인(이 카드엔 B) 부분)
- 하는 일: A) Nav2 코스트맵 라이브러리에서 `observation_persistence` · `expected_update_rate` · `observation_keep_time` · `min_obstacle_height` · `combination_method` 문자열 B) 브리지 실행 파일에서 `clientPublish|parameters|parametersSubscribe|services|connectionGraph|assets` C) realsense 라이브러리에서 `json_file_path` · `depth_module.*` · disparity shift D) 설치된 코스트맵 플러그인 class 이름.
- 출력: B) 기본 capabilities 6 종 → 09-09 판에서 3 종으로 축소. A) · C) 는 STVL 외 대안 표(§8.10)의 근거(다른 카드).

### job159_fgdeploy.sh — lean 배포 · 단독 기동 시험(09-09)
- 하는 일: `/tmp` 의 `foxglove.launch.py` · `sensors.launch.py` CR 제거 → src · install 복사 → 두 파일을 `ast.parse` 로 문법 검사 → `viz` 기본값 grep → `foxglove.launch.py` 단독 기동 10 s → 프로세스 수 · 로그의 error|invalid|not declared|exception|Starting|listening 6 줄 · `ps %cpu` → TERM 정리 · 남은 수.
- 출력: '파라미터 거부 없이 정상(3.2.4, 포트 8765, 유휴 0.7 %)'(§8.10). 원문 없음.
- 결함: 유휴 · 무클라이언트 조건 — 효과의 근거로는 부족(§5.6). `ps %cpu` 는 기동 10 s 생애 평균.
- 지금: 배포 · 문법 검사 형태는 유효.

### job191_nofg.sh — 클라이언트 연결 확인 → 브리지 끄고 30 s(09-10) ★
- [CPU 카드 §9.9](cpu-load-stalls.md) 에 상세. 이 카드에 쓰인 값: `ss -tn | grep :8765` 의 `ESTAB 192.168.0.101:8765 ← 192.168.0.6:65351`, 정지 뒤 30 s EKF 위반 0 · slam 폐기 0 · lifecycle active.
- 결함: 브리지를 끄면 '클라이언트 연결' 과 '브리지 프로세스' 가 함께 사라져 둘을 가르지 않는다 — 결론('연결이 비용')은 job159 유휴 0.7 % 와의 대비로 읽은 것.

### foxglove.launch.py — 09-09 판(커밋 `585df0ea`)
- 실행: Jetson, `sensors.launch.py` 가 `viz` 인자를 넘겨 포함(단독 기동도 가능). `OpaqueFunction` 으로 실행 시점에 `viz` 값(lean · full · cam, 그 외는 lean)을 읽어 화이트리스트를 고른다.
- 하는 일: 위 §4b '조치' 의 세트 · 파라미터. 주석 근거: 09-01(과부하 → 4 초 점프) · 09-09(88~95 %, EKF 위반 동반, 비용 = 건수 × 직렬화).
- 계보: 09-30 `map` 세트(`/tf` · `/tf_static` · `/robot_description` · `/map` · `/map_metadata` · `/scan`, capabilities `clientPublish` 만, max_qos_depth 10) 추가. 지금도 계속 쓰는 파일.

## 9. 용어
- **foxglove_bridge · topic_whitelist**: ROS 토픽을 웹소켓(ws://<jetson>:8765)으로 Foxglove 앱에 중계하는 노드. 클라이언트가 고른 토픽마다 구독 · 직렬화 · 전송을 하므로 고주파 · 대용량 토픽(영상 · 200 Hz IMU)이 많을수록 CPU 를 쓴다. whitelist 는 '광고 자체를 허용할 토픽' 정규식 목록.
- **fixed frame(뷰어)**: 모든 것을 그릴 기준 프레임. `map` 이면 로버 위치 = map→odom × odom→base_link 의 합성이라 두 변환 중 늦게 오는 쪽에 묶인다. `odom` 이면 map→odom 이 빠진다. 이 문제에서는 바꿔도 증상이 같아 '표시층(브리지 · 클라이언트)' 으로 좁히는 데 쓰였다.
- **TF 변화 간격(cadence)**: 버퍼에서 조회한 변환 값이 실제로 바뀐 순간 사이 시간. 발행 주기(hz)와 달리 '움직임이 반영되는 주기' 를 본다(16g · 16h).
- **now − stamp(지연)**: 받는 순간 시계 − 메시지 stamp. 같은 기계 · 같은 시계일 때만 의미가 있다(use_sim_time False 확인).
- **map→odom stamp(slam_toolbox)**: '마지막 스캔 시각 + transform_timeout' 으로 찍힌다(10-01 확인). 그래서 서로 다른 stamp 의 수는 발행 주기가 아니라 스캔 흐름을 반영한다.
- **load average**: 실행 대기 + 실행 중 작업 수의 평균(1 · 5 · 15 분). 6 코어에서 6 이면 포화 근처.
- **top %CPU · TIME+**: %CPU 는 직전 구간(여기선 1 초) 사용률, 코어 1 개 = 100 %. TIME+ 는 그 프로세스가 지금까지 쓴 CPU 시간 누계.
- **감싸개(wrapper) 프로세스**: `ros2 run` 이 띄우는 `ros2` 파이썬 프로세스가 실제 노드 프로세스를 자식으로 띄운다. 둘 다 명령줄에 노드 이름이 들어 있어 `pgrep -f` 가 둘 다 잡는다.
- **sensor_conditioner**: D455f 카메라 IMU(200 Hz)의 바이어스 · covariance 를 다듬고 휠 오도 스케일(VX_SCALE)을 곱해 EKF 에 넘기던 Jetson 쪽 Python 노드(임시 shim). 이 시기 최대 CPU 소비자.
- **queue full 드롭(slam)**: slam_toolbox 메시지 필터가 TF 를 기다리는 스캔을 둘 자리가 없어 버린 것. 이 세션에선 간헐(2 줄).
- **브리지 파라미터(foxglove_bridge 3.2.4)**: `num_threads` = 웹소켓 처리 스레드 수(0 = 코어 수). `max_qos_depth` = 브리지가 각 토픽을 구독할 때 쓰는 큐 깊이 상한(1 이면 밀릴 때 최신 하나만 남기고 버림). `send_buffer_limit` = 클라이언트별 송신 버퍼 상한(바이트, 넘으면 메시지 버림). `use_compression` = 웹소켓 압축. `capabilities` = 클라이언트에 허용하는 기능(파라미터 조회 · 구독, 서비스 호출, 그래프 조회, 자산 전송, 클라이언트 발행 등) — 일부는 브리지가 주기적으로 ROS 그래프를 훑게 만든다.
- **클라이언트 연결(ESTAB)**: `ss -tn` 에서 브리지 포트 8765 에 맺어진 TCP 연결. 연결된 Foxglove Studio 가 구독한 토픽만 실제로 직렬화 · 전송된다 — 광고 목록(화이트리스트)이 같아도 연결 · 열린 패널에 따라 브리지 비용이 달라진다(09-10 §4).
