# 2026-09-17 — mp6 (목표 2.2/0): 상자 옆·뒤 통과 성공, 복귀 회전은 여유 수 cm, 목표가 벽에 가까워 목표 앞 정체

전날 기록: `../2026-09-16/SUMMARY.md` (§1.15 mp5, §2 다음). 이 문서는 재부팅 뒤 기동, 상자 위치 오측정의 원인, mp6 결과와 조치다.

- bag: `bags/bag_mp6.tgz` (git 제외), 시계열 `outputs/mp6.csv`, 드라이브 로그 `outputs/drive_mp6.txt`
- 분석: `outputs/j369_370.txt`(상자 거리 교차검증), `outputs/j371.txt`(고친 감사·코스트맵 비교), `outputs/j374_mp6.txt`(모서리 구간 표·ASCII), `outputs/j376_mp6.txt`(목표 부근 코스트맵)

## 0. 기동
- 사용자: 로버를 초기 위치로 돌리고 Jetson 재부팅. Jetson 은 **WEB_DEV_5G 192.168.0.101** (우선순위 20/5 유지). 설치된 yaml·BT·릴레이·fastdds XML 은 재부팅 후에도 전날 배포 상태 그대로(job367).
- `job240_clean.sh`: 에이전트를 새로 띄웠는데 **보드 리셋 없이 세션이 맺어졌다**(/wheel_odom 25 Hz). 자이로 캘리브·map→odom 0.
- 러너 결함 수정: ssh 큰따옴표 안의 `FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/...` 가 WSL(root) 에서 먼저 풀려 `/root/...`(없는 파일)가 됐다 → 115 개 러너를 `/home/jetson/...` 절대경로로. 런치로 뜬 노드는 자체 경로를 써서 영향 없었고, CLI 도구만 기본 전송(SHM 포함)으로 떴다(통신은 UDP 로 됨).

## 1. 상자 위치 오측정 — 감사 스크립트 결함 (내 실수로 사용자가 로버를 잘못 옮김)
**경과**: 첫 게이트가 상자 전면 x **1.056**(어제 mp5 1.174) → 어제 배치에 맞추려면 로버를 12 cm 뒤로 옮기라고 안내 → 사용자가 옮김 → 재기동 뒤 게이트가 **0.957**(더 가까움)을 보고. 옮긴 방향과 반대.
**교차검증 (주행 보류)**
| 측정 | 상자 전면 x (base) | 근거 |
|---|---|---|
| 게이트 감사(job248) | 0.957 | y 1D 군집 + x 5 % 분위 |
| 컬러 영상 기하(fx≈385, 카메라 높이 0.143) | ≈1.38 | 상자 아래 모서리 행 288(어제 305), 위 모서리 행이 같은 모델로 1 px 내 일치; 어제 영상·깊이 쌍은 3 px 내 일치 |
| 원시 깊이 영상 `/camera/camera/depth/image_rect_raw` (job369) | **1.346** | 낮은 화소 238 중 153 이 카메라 1.1 m 대역 |
| 원시 포인트클라우드 | **1.345** | 158 점 |
| 필터 구름(릴레이 출력, Nav2 입력) | **1.345** | 147 점, 전부 1.3 m 대역 |
| 로컬 코스트맵 상자 셀 | 1.325~1.425 | + 우측 바닥점 2 셀 (0.93~0.98, −0.225) |
**원인**: 감사(job248)와 주행 스크립트(job125)의 상자 검출이 점을 **y 간격으로만** 묶고 5 % 분위 x 를 전면으로 썼다. 원시 구름의 바닥 잡음점(카메라 0.3~0.8 m, 높이 0.03~0.13, 원시 깊이 히스토그램 0.3~0.7 대역 19 화소)이 같은 가로 띠에 들어오면 군집에 섞여 전면을 끌어당긴다. 카메라·릴레이·코스트맵은 정상이었다.
**조치**: 두 스크립트 모두 군집을 x 로 정렬해 10 cm 간격에서 나누고 가장 큰 조각만 쓴다. 고친 감사: 전면 **1.342**, 중심 −0.047 (120 점 중 11 점 제거) — 다른 네 측정과 일치.
**여파**: 어제 mp5 코스트맵 상자 셀 x 1.175~1.225 → 어제 1.174 는 맞았다. 오늘 아침 1.056 은 오염, 실제는 ≈1.22 로 어제와 5 cm 차이였을 것. 내 안내로 로버를 12 cm 뒤로 옮겨 **어제보다 17 cm 뒤**(상자 1.342), 중심 y −0.047(어제 −0.013), 창 0.287 m(어제 0.232)에서 mp6 을 달렸다.

## 2. mp6 — 목표 (2.2, 0), 파라미터 mp5 와 동일 (MPPI 10 Hz·PathFollow 10/20·inflation 0.70·SmoothPath) → TIMEOUT 90 s, 2.64 m
게이트: 상자 1.342/−0.047, 창 0.286, 띠 셀 0. bag T0 1789608787.51, 목표 수신 bag t≈6.5 s.

| bag t (s) | 사건 |
|---|---|
| 6~26 | 출발 → 사선으로 통로 진입, 입구 (1.0, +0.33) 에서 yaw +33°. 26 s 에 v 0.008 로 1 s 머뭇거림(STUCK shadow 경고 19.9 s) |
| 27~33 | 우회전하며 통로 (1.03~1.33, +0.37~0.38) 를 0.08 m/s 로 통과. 상자 왼쪽 가장자리 +0.04 ↔ 차체 오른쪽 +0.20 (여유 ≈16 cm) |
| 33~39 | 상자 뒤 모서리(x 1.45)를 지나면서 **우회전 시작**(yaw −11° → −48°), v 0.08 → 0.01. 34.7·35.8·36.8 s smoother "Smoothed path leads to a collision" (x 1.54~1.59, y 0.22~0.28) 3 연속 → BT 가 **직전 스무딩 경로를 유지**(3 s 묵은 경로) |
| 39~44 | 오른쪽 뒤로 밀리듯 (1.568,0.311)→(1.513,0.275) 이동(명령 v +0.074, SLAM 보정 가능성), 이후 좌회전 +0.32~0.38 rad/s 로 yaw −43° → −3°. 내 풋프린트 계산으로 40 s 에 차체 오른쪽 변 ↔ 상자 뒤-왼쪽 모서리 **≈3.6 cm**; 러너(패딩 포함 다각형) 는 **0.0 cm**, 계획 최소 여유 −0.7 cm. **접촉 여부는 사용자 확인 필요** |
| 44~54 | (1.63~2.08, +0.20~0.22) 로 전진, 목표 방향 −46~−76° 우회전 요구 |
| 54~90 | (2.079, +0.219) yaw +1.5° 에서 **v 0.009 정체**(모터 데드밴드 아래). 목표까지 0.24 m (xy tol 0.15). 68.1 s 진행 실패 → 클리어 → 90 s 러너 취소 |
- 루프 미달 10 Hz 9 건(25 s, 31 s 부근), 조향 부호반전 14 회(5.6/m; mp5 14/m).
**목표 앞 정체의 원인 (`outputs/j376_mp6.txt`)**: 목표 앞 x≈2.55 에 벽/문틀 LETHAL 열(로컬 ASCII 의 '#######'), 목표 (2.20, 0.01) ↔ 최근접 LETHAL **0.367 m**. 목표 자세에 풋프린트(반길이 0.26)를 놓으면 여유 **0.098 m**(job377). 우회전·전진 후보가 모두 내접/LETHAL 을 스쳐 MPPI 가 데드밴드 아래 속도로 기어갔다. → **목표 선택 오류(내 실수)**: 게이트가 통로 폭만 보고 목표 자리의 여유를 보지 않았다.
**모서리 회전**: 목표가 상자 뒤 ≈0.75 m 로 멀어지자 mp5 의 "상자 뒤 즉시 정지" 는 사라졌지만, 경로가 목표 쪽(y 0)으로 상자 뒷면 바로 뒤에서 꺾여 우회전이 여전히 상자 뒤 모서리 옆에서 일어났다. 그 순간 스무딩 실패로 묵은 경로를 따른 것이 겹쳤다.

## 3. 조치 (파일 배포, 다음 nav2 기동 반영)
1. **BT**: `SmoothPath` 실패 시 **새 원경로**를 `{path}` 로 — `Fallback(SmoothPath raw→path, TruncatePath raw→path distance 0.0)`. TODO(improve): TruncatePath 는 마지막 점 방향을 0 으로 덮어써 yaw≠0 목표에서 바뀐다.
2. **목표 여유 게이트**(`jobs/job377_goalclear.py`, 러너 훅): 목표 자세 풋프린트 ↔ 전역 LETHAL ≥ 0.20 m 아니면 주행 거부. mp6 목표는 0.098 m 로 거부됐을 것.
3. **상자 검출 x 분할**: job248(게이트)·job125(주행 지표).

## 4. 다음
1. (해소) 사용자: mp6 상자 접촉 없음.
2. mp7: 목표를 목표 여유 게이트 통과 지점으로(예: (2.0, 0) 또는 (2.2, +0.3); 게이트로 확인), BT fallback 반영(nav2 재기동). 배치는 기록만 하고 어제와 맞추지 않는다(측정 오류가 해소된 오늘 배치를 기준선으로).
3. 모서리 여유: 목표 방향으로 꺾이는 지점을 상자 뒤에서 더 멀리 — 후보 (a) 전역 inflation 0.70 → 0.85 정지 A/B, (b) 경로 크리틱 문턱 A/B(09-16 §2-2).
4. 목표 부근 데드밴드 정체: MPPI 명령 v < 0.02 가 3 s 이상이면 문제 — `vx_min` 대칭·GoalCritic 가중·xy_goal_tolerance 0.15 → 0.20 검토(시뮬 job355 로 먼저).
5. 추후(사용자 지시 유지): Wi-Fi 끊김·새 IP, DDS IP 변경 면역.

## 5. mp7 — 목표 (2.0, 0), BT 스무딩 fallback 반영: **27 s ABORTED (1.72 m, 통로 안, 접촉 없음 최근접 8 cm)** — 원인은 주행이 아니라 SLAM 굶주림 → 정지
사용자: mp6 에서 상자 접촉 없음(§2 의 "접촉 확인 필요" 해소). 로버를 출발점으로 옮김.
준비(`outputs/prep_mp7.txt`): 재기동, 상자 전면 1.207/중심 +0.003(어제 mp5 1.174 와 3 cm), 창 0.231, 띠 셀 0. BT TruncatePath 로드·bt_navigator 오류 0. 목표 여유 게이트(job377): (2.2,0) 0.145 거부 / **(2.0,0) 0.249 통과** / (2.0,+0.2) 0.345 → 모서리 복귀 회전을 그대로 시험하려고 (2.0, 0).

**Nav2 이벤트 (goal 기준, `outputs/j379_mp7_events.txt`)**
| t (s) | 사건 |
|---|---|
| 0~11 | 입구까지 정상 (0.61, +0.22) |
| 11.4 | 루프 미달 → BT "Timed out while waiting for action server to acknowledge goal request for compute_path" ×4 (default_server_timeout 20 ms) → 전역·로컬 클리어 → **BackUp 0.15 m 실행**(11.7~15.3 s, 입구에서) |
| 19.6, 20.7 | SmoothPath 충돌 판정 실패 (0.85/0.97, +0.33) → 새 fallback 으로 원경로 사용 |
| 22.4 | MPPI "Optimizer fail to compute path" → FollowPath abort → 로컬 클리어 → 재시도 |
| 27.1 | smooth·follow·wait·backup 요청 ack 타임아웃 연속 → **Goal failed** |
| 30.7~ | "Unable to transform robot pose into global plan's frame", 전역 코스트맵이 라이다·깊이 메시지를 매초 폐기, planner transformPoseInTargetFrame 외삽 오류 매초 |

**원인 추적**
- 주행 뒤 상태(job380~382): wheel_odom 25 Hz·IMU 200·EKF 29.7·스캔 9.9·깊이 15 Hz 정상. **map→odom 없음("map frame does not exist")**. slam_toolbox 프로세스는 살아 있으나 22 스레드 전부 futex 대기, CPU ≈0.5 %/s, **ROS 그래프에서 사라짐**(/map 발행자 0, /scan 구독자 목록에 없음). 환경변수 프로파일은 UDP 전용 정상(SHM 원인 아님 — 09-09 사고와 증상만 같음).
- bag(job383): map→odom 은 goal −5.6 ~ +30.1 s 동안 354 개 수신되었지만 **+6.8 s 에 5.1 s 공백**, +11.9·+13.2·+15.5 s 에 1.2~1.5 s, +18.0 s 에 3.1 s 공백, 마지막 stamp 지연 4.84 s. 즉 **주행 중 SLAM 이 굶주려 map 프레임이 수 초씩 멈췄고**, 그 공백이 끝나는 11.4 s 에 map 프레임 서버(planner)들이 20 ms ack 를 못 지켜 BT 가 복구로 들어갔다. 완전 정지(데드락 모양)는 bag 종료(+30 s) 뒤.
- slam.log: 기동부터 "Message Filter dropping … queue is full" 28 회(정지 중에도 수 초 간격) — 평소에도 스캔을 다 못 먹는다.
- 전력 모드(job384/385): **nvpmodel 15W**(ID 0, CPU 최대 1497 MHz; 하드웨어 최대 1728; conf 기본은 25W). 상태 파일은 부팅 때 다시 쓰여 어제와 달라졌는지는 확인 불가. 루프 미달 mp5 0 → mp6 9 → mp7 60+ 로 같은 설정에서 악화 — 원인 미확정(후보: MPPI iteration 2 + visualize MarkerArray + bag 5 MB/s + SLAM 루프클로저 시점).
- 판정: **주행 로직 결함이 아니라 계산 자원·SLAM 가용성 문제**. 확정된 것: map→odom 공백과 BT 타임아웃의 시간 일치, 최종 SLAM 무응답. 미확정: 공백의 원인(CPU 굶주림 vs slam_toolbox 내부 블로킹), 최종 데드락 위치(gdb 역추적은 ptrace_scope=1 이라 sudo 필요).

**조치 (파일 배포, 다음 기동 반영)**
1. `bt_navigator.default_server_timeout` 20 → **100 ms**.
2. MPPI `visualize` true → **false**, bag 에서 `/trajectories` 제외 (mp4~mp6 분석 데이터는 확보).
3. 주행 중 `top -b -d 2` 프로세스별 CPU 기록(`/tmp/top_<NAME>.log`) — 다음 공백 때 범인 확인.
4. 주행 게이트에 **SLAM 생존 검사**(`jobs/job386_slamalive.py`): 5 s 동안 map→odom 최대 간격 < 0.5 s·stamp 지연 < 0.5 s 아니면 출발 거부. 현재(정지한 SLAM) FAIL 확인.

**사용자 결정 필요**
- 정지한 slam_toolbox 역추적(`sudo gdb -p <pid> -batch -ex "thread apply all bt"`, 읽기 전용) — 재기동 전에만 가능.
- 전력 모드 15W → 25W(`sudo nvpmodel -m 1`, CPU +15 %) — 로버 배터리·Jetson 전원 회로의 허용 전력 확인 필요. **→ §6.2: 추정 오류, 25W 는 CPU 1344 MHz 로 더 낮음**

## 6. 사용자 승인 두 건 실행: SLAM 역추적 → **Fast DDS 내부 데드락**, 전력 모드 25W → **CPU 가 오히려 느려져 15W 로 원복** (내 판단 오류)
### 6.1 정지한 slam_toolbox 역추적 (`sudo gdb -p 12040 -batch "thread apply all bt 25"`, 읽기 전용, `outputs/slam_bt.txt`)
22 스레드 중 6 개가 뮤텍스 획득 대기(`__lll_lock_wait`), 나머지는 조건변수/TBB 유휴:
| 스레드 | 위치 | 기다리는 것 |
|---|---|---|
| 6 (discovery) | `EDPSimpleSUBListener::onNewCacheChangeAdded → PDP::removeReaderProxyData → EDP::unpairReaderProxy → StatefulWriter::matched_reader_remove → check_acked_status → DataWriterHistory::remove_change_pub → StatefulWriter::change_removed_by_history → (lock)` | **떠난 원격 구독자 제거 중**, 쓰기 쪽 락을 쥔 채 다른 락 대기 |
| 8 (flow controller) | `FlowControllerImpl<SyncPublishMode,Fifo> → RTPSMessageGroup::flush_and_reset → send → (lock)` | 송신 중 락 대기 |
| 5, 7 (UDP 수신) | `MessageReceiver::processCDRMsg → PDP::assert_remote_participant_liveliness → (lock)` | PDP 락(스레드 6 이 보유) |
| 4 (이벤트) | `StatefulWriter::perform_nack_response → (lock)` | 쓰기 락 |
| **16** | `SlamToolbox::publishTransformLoop → TransformBroadcaster::sendTransform → rmw_publish → DataWriterImpl::write → perform_create_new_change → (lock)` | **map→odom /tf 발행이 여기서 멈춤** |
- 해석: 원격 구독자(/tf·/map 을 구독하던 참가자)가 떠나는 순간의 **StatefulWriter 락 순서 역전 데드락**. 최종 정지는 bag 기록기(/tf·/map 구독자) 종료(+30 s) 직후였다 — 시간 일치.
- 설치 버전 **ros-humble-fastrtps 2.6.11**, 후보 **2.6.12**. 2.6.12 릴리스 노트: "Fix lock order inversion in StatefulWriter" (#6463, "flowcontroler loi deadlock" — "LocatorSelectorSender 와 FlowController 사이 LOI, 참가자 해체 중 다른 참가자가 샘플을 계속 보낼 때"). 우리 역추적의 경로(원격 해체 중 matched_reader_remove ↔ flow controller send)와 **강하게 일치**. 스레드 8 의 #4 프레임이 심볼 없음(??) 이라 완전한 동일성은 미확인.
- 주행 중 5.1 s 공백(+6.8 s)도 같은 락 경합일 가능성(짧은 구독자 — CLI·게이트 스크립트 — 가 떠날 때 /tf 쓰기가 막힘)이 있으나 **미검증**(그 시각 역추적 없음).
- 조치 후보(사용자 결정): ① `sudo apt install --only-upgrade ros-humble-fastrtps`(2.6.12) — 호스트 노드 전부에 적용, micro-ROS 에이전트는 컨테이너 자체 Fast DDS 라 무관. ② RMW 를 CycloneDDS 로 교체 — 변경 범위 큼(설치·전 런치 환경변수·에이전트 상호운용 시험). ①을 먼저.
- 재발 방지 운용: 주행 중에는 /tf 구독 CLI(tf2_echo 등)·짧은 노드를 띄우지 않는다. bag 은 SLAM 재기동 전에만 끈다(끈 뒤에는 SLAM 생존 게이트가 잡는다).

### 6.2 전력 모드 — 25W 전환 후 즉시 15W 원복
- 실행: `nvpmodel -m 1`(25W) → CPU `scaling_max_freq` **1344 MHz**(15W 는 1497). `/etc/nvpmodel.conf`:
| 모드 | CPU 상한 | GPU 상한 | EMC 상한 |
|---|---|---|---|
| 15W (ID 0) | 1497.6 MHz | 612 MHz | 2133 MHz |
| 25W (ID 1) | **1344 MHz** | 918 MHz | 3199 MHz |
| MAXN_SUPER (ID 2) | 제한 없음(1728) | 제한 없음 | 제한 없음 |
- **내 오류**: "25W 면 CPU +15 %" 는 확인 없이 한 추정이었다. 이 JetPack 의 25W 는 전력 예산을 GPU·메모리에 주고 CPU 를 낮춘다. 사용자 승인의 목적(CPU 여유)과 반대라 같은 승인 범위에서 **15W 로 원복**(1497 MHz 확인). 전환 중 배터리 12.12 V, 온도 47 °C.
- CPU 를 늘리는 유일한 모드는 MAXN_SUPER(무제한, 전력 최대). 로버 전원 회로 허용 전력 확인 후 사용자 결정.

### 6.3 Fast DDS 2.6.12 적용 (사용자 승인 1번)
- 호스트 ROS 노드 정지(에이전트 컨테이너 유지) → `apt-get -s` 시뮬레이션: **ros-humble-fastrtps 1 개만 변경** 확인 → 설치 2.6.11 → **2.6.12-1jammy.20260725**. (`outputs/j391_fastdds.txt`)
- 재기동: robot_state_publisher·slam_toolbox 가 `libfastrtps.so.2.6.12` 를 매핑(프로세스 maps 확인). 에이전트 세션 유지(보드 리셋 불필요), 자이로 캘리브·map→odom 0 정상.
- 유발 조건 스트레스(`jobs/job393_churn.sh`, 로버 정지): bag 기록기(/tf·/tf_static·/map·/scan) 6 s 기록 후 해체 + `ros2 topic echo /tf`·`/map` 단발 구독자 16 개 생성·해체 × 3 라운드 → 매 라운드 map→odom 최대 간격 0.05~0.07 s, SLAM 그래프 유지, **정지 0 회**. (`outputs/j392_393.txt`)
- 한계: 2.6.11 에서 같은 시험을 돌리지 않았고 데드락은 타이밍 의존이라, 이 결과는 **수정의 보조 증거일 뿐 증명이 아니다**. 실주행(bag 종료 포함)에서 재발 여부를 계속 본다(SLAM 생존 게이트·top 기록).
- 게이트 문턱 조정: 정상 SLAM 의 map→odom stamp 지연이 −0.08~+0.55 s 로 흔들려 기준 측정이 FAIL(0.55) → 지연 문턱 0.5 → **1.0 s**(간격 문턱 0.5 s 유지). mp7 고장 값(간격 5.1 s, 지연 4.8 s)은 여전히 잡힌다.
