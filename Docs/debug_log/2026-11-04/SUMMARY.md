# 2026-11-04 — Jetson 준비 · push · 주석 정정 · 문제 대장 9 기 (로버 주행 없음)

## §0 하루 시작 (사용자: "jetson 실행했다. 확인 스크립트 실행해라." → "추천 순서대로 진행하라.")
- Jetson 09:09 부팅(uptime 5 분 @ 09:14), <LAN-B>.110. 보드 드라이버 확인은 11-03 §11.1 에 적음.
- 순서(사용자 승인): ① Jetson 준비 ② push ③ 8 기 어긋남 · 낡은 주석 정정 ④ 문제 대장 9 기.

## §1 Jetson 준비 — 도구 재전송 · 설치본 링크 복구
- `Docs/tools/up_tools.sh` 고침: 예전 판은 스크래치패드 `tools/`(10-22 소실)를 읽어 옛 판이 올라갈 수 있었다 → 저장소 `Docs/tools` 판을 복사해 올림 · 옛 up950 묶음(job240 등, 지금 안 씀) 뺌 · 끝에 Jetson 쪽 파일 수와 `prep_fast.sh` 의 `--follow-symlinks` 줄 수를 찍음. 실행 결과:
```
  저장소 판 ce1a0bee → …/scratchpad/tools (7 개)
  Jetson /tmp: 7 개 · prep_fast --follow-symlinks 줄 2
```
- 설치본 설정 링크 확인(`jobs/chk_install_links_1104.sh` → `outputs/chk_install_links_1104.txt`): amcl · nvblox_local · BT xml 2 개는 링크, **nav2_params.yaml 만 일반 파일**(2026-10-29 15:52, 내용은 src 와 같음 · PreferForward 15.0 둘 다) — 10-15 §30 의 옛 `sed -i` 흔적.
- 복구(`jobs/up_install_link_1104.sh` → `outputs/up_install_link_1104.txt`): 내용이 src 와 같을 때만 백업(`/tmp/nav2_params_install_backup_1104.yaml`) 뒤 `ln -s` — "링크로 복구: …/src/rover_navigation/config/nav2_params.yaml". sudo 없음.
- Jetson src ↔ 저장소 비교(`jobs/chk_src_md5_1104.sh` · `chk_src_strip_1104.sh` · `anal_src_strip_md5.py` → `outputs/chk_src_md5_1104.txt` · `chk_src_strip_1104.txt`): 8 파일 중 6 개가 다르지만 주석을 빼면 `pad_relief.py` 만 다름(11-03 §3 노드 기본 mode 'on' → 'off'). 표준 prep 은 이 노드를 안 띄우므로 주행 영향 없음 — Jetson src 는 그대로 둠(다음 배포 때 같이).

## §2 push (사용자 승인 순서 ②)
- `git fetch . feature/smac-hybrid:feature/nvblox-migration` → `git push personal …` : d72968a7..8ec8aa13(두 가지).
- `bash private/publish_public.sh`: "점검: 문구 0 · 옛 이메일 0 · 비공개 경로 0 · 비밀번호 0" → 공개 dev 334d638..120cf0f(원본 8ec8aa13). main 은 그대로(--push-main 안 씀).

## §3 8 기 어긋남 · 낡은 주석 정정 (순서 ③ — 11-03 §9 목록)
- 코드 주석(동작 변경 없음, `jobs/up_comment_fix_1104.py` — 정확한 문자열 치환 · 한 번씩): `nvblox_local.yaml` 통합 거리 꼬리 주석의 1.4 근거 · min_weight 기각 근거 추가 · site_distance 설명 위치 표시 · '먼 비스듬한 첫 관측' → 10-19 §14 분해 · `camera.launch.py` emitter_off '오프라인 확인용' → 운용 기본(launch 기본값은 false) · 데시메이션 '확인 중' → 10-20 §8.3 대책 아님 · `fastdds_udp_only.xml` SHM '원인 제거' 에 10-20 §7.2 범위 정정 · `path_blocked_ahead_condition.cpp` 21 행 '목표 5 에 52 s' → 10-23 §20.7(목표 4) · 러너 `2026-11-03/jobs/job551_f0drive.sh`(+ 스크래치패드 실행본) BAG_IR 조건에 emitter_off. 검사: yaml 읽기 · py_compile · xml 파싱 · bash -n 모두 통과(PARSE_OK). Jetson src 에는 아직 안 올림(주석만 — 다음 배포 때).
- 기록 정정 표시(원문 유지, `jobs/up_record_marks_1104.py` 줄 끝에 '→ 2026-11-04 §3 정정'): 10-19 §23.1 조명 원인 · §22 '남쪽 15.7 cm' · §20 mp4 'git 제외' · 10-21 §11.1 mp4 · 10-20 §9.7 ttyUSB0 · §7.3a 표(표 아래 줄) · 10-22 §21 f2sm3 검증 · 10-23 §17.1 표(표 아래 줄) · §21 15.4 두 줄 · §22.2 Smac 비교 무효 · `Docs/06_planner/SMAC_HYBRID_PLAN.md` §2 · §8.
- 안 한 것(결정 대기 또는 다음): MAC 가림(10-21 SUMMARY 31 행 · `2026-10-22/outputs/chk_wifi_1022.txt` 외 추적 파일 73 개) · mp4 2 개 git 제외 · `prep_fast.sh` 70 행 SHM 오류 검사에 cuvslam · nvblox 로그 넣기 · only_new × 재계획 0.5 Hz 조합 시험.

## §4 문제 대장 9 기(10-26 ~ 10-29) (순서 ④)
- 6 묶음 병렬(카드마다 담당 하나): 새 카드 5 장 — `smac-hybrid-adoption` · `mppi-corner-cut-pathalign` · `nvblox-layer-tf-drop` · `drive-gate-consolidation` · `f25-place-navigation`. 시범 2 장 전체 형식으로 확장 — `slam-stamp-freeze`(60 → 282 줄) · `stationary-yaw-drift`(61 → 258 줄). 이어 채움 약 25 장. 카드 88 장(ISSUES.md 제외).
- 머리 표 '관련 문제' 링크 25 장(`jobs/up_issue_links_p9.py`, 값 줄에 이미 있으면 건너뜀) · ISSUES.md 9 기 표 + 시범 두 줄을 9 기로 옮김(`jobs/up_issues_table_p9.py`) · 색인 재생성(SECTIONS 1468 · RUNS 123 · JOBS 1910) · `chk_record_rules.py` RULES_OK · 금지 문구 0.
- 묶음 J 지적으로 `slam-stamp-freeze.md` 10-27 §15 행 '튄 장 2 장' 에 정정 표시(주행 전체 3 장).
- 대조(원본에서 직접): `2026-10-27/outputs/tffix/anal_tffix_sig_f2st1.txt` '§15 서명 장 3' · bag 창 층 경고 22 · `Docs/05_nvblox/nvblox_nav2_rover.patch` 9 행 `return;` · `slam.launch.py` 75~77 행 transform_timeout 1.5 · `nav2_params.yaml` 281 · 285 행 PathAlign 28 · PathFollow 5 · `path_end_yaw.py` 22 행 planner_id 'GridBased'(목표 방향은 여전히 NavFn) · `place_server.py` TODO 218 행 하나 · `places.yaml` 41 행 'f2pl3 에서 첫 도착'(실제 첫 도착 f2pl4 — 어긋남).
- 묶음들이 찾은 기록 어긋남(카드 '기록 어긋남' 칸에 경로와 함께 — 원본 SUMMARY · 코드는 안 고침):
  - 코드 · 문서: `nav2_params.yaml` 748 행 RS 줄 끝 옛 DUBIN 설명 · 278~280 행 채택 근거에 f2sa3 없음 · `places.yaml` 41 행 · `place_server.py` 종료 예외(RCLError) 미처리 · `Docs/06_planner/SMAC_HYBRID_PLAN.md` §10 · §6 · §7 낡음 · `TEST_COURSE_AND_GATES.md` v2.3 게이트 C 문턱 '≤ 0.2 s' · 옛 도구 이름 · P 없음 · `Docs/tools/README.md` 에 chk_drive_gate · run_slam_replay · slam_replay_feed 없음 · `Docs/02_hardware/rover.urdf.xacro` 기록 사본 옛 판 · F2.5 설계 v0.2 와 구현 차이.
  - 기록: 10-27 §15.1 '튀는 장 두 장'(3 장) · §23 '09-22 이후 전체 영향'(코드상 10-08 ~ 10-27) · §29.2 LinkNearChains 중앙(PL.edges 값을 옮김, 실제 141.2) · §25 '77 s'(66 s) · 10-28 §7.1 등 'arrived N' 에 stop 포함 · §10 첫 메시지 유실이 처음 아님 · 10-29 §2 'f2pl1 37 s 뒤'(움직인 뒤 2 s) · 10-30 작업이 10-29 SUMMARY 에 있음(폴더 없음).
- Jetson 확인 못 함: 출발 전 검사 ⓐ(`place_server.py`)가 Jetson 에 배포됐는지 — `jobs/chk_place_md5_1104.sh`(읽기만) 를 두 번 돌렸으나 <LAN-B>.110 핑 50 % 손실 · 'lost connection'. 저장소 판 md5 는 `outputs/chk_place_md5_1104_repo.txt`(place_server 281 줄 f3ec96a4). 다음 접속 때.
- 남은 결정 · 할 일: MAC 가림 · mp4 2 개 · `prep_fast.sh` SHM 오류 검사 범위 · 주석 수정분 Jetson 배포 · 위 코드 · 문서 어긋남 정정 · 기본 구성(NavFn · 0.5 Hz) + MPPI 28 · 5 조합 미주행 · ⓐ 배포 · d2.

## §5 9 기 어긋남 정정 — 주석 · 문서 (사용자: "주행 후보 빼고 진행하라. 당시 어떤 이유인지는 모르겠지만 필요 없다 판단했겠지")
- 사용자 판단 기록: 기본 구성(NavFn · 0.5 Hz) + MPPI 28 · 5 조합 미주행은 당시 필요 없다고 판단했을 것 — 주행 후보(그 확인 주행 · d2)는 이번에 안 함.
- `jobs/up_doc_fix_p9_1104.py`(동작 변경 없음): `nav2_params.yaml` PathAlign 채택 근거에 f2sa3 · 미주행 조합 경고 · RS 줄의 옛 DUBIN 설명 · 09-14 주석 위치 표시 · `places.yaml` 41 행 '첫 도착 f2pl4' · `Docs/06_planner/SMAC_HYBRID_PLAN.md` §11(10-23 판정 무효 · 계획서 밖 결과 · RS 어긋남 · 목표 방향 NavFn) · `TEST_COURSE_AND_GATES.md` 게이트 C 실제 문턱(< 0.5 s · 지연 < 1.0 s) · chk_drive_gate · P 게이트(LOAD_MAX 60 %) 표시 · `Docs/tools/README.md` 에 chk_drive_gate · run_slam_replay · slam_replay_feed 행 + up_tools 설명. YAML 읽기 검사 통과.
- `Docs/02_hardware/rover.urdf.xacro` 기록 사본을 src 판(10-29 §9 urdf 에 맞춘 것)으로 갱신 · CLAUDE.md 데크 상수 목록에 xacro 추가.
- 안 고친 것(동작 변경이라 별도): `place_server.py` 종료 예외(RCLError) 처리 · `prep_fast.sh` SHM 오류 검사 범위 · 옛 날짜 jobs 의 낡은 머리 주석(옛 파일은 안 바꿈).

## §6 MAC 가림 (README §4)
- `jobs/up_mask_mac_1104.py`: 추적 텍스트 파일의 실제 MAC/BSSID 뒤 3 바이트 → `XX`(제조사 앞 3 바이트는 남김). 날짜 · 시각 모양(26-10-23-…)과 00:00:00 은 제외. 결과 "파일 33 · 바꾼 곳 609" + git 이 바이너리로 보는 `2026-10-22/outputs/chk_wifi_1022.txt` 1 곳 따로. 다시 세면 실제 MAC 0.
- 범위: 지금 판만. git 과거 이력(공개 이력 포함)에는 남음 — 이력 다시 쓰기는 안 함(사용자 결정 필요 시).
- ⚠ 가린 파일에 옛 jobs 스크립트(`2026-09-18/jobs/wifi_mon.sh` · `job428c_bss.sh` 등)가 있음 — 기록 보관본이라 그대로 다시 돌리면 BSSID 비교가 안 맞음(Jetson 에 깔린 wifi_mon 은 Jetson 쪽 파일이라 영향 없음).

## §7 mp4 2 개 git 제외
- `git rm --cached` `2026-10-19/figures/f2y1_ir_drive.mp4`(28.8 MB) · `2026-10-21/figures/f2sm2_people_block.mp4`(20.9 MB) — 로컬 파일은 남김. `.gitignore` 에 `Docs/debug_log/*/figures/*.mp4`(예전 규칙은 videos/ 만). 과거 이력 · 공개 이력에는 남음.

## §8 Jetson 배포 · 확인 미실행
- 주석 수정분(§3 · §5) · pad_relief 기본 off 를 Jetson src 로 올리는 것과 F2.5 판(ⓐ) 확인: <LAN-B>.110 핑 손실 50 %(4 중 2) · 전송 'lost connection' 3 회 → 안 함. 다음 접속 때 `jobs/chk_place_md5_1104.sh` 와 배포.

## §9 push
- 원본 8ec8aa13..c27c770b(personal 두 가지) · 공개 dev 120cf0f..bf406f3 — 점검 "문구 0 · 옛 이메일 0 · 비공개 경로 0 · 비밀번호 0". 규칙 검사 경고 3 = 10-21 · 10-22 · 10-23 TOOLS.md 없음(예전부터의 결함, 문제 대장 record-conventions-evolution — 사후 작성은 안 함).

## §10 Jetson 주소 <LAN-A>.8 · 코드 2 건 수정 · src 배포 (사용자: "<LAN-A>.8가 맞다. 두 코드 수정은 진행하라.")
- 신원 확인(`jobs/chk_identity_1104.sh` → `outputs/chk_identity_1104.txt`): host jetson-desktop · 5.15.185-tegra · R36.5 · /dev/rover → ttyCH341USB0 · ws 있음 · wlP1p1s0 <LAN-A>.8 · SSID <WIFI-A> · up 2 h 52 m(09:09 부팅과 맞음). 핑 3/3. → <WIFI-B>(<LAN-B>.110)가 끊겨 ALOPS 로 넘어간 것(원인 미확인 — §4 · §8 의 50 % 손실이 그 전조로 보임, 추정).
- 코드 수정 1 — `ros2_ws/src/rover_navigation/scripts/place_server.py` main: `except _rclpy.RCLError` 추가, 메시지에 'context is not valid' 가 있을 때만 정상 종료로 보고 다른 RCLError 는 다시 올림(`rclpy.impl.implementation_singleton.rclpy_implementation` — Humble 경로). 근거: f2pl4 · f2pl5 서버 로그 끝 traceback(`2026-10-28/outputs/drives/f2pl5/place_server_s1.log`). py_compile 통과, 실행 확인은 다음 F2.5 실행 때.
- 코드 수정 2 — `Docs/tools/prep_fast.sh` 70 행 SHM 오류 집계에 `/tmp/cuvslam.log` · `/tmp/nvblox_node.log` 추가(없으면 무시). 표시 줄이라 판정은 안 바뀜. bash -n 통과.
- src 배포(`jobs/up_src_1104.sh` → `outputs/up_src_1104.txt`, 빌드 안 함 · 원본 백업 Jetson `/tmp/deploy_backup_1104/`): 11 파일. 설치본은 9 개 중 8 개가 링크(바로 반영), place_server.py · places.yaml · cpp 는 설치본 없음(place_* 는 job 스크립트가 src 에서 직접 띄움 · cpp 는 주석만이라 빌드 불필요). `/tmp/prep_fast.sh` 새 판(cuvslam 줄 1).
- **확인된 것**: Jetson 의 옛 `place_server.py` md5 fc0962af ≠ 저장소 10-29 판 f3ec96a4 → 출발 전 검사 ⓐ 는 **배포되지 않았었다**(이제 배포됨 — 다음 F2.5 실행부터 ⓐ 가 켜짐). places.yaml 은 저장소 옛 판과 같았음(55cc18ce).

## §11 8 · 9 월 날짜별 정리 페이지 22 장 (사용자: "다음 진행하자" → 선택 "8·9월 정리 페이지")
- 9 묶음 병렬 작성(브리프 `pg_common.md` — 원천 = 그날 SUMMARY · REPORT.md · BASELINE_STVL.md, 판단마다 스크립트 핵심 줄 · 출력 발췌 · 원문 경로, 원문 없으면 '원문 없음' · '원천 소실', 뒤 정정은 원문 유지 + `.c1104` '11-04 정정' 표시). 머리 = `2026-10-28/jobs/report_1028_head.html`. 09-21 ~ 09-30 의 기존 주제 페이지(11 장 + `2026-09-30/day_0930.html`)는 안 고치고 경로로만 연결.
- 게시 전 검사(`pg_check.py` — 비밀번호 파일 모든 줄 · 금지 문구 · NUL/U+FFFD · MAC · `sshpass -p 값`): 22 장 모두 0(09-15 의 sshpass 1 건은 `&lt;PW&gt;` 가림 줄). 각 날짜 SUMMARY 끝에 페이지 포인터를 덧붙임.
- 묶음 1 이 조립 스크립트를 고치다 다른 묶음 `fig_report_0907 ~ 0930.py` 16 개까지 다시 저장함(글로브 범위 실수) → 16 개를 다시 돌려 생성 페이지 md5 가 게시본과 모두 같음을 확인(바뀐 것 없음).
- 판정 카드 · 정정 표시 합계: 약 160 장 · 약 300 곳(묶음 보고 합).

| 날짜 | 제목 | 게시 | 로컬 |
|---|---|---|---|
| 08-26 | 08-26 보드 연결 · 첫 EKF | https://claude.ai/artifact/KnQzRZoLAegfkjAuD3td5t | `Docs/debug_log/2026-08-26/figures/day_summary_0826.html` |
| 08-27 | 08-27 카메라 자이로 융합 | https://claude.ai/artifact/2Six9th32zSVF5LCQfoVyd | `Docs/debug_log/2026-08-27/figures/day_summary_0827.html` |
| 08-28 | 08-28 라이다 방향 · 첫 지도 | https://claude.ai/artifact/Rrg2KpuxS7tBsVTBAvKKFc | `Docs/debug_log/2026-08-28/figures/day_summary_0828.html` |
| 08-31 | 08-31 스캔 끌림 · 휠 스케일 | https://claude.ai/artifact/SVy8iUoKTAnmcfZRFcJfX9 | `Docs/debug_log/2026-08-31/figures/day_summary_0831.html` |
| 09-02 | 09-02 Nav2 첫 자율주행 | https://claude.ai/artifact/LFgY9MyAaw7Pu3x6Fww29a | `Docs/debug_log/2026-09-02/figures/day_summary_0902.html` |
| 09-03 | 09-03 데드밴드 · 스톨 래치 | https://claude.ai/artifact/58RrCSYAQ4UswYSjXk7bYC | `Docs/debug_log/2026-09-03/figures/day_summary_0903.html` |
| 09-07 | 09-07 PWM 정정과 재보정 | https://claude.ai/artifact/3Ta1T3vEaMq1U33pkcwMmB | `Docs/debug_log/2026-09-07/figures/day_summary_0907.html` |
| 09-08 | 09-08 상자 회피와 오진 | https://claude.ai/artifact/WFX3SBZKcRvtpeATChD6Ag | `Docs/debug_log/2026-09-08/figures/day_summary_0908.html` |
| 09-09 | 09-09 odom 소실 · STVL 도입 | https://claude.ai/artifact/5w1ddJCQydbgDnrPrPXD7Q | `Docs/debug_log/2026-09-09/figures/day_summary_0909.html` |
| 09-10 | 09-10 계측이 벽을 봤다 | https://claude.ai/artifact/HzTebGEaLJRTo3heTvdRDS | `Docs/debug_log/2026-09-10/figures/day_summary_0910.html` |
| 09-11 | 09-11 코스트맵 지우던 BT | https://claude.ai/artifact/19iGrjHGS1gLWfNYN2Rnav | `Docs/debug_log/2026-09-11/figures/day_summary_0911.html` |
| 09-14 | 09-14 중앙 상자 통로 | https://claude.ai/artifact/YBv2ufj4Cyyv7ZDShQCSgC | `Docs/debug_log/2026-09-14/figures/day_summary_0914.html` |
| 09-15 | 09-15 MPPI 첫 주행과 망 | https://claude.ai/artifact/LS5rxnfXdAbJPEG6MzNXnD | `Docs/debug_log/2026-09-15/figures/day_summary_0915.html` |
| 09-16 | 09-16 상자 옆 입구 MPPI | https://claude.ai/artifact/SLbEueXChoH8RRB5tvmog3 | `Docs/debug_log/2026-09-16/figures/day_summary_0916.html` |
| 09-17 | 09-17 상자 뒤 목표 3/3 | https://claude.ai/artifact/FJN7dU7qpyzr94Z6ahoK35 | `Docs/debug_log/2026-09-17/figures/day_summary_0917.html` |
| 09-18 | 09-18 센서 데크 −2.68° | https://claude.ai/artifact/3ucoT6vev8uNtSCj78wGh4 | `Docs/debug_log/2026-09-18/figures/day_summary_0918.html` |
| 09-21 | 09-21 STVL 기준선 고정 | https://claude.ai/artifact/BMPDyhRStznMHcHmZbJtCh | `Docs/debug_log/2026-09-21/figures/day_summary_0921.html` |
| 09-22 | 09-22 nvblox 전역 이전 | https://claude.ai/artifact/6ag61w9uhik6PYuGQ635Ba | `Docs/debug_log/2026-09-22/figures/day_summary_0922.html` |
| 09-23 | 09-23 Phase N 마감 | https://claude.ai/artifact/RNHEuhLY8qumLBWXRuzwzB | `Docs/debug_log/2026-09-23/figures/day_summary_0923.html` |
| 09-28 | 09-28 제자리 회전 슬립 | https://claude.ai/artifact/Lzf781UzFfp8UvTW6sHC1K | `Docs/debug_log/2026-09-28/figures/day_summary_0928.html` |
| 09-29 | 09-29 F0 완료 · 정지 수단 | https://claude.ai/artifact/1Euj4P58ME3K1jHgXqmHf7 | `Docs/debug_log/2026-09-29/figures/day_summary_0929.html` |
| 09-30 | 09-30 사무실 첫 지도 | https://claude.ai/artifact/CdMK9sM1WVSd3iwpZsBZDp | `Docs/debug_log/2026-09-30/figures/day_summary_0930.html` |
- 묶음들이 찾은, 문제 대장 카드에 없던 기록 어긋남(페이지에는 정정 표시, 원문 SUMMARY 는 그대로):
  - 08-28 SUMMARY 29~30 행 경로 문자열이 백슬래시 이스케이프로 깨짐(`F:` 뒤 제어 문자 0x06 · 줄바꿈).
  - CLAUDE.md '트랙 게이지 ≈0.29m' ↔ `Docs/02_hardware/WT600_UPDATE_BRIEF.md` 11 행 '0.245 m 실측 확정 · 0.29 계산치 폐기' → **CLAUDE.md 고침**(11-04).
  - 09-07 `Docs/debug_log/2026-09-07/outputs/job47a_verify.txt` ③ 줄 문구 'EKF(0.783 적용)' 가 VX_SCALE 1.0 배포 뒤에도 그대로(`Docs/debug_log/2026-09-07/jobs/job45_tape.py` 고정 문자열, 동작 영향 없음).
  - 09-08 Foxglove 추가 토픽 수: SUMMARY 7 개 나열 ↔ `foxglove-snap-cpu.md` '6 개'(미대조).
  - 09-09 SUMMARY 806 행 '다음' 의 raytrace_min_range 0.35/0.30 이 같은 날 §8.7(0.60) · §8.11(STVL) 뒤 낡음.
  - 09-10 §0-4 '80 분 정지 후 약 105°' 는 계산값(1.31 °/분 × 80) — 커밋 ebc58859 메시지의 관측은 −2.2° → 115°(약 117°).
  - 09-11 'ABORTED x m' 의 정의 없음(이동 거리로 보임, s4r1 1.22 m vs CSV 최대 전진 0.29 m).
  - 09-14 §2.17 tc2 '≥0.07 비율 87 %' 재현 안 됨(`Docs/debug_log/2026-09-14/outputs/tc2.csv` 정지 포함 56 % · 이동만 73 %).
  - 09-21 `BASELINE_STVL.md` §5 '스크립트는 09-21 jobs/' ↔ 실제 09-17 · 09-18 jobs/, 문서 경로 둘은 09-21 재구성 전 경로.
  - 09-23 `Docs/debug_log/2026-09-23/outputs/j531c_pcl.txt` 27~28 행: C1 3 차가 게이트 N 불합격으로 끝남 — SUMMARY §3 에 없음, `nvblox-n6-global-ghosts.md` §6-6 'fail-open' 은 '판정이 다른 값에 달림' 이 정확(카드에 표시함).
  - 09-30 §16 map→odom '서서히' — `Docs/debug_log/2026-09-30/outputs/j718_map2_break.txt` 10 s 요약에선 y 가 +0.38 m 까지 갔다 돌아옴(결론 영향 없음).
- 크기: 본문 다수가 목표 30 KB 를 넘음(한글 · 정정 표시) — 줄이지 않음.
- 게시는 비공개(소유자만). push 는 안 함(지시 대기).
- 규칙 검사 경고 10 건 = 포인터를 덧붙인 9 월 SUMMARY 에 원래 있던 "적힌 경로가 없음"(09-16 · 22 · 28 · 29 · 30 — job312 · job322 · job627 · job562 · job651 · job692 · job697 · j705 · j713/714 · j717, 원천 소실 · 이름만 적힌 것). 예전 결함이라 고치지 않음.

## §12 강제 장치 ① — 기록 규칙 새 경고는 커밋 차단 (사용자: "1번부터 순서대로 진행하라")
- 배경(사용자 점검 질문): 기계 강제는 비밀번호 · push · sudo 뿐이고 `chk_record_rules.py` 는 경고만(Claude 훅이 개수만 알림) — RULES_WARN 이 남은 채 커밋한 적 있음.
- `Docs/tools/chk_record_rules.py`: `--every`(추적 · 새 Docs 파일 전부) · `--write-baseline` · `--new-only`(기준선에 없는 경고만, 있으면 종료 1) 추가. 기준선 `Docs/tools/rules_baseline.txt` 110 건(N 67 · H 22 · P 18 · T 3 — 옛 기록 결함).
- `Docs/tools/chk_commit_gate.py`: 비밀번호 검사 뒤 `--new-only` 를 돌려 새 경고가 있으면 막음(Claude 훅 종료 2 · git 훅 1). 예전 개수 알림은 뺌.
- 시험: 이름 · 머리 주석 없는 시험 스크립트(jobs 아래 badname_test.sh, 시험 뒤 지움)를 만들어 두 경로 모두 '새 경고 2'(H · N)로 막힘 확인 → 지우고 깨끗한 상태 통과(종료 0). README §8 · 변경 이력에 적음.
- 첫 실전: 이 § 를 커밋할 때 게이트가 내 SUMMARY 의 지운 시험 파일 경로(P 경고)를 잡아 막음 → 문구를 고쳐 통과. 훅은 명령 실행 전에 검사하므로 고치는 명령과 커밋은 따로 실행해야 한다.
