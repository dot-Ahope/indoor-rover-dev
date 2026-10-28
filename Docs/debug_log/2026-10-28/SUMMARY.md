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
