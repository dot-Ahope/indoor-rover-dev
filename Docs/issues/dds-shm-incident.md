# DDS 공유메모리(SHM) 사고 — 살아 있는 노드가 그래프에서 사라짐, 그리고 중첩 프로세스

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회 → 견고성 선택으로 유지**(09-09 SHM 을 끄고 UDP 전용, 재발 0) · 원인 판정은 **10-20 에 일부 정정**(SHM '자체' 가 원인이라는 것은 과한 일반화 — 확인된 것은 '비정상 종료 · 잔재 강제 삭제가 있으면 깨진다' 까지) · 10-20 시험 뒤 카메라 ↔ cuVSLAM 만 SHM 재사용(10-23 운용 기본) | 09-09 (1 회차 · 2 회차) · 09-11(중첩 프로세스) · 이후 10-20 재점검 · 10-23 | [09-09 §8.9](../debug_log/2026-09-09/SUMMARY.md) — 사용자 보고 "지도를 벗어나 이상하게 움직인다" | `ros2_ws/src/rover_bringup/config/fastdds_udp_only.xml`(신규, 커밋 `2a4092b2`) · `base` · `sensors` · `slam` · `navigation` launch 의 `SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', …)` · 정리 스크립트(SIGTERM 우선) · 09-11 `job240_clean.sh` 중복 감사 | [micro-ROS 보드율 회귀](microros-baud-regression.md)(같은 날 오전, `pkill` 오염의 시작) · [CPU 부족 정지](cpu-load-stalls.md)(같은 서명의 다른 원인 — 2 회차 판정과 섞임) · [보드 연결 · 세션](board-link-microros-session.md)(정리 스크립트가 agent 까지 지워 RESET 반복) |

**한 줄**: 09-09 저녁, EKF 프로세스는 CPU 20 % 로 살아 있고 입력도 정상인데 `/odometry/filtered` 퍼블리셔가 **0** 이 됐다. FastDDS 로그에 `open_and_lock_file failed`, `/dev/shm` 에는 본체 없이 잠금 파일(`_el`)만 남은 고아가 있었다. 그날 내가 정리를 '확실히' 하려고 13 개 스크립트에서 `pkill -9` 를 썼고, SIGKILL 은 FastDDS 가 SHM 파일을 치우지 못하게 한다. SIGTERM + 잔재 삭제로 복구했으나 몇 시간 뒤 `slam_toolbox` 에 같은 서명이 다시 나왔고, 'SIGTERM 으로 바꿨는데도 재발 → SHM 을 쓰는 것 자체가 문제' 로 보고 SHM 을 끈 UDP 전용 프로파일을 모든 launch 에 넣었다(재발 0). 10-20 에 사용자 요청으로 다시 보니 2 회차 전 스크립트들이 **살아 있는 참가자의 SHM 파일까지 `rm -f`** 했고 launch 의 SIGKILL 단계도 확인 안 됐으며 같은 날 CPU 정지와 섞여 있었다 → 'SHM 자체' 는 근거가 약했다. 정리 없이 −9 를 섞은 재기동 시험(FastDDS 2.6.12)이 15/15 · 30/30 통과해, 10-23 부터 카메라 ↔ cuVSLAM 경로만 SHM 을 쓴다. 09-11 에는 다른 형태의 '중첩' — launch 를 죽여도 자식 `robot_state_publisher` 가 고아로 남아 같은 이름 노드가 둘 — 을 사용자 지적으로 찾아 기동 절차에 중복 감사를 넣었다.

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

## 4. 조치와 효과
- **정리 규칙**(09-09 §8.9): `pkill -TERM` → 최대 15 s 대기 → 남은 것만 `-9`. `job154` · `job156` · `job174` · `job178` 부터 적용. ⚠ 같은 스크립트들이 끝에 `rm -f /dev/shm/fastrtps_*` 를 함께 했다 — 10-20 이 지목한 '잔재 강제 삭제'(지금은 금지: 10-20 이후 prep 은 `fastdds shm clean`, 아무도 안 잡은 고아만).
- **UDP 전용 프로파일**(09-09 §8.15, `config/fastdds_udp_only.xml`): `UDPv4` transport 하나를 정의하고 기본 participant 프로파일(`is_default_profile="true"`)에서 `useBuiltinTransports=false` → 기본 전송(SHM 포함)을 끈다. 각 launch 의 `SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', <설치본 XML>)` 로 그 launch 의 모든 자식에 적용. 비용 주석: 같은 호스트 통신이 UDP 루프백을 탄다 — 작은 메시지 위주라 감당(가장 큰 점군 15 Hz × 수백 kB).
  - 효과: SHM 오류 0, 이후 '살아 있는데 사라지는 노드' 기록 없음.
  - 한계(메모리 · 10-20): ssh 로 띄운 진단 스크립트 · `ros2` CLI 는 이 환경변수가 없어 여전히 SHM 참가자를 만든다(통신은 UDP 로 협상돼 문제 없음). 10-20 §7.2 측정: 그날도 `/dev/shm` 에 FastDDS 파일 16 개가 생겨 있었다(프로파일 없이 뜬 무언가의 잔재 **추정**).
- **중복 감사**(09-11 §5.9): `job249_nav2only.sh` · `job252_fix_then_drive.sh` 가 14 개 이름 각각 `pgrep -fc` = 1 인지, `ros2 node list | sort | uniq -d`, `/tf` 발행 노드별 수를 찍고 하나라도 아니면 '주행 금지' 로 끝낸다. `job240_clean.sh` 는 기동 전 정리 + `robot_state_publisher` 개수 표시.
- 이후(09-16): Wi-Fi 전환으로 IP 가 바뀌면 이미 뜬 참가자가 옛 IP 를 광고하는 문제로 XML 에 루프백 화이트리스트를 넣었다가, agent 컨테이너가 같은 화이트리스트를 안 써 `/wheel_odom` 0 이 되어 되돌림(job359/360). agent 에도 같은 XML 을 마운트(`base.launch.py` `-v … -e FASTRTPS_DEFAULT_PROFILES_FILE=…`). 상세는 Wi-Fi · DDS 카드(예정) — [Jetson Wi-Fi](jetson-wifi-link.md).
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

## 6. 기록 사이 모순 (원문 대조)
1. **2 회차와 job170 의 연결.** SUMMARY §8.14 는 job170 정지를 'map→base_link 갱신 정지' 로만 쓰고 원인을 말하지 않으며, §8.15 는 2 회차를 job 이름 없이 쓴다. `fastdds_udp_only.xml` 주석은 '2회차: slam_toolbox … → job170 주행 실패(위치가 9.90 초간 동일)' 로, 커밋 `2a4092b2` 도 같은 흐름으로 묶는다. 순서(job170 → job171 · 172 · 173 고아 발견 → job174 UDP)로 보면 맞지만, job170 의 t ≈ 4.0 정지 시각에 slam 이 이미 그래프에서 빠져 있었다는 직접 증거는 원문이 없다(**미확인**). 같은 서명(위치 고정 → 10 s 뒤 실패)이 SHM 0 인 job175 에서 CPU 로 다시 나왔으므로, job170 도 CPU 몫이 섞였을 수 있다(10-20 §7.2 의 셋째 근거).
2. **'4 개 launch'**: SUMMARY · job174 는 base · sensors · slam · navigation 4 개. 같은 커밋이 `camera.launch.py` 도 고쳤지만(gyro/accel_fps) 프로파일 설정은 sensors.launch 가 감싸서 적용된다 — 모순은 아님. 단 09-09 시점 base.launch 의 `SetEnvironmentVariable` 은 launch 자식(RSP)에만 닿고 **docker agent 컨테이너에는 안 들어간다**(agent 는 원래 `MICROROS_DISABLE_SHM=1`). 09-16 에 agent 에도 같은 XML 을 마운트.
3. **'job240_clean.sh 정리 목록에 이름을 추가'**(09-11 §5.9) vs 저장본: 저장된 `job240_clean.sh` 의 정리 패턴 `PATS` 에는 `robot_state_publisher` 가 **없다**. base 계층은 일부러 정리하지 않고('★ 2차: base 계층은 정리하지 않는다') 기동 전에 '각 1 이어야' 로 **개수만 표시**한다. SUMMARY 문장대로라면 이름이 정리 목록에 있어야 하는데, 저장본은 표시만 한다 — 저장 뒤 고친 판이 있었는지 **미확인**.
4. **'15 개' 삭제**: job150 은 정리 전 · 후 파일 수를 찍지만 원문이 없다. SUMMARY 의 '15개' 가 그 출력값으로 보인다(**추정**).

## 7. 남은 것
- 09-09 2 회차의 실제 기전(잔재 삭제 vs launch SIGKILL vs CPU 섞임) — 10-20 은 '이 버전 · 규모에선 재현 안 됨' 까지. 그날 로그가 없어 소급 판별 불가.
- 중복 감사의 `/tf --verbose` 집계(§5.3 함정)가 09-11 job249 에도 남아 있음 — 이후 고정 도구(`Docs/tools/chk_prep.py` · `chk_drive_gate.py`, 10-27)에서 어떻게 세는지는 그 시기 카드에서 확인.
- launch 를 죽였을 때 자식이 고아로 남는 기전(09-11 RSP) — '이전 기동의 자식' 이라는 것만 PID · ppid 로 확인, 왜 안 죽었는지는 **미확인**.

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
