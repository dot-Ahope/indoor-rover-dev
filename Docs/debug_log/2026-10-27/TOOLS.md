# 2026-10-27 도구 안내 · 폴더 지도

이 날 무엇을 했는지는 `SUMMARY.md`(§0~§31), 이 파일은 **어디에 무엇이 있나**와 **어떤 도구를 어떤 상황에 썼나**를 정리한다.
하루 끝(§31)에 `outputs/` 바로 아래 흩어진 파일 8 개를 `outputs/setup/` · `outputs/fig_video/` · `outputs/swap/` 으로 옮기고 SUMMARY 의 경로를 같이 고쳤다. 파일 이름은 바꾸지 않았다.

## 폴더 지도

| 폴더 | 무엇 | SUMMARY |
|---|---|---|
| `jobs/` | 그날만 쓴 스크립트(이름 앞머리 = 용도). 계속 쓰는 도구는 `Docs/tools/` | 전체 |
| `outputs/setup/` | 하루 시작 점검 · prep · 배포 · nvblox 층 수정 빌드 · 정지 확인 | §0 · §9 · §10 · §17 |
| `outputs/swap/` · `parent_chain/` · `tolcp/` · `tolcp_exp/` · `tol_box/` | Smac 서쪽 통로 오프라인(목표 자세 · 부모 사슬 · 허용치 · cost_penalty · 상자 장면) | §1 ~ §8 |
| `outputs/drives/<주행>/` | 주행 하나의 모든 것(러너 · nav2 로그 · 사건 · 여유 · 정지 · 상자 · 경로 출처 · F0 기록). f2tf1 은 `box/`(상자 · 카메라 시야) 포함 | §11 · §19 · §25 |
| `outputs/block_cell/` | 막힘 판정 칸 원자료 대조 · 전역 코스트맵 튐(nvblox 층 TF) 판별 | §14 · §15 · §16 |
| `outputs/tffix/` | §15 서명(단위 변환 슬라이스) 검출 — f2st1 · f2tf1 · f2tt1 | §19 · §25 |
| `outputs/load/` | 부하 · SLAM stamp 정체 · 이력(112 bag) · 시스템 성능 · transform_timeout 배포 | §21 ~ §23 · §25 · §30 |
| `outputs/gate/` | 주행 전 검사 정리(게이트 비교 · prep 원문) | §24 |
| `outputs/slamproc/` | SLAM 정체 원인: 계기 분석 · 재생 A/B(`rep/` 변형별 원문) · 계측판 단계별 시간 · 소스 원문 | §26 · §29 |
| `outputs/tt1_exp/` | f2tt1 통로 Smac 오프라인 재질의 · 탐색 기록 · 지도 판 비교 | §27 · §28 |
| `outputs/fig_video/` | 영상 도구 생성 기록 | §3 · §12 · §13 · §20 · §27 |
| `figures/` | 그림(요약 · 탐색 마지막 장 · 막힘 칸 · 코스트맵 튐) · 정리 페이지 로컬 사본 `day_summary_1027.html` · 그 그림 `report/` | 해당 § · §31 |
| `videos/`(git 제외) | 탐색 영상 · 통로 · 상자 · 복귀 영상 | §3 · §13 · §20 · §27 |
| `bags/`(git 제외) | 주행 bag tgz(f2st1 · f2tf1 · f2tt1) · Jetson 로그 `logs_<주행>/` | §11 · §19 · §25 |

주행 이름: `f2st1` = no5 + Smac tol 0.35 · `f2tf1` = + nvblox 층 TF 수정 · `f2tt1` = + SLAM transform_timeout 1.5 + 게이트 정리판 러너.

## 도구 — 상황 → 도구 → 나온 값 → 그때의 추론(✔ 맞음 · ✘ 틀림 · ？ 미확인)

| § | 상황 | 도구 | 나온 값(원문) | 추론 |
|---|---|---|---|---|
| §0 | 하루 시작 상태 | `jobs/chk_day_start_1027.sh` | 재부팅 · 스택 꺼짐(`setup/chk_day_start_1027.txt`) | ✔ |
| §1 · §2 | 남행 실패 순간 목표를 바꾸면? · 부모 사슬 | `jobs/run_swap_1027.sh` · `jobs/anal_parent_chain.py` | `swap/` · `parent_chain/` | ✘ '좁은 곳 = 벽' 은 틀림 — 탐색이 건넘(§2 정정) |
| §3 | 탐색 영상 같은 일끼리 | `jobs/fig_smac_expansion_v2.py` | 북행 3 · 남행 1 영상 | ✔ 10-26 영상은 남 · 북을 섞었음(사용자 지적) |
| §5 · §6 | 허용치 · cost_penalty 재질의 | `jobs/run_tolcp_1027.sh` · `jobs/anal_tolcp.py` | tol 0.35 에서 남행 성공(`tolcp/`) | ✔ 허용치는 휴리스틱 비교(소스) |
| §8 | tol 0.35 가 상자 장면을 나쁘게 하나 | `jobs/run_tol_box_1027.sh` | 상자 4 장면 차 0(`tol_box/`) | ✔ |
| §9 · §10 | 러너 소실 · prep · 배포 | `jobs/up_prep_params_1027.sh` · `jobs/prep_smac_1027.sh` | blob 일치 · PREP_OK(`setup/`) | ✔ 스크래치패드 7 일 정리 추정(？) |
| §11 | f2st1 주행 | 러너 · `2026-10-1x/jobs/anal_*` | 8/8 · 남행 Smac · 여유 4.1 cm(`drives/f2st1/`) | ✔ |
| §13 | 북행에 NavFn 썼나 | `2026-10-26/jobs/chk_corr_paths.py` | 북행 NavFn 3(`drives/f2st1/chk_corr_paths_f2st1.txt`) | ✔ |
| §14 | 막힘 칸 원자료 대조 | `jobs/anal_block_cell.py` · `jobs/fig_block_cell.py` | 상자 모서리 칸 내접 띠 · 라이다 0 | ✘ §13 '떨어진 덩어리' 는 틀림 → 정정 |
| §15 | 전역 코스트맵 20 s · 31 s 튐 | `jobs/chk_gcm_*.py` · `jobs/chk_slice_tf.py` · `jobs/fig_gcm_*.py` | 단위 변환으로 적힌 슬라이스(`block_cell/chk_gcm_fit_f2st1.txt`) | ✔ 상위 nvblox 층 결함(소스) |
| §16 | 부하 탓인가 | `jobs/chk_tf_lag.py` | 경고 20/22 가 Control loop missed 와 겹침 | ？ → §21 에서 SLAM stamp 정체로 정정 |
| §17 | nvblox 층 수정 · 빌드 | `jobs/prep_nvlayer_tffix_1027.sh` · `jobs/chk_nvlayer_tffix_1027.py` | 일치율 1.000(`setup/run_tffix_chk_1027.txt`) · 패치 `Docs/05_nvblox/nvblox_nav2_rover.patch` | ✔ |
| §19 | f2tf1 — 수정 확인 | `jobs/anal_tffix_sig.py` | 경고 28 · 서명 0(f2st1 3) | ✔ |
| §20 | 복귀 장면 · 상자 시야 | `Docs/tools/fig_rviz_video.py` FIG_FOV · FIG_BOX | 상자 시야 밖 · 접촉(사용자 확인) | ✔ |
| §21 | 카메라가 아무것도 못 봤나 | `jobs/chk_cam_fov.py` | 상자만 못 봄 | ✔ |
| §21 | TF 지연의 정체 | `jobs/anal_load_f2tf1.py` · `jobs/anal_slam_freeze.py` · `jobs/chk_mapodom_window.py` | 실패 33/33 = SLAM stamp 정체 창 | ✔ → transform_timeout 1.5(`jobs/up_slam_tt15_1027.sh`) |
| §22 | UDP 탓 · 공유메모리로? | `jobs/anal_slam_freeze_cause.py` | 입력 제때 · SLAM CPU 몰림 | ✔ 통신 아님(SLAM 안쪽 수신은 ？) |
| §23 | 예전부터 있었나 | `jobs/anal_slam_freeze_hist.py` | 위치 추정 순회 전 주행에 같은 수준 | ✔ |
| §24 | 주행 전 검사 정리 | `Docs/tools/chk_drive_gate.py` · `Docs/tools/chk_prep.py` · `jobs/job551_f0drive.sh` | 게이트 23.6 → 6.7 s · 출발 40 s | ✔ 필터판 prep 무출력 11 s(？) |
| §25 | f2tt1 | `jobs/anal_slam_freeze.py` · `jobs/anal_tffix_sig.py` | TF 실패 0 · 정지 0 | ✔ |
| §26 | 정체 계기 · 재생 A/B | `jobs/anal_slam_freeze_trigger.py` · `Docs/tools/run_slam_replay.sh` · `slam_replay_feed.py` · `jobs/anal_slam_replay.py` | 정합마다 · 채택 변형 없음 | ✔ |
| §27 · §28 | f2tt1 시각화 · 탐색 영상 | `jobs/fig_f2tt1_summary.py` · `jobs/run_tt1_exp_1027.sh` · `jobs/fig_smac_expansion_tt1.py` · `jobs/chk_replan_maps.py` | 재질의 3 번째 실패 = 지도 판 · 출발 경계 | ✘ 첫 영상 이름표가 실주행 실패로 읽힘 → 정정 |
| §29 | SLAM 단계별 시간 | `jobs/prep_slam_dbg_1027.sh`(사본 `~/slam_dbg_ws`) · `jobs/anal_slam_timing.py` | LinkNearChains 64 % · link 0.75 m 에서 긴 정체 절반 이하(기준 미달) | ✔ 결정 안 함 |
| §30 | 시스템 성능 | `jobs/anal_sys_perf.py` | CPU 67 % · 7.3 W · 4 회 8/8 | ✔(4 회, 위치 정답 없음) |
