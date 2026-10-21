# 2026-10-21 — 출발 위치 추정 검사 · 정지 부하 게이트 · f2sm1(공유메모리 그림자 주행)

## §0 하루 시작
- 사용자: "오늘 할 일 뭐냐" → 제안 순서 2 → 1(위치 추정 검사 넣고, 게이트 P 정한 뒤 f2sm1) → "진행하라".
- Jetson 09:16 재부팅 → `/tmp` prep 5 개 없음(재전송), Isaac 컨테이너 정지(nvblox_up.sh 가 docker start), 스택 없음, 배터리 12.4 V, 디스크 129 GB 남음. 원문 `outputs/chk_day_start_1021.txt`.

## §1 출발 위치 추정 검사 (prep 확인에 추가)
- 하려는 것: 10-20 에 prep 직후 SLAM 이 출발 위치를 21°(f2z2 출발) · −41°(d4b 정지 prep) 틀린 적 2 회 — 틀린 채 주행하면 지도 좌표 목표가 엉뚱해진다. 원인 조사 전에 **주행 전에 걸러지게** 한다.
- 본 것(근거): 10-20 정상 prep 15 회의 map→odom = yaw −0.02~1.01°, 위치 3 cm 안(§8.3 · §9.5). 실패 2 회는 21° · 41° · 위치 0.36~0.4 m.
- 만든 것: `Docs/tools/chk_prep.py` — 준비 · 재마킹 뒤 map→base 를 기대 자세(환경 `PREP_POSE`, 기본 `0,0,0` = 출발 테이프)와 비교, **위치 ±0.10 m · yaw ±2°** 밖이면 `★ 불합격` + PREP_FAIL. 출발 테이프가 아닌 곳에서 prep 할 땐 `PREP_POSE=any`(끔) 또는 `'x,y,yaw'`.
  - 한도 근거: 정상 최대(1.0° · 3 cm)의 2 배 · 3 배 여유, 실패(21°)의 1/10.
- 미확인: 실패 원인(SLAM 위치 추정이 초기 자세를 어떻게 잡는지) — 다시 나오면 그 prep 의 slam.log 를 남겨 본다.

## §2 정지 부하 게이트(P) — 그림자 구성에서만 65 %
- 본 것: 10-20 f2sm1 3 차 시도 게이트 P = 62 % > 60 % 로 주행 안 함(§9.7).
- 게이트 출처(job551 주석 · 10-01 §8.9): f2a3 주행 중 CPU 88 %(sy 31 %)에서 서버 응답 시간 초과 → '출발 전에 이미 무거우면 주행하지 않는다'. 당시 정지 기준선 36 % → 한도 60 % = 기준선 + 24 %p.
- 지금 기준선(측정): 기본 구성 45~48 %(10-19 · 10-20), 그림자 + SHM 구성 54.0 · 54.6 · 55.0 %(10-20 §9.3 정지 A/B) · f2v1 게이트 56 %. → 그림자 구성에선 60 % 한도와의 여유가 4~6 %p 뿐이라, 게이트가 '비정상' 이 아니라 평소 흔들림을 잡는다.
- 결정(내 판단, 사용자 "진행하라" 위임): 기본 60 % 그대로, **그림자 구성 주행에서만 `LOAD_MAX=65`**(그 구성 기준선 + ≈ 10 %p). 65 % 도 넘으면 한도를 더 올리지 않고 원인을 찾는다.
- 도구: 스크래치패드 `run_f0.sh` 가 `LOAD_MAX` 를 Jetson 러너로 넘기도록(기본 60) — 전엔 안 넘겼음.
- 시험(원문 `outputs/prep_sm_1021_1.txt`): 그림자 + SHM 구성 prep → `위치 추정 검사(기대 0,0,0): 위치 차 0.008 m · yaw 차 +0.8° → 통과`, PREP_OK. 불합격 경로도 확인 — `PREP_POSE=0,0,10` 으로 `chk_prep.py` 만 다시: yaw 차 −9.2° → `★ 불합격`, PREP_FAIL, 종료 코드 1.

## §3 스크래치패드 러너 파일 소실과 복구
- 본 것: `put_one.sh` 가 없다는 오류 → 스크래치패드를 보니 `put_one.sh` · `job550_f0run.py` · `job613_pathyaw.py` 가 없음(어제 f2v1 은 이 파일들로 돌았음). 남은 파일의 수정 날짜: 10-14 이후만(10-02 1 개 예외), 10-13 이전 것이 사라짐.
- 추론: Windows 임시 폴더의 오래된 파일 자동 삭제(일주일쯤 지난 것)로 추정 — Storage Sense 설정은 확인 안 함(미확인).
- 복구: 저장소의 가장 새 사본(10-13 jobs)으로 되돌림. 10-14 이후 기록에 두 파일을 고쳤다는 내용 없음 → 마지막 판으로 봄(배포 해시는 run_meta 에 러너 파일이 안 남아 대조 불가).
- 대비: 지금 러너 묶음(job550 · job551 · job613 · run_f0 · run_f2c · put_one)을 `jobs/` 에 사본 보관. `run_f0.sh` 사본은 비밀번호 4 곳을 `<PW>` 로 가림(`run_jn.sh` 는 비밀번호가 있어 저장소에 안 넣음 — 스크래치패드에서 사라지면 사용자에게 다시 받아야 함).

## §4 WEB_DEV_5G 소실 → Jetson 이 ALOPS 로 전환, 스택 통신 끊김(10:48)
- 사용자 알림: 내부망 분배기 문제로 192.168.0.110 핑 무응답, 보드 화면엔 `192.168.0.110?`.
- 본 것:
  - PC 에서 192.168.0.110 핑 100 % 손실, 172.30.1.8 응답. ARP MAC `58-02-05-bd-d5-35` = Jetson 무선 MAC(09-17 `j427_wifi.txt` 와 같음) → 다른 기기 아님.
  - Jetson 기록: 10:48:27 연결 끊김 → 스캔 두 번에 `WEB_DEV_5G` 가 안 보여 `ssid-not-found` 로 실패(10:48:42) → 10:48:45 `ALOPS_ROBOTICS_5G` 172.30.1.8 연결. 지금 스캔에도 `WEB_DEV`·`WEB_DEV_2G` 는 보이고 `WEB_DEV_5G` 만 없다 → AP 쪽 5 GHz 송출이 멈춘 것(사용자 설명과 맞음). 09-15~17 의 deauth·PSK 거부와는 다른 유형.
  - 스택 프로세스(agent · display_info_pub · EKF 2 · slam · controller · realsense · cuVSLAM · vslam_twist)는 모두 살아 있지만, 새 참여자로 보면 `/rover/display_info` · `/wheel_odom` · `/vslam/odom` · `/odometry/filtered` 가 하나도 안 보인다.
- 추론: 보드 화면의 `?` 는 펌웨어가 15 s 넘게 `/rover/display_info` 를 못 받았다는 뜻(`display_info_pub.py` 머리 주석). 발행 노드는 살아 있으므로 Jetson 안의 DDS 통신 자체가 끊긴 것 — 주소가 바뀐 뒤 기존 참여자가 옛 주소 기준으로 묶여 있는 것으로 추정(기전 미확인). CLAUDE.md "Wi-Fi 재연결 뒤엔 스택 재기동" 과 같은 상황.
- 결론: 지금 떠 있는 스택은 못 쓴다 → prep 재기동 필요. 러너들은 모두 `JETSON_HOST` 를 받으므로 172.30.1.8 로 넘기면 된다.

## §5 ALOPS 재기동 1 회차 PREP_FAIL — 보드 토픽 0 Hz(에이전트도 옛 주소에 묶임)
- 하려 한 것: §4 결론대로 `prep_sm_1021.sh`(그림자 + SHM prep)만 `JETSON_HOST=172.30.1.8` 로 다시 실행.
- 본 것(`outputs/prep_sm_1021_2.txt`): nvblox · cuVSLAM · vslam_twist · ekf_vslam 은 떴고 `/odometry/filtered 30.0 Hz · /tf 50.0 Hz` 인데 `/wheel_odom 0.0 Hz · 배터리 ? V` → PREP_FAIL.
- 처음 추론(§4): "prep 이 스택을 다시 띄우면 된다". 그런데 prep(`prep_fast.sh` 2 단계)은 micro-ROS 에이전트 컨테이너를 **검사만 하고 재시작하지 않는다** — 에이전트는 09:17 부터 그대로, 즉 옛 주소에서 만든 DDS 참여자. 보드 쪽 USB 는 정상(`/dev/rover → ttyCH341USB0` 존재, 커널 기록에 끊김 없음).
- 판별: 에이전트 컨테이너만 `docker restart` → 에이전트는 `running...` 까지 떴지만 `session established` 없음, `/wheel_odom` 여전히 없음(`outputs/fix_agent_1021.txt`).
- 결론: 펌웨어는 리셋 직후 한 번만 세션을 만들고(`microros_task.c:222` 대기 루프 뒤엔 재접속 없음) 새 에이전트를 찾아가지 않는다 → **보드 리셋이 필요**. 이 순서(주소 변경 → 에이전트 포함 전체 재기동 → 보드 리셋)는 09-16 · 09-23 에 이미 기록해 둔 규칙인데, §4 에서 그 기록을 먼저 찾아보지 않고 "prep 재기동" 으로만 결론 냈다.
- 다음에 알아보는 법: Jetson 주소가 바뀌면 ① 에이전트 컨테이너 재시작 ② 보드 RESET ③ prep 순서. 서명 = prep 에서 `/odometry/filtered` 는 나오는데 `/wheel_odom 0.0 Hz · 배터리 ? V`. 에이전트 재시작 확인은 `docker logs --since` 로 새 로그만 센다(첫 확인 스크립트가 재시작 전 로그 1 건을 세어 1 s 만에 빠져나온 결함 있었음).

## §6 보드 리셋 뒤 복구 — PREP_OK (ALOPS 172.30.1.8)
- 사용자 보드 RESET → 11:30 세션 수립 1 건, `/wheel_odom 24.99 Hz`(아침 prep 과 같은 25 Hz) · `/battery 1.0 Hz`(`outputs/fix_agent_1021.txt`).
- prep 재실행(`outputs/prep_sm_1021_3.txt`): `위치 추정 검사(기대 0,0,0): 위치 차 0.004 m · yaw 차 -0.5° → 통과`, `/wheel_odom 25.0 Hz · /odometry/filtered 30.0 Hz · /tf 49.7 Hz · 배터리 12.32 V`, PREP_OK, nvblox · cuVSLAM · vslam_twist · ekf_vslam 각 1. 70 s.
- 오늘 이후 러너는 `JETSON_HOST=172.30.1.8` 로 부른다(분배기 복구 뒤 WEB_DEV 로 되돌리면 §5 순서를 다시 밟는다).

## §7 f2sm1 공유메모리 그림자 주행 결과 (판정 기준은 10-20 §9.6 에 주행 전 선언)
- 원문: `outputs/run_f2sm1.txt`(러너) · `run_meta_f2sm1.txt` · `chk_f2sm1_logs.txt`(vslam_twist 10 s 통계 · cuVSLAM 경고 시각) · `gaps_f2sm1.txt`(bag 토픽 간격, `jobs/anal_topic_gaps.py`) · `anal_shadow_f2sm1.txt`(`2026-10-20/jobs/anal_ekf_replay.py`, `RTOPICS=/odometry/ekf_vslam`, cuVSLAM = bag 의 `/visual_slam/tracking/odometry`) · 그림 `figures/shadow_f2sm1.png`(범례의 '재실행 EKF_VSLAM' 은 이 경우 주행 중 실시간 그림자 EKF — 스크립트 이름표를 그대로 씀).
- 구성: 프로젝터 상시 끔 + `vslam:=shadow` + `dds_shm:=true`, 상자 둠, 코스 b910, ALOPS 172.30.1.8, 게이트 P 65 %(정지 부하 53 % 로 통과). f2v1 과 다른 것은 SHM(과 망) 뿐.

| 기준(§9.6) | f2sm1 | f2v1(10-20, UDP) | 판정 |
|---|---|---|---|
| 1. 3/3 · 중단 0 | 3/3 · 53.8 / 49.2 / 105.7 s · stuck 진단 1 · map→odom 누적 (−0.04, +0.51) m · −4.2° | 3/3 · 51.8 / 49.8 / 101.4 s | ✔ |
| 2a. `/vslam/odom` ≥ 14 Hz | 15.0 Hz(bag) | 9.5 Hz | ✔ |
| 2b. 0.5 s 넘는 끊김 ≤ 2 | 2(둘 다 bag 시작 t≈3.9 s, 최대 0.66 s) — cuVSLAM 원 출력은 0 | 38(최대 3.8 s) | ✔(경계) |
| 2c. vslam_twist 버림 ≤ 1 / 10 s | 주행 4 분 내내 10 s 마다 출력 142~154 · **버림 0** | 출력 61~119 · 버림 4~18 | ✔ |
| 3a. W3 회전 최대 창 ≥ 10 % 작음 | 주 EKF 24.1 → 그림자 **16.1 cm(−33 %)** | 27.5 → 22.1(−20 %) | ✔ |
| 3b. 상자 옆 +2 cm 넘게 안 나빠짐 | 출발 4.3 → 5.2 · 복귀 2.5 → 3.1 cm(+0.9 · +0.6) | 3.7 → 4.0 · 3.2 → 3.1 | ✔ |
| 4. 부하 f2v1 범위 | top 평균 사용 75.7 %(같은 계산으로 f2v1 75.0 %) | 75.0 % | ✔ |

- 그 밖: 전 구간 95 % 16.0 → 10.4 cm, 절대 끝 51.2 → 32.4 cm(cuVSLAM 단독 5.5 cm). cuVSLAM 프레임 간격 경고(> 80 ms)는 주행 4 분 동안 5 회(11:40:05 × 2 = bag 시작, 11:40:49 · 11:40:57 · 11:42:59) — f2v1 은 10 s 에 20~30 회.
- 읽기:
  - **입력이 빠지지 않자 효과가 커졌다**: W3 −20 % → −33 %. 10-20 §6.4 의 추정("입력 빠진 구간은 휠·자이로만으로 적분돼 효과가 깎인다")과 맞는 방향. 다만 주행 1 회씩 비교라 미끄러짐 크기 자체가 달랐을 수 있다(주 EKF W3 최대 27.5 vs 24.1 cm) — −33 % 는 재실행 예상 범위(−12~29 %)를 약간 넘는다. 반복 확인 필요.
  - 상자 옆은 그대로(+0.6~0.9 cm, 한도 안) — 예상대로 이 경로로는 상자 번짐이 안 준다.
  - 그림 아래 칸: 그림자 EKF 의 절대 오차도 W3 뒤 처음엔 내려가다(cuVSLAM 쪽으로) 이후 주 EKF 와 같은 기울기로 다시 쌓인다 — 그림자 EKF 의 yaw 는 여전히 휠·자이로(cuVSLAM 은 vx·vy 만 넣음)라 방향 드리프트는 그대로이기 때문으로 추정(미확인).
- 결론: §9.6 네 기준 모두 통과. 공유메모리로 cuVSLAM 입력 빠짐이 주행 중에도 해소됨을 확인(10-20 은 정지 시험까지만 확인).

## §8 그림자 반복 f2sm2 · f2sm3 선언 (사용자 "1번 진행하자", 주행은 "시작" 뒤에만)
- 목적: f2sm1 의 W3 −33 % 가 한 번짜리인지 확인 → `vslam:=on`(주 EKF 에 넣기) 시험 여부 결정.
- 이름 f2sm2 · f2sm3(저장소 · 스크래치패드 어디에도 없음 확인). 구성 · 코스 · 러너 인자는 f2sm1 과 같음(NOTE 만 다름). 주행 사이에 로버를 출발 테이프로 되돌린 뒤 prep 재실행(위치 추정 검사 포함).
- 판정(주행마다): 10-20 §9.6 의 네 기준 그대로(3/3 · `/vslam/odom` ≥ 14 Hz · 끊김 ≤ 2 · 버림 ≤ 1/10 s · W3 ≥ 10 % · 상자 옆 +2 cm 이내 · 부하 f2v1 범위).
- 반복 판정(세 번 f2sm1~3 모아서): **W3 감소가 세 번 모두 ≥ 10 % 이고 평균 ≥ 20 %** 면 `vslam:=on` 시험으로 간다. 한 번이라도 < 10 % 면 원인(미끄러짐 크기 · 입력 빠짐)을 먼저 본다. 범위(최소~최대)를 기록하고, 주 EKF W3 최대(미끄러짐 크기)와 감소율을 나란히 적는다.

## §9 f2sm2 1 차 — 게이트 C 불합격(주행 안 함) · 스크래치패드 파일 또 소실
- 하려 한 것: §8 대로 prep(`outputs/prep_sm_1021_4.txt`: 위치 차 0.006 m · −0.6°, PREP_OK) 뒤 f2sm2.
- 본 것(`outputs/run_f2sm2_attempt1.txt`): 게이트 A · B · J 통과, **C 불합격** `map->odom 100 개/5 s, 최대 간격 0.11 s, 최대 stamp 지연 1.05 s`(한도: 간격 < 0.5 · 지연 < 1.0 s, `job386_slamalive.py`). 로버 안 움직임.
- 판별: 1 분 뒤 같은 검사 3 회(`outputs/chk_slamlag_1021.txt`) → 지연 0.09 / 0.29 / −0.32 s, 간격 ≤ 0.09 s 모두 OK, 정지 부하 ≈ 51 %. 09-17 기록상 정상 SLAM 지연은 −0.08~+0.55 s 로 흔들리고 고장 때는 간격 5.1 s · 지연 4.8 s → 이번은 간격이 정상인 채 지연만 한 번 문턱을 넘은 경계값. prep 직후(≈ 1 분)의 일시 지연으로 보고 같은 주행 재시도(원인 미확인).
- 함께 본 것: 러너 로그에 `rescued_jetson_tmp/job386_slamalive.py: No such file or directory` 등 4 건 — 스크래치패드 `rescued_jetson_tmp/` 폴더가 사라짐(f2sm1 러너 로그엔 이 오류가 없다. 그런데 WSL `/tmp/xf0/` 의 네 사본 수정 시각이 10-14 라 f2sm1 때도 새로 쓰이지 않았을 수 있다 — 서로 맞지 않음, 언제 사라졌는지 미확인). 전송 단계는 실패했지만 WSL `/tmp/xf0/` 에 남은 10-14 사본이 대신 올라갔고, 그 4 개는 저장소 사본(09-17 · 09-18 · 09-22 jobs)과 md5 같음 → 게이트 코드는 평소와 같았다. 저장소 사본으로 폴더 복구. §3 에서 복구 대상을 파일 3 개로만 보고 이 폴더를 안 살폈다 — 같은 소실의 일부일 수 있음, 기전 미확인(남은 파일 414 개, 10-14 이후 것만).

## §10 f2sm2 2 차 — 목표 2(W3) 중단 · **사람들이 일부러 길을 막음(사용자)** → 반복 비교에서 제외, 동적 물체 대응 근거로 사용
- 사용자: "이번에 사람들이 앞에서 길을 막으면서 주행을 일부러 방해했다 — 균일한 실험 환경이 아니므로 비교용으로 부적합, 동적 물체가 앞에서 길을 막을 때 어떻게 움직였나 판단하는 근거로 쓰자." → **f2sm2 는 §8 반복 판정(f2sm1~3)에서 뺀다.** 반복 비교는 다른 이름(f2sm3 · f2sm4)으로 채운다.
- 결과(`outputs/run_f2sm2.txt`): 게이트 모두 통과(C 이번엔 통과) → 목표 1 SUCCEEDED 53.4 s · **목표 2 ABORTED 74.9 s**, W3 앞 (5.12, −1.89) 에서 멈춤(목표 대비 0.49 m). 누적 회전 휠 25.8° vs EKF −18.5°(차 44.3° — f2sm1 11.3°), stuck 진단 2. 로버는 W3 근처에 정지해 있음.
- 무엇이 길을 막았나(`jobs/anal_goal_block.py`, 원문 `outputs/anal_goal_block_f2sm2.txt`; W3 목표 반경 0.6 m 안의 라이다 점 · 전역 코스트맵 칸, t = bag 시작 기준):
  | t (s) | 로버 | 라이다 점(반경 안) | 전역 LETHAL 칸 · 가장 가까운 칸 |
  |---|---|---|---|
  | 100 · 110 | (3.6~4.2, −1.4~−1.7) | 0 | 0 |
  | 115 | (4.44, −1.90) | 0(0.65 m 에 점) | 29 · 0.32 m |
  | 120 · 125 | (4.5~4.6, −1.9) | **101 · 128**(가장 가까운 0.20 m) | 44~46 · 0.07~0.12 m |
  | 128 ~ 141.6 | (4.76~5.13, −1.8~−1.9) | **0** | **38~40 · 0.17 m 그대로** |
  - 읽기: t 115~125 에 목표 자리에 라이다로 보이는 물체(사람으로 봄 — 사용자 증언과 시각이 맞음) → t 128 부터 라이다엔 아무것도 없는데 **전역 코스트맵의 LETHAL 칸은 끝(14 s 뒤)까지 남음** → `PathBlockedAhead: (5.50, −2.20) 비용 99 가 2.0 s 지속 → 주행 중단 · 재계획` 반복, `GridBased failed to generate a valid path to (5.50, −2.20)` → 12:18:06 `Goal failed`(nav2 원문 `outputs/chk_abort_f2sm2.txt`).
  - 남은 칸을 누가 들고 있었나: 전역 코스트맵 = nvblox 층(감쇠 0.99 · 기억) + 라이다 ObstacleLayer. 라이다 층은 로버가 0.4~0.7 m 앞에서 빈 곳을 보면 광선으로 지우므로 **nvblox 층이 사람을 기억한 것으로 추정(미확인 — 층별 코스트맵이 bag 에 없음)**. 앞 구간(t 16~45)에도 `PathBlockedAhead`(1.5~2.6, −0.1~−1.5) · `Optimizer fail` 5 회 — 같은 방해로 봄(목표 1 은 53.4 s 로 f2sm1 과 비슷하게 도착).
- 동적 물체 대응으로 본 것(이번 1 회): ① 사람이 길에 있을 때 정지 · 재계획은 했다(충돌 없음, 사용자 확인 필요). ② **사람이 떠난 뒤에도 기억이 목표 칸을 막아 목표 자체를 포기**했다 — 09-29 사용자 요구 "사람 다니는 실내에 강건"([[dynamic-people-robustness]]) 에 어긋나는 행동. ③ 회전 미끄러짐이 컸다(휠−EKF 44°) — 막힌 곳에서 제자리 돌기가 반복된 탓으로 추정.
- ⚠ 분석 도구 첫 판 오류: 코스트맵 메시지 값은 0~100 으로 바뀌어 있는데(100 = LETHAL, 99 = INSCRIBED) ≥ 253 으로 LETHAL 을 세어 늘 0 이 나왔다. 서명 = 'LETHAL 0' 인데 nav2 는 '비용 99' 를 말함. 고친 판으로 위 표를 냄.

## §11 사용자 요청: 출발점 복귀(f2sm2h) · f2sm2 영상 · 복귀 중 멈춤 분석
### §11.1 f2sm2 영상 (`Docs/tools/fig_run_video.py`, 2 배속, 로컬 `figures/f2sm2_people_block.mp4` — mp4 는 git 제외)
- 장면 `figures/f2sm2_frame_60.png`(12:17:46): 목표 (5.5, −2.2) 바로 옆 (5.3, −2.2) 에 라이다 점 호(사람 다리로 봄) · 둘레 전역 LETHAL.
- 장면 `figures/f2sm2_frame_67.png`(12:18:01): 그 자리 라이다 점 없음, (5.0~5.3, −2.2~−2.5) 빨간 칸은 그대로 → 6 s 뒤 Goal failed. §10 표와 같은 이야기.
### §11.2 복귀 주행 f2sm2h (`run_f2c.sh` 에 `home` = `0,0,p` 추가; 원문 `outputs/run_f2sm2h.txt`)
- 사용자 요청("출발 테이프로 되돌아오게") 으로 주행. 게이트 통과 → 목표 (0, 0) **SUCCEEDED 112.9 s**, 경로 5.47 m, 도착 목표 대비 0.147 m · −166°(뒤 보고 도착 — 평소 끝 자세). 휠−EKF 회전 차 37°, stuck 진단 1(그림자, 조치 없음). 비교용 아님.
### §11.3 복귀 중 '중간중간 멈춤' (사용자 관찰) — 원문 `outputs/anal_stops_f2sm2h.txt` · `anal_cmd_dips_f2sm2h.txt` · `nav_events_f2sm2h.txt` · `chk_bt_f2sm2h.txt`, 그림 `figures/stops_f2sm2h.png`
- 도구: `jobs/anal_stops.py`(EKF 속도 |v| < 0.01 · |ω| < 0.05 가 MIN_STOP 넘게 → 멈춤, 그때 /cmd_vel · 앞 라이다 · nav2 사건), `jobs/anal_cmd_dips.py`(/cmd_vel 전진 명령이 0 근처로 떨어진 묶음을 nav2 사건과 맞춤).
- 본 것: 0.3 s 넘게 선 것 3 번(합 6.5 s) + 명령이 잠깐 0 으로 떨어진 '멈칫' 13 번(0~0.45 s).
  1. **12:31:11~16 5.1 s 정지 @ (2.88, −1.45)**: 12:31:09~10 `PathBlockedAhead: 앞 경로 (2.20, −0.85) 비용 99` + `Smoothed path leads to a collision` → 12:31:11 FollowPath 중단 → behavior_server `Running wait`(12:31:11) · `wait completed`(12:31:16). 즉 **BT 복구 RoundRobin 의 Wait 5 s 차례**가 걸린 것(`nav_to_pose_no_spin.xml` 124 행). 그동안 /cmd_vel 5 개뿐(평소 20 Hz). 앞 라이다 최소 0.93 m — 바로 앞이 막힌 건 아님.
  2. **12:31:54~55 1.0 s @ (1.35, 0.05)**: `Optimizer fail to compute path` 3 회 · `PathBlockedAhead (0.93, 0.09) 비용 99` · 클리어 요청 → 곧 재개. 출발점 앞 0.9 m — 출발점 근처 낮은 상자([[start-low-box-test]]) 둘레로 추정(미확인).
  3. **짧은 멈칫 13 번**: 8 번은 FollowPath 중단 → 새 목표 수신(컨트롤러 재시작) 직후, 4 번은 `Passing new path to controller`(재계획 0.5 Hz) + `Control loop missed its desired rate`(43 회) 무렵, 1 번 기타. 컨트롤러가 다시 시작하거나 경로가 바뀌는 순간 명령이 0 으로 한두 주기 떨어지는 모양(기전 미확인).
- 읽기: 멈춤의 공통 뿌리는 **경로 앞(0.3~1.5 m)의 전역 비용 99(내접) 칸** → PathBlockedAhead 가 주행을 끊고 → 재계획 · 복구로 넘어가는 흐름. 그 칸이 무엇인지(상자 · 사람 기억 · 벽 번짐)는 이 bag 만으로는 미확인 — f2sm2 에서 사람이 남긴 nvblox 기억이 복귀 경로 쪽에도 남아 있었을 가능성 있음(f2sm2 때 (1.5~2.6, −0.1~−1.5) 에도 PathBlockedAhead · §10). Wait 5 s 는 복구 순서상 필연이 아니라 RoundRobin 차례 — 같은 막힘에서도 클리어 · MonotoneEscape 차례면 짧게 끝난다.

## §12 사용자 질문: ① f2sm2 가 W3 에서 중단되고 복귀하지 못한 이유 ② 복귀(f2sm2h) 중 짧은 멈칫 원인
- 원문: `outputs/nav_events_ms.txt`(nav2 사건 0.01 s 시각, `chk_nav_ms.sh`), `anal_dip_events_f2sm2h.txt`(`jobs/anal_dip_events.py`), `chk_tf_extrap.txt`, `chk_dip_omega.txt`.
### §12.1 W3 중단 → 복귀 안 함
- 본 것(12:17:40 ~ 12:18:06): `PathBlockedAhead … (5.50~5.55, −2.20~−2.30) 비용 99 가 2.0 s 지속 → 주행 중단 · 재계획` 6 회, 그 사이 계획기 `GridBased failed … tolerance 0.25` 2 회, 복구 차례 MonotoneEscape(12:17:47, 12:18:04 — 둘 다 '최근접 14 cm, 성공' 으로 아무 것도 안 함) · Wait 5 s(12:17:54~59), 마지막 12:18:06 `navigate_to_pose Aborting` · `Goal failed`.
- 추론:
  1. **목표 칸 자체가 비용 99** 로 남았다(§10: 사람이 떠난 뒤에도 LETHAL 38~40 칸). PathBlockedAhead 는 로버 앞 0.3~1.5 m 경로 점을 보는데, W3 0.5 m 앞까지 오면 **경로 끝 = 목표점이 그 범위에 들어와 매번 2 s 만에 주행을 끊는다** — 목표가 막힌 칸이면 끝까지 갈 방법이 없다.
  2. 복구가 그 칸을 못 지운다: 복구의 클리어는 `ClearCostmapExceptRegion reset_distance 3.0`(전역) — **로버 3 m 안은 지우지 않는다**(09-11 결정: 가까운 진짜 장애물을 잊지 않게). 사람 기억은 로버 0.5 m 앞이라 그대로.
  3. 복구 횟수 소진: BT 최상위 `NavigateRecovery number_of_retries="6"` — 목표 2 동안 FollowPath 실패(12:16:56 · 57 Optimizer fail)와 위 6 회 중단으로 재시도를 다 써서 Goal failed.
  4. 복귀를 안 한 것은 **러너 설계**: `job550_f0run.py` 176 행 `if not name.startswith('SUCCEEDED'): break` — 목표 하나라도 실패하면 남은 목표(출발점 복귀 포함)를 보내지 않는다(실패 뒤 자동으로 더 움직이지 않게 한 안전 쪽 선택). 그래서 사용자 요청으로 f2sm2h 를 따로 보냄.
- 결론: 사람이 떠난 뒤 남은 기억(§10) × 목표 근처에서 PathBlockedAhead 가 목표점까지 검사 × 3 m 안은 안 지우는 복구 — 셋이 겹쳐 '비어 있는 목표' 를 포기했다. 기억을 누가 들고 있는지(nvblox 층 추정)는 미확인.
### §12.2 복귀 중 짧은 멈칫 13 번(+ 정지 2 번)
| 묶음 | 수 | 서명(0.01 s 시각 맞춤) | 원인 |
|---|---|---|---|
| A | 6 (12:30:27 · 28, 12:31:08 · 11 · 27 · 28) | 멈칫 −0.96~+0.07 s 에 `Exception in transformPose: Lookup would require extrapolation into the future` → `Unable to transform robot pose into global plan's frame` → `follow_path Aborting` → 곧 `Received a goal` | MPPI 가 로버 자세를 경로 좌표(map)로 못 옮겨 컨트롤러 중단 → 0 명령 → 재시작. 12:31:11 건은 그 뒤 PathBlockedAhead 와 겹쳐 복구 Wait 5 s(§11.3 의 5.1 s 정지) |
| B | 4 (12:31:21 · 34 · 36 · 37) | 사건 없음 처럼 보였으나 `Control loop missed its desired rate of 10 Hz` 가 12:31:21.53 · 34.60 · 36.96 · 37.58 — 멈칫 바닥과 0.01~0.09 s 안. v 와 ω 가 함께 0 으로 5 주기(0.25 s) 떨어졌다 올라옴 | 컨트롤러 한 주기가 늦어 `velocity_smoother velocity_timeout 0.3 s` 를 넘기자 smoother 가 0 을 목표로 감속한 것으로 추정(감속 0.3 m/s² 로 0.08 → 0 에 0.27 s — 모양 일치) |
| C | 2 (12:31:54 · 55) | `Optimizer fail to compute path` 3 회 + `PathBlockedAhead (0.93, 0.09)` → MonotoneEscape '최근접 4.6 cm' → 앞 0.28 m 탈출 | 출발점 앞 좁은 곳에서 MPPI 가 충돌 없는 궤적을 못 찾음(출발점 낮은 상자 둘레 추정) |
| D | 1 (12:32:04) | MonotoneEscape 끝 → 새 목표 | C 의 뒤처리 |
- A 의 시각 차: 요청 시각이 TF 최신값보다 0.004~0.088 s(한 번 0.386 s) 앞섬. 오늘 스택 nav2 로그에 이 예외 50 회(f2sm1 때 로그 31 회). MPPI `transform_tolerance` 는 10-07 §5 에 같은 기제(map→odom 지연)로 0.2 → 0.5 로 올린 상태인데도 남음 — 0.5 s 여유가 왜 0.004 s 차를 못 덮는지는 **미확인**(후보: tolerance 가 '기다리는 시간' 으로만 쓰이고 그동안 TF 가 안 들어옴 · 늦은 제어 주기(B)와 같은 CPU 지연). 
- B · A 둘 다 '컨트롤러 주기가 늦다' 와 이어질 수 있음: 복귀 113 s 동안 `Control loop missed` 43 회, 그림자 구성 CPU 75 % 대. 미확인.
- 다음에 알아보는 법: 멈칫을 볼 때 1 s 해상도 사건 표로는 'Passing new path' 만 보여 원인을 놓쳤다(§11.3 의 '4 번 = 새 경로 전달' 분류는 **틀림** — 실제는 B). 0.01 s 시각으로 맞추고, `Control loop missed` 를 걸러내지 말 것.
