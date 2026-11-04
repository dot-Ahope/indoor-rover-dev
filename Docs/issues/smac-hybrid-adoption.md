# Smac Hybrid 채택 — 오프라인 비교 · 포크 · 실주행 · tolerance 0.35 (9 기: 10-26 §0~§8 · §19 · §20 · §22, 10-27 §1~§11 · §13 · §27 · §28)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **부분 해결(시험 구성 채택 · 기본 아님)** — b910 상자 옆 실제 최소 여유 B0(NavFn) 15.2 · 5.5 · 3.1 cm → Smac 18.4 · 10.8(MPPI 14 · 10) · 14.6 · 14.9 cm(28 · 5), 서쪽 통로 남행은 tolerance 0.35 로 Smac 이 받아 좁은 곳 여유 0.8 → 4.1 cm(1 회). 남은 것: 통로 **북행 · 좁은 곳 안 출발**은 출발 자세에 따라 Smac 이 실패 → NavFn 대체(nav2 로그 Smac 실패 f2st1 3 · f2tf1 0 · f2tt1 0, 10-28 f2tt2 막힘 재계획 1), 러너 목표 방향은 NavFn 경로 끝에서 옴, launch 기본은 `planner:=navfn`, 계획서 §7 종료 조건(결과 문서 · 게이트 판)은 안 채움 | 10-26 §0(오늘 순서) ~ 10-27 §28. 앞 이야기 10-23 §15 · §21 · §22(→ [B0 카드](path-tracking-replan-b0.md)) | [10-26 §4](../debug_log/2026-10-26/SUMMARY.md) 사용자 "Smac Hybrid는 진행하고 싶다." — 같은 날 §3.2 에서 내가 'Phase P 멈춤 · B0 유지' 를 제안한 직후 | [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 102~125 · 203 행 `planner:=navfn\|smac`(커밋 `36e59493`) · [`copy_path_action.cpp`](../../ros2_ws/src/rover_navigation/src/copy_path_action.cpp) `step` 포트 · [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 737~763 행 SmacHybrid(REEDS_SHEPP · cp 3.0 · 해석 1.0 m · 2.0 s · 캐시 끔, 10-26) · 739 행 tolerance 0.35(커밋 `8b89ab51`, 10-27) · [`prep_patrol.sh`](../tools/prep_patrol.sh) 16~17 행 `NAV_ADD` · 오프라인 도구 [`run_variants.sh`](../tools/plan_offline/run_variants.sh) · 패치 2 개 [`smac_fork/`](../06_planner/smac_fork/)(주행 안 씀) | [전역 계획기 NavFn vs Smac](global-planner-choice.md)(09-14 ~ 15 첫 비교 · 이 카드의 앞) · [경로 추종 · 재계획 → B0](path-tracking-replan-b0.md)(B0 수치 · 10-23 오프라인 첫 판, 무효 처리) · [MPPI 굽은 곳 깎기 · PathAlign 28/5](mppi-corner-cut-pathalign.md)(10-26 §9~§14 · §15 통로 — 같은 날 다른 줄기) · [BT 끝 방향 CopyPath](bt-copypath-end-yaw.md)(Smac 블록 · step 재표본) · [F2 기준선 no5](f2-baseline-no5.md)(no5 코스 · 비교 대상 f2rp4) · [PathBlockedAhead only_new](pathblocked-only-new.md)(Smac 경로 막힘 재계획) · [통과 폭 판단](passage-width-analysis.md)(서쪽 통로 폭 0.50 m) · [SLAM stamp 정체](slam-stamp-freeze.md)(10-27 f2tf1 · f2tt1 구성) · [빠른 prep](prep-fast-startup.md)(설치본 링크 · 재전송) · [F2.5 장소 이름 이동](f25-place-navigation.md) · [nvblox 층 TF 실패](nvblox-layer-tf-drop.md) (9 기) |

**한 줄**: B0(NavFn) 의 상자 옆 근접을 계획기 쪽에서 줄이려 10-26 오전에 오프라인으로 전역 비용 완만화 · 패딩 · Smac Lattice · Smac Hybrid 를 차례로 쟀고 모두 기준(+5 cm · 나빠짐 0) 미달이었다. 사용자 결정으로 Hybrid 를 계속 파며 Jazzy 의 해석 확장 비용 상한을 1.1.20 에 이식한 포크까지 만들었으나 이득이 없었고, '왜 cost_penalty 가 안 먹나' 를 쫓다가 **내 도구 결함**을 찾았다 — 1.1.20 Smac 은 운동 표 · 휴리스틱 표가 static 이라 한 planner_server 에 변형을 여럿 올리면 설정이 섞인다(10-23 · 10-26 오전 비교 대부분 무효). 변형마다 프로세스를 따로 띄워 다시 재니 **설치판 REEDS_SHEPP + 해석 확장 1.0 m** 가 평균 +3.1 cm · 나빠짐 0 으로 가장 나았고(여전히 기준 미달), 이 구성으로 `planner:=smac`(실패 시 NavFn)을 만들어 실주행하니 b910 상자 옆이 18.4 · 10.8 cm 로 B0 보다 넓었다. 서쪽 통로에선 Smac 이 5 번 실패해 NavFn 원경로로 지나며 0.8 cm 까지 붙었다. 실패 순간을 나눠 보니 '목표 방향' 탓이 아니었고(13 방향 × 6 순간), 남행 한 번은 탐색이 목표 5.7 cm 앞까지 가고도 **수락 조건(tolerance 를 비용 곱한 휴리스틱과 비교)** 에서 떨어진 것이었다. tolerance 0.25 → 0.35 는 상자 장면을 하나도 바꾸지 않고 그 남행을 살렸고, f2st1 에서 통로 남행이 Smac 경로로 바뀌어 4.1 cm · 24.7 s 가 됐다. 북행(남쪽 주머니 · 좁은 곳 안 출발)은 출발 자세 쪽 원인으로 남아 실패하면 NavFn 이 맡는다 — 같은 날 뒤 두 주행(f2tf1 · f2tt1)은 북행도 Smac 이 받아 실패 0 이었으니 '늘 실패' 가 아니라 출발 자세에 달린 경계다.

## 1. 증상
- **10-23 B0 결함**(→ [B0 카드](path-tracking-replan-b0.md)): b910 복귀 상자 옆 실제 여유 15.2 · 5.5 · 3.1 cm, 다시 그린 NavFn 경로 자체 여유 8.9~13.3 cm. 상자 북쪽 틈 0.70~0.90 m 인데 경로는 꺾임 안쪽으로 짧게 돎(10-23 §22.2, [`anal_box_gap.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_box_gap.txt)).
- **10-26 §15 f2sa3**(Smac 구성의 첫 no5): 서쪽 통로 계획 5 번 모두 `SmacHybrid: failed to create plan` → NavFn 대체, 남행 좁은 곳 로컬 정확 여유 **0.8 cm** · Wait 7.1 s · 1 s 넘는 정지 5 번 15.3 s([`run_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/run_f2sa3.txt) · [`anal_band_run_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_band_run_f2sa3.txt) · [`nav2_f2sa3.log`](../debug_log/2026-10-26/outputs/drives/f2sa3/nav2_f2sa3.log)).
- **10-26 §19** 사용자: "둘 다 planner 일 뿐이고 나오는 것은 컨트롤러가 하는 것인데 왜 플래너가 바뀌었다고 가능해진 것인가?" · "시각화된 영상을 보면, 둘 다 나갈 수 있는 경로를 준 것처럼 보여서" — Smac 은 왜 실패하고 NavFn 은 됐나.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-26 §0 | Jetson 재부팅 뒤 prep 3 개 재전송 | '저장소와 같음' 해시 | ⚠ §7.2 정정: 작업 사본(CRLF)끼리 비교한 해시였음 | [`up_prep_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_prep_1026.txt) |
| 10-26 §1 · §1.1 | **D5 선언 → 결과**: 전역 inflation 완만화(k 1.0 · 0.5, 반경 0.70 · 1.0)로 NavFn 경로가 틈 가운데로 가나 | 차체 ↔ 상자 13.3 · 8.0 · 9.1 · 9.0 → **0.0 · 0.0 · 0.0 · 0.0**, 길이 −6~−15 %. 단면 x 1.2 비용 차 k 2.0 28 · k 1.0 16 · k 0.5 8 | **판정 ① ✘ — 반대로 더 붙음**(완만할수록 곁 대 가운데 차가 줄어 길이가 이김). 첫 판은 CRLF 로 정리 단계가 안 돌아 무효(내 도구 실수) | [`d5_table.txt`](../debug_log/2026-10-26/outputs/planner_offline/d5/d5_table.txt) · 무효 판 `outputs/planner_offline/d5/invalid_crlf/` |
| 10-26 §1.2 · §1.3 | D5b: 전역 패딩 0.03 · 0.05 | 내접 칸 17 981 → 22 680(적용 ✔), NavFn 여유 +0~1.4 cm | ✘ — 패딩은 '바닥' 만 정함, 경로는 이미 그 띠 밖 | [`anal_pad0.05.txt`](../debug_log/2026-10-26/outputs/planner_offline/d5/anal_pad0.05.txt) |
| 10-26 §3 · §3.1 · §3.2 | **D1 Lattice**(diff 원형) cp {2, 5} × 회전 벌점 {5, 20} + 후진판, 해석 0.5 · 1.0 m 판 | 6 변형이 장면마다 **같은 경로**, 평균 +0.55(해석 0.5 m 판 +2.5 · 한 장면 −4.2), 서쪽 통로 남행 실패 | '해석 확장이 경로를 정함' 추정 → §3.2 종합 **'Phase P 멈춤 · B0 유지' 제안**. ⚠ §6.1: 한 서버 여러 변형이라 변형끼리 같은 것은 도구 탓 — 이 읽기 무효 | [`anal_d1.txt`](../debug_log/2026-10-26/outputs/planner_offline/d1/anal_d1.txt) · [`run_d1a.txt`](../debug_log/2026-10-26/outputs/planner_offline/d1/run_d1a.txt) |
| 10-26 §4 · §4.2 | 사용자 "Smac Hybrid는 진행하고 싶다." → 설치판 매개변수 조회 · REEDS_SHEPP 변형 | `analytic_expansion_max_cost` **없음**(1.1.20). RS + 해석 1.0 m: 13.6 · 14.4 · 12.3 · 11.4(평균 +3.1 · 나빠짐 0). 서쪽 통로 RS 전부 실패 | 'RS + 해석 1.0 m 최선'(이 값은 §6.3 단독 판에서도 같음). 첫 RS 판은 기동 30 s 초과를 못 보고 앞 결과를 읽음(내 실수 → 대기 180 s) | [`chk_smac_params.txt`](../debug_log/2026-10-26/outputs/setup/chk_smac_params.txt) · [`anal_rs.txt`](../debug_log/2026-10-26/outputs/planner_offline/hyb/anal_rs.txt) · 무효 `outputs/planner_offline/hyb/invalid_wait30/` |
| 10-26 §5 · §5.1 · §5.2 | **포크**: Jazzy `getAnalyticPath` 의 비용 상한(max_cost 200, 넘는 칸에 들어갔다 나오면 곡선 버림)을 1.1.20 에 이식, Jetson `~/smac_ws` 빌드 2 분 44 초 | 적재 확인(/proc/maps = smac_ws .so · 매개변수 200.0), 같은 판 두 번 결정적. 포크 RS 해석 1.0 m 는 rp2 **14.4 → 4.3 cm**, max_cost 60 · 100 · 200 사이 대부분 같은 경로 | ✘ — 이식은 작동, 상자 여유 이득 없음. 'cp 가 안 먹는 원인은 해석 확장만이 아님' | [`up_smac_fork_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_smac_fork_1026.txt) · [`anal_chk_fork1.txt`](../debug_log/2026-10-26/outputs/planner_offline/fork/anal_chk_fork1.txt) · [`run_chk_fork1.txt`](../debug_log/2026-10-26/outputs/planner_offline/fork/run_chk_fork1.txt) · 패치 [`nav2_smac_planner_rover_maxcost.patch`](../06_planner/smac_fork/nav2_smac_planner_rover_maxcost.patch) |
| 10-26 §6 · §6.1 | cost_penalty 가 왜 안 먹나: 가설 smoother(smooth_path false `_NS` 판) | 끈 판도 cp 1.2 · 3.0 · 6.0 같은 경로 → 기각. **단서**: 같은 설정 `Smac_R10_C30_A10_RS` 가 rp2 에서 14.4(§4.2) · 8.6(§6.1) — 차이는 같이 올린 변형뿐 | **내 도구 결함**: `node_hybrid.hpp:446` `static HybridMotionTable motion_table` 등 static → 한 서버의 Smac 변형들이 한 설정을 공유. 10-23 §22.2 · 10-26 §3 · §3.2 · §4.2 · §5.1 · §6.1 의 변형 간 비교 **무효**(NavFn · Smac 하나만 올린 판은 유효) | [`run_ns.txt`](../debug_log/2026-10-26/outputs/planner_offline/cause/run_ns.txt) · [`anal_ns.txt`](../debug_log/2026-10-26/outputs/planner_offline/cause/anal_ns.txt) · 아래 §5 실수 1 |
| 10-26 §6.2 · §6.3 | **변형마다 프로세스 따로** 다시 잼(설치판 · 포크) | 아래 §4.3 표 — cp 는 경로를 바꾸나 여유를 꾸준히 안 올림. 최선 **RS cp 3.0 해석 1.0 m 13.6 · 14.4 · 12.3 · 11.4(+3.1 · 나빠짐 0)**. 포크 단독도 rp2 4.3. 서쪽 통로 Hybrid 전부 실패 · Lattice 북행만. 비용 골(최소 비용 선)이면 차체 ↔ 상자 약 18 cm | 판정 ✘(동시 만족 없음), 가장 가까운 후보 = 설치판 `Smac_R10_C30_A10_RS`. cp 를 올려도 여유가 안 느는 이유 미확인 | [`sep/anal_all.txt`](../debug_log/2026-10-26/outputs/planner_offline/sep/anal_all.txt) · [`sep_fork/anal_all.txt`](../debug_log/2026-10-26/outputs/planner_offline/sep_fork/anal_all.txt) · 도구 [`run_variants.sh`](../tools/plan_offline/run_variants.sh) |
| 10-26 §7 | 사용자 "A진행" → `planner:=smac` 구현(BT 사본 `PlanSmacOrNavFn`, CopyPath step 0.03, SmacHybrid = §6.3 최선 + 시간 상한 2.0 s · 캐시 끔), 배포 | 첫 배포 launch 문법 오류(파이썬 heredoc '\n' 함정 — 스택 꺼진 동안이라 쓰인 적 없음) → Edit 로 고쳐 재배포, CopyPath .so 재빌드 확인. 설치본 링크 유지 | 주행 선언 §7.1: f2sh1 · f2sh2(b910) · f2sh3(no5), 판정 ② 상자 옆 실제 ≥ 8 cm(2 회) 등 5 개 | [`up_smac_nav_1026_b.txt`](../debug_log/2026-10-26/outputs/setup/up_smac_nav_1026_b.txt) · [`chk_copypath_so.txt`](../debug_log/2026-10-26/outputs/setup/chk_copypath_so.txt) · [`bt_smac_preview.xml`](../debug_log/2026-10-26/outputs/setup/bt_smac_preview.xml) |
| 10-26 §7.2 | prep 첫 시도 실패 | `set: +: invalid option · syntax error` — §0 재전송이 CRLF 사본 | CR 빼고 재전송 → PREP_OK(BT 사본 PlanSmacOrNavFn 1 · step 1 · REEDS_SHEPP · cp 3.0 · 해석 1.0 · 2.0 s) | [`prep_smac_1026_2.txt`](../debug_log/2026-10-26/outputs/setup/prep_smac_1026_2.txt) · [`up_prep_1026b.txt`](../debug_log/2026-10-26/outputs/setup/up_prep_1026b.txt) · [`prep_smac_1026_3.txt`](../debug_log/2026-10-26/outputs/setup/prep_smac_1026_3.txt) |
| 10-26 §7.3 | **f2sh1**(b910, Smac + MPPI 14 · 10) | 3/3 · 205.8 s. SimpleSmoother 호출 0 = BT 경로 전부 Smac. 막힘 재계획 경로 18.5 cm(NavFn 판 8.9~13.3). 실제 최소 갈 때 18.9 · **복귀 18.4 cm**. 후진 지령 38 개 · 1.9 s | 판정 ② ✔(1 회째) | [`run_f2sh1.txt`](../debug_log/2026-10-26/outputs/drives/f2sh1/run_f2sh1.txt) · [`anal_contact_f2sh1_d30.txt`](../debug_log/2026-10-26/outputs/drives/f2sh1/anal_contact_f2sh1_d30.txt) · [`anal_plan_series_f2sh1.txt`](../debug_log/2026-10-26/outputs/drives/f2sh1/anal_plan_series_f2sh1.txt) |
| 10-26 §7.4 | **f2sh2** 반복 | 3/3 · 201.7 s. 복귀 재계획 1 회(TF 외삽 중단 뒤) 경로 17.1 cm, 실제 **10.8 cm**(상자 동쪽 대각선, 로버가 경로보다 상자 쪽 +13~15.6 cm) | ② ✔(2 회 모두 ≥ 8). 남은 손실 = MPPI 굽은 곳 깎기 → [MPPI 카드](mppi-corner-cut-pathalign.md) | [`run_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/run_f2sh2.txt) · [`anal_contact_f2sh2_d30.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/anal_contact_f2sh2_d30.txt) · [`anal_plan_series_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/anal_plan_series_f2sh2.txt) |
| 10-26 §8 | 시각화 — f2sh3(no5)는 통로에 사람이 있어 미룸(사용자) | B0 경로 y ≈ 0.25~0.30, Smac y ≈ 0.31~0.36 · 더 큰 호 | 첫 판 점선이 막힘 전 경로였음 → '최소 여유 순간 경로' 로 고침 | [`fig_box_compare.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare.txt) · 그림 [`box_compare_b0_smac.png`](../debug_log/2026-10-26/figures/compare/box_compare_b0_smac.png) · [`box_compare_b0_smac_mppi.png`](../debug_log/2026-10-26/figures/compare/box_compare_b0_smac_mppi.png) |
| 10-26 §11 ~ §15(이 카드는 계획 몫만) | MPPI 28 · 5 A/B(f2sa1 · f2sa2) · 채택 · f2sa3(no5) | f2sa1 복귀 출발 Smac 'no valid path' → NavFn 대체 1(설계대로). f2sa3 서쪽 통로 Smac 실패 5 → NavFn, 스무딩 5/5 충돌 → 원경로 | f2sh3 대신 f2sa3 이 Smac 구성의 첫 no5 가 됨(MPPI 도 바뀐 상태) | [`nav2_f2sa1.log`](../debug_log/2026-10-26/outputs/drives/f2sa1/nav2_f2sa1.log) · [`nav2_f2sa3.log`](../debug_log/2026-10-26/outputs/drives/f2sa3/nav2_f2sa3.log) · 본체 [MPPI 카드](mppi-corner-cut-pathalign.md) |
| 10-26 §19 | 사용자 질문에 '통로는 차체 계획기로 못 지남' 이라 답함 → 판별 | 통로 창 경로 출처(점 간격): 16:11:55~16:12:59 전부 0.025 = NavFn, **16:13:08.65 Smac(0.074) 이 좁은 곳을 지남**. 실패 5 · 성공 1 순간 칸: 남행 실패 2 번 목표 차체 아래 치명 18 · 22 | 첫 답 **틀림**(Smac 도 통로 경로를 낸 적 있음). '실패 3/5 = 목표 자세 차체 아래 치명' 읽기 → ⚠ §20.1 에서 틀림 | [`chk_corr_paths.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/chk_corr_paths.txt) · [`chk_smac_fail_cells.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/chk_smac_fail_cells.txt) |
| 10-26 §20 · §20.1 | **목표 방향 시험**(선언 → 결과): 6 순간 × 목표 방향 13 가지 = 78 질의, 실주행 값 · Smac 하나만 올린 서버 | 재현 ✔(실패 5 · 성공 1). 실패 순간은 **모든 방향 실패**(65/65), 성공 순간은 목표 아래 치명 2~5 칸 방향까지 **모두 성공**(13/13). 실패까지 0.01~0.06 s(3 순간) · 0.9~1.5 s(2 순간), 상한 2.0 s 전 | **가설 H(목표 방향) 기각**. 내 칸 지표(직사각형 안 전부)는 Smac 충돌 판정과 다름. 남은 후보 = 출발 자세 · 그 순간 지도 | [`anal_goal_yaw.txt`](../debug_log/2026-10-26/outputs/planner_offline/goal_yaw/anal_goal_yaw.txt) · [`run_goal_yaw.txt`](../debug_log/2026-10-26/outputs/planner_offline/goal_yaw/run_goal_yaw.txt) · 그림 [`goal_yaw.png`](../debug_log/2026-10-26/figures/planner_offline/goal_yaw.png) |
| 10-26 §22 | **탐색 시각화**: 1.1.20 원본 + 기록만 넣은 진단 빌드 `~/smac_dbg_ws` 로 6 순간 재질의 | 재현 ✔. 방문 노드 340 556 · **1** · 332 907 · 14 551 · 14 355 · 성공 23 | '가장 좁은 곳이 탐색의 벽'(추정) — ⚠ 10-27 §2: 16:11:56 은 좁은 곳을 **넘었음**(정정) | [`run_expdbg.txt`](../debug_log/2026-10-26/outputs/planner_offline/goal_yaw/run_expdbg.txt) · 기록 [`exp_expdbg.tgz`](../debug_log/2026-10-26/outputs/planner_offline/goal_yaw/exp_expdbg.tgz) · 그림 [`smac_expansion.png`](../debug_log/2026-10-26/figures/planner_offline/smac_expansion.png) · 패치 [`nav2_smac_planner_rover_expdump.patch`](../06_planner/smac_fork/nav2_smac_planner_rover_expdump.patch) |
| 10-27 §1 · §2 | 선언 → **부모 사슬 · 출발 ↔ 지도 바꿔 끼우기** | 16:11:56 통로 남쪽 노드 989 개 모두 좁은 곳 창을 지나 옴(창 밖 우회만 0), 목표에서 최소 **5.7 cm**(방향 차 +15°) · 0.25 m 안 173 개인데 실패. 바꿔 끼우기 10 쌍 중 9 쌍 '출발 · 목표가 정함', 16:12:59 만 지도도 영향 | 실패 5 번은 한 원인 아님: (a) 좁은 곳 안 · 남쪽 끝 출발은 거의 못 뻗음 (b) 북쪽 입구 출발 남행은 넘고도 **목표 수락 조건**에서 실패(추정) | [`anal_parent_chain_115653.txt`](../debug_log/2026-10-27/outputs/parent_chain/anal_parent_chain_115653.txt) · [`chk_goal_reach_1026.txt`](../debug_log/2026-10-27/outputs/parent_chain/chk_goal_reach_1026.txt) · [`anal_swap.txt`](../debug_log/2026-10-27/outputs/swap/anal_swap.txt) · 그림 [`parent_chain_115653.png`](../debug_log/2026-10-27/figures/parent_chain_115653.png) |
| 10-27 §2.1 · §3 | 탐색 영상 → 사용자 지적으로 같은 목표끼리 다시 | 10-26 영상은 남행 실패와 북행 성공을 붙여 비교가 안 됐음 → 북행 3 순간 · 남행 1 순간(가장 가까운 노드 사슬 표시) | 영상은 설명용(판정 아님) | 그림 [`smac_expansion_north_end.png`](../debug_log/2026-10-27/figures/smac_expansion_north_end.png) · [`smac_expansion_south_end.png`](../debug_log/2026-10-27/figures/smac_expansion_south_end.png) · 기록 [`fig_smac_expansion_north.txt`](../debug_log/2026-10-27/outputs/fig_video/fig_smac_expansion_north.txt) |
| 10-27 §4 | 그림 읽기 질의 · **Smac 충돌 판정 소스 확인** | `collision_checker.cpp:90~157`: 중심 칸 ≥ 253 이면 충돌, 아니면 둘레 선 칸 최대 ≥ 254 일 때만 충돌. 목표 4 중심 칸 92, 서쪽 두 열 99 | 10-26 §20.1 의 '소스 미확인' 해소. 목표 방향 −100° 는 러너가 NavFn 경로 끝으로 자동으로 붙인 값 | [`goal_cell_cost.txt`](../debug_log/2026-10-27/outputs/swap/goal_cell_cost.txt) |
| 10-27 §5 · §5.1 · §6 | 선언 → **tolerance · cost_penalty 재질의**(V0~V4, 설치판, 변형마다 따로) | 16:11:56 남행: tol 0.25 실패 1.09 s → **0.35 성공 0.02 s**(끝 10.7 cm · +15°), cp 1.5 도 성공이나 끝 방향 **+105°**, 16:12:59 북행 cp 1.5 는 **14.51 m** 우회. 나머지 3 순간 모두 실패 그대로 | 가설 (b) **지지** — 수락 조건이 막고 있었음. cp 낮추기는 후보에서 뺌. tolerance 는 거리 아닌 휴리스틱 값과 비교(소스) | [`anal_tolcp.txt`](../debug_log/2026-10-27/outputs/tolcp/anal_tolcp.txt) · [`run_V1.txt`](../debug_log/2026-10-27/outputs/tolcp/run_V1.txt) · 그림 [`tolcp_paths.png`](../debug_log/2026-10-27/figures/tolcp_paths.png) |
| 10-27 §7 | 같은 순간 탐색 영상(기준 · tol 0.35 · cp 1.5) | 방문 340 556 대 **1 210** · 1 154 | 셋 다 같은 길로 목표 근처까지 감, 기준만 못 끝냄 | 그림 [`smac_expansion_tol_end.png`](../debug_log/2026-10-27/figures/smac_expansion_tol_end.png) · [`run_V1.txt`](../debug_log/2026-10-27/outputs/tolcp_exp/run_V1.txt) |
| 10-27 §8 · §8.1 | 선언 → tol 0.35 가 10-23 상자 4 · 통로 2 장면을 나쁘게 하나 | 상자 4 장면 0.25 · 0.35 **경로 점까지 같음**, 10-23 통로 남행 g4 는 0.35 에서 새로 성공(치명까지 3.6 cm · NavFn 0.0), 북행 g5 실패 그대로 | 판정 ② 통과 → tol 0.35 주행 후보 | [`anal_W0.txt`](../debug_log/2026-10-27/outputs/tol_box/anal_W0.txt) · [`anal_W1.txt`](../debug_log/2026-10-27/outputs/tol_box/anal_W1.txt) · [`chk_west_g4_end.txt`](../debug_log/2026-10-27/outputs/tol_box/chk_west_g4_end.txt) |
| 10-27 §9 · §10 | 러너 소실 복구 · prep 재전송 · tolerance 0.35 배포(커밋 `8b89ab51`) · prep | 전송 4 파일 PC HEAD blob 과 같음 · CR 0, 설치본 nav2_params 는 **일반 파일**(링크 아님 — 둘 다 덮음). PREP_OK +85 s · tolerance 0.35 확인 | 주행 선언 f2st1(§9.1 ①~⑤) | [`up_prep_params_1027.txt`](../debug_log/2026-10-27/outputs/setup/up_prep_params_1027.txt) · [`prep_smac_1027_1.txt`](../debug_log/2026-10-27/outputs/setup/prep_smac_1027_1.txt) |
| 10-27 §11 | **f2st1**(no5, Smac tol 0.35) | 8/8 · 427.5 s. Smac 실패 3 번 **모두 목표 5(북행)**, 목표 4(남행) Smac 실패 0. 남행 좁은 곳 최소 **4.1 cm**(f2sa3 0.8), 전체 최소 2.9 cm(북행 NavFn 구간) · < 2.7 cm 0 프레임. 1 s 넘는 정지 1 번 4.7 s(상자 막힘 → Wait). 복귀 상자 16.3 cm. 목표 4 · 5 시간 24.7 · 31.9 s(f2sa3 39.7 · 49.8) | 판정 ①~⑤ 통과(③ 은 2.9 = 경계값). 북행은 출발 쪽 원인으로 남음 | [`run_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/run_f2st1.txt) · [`nav2_f2st1.log`](../debug_log/2026-10-27/outputs/drives/f2st1/nav2_f2st1.log) · [`anal_band_run_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/anal_band_run_f2st1.txt) · [`anal_stops_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/anal_stops_f2st1.txt) · [`anal_contact_f2st1_d30.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/anal_contact_f2st1_d30.txt) · 그림 [`f2st1_summary.png`](../debug_log/2026-10-27/figures/f2st1_summary.png) |
| 10-27 §13 | 사용자 "오늘자 주행은 Smac 실패하여 NavFn 으로 주행한 것은 없는 것이지?" → 경로 출처 · 영상 밝은 판 | **있음**: 북행 11:21:02 · 11:21:06 · 11:21:12 세 번 NavFn(0.025, /plan_smoothed 동반), 남행 11:20:37.62 · 목표 6 11:21:34 은 Smac | 영상 도구에 `FIG_STYLE=light`(경로 출처별 색) | [`chk_corr_paths_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/chk_corr_paths_f2st1.txt) · 기록 `outputs/fig_video/fig_light_*.txt` |
| 10-27 §27 · §28 | f2tt1(같은 Smac 구성 + 다른 수정) 통로 세 순간 오프라인 재질의 · 탐색 영상 → 사용자 "통로 영상은 Smac 으로 계속, 탐색 영상은 중간에 실패 — 어떻게 된 것인가?" | 실주행은 세 순간 모두 Smac 성공(15:58:11.40 재계획 0.072 · 26 점). 재질의는 셋째가 실패 — 직전 지도(15:58:09.40 판)엔 경로 위 99 칸 4 개, 계획 시각 판(11.40)엔 0 이지만 'Starting point in lethal space'(출발 차체 외곽 최대 100, 벽까지 약 3 cm) | 재질의 조건(지도 판 · 출발 자세 mm · 도)이 실주행과 달랐던 경계 사례(추정 — 계획기 내부 지도는 bag 에 없음). 영상 이름표를 '재질의 성공 / 실패(실주행은 성공)' 로 다시 | [`chk_replan_maps.txt`](../debug_log/2026-10-27/outputs/tt1_exp/chk_replan_maps.txt) · [`run_V1.txt`](../debug_log/2026-10-27/outputs/tt1_exp/run_V1.txt) · [`chk_corr_paths_f2tt1.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/chk_corr_paths_f2tt1.txt) · 그림 [`smac_expansion_tt1_end.png`](../debug_log/2026-10-27/figures/smac_expansion_tt1_end.png) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 전역 비용을 완만하게 하면 경로가 틈 가운데로(D5) | 10-26 §1 오프라인 k 1.0 · 0.5 | 13.3 · 8.0 · 9.1 · 9.0 → 0.0 × 4 | **기각** — 반대로 붙음(측정), 이유는 단면 비용 차(측정)로 설명 |
| 전역 패딩을 키우면 최소 여유가 는다(D5b) | §1.3 패딩 0.03 · 0.05 | +0~1.4 cm | **기각**(경로가 이미 띠 밖). 0.10~0.15 면 통로가 막힐 것은 추정 · 미시험 |
| Lattice(diff) 가 상자 · 통로에 낫다(D1) | §3 · §3.2(여러 변형 한 서버) → §6.3(따로) | 단독 판: Lattice C20 P5 +1.7 · 나빠짐 1, C50 P5 +0.7 · 2, 서쪽 통로 북행만 성공 | **기각**(기준 미달). §3 의 '변형끼리 같음 · cp · 회전 벌점 무효' 는 도구 결함으로 무효 |
| 1.1.20 해석 확장이 비용을 안 봐 cp 가 안 먹는다 | §5 Jazzy max_cost 이식 포크 | 이식 작동(rp2 경로 바뀜), 여유 이득 없음 | **기각**(주원인 아님) — 그리고 'cp 가 안 먹는다' 는 관찰 자체가 도구 결함이었음(§6.1) |
| 후처리 smoother 가 탐색 차이를 지운다 | §6.1 smooth_path false 판 | 같은 경로 | **기각**(단, 이 판도 여러 변형 한 서버 — 근거 약함) |
| 한 서버에 올린 Smac 변형들이 설정을 공유한다(도구 결함) | 소스 `node_hybrid.hpp:446` · `node_lattice.hpp:417` static, `a_star.cpp:115` 지도 크기 바뀔 때만 초기화 + 같은 설정이 함께 올린 변형에 따라 14.4 · 8.6 | §6.3 단독 판에선 cp 마다 경로가 달라짐 | **지지(소스 + 측정)** |
| Smac(RS · 해석 1.0)이 실주행 상자 옆 여유를 B0 보다 늘린다 | 10-26 §7.3 · §7.4 b910 2 회 | 18.4 · 10.8 cm(B0 15.2 · 5.5 · 3.1), 계획 경로 자체 17.1~18.5(NavFn 8.9~13.3) | **지지(2 회)** — 오프라인 평균 +3.1 보다 실주행 차가 큼: 실주행 재계획 출발 자리 · 지도가 오프라인 6 장면과 다름(추정) |
| 서쪽 통로는 차체 계획기로 지날 수 없다 | 10-26 §19 경로 출처 | 16:13:08.65 Smac 경로가 좁은 곳을 지남 | **기각** |
| Smac 통로 실패는 목표 방향(차체가 안 들어감) 탓 | §20 13 방향 × 6 순간 | 실패 순간은 모든 방향 실패, 성공 순간은 모든 방향 성공 | **기각** |
| 좁은 곳이 탐색의 벽이다 | 10-27 §2 부모 사슬 | 16:11:56 남쪽 노드 989 개 모두 좁은 곳을 지나 옴 | **기각(16:11:56)** · 좁은 곳 안 · 남쪽 끝 출발 순간들엔 '못 뻗음' 이 맞음(방문 1 · 14 551 · 14 355) |
| 출발 자세가 실패를 정한다 | §2 바꿔 끼우기 | 9/10 쌍 일치, 16:12:59 만 지도 영향 | **지지(대부분)** — 출발 칸에서 왜 못 뻗는지 기전은 미확인 |
| 남행 16:11:56 실패는 목표 수락 조건(비용 곱한 휴리스틱 > tolerance) 탓 | §5 tol 0.35 · 0.50 · cp 1.5 재질의 | tol 0.35 만으로 0.02 s 성공, cp 1.5 도 성공 | **지지(측정)** — 휴리스틱 값 자체는 미기록, §6 어림 계산은 추정 |
| tol 0.35 는 상자 장면을 바꾸지 않는다 | §8 10-23 6 장면 | 상자 4 장면 경로 점까지 같음 | **지지(오프라인)** |
| tol 0.35 로 실주행 통로 남행을 Smac 이 받는다 | §11 f2st1 | 남행 Smac 실패 0 · 좁은 곳 4.1 cm | **지지(1 회)** — f2tf1 · f2tt1(10-27) · f2tt2(10-28)도 남행 Smac(같은 tol, 다른 수정이 섞인 주행 — 아래 §4.2) |

## 4. 조치와 효과
### 4.1 지금 시험 구성(`planner:=smac`)
- BT: launch 가 BT 원본의 `PlanAndSmooth`(NavFn → SimpleSmoother, 실패 시 CopyPath 원경로)를 `Fallback PlanSmacOrNavFn` = [SmacHybrid → CopyPath step 0.03] 실패 시 [원래 NavFn 블록] 으로 바꾼 사본 `/tmp/nav_to_pose_active.xml` 을 씀. 원본 xml 은 그대로(`planner_id="GridBased"`).
- SmacHybrid: REEDS_SHEPP · R 0.10 · 72 방향 칸 · cp 3.0 · 해석 확장 최대 1.0 m · 시간 상한 2.0 s · 캐시 끔 · smooth_path true · **tolerance 0.35**. 설치판 .so(/opt/ros). 포크(`~/smac_ws`) · 진단 빌드(`~/smac_dbg_ws`)는 오프라인 전용.
- 함께 바뀐 것(다른 줄기): MPPI PathAlign 28 · PathFollow 5(10-26 §14, NavFn 판에도 적용) → [MPPI 카드](mppi-corner-cut-pathalign.md). 재계획 0.01 Hz + PathBlockedAhead(only_new).
- 부르는 법(10-26 ~ 28 모든 Smac 주행): `NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite`([`prep_smac_1026.sh`](../debug_log/2026-10-26/jobs/prep_smac_1026.sh) 3 행 · [`prep_smac_1027.sh`](../debug_log/2026-10-27/jobs/prep_smac_1027.sh) 3 행).

### 4.2 실주행 수치(상자 = 기록 위치, 판정 도구 = B0 와 같은 `anal_contact.py` · `anal_band_run.py`)
| 주행 | 구성 | 결과 | 상자 옆 실제 최소(복귀) | 서쪽 통로 최소 정확 여유 | Smac 실패 → NavFn | 1 s 넘는 정지 | 데이터 |
|---|---|---|---|---|---|---|---|
| B0 f2rp1 · f2rp2 · f2rp5(10-23) | NavFn · MPPI 14 · 10 | 3/3 × 3 | 15.2 · 5.5 · 3.1 | — | — | — | [`fig_box_compare.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare.txt) |
| B0 f2rp4(10-23) | 〃 no5 | 8/8 · 417.9 s | — | 진입 3.7 · 복귀 4.8 · 최소 2.9 | — | — | → [F2 기준선 카드](f2-baseline-no5.md) |
| f2sh1 · f2sh2 | Smac tol 0.25 · MPPI 14 · 10 | 3/3 · 3/3 | **18.4 · 10.8** | — | 0 · 0 | 0 · 0 | §2 표 |
| f2sa1 · f2sa2 | Smac tol 0.25 · 28 · 5 | 3/3 · 3/3 | 14.6 · 14.9 | — | 1(복귀 출발) · 0 | 0 · 0 | [MPPI 카드](mppi-corner-cut-pathalign.md) |
| f2sa3 | Smac tol 0.25 · 28 · 5, no5 | 8/8 · 448.0 s | 13.2 | **0.8**(남행) | 5(통로 남 · 북 전부) | 5 · 15.3 s | §1 |
| **f2st1** | Smac **tol 0.35** · 28 · 5, no5 | 8/8 · 427.5 s | 16.3 | 남행 **4.1** · 전체 2.9(북행) | 3(북행만) | 1 · 4.7 s | §2 표 |
| f2tf1 · f2tt1(10-27, 참고) | f2st1 + nvblox 층 TF 수정(· + SLAM timeout 1.5) | 8/8 · 412.8 / 8/8 · 412.2 s | 갈 때 17.1 · 18.2 / 복귀 f2tf1 **접촉**(상자 시야 밖, 사용자 확인) · f2tt1 14.4 | 전체 3.8 · 3.1 | **0 · 0**(남 · 북 모두 Smac) | 1 · 0 | `2026-10-27/outputs/drives/f2t{f,t}1/` — 다른 줄기 → [SLAM stamp 정체](slam-stamp-freeze.md) · [nvblox 층 TF](nvblox-layer-tf-drop.md) |

### 4.3 판단에 쓴 핵심 줄 · 출력
- **도구 결함 → 변형마다 프로세스(10-26 §6.1 · §6.2)** — [`run_variants.sh`](../tools/plan_offline/run_variants.sh) 3~5 · 12~15 행(변형 하나씩 `gen_yaml` → 묶음 → Jetson `run_jn.sh … GridBased,$v`):
  ```bash
  #   왜: nav2_smac_planner 1.1.20 의 NodeHybrid · NodeLattice 는 motion_table(cost_penalty · 회전반경 · 운동 모델) · 휴리스틱 표가
  #       static 이라 한 프로세스에 Smac 플러그인을 여럿 올리면 서로 설정을 덮음(src/a_star.cpp:115 은 지도 크기가 바뀔 때만 다시 초기화).
  for v in "$@"; do
    python -X utf8 "$H/gen_yaml.py" "$O/planner_$v.yaml" "$PAD" "$v" >/dev/null
  ```
  출력([`sep/anal_all.txt`](../debug_log/2026-10-26/outputs/planner_offline/sep/anal_all.txt), 열: 점 · 길이 | 차체 ↔ 상자 · 중심 | 치명까지 | 최대 꺾임 | 계획 s):
  ```
  b910_rp2_replan  GridBased     |  121 ·  3.09 |    8.0 ·   10.2 |    7.9 |    90 | 0.002
  b910_rp2_replan  Smac_R10_C30_A10_RS |   43 ·  3.09 |   14.4 ·   14.6 |    1.6 |    34 | 0.006
  b910_rp2_replan  Smac_R10_C30_RS |   47 ·  3.18 |    6.8 ·    6.8 |    5.2 |    52 | 0.005
  b910_rp5_full    Smac_R10_C30  |   96 ·  6.89 |    1.3 ·    1.5 |    7.6 |   175 | 0.009
  west_rp3_g4      Smac_R10_C30_A10_RS | 실패
  ```
  (⚠ 채택판 rp2 는 상자 여유 14.4 인데 '치명까지 차체' 는 1.6 cm — 상자 아닌 다른 치명 칸(벽 · 가구 추정)에 가까워진 경로. SUMMARY 에는 이 열 언급 없음.)
- **포크 비용 상한(10-26 §5)** — [`nav2_smac_planner_rover_maxcost.patch`](../06_planner/smac_fork/nav2_smac_planner_rover_maxcost.patch) 58~70 행:
  ```cpp
  +  // rover fork(2026-10-26): Jazzy 의 비용 상한 검사 이식 — 곡선이 max_cost 를 넘는 칸에 들어갔다가 다시 나오면 버림.
  +    const float max_cost = _search_info.analytic_expansion_max_cost;
  +    if (max_cost_it != node_costs.end() && *max_cost_it > max_cost) {
  ```
  적재 확인([`run_chk_fork1.txt`](../debug_log/2026-10-26/outputs/planner_offline/fork/run_chk_fork1.txt) · [`run_chk_stock1.txt`](../debug_log/2026-10-26/outputs/planner_offline/fork/run_chk_stock1.txt)):
  ```
  확인: Smac_R10_C30_A10_RS.analytic_expansion_max_cost = Double value is: 200.0
  적재된 smac .so: /home/jetson/smac_ws/install/nav2_smac_planner/lib/libnav2_smac_planner.so
  확인: Smac_R10_C30_A10_RS.analytic_expansion_max_cost = Parameter not set
  적재된 smac .so: /opt/ros/humble/lib/libnav2_smac_planner.so
  ```
  포크 단독([`sep_fork/anal_all.txt`](../debug_log/2026-10-26/outputs/planner_offline/sep_fork/anal_all.txt)) `b910_rp2_replan  Smac_R10_C30_A10_RS |   44 ·  3.07 |    4.3 ·    7.0 |` — 설치판 14.4 보다 나쁨.
- **BT 대체 블록(10-26 §7)** — [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 120~125 행:
  ```python
  smac_block = ('<Fallback name="PlanSmacOrNavFn">\n'
                '              <Sequence name="PlanSmac">\n'
                '                <ComputePathToPose goal="{goal}" path="{raw_path}" planner_id="SmacHybrid"/>\n'
                '                <CopyPath input_path="{raw_path}" output_path="{path}" step="0.03"/>\n'
  ```
  prep 확인([`prep_smac_1026_3.txt`](../debug_log/2026-10-26/outputs/setup/prep_smac_1026_3.txt) 9~13 행): `BT 사본: PlanSmacOrNavFn 1 · RateController RateController hz="0.01" · step 1` · `SmacHybrid.motion_model_for_search = String value is: REEDS_SHEPP`.
  Smac 사용 판별 = nav2 로그 SimpleSmoother 줄 수(Smac 블록은 스무더를 안 부름): `grep -c 'Received a path to smooth'` → f2sh1 0 · f2sh2 0 · f2sa1 1 · f2sa2 0 · f2sa3 5(이번에 다시 셈, SUMMARY 와 같음).
- **목표 방향 기각(10-26 §20.1)** — [`anal_goal_yaw.txt`](../debug_log/2026-10-26/outputs/planner_offline/goal_yaw/anal_goal_yaw.txt):
  ```
  == 115653(실주행 실패) — 출발 차체 치명 0
    방향 더하기 | 목표 yaw | 목표 치명 · 내접 | Smac | 시간 s | 길이 m | 실패 문구 | NavFn
      +0 |  -100° |   0 · 117 | 실패 | 0.000 | 0.00 | 해 없음 | 성공
    +180 |    80° |   0 ·  94 | 실패 | 0.000 | 0.00 | 해 없음 | 성공
  ```
- **목표 앞까지 갔다(10-27 §2)** — [`chk_goal_reach_1026.txt`](../debug_log/2026-10-27/outputs/parent_chain/chk_goal_reach_1026.txt) 1 · 6 행:
  ```
  sa3_115653 방문 340556 · 목표 (-1.60, -5.50, -100°) 까지 최소 0.057 m (노드 (-1.54, -5.50, 275°), 방향 차 +15°) · 0.25 m 안 노드 173 · 0.10 m 안 7
  sa3_130865 방문     23 · 목표 (-1.65, -3.70, 82°) 까지 최소 0.429 m (노드 (-1.62, -4.13, 140°), 방향 차 +58°) · 0.25 m 안 노드 0 · 0.10 m 안 0
  ```
  (성공 순간은 노드가 목표 0.43 m 밖에서 끝남 = 해석 확장 곡선으로 이은 것으로 보임, 추정.) 부모 사슬([`anal_parent_chain_115653.txt`](../debug_log/2026-10-27/outputs/parent_chain/anal_parent_chain_115653.txt)): `사슬 분류: {"좁은 곳 지남": 966, "창 밖으로 돌아옴": 0, "둘 다": 23, "둘 다 아님": 0, "사슬 끊김": 0}`.
- **바꿔 끼우기(10-27 §2)** — [`anal_swap.txt`](../debug_log/2026-10-27/outputs/swap/anal_swap.txt)(A = 성공 지도 + 이 출발 · 목표, B = 이 지도 + 성공 출발 · 목표):
  ```
  A_115653 | 16:13:08.65(성공) | 16:11:56.85 | 실패 | 2.30 | 1.0000
  B_115653 | 16:11:56.85 | 16:13:08.65(성공) | 성공 | 0.02 | 1.0000
  A_125954 | 16:13:08.65(성공) | 16:12:59.54 | 성공 | 0.17 | 1.0000
  ```
- **허용치(10-27 §5.1)** — [`anal_tolcp.txt`](../debug_log/2026-10-27/outputs/tolcp/anal_tolcp.txt):
  ```
  16:11:56.85 남행(실패) | 실패 1.09 | 성공 0.02 · 1.99 m · 10.7 cm · +15° | 성공 0.02 · 1.99 m · 10.7 cm · +15° | 성공 0.02 · 2.06 m · 12.9 cm · +105° | ...
  16:12:59.54 북행(실패) | 실패 0.04 | 실패 0.04 | 실패 0.04 | 성공 0.09 · 14.51 m · 2.1 cm · -2° | ...
  ```
  설정 차이는 한 줄([`planner_V1.yaml`](../debug_log/2026-10-27/outputs/tolcp/planner_V1.yaml) 18 행 `tolerance: 0.35`, 13 행 0.25 는 GridBased). 수락 기전(소스, 10-27 §6 원문 요약 — 소스 사본은 저장소에 없음, PC 스크래치패드 `nav2src/nav2_1.1.20`): `a_star.cpp:302 · 333` 에서 tolerance(칸) 를 **휴리스틱 값**과 비교, 휴리스틱 = max(장애물 휴리스틱(× (1 + cp × 비용/252) × 2, 10 cm 칸), Reeds-Shepp 거리)(`node_hybrid.cpp:345 · 441~520`).
- **상자 장면 무변화(10-27 §8.1)** — [`anal_W1.txt`](../debug_log/2026-10-27/outputs/tol_box/anal_W1.txt) 와 [`anal_W0.txt`](../debug_log/2026-10-27/outputs/tol_box/anal_W0.txt) 의 상자 4 장면 줄이 같음, 다른 것은 통로 g4:
  ```
  west_rp3_g4      Smac_R10_C30_A10_RS |   27 ·  1.91 |  420.5 ·  457.3 |    3.6 |    21 | 0.011
  ```
- **f2st1 남행이 Smac 이었나(10-27 §11 · §13)** — [`nav2_f2st1.log`](../debug_log/2026-10-27/outputs/drives/f2st1/nav2_f2st1.log) Smac 실패 3 줄(1793067662 · …666 · …672 = 11:21:02 · 06 · 12, 모두 목표 5 출발 뒤):
  ```
  [planner_server-5] [WARN] [1793067666.895047127] [planner_server]: SmacHybrid: failed to create plan, invalid use: Starting point in lethal space! Cannot create feasible plan..
  ```
  [`chk_corr_paths_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/chk_corr_paths_f2st1.txt)(점 간격 0.075 = Smac, 0.025 = NavFn — 앞 줄은 러너 조회용 NavFn):
  ```
  11:20:37.59 /plan           점   75 간격 0.025 길이 1.98  (-1.64,-3.66)->(-1.60,-5.50)
  11:20:37.62 /plan           점   25 간격 0.075 길이 1.79  (-1.66,-3.68)->(-1.51,-5.46)
  11:21:02.38 /plan_smoothed  점   63 간격 0.025 길이 1.65  (-1.49,-5.31)->(-1.65,-3.70)
  ```
  [`anal_band_run_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/anal_band_run_f2st1.txt) 2 · 4 · 8 행: `최소 정확 여유 2.9 cm · 11:21:13.2` · `fp 100(서 있는 자세 닿음) 프레임 0` · `< 6 cm 구간 11:20:44.4 ~ 11:20:54.6 (18 프레임) 최소 4.1 cm`.

### 4.4 한계
- 실주행은 b910 Smac 4 회(MPPI 두 판에 2 회씩) · no5 Smac tol 0.25 1 회 · tol 0.35 1 회(f2st1). f2tf1 · f2tt1(10-27) · f2tt2(10-28)도 같은 Smac 구성이지만 nvblox 층 · SLAM timeout 수정이 함께 들어간 주행이라 tol 0.35 효과만 떼어 볼 수 없다.
- 오프라인 6 장면은 10-23 B0 주행의 순간들 — 상자 옆 '+3.1 cm' 는 그 6 장면에서만. 실주행 Smac 은 재계획 자리 · 지도가 달라 직접 비교가 아니다.
- '수락 조건' 기전은 tol 만 바꾼 측정으로 지지되나, 노드별 휴리스틱 값은 기록하지 않았다(10-27 §6 어림 계산은 0~100 눈금 환산이라 추정).
- 통로 북행 실패의 출발 쪽 원인(출발 칸에서 왜 못 뻗는가 — 각도 칸 · 원호 조각 길이 · 칸 단위 외곽 검사 후보)은 안 풀었다.
- 계획 시간은 쟀지만(0.001~0.04 s, 실패는 최대 2.0 s 상한) planner_server CPU(계획서 P6)는 따로 재지 않았다.

### 4.5 지금 코드 영향(11-04 확인)
- 기본은 NavFn: [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 203 행 `DeclareLaunchArgument('planner', default_value='navfn', …)`, 106~107 행 navfn|smac 외 값은 오류. [`prep_patrol.sh`](../tools/prep_patrol.sh) 16~17 행 `NAV_ADD` 를 주지 않으면 smac 아님, 재계획 기본 `${REPLAN_HZ:-0.5}`. → **Smac 은 `NAV_ADD="planner:=smac" REPLAN_HZ=0.01` 을 줄 때만**(CLAUDE.md §6 11-03 정정 · [11-03 SUMMARY §7](../debug_log/2026-11-03/SUMMARY.md) ① 과 같음).
- [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 731 행 `planner_plugins: ["GridBased", "SmacHybrid"]`, 739 행 `tolerance: 0.35`, 747 행 `max_planning_time: 2.0`, 748 행 `motion_model_for_search: "REEDS_SHEPP"`, 757 행 `cost_penalty: 3.0`, 760 행 `analytic_expansion_max_length: 1.0`, 762 행 `cache_obstacle_heuristic: false`. GridBased 734 행 tolerance 0.25 그대로.
- BT 원본 [`nav_to_pose_no_spin.xml`](../../ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml) 82 행 `planner_id="GridBased"`, 85 행 `CopyPath`(step 없음 = 그대로 복사) — Smac 블록은 launch 가 만드는 사본에만 있다.
- [`copy_path_action.cpp`](../../ros2_ws/src/rover_navigation/src/copy_path_action.cpp) 12~15 · 41 · 51~70 행 `step` 포트(0 = 예전과 같음).
- 러너 · place_server 의 목표 방향은 여전히 NavFn: [`path_end_yaw.py`](../../ros2_ws/src/rover_navigation/scripts/path_end_yaw.py) 22 행 `g.planner_id = 'GridBased'`(10-13 `job613_pathyaw.py` 21 행과 같음) — 계획서 P2 미해결(11-02 SUMMARY 11 행 '결정 대기' 에도 있음).
- 포크 · 진단 빌드는 저장소 안 코드에서 source 되지 않음(`Docs/tools` · `ros2_ws/src` 에 `smac_ws` 문자열 0, 이번 grep). 주행 .so 를 prep 출력이 직접 찍지는 않는다.

## 5. 내 실수 · 기록 어긋남
1. **한 서버에 Smac 변형 여럿 = static 설정 공유**(10-26 §6.1 칸 형식 원문) — 하려 한 것: 변형 비교를 한 번에(10-23 §22.2 · 10-26 §3 · §3.2 · §4.2 · §5.1 · §6.1) · 본 것: cp · max_cost · 회전 벌점 · 운동 모델을 바꿔도 같은 경로, 같은 설정이 함께 올린 변형에 따라 14.4 · 8.6 · 처음 추론: 1.1.20 동작(해석 확장 · smoother) 탓 · 의심한 이유: 같은 설정 · 같은 장면 · 결정적 실행인데 결과가 다름 · 판별: `node_hybrid.hpp:446` 등 static · 결론: 변형 간 비교 무효, 이 오판 위에 §3.2 에서 'Phase P 멈춤' 을 제안했었다 · 다음에 알아보는 법: 같은 프로세스에 같은 플러그인 여럿이면 static 상태부터, 변형마다 프로세스 · 데이터 [10-26 SUMMARY §6.1](../debug_log/2026-10-26/SUMMARY.md) · [`run_variants.sh`](../tools/plan_offline/run_variants.sh).
2. **CRLF 두 번**(10-26 §1.1 · §7.2) — 주말 체크아웃(core.autocrlf=true) 뒤 `plan_offline/*.sh` 와 prep 재전송본이 CRLF. 첫째는 정리 단계가 안 돌아 planner_server 20 개가 쌓여 D5 첫 판 무효, 둘째는 prep `set: +: invalid option`. §0 '저장소와 같음' 해시도 CRLF 사본끼리였다. 다음에 알아보는 법: Jetson 으로 보내는 텍스트는 `tr -d '\r'`, 해시는 `git show HEAD:<경로>` blob 기준 · 데이터 무효 판 `outputs/planner_offline/d5/invalid_crlf/` · [`prep_smac_1026_2.txt`](../debug_log/2026-10-26/outputs/setup/prep_smac_1026_2.txt).
3. **기동 대기 30 s 로 앞 결과를 읽음**(10-26 §4.2) — RS 판 planner_server 가 조회표 계산으로 30 s 를 넘겨 '계획 서버 없음' 인데 결과 파일은 앞 실행(Lattice) 것. 다음에 알아보는 법: 결과 표의 계획기 이름이 요청과 같은지 먼저 · 무효 판 `outputs/planner_offline/hyb/invalid_wait30/`, 고침 [`query_planners.py`](../tools/plan_offline/query_planners.py) 41 행 180 s.
4. **'통로는 차체 계획기로 못 지남' 을 기록 없이 답함**(10-26 §19) — 일반 지식으로 답했다가 bag 경로 출처로 반박됨(16:13:08.65 Smac 통로 경로). 다음에 알아보는 법: 실패 원인을 말하기 전 실패 · 성공 순간을 bag 에서 나눠 봄.
5. **내 칸 지표를 Smac 판정으로 씀**(10-26 §19 → §20.1) — '목표 차체 아래 치명 18 · 22 칸 → 실패' 는 직사각형 안 전체 표본이라 Smac 판정(중심 칸 + 둘레 선, 10-27 §4 소스)과 달랐다. 13 방향 시험으로 기각. 다음에 알아보는 법: 상관 하나로 원인을 말하지 말고 그 변수만 바꾸는 판별 먼저 · 데이터 [`chk_smac_fail_cells.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/chk_smac_fail_cells.txt) → [`anal_goal_yaw.txt`](../debug_log/2026-10-26/outputs/planner_offline/goal_yaw/anal_goal_yaw.txt).
6. **'좁은 곳 = 넘을 수 없는 벽'**(10-26 §22 → 10-27 §2 정정) — 방문 노드 그림만 보고 추정, 부모 사슬로 16:11:56 은 넘었음을 확인.
7. **탐색 영상 두 번 잘못 짬**(10-27 §3 · §28) — ① 남행 실패와 북행 성공을 붙임(같은 일 아님, 사용자 지적) ② 오프라인 재질의 실패를 '실패' 로만 달아 실주행 실패로 읽힘. 다음에 알아보는 법: 비교는 같은 목표끼리, 상태 글자에 출처(실주행 / 재질의)를 붙임. 첫 렌더링 제목 '더 뻗을 곳 없음' 도 진단 빌드가 시간 상한에 걸렸을 수 있어 '실패' 로 고침(10-27 §2.1).
8. **기록 어긋남**:
   1. **계획서 [`SMAC_HYBRID_PLAN.md`](../06_planner/SMAC_HYBRID_PLAN.md) §10(88~92 행)** 이 10-26 §1~§3 의 'Phase P 멈춤 제안 · B0 NavFn 유지 · Lattice cost_penalty · 회전 벌점 효과 없음(1.1.20)' 을 무효 · 이후 표시 없이 갖고 있다 — 같은 날 §4 에서 사용자가 Hybrid 계속을 정했고, §6.1 이 §3 의 '효과 없음' 을 도구 결함으로 무효 처리했다. 계획서에는 10-26 §4~§22 · 10-27(tol 0.35 · 실주행) 결과 절이 아예 없다. §6 'REEDS_SHEPP 는 이 Phase 밖' 도 지금 채택값(RS)과 어긋남. §7 종료 조건의 `PHASE_P_RESULTS.md` 는 없음(`Docs/06_planner/` 에 계획서 · `smac_fork/` 만).
   2. **[`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 748 행 꼬리 주석** — `motion_model_for_search: "REEDS_SHEPP"` 줄 끝에 옛 DUBIN 설명 '전진만 … 경로에 후진 cusp 을 넣지 않는다(RPP/MPPI 전진 추종)' 이 남아 있다(RS 는 후진 cusp 을 넣음 — f2sh1 후진 지령 38 개). 750~752 행 09-14 R · cost 주석도 지금 값(cp 3.0)과 다른 판의 이야기(→ [계획기 카드 §6-2](global-planner-choice.md)). 동작 영향 없음, 낡은 주석.
   3. **[`up_smac_fork_1026.sh`](../debug_log/2026-10-26/jobs/up_smac_fork_1026.sh) 3 행 '오버레이는 오프라인 시험 · planner:=smac 때만 source'** · SUMMARY §5 '(오버레이는 오프라인 · planner:=smac 때만)' — 실제 Smac 주행 prep 은 `smac_ws` 를 source 하지 않고(§4.5 grep), 채택판은 설치판(§6.3)이다. 'planner:=smac 때 포크를 쓴다' 로 읽힐 수 있는 문구. Jetson `~/ros2_ws` 가 smac_ws 위에 겹쳐 빌드됐는지는 Jetson 을 안 봐서 **미확인**.
   4. **10-27 §9.1 '기록: 목표 4 경로 끝 ↔ 목표 거리'** 를 §11 결과가 적지 않았다. 이번에 [`chk_corr_paths_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/chk_corr_paths_f2st1.txt) 끝점 (−1.51, −5.46) 과 목표 (−1.60, −5.50) 로 계산하면 약 **9.8 cm**(내 계산, 오프라인 V1 10.7 · W1 8.1 cm 와 같은 수준). 러너 도착은 목표 대비 **0.218 m**([`run_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/run_f2st1.txt) 26 행; f2sa3 0.144 m) — 경로 끝이 목표 앞에서 끝나는 허용의 대가로 보임(추정, SUMMARY 미기재).
   5. **10-27 §2 '창 밖으로 돌아온 것 0'** — 원문 분류는 `좁은 곳 지남 966 · 둘 다 23`([`anal_parent_chain_115653.txt`](../debug_log/2026-10-27/outputs/parent_chain/anal_parent_chain_115653.txt)): 23 개 사슬은 좁은 곳을 지나면서 통로 창 밖에도 나갔다. '모두 좁은 곳을 지나 옴' 결론은 맞고, '창 밖 0' 은 '창 밖만 거쳐 온 것 0' 이 정확.
   6. **[`chk_goal_reach_1026.txt`](../debug_log/2026-10-27/outputs/parent_chain/chk_goal_reach_1026.txt) 의 도구 원문 없음** — 10-27 `jobs/` 에 이 출력을 만든 스크립트가 없다(TOOLS.md 에도 없음). 대화 중 일회성 계산으로 보임.
   7. **[`fig_box_compare.py`](../debug_log/2026-10-26/jobs/fig_box_compare.py) 5 행 머리 주석** '경로: 그 구간 시작 직전에 받은 BT 경로' — 54~55 행 코드는 §8 정정대로 '최소 여유 순간 이전 마지막 경로'. 낡은 머리 주석.
   8. 10-26 §7.1 이 선언한 **f2sh3(no5)** 는 달리지 않았다(§8 사람 때문에 미룸 → §14 MPPI 28 · 5 채택 뒤 f2sa3 이 대신). 그래서 'Smac + MPPI 14 · 10 의 no5' 수치는 없다. 계획서 §5 의 '사람이 지나가는 b910(T 시험)' 도 안 함. §7.1 ⑤ 'CPU ≤ B0 + 20 %' 는 판정 기록이 없다(10-27 §30 에 Smac 구성 CPU 중앙 67 % 는 있으나 B0 대비 판정 아님).

## 6. 남은 것 (10-27 시점)
- 서쪽 통로 **북행**(남쪽 주머니 · 좁은 곳 안 출발): 출발 자세에 따라 Smac 실패 → NavFn 원경로(벽 쪽) → 최적화 실패 · 탈출 동작(f2st1 최소 2.9 cm 도 이 구간). f2tf1 · f2tt1 은 북행도 Smac(남쪽을 보고 선 −85° 출발이 146 노드로 풀림, 10-27 §27). 출발 칸에서 왜 못 뻗는가 미확인 — 10-26 §22 '다음 ④' 좁은 곳 통과 조건(각도 칸 144 · 회전반경 · 원호 길이) 오프라인은 안 함.
- 러너 · place_server 목표 방향이 NavFn 경로 끝(P2). Smac 은 그 방향까지 맞춰야 함(tolerance 는 휴리스틱으로 느슨해짐).
- `planner:=smac` 을 기본으로 할지 · 원본 브랜치에 합칠지 · Phase P 종료 문서(계획서 §7) — 사용자 결정 대기. 지금 원본 `feature/nvblox-migration` 은 `feature/smac-hybrid` 를 그대로 받아 push 됨(11-04 §2 `git fetch . feature/smac-hybrid:feature/nvblox-migration`) — 코드상 기본은 여전히 navfn.
- 실주행 경로 끝이 목표 약 10 cm 앞 · 도착 0.218 m(위 어긋남 4) — 정밀 정지가 필요한 목표(F2.5 장소)에서의 영향 미측정.
- 상자 옆: 계획 경로는 17~18 cm 인데 실제 10.8~18.4 — 남은 몫은 컨트롤러(→ [MPPI 카드](mppi-corner-cut-pathalign.md)). 비용 골까지 4~10 cm(10-26 §6.3)는 계획기 손잡이로 못 얻음.
- 계획서 §5.1 'Smac + 재계획 0.5 Hz' A/B · '이어 그리기' — 안 함.

## 7. 이후 (10-28 ~) — 포인터
- 10-28 §1 · §4 · §17: f2tt2 · f2tt3 = 같은 Smac 구성(tol 0.35) 반복. f2tt2 북행 10:25:12.81 Smac → 막힘 재계획 10:25:16.80 **Smac 실패 → NavFn**(10-28 §4 · `2026-10-28/outputs/drives/f2tt2/chk_corr_paths_f2tt2.txt`) — 통로 북행 출발 쪽 원인 그대로. 10-28 §5 대책 후보 ③ 'Smac cp 로 계획을 가운데로' 는 10-27 §5 우회 사례로 신중. 그 시기 카드([SLAM stamp 정체](slam-stamp-freeze.md) · [세워 둔 로버 방향](stationary-yaw-drift.md))에서 채움.
- 10-28 F2.5 `place_server` 가 `path_end_yaw.py`(GridBased)로 경로 끝 방향 · 목표 여유 검사 → [F2.5 장소 이동 카드](f25-place-navigation.md).
- 11-03 §7 ①: 'Smac 은 기본 아님' 확인 · CLAUDE.md 정정. 11-04 §3: 계획서 §2 · §8 에 정정 표시(§10 은 아직, 위 어긋남 1).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| D5 · D5b(10-26 §1) | 전역 inflation 완만화 · 패딩 — NavFn + Smac B144(하나만 올림) | `2026-10-26/outputs/planner_offline/d5/`(무효 `invalid_crlf/`) · 그림 `figures/planner_offline/d5_*/` |
| D1 · D1a(§3) | Lattice 6 · 2 변형(한 서버 — 변형 간 무효) | `outputs/planner_offline/d1/` |
| hyb RS(§4.2) | REEDS_SHEPP 4 변형(한 서버) | `outputs/planner_offline/hyb/`(무효 `invalid_wait30/`) |
| fork · chk(§5) | 비용 상한 포크 7 변형 · 설치판 대 포크 확인 | `outputs/planner_offline/fork/` |
| cause_ns(§6.1) | smooth_path false 3 변형(한 서버) | `outputs/planner_offline/cause/` |
| **sep · sep_fork(§6.3)** | 변형마다 따로 — 유효 판 | `outputs/planner_offline/sep/` · `sep_fork/` |
| f2sh1 · f2sh2(§7.3 · §7.4) | Smac + MPPI 14 · 10, b910 | `outputs/drives/f2sh{1,2}/` · bag `bags/bag_f2sh{1,2}.tgz` |
| f2sa1 · f2sa2 · f2sa3(§11 · §15) | Smac + 28 · 5 (b910 · no5) | `outputs/drives/f2sa{1,2,3}/` → [MPPI 카드](mppi-corner-cut-pathalign.md) |
| goal_yaw(§20) | 6 순간 × 13 방향 | `outputs/planner_offline/goal_yaw/` |
| expdbg(§22) | 진단 빌드 탐색 기록 6 순간 | `outputs/planner_offline/goal_yaw/run_expdbg.txt` · `exp_expdbg.tgz` |
| parent_chain · swap(10-27 §2) | 부모 사슬 · 바꿔 끼우기 16 장면 | `2026-10-27/outputs/parent_chain/` · `outputs/swap/` |
| tolcp · tolcp_exp(§5 · §7) | V0~V4 · 탐색 기록 | `outputs/tolcp/` · `outputs/tolcp_exp/` |
| tol_box(§8) | W0 · W1 × 10-23 6 장면 | `outputs/tol_box/` |
| f2st1(§11) | Smac tol 0.35 첫 no5 | `outputs/drives/f2st1/` · bag `bags/bag_f2st1.tgz` |
| tt1_exp(§27 · §28) | f2tt1 통로 3 순간 재질의 · 지도 판 | `outputs/tt1_exp/` |
| 영상(git 제외) | 10-26 `videos/smac_expansion_fail_vs_ok.mp4` · `f2sh{1,2}_return_box.mp4`, 10-27 `videos/smac_expansion_{north,south,tol,tt1}.mp4` · `cmp_corridor_f2sa3_vs_f2st1_light.mp4` · `f2st1_box_stop_light.mp4` | 생성 기록 `outputs/fig_video/` |

## 9. 도구 해설
공통: 오프라인 계획기 시험은 모두 PC 에서 묶음을 만들어 Jetson `ROS_DOMAIN_ID=42` 에 별도 planner_server 를 띄움(로버 안 움직임, 본 스택과 격리). 실행은 스크래치패드 `run_jn.sh`(비밀번호는 저장소 밖) 경유. 공통 사슬 `prep_scenes.py → gen_yaml.py → up_bundle.sh → run_planner_offline.sh → query_planners.py → anal_plan_compare.py` 의 단계별 해설은 [B0 카드 §9 'Docs/tools/plan_offline/'](path-tracking-replan-b0.md). 여기는 9 기에 더하거나 바꾼 것.

### run_variants.sh — 변형마다 프로세스 따로 (10-26 §6.2, PC → Jetson)
- 부른 형태: `run_variants.sh 출력폴더 장면.npz 패딩 오버레이(없으면 -) 변형…`, 환경 `INFL_R · INFL_K` 는 gen_yaml 로.
- 왜: static 운동 표 공유(위 실수 1) — 변형 간 비교를 살리려고.
- 하는 일: 변형마다 ① `gen_yaml.py` 로 그 변형 하나 + GridBased 만 든 yaml ② `up_bundle.sh`(CR 제거 base64 묶음) ③ Jetson 실행(`GridBased,$v`, 오버레이면 그 ws 를 source) ④ 결과 base64 를 풀어 `result_<v>.npz` ⑤ `anal_plan_compare.py` → `anal_<v>.txt` ⑥ 화면에 `== 변형 적재 .so 경로 n/6 일치` ⑦ 끝에 `anal_all.txt` 로 합침.
- 출력: `outputs/planner_offline/sep/` · `sep_fork/`(10-26), 10-27 `tolcp/` · `tol_box/` 의 실행 스크립트(`run_tolcp_1027.sh` · `run_tol_box_1027.sh`)도 같은 원리(변형마다 따로)를 자체 반복문으로.
- 결함 · 지금: 스크래치패드 경로가 스크립트 안에 고정(9 · 15 행) — 스크래치패드가 바뀌면 고쳐야 함. 변형 이름 규칙은 `gen_yaml.py` 머리(`Smac_R…_C…[_A][_B][_RS][_M][_NS]`, `Lattice_C…_P…[_REV][_A][_M][_NS]`), 환경 `SMAC_TOL`(10-27) · `SMAC_MAXT`(기본 5.0, 실주행 재현은 2.0). 다시 쓸 수 있음.

### gen_yaml.py · query_planners.py · run_planner_offline.sh — 9 기에 바뀐 점
- `gen_yaml.py`: `_RS`(REEDS_SHEPP) · `_A`(해석 확장 최대 길이 ×10) · `_M`(포크 비용 상한) · `_NS`(smooth_path false) · Lattice 이름 · `INFL_R/K`(D5) · `SMAC_TOL`(10-27 §5) · `SMAC_MAXT`(10-26 §20).
- `query_planners.py` 41 행 기동 대기 30 → 180 s(10-26 §4.2 실수 3), 68 행부터 질의마다 planner.log 새 경고 줄(실패 문구)을 붙임(10-26 §20), 장면 JSON 입력(10-26 §20).
- `run_planner_offline.sh` 6 행 로그 버퍼 끔, 15 행 planner_server 기동, 20~24 행 **질의 뒤** 매개변수 · `/proc/<pid>/maps` 의 smac .so 경로 확인(10-26 §5.2 — 기동 전 조회는 의미 없었음), 시작 전 잔재가 있으면 중단(10-26 §1.1), 세 번째 인자 1 = 탐색 기록 받기(10-26 §22). `kill_planoff.sh` 잔재 정리.

### up_smac_fork_1026.sh · nav2_smac_planner_rover_maxcost.patch — 비용 상한 포크 (10-26 §5, Jetson 빌드)
- 하는 일: Jetson `~/smac_ws` 에 navigation2 1.1.20 태그를 sparse clone(nav2_smac_planner 만) → 패치(4 파일 +59/−4: `types.hpp` SearchInfo 2 필드 · hybrid/lattice 매개변수 선언 `analytic_expansion_max_cost`(200) · `…_override`(false) · `analytic_expansion.cpp` 검사) → Release 빌드(2 분 44 초) → .so 문자열 확인.
- 출력 [`up_smac_fork_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_smac_fork_1026.txt) 끝: `소스 a097086 2025-11-17` · `4 files changed, 59 insertions(+), 4 deletions(-)` · `Finished <<< nav2_smac_planner [2min 44s]`.
- Jazzy 와 다른 점: override 거리에 `goal->motion_table.min_turning_radius` 대신 `_search_info.minimum_turning_radius`(칸 단위). 쓰인 곳: §5 판정 ✘ · §6.3 포크 이득 없음. 지금: 주행 안 씀, Jetson 에 남음(10-27 §0 확인).

### up_smac_expdbg_1026.sh · nav2_smac_planner_rover_expdump.patch · run_expdbg_1026.sh — 탐색 기록 진단 빌드 (10-26 §22)
- 패치: `a_star.cpp` 에 환경 `SMAC_EXP_DIR` 이 있을 때만 Hybrid 탐색 방문 노드마다 (x, y, θ 칸, 부모 x, y) 를 모아 질의 끝에 `exp_<n>.txt` 로(동작 그대로 — 재현 6/6 으로 확인). 비용 상한 포크는 경로가 달라질 수 있어 원본 1.1.20 에 따로 빌드(`~/smac_dbg_ws`).
- 결함: 부모는 (x, y) 만이라 사슬은 같은 (x, y) 노드에 붙여 이음(겹침 0 확인). 기록 때문에 느려 16:11:56 류 질의가 2.2~2.35 s(시간 상한 2.0 근처) — 설치판과 탐색이 잘렸을 수 있음(결과 실패는 같음, 10-27 §2 주의).

### fig_smac_expansion.py → _v2 · _tol · _tt1 — 탐색 영상 (10-26 §22 → 10-27 §3 · §7 · §27)
- 입력: 결과 npz · 장면 npz · exp 폴더. 그 순간 재구성 전역 코스트맵 위에 방문 노드를 순서대로 늘려(로그 눈금) 그림, 끝 3 s 붙잡기. v2 = 같은 목표끼리(북행 3 · 남행 1, 남행엔 목표에 가장 가까운 노드와 부모 사슬), _tol = 같은 순간 기준 · tol 0.35 · cp 1.5 세 칸, _tt1 = f2tt1 세 순간(상태 글자에 '재질의' 출처).
- 결함 · 계보: 첫 판의 '칸 n' 은 연속 좌표 고유 수라 무의미(10-27 §2.1 에서 뺌), '−' 글리프 · heredoc '\n' 함정. 판정에는 안 쓰고 설명용.

### chk_corr_paths.py — 경로 출처 가르기 (10-26 §19, PC rosbags)
- 부른 형태: `chk_corr_paths.py bag HH:MM:SS HH:MM:SS`. `/plan` · `/plan_smoothed` 메시지마다 점 수 · **점 간격 중앙**(Smac ≈ 0.07 · NavFn 0.025) · 길이 · 시작 → 끝.
- 쓰인 곳: 10-26 §19(Smac 도 통로 경로를 냄) · 10-27 §13(f2st1 북행 NavFn 3) · §28(f2tt1 셋째 실주행 Smac). 결함: `/plan` 에 러너 조회용 NavFn(0.025, 목표 방향 계산용)도 섞임 — '바로 뒤 0.07 판이 있으면 그쪽이 BT 경로' 로 읽어야 함. 같은 규칙이 `fig_drive_video.py` 106~109 행 · `fig_rviz_video.py` 97 행에 있음.

### chk_smac_fail_cells.py · anal_goal_yaw.py · run_goal_yaw_1026.sh — 목표 자세 칸 · 목표 방향 시험 (10-26 §19 · §20)
- `chk_smac_fail_cells.py bag`: 6 순간(시각 · 목표는 코드 8~9 행에 손으로) 직전 전역 코스트맵에서 출발 · 목표 자세 차체(0.262/−0.248 × ±0.165 + 0.01)를 칸 절반 간격으로 표본 → 중심 · 최대 · 치명 · 내접 칸 수. **결함: Smac 충돌 판정(중심 칸 + 둘레 선)과 다른 지표** — §20.1 · 10-27 §4 가 밝힘. 출력 [`chk_smac_fail_cells.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/chk_smac_fail_cells.txt).
- `run_goal_yaw_1026.sh`: 장면 JSON(6 순간 × 방향 더하기 13) → `prep_scenes` → 실주행 Smac 값 하나 + NavFn 서버로 78 질의. `anal_goal_yaw.py`: 순간 × 방향 표 + 위 칸 지표. 판정 '가설 H 기각'.

### anal_parent_chain.py · run_swap_1027.sh — 부모 사슬 · 바꿔 끼우기 (10-27 §1 · §2)
- `anal_parent_chain.py exp.txt 장면.npz 장면이름 그림.png`: 통로 창(x −2.25~−0.95, y −5.85~−3.25) 안 y < −4.9 노드마다 출발까지 사슬, 좁은 곳 창(x −1.85~−1.25, y −4.9~−4.5) 통과 · 창 밖 여부로 분류(20 · 35 행). 출력 위 §4.3.
- `run_swap_1027.sh`: 장면 JSON 으로 A(성공 지도 + 실패 출발 · 목표) · B(실패 지도 + 성공 출발 · 목표) · C(원래) 16 장면 → 진단 빌드 서버. 출력 [`anal_swap.txt`](../debug_log/2026-10-27/outputs/swap/anal_swap.txt)(재구성 16/16 = 1.0000). 한계: 진단 빌드 느림(위).

### run_tolcp_1027.sh · anal_tolcp.py · run_tol_box_1027.sh — 허용치 · cp 재질의 (10-27 §5 · §8)
- `run_tolcp_1027.sh`: 변형 `이름:tol:cp`(V0 0.25:3.0 · V1 0.35:3.0 · V2 0.50:3.0 · V3 0.25:1.5 · V4 0.35:1.5)마다 `SMAC_TOL` · cp 를 바꾼 yaml 로 설치판 서버를 따로, 10-26 `scenes_expdbg.npz` 6 순간. `anal_tolcp.py`: 순간 × 변형 결과 · 왕복 · 길이 · 끝 ↔ 목표 · 끝 방향 차.
- `run_tol_box_1027.sh`: W0 0.25 · W1 0.35 를 10-23 `scenes_1023.npz` 6 장면에, `anal_plan_compare.py` 로 지표. 판정 '상자 차이 0'. 지금 다시 쓸 수 있음.

### chk_replan_maps.py — 재질의가 실주행과 다른 이유 (10-27 §28, PC rosbags)
- 15:58:05~14 전역 코스트맵 발행본마다 출발 자세 중심 · 외곽 최대 칸, 실주행 Smac 경로가 지나는 99 · 100 칸, PathBlockedAhead 칸 (−1.60, −4.70) 값. 출력 [`chk_replan_maps.txt`](../debug_log/2026-10-27/outputs/tt1_exp/chk_replan_maps.txt). 알려 준 것: 장면 규칙 '직전 발행 지도' 는 계획 시각과 1~2 s 차 — 재질의 실패를 실주행 실패로 읽으면 안 됨.

### prep_smac_1026.sh · prep_smac_1027.sh · up_smac_nav_1026.sh · up_prep_params_1027.sh — 배포 · prep (Jetson, 로버 안 움직임)
- `up_smac_nav_1026.sh`: launch · nav2_params · copy_path_action.cpp 를 Jetson src 로, 이전 sha 출력, rover_navigation 빌드(실행 중 스택엔 미적용). 첫 판 heredoc '\n' 으로 launch 깨짐 → `_b` 재배포.
- `prep_smac_1026.sh`(3 행 `NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite`) + BT 사본 PlanSmacOrNavFn · RateController · step 개수, SmacHybrid 매개변수, 프리셋 · odom1 · MPPI 가중 조회. `prep_smac_1027.sh` 는 tolerance 조회를 더함. 출력 `outputs/setup/prep_smac_102{6,7}_*.txt`.
- `up_prep_params_1027.sh`: prep 3 개 + nav2_params 를 CR 제거판으로 보내고 **git blob 해시**(`git hash-object`)와 CR 수를 찍음, 설치본이 링크인지 일반 파일인지 출력(10-26 §7.2 교훈). → [빠른 prep 카드](prep-fast-startup.md)(설치본 링크 끊김).

### fig_box_compare.py — B0 대 Smac 상자 옆 그림 (10-26 §8 · §12)
- `fig_box_compare.py 출력.png 이름=bag…`(앞 3 개 B0, 이름에 'sh' 있으면 Smac): map 자세로 지나간 길 · 최소 여유 순간 차체 · 그때 BT 경로(B0 `/plan_smoothed`, Smac 점 간격 > 0.04). 출력 [`fig_box_compare.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare.txt) · [`fig_box_compare_mppi.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare_mppi.txt)(`Smac f2sh1 18.4 cm · f2sh2 10.8 cm · f2sa1 14.6 cm · f2sa2 14.9 cm`). B0 15.2 의 출처(0.1 s 표본). 결함: 머리 주석 5 행이 옛 규칙(위 어긋남 7).

## 10. 용어
- **Smac Hybrid-A\***: 위치 + 방향(72 칸 = 5°)을 상태로, 최소 회전반경 원호 조각으로 뻗는 A*. 차체 충돌 검사를 계획에 넣는다. **REEDS_SHEPP** = 전진 · 후진 원호 모두(cusp 허용), **DUBIN** = 전진만.
- **해석 확장(analytic expansion)**: 탐색 중 목표까지 Dubins/RS 곡선을 바로 그어 충돌이 없으면 붙이는 단축. `analytic_expansion_max_length` 로 길이 상한(1.1.20 기본 3 m, 우리 1.0 m). Jazzy 는 곡선 위 칸 비용 상한(`analytic_expansion_max_cost`)도 봄 — 1.1.20 엔 없어 포크로 이식.
- **static 운동 표 공유**: 1.1.20 `NodeHybrid` · `NodeLattice` 의 motion_table · 휴리스틱 표가 클래스 static 이라, 한 프로세스의 Smac 인스턴스들이 마지막(또는 처음) 설정 하나를 같이 쓰는 것. 실주행(Smac 하나)엔 해당 없음.
- **tolerance(Smac 1.1.20)**: m → 칸으로 바꿔 **휴리스틱 값**과 비교하는 목표 수락 허용. 휴리스틱엔 cost_penalty 를 곱한 장애물 비용 거리가 들어가므로, 고비용 칸 근처 목표에서는 '가까운데도 멂' 이 될 수 있다. 허용 안 노드가 생기면 1000 번(`max_on_approach_iterations`) 더 펼친 뒤 가장 가까운 노드로 끝냄 → 경로 끝이 목표 앞에서 끝날 수 있음.
- **PlanSmacOrNavFn**: `planner:=smac` 때 launch 가 만드는 BT 블록 — Smac 이 실패하면 같은 틱에 NavFn(+SimpleSmoother/CopyPath)로 대체.
- **CopyPath step**: 경로를 호 길이 간격으로 다시 찍는 BT 포트. Smac 점 간격 ≈ 0.07 m 를 NavFn 판 0.026~0.047 에 맞춰 MPPI 경로 크리틱 offset(점 개수)의 거리 의미를 유지.
- **부모 사슬**: 탐색 기록에서 노드의 부모를 출발까지 거슬러 이은 것 — 그 노드가 어떤 길로 도달했는지.
- **바꿔 끼우기(swap)**: 실패 순간 지도 + 성공 순간 출발 · 목표, 또는 그 반대로 재질의해 지도와 출발 중 무엇이 결과를 정하는지 가르는 시험.
- **비용 골**: 상자 북쪽 단면에서 비용이 가장 낮은 선 — 그 선을 따르면 차체 ↔ 상자 약 18 cm(10-26 §6.3).
