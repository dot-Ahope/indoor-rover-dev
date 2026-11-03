# rf2o 도입 — 라이다 스캔 정합 속도로 회전 중 미끄러짐을 EKF 에 (5 기 10-02 §13~§18 · 6 기 10-06 ~ 10-08)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| 10-02 시점 **오프라인 통과(R2)** — rf2o 게이트 + '순수 회전 중 휠 병진 σ 0.3' 의 EKF B 가 통제 회전 rot3 을 줄자 대비 **4.3 cm**(지금 EKF 36.9 cm)로 따라가고 직진 축척 **0.998** 유지(재생 **측정**). 구석 기동 지표 R2-c 는 선언 기준 불합격(지표 설계 실수). 라이브 미적용. **10-08 시점 라이브 통과(통제 회전)** — 정식 노드(R3)로 제자리 ±90° × 3 을 한 단계씩 돌며 줄자: EKF B \|오차\| 평균 **1.5 cm**, 방향 원위치 단계 0.0 / +0.1 / +0.7 cm(그림자 EKF A 7.8 cm · 원위치 −10.0 → −15.5 → −17.0 cm 누적) **측정**. 순회(f2c · f2d, 사람 없음)에서는 제자리 회전 구간 번짐 B < A 4/4 이지만 차 0.4~1.5 cm · 최대 10.3 cm 로 **판정 불가에 가까움**, 기본값 결정은 안 함(기본 끔 유지). 사람 · 가림 · 게이트 G1~G4 는 [게이트 · 사람 시험 카드](rf2o-gates-people.md). 이후: **10-23 주 EKF 병진 = cuVSLAM 으로 결정, rf2o 는 기본으로 안 띄움**(지금 `ekf.launch.py rf2o` 기본 false · prep 기본 `ODOM=vslam`) | 10-02 · 10-06 ~ 10-08 (이 카드는 10-02 §13~§18 · 10-06 §1~§4 · §8 · 10-07 §2~§3 · §6 · §15 · 10-08 §3 · §5 · §6.1 의 rf2o 부분을 채움. 10-06 §5~§13 · 10-07 §1 · §3.1 · §3.2 · §4 의 게이트 · 사람 시험은 [별도 카드](rf2o-gates-people.md), 10-12 ~ 는 포인터) | [10-02 §13](../debug_log/2026-10-02/SUMMARY.md) — §12.1 에서 로컬 map 좌표 대책이 불합격한 뒤 사용자 결정 | (10-02) Jetson `~/rf2o_ws`(MAPIRlab `rf2o_laser_odometry` ros2 브랜치 b38c68e) 소스 빌드 · 오프라인 원형 `r2_gate.py`. (지금, 10-06 이후) [`rf2o_gate.py`](../../ros2_ws/src/rover_bringup/scripts/rf2o_gate.py) · [`rf2o.yaml`](../../ros2_ws/src/rover_bringup/config/rf2o.yaml) · [`ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py) `rf2o:=` · `shadow:=` · `gate_*:=` 인자(기본 끔) · `Docs/tools/prep_patrol.sh ODOM=rf2o` | [회전 중 장애물 번짐](rotation-obstacle-smear.md)(동기) · [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(대책 방향 D 의 출발점) · [휠 오도 스케일 · 회전 슬립](wheel-odom-scale-slip.md) · [센서 컨디셔너](sensor-conditioner.md)(B3 공분산) · [센서 데크 yaw −2.68°](sensor-deck-yaw.md)(라이다 yaw 상수) · [slam-fork-rotation.md](slam-fork-rotation.md) · [F2 순회와 위치 점프](f2-patrol-loc-jump.md) · [rf2o 게이트 G1~G4 · 사람 시험](rf2o-gates-people.md)(6 기 갈래) · [회전축 보정 B2 · 회전 분산 B3](icr-b2-b3.md)(B3 = rf2o 의 짝) · [회전 방식 · 트랙 비율](rotation-method-track-ratio.md)(10-08 피벗 시험) · [남서 구석 방향 맞춤 정체](southwest-orient-stall.md)(f2c1 · f2d1 실패) · [낮은 상자 기억](low-box-global-memory.md)(f2c2 상자 접촉) · [전선 밟기](cable-step-over.md) (6 기) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md) · [상자 칸 과장의 근원](box-exaggeration-source.md) (8 기) |

**한 줄**: 회전 중 미끄러짐 30 cm 를 EKF 가 0.3 cm 로 보고(rot2), 회전 모델 B2 와 로컬 map 좌표 둘 다 대책이 못 되자 사용자가 rf2o(연속 라이다 스캔 정합으로 차체 속도를 내는 오도메트리) 도입을 시작했다. 같은 회전 bag 을 rf2o 에 다시 먹이니 rf2o 의 순 이동은 두 시험 모두 0.35 · 0.37 m 로 일관됐고(SLAM 0.322 · 0.114, EKF 0.003), 사용자 줄자(rot3 뒤 27.5 · 오른쪽 24.5 cm)는 rf2o 의 **크기 · 성분과 맞고 부호만 두 축 다 반대**였다 — 라이다가 yaw π − 2.68° 로 뒤집혀 달려 병진이 라이다 좌표로 나온 것이라 차체 속도 = R(π − 0.04677) · v_rf2o 로 고쳤다. 게이트(G1 자이로 일치 · G2 정지 검사 · 가변 σ)를 거쳐 병진 vx · vy 만 EKF 에 넣는 B 를 오프라인 재생 5 차례로 다듬었는데(자이로 없는 bag · QoS 불일치 · 휠이 rf2o 를 누름 · G1 오거부), 마지막 판은 rot3 끝을 줄자 4.3 cm 안으로 잡고 직진 축척을 유지했다. 사용자는 다음 시험을 '90° 마다 줄자' 로 설계했다(→ 10-06 실행). **6 기(10-06 ~ 10-08)**: 게이트를 정식 노드 · `ekf.launch.py rf2o:=` 인자(기본 끔)로 옮겨 라이브로 그 시험을 하니 EKF B 가 줄자를 평균 1.5 cm 로 따라갔고(그림자 EKF A 는 원위치 단계마다 미끄러짐을 0 으로 봐 17 cm 까지 쌓임), rf2o 를 켠 채 F2 순회(f2c 9/10)도 했지만 순회 중 제자리 회전이 4 번뿐이고 기준 SLAM 자체가 수 cm 틀려 번짐 개선을 수치로 보이지 못했다. 직진 드리프트(map→odom 누적 보정 0.42 m)는 rf2o 로 줄지 않았다(직진 몫 2~4 %). 10-08 회전 방식 시험은 미끄러짐이 거의 항상 '차체 뒤로'(38/40)이지만 크기가 회마다 달라(90°당 −18.6~+1.1 cm) 고정 보정 모형(90°당 오차 7.9 → 5.8 cm)이 rf2o 같은 외부 관측을 대신하지 못한다고 정리했다.

## 1. 증상 (도입 동기)
- 통제 회전 rot2(±90° × 3, ω 0.38 rad/s): 누적 이동 **SLAM 0.322 m vs EKF 0.003 m**, 라이다 외곽 최근접 0.397 → 0.212 m([`smear_rot2.txt`](../debug_log/2026-10-02/outputs/smear_rot2.txt), 10-02 §11.1). 로컬 코스트맵 옛 칸 4 → 95.
- 대책 두 가지 실패: B2 회전축 모델(§8.2, 짧은 회전에서 오차 중앙 4.7 > 지금 3.1 cm) · 로컬 코스트맵 map 좌표(§12.1, rot3 번짐 9.2 cm) — [회전 중 장애물 번짐](rotation-obstacle-smear.md).
- 09-23 · 09-29 에 이미 정한 방향: 대책 D = '옆 속도를 재는 입력(rf2o · cuVSLAM)의 **속도만** odom EKF 에 + 회전 중 휠 공분산 키움', rf2o 필수 조건(09-29 §6.1) = 자이로 일치 · 정지 검사 · 가변 σ([F0-a 카드](f0-rotation-side-slip.md) §2).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-02 §13 | 사용자 결정 '**rf2o 도입 작업 시작**' + 사용자 진단 '미끄러짐은 **트랙-바닥 마찰** 문제 — 한쪽 트랙을 거의 세우고 반대쪽만 움직여 회전축을 트랙에 두는 방식(피벗 회전)을 써야 한다' | 계획 R0 소스 빌드 → R1 재생 확인 → R2 게이트 노드(EKF 에 **병진 vx · vy 만**) → R3 bag 재생 EKF A/B → R4 실시험(통제 회전 + 사람 T1~T3 + F2 순회). 피벗 회전 = 회전축을 한쪽 트랙(중심에서 궤간/2 ≈ 0.145 m)에 — MPPI Ackermann 최소 회전 반경 0.145 m 로 표현 가능(제자리 회전 금지 · 한 트랙 정지 회전 허용) | 원래 JetPack 7.2 단계 항목을 앞당김. 피벗 회전 비교 시험(지령 v = ω · 0.145)은 R1 뒤에 두기로(**10-02 에는 미실행**) | — |
| 10-02 §13 R0 | 소스 확인 · 빌드 | MAPIRlab `rf2o_laser_odometry` ros2 브랜치 **b38c68e(2023-04-28)**, `~/rf2o_ws` Release 빌드 1 min 8 s. 소스 grep 에 `covariance` 줄 **0** | **발행 Odometry 에 공분산을 안 채움** → 게이트 노드가 σ 를 정해야 함 | [`job833_rf2o_src.sh`](../debug_log/2026-10-02/jobs/job833_rf2o_src.sh) · [`job834_rf2o_build.sh`](../debug_log/2026-10-02/jobs/job834_rf2o_build.sh) · [`j834_rf2o_build.txt`](../debug_log/2026-10-02/outputs/j834_rf2o_build.txt) |
| 10-02 §13.1 R1 | rot2 · rot3 bag 을 rf2o 에 재생(도메인 42 · sim time · `publish_tf false`) — rf2o vs SLAM(map) vs EKF(odom) | 순 이동 rf2o **0.350 / 0.370** · SLAM 0.322 / 0.114 · EKF 0.003 / 0.003 m. 순 회전 rf2o +4.2 / +7.8 · SLAM −1.4 / 0.0 · EKF −3.1 / +0.7°. 회전 중 ω 비 rf2o/EKF 중앙 **0.994 / 0.989**(표본 258 / 260). 회전 중 rf2o 병진 \|v\| 중앙 0.014 / 0.015 · 최대 0.091 / 0.090 m/s. 경로 길이 rf2o 1.96 / 1.89 · SLAM 0.80 / 0.79 · EKF 0.03 / 0.02 m | 실제 미끄러짐이 비슷했는데(라이다 최근접 0.397 → 0.212 · 0.407 → 0.192) **rf2o 만 일관**. 회전 속도는 자이로와 1 % 안이지만 540° 뒤 각 누적 오차 4~8° → **EKF 에는 병진만, 회전은 자이로 유지**. 경로 길이가 순 이동의 5 배 = 회전 중 병진 잡음(중앙 1.4 cm/s) → σ 를 이 수준에. CPU: 재생 47 s 에 누적 3 s(코어 하나 ≈ 6 %, **출력 원문 없음**). **실측 필요**: rot3 실제 이동(줄자) | [`job835_rf2o_replay.sh`](../debug_log/2026-10-02/jobs/job835_rf2o_replay.sh) · [`job835_rf2o_rec.py`](../debug_log/2026-10-02/jobs/job835_rf2o_rec.py) · [`rf2o_cmp.py`](../debug_log/2026-10-02/jobs/rf2o_cmp.py) · [`rf2o_cmp_rot23.txt`](../debug_log/2026-10-02/outputs/rf2o_cmp_rot23.txt) · npz `rf2o_rot{2,3}.npz`(스크래치패드, **원천 소실**) |
| 10-02 §13.2 | **사용자 줄자**: rot3 동안 로버가 **뒤로 27.5 cm · 오른쪽으로 24.5 cm(0.368 m)** | rf2o 자세 차 (+0.274, +0.249) 0.370 m — **크기 · 성분 5 mm 안, 부호만 두 축 반대**. SLAM (−0.047, −0.104) 0.114 m. 직진 bag(f2b4) 재생에서도 rf2o vx / EKF vx 음수 | **rf2o 가 맞고 SLAM(위치 추정 모드)은 틀림**. 라이다가 뒤집혀(yaw π − 2.68°) 달려 rf2o 병진이 라이다 좌표 방향으로 나옴(회전 부호는 맞음, `PoseUpdate` 의 laser_pose_ / robot_pose_ 합성 — 초기 자세 주입 없이 쓰면 생기는 것으로 **추정**). **보정: 차체 속도 = R(π − 0.04677) · v_rf2o**. 지렛대 ω × r 추가 보정은 경로 길이 0.54 → 1.65 m 로 '오히려 나빠짐 = rf2o 가 이미 반영' 으로 판단(§5 모순 2 참조) | [`rf2o_fix.py`](../debug_log/2026-10-02/jobs/rf2o_fix.py) · [`rf2o_fix.txt`](../debug_log/2026-10-02/outputs/rf2o_fix.txt) · 줄자 원문 = 대화(사용자 보고) |
| 10-02 §13.2 직진 축척 | f2b4 직진 3 s 창 | SUMMARY: SLAM/EKF **1.000**, rf2o/SLAM **0.932**(창 16 개) — 원문 `rf2o_fix.txt` 는 EKF 기준 rf2o vx 비 **0.911**(회전 보정 b, 표본 683) | 직진에서 rf2o 는 병진을 약 7~9 % 작게 봄 → 직진 vx 는 휠 우선. R2 설계: \|ω\| 작을 때 vx σ 크게, 회전 중 vx · vy σ 작게 | 0.932 · 1.000 · '16 개' 는 **출력 원문 없음**(§5 모순 1) |
| 10-02 §14 선언 | R2 오프라인 — EKF **A** = 지금 설정(휠 vx 0.02² · vy 0.01² · vyaw 0.1²) / **B** = A + B3(휠 순수 회전 \|vx\| < 0.02 · \|ω\| > 0.10 동안 vx · vy 0.03²) + **odom1 = rf2o 게이트(vx · vy 만)**. 게이트: G1 \|Δω\| > max(0.05, 0.3\|ω\|) 버림 · G2 휠 정지인데 rf2o \|v\| > 0.02 버림 · σ 회전 중 0.03 / 직진 vx 0.10 · vy 0.03. bag: rot3 · rot2 · f2b3 · f2b4 | — | 판정 **R2-a** rot3 끝 이동 vs 줄자 B 오차 ≤ 5 cm · **R2-b** f2b4 직진 축척 B/SLAM 0.97~1.03 · **R2-c** f2b3 구석 기동(13:25:30 +26~49 s) 서쪽 구조물을 각 EKF odom 좌표로 옮긴 범위 B ≤ A/2 · R2-d 게이트 거부율 기록 | [`r2_run.sh`](../debug_log/2026-10-02/jobs/r2_run.sh) · [`r2_gate.py`](../debug_log/2026-10-02/jobs/r2_gate.py) · [`r2_rec.py`](../debug_log/2026-10-02/jobs/r2_rec.py) · [`r2_eval.py`](../debug_log/2026-10-02/jobs/r2_eval.py) |
| 10-02 §14.1 1 차 | 재생 | 회전 시험 bag 에 `/imu/data` 없음 → 게이트 자이로 0 → 회전 중 rf2o 를 G1 이 거의 다 버림 | **무효**(§5 실수 1). 고침: 자이로가 1 s 넘게 없으면 라이브 EKF 회전 속도를 대용(`/r2/live_w` 로 중계, EKF odom2 vyaw σ 0.02) | 수치 버림 |
| 10-02 §14.1 2 차 | 재생 | 게이트가 `/wheel_odom` 을 reliable 로 구독 — bag 재생 발행은 micro-ROS 원래대로 best-effort → **휠 입력 0**(EKF A 출력 0, B 는 rf2o 만으로 움직임) | **무효**(§5 실수 2). 고침: 센서 QoS(best-effort) | 수치 버림 · [`job843_dbg.sh`](../debug_log/2026-10-02/jobs/job843_dbg.sh)('EKF A 가 휠을 융합하지 않는 이유' 확인) · `job841_imuaxis.py` · `job842_stamp.py` |
| 10-02 §14.1 3 차 | 휠 정상 | A = 라이브와 일치(R2-a 기준). B(휠 B3 σ 0.03 + rf2o σ 0.03): rot3 이동 **7.2 cm**(줄자 36.8) | 휠(25 Hz)의 '옆 이동 0' 이 rf2o(10 Hz)를 눌러 미끄러짐을 대부분 지움 → 순수 회전 중 휠 병진 σ 를 **0.3**(사실상 무시, `rot_sd`) | 3 차 CSV(\|Δω\| 90 % 값 직진 0.09 · 회전 0.12)는 **원천 소실** |
| 10-02 §14.1 4 차 | 휠 회전 σ 0.3 | R2-a A 0.369 / **B 0.038 m**((−0.298, −0.214)) ✔ · R2-b A 0.999 / **B 0.998** ✔ · R2-c A 0.128 / B 0.107 m ✘ · R2-d G1 거부 rot3 29/402 · **f2b3 561/1516(37 %)** | R2-c 미달 해석: 구석 기동은 후진 · 회전 섞임 → B3(휠 \|vx\| < 0.02 일 때만)가 거의 안 걸리고, G1 이 움직이는 중 34~37 % 를 버림(사람 없는데도 — 시각 어긋남 · 잡음, §5 실수 3). → 5 차: G1 을 rf2o 추정 구간(0.1 s)의 자이로 **평균**과, 바닥 **0.12** | 4 차 출력 원문 없음(SUMMARY 표만) |
| 10-02 §14.2 5 차(마지막) | G1 시각 맞춤 · 바닥 0.12 | G1 거부 rot3 3 · rot2 2 · f2b3 2 · f2b4 2(1~2 ‰). R2-a A 0.369 / **B 0.043 m** ✔ · R2-b A 1.000 / **B 0.998** ✔ · R2-c 중심 흔들림 A 0.131 / B 0.112 ✘(기준 0.065) | R2-c 재검토(기준을 바꿔 통과시키지 않음, 둘 다 기록): 같은 지표를 **SLAM 자세로 계산해도 0.079 m** — 회전하며 보이는 부분이 바뀌어 중심이 움직이는 몫이라 **선언 기준(0.065)은 SLAM 도 못 넘는 값**(지표 설계 실수, §5 실수 4). '안쪽 면'(x 95 백분위) 범위로는 **A 0.198 · B 0.099 · SLAM 0.084 m**. 오프라인 조정은 여기서 멈춤(같은 bag 과적합 방지). R2 결론: 게이트 + 회전 중 휠 병진 σ 0.3 + rf2o σ(회전 0.03 / 직진 vx 0.10 · vy 0.03) | [`r2_eval_run5.txt`](../debug_log/2026-10-02/outputs/r2_eval_run5.txt) · 게이트 csv [`r2_rot3_gate.csv`](../debug_log/2026-10-02/outputs/r2_rot3_gate.csv) · [`r2_rot2_gate.csv`](../debug_log/2026-10-02/outputs/r2_rot2_gate.csv) · [`r2_f2b3_gate.csv`](../debug_log/2026-10-02/outputs/r2_f2b3_gate.csv) · [`r2_f2b4_gate.csv`](../debug_log/2026-10-02/outputs/r2_f2b4_gate.csv) |
| 10-02 §15 | 하루 마무리 시각화 · 정리 페이지 | 그림 `rot3_paths`(줄자 대비 A · B · SLAM · rf2o) · `smear_rot23` · `f2b3_wall_AB`(A 19.8 · B 9.9 · SLAM 8.4 cm) · `r2_runs`. 정리 페이지 [`2026-10-02_report.html`](../debug_log/2026-10-02/2026-10-02_report.html)(그림 9 장 내장) | rf2o 는 `~/rf2o_ws` 빌드만, 라이브 스택엔 안 들어감. 다음 R3 = 게이트 노드 라이브(ekf.launch 인자, 기본 끔) → 통제 회전 + 줄자 → 사람 T1~T3 · 피벗 회전 시험 | [`render_day1002.py`](../debug_log/2026-10-02/jobs/render_day1002.py) · 그림 [`2026-10-02_rot3_paths.png`](../04_navigation/figures/2026-10-02_rot3_paths.png) · [`_r2_runs.png`](../04_navigation/figures/2026-10-02_r2_runs.png) |
| 10-02 §16 | 사용자 요청: EKF B 가 실제 미끄러짐을 잘 인식했나 | rot3 끝 B (−0.295, −0.207) vs 줄자 (−0.275, −0.245) → **4.3 cm**(A 36.9). 누적 이동이 회전 구간마다 계단식으로 늘어 끝 35.9 cm(줄자 36.8). 독립 검사(정적 구조물을 각 EKF 자세로 odom 에 놓아 첫 스캔과의 어긋남 중앙): rot3 A 22.1 · **B 3.2 cm**, rot2 A 23.1 · **B 2.5 cm**. B 는 회전 중 2~6 cm 까지 올랐다 내려옴 | B 가 미끄러짐을 따라감. 회전 중 일시 상승은 rf2o 10 Hz 지연 · σ 로 **추정**. rf2o 단독 자세는 회전 중 0.3 m 안팎 출렁(병진 속도는 정상) — '라이다 위치라서' | [`render_ekfB_slip.py`](../debug_log/2026-10-02/jobs/render_ekfB_slip.py) · 그림 [`2026-10-02_ekfB_slip.png`](../04_navigation/figures/2026-10-02_ekfB_slip.png) · 수치는 화면 출력뿐(**출력 원문 없음**) |
| 10-02 §17 | **사용자 제안(다음 시험 설계): 90° 마다 줄자** — 회색 = 좌 · 우 90° 구간, 그래프는 시작점에서 멀어진 거리 | 절차: 오른쪽 앞끝(차체 (+0.262, −0.165)) 바닥 표시 → 회전 스크립트 **한 단계(90°)씩** → 사용자가 표시 ↔ 오른쪽 앞끝 대각 거리 → 다음. ±90° × 3 = 6 측정. 각 정지 시점 EKF A · B · rf2o 단독 · SLAM 자세로 같은 모서리 예측 → **예측 − 줄자** 오차(회전만으로도 모서리는 약 0.44 m 움직이므로 거리 자체가 아니라 오차로). 짝(±90°)이 끝난 시점은 순수 미끄러짐만 | 지표: 단계별 오차 · 단계 사이 증분 — rf2o 가 매 밀림을 따라가면 B 의 오차가 쌓이지 않아야 함. 준비: 회전 스크립트 단계 모드 · R3 게이트 라이브 또는 재생 · 기록 토픽에 `/imu/data` | (이후 10-06 §4 에서 실행) |
| 10-02 §18 | 사용자 'rot3_paths 형식(시작 자세 기준 궤적)이 비교하기 좋다 · 로버가 rf2o 도식처럼 크게 출렁이며 움직였다고 인지' → 확인 | rf2o 원 자세(부호 보정)를 **라이다 위치**(중심 앞 0.152 m)로 보고 지렛대를 빼 중심으로: 경로 1.89 → **0.73 m**(EKF B 0.61 m), 끝 (−0.274, −0.252) = **줄자와 0.7 cm**(EKF B 4.3 cm) | 사용자가 본 출렁임 = 차체 앞부분(라이다 · 데크)의 실제 움직임. rf2o 원 자세가 틀린 게 아니라 '어느 점의 궤적인가' 의 차이. 추가: 중심 환산 rf2o 끝이 EKF B 보다 줄자에 가까움 → B 는 σ 가중으로 rf2o 를 일부만 반영 → R3 비교 후보 '회전 중 rf2o σ 더 작게 / rf2o 자세 증분 직접'. 다음 도식: 중심 + 오른쪽 앞끝 궤적을 A · B · rf2o · SLAM 별로, 90° 마다 줄자 점 | [`rf2o_lever.py`](../debug_log/2026-10-02/jobs/rf2o_lever.py) · 그림 [`2026-10-02_rf2o_lever.png`](../04_navigation/figures/2026-10-02_rf2o_lever.png) · 수치 화면 출력(**출력 원문 없음**) |
| 10-06 §1~§3 | R3 — `rf2o_gate.py` 정식 노드 · `ekf.launch.py rf2o:=true shadow:=true`(그림자 EKF A `/odometry/ekf_a` = rf2o 이전 구성, TF 없음), 재생 검증 → 라이브 정지 기동(출발 테이프 45 cm 앞) | 재생: f2b4 직진 축척 B 0.998 · f2b3 안쪽 면 A 0.196 / B 0.096 / SLAM 0.084 m(R2 원형과 0.2~0.3 cm 차). 라이브: /odom_rf2o 10.0 · gated 10.0 · EKF B 30 · A 29 Hz, B3 `rot_vx_var 0.09`, 게이트 CPU 39 % | 정식판 = 원형. 회전 bag rot2 · rot3 는 재부팅으로 소실 → R2-a(줄자) 재현은 새 실측으로(실수 5). 세부 · CPU 대책은 [게이트 카드](rf2o-gates-people.md) | [`r3_eval.txt`](../debug_log/2026-10-06/outputs/r3_eval.txt) · [`j851_r3prep.txt`](../debug_log/2026-10-06/outputs/j851_r3prep.txt) |
| 10-06 §4 선언 | **단계별 회전 실측(10-02 §17 실행)** — 한 번 = 제자리 90°(ω 0.38, 외곽 0.08 m 안이면 중단) → 정지 → EKF B · 그림자 A · rf2o 중심 환산 · SLAM 으로 오른쪽 앞끝(+0.262, −0.165)의 예측 대각 거리 → 사용자 줄자. +90 · −90 × 3 = 6 단계, bag `bag_step1`(`/imu/data` 포함, 끝나면 즉시 PC 회수) | — | 판정(실행 전): **EKF B 평균 ≤ 3 cm 이고 6 단계 ≤ 5 cm(쌓이지 않음)**. A · SLAM · rf2o 는 기록(A 는 쌓일 것으로 예상). 짝수 단계(방향 원위치) = 순수 미끄러짐 | [`step_rot.py`](../debug_log/2026-10-06/jobs/step_rot.py) · [`job853_step_init.sh`](../debug_log/2026-10-06/jobs/job853_step_init.sh) · [`run_step.sh`](../debug_log/2026-10-06/jobs/run_step.sh) |
| 10-06 §4.1 | 실행(스크립트 오류 2 회 · Wi-Fi 끊김 2 회는 모두 회전 전 · 로버 안 움직임 확인 뒤 재실행 — 실수 7) | 줄자 44.8 · 10.8 · 43.3 · 16.1 · 43.5 · 17.6 cm. 예측 − 줄자(cm): **B −2.9 / 0.0 / −2.8 / +0.1 / −2.3 / +0.7(평균 1.5)** · A +0.3 / −10.0 / +2.1 / −15.5 / +1.9 / −17.0(7.8) · SLAM +0.8 / −4.8 / 0.0 / −1.2 / +1.8 / −6.2(2.5). B 단계 2 끝 (−0.088, −0.063) = 사용자가 본 '뒤 · 오른쪽'. EKF 각도는 단계마다 +93~94° · 0.4~1.4° | **통과**(평균 1.5 ≤ 3, 6 단계 0.7 ≤ 5, 쌓이지 않음). A 는 미끄러짐을 거의 0 으로 봐 원위치 오차가 쌓임(예상대로). SLAM 은 회전 중 기준으로 부족(6 cm 까지 틀림). B 의 홀수 단계 −2.3~−2.9 cm 같은 쪽 치우침은 **원인 미분리**(후보: 회전 중간 각도 민감 1° ≈ 0.5 cm · 줄자 측정점 — 모순 5). rf2o 단독 누적 자세는 단계 3 부터 각도 59°(실제 94°)로 무너져 비교에서 뺌 — B 는 rf2o **속도만** 써서 무관 | [`step_tape.csv`](../debug_log/2026-10-06/outputs/step_tape.csv)(줄자) · [`step_state_1.json`](../debug_log/2026-10-06/outputs/step_state_1.json)(단계별 네 추정 자세) · [`render_step1.py`](../debug_log/2026-10-06/jobs/render_step1.py) · 그림 [`2026-10-06_step_rot1.png`](../04_navigation/figures/2026-10-06_step_rot1.png) · bag `2026-10-06/bags/bag_step1.tgz`(로컬). 오차 줄의 원 출력은 **원천 소실**이나 입력 · 스크립트가 남아 11-02 에 같은 식으로 다시 계산해 SUMMARY 표와 일치 확인(아래 §2.1) |
| 10-06 §8 | 갱신 계획 — 사용자 결정 순서 ① CPU → ② 사람 T1 · T2 → **③ rf2o 켠 F2 순회 비교(+T3) → 기본값 결정** → ④ 피벗 회전 → ⑤ 전선 시험 | — | 내 평가: 목표('rf2o 켠 순회가 나아지나')를 앞당기고, 피벗 회전은 원인 제거라 그 다음 | [10-06 §8](../debug_log/2026-10-06/SUMMARY.md) · ①② 는 [게이트 카드](rf2o-gates-people.md) |
| 10-07 §2 선언 | ③ rf2o 켠 F2 순회 — 10-02 f2b 와 같은 구성 · 10 목표, 바뀐 것은 `rf2o:=true gate_v:=on shadow:=true`(TF = EKF B, 그림자 A = 대조군), 사람 없이 | 비교 기준 f2b1~4: 시도 7 · 성공 6 · 실패 1 · 측면 접촉 2 · 위치 점프 최대 0.184 m, 벽 번짐 f2b3 실측 A 15 cm | 판정: ③-a 10 목표 성공 · 접촉 0 · 복귀 줄자 ≤ 5 cm, **③-b(핵심) 제자리 회전 구간마다 B − SLAM 이 A 보다 작고 최대 ≤ 5 cm**, ③-c 게이트 비용 ≤ 5 %, ③-d 부하 기록. ③-a 가 f2b 보다 나쁘지 않고 ③-b 통과면 `rf2o:=true gate_v:=on` 기본 제안 | [`run_f2c.sh`](../debug_log/2026-10-07/jobs/run_f2c.sh) · [`job903_prep_rf2o_g4.sh`](../debug_log/2026-10-07/jobs/job903_prep_rf2o_g4.sh) |
| 10-07 §2.2~§2.6 | f2c1(목표 1~4) · f2c2(남서 구석에서 5~10) | f2c1 3 성공 · **목표 4 남서 방향 맞춤 정체 → nav_guard 취소 71.2 s**, f2c2 6/6(목표 6 은 방향 130° 차로 위치만 성공). 합 **9/10**. 사용자: 복귀 때 **상자를 밀며 옴**(뒤끝은 출발 선) | ③-a **불합격**(실패 1 · 접촉 1). 남서 정체는 f2b3 와 같은 자리 · 같은 양상 → rf2o 와 무관한 '구석 · 목표 자세' 문제로 **추정**, 상자 접촉은 카메라만 보는 낮은 상자 ② 를 계획기가 잊은 것(10-07 §7 · §8 재해석) — 둘 다 [F2 순회 카드](f2-patrol-loc-jump.md) 이후 칸 | [`f0_f2c1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c1_runner.log) · [`f0_f2c2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2c2_runner.log) · bag `2026-10-07/bags/bag_f2c1.tgz` · `bag_f2c2.tgz`(로컬) |
| 10-07 §3.3 | ③-b — 제자리 회전 구간(EKF B \|ω\| > 0.15 · \|v\| < 0.03 이 1.5 s 넘게)의 SLAM 이동 대비 B · A 이동 차 | f2c1 2 구간(−24° · +51°): SLAM 3.3 · 2.1 / **B − SLAM 4.2 · 3.8** / A − SLAM 4.6 · 4.3 cm. f2c2 2 구간(−35° · −28°): 8.9 · 5.7 / **10.3 · 6.6** / 11.8 · 7.3 cm | B < A **4/4** 이지만 차 0.4~1.5 cm, 최대 10.3 > 5 → 선언 기준 **불합격**. 그러나 ① 제자리 회전이 4 번뿐(순회 회전은 대부분 곡선) ② 기준 SLAM 이 회전 직후 보정이라 그 자체 오차 수 cm ③ G4 가 이 구간 rf2o 를 줄인 몫 섞임 → **이 데이터로 rf2o 효과를 말하기 어렵다**, 10-06 줄자 시험이 더 직접적 근거(모순 6) | [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) · [`f2c_anal.py`](../debug_log/2026-10-07/jobs/f2c_anal.py) · [`job913_extract.py`](../debug_log/2026-10-07/jobs/job913_extract.py) |
| 10-07 §3.4 | map→odom 누적 보정 0.42 m · −9.7° 는 rf2o 탓 이상치인가 | f2b3(rf2o 끔, 293 s) Δ(0.393, 0.137) m · −5.70° vs f2c2(430 s) Δ(0.422, 0.265) · −9.65°. f2c2 보정 크기 합 회전 중 1.163 · 그 밖 1.505 m, yaw 8.56 · 17.49°, 한 번 5 cm 넘는 보정 15 회 | **이상치 아님**. rf2o 는 직진 드리프트를 못 줄임(직진 몫 2~4 %, 예상대로) | [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt)(f2c2 쪽) · f2b3 쪽 Δ 는 SUMMARY §3.4 에만(이 출력엔 없음) |
| 10-07 §3.1 · §3.2 · §4 | rf2o 발행률 9.6~9.7 Hz(bag), ③-c 버림 2.3 · 4.2 % 통과 · G4 곡선 오판 → 휠 잔차 | — | [게이트 카드](rf2o-gates-people.md) §2 | — |
| 10-07 §6 · §7 | f2d1 · f2d2 — rf2o + G4 휠 잔차 + MPPI transform_tolerance 0.5 | f2d1 목표 4 남서 정체 재현(3/3) · f2d2 남서 '위치만(f)' SUCCEEDED_XY · 목표 10 상자 앞 정지 | rf2o 구성은 그대로 유지, 실패 원인은 rf2o 밖(남서 구석 · 계획기와 MPPI 지도 불일치) | [F2 순회 카드](f2-patrol-loc-jump.md) 이후 칸 · [`f0_f2d1_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d1_runner.log) · [`f0_f2d2_runner.log`](../debug_log/2026-10-07/outputs/f0_f2d2_runner.log) |
| 10-07 §15 | 하루 마무리 결론 | rf2o 기본값에 대한 문장 없음 | ③ 의 '기본값 결정' 은 **내려지지 않음** — ③-a 불합격(원인은 rf2o 밖), ③-b 판정 불가, ③-d 미측정. rf2o 는 prep 인자로만 켜는 상태 유지 | [10-07 §15](../debug_log/2026-10-07/SUMMARY.md) |
| 10-08 §3 | 전역 nvblox + 주기 재계획 B 구성 주행(f2e1 · f2e2) | 'rf2o · G4 잔차 · 그림자 A 그대로' | rf2o 를 켠 채 다른 문제(전역 카메라 기억)를 시험 — rf2o 쪽 새 수치 없음 | [10-08 §3](../debug_log/2026-10-08/SUMMARY.md) · `job934_prep.sh` |
| 10-08 §5 · §5.6 | ④ 피벗 회전(사용자 진단의 시험) — 트랙 비율 통제 시험 rt1 · rt2(빠른/느린 트랙 비 r −1 제자리 ~ 0 피벗, 40 회) | 90°당 미끄러짐 중앙 제자리 6.2 · r −0.6 13.5 · −0.4 6.9 · −0.2 10.6 · **0 피벗 4.0** cm. 40 회 중 38 회가 **차체 뒤로**, 시간이 갈수록 커짐(앞 12 회 중앙 3.2 · 뒤 20 회 12.0) | 판정 Q1(제자리의 절반 이하인 r) **모두 불충족**. r 효과와 순서 효과가 섞임(설계 결함: 블록 단위로 r 을 묶음) — 피벗 회전으로 미끄러짐을 확실히 줄인다는 근거 없음 | [10-08 §5.6](../debug_log/2026-10-08/SUMMARY.md) · [`rt12_anal.txt`](../debug_log/2026-10-08/outputs/rt12_anal.txt) · [`rt12_pool.txt`](../debug_log/2026-10-08/outputs/rt12_pool.txt) |
| 10-08 §5.11 · §6.1 | 사용자 질문 '뒤 밀림이 일정한가' · 고정 보정 모형 적합 | 방향 일정: 통제 38/40 · 주행 중 회전 21/22 뒤로. 크기 불안정: 90°당 앞뒤 중앙 통제 −7.3 [−18.6~+1.1] · 주행 −5.9 [−13.6~+1.0] cm, 변동계수 66~76 %. 모형 M1(회전량 비례 뒤로, k 0.05 m/rad) 한 개 빼고 검증: 90°당 오차 중앙 **7.9 → 5.8 cm**(M2 5.3) | 평균 치우침은 모형으로 일부 줄지만 회마다 편차가 커 **rf2o 같은 외부 관측을 대신하지 못함** → 다음 세션 '뒤 밀림은 고정 보정 대신 rf2o · 가변 σ 쪽으로'(10-08 §7 ③) | [`slip_consistency.txt`](../debug_log/2026-10-08/outputs/slip_consistency.txt) · [`slip_model.txt`](../debug_log/2026-10-08/outputs/slip_model.txt) |

### 2.1 근거 발췌 — 단계별 줄자 시험(10-06 §4.1)
```python
# Docs/debug_log/2026-10-06/jobs/render_step1.py 5~15 행 — 시작 자세 기준 상대 자세 → 오른쪽 앞끝의 이동 → 대각 거리 − 줄자
S = json.load(open('step1/step_state_1.json')); TAPE = [44.8, 10.8, 43.3, 16.1, 43.5, 17.6]
CR = np.array([0.262, -0.165])
def rel(p, p0): c0, s0 = math.cos(p0[2]), math.sin(p0[2]); dx, dy = p[0] - p0[0], p[1] - p0[1]; return [c0 * dx + s0 * dy, -s0 * dx + c0 * dy, p[2] - p0[2]]
def corner(p): c, s = math.cos(p[2]), math.sin(p[2]); return np.array([p[0] + c * CR[0] - s * CR[1], p[1] + s * CR[0] + c * CR[1]]) - CR
for st in S['steps']:
    for k in 'BAS': d = corner(rel(st['pose'][k], S['s0'][k])); pred[k].append(np.hypot(*d) * 100)
err = {k: np.array(pred[k]) - np.array(TAPE) for k in 'BAS'}
```
```
# 11-02 같은 식으로 다시 계산(입력 outputs/step_state_1.json · TAPE — 화면 출력, 파일로 남기지 않음)
B -2.9 -0.0 -2.8 +0.1 -2.3 +0.7 | mean 1.5
A +0.3 -10.0 +2.1 -15.5 +1.9 -17.0 | mean 7.8
S +0.8 -4.8 -0.0 -1.2 +1.8 -6.2 | mean 2.5
# step_state_1.json 의 단계별 회전 판정 각(EKF B 누적) · B yaw · 외곽 최근접
1 +90 91.2° B yaw 93.4° gap 0.358 m … 6 -90 90.6° B yaw 0.4° gap 0.344 m
```
- 회전은 `step_rot.py` 48~51 행: EKF B yaw 증분을 지령 중에만 누적해 90° 가 되면 정지 지령(10 회) — 감속 중 더 돈 몫(약 2~3°)이 B yaw 93~94° 로 남는다(위 출력). 오차는 시작 대비 '자세' 로 계산하므로 이 초과 회전은 예측에 그대로 들어간다(오차 원인이 아님).

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 회전 중 미끄러짐을 rf2o 가 본다 | rot2 · rot3 재생 순 이동 + rot3 줄자 | rf2o 0.350 · 0.370 일관, 줄자 0.368 과 크기 · 성분 5 mm 안 | **지지(측정)** |
| 위치 추정 SLAM 이 회전 중 미끄러짐을 본다 | 같은 재생 · 줄자 | rot2 0.322, rot3 0.114(줄자 0.368) | **기각**(일정하지 않음) |
| rf2o 병진 부호 반대 = 라이다 뒤집힘 장착(yaw π − 2.68°) | 회전 보정 R(π − 0.04677) 뒤 줄자 · 직진 비교 | 줄자와 같은 사분면, f2b4 직진 vx 비 −0.912 → +0.911 | 보정 효과 **지지**. rf2o 코드 안의 기전(`PoseUpdate` 합성)은 **미확인** |
| 지렛대(ω × 0.152) 보정이 필요하다 | `rf2o_fix.py` c 판 | 경로 길이 0.54 → 1.65 m(나빠짐), 끝점은 c 6.7 cm vs b 8.1 cm(c 가 가까움) | 경로 기준 **기각**(이후 게이트에 지렛대 없음). 끝점 기준으론 반대 — **미확인**(§5 모순 2) |
| rf2o 회전(ω)도 EKF 에 넣을 만하다 | 540° 뒤 각 누적 | rf2o +4.2 · +7.8° vs 자이로(EKF) −3.1 · +0.7° | **기각** — 병진만 |
| 휠 B3 σ 0.03 이면 rf2o 가 살아난다 | 3 차 재생 | rot3 7.2 cm(36.8 중) | **기각** → σ 0.3 |
| G1(자이로 일치) 최신 표본 비교 · 문턱 0.05 가 사람 없는 bag 을 통과시킨다 | 4 차 거부율 | f2b3 37 % 거부 | **기각** → 0.1 s 평균 · 바닥 0.12 → 1~2 ‰ |
| EKF B 가 구석 기동 번짐을 절반 이하로 | R2-c 중심 흔들림 | B 0.112 vs A 0.131(SLAM 0.079) | 선언 기준 **불합격** · 지표가 SLAM 바닥보다 엄격 → 안쪽 면 지표 B 0.099 vs A 0.198(단 라이브 0.130 — §5 모순 3) |
| 직진 vx 는 휠이 rf2o 보다 정확 | 직진 창 축척 | rf2o 0.91~0.93, 휠 · SLAM 1.000 | **지지** → 직진 rf2o vx σ 0.10 |
| (6 기) 라이브에서도 EKF B 가 회전 미끄러짐을 매 단계 따라간다 | 10-06 §4 단계별 줄자(선언 기준 평균 ≤ 3 · 6 단계 ≤ 5 cm) | 평균 1.5 · 원위치 0.0 / 0.1 / 0.7 cm, A 는 −10 → −17 누적 | **지지(측정)** — 오프라인 4.3 cm 보다 좋음. n = 6 단계 · 한 자리 · 사람 없음 |
| (6 기) 위치 추정 SLAM 은 회전 중 미끄러짐 기준으로 쓸 만하다 | 같은 시험 SLAM 열 | 원위치 −4.8 · −1.2 · −6.2 cm | **기각**(10-02 와 같음) — 순회 ③-b 의 기준으로도 약함 |
| (6 기) rf2o 를 켜면 순회의 회전 뒤 번짐이 줄어든다 | 10-07 ③-b, 제자리 회전 구간 B − SLAM vs A − SLAM | B < A 4/4, 차 0.4~1.5 cm, 최대 10.3 | **미확인** — 표본 4 · 기준(SLAM) 오차 · G4 몫 섞임 |
| (6 기) rf2o 가 직진 드리프트(map→odom 누적 보정)를 줄인다 | f2b3(끔) vs f2c2(켬) 누적 보정 | Δ(0.393, 0.137) vs (0.422, 0.265) m | **기각**(예상대로 — 직진 몫 2~4 %). 다만 주행 길이 293 vs 430 s 로 다름 |
| (6 기) 회전 미끄러짐은 고정 모형으로 보정할 수 있다 | 10-08 M1 · M2 한 개 빼고 검증 | 90°당 7.9 → 5.8 · 5.3 cm, 최대 13.4 · 13.7 | 평균만 일부 — **외부 관측 대체 기각** |
| (6 기) 피벗 회전(r 0)이 미끄러짐을 절반 이하로 | 10-08 rt1 · rt2 | 피벗 중앙 4.0 vs 제자리 6.2(절반 3.1 미달), 순서 효과 섞임 | **미확인**(설계 결함으로 판별 불가) |

## 4. 조치와 효과
- **10-02 에 바뀐 것**: Jetson `~/rf2o_ws` 빌드(라이브 스택 미연결) · 오프라인 원형 `r2_gate.py`. 스택 기본값은 그대로.
- **효과(재생)**: rot3 끝 오차 0.369 → **0.043 m**, 직진 축척 0.998, 구석 기동 벽 안쪽 면 범위 0.198 → 0.099 m(SLAM 0.084), §19 '기동 뒤 남은 차' A −15.2 → B −4.9 cm([회전 중 장애물 번짐](rotation-obstacle-smear.md) §2).
- **한계**: 같은 bag 4 개로 5 차례 조정(과적합 위험을 알고 멈춤). 사람 섞인 오염을 G1 이 잡는지는 미검증(T1~T3 몫). 라이브 CPU 미측정.
- **10-06 ~ 10-08 에 바뀐 것**: 정식 게이트 노드 · `ekf.launch.py rf2o:=` · `shadow:=` · `gate_*:=`(전부 기본 끔, 커밋 4fdeeaaf → 1e3819e6 — [게이트 카드](rf2o-gates-people.md) §4), prep 은 `EXTRA_SENSORS` 로만 켬(10-06 `job852` · 10-07 `job903` · `job918` · 10-08 `job934`). **기본값 전환은 하지 않음**(10-07 §15 에 결정 없음).
- **효과(6 기)**: 라이브 통제 회전 줄자 대비 EKF B 1.5 cm(A 7.8 cm), 원위치 단계 미끄러짐을 0.0~0.7 cm 로 따라감. 순회 번짐 · 직진 드리프트 개선은 **보이지 못함**(§2 10-07 §3.3 · §3.4).
- **지금 코드**(10-06 R3 이후 정식): `ekf.launch.py rf2o:=true` 면 `rf2o_laser_odometry_node`(`rf2o.yaml`: `/scan` → `/odom_rf2o`, `publish_tf false`, `init_pose_from_topic ""`, 10 Hz) + `rf2o_gate.py` → `/odom_rf2o/gated` 를 주 EKF `odom1`(vx · vy 만)으로, 컨디셔너 B3 를 σ 0.3 으로(39~40 · 53~62 행). `conditioner:=py` 와는 같이 못 씀(48 행). **기본은 꺼짐**이고 prep 기본은 `ODOM=vslam`(cuVSLAM) — rf2o 구성은 `ODOM=rf2o`(→ `rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel`, `prep_patrol.sh` 12 행).

### 게이트가 하는 일 — 지금 [`rf2o_gate.py`](../../ros2_ws/src/rover_bringup/scripts/rf2o_gate.py) (10-02 R2 원형 → 10-06 정식 노드 → 10-06 §5 · §12 · 10-07 §4 수정)
입력 `/odom_rf2o`(rf2o, 10 Hz, best-effort) · 회전 속도 원천(`gyro_source`: 기본 **`ekf`** = `/odometry/filtered` 의 ω 30 Hz, 또는 `imu` = `/imu/data` 의 −ω_y 200 Hz) · `/wheel_odom`(best-effort). 출력 `/odom_rf2o/gated`(frame odom, child base_link, twist 만). rf2o 메시지 하나마다:
1. **좌표**: (vx, vy) 를 R(`lidar_yaw` = π − 0.04677) 로 돌려 차체 속도 (bx, by). 지렛대 보정 없음.
2. **회전 기준 ω̄**: rf2o stamp 직전 `win` 초(ekf 0.15 s · imu 0.1 s)의 회전 속도 평균(없으면 최신값). 10-02 4 차의 '최신 표본 하나' 비교가 시각 어긋남으로 37 % 오거부를 낸 것을 고친 형태.
3. **G1 자이로 일치**: |ω_rf2o − ω̄| > max(`g1_floor` 0.12, 0.3 |ω̄|) 면 버림 — 사람 등 움직이는 물체가 스캔 흐름을 오염시키면 회전 추정도 같이 틀어진다는 가정(09-29 §6.1). `ekf` 원천이어도 순환은 없다 — rf2o 는 EKF 에 ω 를 넣지 않음(odom1 은 vx · vy 만).
4. **G2 정지 검사**: 휠 |vx| < 0.005 이고 |ω̄| < 0.02 인데 |(bx, by)| > 0.02 면 버림(정지 중 가짜 이동). (10-02 원형은 ω̄ 대신 최신 자이로 값을 씀.)
5. **G3 스캔 겹침 q**(`q_mode`, 기본 off): 직전 스캔을 후보 움직임(bx, by, ω̄)으로 옮겨 이번 스캔과 비교, 5 cm 넘게 어긋난 점 비율 q > 0.30 이면 버림, 0.15~0.30 은 σ 1~10 배. **10-06 §12 기각**(천천히 움직이는 큰 몸은 프레임당 2.4 cm 라 못 가름) — 코드는 남음.
6. **G4 회전 중 병진 타당성**(`v_mode`, 노드 기본 off · `ekf.launch gate_v` 기본 off · prep `ODOM=rf2o` 는 on): |ω̄| > `rot_w` 0.15 일 때 판정량 vb = **|(bx − v_휠, by)|**(`v_ref wheel`, 10-07 §4 — 곡선 회전의 정상 전진을 오염으로 보던 결함 수정; `abs` 면 |(bx, by)|) > 0.10 이면 버림, 0.05~0.10 이면 σ 1~10 배.
7. **σ**: 회전 중(|ω̄| > 0.15) vx · vy **0.03**, 그 밖 vx **0.10**(직진은 휠 우선 — rf2o 축척 0.93) · vy **0.03**. yaw 분산 1e3(어차피 EKF 가 안 씀).
8. 30 s 마다 '통과 · G1~G4 거부' 수 로그, `csv` 를 주면 판정 한 줄씩(`t,w_rf2o,w_gyro,v_wheel,bx,by,q,res`). `relay_plain`(shadow)이면 휠을 컨디셔너 기본 공분산으로 `/wheel_odom/plain` 에 중계(그림자 EKF A 용).
- 짝 설정(게이트 밖): 컨디셔너 B3 순수 회전 중 휠 vx · vy σ 0.3 — 0.03 이면 25 Hz 휠이 10 Hz rf2o 를 눌러 미끄러짐을 지움(10-02 §14.1 3 차).
- ⚠ 이 노드의 `lidar_yaw` 기본값(π − 0.04677)과 G3 의 라이다 x 0.152 는 **URDF 를 읽지 않고 상수로 박혀 있다** — 데크를 다시 조립 · 측정하면 `stuck_monitor.py LIDAR_YAW` 처럼 이 값도 같이 바꿔야 한다(CLAUDE.md 하드웨어 요약에는 stuck_monitor 만 적혀 있음).

## 5. 내 실수
**실수 1 — 자이로 없는 bag 으로 게이트를 돌림(R2 1 차)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | rot2 · rot3 bag 으로 게이트 + EKF A/B 재생 — `r2_run.sh` 가 `/imu/data` 를 재생하고 `r2_gate.py` G1 이 자이로와 비교 |
| 본 것 | 회전 중 rf2o 를 G1 이 거의 다 버림 |
| 처음 추론 | (없음 — 원인을 바로 찾음) |
| 판별 | bag `metadata.yaml` 에 `/imu/data` 없음 — 통제 회전 기록 토픽(`job825_rot.py` `TOP`)에서 빠짐 |
| 결론 | 자이로 0 과 비교해 회전 중 rf2o 가 전부 '불일치'. 고침: `r2_run.sh` 가 bag 에 `/imu/data` 가 없으면(`NOIMU`) EKF 에 `odom2 = /r2/live_w`(라이브 EKF 회전 속도, σ 0.02), 게이트는 자이로가 1 s 넘게 없으면 `/odometry/filtered` ω 를 대신 씀 |
| 다음에 알아보는 법 | 재생 시험 전에 bag 토픽 목록을 '재생 노드 입력' 과 대조. 시험 bag 은 나중 재생 입력 기준으로 기록 |
| 데이터 | 1 차 수치는 버림(원문 없음). 고친 코드 [`r2_run.sh`](../debug_log/2026-10-02/jobs/r2_run.sh) · [`r2_gate.py`](../debug_log/2026-10-02/jobs/r2_gate.py) |

**실수 2 — 휠을 reliable 로 구독(R2 2 차)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 게이트가 `/wheel_odom` 을 받아 EKF A · B 용 공분산으로 중계 |
| 본 것 | EKF A 출력 0, B 는 rf2o 만으로 움직임 |
| 처음 추론 | EKF A 가 휠을 융합하지 않는 이유를 설정에서 찾음(`job843_dbg.sh` — `r2_ekfA.yaml` 의 odom0 · 중계 토픽 · hz 확인) |
| 판별 | 재생 발행 `/wheel_odom` 은 micro-ROS 원래 QoS(best-effort) — reliable 구독자와 매칭 안 됨 |
| 결론 | `qos_profile_sensor_data` 로 구독(이후 정식 `rf2o_gate.py` 도 같음, 주석 'micro-ROS 는 best-effort') |
| 다음에 알아보는 법 | 토픽이 '있는데 콜백이 0' 이면 QoS 부터 본다(`ros2 topic info -v`). micro-ROS 출처 토픽은 항상 best-effort |
| 데이터 | 2 차 수치 버림. [`job843_dbg.sh`](../debug_log/2026-10-02/jobs/job843_dbg.sh)(출력 원문 없음) |

**실수 3 — G1 을 최신 자이로 한 표본과 비교(R2 4 차 → 5 차)**: 3 차 CSV 에서 사람 없는 bag 인데도 |Δω| 90 % 값이 직진 0.09 · 회전 0.12 로 문턱 0.05 를 넘었고, 4 차에서 f2b3 의 37 % 를 버렸다. rf2o 의 ω 는 '직전 스캔 → 이번 스캔' 0.1 s 구간의 평균인데 자이로는 순간값이라 비교 대상이 달랐다. 고침: 같은 구간 평균 + 바닥 0.12 → 1~2 ‰. 알아보는 법: 두 센서 값을 비교할 때 **각 값이 대표하는 시간 창**을 먼저 맞춘다. 데이터: 3 · 4 차 CSV 원천 소실, 5 차 `r2_*_gate.csv`.

**실수 4 — R2-c 기준이 SLAM 자신도 못 넘는 값(§14.2)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 구석 기동 번짐이 줄었는지 — 서쪽 구조물 점의 **중심**을 각 EKF odom 좌표로 옮겨 흔들림 최대 ≤ A/2 |
| 본 것 | A 0.131 · B 0.112 m — 불합격 |
| 처음 추론 | (4 차) G1 오거부 · B3 미적용 탓 |
| 의심한 이유 | 5 차에서 G1 을 고쳐도 거의 안 바뀜 |
| 판별 | 같은 지표를 SLAM(map) 자세로 계산 → 0.079 m — '정답' 자세로도 0.065 를 못 넘음 |
| 결론 | 회전하며 구조물의 보이는 부분이 바뀌어 **중심 자체가 움직이는 몫**이 지표에 섞임 = 지표 설계 실수. 로버 쪽 가장자리(x 95 백분위) 범위로 보면 A 0.198 · B 0.099 · SLAM 0.084. 기준을 바꿔 통과로 바꾸지 않고 둘 다 기록 |
| 다음에 알아보는 법 | 새 지표는 **정답 자세(SLAM 또는 줄자)로 먼저 계산해 바닥값**을 보고 문턱을 정한다 |
| 데이터 | [`r2_eval_run5.txt`](../debug_log/2026-10-02/outputs/r2_eval_run5.txt) · [`r2_eval.py`](../debug_log/2026-10-02/jobs/r2_eval.py) · 입력 `r2_f2b3.npz`(스크래치패드, **원천 소실**) |

**실수 5 — 회전 시험 bag 을 Jetson `/tmp` 에만 둠(10-06 §2)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | R3 정식 launch 가 R2-a(rot3 줄자 4.3 cm)를 재현하는지 같은 bag 으로 재생 |
| 본 것 | `/tmp/bag_rot2` · `bag_rot3` 없음 — Jetson 재부팅으로 `/tmp` 와 함께 소실 |
| 판별 | PC 스크래치패드 · 저장소 `bags/` 어디에도 사본 없음 |
| 결론 | R2-a 재현 불가 → 10-06 §4 단계별 실측이 그 자리를 대신함. 규칙: **시험 bag 은 끝나는 즉시 PC 로 회수**(같은 날 `job856_end.sh` · `run_x856.sh` 가 bag_step1 을 tgz 로 묶어 바로 회수 — 그 형식) |
| 다음에 알아보는 법 | 시험 직후 '그날 `bags/` 에 tgz 가 있나' 를 확인 항목으로. Jetson `/tmp` 는 prep · 재부팅이 지운다 |
| 데이터 | 원천 소실(rot2 · rot3 bag) · [10-06 §2](../debug_log/2026-10-06/SUMMARY.md) |

**실수 6 — WSL 에서 F: 경로가 안 보여 배포 파일이 안 올라감(10-06 §2 첫 시도)**: 재생 검증 첫 시도가 무효 → 스크래치패드를 거쳐 다시([`run_x850.sh`](../debug_log/2026-10-06/jobs/run_x850.sh) 4~7 행: 스크래치패드 사본에서 `\r` 를 지워 `/tmp/r3up` 에 모은 뒤 scp). SUMMARY 가 '전에도 겪음' 이라 적은 같은 함정. 알아보는 법: WSL 러너는 Windows 드라이브 경로를 직접 쓰지 말고 스크래치패드(`/mnt/c/…`) 사본을 보낸다. 데이터: 첫 시도 출력 원천 소실.

**실수 7 — 단계별 시험 스크립트 오류 2 회(10-06 §4.1)**: ① 단계 2 첫 시도 `KeyError` — DDS 발견 지연으로 첫 메시지 전에 계산 → [`step_rot.py`](../debug_log/2026-10-06/jobs/step_rot.py) 46 행 '세 토픽이 다 올 때까지 최대 8 s 대기' ② 단계 3 첫 시도 — 유효 점 없는 스캔에서 최근접 계산 실패 → 21 행 `if not ok.any(): return`. 둘 다 회전 전에 멈춰 로버 안 움직임(SUMMARY). 알아보는 법: 단계 실행 스크립트는 입력 토픽 · 빈 메시지를 먼저 확인하고 나서 지령을 낸다. 데이터: 오류 화면 원천 소실, 고친 코드는 커밋 ca37d9f4 판.

**모순 · 원문 대조(이 카드를 쓰며 찾은 것)**
1. §13.2 '직진 bag(f2b4) 재생에서도 rf2o vx / EKF vx = **−0.94**' · 'SLAM/EKF 1.000, rf2o/SLAM **0.932**(창 16 개)': 원문 [`rf2o_fix.txt`](../debug_log/2026-10-02/outputs/rf2o_fix.txt) 는 보정 전 vx 비 **−0.912**, 보정 후 **0.911**(EKF 기준, 표본 683). 0.932 · 1.000 · 16 개는 원문 출력이 없다(별도 계산 — 원천 미상). 결론(직진은 rf2o 가 7~9 % 작게 봄 → 휠 우선)은 어느 값이든 같다.
2. 지렛대 판단: §13.2 는 'ω × r 보정은 경로 0.54 → 1.65 m 로 나빠짐 = rf2o 가 이미 반영' 이라 했는데, 같은 원문에서 끝점은 보정 c (−0.308, −0.187) 가 줄자에 **6.7 cm**, 보정 안 한 b (−0.340, −0.197) 가 **8.1 cm** 로 c 가 더 가깝다. 또 §18 은 'rf2o 원 **자세**는 라이다 위치의 궤적' 이라 지렛대를 빼야 중심이 된다고 했다(끝 0.7 cm). '속도는 이미 반영' 과 '자세는 라이다 위치' 가 rf2o 안에서 어떻게 함께 성립하는지는 **미확인**(코드 미검토). 지금 게이트는 지렛대를 빼지 않는다(b 방식).
3. §14.1 '3 차: A = 라이브와 일치(검증)': R2-a 에선 맞지만(A · 라이브 둘 다 0.369) [`r2_eval_run5.txt`](../debug_log/2026-10-02/outputs/r2_eval_run5.txt) R2-c 안쪽 면 범위는 **A 0.198 vs 라이브 0.130**(중심 흔들림은 0.131 vs 0.128 로 비슷)으로 다르다. 같은 설정이어야 할 두 EKF 가 구석 기동에서 갈라진 이유는 **미확인**(10-06 §2 R3 도 '그림자 A 가 라이브와 일치' 라고만 적음). 그래서 'B 가 A 의 절반' 은 재생 A 기준이고, 라이브 기준이면 0.130 → 0.099(약 24 % 감소)다.
4. §14.2 G1 거부 'f2b3 2': 5 차 csv [`r2_f2b3_gate.csv`](../debug_log/2026-10-02/outputs/r2_f2b3_gate.csv) 는 g1 **3** · g2 **4**. 다른 bag 도 G2 거부가 2~5 건씩 있는데(rot3 5 · rot2 4 · f2b4 3) SUMMARY 는 G1 만 적었다. 정지 검사가 사람 없는 bag 에서 몇 건 걸리는 것은 기록할 가치가 있음(원인 미확인).
5. (6 기) 10-06 §4.1 B 홀수 단계(+90°) −2.3~−2.9 cm 치우침의 원인: SUMMARY 는 '회전 중간이라 모서리 위치가 각도에 민감(1° ≈ 0.5 cm), EKF 각도 +93~94°, 줄자 측정점 잡기 차이' 를 후보로 두고 '원인 미분리' 라 했는데, 정리 페이지 [`2026-10-06_report.html`](../debug_log/2026-10-06/2026-10-06_report.html) 은 '직진 축척 0.93 또는 오른쪽 앞끝 위치 오차로 추정' 이라 다른 후보를 적었다. 제자리 회전에는 직진 구간이 없고 회전 중 rf2o σ 는 0.03(축척 0.93 은 직진 창에서 잰 값)이라 '직진 축척' 후보는 근거가 약하다. 어느 쪽도 측정되지 않았다 — **미확인**.
6. (6 기) 10-07 §2 ③-b 의 선언(제자리 회전 구간마다 B − SLAM 최대 ≤ 5 cm): 10-06 §4.1 · 10-02 §13.2 가 이미 '회전 중 SLAM 은 기준으로 부족(6 cm 까지 틀림)' 이라 적었는데 그 SLAM 을 기준으로 5 cm 문턱을 둬 판정이 '불가에 가까움' 으로 끝났다 — 지표 설계 때 기준 자체의 오차를 먼저 보지 않은 것(10-02 실수 4 와 같은 종류). 순회 중 제자리 회전 표본 수(4)도 미리 세지 않았다.
7. (6 기) 10-07 §2 선언 ③-d(주행 중 게이트 + rf2o + 그림자 CPU 기록)는 §3 분석에 결과가 없다 — 미측정. 정지 기준값(게이트 16.5 · rf2o 4.4 · EKF 13.3 / 10.8 %)도 `job907_postchk.sh` 화면 출력뿐이라 원천 소실.

## 6. 남은 것 (10-02 시점)
- R3: 게이트를 정식 노드로 · ekf.launch 인자(기본 끔) · 라이브 CPU.
- 단계별 90° 줄자 시험(§17) — 오프라인 4.3 cm 가 라이브 · 매 단계에서도 성립하는지.
- 사람 섞인 스캔 오염(T1~T3) — G1 이 잡는지.
- 회전 중 rf2o σ 0.03 을 더 작게 / rf2o 자세 증분 직접(§18 후보).
- 피벗 회전(사용자 진단)의 미끄러짐 비교 — 미시험.
- rf2o 부호 반대의 코드 기전 · 지렛대 반영 여부 — 미확인.

### 남은 것 (10-08 시점)
- 기본값 결정(10-06 §8 ③) — 순회 비교가 판정 불가로 끝나 미결. 순회에서 rf2o 효과를 보일 지표(기준 오차가 작은 것, 예: 줄자 · 정적 벽 일관성)부터 다시 설계해야 함.
- 사람 섞인 환경(T2 실제 · T3)과 움직이는 큰 가림 — [게이트 카드](rf2o-gates-people.md) §6.
- 회전 중 rf2o σ 0.03 을 더 작게 / rf2o 자세 증분 직접(10-02 §18 후보) — 미시험(단계별 1.5 cm 로 필요성 약해짐).
- 홀수 단계 −2.3~−2.9 cm 치우침의 원인 — 미분리(모순 5).
- 회전 미끄러짐 자체: 뒤로 끌림의 원인(10-08 §5.6 후보: 외력 · 트랙 장력 · 온도 · 회전 중심) · ABAB 교대 재시험 — 미실행.
- 직진 드리프트(map→odom 누적 0.4 m 대)는 rf2o 로 안 줄어 — 다른 수단 과제.

## 7. 이후 (10-12 ~)
- 10-06 ~ 10-08 은 위 §2 · §3 · §5 와 [게이트 · 사람 시험 카드](rf2o-gates-people.md)로 채움.
- 포인터(앞서 적어 둔 것, 8 기에서 확인 — 아래 §7.1): 10-20 cuVSLAM 병진 속도 융합(재실행 V4: 회전 미끄러짐 창 −12~29 %, rf2o 와 같이 써도 같음) → **10-23 §16 사용자 결정: 주 EKF 병진 = cuVSLAM**(`vslam:=on`, rf2o 안 띄움 — W3 회전 창 13.2~16.8 cm vs rf2o 21.5~30.7 · 멈칫 5 vs 12~14 · CPU 70 vs 75~76 %) — [10-23 SUMMARY](../debug_log/2026-10-23/SUMMARY.md). rf2o 구성은 `ODOM=rf2o` 로 남음(지금 [`prep_patrol.sh`](../tools/prep_patrol.sh) 10 · 12 행).

### 7.1 8 기 (10-19 ~ 10-23) — rf2o 가 기준선이 되고, cuVSLAM 에 자리를 넘김
본줄기는 [cuVSLAM 병진 속도 융합](cuvslam-velocity-fusion.md). 여기엔 **rf2o 쪽에서 본 것**만.

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-20 §5 · §5.1 | EKF 오프라인 재실행 V0 를 `ekf.yaml` 만으로 만듦 — **rf2o · B3 를 빠뜨림** | V0 가 기록 EKF 를 회전 때만 못 따라감(f2z1 끝 58.9 → 67.3 cm) | 메시지 순서 · 지연 탓(**틀림**) | [`anal_ekf_replay_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_f2z1.txt) |
| 10-20 §5.2 · §5.3 | 주행 bag `params.txt` 로 주 EKF odom1 = `/odom_rf2o/gated` 확인 → rf2o · B3 를 넣어 재실행 | V0 재현(f2z1 17.0 / 17.1 · 끝 58.9 / 58.9 cm). **rf2o 의 몫** = rf2o 없는 V0(§5.1) 대비 f2z1 W3 최대 창 28.7 → 26.5 cm(**−2 cm**). cuVSLAM 병진을 더하면 18.7, rf2o 를 빼고 cuVSLAM 만(V4) 18.6 — **V3 ≈ V4** | 순회 주행에서 rf2o 가 W3 되돌아 회전에 주는 것은 작다(1 주행 재실행 **측정**). cuVSLAM 이 있으면 rf2o 는 더하는 게 없다 → 운용 후보 V4(rf2o 대신 cuVSLAM) | [`anal_ekf_replay_live.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_live.txt) · [`mk_ekf_replay_params.py`](../debug_log/2026-10-20/jobs/mk_ekf_replay_params.py) 12 · 17~19 행 |
| 10-20 §6.4 ~ 10-23 §9 | 그림자 주행 5 회 — 주 EKF = rf2o + G4(그때 prep 기본), 그림자 = V4 | W3 최대 창 주 EKF **21.5~30.7**(f2v1 27.5 · f2sm1 24.1 · f2sm3 30.7 · f2pa1 24.0 · f2pa2 21.5 cm) → 그림자 14.3~22.1 | 같은 주행 안에서 rf2o 자리를 cuVSLAM 으로 바꾸면 −20~−41 % | 각 `anal_shadow_*.txt`(목록은 [cuVSLAM 카드 §2.1 ⑤](cuvslam-velocity-fusion.md)) |
| 10-22 §18 | 노드별 CPU(f2pi1, 그림자 구성) | `rf2o_gate` **12.3** · ekf_node 둘 11.1 · 9.7(코어 %) — rf2o 노드 자체는 표에 따로 없음 | 게이트(Python) 비용이 rf2o 본체보다 크다(10-06 16 % 와 같은 크기) | [`anal_cpu_nodes_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_cpu_nodes_f2pi1.txt) · [10-22 SUMMARY §18](../debug_log/2026-10-22/SUMMARY.md) |
| 10-23 §10 · §11 | `vslam:=on` 주행 f2von1 · f2von2 — prep 은 옛 기본(`rf2o:=true …`) + `SENSORS_ADD="… vslam:=on …"` 이었으나 `ekf.launch.py` 53 행 `if rf2o and vslam != 'on'` 때문에 rf2o 노드 · 게이트 **0 개** | W3 16.8 · 13.2 cm · CPU 70 %(그림자 + rf2o 구성 75~76 %) | rf2o · rf2o_gate · 그림자 EKF 를 안 띄운 몫이 CPU 차로 **추정** | [`prep_von_1023_1.txt`](../debug_log/2026-10-23/outputs/prep_von_1023_1.txt) 11 행 `rf2o 노드 0` |
| 10-23 §16 | **사용자 결정: 주 EKF 병진 = cuVSLAM** — `prep_patrol.sh` 기본 `ODOM=vslam`, rf2o 구성은 `ODOM=rf2o`(`rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel`) | — | rf2o 는 기본에서 빠짐(launch `rf2o` 기본 false 는 원래부터) | [`prep_patrol.sh`](../tools/prep_patrol.sh) 10~14 행 · 커밋 `dcfdb0b6` |

- 판정에 쓰인 범위 주의: CLAUDE.md §6 · `prep_patrol.sh` 5 행의 'rf2o 주 EKF 21.5~30.7' 은 10-21 ~ 23 그림자 주행 4 개의 값이다. 같은 rf2o 주 EKF 의 f2z2(10-20) 는 **12.1 cm**(재실행 V0 · 기록 둘 다), f2z1 26.6 · f2v1 27.5 — 주행 사이 비교는 미끄러짐 크기에 따라 크게 달라 약하다([cuVSLAM 카드 §5 기록 어긋남 3](cuvslam-velocity-fusion.md)).
- 남은 것(10-23 시점): rf2o 를 다시 쓸 조건(cuVSLAM 이 약한 어두운 곳 · 무늬 없는 곳 — 라이다는 조명과 무관)은 미검토. 그때 게이트 Python → C++ 이식(CPU 12~16 %)은 여전히 TODO.
- 이후(10-26 ~): 다음 시기에서 채움.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| R0 | rf2o 소스 · 빌드 | `j834_rf2o_build.txt` |
| R1 rot2 · rot3 재생 | rf2o vs SLAM vs EKF | `rf2o_cmp_rot23.txt` |
| rot3 줄자 | 뒤 27.5 · 오른 24.5 cm | 대화(사용자), SUMMARY §13.2 표 |
| R1b 좌표 보정 | a · b · c 판 · f2b4 직진 | `rf2o_fix.txt` |
| R2 1~5 차 | 게이트 + EKF A/B 재생 | 5 차 `r2_eval_run5.txt` · `r2_{rot2,rot3,f2b3,f2b4}_gate.csv` (1~4 차 원문 없음) |
| 그림 | 궤적 · 미끄러짐 · 지렛대 · 회차별 | `Docs/04_navigation/figures/2026-10-02_rot3_paths.png` · `_ekfB_slip.png` · `_rf2o_lever.png` · `_r2_runs.png` · 정리 페이지 `2026-10-02/2026-10-02_report.html` |
| 도구 | `job833` · `job834` · `job835_rf2o_replay.sh` · `job835_rf2o_rec.py` · `rf2o_cmp.py` · `rf2o_fix.py` · `r2_run.sh` · `r2_gate.py` · `r2_rec.py` · `r2_eval.py` · `job841_imuaxis.py` · `job842_stamp.py` · `job843_dbg.sh` · `render_ekfB_slip.py` · `rf2o_lever.py` · `render_day1002.py` | `2026-10-02/jobs/` |
| (6 기) R3 재생 · 라이브 정지 | 정식 launch 재현 · 발행률 · CPU | `2026-10-06/outputs/r3_eval.txt` · `j850_r3_replay.txt` · `j851_r3prep.txt`(세부는 [게이트 카드](rf2o-gates-people.md)) |
| (6 기) step1 | 단계별 90° 줄자 6 단계 | `2026-10-06/outputs/step_tape.csv` · `step_state_1.json` · 그림 `Docs/04_navigation/figures/2026-10-06_step_rot1.png` · bag `2026-10-06/bags/bag_step1.tgz`(로컬, git 제외) |
| (6 기) f2c1 · f2c2 | rf2o + G4 켠 순회 9/10 · ③-b · ③-c · map→odom | `2026-10-07/outputs/f0_f2c1_runner.log` · `f0_f2c2_runner.log` · `f2c_anal.txt` · `f2c_g4arc.txt` · bag `2026-10-07/bags/bag_f2c1.tgz` · `bag_f2c2.tgz`(로컬) |
| (6 기) f2d1 · f2d2 · f2e1 · f2e2 | rf2o 켠 채 다른 문제 시험 | [F2 순회 카드](f2-patrol-loc-jump.md) 이후 칸 |
| (6 기) rt1 · rt2 | 트랙 비율 통제 시험(피벗 회전) | `2026-10-08/outputs/rt12_anal.txt` · `rt12_pool.txt` · `slip_model.txt` · `slip_consistency.txt` |
| (6 기) 도구 | `step_rot.py` · `job853_step_init.sh` · `job854_step.sh` · `job856_end.sh` · `run_step.sh` · `run_x856.sh` · `render_step1.py` · `run_x850.sh` | `2026-10-06/jobs/` |
| (6 기) 도구 | `job903_prep_rf2o_g4.sh` · `job907_postchk.sh` · `run_f2c.sh` · `job913_extract.py` · `job913_run.sh` · `f2c_anal.py` | `2026-10-07/jobs/` |
| 지금 코드 | 게이트 · 설정 · launch | `ros2_ws/src/rover_bringup/scripts/rf2o_gate.py` · `config/rf2o.yaml` · `launch/ekf.launch.py` |

## 9. 도구 해설
공통: Jetson 재생은 **도메인 42 · sim time · `fastdds_udp_only.xml`**, `ros2 bag play --clock 100`(100 Hz 시계). npz 는 `/tmp` → PC 스크래치패드(`…\scratchpad\f2a6\…`)로 옮겨 분석했고 **지금은 소실**. rot2 · rot3 bag 도 소실(10-06 §2) — 이 카드의 R1 · R2 결과는 다시 만들 수 없다(f2b3 · f2b4 bag 은 10-06 재생에 쓰였으나 PC 사본 위치 미확인). → (11-02 추가) 10-06 [`run_x850.sh`](../debug_log/2026-10-06/jobs/run_x850.sh) 6 행이 PC 스크래치패드 `f0_f2b3/bag_f2b3.tgz` · `f0_f2b4/bag_f2b4.tgz` 에서 올렸다 — 지금 스크래치패드에도, 저장소 `2026-10-02/` 에도(bags 폴더 없음) 없어 **원천 소실**.
도구 계보: `job835_rf2o_replay.sh`(rf2o 만) → `r2_run.sh`(rf2o + 게이트 + EKF A/B, 1~5 차) → 10-06 `r3_replay.sh`(정식 `ekf.launch.py rf2o:=true shadow:=true`) → 상시 도구 없음(10-23 이후 rf2o 비활성). 게이트: `r2_gate.py`(오프라인 원형, 휠 중계 겸함) → 10-06 `rf2o_gate.py`(정식, 휠 중계는 shadow 때만) → 10-06 §5 `gyro_source ekf` · §12 G3 · §12.1 G4 → 10-07 §4 `v_ref wheel`.

### job833_rf2o_src.sh · job834_rf2o_build.sh — R0 (Jetson, bash)
- 833: MAPIRlab · Adlink-ROS 저장소 브랜치를 `git ls-remote` 로 · 설치된 rf2o 패키지 · `~/ros2_ws/src` 목록(인터넷 · 중복 확인). 출력 원문 없음.
- 834: `~/rf2o_ws/src` 에 `-b ros2` 클론(있으면 건너뜀) → 커밋 · 날짜 → 소스에서 `covariance` · 토픽 · `freq` · `publish_tf` · `init_pose` grep → `colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release`. 출력 [`j834_rf2o_build.txt`](../debug_log/2026-10-02/outputs/j834_rf2o_build.txt) — grep 결과에 covariance 줄이 없음 = 공분산 미설정의 근거, `init_pose_from_topic` 기본이 `/base_pose_ground_truth`(구독하면 그 토픽을 기다림 → 빈 문자열로 줘야 함; 명령줄 `-p` 로는 빈 문자열을 못 넘겨 파일로 둠 — 지금 `rf2o.yaml` 주석).
- 지금 다시: Jetson 을 다시 세팅할 때 그대로 쓸 수 있음(커밋 고정은 안 함 — 브랜치 최신을 받음).

### job835_rf2o_replay.sh · job835_rf2o_rec.py — R1 재생 (Jetson)
- 부른 형태: `bash job835_rf2o_replay.sh /tmp/bag_rot2 /tmp/rf2o_rot2.npz`(rot3 · f2b4 도 같은 형태).
- 하는 일(sh): bag 길이 + 3 s 계산 → `/tmp/rf2o_params.yaml`(sim time · `publish_tf false` · `/scan` → `/odom_rf2o` · base_link/odom · `init_pose_from_topic ""` · 10 Hz) → rf2o 노드 → 3 s 뒤 기록기(길이 + 6 s) → `ros2 bag play --clock 100 --topics /scan /tf /tf_static` → rf2o 누적 CPU 시간(`ps -o times`) · 로그 경고.
- 하는 일(py): sim time 노드로 `/odom_rf2o`(t, 자세 x · y · yaw, 속도 vx · vy · ω) · `/tf` 의 map→odom · odom→base_link 를 모아 npz.
- 출력: 화면(rf2o 수 · CPU) 원문 없음 → npz(소실) → `rf2o_cmp.py`.
- 결함: 재생 `/tf` 에는 bag 의 기록된 map→odom 이 그대로 있어 'SLAM' = 라이브 위치 추정 결과(재계산 아님) — 의도대로이나 이름 주의.

### rf2o_cmp.py — R1 비교 (PC)
- 부른 형태: `python rf2o_cmp.py rf2o_rot2.npz rf2o_rot3.npz`.
- 하는 일: 시험 처음 + 0.5 s ~ 끝 − 0.5 s 의 순 이동(rf2o 자세 · map 자세 = map→odom ∘ odom→base · EKF odom 자세 각각 시작-끝 거리)과 순 회전, 회전 중(EKF yaw 미분 |ω| > 0.2) rf2o ω / EKF ω 비 중앙 · rf2o 병진 |v| 중앙 · 최대, 전 구간 경로 길이.
- 출력: [`rf2o_cmp_rot23.txt`](../debug_log/2026-10-02/outputs/rf2o_cmp_rot23.txt). 쓰인 곳 §13.1 · §13.2(rf2o '자세 차' 는 이 원 자세 — 부호 반대 상태).
- 결함: 순 이동은 '크기' 만 — 부호 반대를 이 도구로는 못 봄(줄자 성분 비교에서 드러남).

### rf2o_fix.py — R1b 좌표 보정 검증 (PC)
- 하는 일: rf2o 속도를 (a) 그대로 (b) R(π − 0.04677) 회전 (c) 회전 + `by −= ω · 0.152` 로 차체 속도화 → **EKF yaw 로 적분**해 시작 자세 기준 끝 이동 · 경로 길이(rot3 은 줄자 함께, rot2). f2b4: EKF odom 자세 미분으로 vx · ω 를 만들고 직진(|vx| > 0.04 · |ω| < 0.05) 표본에서 rf2o vx 비 중앙 · vy 중앙, 제자리 회전(|ω| > 0.25 · |vx| < 0.02) vy · |v| 중앙.
- 출력: [`rf2o_fix.txt`](../debug_log/2026-10-02/outputs/rf2o_fix.txt) — f2b4 에 제자리 회전 표본 0(nan).
- 쓰인 곳: §13.2 '보정 = R(π − 0.04677) · v_rf2o', 지렛대 기각. 모순 1 · 2 참조.
- 지금: 이 b 방식이 `rf2o_gate.py` 1 단계로 들어감.

### r2_run.sh — R2 재생 묶음 (Jetson, bash + 인라인 Python)
- 부른 형태: `bash r2_run.sh /tmp/bag_rot3 /tmp/r2_rot3.npz`(rot2 · f2b3 · f2b4 도).
- 하는 일: ① 설치본 `ekf.yaml` 의 `ekf_filter_node` 파라미터를 복사해 **A**(`odom0 = /r2/wheel_A`) · **B**(`odom0 = /r2/wheel_B` + `odom1 = /r2/rf2o_gated`, vx · vy 만, `odom1_differential false`) 두 설정 파일 생성, 둘 다 `use_sim_time true` · `publish_tf false`. bag 에 `/imu/data` 가 없으면 두 EKF 에 `odom2 = /r2/live_w`(vyaw 만) ② rf2o 노드 · `r2_gate.py`(csv = OUT 이름 + `_gate.csv`) · EKF 두 개(`/r2/ekfA` · `/r2/ekfB` 로 출력 이름 바꿈) 기동 ③ `r2_rec.py` ④ `ros2 bag play --clock 100 --topics /scan /tf /tf_static /wheel_odom /imu/data /odometry/filtered` ⑤ 게이트 집계 · EKF A 로그 앞부분 · 오류 grep.
- 결함: A 도 재생 EKF 라 라이브 EKF 와 같다는 보장이 설정 복사뿐(모순 3).

### r2_gate.py — R2 게이트 원형 (Jetson, rclpy)
- 하는 일: `/wheel_odom`(best-effort) → `/r2/wheel_A`(vx 0.02² · vy 0.01² · vyaw 0.1²) · `/r2/wheel_B`(같되 휠 |vx| < 0.02 · |ω_휠| > 0.10 이면 vx · vy `rot_sd`² = 0.3²). `/imu/data` −ω_y = 자이로, 1 s 넘게 없으면 `/odometry/filtered` ω 로 대신하고 `/r2/live_w` 중계. `/odom_rf2o` → R(π − 0.04677) → G1(0.1 s 자이로 평균, 바닥 `g1_floor` 0.12) → G2(휠 |vx| < 0.005 · **최신** |ω| < 0.02 · |v| > 0.02) → σ(최신 |ω| > 0.15 면 vx · vy 0.03, 아니면 vx 0.10 · vy 0.03) → `/r2/rf2o_gated`. csv 한 줄씩(`t,w_rf2o,w_gyro,v_wheel,w_wheel,bx,by,res`), 10 s 마다 집계.
- 출력: `r2_*_gate.csv`(5 차) — [`r2_rot3_gate.csv`](../debug_log/2026-10-02/outputs/r2_rot3_gate.csv) 등 4 개.
- 지금 판과 차이: G2 · σ 판단에 최신값 대신 창 평균(지금), 휠 중계는 shadow 때만, G3 · G4 · `gyro_source` 없음.

### r2_rec.py — R2 기록기 (Jetson)
- sim time 으로 `/r2/ekfA` · `/r2/ekfB` 자세, `/tf` 의 map→odom · odom→base(라이브 기록 재생분), `/scan` 0.5 s 마다(거리 · 각) → npz(소실). 화면 한 줄 개수 요약.

### r2_eval.py — R2 판정 (PC)
- 하는 일: **R2-a** rot3 처음 + 1 s ~ 끝 − 1 s 의 시작 자세 기준 끝 이동(A · B · 라이브) vs 줄자 (−0.275, −0.245), rot2 크기. **R2-b** f2b4 를 3 s 창으로 잘라 라이브 EKF 가 |Δyaw| < 3° · 이동 > 0.15 m 인 창만, 각 EKF 이동 / map(SLAM) 이동 중앙. **R2-c** f2b3 13:25:30 + 26~49 s 스캔 중 라이브 map 자세로 서쪽 구조물 구역(y −5.95~−5.35, x −2.1~−1.6)에 드는 점을 골라, 같은 점을 A · B · 라이브 · SLAM 자세로 놓아 중심 (x, y) 흔들림 · 안쪽 면(x 95 백분위) 범위. 재생 A 가 비면 라이브로 대신.
- 출력: [`r2_eval_run5.txt`](../debug_log/2026-10-02/outputs/r2_eval_run5.txt)(5 차만 남음). 쓰인 곳 §14.2.
- 결함: R2-c 중심 지표(실수 4). 창 크기 · 구역 하드코딩.

### job841_imuaxis.py · job842_stamp.py · job843_dbg.sh — R2 디버그 (Jetson)
- 841: `/tmp/bag_f2b4` 의 `/imu/data` 각속도 세 축과 `/wheel_odom` ω 를 보간해 휠 |ω| > 0.2 구간의 축별 비 중앙 + frame_id — 게이트의 '로봇 yaw = −ω_y' 약속 확인.
- 842: 같은 bag 에서 `/wheel_odom` · `/scan` 의 '기록 시각 − 헤더 stamp' 중앙 · 범위 + frame — 시각 어긋남 확인(G1 오거부 조사).
- 843: f2b4 를 60 s 지점부터 재생하며 `/r2/wheel_A` 한 개 · `/r2/ekfA` 한 개 · `/r2/wheel_A` hz · EKF A 로그 — 2 차 '휠 미융합' 원인 조사(실수 2).
- 세 도구 모두 출력 원문 없음.

### render_ekfB_slip.py — EKF B 미끄러짐 추적 그림 (PC, matplotlib · scipy)
- 하는 일: rot3 · rot2 의 `r2_*.npz` 로 ① 시작 자세 기준 A · B 궤적 + 줄자 끝 ② 누적 이동 크기 시계열(회전 지령 구간 음영) ③ **독립 검사** — 첫 스캔을 기준 KD 트리로, 이후 스캔을 각 EKF 자세로 odom 에 놓아 최근접 거리 중앙(cm). EKF 가 미끄러짐을 따라가면 정적인 벽이 제자리라 작게 유지.
- 출력: 그림 [`2026-10-02_ekfB_slip.png`](../04_navigation/figures/2026-10-02_ekfB_slip.png), 화면 'A … B …' 한 줄(원문 없음 — §16 의 22.1 / 3.2 · 23.1 / 2.5 cm).
- 재사용: 줄자 없는 회전 검사로 쓸 만한 형식(10-06 이후 단계별 시험 그림의 바탕).

### rf2o_lever.py — 출렁임 = 라이다 지렛대 (PC, matplotlib)
- 하는 일: `rf2o_rot3.npz` 의 원 자세를 시작 자세 기준으로 옮기고 **부호 반전**(라이다 뒤집힘) → 그것을 라이다 위치로 보고 중심 = 라이다 − R(yaw)·(0.152, 0) + (0.152, 0) → EKF B 와 비교, 오른쪽 앞끝((+0.262, −0.165)) 궤적도. 끝값 · 경로 길이 출력.
- 출력: 그림 [`2026-10-02_rf2o_lever.png`](../04_navigation/figures/2026-10-02_rf2o_lever.png), 화면 한 줄(원문 없음 — §18 의 1.89 → 0.73 m · 0.7 cm).
- 한계: '원 자세 = 라이다 위치' 는 가정(모순 2).

### render_day1002.py — 하루 그림 (PC)
- 해설은 [회전 중 장애물 번짐 §9](rotation-obstacle-smear.md). 이 카드 관련: ① `rot3_paths.png`(줄자 대비 A · B · SLAM · rf2o 궤적) ④ `r2_runs.png`(R2 회차별 R2-a · b · c).

### (6 기) step_rot.py · job853_step_init.sh · job854_step.sh · job856_end.sh · run_step.sh — 단계별 90° 줄자 시험 (Jetson rclpy · PC 래퍼, **로버 회전**)
- 부른 형태(PC): `bash run_step.sh init` → `+90` → (사용자 줄자) → `-90` → … 6 단계 → `run_x856.sh`(끝). `run_step.sh` 는 `init` 때 스크립트 3 개를 `\r` 제거해 Jetson `/tmp` 로 보내고, 매 단계 `run_jn.sh`(JX_WHY · JX_TIMEOUT 60)로 `job854_step.sh "+90"` 을 부름 — 실행 투명성 규칙(`/tmp/live/current.log`).
- 853(init): 이전 기록기를 끄고 `ros2 bag record -o /tmp/bag_step1 /scan /tf /tf_static /imu/data /wheel_odom /cmd_vel /odom_rf2o /odom_rf2o/gated /odometry/filtered /odometry/ekf_a /local_costmap/costmap /map` → 4 s 뒤 `step_rot.py init`.
- step_rot.py: 구독 `/odometry/filtered`(B) · `/odometry/ekf_a`(A) · `/odom_rf2o`(R) 자세, `/scan` → 차체 외곽(x −0.248~+0.262 · y ±0.165) 최근접 거리, TF map→base_link(SLAM). `init` = 3 s 뒤 네 자세를 `/tmp/step_state.json` 의 `s0` 로. 단계 = 세 토픽 대기(최대 8 s) → **ω = ±0.38 rad/s 를 20 Hz 로 지령하며 EKF B yaw 증분 누적, 90° 가 되거나 10 s 지나면 멈춤, 외곽 최근접 < 0.08 m 면 즉시 중단** → 정지 지령 10 회 → 1.5 s + 1 s 기다린 뒤 네 자세 스냅샷 → 단계 기록 → 각 추정의 중심 · 오른쪽 앞끝 이동 · 예측 대각 거리 출력. rf2o 는 '라이다 위치 · 병진 부호 반대' 로 보고 시작 기준 이동을 반전 · 지렛대 0.152 를 빼 중심으로(33~37 행, 10-02 §18 식).
- 856: 기록기 INT → tgz → `step_state.json` 을 `step_state_1.json` 으로. `run_x856.sh` 가 PC 로 회수(스크래치패드 `step1/`) → 저장소 `outputs/step_state_1.json` · `bags/bag_step1.tgz`.
- 출력: 화면(단계별 네 추정 줄)은 **원천 소실**, 상태 파일 [`step_state_1.json`](../debug_log/2026-10-06/outputs/step_state_1.json)(단계마다 `deg` · `gap` · `abort` · 네 자세)이 남음. 줄자는 사용자가 대화로 알려 준 값을 [`step_tape.csv`](../debug_log/2026-10-06/outputs/step_tape.csv) 로.
- 결함: rf2o 누적 자세(R)는 단계 3 부터 각도가 무너져(59° vs 94°) 비교에서 뺐다(원인 미확인). 상수(라이다 yaw · x · 외곽)를 하드코딩. 계보: 10-02 §17 사용자 설계 → 이 스크립트 → 10-08 `job940_ratio.py`(비율 시험, Nav2 거치지 않고 `/cmd_vel`). 지금 다시: rf2o 구성에서 그대로 쓸 수 있음(그림자 A 가 없으면 46 행 대기가 8 s 뒤 풀리고 A 는 '없음' 으로 찍힘 — 57~58 행, 회전 판정은 B 만 씀).

### (6 기) render_step1.py — 단계별 시험 그림 (PC, matplotlib)
- 하는 일: §2.1 의 식으로 B · A · SLAM 의 예측 대각 거리 − 줄자 막대(±3 cm 띠) + 짝수 단계의 오른쪽 앞끝 예측 위치와 줄자 원. 화면에 세 줄(추정별 오차 · 평균) — 원천 소실, 11-02 재계산은 §2.1.
- 출력: 그림 [`2026-10-06_step_rot1.png`](../04_navigation/figures/2026-10-06_step_rot1.png). 입력 경로 `step1/step_state_1.json` 은 스크래치패드 기준 — 지금은 저장소 `outputs/` 사본을 가리키게 고쳐야 다시 돈다.

### (6 기) f2c_anal.py · job913_extract.py — 순회 ③-b 번짐 · map→odom (Jetson 추출 · PC 분석)
- 913(Jetson): bag 의 `/tf` map→odom · odom→base · `/odometry/ekf_a` 자세 · `/odometry/filtered` 속도 · `/odom_rf2o` · `/odom_rf2o/gated`(+ 공분산) · `/cmd_vel` · `/plan` 을 수신 시각으로 npz(`x913_f2c{1,2}.npz` — **원천 소실**). `job913_run.sh` 가 f2c1 · f2c2 를 차례로.
- f2c_anal ③-b: EKF B 속도에서 \|ω\| > 0.15 · \|v\| < 0.03 이 1.5 s 넘는 구간 = 제자리 회전. 구간 시작 · 끝의 SLAM 자세(map→odom ∘ odom→base, 끝은 map→odom 을 **끝 + 2 s** 값으로 — 회전 직후 SLAM 보정을 기다린 것), B(odom→base) · A 이동을 시작 map 방향으로 돌려 \|dB − dS\| · \|dA − dS\|(cm). map→odom 부분: 연속 map→odom 변화 크기 합을 회전 중(\|ω\| > 0.15) · 그 밖으로, 끝 − 처음 Δ, 한 번 > 5 cm 보정 목록(앞 12 개만 출력 — f2c2 는 15 회 중 12 개 표시). ③-c 부분은 [게이트 카드](rf2o-gates-people.md) §9.
- 출력 [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt). 결함: 기준이 SLAM(회전 중 수 cm 틀림, 모순 6) · '+2 s' 는 근거 없는 고정값 · 회전량 표시 줄의 각도 펼침이 임시식(24 행).

### (6 기) job903_prep_rf2o_g4.sh · job907_postchk.sh · run_f2c.sh — rf2o 켠 순회 준비 · 러너 (Jetson · PC)
- 903: `EXTRA_SENSORS="rf2o:=true shadow:=true gate_v:=on"` 로 그때 prep(`job780_prep_navmap.sh`) → sensors 인자 · `/rf2o_gate v_mode` 매개 확인. 출력 [`j903_prep.txt`](../debug_log/2026-10-07/outputs/j903_prep.txt).
- 907(읽기만): Nav2 3 노드 lifecycle · `/odom_rf2o` · gated · `/odometry/ekf_a` 6 s hz · `top -b -n2 -d5` 둘째 화면에서 rf2o_gate · rf2o_laser · ekf_node %CPU · EKF 위반 줄 · uptime. 출력 **원천 소실**(SUMMARY §2.1 의 7.8 Hz · 16.5 % 에만).
- run_f2c.sh: f2b 와 같은 10 목표 문자열을 파일 안에 둔 순회 래퍼(STAGE=F2c, `rest5` · 이후 `fullf` 인자) — 해설은 [F2 순회 카드](f2-patrol-loc-jump.md) 이후 칸에서.

## 10. 용어
- **rf2o(Range Flow-based 2D Odometry)**: 연속 두 라이다 스캔의 거리 변화(range flow)로 센서의 평면 운동(vx · vy · ω)을 추정하는 라이다 오도메트리. 지도 없이 프레임 간 정합만 하므로 미끄러짐을 바로 보지만, 움직이는 물체 · 특징 없는 복도에 약하다.
- **게이트(gate)**: 다른 센서와 어긋나는 측정을 EKF 에 넣기 전에 걸러 내거나 믿음(σ)을 낮추는 노드. 여기선 G1 자이로 일치 · G2 정지 검사 · (이후) G3 스캔 겹침 · G4 병진 타당성.
- **twist 만 융합**: EKF 에 자세(pose)가 아니라 속도만 넣는 방식(`odom1_config` 의 vx · vy 만 true). 자세를 넣으면 rf2o 누적 오차가 odom 을 끌고 다니고 계단이 생길 수 있어 속도만 쓴다.
- **B3(회전 중 휠 공분산 확대)**: 컨디셔너가 '순수 회전'(휠 |vx| 작고 |ω| 큼) 동안 휠의 vx · vy 분산을 키워, 휠의 '옆 이동 0' 주장이 rf2o(또는 cuVSLAM)의 옆 속도를 누르지 않게 하는 것.
- **지렛대(lever arm)**: 센서가 회전 중심에서 떨어져 있으면(라이다 x 0.152 m) 회전만으로도 센서는 원을 그리며 움직인다(v = ω × r). 센서 속도 · 자세를 차체 중심으로 바꿀 때 이 몫을 빼야 한다.
- **sim time · 도메인 42 재생**: bag 의 `/clock` 으로 노드 시계를 돌리고(sim time), 라이브 스택과 다른 DDS 도메인에서 돌려 서로 간섭하지 않게 하는 이 프로젝트의 재생 관례.
- **피벗 회전(사용자 제안)**: 한쪽 트랙을 거의 세우고 반대쪽만 움직여 회전축을 그 트랙에 두는 회전. 제자리 회전(양 트랙 반대 방향)보다 바닥을 덜 긁을 것이라는 진단.
- **(6 기) 그림자 EKF A**: rf2o 를 넣기 전 구성(휠 + 자이로)을 같은 입력으로 함께 돌리는 비교용 EKF(`/odometry/ekf_a`, TF 를 안 냄). 같은 주행 · 같은 시각에서 rf2o 의 효과만 떼어 보기 위한 대조군.
- **(6 기) 단계별 줄자 시험**: 제자리 90° 를 한 번씩 돌고 멈출 때마다 차체 모서리와 바닥 표시 사이 거리를 줄자로 재 각 추정의 예측과 비교하는 방식. 방향이 처음으로 돌아온 단계는 회전 효과가 빠져 순수 미끄러짐만 남는다.
- **(6 기) map→odom 누적 보정**: 위치 추정 SLAM 이 odom(EKF) 자세를 지도에 맞추려 더한 보정의 총량. 오도메트리가 드리프트할수록 커진다.
- **(6 기) 트랙 비 r**: 회전할 때 느린 트랙 속도 / 빠른 트랙 속도(부호 포함). r −1 = 제자리 회전, r 0 = 한쪽 트랙 정지(피벗).
