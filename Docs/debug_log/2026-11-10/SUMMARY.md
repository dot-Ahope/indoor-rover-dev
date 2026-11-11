# 2026-11-10 — 현재 구성 점검: 저장소 ↔ CURRENT_STACK ↔ Jetson (로버 주행 없음 · 코드 수정 없음)

## §0 저장소 쪽 점검 (사용자: "현재 구성 체크.")
- 비교 규칙: `Docs/04_navigation/CURRENT_STACK.md`(11-04 판)가 값마다 적은 '정하는 곳'(파일 · 줄)을 그대로 뽑아 문서 값과 같은지 본다. 같으면 ✔. (점검이라 판정 기준을 따로 선언하지 않았다 — 기준은 이 한 줄이 전부.)
- 결과: 확인한 값 약 45 개 전부 일치(launch 기본 = 표준 prep 인 11-04 §17 변경이 코드에 들어 있음). 발췌(원문 없음 — 대화에서 줄을 뽑아 본 것이 전부):
```
navigation.launch.py:201: DeclareLaunchArgument('replan_hz', default_value='0.5',
navigation.launch.py:203: DeclareLaunchArgument('planner', default_value='navfn',
navigation.launch.py:220: DeclareLaunchArgument('stuck_shadow', default_value='true',
ekf.launch.py:109: DeclareLaunchArgument('vslam', default_value='on',
camera.launch.py:117: DeclareLaunchArgument('emitter_off', default_value='true'),
nav2_params.yaml:255: critics: ["ConstraintCritic", "CostCritic", "GoalCritic", "GoalAngleCritic", "PathAlignCritic", "PathFollowCritic", "PathAngleCritic", "PreferForwardCritic"]
nvblox_local.yaml:57: projective_integrator_max_integration_distance_m: 2.0
```
- 작은 어긋남(동작 영향 없음, 고치지 않음): 문서 §1 이 정체 감시 · pad_relief 를 `navigation.launch.py` 219 · 231 로 가리키나 그 줄은 주석, 선언은 220 · 232. 재계획 0.5 의 '정하는 곳' 에 `navigation.launch.py:201` 기본도 0.5 라는 것이 빠짐.
- 저장소 상태: `CLAUDE.md` 미커밋 수정 1 건(프로젝트 성격 문구 2 줄 — 이 세션이 고친 것 아님, 누가 · 언제인지 미확인) · 로컬 커밋 10 개(11-04)가 비공개 원격보다 앞섬(`git rev-list --left-right --count personal/feature/smac-hybrid...HEAD` → `0 10`).

## §1 Jetson 쪽 점검 (사용자: "Jetson도 확인") — 읽기만, 로버 안 움직임, DDS 참여자 안 만듦
### §1.1 신원 · 주소
- PC 에서 ping: `<LAN-A>.8 ping False` · `<LAN-B>.110 ping True`(CURRENT_STACK 의 11-04 주소는 지금 응답 없음). <LAN-B>.110 은 사용자가 Jetson 에 예약한 주소라 그대로 붙고, job 첫 줄에서 신원부터 찍음.
- `jobs/chk_config_1110.sh` → `outputs/chk_config_1110.txt`:
```
host jetson-desktop · user jetson · 5.15.185-tegra · # R36 (release), REVISION: 5.0
rover -> ttyCH341USB0 · rplidar -> ttyUSB0
주소: wlP1p1s0 <LAN-B>.110/24 docker0 172.17.0.1/16
SSID: <WIFI-B>
가동 up 25 minutes · 부팅 2026-11-10 14:25:17 · 디스크 / 남음 122G
```
- 결론: 우리 Jetson(11-04 §10 과 같은 호스트 이름 · 커널 · 보드 별칭), 오늘 14:25 재부팅, <WIFI-B> 로 돌아와 있음. → CURRENT_STACK §3 'Jetson 주소' 칸은 낡음(고치지 않음, §2).

### §1.2 실행 상태 — base 만 떠 있음
- 같은 출력 ⑤:
```
  micro_ros_agent        2
  robot_state_publisher  1
  realsense2_camera      0   (… sensor_conditioner · ekf_node · slam_toolbox · controller_server · nvblox 모두 0)
  컨테이너: microros_agent(Up 5 days)
  에이전트 세션 수립 기록 1 건
```
- `micro_ros_agent 2` = 호스트 쪽 `docker run` 아래의 컨테이너 안 `ros2 run micro_ros_agent` 와 그 실행 파일 2 개(`outputs/chk_config_1110b.txt` 프로세스 목록 PID 2648 · 2689). 에이전트 1 개.
- 세션 수립 1 건 · 로그 끝이 `create_datawriter … client_key: 0x59AD87DB` → 보드가 붙어 발행자를 만든 상태(토픽 주기는 DDS 참여자를 만들어야 보므로 안 봄 — 미확인).
- `/tmp` prep 도구 7 개 전부 없음(재부팅으로 지워짐) → 주행 전 `bash Docs/tools/up_tools.sh`(JETSON_HOST=<LAN-B>.110) 필요. 지금은 올리지 않음(사용자 지시 범위 밖).

### §1.3 'Up 5 days' 와 가동 25 분의 모순 — 부팅 직후 시계 (추정)
- 본 것(`outputs/chk_config_1110b.txt`, `jobs/chk_config_1110b.sh`):
```
microros_agent Created 2026-11-04T08:28:53.33504036Z · StartedAt 2026-11-04T08:28:53.434538664Z · Restart no · AutoRemove true
   2590    2567 Tue Nov 10 14:25:44 2026       26:30 docker run --rm --name microros_agent --net host …
System clock synchronized: yes
```
- 추론: 같은 컨테이너를 띄운 `docker run` 프로세스는 오늘 14:25:44 시작(ps 는 부팅 후 경과로 계산)인데 docker 가 적은 생성 시각은 11-04 → 부팅 직후 시스템 시계가 11-04 에 머물러 있다가 NTP 로 뒤에 맞춰진 것. 에이전트 로그 시각 `1793780936`(유닉스 초)도 11-04 무렵(계산).
- 결론(추정): 컨테이너 상태의 'Up N days' 는 부팅 직후 시계 탓이라 믿지 않는다 — 가동 시간은 `uptime -s` · ps 시작 시각으로 본다. 시계가 왜 11-04 였는지(RTC · 시계 저장 방식)는 미확인. 같은 계열: 메모리 'Jetson Wi-Fi 문제' 의 wifi_mon 1970 타임스탬프.

### §1.4 src · 설치본이 저장소와 같은가
- 규칙: Jetson `~/ros2_ws/src/rover_*` 전 파일 md5(CR 제거, 앞 12 자) ↔ PC `git show HEAD:<경로>` 같은 방식. 대조 도구 `jobs/anal_src_cmp_1110.sh`(대화에서 돌린 한 줄 명령을 옮김 — 다시 돌려 출력 md5 같음 확인) → `outputs/chk_config_1110_cmp.txt`:
```
      4 DIFF
     43 JETSON만     (전부 *.bak_10xx_* · *.site1_* · __pycache__/*.pyc — 10-15 · 10-19 · 10-20 배포 때 백업)
     58 SAME
     (PC만 0)
```
- DIFF 4 개 내용(`outputs/chk_config_1110_diff4.txt`, Jetson 원문은 `chk_config_1110b.txt` 의 `@@FILE` 블록):

| 파일 | Jetson 판 | 차이 | 영향 |
|---|---|---|---|
| `rover_description/launch/description.launch.py` | 08-27 | 첫 줄 주석 경로(`Docs/rover.urdf` → `Docs/02_hardware/rover.urdf`) | 없음 |
| `rover_navigation/launch/localization.launch.py` | 10-01 | 예시 주석 office_v2 → office_v3 | 없음 |
| `rover_description/urdf/rover.urdf.xacro` | 09-18 | 08-27 초안(10-30 커밋 `73cabe09` 재작성 전 — 라이다 x 15 cm 어긋난 판) | 지금은 없음: `description.launch.py:29 use_xacro default_value='false'` → RSP 는 확정본 `rover.urdf`(SAME) 를 씀. `use_xacro:=true` 로 띄우면 옛 값 |
| `rover_navigation/scripts/place_web.py` | 10-28 16:05 | `rclpy.executors.ExternalShutdownException` 처리 2 줄 없음(HEAD 마지막 변경 `be17666e` 10-28 16:12 — 배포 뒤 7 분 고친 판이 안 올라감) | 종료 때 예외 출력뿐(추정 — 시험 안 함). F2.5 웹 창구는 launch 밖 시험 단계 |

- 설치본 share 설정 32 개 전부 src 링크(`종류별 개수 32 LINK`, 링크 아닌 파일 0) — 11-04 §1 의 링크 복구가 재부팅 뒤에도 유지.

### §1.5 내 실수 2 건 (같은 점검 안에서 바로잡음)
**① 기동 서비스 범위 오판**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | base 를 띄운 주체 확인 — `jobs/chk_config_1110.sh` ⑤ `systemctl is-active rover-base` |
| 본 것 | `rover-base 서비스: inactive · 사용 설정 ` (빈칸) |
| 처음 추론 | 서비스가 꺼졌는데 에이전트 · RSP 가 떠 있음 → 누가 손으로 띄웠나 |
| 의심한 이유 | 같은 출력에 `ros2 launch rover_bringup base.launch.py` 가 부팅 25 초 뒤(14:25:42) 시작 — 손 기동치고 너무 이름 |
| 판별 시험 | `jobs/chk_config_1110c.sh`: base.launch 부모 사슬 + `systemctl --user list-unit-files` |
| 결론 | 부모 = `/lib/systemd/systemd --user`, `user: rover-base.service enabled enabled` → **사용자 단위 서비스**. 시스템 범위로 물어 'inactive' 가 나온 것 |
| 다음에 알아보는 법 | rover-base 는 `systemctl --user …` 로 본다. 사용 설정 칸이 빈칸이면 단위를 못 찾은 것(꺼짐 아님) |
| 스크립트 핵심 | `echo "  rover-base 서비스: $(systemctl is-active rover-base 2>/dev/null) · 사용 설정 $(systemctl is-enabled rover-base 2>/dev/null)"` → 고친 판 `systemctl --user list-unit-files --no-legend \| grep -iE 'rover\|ros2\|micro'` |
| 나온 결과 | `2567 1388 jetson /usr/bin/python3 /opt/ros/humble/bin/ros2 launch rover_bringup base.launch.py` · `1388 1 jetson /lib/systemd/systemd --user` |
| 데이터 | `outputs/chk_config_1110.txt` · `outputs/chk_config_1110c.txt` |

**② C++ 빌드물 시각을 링크 시각으로 읽음**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 설치된 C++ 플러그인이 지금 소스로 빌드됐는지 — `chk_config_1110.sh` ③ `stat -c %y ~/ros2_ws/install/<lib>` |
| 본 것 | `BIN 2026-10-01 17:28 …librover_path_blocked_ahead_bt_node.so` · `BIN 2026-10-14 14:44 …librover_copy_path_bt_node.so` |
| 처음 추론 | `only_new`(10-23 `0a6e5f73`) · `step`(10-26 `36e59493`) 포트를 더한 소스보다 빌드가 옛것 → 옛 플러그인이 돌 수도 |
| 의심한 이유 | 그러면 BT XML 의 `only_new="true"` · `step="0.03"` 가 없는 포트라 BT 적재가 실패했어야 하는데 10-23 뒤 주행이 돌았다(기록상) |
| 판별 시험 | `jobs/chk_config_1110d.sh`: install · build 두 곳 시각 · 크기 · md5 + `strings` 로 포트 이름 검색(2 차에 영문 낱말 · `ls -l` 추가) |
| 결론 | install 의 .so 는 **build 를 가리키는 심볼릭 링크**(크기 82 · 73 B = 경로 길이), md5 가 build 와 같고 build 시각 10-23 15:10 · 10-26 12:37, `only_new` · `step` 문자열 있음 → **최신 빌드** |
| 다음에 알아보는 법 | 이 작업공간 install 은 `--symlink-install` — 시각은 `stat -L`(링크 따라감)이나 build 쪽에서 본다. 한글 설명문은 `strings` 로 안 잡힘(1 차의 `CopyPath step 설명: 0`), 영문 포트 이름으로 찾는다 |
| 스크립트 핵심 | `echo "$(stat -c '%y %s' $f …) $(md5sum < $f …)"` · `strings … \| grep -cx 'step'` |
| 나온 결과 | `2026-10-23 15:10 6139272 9506134816aa build/…path_blocked_ahead…` · `PathBlockedAhead only_new: 1` · `CopyPath 'step' 낱말: 1` · `lrwxrwxrwx install/…copy_path_bt_node.so -> build/…` |
| 데이터 | `outputs/chk_config_1110d.txt`(1 차) · `outputs/chk_config_1110d2.txt`(2 차) |
- 같은 이유로 `chk_config_1110.txt` ③ 의 다른 `BIN` 시각(sensor_conditioner_node 09-28 등)도 링크 시각일 수 있다 — 따로 보지 않음(미확인).
- 실행 실수 1 건(결과 영향 없음): `chk_config_1110b.sh` 자동 기동 줄의 `sed 's/^/  /etc\/…/'` 가 구분자 `/` 와 경로가 겹쳐 `unknown option to 's'` → `chk_config_1110c.sh` 에서 구분자 `|` 로 다시 함.

### §1.6 정리
- 저장소 판과 Jetson 에서 실제로 쓰이는 판은 같다(동작에 쓰이는 파일 기준). 다른 것은 주석 2 · 안 쓰는 xacro 1 · 시험 단계 place_web 1.
- 지도 office_v3(.data · .pgm · .posegraph · .yaml) · slam 포크 `localization_slam_toolbox_node` 있음.

## §2 남은 것 (사용자 결정 대기, 이 날 하지 않음)
- 주행하려면: `up_tools.sh` 로 prep 도구 7 개 재전송 → prep.
- Jetson 에 xacro(10-30 판) · place_web(10-28 16:12 판) 올리기 — 다음 배포 때 같이.
- CURRENT_STACK §3 Jetson 주소(지금 <LAN-B>.110, <WIFI-B>) · §1 줄 번호 219 → 220 · 231 → 232 정정.
- Jetson src 의 `*.bak_*` 43 개 정리 여부(GB 단위 아님 — 메모리 '정리 보류 결정' 대로 먼저 제안하지 않음, 목록만 남김).

## §3 학습식 6D 자세 추정이 이 플랫폼에서 되는가 (사용자: "고전방식 말고 학습방식 사용하고 싶은데 가능한지 체크.") — 조사 · 읽기만
- 판정 기준(조사 전): 후보마다 ① Jetson(Orin Nano Super 8GB · L4T R36.5 · Isaac ROS 3.2 이미지)에서 변환 · 실행 가능 ② 주행 스택과 함께 둘 메모리 여유 ③ 우리 물체(시험 상자)용 모델을 지금 장비로 만들 수 있나.
- 외부 출처(웹, 원문 확인 범위만):
  - Isaac ROS 성능표(release-5.0, JetPack 7.2 기준 — 우리 3.2 와 판 다름, 참고값): FoundationPose AGX Orin `0.746 fps` · Orin Nano Super 8GB `–`(값 없음) / DOPE TensorRT Orin Nano Super `20.8 fps` / CenterPose `35.0 fps, 1.8 ms @ 30Hz` / RT-DETR `40.0 fps`.
  - NVIDIA 포럼(Orin Nano 8GB · JetPack 6.2): FoundationPose `refine_model.onnx` 변환에서 `Cuda Runtime (out of memory)` · `Tactic Device request: 1000MB Available: 470MB`. 답변 "FoundationPose … requires a substantial 7.5 GB GPU margin", Orin Nano 8GB 에는 CenterPose 또는 DOPE 권장. 해결 표시 없음.
  - DOPE 는 물체마다 학습 필요, NVIDIA 안내 경로는 Isaac Sim 합성 데이터. CenterPose 의 사전 학습 범주 목록은 이번에 원문 확인 못 함(미확인).
- 우리 쪽 측정:
  - Jetson(`jobs/chk_ml_capacity_1110.sh` → `outputs/chk_ml_capacity_1110.txt`): `Mem: 7607 total · 6435 available`(스택 안 뜬 상태) · `NV Power Mode: 15W` · 이미지 `isaac_ros_dev-aarch64-rs:apt 43.8GB` 등 · 디스크 남음 122G.
  - 주행 중 부하(10-28 f2tt2 `tegra_f2tt2.log` 420 줄): `RAM 2909~3104 MB` · `GR3D` 평균 10 % · 최대 99 % → 주행 중 메모리 여유 약 4.5 GB(계산).
  - PC: `AMD Radeon(TM) Graphics`, `nvidia-smi 없음`, RAM 15.4 GB → CUDA 학습 · Isaac Sim 합성 데이터 불가.
- 추론 → 결론:
  - FoundationPose: 변환만 GPU 여유 7.5 GB 요구(포럼) > 이 기기 전체 7607 MB, 공식표 값 없음 → **이 Jetson 에서는 불가**로 봄.
  - DOPE: 실행은 가능 쪽(공식표 20.8 fps, 판 다름). 막히는 곳은 학습 — 합성 데이터 · 학습에 NVIDIA GPU 가 필요한데 PC 에 없음 → 클라우드 GPU 가 있어야 함.
  - CenterPose: 가장 가볍고(35 fps) 범주 단위라 사전 학습 모델이 상자에 맞으면 학습 없이 시험 가능. 범주 목록 확인이 먼저.
  - §3.1 이어서(사용자: "집에 있는 pc에서 cuda 사용 가능") — 학습 GPU 막힘이 풀림. 웹 확인:
    - CenterPose 사전 학습(NGC 카드): 8 범주 bike · book · bottle · camera · **cereal box** · chair · laptop · shoe, cereal box 3D IoU 0.81(DLA34) · 0.83(FAN-Small). 우리 시험 상자(무늬 없는 골판지)에 일반화되는지는 미확인 — 학습 없이 먼저 볼 수 있는 유일한 길.
    - DOPE 데이터: 저장소가 BlenderProc 경로 제공(NVISII 는 유지 중단), "RTX-capable GPU is strongly recommended", 물체 하나에 약 20k 장(NVIDIA 블로그). 학습 GPU 최소 사양은 공개 수치 없음(기본 batch 32).
    - Isaac Sim 6.x 최소 GPU = RTX 4080 16 GB — 집 PC 가 못 미치면 BlenderProc 쪽. Isaac Sim 의 자세 합성 튜토리얼은 deprecated.
    - FoundationPose 는 x86 GPU 에서는 돌아감(성능표 RTX 5070 3.32 fps, release-5.0) → Jetson 실시간용이 아니라 PC 에서 녹화 영상의 기준 자세(정답) 만들기 용도 후보.
  - 공통 미확인(§3 끝): Isaac ROS 3.2 에서 이 패키지들이 지금 이미지에 바로 들어가는지 · 15W 모드에서의 실제 fps(공식표는 다른 판 · 전원 모드 미기재) · 주행 스택과 동시 실행 시 메모리. 전원 모드 변경은 sudo 라 사용자 결정.

## §4 주행 기록에서 사이클타임 · 성공률 표 (사용자: "사이클타임과 성공률을 기록에서 뽑아 표로 만들어 봐라.") — 기록 읽기만
- 선언(뽑기 전):
  - 범위 = F0 러너 형식 로그(`########## F0 주행` 머리줄)가 있는 09-23 이후 주행. 그 전(09-02~09-08)은 단일 목표 조정 시험이라 형식 · 목적이 달라 뺀다.
  - 같은 주행이 `run_<이름>.txt` · `f0_<이름>.log` · `bags/` 사본에 겹침 → 날짜 · 머리줄 시각 · 목표 문자열이 같으면 하나로(outputs 우선).
  - 목표 성공 = 러너가 찍은 Nav2 결과 `SUCCEEDED`(Nav2 목표 판정: `xy_goal_tolerance 0.15` · `yaw_goal_tolerance 0.35` · `stateful: True`). 주행 성공 = 계획한 목표 전부 SUCCEEDED. 실패 뒤 러너가 멈춰 출발하지 않은 목표는 '시도 안 함' 으로 따로 센다.
  - 사이클타임 = 러너가 잰 목표별 소요 시간(출발 → 결과). 구간 길이가 달라 비교는 같은 목표 좌표끼리 + 평균 진행 속도(직선 거리 ÷ 시간)로.
  - 한계(미리): 로그에 접촉 · 사람 개입 · 줄자 오차는 없다 → SUCCEEDED 여도 접촉했을 수 있음(그날 SUMMARY 에만 있음). 구성 메타 `run_meta.txt` 는 1 건만 남아 구성은 날짜 · 시리즈 이름으로만 구분.
- 판정 정정(뽑는 중, 결과 보기 전 기준을 바꿈 — 사실을 적는다): 1 차 표에서 `SUCCEEDED_XY` 를 실패로 셌는데, 이것은 '위치만' 목표(목표 문자열의 `f`)에서 러너가 xy 도달 뒤 **일부러** 취소한 성공이다 — 러너 원문 `Docs/debug_log/2026-10-21/jobs/job550_f0run.py` 169 행 `name = 'SUCCEEDED_XY' if xy_done else {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}`. → 성공에 넣음. `CANCELED` 는 러너 한도 초과(같은 파일 159 행 `★ 목표 %d 한도 초과 — 취소`)와 그 밖(nav_guard · 사람 등, 원인 로그 없음)으로 나눔. 구간은 같은 목표 좌표가 아니라 (이전 목표 → 목표) 쌍으로(같은 (0,0) 도 출발점이 달라 39.8~157 s 로 흩어졌음).
- 도구 `Docs/tools/anal_drive_results.py`(상시) → 원문 `outputs/anal_drive_results.txt` · `_runs.csv`(91 주행) · `_goals.csv`(300 목표). 중복 검사: 같은 날 같은 이름 0 건.
- 결과(기간 = CURRENT_STACK · CLAUDE.md 의 구성 변경 날짜):
  | 기간 | 주요 구성 | 주행 성공 / 주행 | 목표 성공 / 시도 | 출발 → (2.2, −1.6) 중앙값 s (n) | (5.5, −2.2) → (0, 0) 중앙값 s (n) |
  |---|---|---|---|---|---|
  | 09-23 ~ 09-29 | F0 코스, nvblox 채택 직후 | 6 / 9 | 14 / 17 | - | 103.2 (2) |
  | 10-01 ~ 10-08 | F2 첫 순회(지도 v2 → v3) | 7 / 21 | 42 / 56 | 52.5 (9) | 120.0 (3) |
  | 10-12 ~ 10-15 | PreferForward 15 · lite · CopyPath · MonotoneEscape | 18 / 32 | 95 / 109 | 51.7 (28) | 104.3 (16) |
  | 10-19 ~ 10-22 | 프로젝터 끔 · 깊이 프리셋 3 · cuVSLAM 시험 | 8 / 11 | 27 / 29 | 52.3 (9) | 102.9 (8) |
  | 10-23 ~ 10-28 | cuVSLAM 기본 + Smac 시험 · SLAM timeout 1.5 | **18 / 18** | **89 / 89** | 51.9 (18) | 103.5 (18) |
  - 합계 91 주행 중 57 성공 · 목표 300 시도 중 267 성공 · 실패 뒤 시도 안 함 75.
  - 표준 구간 3 개: 출발 → (2.2, −1.6) 69 시도 93 % · 중앙값 52.0 s(2.76 m), (2.2, −1.6) → (5.5, −2.2) 44 시도 93 % · 48.8 s(3.30 m), (5.5, −2.2) → (0, 0) 56 시도 84 % · 104.2 s(5.92 m). 도착 오차 중앙값 0.13~0.15 m.
- 추론:
  - 성공률은 기간마다 올라 마지막 기간 18/18 · 89/89. 사이클타임은 **기간 사이에 거의 그대로**(52 s · 103 s 근처).
  - 왜 그대로인가: MPPI `vx_max: 0.08`(펌웨어 한계 0.085, `nav2_params.yaml` 219 행)이 09-16 뒤로 안 바뀜(`git log -S vx_max` 마지막 a5853162 09-16). 출발 → (2.2, −1.6) 직선 2.76 m ÷ 0.08 = 34.5 s(계산) 대비 실제 52 s → 직선 기준 약 66 %(회전 · 경로 굽음 포함). 즉 개선은 '실패를 없앤 쪽' 이고 속도는 모터 상한이 정함(추정 — 회전 시간 비중은 bag 으로 따로 봐야 함).
  - 도착 오차 중앙값 0.14 m 가 xy 허용 0.15 m 에 붙어 있음 — stateful 판정(한 번 xy 안이면 그 뒤 방향만 맞춤) 중 제자리 회전 미끄러짐으로 밀린 값으로 봄(추정, 09-28 nav2_params 주석과 같은 기전).
  - 주의: 마지막 기간 18 주행의 구성이 하나가 아님(f2von · f2rp · f2sa · f2sh · f2st · f2tf · f2tt — NavFn · Smac 섞임). '지금 구성 하나의 성공률' 로 읽으면 안 된다. 접촉은 로그에 없어 빠짐(예 10-22 f2lp1 접촉).

## §5 접촉을 더함 (사용자: "접촉도 더해") — 기록 읽기만
- 선언(분류 전):
  - 근거 = 그 주행 날짜 SUMMARY 의 **결과 서술**(사용자 관찰 · 영상 확인 · bag 계산). 주행 **전** 판정 선언("판정: … 접촉 0")은 근거가 아니다.
  - 분류 3 가지: **접촉 있음**(닿음 · 밀기 · 긁음 · 스침을 사실로 적음) / **접촉 없음 확인**(결과로 '닿지 않았다 · 접촉 0 · 접촉 없음' 을 적음, 또는 `anal_contact` 최소 거리 > 0 이고 사용자 반대 관찰 없음) / **기록 없음**(둘 다 없음). '기록 없음' 을 '접촉 없음' 으로 세지 않는다.
  - `anal_contact`(10-22~)는 출발점 낮은 상자 하나만 · SLAM 오차 수 cm 포함 → 사용자 관찰과 다르면 관찰을 따른다.
  - 대상 = §4 의 91 주행(같은 이름 · 날짜).
- 분류 과정: 1 차 = 에이전트(날짜별 SUMMARY · anal_contact 원문을 읽고 주행마다 근거 file:line + 원문 발췌). 내가 접촉 11 건 전부와 판단이 갈릴 7 줄, 합계 18 줄을 원문과 대조해 전부 일치. 그 뒤 선언 기준으로 고침:
  - 바닥 전선 · 케이블 가드(f0b1 · f0b2 · f2pr1 · f2a9)는 장애물 충돌이 아니라 `FLOOR` 로 따로(f2a9 는 사람이 발로 밀어 줌 = 개입).
  - `UNKNOWN` 으로 내림: 기록 스스로 '사용자 확인 필요' 라 적은 f2u2(10-14:572) · f2sm2(10-21:95), 정체 구간만 본 f2c1(10-07:74), 코스트맵 지표(fp 100)만으로 '접촉 0' 인 f2rp3 · f2rp4 — f2b4 · f2c2 처럼 코스트맵에 상자가 없을 때 실제로 닿은 사례가 있어 코스트맵 지표는 물리 접촉 근거로 약하다.
- 도구 · 원문: `jobs/anal_contacts_table_1110.py` → `outputs/anal_drive_contacts.csv`(91 행, 주행마다 근거 줄) → `Docs/tools/anal_drive_results.py` 가 합침 → `outputs/anal_drive_results.txt` · `_runs.csv`(contact · touched 열).
- 결과: 91 주행 = 접촉(장애물) 6 · 바닥 전선 4 · 접촉 없음 확인 38 · 기록 없음 43. 접촉 열 빈 주행 0(이름 맞춤 확인).
  | 기간 | 주행 성공 / 주행 | 접촉(장애물) · 바닥 전선 · 없음 확인 · 기록 없음 | 성공 + 접촉 없음 확인 |
  |---|---|---|---|
  | 09-23 ~ 09-29 | 6 / 9 | 0 · 2 · 0 · 7 | 0 / 9 |
  | 10-01 ~ 10-08 | 7 / 21 | 4 · 1 · 3 · 13 | 1 / 21 |
  | 10-12 ~ 10-15 | 18 / 32 | 0 · 0 · 18 · 14 | 13 / 32 |
  | 10-19 ~ 10-22 | 8 / 11 | 1 · 1 · 2 · 7 | 2 / 11 |
  | 10-23 ~ 10-28 | 18 / 18 | 1 · 0 · 15 · 2 | 15 / 18 |
  - 장애물 접촉 6: f2b3 의자 다리(주행 실패) · f2b4 출발 방 상자 · f2c2 복귀 길 상자 ② 밀기 · f2e1 상자 ② · f2lp1 출발 상자 밀림(주행 실패) · f2tf1 출발 상자 밀림. **6 중 4 가 러너 기준 '주행 성공'**(f2b4 · f2c2 · f2e1 · f2tf1).
- 추론:
  - 'Nav2 SUCCEEDED = 작업 성공' 이 아니다 — 성공 57 주행 중 장애물 접촉 4 · 바닥 4 · 기록 없음 18, 접촉 없음까지 확인된 것은 31. 공개 성공률은 '도착' 과 '접촉 없이 도착' 을 나눠 써야 한다.
  - 접촉 6 건 모두 라이다(0.185 m) 아래 낮은 물체(상자 · 의자 다리) — CURRENT_STACK 의 '상자 옆 근접' 열린 문제 · 카메라 시야 · 기억 한계와 같은 줄기(10-27 §21 사용자: 기능 · 센서 한계). 10-12 ~ 10-15 는 접촉 0 이지만 기록 없음 14 라 '0' 이라 단정 못 함.
  - 마지막 기간은 bag 계산(`anal_contact`)이 붙어 기록 없음 2 로 줄었다. 단 bag 계산은 출발 상자 하나만 본다(복도 물체 · 벽 · 의자는 안 봄).

## §6 주행 시연 f2dm1 — 서쪽 통로 포함 no5 코스 (사용자: "로버 오늘 한 번 돌려보자. 주행시연. 준비 빠르게." → "서쪽 통로 지나는 주행까지 진행하라.") — 선언(주행 전)
- 준비(로버 안 움직임): 재부팅(14:25)으로 지워진 Jetson `/tmp` prep 도구 7 개를 `Docs/tools/up_tools.sh`(JETSON_HOST=<LAN-B>.110)로 다시 올림 → `Jetson /tmp: 7 개 · prep_fast --follow-symlinks 줄 2`. PC 스크래치패드 러너 의존 5 개도 7 일 자동 삭제로 사라져 저장소 판으로 복구: `job550_f0run.py` · `job613_pathyaw.py`(2026-10-21/jobs, 커밋 e43798c2 — 그 뒤 수정 기록 없음), `job451_paramsnap.py`(09-18) · `job453_runmeta.sh`(09-22), `chk_drive_gate.py`(Docs/tools), 래퍼 `run_f2c.sh`(2026-10-22/jobs). `job551_f0drive.sh` 는 스크래치패드 판 = 2026-11-03/jobs 판(cmp 같음).
- 구성 = 표준 prep `/tmp/prep_patrol.sh lite`(planner navfn · 재계획 0.5 Hz · ODOM=vslam · 프로젝터 끔 · mppi_viz lite · PreferForward 15, 지도 office_v3) — 래퍼 `jobs/prep_demo_1110.sh`.
- 코스 = `run_f2c.sh` 의 `no5`(8 목표, 10-14 §13 사용자 기준선): `2.25,-1.6,p;-1.6,-2.0,p;-1.65,-3.7,p;-1.6,-5.5,f;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p` — 서쪽 통로(−1.65, −3.7)를 남 · 북 두 번 지남, 남서(−1.6, −5.5)는 위치만(f). 속도 0.07.
- 러너 인자: NAME `f2dm1` · STAGE `F2-std-1110` · NOTE `11-10 시연, 표준 prep(navfn·0.5Hz·vslam), no5` · GIT_HEAD = 주행 때의 `git rev-parse --short HEAD`.
- 판정(주행 전 선언):
  - **도착**: 8 목표 전부 `SUCCEEDED`(4 번째는 `SUCCEEDED_XY`) — 1 개라도 CANCELED · ABORTED 면 불합격.
  - **접촉 없음**: 사용자 관찰로 장애물 · 벽 · 의자 접촉 0(바닥 전선은 따로 적음). bag 의 `anal_contact` 는 출발 상자만 보므로 보조.
  - **시간(참고, 합불 아님)**: 같은 코스 최근 8 회(10-14 ~ 10-28 성공 주행) 412 ~ 605 s, 10-23 뒤 412 ~ 450 s(`outputs/anal_drive_results_runs.csv`). 이 범위 안이면 '같은 수준'.
  - 사람 개입(밀기 · 들기 · 수동 정지)이 있으면 결과와 별개로 적는다.
- 출발 조건: 로버를 출발 테이프 위 정지(prep 의 자이로 캘리브 · PREP_POSE 위치 검사), 코스 배치는 `Docs/04_navigation/TEST_COURSE_AND_GATES.md` 그대로(출발점 낮은 상자 포함). 로버는 사용자 "시작" 뒤에만 움직인다.

## §7 f2dm1 결과(1 차) · 발로 돌린 뒤 복귀 주행 f2dm1h — 선언(주행 전)
- f2dm1 결과(`outputs/run_f2dm1.txt`): 목표 1~3 SUCCEEDED(85.8 · 55.0 · 27.2 s) · 4 SUCCEEDED_XY 30.0 s · **5 CANCELED 49.8 s**(러너 한도 81 s 전, 도착 map (−1.521, −5.246, −10.4°) — 경로 끝 방향 76° 로 돌아야 할 자리에서 −93° → −10° 로 돈 뒤 멈춤). → §6 판정 **불합격**(도착). 사용자: "접촉없이 멈췄다". 취소 주체는 아직 미확인(`jobs/chk_cancel_1110.sh` 는 사용자 메시지로 중단 — 다시 돌릴 것).
- 사용자가 멈춘 로버를 발로 돌림 → `jobs/chk_pose_1110.sh` → `outputs/chk_pose_1110.txt`: `map base_link (-1.626, -5.206) 51.039°` · `odom base_link 24.693°` · `map odom 26.369°`. 계산: 멈출 때 odom yaw ≈ −6°(map −10.4° − 주행 누적 보정 −4.43°) → 자이로가 본 회전 ≈ +31°, SLAM 보정이 −4.4° → +26.4° 로 따로 +31°. 가설 ① 실제 ≈ 61° 돌림(SLAM 맞음) ② 실제 ≈ 31°(SLAM 이 31° 틀리게 맞춤) — 판별 안 됨(사용자 물리 방향 답 없음).
- 복귀 f2dm1h: 사용자 "시작" — 방향 확인 없이 진행(위 위험을 대화에 알림). `run_f2c.sh f2dm1h … homew` = `-1.65,-3.7,f;0,0,p`, 속도 0.07, STAGE `F2-std-1110`.
- 판정(주행 전): **도착** = 2 목표 SUCCEEDED_XY · SUCCEEDED. **접촉 없음** = 사용자 관찰. 그리고 **자세 판별** = 출발점 도착 뒤 러너의 '출발 대비 최종 map' 과 사용자가 본 실제 위치(테이프 대비)가 0.15 m 안이면 SLAM 자세가 맞았던 것(가설 ①), 크게 어긋나거나 통로에서 정체하면 가설 ② 쪽.

## §8 f2dm1h(1 차 복귀) 실패 → 제자리 자세 다시 잡기 → f2dm1h2 복귀 성공 (사용자: "아까 발로 통로를 바라보게 돌렸다." · "지금 상황에서 복귀하게 만들어라." · "재시작을 하든 출발할 수 있도록 하라.")
- **f2dm1 목표 5 취소 주체 = nav_guard**(`jobs/chk_cancel_1110.sh` → `outputs/chk_cancel_1110.txt`): `nav_guard 개입 — 무진행: 45 s 동안 최대 0.25 m 이동 < 0.25 m → 모든 목표 취소·정지`. 목표 5 시작 때 경로는 있었음(`경로 64 점, 끝 0.318 m 구간 방향 76.3°`) — 그런데 −93° → −10° 로 돌며 정체(stuck_monitor 관찰 `지령 6.1cm/7° 인데 관측 0.1cm/1.3°`). 반대쪽으로 돈 이유는 미확인(bag `bags/f0_f2dm1/` 로 볼 것).
- **f2dm1h(`outputs/run_f2dm1h.txt`)**: `경로 자동 yaw: FAIL 경로 없음(상태 6)` → `목표 1 ABORTED 18.4 s`, 로버 안 움직임(Δ 0.002 m). 계획기 `GridBased: failed to create plan with tolerance 0.25` 반복, monotone_escape 2 회 '성공(최근접 29.0 cm)' 뒤 BT 실패.
  - 추론(추정): 사용자 말로 실제 방향 = 통로 쪽(map 76~92°), SLAM 은 51°, 자이로(EKF)는 ≈ 20° → 자세가 30° 넘게 틀린 채 실시간 장애물이 map 에 돌아간 자리로 찍혀 통로를 막음(10-28 §16.1 '돌아간 벽이 출구 막음' 과 같은 모양). 자이로가 발로 돌린 회전의 약 1/3 만 본 이유(휠 '회전 0' 을 EKF 가 함께 믿었나 등)는 미확인.
- **제자리 자세 다시 잡기**(`jobs/prep_relocalize_1110.sh` → `outputs/prep_relocalize_1110.txt`, 로버 안 움직임): `/initialpose Subscription count: 1` → (x −1.626, y −5.206, yaw 85°, 분산 xy 0.04 · yaw 0.12) 1 회 발행 → `LocalizePoseCallback: Localizing to: (-1.63 -5.21), theta=1.48` → 3 · 8 s 뒤 `[-1.333, -5.452] 102.441° / 102.428°`(안정). 준 값보다 +17° · 위치 0.38 m 옮겨 맞춤 — 실제와의 일치는 직접 확인 못 함(아래 주행 성공이 간접 근거). 코스트맵 비우기 응답 줄은 비어 성공 여부 미확인.
- **f2dm1h2**(`outputs/run_f2dm1h2.txt`, bag `bags/f0_f2dm1h2/`): 게이트 통과(P 47 %) → `경로 71 점` → `목표 1 SUCCEEDED_XY 26.0 s`(서쪽 통로) · `목표 2 SUCCEEDED 140.4 s | 도착 map (0.124, 0.040, -169.1°) 목표 대비 0.131 m` · 총 166.6 s. 접촉은 사용자 관찰 대기.
  - §7 판정: 도착 ✔(2/2). 자세 판별 — 다시 잡은 자세에서 계획 · 도착이 정상이라 '발로 돌린 뒤 자세가 틀려 경로 없음' 쪽이 맞음(간접). 물리 위치(테이프 대비)는 사용자 확인 대기.
  - 목표 2 가 한도 146 s 에 가까움(140.4 s, 4.05 m) — 끝 방향 −170° 로 돌기 · 출발 방 상자 회피 몫인지 미확인.
- 다음에 알아보는 법: 주행 중 사람이 로버 방향을 바꾸면 SLAM · 자이로 둘 다 틀릴 수 있다(이번 30~50°). 그 뒤 '경로 없음' 이면 자세부터 의심 — `/initialpose` 로 대략값을 주면 위치 추정이 스캔으로 다듬는다(이번 +17°).
- 시연 전체: no5 는 목표 4 까지(서쪽 통로 남행 · 남서 도달) 접촉 없이 갔고 목표 5(북행 복귀)에서 nav_guard 취소 → §6 판정 **불합격**. 사람 개입: 발로 방향 바꿈 1 회.

## §9 정정 · 분석: "문서 정리 뒤 주행 품질이 매우 나빠졌다. 상자도 피해가지 못했다." (사용자)
- **정정**(§7 · §8 의 '접촉 없음'): 사용자 "접촉없이 멈췄다" 는 목표 5 정지 순간에 대한 말이었고, 이번 시연에서 **상자를 피하지 못함**(사용자). 어느 주행(f2dm1 / f2dm1h2) · 어느 상자 · 시각은 사용자 확인 대기 → §6 · §7 판정의 '접촉 없음' 은 **불합격**으로 고친다.
- 가설 ① "문서 정리(11-02 ~ 11-04 커밋)가 동작을 바꿨다" — 판별:
  - 실행 중 파라미터: 오늘 `bags/f0_f2dm1/bag_f2dm1.tgz` 의 `params.txt`(12 노드: controller · local/global costmap · planner · smoother · bt_navigator · behavior · velocity_smoother · slam_toolbox · ekf · stuck_monitor · depth_relay) ↔ 10-27 f2tt1(`2026-10-27/bags/bag_f2tt1.tgz`) 차이 = **`ClearanceBandCritic` 이 MPPI critics 목록에서 빠짐 하나**(f2tt1 에서도 `enabled: False` — 동작 영향 없음으로 봄, 추정).
  - 코드: `git diff a813ac8a HEAD`(10-27 16:00 직전 → 지금)의 주석 아닌 줄 = launch 기본값을 prep 이 넘기던 값과 같게(11-04 §17: emitter_off · dds_shm · vslam · replan_hz · mppi_viz · global_camera · stuck_shadow), launch 가 덮어쓰는 `plugins` 줄, prep_fast 의 PreferForward 처리(같은 15.0), prep_patrol rf2o 판 명시. nvblox · 카메라 값 같음. 펌웨어 변경은 주석(재플래시 안 함).
  - 결론: **코드 · 실행 값으로는 문서 정리가 동작을 바꾼 근거 없음.**
- 가설 ② "오늘 쓴 '표준 prep' 조합이 검증된 적 없다" — 기록(`outputs/anal_drive_results_runs.csv` · 10-26 SUMMARY 227 행 · 10-28 SUMMARY 9 행):
  - MPPI PathAlign 28 · PathFollow 5(10-26) · transform_timeout 1.5 · 수정 nvblox 층(10-27) 뒤의 주행 f2sa1~3 · f2st1 · f2tf1 · f2tt1 · f2tt2 는 **전부 `NAV_ADD="planner:=smac" REPLAN_HZ=0.01`**.
  - NavFn + 재계획 0.5 Hz 의 마지막 주행 = 10-23 f2rp · f2von(그때 MPPI 14 · 10, timeout 0.5).
  - → 오늘 조합(NavFn + 0.5 Hz + MPPI 28 · 5 + timeout 1.5)은 **처음 달린 것**. 11-04 정리에서 CURRENT_STACK · CLAUDE.md 가 '표준 prep = navfn · 0.5 Hz' 로 적고 launch 기본도 그렇게 맞췄으나, 그 사이 바꾼 값은 Smac · 0.01 시험에서만 검증됐다. 11-10 §0 내 점검도 '문서 ↔ 코드 일치' 만 보고 '그 구성이 검증됐나' 는 보지 않았다(점검 빈틈).
  - 결론(추정 — A/B 전): 품질 저하의 가장 유력한 설명 = 문서 정리가 코드를 바꾼 것이 아니라 **검증 안 된 조합을 '표준' 으로 정의**한 것.
- 다음에 알아보는 법: 구성 문서를 고칠 때 '이 값 조합으로 마지막에 성공한 주행 이름' 을 같이 적는다 — 이름이 없으면 그 조합은 미검증.
- 판별 시험(제안, 사용자 결정): 같은 no5 를 마지막 검증 구성(`NAV_ADD="planner:=smac" REPLAN_HZ=0.01` = f2tt1 · f2tt2)으로 1 회 → 상자 회피 · 목표 5 정체가 사라지면 ② 확정. 그 전에 bag 으로 접촉 순간(사용자 확인 시각) 의 코스트맵 상자 칸 · 경로 · MPPI 를 `Docs/tools/anal_box_history.py` 로.

## §10 판별 시험 f2dm2 — 마지막 검증 구성(f2tt1 · f2tt2)으로 같은 no5 (사용자: "마지막으로 검증된 구성으로 수행해보자.") — 선언(주행 전)
- 구성: `jobs/prep_smac_1110.sh` = `NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite`(10-28 `prep_smac_1028.sh` 와 같음). 코드 · 배포는 §9 대로 f2tt1 과 같음(꺼진 크리틱 1 줄만 다름).
- 코스 · 러너: §6 과 같은 `no5`, 속도 0.07, NAME `f2dm2`, STAGE `F2-tt-1110`(10-28 f2tt2 와 같은 구성 표시), NOTE `11-10 §9 판별: 검증 구성(smac·0.01)으로 no5`.
- 출발: 사용자가 로버를 출발 테이프 위 · **처음 방향(yaw 0)** 으로 놓음(직전 f2dm1h2 가 −169° 로 서서 반대 방향) → prep(출발 위치 검사 ±0.10 m · ±2°) → 사용자 "시작" 뒤 러너.
- 판정(주행 전 선언):
  - **도착**: 8 목표 SUCCEEDED(4 번째 SUCCEEDED_XY).
  - **접촉 없음**: 사용자 관찰(상자 · 벽 · 의자).
  - **§9 가설 ② 판별**: f2dm2 가 도착 + 접촉 없음이고 목표 5 를 nav_guard 취소 없이 지나면 → '오늘 저하 = NavFn · 0.5 Hz 조합 탓' 을 지지(1 회라 확정은 아님 — f2dm1 과 같은 자리 · 같은 상자 배치에서 비교). f2dm2 도 상자를 못 피하면 → 조합 말고 다른 원인(상자 배치 · 센서 · 오늘 상태)을 본다.
  - 시간(참고): f2tt1 412.2 s · f2tt2 413.7 s.
- **선언 변경(prep 뒤 · 주행 전, 사용자 "서쪽 통로 쪽 회전 하는 위치 공간이 너무 좁은데, 더 들어가서 회전하도록 하자.")**: prep `outputs/prep_smac_1110_1.txt` = `PREP_OK`(위치 차 0.017 m · yaw +0.1° · `BT RateController hz="0.01"` · planner tol 0.35 REEDS_SHEPP). 코스를 `no5` → **`no5d`**: 목표 4 를 (−1.6, −5.5) → **(−1.5, −5.85)**(위치만 f) — `jobs/run_f2c_1110.sh`(10-22 래퍼 사본 + NO5D). 근거 `figures/sw_area_office_v3.png`(office_v3: 남서 목표 바로 아래 y −5.6 ~ −6.2 가 동서로 트임, x = −1.6 열 y −5.3 ~ −6.25 빈칸 · −6.30 벽): 제자리 회전 외접 반경 ≈ 0.31 m(계산 √(0.262² + 0.165²)) 대비 남쪽 벽 ≈ 0.40 m · 서쪽 벽(x ≈ −2.05) ≈ 0.55 m(지도 기준, 계산). 지도는 10-02 — 지금 그 방 물건은 미확인.
  - ⚠ 이 변경으로 §10 의 'f2dm1 과 같은 코스' 비교가 목표 4 · 5 구간에서 깨진다 → 목표 5 결과는 구성 · 회전 지점 둘이 섞인 것으로 읽는다. 목표 1 ~ 3 · 6 ~ 8 구간(상자 회피 포함)은 같은 코스로 비교 가능.
- **결과 → 11-11 §0 · §1**(주행은 목표 3 진행 중 사용자 강제 종료, Jetson 재부팅으로 bag · 러너 원문 소실 — `~/.ros/log` 노드 로그로 재구성: 목표 1 · 2 성공, 3 미완, §10 판정 불가).
