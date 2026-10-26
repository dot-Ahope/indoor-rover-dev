# 2026-10-26 도구 안내 · 폴더 지도

이 날 무엇을 했는지는 `SUMMARY.md`(§0~§18), 이 파일은 **어디에 무엇이 있나**와 **어떤 도구를 어떤 상황에 썼나**를 정리한다.
폴더는 18:00 무렵 주제별로 다시 묶었다(§18). 파일 이름은 바꾸지 않았다.

## 폴더 지도

| 폴더 | 무엇 | SUMMARY |
|---|---|---|
| `jobs/` | 그날만 쓴 스크립트(이름 앞머리 = 용도). 계속 쓰는 도구는 `Docs/tools/` | 전체 |
| `outputs/setup/` | Jetson 전송(`up_*`) · prep(`prep_smac_1026_1~7`) · BT 미리보기 · Smac 매개변수 · CopyPath .so 확인 | §0 · §4 · §5 · §7 · §11 · §14 |
| `outputs/planner_offline/` | 계획기 오프라인 비교 원문: `d5/`(inflation · 패딩) · `d1/`(Lattice) · `hyb/`(REEDS_SHEPP) · `fork/`(Jazzy 비용 상한 포크) · `cause/`(smoother 끔) · **`sep/` · `sep_fork/`(변형마다 프로세스 따로 — 유효 판)** | §1 · §3 ~ §6 |
| `outputs/rev_sign/` | 반전 순간 휠 부호 오차(v1 · v2 = 무효 판) | §2 |
| `outputs/drives/<주행>/` | 주행 하나의 모든 것: 러너 `run_*` · nav2 로그 · 사건 `nav_events_ms_*` · 상자 여유 `anal_contact_*` · 경로 `anal_plan_series_*` · 정지 `anal_stops_*` · 굽은 곳 `anal_bend_dev_odom_*` · `f0_*/`(F0 관찰 · 메모리) | §7.3 · §7.4 · §9 · §11 · §15 · §16 |
| `outputs/mppi_sim/` | MPPI 오프라인 시뮬(굽은 곳 `sim_corner_*`, 정지 장면 `sim_stall_*`) | §10 |
| `outputs/compare/` | 주행 여럿을 함께 본 것: 상자 옆 비교 그림 기록 · 멈칫 사건 4 주행 · W3 돌아서기 | §8 · §12 · §13 |
| `outputs/fig_video/` | 영상 도구 생성 기록(fig_drive_video · fig_rviz_video) | §8 · §12 · §16 · §17 |
| `figures/planner_offline/<변형>/` | 오프라인 비교 장면 6 장씩(변형 폴더 이름 = `outputs/planner_offline` 의 변형) | §1 · §3 ~ §6 |
| `figures/compare/` | B0 대 Smac 상자 옆 그림 · 영상 정지 장면 | §8 · §12 |
| `figures/real_video/` | 실제 촬영 장면 묶음 · 합본 확인 장면 | §16 · §17 |
| `videos/`(git 제외) | 완성 영상(합본 · 비교). 중간 파일 `videos/real/` 은 사용자 지시로 삭제(§18.1) | §8 · §12 · §16 · §17 |
| `bags/`(git 제외) | 주행 bag tgz 5 개 · Jetson 로그 `logs_<주행>/` | §7 ~ §15 |

주행 이름: `f2sh1 · f2sh2` = Smac Hybrid + MPPI 14 · 10(b910) · `f2sa1 · f2sa2` = Smac + MPPI 28 · 5(b910) · `f2sa3` = Smac + 28 · 5(no5 서쪽 통로 포함).

## 도구 — 상황 → 도구 → 나온 값 → 그때의 추론(✔ 맞음 · ✘ 틀림 · ？ 미확인)

| § | 상황 | 도구 | 나온 값(원문) | 추론 |
|---|---|---|---|---|
| §0 · §7.2 | 재부팅으로 /tmp prep 소실 | `jobs/up_prep_1026.sh` | 해시 '같음'(`setup/up_prep_1026.txt`) | ✘ CRLF 사본끼리 비교였음 → CR 빼고 재전송(`up_prep_1026b.txt`) |
| §1 | 전역 inflation 완만화가 경로를 틈 가운데로? | `Docs/tools/plan_offline/`(gen_yaml INFL_R/K) | k 1.0 · 0.5 → 상자 여유 0.0 cm(`planner_offline/d5/`) | ✘ 완만할수록 더 붙음. 첫 판은 CRLF 로 무효(`d5/invalid_crlf/`) |
| §1.3 | 전역 패딩 0.03 · 0.05 | 같은 도구 | +0~1.4 cm(`d5/run_pad0.0*.txt`) | ✔ 패딩은 바닥만 정함 |
| §2 | 반전 순간 FG 부호 오차 크기 | `jobs/anal_rev_sign.py` | 최대 3.1 mm(`rev_sign/anal_rev_sign.txt`) | ✔ 지금 속도에선 무시 가능. v1(IMU 축) · v2(EKF yaw) 기준 잘못 → 무효 판 보존 |
| §3 | Smac Lattice 오프라인 | plan_offline | 평균 +0.55 cm(`planner_offline/d1/`) | ✘ 변형끼리 같음 — 뒤에 static 공유 탓으로 판명(§6.1) |
| §4 | REEDS_SHEPP Hybrid | plan_offline | RS + 해석 1.0 m 평균 +3.1 · 나빠짐 0(`planner_offline/hyb/`) | ？ 한 서버 여러 변형 판 — §6.3 에서 단독으로 다시 잼(같은 값) |
| §5 | Jazzy 비용 상한 이식 | `jobs/up_smac_fork_1026.sh` + 패치 `Docs/06_planner/smac_fork/` | 이득 없음(`planner_offline/fork/`) | ✔ 이식은 작동 · 여유는 안 늚 |
| §6 | cost_penalty 가 왜 안 먹나 | `Docs/tools/plan_offline/run_variants.sh`(변형마다 프로세스) | `planner_offline/sep/anal_all.txt` | ✔ 원인 = 도구(Smac static 상태 공유). 유효 결과는 sep · sep_fork 만 |
| §7 | planner:=smac 배포 · prep | `jobs/up_smac_nav_1026.sh` · `jobs/prep_smac_1026.sh` | PREP_OK(`setup/prep_smac_1026_3.txt`) | ✔ 첫 배포 heredoc '\n' 깨짐 → Edit 로 고침 |
| §7.3 · §7.4 | b910 실제 상자 여유 | `Docs/debug_log/2026-10-23/jobs` 계열 anal_contact · anal_plan_series · anal_track_dev | 18.4 · 10.8 cm(`drives/f2sh1` · `f2sh2`) | ✔ 계획 경로는 멀어짐, 남은 손실 = 굽은 곳 깎기 |
| §8 · §12 | B0 대 Smac 상자 옆 비교 | `jobs/fig_box_compare.py` | `figures/compare/box_compare_b0_smac*.png` | ✔ 첫 판 점선이 막힘 전 경로였음 → 고침 |
| §9 | 깎기가 컨트롤러 탓인가 | `jobs/chk_dev_frame_f2sh2.py` | odom 좌표 이탈 +15.7 cm(`drives/f2sh2/`) | ✔ MPPI 가 받은 경로 안쪽을 깎음 |
| §10.1 | 시뮬이 왜 재현 안 되나 | `jobs/chk_cmd_vs_motion_f2sh2.py` | 바깥 바퀴 0.086 = 한계 0.085(`drives/f2sh2/`) | ✔ 펌웨어 비례 축소 → 시뮬 `wheel_max` 추가 |
| §10.3 ~ §10.5 | MPPI 변형별 깎기 | `jobs/run_sim_corner_1026{,b,c,d}.sh` + `jobs/anal_sim_corner_summary.py`, 시뮬 `Docs/tools/anal_mppi_sim.py` | 28 · 5 최악 19.8 → 11.2(`mppi_sim/sim_corner_1026d_summary.txt`) | ？ 평균 차는 구분 불가, 꼬리만 줄어드는 경향 |
| §10.7 | 28 이 정지를 부르나 | `jobs/run_sim_stall_1026.sh` | 정지 0(`mppi_sim/sim_stall_1026_summary.txt`) | ？ 시뮬이 실제 정지를 재현 못함 |
| §11 | 28 · 5 실주행 A/B | `jobs/up_mppi_path_1026.sh` · `jobs/anal_bend_dev_odom.py` | 안쪽 이탈 +4.6 · +1.6 cm(`drives/f2sa1` · `f2sa2`) | ✔ 깎기 줄어듦(2/2) |
| §13 | 28 · 5 에 멈칫이 있었나 | `2026-10-21/jobs/anal_dip_events.py` · `jobs/chk_w3_turn.py` | `compare/anal_dip_events_*` | ✔ 1 s 넘는 '이유 없는' 정지 없음 |
| §14 | 28 · 5 채택 배포 | `jobs/up_params_1026.sh` | sha 7bce0cb94734(`setup/up_params_1026.txt`) | — |
| §15 | 서쪽 통로 추종 비교 | `jobs/anal_corridor_track.py` | 이탈 중앙 4.1 → 1.0 cm(`drives/f2sa3/`) | ？ 1 회씩 — NavFn 경로를 바짝 따른 탓(추정) |
| §16 | 실제 촬영 판독 · 통로 폭 | `jobs/fig_real_tiles.py` · `jobs/anal_corridor_gap.py` | 통로 0.50 m 두 날 같음(`drives/f2sa3/anal_corridor_gap.txt`) | ✔ f2rp4 비교 유효 |
| §17 | 실제 + RViz 합본 | `Docs/tools/fig_rviz_video.py` + ffmpeg | `videos/f2sa3_real_rviz_*_hd_x2.mp4` | 첫 판 -t 위치 실수(§17.1) |
| §19 | 통로에서 Smac 실패 · NavFn 성공 차이 | `jobs/chk_corr_paths.py` · `jobs/chk_smac_fail_cells.py` | Smac 도 16:13:08 통로 경로 냄 · 실패 3/5 는 목표 자세 차체 아래 치명(`drives/f2sa3/chk_*`) | ✘ 처음 답(통로가 Smac 에 불가능) 틀림 · 나머지 2 번 ？ |
| — | bag · 로그 가져오기 | `jobs/get_logs_<주행>.sh` | `bags/logs_<주행>/` → `outputs/drives/<주행>/nav2_*.log` | — |
