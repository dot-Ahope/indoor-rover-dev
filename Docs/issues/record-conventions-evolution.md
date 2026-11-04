# 기록 규칙의 진화 — 큰 bag 수명 · 실수 칸 형식 · 추론별 데이터 위치 · 영상 도구 (8 시기: 10-19 ~ 10-23 · 9 기 10-26 ~ 10-29 이어 채움: 실제 촬영 합본 · 폴더 정리 · 문제 대장 시작)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 규칙 | 관련 문제 |
|---|---|---|---|---|
| **해결(규칙 확정)** — 네 규칙 모두 사용자 결정으로 정해져 지금은 [README](../debug_log/README.md) §2.3 · §6 과 [`Docs/tools/README.md`](../tools/README.md) 46 행에 있다(11-02 재작성 때 CLAUDE.md 에서 옮김). **적용 결함 남음**: 10-21 · 10-22 · 10-23 `TOOLS.md` 없음 · '`git` 제외' 라 적힌 mp4 2 개(≈ 50 MB)가 실제로는 추적됨 · 큰 bag 정리(Jetson `~/bags` 약 10 GB, 10-20 §10 목록)는 사용자 확인 대기(**보류**) | 10-19 §18 ~ 10-23 §20.7 · (9 기) 10-26 §16 ~ §21 · 10-29 §6 · §7 — 9 기에 새 규칙은 없고, 영상 합본 · 폴더 정리 · 문제 대장이 기존 규칙 위에서 생김. 10-26 TOOLS.md 사후 작성 · 10-30 작업이 10-29 SUMMARY 에 들어간 것이 새 어긋남(§3 · §5) | [10-19 §18](../debug_log/2026-10-19/SUMMARY.md) 사용자 "이렇게 큰 bag 는 실험 후, 중요 정보 기록 및 시각화만 시킨 후, 삭제하는 것이 좋을 것 같다" | 10-21 CLAUDE.md 커밋 `3f504e12`(실수 칸) · `426a08c3`(데이터 칸) → 11-02 README(커밋 `203461b4`) · 10-23 [`Docs/tools/fig_drive_video.py`](../tools/fig_drive_video.py)(커밋 `f433c4ef`) · [`Docs/tools/README.md`](../tools/README.md) 46 행 | [저장 공간 · 정리 보류](storage-housekeeping.md)(09-18 'GB 단위가 아니면 정리 뒤로' 의 다음 단계) · [주행 전 검사와 운용 사고](drive-ops-1019-1023.md)(같은 시기 휘발 위치 소실) · [빠른 prep](prep-fast-startup.md)(`/tmp/logkeep` — 휘발) · [저장소 공개 운영](repo-public-ops.md)(추적된 mp4 는 공개 쪽에도 나갈 수 있음) · [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md) · [경로 추종 · 재계획 B0](path-tracking-replan-b0.md)(영상 도구를 쓴 분석) |

> 병합 여부: 이 카드는 '기록 · 보관 방식' 규칙만 다룬다. 같은 시기의 운용 사고(파일 소실 · prep 실패)는 [주행 전 검사와 운용 사고](drive-ops-1019-1023.md)에 두었다 — 원인(사람 규칙 vs 시스템 사고)이 달라 나눔.

**한 줄**: 8 시기에 기록 규칙이 넷 생겼다. ① **큰 bag 수명**(10-19 §18 → §18.1 정정): IR bag 이 18.4 MB/s(4 분 ≈ 4 GB)라 처음엔 '기록 · 시각화 뒤 삭제' 로 정했다가, 사용자가 곧 '영상으로 보여 준 뒤 내가 짚는 부분을 분석하고, 확인 받고 지운다' 로 고쳤다. ② **실수 칸 형식**(10-20 §11): 사용자가 '같은 실수를 다시 했을 때 알아볼 수 있게 — 본 것 · 추론 · 결론 · 알아보는 법' 을 요구해, 측정 실수 두 건을 하려 한 것 → 본 것 → 처음 추론 → 의심한 이유 → 판별 → 결론 → 다음에 알아보는 법으로 다시 썼고 이것이 규약 본보기가 됐다. ③ **추론별 데이터 위치**(10-21 §23): '어떤 로그에 그 추론의 데이터가 있는지' 를 적게 했고, 휘발 위치(Jetson `/tmp` · PC 스크래치패드)에만 있던 것은 그날 `outputs/` · `bags/` 로 옮기거나 '원천 소실' 로 적는다. ④ **영상 도구 재설계**(10-23 §20.6): 사용자가 '디자인이 별로' 라 해 화면만 새로 만든 `Docs/tools/fig_drive_video.py` 가 영상 기본 도구가 됐다(바로 다음 § 에서 '어떤 경로를 그리는가' 실수 1 건을 고침). 규칙 자체는 정착했지만, 이 시기의 기록 몇 곳은 자신이 적은 규칙과 맞지 않는다(§5).

## 1. 증상 (규칙이 생긴 계기)
- **10-19 §16 · §18 — IR bag 의 크기(계산 = 실측)**: IR 640×480 mono8 = 307 200 B/장 × 좌우 × 30 Hz(켬 · 끔 모두) ≈ 18.4 MB/s, S3 86 s 의 IR 2549 × 2 장 = 1.46 GiB ≈ bag 1.5 GiB — 깊이 bag(0.58 MB/s)의 약 30 배. 그날 f2y1 IR bag `/home/jetson/bags/bag_f2y1_ir` **4.0 GiB / 230 s**([10-19 §19.1](../debug_log/2026-10-19/SUMMARY.md), 원문 [`run_f2y1.txt`](../debug_log/2026-10-19/outputs/run_f2y1.txt)).
- **10-20 §11 — 측정 실수 두 건**: §7.3b '공유메모리 전용' 시험이 수신 0 · 오류 0 을 냈고(시험 설계 결함 — 한쪽만 transport 를 바꾸면 발견이 안 됨), §9.3 측정 노드가 시스템 전체 `RcvbufErrors` 를 오염시켜 S 520/s 라는 값을 만들었다. 그날 정정 6 건이 대부분 한 줄이었다(§10 '정정한 내 오류' 목록).
- **10-21 §23 — 데이터가 어디 있는지 모름**: 사용자 "추론 정리할 때, 어떤 로그에 해당 추론에 사용된 데이터들이 저장되어 있는지도 적어달라." 확인해 보니 확인 출력 4 건이 파일로 안 남았고, bag 10 개가 스크래치패드에만 있었고, nav2 사건 원천(Jetson `/tmp/nav2.log`)은 이미 prep 이 덮었다.
- **10-23 §20.6 — 영상 화면**: 사용자 "동영상 시각화에 사용한 파이썬 코드의 디자인이 별로".

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-19 §18 | 사용자 '큰 bag 은 기록 · 시각화 뒤 삭제' → 규칙 1 판 · 대상 목록 | Jetson `~/bags`: `s2_flash30rec` 0.45 GB · `s2_comp30rec` 1.5 GB · `_b` 1.5 GB | '작은 파생 자료와 그림을 outputs · figures 에 남기고, 지운 경로 · 크기를 적은 뒤 삭제' | [10-19 §18](../debug_log/2026-10-19/SUMMARY.md) |
| 10-19 §18(15:2x) | 사용자 승인 → `rm_s2_flash.sh` 로 `s2_flash30rec` 삭제 | 448 MB · 메시지 30373 · IR2 729 장(§16.1 표와 일치), 디스크 146 GB 남음 | 삭제 전 대상 확인 → 삭제 → 남은 bag 목록 순서 | [`rm_s2_flash.sh`](../debug_log/2026-10-19/jobs/rm_s2_flash.sh)(출력 파일 없음 — [TOOLS 25 행](../debug_log/2026-10-19/TOOLS.md) · SUMMARY 서술이 전부) |
| 10-19 §18.1 | 사용자 '바로 삭제하지 말고, 영상 등으로 시각화한 후, 내가 말하는 부분 등을 분석 후 bag 정리' | — | ✘ §18 의 '기록 · 시각화 후 삭제' → **시각화 → 사용자가 짚는 부분 분석 → 기록 → 사용자 확인 뒤 삭제**. '내가 분석이 끝났다고 판단해 지우지 않는다'. 대상 `bag_f2y1_ir` 4.0 GB · `s2_comp30rec` · `_b` | [10-19 §18.1](../debug_log/2026-10-19/SUMMARY.md)(파일에서는 §19.1 뒤에 있음 — 나중에 쓴 정정) |
| 10-19 §20 · §21 | 큰 bag 을 영상으로(규칙 첫 적용) | `figures/f2y1_ir_drive.mp4` 28.6 MB · 230 s, 상자 확대 판 추가 | 사용자가 '복귀 때 상자 칸' 을 짚음 → §22 분석 | `jobs/fig_ir_extract.py` · `jobs/fig_ir_drive_video.py` |
| 10-19 §26 | 마무리 정리 페이지 | 게시 + 사본 `figures/day_summary_1019.html` | 큰 bag 정리는 '§18.1 순서로' 다음 날 | [10-19 §26](../debug_log/2026-10-19/SUMMARY.md) |
| 10-20 §10 | 마무리 — 큰 bag 정리 대기 목록 | `bag_f2y1_ir` 4.0 GB · `bag_f2z1_ir` · `bag_f2z2_ir` ≈ 1.9 GB 씩 · `vslam/f2y1_split` · `f2z1_split` · `f2z2_split` · `s2_comp30rec(_b)` 1.5 GB 씩 · 작은 시험 bag 수십 MB | '사용자 확인 뒤' — **이후 기록에 처리 없음**(이 카드에서 10-21 ~ 11-03 SUMMARY 검색, §6) | [10-20 §10](../debug_log/2026-10-20/SUMMARY.md) |
| 10-20 §11 | 사용자 '같은 실수를 다시 했을 때 알아볼 수 있게 — 본 것 · 추론 · 결론 · 알아보는 법' → 실수 두 건을 칸으로 | 칸: 무엇을 하려 했나 · 무엇을 만들었나 · 무엇을 봤나 · 처음 추론(틀림) · 왜 의심했나 · 판별 시험(표) · 결론(기전 미확인 표시) · 다음에 알아보는 법. §11.3 공통: '신호는 같은 창의 다른 지표와의 모순, 판별은 변수를 하나만 바꾼 작은 시험' | 이 절이 규약 본보기 | [10-20 §11](../debug_log/2026-10-20/SUMMARY.md) · 정리 페이지 원본 [`report_1020_body.html`](../debug_log/2026-10-20/jobs/report_1020_body.html)('바로잡은 내 오류' 절, 커밋 `da94f9e7`) |
| 10-21(커밋 `3f504e12`) | CLAUDE.md 기록 규약에 '추론 경로 기록 규약(2026-10-20 사용자 결정)' | 칸 7 개(하려 한 것 → 본 것 → 처음 추론 → 의심한 이유 → 판별 시험 → 결론 → **다음에 알아보는 법**) · '한 줄 정정 금지' · 정리 페이지도 같은 원칙 | 규칙이 문서가 됨 | `git show 3f504e12 -- CLAUDE.md` |
| 10-21 §5 | 첫 적용 — '§4 결론을 옛 기록을 안 찾고 냈다' 를 하려 한 것 · 처음 추론 · 판별 · 결론 · 다음에 알아보는 법으로 | (칸 이름을 굵게 · 줄글로) | — | → [운용 사고 카드 §5.1](drive-ops-1019-1023.md) |
| 10-21 §11.1 | 사람이 길을 막은 f2sm2 영상 — 기존 [`fig_run_video.py`](../tools/fig_run_video.py)(10-14) 2 배속 | `figures/f2sm2_people_block.mp4`, 장면 `f2sm2_frame_60.png` · `_67.png` | SUMMARY '`mp4 는 git 제외`' ✘ — 실제로는 커밋됨(§5-1) | [10-21 §11.1](../debug_log/2026-10-21/SUMMARY.md) |
| 10-21 §18.2 | 실수 2 건을 **표**(칸 × 실수)로 | 칸 이름 = 하려 한 것 · 본 것 · 처음 추론 · 의심한 이유 · 판별 · 결론 · 다음에 알아보는 법 | 표 형식이 처음 쓰임(지금 README 형식의 원형) | [10-21 §18.2](../debug_log/2026-10-21/SUMMARY.md)(내용은 [카메라 컨테이너 SHM](camera-container-shm.md) 쪽) |
| 10-21 §22 | 마무리 페이지 | 게시 + 사본 `figures/day_summary_1021.html`, 생성기 `jobs/fig_day_summary_1021.py`, mx2 상세 페이지 따로 | — | [10-21 §22](../debug_log/2026-10-21/SUMMARY.md) |
| 10-21 §23 | 사용자 '추론마다 어떤 로그에 데이터가 있는지' → 정리 · 옮기기 · 표 | 대화 기록에서 확인 출력 4 건을 파일로(머리줄에 출처 표시), 스크래치패드 bag 10 개 → `bags/`(≈ 0.5 GB; 이 카드에서 `du` = 466 MiB), Jetson `/tmp/nav2.log` 는 **원천 소실**(발췌만), 추론 9 개 × (결과 원문 · 도구 · 입력 원천) 표 | '앞으로 정지 시험도 짧은 bag 으로 남겨 다시 셀 수 있게' | [10-21 §23](../debug_log/2026-10-21/SUMMARY.md) · 커밋 `426a08c3`(CLAUDE.md '데이터 칸') |
| 10-22 §4 | 데이터 칸 규칙 적용 — Jetson 로그를 prep 이 덮기 전에 `bags/logs_f2pr1/`, nav2 는 `outputs/nav2_f2pr1.log` 에도 | 사건 0.01 s 표 `outputs/nav_events_ms_f2pr1.txt`(도구 `jobs/anal_nav_ms.py` — 10-21 `chk_nav_ms.sh` 의 PC 판) | 이후 주행마다 `get_logs_<이름>.sh` 로 회수(10-22 · 10-23 jobs) | [10-22 §4](../debug_log/2026-10-22/SUMMARY.md) |
| 10-22 §7 | §6 정정을 칸 이름 줄글로 한 항목 안에 | '하려 한 것: … 본 것: … 처음 추론: … 의심한 이유: … 판별: … 결론: … 다음에 알아보는 법: …' | 칸은 다 있으나 표 · 새 § 가 아님(README §2.3 '새 § 에 칸을 나눠' 와 비교하면 약식) | [10-22 §7](../debug_log/2026-10-22/SUMMARY.md) |
| 10-23 §19 | 재계획 설명 영상 — `jobs/fig_replan_video.py` = `fig_run_video.py` + 막힘 검사 구간 · 비용 ≥ 99 점 · nav2 사건 줄 | `videos/f2rp2_replan.mp4`(3 배속) | 날짜 `videos/` 에(git 제외) | [10-23 §19](../debug_log/2026-10-23/SUMMARY.md) · `outputs/fig_replan_video_f2rp2.txt` |
| 10-23 §20.6 | 사용자 '디자인이 별로' → 화면 재설계 `Docs/tools/fig_drive_video.py`(matplotlib 그대로) | 1920 × 1080, 큰 판 = 로버 따라가는 3.6 × 2.6 m 창, 미니맵 · 상태 · 범례 · 사건 시간줄. 색은 차분하게 · 빨강 · 주황은 경고만. 화면 틀을 한 번 만들고 값만 바꿔 8 s 구간 2 배속 40 장 ≈ 14 s | 영상 기본 도구(`Docs/tools/README.md` 46 행 '영상은 이것을 기본으로') | [10-23 §20.6](../debug_log/2026-10-23/SUMMARY.md) · 커밋 `f433c4ef` |
| 10-23 §20.7 | 새 도구 첫 실수 — '컨트롤러가 받은 경로' 를 `/plan_smoothed` 하나로 그림 | 재생 시험에서 BT 경로의 절반이 스무딩 실패 원경로(f2rp3 7/14 · f2rp4 4/10) → f2rp4 서쪽 통로 영상에서 원경로 4 개 누락 | ✘ §20.6 '경로는 `/plan_smoothed`(BT 가 넘긴 것)' 는 틀림 → nav_events 로 계획마다 스무딩 / 원경로를 골라 그림, 다시 렌더 | [10-23 §20.7](../debug_log/2026-10-23/SUMMARY.md) 340 행 · [`fig_drive_video.py`](../tools/fig_drive_video.py) 89~103 행 · `outputs/fig_drive_video_f2rp4.txt` |
| 이후(10-26 ~) | (9 기는 아래 행으로 채움 — 11-02 항목은 다음 시기) 포인터: 10-26 `fig_drive_video.py` 로 영상 여러 개(`outputs/fig_video/`) · 11-02 README 재작성(규칙 원본 이동, 커밋 `203461b4`) · 11-02 §11 '설명에 스크립트 핵심 · 나온 결과 발췌'(칸 2 개 추가) | — | — | [10-26 SUMMARY](../debug_log/2026-10-26/SUMMARY.md) · [11-02 SUMMARY](../debug_log/2026-11-02/SUMMARY.md) |
| 10-26 §8 · §12 | `fig_drive_video.py` 로 주행 영상 · 비교 영상(10-23 §20.7 규칙대로 nav_events 를 같이 줌) | 생성 기록 `outputs/fig_video/fig_drive_video_*.txt` 6 개, 영상 `videos/f2sh1_return_box.mp4` · `cmp_f2sh2_vs_f2sa2.mp4` 등 | 영상 기본 도구가 그대로 쓰임 | [10-26 TOOLS](../debug_log/2026-10-26/TOOLS.md) `outputs/fig_video/` 행 |
| 10-26 §16 | 사용자 촬영 영상(4K HEVC 120 fps · 445 s · **2.7 GB**)을 주행 시각화와 붙이기 — 사용자 '토큰 문제 검증 후' | 영상은 PC ffmpeg 로만 다루고, 들여다본 것은 640×360 장면 6 장을 1 장으로 묶은 그림 4 장 + 확인 1 장(`jobs/fig_real_tiles.py`). 시각 맞춤 = 파일 이름 16:09:44 + 445 s = 생성 시각 16:17:11 → '시작 16:09:44(±1 s 추정)'. 위 = 실제 · 아래 = 시각화 1 배속 `videos/cmp_f2sa3_{corridor,box}.mp4` | 큰 원본은 지우지 않음(큰 파일 규칙 — 사용자 확인 뒤) | [10-26 §16](../debug_log/2026-10-26/SUMMARY.md) · `figures/real_video/corridor_a.png` · `cmp_corridor_161217.png` |
| 10-26 §17 · §17.1 | 사용자 '실촬영 영상과 시각화 데이터 합쳐달라. 시각화 영상은 rviz스타일로' → 새 상시 도구 `Docs/tools/fig_rviz_video.py`(720×720, 로버 따라가는 3 m 창) · 옆으로 붙인 합본 → '해상도가 좋지 못해 … 조금 배속' → 4K 에서 1920×1080(lanczos) · 2 배속 · crf 19, RViz 판 1080×1080 · 2 배속(한 변 px 인자 추가) | 합본 1 배속 `videos/f2sa3_real_rviz_{corridor,box}.mp4` · 3000×1080 2 배속 `…_hd_x2.mp4`(55 s · 27 s). 첫 통로 판 실수: `-t 110` 을 입력 뒤에 둬 원본 220 s 를 잘랐고(3300 장), `-shortest` 가 필터 그래프에 안 먹어 시각화 끝 장면이 55 s 멈춤 → `-t` 를 입력 앞으로 · hstack `shortest=1` | 다음에 알아보는 법(§17.1): 자른 뒤 ffprobe 로 길이 · 장 수를 기대값과 대조. 실수 기록이 항목 안 한 줄 — README §2.3 '새 § 에 칸을 나눠' 의 약식(§5-8) | [10-26 §17](../debug_log/2026-10-26/SUMMARY.md) · `outputs/fig_video/fig_rviz_video_f2sa3_*.txt` · 커밋 `7d949a6c`. 자르기 · 합치기 ffmpeg 명령은 **스크립트 파일 없음**(SUMMARY 서술이 전부) |
| 10-26 §18 | 사용자 '폴더 구조가 너무 난잡하다. 분석 후 정리해달라' → 주제별 하위 폴더로 `git mv`(이름 그대로) · SUMMARY 경로 치환 · `TOOLS.md` 신설 | 전: `outputs/` 맨 위 파일 86 · 폴더 12, `figures/` 맨 위 변형 폴더 18 · 그림 4, TOOLS.md 없음. 후: `outputs/{setup,planner_offline,rev_sign,drives/<주행>,mppi_sim,compare,fig_video}/` · `figures/{planner_offline,compare,real_video}/`. SUMMARY 경로 54 줄 스크립트 치환 뒤 모든 경로 존재 확인(없다고 나온 것은 글롭 · 10-23 경로뿐), 다른 날짜 · `Docs/tools` 에서 10-26 산출물을 가리키는 곳 0(grep). 원본 촬영 2.7 GB 는 **사용자가 지움** → 두 구간 밖 장면 · 4K 재자르기는 원천 소실 | 폴더 지도 · 도구 색인 = `TOOLS.md`. '날짜 폴더 안 주제별 하위 폴더 + `drives/<주행>/`' 이 10-27 · 10-28 의 본보기가 됨(10-28 `outputs/drives/f2pl5/` 등) | [10-26 §18](../debug_log/2026-10-26/SUMMARY.md) · [10-26 TOOLS.md](../debug_log/2026-10-26/TOOLS.md) '폴더 지도' · 커밋 `88139086` |
| 10-26 §18.1 | 사용자 '중간파일 지워라' | `videos/real/` 10 개 · 282 MB 지움(잘라 둔 실제 촬영 4 · RViz 단독 4 · 옛 스타일 단독 2). 남은 `videos/` 243 MB = 합본 · 비교 11 개 — 실제 촬영 장면은 이제 합본 안에만 | 시각화 단독 판은 bag + 도구로 다시 만들 수 있음, 실제 촬영 단독은 원천 소실 | [10-26 §18.1](../debug_log/2026-10-26/SUMMARY.md) · 커밋 `87a16020` |
| 10-26 §21 | 하루 정리 페이지(아티팩트) + 로컬 사본 | `figures/day_summary_1026.html`(494 kB, 그림 내장) = `jobs/report_1026_head.html`(10-20 틀) + `jobs/report_1026_body.html` + `figures/report/*.jpg` → `jobs/fill_report_1026.py` | 10-20 부터의 '머리 + 본문 + 그림 → 조립' 방식 그대로(10-28 · 11-02 도 같은 머리) | [10-26 §21](../debug_log/2026-10-26/SUMMARY.md) |
| 10-27 §13 · §20 · 10-28 §14.1 | 영상 · 그림 도구 확장(사용자 'RViz 스타일은 보기 안 좋고 그쪽이 눈이 편함') | `fig_rviz_video.py` 환경 `FIG_STYLE=light`(흰 바탕 · 경로 출처별 색 Smac 초록 · NavFn 주황 점선 · 막힘 판정 칸 빨간 X) · `FIG_FOV` · `FIG_BOX`. 10-28 새 상시 도구 `Docs/tools/fig_place_run.py`(명령별 궤적 · 결과 · 시간축) | 영상 기본은 여전히 `fig_drive_video.py`(`Docs/tools/README.md` 46 행), RViz 판은 실제 촬영 합본용(47 행) | `fig_rviz_video.py` 27~30 행 · [10-27 SUMMARY](../debug_log/2026-10-27/SUMMARY.md) 155 행 · [10-28 §14.1](../debug_log/2026-10-28/SUMMARY.md) |
| 10-29 §6 | 사용자 '도구 · 결과 이름이 비슷하고 SUMMARY 도 요약본이라 오래된 것 이해가 힘들다. 해결방안은?' → 제안 → '그 순서로 진행하라' — **문제 대장 시작** | 진단: 날짜 41 개 · SUMMARY 약 16 000 줄 · jobs 약 1 900 · outputs 약 2 600, TOOLS.md 는 10-12 부터만. 순서(사용자 확정): 자동 색인 → 최근 2 장으로 형식 시범 → 확인 뒤 **오래된 것부터** 시기별(처음 제안 '최근부터 거꾸로' 는, 사용자가 힘들다고 한 것이 오래된 기록이고 근본 원인이 앞쪽에 있어 바꿈). 자동 색인 `Docs/tools/anal_record_index.py` → SECTIONS 1 432 · RUNS 123 · JOBS 1 887 + 상시 37(설명 줄 없는 파일 약 600 빈칸) | 문서 = `Docs/issues/ISSUES.md`(형식 · 상태 정의 · 목록), 시범 카드 2 장([SLAM 시각 정체](slam-stamp-freeze.md) · [세워 둔 로버 드리프트](stationary-yaw-drift.md)) | [10-29 §6](../debug_log/2026-10-29/SUMMARY.md) · 커밋 `b0e7365d` |
| 10-29 §7 | 사용자 '할 수 있는 한 자세히 — 초창기일수록 매번 도구를 새로 만들어 도구 하나 파악하기도 힘들다. 시기별로 진행하자' → 카드 형식에 **도구 해설 · 용어** 칸 · 색인 보강 · 1 기 카드 16 장 | 색인 도구가 확장자 없는 옛 이름(job4y) 언급도 셈 · 설명 주석이 없으면 셸 단계 제목으로 대신 → 설명 빈칸 468 → 298. 카드 작성은 주제 5 묶음 병렬 → 원본 대조로 판단을 바꾸는 주장 4 개 확인 | README §7.2(문제 대장) · 변경 이력 198 행 '2026-10-29 문제 대장 · 자동 색인 — 사용자' | [10-29 §7](../debug_log/2026-10-29/SUMMARY.md) · 커밋 `05d0bd61` |
| 10-29 §8 · §9 | 10-30 작업(2 기 · 3 기 카드, 사용자 결정 2 건)이 **10-29 SUMMARY 에 이어 적힘** — `2026-10-30/` 폴더 없음 | §8 · §9 제목에 '(10-30)' 표시만 | 날짜 폴더 규칙(README §1)과 어긋남 — 10-30 을 찾으려면 10-29 SUMMARY 를 열어야 한다(§5-9) | [10-29 §8 · §9](../debug_log/2026-10-29/SUMMARY.md) |

## 3. 규칙이 지켜졌나 (이 카드에서 원문 대조)
| 규칙 | 확인한 것 | 결과 | 판정 |
|---|---|---|---|
| 큰 bag — 사용자 확인 뒤 삭제 | 10-19 §18.1 뒤 삭제 기록 검색(10-20 ~ 11-03 SUMMARY `bag_f2y1_ir` · `s2_comp30rec`) | 10-20 §10 목록 한 번 뒤 기록 없음. 지운 것은 §18.1 **전**의 `s2_flash30rec` 448 MB 하나(그때 규칙 1 판 · 사용자 승인) | 지켜짐(지운 것 없음) · 정리 자체는 **보류** |
| 실수 칸 형식 | 10-20 §11 이후 실수 기록 | 10-21 §5 · §9 · §18.2, 10-22 §7, 10-23 §20.7 — 칸이 다 있음. 형식은 줄글 · 표 · 한 항목 안 줄글로 섞임 | 대체로 지켜짐(형식 통일은 11-02 README 표에서) |
| 데이터 칸 · 휘발 위치 옮기기 | 10-22 · 10-23 의 nav2 로그 회수 | `outputs/nav2_f2*.log` 5 개(10-22) · `get_logs_*.sh` 9 개(10-23) | 지켜짐 |
| 데이터 칸 — 하루 시작 점검 출력 | 10-21 §0 `outputs/chk_day_start_1021.txt` | 파일 · 스크립트 없음([운용 사고 카드 §5.2-2](drive-ops-1019-1023.md)) | ✘ 1 건 |
| TOOLS.md(10-12 규약) | 날짜 폴더 | 10-19 · 10-20 있음, **10-21 · 10-22 · 10-23 없음** | ✘ — README §9 표 '10-12 이후도 빠진 날이 있다' 에 해당 |
| 도구 앞머리 6 개(10-12 규약) | 날짜 `jobs/` 이름 | `get_` 20 개(10-19 3 · 10-20 4 · 10-22 4 · 10-23 9) · `mk_` 3 · `rp_` 3 · `put_one` · `fill_report` · `stop_now` · `rm_s2_flash` 등 | ✘ 다수 — README §3.1(11-02) 이 '`get_` · `fill_` · `mk_` · `put_` 은 규약에 넣지 않음' 으로 정리(이름은 바꾸지 않음) |
| 영상은 git 제외(09-30 `.gitignore` 52 행 `Docs/debug_log/*/videos/`) | `git ls-files \| grep mp4` | `2026-10-19/figures/f2y1_ir_drive.mp4`(28.8 MB) · `2026-10-21/figures/f2sm2_people_block.mp4`(20.9 MB) **추적됨** — 둘 다 SUMMARY 는 'git 제외' 라 씀. 10-22 부터는 `videos/` 에 둬 제외 | ✘ 2 건(§5-1) |
| (9 기) TOOLS.md · 도구를 쓸 때마다 | 10-26 · 10-27 · 10-28 · 10-29 | 10-26 은 §18 폴더 정리 때 **처음 만듦**(§18 '`TOOLS.md` 없음(10-12 도구 규약 위반)' — 그날 §0 ~ §17 을 몰아 씀, 뒤에 §19 행 따로 커밋 `b9547f52`), 10-27 · 10-28 · 10-29 있음 | 부분 ✘(10-26 사후 작성 — README §3.3 '끝난 뒤 몰아 쓰지 않는다') |
| (9 기) 영상 git 제외 | `git ls-files Docs/debug_log/2026-10-26` 에서 mp4 | 0 개 — 영상 12 개는 모두 `videos/`(git 제외), `figures/real_video/` 는 png 9 장만 | ✔(8 기 결함 반복 안 함) |
| (9 기) 큰 파일 규칙 | 10-26 §16 원본 2.7 GB | 내가 지우지 않았고 사용자가 직접 지움(§18) · 중간 파일 282 MB 는 사용자 지시로 지움(§18.1) | ✔ |

## 4. 조치와 효과 — 지금 규칙이 있는 곳
| 규칙 | 처음 | 지금 원본 | 문구(발췌) |
|---|---|---|---|
| 큰 bag 수명 | 10-19 §18.1(사용자) · 세션 메모리 | [README §6](../debug_log/README.md) 125 행 · 변경 이력 194 행 | '**GB 급 bag**은 바로 지우지 않는다(10-19): ① 시각화해 보여 줌 → ② 사용자가 짚는 부분 분석 → ③ 수치 · 그림 기록, SUMMARY 에 "무엇을 남기고 무엇을 지웠나(경로 · 크기)" → ④ **사용자 확인 뒤** 삭제' |
| 실수 칸 형식 | 10-20 §11 → CLAUDE.md `3f504e12`(10-21) | [README §2.3](../debug_log/README.md) 58 행 표(칸 10 개 — 11-02 에 '스크립트 핵심 · 나온 결과' 추가) · §7.1 133 행(정리 페이지 본보기 `report_1020_body.html`) · §9 181 행('~ 10-19 실수 칸 형식 · 데이터 칸 없음') | '**내 실수 · 정정**은 새 § 에 칸을 나눠 쓴다(한 줄 "정정" 금지). 본보기 `2026-10-20/SUMMARY.md §11`' |
| 추론별 데이터 위치 | 10-21 §23 → CLAUDE.md `426a08c3` | [README §2.3](../debug_log/README.md) 54 · 55 행 · 변경 이력 196 행 | '**추론마다 데이터 위치**를 적는다 — 결과 원문(`outputs/`), 도구(`jobs/` · `Docs/tools/`), 입력 원천(bag 경로 · 토픽, Jetson 로그 경로), 그림' · '휘발 위치 … 에만 있는 것은 그날 `outputs/` · `bags/` 로 옮긴 뒤 그 경로를 쓴다. 못 옮겼으면 **'원천 소실'**' |
| 영상 도구 | 10-23 §20.6(사용자) · 세션 메모리 | [`Docs/tools/README.md`](../tools/README.md) 46 행 — README(규약 원본)에는 영상 도구 기본값이 없다 | '영상은 이것을 기본으로 \| (10-23 신규, 사용자: 옛 화면 디자인 별로)' |
| 주행 직후 bag 회수 · prep 원문 보관 | 10-21 §23 의 '원천 소실' 경험(추정 — 문구의 날짜는 없음) | [README §5](../debug_log/README.md) 119 · 120 행 | 'prep 출력은 필터 파이프로 거르지 말고 원문을 파일로' · '주행 직후 bag 을 PC `bags/` 로 회수' |
- 효과: 10-22 부터 주행마다 nav2 · slam · sensors 로그를 저장소로 회수(10-21 §23 의 nav2 원천 소실 같은 일이 10-22 · 10-23 주행엔 없음 — 회수 파일 존재로 확인). 10-21 §23 이 옮긴 bag 10 개는 PC 로컬 `2026-10-21/bags/` 466 MiB(이 카드에서 `du`). 8 시기 날짜 폴더 `bags/` 합 약 1.2 GiB(10-21 466 · 10-22 345 · 10-23 403 MiB), 저장소 작업 트리 `bags/` 전체 약 4.4 GiB · `videos/` 약 3.8 GiB(이 카드에서 `du`, 둘 다 git 제외).
- 한계: 큰 bag 규칙은 'GB 급' 만 정한다 — 수백 MB bag(예: 10-22 §13 `bag_f2lp1` 470 MB, Jetson `~/bags`)은 09-18 '정리 보류' 그대로([저장 공간 카드](storage-housekeeping.md)).

## 5. 내 실수 · 기록 어긋남
1. **'mp4 는 git 제외'(10-19 §20 · 10-21 §11.1) vs 저장소**: 두 영상은 날짜 폴더 `figures/` 에 저장됐고, `.gitignore`(51 · 52 행)는 `Docs/debug_log/*/videos/` 만 뺀다 → 커밋됨(`2026-10-19/figures/f2y1_ir_drive.mp4` 는 커밋 `d788c132`, `2026-10-21/figures/f2sm2_people_block.mp4` 는 `30581757` 에서 추가). 이 저장소는 비공개 원본 · 공개 사본으로 나가므로(README §8) 공개 쪽 포함 여부는 `private/publish_public.sh` 설정에 달림 — 이 카드에서는 확인 안 함. **다음에 알아보는 법**: 영상은 `videos/` 에만 둔다. 'git 제외' 라 쓰기 전에 `git check-ignore -v <파일>` 로 확인.
2. **10-19 §18.1 의 위치**: 정정 § 가 §19.1 뒤에 있다(시간순으로 나중에 씀). 번호는 §18 의 하위라 목차에서 §18 다음으로 찾으면 안 보인다 — 읽을 때 주의.
3. **`fig_drive_video.py` 독스트링 '(2026-10-23 §20.5)'** vs SUMMARY 의 도구 절 §20.6: 커밋 `f433c4ef` 이 '§20.5' 커밋에 함께 들어가 생긴 번호 차(같은 도구).
4. **§20.6 '경로는 `/plan_smoothed`(BT 가 컨트롤러에 넘긴 것)'** → §20.7 에서 정정(위 흐름 표). 코드 89~90 행에 정정 주석이 있다.
5. **10-21 §23 표의 '도구(jobs/)' 칸 `chk_nav_ms.sh`**: 저장소 [`2026-10-21/jobs/chk_nav_ms.sh`](../debug_log/2026-10-21/jobs/chk_nav_ms.sh) 있음 ✔. 반면 같은 날 §5 · §9 의 확인 스크립트(에이전트 · `chk_slamlag`)와 `prep_sm_1021.sh` 는 표에도 `jobs/` 에도 없다 — 데이터 칸 규칙을 만든 날의 앞 절은 소급되지 않았다.
6. **`chk_wifi_1022.txt` 원문에 AP BSSID(MAC)가 그대로**: README §4 '출력에 MAC 주소가 나오면 가린다' 와 어긋남(이 카드 · 운용 사고 카드는 옮기지 않음). 10-21 §4 SUMMARY 본문에도 Jetson 무선 MAC 이 그대로 있다.
7. **10-20 §10 '생성 `jobs/fig_shm_day.py` + 스크래치패드 fill_report_1020.py'**: `fill_report_1020.py` 는 저장소 `2026-10-20/jobs/` 에도 있다(커밋 `271bb68b` 에서 추가). '스크래치패드' 는 실행 위치를 말한 것으로 보임 — 어긋남 아님, 읽을 때 혼동 주의.
8. (9 기) **10-26 §17.1 의 ffmpeg 실수 기록은 한 항목 안 한 줄**('내 실수: … 다음에 알아보는 법: …'): README §2.3 의 칸 표 · 새 § 형식이 아니다. 같은 날 §1.1 · §6.1 · §7.2 의 실수는 별 § 제목으로 뒀다 — 형식이 날 안에서도 섞임. 자르기 · 합치기 ffmpeg 명령 자체도 파일로 안 남았다(§2 표 — 다시 만들려면 SUMMARY 서술로 재구성해야 함).
9. (9 기) **10-30 작업이 10-29 SUMMARY 에**(§8 · §9, 제목에 '(10-30)'): 날짜 폴더가 없어 `index/SECTIONS.md` 에서도 10-30 으로는 안 나온다.
10. (9 기) **10-26 §18 'SUMMARY 의 모든 경로가 실제로 있는지 확인'** 뒤에도 같은 날 TOOLS 40 행은 `anal_contact` 를 '10-23 jobs 계열' 이라 적었다(실제 `2026-10-22/jobs/anal_contact.py` — 11-03 §2 정정 표). 경로 존재 검사는 '적힌 경로' 만 보고 '말로 적은 위치' 는 못 본다.

## 6. 남은 것
- 큰 bag 정리: 10-20 §10 목록(Jetson `~/bags` — `bag_f2y1_ir` 4.0 GB · `_f2z1_ir` · `_f2z2_ir` ≈ 1.9 GB 씩 · `s2_comp30rec(_b)` 1.5 GB 씩 · `vslam/*_split`)은 '사용자 확인' 단계에서 멈춰 있다. 10-23 Jetson 디스크 여유 122 GB(10-21 129 → 10-22 124 → 10-23 122 GB, 각 날 하루 시작 점검)라 급하지는 않다.
- 추적된 mp4 2 개를 `videos/` 로 옮길지 · 이력에서 뺄지(사용자 결정 — 이력 다시 쓰기는 [저장소 공개 운영](repo-public-ops.md) 소관).
- 10-21 · 10-22 · 10-23 `TOOLS.md`: 사후로 채울지(README §3.3 '끝난 뒤 몰아 쓰지 않는다' 와 충돌) — 지금은 문제 대장 '도구 해설' · 색인 `index/JOBS.md` 가 대신한다.
- 영상 도구 기본값이 규약 원본(README)에 없고 `Docs/tools/README.md` 에만 있다.
- (9 기) 실제 촬영 합본 절차(ffmpeg 자르기 · 배속 · hstack)가 도구로 없다 — 다음에 촬영 영상을 받으면 §17.1 같은 실수를 피하려면 `fig_` 스크립트로 묶는 것이 맞다(제안, 결정 없음).
- (9 기) 문제 대장: 시기별 카드 작성 중(11-04 9 기). 색인은 손으로 고치지 않는 규칙이라 카드 추가 뒤 `anal_record_index.py` 를 다시 돌려야 한다(README §7.2).

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `rm_s2_flash.sh` | 큰 bag 1 개 삭제(삭제 전 크기 · 메타데이터 확인) | [`2026-10-19/jobs/`](../debug_log/2026-10-19/jobs/rm_s2_flash.sh)(출력 없음) |
| `fig_ir_extract.py` · `fig_ir_drive_video.py` | 큰 IR bag → 짝 영상(규칙 첫 적용) | `2026-10-19/jobs/` → `figures/f2y1_ir_drive.mp4`(추적됨) |
| `fig_run_video.py` | 주행 구간 영상 일반판(10-14) | [`Docs/tools/`](../tools/fig_run_video.py) → `2026-10-21/figures/f2sm2_people_block.mp4`(추적됨) |
| `fig_replan_video.py` | `fig_run_video` + 막힘 검사 구간 | `2026-10-23/jobs/` → `videos/f2rp2_replan.mp4` |
| `fig_drive_video.py` | 화면 재설계판(10-23 ~ 기본) | [`Docs/tools/`](../tools/fig_drive_video.py) → `2026-10-23/videos/f2rp{3,4,5}_*.mp4` · `f2von2_return_box.mp4` |
| 정리 페이지 | 10-19 · 10-20 · 10-21 | `figures/day_summary_1019.html` · `day_summary_1020.html`(+ `jobs/report_1020_{head,body}.html` · `fig_shm_day.py` · `fill_report_1020.py`) · `day_summary_1021.html`(+ `jobs/fig_day_summary_1021.py`) |
| 회수 도구 | 주행 로그 · bag 을 PC 로 | `2026-10-22/jobs/get_bag_f2lp1.sh` · `get_logs_f2{pi1,sm3}.sh` · `2026-10-23/jobs/get_logs_*.sh` |
| `fig_real_tiles.py`(9 기) | 실제 촬영 작업본에서 지정 시각 장면을 뽑아 격자 한 장으로(토큰 절약) | `2026-10-26/jobs/` → `figures/real_video/*.png` |
| `fig_rviz_video.py`(9 기) | RViz 스타일 정사각 주행 영상(실제 촬영과 붙이기용, 10-27 `FIG_STYLE=light`) | [`Docs/tools/`](../tools/fig_rviz_video.py) → `2026-10-26/videos/f2sa3_real_rviz_*.mp4`(합본) |
| `anal_record_index.py`(9 기) | 문제 대장 자동 색인 3 종 | [`Docs/tools/`](../tools/anal_record_index.py) → [`index/`](index/SECTIONS.md) |
| 정리 페이지(9 기) | 10-26 | `2026-10-26/figures/day_summary_1026.html`(+ `jobs/report_1026_{head,body}.html` · `fill_report_1026.py`) |

## 8. 도구 해설
### 8.1 `rm_s2_flash.sh` (10-19 §18, Jetson, bash — 로버 안 움직임)
- 왜: 규칙 1 판의 첫 삭제 — 수치는 §16.1 에 다 기록됐고 더 쓸 데 없는 IR 8 Hz bag.
- 하는 일: 대상 디렉터리 없으면 중단 → `du -sh` · 파일 목록 · `metadata.yaml` 의 길이 · 메시지 수 → `rm -rf` → 남은 bag 상위 8 · 디스크.
  ```bash
  [ -d "$B" ] || { echo "없음: $B"; exit 1; }
  echo "== 삭제 전"; du -sh $B; ls $B; grep -aE "duration|message_count: [0-9]{3,}" $B/metadata.yaml | head -4
  rm -rf "$B" && echo "== 삭제함 $B"
  ```
- 출력: 파일로 안 남음(**원천 소실**) — '448 MB · 메시지 30373 · IR2 729 장 · 남음 146 GB' 는 SUMMARY · TOOLS 서술. 지금 규칙(README §6)대로라면 이 출력이 'SUMMARY 에 무엇을 지웠나(경로 · 크기)' 의 근거 원문이 됐어야 한다.
- 지금: 그날 전용. 삭제 도구의 본보기(삭제 전 확인 → 삭제 → 남은 것)로는 쓸 수 있음.

### 8.2 `fig_run_video.py` (10-14 → 10-21 §11.1 사용, PC, matplotlib · rosbags)
- 부른 형태: `fig_run_video.py bag 출력.mp4 시작HH:MM:SS 끝HH:MM:SS [배속=3]`(10-21 은 2 배속).
- 하는 일: 왼쪽 주행 구역 전체 · 오른쪽 로버 주변 3 × 3 m. 바탕 전역 코스트맵(빨강 치명 · 주황 내접 · 회색 감쇠), 보라 = 지금 전역 경로(바뀐 뒤 3 s 는 옅은 직전 경로), 빨간 네모 = 로컬 치명 칸, 파란 점 = 라이다, 노란 부채꼴 = 카메라 시야(±43°, 1.4 m). 끝에 경로 길이가 0.3 m 넘게 달라진 시각 표.
- 출력: mp4 + 장면 png(10-21 `figures/f2sm2_frame_60.png` · `_67.png`).
- 계보: → 10-23 `jobs/fig_replan_video.py`(막힘 검사 구간 추가) → `fig_drive_video.py`(화면 재설계). 지금은 `fig_drive_video.py` 가 기본, 이것은 남아 있음(다시 쓸 수 있음).

### 8.3 `fig_drive_video.py` (10-23 §20.6, PC, matplotlib · rosbags) ★
- 부른 형태: `python Docs/tools/fig_drive_video.py bag 출력.mp4 HH:MM:SS HH:MM:SS [배속=2] [nav_events.txt|-] [제목]`. `nav_events.txt` = 'HH:MM:SS.cc 노드 메시지' 줄(예 `2026-10-23/outputs/nav_events_ms_f2rp3.txt`).
- 왜: 사용자 '디자인이 별로'. 데이터 처리는 `fig_replan_video.py` 와 같고 화면만.
- 하는 일(코드 기준):
  - 읽는 토픽: `/tf` · `/tf_static` · `/local_costmap/costmap` · `/global_costmap/costmap` · `/plan` · `/plan_smoothed` · `/scan` · `/cmd_vel`(48 행).
  - 그릴 경로 고르기(89~103 행, 10-23 §20.7 정정): nav_events 가 있으면 BT 계획마다 스무딩 성공이면 1.5 s 안의 `/plan_smoothed`, 실패('Smoothed path leads to a collision')면 직전 `/plan` 원경로.
  - 막힘 검사 구간: 로버 앞 경로 누적 길이 0.30~1.5 m 점들의 전역 비용 ≥ 99 를 표시(202~207 행 `seg = pl[i0:][(sacc >= 0.30) & (sacc <= 1.5)]` · `bad = seg[vv >= 99]`) — `PathBlockedAhead` 와 같은 범위로 그린 것(판정 자체는 아님).
  - 색(26~37 행): 코스트맵 −1 미지 · 0 흰색 · 1~98 옅은 회색 단계 · 99 연살구 · 100 회청. 빨강(`C_BLOCK`) · 주황(`C_CHECK`)은 막힘 표시에만.
  - 속도: 화면 틀을 한 번 만들고 매 장 `set_data` · `set_offsets` 로 값만 바꿈(186~210 행) → `wr.grab_frame()`.
- 출력: mp4(날짜 `videos/`, git 제외) + 실행 요약 `outputs/fig_drive_video_*.txt`(예 f2rp4: BT 경로 8 개 · 원경로 4).
- 결과가 쓰인 곳: 10-23 §20 서쪽 통로 · 복귀 상자 영상, 10-26 이후 영상(다음 시기).
- 알려진 결함: ① nav_events 없이 부르면 첫 판처럼 `/plan_smoothed` 만 씀(스무딩 실패 구간 경로가 묵음 — 코드 주석의 결함 그대로) ② 폰트 `Malgun Gothic` · ffmpeg 경로 `C:/ffmpeg/bin/ffmpeg.exe` 고정(이 PC 전용) ③ 막힘 표시는 전역 코스트맵 메시지(≈ 1.5 s 간격) 기준이라 실제 판정 시각과 어긋날 수 있다.
- 지금: 영상 기본 도구.

### 8.4 `fig_real_tiles.py` (10-26 §16, PC, PIL · ffmpeg)
- 부른 형태: `fig_real_tiles.py 작업본.mp4 작업본시작HH:MM:SS 출력.png 열수 HH:MM:SS.s=설명 …`.
- 왜: 4K 2.7 GB 영상을 내가 '보려면' 장면 그림이 토큰을 쓴다 → 640×360 장면 여러 장을 한 장으로 묶어 그림 수를 줄임(사용자 '토큰 문제 검증 후').
- 하는 일: 시각마다 `ffmpeg -ss (시각 − 작업본 시작) -i 작업본 -frames:v 1 -vf scale=640:360` 로 png 한 장을 파이프로 받아 위에 검은 띠 + 노란 '시각 설명' 글씨(맑은 고딕 22) → 열수로 격자(회색 바탕) 저장.
  ```python
  png = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', '%.2f' % off, '-i', vid, '-frames:v', '1', '-vf', 'scale=%d:%d' % (W, H), ...]).stdout
  d.rectangle([0, 0, W, 30], fill=(0, 0, 0)); d.text((6, 3), '%s  %s' % (ts, lab), fill=(255, 255, 0), font=font)
  ```
- 출력: `2026-10-26/figures/real_video/corridor_a.png` · `corridor_b.png` · `corridor_c_box_a.png` 등. 결함: 폰트 경로 Windows 고정 · 작업본 시작 시각을 사람이 넣음(시각 맞춤 오차 ±1 s 가 그대로 들어감) · `-ss` 를 입력 앞에 둔 빠른 탐색이라 몇 장 어긋날 수 있음(추정 — 확인 안 함). 지금: 그날 전용이지만 작업본 · 시각만 바꾸면 다시 쓸 수 있음.

### 8.5 `fig_rviz_video.py` (10-26 §17 신규 → 10-27 §13 · §20 확장, PC, matplotlib · rosbags)
- 부른 형태: `python Docs/tools/fig_rviz_video.py bag 출력.mp4 시작HH:MM:SS 끝HH:MM:SS [배속=1] [nav_events.txt|-] [제목] [창 m=3.0] [한 변 px=720]`, 환경 `FIG_STYLE=light` · `FIG_FOV=반각,거리` · `FIG_BOX=x0,x1,y0,y1`.
- 왜: 사용자 '실촬영 영상과 시각화 데이터 합쳐달라. 시각화 영상은 rviz스타일로' — 16:9 실제 촬영 옆에 붙이기 쉬운 정사각, RViz 에 익숙한 색.
- 하는 일(코드 기준): 읽는 토픽 `/tf` · `/tf_static` · `/local_costmap/costmap` · `/global_costmap/costmap` · `/plan` · `/plan_smoothed` · `/scan` · `/cmd_vel`(54 행). BT 경로 고르기는 `fig_drive_video.py` 와 같은 규칙(nav_events 의 스무더 사건) + `/plan` 점 간격 중앙 > 0.04 m 면 Smac 경로로 표시(97 행). 바탕 = 전역 코스트맵을 RViz 'costmap' 색표 흉내로(37~43 행: 1~98 파랑 → 빨강, 낮은 비용일수록 투명 · 99 하늘색 · 100 자홍 · 미지 회청), 노란 칸 = 로컬 치명, 빨간 점 = 라이다, 초록 = 경로 · 차체(풋프린트 앞 0.262 · 뒤 −0.248 · 옆 ±0.165), 빨강 / 초록 = base_link x / y 축. 10 fps · 한 장 간격 `DT = 배속 / 10` s.
  ```python
  for i in range(1, 99):   # 1~98: 파랑 → 빨강
      f = (i - 1) / 97.0; cols.append((f, 0.0, 1.0 - f, 0.18 + 0.27 * f))   # 낮은 비용은 더 투명
  cols += [(0.0, 1.0, 1.0, 0.45), (1.0, 0.0, 1.0, 0.85)]   # 99 내접 하늘색 · 100 치명 자홍
  ```
- 출력: mp4 + 화면 한 줄 → `2026-10-26/outputs/fig_video/fig_rviz_video_f2sa3_*.txt` 4 개(예 '저장 …/f2sa3_rviz_corridor_1080_x2.mp4 프레임 550 · 경로 10').
- 결함: 폰트 · ffmpeg 경로 이 PC 고정(`fig_drive_video.py` 와 같음) · Smac 판별이 '점 간격' 근사 · 실제 촬영과의 시각 맞춤은 도구 밖(파일 이름 시각, ±1 s 추정). 지금: 상시 도구(`Docs/tools/README.md` 47 행).

### 8.6 `anal_record_index.py` (10-29 §6 · §7, PC)
- 부른 형태: `python Docs/tools/anal_record_index.py`(저장소 어디서든). `bags/` 가 git 제외라 이 PC 에서 돌려야 RUNS 가 맞다.
- 왜: 사용자 '도구 · 결과 이름이 비슷하고 SUMMARY 도 요약본이라 오래된 것 이해가 힘들다'.
- 하는 일: 날짜 폴더마다 SUMMARY 의 `##` · `###` 제목 → SECTIONS.md, `bags/bag_<이름>` · `outputs/drives/<이름>` 에서 실험 이름을 모아 SUMMARY 에서 처음 · 마지막 § 와 횟수 → RUNS.md, `jobs/` · `Docs/tools/` 파일마다 첫 설명 줄(없으면 셸 단계 제목, 10-29 §7 보강) + 언급된 §(확장자 없는 옛 이름도 셈) → JOBS.md. 덮어쓴다.
- 출력: `Docs/issues/index/{SECTIONS,RUNS,JOBS}.md`(11-04 SECTIONS 머리 '날짜 42 개 · 제목 1460 개').
- 한계(독스트링): 이름 대장은 bag · drives 폴더가 있는 주행만(대략 09-1x 이후). 10-29 SUMMARY 안의 10-30 절은 10-29 로 색인된다(§5-9).

## 9. 용어
- **큰 bag(GB 급)**: 원시 IR · 깊이 영상을 담은 주행 기록. 분석 원천이지만 저장소에 넣지 않고 Jetson `~/bags` 와 PC 로컬에만 둔다.
- **파생 자료**: bag 에서 뽑은 작은 결과(csv · 표 · 그림 · 영상). 저장소 `outputs/` · `figures/` 에 둬 bag 을 지워도 판정 근거가 남게 한다.
- **실수 칸 형식**: 틀린 판단을 '하려 한 것 · 본 것 · 처음 추론 · 의심한 이유 · 판별 시험 · 결론 · 다음에 알아보는 법'(+ 11-02 '스크립트 핵심 · 나온 결과 · 데이터')으로 나눠 쓰는 방식. 다음에 같은 서명을 보면 알아보게 하는 것이 목적.
- **데이터 칸 · 원천 소실**: 추론에 쓴 결과 원문 · 도구 · 입력 원천의 위치. 휘발 위치에만 있다가 사라졌으면 그 사실을 '원천 소실' 로 적는다.
- **휘발 위치**: Jetson `/tmp`(prep 이 로그를 덮고 재부팅이 지움) · PC 스크래치패드(오래된 파일 자동 삭제 추정).
- **합본(실제 촬영 + 시각화)**: 사용자가 찍은 영상과 bag 으로 그린 영상을 같은 시각으로 맞춰 위아래 · 옆으로 붙인 것(ffmpeg `vstack` · `hstack`). 시각 맞춤은 촬영 파일 이름 · 생성 시각으로 ±1 s 추정.
- **문제 대장**: 날짜별 기록을 문제별 카드로 다시 묶은 길잡이(`Docs/issues/`, 10-29 ~). 카드 = 증상 → 흐름 → 가설과 판별 → 조치 → 실수 → 남은 것 → 도구 해설 · 용어.
- **자동 색인**: 손으로 쓰지 않고 스크립트가 기록에서 뽑아 덮어쓰는 목록(SECTIONS · RUNS · JOBS). 손으로 고치면 다음 실행에 사라진다.
