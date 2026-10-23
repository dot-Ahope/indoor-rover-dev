# 전역 계획기 전환 계획 — NavFn → Smac Hybrid-A* (Phase P)

- 작성: 2026-10-23 (사용자: "우린 직사각형의 로버를 구동중이므로, Smac Hybrid를 쓰는게 좋겠다", "바꾸고 잘 되어 git에 push할 경우, NavFn과 분리하도록 하자", "플래너 변경 계획 진행하자")
- 근거 기록: `Docs/debug_log/2026-10-23/SUMMARY.md` §14~§20(추종 · 재계획 분석), §15(NavFn 보정 목록 · Smac 09-14~15 결과), `Docs/debug_log/2026-09-14/SUMMARY.md` §2.19~2.26, `Docs/debug_log/2026-09-15/SUMMARY.md` §1~2.

## 1. 왜 바꾸나

| 근거(측정) | 출처 |
|---|---|
| 차체 옆 여유의 마지막 몫은 **계획 경로 자체의 여유**: 재계획 누적을 끈 뒤(f2rp1 · f2rp2) 로버는 경로 선을 따랐으나 다시 그린 NavFn 경로의 상자 여유가 10.2~13.3 cm → 실제 여유 15.4 · 5.5 cm | 10-23 §17.1 · §18.1 |
| NavFn 은 여유 선호를 키우기 어려움: 전역 감쇠 2 → 5 로 경로가 0~5 cm 만 멀어짐(격자 1 칸), 상자 옆 단면 비용 최소는 y ≈ 0.35 인데 경로는 0.27~0.30 | 10-23 §1.1 · §12 |
| NavFn 은 점(로버 중심) 계획 — 직사각 차체 · 방향을 모름. 그래서 붙인 보정 7 가지(팽창 0.70/2.0 · SimpleSmoother · CopyPath · 패딩 0.01 · 러너 경로 끝 yaw · yaw 허용 0.35 · 재계획 정책) | 10-23 §15 |
| Smac Hybrid-A* 는 차체 다각형 충돌 검사 · 방향 · 최소 회전반경 · 비용 벌점(cost_penalty)을 계획에 넣음 | Nav2 Smac 설계(일반 지식, 미검증 항목은 §6 에서 측정) |

**바꿔도 남는 것(미리 적음)**: 재계획을 로버 자리에서 시작하면 생기는 치우침 누적(10-23 §14)은 계획기와 무관 → B0 기준선부터 '목표당 1 회 + 막힘 시' 구성을 씀. 기억 밀림 · 칸 반올림(10-22 §11~§17)도 계획기와 무관.

## 2. 버전 · git 전략 (사용자: "NavFn과 분리")

1. **B0 = NavFn 기준선 고정**(이 계획의 출발점): 구성 = 깊이 프리셋 3 · nvblox 통합 2.0 · `vslam:=on` · 재계획 0.01 Hz + PathBlockedAhead · PathAlign 14. 기준 주행 = b910 2 회(f2rp1 · f2rp2, 10-23) + no5 1 회(f2rp3, §20). 통과 뒤 원본 브랜치 `feature/nvblox-migration` 커밋에 태그 `navfn-baseline-<날짜>`(push 는 사용자 결정).
2. **작업 브랜치 `feature/smac-hybrid`** 를 그 태그에서 분기. Smac 관련 변경은 모두 여기서.
3. **같은 코드에서 고를 수 있게**: launch 인자 `planner:=navfn|smac`(기본 navfn — `camera_layer:=nvblox|stvl` 과 같은 방식). BT · 계획기 파라미터 · 러너 조회기 · MPPI 경로 크리틱 값 묶음을 인자로 바꿔 끼움. NavFn 설정은 지우지 않고 대조군으로 남김.
4. Phase P 종료(§7) 뒤 원본 브랜치로 합칠지 · 기본값을 smac 로 바꿀지는 사용자 결정. `TEST_COURSE_AND_GATES.md` 는 Phase P 판을 새로 씀(CLAUDE.md 규칙).

## 3. 전환 전에 고칠 것 (10-23 §15 의 걸림돌)

| # | 걸림돌 | 대책(안) | 확인 방법 |
|---|---|---|---|
| P1 | **출발 차체 충돌 거부**: 09-15 mp1 — 패딩 차체가 가구 LETHAL 에 겹치자 Smac 'no valid path' 15 회 → 48 s ABORT(NavFn 은 출발 칸만 봄) | BT 에서 계획 실패 시 **NavFn 으로 한 번 계획하는 대체 경로**(Fallback: Smac → NavFn), 또는 실패 시 MonotoneEscape 를 먼저(로컬 · 전역 둘 다 보는 판으로) | 정지 시험: 로버를 상자 옆 3~4 cm 자리에 두고 계획 요청 |
| P2 | 러너 `job613_pathyaw.py` 가 `planner_id='GridBased'` 고정 → 경로 끝 yaw 를 NavFn 으로 계산 | planner_id 를 인자로(구성과 같게). Smac 은 목표 yaw 를 지키므로 경로 끝 yaw 대신 **목표 지점의 통로 방향**을 직접 줄지 검토 | 조회 결과를 두 계획기로 비교 |
| P3 | SimpleSmoother 가 Smac 경로의 회전반경을 깰 수 있음 | smac 묶음에선 SmoothPath 끄고 Smac 자체 smoother(`smooth_path: true`) 사용, CopyPath 는 유지 | 경로 곡률 비교 |
| P4 | MPPI 경로 크리틱 offset 이 NavFn 점 간격(0.025 m) 기준 — Smac 은 약 0.1 m | smac 묶음에서 offset 을 **거리 기준으로 같게**(PathFollow 20 × 0.025 = 0.5 m → 약 5, PathAlign 3 → 1) | 오프라인 MPPI 모의(10-01 job776) · 주행 |
| P5 | Smac 파라미터(R 0.10 · cost_penalty 1.2)는 팽창 0.55 시절 값 | 팽창 0.70 에서 R ∈ {0.10, 0.15} × cost_penalty ∈ {1.2, 2.0, 3.0} 오프라인 스윕 | §4 오프라인 비교 |
| P6 | CPU 미측정(지금 70 %) | 계획 시간 · planner_server CPU 측정, `max_planning_time` 5 s 안에서 | 오프라인 · 주행 proc 로그 |
| P7 | 분석 도구가 NavFn 흉내(Dijkstra) 기반 | 실제 planner_server 로 계획하는 오프라인 도구로 교체(§4) | — |

## 4. 오프라인 비교 (로버 안 움직임)

- Jetson 에 **두 번째 planner_server**(ROS_DOMAIN_ID 42, nvblox 재생과 같은 격리)를 띄우고, 기록된 전역 코스트맵(bag `/global_costmap/costmap`)을 그 계획기의 지도로 넣어 `ComputePathToPose(use_start)` 를 NavFn · Smac 각각 호출.
- 입력 장면: 10-22~10-23 bag 의 복귀 접근(상자 보인 뒤, PathBlockedAhead 순간 로버 자리), 서쪽 통로(no5), 문 통과, W3 앞(10-23 §7 의 U 자 경로 자리).
- 지표: 실제 상자 · 통로 벽까지 경로 여유(차체 다각형 기준), 경로 길이, 최대 곡률, 계획 시간, 실패 여부.
- 합격(주행 시험으로 가는 조건): 상자 옆 경로 여유가 NavFn 보다 **≥ 5 cm 큼**(같은 출발 · 같은 지도), 서쪽 통로에서 계획 실패 0, 계획 시간 중앙 ≤ 0.5 s.

## 5. 주행 시험 (Smac, 작업 브랜치)

- 순서: b910 2 회 → no5 1 회 → 사람이 지나가는 b910 1 회(T 시험, 09-29 요구).
- 판정(B0 와 같은 도구): 상자 옆 실제 최소 여유 ≥ 8 cm(2 회 모두), 서쪽 통로 최소 여유 ≥ B0, 계획 실패로 인한 ABORT 0, 출발 차체 충돌 거부 0(있으면 P1 대체 경로가 처리했는지), 짧은 멈칫 · CPU ≤ B0 + 20 %, 목표 시간 ≤ B0 + 15 %.

## 6. 미리 적는 위험 · 모르는 것

- 09-14 sm1: 계획기를 바꿔도 모서리 통과 띠가 0.10~0.14 m 라 같은 곳을 지났음 — 이번 코스(상자 옆 통로 폭)는 더 넓으나 같은 한계가 나올 수 있음.
- Humble Smac Hybrid 는 목표 방향을 반드시 지킴 → 목표 방향이 통로와 어긋나면 루프 경로(09-14 R 0.20 의 4.3 m 루프와 같은 기제).
- DUBIN(전진만) — 후진이 필요한 자리는 MPPI · MonotoneEscape 몫. REEDS_SHEPP 는 이 Phase 밖(10-01 §8.28~8.30).
- cost_penalty 를 키우면 좁은 곳에서 길을 못 찾을 수 있음(여유와 통과의 맞바꿈).

## 7. Phase P 종료 조건

- §5 판정 전부 통과(2 회 이상 재현), B0 대비 상자 옆 여유 개선이 수치로 남음, `planner:=navfn` 로 되돌렸을 때 B0 와 같은 결과(대조군 유지 확인).
- 결과 요약 `Docs/06_planner/PHASE_P_RESULTS.md`, `TEST_COURSE_AND_GATES.md` Phase P 판, CLAUDE.md §6 갱신.
