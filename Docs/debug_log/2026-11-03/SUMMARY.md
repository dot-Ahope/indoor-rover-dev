# 2026-11-03 SUMMARY

## §0 문제 대장 7 기(10-12 ~ 10-15) 착수 (사용자: "7기 진행.")
- 묶음 6 개, 카드마다 담당 하나. 각 묶음은 11-02 §12 에서 발췌를 붙인 그날 정리 페이지(10-12 · 10-13 · 10-14 · 10-15)를 길잡이로 쓰고 SUMMARY · 원문으로 다시 확인.
  - A 통신 포화(MPPI 궤적 발행 · /tf HEARTBEAT · 기록기 best effort) 새 카드 + W3 떨림 · TF 지연 이어 채움
  - B DDS 공유메모리 · 제로카피 질의(이어 채움) · 빠른 prep 새 카드 · 회전 방식 카드에 PreferForward 15 검증
  - C 상자 옆 정지 — 원인 새 카드 + 낮은 상자 기억 이어 채움
  - D 갇힘 해제 pad_relief · 실행 중 패딩 변경 멈칫 새 카드
  - E 상자 옆 정지 — 그 밖의 대책(전역 감쇠 · cost_weight · 통합 거리 · MonotoneEscape · ClearanceBand) 새 카드
  - F BT 끝 방향(TruncatePath → CopyPath) 새 카드 · F2 기준선 no5 새 카드 · 남서 정체 · Jetson Wi-Fi 이어 채움

## §1 7 기 완료 — 새 카드 7 · 이어 채움 6
- 새: `network-saturation-mppi-viz` · `prep-fast-startup` · `box-side-stall-cause` · `box-side-stall-remedies` · `pad-relief-runtime-padding` · `bt-copypath-end-yaw` · `f2-baseline-no5`. 이어 채움: tf-lag-w3-wobble · dds-shm-incident · rotation-method-track-ratio · low-box-global-memory · southwest-orient-stall · jetson-wifi-link. 묶음 보고의 링크를 머리 표 '관련 문제' 칸에 덧붙임(카드 18 장). ISSUES.md 7 기 표 · 색인 다시 생성. 카드 73 장(ISSUES.md 제외).
- F 묶음이 bag 을 PC 에서 다시 분석해 10-14 '원천 소실' 이던 끝 방향 출력을 되찾음 → `outputs/anal_path_endyaw_s1g3.txt` · `anal_path_endyaw_t1g3.txt` · `anal_path_endyaw_t1g5.txt`(스크립트 `2026-10-14/jobs/anal_path_endyaw.py`, 스크래치패드 결과를 옮김). 남서 목표: TruncatePath 시절 컨트롤러 끝 방향 0.0° · 계획기 −101.3° 직접 확인.
- 내 대조(직접 확인): 러너 `2026-10-27/jobs/job551_f0drive.sh` 46~67 행 — `/tf` best effort 재정의(54 행)가 `BAG_BE_TRAJ` 조건 안 · `prep_fast.sh` 12 행 `sed -i` 남음 · `pad_relief.py` 35 행 mode 기본 'on'(launch 기본 off, 표준 prep 은 안 띄움) · `nav2_params.yaml` 255 · 276 ClearanceBandCritic 목록에 있고 enabled false · `monotone_escape_behavior.cpp` 58~60 · `nav2_params.yaml` 804~806 풋프린트 손 입력값 · BT 108 PathBlockedAhead min_cost 99.
- **바로 고친 것 1 건(보안)**: PC 스크래치패드 실행본 `run_f0.sh` 4 행 기본 주소가 옛 `192.168.0.101`(10-14 다른 서버가 가져간 주소) — 직접 부르면 그 주소로 비밀번호를 보낼 수 있어 `192.168.0.110` 으로 바꿈(저장소 밖 파일, 되돌리기 쉬움). 저장소의 날짜 사본(2026-10-14 · 10-21 · 10-27 jobs)은 기록이라 그대로.
- 지금 코드 · 문서에 걸린 것(결정 대기, 바꾸지 않음):
  - 러너 `/tf` 재정의를 `BAG_BE_TRAJ` 조건 밖으로 · `prep_fast.sh` `sed -i` 링크 끊김 · `pad_relief.py` 기본 'on' · `chk_padding_dynamic.py` 에 '돌린 뒤 prep 재기동' 경고 없음 · MonotoneEscape 풋프린트를 코스트맵에서 읽게(데크 · 차체 상수 목록에 추가).
  - 낡은 주석: `navigation.launch.py` 229~230(pad_relief off 이유) · 133~134('4/4' → 6/6) · BT 74 행 · 러너의 기각된 '재전송 씨앗' 근거.
  - CLAUDE.md: 'prep 기본 shadow'(지금 안 띄움) · '4~5 cm 밀림'(출발점 상자만) · TEST_COURSE 'v2.2'(파일은 v2.3) · 'A/B 확정' 범위.
  - 남서 목표 `p` 재시험(BT 결함은 해소, 고친 뒤 3 회 모두 f) · F2 기준선 문서 `BASELINE_F2.md` · 태그 없음 · ClearanceBand 를 목록에서 뺄지.

## §2 어긋남 23 건 정정 (사용자: "어긋남 23건 및 코드,문서 수정 진행.") — 원문은 지우지 않음(README §2.1)
- 페이지 17 건(11-02 §12 목록): 정리 페이지마다 해당 문장 옆에 '11-03 정정' 표시를 덧붙여 같은 주소로 다시 게시 — 묶음 하나가 게시본을 읽고 근거를 다시 확인한 뒤 진행(결과는 §5).
- 원본 기록 6 건 — 틀린 줄 끝에 '→ 2026-11-03 §2 정정' 만 덧붙임:

  | 원본 | 적힌 것 | 원문 | 처리 |
  |---|---|---|---|
  | 2026-10-07 SUMMARY 229 행(§8.5) | '출발 방 그 밖 고비용' 49 → 86 | `2026-10-07/outputs/j924_box_steps.txt` 69 · 74 … (65~76 → 107~184, 11-02 묶음 보고) | 표시 |
  | 2026-10-12 TOOLS.md 123 행 | f2k1 '포화 전 기록기 손실 원래 0~2' | 출력 42.5 /s 는 T−60 s 창이 15:25:19 폭증 표본을 포함, 2 s 표는 0~2 — 둘 다 맞음 | 표시(✔ 는 10-13 결과로 낡음) |
  | 2026-10-26 TOOLS.md 40 행 | `anal_contact` 가 10-23 jobs 계열 | 실제 `2026-10-22/jobs/anal_contact.py` | 표시 |
  | 2026-10-26 SUMMARY 137 · 150 행 | B0 15.4 | `2026-10-26/outputs/compare/fig_box_compare.txt` 15.2(같은 SUMMARY 153 행도 15.2) | 표시 |
  | `Docs/tools/plan_offline/up_bundle.sh` 7 행 주석 | planner_server 5 개 | 10-26 SUMMARY 18 행 '정리 전 20 개 프로세스' | 주석 고침(계속 쓰는 도구라 기록 아님) |
  | `firmware/.../microros_task.c` 72 행 주석 | V_MAX '0.100' | `rover_platform.h` 82 행 0.085(09-07 스케일 정정) | 주석 고침(펌웨어 재플래시 불필요) |
- 10-27 §24 '같은 값' 은 다시 보니 원문(337 행)이 새 C 의 FAIL(stamp 지연 1.14 s)을 이미 적고 있어 어긋남이 아님 — 정정 안 함(23 건 중 1 건 철회).

## §3 코드 · 주석 수정
- **러너 `job551_f0drive.sh`**(실행본 = PC 스크래치패드, 오늘 판 사본 `jobs/job551_f0drive.sh`): `/tf` · 깊이 QoS 재정의를 `BAG_BE_TRAJ` 조건 밖으로 — 항목마다 따로 켜고, 파일이 비지 않았을 때만 `--qos-profile-overrides-path`. 확인: 그 블록만 떼어 `BAG_BE_TRAJ=1 · 0` 으로 돌려 둘 다 `/tf:` 1 줄(전엔 0 이면 없음). 실주행 확인은 다음 주행.
- **`Docs/tools/prep_fast.sh`**: PreferForward `sed -i` 를 '값이 같으면 손대지 않음 · 다르면 `--follow-symlinks`(링크 유지, 알림)' 로 + 설치본이 링크가 아니면 경고. 확인 `jobs/chk_prep_sed_1103.sh` → `outputs/chk_prep_sed_1103.txt`(WSL 리눅스, 임시 링크 파일: 15.0 → 안 건드림 · 링크 유지, 5.0 → 바꿈 · 링크 유지). Jetson 실 prep 은 미검증 — ⚠ Jetson 의 `/tmp/prep_fast.sh` 는 옛 판이므로 다음 prep 전에 올려야 함. `Docs/tools/up_tools.sh` 는 스크래치패드 `tools/` 폴더를 읽는데 그 폴더가 지금 없음(전송 경로 정리 필요).
- **`pad_relief.py`**: `mode` 기본 'on' → 'off' + 머리말에 '쓰지 않는다' 경고. `navigation.launch.py` 의 pad_relief off 이유 주석 정정.
- **`chk_padding_dynamic.py`** · `Docs/tools/README.md`: '돌린 뒤 주행 전 prep 재기동' 경고.
- 주석: `nav2_params.yaml` 전역 nvblox 층 프레임 전제(563 행 부근) · `monotone_escape` footprint 손 입력값 경고 · `rf2o_gate.py` 머리말(회전 속도 원천 ekf · 0.15 s, 데크 상수) · `navigation.launch.py` 궤적 발행 '4/4' → 6/6 · BT XML ForceSuccess → CopyPath · 러너의 '재전송 씨앗' 근거(10-13 으로 /tf 였음).
- 바꾸지 않은 것: MonotoneEscape 가 코스트맵 풋프린트를 직접 읽게 하는 C++ 수정(빌드 · 실험 필요 — 경고 주석과 CLAUDE.md 목록으로 대신), ClearanceBandCritic 을 목록에서 빼기(enabled false 라 동작 영향 없음), 남서 `p` 재시험 · F2 기준선 문서(주행 · 결정 필요).

## §4 CLAUDE.md 정정
- B3 는 vslam/rf2o 때 자동 켜짐(옛 'B2 · B3 기본 끔') · stuck_monitor 는 표준 prep 에서 관찰만 · 데크 재측정 때 함께 고칠 곳(`rf2o_gate.py`, `monotone_escape` footprint) · pad_relief 'prep 기본 shadow' 정정 · A/B 범위 · '4~5 cm 밀림' 은 출발점 상자 기준 · TEST_COURSE v2.3.

## §5 내 실수 — 대화에 Jetson 비밀번호를 출력함
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 러너가 어느 job551 을 올리는지 보려고 `grep -n "job551" run_f0.sh run_f2c.sh` |
| 본 것 | `run_f0.sh` 10 행 전체가 출력되며 `sshpass -p` 뒤 값이 그대로 나옴 |
| 왜 생겼나 | 러너 파일은 비밀번호를 평문으로 가진다(README §4). 같은 세션 앞쪽에서는 `sed 's/sshpass -p [^ ]*/…/'` 로 가렸는데 이번 명령은 가림 없이 grep 했다 |
| 영향 | 값은 저장소 · 공개물에는 없음(이 기록에도 안 씀). 대화 기록(로컬 transcript 와 모델 요청)에 남았다 |
| 다음에 알아보는 법 | 러너(`run_*.sh`) · 비밀번호 파일을 읽는 명령은 **항상** `sed 's/sshpass -p [^ ]*/sshpass -p <PW>/g'` 를 붙이거나 줄 번호만 찍는다(`grep -c`, `grep -n … | cut -d: -f1`) |
| 조치 | 사용자에게 알리고 Jetson 비밀번호 변경 여부를 묻는다. 바꾸면 `~/.config/rover_jetson/pw` 첫 줄 · 러너 2 개를 새 값으로, 옛 값은 둘째 줄 이하로 |

## §6 정리 페이지 17 건 정정 결과 (§2 의 묶음)
- 17 건 모두 원문과 다시 대조해 근거 확인 → 페이지 10 장에 정정 표시 25 곳(`<span class="c1103">(11-03 정정: … — 근거 경로)</span>`, 각 페이지 색 토큰 사용), 머리글 아래 한 줄 안내, 같은 주소로 다시 게시(10-01 · 06 · 08 · 19 · 21 · 22 · 23 · 26 · 27 · 28). 10-22 f2pi1 카드는 통과 → 보류 색으로 바꾸고 기준 4 ✘ 를 적음. 10-26 ~ 28 은 본문만 고쳐 빌더로 다시 만듦(10-28 머리 그대로).
- 보존 확인(묶음): 정정 표시 · 안내 한 줄 · CSS 한 줄을 빼고 카드 색을 되돌리면 13 파일 모두 백업과 같음. 검사 13 파일 모두 비밀번호 · 금지 문구 · U+FFFD · NUL · MAC 0. 삭제 줄 1~5 는 정정을 원문 줄 안에 끼운 탓.
- 묶음이 더 찾은 것: ① 10-08 SUMMARY 23 행도 '8 칸 중 6 칸(75 %) 3 s' — 정정 표시 덧붙임(→ 이 §) ② 10-23 페이지 판정 카드에도 B0 15.4 가 하나 더 있음 — 표시 안 됨(남은 것) ③ 10-23 '58~59 s' 와 맞지 않는 줄이 f2von2 에도 있음(경로 받고 0.03 s 뒤) — 표시 안 됨(남은 것).

## §7 CLAUDE.md 지적 4 건 대조 (사용자가 붙여 준 평가)
- ① Smac 은 기본이 아님 — 맞음: `navigation.launch.py` 203 행 planner 기본 'navfn', `Docs/tools/prep_patrol.sh` 17 행 재계획 기본 0.5. 10-26 ~ 28 jobs · SUMMARY 에 `NAV_ADD="planner:=smac"` 5 회 · `REPLAN_HZ=0.01` 5 회 → CLAUDE.md 10-27 ① 에 '기본 아님' 과 시험 인자를 적음.
- ② 'B2 · B3 기본 끔' — 맞음, §4(커밋 ce1a0bee)에서 이미 고침(B3 는 vslam/rf2o 때 자동 켜짐).
- ③ `place_server` · `place_web` 은 어떤 launch 에도 없음 — 맞음(`ros2_ws/src/*/launch/` 검색 0) → F2.5 줄에 시험 단계라고 적음.
- ④ `rover_msgs` 없음 — 맞음(`ros2_ws/src/` 에 rover_bringup · rover_description · rover_navigation 뿐) → 디렉토리 표에 '지금은 없음'.

## §8 10-23 페이지 남은 2 건 (사용자: "10-23 남은 2건 고치라.")
- 판정 카드 B0 15.4: 출처는 `2026-10-23/outputs/anal_track_dev_f2rp1.txt` 의 1 s 간격 표본(205.0 행) — 틀린 값이 아니라 표본 간격 차이. 0.1 s 간격 복귀 구간 최소는 15.2(`2026-10-26/outputs/compare/fig_box_compare.txt`) → 그 차이를 적은 정정 표시.
- '상자 58~59 s' 판별 줄: f2von2(재계획 0.5 Hz)의 상자 옆 막힘 (1.34, 0.05) 은 경로 받고 0.03 s 뒤(`2026-10-23/outputs/anal_pba_timing.txt`, 10-23 SUMMARY §20.2) → 정정 표시 추가. 머리 안내 5 → 7 건.
- 같은 주소 다시 게시(5 판). 검사 0.

## §9 문제 대장 8 기(10-19 ~ 10-23) (사용자: "jetson 비밀번호안바꿔도 된다. 8기 진행하라.")
- 사용자 결정: Jetson 비밀번호는 바꾸지 않음(§5 의 노출은 이 대화 안에서만).
- 7 묶음 병렬 작성(카드마다 담당 하나): 새 카드 10 장 — `box-exaggeration-source` · `box-return-cells` · `projector-ir-alternation` · `cuvslam-velocity-fusion` · `camera-container-shm` · `ghost-cells-depth-preset` · `path-tracking-replan-b0` · `pathblocked-only-new` · `drive-ops-1019-1023` · `record-conventions-evolution`. 이어 채움 26 장. 카드 합계 83 장(ISSUES.md 제외).
- 머리 표 '관련 문제' 링크 34 장(스크립트, 이미 있으면 건너뜀) · ISSUES.md 8 기 표 · 색인 재생성(SECTIONS 1460 · RUNS 123 · JOBS 1895) · `chk_record_rules.py` RULES_OK.
- 대조(원본에서 직접 확인): mp4 2 개 git 추적 중(`git ls-files`) · `path_blocked_ahead_condition.cpp` 21 행 '목표 5 에 52 s' 그대로 · `fastdds_shm_udp.xml` 23 행 8 MB · `2026-10-20/outputs/anal_ekf_replay_live.txt` 13 행 W3 최대 12.1 · `2026-10-21/outputs/nav_events_ms.txt` 309~313 행 MonotoneEscape 4.6 → 5.1 cm.
- 묶음이 찾은 기록 어긋남(카드 '내 실수 · 기록 어긋남' 칸에 경로와 함께 적음 — 원본 SUMMARY · 코드는 아직 안 고침, 결정 대기):
  - 코드 주석: `nvblox_local.yaml` 57 · 62~64 행(1.4 근거 · '먼 비스듬한 첫 관측' 설명 낡음) · `camera.launch.py` 26~27 행(`emitter_off` 를 '오프라인 확인용') · 62~63 행(데시메이션 '확인 중') · `fastdds_udp_only.xml` 19~21 행(SHM '원인 제거') · `path_blocked_ahead_condition.cpp` 21 행 · `2026-10-27/jobs/job551_f0drive.sh` 40 행(BAG_IR 조건).
  - 기록: 10-19 §23.1 '근적외선 없음' 원인에 §24 정정 표시 없음 · 10-19 §22 '남쪽 15.7 cm' 는 북쪽 면 값 · 10-20 §7.3a 열 값 · 10-20 §9.7 'ttyUSB0 = 보드' 는 라이다 · 10-22 §21 '두 검증' 중 f2sm3 은 지표 없음 · '맨바닥 A' 지표 둘 · 10-23 §22.2 Smac 비교에 10-26 §6.1 무효 표시 없음 · B0 15.4 가 SUMMARY §17.1 · §21 · `SMAC_HYBRID_PLAN.md` 에 남음 · mp4 'git 제외' 서술.
  - 운용: `prep_fast.sh` 70 행 SHM 오류 검사가 cuvslam · nvblox 로그를 안 봄 · only_new(기본 true)와 표준 prep 0.5 Hz 조합 미시험 · `up_tools.sh` 가 스크래치패드 `tools/` 를 읽음(소실) · 10-22 13:42 172.30.1.8 에 정체 모를 기기 응답(그 주소 쓰기 전 신원 확인).
- MAC: 10-21 SUMMARY 31 행 · `2026-10-22/outputs/chk_wifi_1022.txt` 에 MAC/BSSID 가 가려지지 않음. 저장소 전체로는 MAC 모양 문자열이 있는 추적 파일 73 개(08-31 ~, 일부는 오탐 가능) — README §4 '가린다' 규칙 이전 기록 포함. 가림 여부는 사용자 결정.

## §10 하루 마무리 (사용자: "우선 오늘 일 마무리하자")
- 한 일: 7 기 · 8 기 문제 대장(카드 59 → 83 장) · 어긋남 23 건 정정 · 낡은 주석 · 러너 /tf QoS · prep PreferForward 링크 유지 · pad_relief 기본 off · CLAUDE.md 정정 · 정리 페이지 정정 표시(10-23 5 판 포함).
- 내 실수 1 건(§5 비밀번호 출력) — 사용자: 비밀번호 교체 불필요(§9).
- 결정 대기: push(11-02 마지막 push 뒤 로컬 커밋 13 개) · §9 어긋남 · 주석 고치기 · MAC 가림 범위(추적 파일 73 개) · mp4 2 개 git 제외 여부 · 9 기(10-26 ~ 29) · 63 개 그림 날짜 폴더 복사 · 8 · 9 월 날짜별 페이지.
- 다음 주행 전에 할 것: 새 `prep_fast.sh` 를 Jetson 에 배포(지금 Jetson `/tmp` 판은 옛 판) · `up_tools.sh` 전송 경로(스크래치패드 `tools/` 없음) 고치기.
