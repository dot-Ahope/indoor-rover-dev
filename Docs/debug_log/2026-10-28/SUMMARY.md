# 2026-10-28 SUMMARY

## §0 하루 시작 (사용자: "오늘 할 일 뭔가" → 제안: 시작 점검 → 확인 주행 1~2 회 → (SLAM A/B 한 회 더는 결과 보고) → F2.5 설계 착수; 사용자: "진행하라")
- 점검 `jobs/chk_day_start_1028.sh` → `outputs/chk_day_start_1028.txt`: Jetson 10:05 기준 가동 1 h 11 min(**밤사이 재부팅**) · Wi-Fi WEB_DEV_5G · `/tmp` prep 스크립트 전부 없음 · 스택 꺼짐(에이전트 컨테이너 1) · 10-27 수정 유지(`slam.launch.py` transform_timeout 1.5 · nvblox 층 return 수정 1 줄) · 디스크 45 %.
- 스크래치패드 러너 파일 수정 시각 갱신(7 일 자동 삭제 대비, 10-27 §9).

## §1 확인 주행 선언 — 결과 보기 전
- 목적: 10-27 의 두 변경(SLAM 위치 추정 transform_timeout 1.5 · 게이트 정리판 러너)은 f2tt1 1 회만 확인 → 같은 구성 반복.
- 구성: f2tt1 과 같음(no5 · `prep_patrol` + `planner:=smac` + 재계획 0.01 · Smac tol 0.35 · MPPI 28 · 5 · 수정 nvblox 층 · timeout 1.5). 주행 이름 f2tt2(· f2tt3). 상자는 테이프 자리.
- 판정(회마다): ① 8/8 · ABORT 0 · nav_guard 취소 0 ② nav2 odom→map 외삽 실패 0(SLAM 정체가 1.5 s 를 넘은 창 안의 실패는 따로 셈) · 'TF 외삽 → 중단' 0 ③ 1 s 넘는 정지 ≤ 1 ④ 통로 최소 정확 여유 ≥ 2.9 cm ⑤ 게이트 → 출발 ≤ 50 s. 기록: SLAM 정체 > 0.5 s 수 · 최대, 미래 여유 최소, 상자 복귀 최소, 통로 Smac 사용, Control loop missed.

## §2 prep 재전송 · prep
- `jobs/up_prep_1028.sh`(재전송 + `jobs/prep_smac_1028.sh`, 원문은 Jetson `/tmp/prep_full_1.txt`) → `outputs/prep_smac_1028_1.txt`: prep_fast aeb6e6cf3b · prep_patrol 4fe16954f6 · chk_prep 64b8beeadd · chk_drive_gate 5e92ec4a0a — **모두 PC HEAD blob 과 같음** · CR 0. 보드 세션 그대로(에이전트 세션 1 · /wheel_odom 25 Hz, 리셋 불필요).
- **PREP_OK** +86 s · 위치 추정 0.008 m · −0.3° · 배터리 12.37 V · tolerance 0.35 · REEDS_SHEPP · cp 3.0 · PathAlign 28 · PathFollow 5 · 프리셋 3 · odom1 /vslam/odom · SLAM localization · transform_timeout 1.5. chk_prep 이름표 수정(10-27 §24) 반영 확인(PathAlign · PathFollow 로 찍힘).

## §3 f2tt2 첫 시도 — PC WSL 기동 실패로 러너 미실행
- 사용자 "시작" 10:21:37 → 러너 호출(`wsl … run_f2c.sh f2tt2 …`)이 즉시 끝남, `outputs/drives/f2tt2/run_f2tt2.txt` 0 B. 이어 Jetson 상태 확인도 같은 오류: `wsl -l -v` = Ubuntu-22.04 · docker-desktop 모두 Stopped, 실행 시 'Wsl/Service/CreateInstance/E_FAIL'(PC 쪽). Jetson 에 닿는 모든 명령이 WSL(sshpass) 경유 → **러너는 시작 안 됨, 로버 안 움직였을 것**(현장 확인 요청).
- 대응: `wsl --shutdown` 뒤 재시도 — PC 의 WSL · Docker Desktop 을 모두 내리는 조치라 사용자 확인 대기. 원인 미확인.

## §4 f2tt2 결과(f2tt1 반복) — 8/8 · **TF 실패 0** · §1 판정 전부 통과 · §3 의 '러너 미실행' 은 틀림
- 사용자: "주행 완료하고 돌아왔다." → WSL 다시 동작 확인 뒤 Jetson 에서 직접 회수(`jobs/get_f2tt2.sh`; PC 쪽 러너 폴링이 끊겨 자동 회수 안 됨). 러너 원문 `outputs/drives/f2tt2/f0_f2tt2/f0_f2tt2.log`(STAGE F2c-smac-tol35-tffix-tt15, GIT_HEAD 1f0dd692 — 호출 인자), bag `bags/bag_f2tt2.tgz`, 로그 `bags/logs_f2tt2/`, 사건 `outputs/drives/f2tt2/nav_events_ms_f2tt2.txt`.
- ① ✔ 8/8 — 53.7 · 55.9 · 27.9 · 24.1 · 31.5 · 23.8 · 94.0 · 102.5 s(총 413.7; f2tt1 412.2). ABORT 0 · nav_guard 취소 0.
- ② ✔ nav2 odom→map 외삽 실패 0 · 층 경고 0 · §15 서명 0 · 컨트롤러 TF 중단 0(`anal_slam_freeze_f2tt2.txt` · `anal_tffix_sig_f2tt2.txt`). SLAM 정체 > 0.5 s 31 번 · 최대 0.996 s · 스캔 버림 53, 미래 여유 최소 1.003 s(f2tt1 1.139). Control loop missed 70.
- ③ ✔ 1 s 넘는 정지 1 번 4.9 s(10:29:03, `anal_stops_f2tt2.txt`) — TF 아님: PathBlockedAhead '(−0.02, 0.07) 비용 99' 2 s → 중단 · Wait 5 s, 마지막 목표(출발점 (0, 0)) 바로 앞. 무엇이 99 였는지 미확인.
- ④ ✔ 통로 최소 정확 여유 4.2 cm(< 2.7 cm 0 · fp 100 0, `anal_band_run_f2tt2.txt`).
- ⑤ ✔ 게이트 10:21:43 → 출발 10:22:23 = 40 s.
- 기록: 출발 상자 복귀 최소 14.0 cm(복귀 때 상자 칸 11 — 카메라가 봄, `anal_contact_f2tt2_d30.txt`). 통로(`chk_corr_paths_f2tt2.txt`): 남행 10:24:48.67 Smac · 북행 10:25:12.81 Smac → 10:25:13.80 PathBlockedAhead **(−1.59, −4.41)** 2 s → 중단 · 재계획 10:25:16.80 **Smac 실패 → NavFn**(스무딩도 실패, 원경로). 10-27 f2tt1 15:58:08 막힘 칸 (−1.60, −4.70) · (−1.59, −4.63) 과 같은 통로 남쪽 좁은 곳 — 두 주행 모두 북행 출발 직후 이 자리에 내접 칸이 잠깐 생김(실체 · 유령 미확인, §28 · 10-27). 복귀 10:28:34 막힘 (1.50, 0.06)~(1.44, 0.07) → MonotoneEscape(상자 쪽, §14 기전과 같음).
- 판정: f2tt1 · f2tt2 2/2 에서 TF 실패 0 → **10-27 의 두 변경(timeout 1.5 · 게이트 정리판)을 운용으로 확정할 근거 충분**(2 회). 남은 정지 원인은 TF 가 아니라 막힘 판정(경로 위 99 칸) — 다음 과제 후보.

### §3.1 내 실수 · 정정 — '러너는 시작 안 됨, 로버 안 움직였을 것'
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2tt2 러너 실행(`run_f2c.sh` → `run_f0.sh` → Jetson `job551_f0drive.sh`), 출력은 `outputs/drives/f2tt2/run_f2tt2.txt` 로 |
| 본 것 | 명령이 바로 끝나고 출력 파일 0 B, 'grep: write error: No medium found'. 이어 WSL 실행이 'E_FAIL' |
| 처음 추론 | WSL 이 처음부터 안 떠서 러너가 시작조차 못 함 → 로버 안 움직임 |
| 틀린 이유 | 실제로는 WSL 이 떴고 `run_f0.sh` 가 Jetson 에 `job551` 을 **setsid nohup** 으로 띄움(독립 실행). PC 쪽은 출력을 F: 파일로 쓰다 'No medium found'(F: 드라이브 쓰기 실패로 추정, 미확인)로 폴링 · 회수만 죽음 → 주행은 끝까지 감(f0 로그 10:21:43 게이트 → 10:29:49 끝). 그 뒤 WSL 이 잠시 E_FAIL — 연관 · 원인 미확인 |
| 판별 | Jetson `/tmp/f0_f2tt2.log` · bag 존재 확인, 사용자 '주행 완료' |
| 다음에 알아보는 법 | PC 쪽 러너 출력이 끊겨도 Jetson 러너는 계속 돈다 — '안 움직였다' 고 말하기 전에 Jetson `/tmp/f0_<이름>.log` · `pgrep job551` 을 본다(그게 안 되면 '모름' 이라고 말하고 현장 확인을 요청). 주행 중 PC 연결이 끊기면 PC 에서 멈출 수 없다는 뜻이기도 함 — 정지 수단은 온보드 · 현장 |

## §5 통로 남쪽 좁은 곳 반복 막힘 칸 원자료 대조 (사용자: "통로 반복 칸 원자료 대조 진행하라") — 결론: 유령 아님, **벽 · 물체 가장자리가 회전 중 한 칸(5 cm) 더 안쪽으로 찍혀** 96 이던 경로 점이 99 로 넘어감
- 도구 `jobs/anal_corridor_cell.py`(사건 전 마지막 /plan 의 실제 점들 칸 값을 지도 판마다 → 처음 99 가 된 판에서 그 경로 점 0.4 m 안 '새로 생긴 치명 칸' 을 출처별로: /map(SLAM 정적) · nvblox 슬라이스 ≤ 0 · 라이다 점 5 cm 안). 원문 `outputs/corridor_cell/anal_corridor_cell_{f2tt2,f2tt1}.txt` · `anal_corridor_cell_f2tt1_lid4.txt`(라이다 창 4 s), 입력 `bags/bag_f2tt2.tgz` · `2026-10-27/bags/bag_f2tt1.tgz`.
- 첫 판 오류(같은 § 안 정정): 로그 좌표 (−1.59, −4.41) 의 칸을 그대로 보니 bag 지도 어디에도 99 가 없었음 → 로그 좌표는 경로 점을 cm 로 반올림한 값이라 5 cm 칸 경계에서 이웃 칸을 읽은 것. 경로 점 자체로 다시 봄. 또 '사건 판' 을 사건 직전 판으로 잡았던 것을 '처음 99 가 된 판' 으로 고침.

| | f2tt2 10:25:13.80 | f2tt1 15:58:08.39 |
|---|---|---|
| 막힌 경로 점(실제) | (−1.587, −4.396) | (−1.604, −4.663) |
| 그 점 칸 값 변화 | 96 → **99**(10:25:13.80 판) | 84 → 99(15:58:08.39 판) |
| 로버 | 남쪽 주머니 (−1.47, −5.36), 북행 출발 제자리 회전 중(−103 → −145°), P 까지 0.96 m | (−1.48, −5.36), 회전 중(−103 → −141°), 0.67 m |
| 새로 생긴 치명 칸(0.4 m 안) | 4 개, **통로 동쪽** x −1.32~−1.42 · /map 0(정적 지도엔 없는 물체) · **nvblox 4/4** · 라이다 1 칸(45 점) | 11 개, 대부분 **통로 서쪽 벽** x −1.77~−1.92 · 라이다 8 · /map 점유 3 · nvblox 1 · 출처 없음 2 |
| 99 를 만든 가장 가까운 칸 | (−1.415, −4.335) 18 cm — nvblox(카메라) | (−1.765, −4.635) 16 cm — 출처 **없음**(직전 4 s 라이다 5 cm 안 0 · nvblox 거리 0.20) |

- 읽기: 두 번 다 북행 출발 직후 남쪽 주머니에서 **제자리 회전하는 동안** 통로 좁은 곳 가장자리(f2tt2 = 동쪽 물체를 카메라가 새 각도에서 봄, f2tt1 = 서쪽 벽을 라이다가 다시 찍음)가 통로 쪽으로 한 칸 더 찍힘. 계획 경로가 이미 내접 띠 바로 옆(96)이라 한 칸 차이로 99 → PathBlockedAhead 2 s → 중단 · 재계획 → f2tt2 는 재계획 Smac 실패 → NavFn. 사라졌다 다시 나오는 '유령' 이 아니라 실재 가장자리의 칸 단위 흔들림(10-15 상자 옆 '칸 판정 뒤집힘 2.7~4.4 cm' 과 같은 꼴, 메모리 box-side-stall).
- 동쪽 물체 = 정적 지도에 없는 통로 안 물체(10-26 사진의 쇼핑백 · 날개 열린 상자로 추정, 미확인 — 사용자 확인 필요).
- 미확인: f2tt1 의 가장 가까운 새 칸 (−1.765, −4.635) 출처(라이다 점이 5 cm 밖에 있었거나 회전 중 투영 시각 차로 이웃 칸에 마킹된 것으로 추정).
- 대책 후보(결정 안 함): ① PathBlockedAhead 를 99(내접)가 아니라 100(치명) 또는 '99 가 경로 점 n 개 이상' 으로 — 한 칸 흔들림에 덜 민감, 대가는 실제 막힘을 늦게 봄 ② 통로 안 물체를 치우거나 정적 지도에 넣기(환경) ③ 계획을 가운데로(Smac cost_penalty — 10-27 §5 에서 cp 낮추면 우회 14 m 사례, 신중).

## §6 F2.5 설계 착수 (사용자: "F2.5 설계로 넘어가자")
- 출발점: 09-30 §9(사용자 최종 목표 · 제안 구조 · 입력 = 텍스트 결정) · `NAV2_EXPLORATION_PLAN.md §7.4` 4.5 행.
- 설계 초안 **`Docs/07_language/F25_PLACE_LLM_DESIGN.md` v0.1**: 원칙(LLM 은 좌표를 만들지 않음 — 오인식은 '정지' 로 끝남) · 전제(지금 스택 측정값: prep 위치 검사 ≤ 1.6 cm, no5 4 회 8/8, 도착 오차 0.09~0.23 m, 주행 중 RAM 3.2/7.6 GB · GPU 90 % 56~64 %) · 구조(장소 등록부 `places.yaml` → `place_server`(서비스 · NavigateToPose · 목표 여유 검사) ← `intent_node`(규칙 기준선 + llama.cpp 문법 고정 JSON) · 정지는 LLM 우회 빠른 길) · 안전 · LLM 후보와 자원 예산(추정, 추론은 정지 상태에서만) · 시험 T1~T5 초안 · 단계 S0~S5 · 결정 항목 6 개 · 위험.
- 색인 `Docs/INDEX.md` 에 `07_language/` 행, `NAV2_EXPLORATION_PLAN.md §7.4` 4.5 행에 설계 링크.
- 다음: §8 결정(장소 이름 · '돌아와' 뜻 · 입력 창구 · 이동 중 새 명령 · 여러 단계 명령 · 모델 라이선스) → S0(places.yaml) → S1(place_server, LLM 없이 실주행).

## §7 F2.5 S0 · S1 구현 · dry_run 정지 시험 (사용자: "우선 우리가 부르던 이름으로 수행하자")
- 이름(설계 §8-1) = 기록에서 써 온 이름 그대로(10-01 §8.3x · 10-14 §27.3): 출발점 (0, 0) · B (2.25, −1.6) · C (−1.6, −2.0; 별칭 '위 복도' — 위 복도 (−1.6, −2.1) 와 10 cm 차라 한 자리로) · 통로 북쪽 (−1.65, −3.7) · 남서 (−1.6, −5.5, 위치만 f) · W3 (5.5, −2.2). '돌아와' = 출발점(09-30 §9 사용자 표현). 이동 중 새 go_to = 거절('먼저 stop', 설계 §8-4 결정 전 기본값).
- 코드(ros2_ws/src/rover_navigation): `config/places.yaml`(등록부) · `scripts/place_server.py`(/place/command → 등록부 → 경로 끝 방향(별도 상주 `path_end_yaw.py` — 09-28 §20 사고 교훈) → 목표 여유 검사(차체 ↔ 치명 ≥ 0.10 m, 장소별 min_clear) → NavigateToPose, f 모드는 xy 0.15 m 안이면 취소하고 arrived, stop = Nav2 목표 전부 취소, dry_run 파라미터) · `scripts/place_cmd.py`(명령 창구 — 여러 명령을 한 프로세스 · 참여자 1 개로, '@stopN' 정지 시험, 기대 상태 아니면 멈춤) · `scripts/path_end_yaw.py`(러너 job613 사본) · CMakeLists 설치 줄. 아직 colcon 설치는 안 함(Jetson src 에서 직접 실행).
- dry_run 시험 `jobs/up_place_dry_1028.sh` → `jobs/chk_place_dry_1028.sh`, 원문 `outputs/chk_place_dry_1028.txt`(1 차) · `outputs/chk_place_dry_1028b.txt`(수정 뒤):
  - 1 차: list · where · 별칭('위 복도' → C) · 모르는 장소('화장실' · 빈 이름) 거절 · stop 정상. B · C · W3 · 출발점 경로 끝 방향 계산 · 여유 0.29~0.75 m. **남서 거절 — 목표 여유 0.000 m**(등록 좌표에 차체를 놓으면 벽 칸에 닿는 좁은 구석). dry_run 의 accepted 가 끝 상태가 아니어서 창구가 25 s 기다림 · 종료 때 ExternalShutdownException 출력.
  - 수정: 장소별 `min_clear`(남서 0.0 — no5 에서 위치만 목표로 f2tf1 · f2tt1 · f2tt2 반복 도착 (−1.47~−1.50, −5.31~−5.37), 근거를 등록부 주석에, TODO(improve) 좌표 옮김 검토) · dry_run 끝 상태 'checked' · 종료 예외 처리 · stop 때 진행 중 이동 명령에도 canceled 알림(기다리는 쪽이 멈추지 않게).
  - 2 차: 이동 명령 5 개 모두 checked(0.0~0.8 s), 거절 2 · stop 정상. 관찰: **출발점에서 남서로 바로** 가면 경로 끝 방향 154°(431 점 · 5.63 m) — no5(북쪽에서 −100° 로 진입)와 다른 진입, 검증 안 된 길.
### §7.1 S1 실주행 선언(f2pl1) — 결과 보기 전
- 실행: `jobs/up_place_s1_1028.sh` → Jetson `jobs/run_place_s1_1028.sh`(setsid nohup — PC 끊겨도 계속): 게이트(chk_drive_gate B · C · G2) → place_server · bag(/place/* 포함) · tegrastats 기동 → 30 s → 명령 한 묶음: where; go_to B; go_to 위 복도; go_to 통로 북쪽; go_to 남서; go_to 통로 북쪽; go_to 위 복도; **go_to W3 @stop20**(이동 20 s 뒤 stop); wait 5; go_to W3; return. 순서는 no5 와 같게(검증된 길만).
- 판정: ① 이동 명령 9 개 arrived(남서는 위치 도착), @stop 은 canceled ② stop 뒤 1 s 안에 /cmd_vel 0 · 로버 정지(bag 으로) · 다시 보낸 go_to W3 arrived ③ nav2 TF 실패 0 · 접촉 0 ④ 구간 시간이 no5 같은 구간(f2tt1 · f2tt2)과 ±20 % 안 ⑤ 명령 → moving 지연 기록(경로 방향 조회 포함).

## §8 f2pl1 결과: B · 위 복도 도착 뒤 '통로 북쪽' 거절 → 로버 C 에서 멈춤(판정 ① 불합격) · 원인 · 수정
- 주행(13:11:41 게이트, 13:12:18 명령, 13:14:10 끝 rc 1): 게이트 B 25.0 Hz · C 최대 간격 0.06 s · G2 0.379 m 통과. where info 1.0 s → **go_to B arrived 54.6 s**(no5 목표 1: 50.7~53.7 s, +2~8 %) → **go_to 위 복도 arrived 53.9 s**(no5 목표 2: 54.3~55.9 s) → **go_to 통로 북쪽 rejected 0.0 s '목표 여유 0.000 m < 0.10'** → 창구가 설계대로 뒤 명령을 보내지 않고 끝. 로버는 C(−1.50, −2.01, −176°)에 멈춤. 주행 중 nav2 TF 실패 0(nav2.log 의 2 건은 10:06 스택 기동 때). 명령 → moving 0.0~0.1 s.
  데이터: 원문 `outputs/drives/f2pl1/place_s1.log` · `place_server_s1.log` · `nav2.log` · `slam.log` · `tegra_f2pl1.log`, bag `bags/bag_f2pl1.tgz`(14 MB).
- 판정(§7.1): ① 불합격(9 개 중 2 개 도착 · 1 거절, 나머지 안 보냄) ② 정지 시험 안 함 ③ TF 실패 0 · 접촉 미확인(두 구간만, 사용자 관찰 대기) ④ 두 구간 ±20 % 안 ⑤ 0.0~0.1 s.

### §8.1 내 실수: dry_run 에서 '통로 북쪽' 을 시험하지 않고 "이동 명령 5 개 모두 통과" 로 보고
| 칸 | 내용 |
|---|---|
| 하려 한 것 | §7 dry_run(`jobs/chk_place_dry_1028.sh`)으로 등록부 장소 전부의 목표 검사(경로 끝 방향 · 여유)를 실주행 전에 확인 |
| 본 것 | `outputs/chk_place_dry_1028b.txt`: checked 5 = B · C · 남서 · W3 · 출발점. 명령 목록(스크립트 9 행)에 **통로 북쪽이 없음** |
| 처음 추론 | "이동 명령 5 개 모두 checked" = 등록부 전부 통과 → 실주행 준비 끝(사용자에게도 그렇게 보고) |
| 의심한 이유 | f2pl1 이 바로 그 장소에서 거절 |
| 판별 | 스크립트 명령 목록과 원문 대조 — 6 곳 중 5 곳만, 그것도 '이동 명령 5 개' 라 수가 맞아 보였음 |
| 결론 | 통로 북쪽은 실주행 전 한 번도 검사되지 않았음. 게다가 dry_run 은 출발점에서만 해서 **실주행과 다른 출발 자리**(C 에서 통로 북쪽으로)의 경로 끝 방향은 볼 수 없었음 |
| 다음에 알아보는 법 | dry_run 은 등록부를 읽어 **모든 장소**를 돌게 만들고 결과 수 = 장소 수 확인. 실주행 명령 순서 그대로(구간마다 출발 자리 바뀜)는 dry_run 으로 못 봄 — 출발 자리가 바뀌는 검사(경로 끝 방향)는 해당 자리에서 다시 보거나 bag 으로 재계산 |

### §8.2 거절 원인 — 경로 끝 방향이 통로에 비스듬함(−51°) + 등록 좌표가 통로 동쪽 물체 쪽으로 치우침
| 본 것 | 추론 | 데이터 |
|---|---|---|
| f2pl1 거절 순간 전역 코스트맵(13:14:07.80 판)에서 목표 (−1.65, −3.70) 방향별 여유: −90° 0.110 · −75° 0.078 · −60° 0.029 · −45° 0.002 · −30~−15° 0.000(차체 안 치명 칸 1) · 0° 0.025 m. 가장 가까운 치명 칸은 늘 **x −1.365**(목표에서 동쪽 0.285 m) — 정적 지도(/map) 값 0 | 통로 동쪽의 치명 칸 줄은 정적 지도에 없는 물체(§5 의 동쪽 물체와 같은 줄). 서쪽 벽은 x ≈ −2.15 → 목표가 가운데(≈ −1.76)보다 동쪽으로 11 cm 치우침. 통로 축 방향으로 서면 0.11 m, 비스듬하면 차체 모서리(대각 반길이 0.313 m > 0.285)가 물체 칸에 닿음 | `jobs/anal_place_clear.py` → `outputs/place_clear_f2pl1.txt`(격자 그림 포함), bag `bags/bag_f2pl1.tgz` /global_costmap/costmap · /map |
| 같은 자리(C)에서 dry_run 재현 3/3: '목표 여유 0.000 · 방향 **−51°** 경로 끝 방향(77 점)'(거절 메시지에 방향을 넣도록 고친 판) | 거절 원인 = 경로 끝 0.3 m 가 통로로 비스듬히 들어가는 방향. bag 의 방향별 표와 맞음(−45° 0.002, −60° 0.029 사이) | `jobs/up_place_dry_1028c.sh` → `jobs/chk_place_dry_1028c.sh`, `outputs/chk_place_dry_1028c1.txt` |
| no5 의 같은 목표 3: 보낸 방향 −55~−64°(f2tt2 · 10-27 3 회), 4/4 SUCCEEDED, 도착 방향 −74~−87°(목표 대비 −18~−24°), 거리 0.03~0.20 m. 목표 5(남쪽에서)도 72~76° 로 보내 82~94° 로 도착 | no5 러너에는 여유 검사가 없어 같은 비스듬한 자세를 Nav2 가 받았고, 로버는 실제로 통로 축 쪽으로 서서 끝냈음(방향 허용 0.35 rad 근처). 즉 **검사가 실제로는 서지 않는 명목 자세를 판정**한 것 | `outputs/drives/f2tt2/f0_f2tt2/f0_f2tt2.log`, `2026-10-27/outputs/drives/*/f0_*/f0_*.log` |

### §8.3 수정(place_server)
- 경로 끝 방향의 여유가 기준 미달이면, 그 방향에서 ±5° 씩 넓혀 **±45° 안에서 가장 가까운, 기준을 넘는 방향**으로 고쳐 보낸다(못 찾으면 거절). 위치만(f) · 고정 방향 장소는 그대로. 근거: no5 에서 로버가 실제로 선 방향(통로 축 쪽)과 같은 쪽이고, 명목 자세가 차체를 치명 칸에 겹치게 두는 목표를 보내지 않음. 기각: ① 통로 북쪽 min_clear 0(남서처럼) — 물체가 더 들어와도 못 거름 ② 좌표를 통로 가운데로 — 검증된 자리를 바꿈(후보로 남김). TODO(improve): ±45° · 5° 는 한 사례로 정한 값.
- 거절 · 수락 메시지에 방향과 고친 양을 남김.
- dry_run(C 에서, `outputs/chk_place_dry_1028c2.txt`): 통로 북쪽 3/3 checked '경로 끝 방향(77 점) → 여유 위해 −35° 고침(원래 여유 0.000) · 방향 −86° · **여유 0.10 m**' — 기준에 딱 걸치는 값(bag −90° 0.110). 남서 · B · W3 · 출발점 checked.
- 러너 `run_place_s1_1028.sh` 에 둘째 인자 PLAN(full 기본 · fromC = C 에서 B 구간 빼고 나머지) — 로버를 옮기지 않고 C 에서 다시 시작하려고.

### §8.4 다음 실주행 선언(f2pl2, PLAN fromC) — 결과 보기 전
- 명령: where; go_to 통로 북쪽; go_to 남서; go_to 통로 북쪽; go_to 위 복도; go_to W3 @stop20; wait 5; go_to W3; return.
- 판정: §7.1 과 같음(이동 7 개 arrived · @stop canceled · stop 뒤 1 s 안 /cmd_vel 0 · TF 실패 0 · 접촉 0 · 구간 시간 no5 ±20 %) + 통로 북쪽 두 번 모두 '고침' 으로 수락되고 도착할 것. 여유가 0.10 경계라 물체 칸이 한 칸 더 찍히면 거절될 수 있음 — 그때는 거절로 멈추는 것이 설계대로의 동작(안전 쪽)으로 기록.
