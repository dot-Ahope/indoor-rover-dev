# SLAM 이 그래프에서 사라진 채 정지 — Fast DDS 2.6.11 락 순서 역전 데드락 (mp7)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회 + 수정판 적용**(Fast DDS 2.6.11 → 2.6.12, 사용자 승인) · 재발 기록 없음(09-17 이후 SUMMARY 에 같은 서명 없음) · **증명은 아님**(스트레스 3 라운드 정지 0, 2.6.11 대조 없음) · 주행 중 5 s 공백의 원인은 **미확정** | 09-17 §5 ~ §6.3 (게이트는 10-27 까지 이어 씀) | [09-17 §5](../debug_log/2026-09-17/SUMMARY.md) mp7 | Jetson 패키지 `ros-humble-fastrtps` 2.6.11-1jammy.20260214 → **2.6.12-1jammy.20260725**(저장소 파일 아님) · `nav2_params.yaml`(`bt_navigator.default_server_timeout` 20 → **100**, `FollowPathMPPI.visualize` true → **false**) · 러너 게이트에 SLAM 생존 검사(`job386_slamalive.py` → 10-27 `Docs/tools/chk_drive_gate.py` 의 C) · bag 기록에서 `/trajectories` 제외 · 주행 중 `top -b -d 2` 기록 | [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(10-27, **다른 현상**: 정합 중 stamp 멈춤 · 프로세스는 정상) · [DDS 공유메모리 사고](dds-shm-incident.md)(09-09, '살아 있는데 그래프에서 사라짐' 같은 서명의 다른 원인) · ['후진하고 멈췄다' — CPU · 위치 추정 정지](cpu-load-stalls.md)(같은 날 전력 모드 오판) · [Nav2 첫 구축](nav2-first-setup.md) |

**한 줄**: 09-17 mp7 은 통로 안에서 27 s 만에 ABORTED 됐는데 원인은 주행이 아니었다. bag 을 보니 주행 중 map→odom 이 **+6.8 s 에 5.1 s** 끊기는 등 SLAM 이 수 초씩 멈췄고, 그 공백이 끝날 무렵(11.55 s) map 프레임을 쓰는 서버들이 BT 의 20 ms 응답 기한을 못 지켜 복구 · BackUp 으로 들어갔다. 주행 뒤엔 slam_toolbox 프로세스는 살아 있는데 **22 스레드 전부 futex 대기, ROS 그래프에서 사라짐**(`/map` 발행자 0) 상태였다. 사용자 승인으로 `gdb` 역추적을 떠 보니 6 스레드가 Fast DDS 내부 뮤텍스를 서로 기다렸다 — 원격 구독자 제거(`StatefulWriter::matched_reader_remove`) 경로와 흐름 제어기 송신 경로가 엇갈린 **락 순서 역전**, 그리고 SLAM 의 `/tf` 발행 스레드가 `DataWriterImpl::write` 에서 멈춰 map→odom 이 사라졌다. 이는 Fast DDS 2.6.12 릴리스 노트의 'Fix lock order inversion in StatefulWriter'(#6463)와 강하게 일치해 2.6.12 로 올렸다. 유발 조건(구독자 생성 · 해체)을 3 라운드 반복한 스트레스에서 정지 0 이었지만 2.6.11 에서 같은 시험을 안 했으므로 **보조 증거일 뿐**이다. 주행 중 5 s 공백이 같은 락 경합이었는지는 그 시각 역추적이 없어 **미확인**. 운용 대책으로 SLAM 생존 게이트 · BT 응답 기한 100 ms · MPPI 시각화 끄기를 넣었다.

---

## 1. 증상
- mp7(목표 (2.0, 0), BT 스무딩 fallback 첫 반영): **27 s ABORTED**, 1.72 m 주행, 통로 안, 접촉 없음(최근접 8 cm). [09-17 §5](../debug_log/2026-09-17/SUMMARY.md) · [`outputs/drive_mp7.txt`](../debug_log/2026-09-17/outputs/drive_mp7.txt)
- Nav2 이벤트(goal 기준, [`outputs/j379_mp7_events.txt`](../debug_log/2026-09-17/outputs/j379_mp7_events.txt)): 6.54 s 'Behavior Tree tick rate 100.00 was exceeded' → 11.36 · 11.47 s 'Control loop missed its desired rate of 10.0000Hz' → **11.55 · 11.57 · 11.63 · 11.66 s 'Timed out while waiting for action server to acknowledge goal request for compute_path…'**(4 회) → 전역 · 로컬 'clear except a region' → 11.66 s 'Running backup'(15.27 s 완료) → 19.63 · 20.69 s SmoothPath 충돌 판정 실패(새 fallback 으로 원경로) → 22.4 s 'Optimizer fail to compute path' → 27.1 s ack 타임아웃 연속 → Goal failed → 30.7 s~ 'Unable to transform robot pose into global plan's frame'.
- 주행 뒤([`outputs/j380_health.txt`](../debug_log/2026-09-17/outputs/j380_health.txt)): `/wheel_odom` 25.000 · `/imu/data` 199.859 · `/odometry/filtered` 29.657 · `/scan` 9.921 · 깊이 14.952 · `/tf` 29.262 Hz 정상인데 `map odom` 변환 칸이 빈칸. load 3.58.
- [`outputs/j381_slam.txt`](../debug_log/2026-09-17/outputs/j381_slam.txt): slam pid 12040 · 상태 `Sl` · 스레드 22, slam.log 36 줄 중 'queue is full' 28, `/map` hz 빈칸, `tf2_echo map odom` → 'Invalid frame ID "map" … frame does not exist'.
- [`outputs/j382.txt`](../debug_log/2026-09-17/outputs/j382.txt): 노드 목록에 slam **0**, `/map` 발행자 0, `/scan` 구독자 목록에 slam 없음(scan_deskew · stuck_monitor · 두 코스트맵만), 스레드 22 개 전부 `S` · wchan `futex_wait_queue_me`, 프로파일 env = UDP 전용 XML, 소켓 7, 5 s 동안 utime 1623 → 1628.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-17 §5 준비 | 재기동 · 게이트 · 목표 여유 게이트(`job377`) | 상자 1.207/+0.003, 창 0.231, (2.0, 0) 목표 여유 0.249 통과 | 주행 | [`outputs/prep_mp7.txt`](../debug_log/2026-09-17/outputs/prep_mp7.txt) |
| §5 주행 | mp7 | 27 s ABORTED(위 §1) | — | `drive_mp7.txt` · `j379_mp7_events.txt` · `mp7_nav2_tail.log` |
| §5 원인 추적 1 | `job380_health.sh` · `job381_slam.sh` · `job382_slamgraph.sh` | 센서 · EKF 정상, map→odom 없음, slam 프로세스 생존 · 그래프 없음 · 22 스레드 futex | **SLAM 이 그래프에서 사라진 채 정지**. 환경변수 프로파일은 UDP 전용 정상 → SHM 원인 아님(09-09 사고와 증상만 같음) | `j380_health.txt` · `j381_slam.txt` · `j382.txt` |
| §5 원인 추적 2 | `job383_slamlast.sh`(bag 의 `/tf` · `/map` 수신 시각) | map→odom 354 개(goal −5.6 ~ +30.1 s), **+6.8 s 에 5.1 s 공백**, +11.9 · +13.2 · +15.5 s 에 1.2~1.5 s, +18.0 s 에 3.1 s, 마지막 stamp 지연 4.84 s | 주행 중 SLAM 이 수 초씩 멈췄고 그 끝무렵 BT 타임아웃 — 시간 일치. 완전 정지는 bag 종료(+30 s) 뒤 | 출력 원천 소실(SUMMARY 서술) · bag `2026-09-17/bags/bag_mp7.tgz`(로컬) |
| §5 | slam.log 확인 | 기동(goal 약 340 s 전) 직후부터 — 첫 폐기는 goal 약 316 s 전 — 'Message Filter dropping … queue is full' 28 회, 정지 중에도 수 초 간격 | 평소에도 스캔을 다 못 먹는다 | [`outputs/mp7_slam.log`](../debug_log/2026-09-17/outputs/mp7_slam.log) |
| §5 | 전력 모드 확인(`job384` · `job385`) | nvpmodel 15 W(CPU 최대 1497 MHz) | 25 W 로 올리면 CPU +15 % 라는 제안 — **❌ §6.2 에서 틀림**([CPU 카드](cpu-load-stalls.md)) | 원천 소실 |
| §5 판정 | — | 루프 미달 mp5 0 → mp6 9 → mp7 60+(같은 설정에서 악화, 원인 미확정) | '**주행 로직 결함이 아니라 계산 자원 · SLAM 가용성 문제**'. 확정: 공백 ↔ BT 타임아웃 시간 일치, 최종 SLAM 무응답. 미확정: 공백 원인(CPU 굶주림 vs 내부 블로킹), 데드락 위치(gdb 는 `ptrace_scope=1` 이라 sudo 필요) | — |
| §5 조치 | BT 응답 기한 · 시각화 · top 기록 · SLAM 생존 게이트 | `default_server_timeout` 20 → 100 ms, `visualize` false, bag 에서 `/trajectories` 제외, `top -b -d 2` → `/tmp/top_<NAME>.log`, `job386_slamalive.py` | 정지한 SLAM 에서 게이트 FAIL 확인 | `nav2_params.yaml` · [`jobs/job386_slamalive.py`](../debug_log/2026-09-17/jobs/job386_slamalive.py) |
| **§6.1**(사용자 승인 1) | `run_slambt.sh` → `job387_slambt.sh`: `sudo gdb -p 12040 -batch … "info threads" "thread apply all bt 25"`(읽기 전용, 끝나면 detach) | 22 스레드 중 **6 개가 `__lll_lock_wait`**(뮤텍스 획득 대기), 나머지는 조건변수 · TBB 유휴. 스레드 16 = `SlamToolbox::publishTransformLoop → TransformBroadcaster::sendTransform → rmw_publish → DataWriterImpl::write → perform_create_new_change → (lock)` | **StatefulWriter 락 순서 역전 데드락** — 원격 구독자가 떠나는 순간. 최종 정지는 bag 기록기(/tf · /map 구독자) 종료(+30 s) 직후와 시간 일치 | [`outputs/slam_bt.txt`](../debug_log/2026-09-17/outputs/slam_bt.txt)(323 줄) |
| §6.1 | 설치 버전 · 후보 확인(`job388_pm25.sh` 의 앞부분) | `ros-humble-fastrtps` 설치 2.6.11-1jammy.20260214, 후보 2.6.12-1jammy.20260725. 릴리스 노트: 'Fix lock order inversion in StatefulWriter'(#6463, 'flowcontroler loi deadlock' — LocatorSelectorSender 와 FlowController 사이, 참가자 해체 중 다른 참가자가 계속 보낼 때) | 우리 역추적 경로와 **강하게 일치**. 스레드 8 의 #4 프레임이 심볼 없음(`??`)이라 완전한 동일성은 미확인. 후보 ① 2.6.12 ② CycloneDDS 교체(범위 큼) → ① 먼저 | [`outputs/j388_pm25.txt`](../debug_log/2026-09-17/outputs/j388_pm25.txt) 첫 블록 |
| **§6.3**(사용자 승인 2) | `run_fastdds.sh` → `job391_fastdds.sh`: 호스트 ROS 노드 정지(에이전트 컨테이너 유지) → `apt-get -s` 시뮬 → 설치 | 남은 호스트 ROS 프로세스 1(에이전트 `docker run` 줄), 시뮬 '1 upgraded … **Inst ros-humble-fastrtps** [2.6.11…] (2.6.12…)' 한 줄 → 설치 → `libfastrtps.so.2.6.12` | 다른 패키지 변경 0 확인 뒤 설치 | [`outputs/j391_fastdds.txt`](../debug_log/2026-09-17/outputs/j391_fastdds.txt) |
| §6.3 | `run_verify2612.sh`: `job392_rsp_start.sh`(robot_state_publisher 단독 기동 · 매핑 lib 확인) → `job240_clean.sh` → `job393_churn.sh` | RSP 가 `/opt/ros/humble/lib/libfastrtps.so.2.6.12` 매핑. 에이전트 세션 유지(보드 리셋 불필요), 자이로 캘리브 · map→odom 0. slam lib 2.6.12. **기준 측정 FAIL**(지연 0.55 s), 라운드 1 · 2 · 3 = 간격 0.06 · 0.05 · 0.07 s, 지연 −0.08 · 0.16 · 0.16 s **OK**, 그래프 slam 1, 'lock 대기' 14 | 정지 0 회 — **보조 증거, 증명 아님**(2.6.11 대조 없음 · 타이밍 의존). 게이트 지연 문턱 0.5 → **1.0 s**(간격 0.5 유지) | [`outputs/j392_393.txt`](../debug_log/2026-09-17/outputs/j392_393.txt) |
| §7 mp8 | 오늘 조치 전부(visualize off · BT 100 ms · fallback · 2.6.12 · 15 W) | **BT 타임아웃 0 · 제어 루프 미달 0 · SmoothPath 실패 0 · SLAM 생존(주행 후 간격 0.05 s)**. bag 25 MB(mp7 138 MB). top 50 샘플 load 평균 8.5 · controller_server 36 %(최대 70) · slam 7 % | 처음으로 '깨끗한' 주행. 목표 앞 정지는 다른 원인([데드밴드 카드](start-deadband.md)) | `j379_mp8_events.txt` · `prep_mp8.txt` |
| §9 ~ §13 mp9 ~ mp12 | 같은 구성 | 주행 후 SLAM 간격 0.05~0.06 s, 정지 재발 없음 | — | `j379_mp9~12.txt` · `prep_mp9~12*.txt` |
| 이후(09-28 · 10-12 · 10-21) | 게이트 C(= job386 기준) | 지연 2.38 · 1.32 · 1.05 s 로 **불합격 → 재시도 통과**(발행률 정상) | 데드락이 아니라 정상 SLAM 의 stamp 튐 — 10-27 에 기전이 밝혀짐([시각 정체 카드](slam-stamp-freeze.md)) | [09-28 SUMMARY](../debug_log/2026-09-28/SUMMARY.md) L66 · [10-12](../debug_log/2026-10-12/SUMMARY.md) L538 · [10-21 §9](../debug_log/2026-10-21/SUMMARY.md) |
| 이후(10-27 §24) | 게이트 B · C · G2 를 한 노드로 | C 기준 그대로(간격 < 0.5 · 지연 < 1.0 s) | `job386` 은 `chk_drive_gate.py` 로 흡수 | [`Docs/tools/chk_drive_gate.py`](../tools/chk_drive_gate.py) 머리 주석 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| mp7 실패는 주행 로직(MPPI · BT · 스무딩) 결함 | 이벤트 시각 ↔ map→odom 공백(bag) | 첫 실패(11.55 s ack 타임아웃)가 공백(+6.8 ~ +11.9 s) 끝무렵. 그 전 0~11 s 는 정상 | **기각** — 원인은 map 프레임 가용성 |
| 09-09 와 같은 SHM 문제 | 프로세스 env 의 프로파일 | UDP 전용 XML 정상 | **기각**(증상만 같음, [DDS 카드](dds-shm-incident.md)) |
| SLAM 이 CPU 를 못 받아 굶었다(최종 정지) | 스레드 상태 · utime | 22/22 futex, 5 s 동안 utime +5 tick(CPU 거의 안 씀), load 3.58 | **기각(최종 정지에 대해)** — 굶은 게 아니라 잠김 |
| Fast DDS 내부 데드락(락 순서 역전) | `gdb thread apply all bt` | 아래 §6.1 — 4 개 서로 다른 뮤텍스에 6 스레드, 그중 발견 · 송신 · 쓰기 경로가 서로 엇갈림. 릴리스 노트 #6463 과 일치 | **지지(강함)** — 뮤텍스 소유자를 직접 읽지 않아 '순환' 자체는 경로로 **추정**, `??` 프레임 1 개 |
| 방아쇠 = 원격 구독자(bag 기록기 · CLI)가 떠나는 순간 | 최종 정지 시각 ↔ bag 기록기 종료(+30 s) | 시간 일치(bag 은 +30.1 s 에 끝났고 마지막 stamp 지연이 이미 4.84 s) | **지지(정황)** — '직후' 의 정확한 시각은 bag 이 끝나서 안 보임 |
| 주행 중 5.1 s 공백도 같은 락 경합(짧은 구독자가 떠날 때 `/tf` 쓰기 막힘) | 그 시각 역추적 | 없음 | **미확인** — 대안 'CPU 굶주림'(queue is full 28 회, 루프 미달 60+)도 남음 |
| 2.6.12 가 이 데드락을 고친다 | 유발 조건 스트레스(`job393`) 3 라운드 | 정지 0, 간격 0.05~0.07 s | **지지(약함)** — 2.6.11 에서 같은 시험을 안 했다(재현 여부부터 모름). 이후 실주행에서 재발 기록 없음(정황) |

## 4. 조치와 효과
| 바꾼 것 | 전 → 후 | 효과(측정) | 한계 |
|---|---|---|---|
| Fast DDS | `ros-humble-fastrtps` 2.6.11 → 2.6.12(호스트 노드 전부. micro-ROS 에이전트는 컨테이너 자체 Fast DDS 라 무관) | 스트레스 3 라운드 정지 0. mp8~mp12 주행 후 SLAM 생존 | 증명 아님. 저장소 밖(Jetson apt) 변경이라 재설치 · 이미지 복구 때 되돌아갈 수 있음 — 저장소에 이 버전 고정 기록은 SUMMARY · 메모뿐 |
| BT 응답 기한 | `bt_navigator.default_server_timeout` 20 → **100 ms** | mp8 BT 타임아웃 0 | 공백이 100 ms 보다 길면 같은 복구 진입. 현재 `nav2_params.yaml:21` 이 100(10-30 확인) |
| MPPI 시각화 | `visualize` true → **false**, bag 에서 `/trajectories` 제외 | mp8 bag 25 MB(mp7 138 MB), 루프 미달 0 | 각 몫(시각화 vs bag vs 2.6.12)은 안 나눔. 현재 `nav2_params.yaml:248` false(10-30 확인). 10-12 의 `mppi_viz` 포화 문제와 같은 계열 |
| SLAM 생존 게이트 | 없음 → 5 s 동안 map→odom 수신 간격 최대 < 0.5 s · stamp 지연 최대 < 1.0 s(처음 0.5, 같은 날 1.0 으로) | 정지한 SLAM 에서 FAIL, 정상 SLAM 에서 OK | 지연 기준은 정상 SLAM 의 stamp 튐(정합 중 정체)에도 걸려 이후 '재시도로 통과' 가 반복됨(§2 이후 행) |
| 주행 중 top 기록 | 없음 → `top -b -d 2` 를 `/tmp/top_<NAME>.log` 로, `job379` 가 프로세스별 평균 · 최대 | 다음 공백 때 범인 확인용 | 2 s 간격이라 1~2 s 공백은 놓칠 수 있음 |
| 운용 규칙 | 주행 중 `/tf` 구독 CLI(`tf2_echo` 등) · 짧은 노드 금지, bag 은 SLAM 재기동 전에만 끄기 | — | 이후 '주행 30 s 전 DDS 참여자 생성 금지'(09-21) 규칙으로 일반화 |

## 5. 내 실수
### 실수 ① 'CPU 굶주림' 을 먼저 세우고, 정지 원인을 전력 모드로 풀려 함 (09-17 §5 → §6)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | mp7 의 SLAM 공백 · 정지 원인을 찾고 대책을 정하기 |
| 본 것 | slam.log 'queue is full' 28 회, 루프 미달 mp5 0 → mp6 9 → mp7 60+, 그리고 정지한 SLAM 의 22 스레드 전부 futex |
| 처음 추론 | '주행 중 SLAM 이 **굶주려** map 프레임이 멈췄다' → 대책 후보로 전력 모드 15 W → 25 W('CPU +15 %')를 사용자 결정 항목에 올림 |
| 의심한 이유 | 최종 정지는 CPU 를 거의 안 쓰는(utime 5 s 에 +5 tick) **잠김**이었다 — 굶주림이면 CPU 를 쓰려고 해야 한다. 그래서 역추적이 필요했고(사용자 승인), 25 W 는 실제로 CPU 상한을 낮췄다([CPU 카드 실수](cpu-load-stalls.md)) |
| 판별 | `gdb` 역추적 → Fast DDS 뮤텍스 대기 6 스레드 · `/tf` 쓰기 스레드 정지 |
| 결론 | **최종 정지는 굶주림이 아니라 라이브러리 데드락**. 주행 중 공백의 원인은 여전히 둘 중 미정. 25 W 는 같은 승인 범위에서 15 W 로 되돌림 |
| 다음에 알아보는 법 | '프로세스는 사는데 응답이 없음' 이면 **CPU 사용 여부부터**: 쓰고 있으면 바쁜 것(굶주림 · 무한 루프), 안 쓰면 잠긴 것(락 · I/O 대기) → 잠김이면 스레드 역추적(`gdb -p … thread apply all bt`)이 1 순위. 'futex 대기' 자체는 유휴 스레드도 다 그렇다(§6.2) — 판별은 **어떤 함수에서** 기다리는지 |
| 데이터 | [`outputs/j382.txt`](../debug_log/2026-09-17/outputs/j382.txt) · [`outputs/slam_bt.txt`](../debug_log/2026-09-17/outputs/slam_bt.txt) · [`outputs/mp7_slam.log`](../debug_log/2026-09-17/outputs/mp7_slam.log) · [09-17 §5 · §6](../debug_log/2026-09-17/SUMMARY.md) |

## 6. 원문 대조 · 이번에 따져 본 것
### 6.1 `slam_bt.txt` 를 다시 읽기 — 누가 무엇을 기다리나
`info threads` 표와 각 스레드 역추적(`#0 futex_wait … futex_word=<주소>`)에서 기다리는 뮤텍스 주소를 맞춰 보면:

| 스레드(LWP) | 하는 일(역추적 위쪽 프레임) | 기다리는 뮤텍스 |
|---|---|---|
| 4 (12050) | 타이머 이벤트 `StatefulWriter::perform_nack_response` | `0x…de155530` |
| **16** (12062) | SLAM `publishTransformLoop → sendTransform → rmw_publish → DataWriterImpl::write → perform_create_new_change` | `0x…de155530` (스레드 4 와 같음 — 같은 Writer 로 **추정**) |
| 5 (12051) · 7 (12053) | UDP 수신 `MessageReceiver::processCDRMsg → PDP::assert_remote_participant_liveliness` | `0x…dde6be80` (PDP 쪽) |
| **6** (12052) | 발견(EDP) 수신 `EDPSimpleSUBListener::onNewCacheChangeAdded → PDP::removeReaderProxyData → EDP::unpairReaderProxy → StatefulWriter::matched_reader_remove → check_acked_status → DataWriterHistory::remove_change_pub → … → StatefulWriter::change_removed_by_history → ??` | `0x…ddfb4a78` |
| **8** (12054) | 흐름 제어기 `FlowControllerImpl<SyncPublishMode, Fifo>::run → RTPSMessageGroup::flush_and_reset → flush → send → ??` | `0x…de155a80` |

- 네 개의 서로 다른 뮤텍스에 6 스레드. SUMMARY 의 그림('스레드 6 이 쓰기 쪽 락을 쥔 채 다른 락 대기 ↔ 스레드 8 이 송신 중 락 대기')은 **경로로 읽은 것**이다 — gdb 로 각 뮤텍스의 `__owner` 를 찍지 않아 '누가 쥐고 있나' 는 직접 확인하지 않았다(**추정**). 스레드 6 · 8 의 마지막 프레임이 둘 다 심볼 없는 `??`(SUMMARY 는 8 번만 언급).
- 스레드 6 이 PDP 경로(`removeReaderProxyData`) 안에 있으므로 5 · 7 이 기다리는 PDP 뮤텍스를 6 이 쥐고 있을 가능성이 높다(SUMMARY 표의 'PDP 락(스레드 6 이 보유)') — 이것도 경로 추론.
- 그래서 '락 순서 역전' 판정의 근거는 ① 이 경로 모양 ② 같은 경로를 설명하는 상류 수정(#6463) — 두 가지. 실험으로 재현 · 소거한 것은 아니다.
### 6.2 'futex 대기' 는 판별 서명이 아니다
- `j382.txt`: 정지한 SLAM 의 22 스레드 전부 `futex_wait_queue_me`. 그런데 2.6.12 로 올린 뒤 **정상 동작하는** SLAM 에서 `job393` 이 같은 방식으로 센 'lock 대기' 도 **14**(`j392_393.txt` 마지막 줄)였다. 유휴 스레드(조건변수 · TBB 작업자 · WaitSet)는 평소에도 futex 에서 잔다.
- 따라서 SUMMARY §5 의 '22 스레드 전부 futex 대기' 는 이상 신호이긴 하지만(평소엔 일부가 깨어 있음) 그 자체로 데드락의 증거는 아니다. 결정적인 것은 그래프 소실 · map→odom 없음 · CPU 0 근처, 그리고 역추적의 **뮤텍스(`__lll_lock_wait`)** 대기 위치였다. `job393` 의 'lock 대기' 칸 이름은 오해를 부른다(실제로는 wchan 이 futex 인 스레드 수).
### 6.3 그 밖의 대조
1. **'CPU ≈ 0.5 %/s'**(§5) ↔ `j382.txt`: `ps -o pcpu` 5.5(**프로세스 수명 평균**), utime 1623 → 1628(약 5 s 사이 +5 tick). 리눅스 기본 tick 100 Hz 라면 0.05 s / 5 s ≈ 1 %(계산 · tick 값은 기록 안 됨 — **추정**). 어느 쪽이든 '거의 0' 이라는 결론은 같다.
2. **'그 공백이 끝나는 11.4 s 에'**(§5) ↔ 공백 시작 +6.8 + 5.1 = 약 +11.9 s, `j379_mp7_events.txt` 의 첫 ack 타임아웃 11.55 s(루프 미달 11.36 s). 타임아웃은 공백이 끝나기 직전에 났다. 결론(시간 일치)은 그대로.
3. **job383 출력 원문 없음** — map→odom 354 개 · 공백 목록 · 지연 4.84 s 는 SUMMARY 서술이 유일. bag(`bag_mp7.tgz`, 로컬)이 있어 `job383` 을 다시 돌리면 재현 가능.
4. **ICP 결과 없음과 같은 날의 다른 공백**: (이 카드 밖) `run_j369.sh` 의 ICP(`job370`) 출력도 비어 있다 — [계측 카드](avoid-run-metrics.md).
5. **2.6.12 설치 시 남은 호스트 ROS 프로세스 1** — `j392_393.txt` 첫 줄이 그 정체: `docker run --rm --name microros_agent …` 줄(에이전트 컨테이너를 띄운 명령)이라 의도대로 유지된 것.

## 7. 남은 것
- 주행 중 5.1 s 공백의 원인(CPU 굶주림 vs 같은 락 경합) — 미확정. 이후 SLAM 쪽 정체는 10-27 에 '위치 추정 정합(LinkNearChains) 동안 stamp 정체' 라는 **다른** 기전으로 측정됐다([시각 정체 카드](slam-stamp-freeze.md)) — mp7 의 공백이 그 기전이었는지는 그때(매핑 모드 · 09-17 slam_toolbox apt 판) 로그가 없어 **미확인**.
- 2.6.11 에서의 재현 시험 — 안 함(이제 되돌릴 이유도 약함).
- Fast DDS 버전 고정을 저장소에 기록하는 곳(설치 절차 문서) — `Docs/03_jetson/` 쪽 확인 필요(이 카드에서는 확인 안 함).
- SLAM 생존 게이트 C 의 지연 기준(1.0 s)이 정상 SLAM 의 stamp 튐을 FAIL 로 보는 문제 — 지금 `chk_drive_gate.py` 도 같은 기준(10-30 확인: 6 · 47~48 행). 러너가 재시도로 넘기는 운용.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| mp7 | 27 s ABORTED, SLAM 정지 | 09-17 §5, `drive_mp7.txt` · `j379_mp7_events.txt` · `mp7_slam.log` · `mp7_sensors.log` · `mp7_nav2_tail.log`, bag `bag_mp7.tgz`(로컬) |
| 원인 추적 | 상태 · SLAM · 그래프 · bag 공백 | `job380` · `job381` · `job382` · `job383`, `j380_health.txt` · `j381_slam.txt` · `j382.txt` |
| 역추적 | gdb | `job387_slambt.sh` · `run_slambt.sh`, `slam_bt.txt` |
| 버전 · 설치 · 검증 | 2.6.12 | `job388_pm25.sh`(버전 목록 부분) · `job391_fastdds.sh` · `run_fastdds.sh` · `job392_rsp_start.sh` · `job393_churn.sh` · `run_verify2612.sh`, `j388_pm25.txt` · `j391_fastdds.txt` · `j392_393.txt` |
| 게이트 | SLAM 생존 | `job386_slamalive.py` → `Docs/tools/chk_drive_gate.py`(10-27) |
| 사후 이벤트 집계 | nav2.log · 드라이브 표 · top | `job379_navevents.sh` |
| mp8 ~ mp12 | 조치 뒤 주행 | 09-17 §7 · §9~§13 |

## 9. 도구 해설
공통 실행: PC 스크래치패드(`82ce61d4-…/scratchpad`, 지금 자동 정리로 소실) → WSL `run_*.sh`(`sshpass -p <PW>`, CR 제거 후 `scp`) → Jetson `/tmp`. Jetson 쪽 스크립트는 맨 앞에서 `FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/…/fastdds_udp_only.xml` 을 절대 경로로 export(09-17 §0: 러너 ssh 큰따옴표 안의 `$HOME` 이 WSL root 에서 먼저 풀려 `/root/…` 가 되던 결함을 고친 뒤). sudo 가 필요한 것(`job387` · `job388` · `job390` · `job391`)은 저장소 사본에 `__PW__` 자리표시자가 있고 감싸개가 전송 직전에 `sed` 로 넣은 뒤 실행 후 원격 파일을 지운다(저장소 사본은 `<PW>` 로 가림).

**도구 계보**: 사후 집계 `job379_navevents.sh` → 상태 `job380_health.sh` → SLAM `job381_slam.sh` → 그래프 · 스레드 `job382_slamgraph.sh` → bag 공백 `job383_slamlast.sh` → 게이트 `job386_slamalive.py` → (승인) 역추적 `job387_slambt.sh` → 버전 `job388_pm25.sh` 앞부분 → (승인) 설치 `job391_fastdds.sh` → 검증 `job392_rsp_start.sh` → `job393_churn.sh`(안에서 `job386` 을 4 번). 게이트 계보: `job386`(09-17, 같은 날 mp8 준비부터) → 러너 게이트 C(이후 러너들 — 10-27 직전엔 `job551` — 가 따로 띄움) → `Docs/tools/chk_drive_gate.py` 의 C(10-27, 한 노드로).

### 9.1 `job379_navevents.sh` — 주행 뒤 nav2 이벤트 · 드라이브 표 · bag 압축 · SLAM 생존 · top 요약
- 실행 위치 · 형태: Jetson, `bash job379_navevents.sh [NAME=mp7]`. 로버 안 움직임.
- 왜: 실패한 주행에서 '무슨 일이 언제' 를 goal 기준 시각으로 한 화면에.
- 하는 일: ① `/tmp/nav2.log` 에서 마지막 'Begin navigating' 이후 줄을 goal 기준 초로(경로 전달 · 스무딩 요청 · StaticLayer 크기 조정 줄 제외) ② `/tmp/drive_<NAME>.log` 표를 10 줄마다(1 s) ③ `/tmp/bag_<NAME>` 를 tgz 로 ④ `job386_slamalive.py` 로 주행 후 SLAM 생존 ⑤ `tf2_echo map base_link` ⑥ `/tmp/top_<NAME>.log`(2 s 스냅샷)에서 프로세스별 평균 · 최대 %CPU 와 load 평균 · 최대(첫 스냅샷 제외).
- 출력: `outputs/j379_mp7_events.txt` 등(mp7 은 이벤트 부분만 남음 — 그때는 top 기록 전).
- 결과가 쓰인 곳: 09-17 §5 Nav2 이벤트 표, §7 이후 top 수치.
- 알려진 결함: 'Begin navigating' 이 여러 번이면 마지막 것만. top 평균의 분모가 '스냅샷 수 − 1' 이라 중간에 사라진 프로세스는 낮게 나옴. 주행 직후 `job386` · `tf2_echo` 로 DDS 참여자를 만듦(주행 뒤라 무해).
- 지금 다시 쓸 수 있나: 개념은 예 — 지금은 러너 · `Docs/tools/` 의 anal_ 도구들이 대신.

### 9.2 `job380_health.sh` — 주행 뒤 전체 상태 한 장
- 실행 위치 · 형태: Jetson, 인자 없음.
- 하는 일: 프로세스 12 종 `pgrep -fc` 개수 → 토픽 6 개 hz(각 6 s) → `tf2_echo odom base_link` · `map odom` 의 'At time' · Translation → `/odometry/filtered` · `/scan` stamp → `top -bn1` 상위 10 · load · 최고 온도 → sensors.log WARN/ERROR 끝 3 · slam.log 끝 2 → syslog 의 그 시각 Wi-Fi 끊김 · IP.
- 출력: [`outputs/j380_health.txt`](../debug_log/2026-09-17/outputs/j380_health.txt).
- 읽는 법 · 결함: `micro_ros_agent:2` 는 `docker run` 명령 줄 + 컨테이너 안 프로세스가 둘 다 이름에 걸린 것으로 **추정**(중복 아님). `map odom` 칸이 **빈칸** = 변환 없음 — 이 도구는 실패 문구를 따로 안 찍는다(빈칸 = 무응답, 1 기부터의 공통 결함). `top -bn1` 첫 화면은 직전 구간 값이 아니다.
- 지금: 같은 역할은 `Docs/tools/chk_prep.py` · prep 출력이 대신.

### 9.3 `job381_slam.sh` — SLAM 프로세스 · 로그 · 발행
- 하는 일: `async_slam_toolbox_node` pid 의 상태 · %CPU · 경과 · RSS · 스레드 수 → slam.log 줄 수 · 'queue is full' 수 · 끝 3 줄 → `/map` hz(12 s) → `tf2_echo map odom`(10 s) → `/tf` 에서 `child_frame_id: odom` 앞 stamp → 현재 epoch → 설치 slam yaml 의 주요 파라미터.
- 출력: [`outputs/j381_slam.txt`](../debug_log/2026-09-17/outputs/j381_slam.txt) — `throttle_scans 1 · transform_publish_period 0.05 · map_update_interval 2.0 · resolution 0.05 · minimum_time_interval 0.1` 도 여기서.
- 결함: `/tf` echo 의 `grep -B3` 은 메시지 형식에 의존(이 회차는 빈칸 = map→odom 없음). 지금: 쓰지 않음.

### 9.4 `job382_slamgraph.sh` — 그래프 · 스레드 · 환경 ★ '살아 있는데 사라짐' 판별
- 하는 일: `ros2 daemon stop`(캐시된 그래프 대신 새로 탐색) → `node list` 에 slam 수 → `/map` 발행자 수 → `/scan` 구독자 노드 이름 → `/proc/<pid>/task/*/stat` 3 번째 칸(상태) 집계 → `/proc/<pid>/task/*/wchan`(커널 대기 함수) 집계 → `/proc/<pid>/environ` 의 FASTRTPS 변수 → 소켓 fd 수 → 3 s 뒤 `pcpu` · utime(`/proc/<pid>/stat` 14 번째 칸) → 5 s 뒤 utime.
- 출력: [`outputs/j382.txt`](../debug_log/2026-09-17/outputs/j382.txt).
- 결과가 쓰인 곳: §5 '그래프에서 사라짐 · 22 스레드 futex · SHM 원인 아님'.
- 결함: §6.2(futex 수는 판별 서명이 아님), §6.3 ①(pcpu 는 수명 평균). 지금 다시 쓸 수 있나: 예 — 같은 서명(프로세스 생존 · 그래프 없음)의 첫 진단으로 유효.

### 9.5 `job383_slamlast.sh` — bag 에서 map→odom 이 언제 끊겼나
- 하는 일: `ptrace_scope` · `gdb` · `eu-stack` 유무 출력(역추적 가능성 확인) → 파이썬으로 `/tmp/bag_mp7` 의 `/tf` 를 읽어 `frame_id == 'map'` 인 변환의 (수신 시각, stamp) 목록, `child == base_link` 마지막, `/map` 수신 시각 → goal 기준(`G = 1789610470.807` 하드코딩) bag 범위, map→odom 개수 · 마지막 수신 · 지연 · 0.5 s 넘는 간격 8 개.
- 출력: 원문 **원천 소실**(SUMMARY §5 에 값). bag 은 로컬에 있음.
- 결함: goal 시각 · bag 이름 하드코딩. 'map' 부모 변환이면 전부 셈(이 스택에선 map→odom 뿐). slam 이 같은 stamp 를 두 번 발행하는 성질(CLAUDE.md §6)을 고려 안 함 — 개수가 부풀 수 있음(간격 판정엔 영향 작음, **추정**).
- 지금: `Docs/tools/` 의 bag 분석 도구가 대신.

### 9.6 `job386_slamalive.py` — SLAM 생존 게이트 (5 s)
- 실행 위치 · 형태: Jetson, 인자 없음. 마지막 줄 `OK` / `FAIL` 을 감싸개 · 러너가 읽음.
- 왜: slam_toolbox 프로세스가 살아 있어도 그래프에서 사라지거나 map→odom 이 끊길 수 있다 — 출발 전에 막으려고.
- 하는 일: `/tf` 구독(depth 100) → `frame_id == 'map' · child == 'odom'` 이면 (지금 ROS 시각, 지금 − stamp) 기록 → 5 s → 2 개 미만이면 'SLAM 무응답' FAIL, 아니면 최대 간격 · 최대 지연 출력 후 `간격 < 0.5 and 지연 < 1.0` 이면 OK.
- 출력: 한두 줄. 예 `map->odom 98 개/5 s, 최대 간격 0.05 s, 최대 stamp 지연 0.55 s` / `FAIL`(`j392_393.txt` 기준 측정).
- 결과가 쓰인 곳: 09-17 이후 모든 러너 게이트 C, `job379` · `job393` 안.
- 계보: 지연 문턱 0.5 → 1.0 s(09-17 §6.3, 정상 SLAM 지연 −0.08~+0.55 s) → 10-27 `chk_drive_gate.py` C 로 흡수(기준 그대로).
- 알려진 결함: ① 지연 기준이 정상 SLAM 의 정합 중 stamp 정체(0.5~1.3 s, 10-27)에도 걸림 → 09-28 · 10-12 · 10-21 불합격 · 재시도. ② 새 노드를 만들어 5 s 듣는다 — 주행 직전 DDS 참여자 생성(지금 규칙 위반 소지) → 10-27 에 게이트를 한 노드로 묶은 이유. ③ 같은 stamp 두 번 발행이면 간격 0 이 섞임(최대값엔 영향 없음).
- 지금 다시 쓸 수 있나: 단독으로는 안 씀 — `chk_drive_gate.py` 를 쓴다.

### 9.7 `job387_slambt.sh`(+ `run_slambt.sh`) — 정지한 SLAM 의 전 스레드 역추적 (사용자 승인)
- 실행 위치 · 형태: Jetson, sudo. 감싸개가 `__PW__` 를 넣어 올리고 실행 뒤 원격 파일 삭제, `/tmp/slam_bt.txt` 를 PC 로 회수.
- 왜: 정지 위치를 추측이 아니라 코드 경로로 보려고. `ptrace_scope=1` 이라 남의 프로세스 attach 에 sudo 필요(`job383` 이 확인).
- 하는 일: `gdb -p <pid> -batch -nx -ex "set pagination off" -ex "set print thread-events off" -ex "info threads" -ex "thread apply all bt 25"` → 파일. 읽기 전용 attach — 끝나면 detach, 앞뒤 `ps` 상태 출력.
- 출력: [`outputs/slam_bt.txt`](../debug_log/2026-09-17/outputs/slam_bt.txt)(323 줄: LWP 목록 · `info threads` 22 줄 · 스레드별 최대 25 프레임).
- 결과가 쓰인 곳: §6.1 판정 · 2.6.12 결정.
- 알려진 결함: 뮤텍스 소유자(`p *(pthread_mutex_t*)<주소>` 의 `__owner`)를 안 찍어 순환을 직접 증명하지 못함(§6.1). libfastrtps 디버그 심볼이 없어 `??` 프레임.
- 지금 다시 쓸 수 있나: 예 — 같은 서명이 나오면 1 순위(사용자 승인 필요, 재기동 **전에만** 가능). 다음엔 `__owner` 출력을 추가.

### 9.8 `job388_pm25.sh` 의 앞부분 — DDS 패키지 버전 · 후보
- 하는 일(이 카드 관련 부분): `ros-humble-fastrtps` · `fastcdr` · `rmw-fastrtps-cpp` · `rmw-cyclonedds-cpp` · `cyclonedds` 의 설치 버전(`dpkg-query`)과 후보(`apt-cache policy`).
- 출력: [`outputs/j388_pm25.txt`](../debug_log/2026-09-17/outputs/j388_pm25.txt) 첫 블록 — fastrtps 2.6.11 → 후보 2.6.12, CycloneDDS 미설치(후보 1.3.5 / 0.10.5). 뒷부분(전력 모드 전환)은 [CPU 카드](cpu-load-stalls.md).

### 9.9 `job391_fastdds.sh`(+ `run_fastdds.sh`) — Fast DDS 2.6.12 설치 (사용자 승인)
- 실행 위치 · 형태: Jetson, sudo. 감싸개가 비밀번호를 넣고 끝에 'exit <코드>' 를 찍은 뒤 원격 파일 삭제.
- 하는 일: ① 호스트 ROS 노드 23 패턴 `pkill -TERM` → 최대 15 s 대기 → 남으면 `-9`(에이전트 컨테이너는 패턴에 없어 유지) → 남은 호스트 ROS 프로세스 수 · 에이전트 수 ② 설치 전 버전 ③ `apt-get -s install --only-upgrade --no-install-recommends ros-humble-fastrtps` **시뮬레이션** — `Inst`/`Remv` 줄 중 fastrtps · fastcdr 외가 하나라도 있으면 **exit 2 로 중단**(사용자 확인 필요) ④ 실제 설치(noninteractive) ⑤ 설치 후 버전 · `libfastrtps.so*` 목록.
- 출력: [`outputs/j391_fastdds.txt`](../debug_log/2026-09-17/outputs/j391_fastdds.txt).
- 알려진 결함: 정지에 `-9` 를 섞는다(09-09 이후 규칙은 TERM 후 대기 · 남은 것만 `-9` 라 규칙 범위 안). 설치 후 재기동 · 검증은 다른 스크립트(`run_verify2612.sh`).
- 지금 다시 쓸 수 있나: 패키지 하나만 올리는 '시뮬 → 범위 확인 → 설치' 형태는 그대로 쓸 만함.

### 9.10 `job392_rsp_start.sh` · `run_verify2612.sh` — 재기동과 새 라이브러리 매핑 확인
- `job392`: 남은 ROS 프로세스 목록 → `description.launch.py`(robot_state_publisher) 단독 기동 → 6 s 뒤 그 프로세스의 `/proc/<pid>/maps` 에서 `libfastrtps` 경로 = **실제로 2.6.12 를 물었나**.
- `run_verify2612.sh`(PC WSL): `job392` · `job393` · `job386` 전송 → `job392` → `job240_clean.sh`(base 유지 · 센서 · SLAM · Nav2) → `job393`.
- 출력: [`outputs/j392_393.txt`](../debug_log/2026-09-17/outputs/j392_393.txt) 앞부분(RSP 1 · `libfastrtps.so.2.6.12`, job240 '에이전트 살아 있고 보드 송수신 정상 → base 재기동 생략(세션 유지)').
- 결함 · 지금: RSP 를 launch 가 아닌 곳에서 따로 띄우면 이후 기동과 겹칠 수 있음(job240 이 base 계층 RSP 1 개를 기대하므로 맞춰 둔 것). 지금 쓰지 않음.

### 9.11 `job393_churn.sh` — 유발 조건 스트레스 (구독자 생성 · 해체 반복)
- 실행 위치 · 형태: Jetson, 인자 없음. 로버 정지.
- 왜: 데드락의 방아쇠로 본 '원격 구독자 해체' 를 일부러 반복해 2.6.12 에서 SLAM 이 버티는지.
- 하는 일: slam 이 매핑한 libfastrtps 경로 → 기준 `job386` → 라운드 1~3: `timeout -s INT 6 ros2 bag record /tf /tf_static /map /scan`(6 s 기록 후 해체, 파일 삭제) + `ros2 topic echo /tf --once` · `/map --once --no-arr` 를 8 번씩(= 단발 구독자 16 개 생성 · 해체) → `job386` → 끝에 slam 노드 수 · wchan 이 futex 인 스레드 수.
- 출력: [`outputs/j392_393.txt`](../debug_log/2026-09-17/outputs/j392_393.txt) 뒷부분 — 기준 FAIL(지연 0.55) · 라운드 1~3 OK · 그래프 1 · 'lock 대기' 14.
- 결과가 쓰인 곳: §6.3 '정지 0 회' · 게이트 지연 문턱 1.0 s.
- 알려진 결함: ① 대조군(2.6.11) 없음 — 이 시험이 2.6.11 에서 데드락을 일으키는지조차 모름. ② 3 라운드는 타이밍 의존 버그에 비해 작다. ③ 마지막 칸 이름 'lock 대기' 가 실제로는 futex 대기 스레드 수(§6.2). ④ 라운드 2 의 map→odom 수 57 개/5 s(다른 라운드 98~100) — 원인 기록 없음(측정 노드가 늦게 붙었을 가능성, **추정**).
- 지금 다시 쓸 수 있나: DDS 라이브러리를 바꿀 때 회귀 확인용으로 쓸 만함 — 대조군과 함께.

## 10. 용어
- **Fast DDS(eProsima, 패키지 이름 `ros-humble-fastrtps`)**: ROS 2 Humble 기본 미들웨어(RMW) 구현. 노드 사이 토픽은 이 라이브러리의 Writer/Reader 로 오간다.
- **참가자(participant) · 발견(PDP / EDP)**: DDS 에서 프로세스(노드 묶음) 단위 = 참가자. PDP 는 참가자끼리, EDP 는 Writer/Reader 끼리 서로를 알리고 짝짓는 발견 프로토콜. 상대가 떠나면 EDP 가 짝을 푼다(`unpairReaderProxy`).
- **StatefulWriter**: 신뢰성(RELIABLE) 토픽의 Writer — 짝지은 Reader 마다 무엇을 보냈고 무엇을 확인(ACK)받았는지 상태를 들고 있다. Reader 가 떠나면 `matched_reader_remove` 로 그 상태를 지우고 확인이 끝난 샘플을 기록(history)에서 치운다.
- **흐름 제어기(FlowController)**: 보낼 샘플을 모아 실제 소켓 전송을 하는 스레드. 'SyncPublishMode · Fifo' 는 동기 발행 · 선입선출 모드.
- **lock-order inversion(락 순서 역전)**: 스레드 A 는 락 X 를 쥐고 Y 를, 스레드 B 는 Y 를 쥐고 X 를 기다리는 식으로 두 경로가 **반대 순서**로 락을 잡아 서로 영원히 기다리는 데드락. 타이밍이 맞을 때만 나서 재현이 어렵다.
- **futex**: 리눅스의 사용자 공간 뮤텍스 · 조건변수가 기다릴 때 들어가는 커널 대기(fast userspace mutex). `wchan = futex_wait_queue_me` 는 '무언가를 기다리며 잠듦' 일 뿐, 뮤텍스(`__lll_lock_wait`)인지 조건변수(`pthread_cond_wait`)인지는 역추적으로 봐야 한다.
- **gdb `thread apply all bt N`**: 붙은 프로세스의 모든 스레드에 대해 콜 스택 위쪽 N 프레임을 찍는 명령. `-batch` 는 명령을 실행하고 바로 끝냄(detach). `-p <pid>` 로 실행 중 프로세스에 attach.
- **`ptrace_scope`**: 다른 프로세스에 디버거를 붙일 수 있는 범위를 정하는 커널 설정. 1 이면 자기 자식만 → 실행 중인 노드엔 sudo 필요.
- **BT 응답 기한(`default_server_timeout`)**: bt_navigator 가 액션 서버(planner · controller 등)에 목표를 보내고 '받았다(ack)' 를 기다리는 시간. 넘으면 그 노드는 실패로 처리되고 복구 분기로 간다. map 프레임이 멈추면 서버들이 바빠 이 기한을 못 지킨다.
- **map→odom 생존 게이트(게이트 C)**: 출발 전 5 s 동안 SLAM 의 map→odom 이 끊김 없이(간격 < 0.5 s) · 늦지 않게(지연 < 1.0 s) 오는지 보는 검사.
- **stamp 지연**: 받은 시각 − 메시지에 찍힌 시각. 음수는 두 시계 차 또는 미래 stamp(slam 의 `transform_publish_period` 앞당김) 때문.
