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
