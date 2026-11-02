# Phase S — 현재 스택(STVL) 완성 조건 S1~S6 과 기준선 BASELINE_STVL

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **완료(09-21 Phase S 종료)** — 기준선 cc2~cc5 4/4 성공 · 코스트맵 상자 여유 8.4~12.9 cm · CPU 합 ≈ 320 % · GPU 0 % · 6.6 W. 09-22 N4 에서 S 2 회가 재현(여유 9.3 · 11.7, CPU 318 · 315) → nvblox 비교의 기준으로 쓰임. 단 표의 몇 칸은 이름과 실제 계측이 다르다(§5) | 09-09(계획 수립) ~ 09-21 §5~§8 (이 카드), 이후 09-22 N4 · 09-23 Phase N 종료 | [`NVBLOX_MIGRATION_PLAN.md` 'Phase S — 현재 스택 개선 (이전 전 완료 조건)'](../05_nvblox/NVBLOX_MIGRATION_PLAN.md) | `Docs/debug_log/2026-09-21/BASELINE_STVL.md`(새로) · `NVBLOX_MIGRATION_PLAN.md`('2026-09-21 — Phase S 종료·N0 착수 시 결정' 절) · `Docs/04_navigation/TEST_COURSE_AND_GATES.md` v1.0(커밋 `35308b81`) · `2026-09-21/jobs/job231_drive.sh`(tegrastats · RSS) · `run_post3.sh`(tegra · rss 회수) · 태그 `stvl-baseline`(84a41e6, 로컬 · personal) | [CostCritic 교체](obstacles-to-costcritic.md)(cc1~cc3) · [주행 직전 DDS 참여자](pre-drive-dds-participants.md)(cc1 제외) · [깊이 장애물 · 코스트맵](depth-obstacle-costmap.md)(S1 · S2) · [CPU 부하 · 정지](cpu-load-stalls.md)(S6) · [Phase N 전반 N0~N4](nvblox-migration-n0-n4.md)(기준선 사용처) · [회피 주행 계측 결함](avoid-run-metrics.md)(러너 지표 ①~⑥) |

**한 줄**: nvblox 로 옮기기 전에 '지금 스택을 끝까지 다듬고 그 성능을 숫자로 고정한다' 는 단계가 Phase S 였다(09-09 계획). 여섯 항목(S1 감쇠 · S2 카메라 사각 · S3 동적 망각 · S4 회피 반복 · S5 기준선 · S6 CPU) 중 09-21 에 S2 를 정지 측정으로 끝내고(센서 한계 ≤ 0.316 m · 디시메이션 4 유지 · 코스트맵 한계는 릴레이 min_range 0.45), S5 를 CostCritic 채택 구성의 같은 코스 4 회(cc2~cc5)로 `BASELINE_STVL.md` 에 고정했다. S3 은 STVL 구조 한계로 문서화만, S6 은 기준선 수치로 대체. 기준선 §4 에 nvblox 채택 기준을 수치로 미리 적어 둔 것이 다음 날 N4 판정(CPU 만 불합격 → 사용자 결정 로컬 채택)의 틀이 됐다. 원문을 다시 대조하니 표의 '⑥ 상자 미관측 최대 s' 는 실제로는 '러너 재고정 뒤 경과 시간'(≈ 주행 시간)이고, 'EKF 위반 19~39' 는 주행 중 값이 아니라 센서 기동 뒤 누적이다.

## 1. 증상 · 배경 — Phase S 가 무엇이었나
- 계획서(09-09 수립, `NVBLOX_MIGRATION_PLAN.md`): '현재 스택(Nav2 + STVL) 완성 → 기준선 고정 → nvblox 이전'. Phase S 의 목적은 두 가지 — 이전 전에 지금 스택의 알려진 결함을 정리하고, **같은 코스 · 같은 스크립트로 잰 비교 기준**을 남겨 nvblox 채택/기각을 숫자로 판단하는 것.
- 항목과 종료 조건(계획서 원문) · 09-21 종결 상태(계획서 '2026-09-21 — Phase S 종료' 절):

| 항목 | 내용 | 종료 조건(계획서) | 09-21 종결 |
|---|---|---|---|
| S1 STVL 감쇠 | voxel_decay 15 → 30(근거 job167: 깊이점 소실부터 상자 통과까지 ≈ 22 s 필요) | 상자를 완전히 지날 때까지 `lc_box` 유지, 실제 최근접 ≥ 5 cm | 종결 문구에 S1 없음. 기준선 구성은 로컬 decay 120 · 전역 180 s, 기준선 ③ 로컬/전역 99~100(기억 소실 0) · ① 9.4~18.0 cm 로 조건은 충족. 첫 완주 기록은 09-10 job192(이후 [깊이 카드](depth-obstacle-costmap.md) §3 표에 언급, 이 카드에서 원문 미확인) |
| S2 카메라 사각 | 디시메이션 4 재검토(근거 job167: 깊이점이 카메라~상자 0.51 → 0.45 m 에서 142 → 0) | 끊김 거리 ≤ 0.35 m, CPU 증가가 EKF 위반 재발을 유발하지 않을 것 | **09-21 §5~§6 측정으로 종결**: 센서 한계 ≤ 0.316 m, 디시메이션 4 유지(2 는 이득 없이 CPU ×2), 코스트맵 한계 = 릴레이 min_range 0.45 → [깊이 카드 §2.1](depth-obstacle-costmap.md) |
| S3 동적 망각 | 상자 제거 시험, decay_acceleration 튜닝 | 상자 제거 뒤 절두체 안에서 다시 볼 때 소거, 전역에 유령 없음 | **문서화만**(STVL 구조 한계 — 절두체 근평면 안 · 화각 밖은 감쇠로만 지움). nvblox 동적 모드는 N7 후보로 이월 |
| S4 회피 반복 | 같은 코스 3 회 연속 | 접촉 0/3 · 완주 3/3 · 계획 좌우 전환 0 · 직진 ω 부호반전 ≤ 1.0 /m · 실제 최근접 ≥ 5 cm | 09-11 'S4 3/3 완료'(계획서 09-11 판정 절, 09-11 §5.13). 기준선의 부호반전은 1.05~5.6 /m 로 **≤ 1.0 조건은 4 회 모두 미달**(§5 ⑤) |
| S5 기준선 고정 | 노드별 CPU · GPU · 전력 · 온도 · 코스트맵 주기 · 장애물 지속 · 회피 ①②④ · 부호반전 · 메모리 | `BASELINE_STVL.md` 작성('nvblox 채택/기각의 유일한 근거') | **09-21 §7 완료**(cc2~cc5) |
| S6 CPU 여유 | 09-09 신설: EKF 주기 위반이 정지의 뿌리, 최대 소비원 sensor_conditioner 35~37 % | 주행 30 s 동안 EKF 위반 0 · `Message Filter dropping` 0 · load < 6 | **기준선 수치로 대체**(합 ≈ 320 %, conditioner ≈ 43 %). 종료 조건 자체는 판정하지 않음(§5 ⑤) → 09-28 컨디셔너 C++ 이식(다음 시기) |

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-09 | 계획서 수립: Phase S(S1~S5) · Phase N(N1~N5) · git 전략(S5 후 main 병합 + 태그) | — | '이전 전에 S2 는 끝낸다' | `NVBLOX_MIGRATION_PLAN.md` |
| 09-09 저녁 | S6 추가(EKF 위반 → TF → SLAM 폐기 → 정지 연쇄) | conditioner 35~37 % | 우선순위 높음 → 09-10 §1 '열화' 로 하향 | [CPU 카드](cpu-load-stalls.md) |
| 09-11 | S4 3/3 · '지금 단계에서 이전하지 않는다' 판정, 이전 트리거 3 개(S3 실패 · S5 병목 · N1 구조) | STVL 은 CPU 상위 8 밖 | 이전 보류 | 계획서 09-11 절 |
| 09-14 | 재검토: 목표가 '청소기형 자유 이동' 이면 판단이 달라짐 | — | 이전 쪽으로 | 계획서 09-14 절 |
| 09-21 §1~§4 | CostCritic 판정 cc1~cc3 | cc2 · cc3 깨끗, cc1 미달 18 | CostCritic 채택 → 기준선 구성 확정 | [CostCritic 카드](obstacles-to-costcritic.md) |
| 09-21 §5 | S2 정지 측정(상자 · 의자 다리 × 거리 × 디시메이션) | 센서 ≤ 0.316 m, 릴레이 0.45 m 안 0 점 | S2 센서 기준 통과, dec 4 유지, min_range 0.35 A/B 후보 | [깊이 카드 §2.1](depth-obstacle-costmap.md) |
| 09-21 §6 | 사용자 "뭐가 더 나은가" → min_range A/B 보류, S5 로. 러너에 tegrastats(1 s) · 노드 RSS(ps) 추가, sudo 없이 tegrastats 동작 확인 | [j461_tegratest.txt](../debug_log/2026-09-21/outputs/j461_tegratest.txt)(rc 0, GR3D 0 %) | 코스트맵 주기는 bag 에서 사후 계산(주행 전 `ros2 topic hz` 금지) · cc2 · cc3 를 표본으로 쓰고 cc4(+cc5)로 채움 | [09-21 §6](../debug_log/2026-09-21/SUMMARY.md) |
| 09-21 §7 cc4 | 첫 시도는 감사 출력 불완전 → 창 −0.172 로 계산돼 러너가 거부(정지 상태), 재시도 통과 | 성공 31.3 s · 미달 0 · 여유 12.5 · 복귀 회전 8.1~9.1 · Δ +1.4~+5.5 · 부호반전 2.6 | 파서 취약점 기록 | [drive_cc4_runner.txt](../debug_log/2026-09-21/outputs/drive_cc4_runner.txt) · [j435_cc4_verify.txt](../debug_log/2026-09-21/outputs/j435_cc4_verify.txt) · [j446_cc4.txt](../debug_log/2026-09-21/outputs/j446_cc4.txt) · [tegra_cc4.log](../debug_log/2026-09-21/outputs/tegra_cc4.log) · [rss_cc4.txt](../debug_log/2026-09-21/outputs/rss_cc4.txt) |
| 09-21 §7 cc5 | 같은 절차 | 성공 31.3 s · 미달 0 · 여유 12.9 · 9.0~9.2 · Δ −0.2~+2.5 · 부호반전 5.6 | — | drive_cc5 · j435_cc5 · j446_cc5 · tegra_cc5 · rss_cc5 |
| 09-21 §7 | 계측 요약: `job462_baghz.py`(bag 발행 주기) · `job463_tegra.py`(tegrastats) | GPU 0 % · CPU 6 코어 58~59 %(최대 92) · VDD_IN 6.6/7.9 W · tj 48.8 °C · RAM 1.6 GB · 로컬 코스트맵 1.67 Hz · 전역 0.57~0.67 · /plan 0.95 · cmd_vel 20 · odom 30 · scan 10 · tf 50 | **기준선 = cc2~cc5**, `BASELINE_STVL.md` 작성(표 · 한계 5 · 채택 기준 · 재현 절차) | [j462_baghz.txt](../debug_log/2026-09-21/outputs/j462_baghz.txt) · [j462_baghz_cc5.txt](../debug_log/2026-09-21/outputs/j462_baghz_cc5.txt) · [j463_tegra_cc4.txt](../debug_log/2026-09-21/outputs/j463_tegra_cc4.txt) · [j463_tegra_cc5.txt](../debug_log/2026-09-21/outputs/j463_tegra_cc5.txt) · 커밋 `84a41e6f` |
| 09-21 §8 | git: 사용자 결정 **main 은 건드리지 않는다**(회사 공용 리포). `feature/wt600-migration` push, 태그 `stvl-baseline` 은 로컬만 → 개인 리포 `personal` 생성 후 브랜치 + 태그 push | — | 계획서 'S5 후 main 병합 · 태그' 보류 | [09-21 §8](../debug_log/2026-09-21/SUMMARY.md) |
| 09-21 오후 | `TEST_COURSE_AND_GATES.md` v1.0 — 09-11~21 파편 규칙(배치 · 게이트 A~I · 절차 9 단계 · 운영 규칙 8)을 한 문서로 | — | Phase 가 바뀌면 절 단위로 새 판 | 커밋 `35308b81` |
| 09-21 | 계획서에 'Phase S 종료 · N0 착수 시 결정' | 위 §1 표 '09-21 종결' 열 | Phase N 시작(`feature/nvblox-migration`) | `NVBLOX_MIGRATION_PLAN.md` |
| 이후 09-22 §3.1 | N4: S 2 회(n4s1 · n4s2) + nvblox 3 회, 판정 = BASELINE §4 | S 여유 9.3 · 11.7 · CPU 318 · 315(기준선 재현), N 여유 12.3~14.6 · CPU 330~337 · GPU 3 % | **CPU 합 < 320 만 불합격**(로컬만 교체 — 릴레이 · 전역 STVL 잔존) → 사용자 결정 (a) 로컬 채택 | [Phase N 전반 카드](nvblox-migration-n0-n4.md) · BASELINE §6 |
| 이후 09-23 | N6 전역 이전 뒤 CPU 는 STVL 과 동등(320~325 %), 절감 기대 미달 → 채택 근거는 회피 여유 · 기억 · 3D/GPU 경로 | — | Phase N 종료 | [N6 카드](nvblox-n6-global-ghosts.md) · `Docs/05_nvblox/PHASE_N_RESULTS.md` |

### 2.1 기준선 표(BASELINE §2) — 칸마다 잰 방법
| 지표 | 기준선 | 잰 도구 · 원천 | 주의 |
|---|---|---|---|
| 결과 · 소요 · 거리 | 4/4 성공, 31.5 s | 러너 `job125_avoid3.py` '결과' 줄 | — |
| 중단 · 1 s 정지 · Optimizer fail · TF 외삽 | 0 | `job379_navevents.sh`(nav2 구간 로그) · 러너 csv | — |
| 제어 주기 미달 / EKF 위반 | 0 / 19~39 | nav2 로그 grep / `sensors.log` grep | **EKF 는 누적값**(§5 ①) |
| 코스트맵(로컬) 상자 최소 여유 | 8.4~12.9 cm | `job416_boxclear.py`(bag 로컬 코스트맵 상자 LETHAL ↔ 차체) via `run_j435*.sh` | 5 cm 칸 · 가장자리 점으로 실물보다 넓음(BASELINE §3-3) |
| 복귀 회전 자리(x 1.10~1.25) 여유 | ≥ 8.1 cm | 같은 job416 출력의 t 14~29 s 행 | — |
| 컨트롤러 − 원경로 여유 Δ(뒤 모서리) | 안으로 안 붙음 | `job446_pathdecomp.py`(전역 코스트맵 기준, L = 3 s) via `run_j446*.sh` | 엄밀히는 스무딩 → 실제([CostCritic 카드 §2.1](obstacles-to-costcritic.md)) |
| 러너 ① 실제 최근접 / ② 계획 여유 | ① 9.4~18.0 | job125 상자 사각형 모델(재고정 yaw ±5°) | 모델 기하라 코스트맵 여유와 다름 |
| ③ 상자 자리 비용 로컬/전역 | 99~100 | job125 `cost_at` | — |
| ④ 경로 좌우 전환 / 계획 접촉 샘플 | 0 / 0 % | job125 | — |
| ⑥ 상자 미관측 최대 s (깊이점 0 시작 전진 m) | 30.8~31.4 (0.31~0.35) | job125 `box_age` 최대 / csv `box_pts` 가 0 이 된 첫 전진 | **앞 숫자는 재고정 뒤 경과 시간**(§5 ②), 괄호 숫자만 카메라 관측 지표 |
| 직진 부호반전 /m · 고주파 \|ω\| | 1~5.6 · 0.08~0.09 | job125 | 위치 영향 < 0.1 mm(09-18) |
| SLAM 게걸음 각 · b | −0.8~−1.8° | `job431b_crab.py` | 코스 성분 vs 데크 잔여 미분리 |
| 전체 CPU % | ≈ 320(316~323) | `bags/top_ccN.log`(2 s) 스냅숏별 %CPU 합의 평균(11-02 같은 값 재계산) | 기록기 · 러너 · top 자신 포함(§5 ③) |
| 노드별 CPU | controller 34~35/66~69 · planner 11~12 · slam 11~12 · ekf 12 · realsense 14 · rplidar 15 · python3 108~110 · bt 15~16 | `job379_navevents.sh` top 절(이름별 평균/최대) | python3 은 이름이 같은 여러 프로세스 합(평균) · 하나(최대) |
| tegrastats CPU · 클럭 · GPU · 전력 · 온도 · RAM | 58~59 % · 1146~1187 MHz · 0 % · 6.6/7.9 W · 48.8 °C · 1.6 GB | `job463_tegra.py` ← `tegra_ccN.log`(cc4 · cc5 만) | 창 = 파일 전체 40 s(주행 앞뒤 포함) |
| 노드 RSS | realsense 103 · planner 89 · controller 67 · slam 45 MB | `rss_ccN.txt`(ps, 주행 전) | ps 의 %CPU 열은 수명 평균이라 쓰지 않음 |
| 발행 주기 | 로컬 1.67 · 전역 0.57~0.67 · /plan 0.95 · cmd_vel 20 · odom 30 · scan 10 · tf 50 Hz | `job462_baghz.py`(bag 수신 시각, 첫 ~ 마지막 움직임 지령 사이) | 로컬 '갱신 5 Hz' 는 설정값이라 bag 으로 못 봄 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 기준선이 다른 날에도 재현된다 | 09-22 N4 S 회차 2 번(같은 코스 · 같은 러너) | 여유 9.3 · 11.7(기준선 8.4~12.9 안), CPU 318 · 315(≈ 320) | **지지**(n = 2) — [Phase N 전반 카드](nvblox-migration-n0-n4.md) |
| STVL 이 CPU 병목이다(계획서 이전 트리거 b) | 기준선 노드별 CPU | STVL 은 controller_server 프로세스 안이라 따로 안 보임. 릴레이 ≈ 19~24 %, conditioner ≈ 43 % | **미확인**(분리 측정 없음). BASELINE §4 는 '릴레이 + STVL 분 ≥ 30 %p 감소 기대' 를 적었으나 그 30 %p 의 근거 계산은 기록에 없음 |
| cc1 을 빼도 된다 | cc1 미달 18 의 원인 판별 | 메타 스냅숏(절차) 탓으로 판정 | **지지(약함)** — [DDS 참여자 카드 §3](pre-drive-dds-participants.md) |
| 디시메이션 4 가 근거리 사각을 만든다(S2 전제) | 09-21 §5 dec 4 vs 2 | 끊김 거리 동일 | **기각** — [깊이 카드](depth-obstacle-costmap.md) |

## 4. 조치와 효과
- `BASELINE_STVL.md`: 구성(파일 md5 · 레이어 · 컨트롤러 · 센서 · 전력 모드 · 코스) · 주행 표본 표 · 알려진 한계 5(근거리 사각 0.43 m · 옆 통과 중 미관측 · 상자 셀 과대 · 게걸음 · 관찰자 흔적과 DDS 규칙) · **nvblox 채택 기준을 주행 전에 수치로**(같은 코스 3 회 중단 0 · 미달 ≤ 1, 여유 ≥ 8 cm · 평균 ≥ 11, ①④ 동등 이상, CPU 합 < 320 %, GPU · 전력 · 온도 한계 안) · 재현 절차 · (09-22 추가) 판정 결과.
- 러너 계측 추가(job231): tegrastats 1 s · 노드 RSS — 이후 모든 주행의 기본(10-27 에 top 루프는 /proc 틱 기록으로 대체).
- 복귀 지점: 태그 `stvl-baseline` + `navigation.launch.py camera_layer:=stvl`(설정 블록 보존 — 지금도 `_LOCAL_PLUGINS['stvl']` 로 남아 있음, 11-02 저장소 확인).
- 한계: 기준선은 '상자 하나 · 2 m 직진' 한 코스다. 사람 · 회전 · 좁은 문 · 긴 순회는 들어 있지 않다(이후 F0~F2 에서 별도 기준).

## 5. 한계 · 모순 기록(원문 대조)
- ① **'EKF 위반 0 / 19~39'(BASELINE 표)는 주행 중 횟수가 아니라 `sensors.log` 누적값**(센서 기동 뒤 전부). 주행 창 증분은 cc2 +1 · cc3 +1 · cc4 0 · cc5 0([drive_ccN_runner.txt](../debug_log/2026-09-21/outputs/drive_cc2_runner.txt) 'EKF 위반' 두 줄의 차). 기준선 표대로 읽으면 S6 조건(위반 0)이 크게 깨진 것처럼 보이지만 실제 주행 중은 0~1.
- ② **'⑥ 상자 미관측 최대 30.8~31.4 s' 는 카메라 미관측 시간이 아니다.** job125 의 ⑥ = `box_age` = 마지막으로 **채택된 재고정** 이후 경과(코드 `box_age = (now - t1) - last_fix_t`). 09-18 부터 재고정은 출발 yaw ±5° 안에서만 하므로 4 회 모두 0.5 s 에 1 번 채택된 뒤 끝까지 0 → ⑥ ≈ 주행 시간 − 0.5 s(31.9 − 0.5 = 31.4). 카메라가 상자를 못 본 시간은 csv `box_pts`(원시 점군 `/camera/camera/depth/color/points` 의 상자 영역 점 수)로 봐야 하고, 예: cc2 는 t ≈ 6 s(전진 0.36 m)에 0 이 된 뒤 끝까지 0([cc2.csv](../debug_log/2026-09-21/outputs/cc2.csv) · 러너 1 s 표). BASELINE 의 괄호 숫자(0.31~0.35 m)는 이 쪽이라 맞다. 09-22 nvblox 비교([Phase N 전반 카드](nvblox-migration-n0-n4.md))는 괄호 숫자(전진 0.31~0.35 m)를 썼다.
- ③ **CPU 합 ≈ 320 % 에는 계측 자신이 들어 있다**: top 의 'ros2'(= `ros2 bag record`, 평균 ≈ 20 %), 러너 python3(≈ 40 %, BASELINE 은 이것만 적음), top. N4 도 같은 러너 · 기록기를 써서 비교는 공정하지만, '< 320 %' 는 운용 CPU 가 아니라 '계측 포함 CPU' 기준이다.
- ④ tegrastats CPU '6 코어 평균 58~59 %'(= 약 350 % 상당)와 top 합 316~323 % 는 서로 다른 계기다(tegrastats 는 코어 바쁨 비율, 창도 주행 앞뒤 포함 40 s). 두 값을 섞어 쓰지 않는다.
- ⑤ 종료 조건 대비: S4 '직진 ω 부호반전 ≤ 1.0 /m' 에 기준선 4 회 모두 미달(1.05 · 2.0 · 2.6 · 5.6), S6 'load < 6' 도 러너 게이트 시점 load 6.45~10.30 으로 미달 — 둘 다 계획서 09-21 종결 절에서 '대체' · 언급 없이 넘어갔다. S2 '끊김 ≤ 0.35 m' 는 **센서 기준**으로 통과 판정했고, 코스트맵이 실제로 받는 한계(릴레이 0.45 m)는 조건을 넘는다 — 판정 문구('센서 기준 통과')가 그 구분을 적어 두긴 했다.
- ⑥ 계획서 S5 표는 '노드별 CPU — 주행 중 30 초 평균', '코스트맵 갱신 주기 — hz' 였는데 실제는 주행 전체 창(≈ 40 s) 평균, bag 발행 주기(갱신 아님)다. BASELINE 이 '갱신 5 Hz 는 설정값, bag 으로 못 봄' 으로 적어 둠.
- ⑦ BASELINE §2 머리 '(cc1 은 주행 직전 메타 스냅샷의 DDS 부하로 제외)' — 판정의 강도는 [DDS 카드](pre-drive-dds-participants.md) §3 · §5(스냅숏 앞 게이트에서 이미 SLAM 발행 절반).
- ⑧ 상자 치수: BASELINE '18×14×11 cm' · 09-08 사용자 실측 '폭 0.18 · 높이 0.11 · 세로 0.11'. 09-21 §5 의 픽셀 기하 모델은 정면 폭을 0.14 로 두면 맞고 0.18 이면 17~24 % 어긋난다([깊이 카드 §5.18](depth-obstacle-costmap.md), 내 재계산) — 어느 면이 로버를 보는지 미확인.

## 6. 내 실수
### M1. 재고정 경과 시간을 '상자 미관측' 으로 기준선에 넣음 (09-21 §7 BASELINE ⑥)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 계획서 S5 '장애물 지속 시간(깊이점 소실 후 마킹 유지 시간)' 칸을 러너 지표로 채우기 — 러너 끝 요약의 '⑥ 상자 미관측 최대 N초' 줄을 그대로 옮김 |
| 본 것 | cc2~cc5 ⑥ = 31.4 · 30.8 · 30.8 · 30.8 s([drive_cc2_runner.txt](../debug_log/2026-09-21/outputs/drive_cc2_runner.txt) 52 행 등), 같은 표의 소요 31.3~31.9 s |
| 처음 추론 | '상자가 출발 직후 화각을 벗어나 주행 거의 내내 미관측 → STVL 기억으로 주행' (BASELINE §3-2 '이후 25~30 s 는 STVL 기억으로') |
| 의심한 이유 | (11-02 이 카드 작성 중) ⑥ 이 4 회 모두 '소요 − 0.5 s' 와 같다 — 장면에 따라 달라야 할 관측 시간이 주행 시간과 0.1 s 단위로 일치. 재고정 기록은 4 회 모두 '채택 1(0.5 s)' |
| 판별 시험 | job125 코드 읽기: `box_age = (now - t1) - last_fix_t`, `last_fix_t` 는 재고정 **채택** 때만 갱신, 재고정은 \|dyaw\| ≤ REFIX_YAW(±5°)일 때만 시도(09-18 1안). csv `box_pts` 로 실제 관측 끊김 시각 확인(cc2 t ≈ 6 s) |
| 결론 | ⑥ 의 앞 숫자는 '재고정 뒤 경과' 이며 09-18 재고정 제한 이후 주행 시간과 같아지는 값. '25~30 s 기억 주행' 이라는 결론의 방향은 `box_pts` 로도 같다(전진 0.31~0.35 m 부터 0, 그 뒤 25 s 안팎) — 수치의 출처만 틀렸다. 09-22 비교는 괄호 숫자를 써서 영향 없음 |
| 다음에 알아보는 법 | 서명: **지표가 회차 사이에서 주행 시간과 함께만 움직인다**(장면과 무관) → 정의를 코드에서 확인. 규칙: 러너 요약 줄을 표로 옮길 때 그 변수의 갱신 조건을 한 번 읽는다. 앞판 정의(09-10, 재고정이 늘 가능하던 때)와 지금 정의가 같은지 본다 |
| 데이터 | 도구 `2026-09-21/jobs/job125_avoid3.py`(302~324 · 411 행), 결과 `outputs/drive_cc2~5_runner.txt` · `cc2~5.csv` · `cc2~5_refix.csv` |

- cc1 의 메타 스냅숏 실수는 [DDS 참여자 카드 §6 M1](pre-drive-dds-participants.md).

## 7. 남은 것
- STVL 자체 CPU 몫(컨트롤러 · 코스트맵 프로세스 안) 분리 — Phase S 에서 안 함. N6 뒤 CPU 동등(320~325 %)이라 '절감' 은 결과적으로 없었다(09-23).
- S3 동적 망각은 STVL 에선 해결하지 않음 — nvblox 쪽 과제(사람 이동 강건성은 이후 시기).
- S4 부호반전 ≤ 1.0 /m · S6 load < 6 은 판정 없이 넘어감(§5 ⑤).
- 기준선의 코스 일반성(상자 하나 · 2 m) — F0 이후 순회 코스는 다른 기준.
- 이후(09-22 ~): N4 비교 세부는 [Phase N 전반 카드](nvblox-migration-n0-n4.md), N6 · 최종은 [N6 카드](nvblox-n6-global-ghosts.md).

## 8. 실험 · 도구 색인
- 주행: 09-21 cc2 · cc3 · cc4 · cc5(기준선), cc1(제외). bag `Docs/debug_log/2026-09-21/bags/bag_ccN.tgz` · top `bags/top_ccN.log`(로컬, git 제외).
- 결과: `2026-09-21/outputs/` — drive_ccN(.txt · _runner.txt) · ccN.csv · ccN_refix.csv · j379_ccN · nav2_ccN.log · j435_ccN_verify · j446_ccN · meta_ccN · params_ccN · prep_ccN · tegra_cc4/5.log · rss_cc4/5.txt · j461_tegratest · j462_baghz(_cc5) · j463_tegra_cc4/5.
- 도구: `run_mp9prep.sh`(09-17 폴더) · `run_drive_nohup.sh` → `job254_s4run.sh` → `job231_drive.sh` → `job125_avoid3.py` · `run_post3.sh` → `job379_navevents.sh` · `run_j435h~k.sh`(job416 · 426 · 431 · 431b) · `run_j446c~f.sh`(job446) · `job461_tegratest.sh` + `run_j461.sh` · `job462_baghz.py` + `run_j462.sh` · `run_j462b.sh` · `job463_tegra.py`.

## 9. 도구 해설
공통: PC WSL 감싸개 → Jetson `/tmp`(`sshpass -p <PW>`). 09-21 새 감싸개(`run_j46x.sh`)는 이 세션 스크래치패드(`21d4aa9f…`, `NSPS=`)를, 주행 묶음은 옛 스크래치패드(`82ce61d4…`, 09-28 소실)를 가리킨다 → 다시 쓰려면 저장소 `jobs/` 를 올린다. 주소는 당시 192.168.0.101.

### 주행 · 회수 · 검증 묶음 — 다른 카드 해설로
| 도구 | 이 카드에서 맡은 칸 | 해설 위치 |
|---|---|---|
| `run_mp9prep.sh`(09-17) | 회차마다 스택 재기동(job240) · 릴레이 · readback · 상자 게이트(run_gate2) · 크리틱 readback(job403) · SLAM 생존 · 목표 여유 | [MPPI 통로 카드 §9.6](mppi-passage-tuning.md) |
| `run_drive_nohup.sh` · `job254_s4run.sh` | 게이트 → 주행 | [DDS 참여자 카드 §9](pre-drive-dds-participants.md) |
| `job231_drive.sh` | bag · top · **tegrastats · RSS(09-21 S5 추가)** · 러너 · 메타 | [DDS 참여자 카드 §9](pre-drive-dds-participants.md) |
| `job125_avoid3.py` | ①~⑥ · 부호반전 · 재고정 기록 | [회피 계측 카드](avoid-run-metrics.md) · [깊이 카드 §8](depth-obstacle-costmap.md)(09-09 판) — ⑥ 정의는 위 §5 ② |
| `run_post3.sh` → `job379_navevents.sh` | nav2 사건 · top 이름별 평균/최대 · 회수 9 종(09-21 tegra · rss 추가) | [CostCritic 카드 §9 표](obstacles-to-costcritic.md) · [SLAM 데드락 카드](slam-dds-deadlock.md) |
| `run_j435*.sh` · `run_j446*.sh` | 코스트맵 여유 · 복귀 회전 · Δ · 게걸음 | [CostCritic 카드 §9](obstacles-to-costcritic.md) |

### job461_tegratest.sh · run_j461.sh — tegrastats 가 sudo 없이 되는지
- 실행 위치 · 형태: PC `run_j461.sh [job461_tegratest.sh]` → Jetson `bash /tmp/job461_tegratest.sh`.
- 왜: 계획서 S5 의 GPU · 전력 · 온도 칸을 채우려면 주행 중 tegrastats 가 필요한데, 러너는 sudo 없이 돈다(sudo 가 되는지부터).
- 하는 일: `command -v tegrastats` 위치, `timeout 4 tegrastats --interval 1000 | head -2`(앞 260 자), 종료 코드.
- 출력: [j461_tegratest.txt](../debug_log/2026-09-21/outputs/j461_tegratest.txt) — `/usr/bin/tegrastats`, 두 줄(RAM 1595/7607 MB · CPU 6 코어 % @ MHz · GR3D 0 % · 온도 · VDD_IN 5716 mW), rc 0.
- 쓰인 곳: §6 'sudo 없이 동작 확인' → job231 에 tegrastats 추가. 계보 · 지금: 일회성. 결함: `rc=$?` 는 파이프 끝(cut)의 종료 코드라 tegrastats 자체 성공 여부는 아님(출력 두 줄이 실제 근거).

### job462_baghz.py · run_j462.sh · run_j462b.sh — bag 에서 토픽별 실측 발행 주기
- 실행 위치 · 형태: Jetson(`rosbag2_py` 필요), `python3 /tmp/job462_baghz.py /tmp/bag_cc2 /tmp/bag_cc3 /tmp/bag_cc4`(run_j462) · `/tmp/bag_cc5`(run_j462b). timeout 600 s.
- 왜: 계획서 S5 '코스트맵 갱신 주기 실측' 을 주행 전 `ros2 topic hz`(참여자 생성 — [DDS 규칙](pre-drive-dds-participants.md)) 없이 사후에.
- 하는 일: bag 을 처음부터 읽어 10 토픽(`/local_costmap/costmap` · `/global_costmap/costmap` · `/plan` · `/plan_smoothed` · `/cmd_vel` · `/odometry/filtered` · `/wheel_odom` · `/scan` · `/tf` · `/map`)의 **기록 시각**(bag 수신 시각, 메시지 stamp 아님)을 모음. 주행 창 = `/cmd_vel` 중 \|v\| > 0.01 또는 \|ω\| > 0.02 인 첫 ~ 마지막 시각. 창 안에서 개수 · Hz = (개수 − 1)/(마지막 − 처음) · 간격 중앙 · 최대.
- 출력: 토픽마다 '개수 · Hz · 간격 중앙 · 최대' 한 줄. [j462_baghz.txt](../debug_log/2026-09-21/outputs/j462_baghz.txt)(cc2~cc4) · [j462_baghz_cc5.txt](../debug_log/2026-09-21/outputs/j462_baghz_cc5.txt). 예: cc2 로컬 코스트맵 53 개 1.67 Hz(간격 0.600) · 전역 18 개 0.57 Hz · /tf 1595 개 50.02 Hz.
- 쓰인 곳: BASELINE 발행 주기 줄, 09-22 N4 비교. 판정 영향: 로컬 코스트맵 1.67 Hz = `publish_frequency` 설정(갱신 5 Hz 와 구분)이라는 해석.
- 계보 · 결함 · 지금: 이후 `Docs/tools/anal_bag_rates.py`(10-13, 기록기가 받은 수 · 주기 · 크기를 bag 여러 개 나란히 — 목적은 통신 포화 조사)가 비슷한 일을 상설 도구로 한다. 결함: 기록 시각 기준이라 기록기 지연이 섞임, sqlite3 저장소 고정(mcap bag 은 못 읽음). 지금 다시 쓸 수 있음(로컬 bag 을 Jetson 이나 ROS 있는 곳에 풀면).

### job463_tegra.py — tegrastats 로그 요약
- 실행 위치 · 형태: `python3 job463_tegra.py tegra_cc4.log [tegra_cc5.log …]` — 파일만 읽는 순수 파이썬(numpy). 감싸개가 없어 어디서 돌렸는지 기록 없음(회수된 로그를 PC 에서 돌렸을 것, 추정).
- 왜: S5 의 GPU · 전력 · 온도 · RAM 칸.
- 하는 일: 줄마다 정규식으로 `RAM a/bMB` · `(\d+)%@(\d+)`(코어별 부하 · 클럭 → 6 코어 평균) · `GR3D_FREQ n%` · `cpu@` · `gpu@` · `tj@` 온도 · `VDD_IN n mW` · `VDD_CPU_GPU_CV n mW` 를 뽑아 평균 · 최대. 창 = 파일 전체(러너가 주행 앞뒤 몇 초를 더 기록).
- 출력: 파일당 한 줄. [j463_tegra_cc4.txt](../debug_log/2026-09-21/outputs/j463_tegra_cc4.txt): 40 s · RAM 1601/1618 MB · CPU 평균 59 % 최대 88 % · 클럭 1187 MHz · GR3D 0.0 % · tj 48.4(최대 48.8) °C · VDD_IN 6602/7827 mW · CPU+GPU+CV 1744 mW. cc5 는 [j463_tegra_cc5.txt](../debug_log/2026-09-21/outputs/j463_tegra_cc5.txt).
- 쓰인 곳: BASELINE tegrastats · GPU · 전력 · 온도 · RAM 줄, 채택 기준(6.6/7.9 W · 48.8 °C). 결함: 'CPU 최대' 는 6 코어 **평균의** 최대(한 코어 최대 아님), 주행 창을 따로 자르지 않음(§5 ④). 계보 · 지금: 이후 러너가 tegrastats 를 상시 기록, 요약 도구는 날짜별로 재작성 — 이 판도 다시 쓸 수 있음(형식 같으면).

### top 합계(11-02 이 카드에서 계산 — 도구 파일 없음)
- 형태: `awk '/^top -/{if(n)print s; s=0; n++} /^ *[0-9]+ /{s+=$9} END{print s}' bags/top_ccN.log` → 스냅숏별 %CPU 합, 그 평균 · 최대.
- 값: cc1 433/473 · cc2 316/405 · cc3 321/454 · cc4 323/426 · cc5 317/434. BASELINE '전체 CPU %' 316 · 321 · 323 · 317 과 일치 — 09-21 에도 같은 방식으로 셌다고 봄(그날 쓴 명령은 기록 없음).
- 한계: top `-w 180` 출력의 9 번째 열이 %CPU 라는 가정, 첫 스냅숏(누적 평균) 포함.

## 10. 용어
- **Phase S / Phase N**: 계획서의 두 단계 — S = 현재 스택(STVL) 개선 · 기준선, N = nvblox 이전(N0 설치 ~ N6 전역 이전).
- **기준선(baseline)**: 같은 코스 · 같은 러너 · 같은 계측으로 잰 '바꾸기 전' 표. 채택 기준을 그 위에 수치로 미리 적어 둔다.
- **STVL**: spatio_temporal_voxel_layer — 복셀마다 관측 시각을 두고 시간 감쇠 · 깊이 절두체 소거로 지우는 Nav2 코스트맵 층([깊이 카드 §9](depth-obstacle-costmap.md)).
- **depth_relay**: 우리 노드. 원시 점군에서 카메라 거리 < min_range(0.45) 제거 · 복셀 점 수 < 3 제거 · 5 프레임 중 3 지속 → `/camera/depth/points_filtered`([깊이 릴레이 카드](depth-relay-artifacts.md)).
- **재고정(refix)**: 러너 job125 가 주행 중 상자 사각형을 새 검출로 다시 놓는 것. 09-18 부터 출발 yaw ±5° 안에서만.
- **tegrastats · GR3D · VDD_IN · tj**: Jetson 상태 출력 도구 · GPU 사용률 · 보드 입력 전력 · 접합부 온도(가장 뜨거운 지점).
- **RSS**: 프로세스가 실제 차지한 물리 메모리.
- **태그 `stvl-baseline`**: 기준선 시점 커밋(84a41e6)에 붙인 git 태그 — nvblox 를 기각할 때 돌아갈 자리.
