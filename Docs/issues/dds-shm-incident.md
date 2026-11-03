# DDS 공유메모리(SHM) 사고 — 살아 있는 노드가 그래프에서 사라짐, 그리고 중첩 프로세스

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회 → 견고성 선택으로 유지**(09-09 SHM 을 끄고 UDP 전용, 재발 0) · 원인 판정은 **10-20 에 일부 정정**(SHM '자체' 가 원인이라는 것은 과한 일반화 — 확인된 것은 '비정상 종료 · 잔재 강제 삭제가 있으면 깨진다' 까지) · 10-20 시험 뒤 카메라 ↔ cuVSLAM 만 SHM 재사용(10-23 운용 기본) | 09-09 (1 회차 · 2 회차) · 09-11(중첩 프로세스) · 10-12 재사용 검토(§8.3~§8.6 · §17~§19 · §21 — 결정 · 설명만, 바꾼 파일 없음) · 이후 10-20 재점검 · 10-23 | [09-09 §8.9](../debug_log/2026-09-09/SUMMARY.md) — 사용자 보고 "지도를 벗어나 이상하게 움직인다" | `ros2_ws/src/rover_bringup/config/fastdds_udp_only.xml`(신규, 커밋 `2a4092b2`) · `base` · `sensors` · `slam` · `navigation` launch 의 `SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', …)` · 정리 스크립트(SIGTERM 우선) · 09-11 `job240_clean.sh` 중복 감사 | [micro-ROS 보드율 회귀](microros-baud-regression.md)(같은 날 오전, `pkill` 오염의 시작) · [CPU 부족 정지](cpu-load-stalls.md)(같은 서명의 다른 원인 — 2 회차 판정과 섞임) · [보드 연결 · 세션](board-link-microros-session.md)(정리 스크립트가 agent 까지 지워 RESET 반복) · [W3 떨림 · TF 지연](tf-lag-w3-wobble.md) (6 기) · [통신 포화 · MPPI 궤적 발행](network-saturation-mppi-viz.md)(7 기 — 10-12 SHM 재검토의 출발점) · [빠른 prep](prep-fast-startup.md)(정리 단계 · `fastdds shm clean`) |

**한 줄**: 09-09 저녁, EKF 프로세스는 CPU 20 % 로 살아 있고 입력도 정상인데 `/odometry/filtered` 퍼블리셔가 **0** 이 됐다. FastDDS 로그에 `open_and_lock_file failed`, `/dev/shm` 에는 본체 없이 잠금 파일(`_el`)만 남은 고아가 있었다. 그날 내가 정리를 '확실히' 하려고 13 개 스크립트에서 `pkill -9` 를 썼고, SIGKILL 은 FastDDS 가 SHM 파일을 치우지 못하게 한다. SIGTERM + 잔재 삭제로 복구했으나 몇 시간 뒤 `slam_toolbox` 에 같은 서명이 다시 나왔고, 'SIGTERM 으로 바꿨는데도 재발 → SHM 을 쓰는 것 자체가 문제' 로 보고 SHM 을 끈 UDP 전용 프로파일을 모든 launch 에 넣었다(재발 0). 10-20 에 사용자 요청으로 다시 보니 2 회차 전 스크립트들이 **살아 있는 참가자의 SHM 파일까지 `rm -f`** 했고 launch 의 SIGKILL 단계도 확인 안 됐으며 같은 날 CPU 정지와 섞여 있었다 → 'SHM 자체' 는 근거가 약했다. 정리 없이 −9 를 섞은 재기동 시험(FastDDS 2.6.12)이 15/15 · 30/30 통과해, 10-23 부터 카메라 ↔ cuVSLAM 경로만 SHM 을 쓴다. 09-11 에는 다른 형태의 '중첩' — launch 를 죽여도 자식 `robot_state_publisher` 가 고아로 남아 같은 이름 노드가 둘 — 을 사용자 지적으로 찾아 기동 절차에 중복 감사를 넣었다. **10-12(7 기)** 에는 통신 포화(UDP 수신 버퍼 208 kB 넘침이 의심됨) 대책으로 사용자가 SHM 재사용을 물었다. 나는 처음에 질문을 DDS SHM 으로 읽고 '지금은 바꾸지 않는다'(원인 미확정 · 고아 위험)로 답했는데(§8.3), 사용자가 물은 것은 Jetson 의 CPU·GPU 통합 메모리였다(§8.4 — 내 오독). 이어서 전송은 프로세스 단위로 섞을 수 있다(§8.5), micro-ROS 는 SHM 을 막지 않는다(§8.6), 가변 길이 표준 메시지(Image · PointCloud2)는 zero-copy 대상이 아니다(§18 · §19)를 정리했고, 사용자는 '프로세스 간 전달은 DDS SHM 으로' 를 결정했다(§17). 그러나 10-13 캡처가 포화의 시작을 bag 기록기의 reliable `/tf` 로 좁혀 기록기 QoS 로 막았고([통신 포화 카드](network-saturation-mppi-viz.md)), SHM 도입은 10-15 까지 실행되지 않았다(보류한다는 문장도 없음). 실제 도입은 10-20 의 카메라 ↔ cuVSLAM 경로 하나. 10-12 설명 가운데 '깊이 영상 614 kB' 는 틀린 계산값이었다(실제 38 kB, 10-20 §7.5 — §5.6).

## 1. 증상
- 1 회차(09-09 §8.9): 사용자 "지도를 벗어나 이상하게 움직인다". `/odometry/filtered` **Publisher count: 0**, `ekf_node` 살아 있음(CPU 20 %, 상태 `Sl`), 입력 정상(`/wheel_odom/conditioned` 25 Hz · `/imu/data` 199.7 Hz), 타임스탬프 오프셋 −0.002~−0.032 s · 역행 0. 로그 `[RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_port7423: open_and_lock_file failed`, `/dev/shm/fastrtps_port7423` **없음** · `fastrtps_port7423_el` **있음**.
- 연쇄(SUMMARY 서술): EKF 가 TF 를 못 냄 → map 좌표 얼어붙음 → SLAM 이 `/map` 을 못 냄 → 코스트맵이 `Message Filter dropping message: frame 'camera_depth_optical_frame' / 'lidar_link'` 로 **라이다 · 카메라를 둘 다 버림** → 계획 · 복구가 엉킴. 보드 토픽만 멀쩡(agent 컨테이너 `MICROROS_DISABLE_SHM=1`).
- 2 회차(09-09 §8.15): `slam_toolbox` 프로세스 생존(CPU 정상)인데 노드가 그래프에서 사라짐, `/map` 퍼블리셔 0, map 프레임 소멸, `/dev/shm` 고아 `fastrtps_port7425`(잠금 파일만). 이 2 회차가 `job170` 주행의 '위치가 9.90 s 동안 소수점 17 자리까지 같다가 조회 실패' 와 같은 사건이라는 연결은 SUMMARY 본문이 아니라 `fastdds_udp_only.xml` 주석 · 커밋 `2a4092b2` 에만 있다(§6 모순 1).
- 09-11 §5.9: `robot_state_publisher` 프로세스 **2 개**(PID 3054 / 5769), `base.launch` 는 1 개. 같은 URDF 정적 TF 를 둘이 발행해 값은 같지만 그래프에 노드 이름 중복.
- 출력 원문: 09-09 · 09-11 모두 해당 job 의 `outputs/` 없음(09-09 는 폴더가 비어 있음, 10-20 §7.2 도 확인) — 수치는 SUMMARY 서술뿐. **원천 소실**.

## 2. 흐름 (시간순)
jobs 는 [2026-09-09/jobs/](../debug_log/2026-09-09/jobs/) · [2026-09-11/jobs/](../debug_log/2026-09-11/jobs/). 출력은 전부 원문 없음.

| 곳 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 도구 |
|---|---|---|---|---|
| 09-09 오전~오후 | 정리를 `pkill -9` 로(오전 ERE 패턴 결함을 고친 for-루프판도 `-9`) | 13 개 job 에서 반복: job97·100·101·102·104·115·121·122·123·127·129·132·143(SUMMARY §8.9 목록) | (그때는 무해하다고 봄) | 각 job |
| §8.9 | 이상 주행 보고 → 부하 · 중복 · TF · 온도 · 배터리 | (수치 미기록) | — | `job139_sys.sh` |
| | 보드 스톨 · 래치 · 배터리 · nav2 마지막 | (미기록) | — | `job142_stall.sh` |
| | **즉시 정지**: 지령 노드 `pkill -9` → 0 Twist 25 회 | — | — | `job143_estop.sh` |
| | TF 체인 · `/map` 범위 vs 로버 · slam 경고 · 취소 뒤 nav2 로그 | 보드 `/wheel_odom` x = 1.614 | '**SLAM 정합이 어긋났다**' · '보드 odom 대비 **헛돌았다**' — 둘 다 **틀림**(§5.2) | `job144_slam.sh` |
| | 프로세스 수 · 토픽 Hz · 'died · exit code · Failed to meet update rate' · `/dev/shm` 사용량 · 파일 수 · 메모리 | `ekf_node` 살아 있음 | — | `job145_alive.sh` |
| | EKF 입력 8 토픽 Hz · 노드별 CPU · 상태 | 입력 정상, ekf CPU 20 % `Sl` | 'EKF 가 입력은 받는데 출력을 안 함' | `job146_ekfin.sh` |
| | 가설: 보드 time resync 가 튀어 EKF 가 '과거 메시지' 로 버린다 → 토픽별 마지막 stamp − host · 역행 · 최대 전진폭 12 s | 오프셋 −0.002~−0.032 s · 역행 **0** | 시각 동기 **기각** | `job147_stamp.py` |
| | `/dev/shm` 내용 · 문제 포트 파일 소유 · 잠금(`fuser`) · `/odometry/filtered` · `/tf` 퍼블리셔 | 7423 본체 없음 · `_el` 있음, 퍼블리셔 0 | **SHM 고아 잠금 파일**(서명 확정) | `job148_shm.sh`(7423 과 7427 두 포트를 봄 — 7427 결과는 미기록) |
| | 0 지령 20 회 · 보드가 보는 모터 상태 3 회 · 5 s 휠 오도 변화 | (미기록) | — | `job149_hardstop.sh` |
| | **복구**: `pkill -TERM -f "ros2 launch"` + 노드별 TERM → 최대 12 s 대기 → 남은 것만 `-9` → **agent 컨테이너 삭제** · `ros2 daemon stop` → `rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_*` | 정리 전 fastrtps 파일 15 개 삭제(SUMMARY '15개') | 'SIGKILL 이 원인' | `job150_recover.sh` |
| | 복구 확인 | `/odometry/filtered` 퍼블리셔 1 · **30.007 Hz**, `/tf` 퍼블리셔 4 · **47.4 Hz**, `/map` 퍼블리셔 1 · **0.500 Hz**. 보드는 '없음 — RESET 필요'(agent 를 지웠으므로) | 복구 | `job151_check.sh` |
| §8.9 재발 방지 | 정리 = `pkill -TERM` → 최대 15 s → 남은 것만 `-9` | `job154_reinit.sh` · `job156_stop.sh` 는 SIGTERM 만으로 잔존 0 | — | `job154_reinit.sh` · `job156_stop.sh`(둘 다 끝에 `rm -f /dev/shm/fastrtps_*`) |
| §8.11 | STVL 배포 + 스택 전체 재기동: 노드 TERM → **고정 8 s** → agent 삭제 → `rm -f /dev/shm/fastrtps_*` → base → sensors → slam → nav2 | 기동 성공(보드는 RESET 필요 상태) | — | `job164_stvlup.sh` |
| §8.13~§8.14 | `job170` 주행 → t ≈ 4.0 부터 위치 고정 → 9.90 s 뒤 조회 실패 | (→ [CPU 카드](cpu-load-stalls.md)) | 처음엔 '배터리' → 정정 'map→base_link 갱신 정지' | `job125_avoid3.py`(run 이름 job170) · `job171_chk.sh` · `job172_freeze.sh` |
| §8.15 | slam 프로세스 · 노드 · CPU · 발행 여부 · map→odom 조회 · **고아 찾기**(이름이 `fastrtps_portN` 인데 본체 없고 `N_el` 만 있는 것) · slam 로그 끝 | slam 프로세스 살아 있음, `/map` 퍼블리셔 0, 고아 **`fastrtps_port7425`** | **2 회차** — 'SIGTERM 으로 바꿨는데도 재발 → SHM 전송 자체가 문제' | `job173_slam.sh` |
| §8.15 조치 | `fastdds_udp_only.xml` + 4 개 launch 배포 → 전체 TERM(최대 15 s) → agent 삭제 · daemon stop · SHM 삭제 → 재기동 → 검증 | SHM 재생성 **0 개**, `RTPS_TRANSPORT_SHM` 오류 sensors · slam · nav2 각 **0 건**, `/tf` **45.5 Hz**(퍼블리셔 3 = ekf + slam + RSP), `/map` **0.5 Hz**, slam 복귀 | 이 실패 유형 제거 | `job174_dds.sh` |
| §8.15 검증 | 프로세스 환경변수로 프로파일 적용 확인 · slam 상세 | slam · ekf · conditioner · rplidar · realsense · controller 전부 `FASTRTPS_DEFAULT_PROFILES_FILE` 적용 | — | `job176_who.sh` · `job177_env.sh` |
| §8.16 | UDP 전용 **뒤에도** `job175` 에서 같은 정지(SHM 오류 0) | EKF 위반 91 회 · load 9.01 | 다른 원인 = CPU 부족(→ [CPU 카드](cpu-load-stalls.md)) | `job177_env.sh` |
| §8.16 내 오류 2 | `ros2 topic info /tf --verbose` 노드 목록 → 'slam_toolbox **중복**' → 정리 · 재기동 | 그 출력은 발행자와 구독자를 함께 나열 | **판단 취소**(중복 아님, §5.3) | `job180_imuparam.sh` → `job181_dedup.sh` |
| 09-11 §5.4 | 사용자 "너가 설정을 깔끔하게 초기화하지 못해서, 재부팅했다" → 기동 절차 고정 | — | `job240_clean.sh` 제정(정리 · 기동 순서 · 검증 · 클리어 · 재마킹 대기) | `job240_clean.sh` |
| 09-11 §5.9 | 사용자 "중첩된 프로세스가 있어 충돌이 일어나지 않게" → nav2 만 재기동하며 전 스택 중복 감사 | **`robot_state_publisher` 2 개**(3054 / 5769) | 이전 기동의 자식이 launch 종료 때 안 죽고 고아로 남음 | `job249_nav2only.sh` |
| | RSP 프로세스 · 그래프 이름 수 · `/tf_static` 발행자 GID → 1 개일 때만 주행 | (프로세스 수 미기록) | 스크립트 문구: '그래프 중복은 DDS 잔상(UDP 참가자 lease 만료 대기)으로 판단' — 프로세스 2 개였다면 이 경로는 중단으로 끝남 | `job250_rsp_then_drive.sh` |
| | 현재 `base.launch` 의 자식 PID 를 `/tmp/base.log` 에서 찾고 나머지 RSP 를 TERM → 3 s → KILL → 1 개 확인 → 전 스택 재감사 → 주행 job251 | 1 개 확인 후 주행 | 고아 제거, `job240_clean.sh` 에 반영(§6 모순 3) | `job252_fix_then_drive.sh` |
| 10-12 §8.2 | (통신 포화 조사의 일부 — 본문은 [통신 포화 카드](network-saturation-mppi-viz.md)) 커널 UDP 통계 · 소켓별 손실 | `rmem_default 212992 rmem_max 212992`, 부팅 뒤 `InDatagrams=133271653` 중 `RcvbufErrors=8592442`(6.4 %), `/trajectories` 1 개 206 kB ≈ 버퍼 한 개 | 'UDP 전용(09-09 결정)이라 큰 메시지가 같은 소켓의 `/tf` 를 밀어낸다'(**추정**) — SHM 재검토의 계기 | [`j967_net.txt`](../debug_log/2026-10-12/outputs/j967_net.txt) · [`job967_net.sh`](../debug_log/2026-10-12/jobs/job967_net.sh) |
| 10-12 §8.3 | 사용자 "공유메모리 방식을 다시 사용하는 건 어떤가" → 사실 확인 | nvblox 컨테이너 `ipc host · net host`, 에이전트 `ipc private · net host`, 호스트 Fast DDS `2.6.12-1jammy…`, 컨테이너 안 프로파일 '없음', 호스트 `/dev/shm` 3.8G 중 84K · fastrtps 잔류 0 | **'지금은 바꾸지 않는다'**: ① 수신 버퍼 원인은 추정 ② 같은 가설을 더 작은 변경(rmem 상향 · `lite`)으로 시험 가능 ③ SHM 은 그 뒤 단계, 그때 `fastdds shm clean` + 발행자 존재 게이트. ✘ 질문을 DDS SHM 으로 오독(§8.4, §5.5) | [`j968_shm.txt`](../debug_log/2026-10-12/outputs/j968_shm.txt) · [`job968_shm.sh`](../debug_log/2026-10-12/jobs/job968_shm.sh)(§9.16) |
| 10-12 §8.4 | 사용자 정정 "DDS 공유메모리가 아니라 **Jetson 보드 고유의 공유메모리**(CPU·GPU 통합 메모리)" | (측정 없음) | 통합 메모리는 **한 프로세스 안**의 CPU↔GPU 복사를 줄인다 — 오늘 병목(프로세스 사이 DDS 전달)에는 직접 안 닿음. 프로세스 사이에 같은 취지 = 노드 합치기(composition, Nav2 `use_composition`) · DDS SHM. nvblox 3.2.5 가 깊이를 NITROS 로 받는지 **미확인**. 중기 후보 'Nav2 합치기' 기록 | SUMMARY 문장(지식 기반) |
| 10-12 §8.5 | 사용자 제안 "영상·라이다 같은 대용량은 SHM 제로카피로, 문제 생기는 부분은 UDP 로" | (측정 없음) | Fast DDS 전송은 토픽별이 아니라 **프로세스(참여자)별** → '프로세스를 골라' 섞기는 가능. 가변 길이 표준 메시지(Image · PointCloud2 · LaserScan)는 Humble 대여(loan) 대상이 아니라 SHM 이면 'UDP 경로(커널 버퍼 · 64 kB 조각)를 건너뜀' 까지. 후보 = realsense(와 depth_relay)만 SHM, 재기동 잦은 Nav2 · 09-09 에 죽었던 ekf · slam 은 UDP. 게이트 J(nvblox 깊이 ≥ 10 Hz)가 조용한 실패를 잡음. 판단: 구조는 타당, 원인 확정 뒤 '카메라 → nvblox 만 SHM' A/B. ⚠ '깊이 약 614 kB × 15 Hz ≈ 9 MB/s(계산값)' 와 그로부터의 '크기만의 문제가 아닐 수 있다' 는 **틀린 전제**(§5.6) | SUMMARY 문장 |
| 10-12 §8.6 | 사용자 "DDS 로 공유메모리 통신이 되면 하는 게 맞다. micro-ROS 때문에 문제가 생기나?" | (측정 없음) | **micro-ROS 는 원인 아님**: 에이전트는 `MICROROS_DISABLE_SHM=1` · `ipc private` → SHM+UDP 프로세스와도 UDP 로 만남, 09-09 두 사고에서 보드 토픽만 멀쩡. 에이전트는 계속 SHM 끔. 진행안 ① SHM + UDP 프로파일('루프백 고정 유지' — ✘ 지금 UDP 프로파일엔 루프백 고정이 없음, §6 모순 5) ② `fastdds shm clean` · 기동 로그 `Failed init_port` · `RTPS_TRANSPORT_SHM Error` 면 prep 불합격 · 발행자 확인 ③ 정지 시험(Nav2 재시작 5 회 고아 재발) ④ 주행 A/B | SUMMARY 문장 |
| 10-12 §17 | 마무리 뒤 사용자 "UDP 버퍼는 늘렸나? 늘리면 CPU 문제? 메시지 전달은 DDS SHM 을 이용하고 싶다" | 수신 버퍼 **안 늘림**(208 kB 그대로) — 그날 해결은 궤적을 206 → 28 kB(`lite`)로 줄여 피한 것 | (지식 기반, 측정 아님) 버퍼 크기 자체는 CPU 를 안 씀, 받는 쪽이 계속 느리면 버려질 것이 줄 서서 늦게 처리될 뿐(좌표 변환엔 '늦은 옛 값' 이 더 나쁠 수 있음), UDP 소켓 ≈ 180 개(참여자 ≈ 45 × 4 — **추정**)라 26 MB 면 최악 수 GB → 넣더라도 4~8 MB. **사용자 결정: 프로세스 간 전달은 DDS SHM** — §8.6 진행안을 다음 세션 첫 작업으로, 세그먼트 크기 지정(궤적 206 kB · 깊이 614 kB ✘ §5.6) | SUMMARY 문장 |
| 10-12 §18 | 사용자 "DDS 는 zero-copy 를 지원하고 이미지·점군도 된다던데 왜 한 번은 복사해야 한다고 했나" → 웹 문서 확인 | Fast DDS zero-copy = 데이터 공유 전달 + loan, 조건 **plain · 크기 고정 타입**(eProsima 문서 15.8). `sensor_msgs/Image` · `PointCloud2` 는 `data` 가 가변 길이라 대상 아님(ROS Discourse · ros2_shm_msgs 안내) | 앞 표현 정정: 표준 타입을 SHM 으로 보내면 **보내는 쪽 직렬화 1 + 받는 쪽 역직렬화 1** 이 남음. 이미지·점군 zero-copy 가 되는 경우 = ① 고정 타입 + loan API ② 같은 프로세스 ③ NITROS. Humble 에서 `borrow_loaned_message()` 시험 안 함 | SUMMARY §18 출처 4 개(URL) |
| 10-12 §19 | 사용자 "현재 구성에서 크기 고정 타입으로 바꾸는 건 좋지 못한가" | 계산: 깊이 640×480×16 bit = 614 kB × 15 Hz ≈ 9 MB/s → 없앨 복사 ≈ 18 MB/s ≈ CPU 1 % 미만(**추정**). ✘ 입력값 틀림 — 실제 발행 깊이 38 kB(§5.6), 이득은 더 작음 | 본 경로엔 **권하지 않음**: ① 포화를 낸 `MarkerArray` · `TFMessage` 는 고정 타입이 될 수 없음 ② realsense · nvblox · Nav2 포크 필요, 변환 노드는 복사 2 번 ③ 이득 작음 ④ bag · Foxglove · RViz 호환 상실 ⑤ Humble loan 덮어쓰기 사용자 보고(미검증). 따로 떨어진 벤치마크로는 가능 | SUMMARY 문장(계산 · 지식 기반) |
| 10-12 §21 | 사용자 "공유메모리 방식이었다면, BT 가 요청을 쏟아내는 것이 원인일 때 밝히기 어려웠을까" | f2g2 Nav2 로그 포화 전 → 후(분당): smoother 'Received a path to smooth' 27.6 → 17.6 · 'Passing new path' 25.1 → 14.1 · 'Received a goal' 2.4 → 6.2 · 코스트맵 비우기 0 → 4.4 · 4.0 · 서버 응답 시간 초과 0 → 7.5. 계산 스크립트 · 출력 **원천 소실** — 카드 작성 중 재계산(§9.17): 같은 경향, 값은 창 · 패턴 차이로 다름 | 통신 쪽 관찰(커널 UDP 통계 · 소켓 손실 · 캡처)은 SHM 에서 어려워짐 — SHM 대기열 넘침은 커널 통계에 안 잡힘. 'BT 요청 수' 자체는 전송과 무관하게 Nav2 로그로 셀 수 있음. 요청은 분당 수십이라 초당 5 만 증가를 설명 못 함 → (나) 'BT 요청 폭주' **약함**, 늘어난 것은 DDS 아래 층(재전송 · 확인 · 생존 신호)일 가능성(**추정**) | [`nav2_f2g2.log.gz`](../debug_log/2026-10-12/outputs/nav2_f2g2.log.gz) · [`f2g2_navlog.txt`](../debug_log/2026-10-12/outputs/f2g2_navlog.txt) |
| 10-12 §22 | 사용자 "캡처 한 번 하고 넘어가자" | — | 다음 세션 순서: ① 포화 재현 + 루프백 캡처 → ② DDS SHM 도입(§17 진행안) → 나머지 | SUMMARY 문장 |
| 10-13 §1.2 · §2 · §15 | (통신 포화 카드) 캡처 → `/tf` 쓰는 쪽 HEARTBEAT 폭주, 가장 먼저 뒤처진 읽는 쪽 = bag 기록기 → 기록기 `/tf` best effort 에서 포화 없음(1 회) | 수치는 [통신 포화 카드](network-saturation-mppi-viz.md) | §1.2 '공유메모리 도입에 주는 뜻': 소켓 넘침으로 `/tf` 가 버려지는 것은 없어지나(**추정**) '느린 reliable 구독자 하나가 쓰는 쪽 보관함을 붙잡는' 구조는 전송 방식과 무관 → 도입 뒤 검증은 HEARTBEAT 수 · 읽는 쪽 뒤처짐으로. §15 '다음에 할 것' 에 SHM 도입 **없음**, 보류 결정 문장도 없음 | [10-13 SUMMARY](../debug_log/2026-10-13/SUMMARY.md) |
| 10-13 §0 · 10-14 · 10-15 | — | `rmem_max 212,992`(10-13 §0 `chk_jetson_state.sh`). 10-14 · 10-15 SUMMARY 에 SHM · 수신 버퍼 작업 기록 없음(카드 작성 중 grep) | 수신 버퍼는 끝까지 안 늘림 · SHM 은 7 기에 미실행 | [`chk_jetson_state.sh`](../tools/chk_jetson_state.sh) 8 행 |
| 이후(10-19 ~) | **다음 시기에서 채움** — 아래 10-20 · 10-23 행은 카드 첫 판(2 기)에서 미리 적은 요약이다. 메모리 '10-20 재점검: SHM 자체가 원인이라는 것은 과한 일반화' 를 그 시기 원문(10-20 §7.1~§7.5 · §9.5, 10-23 §16)과 대조해 다시 채운다 | — | — | — |
| 10-20 §7.2 | 사용자 질문 "실행 종료 방식이 문제인지, 통신 방식이 문제인지" → 09-09 기록 · jobs 재독 | 1 회차 = 종료 방식(pkill −9) 맞음. 2 회차 전 job156 · 164 · 174 가 **살아 있을 수 있는 참가자 파일까지 `rm -f`**, launch 의 SIGKILL 단계 미확인, CPU 정지와 섞임 | **'SHM 자체' 는 과한 일반화** — 확인된 것은 '비정상 종료 · 잔재 강제 삭제 시 깨진다' 까지 | [10-20 SUMMARY §7.2](../debug_log/2026-10-20/SUMMARY.md) |
| 10-20 §7.3a~c | SHM+UDP 프로파일, 호스트 발행 → 컨테이너 구독 640×480 15 Hz, 종료를 INT · TERM · KILL 돌림 | 팔 A(정리 없음) **15/15**, 팔 B(`fastdds shm clean` 뒤) **30/30**, SHM 오류 0. 호스트 ↔ 컨테이너 SHM 통함(SHM 전용 V1) | 09-09 실패는 이 버전 · 규모에선 재현 안 됨 — `rm -f` 가 더 유력(**추정**) | 10-20 `outputs/run_shm_test.txt` · `run_shm_test_shmonly.txt` · `chk_shm_path.txt` |
| 10-20 §9.5 | 실제 스택(카메라 ↔ cuVSLAM 만 SHM) prep 10 회 + 카메라 · nvblox · cuVSLAM −9 섞음 | **10/10**: `/vslam/odom` 15 Hz · nvblox 깊이 15.1 Hz · SHM 오류 0 · −9 뒤 다음 prep 에서 정상 복귀 | 합격 | 10-20 `outputs/run_shm_restart.txt` |
| 10-23 §16 | 운용 기본 `prep_patrol.sh` 에 `dds_shm:=true`(카메라 ↔ cuVSLAM) | — | 사용자 결정(cuVSLAM 오도메트리 채택과 함께) | [10-23 SUMMARY](../debug_log/2026-10-23/SUMMARY.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| SLAM 정합 실패 | job144 TF · 맵 범위 | (그때 '어긋났다') → SLAM 은 입력 TF 자체를 못 받았다 | **기각**(§8.9 참고 문단) |
| 보드 오도가 헛돌았다(x 1.614 vs map) | 기준 비교 | 보드 오도는 보드 리셋 이후 누적, map 좌표는 `job123_reinit` 이후 상대 — 기준이 다름 | **기각**(비교 자체가 무효) |
| 시각 동기 · stamp 튐 → EKF 가 메시지를 '과거' 로 버림 | job147 오프셋 · 역행 | −0.002~−0.032 s · 역행 0 | **기각** |
| EKF 프로세스가 죽었다 | job145 · 146 | 살아 있음, CPU 20 % | **기각** |
| SHM 고아 잠금 파일 때문에 퍼블리셔가 등록 못 됨 | job148 파일 · 로그, job150 정리 → job151 | 본체 없는 `_el`, `open_and_lock_file failed` → 정리 뒤 퍼블리셔 복귀 | **지지**(1 회차) |
| 1 회차 원인 = SIGKILL | 그날 `pkill -9` 13 개 job | 정리를 TERM 으로 바꾼 job154 · 156 은 잔존 0 | **지지**(10-20 도 같은 판정). 기전('SIGKILL 이면 FastDDS 가 파일을 못 치움')은 일반 동작 설명 — 이 장비에서 −9 로 재현한 시험은 09-09 엔 없음 |
| 2 회차 원인 = SHM 전송 자체(종료 방식 무관) | 'TERM 으로 바꿨는데도 재발' | 10-20 재독: 사이에 `rm -f /dev/shm/fastrtps_*`(job156 · 164 · 174)가 살아 있는 참가자(ros2 데몬 · ssh 의 ros2 CLI = 프로파일 없는 SHM 참가자) 파일을 지웠을 수 있음, launch 가 느린 자식에 SIGKILL 을 보냈을 수 있음, 2 회차 서술엔 SHM 오류 줄 인용이 없음 | **근거 약함 → 정정**(10-20 §7.2). 10-20 시험에서 정리 없이 −9 를 섞어도 15/15 정상 → '종료 방식을 고쳐도 SHM 이 깨진다' 는 재현 안 됨 |
| UDP 전용이면 이 유형은 안 난다 | job174 검증 · 이후 운용 | SHM 파일 재생성 0 · 오류 0, 이후 같은 서명 기록 없음 | **지지**(증상 소거) |
| UDP 전용 뒤의 정지도 SHM 탓 | job175 · job177 | SHM 오류 0, EKF 위반 91 회 | **기각** → CPU([CPU 카드](cpu-load-stalls.md)) |
| slam_toolbox 가 중복 실행 중 | job180 `/tf --verbose` 노드 목록 | 발행자 + 구독자 함께 나열한 것 | **기각**(오독, §5.3) |
| `robot_state_publisher` 그래프 중복 = DDS 잔상(lease 만료 대기) | job250 의 판단 문구 → job252 프로세스 PID 비교 | 실제 프로세스 2 개(고아) | 잔상 가설 **기각**(09-11 §5.9) |
| (10-12) 통신 포화의 원인 = UDP 수신 버퍼(208 kB) → SHM 이면 사라진다 | §8.2 누적 손실 · 메시지 크기, 10-13 캡처 · f2n1 | 10-13: 시작점은 기록기의 reliable `/tf` 뒤처짐 → HEARTBEAT 폭주. 버퍼 넘침은 유지 기전의 일부. 기록기 QoS 만 바꿔 포화 0/1 | **부분 지지 · 미시험** — SHM 으로는 시험하지 않음(7 기 미실행). '느린 구독자' 구조는 SHM 에서도 남음(10-13 §1.2, 추정) |
| (10-12 §8.6) micro-ROS 에이전트 때문에 호스트가 SHM 을 못 쓴다 | 에이전트 설정 · 09-09 기록 | 에이전트 `MICROROS_DISABLE_SHM=1` · `ipc private`, SHM+UDP 와 UDP 전용 참가자는 UDP 로 만남, 09-09 두 사고에서 보드 토픽만 정상 | **기각**(설정 · 문서 근거. 10-20 혼합 운용에서 보드 토픽 정상은 그 시기 카드에서 확인) |
| (10-12 §8.5 · §18) SHM 이면 이미지 · 점군도 zero-copy | 문서 확인(§18) | 가변 길이 `data` → loan 대상 아님. SHM 전송은 직렬화 · 역직렬화 각 1 회가 남고 UDP 경로만 건너뜀 | **기각**(문서 근거, Humble 직접 시험 없음) |
| (10-12 §20 (나)) 포화 = BT 의 액션 · 서비스 요청 폭주 | f2g2 Nav2 로그 분당 줄 수(§21) | 요청은 분당 수십, 일부는 포화 뒤 줄어듦. 초당 5 만 증가와 자릿수가 안 맞음 | **약함**(§21). 10-13 캡처가 `/tf` HEARTBEAT 으로 확정 쪽 근거(통신 포화 카드) |

## 4. 조치와 효과
- **정리 규칙**(09-09 §8.9): `pkill -TERM` → 최대 15 s 대기 → 남은 것만 `-9`. `job154` · `job156` · `job174` · `job178` 부터 적용. ⚠ 같은 스크립트들이 끝에 `rm -f /dev/shm/fastrtps_*` 를 함께 했다 — 10-20 이 지목한 '잔재 강제 삭제'(지금은 금지: 10-20 이후 prep 은 `fastdds shm clean`, 아무도 안 잡은 고아만).
- **UDP 전용 프로파일**(09-09 §8.15, `config/fastdds_udp_only.xml`): `UDPv4` transport 하나를 정의하고 기본 participant 프로파일(`is_default_profile="true"`)에서 `useBuiltinTransports=false` → 기본 전송(SHM 포함)을 끈다. 각 launch 의 `SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', <설치본 XML>)` 로 그 launch 의 모든 자식에 적용. 비용 주석: 같은 호스트 통신이 UDP 루프백을 탄다 — 작은 메시지 위주라 감당(가장 큰 점군 15 Hz × 수백 kB).
  - 효과: SHM 오류 0, 이후 '살아 있는데 사라지는 노드' 기록 없음.
  - 한계(메모리 · 10-20): ssh 로 띄운 진단 스크립트 · `ros2` CLI 는 이 환경변수가 없어 여전히 SHM 참가자를 만든다(통신은 UDP 로 협상돼 문제 없음). 10-20 §7.2 측정: 그날도 `/dev/shm` 에 FastDDS 파일 16 개가 생겨 있었다(프로파일 없이 뜬 무언가의 잔재 **추정**).
- **중복 감사**(09-11 §5.9): `job249_nav2only.sh` · `job252_fix_then_drive.sh` 가 14 개 이름 각각 `pgrep -fc` = 1 인지, `ros2 node list | sort | uniq -d`, `/tf` 발행 노드별 수를 찍고 하나라도 아니면 '주행 금지' 로 끝낸다. `job240_clean.sh` 는 기동 전 정리 + `robot_state_publisher` 개수 표시.
- 이후(09-16): Wi-Fi 전환으로 IP 가 바뀌면 이미 뜬 참가자가 옛 IP 를 광고하는 문제로 XML 에 루프백 화이트리스트를 넣었다가, agent 컨테이너가 같은 화이트리스트를 안 써 `/wheel_odom` 0 이 되어 되돌림(job359/360). agent 에도 같은 XML 을 마운트(`base.launch.py` `-v … -e FASTRTPS_DEFAULT_PROFILES_FILE=…`). 상세는 Wi-Fi · DDS 카드(예정) — [Jetson Wi-Fi](jetson-wifi-link.md).
- **10-12 결정과 그 뒤**(7 기): 바꾼 파일 없음. §8.3 '지금은 안 바꿈' → §17 사용자 결정 'DDS SHM 으로'(다음 세션 첫 작업) → §22 '캡처 먼저' → 10-13 캡처 · 기록기 `/tf` best effort 로 포화가 막히자 SHM 은 '다음에 할 것' 에서 빠짐(10-13 §15) → 10-15 까지 미실행. 수신 버퍼(`net.core.rmem_max`)도 sudo 필요 · 사용자 결정 사항으로 남은 채 **안 늘림** — 저장소에 sysctl 설정 파일은 없고 `Docs/tools/chk_jetson_state.sh` 8 행이 값을 찍기만 한다(카드 작성 중 확인). 10-20 의 SHM+UDP 프로파일 주석(`fastdds_shm_udp.xml` 5~7 행)은 'rmem_max 상향(sudo) 대신 이 길을 택함' 이라 적는다.
- 이후(10-20 · 10-23): SHM+UDP 프로파일 `fastdds_shm_udp.xml`(세그먼트: 카메라 8 MB, cuVSLAM 4 MB)을 **카메라 프로세스 · cuVSLAM 컨테이너에만**(`camera.launch.py dds_shm:=`, `ekf.launch.py dds_shm:=` → `cuvslam_up.sh`) — 나머지는 UDP 그대로. 근거: 깊이(데시메이션 ×4 = 38 kB)는 UDP 로 15 Hz 문제없고, IR 307 kB × 2 가 소켓 버퍼(212 992 B)보다 커서 UDP 에서 빠짐(10-20 §7.5). 10-23 부터 prep 기본.

## 5. 내 실수
### 5.1 `pkill -9` 반복 — 정리를 '확실히' 하려던 것이 정리를 못 하게 함
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 하루에 Nav2 · 센서를 수십 번 재기동하며 매번 잔존 프로세스 없이 깨끗하게(오전의 ERE 패턴 결함을 고친 뒤 '확실히' 죽이려고 `-9`) |
| 본 것 | 이상 주행 → `/odometry/filtered` 퍼블리셔 0 인데 ekf_node CPU 20 % · 입력 정상, `open_and_lock_file failed`, `_el` 만 남은 7423 |
| 처음 추론 | 차례로: SLAM 정합 실패(job144) → EKF 입력 문제(job146) → 시각 동기(job147) — 전부 '노드 내부 계산' 쪽을 의심 |
| 의심한 이유 | 입력 정상 · 시각 정상 · 프로세스 정상인데 출력만 그래프에 없음 = 계산이 아니라 **통신 등록** 문제. `job145` 의 `/dev/shm` 파일 수가 단서 |
| 판별 | `job148`: 포트 파일 본체 없음 · 잠금 파일 있음 · FastDDS SHM 오류 로그 → `job150`(TERM + 잔재 삭제) → `job151` 퍼블리셔 · 주기 복귀 |
| 결론 | SIGKILL 은 FastDDS 가 SHM 세그먼트 · 잠금 파일을 치울 기회를 없앤다. 13 개 job 의 `-9` 가 원인 |
| 다음에 알아보는 법 | 서명: **프로세스는 살아 CPU 를 쓰는데 그 노드의 퍼블리셔 수가 0**(노드 목록에서도 빠짐) + `RTPS_TRANSPORT_SHM Error … open_and_lock_file failed`. 확인 순서: `ros2 topic info <토픽>` 퍼블리셔 수 → 로그의 SHM 오류 → `ls /dev/shm \| grep fastrtps`(본체 없는 `_el`). 정리는 TERM → 대기 → 남은 것만 KILL, 잔재는 `fastdds shm clean`(아무도 안 잡은 것만) — `rm -f` 금지 |
| 데이터 | SUMMARY §8.9, 도구 `job144`~`job151`, 원문 없음(**원천 소실**). 재평가 [10-20 §7.2](../debug_log/2026-10-20/SUMMARY.md) |

### 5.2 'SLAM 정합이 어긋났다' · '보드 오도 대비 헛돌았다'
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 보고("지도를 벗어나 이상하게 움직인다")의 원인을 TF · 지도에서 찾기(`job144_slam.sh`) |
| 본 것 | map 좌표가 실제와 어긋남, 보드 `/wheel_odom` x = 1.614 |
| 처음 추론 | SLAM 이 정합에 실패했다 / 보드 오도에 비해 로버가 헛돌았다 |
| 의심한 이유 | SHM 서명이 나온 뒤 보니 EKF 가 TF 를 못 내고 있었다 — SLAM 은 입력 TF 를 받지 못한 상태였다. 보드 x 는 시작점이 다른 값 |
| 판별 | (논리) 보드 오도 = 보드 리셋 이후 누적, map 좌표 = `job123_reinit` 이후 상대 → 같은 축에서 뺄 수 없다 |
| 결론 | 두 진단 모두 철회(§8.9 '참고' 문단) |
| 다음에 알아보는 법 | 두 좌표를 비교하기 전에 **원점이 같은가**(언제 0 이 됐나)를 먼저 적는다. 'SLAM 이상' 을 말하기 전에 SLAM 의 입력(scan · odom→base TF)이 오고 있는지 본다 |
| 데이터 | SUMMARY §8.9 마지막 인용 문단, `jobs/job144_slam.sh` |

### 5.3 `ros2 topic info /tf --verbose` 를 '중복 노드' 로 오독
| 칸 | 내용 |
|---|---|
| 하려 한 것 | CPU 부족 정지 뒤 중복 프로세스 확인(`job180_imuparam.sh` 끝의 `/tf` 발행 주체 집계) |
| 본 것 | `Node name` 줄을 `sort \| uniq -c` 한 결과에 slam_toolbox 가 두 번 |
| 처음 추론 | slam_toolbox 가 두 개 떠 있다 → `job181_dedup.sh` 로 정리 · 재기동 |
| 의심한 이유 | job181 의 `pgrep -fc slam_toolbox` = 1(프로세스는 하나) |
| 판별 | `--verbose` 출력은 **발행자 블록과 구독자 블록을 함께** 나열한다. slam 은 `/tf` 를 발행(map→odom)하면서 구독(odom→base 조회)도 한다 |
| 결론 | 중복 아님, 판단 취소(SUMMARY §8.16 '내가 낸 오류 2건' 둘째) |
| 다음에 알아보는 법 | `--verbose` 를 셀 땐 'Publisher count' 아래 블록만 자른다(09-11 job249 는 여전히 `Node name` 전체를 센다 — 같은 함정이 남아 있음). 중복 판정은 프로세스(`pgrep -fa`)와 그래프 이름(`ros2 node list \| uniq -d`) 둘로 |
| 데이터 | SUMMARY §8.16, `jobs/job180_imuparam.sh` · `job181_dedup.sh` |

### 5.4 '종료 방식을 고쳤는데도 재발 → SHM 자체가 원인' (10-20 정정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 2 회차(slam_toolbox) 뒤 재발 방지 대책 결정 |
| 본 것 | 고아 `fastrtps_port7425`, `/map` 퍼블리셔 0, 그 사이 정리 스크립트들은 SIGTERM 판 |
| 처음 추론 | 종료 방식은 이미 고쳤다 → 개발 중 포트 churn 은 못 피한다 → SHM 을 쓰는 것 자체가 문제 → 끈다. 메모리 · XML 주석 · 커밋에 '원인 제거' 로 기록 |
| 의심한 이유 | 10-20 사용자 질문("종료 방식이 문제인지, 통신 방식이 문제인지") — SHM 을 cuVSLAM 경로에 다시 켤지 결정해야 했다 |
| 판별 | 기록 재독: ① job156 · 164 · 174 가 TERM 뒤 고정 대기 후 확인 없이 `rm -f /dev/shm/fastrtps_*`(살아 있는 ros2 데몬 · ssh CLI 의 파일까지) ② launch 는 느린 자식에 SIGINT → SIGTERM → SIGKILL 로 올린다 — 그날 launch 로그가 없어 확인 불가 ③ 2 회차엔 SHM 오류 줄 인용이 없음, 같은 날 CPU 정지와 섞임. 측정: 정리 없이 −9 섞은 15/15, `fastdds shm clean` 30/30, 실제 스택 10/10 |
| 결론 | 'SHM 자체' 는 과한 일반화. 확인된 것: 비정상 종료 · 잔재 강제 삭제가 있으면 깨진다. UDP 전용 유지는 견고성 선택으로 여전히 합리적(prep 도 TERM 15 s 뒤 −9 단계가 있음) |
| 다음에 알아보는 법 | '고쳤는데 재발' 이라고 쓰기 전에 **그 사이에 다른 개입(파일 삭제 · 강제 종료 단계)이 있었는지** 스크립트를 다시 읽는다. 원인 판정은 '그 조건만 바꾼 재현 시험' 으로 — 이 경우 −9 를 섞은 재기동 반복 |
| 데이터 | [10-20 §7.2 · §7.3a~c · §9.5](../debug_log/2026-10-20/SUMMARY.md), 10-20 `outputs/run_shm_test.txt` · `run_shm_restart.txt`, 09-09 `jobs/job156_stop.sh` · `job164_stvlup.sh` · `job174_dds.sh` |

### 5.5 '공유메모리' 질문을 DDS SHM 으로 오독(10-12 §8.3 → §8.4)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 질문 "공유메모리 방식을 다시 사용하는 건 어떤가" 에 답하기(`job968_shm.sh` 로 컨테이너 ipc · Fast DDS 판 확인) |
| 본 것 | 그날 맥락이 'UDP 수신 버퍼 손실'(§8.2)이고, 09-09 에 끈 것이 DDS SHM 이었다 |
| 처음 추론 | '공유메모리' = 09-09 에 끈 FastDDS SHM 전송 → 고아 위험 · 원인 미확정을 들어 '지금은 바꾸지 않는다' |
| 의심한 이유 | 사용자 정정(§8.4): "DDS 공유메모리가 아니라, Jetson 보드 고유의 공유메모리(CPU·GPU 통합 메모리)" |
| 판별 시험 | (없음 — 질문의 뜻 확인) |
| 결론 | 내 오독. §8.3 내용은 DDS SHM 주제로는 유효. 통합 메모리는 프로세스 안 CPU↔GPU 복사 문제라 그날 병목(프로세스 사이)엔 직접 안 닿음(§8.4, 지식 기반). SUMMARY §14 '기각 · 정정한 내 판단' 에 '공유메모리 질문 오독(§8.3)' 로 기록 |
| 다음에 알아보는 법 | 같은 낱말이 두 층(DDS 전송 · 하드웨어 메모리)에 있으면 답하기 전에 어느 층인지 되묻거나 둘 다 짧게 구분해 답한다 |
| 스크립트 핵심 | `docker inspect --format '{{.HostConfig.IpcMode}}' $c` · `dpkg -l \| grep -a 'ros-humble-fastrtps '` · `docker exec … 'echo ${FASTRTPS_DEFAULT_PROFILES_FILE:-없음}; ls /dev/shm \| wc -l'` ([`job968_shm.sh`](../debug_log/2026-10-12/jobs/job968_shm.sh)) |
| 나온 결과 | `isaac_ros_dev-aarch64-container: ipc host · net host` · `microros_agent: ipc private · net host` · `호스트 Fast DDS: 2.6.12-1jammy.20260725.060440` · `컨테이너 안 프로파일: 없음 43` · `호스트 /dev/shm: 3.8G 중 84K 사용 · fastrtps 잔류 파일 0` ([`j968_shm.txt`](../debug_log/2026-10-12/outputs/j968_shm.txt)) |
| 데이터 | 10-12 SUMMARY §8.3 · §8.4 · §14 |

### 5.6 '깊이 영상 614 kB × 15 Hz ≈ 9 MB/s' — 해상도를 확인하지 않은 계산값(10-12 §8.5 · §17 · §19, 10-20 §7.5 정정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | SHM 으로 옮길 대용량 흐름과 크기 고정 타입의 이득을 어림(§8.5 · §19), 세그먼트 크기 정하기(§17) |
| 본 것 | (측정 없음) 카메라 깊이 해상도를 640×480 으로 놓고 640×480×2 B = 614 kB 로 계산 |
| 처음 추론 | §8.5 '깊이 9 MB/s 가 이미 같은 UDP 로 문제없이 15 Hz 로 들어가는 점은 크기만의 문제가 아닐 수 있음' · §17 세그먼트 '깊이 영상 614 kB' · §19 '없앨 복사 18 MB/s ≈ CPU 1 % 미만' |
| 의심한 이유 | (7 기에는 의심 안 함) 10-20 §7.5 사용자 질문 "해상도를 낮춰서 UDP 대역폭에 적절하기 때문인지 검증" 으로 bag 을 재 봄 |
| 판별 시험 | 10-20 §7.5: f2z1 bag 실측 — 깊이는 데시메이션 ×4(09-08 N1.5 `decimation_filter.filter_magnitude: 4`)로 **160×120 16UC1, 직렬화 38 472 B** |
| 결론 | 614 kB 는 틀림. §8.5 의 '크기만의 문제가 아닐 수 있다' 는 정반대 — 깊이가 빠지지 않은 이유가 바로 작은 크기(10-20 §7.5: 307 kB 1 % · 614 kB 6~11 % 빠짐). §19 의 '이득 작음' 결론은 입력이 더 작아지므로 그대로 성립 |
| 다음에 알아보는 법 | 메시지 크기는 계산하지 말고 bag `metadata.yaml`(크기/개수)이나 `ros2 topic bw` · `camera_info` 의 width · height 로 먼저 잰다. 카메라 설정에 데시메이션 · 정렬이 끼어 있는지 launch 인자를 본다 |
| 스크립트 핵심 | (계산은 SUMMARY 문장뿐 — 원문 없음 — 발췌가 전부) §19 '깊이 영상 640×480×16 bit = 614 kB, 15 Hz → 약 9 MB/s' |
| 나온 결과 | 10-20 §7.5: '실제 발행 깊이는 데시메이션 ×4 로 160×120 16UC1, 직렬화 38 472 B(f2z1 bag 실측; camera_info 도 160×120, fx 98.3)' |
| 데이터 | 10-12 SUMMARY §8.5 · §17 · §19, [10-20 SUMMARY §7.5](../debug_log/2026-10-20/SUMMARY.md)(정정의 원문 · 표는 그 시기 카드에서) |

### 5.7 뭉뚱그린 설명 두 건 — 스스로 정정(10-12 §18 · §21)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | ① zero-copy 설명(§8.5 '복사가 한 번 남는다') ② 포화 계기 후보 정리(§20 (가) · (나) · (다)) |
| 본 것 | ① 사용자 "DDS 는 zero-copy 를 지원하고 이미지·점군도 된다던데" ② 사용자 "SHM 이었다면 BT 요청 폭주를 밝히기 어려웠을까" |
| 처음 추론 | ① '한 번은 복사' ② (나) BT 요청 폭주를 (가) 재전송 되먹임과 같은 무게로 |
| 의심한 이유 | ① 사용자 반문 → 문서 확인 ② (나)를 이미 가진 로그 수치와 대조하지 않았음 |
| 판별 시험 | ① eProsima 15.8 · ROS 문서 · 커뮤니티 글 ② f2g2 Nav2 로그 포화 전 → 후 분당 줄 수 |
| 결론 | ① 표준 타입 SHM = 직렬화 + 역직렬화 각 1 회, zero-copy 는 고정 타입 · 같은 프로세스 · NITROS 에서만 ② 요청은 분당 수십 → (나) 약함 |
| 다음에 알아보는 법 | 가설 목록을 쓸 때 이미 가진 기록으로 자릿수부터 맞춰 본다(분당 수십 vs 초당 5 만). '복사 n 번' 같은 말은 어느 단계(직렬화 · 커널 · 조각)인지 적는다 |
| 스크립트 핵심 | ② §9.17 재계산(SUMMARY 의 계산 원문은 없음) |
| 나온 결과 | ② SUMMARY 표: smoother 27.6 → 17.6 · Passing new path 25.1 → 14.1 · Received a goal 2.4 → 6.2 · 비우기 0 → 4.4 · 4.0 · 응답 시간 초과 0 → 7.5 /분 |
| 데이터 | 10-12 SUMMARY §18 · §20 · §21, [`nav2_f2g2.log.gz`](../debug_log/2026-10-12/outputs/nav2_f2g2.log.gz) |

## 6. 기록 사이 모순 (원문 대조)
1. **2 회차와 job170 의 연결.** SUMMARY §8.14 는 job170 정지를 'map→base_link 갱신 정지' 로만 쓰고 원인을 말하지 않으며, §8.15 는 2 회차를 job 이름 없이 쓴다. `fastdds_udp_only.xml` 주석은 '2회차: slam_toolbox … → job170 주행 실패(위치가 9.90 초간 동일)' 로, 커밋 `2a4092b2` 도 같은 흐름으로 묶는다. 순서(job170 → job171 · 172 · 173 고아 발견 → job174 UDP)로 보면 맞지만, job170 의 t ≈ 4.0 정지 시각에 slam 이 이미 그래프에서 빠져 있었다는 직접 증거는 원문이 없다(**미확인**). 같은 서명(위치 고정 → 10 s 뒤 실패)이 SHM 0 인 job175 에서 CPU 로 다시 나왔으므로, job170 도 CPU 몫이 섞였을 수 있다(10-20 §7.2 의 셋째 근거).
2. **'4 개 launch'**: SUMMARY · job174 는 base · sensors · slam · navigation 4 개. 같은 커밋이 `camera.launch.py` 도 고쳤지만(gyro/accel_fps) 프로파일 설정은 sensors.launch 가 감싸서 적용된다 — 모순은 아님. 단 09-09 시점 base.launch 의 `SetEnvironmentVariable` 은 launch 자식(RSP)에만 닿고 **docker agent 컨테이너에는 안 들어간다**(agent 는 원래 `MICROROS_DISABLE_SHM=1`). 09-16 에 agent 에도 같은 XML 을 마운트.
3. **'job240_clean.sh 정리 목록에 이름을 추가'**(09-11 §5.9) vs 저장본: 저장된 `job240_clean.sh` 의 정리 패턴 `PATS` 에는 `robot_state_publisher` 가 **없다**. base 계층은 일부러 정리하지 않고('★ 2차: base 계층은 정리하지 않는다') 기동 전에 '각 1 이어야' 로 **개수만 표시**한다. SUMMARY 문장대로라면 이름이 정리 목록에 있어야 하는데, 저장본은 표시만 한다 — 저장 뒤 고친 판이 있었는지 **미확인**.
4. **'15 개' 삭제**: job150 은 정리 전 · 후 파일 수를 찍지만 원문이 없다. SUMMARY 의 '15개' 가 그 출력값으로 보인다(**추정**).

5. **'루프백 고정 유지'(10-12 §8.6 ① · §17 ①)**: 진행안이 'SHM + UDP(루프백 고정 유지 — 09-16 IP 변화 대책)' 이라 적었으나, 저장소 `fastdds_udp_only.xml` 에는 루프백 화이트리스트가 **없다** — 09-16 저녁에 agent 통신이 끊겨 되돌리고 주석만 남겼다(36~44 행, 이 카드 §4 '이후(09-16)'). 10-20 의 `fastdds_shm_udp.xml` 도 UDP 쪽에 화이트리스트가 없다(25~28 행). 10-12 문장이 옛 상태를 기억으로 적은 것(**내 기록 오류**).
6. **10-13 SUMMARY 제목 '포화 패킷 캡처 → DDS 공유메모리 도입'** vs 본문: 그날 SHM 도입 작업은 없다(본문 '공유메모리' 는 §1.2 '도입에 주는 뜻' 과 머리말뿐, §15 마무리 '다음에 할 것' 에도 없음). 제목은 10-12 §22 계획대로 붙였고 계획이 바뀐 뒤 고치지 않은 것으로 보인다(**추정**).
7. **10-12 §8.3 'nvblox 컨테이너는 공유메모리 가능 상태'**: 근거는 `ipc host` + 컨테이너 안 프로파일 없음(= 기본 SHM + UDP)이라는 설정 읽기다. 실제 호스트 ↔ 컨테이너 SHM 통과는 10-20 §7.3b~c 에서 처음 확인했다. `j968_shm.txt` 의 '컨테이너 안 프로파일: 없음 **43**' 의 43 은 컨테이너 안 `ls /dev/shm | wc -l`(항목 수, 이름 미확인)인데 SUMMARY 는 이 수를 언급하지 않는다 — 호스트 쪽 'fastrtps 잔류 0' 과 같은 `/dev/shm` 인지(ipc host 면 같아야 함)는 확인 안 됨.
8. **10-12 §21 표의 수치 재현**: 계산 스크립트 · 출력이 없다(**원천 소실**). 카드 작성 중 같은 로그로 다시 세면 포화 전(12:16:03~12:17:24) smoother 25.2 · Passing new path 23.0 · Received a goal 2.2 /분, 포화 뒤(12:17:24~12:19:15 주행 끝) 20.0 · 15.7 · 7.0 /분, 비우기 local 4.3 · global 5.9, 'Timed out while waiting · timed out while executing' 8.1 /분(§9.17). SUMMARY 값과 다르지만(창 끝 · 정규식이 다른 것으로 보임 — **추정**) '분당 수십 이하, 일부는 줄어듦' 이라는 결론은 같다.

## 7. 남은 것
- 09-09 2 회차의 실제 기전(잔재 삭제 vs launch SIGKILL vs CPU 섞임) — 10-20 은 '이 버전 · 규모에선 재현 안 됨' 까지. 그날 로그가 없어 소급 판별 불가.
- 중복 감사의 `/tf --verbose` 집계(§5.3 함정)가 09-11 job249 에도 남아 있음 — 이후 고정 도구(`Docs/tools/chk_prep.py` · `chk_drive_gate.py`, 10-27)에서 어떻게 세는지는 그 시기 카드에서 확인.
- launch 를 죽였을 때 자식이 고아로 남는 기전(09-11 RSP) — '이전 기동의 자식' 이라는 것만 PID · ppid 로 확인, 왜 안 죽었는지는 **미확인**.

- (7 기) 10-12 §17 사용자 결정('프로세스 간 전달은 DDS SHM')의 범위 — 7 기에 미실행, 10-20 은 카메라 ↔ cuVSLAM 하나로 줄였다. 나머지 경로(Nav2 · 기록기 등)를 SHM 으로 옮길지는 그 시기 카드에서.
- (7 기) 수신 버퍼 상향 — 시험 안 함(sudo · 사용자 결정). 10-12 §17 의 'CPU 무관 · 지연 증가 · 4~8 MB' 는 지식 기반 설명이라 이 장비 측정 없음.
- (7 기) 'Nav2 합치기(composition)'(§8.4 중기 후보) · 크기 고정 타입 벤치마크(§19) — 기록만, 착수 안 함.
- (7 기) SHM 구간의 관찰 수단(§21: Fast DDS 통계 기능을 Humble 배포본에서 켤 수 있는지) — 미확인.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job139 · 142 · 143 · 149 | 이상 주행 뒤 상태 · 즉시 정지 | `2026-09-09/jobs/` |
| job144 · 145 · 146 · 147 | TF · 프로세스 · EKF 입력 · stamp — 원인 좁히기 | 같은 곳 |
| job148 · 150 · 151 | SHM 서명 · 복구 · 확인(1 회차) | 같은 곳 |
| job154 · 156 · 164 | SIGTERM 정리판(+ `rm -f` 잔재 삭제) | 같은 곳 |
| job171 · 172 · 173 | job170 정지 뒤 확인 · 로그 · 고아 찾기(2 회차) | 같은 곳 |
| job174 · 176 · 177 | UDP 전용 배포 · 검증 · 환경변수 확인 | 같은 곳 |
| job180 · 181 | `/tf` 발행자 오독 · 중복 정리 | 같은 곳 |
| job240 · 249 · 250 · 252 | 깨끗한 기동 · nav2 만 재기동 + 중복 감사 · RSP 판정 · 고아 정리 | `2026-09-11/jobs/` |
| run_shm_test · run_shm_restart | SHM 재기동 견고성(15/15 · 30/30 · 10/10) | `2026-10-20/jobs/shm_test/` · `jobs/run_shm_restart.sh`, `outputs/` 같은 이름 |
| `fastdds_udp_only.xml` | UDP 전용 프로파일 | `ros2_ws/src/rover_bringup/config/` |
| job968 | (10-12 §8.3) SHM 재사용 검토용 사실 — 컨테이너 ipc · Fast DDS 판 · `/dev/shm` | [`2026-10-12/jobs/job968_shm.sh`](../debug_log/2026-10-12/jobs/job968_shm.sh) → [`j968_shm.txt`](../debug_log/2026-10-12/outputs/j968_shm.txt) |
| job967 · f2g2 Nav2 로그 | (10-12 §8.2 · §21) 커널 UDP 통계 · BT 요청 분당 수 | [`j967_net.txt`](../debug_log/2026-10-12/outputs/j967_net.txt) · [`nav2_f2g2.log.gz`](../debug_log/2026-10-12/outputs/nav2_f2g2.log.gz) — 해설은 통신 포화 카드 |

## 9. 도구 해설
**공통**: 전부 Jetson 에서 실행(PC WSL → `run_j.sh`, [보드율 카드 §9](microros-baud-regression.md) 공통 항목과 같음 — 출력은 마지막 60 줄만, 비밀번호 `<PW>`, 출력 원문 없음). 09-11 스크립트는 맨 위에 `set +u`(주석: `set -u` 면 ROS `setup.bash` 가 미정의 변수를 참조해 즉시 죽는다).

**도구 계보**
- 진단: job139(부하 · 중복 · TF Hz · 온도) → job145(프로세스 생존 · `/dev/shm`) → job146(입력 · CPU) → job147(stamp) → job148(SHM 서명) → job173(고아 자동 찾기) — 이후 '프로세스는 사는데 그래프에 없음' 검사는 [CPU 카드](cpu-load-stalls.md) 의 job176 · 177 과 09-11 감사로
- 정지: job143(`-9` + 0 Twist 25 회) → job149(0 Twist 20 회 + 보드 모터 상태 확인)
- 정리: (오전) `pkill -f "a\|b"` → job102(for-루프 `-9`) → **job150(TERM → `-9` → agent 삭제 · daemon stop · `rm -f` SHM)** → job154 · 156(TERM 만, 잔재 삭제 유지) → job164(TERM 고정 8 s) → job174(TERM 최대 15 s) → job179 · 181(SIGTERM → 잔존 세기 → `-9`, 'SHM 비활성이라 잔재 위험 없음') → 09-11 job240(base 계층 보존) · job249(nav2 만) — 이후 `prep_fast.sh` 의 TERM 15 s → `-9` + `fastdds shm clean`(10-20)

### 9.1 `job139_sys.sh` — 부하 · 중복 · TF · 온도
- 하는 일: `/proc/loadavg` · `nproc` → 11 개 이름 `pgrep -fc`(1 이 아니면 표시) → `/tf` · `/tf_static` · `/odometry/filtered` · `/map` hz → `/tf` 1 개 메시지의 frame 쌍 → top 상위 7 → thermal_zone 4 개 온도 → 배터리.
- 출력: 원문 없음(SUMMARY §8.12 '이전: foxglov+ 88.2 %' 가 이 도구 또는 같은 형식 도구의 값일 수 있음 — **추정**, [Foxglove 카드](foxglove-snap-cpu.md)).
- 지금: 형식만 참고.

### 9.2 `job143_estop.sh` · `job149_hardstop.sh` — 즉시 정지
- job143: Nav2 지령 노드 10 패턴 `pkill -9` → `ros2 topic pub -1 /cmd_vel Twist "{}"` 25 회 → `/cmd_vel` 퍼블리셔 수 · 보드 상태 4 줄 · 휠 속도.
- job149: 퍼블리셔 수 → 0 Twist 20 회 → `/rover/status` 의 `message` · `tgt` 값 3 회(보드가 실제로 목표 0 을 받았는지) → 5 s 사이 `/wheel_odom` x · y 전후.
- 왜: 이상 주행 중 사람이 차를 세울 수단이 스크립트뿐이었다(온보드 정지 수단은 09-29 과제).
- 결함: job143 의 `-9` 도 SHM 잔재 원인 목록에 들어 있다(§8.9 목록 마지막 143). `ros2 topic pub -1` 은 매번 새 DDS 참가자를 만들고 발견을 기다려 1 회에 수백 ms 걸린다 — 25 회면 수 초(**추정**). 펌웨어 watchdog(500 ms 무지령 정지)이 실제 정지 보장.

### 9.3 `job144_slam.sh` — TF 체인 · 지도 범위
- 하는 일: map→odom · odom→base_link · map→base_link 각 10 s(마지막 Translation · RPY) → `/odometry/filtered` x · y → `/map` info(크기 · 원점) → slam 로그 warn|error|loop|reject|fail|jump 12 줄 → nav2 로그 'Goal canceled' 이후 15 줄 → conditioner 의 slip · scale · reject 경고.
- 쓰인 곳: '정합 어긋남' 오판(§5.2)의 재료.
- 결함: `tf2_echo` 는 변환이 없을 때 오류 줄만 내는데 이 스크립트는 Translation 줄만 grep → 변환 부재가 빈 줄로 보인다.

### 9.4 `job145_alive.sh` · `job146_ekfin.sh` — 살아 있나 · 입력은 오나
- job145: 9 개 이름 `pgrep -fc` · docker 수 · load → `/tf` · `/odometry/filtered` · `/wheel_odom` · `/scan` · `/map` hz → sensors.log 의 died · exit code · `Failed to meet update rate` → `df -h /dev/shm` · 파일 수 → `free -m`.
- job146: EKF 입력 계통 8 토픽 hz → 6 개 노드의 첫 pid · `ps -o %cpu,stat` → conditioner · 카메라 로그 6 줄.
- 판정 읽는 법: 프로세스 1 · CPU 정상 · 입력 정상 · 출력 무발행 = '계산' 이 아니라 '통신 등록' 쪽.
- 결함: `pgrep -f "$p" | head -1` 은 launch 감싸개를 고를 수 있다([Foxglove 카드 §5.2](foxglove-snap-cpu.md) 와 같은 함정 — ekf 의 'CPU 20 %' 가 본체 값인지 **미확인**, 다만 감싸개라면 0 % 에 가까웠을 것).

### 9.5 `job147_stamp.py` — 시각 가설 판별
- 가설(독스트링): robot_localization 은 필터 시각보다 과거인 stamp 를 버리고, 미래로 크게 튀면 필터를 끌고 간 뒤 이후 정상 메시지를 전부 '과거' 로 버린다. 보드는 60 s 마다 `rmw_uros_sync_session` 으로 재동기하므로 그 보정이 튀면 이 상태가 된다.
- 하는 일: `/wheel_odom` · `/wheel_odom/conditioned` · `/imu/data` · `/scan`(BEST_EFFORT) · `/odometry/filtered`(깊이 10) 12 s 구독 → 토픽별 수신 수 · 마지막 stamp · 수신 host 시각 · 오프셋(stamp − host) · stamp 진행 vs 실경과 → 토픽별 stamp 역행 횟수 · 최대 전진폭.
- 출력: 오프셋 −0.002~−0.032 s, 역행 0(§8.9). 원문 없음. `/odometry/filtered` 는 퍼블리셔 0 이라 '수신 없음' 이었을 것.
- 지금: 재사용 가능(시각 문제 1 차 점검).

### 9.6 `job148_shm.sh` — SHM 서명 ★
- 하는 일: `ls -l /dev/shm` 앞 5 줄 · 총수 · `fastrtps_port*` 수 · `fastrtps_*` 수 · `sem.fastrtps*` 수 → 문제 포트 두 개(7423 · 7427, 로그에서 본 번호를 하드코딩)의 `ls -l` · `fuser -v` → `/dev/shm/*` 를 여는 프로세스 수 → `/odometry/filtered` 퍼블리셔 · `/tf` 정보.
- 읽는 법: FastDDS SHM 포트 하나 = 세그먼트 파일 `fastrtps_portN` + 잠금 파일 `fastrtps_portN_el`(+ 세마포어). 본체 없이 `_el` 만 있으면 비정상 종료의 고아 → 다음에 같은 포트를 여는 참가자가 `open_and_lock_file failed`.
- 지금: `fastdds shm clean`(FastDDS 공식 도구) 이 같은 판정 + 정리를 한다(10-20 부터).

### 9.7 `job150_recover.sh` — SHM 잔재 복구
- 하는 일: ① `pkill -TERM -f "ros2 launch"` + 19 개 노드 TERM → 1 s 간격 최대 12 회 `pgrep -fc` 로 7 개 핵심 이름 0 확인 ② 남은 것 `-9` ③ agent 컨테이너 삭제 · `ros2 daemon stop` ④ 정리 전 파일 수 · `/dev/shm` 을 여는 프로세스 수 → `rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_*` → 정리 후 수 ⑤ ROS 프로세스 수 · docker 수 · load.
- 결함: (a) `pgrep -fc … || echo 0` 은 0 개일 때 두 줄('0' · '0')을 내 `[ "$n" = "0" ]` 이 거짓 → 루프가 일찍 안 끝나고 12 s 를 다 기다린다(판정 실패는 아님, **추정** — 코드 읽기). (b) agent 를 지우므로 **보드 RESET 이 필요**해진다(job151 '없음 — RESET 필요', [보드 카드](board-link-microros-session.md)). (c) `rm -f` 로 아직 열린 파일까지 지울 수 있다 — '아직 /dev/shm 을 여는 프로세스' 수를 찍지만 그 값으로 분기하지 않는다(10-20 이 지목한 정리 방식).
- 지금: 쓰지 않는다. 대체 = TERM → 대기 → `-9` → `fastdds shm clean`.

### 9.8 `job151_check.sh` · `job154_reinit.sh` · `job156_stop.sh` — 복구 확인 · TERM 판
- job151: `/odometry/filtered` · `/tf` · `/map` · `/scan` 의 'Publisher count' + hz → map→odom · odom→base → `/dev/shm` fastrtps 수('정상 재생성') → 보드 노드 · load.
- job154: `nav2_params.yaml`(depth `clearing: false` 진단판) CR 제거 · 배포 → TERM 정리(최대 12 s) → 잔존 · fastrtps 잔재 · 보드 유지 → sensors(26 s) → slam(14 s) → nav2(28 s) → lifecycle · filtered · odom→base · clearing 적용값. 주석에 'SIGKILL 은 FastDDS 공유메모리 잔재를 남겨 … 사고를 낸다 — 2026-09-09 실측'.
- job156: 설정 되돌림(`clearing: true`) → 배터리 → 0 Twist 12 회 → TERM 정리(최대 15 s) → agent 삭제 · daemon stop · `rm -f` SHM → 잔재 · 프로세스 · load → '충전 진행하셔도 됩니다'(하루 종료용).
- 결함: job154 · 156 도 `pgrep -fc … || echo 0` 두 줄 문제(대기 루프만 영향). job156 의 `rm -f` 는 10-20 지목 대상.

### 9.9 `job164_stvlup.sh` — 전체 재기동(2 회차 직전 정리판)
- 하는 일: STVL 판 `nav2_params.yaml` 배포 → `"ros2 launch"` 포함 20 개 패턴 TERM → **고정 8 s** → agent 삭제 → `rm -f` SHM → base(12 s) → sensors(26 s) → slam(12 s) → nav2(30 s, STVL 로드 확인).
- 결함: 8 s 는 종료 확인이 아니라 고정 대기 — 느린 노드(slam 등)가 아직 살아 있을 때 그 SHM 파일을 지웠을 수 있다(10-20 §7.2 근거 1). agent 를 지워 RESET 필요(§8.11 '주행 검증 미실행(보드 RESET 필요 상태)').

### 9.10 `job173_slam.sh` — 고아 자동 찾기 ★
- 하는 일: `pgrep -af slam_toolbox` · 노드 목록 · `ps -o %cpu,stat,etime` → `/map` · `/map_metadata` · `/slam_toolbox/graph_visualization` hz · `/map` 퍼블리셔 수 → map→odom 조회(12 s, 'does not exist' · 'Invalid' 포함) → `/dev/shm` 의 `fastrtps_portN` 이름들 중 **본체 파일이 없고 `N_el` 만 있는 것** 목록 → slam 로그 끝 6 줄.
- 출력: 고아 7425(§8.15). 원문 없음.
- 지금: 판정 논리는 유효, 실제로는 `fastdds shm clean` 이 대신.

### 9.11 `job174_dds.sh` — UDP 전용 배포 + 전체 재기동 + 검증 ★
- 하는 일: `/tmp` 의 XML · 4 개 launch CR 제거 → src · install 에 복사(config 폴더 생성 포함) → '배포 확인: XML OK, launch N 개'(`grep -lc FASTRTPS_DEFAULT_PROFILES_FILE` 수) → TERM 정리(최대 15 s) → agent 삭제 · daemon stop · `rm -f` SHM → base(12) → sensors(26) → slam(12) → nav2(30) → 검증: **SHM 재생성 수('0 이면 SHM 미사용 — 의도한 상태')**, 세 로그의 `RTPS_TRANSPORT_SHM` 수, 6 토픽 hz, `/tf` 퍼블리셔 수('ekf + slam + RSP = 3 이 정상'), 노드 수, 보드 노드, load.
- 출력: §2 의 검증 줄. 원문 없음.
- 결함: 'SHM 재생성 0' 은 프로파일 있는 노드만의 이야기 — 이 스크립트를 ssh 로 부른 셸의 ros2 CLI(hz · info)는 프로파일 없이 SHM 참가자를 만들 수 있다(메모리 기록). 측정 시점엔 끝나 있어 0 으로 보였을 것(**추정**).

### 9.12 `job176_who.sh` · `job177_env.sh` — 정지 재발 뒤 '누가 · 무엇이'
- job176: `/tf` 발행 주체(`--verbose` 의 Node name — §5.3 함정 포함) · 7 토픽 hz · 6 개 프로세스 CPU · 상태 · 노드 목록 · fastrtps 파일 수 · SHM 오류 수 · 로그 끝 3 줄씩 · load · 메모리 · top 상위 5.
- job177: 6 개 노드 첫 pid 의 `/proc/<pid>/environ` 에서 `FASTRTPS_DEFAULT_PROFILES_FILE`(없으면 '미설정') → slam 상태 · 스레드 수 · 로그 수준별 건수 · 'Message Filter dropping' 이 아닌 마지막 로그 → `Failed to meet update rate` 총수 · `Took` 값 평균 · 최대 → `/camera/camera/imu` · `/imu/data` hz.
- 출력: 프로파일 전부 적용(§8.15), EKF 91 회 · 평균 0.055 s · 최대 0.197 s(§8.16 — [CPU 카드](cpu-load-stalls.md)). 원문 없음.
- 결함: environ 은 첫 pid 만 — 감싸개를 고르면 감싸개의 환경이다(launch 가 설정한 변수는 감싸개 · 본체 모두에 있으므로 이 용도에선 결과가 같음, **추정**).

### 9.13 `job249_nav2only.sh` — nav2 만 재기동 + 전 스택 중복 감사 ★(09-11)
- 하는 일: `nav2_params.yaml` CR 제거 → 파이썬으로 YAML 검증(충돌 지평 = 1.5, 모든 코스트맵 플러그인에 `plugin` 키 — 09-09 §8.11 '블록 잘림' 사고 대책) → 배포 → 유지 계층 11 개 · nav2 10 개 이름별 개수 → nav2 TERM(최대 15 s, `cnt1` = `pgrep -fc | head -1` 로 두 줄 문제 해결) → 남으면 `-9` → **유지 계층 5 개가 정확히 1 개씩인지** · agent 1 개인지(아니면 '전체 재기동(job240_clean) 필요' 로 중단) → nav2 기동(30 s) · lifecycle · 적용값 · BT 로드 오류 → **전 스택 14 개 이름 각 1 개**(아니면 '← !!', '주행 금지' exit 1) · 그래프 이름 중복(`uniq -d`) · `/tf` 발행 노드별 수 → 코스트맵 클리어 + 15 s → 자세 → `job248_audit.py`(통과 가능성).
- 출력: RSP 2 개 발견(09-11 §5.9). 원문 없음.
- 결함: `/tf` 발행자 집계가 `--verbose` 전체의 Node name 을 셈(§5.3 함정 그대로). `pgrep -fc robot_state_publisher` 는 cmdline 에 그 이름이 든 다른 프로세스(예: 그 이름을 인자로 받은 셸)도 센다.
- 지금: 감사 개념은 이후 `chk_prep.py`(10-27, 파라미터 · 노드 확인 한 노드)로 이어짐.

### 9.14 `job250_rsp_then_drive.sh` → `job252_fix_then_drive.sh` — RSP 판정 · 고아 정리
- job250: RSP 프로세스 수 · `pgrep -fa` 명령줄 · base.launch 수 · 그래프의 `/robot_state_publisher` 횟수 · `/tf_static` 발행자 GID → 프로세스 ≠ 1 이면 중단, 1 이면 '그래프 중복은 DDS 잔상(UDP 참가자 lease 만료 대기)으로 판단' 하고 `job231_drive.sh job251 1.60 90` 주행.
- job252: `/tmp/base.log` 에서 `robot_state_publisher-2]: process started with pid [N]` 로 **현재 launch 의 자식 PID** 를 얻고, 그 외 RSP 마다 ppid · 시작 시각을 찍고 TERM → 3 s 뒤 남으면 KILL → 1 개 확인 → `/tf_static` 퍼블리셔 · `base_link→camera_link` 생존 → 전 스택 재감사 → 주행.
- 결함: job250 의 '잔상' 분기는 근거 없는 가정이었다(실제 2 개). job252 의 '현재 자식 PID' 는 `base.log` 가 현재 launch 의 로그일 때만 맞다 — base 를 유지하고 로그를 다시 안 쓴 경우 옛 PID 를 기준으로 삼을 수 있다(**추정**).

### 9.15 `fastdds_udp_only.xml` — UDP 전용 프로파일
- 위치: `ros2_ws/src/rover_bringup/config/`, 4 개 launch 가 설치본 경로를 `FASTRTPS_DEFAULT_PROFILES_FILE` 로 지정.
- 내용: `transport_descriptor` `udp_only_transport`(UDPv4) → participant 프로파일 `udp_only_participant`(기본 프로파일)에서 `userTransports` = 그것, `useBuiltinTransports` = false.
- 계보: 09-09 신규 → 09-16 루프백 화이트리스트 추가 → 같은 날 저녁 되돌림(agent 미적용으로 `/wheel_odom` 0) · 주석만 남김 → 10-20 짝 프로파일 `fastdds_shm_udp.xml`(카메라 · cuVSLAM 만).
- ⚠ 주석에 'ROS_LOCALHOST_ONLY 는 rmw 가 SHM 을 다시 켜므로 쓰지 않는다'(09-16).
- 지금: 계속 쓰는 파일.

### 9.16 `job968_shm.sh` — SHM 재사용 검토용 사실 확인(10-12 §8.3)
- 실행: Jetson(PC WSL → `run_j.sh`), 인자 없음, 로버 안 움직임.
- 왜: 사용자 'SHM 을 다시 쓰면?' 에 답하려면 컨테이너 둘(nvblox · micro-ROS 에이전트)이 호스트와 SHM 을 나눌 수 있는 상태인지, 호스트 Fast DDS 판, `/dev/shm` 잔재를 알아야 했다.
- 하는 일(5 줄): ① 컨테이너 둘마다 `docker inspect` 로 `HostConfig.IpcMode` · `NetworkMode` · `/dev/shm` 마운트 ② `dpkg -l | grep -a 'ros-humble-fastrtps '` 판 · `RMW_IMPLEMENTATION`(없으면 '기본(fastrtps)') ③ nvblox 컨테이너 안 `FASTRTPS_DEFAULT_PROFILES_FILE`(없으면 '없음')과 `ls /dev/shm | wc -l` ④ 호스트 `df -h /dev/shm` · `fastrtps` 이름 파일 수. 판정 문턱 없음(읽기만).
- 출력: §5.5 '나온 결과' 그대로. 원문 [`j968_shm.txt`](../debug_log/2026-10-12/outputs/j968_shm.txt).
- 쓰인 곳: §8.3 '사실' · §8.5 'nvblox 컨테이너는 이미 SHM 가능 상태'.
- 결함: ① `/dev/shm 공유` 칸이 둘 다 빈 값 — `ipc host` 는 마운트가 아니라 IPC 이름공간 공유라 `Mounts` 에 안 나온다(코드 읽기, 그래서 이 칸은 아무것도 판별 못 함) ② 컨테이너 안 수 43 이 무엇인지(이름) 안 찍음(§6 모순 7) ③ 에이전트 컨테이너의 `MICROROS_DISABLE_SHM` 은 확인하지 않음(§8.6 은 기억 · 09-09 주석 근거).
- 계보 · 지금: 일회용. 10-20 의 SHM 경로 확인(`chk_shm_path.sh`)이 실제 통과를 잰다(그 시기 카드).

### 9.17 (카드 작성 중) 10-12 §21 표 재계산 — f2g2 Nav2 로그 분당 줄 수
- 실행: PC(카드 작성 중, 스크래치 — 파일은 남기지 않음, 아래 발췌가 전부). 입력 [`nav2_f2g2.log.gz`](../debug_log/2026-10-12/outputs/nav2_f2g2.log.gz), 창 = 주행 시작 12:16:03(`f0_f2g2_runner.log` 출발 · 게이트 뒤 SUMMARY §5.2) · 포화 시작 12:17:24(§5.2) · 주행 끝 12:19:15(시작 + 총 192.5 s, 러너 '결과' 줄).
- 핵심: 줄의 `[1791…]` epoch 를 KST 로, 정규식 `Received a path to smooth` · `Passing new path` · `controller_server.*Received a goal` · `clear.*local_costmap|local_costmap.*clear` · 같은 global · `Timed out while waiting|timed out while executing` 을 전 · 후로 세어 분으로 나눔.
- 나온 결과:
```
창: 시작 12:16:03 포화 12:17:24 끝 12:19:15
전 1.35 분 · 후 1.85 분
smoother Received a path to smooth     전  34 (25.2/분) → 후  37 (20.0/분)
controller Passing new path            전  31 (23.0/분) → 후  29 (15.7/분)
controller Received a goal             전   3 (2.2/분) → 후  13 (7.0/분)
clear local                            전   0 (0.0/분) → 후   8 (4.3/분)
clear global                           전   0 (0.0/분) → 후  11 (5.9/분)
timeout ack                            전   0 (0.0/분) → 후  15 (8.1/분)
```
- 읽는 법: SUMMARY 의 값과 자릿수 · 방향(경로 관련 감소, 목표 · 비우기 · 시간 초과 증가)이 같다. 끝을 로그 끝(12:23:15)까지 넓히면 smoother 6.8 /분처럼 크게 달라지므로, SUMMARY 의 창 끝은 주행 끝 근처였을 것(**추정**).

## 10. 용어
- **DDS · FastDDS(Fast RTPS)**: ROS 2 의 통신 계층 표준(DDS)과 그 구현 하나(eProsima). Humble 기본 rmw 가 FastDDS. 로그 접두어 `RTPS_` 는 그 내부 모듈.
- **participant(참가자)**: DDS 에서 '통신에 참여하는 주체' 단위. ROS 2 노드(정확히는 프로세스의 컨텍스트)마다 하나. 참가자끼리 서로를 **발견(discovery)** 해야 토픽이 이어진다. `ros2` CLI 명령 하나도 실행되는 동안 참가자다.
- **transport(전송) — UDPv4 / SHM**: 참가자 사이 바이트를 실어 나르는 방식. 기본은 둘 다 켜져 있어 같은 호스트면 SHM, 아니면 UDP. SHM 은 `/dev/shm` 의 파일(세그먼트 · 잠금 · 세마포어)로 메모리를 공유해 복사가 적다. UDP 는 루프백(127.0.0.1)이라도 커널 소켓 버퍼를 거친다.
- **`/dev/shm` · 고아 잠금 파일(`_el`)**: 리눅스 공유메모리 파일 시스템. FastDDS 포트 `fastrtps_portN` 의 잠금 파일이 `fastrtps_portN_el`. 정상 종료 때 지우고, 비정상 종료(SIGKILL)면 남는다. 남은 잠금 때문에 다음 참가자가 그 포트를 못 열면 `open_and_lock_file failed`.
- **profile XML · `FASTRTPS_DEFAULT_PROFILES_FILE`**: FastDDS 설정을 XML 로 덮어쓰는 방식, 그 파일을 가리키는 환경변수. 환경변수는 프로세스마다 상속되므로 launch 가 설정하면 그 자식들에만 적용된다.
- **`fastdds shm clean`**: FastDDS 가 주는 도구. 어떤 프로세스도 잡고 있지 않은 SHM 파일만 지운다(`rm -f` 와 달리 살아 있는 참가자를 안 건드림).
- **SIGTERM / SIGINT / SIGKILL(−9)**: 종료 신호. TERM · INT 는 프로세스가 받아 정리할 수 있고, KILL 은 즉시 끝나 정리 기회가 없다. `ros2 launch` 는 종료 때 자식에게 INT → (몇 초 뒤) TERM → KILL 로 올린다.
- **Publisher count · `--verbose`**: `ros2 topic info` 가 내는 발행자 수. `--verbose` 는 발행자 블록 다음에 구독자 블록까지 노드 이름을 나열한다(§5.3).
- **고아(orphan) 프로세스**: 부모(launch)가 죽었는데 안 죽고 남은 자식. 09-11 RSP 처럼 같은 이름 노드가 그래프에 둘이 된다.
- **`MICROROS_DISABLE_SHM=1`**: micro-ROS agent 이미지의 환경변수 — agent 의 DDS 참가자가 SHM 을 안 쓰게 한다. 09-09 두 사고에서 보드 토픽만 멀쩡했던 이유.
- **통합 메모리(Jetson unified memory)**: Jetson 은 CPU 와 GPU 가 같은 물리 RAM 을 쓴다 → 한 프로세스 안에서 CPU↔GPU 사이 큰 데이터를 복사 없이 넘길 수 있음(CUDA 통합 · 고정 메모리). 프로세스 사이 ROS 메시지 전달과는 다른 층(10-12 §8.4).
- **NITROS**: Isaac ROS 가 노드 사이에 GPU 버퍼를 직렬화 없이 넘기는 방식(같은 프로세스 · 지원 노드끼리).
- **노드 합치기(composition)**: 여러 ROS 노드를 한 프로세스(컴포넌트 컨테이너)에 올려 그 사이 메시지를 포인터로 넘기는 것. Nav2 `use_composition`.
- **zero-copy · 대여 메시지(loan)**: 발행자가 미들웨어 버퍼를 빌려 그 안에 바로 쓰고 구독자가 그 버퍼를 그대로 읽는 것. Fast DDS 에선 plain · 크기 고정 타입에서만(가변 길이 배열 · 문자열이 없어야). `sensor_msgs/Image` · `PointCloud2` · `MarkerArray` · `TFMessage` 는 해당 안 됨(10-12 §18 · §19).
- **`net.core.rmem_max` · `rmem_default`**: 리눅스 소켓 수신 버퍼의 최댓값 · 기본값(이 Jetson 212 992 B). 바꾸려면 sudo(sysctl). UDP 메시지 하나가 이보다 크거나 몰려 오면 커널이 버린다(`RcvbufErrors`).
- **SHM `segment_size`**: Fast DDS SHM 전송에서 참가자마다 `/dev/shm` 에 만드는 쓰는 쪽 버퍼 크기. 큰 메시지 여러 장이 들어가야 함(10-20 `fastdds_shm_udp.xml` 8 MB).
