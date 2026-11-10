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
