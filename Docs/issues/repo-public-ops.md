# 저장소 공개 운영 — 첫 페이지 영상 · 공개용 정리 · 원본/공개 두 줄 · 공개 이력의 옛 비밀번호 (6 기: 10-07 + 11-02 이어 채움)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 규칙 | 관련 문제 |
|---|---|---|---|---|
| **해결(공개 이력)** · **보류(비공개 이력 · GitHub 캐시, 사용자 결정)** — 공개 줄은 `private/publish_public.sh` 로만 운용 중 | 10-07 §9 ~ §15 · 11-02 §4 ~ §9 | [10-07 §9](../debug_log/2026-10-07/SUMMARY.md) '저장소 공개 준비(사용자: personal 공개 전환 전제, 장면은 영상 보고 선택, 한국어)' | 루트 `README.md` · `Docs/media/*.gif` · `PROJECT_OVERVIEW.md` 문구 · `.gitignore` · `private/publish_public.sh`(비공개 — 공개 줄에서 빠짐) · `navigation.launch.py mppi_viz` · `job551` `LONG_REC` · 11-02: [`.claude/settings.json`](../../.claude/settings.json) deny · 훅, [`Docs/tools/chk_commit_gate.py`](../tools/chk_commit_gate.py), [`Docs/debug_log/README.md` §8](../debug_log/README.md) | [낮은 상자 전역 기억](low-box-global-memory.md)(영상 131646 의 정체 원인 본체) · [로그 · 산출물 정리 보류](storage-housekeeping.md)(평문 비밀번호 사본 · 원본이 저장소 밖에만 있을 위험) |

**한 줄**: 10-07 오후, 사용자는 저장소를 공개하려고 휴대폰 주행 영상 6 개를 같은 시각 bag 시각화(RViz 풍)와 좌우로 붙여 보고 첫 페이지(README)에 올릴 장면을 골랐다. 그 과정에서 '지도는 상자를 보는데 계획 경로가 안 바뀐다'(131646)가 측정으로 확인됐고(계획기 · MPPI 지도 불일치 + 주기 재계획 없음 — 본체는 [낮은 상자 전역 기억](low-box-global-memory.md)), '계획하는 모습' 을 그리려 장기 주행에만 MPPI 궤적을 기록하게 했다. README 는 기능 · 절차만 남긴 짧은 판 + GIF 2 개로 줄였고, 공개에 맞지 않는 개인 계획 표현을 추적 파일에서 걷어 냈다. 저장소 운영은 **원본 줄(비공개 `personal`, 모든 것) → `private/publish_public.sh` 가 걸러 만든 공개 줄(`public` 의 `dev` · `main`)** 로 확정했다. 그런데 10-07 의 '전 이력 비밀번호 0 건' 점검은 **지금 값만** 찾아서, 05-21 부터 추적되던 `.claude/settings.local.json` 안의 **옛 비밀번호**를 놓쳤다 — 11-02 에 발견해 추적 해제 · 게이트 강화(옛 값 · 작업 트리) · 공개 이력 다시 쓰기(강제 push 1 회)로 공개 쪽은 0 이 됐다. 비공개 이력은 사용자 결정으로 그대로 두고, GitHub 가 끊긴 옛 커밋을 해시로 한동안 보여 줄 수 있는 한계는 남았다.

> 읽는 법: 10-07 의 이 묶음은 **영상 · 문서 작업**이라 `outputs/` 원문이 거의 없다(예외 [`plan_vs_box.txt`](../debug_log/2026-10-07/outputs/plan_vs_box.txt)). 렌더 · 결합 결과는 `Docs/debug_log/2026-10-07/videos/fused/`(git 제외, 이 PC 에만)에 있고, 중간 파일(`fz_*.npz` · `sc_*.npz` · `rv_*.mp4` · `lab_real.png`)은 저장소 · 그 폴더 어디에도 없다 → **원천 소실**(다시 만들려면 `bags/bag_f2d1.tgz` · `bag_f2d2.tgz`(로컬, git 제외)에서 추출부터). 11-02 수치는 그날 대화 출력을 옮긴 [`leak_scan_1102.txt`](../debug_log/2026-11-02/outputs/leak_scan_1102.txt) · [`gate_tests_1102.txt`](../debug_log/2026-11-02/outputs/gate_tests_1102.txt) · [`publish_rewrite_1102.txt`](../debug_log/2026-11-02/outputs/publish_rewrite_1102.txt)(모두 '대화 기록에서 옮김' 표시, 비밀번호 값 없음). 이 카드는 공개 줄에도 나가므로 비밀번호 · 개인 계획 문구 · 치환 목록 · 이메일 대응표의 **내용**은 적지 않는다.

## 1. 증상
- 문제가 터진 게 아니라 **사용자 요청 작업**에서 시작: "personal 공개 전환 전제, 장면은 영상 보고 선택, 한국어"([10-07 §9](../debug_log/2026-10-07/SUMMARY.md)).
- 작업 중 사용자가 본 것 두 가지:
  1. 영상 131646: "지도는 상자를 보는데 플래너가 경로를 못 고쳐 문제"(10-07 §10 제목) · "경로가 이미 그려져 있어 계획하는 모습이 안 보임"(같은 곳).
  2. "녹색 선대로 안 움직이는 것 같다"(10-07 §11 제목).
- 11-02: 다른 세션 평가를 계기로, 공개 `dev` · `main` 의 **현재 파일과 이력 4 커밋**에 옛 비밀번호가 든 `sshpass` 명령 38 줄이 있음을 확인([11-02 §6](../debug_log/2026-11-02/SUMMARY.md), [`leak_scan_1102.txt`](../debug_log/2026-11-02/outputs/leak_scan_1102.txt) '값0 public/dev 그 값을 넣거나 뺀 커밋 4 현재 트리 파일 ['.claude/settings.local.json']').

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 10-07 §9 | 원본 영상 6 개(4K, 합 2.6 GB)를 5 s 간격 요약 그림으로 보고 장면 3 개 선택 → bag 구간 추출 → 위에서 본 데이터 영상 + 자막 → 실제 영상과 좌우 결합 | ① f2d1 남서 구석 정체(130300) ② f2d2 서쪽 통로(131424) ③ f2d2 상자 ② 앞 정지(131646 끝 + 131823). 결과 `Docs/showcase/2026-10-07_{corner,corridor,box}.mp4` 각 6~7 MB · 1126×720. 남서 '위치만' 성공 구간은 촬영 없음 | 루트 README(한국어) 신설 | jobs [`job930_extract.py`](../debug_log/2026-10-07/jobs/job930_extract.py) · [`job930_run.sh`](../debug_log/2026-10-07/jobs/job930_run.sh) · [`render_sc.py`](../debug_log/2026-10-07/jobs/render_sc.py) · `cap_*.json` · [`compose_sc.sh`](../debug_log/2026-10-07/jobs/compose_sc.sh). 원본 영상 `videos/20261007_*.mp4`(git 제외). 5 s 요약 그림 · npz = **원천 소실** |
| 10-07 §9 | 시각 맞춤 | 휴대폰 파일 이름 시각(시작) = KST, Jetson epoch 1791346297 = 13:11:37 | 두 기기 모두 네트워크 시각이라 **±1~2 s 로 가정**(검증은 장면 대조뿐 — 미확인) | `job930_run.sh` 3 행 `e()` 함수 |
| 10-07 §9 | 공개 전 점검 | **모든 브랜치 이력(471 커밋)에서 Jetson 비밀번호 0 건**(`git log --all -S`) | 공개해도 됨 — ⚠ **틀림(11-02 §6)**: 지금 값만 찾았고 옛 값은 안 찾음 | 출력 원문 없음(**원천 소실**) |
| 10-07 §9.1 | 사용자: RViz 풍(회색 미지 · 흰 빈 곳 · 검은 벽, 코스트맵 청록/자홍), 쇼케이스 폴더에 넣지 말 것, 6 개 전부 융합 뒤 함께 선택 | — | `Docs/showcase/` · README 를 저장소에서 내림(→ `videos/fused/`, README 는 `README_draft.md`) | 커밋 a0dde9cf |
| 10-07 §9.2 | 6 개 전부 RViz 풍 융합: 추출 f2d1 13:02:50~13:06:30 · f2d2 13:11:35~13:19:00 → 렌더 720×720 · 10 fps → 결합 | 130300 205 s 46 MB · 131145 47 s 13 MB · 131400 10 s 3 MB · 131424 72 s 18 MB · 131646 84 s 19 MB · 131823 25 s 5 MB | 사용자 검토로 첫 페이지 결정 | [`job931_run.sh`](../debug_log/2026-10-07/jobs/job931_run.sh) · [`render_rviz.py`](../debug_log/2026-10-07/jobs/render_rviz.py) · [`fuse_all.sh`](../debug_log/2026-10-07/jobs/fuse_all.sh) → `videos/fused/fused_<HHMMSS>.mp4`(git 제외, 6 개 있음 — 11-02 확인) |
| 10-07 §10 | 사용자 검토: 첫 페이지 후보 131145 17~43 s · 130300 0~47 s. 131646 '지도는 상자를 보는데 경로가 안 바뀜' 측정 | 경로 발행 13:16:44 다음은 **13:17:58** 뿐. 로컬 상자 근처 치명 칸 13:17:25 에 4 → 13:17:39 60, 그때 남은 경로 ↔ 그 칸 **0.01~0.02 m**(차체 반폭 0.165). 재계획 경로는 전역 < 99 인 **7 칸**(x 1.29~1.45 · y −0.41~−0.31)에서 0.02 m | 계획기와 MPPI 가 다른 지도 + 주기 재계획 없음(→ [낮은 상자 전역 기억](low-box-global-memory.md)) | [`plan_vs_box.py`](../debug_log/2026-10-07/jobs/plan_vs_box.py) → [`plan_vs_box.txt`](../debug_log/2026-10-07/outputs/plan_vs_box.txt) ('계획 발행 시각:' 줄 · '전역 < 99(계획기는 통과 가능) 7 칸' 줄). 입력 `fz_f2d2.npz` = 원천 소실, 원천 bag `bags/bag_f2d2.tgz`(로컬) |
| 10-07 §10.2 | 시각화 보강: 앞 남은 경로만 · 새 경로 3 s 강조 · 직전 경로 회색 · 지나온 궤적 파랑 · `global` 인자 시 전역 내접 · 치명 주황 테두리 | 고른 두 구간 안에는 **경로 발행이 없음**(131145 17~43 s = 13:12:02~28, 발행 13:11:57 · 13:12:35 / 130300 0~47 s, 발행 13:02:56 · 13:03:56) → '계획하는 모습' 은 목표 시작 · 막힘 때만 | 130300 0~62 s 판(56 s 에 발행)도 만듦. MPPI 매 주기 예측은 bag 에 없어 못 그림 | `render_rviz.py`(10-07 판). 산출 `videos/fused/cand_A_131145_17-43s` · `cand_B_130300_0-47s` · `cand_B_130300_0-62s` · `debug_131646_global` · `debug_131823_global` |
| 10-07 §11 | 사용자: 장기 주행만 `/local_plan` · MPPI 후보 기록, 깃발 빼기, 녹색 · 파랑 선은 무엇인가 | 이 구성엔 `/local_plan` 없음. MPPI `visualize` 켜면 `/trajectories` · `/transformed_global_plan`. 선 차이(0.5 s 간격): 131145 중앙 3.3 · 90 % 5.7 · 최대 6.1 cm, 130300 0~62 s 중앙 4.2 · 90 % 9.7 · 최대 12.2 cm. 131145 구간 map→odom 보정 합 0.21 m · 한 번 최대 0.10 m | 녹색 = 전역 계획 경로, 파랑 = 실제 궤적(map→odom ∘ odom→base_link). 차이 원인 = MPPI 의 비용 합 최적화(모서리 깎기) + 보정 계단(**추정 + 기존 측정**) | [`job932_topics.sh`](../debug_log/2026-10-07/jobs/job932_topics.sh) — 출력 원문 없음(**원천 소실**). 선 차이 계산 스크립트도 저장소에 없음(**원천 소실**) |
| 10-07 §11 | 구현 `navigation.launch.py mppi_viz:=true`(기본 false): visualize true + trajectory_step 20(후보 1000 중 50) · time_step 2. 순회 prep 만 `EXTRA_NAV=mppi_viz:=true`, 러너 `LONG_REC=1` → `job551` 이 두 토픽 기록 | — | 장기 주행만 켬 — ⚠ 이후 10-12 §7.3 에서 'true' 가 포화 원인으로 판명(§6 이후) | 커밋 e3e1fe88 · [`job551_f0drive.sh`](../debug_log/2026-10-07/jobs/job551_f0drive.sh) 35 행 · [`run_f2c.sh`](../debug_log/2026-10-07/jobs/run_f2c.sh) 7 행 |
| 10-07 §12 | 첫 페이지 영상 확정(cand_A 17~43 s · cand_B 0~47 s), 소리 제거, 포스터 → 클릭 재생 | 결합 영상 11 개 모두 오디오 트랙 0(처음부터 `-an`), 원본 휴대폰 영상만 aac. 메타데이터: 원본 = Android 버전 · 시간대 태그(GPS 없음), 최종본 `-map_metadata -1`. B 제목이 62 s 판의 '출발 → W3' 로 남은 것 정정 → '출발 → B 지점' | `Docs/media/2026-10-07_start_through_door.{mp4,jpg}`(47 s, 12 MB) · `corridor_to_D.{mp4,jpg}`(26 s, 7 MB) + README | 커밋 5cf324ce. ffprobe 출력 원문 없음(**원천 소실**) |
| 10-07 §12.1 | 사용자: "README 가 장황하다 — nvblox 저장소처럼 구현한 기능과 작업 절차만, mp4 대신 가벼운 gif" | 1 차 2 배속 · 8 fps · 720 폭 = 15 · 25 MB(너무 큼) → 3 배속 · 6 fps · 폭 560 · 64 색 · 디더 없음 = 6.4 MB(15.7 s) · 3.7 MB(8.7 s) | README = 소개 한 줄 · GIF 2 · 기능 5 줄 · 절차 4 단계 · 문서 링크. mp4 · jpg 는 저장소에서 내림(`videos/fused/media_prev/` 보관) — **이미 push 된 이력엔 남음** | 커밋 99bd6c42 · [`README.md`](../../README.md) · `Docs/media/*.gif`. GIF 변환 명령 원문 없음(**원천 소실**, 인자는 SUMMARY 문장만) |
| 10-07 §13 | 사용자: PROJECT_OVERVIEW 의 개인 계획 이야기는 공개 프로젝트에 좋지 않다 → 문구 수정 | PROJECT_OVERVIEW(구분 · 범위 배너 · 변경 이력 1.4) · debug_log 08-31 · 09-02 · 09-07 · 09-18 · 10-07 · job231 주석 · NAV2_EXPLORATION_PLAN · TEST_COURSE_AND_GATES → '개인 프로젝트' · '개선 전후 비교' 등. 추적 파일 잔여 **0 건(CLAUDE.md 제외)** | CLAUDE.md 는 `.gitignore` 에 넣고 추적 해제. 과거 이력(그 문구가 든 커밋 6 개 + 옛 mp4 · 쇼케이스) 처리는 사용자 결정 대기 | 커밋 0652030d(11 파일) · 8db85b9b. 검색 출력 원문 없음(**원천 소실**) |
| 10-07 §14 | 사용자: "새 작업까지 이중 백업, public 에 안 올라가는 것(CLAUDE.md 등)도 올라가게" | — | **원본 줄** = 비공개 `personal` 의 `feature/nvblox-migration`(CLAUDE.md 다시 추적, 실명 이메일 이력 포함). **공개 줄** = `private/publish_public.sh` 가 원본에서 걸러 `public`(`indoor-rover-dev`)의 `dev` 로. `main` 반영은 `--push-main`(사용자 결정 뒤). §13 의 '과거 이력' 대기 항목은 필터 제외 목록으로 공개 쪽에서 처리 | 커밋 937d2fa6(`private/` 3 파일 · CLAUDE.md 다시 추적) · cd6d020a |
| 10-07 §15 | 공개 `main` 반영 | `bash private/publish_public.sh --push-main` → public main = dev = eec6f67 | 하루 마무리 | 실행 출력 원문 없음(**원천 소실**) |
| 10-07 ~ 10-31 | 이후 공개 push 는 같은 스크립트로 일반 push(예: [10-26](../debug_log/2026-10-26/SUMMARY.md) 머리 '공개 dev 1cef72c → e1c1104(점검 0 · 0 · 0)') | 점검 3 항목(문구 · 옛 이메일 · 비공개 경로)만 — **비밀번호 검사는 공개 스크립트에 없었음** | — | 각 날 SUMMARY push 줄 |
| 11-02 §4 | `.claude/settings.json` deny: `git push origin …` · `git push public …` · `sudo …`(Bash · PowerShell) | `git push --dry-run origin no-such-branch-xyz` → 도구가 거부 | 공개는 점검 있는 `publish_public.sh` 로만. 한계: ssh 문자열 안 `sudo` 같은 간접 실행은 못 잡음 | [11-02 §4](../debug_log/2026-11-02/SUMMARY.md) |
| 11-02 §5 | 비밀번호를 저장소 밖 `~/.config/rover_jetson/pw` 로, 커밋 게이트 훅 `chk_commit_gate.py`(PreToolUse) | 시험 5 개: 누출 → exit 2 · commit 아님 → 0 · 파일 없음 → 2 · 한글 메시지 → 0(첫 판은 stdin 을 cp949 로 읽어 JSON 이 깨지면 통과해 버리는 결함 → utf-8 로 고침) · 실세션 막음 | 커밋 전 기계적 차단 | [`gate_tests_1102.txt`](../debug_log/2026-11-02/outputs/gate_tests_1102.txt) '## §5' 절 |
| 11-02 §6 | 다른 세션 평가 → `settings.local.json` 내용 확인 | 05-21(`c8593604`)부터 추적, `sshpass -p <옛 값>` 38 줄(옛 주소 192.168.0.104), 값 한 종류 · 지금 값과 다름 → 지금 값만 보던 게이트를 통과. 공개 dev · main · 원본 모두 '그 값을 넣거나 뺀 커밋 4'. 다른 파일엔 없음 | 원인 = 개인 설정 파일 추적 + 게이트가 지금 값 하나만 봄. 조치 ①~⑥(§5 표) | [`chk_leak_scan_1102.py`](../debug_log/2026-11-02/jobs/chk_leak_scan_1102.py) → [`leak_scan_1102.txt`](../debug_log/2026-11-02/outputs/leak_scan_1102.txt) 3~6 줄. 첫 판 정규식 오결과도 같은 파일 7 줄 |
| 11-02 §6 | 게이트 둘째 판 시험 | 추적 해제 전 모의 `git commit -am` → '.claude/settings.local.json(staged, 옛 값 1), …(작업 트리, 옛 값 1)' 로 막음 · 해제 뒤 Claude 훅 0 · git 훅 0 · 임시 저장소 stage 안 한 추적 파일 → Claude 훅 2 · 터미널 `git commit -am` → 1, 커밋 수 그대로 | staged + 작업 트리 · 옛 값까지 검사가 작동 | [`gate_tests_1102.txt`](../debug_log/2026-11-02/outputs/gate_tests_1102.txt) '## §6' 절 |
| 11-02 §7 | 승인 명령 누적 정리 | `settings.local.json` allow 63 줄(PowerShell 53 · Bash 8 · Read 2, 200 자 넘는 한 번짜리 35) → 와일드카드 11 줄. 지운 줄 하나가 `SSHPASS=<값>` 형식(벤더 이미지 기본 비밀번호로 보임) — 공개 main 현재 트리 1 파일 · 이력 1 커밋, dev 이력 2 커밋 | 원인 = 승인 창 '다시 묻지 않음' 이 명령 문자열을 통째로 저장. §6 검색은 `sshpass -p` 형식만 봐서 놓침. 흔한 단어라 게이트 감시 값엔 안 넣음 | [`leak_scan_1102.txt`](../debug_log/2026-11-02/outputs/leak_scan_1102.txt) 8~13 줄. 원본 백업은 저장소 밖 |
| 11-02 §8 | 사용자 "B로 가자" → 공개 이력 다시 쓰기 | 마른 실행: 점검 0 · 0 · 0 · 0, 필터된 이력 846 커밋, settings.local 커밋 0, 남은 `SSHPASS=` 1 건은 `<PW>` 자리표시, 벤더 기본값 0. 실행 `--push-main --rewrite`: dev 7d8ed124 → 93c12242 · main eec6f67a → 93c12242(forced update). 확인: 두 가지 모두 settings.local 커밋 0 · 비밀번호 0 · 벤더값 0, 원격 가지는 dev · main 뿐 | 공개 쪽 해결. 남은 한계: GitHub 가 끊긴 옛 커밋을 해시로 한동안 보여 줄 수 있음 | [`publish_rewrite_1102.txt`](../debug_log/2026-11-02/outputs/publish_rewrite_1102.txt) · [`chk_pub_filtered_1102.sh`](../debug_log/2026-11-02/jobs/chk_pub_filtered_1102.sh) |
| 11-02 §9 | 사용자: "비공개는 냅둬라 어짜피 아무도 못보는데" | — | 비공개 `personal` 이력은 다시 쓰지 않음(옛 비밀번호 남음) — **보류(사용자 결정)** | [11-02 §9](../debug_log/2026-11-02/SUMMARY.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 131646 에서 경로가 상자 위를 지난 것은 렌더러 좌표 오류다 | `plan_vs_box.py` 로 같은 npz 에서 로컬 치명 칸(odom → map 변환)과 남은 경로 거리, 같은 칸의 전역 값을 수치로 | 로컬 치명 4 → 60 칸이 경로에서 0.01~0.02 m, 그 칸 전역 값은 치명 · 내접 · **< 99** 가 섞임(13:17:39 치명 11 · 내접 36 · < 99 13) | 기각 — 실제 지도 불일치(본체는 [낮은 상자 전역 기억](low-box-global-memory.md)) |
| 파랑 선(실제 궤적)이 녹색(계획)에서 3~12 cm 떨어지는 것은 MPPI 가 경로를 안 따르기 때문 | 0.5 s 간격 거리 · 같은 구간 map→odom 보정 크기 | 131145 중앙 3.3 cm, 보정 합 0.21 m · 한 번 최대 0.10 m | 부분 지지(MPPI 비용 합 + 보정 계단의 몫) — 두 몫의 분리는 **미확인** |
| 휴대폰 영상과 bag 시각이 ±1~2 s 안에서 맞다 | 파일 이름 시각 vs Jetson epoch, 장면 대조 | 장면 대조만 | **미확인**(측정 없음) |
| 공개 이력에 비밀번호가 없다(10-07 §9) | 11-02 §6: 추적 파일 중 `*.local.*` 내용 열기 · 값 종류별 `git log -S` | 옛 값 1 종 · 공개 두 가지 각 4 커밋 | **기각** — 10-07 점검이 지금 값만 찾았음 |
| `sshpass -p` 형식만 보면 남은 노출을 다 찾는다(11-02 §6) | §7 정리 중 지운 줄 대조 | `SSHPASS=` 형식 1 종 추가 발견 | 기각 — 형식별 검색 필요 |
| 다시 쓴 공개 이력에 노출이 없다 | 비밀번호 파일 전 줄로 `git log -p` 전체 검색 + settings.local 커밋 수 + `SSHPASS=` 앞머리 | 0 · 0 · `<PW>` 자리표시 1 · 벤더값 0 | 지지(공개 dev · main) |

## 4. 조치와 효과
| 조치 | 날짜 · § | 효과 | 한계 |
|---|---|---|---|
| README 짧은 판 + GIF 2 개(6.4 · 3.7 MB) | 10-07 §12.1 | 첫 페이지 = 실제 영상 · bag 좌우 결합(3 배속) | GIF 화질은 64 색 · 폭 560 |
| 장기 주행만 MPPI 궤적 발행 · 기록(`mppi_viz` · `LONG_REC`) | 10-07 §11 | 10-08 §3.4 에서 MPPI 후보 · 최적 궤적을 영상에 그림 | 'true' 판(마커 832 개 · 206 kB × 10 Hz)이 10-12 §7.3 에서 포화 원인 → `lite` 추가(현재 [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 133~140 행) |
| 개인 계획 표현 걷어 냄 | 10-07 §13 | 추적 파일(CLAUDE.md · `private/` 제외) 잔여 0 — 11-02 이 카드 작성 때 다시 셈: `git grep -l` 0 파일 | 원본 이력엔 남음 — 공개 줄은 치환 목록으로 이력 · 메시지까지 바꿈 |
| 원본/공개 두 줄 · `publish_public.sh` | 10-07 §14 | 같은 입력 · 같은 옵션이면 같은 해시 → 일반 push. 점검(문구 · 옛 이메일 · 비공개 경로)과 '공개 dev 가 조상인가' 확인, 아니면 중단 | 10-07 판엔 비밀번호 검사 없음(11-02 §8 에 추가) |
| deny(origin · public 직접 push · sudo) | 11-02 §4 | 점검 없는 직접 push 를 도구가 거부 | 스크립트 안 push · ssh 안 sudo 는 못 잡음(의도 · 한계) |
| 커밋 게이트(Claude 훅 + git pre-commit, 지금 값 · 옛 값, staged + 작업 트리) | 11-02 §5 · §6 | 시험 전부 막음/통과 기대대로 | git 훅은 이 PC 만(`.git/hooks` 는 커밋 안 됨) · 비밀번호 파일이 없으면 막음 |
| `settings.local.json` 추적 해제 + `.gitignore` · allow 63 → 11 줄 | 11-02 §6 · §7 | 새 승인 명령이 저장소로 안 들어감 | 비공개 이력엔 남음 |
| 공개 이력 다시 쓰기(제외 목록에 settings.local · 점검 n4 · `--rewrite`) | 11-02 §8 | 공개 dev · main = 93c12242, 노출 0 | 끊긴 옛 커밋의 해시 접근(GitHub 지원 요청 전엔 남을 수 있음) · 옛 값을 다른 기기 · 계정에서 쓰는지는 사용자 몫(11-02 §6 '1d') |

### 4.1 지금 코드 확인 (11-02, 이 카드 작성 때 읽기만)
- [`.gitignore`](../../.gitignore) 50 행 `Docs/debug_log/*/bags/` · 52 행 `Docs/debug_log/*/videos/` · 56 행 `.claude/settings.local.json`. `CLAUDE.md` 는 ignore 에 없음(§14 대로 원본 줄에서 추적, 공개 줄은 필터 제외). `git ls-files .claude` = `settings.json` 하나.
- [`.claude/settings.json`](../../.claude/settings.json) 7~28 행 deny 20 줄(Bash · PowerShell 각 origin 4 · public 4 · sudo 2), 31~51 행 PreToolUse 훅 2 개(Bash · PowerShell → `chk_commit_gate.py`, timeout 60). 3~6 행 allow 2 줄은 옛 다른 경로(`c:/Workspace/...icm20948`) 읽기 규칙 — 이 문제와 무관한 잔재.
- [`Docs/tools/chk_commit_gate.py`](../tools/chk_commit_gate.py) 21 행 `git … commit` 정규식 · 25~30 행 비밀번호 파일(없거나 비면 막음) · 32~40 행 값마다 `git grep --cached -l -F` 와 `git grep -l -F` · 41~43 행 막음(exit 2 / git 훅 1) · 45~49 행 규약 경고 개수 알림. `.git/hooks/pre-commit`(이 PC) 3 행이 `--git-hook` 으로 부름.
- `private/publish_public.sh`(35 줄, 비공개) 13~15 행 filter-repo 제외(CLAUDE.md · `private` · `Docs/showcase` · `.claude/settings.local.json` · `Docs/media/*.mp4` · `*.jpg`) + 치환 · 메일 대응 · 20 행 n3 · 22~23 행 n4(파일 없으면 중단) · 24 행 0000 아니면 중단 · 27~29 행 `--rewrite` 는 `--force-with-lease` · 31~32 행 조상 확인.

## 5. 내 실수 · 기록 사이 어긋남
1. **10-07 §9 '모든 브랜치 이력(471 커밋)에서 Jetson 비밀번호 0 건'** — 하려 한 것: 공개 전 비밀번호 확인(`git log --all -S <지금 값>`). 본 것: 0 건(출력 원문 없음, **원천 소실**). 처음 추론: 이력이 깨끗하다. 의심한 이유: 11-02 다른 세션 평가가 `settings.local.json` 을 짚음. 판별: [`chk_leak_scan_1102.py`](../debug_log/2026-11-02/jobs/chk_leak_scan_1102.py) — 스크립트 핵심 `vals = set(re.findall(r"sshpass -p (\S+) (?:ssh|scp) ", s))` 뒤 값마다 `git log <가지> -S v` · `git grep -l -F v <가지>`. 나온 결과 '서로 다른 값 1 [('다름', …)]' · '값0 public/dev 그 값을 넣거나 뺀 커밋 4 현재 트리 파일 ['.claude/settings.local.json']'([`leak_scan_1102.txt`](../debug_log/2026-11-02/outputs/leak_scan_1102.txt) 3~4 줄). 결론: 10-07 점검은 **지금 값 하나**만 봤다. 11-02 §6 의 실수 칸은 §4 에서 이 파일을 안 연 것과 게이트 한계만 적었고, **10-07 §9 의 '0 건' 문장과의 연결은 기록에 없다**(이 카드에서 처음 잇는다). **다음에 알아보는 법**: '비밀번호 0 건' 은 어느 값 · 어느 형식으로 찾았는지와 함께 쓴다 · 비밀번호를 바꾼 적이 있으면 옛 값도 검색 목록에 넣는다 · 추적 파일 중 `*.local.*` 는 내용을 연다.
2. **10-07 §13 '추적 파일 잔여 0 건(CLAUDE.md 제외)'** — 같은 시각 `settings.local.json` 이 추적 중이었다. 그 파일에 개인 계획 문구가 있었는지는 기록이 없다(**미확인**). 공개 줄은 치환 목록이 이력 전체에 적용되므로 결과엔 영향이 없었다고 보이나, 이 '0 건' 도 검색 명령 · 출력이 없다(**원천 소실**).
3. **10-07 §11 의 부담 판단** — 'trajectory_step 20 으로 간격을 넓혀 부담을 줄임' 이라 적었지만 메시지 크기 · 대역폭은 재지 않았다. 10-12 §7.3 에서 그 설정이 206 kB × 10 Hz ≈ 2 MB/s 로 포화(현재 `navigation.launch.py` 133~135 행 주석). **다음에 알아보는 법**: 시각화 토픽을 켤 때는 `ros2 topic bw` 한 번으로 크기를 재고 적는다.
4. **10-07 §9 `job930_run.sh` 가 상자 장면만 남김** — 지금 파일 4 행은 `sc_box.npz` 하나만 추출한다. 다른 두 장면(corner · corridor)의 추출 줄은 같은 파일을 고쳐 쓰며 사라진 것으로 보인다(**추정**). 장면별 시각 인자는 [`compose_sc.sh`](../debug_log/2026-10-07/jobs/compose_sc.sh) 5~7 행 주석에 남음.
5. **'이미 push 된 이력엔 남음'(10-07 §12.1 · §13)의 처리** — §14 에서 공개 줄 필터(`Docs/showcase` · `Docs/media/*.mp4` · `*.jpg`)로 공개 쪽은 해결됐는데 SUMMARY 에는 '사용자 결정 대기' 가 닫혔다는 문장이 따로 없다. §14 본문 '옛 쇼케이스/mp4 제외' 가 그 답이다.
6. **10-07 §14 '앞선 공개본(5754c26)은 이 규칙으로 만든 것과 같아야 함 → 첫 실행에서 확인'** — 확인 결과가 기록에 없다. §15 실행이 중단 없이 끝났으므로 조상 확인(스크립트 31~32 행)은 통과했다고 보이나(**추정**), 그때 5754c26 이 공개 `dev` 였는지 `main` 이었는지도 적혀 있지 않다.

## 6. 남은 것
- 비공개 `personal` 이력의 옛 비밀번호(사용자 결정으로 유지, 11-02 §9).
- GitHub 의 끊긴 옛 커밋 해시 접근 — 완전 삭제는 GitHub 지원 요청(11-02 §8, 미실행).
- 옛 값 · 벤더 기본값을 다른 기기 · 계정에서 쓰는지(사용자 확인, 11-02 §6 · §7).
- 러너 스크립트의 평문 비밀번호 사본 문제는 [로그 · 산출물 정리 보류](storage-housekeeping.md) §6 에 이어짐(지금은 러너 · 저장소 밖 파일에서 읽음 — README §8).
- 10-07 영상 중간 파일(npz · 데이터 영상) 원천 소실 — 다시 만들 때는 `bags/` 에서 추출부터. 지금 영상 도구는 `Docs/tools/fig_drive_video.py`(10-23).

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| 영상 6 개 | 휴대폰 4K 세로, 130300 · 131145 · 131400 · 131424 · 131646 · 131823 | `2026-10-07/videos/`(git 제외, 합 2.6 GB) |
| f2d1 · f2d2 bag | 영상과 같은 시각 순회 기록 | `2026-10-07/bags/bag_f2d1.tgz` · `bag_f2d2.tgz`(git 제외) |
| `job930_extract.py` · `job930_run.sh` · `job931_run.sh` | bag 구간 → npz(Jetson) | `2026-10-07/jobs/` → npz 원천 소실 |
| `render_sc.py` · `cap_*.json` · `compose_sc.sh` | 첫 쇼케이스(위에서 본 그림 + 자막) · 좌우 결합 | `2026-10-07/jobs/` → `videos/fused/2026-10-07_{corner,corridor,box}.mp4` |
| `render_rviz.py` · `fuse_all.sh` | RViz 풍 렌더 · 6 개 융합 | `2026-10-07/jobs/` → `videos/fused/fused_*.mp4` · `cand_*` · `debug_*` |
| `plan_vs_box.py` | 131646 로컬 치명 칸 ↔ 경로 · 전역 값 | `2026-10-07/jobs/` → [`outputs/plan_vs_box.txt`](../debug_log/2026-10-07/outputs/plan_vs_box.txt) |
| `job932_topics.sh` | 컨트롤러 시각화 토픽 · 파라미터 확인 | `2026-10-07/jobs/` → 출력 원문 없음 |
| `publish_public.sh` | 원본 → 공개 줄 | `private/`(비공개) |
| `chk_leak_scan_1102.py` · `up_pw_old_1102.py` · `chk_pub_filtered_1102.sh` | 노출 검색 · 옛 값 보관 · 필터 이력 `SSHPASS=` 앞머리 | `2026-11-02/jobs/` → [`leak_scan_1102.txt`](../debug_log/2026-11-02/outputs/leak_scan_1102.txt) · [`publish_rewrite_1102.txt`](../debug_log/2026-11-02/outputs/publish_rewrite_1102.txt) |
| `chk_commit_gate.py` | 커밋 게이트 | `Docs/tools/` → [`gate_tests_1102.txt`](../debug_log/2026-11-02/outputs/gate_tests_1102.txt) |

## 8. 도구 해설

### job930_extract.py — bag 구간 → 시각화용 npz (10-07 §9 · §9.2, Jetson, 읽기만)
- 부른 형태: `python3 /tmp/job930_extract.py <bag> <TA epoch> <TB epoch> <out.npz>` — `job930_run.sh`(상자 13:16:38~13:18:55 → `sc_box.npz`) · `job931_run.sh`(f2d1 13:02:50~13:06:30 → `fz_f2d1.npz`, f2d2 13:11:35~13:19:00 → `fz_f2d2.npz`). 두 러너의 `e()` 는 KST 시각을 'epoch 1791346297 = 13:11:37' 기준으로 바꾼다.
- 왜: 영상과 같은 시각의 로봇 상태를 PC 에서 그리려고(job912 변형 — 머리말).
- 하는 일: rosbag2 sqlite3 를 차례로 읽어 ① 첫 `/map` 한 장 ② 구간 안 `/tf` 의 map→odom · odom→base_link(x, y, yaw) ③ `/odometry/ekf_a`(그림자 A) ④ `/cmd_vel` ⑤ `/plan` 전부 ⑥ 전역 코스트맵 2 s 간격 ⑦ 로컬 코스트맵 0.5 s 간격 ⑧ `/scan` 0.2 s 간격. map 위 자세 = map→odom ∘ odom→base_link(직전 표본, 39 행 odom→base_link 3 개 중 1 개). 그림자 A 는 같은 map→odom 으로 올림(같은 보정을 받았다고 가정 — 43 행).
- 출력: 화면 한 줄 '궤적 · A · plan · 전역 · 로컬 · 스캔 · cmd 개수' + npz. **원천 소실**(Jetson `/tmp`, 출력 줄도 저장 안 함).
- 결함: 머리말은 '로컬 1 s · 스캔 1 s' 라 적었지만 코드는 로컬 0.5 s(31 행) · 스캔 0.2 s(33 행). `/map` 은 구간 밖에서도 첫 장만.
- 계보: job912/913(10-07 §2 분석용) → 이것 → 10-08 `extract_pc.py`(PC 판, `/trajectories` 포함) → 10-23 `Docs/tools/fig_drive_video.py`. 지금 다시: 쓸 수 있음(sqlite3 bag 한정).

### render_sc.py + cap_*.json — 첫 쇼케이스 데이터 영상 (10-07 §9, PC)
- 부른 형태: `render_sc.py <npz> <out.mp4> <시작KST> <길이s> <제목> <자막json>`(머리말). 실제 호출 인자 원문 없음(**원천 소실**).
- 하는 일(머리말 기준): matplotlib 720×720 · 10 fps, 배경 저장 지도 · 전역 코스트맵 고비용 · 로컬 치명 칸(odom → map 변환) · 라이다 점 · 전역 경로 점선 · 지나온 궤적 · 차체 0.51×0.33 m · 아래 v · ω 막대. 자막 json = `[["HH:MM:SS", "문구"], …]`, 다음 자막 전까지 표시(상자 5 · 구석 4 · 통로 2 줄).
- 쓰인 곳: §9 의 `Docs/showcase/` 3 개 → §9.1 에서 사용자가 형식을 바꿔 내림. 지금 다시: 쓸 수 있으나 `render_rviz.py` 로 대체됨.

### compose_sc.sh · fuse_all.sh — 실제 영상과 좌우 결합 (10-07 §9 · §9.2, PC Git Bash ffmpeg)
- 하는 일: 원본(세로 4K)을 `fps=30,scale=406:720,setsar=1 -an`(소리 제거) 으로 먼저 줄인 뒤 `lab_real.png` 라벨을 overlay, 데이터 영상을 `fps=30` 으로 맞춰 `hstack` → libx264 · `+faststart`. compose 는 구간(`-ss` · `-t`: 130300 130 s 부터 75 s · 131424 0 s 부터 72 s · 131646 44 s 부터 40 s), fuse_all 은 6 개 전체.
- 왜 두 단계: 한 필터 그래프로 하면 'hstack 입력 높이 0' 오류(fuse_all 2 행 주석). Git Bash ffmpeg 의 drawtext 는 fontconfig 로 죽어 라벨을 PNG 로(compose 2 행 주석).
- 결함: `lab_real.png` · `data_*.mp4` · `rv_*.mp4` 는 작업 폴더에만 있었다(**원천 소실**) — 스크립트만으로는 재현 안 됨. 지금 다시: 입력을 다시 만들면 쓸 수 있음.

### render_rviz.py — RViz 풍 렌더 (10-07 §9.2 · §10.2 · §11, PC)
- 부른 형태: `render_rviz.py <npz> <out.mp4> <시작KST> <길이s> <라벨> [global]`. 실제 호출 인자 원문 없음.
- 하는 일: 4 m × 4 m 창(1 px = 5.6 mm), 화면 위 = 로버 앞. 픽셀마다 map 좌표 → 저장 지도(미지 160 회색 · < 50 흰색 · ≥ 50 검정) → 로컬 코스트맵은 map→odom 역변환으로 odom 격자 조회, 팔레트 1~98 파랑→빨강 · 99 청록 · 100 자홍 · 알파 0.7 → 1 m 격자 → (`global`) 전역 ≥ 99 칸 주황 테두리(±2.9 m 안) → 지나온 궤적 파랑 → 직전 경로 회색(6 s 안) · 새 경로 3 s 굵은 밝은 초록 + '새 경로 계획 HH:MM:SS' · 그 뒤 초록 → 라이다 점 빨강(라이다 x 0.152 · yaw π−0.04677) → footprint 초록(x −0.248~+0.262 · y ±0.165) · 라이다 보라 원통 · TF 이름 → 위 띠 라벨 · KST, 아래 띠 지령 v · ω · map 자세. 프레임을 ffmpeg stdin 으로(crf 20).
- 결함: 시각 기준 `E0 = 1791346297`(10-07 13:11:37)이 고정이라 **다른 날 bag 에서 하루 어긋남** — 10-08 §3.4 에서 bag 시각에서 날짜를 읽게 고친 판이 `2026-10-08/jobs/render_rviz.py`. 데크 yaw · 차체 치수가 코드에 직접 들어 있음(재측정 시 같이 고쳐야).
- 계보: render_sc → 이것(10-07) → 10-08 판(MPPI 후보 · 최적 궤적) → `Docs/tools/fig_drive_video.py`(10-23 재설계).

### plan_vs_box.py — 131646 지도 불일치 측정 (10-07 §10.1, PC)
- 부른 형태: 인자 없음, 작업 폴더의 `fz_f2d2.npz` 를 읽음(**원천 소실**).
- 하는 일: 경로 발행 시각 전부 출력 → 13:17:07~13:18:57 의 로컬 코스트맵을 4 개마다(≈ 2 s) — 치명(≥ 100) 칸을 map 으로 옮겨 상자 영역(x 1.0~1.8 · y −0.6~0.25)만 고르고, 그때 경로 중 로버 앞 남은 부분과의 최소 거리, 같은 칸의 전역 값(치명 · 내접 99 · < 99) 개수 → 13:18:01 한 장에서 전역 값별 칸 범위와 새 경로(13:17:58)까지 최소 거리, 새 경로가 x 0.9~1.8 에서 지나는 y 범위.
- 나온 결과(발췌): '13:17:39 … 로컬 상자 근처 치명  60 | 남은 경로 ↔ 그 칸 최소 0.01 m' · '전역 < 99(계획기는 통과 가능) 7 칸: x 1.29~1.45 · y -0.41~-0.31 | 새 경로(13:17:58)까지 최소 0.02 m' · '새 경로가 x 0.9~1.8 에서 지나는 y: -0.31 ~ -0.20'([`plan_vs_box.txt`](../debug_log/2026-10-07/outputs/plan_vs_box.txt)).
- 결함: `at()` 이 `searchsorted` 를 −1 없이 써 **다음** 표본을 집음(≤ 표본 간격 오차) · 전역은 2 s 간격 표본이라 최대 2 s 묵은 값 · 전역 인덱스 범위 검사 없음. 판정(불일치 존재)에는 영향 작다고 봄(**추정**).
- 쓰인 곳: §10.1 결론 → [낮은 상자 전역 기억](low-box-global-memory.md).

### job932_topics.sh — 시각화 토픽 확인 (10-07 §11, Jetson, 읽기만)
- 하는 일: `ros2 topic list | grep -iE "local_plan|trajector|transformed|optimal|received_global"` · `ros2 param list /controller_server | grep -iE "visualiz|Visualizer|publish"`. 출력 원문 없음(**원천 소실**) — 결론 '`/local_plan` 없음' 은 SUMMARY 문장만. 주의: 이 스크립트 실행 자체가 DDS 참여자를 만든다(주행 직전 금지 규칙).

### mppi_viz · LONG_REC — 장기 주행 MPPI 궤적 기록 (10-07 §11, launch 인자)
- 지금 코드: [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 130~135 행 근거 주석(10-07 §11 · 10-12 §7.3) · 137~140 행 `'1','true','yes','lite'` 면 `visualize` True, `lite` = trajectory_step 100 · time_step 4, 그 밖 = 20 · 2 · 205~206 행 인자(기본 false). 순회 prep 은 지금 `Docs/tools/prep_patrol.sh` 9 행 `VIZ`(lite|true|off).
- 기록: [`job551_f0drive.sh`](../debug_log/2026-10-07/jobs/job551_f0drive.sh) 35 행 `LONG_REC=1` 이면 `/trajectories /transformed_global_plan` 추가, [`run_f2c.sh`](../debug_log/2026-10-07/jobs/run_f2c.sh) 7 행이 기본 `LONG_REC=1`.
- 결함 · 계보: 10-07 판 'true' 는 10-12 §7.3 에서 포화(마커 832 개 · 206 kB × 10 Hz) → `lite`(마커 112 개, 계산상 ≈ 28 kB) 추가, 10-12 §12.2 f2l1 3/3 포화 없음.

### publish_public.sh — 원본 → 공개 줄 (10-07 §14 · 11-02 §8, PC, 비공개 파일)
- 부른 형태: `bash private/publish_public.sh [--push-main] [--rewrite]`(5~6 행). 기본은 `dev` 만.
- 하는 일: ① 원본 `feature/nvblox-migration` 을 임시 폴더에 단일 가지로 clone ② `git filter-repo --invert-paths` 로 CLAUDE.md · `private` · `Docs/showcase` · `.claude/settings.local.json`(11-02 추가) · `Docs/media/*.mp4` · `*.jpg` 를 **전 이력에서** 빼고, 치환 목록으로 파일 · 커밋 메시지의 개인 계획 표현을 바꾸고, 메일 대응표로 작성자 이메일을 익명화(이름 유지) ③ 가지 이름 `dev` ④ 공개 전 점검 n1 문구 · n2 옛 이메일 · n3 비공개 경로 · **n4 비밀번호**(저장소 밖 비밀번호 파일의 모든 줄로 `git log -p --all` 검색, 값 출력 없음, 파일 없으면 중단 — 11-02 추가) — 하나라도 0 이 아니면 중단 ⑤ 일반 모드는 '공개 dev 가 새 결과의 조상인가' 확인 뒤 push, `--rewrite` 는 `--force-with-lease`(사용자 결정 때만).
- 왜 이 방식: filter-repo 는 같은 입력 · 옵션이면 같은 해시 → 평소 공개 push 가 새 커밋만 덧붙는 일반 push(3~4 행 주석). 옵션 · 치환 목록 · 대응표를 바꾸면 해시가 바뀌어 일반 push 가 거부됨(7 행) — 11-02 의 강제 push 1 회가 그 경우.
- 출력: '점검: 문구 N · 옛 이메일 N · 비공개 경로 N · 비밀번호 N' · '공개 dev = <해시> (원본 <해시>)'. 10-07 · 10-26 등 일반 실행 출력은 SUMMARY 한 줄씩, 11-02 는 [`publish_rewrite_1102.txt`](../debug_log/2026-11-02/outputs/publish_rewrite_1102.txt).
- 결함: 10-07 ~ 11-02 판엔 n4 가 없었다(§5 실수 1). 공개 줄에서 빠지는 파일이라 공개 저장소만 보는 사람은 이 과정을 못 본다(이 카드가 대신 설명). 지금 다시: 그대로 씀(README §8 push 3 단계).

### chk_leak_scan_1102.py · up_pw_old_1102.py · chk_pub_filtered_1102.sh (11-02 §6 · §8, PC, 값 출력 없음)
- `chk_leak_scan_1102.py`: `settings.local.json` 에서 `sshpass -p (\S+) (?:ssh|scp) ` 값 종류를 뽑아 지금 값과 같은지(길이만 표시) · 공개 dev/main · 원본에서 `git log -S` 커밋 수 · `git grep` 현재 트리 파일. 첫 판 정규식(1 · 3 글자 조각까지 잡음)은 48 커밋 · 수십 파일이 걸린 **틀린 결과로 버림**([`leak_scan_1102.txt`](../debug_log/2026-11-02/outputs/leak_scan_1102.txt) 7 줄). 지금 다시: 로컬 `settings.local.json` 을 11-02 §7 에 정리해 값이 없으므로 같은 결과는 안 나옴.
- `up_pw_old_1102.py`: 같은 정규식으로 옛 값을 저장소 밖 비밀번호 파일 둘째 줄부터 더함(첫 줄 = 지금 값 유지). 출력 '줄 수 N'.
- `chk_pub_filtered_1102.sh`: 마른 실행 끝에서 필터된 이력의 `SSHPASS=` 뒤 세 글자까지만 세어 자리표시(`<`)인지 확인. 벤더 기본값 검색어는 공개 파일에 안 쓰려 뺐고 그날 대화에서 따로 셈(머리말).

### chk_commit_gate.py — 커밋 게이트 (11-02 §5 · §6, PC)
- 부른 형태: ① Claude PreToolUse 훅(stdin 훅 JSON) ② `.git/hooks/pre-commit` 에서 `--git-hook`.
- 하는 일: ① 모드는 명령에 `git … commit` 이 있을 때만(21 행), stdin 을 utf-8 로 읽고 JSON 이 깨지면 원문에서 찾음(18~20 행 — 첫 판 cp949 결함의 수정) → 비밀번호 파일 모든 줄(없거나 비면 막음) → 값마다 staged(`git grep --cached`) · 추적 작업 트리(`git grep`) → 걸리면 '파일(staged|작업 트리, 지금 값|옛 값 N)' 만 출력하고 막음 → 통과면 `chk_record_rules.py` 경고 개수를 systemMessage 로.
- 출력 · 결과: [`gate_tests_1102.txt`](../debug_log/2026-11-02/outputs/gate_tests_1102.txt). 결함: git 훅은 이 PC 만(새 clone 은 README §8 한 줄로 재설치) · 벤더 기본값 같은 흔한 단어는 오탐 때문에 감시 안 함(11-02 §7). 지금 다시: 상시 작동.

## 9. 용어
- **원본 줄 / 공개 줄**: 원본 = 비공개 `personal` 저장소의 작업 가지(모든 파일 · 실명 작성자). 공개 = 원본을 `publish_public.sh` 로 걸러 만든 `public` 저장소의 `dev`(·`main`). 작업 · 커밋은 원본에서만.
- **git filter-repo**: 이력 전체를 다시 써 파일을 빼거나(`--invert-paths --path`) 내용 · 메시지를 바꾸고(`--replace-text` · `--replace-message`) 작성자를 바꾸는(`--mailmap`) 도구. 입력 · 옵션이 같으면 결과 해시도 같다.
- **강제 push(`--force-with-lease`)**: 원격 가지를 내 결과로 덮되, 원격이 내가 마지막에 본 해시일 때만 덮는 안전판. 옛 커밋은 참조가 끊길 뿐 GitHub 에 한동안 남을 수 있다.
- **PreToolUse 훅 · deny**: Claude Code 가 도구 실행 직전에 부르는 명령(여기선 커밋 게이트)과, 명령 문자열 패턴으로 실행 자체를 거부하는 규칙(`.claude/settings.json`).
- **`settings.local.json`**: Claude Code 승인 창에서 '다시 묻지 않음' 을 고르면 그 명령 문자열이 통째로 쌓이는 개인 설정 파일. 비밀번호가 든 명령을 승인하면 비밀번호도 저장된다 — 그래서 추적 금지.
- **마른 실행(dry run)**: push 직전까지만 돌려 점검 · 결과를 보고 멈추는 실행.
- **RViz 풍 색**: 지도(미지 회색 · 빈 곳 흰색 · 벽 검정), 코스트맵(1~98 파랑→빨강, 99 내접 청록, 100 치명 자홍).
