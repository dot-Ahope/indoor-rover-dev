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
