# rf2o 도입 — 라이다 스캔 정합 속도로 회전 중 미끄러짐을 EKF 에 (5 기 부분: 10-02 §13~§18)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| 10-02 시점 **오프라인 통과(R2)** — rf2o 게이트 + '순수 회전 중 휠 병진 σ 0.3' 의 EKF B 가 통제 회전 rot3 을 줄자 대비 **4.3 cm**(지금 EKF 36.9 cm)로 따라가고 직진 축척 **0.998** 유지(재생 **측정**). 구석 기동 지표 R2-c 는 선언 기준 불합격(지표 설계 실수). 라이브 미적용. 이후: 10-06 R3 라이브 · 단계별 줄자 평균 1.5 cm, 10-07 G4 → **10-23 주 EKF 병진 = cuVSLAM 으로 결정, rf2o 는 기본으로 안 띄움**(지금 `ekf.launch.py rf2o` 기본 false · prep 기본 `ODOM=vslam`) | 10-02 (이 카드는 10-02 §13~§18 을 채움, '이후' 는 포인터) | [10-02 §13](../debug_log/2026-10-02/SUMMARY.md) — §12.1 에서 로컬 map 좌표 대책이 불합격한 뒤 사용자 결정 | (10-02) Jetson `~/rf2o_ws`(MAPIRlab `rf2o_laser_odometry` ros2 브랜치 b38c68e) 소스 빌드 · 오프라인 원형 `r2_gate.py`. (지금, 10-06 이후) [`rf2o_gate.py`](../../ros2_ws/src/rover_bringup/scripts/rf2o_gate.py) · [`rf2o.yaml`](../../ros2_ws/src/rover_bringup/config/rf2o.yaml) · [`ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py) `rf2o:=` · `shadow:=` · `gate_*:=` 인자(기본 끔) · `Docs/tools/prep_patrol.sh ODOM=rf2o` | [회전 중 장애물 번짐](rotation-obstacle-smear.md)(동기) · [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(대책 방향 D 의 출발점) · [휠 오도 스케일 · 회전 슬립](wheel-odom-scale-slip.md) · [센서 컨디셔너](sensor-conditioner.md)(B3 공분산) · [센서 데크 yaw −2.68°](sensor-deck-yaw.md)(라이다 yaw 상수) · [slam-fork-rotation.md](slam-fork-rotation.md) · [F2 순회와 위치 점프](f2-patrol-loc-jump.md) |

**한 줄**: 회전 중 미끄러짐 30 cm 를 EKF 가 0.3 cm 로 보고(rot2), 회전 모델 B2 와 로컬 map 좌표 둘 다 대책이 못 되자 사용자가 rf2o(연속 라이다 스캔 정합으로 차체 속도를 내는 오도메트리) 도입을 시작했다. 같은 회전 bag 을 rf2o 에 다시 먹이니 rf2o 의 순 이동은 두 시험 모두 0.35 · 0.37 m 로 일관됐고(SLAM 0.322 · 0.114, EKF 0.003), 사용자 줄자(rot3 뒤 27.5 · 오른쪽 24.5 cm)는 rf2o 의 **크기 · 성분과 맞고 부호만 두 축 다 반대**였다 — 라이다가 yaw π − 2.68° 로 뒤집혀 달려 병진이 라이다 좌표로 나온 것이라 차체 속도 = R(π − 0.04677) · v_rf2o 로 고쳤다. 게이트(G1 자이로 일치 · G2 정지 검사 · 가변 σ)를 거쳐 병진 vx · vy 만 EKF 에 넣는 B 를 오프라인 재생 5 차례로 다듬었는데(자이로 없는 bag · QoS 불일치 · 휠이 rf2o 를 누름 · G1 오거부), 마지막 판은 rot3 끝을 줄자 4.3 cm 안으로 잡고 직진 축척을 유지했다. 사용자는 다음 시험을 '90° 마다 줄자' 로 설계했다(→ 10-06 실행).

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

## 4. 조치와 효과
- **10-02 에 바뀐 것**: Jetson `~/rf2o_ws` 빌드(라이브 스택 미연결) · 오프라인 원형 `r2_gate.py`. 스택 기본값은 그대로.
- **효과(재생)**: rot3 끝 오차 0.369 → **0.043 m**, 직진 축척 0.998, 구석 기동 벽 안쪽 면 범위 0.198 → 0.099 m(SLAM 0.084), §19 '기동 뒤 남은 차' A −15.2 → B −4.9 cm([회전 중 장애물 번짐](rotation-obstacle-smear.md) §2).
- **한계**: 같은 bag 4 개로 5 차례 조정(과적합 위험을 알고 멈춤). 사람 섞인 오염을 G1 이 잡는지는 미검증(T1~T3 몫). 라이브 CPU 미측정.
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

**모순 · 원문 대조(이 카드를 쓰며 찾은 것)**
1. §13.2 '직진 bag(f2b4) 재생에서도 rf2o vx / EKF vx = **−0.94**' · 'SLAM/EKF 1.000, rf2o/SLAM **0.932**(창 16 개)': 원문 [`rf2o_fix.txt`](../debug_log/2026-10-02/outputs/rf2o_fix.txt) 는 보정 전 vx 비 **−0.912**, 보정 후 **0.911**(EKF 기준, 표본 683). 0.932 · 1.000 · 16 개는 원문 출력이 없다(별도 계산 — 원천 미상). 결론(직진은 rf2o 가 7~9 % 작게 봄 → 휠 우선)은 어느 값이든 같다.
2. 지렛대 판단: §13.2 는 'ω × r 보정은 경로 0.54 → 1.65 m 로 나빠짐 = rf2o 가 이미 반영' 이라 했는데, 같은 원문에서 끝점은 보정 c (−0.308, −0.187) 가 줄자에 **6.7 cm**, 보정 안 한 b (−0.340, −0.197) 가 **8.1 cm** 로 c 가 더 가깝다. 또 §18 은 'rf2o 원 **자세**는 라이다 위치의 궤적' 이라 지렛대를 빼야 중심이 된다고 했다(끝 0.7 cm). '속도는 이미 반영' 과 '자세는 라이다 위치' 가 rf2o 안에서 어떻게 함께 성립하는지는 **미확인**(코드 미검토). 지금 게이트는 지렛대를 빼지 않는다(b 방식).
3. §14.1 '3 차: A = 라이브와 일치(검증)': R2-a 에선 맞지만(A · 라이브 둘 다 0.369) [`r2_eval_run5.txt`](../debug_log/2026-10-02/outputs/r2_eval_run5.txt) R2-c 안쪽 면 범위는 **A 0.198 vs 라이브 0.130**(중심 흔들림은 0.131 vs 0.128 로 비슷)으로 다르다. 같은 설정이어야 할 두 EKF 가 구석 기동에서 갈라진 이유는 **미확인**(10-06 §2 R3 도 '그림자 A 가 라이브와 일치' 라고만 적음). 그래서 'B 가 A 의 절반' 은 재생 A 기준이고, 라이브 기준이면 0.130 → 0.099(약 24 % 감소)다.
4. §14.2 G1 거부 'f2b3 2': 5 차 csv [`r2_f2b3_gate.csv`](../debug_log/2026-10-02/outputs/r2_f2b3_gate.csv) 는 g1 **3** · g2 **4**. 다른 bag 도 G2 거부가 2~5 건씩 있는데(rot3 5 · rot2 4 · f2b4 3) SUMMARY 는 G1 만 적었다. 정지 검사가 사람 없는 bag 에서 몇 건 걸리는 것은 기록할 가치가 있음(원인 미확인).

## 6. 남은 것 (10-02 시점)
- R3: 게이트를 정식 노드로 · ekf.launch 인자(기본 끔) · 라이브 CPU.
- 단계별 90° 줄자 시험(§17) — 오프라인 4.3 cm 가 라이브 · 매 단계에서도 성립하는지.
- 사람 섞인 스캔 오염(T1~T3) — G1 이 잡는지.
- 회전 중 rf2o σ 0.03 을 더 작게 / rf2o 자세 증분 직접(§18 후보).
- 피벗 회전(사용자 진단)의 미끄러짐 비교 — 미시험.
- rf2o 부호 반대의 코드 기전 · 지렛대 반영 여부 — 미확인.

## 7. 이후 (10-06 ~) — 포인터
- **10-06 §1~§3 R3**: `rf2o_gate.py` 정식 노드 · `ekf.launch.py rf2o:=` · `shadow:=`(그림자 EKF A) — 재생으로 R2 결과 재현(f2b4 축척 0.998, f2b3 안쪽 면 A 0.196 / B 0.096 / SLAM 0.084), **rot2 · rot3 bag 은 Jetson 재부팅으로 소실**(PC 회수 안 한 내 실수, 10-06 §2) — [10-06 SUMMARY](../debug_log/2026-10-06/SUMMARY.md).
- **10-06 §4.1 단계별 90° 줄자(§17 실행)**: EKF B **줄자 대비 |오차| 평균 1.5 cm**, 방향 원위치 단계(2 · 4 · 6) 0.0 / +0.1 / +0.7 cm(EKF A 단계 2 −10.0 cm) — 메모리 '회전 미끄러짐 · rf2o' 의 '라이브 1.5 cm'.
- 10-06 §5: 게이트 회전 기준 `/imu/data`(200 Hz) → EKF ω(30 Hz, `gyro_source ekf` 기본) — 라이브 정지 기동에서 게이트 CPU 39 %(코어 하나).
- 10-06 §9~§11 사람 시험: T1 · T1b 통과, T2 합성 정지 몸 ≤ 2.8 cm 통과, **움직이는 큰 가림(C · D · E) 불합격 9.5~27.9 cm** → §12 **G3(스캔 겹침) 기각** → §12.1 G4(회전 중 병진 타당성).
- 10-07 §1.1 G4: C · D · E 4.5 / 7.3 / 7.4 cm(> 3 불합격) · 깨끗 2.0 — 오차 3~4 배 감소. §3.2 G4 설계 결함(곡선 회전의 정상 전진을 오염으로) → **§4 휠 잔차 기준**(곡선 σ 키움 · 버림 35 → 2 %) — [10-07 SUMMARY](../debug_log/2026-10-07/SUMMARY.md). 10-07 §2 rf2o 켠 순회 f2c1 · f2c2 9/10(남서 방향 맞춤 실패는 [F2 순회와 위치 점프](f2-patrol-loc-jump.md) 이후 칸).
- 10-08 회전 방식 시험(사용자 피벗 진단의 시험 — 비율 시험 Q1 전부 미달, 메모리 '회전 방식 시험').
- 10-20 cuVSLAM 병진 속도 융합(재실행 V4: 회전 미끄러짐 창 −12~29 %, rf2o 와 같이 써도 같음) → **10-23 §16 사용자 결정: 주 EKF 병진 = cuVSLAM**(`vslam:=on`, rf2o 안 띄움 — W3 회전 창 13.2~16.8 cm vs rf2o 21.5~30.7 · 멈칫 5 vs 12~14 · CPU 70 vs 75~76 %) — [10-23 SUMMARY](../debug_log/2026-10-23/SUMMARY.md). rf2o 구성은 `ODOM=rf2o` 로 남음.

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
| 지금 코드 | 게이트 · 설정 · launch | `ros2_ws/src/rover_bringup/scripts/rf2o_gate.py` · `config/rf2o.yaml` · `launch/ekf.launch.py` |

## 9. 도구 해설
공통: Jetson 재생은 **도메인 42 · sim time · `fastdds_udp_only.xml`**, `ros2 bag play --clock 100`(100 Hz 시계). npz 는 `/tmp` → PC 스크래치패드(`…\scratchpad\f2a6\…`)로 옮겨 분석했고 **지금은 소실**. rot2 · rot3 bag 도 소실(10-06 §2) — 이 카드의 R1 · R2 결과는 다시 만들 수 없다(f2b3 · f2b4 bag 은 10-06 재생에 쓰였으나 PC 사본 위치 미확인).
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

## 10. 용어
- **rf2o(Range Flow-based 2D Odometry)**: 연속 두 라이다 스캔의 거리 변화(range flow)로 센서의 평면 운동(vx · vy · ω)을 추정하는 라이다 오도메트리. 지도 없이 프레임 간 정합만 하므로 미끄러짐을 바로 보지만, 움직이는 물체 · 특징 없는 복도에 약하다.
- **게이트(gate)**: 다른 센서와 어긋나는 측정을 EKF 에 넣기 전에 걸러 내거나 믿음(σ)을 낮추는 노드. 여기선 G1 자이로 일치 · G2 정지 검사 · (이후) G3 스캔 겹침 · G4 병진 타당성.
- **twist 만 융합**: EKF 에 자세(pose)가 아니라 속도만 넣는 방식(`odom1_config` 의 vx · vy 만 true). 자세를 넣으면 rf2o 누적 오차가 odom 을 끌고 다니고 계단이 생길 수 있어 속도만 쓴다.
- **B3(회전 중 휠 공분산 확대)**: 컨디셔너가 '순수 회전'(휠 |vx| 작고 |ω| 큼) 동안 휠의 vx · vy 분산을 키워, 휠의 '옆 이동 0' 주장이 rf2o(또는 cuVSLAM)의 옆 속도를 누르지 않게 하는 것.
- **지렛대(lever arm)**: 센서가 회전 중심에서 떨어져 있으면(라이다 x 0.152 m) 회전만으로도 센서는 원을 그리며 움직인다(v = ω × r). 센서 속도 · 자세를 차체 중심으로 바꿀 때 이 몫을 빼야 한다.
- **sim time · 도메인 42 재생**: bag 의 `/clock` 으로 노드 시계를 돌리고(sim time), 라이브 스택과 다른 DDS 도메인에서 돌려 서로 간섭하지 않게 하는 이 프로젝트의 재생 관례.
- **피벗 회전(사용자 제안)**: 한쪽 트랙을 거의 세우고 반대쪽만 움직여 회전축을 그 트랙에 두는 회전. 제자리 회전(양 트랙 반대 방향)보다 바닥을 덜 긁을 것이라는 진단.
