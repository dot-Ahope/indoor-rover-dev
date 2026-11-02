# 2026-11-02 SUMMARY

## §0 문제 대장 4 기 마무리 · 5 기 착수 (사용자: "A·C 이어서 마무리하자. 그리고 다음 기수 진행하자.")
- 10-30 중단된 두 묶음은 이어 붙일 수 없어(중지된 작업 재개 불가) 남은 일만 맡긴 새 묶음 둘로 마무리 → 4 기 카드 전부 완료: 새 `pre-drive-dds-participants.md` · `phase-s-baseline.md`, `obstacles-to-costcritic.md` 도구 해설, `depth-obstacle-costmap.md` 09-21 §5~§6, `f0-rotation-side-slip.md` · `sensor-conditioner.md` 완료 확인, `jetson-wifi-link.md` 09-23 보강. `Docs/issues/ISSUES.md` 4 기 표 갱신(‘이어서 할 일’ 절 제거).
- 원본 대조(내가 확인): `ros2_ws/src/rover_bringup/launch/ekf.launch.py` 39~40 행 — vslam ≠ off(기본 prep) 또는 rf2o 면 **B3(회전 구간 vx·vy σ 0.3) 자동 켜짐**(10-06 R3 · 10-20 근거 주석) → 의도된 동작. CLAUDE.md §6 'B2·B3 는 코드만 있고 기본 끔' 은 B3 에 대해 낡음(문서만, 결정 대기).
- 묶음 보고(대조 안 함): cc1 원인(메타 스냅숏) 근거가 기록보다 약함 — 스냅숏 전에 이미 map→odom 이 절반 속도 · '30 s' 는 측정 근거 없음 · relay min_range 0.45 는 기본 global_camera:=obstacle 에만 걸리고 순회 구성(nvblox)은 우회.

## §1 문제 대장 5 기(09-28 ~ 10-02) 완료 — 새 카드 10 장 · 앞 카드 8 장 이어 채움
- 새: slam-fork-rotation · icr-b2-b3 · board-oled-autostart · isaac-cuvslam-evaluation · onboard-stop-nav-guard · f0b-course · f1-office-mapping · f2-patrol-loc-jump · rotation-obstacle-smear · rf2o-introduction. 이어 채움: f0-rotation-side-slip · sensor-conditioner · foxglove-snap-cpu · joystick-teleop · slam-stamp-freeze · first-slam-map 등.
- 원본 대조(내가 확인): ① `Docs/tools/prep_patrol.sh` 17 행 `STUCK_SHADOW=true`(prep_fast 기본도 true) → 순회 때 stuck_monitor 는 **관찰만**(use_gyro 끔과 함께 로그만 남김) ② `rf2o_gate.py` 35 · 101 · 104 행이 데크 yaw π−0.04677 · 라이다 x 0.152 를 직접 가짐 — 데크 재측정 시 CLAUDE.md 가 적은 stuck_monitor 말고 이것도 고쳐야 함.
- 묶음 보고(대조 안 함, 결정 대기): SLAM 포크 회전 처리는 위치 추정 문턱 0.15 rad(6.9°)에서 효과 미측정 · `path_end_yaw.py` 는 GridBased(NavFn)에 묻고 실주행은 Smac 경로 · `conditioner:=py` + vslam 이면 B3 가 말없이 빠짐 · nav_guard CPU 19.5 % · 매핑 루프 창 3.0 m(09-30 부족) · nav2_params 264 행 '0.5×0.33' · localization.launch.py 예시 office_v2 등 주석.

## §2 낡은 주석 정리 (사용자: "낡은 주석 업데이트 하라. 그리고 push 진행.") — 커밋 9f1adbf4, 동작 변경 없음
- `nvblox_local.yaml` 머리말(미통합 · STVL 기본 → 09-23 통합, 슬라이스 0.03 → 0.06, 통합 거리 이력 → 지금 2.0) · 68 행 '거리(1.4 m)'.
- `nav2_params.yaml` temperature 묶음 위에 "ESS 기제는 09-17 §13 실주행 미확인 — 이력" · 264 행 풋프린트 0.5×0.33 → 0.51×0.33(09-30 실측) · cost_penalty 옛 주석 정정(09-14 §2.19 시행 1 = R · cost · non_straight 동시 변경).
- `safety_monitor.c` 승격값 0.020 · 초기 duty 0.37 → 지금 값 0.008 · 0.34 + 5.8×0.008 ≈ 0.39(계산, job397 실측 41 %) · `CTRL_HZ` 중복 정의 표시 + TODO(improve). 펌웨어 재플래시 불필요(주석만).
- `localization.launch.py` 예시 지도 office_v2 → office_v3.
- 남은 것: CLAUDE.md 'B2 · B3 기본 끔'(B3 는 자동 켜짐, §0) · stuck_monitor '작동 모드' 표현.

## §3 규약 원본 정리 (사용자 질문: README 가 낡았는데 지금은 세션 컨텍스트를 따르는가 → "1번부터 진행하라")
- 확인: `Docs/debug_log/README.md` 는 08-27 이후 미갱신(하루 끝 정리 · `jobNN` 이름 · 깨진 링크 `../JETSON_SETUP_BRIEF.md`). 실제 작업은 CLAUDE.md §1 과 세션 메모리 규칙 11 건을 따랐다 — 같은 규칙이 여러 곳에 있어 한 곳만 고치면 어긋남. 10 월 날짜 폴더 19 개 중 TOOLS.md 있는 곳 10 개.
- 조치: README 를 **규약 원본**으로 재작성(§0 언제 무엇을 읽나 · SUMMARY · 도구 · Jetson 실행 · 주행 · 보관 · 정리 페이지/대장 · 비밀/push · 옛 기록 읽는 법 · 변경 이력). CLAUDE.md §1 의 규약 본문은 "작업 전 README 해당 절을 읽는다" 로 줄임. 세션 메모리의 규칙 본문은 결정 날짜 · 이유 + README 절 연결로 줄임.
- 발견(고치지 않음): `Docs/tools/up_tools.sh` 기본 호스트가 옛 주소 `192.168.0.101`(지금은 `JETSON_HOST` 를 넘겨야 맞음).
- 다음(사용자 결정 대기): ② `.claude/settings.json` deny(origin push · sudo) + 경고용 점검 스크립트 ③ 커밋 훅(비밀번호 보관 위치 결정 필요).

## §4 규약 기계 장치 (사용자: "2번 진행하라")
- `.claude/settings.json` deny: `git push origin …` · `git push public …`(공개는 점검 있는 `private/publish_public.sh` 로만) · `sudo …` (Bash · PowerShell). 확인: `git push --dry-run origin no-such-branch-xyz` → 도구가 거부. 한계: ssh 문자열 안 `sudo` 같은 간접 실행은 못 잡음.
- 점검 도구 `Docs/tools/chk_record_rules.py`(경고만, README §8): 기본 = git 에서 바뀐 파일 · 그 날짜 폴더 → `RULES_OK`. `--all`(10-13 이후 전부) 결과 `outputs/chk_record_rules_all.txt`: 경고 93 = 앞머리 없음 N 64 · 설명 주석 없음 H 22 · 적힌 경로 없음 P 4 · TOOLS.md 없음 T 3(10-21 · 10-22 · 10-23).
- 읽은 것: N 64 중 `get_` 29 · `fill_` 4 · `put_` 3 · `mk_` 3 등 — 실제 작업이 규약 앞머리 6 개 밖의 이름을 계속 썼다(가져오기 `get_` 가 가장 많음). 규약을 넓힐지(예: `get_` = 가져오기) 이름을 지킬지는 사용자 결정. P 4 건: `2026-10-20/jobs/anal_vslam_cmp.py` · `2026-10-21/outputs/chk_day_start_1021.txt` · `2026-10-26/outputs/plan_offline/scenes_1023.npz` · `2026-10-26/outputs/planner_offline/goal_yaw/exp/` — 기록에 적혔으나 저장소에 없음(원천 확인 전, 고치지 않음).
- 비밀번호 게이트는 `ROVER_RUNNER=<run_jn.sh>` 를 줄 때만 돈다(값 출력 없음) — 커밋 훅(3 번)은 비밀번호 보관 위치 결정 대기.

## §5 앞머리 6 개 유지 · 비밀번호 저장소 밖 · 커밋 훅 (사용자: "지금 6개 지키기. 비밀번호를 저장소 밖 파일에 두어라. push하라.")
- 앞머리: 6 개(`prep_` `chk_` `run_` `anal_` `fig_` `up_`)만. Jetson → PC 가져오기는 `up_`(전송, 양방향)로 쓰고 `get_` · `put_` 은 새로 만들지 않음 — README §3.1. 옛 파일 이름은 그대로(§4 의 N 64 건은 옛 기록이라 안 고침).
- 비밀번호: PC `~/.config/rover_jetson/pw`(저장소 밖)에 러너 값을 옮김(출력 없음). ⚠ PC 홈 폴더 자체가 커밋 없는 git 저장소(원격 없음)라 그 저장소의 `.git/info/exclude` 에 `.config/rover_jetson/` 를 더함(로컬 설정, 커밋 아님).
- 훅 `Docs/tools/chk_commit_gate.py` 를 `.claude/settings.json` PreToolUse(Bash · PowerShell)에 등록: 명령에 `git commit` 이 있으면 staged 에서 비밀번호를 찾아 있으면 막고(exit 2), 파일이 없어도 막음. 통과 때 규약 경고 개수를 알림.
- 시험: ① 임시 저장소에 비밀번호 파일 staged → 막음(파일 이름만 표시) ② commit 아닌 명령 → 통과 ③ 비밀번호 파일 없음 → 막음 ④ 한글 커밋 메시지 → 통과(처음 판은 stdin 을 콘솔 기본 인코딩으로 읽어 JSON 이 깨지면 그냥 통과하는 결함 — utf-8 로 읽고, 깨져도 원문에서 git commit 을 찾게 고침) ⑤ 실제 세션: 비밀번호 파일을 잠시 치우고 `echo "git commit …"` → 훅이 막음, 되돌림.
- `chk_record_rules.py` 의 비밀번호 점검도 같은 파일을 기본으로 읽음.

## §6 규약 장치 평가 반영 (다른 세션 평가 → 사용자: "1b, 1c 빼고 수행하자.")
- **공개 저장소의 옛 비밀번호(확인)**: `.claude/settings.local.json` 이 05-21(`c8593604`)부터 추적되어 `sshpass -p <옛 값>` 명령 38 줄(옛 주소 192.168.0.104)이 공개 `dev` · `main` 의 현재 파일과 이력 4 커밋에 있다. 값은 한 종류 · 지금 값과 다름 → 게이트(지금 값만 검사)를 통과했다. 다른 파일에는 없음(전 이력 `-S` 검색). 도구 `outputs/` 대신 스크래치패드 일회성 스캔(값 출력 없음, 원천 = 대화 기록).
  - 내 실수: §4 에서 이 파일을 "옛 허용 규칙" 으로 보고 내용을 안 열었다. 게이트가 지금 값 하나만 본다는 한계도 못 짚었다. 다음에 알아보는 법: 추적 파일 목록에 개인 설정(`*.local.*`)이 있으면 내용을 연다 · 비밀 게이트는 옛 값도 넣는다.
  - 하지 않은 것(사용자 결정): 공개 · 비공개 이력 다시 쓰기(1b · 1c). 옛 값이 다른 기기 · 계정에서 아직 쓰이면 바꾸는 것은 사용자 몫(1d).
- 조치: ① `git rm --cached .claude/settings.local.json` + `.gitignore`(로컬 파일 유지) ② 비밀번호 파일을 여러 줄로(첫 줄 지금 값, 둘째 줄 옛 값) ③ 게이트가 staged + 추적 작업 트리를 모두 검사 ④ git 자체 `.git/hooks/pre-commit` 설치(터미널 커밋) ⑤ `up_tools.sh` 기본 주소 192.168.0.110 ⑥ README §0 표를 CLAUDE.md 에 사본으로 두고 `chk_record_rules.py` 가 두 표를 비교(D).
- 시험: ⓐ 추적 해제 전 이 저장소에서 `git commit -am` 모의 → 옛 값으로 막음(실제로는 그 명령 문자열 때문에 Claude 훅이 먼저 막았다) ⓑ 해제 뒤 → 통과 ⓒ 임시 저장소: 추적 파일에 지금 값을 넣고 stage 안 함 → Claude 훅 모드 막음(exit 2) · 실제 `git commit -am` → git 훅이 막음(exit 1, 커밋 수 그대로).

## §7 승인 명령 누적 정리 (사용자: "한번만 쓴 명령이 쌓이고 있는 것 같은데, 해결방안은?" → "진행하라.")
- 원인: 승인 창의 '다시 묻지 않음' 이 명령 문자열을 통째로 `.claude/settings.local.json` allow 에 저장 → 63 줄(PowerShell 53 · Bash 8 · Read 2, 200 자 넘는 한 번짜리 35), 대부분 05 월 다른 PC 경로 · 옛 WSL 명령. §6 의 비밀번호 노출도 같은 경로.
- 조치(로컬 파일, 추적 안 함): 원본을 저장소 밖 `~/.config/rover_jetson/settings.local.backup_1102.json` 에 백업 → allow 를 읽기 전용 · 빌드 와일드카드 11 줄로 교체(git status/log/diff/show · 규약 점검 · 색인 생성 · 펌웨어 make · gcc 버전). 러너 · 플래시 · Jetson 명령은 넣지 않음(매번 확인). deny 2 줄 유지. 정리 뒤 파일에 비밀번호 0.
- README §8 에 두 줄: 명령 문자열에 비밀번호 금지 · 한 번짜리는 '이번만', 반복은 와일드카드 한 줄.
- 추가 발견: 지운 줄 중 하나가 `SSHPASS=<값>` 형식(벤더 이미지 기본 비밀번호로 보임, §6 검색은 `sshpass -p` 형식만 봐서 놓침)이었고 공개 `main` 현재 트리 · 이력 1 커밋, `dev` 이력 2 커밋에 있다. 흔한 단어라 게이트 감시 값에는 넣지 않음(오탐). 쓰는 곳이 있는지는 사용자 확인.

## §8 공개 이력 다시 쓰기 (사용자: "B로 가자. 누가 사본 가져가지는 않았을 거다.")
- 질문에 대한 답(사용자: "main 갱신은 보안상 문제가 있는 커밋까지 수정한다는 의미인가?"): 아니다 — `--push-main` 은 `dev:main` 앞당기기라 옛 커밋은 그대로 남는다. 커밋에서 지우려면 이력 다시 쓰기 + 강제 push(B).
- 조치: `private/publish_public.sh` ① 제외 목록에 `.claude/settings.local.json` ② 점검에 비밀번호 n4(저장소 밖 비밀번호 파일의 모든 줄을 공개 이력 전체에서 검색, 값 출력 없음 — 파일이 없으면 중단) ③ `--rewrite`(사용자 결정 때만, `--force-with-lease`).
- 먼저 마른 실행(push 직전에서 멈춤): 점검 0 · 0 · 0 · 0, 필터된 이력 846 커밋, settings.local 커밋 0, 남은 `SSHPASS=` 1 건은 `<PW>` 자리표시, 벤더 기본값 0.
- 실행 `--push-main --rewrite`: 공개 `dev` 7d8ed124 → 93c12242 · `main` eec6f67a → 93c12242(강제). 확인: 두 가지 모두 settings.local 커밋 0 · 비밀번호 0 · 벤더 기본값 0. 공개 저장소 가지는 dev · main 둘뿐(태그 없음).
- 남은 한계: GitHub 는 참조가 끊긴 옛 커밋을 해시로 한동안 보여 줄 수 있다(완전 삭제는 GitHub 지원 요청). 비공개 `personal` 이력은 그대로(사용자 결정 1c 제외). 다음 공개부터는 같은 옵션이라 일반 push.

## §9 마무리 (사용자: "비공개는 냅둬라 어짜피 아무도 못보는데. 오늘 한 일 정리하고 마무리해라.")
- 결정: 비공개 `personal` 이력은 다시 쓰지 않는다(옛 비밀번호 남음, 비공개).
- 오늘 한 일
  1. 문제 대장 4 기 마무리 · 5 기(09-28 ~ 10-02) — 카드 60 장(§0 · §1).
  2. 낡은 주석 정리(동작 변경 없음, §2).
  3. 규약 원본을 `Docs/debug_log/README.md` 하나로 · CLAUDE.md 는 §0 표 사본 + 요지 · 메모리는 이유만(§3).
  4. 기계 장치: deny(origin · public 직접 push · sudo) · 점검 `chk_record_rules.py`(경고) · 커밋 게이트 `chk_commit_gate.py`(Claude 훅 + git pre-commit, 지금 값 · 옛 값, staged + 작업 트리) · 비밀번호 저장소 밖(§4 · §5 · §6).
  5. 옛 비밀번호 노출 처리: `settings.local.json` 추적 해제 · 허용 목록 63 → 11 줄 · 공개 이력 다시 쓰기(dev · main = 같은 커밋, 비밀번호 0)(§6 · §7 · §8).
- 다음 후보(결정 대기)
  - 문제 대장 6 기(10-06 ~: rf2o 라이브 · G3/G4 · 남서 정체 · 10-08 회전 방식 · 10-12 MPPI 포화).
  - CLAUDE.md 'B2 · B3 기본 끔'(B3 자동 켜짐, §0) · stuck_monitor '작동 모드' 표현.
  - 10-29 이후 묶음 보고 항목(대조 전): SLAM 포크 0.15 rad 효과 · path_end_yaw 계획기 불일치 · conditioner:=py + vslam B3 누락 · nav_guard CPU · 매핑 루프 창 3.0 m 등.
  - 드리프트: 위치 확인 ⓐ 배포 · d2(10-29 §4 선언).
  - F2.5: place_web 휴대폰 시험 · §8-4~6.
  - 기록에 적혔으나 없는 파일 4 건(§4) · TOOLS.md 빠진 날 3 개(10-21~23).

## §10 정리 페이지 · 규약의 아티팩트 항목 (사용자: "아티팩트로도 정리해주고, 로컬에도 저장 후 push하라. 그리고 현재 규약에 아티팩트 관련 내용도 있는지 확인")
- 정리 페이지(아티팩트 https://claude.ai/artifact/9oVgtwC3JSKStBX82JnbAe): `figures/day_summary_1102.html`(머리 = `2026-10-28/jobs/report_1028_head.html` 제목만 바꿈 + 본문 `jobs/report_1102_body.html`, 조립 `jobs/fig_report_1102.py`, 그림 없음). 원천 = 이 SUMMARY §0 ~ §9 · `TOOLS.md`.
- 규약 확인: README §7.1 에는 **형식**(본 것 → 추론 → 결론 · 실수 `.pm` 칸)만 있었고, 만드는 때 · 로컬 사본 위치 · SUMMARY 에 남길 것 · 공개 저장소 주의는 없었다(10-20 ~ 10-28 실제 방식은 SUMMARY 에만). → §7.1 에 네 항목 추가, 변경 이력 한 줄.
- 오늘 쓴 일회성 스크립트를 스크래치패드에서 `jobs/` 로 옮김(`chk_leak_scan_1102.py` · `up_pw_old_1102.py` · `chk_pub_filtered_1102.sh`, 값 출력 없음 · 벤더 기본값 검색어는 공개 파일이라 뺌) · `TOOLS.md` 작성(그날 끝에 몰아 씀 — 규약 §3.3 위반, 사후 표시).

## §11 설명에 스크립트 · 결과 내용을 함께 (사용자: "설명할 때, 스크립트 내용 및 추론에 사용된 결과 내용도 같이 적는게 좋을 것 같다.")
- 규약 README §2.3 · §7.1: 추론마다 **스크립트 핵심(판정 · 계산 줄 발췌)** 과 **나온 결과(출력 원문 발췌, 비밀은 가림)** 를 본문에 같이 둔다. 실수 칸에 '스크립트 핵심' · '나온 결과' 두 칸 추가. SUMMARY · 정리 페이지 · 대화 설명 모두.
- 오늘 정리 페이지에 적용(같은 주소 다시 게시): 규약 점검 판정식 + 실제 경고 줄, 노출 검색 스크립트 + 결과, 공개 스크립트 추가분 + 강제 push · 확인 출력, 실수 4 건 각각 코드 · 출력.
- 대화에만 있던 출력을 `outputs/` 로 옮김(규약 §2.3): `outputs/leak_scan_1102.txt` · `outputs/gate_tests_1102.txt` · `outputs/publish_rewrite_1102.txt`(모두 '대화 기록에서 옮김' 표시, 비밀번호 0).
- §11 보강: 발췌마다 결과 · 스크립트 원문 경로(커밋 해시 · '원문 없음' 포함), 정리 페이지 3 판.

## §12 10 월 정리 페이지 17 장에 발췌 · 원문 경로 붙임 (사용자: "10월달 아티팩트에도 적용 가능하면 적용하자" → "17장 전부 발췌까지")
- 방법: 병렬 묶음 6 개(페이지마다 담당 하나). 각 묶음이 게시본을 먼저 읽어 로컬과 대조(17 장 모두 감싸개 · 줄끝만 다름) → 판단마다 스크립트 핵심 · 나온 결과 · 두 원문 경로(나중에 바뀐 스크립트는 그날 판 커밋) · 없으면 '원천 소실' → 같은 주소로 다시 게시. 근거는 저장소 파일에서만.
- 붙인 판단 수: 10-01 9 · 10-02 11 · 10-06 7 · 10-07 6 · 10-08 7 · 10-12 7 · 10-13 9 · 10-14 3 · 10-15 7 · 10-19 8 · 10-20 9 + 실수 3 · 10-21 9 + 실수 4 · 10-21 2 쪽 1 · 10-22 11 · 10-23 10 · 10-26 11 · 10-27 12 · 10-28 8.
- 내 확인: 바뀐 파일 22 개 전부 비밀번호 · 벤더 기본값 · 금지 문구 · U+FFFD · NUL · `sshpass -p 값` · MAC 0. 지운 줄은 페이지마다 0~2(머리말 한 줄 · CSS 한 줄을 고친 것). 10-28 머리(11-02 페이지 공용)는 안 바뀜. 보고 대조 2 건 직접 확인: 10-22 SUMMARY §16 기준 4 ✘(페이지 카드는 ok) · 10-26 `outputs/compare/fig_box_compare.txt` B0 15.2(페이지 15.4).
- 진행 중 문제: 묶음끼리 스크래치패드 도우미 이름(`ann.py`)이 겹쳐 덮어씀 → 날짜 붙인 이름으로 바꾸게 하고 각자 백업과 diff 로 자기 변경만 들어간 것을 확인. 10-07 첫 게시본에 원문 출력의 NUL 문자가 섞여 바로 다시 게시. 10-14 묶음은 응답이 분류기에 막혀 한 번 멈췄다가 이어서 끝냄.
- **페이지 · 원본 기록과 원문 출력이 어긋난 곳(고치지 않음, 사용자 결정 대기)**:
  - 페이지 쪽: 10-01 채택 지도 설명(채택본 = +590 s 자른 판, '점프 3 s 전' 은 기각 후보) · 10-01 '끝까지 재생 0.17 m 휨'(실제 +699 s 후보) · 10-06 홀수 단계 원인에 '직진 축척 0.93'(SUMMARY §4.1 에 없음) · 10-08 '치운 뒤 2~5 s'(원문 3~5 s) · 10-08 여유 0.029~0.057(원문은 seed 1 만) · 10-19 '시험 상자 치움'(10-20 §3.2 에서 정정됨) · 10-21 '정지 부하 75.7 %'(주행 중 CPU, 정지 부하는 53 %) · 10-21 '토픽에 노드 이름을 안 붙임'(원문 목록엔 붙어 있음) · **10-22 f2pi1 3/3 카드가 ok(기준 4 ✘)** · 10-22 1.1 · 1.2 cm(표본 시각 차) · 10-23 12.3 · 15.4 cm 출처(track_dev) · 10-23 '58~59 s'(원문 62.99 s) · 10-23 '해석 확장 줄이면 즉시 실패'(rp1 장면 일부 작동) · 10-26 B0 15.4(원문 15.2) · 10-26 '0.01~0.05 s'(SUMMARY 0.01~0.06) · 10-27 §15 '두 장뿐'(원문 3 장) · 10-28 0.39 °/min 과 10.95 °/min(다른 양, 혼동 주의).
  - 원본 기록 쪽: 10-07 SUMMARY §8.5 '49 → 86'(원문 65~76 → 107~184) · 10-12 TOOLS.md '손실 원래 0~2'(원문 42.5 /s, 창 차이일 수 있음) · 10-26 TOOLS.md `anal_contact` 위치(실제 `2026-10-22/jobs/`) · 10-26 `up_bundle.sh` 주석 '5 개'(20 개) · 10-27 §24 '같은 값'(새 게이트 C FAIL) · 펌웨어 `microros_task.c` V_MAX 주석 0.100(정의 0.085).
- 다음: 문제 대장 6 기(사용자: "10월 끝나면, 먼저 마무리할 수 있어 보이는 문제 대장을 진행하자").
