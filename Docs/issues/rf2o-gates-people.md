# rf2o 게이트 G1~G4 · 사람 시험 — 정식 노드, EKF 가 rf2o 를 믿는 정도, 움직이는 가림 (6 기: 10-06 · 10-07)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **보류(부분 해결)** — 정지 중 사람(T1 · T1b, 실측)과 회전 중 정지한 몸 · 걸어 지나가는 다리(T2 합성)는 EKF B 오차 ≤ 2.8 cm 로 통과. **크게 가린 채 움직이는 몸(합성 C · D · E)은 G4 를 켜도 4.5 / 7.3 / 7.4 cm 로 목표 3 cm 미달**(재생 **측정**, G4 없이 9.5~27.9) — 남은 오차는 '가린 동안 라이다에 미끄러짐 정보가 없다' 로 **추정**. G4 의 곡선 회전 오판은 휠 잔차 판정으로 고침(재생 35 → 2 %, **측정**). 실제 사람이 주행 중 끼는 T3 · 전선 시험 W 는 이 기간에 안 함. 이후 10-23 주 EKF 병진 = cuVSLAM 결정으로 rf2o 는 기본으로 안 띄움 — 게이트는 `ODOM=rf2o` 구성에만 남음 | 10-06 §1 ~ 10-07 §6.1 (10-08 은 같은 구성 유지만) | [10-06 §1](../debug_log/2026-10-06/SUMMARY.md) — 10-02 R2 오프라인 원형을 정식 노드로(사용자 '1 번 진행'). 사람 시험의 근거는 09-29 §6.1 rf2o 필수 조건(자이로 일치 · 정지 검사 · 가변 σ) | [`rf2o_gate.py`](../../ros2_ws/src/rover_bringup/scripts/rf2o_gate.py)(커밋 4fdeeaaf → 10a93fa4 `gyro_source` → 404f81fe G3 · G4 → 1e3819e6 `v_ref wheel`) · [`ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py) `rf2o:=` · `shadow:=` · `gate_csv:=` · `gate_src:=` · `gate_q:=` · `gate_v:=` · `gate_vref:=`(지금 98~106 행) · [`rf2o.yaml`](../../ros2_ws/src/rover_bringup/config/rf2o.yaml) · CMakeLists `install(PROGRAMS … rf2o_gate.py)` · prep `job240_clean.sh`(`~/rf2o_ws` source · 정리 목록) | [rf2o 도입](rf2o-introduction.md)(이 카드의 본줄기 — 단계별 줄자 시험 · rf2o 켠 순회) · [센서 컨디셔너](sensor-conditioner.md)(B3 공분산이 사는 노드) · [회전축 보정 B2 · 회전 분산 B3](icr-b2-b3.md)(B3 = 이 게이트의 짝) · [F2 순회 · 위치 점프](f2-patrol-loc-jump.md)(rf2o 켠 f2c · f2d 순회) · [회전 중 장애물 번짐](rotation-obstacle-smear.md)(동기) · [센서 데크 yaw −2.68°](sensor-deck-yaw.md)(게이트에 박힌 라이다 yaw 상수) · [DDS 공유메모리 사고](dds-shm-incident.md)(재생 도메인 분리 관례) · [바닥 전선 · 시험 W](cable-step-over.md)(10-06 §7 — rf2o 평면 가정 위반) · [회전 방식 · 트랙 비율](rotation-method-track-ratio.md)(10-08, 게이트 밖 수단 ①) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md) (8 기) |

**한 줄**: 10-02 의 오프라인 게이트를 정식 노드 · launch 인자(기본 끔)로 옮겨 재생 결과를 0.2~0.3 cm 차로 재현하고, 라이브 정지 기동에서 게이트 CPU 39 % 를 회전 기준 = EKF ω(30 Hz)로 바꿔 16 % 로 줄였다. EKF 가 rf2o 를 믿는 몫은 이산 σ 두 단계로 정해져 직진 · 정지 2~4 %, 제자리 회전 ≈ 98 % 라(1/σ² × 발행률 근사), 정지 중 사람(T1 · T1b)은 rf2o 원 출력이 1.8 cm 흔들려도 EKF 는 0.0 cm 였지만 **위험은 회전 중 가림**이었다. 단계별 줄자 bag 에 원기둥 몸을 그려 넣은 합성 재생(T2)에서 정지한 몸 · 걸어 지나가는 다리는 통과했고, 30~50 % 를 가린 채 움직이는 몸은 9.5~27.9 cm 로 실패했다 — G1(자이로 일치)은 '회전은 맞고 병진만 틀린' 오염을 못 본다. G3(스캔 겹침 q)는 느린 몸이 프레임당 2.4 cm 라 못 갈라 기각, G4(회전 중 병진 속도 물리 범위)는 오차를 3~4 배 줄였으나 목표 3 cm 미달이고, 실제 순회에서 '전진하며 도는 곡선' 의 정상 속도를 오염으로 보는 설계 결함이 드러나 판정량을 휠과의 잔차로 고쳤다.

## 1. 증상 (이 카드가 다루는 질문)
- 10-02 R2 는 사람 없는 bag 4 개로만 조정했다 — 사람 섞인 스캔 오염을 G1 이 잡는지 미검증, 라이브 CPU 미측정([rf2o 도입](rf2o-introduction.md) §4 한계).
- 10-06 §3 라이브 정지 기동: **게이트 CPU 39 %**(코어 하나, csv 끔) — [`j851_r3prep.txt`](../debug_log/2026-10-06/outputs/j851_r3prep.txt) `CPU rf2o_gate.py: 39 %`.
- 10-06 §9.2 사용자 지적: 단계별 줄자 시험(§4) 때 줄자를 재며 **몸으로 라이다 시야 약 70 %** 를 가렸다 — 그게 결과에 영향이 있었나.
- 09-29 §6.1 의 rf2o 필수 조건 중 '정지 검사' · '자이로 일치' 가 실제 사람 환경에서 충분한지(09-29 사용자 요구 '사람 다니는 실내에 강건').

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-06 §1 | R3 코드 — `r2_gate.py` 를 `rover_bringup/scripts/rf2o_gate.py` 로, `rf2o.yaml`, `ekf.launch.py rf2o:=true\|false`(**기본 false**) · `shadow:=true`(그림자 EKF A `/odometry/ekf_a`, TF 없음, rf2o 이전 구성) · `use_sim_time` · `gate_csv`. `rf2o:=true` 면 컨디셔너 B3 를 σ 0.3 으로 켬, `conditioner:=py` 와 같이 쓰면 거부 | — (코드) | 방향 보정 R(π − 0.04677) · G1 0.1 s 평균 · 바닥 0.12 · G2 · σ 회전 0.03 / 직진 vx 0.10 · vy 0.03 — 10-02 5 차 그대로. TODO(improve): 200 Hz 자이로를 Python 으로 받음 | 커밋 4fdeeaaf 의 `rf2o_gate.py` · `ekf.launch.py` · `rf2o.yaml` · [`job850_deploy.sh`](../debug_log/2026-10-06/jobs/job850_deploy.sh) |
| 10-06 §2 | 재생 검증(도메인 42 · sim time, 로버 안 움직임) — 정식 launch 로 f2b3 · f2b4 bag | f2b4 직진 축척 **B 0.998 · A 0.999 · 라이브 1.000**(3 s 창 17 개). f2b3 안쪽 면 범위 **A 0.196 · B 0.096 · 라이브 0.130 · SLAM 0.084 m**. 게이트(f2b3) 통과 1290 · G1 1 · G2 2. 게이트 CPU 누적 85 s | 오프라인 원형과 **같은 결과**(차 0.2~0.3 cm). '그림자 EKF A 도 라이브 기록과 일치' — **⚠ 안쪽 면 범위는 A 0.196 vs 라이브 0.130 으로 다름**(중심 최대는 0.129 vs 0.128 로 같음, §5 모순 1). 회전 bag rot2 · rot3 는 재부팅으로 소실(→ [rf2o 도입](rf2o-introduction.md) 실수 칸) | [`r3_eval.txt`](../debug_log/2026-10-06/outputs/r3_eval.txt) · [`j850_r3_replay.txt`](../debug_log/2026-10-06/outputs/j850_r3_replay.txt) · [`r3_replay.sh`](../debug_log/2026-10-06/jobs/r3_replay.sh)(이날 쓴 판 = 커밋 4fdeeaaf) · [`r3_rec.py`](../debug_log/2026-10-06/jobs/r3_rec.py) · [`r3_eval.py`](../debug_log/2026-10-06/jobs/r3_eval.py). '기동 뒤 남은 차 A −15.1 / B −4.7 cm' · '재생 297 s' 는 **원천 소실**(r3_eval 은 이 줄을 안 냄) |
| 10-06 §3 | 라이브 정지 기동(사용자: 출발 테이프 45 cm 앞) — `EXTRA_SENSORS="rf2o:=true shadow:=true"` | /odom_rf2o 9.997 · gated 10.007 · EKF B 30.005 · A 29.135 · /wheel_odom/plain 25.143 Hz. B3 켜짐(`rot_vx_var 0.09`), EKF `odom1 = /odom_rf2o/gated`. 게이트 통과 1957 · G1 3 · G2 7. **CPU rf2o 4 % · 게이트 39 % · 그림자 A 11 %**, load 10~12 | 게이트 39 % 의 원인 = Python 200 Hz 자이로 콜백(**추정** — 분리 측정 안 함). 대책 후보: 회전 기준을 EKF ω(30 Hz)로 | [`j851_r3prep.txt`](../debug_log/2026-10-06/outputs/j851_r3prep.txt) · [`job852_prep_rf2o.sh`](../debug_log/2026-10-06/jobs/job852_prep_rf2o.sh) · [`job851_r3chk.sh`](../debug_log/2026-10-06/jobs/job851_r3chk.sh) |
| 10-06 §5 | `gyro_source`(기본 **ekf**): 회전 기준 `/imu/data` 200 Hz → `/odometry/filtered` ω 30 Hz, 비교 창 0.1 → **0.15 s**. 되돌리기 `gate_src:=imu` | — | EKF ω 는 자이로(σ 0.02)가 지배하고 rf2o 는 ω 를 안 넣으므로(odom1 = vx · vy) **순환 없음**. 첫 재생 시도는 재생 제한 500 s 를 bag_step1(2021 s)보다 짧게 잡아 기록기가 저장 전에 끊김(실수 2) | 커밋 10a93fa4 |
| 10-06 §5.1 | 검증 재생(bag_step1, ekf 기준 vs 라이브 imu 기준) | 정확도: EKF B 차 최대 0.7 · 끝 0.2 cm, 끝 이동 18.7 vs 18.5 cm. CPU 재생 수치(ekf 2100 s/300 s · imu 198 s/300 s 등) | 정확도는 같음. **CPU 는 무효** — `r3_replay.sh` 가 정리 때 이름으로 `pkill -f ekf_node` 등을 해 **라이브 스택까지 껐고**, CPU `pgrep` 도 다른 프로세스를 잡음(실수 1). 고침: launch PID 의 프로세스 그룹만 | 정확도 · CPU 수치 모두 **원천 소실**(대화에만). 고친 판 [`r3_replay.sh`](../debug_log/2026-10-06/jobs/r3_replay.sh)(커밋 3e71a37d) |
| 10-06 §6 | 사용자 질의 '공분산은 이산인가 연속인가' 정리 | 휠(B3): 순수 회전(\|vx\| < 0.02 · \|ω\| > 0.10) vx · vy 0.3 / 그 밖 0.02 · 0.01. rf2o: \|ω\| > 0.15 면 0.03 · 0.03 / 그 밖 0.10 · 0.03. 실효 몫(1/σ² × 휠 25 · rf2o 10 Hz, 과정 잡음 무시): **직진 vx ≈ 2 % · vy ≈ 4 %, 제자리 회전 ≈ 98 %**, \|ω\| 0.10~0.15 틈에서 vx ≈ 78 % | **이산 두 단계**. 한계 ① \|ω\| 경계에서 가중이 뜀 ② 휠 · rf2o 문턱 불일치(0.10 vs 0.15 — 게다가 휠 쪽 ω 는 자이로 우선, 게이트 쪽은 EKF ω) ③ rf2o 자체 품질을 안 봄. 계획 항목 C(연속 · 품질 σ) | 손 계산(**계산 출력 없음** — 아래 §2.1 에서 다시 계산) · 휠 σ 출처 [`conditioner_core.hpp`](../../ros2_ws/src/rover_bringup/include/rover_bringup/conditioner_core.hpp) 43~48 · 184 행 |
| 10-06 §8 | 갱신 계획 1~8 + 내 평가 | — | 평가: 1~6 이 모두 rf2o 다듬기라 목표('rf2o 켠 순회가 나아지나')가 맨 뒤, 연속 σ 는 정확도 이득 근거 없음, 피벗 회전은 원인 제거, TF 기울기는 비용 큼. **사용자 결정: ① CPU → ② 사람 T1 · T2 → ③ rf2o 켠 F2 순회 비교(+T3) → 기본값 결정 → ④ 피벗 회전 → ⑤ 전선 시험 → ⑥ 결과 따라 C · G3 · TF 기울기** | — |
| 10-06 §9 | ① CPU 판정 + ② T1 · T2 선언. prep 때 로버가 사용자 쪽을 보게 놓여 map (0.043, 0.275, −10.7°) — 지도 위치는 틀렸을 수 있음(T 지표는 odom · rf2o 끼리라 무관) | **게이트 39 → 16 %**(정지 10 s, 같은 방식) · rf2o 4 % · 그림자 A 11 %. 기동 직후 G1 거부 64 | ① **통과**(절반 이하). G1 64 는 '사람이 앞에 있던 구간' 으로 **추정**. T1 판정: EKF B 최대 이동 ≤ 2 cm. T2 판정: 원위치 단계 \|예측 − 줄자\| ≤ 3 cm | [`j859_prep_people.txt`](../debug_log/2026-10-06/outputs/j859_prep_people.txt) |
| 10-06 §9.1 T1 | 정지 60 s, 사용자가 앞 0.5~2 m 에서 발만 움직임(라이다 높이) | EKF B · A 끝 · 최대 **0.000 m**, rf2o 원 자세 최대 0.002 m. rf2o 원 속도 최대 0.006 m/s(0.02 넘음 0/595). 게이트 누계 전후 G1 64 → 64 · G2 11 → 11(증가 0). 2 m 안 바뀐 점 스캔당 중앙 156 · 최대 1228, 각도 −82~+120° | **통과** — 걸러낼 오염 자체가 안 생김. 해석: rf2o 강건 추정이 수백 점(1800 빔 중)은 무시(**추정**). 바뀐 점 수는 첫 스캔 대비라 잡음 · 가장자리 점 섞임(사람 몫 분리 못 함) | [`j860_t1.txt`](../debug_log/2026-10-06/outputs/j860_t1.txt) · bag `2026-10-06/bags/bag_t1.tgz`(로컬, git 제외) · [`t1_still.py`](../debug_log/2026-10-06/jobs/t1_still.py) · [`job860_t1.sh`](../debug_log/2026-10-06/jobs/job860_t1.sh) · [`job861_t1scan.py`](../debug_log/2026-10-06/jobs/job861_t1scan.py)(출력 **원천 소실** — 156 · 1228 · −82~+120 은 SUMMARY 에만) |
| 10-06 §9.2 T1b | 사용자 제안: 줄자 잴 때처럼 몸으로 시야를 크게 가림, 정지 90 s | 바뀐 점 스캔당 중앙 253 · 90 % 477 · 최대 975(≈ 54 %, 잡음 섞임), 각도 −69~+110°. **EKF B 0.000 m**, A 0.000, **rf2o 원 자세 최대 0.018 m**(+25~35 s), 원 속도 최대 0.025 m/s(0.02 넘음 1/889) → G2 1 개 거부, 통과분 최대 0.016 | **통과**. 막은 것은 ① 정지 중 휠 가중(rf2o 몫 2~4 %) ② G2. → 단계별 줄자 중 가림은 영향 거의 없음(정지 구간). **위험한 경우 = 회전 중 가림**(휠 σ 0.3 → rf2o ≈ 98 %) | [`j863_t1b.txt`](../debug_log/2026-10-06/outputs/j863_t1b.txt) · bag `bag_t1b.tgz` · [`job862_t1b_start.sh`](../debug_log/2026-10-06/jobs/job862_t1b_start.sh) · [`job863_t1bscan.py`](../debug_log/2026-10-06/jobs/job863_t1bscan.py) |
| 10-06 §10 | T2 합성 선언(사용자 동의: 2D 라이다라 거친 몸 모양은 문제 아님) — bag_step1 재생 스캔에 시작 자세 기준 바닥 고정 원기둥(반경 0.08, 로버 중심 0.6 m 호, 호 중심 앞 +20°), 가림 0 · 15 · 30 · 50 · 70 %(도메인 51~55 동시) | — | 판정: 가림 0 % 가 §4(1.5 cm)를 재현해야 방법 유효, 각 가림 EKF B \|예측 − 줄자\| 평균 ≤ 3 cm | [`occ_scan.py`](../debug_log/2026-10-06/jobs/occ_scan.py)(커밋 a8b61aa1 판) · [`occ_run.sh`](../debug_log/2026-10-06/jobs/occ_run.sh) · [`occ_rec.py`](../debug_log/2026-10-06/jobs/occ_rec.py) · [`job864_occ.sh`](../debug_log/2026-10-06/jobs/job864_occ.sh) |
| 10-06 §10.1 | 재생(첫 시도 무효: 정수 매개를 DOUBLE 선언 노드에 줘 가림 노드가 안 뜸 + 이름 pkill 이 자기 ssh 명령까지 죽임 → `occ_kill.sh`) | 실제 가린 빔 −1 · 16 · 32 · 52 · 72 %. EKF B 평균 \|오차\| **1.6 · 2.2 · 2.8 · 2.8 · 1.5 cm**, 원위치(2 · 4 · 6) 0 % 0.0 / 0.0 / 0.2 · 30 % 0.6 / 2.0 / 3.6. G1 거부 35 · 5 · 6 · 11 · 32 | **전부 통과**. 방법 유효(0 % 가 1.6 · 0.0/0.0/0.2 로 라이브 1.5 · 0.0/0.1/0.7 재현). 30~50 % 에서 원위치 오차가 조금씩 쌓임. 72 % 가 오히려 좋은 건 **합성 몸이 고정이라 rf2o 가 몸 자체를 정합 특징으로 씀**(추정). 한계: 실제 사람은 움직인다 | [`occ_eval.txt`](../debug_log/2026-10-06/outputs/occ_eval.txt) · [`occ_eval.py`](../debug_log/2026-10-06/jobs/occ_eval.py) · [`occ_kill.sh`](../debug_log/2026-10-06/jobs/occ_kill.sh) |
| 10-06 §11 | 움직이는 몸 5 조건(도메인 61~65): A 다리 앞 0.8 m 걸어 지나감(최고 0.52 m/s) · B 다리 0.5 m(0.47) · C 50 % 가린 채 좌우 흔듦(0.24) · D 30 % 다가갔다 물러남(0.42) · E 50 % 빠르게(0.63) | — | 판정 같음(평균 ≤ 3 cm) | `occ_scan.py`(커밋 9c5c03be — `amp` · `period` · `move_deg` · `legs`) · [`job870_occmove.sh`](../debug_log/2026-10-06/jobs/job870_occmove.sh) |
| 10-06 §11.1 | 재생 | 평균 \|오차\| **A 2.1 ✔ · B 2.1 ✔ · C 9.5 ✘ · D 21.0 ✘ · E 27.9 ✘**. G1 / G2 거부 A 7/5 · B 4/4 · C 27/13698 · D 19/9405 · E 1698/11836. B − 진실 어긋남 경로 회전 중 1.64~4.20 · 정지 중 0.20~0.27 m(C · D · E) | 틀어진 곳은 **회전 중** — 정지 중엔 G2 가 수천 개를 버려 막음. G1 은 C · D 에서 27 · 19 개만 → **회전은 맞고 병진만 틀린 오염**(§7 에서 예상한 G1 의 맹점)이 그대로 EKF 로. 실제 §4 에서 문제가 없던 건 측정 중 로버가 정지해 있었기 때문 | [`occm_eval.txt`](../debug_log/2026-10-06/outputs/occm_eval.txt)(오차 줄만) · [`occm_eval.py`](../debug_log/2026-10-06/jobs/occm_eval.py) · 그림 [`2026-10-06_occ_results.png`](../04_navigation/figures/2026-10-06_occ_results.png). **G1 / G2 거부 수와 어긋남 경로는 원천 소실**(job870 화면 출력 · 대화 계산) |
| 10-06 §12 | 항목 C — G3(`q_mode`): 직전 스캔을 후보 움직임(rf2o 병진 + 자이로 회전)으로 옮겨 이번 스캔과 비교, 5 cm 넘게 어긋난 점 비율 q. 보정 재생(q 기록만, 첫 시도는 csv 쓰는 줄이 편집에서 빠져 q 미기록 — 실수 4) | 회전 중 q 중앙 / 90 %: 깨끗 0.048 / 0.094 · 정지한 몸 50 % 0.017 / 0.040 · 다리 0.065 / 0.115 · **C 0.023 / 0.049** · E 0.090 / 0.250. 회전 중 rf2o 병진 \|v\| 중앙 / 90 %: 깨끗 0.010 / 0.037 · 정지 몸 0.010 / 0.032 · 다리 0.012 / 0.035 · **C 0.063 / 0.168 · E 0.113 / 0.401** | **G3 기각** — 오염이 가장 큰 C 의 q 가 깨끗보다 낮음: 0.24 m/s 몸은 0.1 s 프레임당 2.4 cm 라 허용 5 cm 안. **G4 채택 후보**: 회전 중 \|v\| > 0.05 면 σ 1~10 배, > 0.10 이면 버림 | 커밋 404f81fe `rf2o_gate.py`(G3 · G4) · [`job871_qcal.sh`](../debug_log/2026-10-06/jobs/job871_qcal.sh) · 그림 [`2026-10-06_gate_quality.png`](../04_navigation/figures/2026-10-06_gate_quality.png) · 입력 `qcal_*_gate.csv` 는 PC 스크래치패드에만 있었음 → **원천 소실**(표 값은 SUMMARY 에만) |
| 10-06 §13 | G4 5 조건 재생 중 사용자 '내일로' → 중단, 시험 프로세스만 PID 로 정리 | 라이브 ekf 2 · 게이트 1 살아 있음 확인 | **G4 결과 없음 — 부분 결과도 판정에 안 씀**. 내일 판정: C · D · E 평균 ≤ 3 cm **이고** 깨끗 · A 가 나빠지지 않음. G4 의 비용 = 버리는 순간 실제 미끄러짐도 못 봄 | `run_kill.sh`(저장소에 없음) |
| 10-07 §1 | G4 재생 A/B 선언(`v_mode=on`, 같은 합성 5 조건, 도메인 81~85) | 기준(G4 끔) 깨끗 1.6 · A 2.1 · C 9.5 · D 21.0 · E 27.9 | 판정 1: C · D · E 각각 ≤ 3 cm. 판정 2: 깨끗 · A 가 +0.5 cm 넘게 나빠지지 않음(≤ 2.1 · ≤ 2.6) | [`job876_g4.sh`](../debug_log/2026-10-07/jobs/job876_g4.sh) · 이날 쓴 `occ_run.sh` 는 `gate_q` · `gate_v` 를 넘기는 판 — **저장소에는 10-07 §4 에 `GVREF` 까지 더한 판([`2026-10-07/jobs/occ_run.sh`](../debug_log/2026-10-07/jobs/occ_run.sh), 커밋 1e3819e6)만 있음**(§5 모순 3) |
| 10-07 §1.0 | 시작 점검 — Jetson 재부팅으로 `/tmp` 비어 bag_step1 · 합성 스크립트 · 게이트 다시 올림(설치 sha 2cd52501 = 저장소). 재생 부하(사용자 '배속 가능?') | 5 개 동시 1 배속에 CPU ≈ 79 %(idle 21 %), python 15 개 각 19~22 % | 2 배속은 용량 초과 **추정** — best-effort 소실 · rf2o 프레임 간격 변화로 결과가 달라질 위험 | [`job902_load.sh`](../debug_log/2026-10-07/jobs/job902_load.sh)(출력 **원천 소실**) · `up901.sh` |
| 10-07 §1.1 | G4 결과 | 평균 \|오차\| **깨끗 2.0(+0.4) ✔ · A 1.9 ✔ · C 4.5 ✘ · D 7.3 ✘ · E 7.4 ✘**. 회전 중 표본 · σ 키움 · 버림: 깨끗 231 · 12 · 0 / A 228 · 12 · 0 / C 241 · 81 · 58 / D 242 · 28 · 145 / E 223 · 33 · 115. 회전 구간 차 합(T 대용 vs B): 깨끗 3 · A 3 → 4 · C 72 → 26 · D 64 → 17 · E 142 → 27 cm | 판정 1 **불합격**, 판정 2 **통과**, 오차 3~4 배 감소. 남은 것: D · E 는 **첫 회전(T 10 cm)을 B 가 1~2 cm 로 봄 = 버림의 비용**, C 는 **문턱 0.05 아래 오염**이 σ 키움만 받고 통과. 깨끗 +0.4 cm 가 G4 탓인지 재생 흔들림인지 모름(반복 재생 안 함). 해석(추정): 가린 동안 라이다엔 미끄러짐 정보가 없다 — 게이트는 덜 믿기까지만 | [`g4_eval.txt`](../debug_log/2026-10-07/outputs/g4_eval.txt) · [`j901_g4_progress.txt`](../debug_log/2026-10-07/outputs/j901_g4_progress.txt) · [`g4_eval.py`](../debug_log/2026-10-07/jobs/g4_eval.py) · [`g4_why.py`](../debug_log/2026-10-07/jobs/g4_why.py) |
| 10-07 §2.1 | rf2o + G4 켠 순회 prep(`rf2o:=true shadow:=true gate_v:=on`) | CPU 게이트 16.5 % · rf2o 4.4 % · EKF 13.3 / 10.8 %. /odom_rf2o **7.8 Hz**(설정 10) | 10-06 과 같은 수준. 7.8 Hz 는 확인 필요 | [`job903_prep_rf2o_g4.sh`](../debug_log/2026-10-07/jobs/job903_prep_rf2o_g4.sh) · [`j903_prep.txt`](../debug_log/2026-10-07/outputs/j903_prep.txt)(`v_mode on` 만) · [`job907_postchk.sh`](../debug_log/2026-10-07/jobs/job907_postchk.sh)(CPU · Hz 출력 **원천 소실**) |
| 10-07 §3.1 | rf2o 발행률 — bag 메시지 간격 | rf2o 원 **9.58 / 9.73 Hz**, 게이트 출력 9.51 / 9.62 Hz(f2c1 / f2c2) | prep 때 CLI 7.8 Hz 는 **측정 한계**(기동 직후 부하 + `ros2 topic hz`) | [`f2c_anal.txt`](../debug_log/2026-10-07/outputs/f2c_anal.txt) · [`f2c_anal.py`](../debug_log/2026-10-07/jobs/f2c_anal.py) · [`job913_extract.py`](../debug_log/2026-10-07/jobs/job913_extract.py) · bag `bag_f2c1.tgz` · `bag_f2c2.tgz` |
| 10-07 §3.2 | ③-c 게이트 비용(사람 없는 주행) | 회전 중 rf2o 원 → 통과: f2c1 298 → 291(**2.3 %** 버림) · f2c2 644 → 617(**4.2 %**). 회전 표본을 EKF B 전진 속도로 나누면 σ 키움 **제자리 11~17 % · 곡선 43~58 %**, 버림 곡선 1~6 %. 곡선 중 rf2o \|v\| 중앙 0.046 / 0.047 = EKF v 0.049 / 0.042 | ③-c ≤ 5 % **통과**. 그러나 **G4 설계 결함**: 10-06 합성은 제자리 회전만이라 정상 병진 ≈ 0 이었는데, 실제 순회의 회전은 대부분 0.04~0.08 m/s 로 전진하며 도는 곡선 → 정상 전진이 문턱 0.05 에 걸림. 곡선에선 휠 σ 가 작아 rf2o 몫이 원래 작다 → 정확도 영향은 작다고 **추정** | [`f2c_g4arc.txt`](../debug_log/2026-10-07/outputs/f2c_g4arc.txt) · [`f2c_g4arc.py`](../debug_log/2026-10-07/jobs/f2c_g4arc.py) · 첫 계산('버림 90 %', 짝짓기 시각 반올림)은 **원천 소실**(실수 5) |
| 10-07 §4 | G4 판정량 \|(bx, by)\| → **\|(bx − v_휠, by)\|**(`gate_vref:=wheel\|abs`, 기본 wheel). 확인 B = f2c2 bag 을 abs · wheel 로 동시 재생(도메인 91 · 92) | — | 선언 B-1(재현): abs 재생의 곡선 σ 키움 · 버림이 라이브와 ±10 %p. B-2(목표): wheel 곡선 합 ≤ 10 %, 제자리는 abs 와 ±10 %p. A: 10-06 합성을 wheel 로 ±0.5 cm | 커밋 1e3819e6 · [`rp_run.sh`](../debug_log/2026-10-07/jobs/rp_run.sh) · [`job915_rp.sh`](../debug_log/2026-10-07/jobs/job915_rp.sh) |
| 10-07 §4.1 | 결과(게이트 sha a474f584 = Jetson) | 곡선 σ 키움 · 버림 — 라이브 abs 43 % · 6 % / 재생 abs 34 % · 1 %(합 35 %) / **재생 wheel 2 % · 0 %(합 2 %)**. 제자리 재생 abs 합 12 % · wheel 6 %. 판정량 곡선 중앙 0.044 → 0.012 m/s. 재생 B − 라이브 B 최대 abs 1.3 · wheel 1.9 cm. 전체 G1 거부 abs 5 · wheel 40. A(오프라인): 10-06 보정 csv 에서 휠 \|vx\| 중앙 0.0005 · 최대 0.005 → 판정 바뀐 회전 표본 0~1 / ~220 | B-1 · B-2 **통과**. A 는 오프라인 동치 확인으로 대신(35 분 재생 생략 제안 — D 조건은 보정 csv 가 없어 같은 bag · 같은 휠 값으로 갈음). **G1 거부 5 vs 40 은 v_ref 와 무관한데 다름 — 재생 간 흔들림으로 추정, 미확인**. ⚠ B-1 의 라이브 쪽은 EKF B 속도로, 재생 쪽은 휠 속도로 나눈 값(§5 모순 2) | [`rp_eval.txt`](../debug_log/2026-10-07/outputs/rp_eval.txt) · [`j915_rp_progress.txt`](../debug_log/2026-10-07/outputs/j915_rp_progress.txt) · [`rp_eval.py`](../debug_log/2026-10-07/jobs/rp_eval.py) · [`g4ref_offline.txt`](../debug_log/2026-10-07/outputs/g4ref_offline.txt) · [`g4ref_offline.py`](../debug_log/2026-10-07/jobs/g4ref_offline.py) |
| 10-07 §6 · §6.1 | F2 재주행 준비 — G4 휠 잔차 기본 + MPPI transform_tolerance 0.5. 라이브 판정 'G4 곡선 ≤ 10 %' 선언 | prep 에서 게이트 `v_mode on` · **`v_ref wheel`** 확인 | 라이브 G4 곡선 비율은 f2d1 · f2d2 bag 으로 **집계 안 함**(선언만 있고 결과 없음 — §6 남은 것) | [`j918_prep.txt`](../debug_log/2026-10-07/outputs/j918_prep.txt) · `job918_prep.sh` · `job919_chk.sh` · `job920_chk.sh` |
| 10-08 §3 | 전역 nvblox B 구성 주행에서도 'rf2o · G4 잔차 · 그림자 A 그대로' | — | 게이트 자체는 바뀌지 않음(이 기간 끝) | [10-08 SUMMARY §3](../debug_log/2026-10-08/SUMMARY.md) · `job934_prep.sh` |

### 2.1 근거 발췌 (README §2.3 — 스크립트 핵심 · 나온 결과 · 경로)
**① 게이트 CPU 39 → 16 %** — 정지 10 s 동안 `/proc/<pid>/stat` 의 utime + stime 틱 차.
```bash
# Docs/debug_log/2026-10-06/jobs/job851_r3chk.sh 9~11 행
for p in rf2o_laser_odometry_node rf2o_gate.py ekf_shadow_a; do P=$(pgrep -f "$p" | head -1); [ -n "$P" ] && a=$(awk '{print $14+$15}' /proc/$P/stat); declare "c_$P=$a"; done
sleep 10
for p in ...; do ...; echo "  CPU $p: $(( (b - ${!v}) * 100 / 1000 )) %"; done   # 틱(1/100 s) 차 / 10 s → %
```
```
# outputs/j851_r3prep.txt (자이로 200 Hz 기준)       # outputs/j859_prep_people.txt (EKF ω 30 Hz)
  CPU rf2o_gate.py: 39 %                              CPU rf2o_gate.py: 16 %
```
(틱 → % 식은 `CLK_TCK = 100` 을 가정 — Jetson 값은 이 카드에서 미확인. `pgrep -f … | head -1` 은 같은 이름의 첫 프로세스를 잡는다 — §5.1 재생 때 이것이 다른 프로세스를 잡음.)

**② EKF 가 rf2o 를 믿는 몫(§6)** — 출력 원문이 없어 이 카드를 쓰며 같은 근사식으로 다시 셈: 몫 = (f_rf2o/σ_rf2o²) / (f_rf2o/σ_rf2o² + f_휠/σ_휠²), f_휠 25 · f_rf2o 10 Hz.
- 직진 vx: (10/0.10²) / (10/0.10² + 25/0.02²) = 1000 / 63 500 = **1.6 %** · vy: 11 111 / (11 111 + 250 000) = **4.3 %** · 제자리 회전: 11 111 / (11 111 + 25/0.3² = 278) = **97.6 %** · 틈(휠 B3 켜짐 · 게이트 직진 σ): 1000 / (1000 + 278) = **78 %**. SUMMARY 2 · 4 · 98 · 78 % 와 같다. σ 가 붙는 곳: `rf2o_gate.py` 135~136 행(`cv[0] = (sd_rot if rot else sd_vx)**2`), 휠은 `conditioner_core.hpp` 184 행.

**③ T1 · T1b — 정지 중 최대 이동**
```python
# Docs/debug_log/2026-10-06/jobs/t1_still.py 18~21 · 13~14 행
P0 = dict(P); D = {k: 0.0 for k in P0}
    for k in P0: D[k] = max(D[k], math.hypot(P[k][0] - P0[k][0], P[k][1] - P0[k][1]))
def cbr(m): v = math.hypot(m.twist.twist.linear.x, m.twist.twist.linear.y); ... F['over2'] += (v > 0.02)
```
```
# outputs/j863_t1b.txt
T1 결과 90 s: 끝 이동 B 0.000 · A 0.000 · rf2o 원 0.010 m | 최대 B 0.000 · A 0.000 · rf2o 원 0.018 m
  rf2o 원 속도: 표본 889, 최대 0.025 m/s, 0.02 넘음 1 | 게이트 통과분: 표본 878, 최대 0.016 m/s, 0.02 넘음 0
  게이트 누계 전: 통과 5924 · G1 거부 64 · G2 거부 11 → 후: 통과 7080 · G1 거부 64 · G2 거부 12
스캔 1263 개, 2 m 안 바뀐 점: 중앙 253 · 90% 477 · 최대 975
```

**④ T2 합성 판정** — 정지 구간(진실 대용 \|ω\| < 0.02 가 2 s 넘게) 끝 0.5 s 전 자세로 오른쪽 앞끝 대각 거리 − 줄자.
```python
# Docs/debug_log/2026-10-06/jobs/occ_scan.py 57~60 행 — 몸(원기둥)에 먼저 닿는 빔을 그 거리로
fx, fy = cx - ox, cy - oy; b = dx * fx + dy * fy; d2 = fx * fx + fy * fy - b * b
ok = (b > 0) & (d2 < self.br ** 2); t = b - np.sqrt(np.maximum(self.br ** 2 - d2, 0)); hit = np.where(ok & (t < hit), t, hit)
valid = np.isfinite(r) & (r > 0); occl = np.isfinite(hit) & (~valid | (hit < r))
# Docs/debug_log/2026-10-06/jobs/occm_eval.py 27 행
eB = [corner_d(at(B, s[1] - 0.5), at(B, t0)) - TAPE[k] for k, s in enumerate(keep[1:])]
```
```
# outputs/occm_eval.txt
가림 C_arc50_sway: 단계 6 | EKF B −줄자 +7.6 +3.9 +22.2 +6.5 +15.4 -1.4 | 평균 |오차| 9.5 · 원위치(2·4·6) +3.9 +6.5 -1.4 | (진실 대용 라이브 B 평균 1.5)
가림 D_arc30_inout: 단계 6 | EKF B −줄자 -8.5 +11.7 -26.5 +21.6 -40.1 +17.4 | 평균 |오차| 21.0 · ...
가림 E_arc50_fast: 단계 6 | EKF B −줄자 -19.0 +15.0 -4.2 +47.7 +29.6 +51.7 | 평균 |오차| 27.9 · ...
```

**⑤ G4 결과 · 남은 오차의 성격**
```python
# Docs/debug_log/2026-10-07/jobs/g4_why.py 10~15 행 — 진실 대용 T 의 |ω| > 0.1 구간(2 s 넘게)마다 T 이동 vs B 이동
rot = np.abs(w) > 0.1; edges = np.flatnonzero(np.diff(rot.astype(int)))
dT = at(T, e) - at(T, s); dB = at(B, e) - at(B, s); r.append((100 * np.linalg.norm(dT), 100 * np.linalg.norm(dB), 100 * np.linalg.norm(dB - dT)))
```
```
# outputs/g4_eval.txt
가림 D_inout: 단계 6 | EKF B −줄자 +1.3 -9.8 +1.1 -14.8 +3.3 -13.5 | 평균 |오차| 7.3 · ...
D_inout   판정 {'pass': 8547, 'g1': 16, 'g2': 10805, 'g4': 145} | 회전 중 표본 242 · σ 키움 28 · 버림 145
D_inout   끔: T10/B17/차8 T2/B16/차17 ... | 차 합 64 || 켬: T10/B1/차11 T2/B1/차1 ... | 차 합 17
```

**⑥ G4 곡선 오판 → 휠 잔차**
```python
# Docs/debug_log/2026-10-07/jobs/rp_eval.py 7~10 행
res = np.array([r['res'] for r in R]); vb = np.hypot(bx - vw, by) if ref == 'wheel' else np.hypot(bx, by)
rot = np.abs(w) > 0.15
for lab, sel in (('제자리(|v_휠|<0.03)', rot & (np.abs(vw) < 0.03)), ('곡선(|v_휠|≥0.03)', rot & (np.abs(vw) >= 0.03))):
    k = sel.sum(); soft = (sel & (res == 'pass') & (vb > 0.05)).sum(); rej = (sel & (res == 'g4')).sum()
```
```
# outputs/rp_eval.txt
abs   곡선(|v_휠|≥0.03)     표본 433 | 판정량 중앙 0.044 · 90 % 0.068 m/s | σ 키움 147 (34 %) · 버림  5 (1 %) | 합 35 %
wheel 곡선(|v_휠|≥0.03)     표본 431 | 판정량 중앙 0.012 · 90 % 0.042 m/s | σ 키움   8 (2 %) · 버림  1 (0 %) | 합 2 %
# outputs/f2c_g4arc.txt (라이브, abs)
f2c2 곡선(|v_B|≥0.03)     표본 505 | rf2o |v| 중앙 0.047 m/s · EKF v 중앙 0.042 | σ 키움 217 (43 %) · 버림 30 (6 %)
```

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 정식 노드 · launch 가 R2 원형과 같은 결과를 낸다 | 같은 bag 재생(§2) | 직진 0.998 · 안쪽 면 B 0.096(원형 0.099) | **지지(측정)** |
| 게이트 CPU 39 % 는 200 Hz 자이로 Python 콜백 탓 | 회전 기준만 30 Hz EKF ω 로 바꿔 같은 방식 측정(§9) | 39 → 16 % | **지지**(바꾼 것이 하나라 원인으로 볼 수 있음, 내부 분해는 안 함) |
| 회전 기준을 EKF ω 로 바꿔도 정확도가 같다 | bag_step1 재생 vs 라이브(§5.1) | 최대 0.7 cm | 지지(수치 **원천 소실**) |
| 정지 중 사람이 EKF 를 움직인다 | T1 · T1b | EKF 0.000 m(rf2o 원 최대 1.8 cm) | **기각**(정지 중엔 휠 가중 + G2) |
| 회전 중 정지한 몸 · 걸어 지나가는 다리는 EKF 를 흔든다 | T2 합성 0~72 % · A · B | 평균 ≤ 2.8 cm | **기각**(합성 한계: 원기둥 · 사인 운동) |
| 회전 중 크게 가린 채 움직이는 몸은 G1 이 막는다 | T2 C · D · E | 9.5~27.9 cm, G1 은 C · D 27 · 19 개만 | **기각** — 회전은 맞고 병진만 틀린 오염 |
| 스캔 겹침 q(G3)가 오염을 가른다 | 보정 재생 q 분포 | C 의 q 중앙 0.023 < 깨끗 0.048 | **기각** |
| 회전 중 병진 속도 범위(G4)가 오염을 막는다 | G4 재생 A/B | C · D · E 4.5 / 7.3 / 7.4(3~4 배 감소, 목표 3 미달) | **부분 지지** |
| G4 의 비용(깨끗 조건 악화)은 작다 | 같은 재생 | 깨끗 +0.4 · A −0.2 cm | 지지(반복 재생 없음 — 흔들림과 구분 못 함) |
| G4 남은 오차 = 버림의 비용 + 문턱 아래 오염 | 회전 구간별 T vs B(g4_why) | D · E 는 첫 회전 T 10 → B 1~2 cm, C 는 회전마다 3~6 cm | 지지(**측정**). '가린 동안 정보 없음' 은 **추정** |
| 순회(사람 없음)에서 G4 비용이 작다 | f2c bag 집계 | 버림 2.3 · 4.2 % ✔, 그러나 곡선 σ 키움 43~58 % | ③-c **통과**, 설계 결함 발견 |
| 판정량을 휠 잔차로 하면 곡선 오판이 사라지고 제자리 판정은 그대로 | f2c2 재생 abs · wheel + 10-06 csv 오프라인 | 곡선 35 → 2 %, 제자리 판정 바뀜 0~1 / ~220 | **지지** |

## 4. 조치와 효과
- **바뀐 코드**(기본은 전부 꺼짐 — `ekf.launch.py rf2o` 기본 false): 정식 게이트 노드 · launch 인자(4fdeeaaf), 회전 기준 EKF ω(10a93fa4, 기본 ekf), G3 · G4(404f81fe, 기본 off), G4 휠 잔차(1e3819e6, `gate_vref` 기본 wheel).
- **효과**: 게이트 CPU 39 → 16 %(라이브 정지). 합성 움직이는 큰 가림 9.5~27.9 → 4.5~7.4 cm(G4). 곡선 회전 오판 35 → 2 %(재생). 정지 중 사람 · 다리 · 정지한 몸은 원래 통과.
- **한계**: 움직이는 큰 가림은 목표 미달 — 게이트 밖 수단 후보(10-07 §1.1, 추정): ① 미끄러짐 자체 줄이기(피벗 회전 — 10-08 비율 시험은 근거 못 얻음, [rf2o 도입](rf2o-introduction.md) 이후 칸) ② '회전 중 rf2o 를 많이 버림' 을 신호로 회전 뒤 로컬 코스트맵 정리 ③ rf2o 입력에서 가까운 점 제외(합성 기하에 맞춘 꼴이 될 위험). 셋 다 이 기간에 안 함. 합성은 원기둥 · 사인 운동이고 진실 대용이 라이브 EKF B(줄자 대비 1.5 cm)다. 실제 사람 T2(회전 + 사람 줄자) · T3(주행 중 사람)는 미실행.

### 지금 코드에서 확인한 것 (11-02, 저장소 기준 — 코드는 바꾸지 않음)
- 판정 순서 [`rf2o_gate.py`](../../ros2_ws/src/rover_bringup/scripts/rf2o_gate.py) 125~129 행: G1 → G2 → G3(`q_mode on` 일 때만) → G4(G1~G3 통과분 중 \|ω̄\| > `rot_w` 0.15 이고 vb > `v_rej` 0.10). σ 키움은 139~140 행(`rot and vb > v_soft` 0.05 → 1 + 9 · min(1, (vb − 0.05)/0.05) 배, 분산은 그 제곱). 기본값: `gyro_source` ekf · 창 0.15 s(41~42), `q_mode` off(47), `v_mode` off(54), `v_ref` wheel(59).
- ⚠ 같은 파일 머리 주석 8 · 11 행은 아직 '입력 /imu/data' · '직전 0.1 s 자이로 평균' — 10-06 §5 이후 기본은 `/odometry/filtered` · 0.15 s(17~19 행 주석과 41~42 행 코드가 맞음). 문서 낡음, 동작 영향 없음.
- ⚠ 상수: `lidar_yaw` 기본 π − 0.04677(35 행) · G3 의 라이다 x 0.152(101 · 104 행)는 URDF 를 읽지 않는다 — `stuck_monitor.py` 32 행 `LIDAR_YAW` 와 같은 값. CLAUDE.md 하드웨어 요약의 '데크를 다시 조립하면 재측정' 문장은 stuck_monitor 만 적고 이 노드를 빼먹음([rf2o 도입](rf2o-introduction.md) §4 와 같은 지적).
- G4 의 v_휠(128 행)은 최신 `/wheel_odom` vx 하나(시각 맞춤 없음, 25 Hz 라 최대 약 40 ms 묵은 값) — 곡선에서 가속 중이면 잔차에 그 차가 섞인다(**추정**, 미측정).
- [`ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py): `rf2o` 기본 false(98), `gate_src` ekf(102) · `gate_q` off(103) · `gate_v` **off**(104) · `gate_vref` wheel(105). `rf2o or vslam ≠ off` 면 B3 를 σ 0.3 으로 강제(39~40). `conditioner:=py` + rf2o 거부(47~48). **`vslam:=on` 이면 rf2o:=true 여도 odom1 은 cuVSLAM**(53 행 `if rf2o and vslam != 'on'` — rf2o 노드 · 게이트도 안 뜸). `shadow` 는 rf2o 가 켜져야 유효(23).
- [`prep_patrol.sh`](../tools/prep_patrol.sh) 10 행 `ODOM` 기본 **vslam**, 12 행 `ODOM=rf2o` = `rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel` → **G4 는 launch 기본으로는 꺼져 있고 prep 의 rf2o 구성에서만 켜진다**.
- 휠 쪽 '순수 회전' 문턱 [`conditioner_core.hpp`](../../ros2_ws/src/rover_bringup/include/rover_bringup/conditioner_core.hpp) 43~44 행(`icr_v_max` 0.02 · `icr_w_min` 0.10) · 157~160 · 184 행, 회전 판정 ω 는 최근 0.1 s 자이로가 있으면 자이로 아니면 휠([`sensor_conditioner.cpp`](../../ros2_ws/src/rover_bringup/src/sensor_conditioner.cpp) 117~121 행). 게이트는 EKF ω · 0.15 — **§6 의 '문턱 불일치' 는 지금도 그대로**(rf2o 구성일 때).

## 5. 내 실수 · 모순
**실수 1 — 재생 정리를 이름으로 pkill(§5.1)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `r3_replay.sh` 로 bag_step1 을 ekf · imu 기준 두 번 재생해 정확도 · CPU 비교 |
| 본 것 | CPU 재생 수치 ekf 2100 s/300 s 등 비현실적 값, 뒤에 Jetson 에 EKF · 게이트 프로세스 없음 |
| 처음 추론 | (재생 CPU 를 판정에 쓰려 함) |
| 의심한 이유 | 누적 CPU 가 재생 길이보다 큼 · 라이브 스택 프로세스가 사라짐 |
| 판별 | 정리 줄 `pkill -f "ekf.launch.py"; … pkill -f ekf_node; pkill -f sensor_conditioner` 가 도메인과 무관하게 라이브(도메인 0) 프로세스까지 죽임, CPU `pgrep -f rf2o_gate.py \| head -1` 도 재생 것이 아닌 프로세스를 잡을 수 있음 |
| 결론 | CPU 재생 수치 **무효**, 주행 전 prep 필수. 고침: `LPID=$!` 로 launch 프로세스 그룹만 `kill -INT -- -$LPID`, CPU 도 `pgrep -g $LPID`. ⚠ **같은 정리 코드가 §2 재생(4fdeeaaf 판)에서도 돌았다** — 그때 라이브 EKF · 컨디셔너가 떠 있었다면 같이 꺼졌을 것(**추정** — §2 직후 §3 prep 이 다시 띄워 드러나지 않음, 그때 라이브 상태 기록 없음) |
| 다음에 알아보는 법 | 같은 기계에서 재생 · 라이브를 함께 돌리면 정리는 **PID · 프로세스 그룹으로만**. 정리 뒤 라이브 노드 수를 출력(10-06 §10.1 `occ_kill.sh` 마지막 줄이 그 형식) |
| 스크립트 핵심 | 첫 판(4fdeeaaf) `pkill -f "ekf.launch.py"; sleep 2; pkill -f rf2o_laser_odometry_node; pkill -f rf2o_gate.py; pkill -f ekf_node; pkill -f sensor_conditioner` → 고친 판(3e71a37d) `kill -INT -- -$LPID 2>/dev/null; sleep 3; kill -9 -- -$LPID` |
| 나온 결과 | 원천 소실(무효 수치는 SUMMARY §5.1 에만) |
| 데이터 | [`r3_replay.sh`](../debug_log/2026-10-06/jobs/r3_replay.sh)(지금 판 = 3e71a37d), 첫 판은 `git show 4fdeeaaf:Docs/debug_log/2026-10-06/jobs/r3_replay.sh` |

**실수 2 — 재생 제한 500 s < bag 2021 s(§5)**: 기록기가 저장 전에 끊겨 첫 검증 재생이 무효(정리 페이지 10-06: '3000 s 로 늘렸다'). `r3_replay.sh` 안의 시간은 bag 길이에서 계산하므로(6 행 `D = duration + 3`, 기록 `D + 6`) 500 s 는 바깥 실행 래퍼의 시간 한도(`run_jn.sh` 의 `JX_TIMEOUT`)였던 것으로 **추정** — §5 재생 래퍼는 저장소에 없음(같은 날 35 분 재생 래퍼 `run_x864.sh` · `run_x870.sh` 는 `JX_TIMEOUT=3000`). 알아보는 법: 바깥 시간 한도도 bag 길이에서 계산한다. 데이터: 원천 소실.

**실수 3 — 정수 매개를 DOUBLE 선언 노드에(§10.1 첫 시도)**: `coverage:=0` · `center_deg:=20` 을 넘겨 `occ_scan.py`(`declare_parameter('coverage', 0.5)` = DOUBLE)가 형 불일치로 안 뜸 + 이름 pkill 이 자기 ssh 명령까지 죽여 정리 실패. 고침: `0.0` · `20.0` 형태(`job864_occ.sh` 3 행 `for c in 0.0 0.15 …`), 정리는 [`occ_kill.sh`](../debug_log/2026-10-06/jobs/occ_kill.sh). 알아보는 법: rclpy 매개 선언 기본값의 형이 곧 형 — 명령줄 값에 소수점을 붙인다. 원천 소실(첫 시도 로그).

**실수 4 — q 를 쓰는 csv 줄이 편집에서 빠짐(§12)**: 첫 보정 재생은 q 미기록 → 재실행. 지금 판 `rf2o_gate.py` 66 · 131 행이 q 열을 씀. 알아보는 법: 새 열을 넣은 기록은 첫 몇 줄을 열어 열 개수부터 본다.

**실수 5 — 원 출력 · 게이트 출력 짝을 시각 반올림으로(10-07 §3.2)**: '버림 90 %' 로 잘못 셈 → 가장 가까운 수신 시각(30 ms 안)으로 다시. 근거 주석 [`f2c_g4arc.py`](../debug_log/2026-10-07/jobs/f2c_g4arc.py) 8~10 행. 알아보는 법: 같은 메시지를 다시 낸 두 토픽은 수신 시각이 수 ms 다르다 — 반올림 일치 대신 최근접 + 허용 폭. 첫 결과 원천 소실.

**실수 6 — 재생 B 와 라이브 B 를 원점 그대로 비교(10-07 §4, SUMMARY 에 없음)**: [`rp_eval.py`](../debug_log/2026-10-07/jobs/rp_eval.py) 14 행 주석 '첫 판은 원점 그대로 비교해 5.6 m 로 나옴' — 재생 EKF 는 bag 시작에서 원점, 라이브 B 는 이미 odom (−1.2, −5.5). 고친 판은 시작 자세에 맞춰 이동량끼리 비교(15~18 행). SUMMARY §4.1 은 고친 값(1.3 · 1.9 cm)만 적음 — 이 카드에서 코드 주석으로 찾음.

**실수 7 — G4 를 제자리 회전 합성만으로 설계(10-06 §12.1 → 10-07 §3.2)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 회전 중 rf2o 병진 \|v\| 의 물리 범위로 오염 판정(깨끗 90 % 0.037 · 최대 ≈ 0.1 m/s) |
| 본 것 | 실제 순회(f2c)에서 곡선 회전 표본 σ 키움 43~58 % |
| 처음 추론 | (10-07 §2 선언 ③-c 는 '버림 비율' 만 봄 — 2.3 · 4.2 % 로 통과) |
| 의심한 이유 | 같은 집계에서 σ 키움이 회전 표본의 절반, 곡선 중 rf2o \|v\| 중앙 0.046 = EKF 전진 속도 |
| 판별 | 회전 표본을 EKF B 전진 속도 0.03 기준으로 제자리 · 곡선 분리(`f2c_g4arc.py`) |
| 결론 | 보정 데이터(bag_step1)가 제자리 회전뿐이라 '정상 병진 ≈ 0' 을 가정한 판정량. 휠 잔차로 고침 |
| 다음에 알아보는 법 | 문턱을 정한 데이터의 **운동 범위**(제자리 · 곡선 · 직진)를 판정 대상 범위와 대조한다. 선언 지표에 '비율' 만 두지 말고 σ 키움 · 버림을 운동 종류별로 |
| 데이터 | [`f2c_g4arc.txt`](../debug_log/2026-10-07/outputs/f2c_g4arc.txt) · [`rp_eval.txt`](../debug_log/2026-10-07/outputs/rp_eval.txt) |

**모순 · 원문 대조(이 카드를 쓰며 찾은 것)**
1. 10-06 §2 '그림자 EKF A 도 라이브 기록과 일치': [`r3_eval.txt`](../debug_log/2026-10-06/outputs/r3_eval.txt) 는 중심 최대 A 0.129 · 라이브 0.128(같음), 직진 0.999 · 1.000(같음)이지만 **안쪽 면 범위 A 0.196 vs 라이브 0.130**, 범위 y A 0.150 vs 라이브 0.234 로 다르다. 10-02 R2 에서도 같은 차(0.198 vs 0.130)였고([rf2o 도입](rf2o-introduction.md) 모순 3), R3 가 그 차를 그대로 재현했을 뿐 원인은 **미확인**. 'B 가 A 의 절반' 은 재생 A 기준이다.
2. 10-07 §4.1 B-1 '재생이 라이브를 대표': 라이브 쪽([`f2c_g4arc.py`](../debug_log/2026-10-07/jobs/f2c_g4arc.py) 12~13 행)은 회전 표본을 **EKF B 전진 속도**로 나누고 σ 키움을 '게이트 출력 공분산 > 0.03² × 1.5' 로 세며, 재생 쪽([`rp_eval.py`](../debug_log/2026-10-07/jobs/rp_eval.py) 9~10 행)은 **휠 속도**로 나누고 '통과이며 판정량 > 0.05' 로 센다. 두 집계의 정의가 달라 34 vs 43 % 의 차(9 %p)에는 정의 차가 섞여 있다(얼마인지는 미확인). 정리 페이지 10-07 의 표 '라이브(예전 판정) 12 % · 49 %' 를 '같은 집계' 라 적은 것도 같은 이유로 엄밀하지 않다. 또 f2c_g4arc 의 '회전 중' 판정은 bag 의 EKF ω 보간이라 게이트 자신의 ω̄(0.15 s 평균)와 경계에서 다를 수 있고, 그때 게이트가 직진 σ(0.10²)를 붙인 표본도 'σ 키움' 으로 셀 수 있다(**추정**).
3. 10-06 §12 qcal · 10-07 §1 G4 재생에 쓴 `occ_run.sh` 판(`GQ` · `GV` 를 `gate_q` · `gate_v` 로 넘김)은 그날 커밋되지 않았다 — [`2026-10-06/jobs/occ_run.sh`](../debug_log/2026-10-06/jobs/occ_run.sh) 는 §10~§11 판(게이트 인자 없음, `gate_csv` 도 없음), 저장소의 [`2026-10-07/jobs/occ_run.sh`](../debug_log/2026-10-07/jobs/occ_run.sh)(1e3819e6)는 `GVREF`(기본 abs)까지 더한 판. 즉 §12 · 10-07 §1 을 낸 정확한 판은 **원천 소실**(10-07 판에서 `gate_vref` 를 뺀 것으로 **추정** — 그때 게이트엔 v_ref 가 없어 abs 동작).
4. `occ_eval.py` · `occm_eval.py` · `g4_eval.py` 22 행 주석 '회전량 85° 넘게 바뀐 경계만' — 코드 25 행은 `math.radians(60)`. 결과엔 영향 없음(단계가 ≈ 90° 라 둘 다 같은 경계).
5. 10-06 §11.1 표의 E 'G1 1698' 과 10-07 §1.1 E(G4 켬) csv 'g1 2030' · 로그 마지막 줄 'G1 1837' — G1 은 G4 보다 먼저 판정되므로 G4 켬/끔과 무관해야 한다. 차이는 30 s 로그 간격 · 재생 흔들림으로 **추정**(10-07 §4.1 G1 5 vs 40 과 같은 종류, 미확인). 1698 의 원문은 원천 소실.
6. 10-06 §9.2 '시야 ≈ 70 % 가림(사용자) · 최대 ≈ 54 %(측정)': 같은 지표가 사람이 발만 움직인 T1 에서도 스캔당 중앙 156 · 최대 1228 이다 — 첫 스캔 대비 '바뀐 점' 에 잡음 · 가장자리 점이 크게 섞여, T1b 의 975 / 1800 은 가림 비율로 읽기 어렵다(**추정**). 정리 페이지 10-06 머리의 '몸으로 시야 ≈ 54 % 가려도' 도 같은 주의가 필요.
7. 10-07 §2 선언 ③-d(주행 중 게이트 + rf2o + 그림자 CPU 기록)는 f2c 분석(§3)에 결과가 없다 — **미측정**.

## 6. 남은 것 (10-08 시점)
- 움직이는 큰 가림(C · D · E 4.5~7.4 cm) — 게이트 밖 수단(§4 한계) 미시도.
- 실제 사람 T2(회전 + 사람) · T3(주행 중 사람) — 미실행(10-07 f2c 는 '사람 없이').
- 연속 · 품질 σ(항목 C) — G3 기각 뒤 G4 로 대체, 연속 σ 자체는 미구현. 휠 · 게이트 문턱 불일치(0.10 vs 0.15) 그대로.
- 전선 시험 W · 기울기 감지 · TF 기울기(10-06 §7 · §8) — 미실행.
- 라이브 G4 곡선 비율(10-07 §6 선언) · 주행 중 게이트 CPU(③-d) — 미집계.
- G4 깨끗 조건 +0.4 cm 의 원인(반복 재생) · G1 거부 수 재생 간 차 — 미확인.
- 게이트 Python → C++ 이식(TODO(improve), CPU 16 %) — 안 함.

## 7. 이후 (10-12 ~)
- 포인터(앞 카드에 이미 적힌 것): 10-20 cuVSLAM 병진 속도 융합 · **10-23 §16 주 EKF 병진 = cuVSLAM**(rf2o 안 띄움), rf2o + G4 구성은 `ODOM=rf2o` 로 남음 — [rf2o 도입](rf2o-introduction.md) §7 · 본줄기 [cuVSLAM 병진 속도 융합](cuvslam-velocity-fusion.md).

### 7.1 8 기 (10-19 ~ 10-23) — 주행 중 실제 사람(계획 안 한 T3 꼴 관찰 2 건)과 rf2o 의 퇴장
10-19 ~ 10-22 의 주행은 모두 그때 prep 기본(`rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel`, 10-20 부터 + `vslam:=shadow`)이라 **주 EKF 는 rf2o + G4 휠 잔차** 였다. 이 기간에 사람이 주행 중에 낀 경우가 두 번 있었지만, 둘 다 선언한 T3 시험이 아니었고 게이트 판정 수(G1 · G2 · G4)나 rf2o 원 출력은 **분석하지 않았다** — 아래는 코스트맵 · 주행 결과 쪽 관찰뿐.

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 10-21 §10 | f2sm2 2 차(그림자 cuVSLAM 반복 주행) — 사용자: "사람들이 앞에서 길을 막으면서 주행을 일부러 방해했다" | 목표 1 SUCCEEDED 53.4 s · **목표 2(W3) ABORTED 74.9 s**(목표 대비 0.49 m). W3 목표 반경 0.6 m 안 라이다 점 t 120 · 125 s **101 · 128 개**(가장 가까운 0.20 m) → t 128 s 부터 **0** 인데 전역 LETHAL **38~40 칸**이 끝(t 141.6)까지 남음. 휠 25.8° vs EKF −18.5°(차 **44.3°** — f2sm1 11.3°), stuck 진단 2 | 반복 비교에서 제외 · **동적 물체 대응의 근거**로 사용(사용자). ① 사람이 있을 때 정지 · 재계획은 함(충돌 없음 — 사용자 확인 필요로 적힘) ② **사람이 떠난 뒤에도 기억이 목표 칸을 막아 목표를 포기** — 09-29 요구 '사람 다니는 실내에 강건' 에 어긋남 ③ 회전 차 44° = 막힌 곳에서 제자리 돌기 반복 탓(**추정**). 칸을 든 층은 nvblox 로 **추정**(층별 코스트맵이 bag 에 없어 미확인) | [`run_f2sm2.txt`](../debug_log/2026-10-21/outputs/run_f2sm2.txt) 19 · 24 행 · [`anal_goal_block_f2sm2.txt`](../debug_log/2026-10-21/outputs/anal_goal_block_f2sm2.txt) · [`chk_abort_f2sm2.txt`](../debug_log/2026-10-21/outputs/chk_abort_f2sm2.txt) · 영상 장면 [`f2sm2_frame_60.png`](../debug_log/2026-10-21/figures/f2sm2_frame_60.png) · [`f2sm2_frame_67.png`](../debug_log/2026-10-21/figures/f2sm2_frame_67.png) · bag `2026-10-21/bags/bag_f2sm2.tgz` |
| 10-21 §12.1 | W3 중단 → 복귀 안 한 이유 | `PathBlockedAhead (5.50~5.55, −2.20~−2.30) 비용 99 가 2.0 s 지속` 6 회 · `GridBased failed … tolerance 0.25` 2 회 · MonotoneEscape 2 회('최근접 14 cm, 성공') · Wait 5 s · `Goal failed` | 사람 기억(남은 칸) × PathBlockedAhead 가 목표점까지 검사 × 복구 클리어 `reset_distance 3.0` 이 로버 3 m 안은 안 지움 × 재시도 6 회 소진 — 넷이 겹침. 복귀 안 함 = 러너 설계(`job550_f0run.py` 176 행 실패 시 남은 목표 안 보냄) | [`nav_events_ms.txt`](../debug_log/2026-10-21/outputs/nav_events_ms.txt) · nav2 원 로그 **원천 소실**(10-21 §23) |
| 10-22 §2 · §4 | f2pr1(깊이 프리셋 시험 주행) — 사용자: "사람들이 돌아다니고 있다. 문제 발생시 여부 확인" | 3/3. 사용자 확인 "사람 장애물 문제 없었음". 누적 회전 휠 −79.5° vs EKF −161.7°(차 **82.2°**) | 비교용 유지. 회전 차 82° 가 사람 통행과 관련 있는지는 **미분석**(10-22 §3 이 그렇게 적음) | [10-22 SUMMARY §2 · §3 · §4](../debug_log/2026-10-22/SUMMARY.md) · bag `2026-10-22/bags/bag_f2pr1.tgz` |
| 10-23 §16 | 주 EKF 병진 = cuVSLAM(`prep_patrol.sh` 기본 `ODOM=vslam`) | — | rf2o 노드 · 게이트는 기본으로 안 뜸. 이 카드의 게이트 G1~G4 는 `ODOM=rf2o` 에서만 살아 있음 | [`prep_patrol.sh`](../tools/prep_patrol.sh) 10~14 행 · [cuVSLAM 카드](cuvslam-velocity-fusion.md) |

- 이 카드 질문에 대한 함의(**추정**): 실제 주행에서 사람 때문에 생긴 문제는 오도메트리(rf2o 오염)가 아니라 **코스트맵 기억**(사람이 떠난 자리를 막힌 칸으로 붙잡음) 쪽에서 먼저 드러났다. 그러나 f2sm2 의 회전 차 44° · f2pr1 의 82° 가 게이트를 통과한 rf2o 오염과 관련 있는지는 게이트 csv 를 안 남겨(`gate_csv` 빈 값) **판정할 수 없다**.
- 같은 질문을 cuVSLAM 에 다시: 사람이 시야를 크게 가릴 때 cuVSLAM 병진 속도가 어떻게 되는지는 이 기간에 측정 없음(09-29 정지 중 사람 걸음 1.10 cm 만 — [Isaac 평가 카드](isaac-cuvslam-evaluation.md)). 사람 기억이 목표 칸을 막는 문제는 10-22 §21 '미뤄 둔 것' 5 에 남음.
- 남은 것(10-23 시점): T3(선언한 주행 중 사람 시험) — 여전히 미실행. '사람이 떠난 뒤 기억' 대책 — 미결정. 게이트 판정 수를 주행마다 남기는 것(`gate_csv`) — rf2o 가 기본에서 빠져 필요성 낮아짐.
- 이후(10-26 ~): 다음 시기에서 채움.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| R3 재생 | 정식 launch 로 f2b3 · f2b4 | `2026-10-06/outputs/r3_eval.txt` · `j850_r3_replay.txt` |
| R3 정지 | 라이브 발행률 · 게이트 · CPU 39 % | `2026-10-06/outputs/j851_r3prep.txt` |
| CPU 판정 | gyro_source ekf, 16 % | `2026-10-06/outputs/j859_prep_people.txt` |
| T1 · T1b | 정지 + 사람 | `2026-10-06/outputs/j860_t1.txt` · `j863_t1b.txt` · bag `2026-10-06/bags/bag_t1.tgz` · `bag_t1b.tgz`(로컬) |
| T2 합성 정지 몸 | 가림 0~72 %, 도메인 51~55 | `2026-10-06/outputs/occ_eval.txt` |
| T2 합성 움직이는 몸 | A~E, 도메인 61~65 | `2026-10-06/outputs/occm_eval.txt` |
| G3 보정(qcal) | q · \|v\| 분포, 도메인 71~75 | 그림 `Docs/04_navigation/figures/2026-10-06_gate_quality.png`(csv 원천 소실) |
| G4 재생 | 5 조건, 도메인 81~85 | `2026-10-07/outputs/g4_eval.txt` · `j901_g4_progress.txt` |
| f2c ③-c | 순회 게이트 비용 · 곡선 오판 | `2026-10-07/outputs/f2c_anal.txt` · `f2c_g4arc.txt` · bag `2026-10-07/bags/bag_f2c1.tgz` · `bag_f2c2.tgz` |
| G4 잔차 재생 | f2c2 abs · wheel, 도메인 91 · 92 | `2026-10-07/outputs/rp_eval.txt` · `j915_rp_progress.txt` · `g4ref_offline.txt` |
| 그림 | 합성 결과 · 게이트 품질 | `Docs/04_navigation/figures/2026-10-06_occ_results.png` · `2026-10-06_gate_quality.png` · 정리 페이지 `2026-10-06/2026-10-06_report.html` · `2026-10-07/2026-10-07_report.html` |
| 도구 | 아래 §9 | `2026-10-06/jobs/` · `2026-10-07/jobs/` · `ros2_ws/src/rover_bringup/` |

## 9. 도구 해설
공통: 재생은 Jetson 에서 **도메인을 시험마다 따로**(42 · 51~55 · 61~65 · 71~75 · 81~85 · 91 · 92) · `use_sim_time` · `fastdds_udp_only.xml` · `ros2 bag play --clock 100`. 여러 도메인을 동시에 돌리면 각자 `/clock` 을 가진다. 시험받는 EKF 는 매번 새로 띄운 `ekf.launch.py rf2o:=true use_sim_time:=true`(컨디셔너 포함 — 원시 IMU 가 없어 `/imu/data` 는 bag 것을 쓰고 휠 B3 공분산만 냄). 진실 대용 = bag 의 라이브 EKF B(`/odometry/filtered` → `/truth_odom` 으로 이름 바꿔 재생, 줄자 대비 1.5 cm). npz · csv 는 Jetson `/tmp` → PC 스크래치패드 `f2a6/` · `occ/` · `qcal/` · `g4/` · `rp/` 로 옮겨 분석했고 **지금은 모두 소실** — bag(`bag_step1.tgz` · `bag_f2c2.tgz` 등)과 스크립트는 남아 있어 다시 만들 수 있다.

### rf2o_gate.py — 게이트 노드 (Jetson, rclpy) — 판별 계보
- 부른 형태: `ekf.launch.py rf2o:=true [shadow:=true] [gate_csv:=…] [gate_src:=ekf|imu] [gate_q:=off|log|on] [gate_v:=off|on] [gate_vref:=wheel|abs]` 가 매개로 넘김(지금 62~66 행).
- 왜: 10-02 R2 의 오프라인 원형(`r2_gate.py`, 휠 중계 겸함)을 라이브 스택에 넣기 위해.
- 하는 일(지금 판, rf2o 메시지마다 — [rf2o 도입](rf2o-introduction.md) §4 '게이트가 하는 일' 1~8 단계와 같음): 좌표 R(π − 0.04677) → 창 평균 ω̄ → G1 \|ω_rf2o − ω̄\| > max(0.12, 0.3\|ω̄\|) → G2 휠 \|vx\| < 0.005 · \|ω̄\| < 0.02 · \|(bx, by)\| > 0.02 → G3(on 일 때) q > 0.30 → G4(on 일 때) \|ω̄\| > 0.15 · vb > 0.10 → 통과분에 σ(회전 0.03 / 그 밖 vx 0.10 · vy 0.03, yaw 분산 1e3) · q 0.15~0.30 또는 vb 0.05~0.10 이면 σ 1~10 배 → `/odom_rf2o/gated`. 30 s 마다 'rf2o 게이트 통과 … G4 거부' 로그(지금 76 행), csv 한 줄씩(`t,w_rf2o,w_gyro,v_wheel,bx,by,q,res`). `relay_plain`(shadow)이면 휠을 고정 공분산(vx 0.02² · vy 0.01² · vyaw 0.1²)으로 `/wheel_odom/plain` 에 중계.
- 판별 차이:
  - **4fdeeaaf(10-06 §1~§4)**: `/imu/data` 200 Hz 구독, 창 0.1 s, deque 400, G1 · G2 만, csv 열에 q 없음(`t,w_rf2o,w_gyro,v_wheel,bx,by,res`). 원형과 차이 = 휠 중계를 shadow 때만 · G2 · σ 판단에 최신값 대신 창 평균.
  - **10a93fa4(§5)**: `gyro_source`(기본 ekf, `/odometry/filtered` ω 30 Hz) · 창 ekf 0.15 s / imu 0.1 s · deque 100.
  - **404f81fe(§12)**: G3 `quality()`(직전 · 이번 스캔, 거리 0.2~4.0 m · 빔 절반 · 라이다 x 0.152 · 유효 점 100 미만이면 판단 불가 · 어긋남 허용 `q_tol` 0.05) · G4(abs 판정량) · csv q 열 · 로그에 G3 · G4.
  - **1e3819e6(10-07 §4)**: `v_ref`(기본 wheel) — vb = \|(bx − v_휠, by)\|.
- 출력이 남은 곳: 라이브 로그 줄은 각 prep 출력(`j851` · `j859` · `j903` · `j918`), 재생 로그는 `j850` · `occ_eval.txt`(정지 몸) · `g4_eval.txt` · `j901` · `j915`. csv 는 모두 원천 소실.
- 결함: 상수(라이다 yaw · x) 하드코딩, 머리 주석 낡음(§4 '지금 코드'), Python(16 %). G1 은 '회전도 같이 틀어지는 오염' 만 잡는다(§11.1).
- 지금 다시: `ODOM=rf2o` prep 으로 그대로 쓸 수 있음(G4 on · wheel).

### ekf.launch.py 의 rf2o 묶음 (Jetson)
- 4fdeeaaf: `rf2o` · `shadow` · `use_sim_time` · `gate_csv` 인자, `rf2o` 면 B3 강제 σ 0.3 · EKF odom1(vx · vy 만, `differential false`) · rf2o 노드(`rf2o.yaml`) · 게이트 · (shadow) 그림자 EKF A(`ekf.yaml` 을 읽어 `publish_tf false` · `odom0 = /wheel_odom/plain`, 출력 `/odometry/ekf_a`). 10a93fa4 `gate_src`, 404f81fe `gate_q` · `gate_v`, 1e3819e6 `gate_vref`. 이후 10-20 `vslam` 이 같은 파일에 들어옴(§4 '지금 코드').

### r3_replay.sh · r3_rec.py · r3_eval.py — R3 재생 검증 (Jetson · PC)
- 부른 형태: `bash r3_replay.sh /tmp/bag_f2b3 /tmp/r3_f2b3.npz [ekf|imu]`(f2b4 도). 배포 · bag 풀기는 [`job850_deploy.sh`](../debug_log/2026-10-06/jobs/job850_deploy.sh)(rover_bringup 4 파일 복사 → `colcon build --packages-select rover_bringup` → 설치 링크 확인 → `/tmp/bag_f2b3` · `f2b4` 풀기), 실행 래퍼 `run_x850.sh`.
- 하는 일(sh): bag 길이 + 3 s → `setsid ros2 launch … rf2o:=true shadow:=true use_sim_time:=true gate_csv:=… gate_src:=…` → 6 s 뒤 `r3_rec.py`(길이 + 6 s) → `ros2 bag play --clock 100 --topics /scan /tf_static /imu/data /wheel_odom` → 게이트 CPU 누적(`ps -o times`) · 마지막 게이트 로그 · 정리(실수 1 전후 판) · 오류 grep. `/tf` 는 재생하지 않음 — bag 의 map · odom 은 r3_eval 이 10-02 의 `r2_*.npz` 에서 가져옴.
- 하는 일(r3_rec): sim time 노드로 `/odometry/filtered`(B) · `/odometry/ekf_a`(A) 자세 → npz.
- 하는 일(r3_eval, PC): 10-02 `r2_eval.py` 의 R2-b · R2-c 계산을 그대로, A · B 만 R3 npz 로 바꿈 — **R3-b** f2b4 3 s 창 중 라이브 \|Δyaw\| < 3° · 이동 > 0.15 m 인 창의 이동 / map 이동 중앙 · **R3-c** f2b3 13:25:30 + 26~49 s 서쪽 구조물(map y −5.95~−5.35 · x −2.1~−1.6) 점을 각 EKF 자세로 odom 에 놓아 중심 흔들림 · 안쪽 면(x 95 백분위) 범위. R2-a(rot3 줄자)는 bag 소실로 없음.
- 출력: [`r3_eval.txt`](../debug_log/2026-10-06/outputs/r3_eval.txt) · [`j850_r3_replay.txt`](../debug_log/2026-10-06/outputs/j850_r3_replay.txt)(f2b3 판 한 번 분량). 쓰인 곳 §2 · §5.1. 결함: 실수 1, 입력 npz 원천 소실. 지금 다시: 10-02 npz 가 없어 r3_eval 은 그대로 못 돌림(bag 에서 다시 추출해야 함).

### job851_r3chk.sh · job852_prep_rf2o.sh — 라이브 정지 확인 (Jetson)
- 852: `EXTRA_SENSORS="rf2o:=true shadow:=true"` 로 `job780_prep_navmap.sh`(그때 prep, 10-12 뒤 `Docs/tools/prep_fast.sh` 계열로 대체) 실행 뒤 sensors 인자 줄 확인.
- 851: rf2o · 게이트 · ekf · 컨디셔너 프로세스 수 → 5 토픽 `ros2 topic hz` 6 s → `rot_cov_enable` · `rot_vx_var` · EKF `odom1` 매개 → 마지막 게이트 로그 → CPU 10 s(§2.1 ①) → map→base 위치 · load. 출력은 prep 출력 파일 끝에 붙음([`j851_r3prep.txt`](../debug_log/2026-10-06/outputs/j851_r3prep.txt) · [`j859_prep_people.txt`](../debug_log/2026-10-06/outputs/j859_prep_people.txt)). 결함: `ros2 topic hz` 는 기동 직후 부하에서 낮게 나올 수 있음(10-07 §3.1 의 7.8 vs 9.7 Hz). 지금은 `chk_prep.py` 가 매개 확인을 맡음(10-27).

### t1_still.py · job860_t1.sh · job862_t1b_start.sh — T1 · T1b (Jetson, 로버 정지)
- 부른 형태: `python3 t1_still.py 60`(T1) · `90`(T1b — job862 가 백그라운드로 돌리고 6 s 뒤 시작 알림, 사용자가 그 뒤 가림).
- 하는 일: `/odometry/filtered`(B) · `/odometry/ekf_a`(A) · `/odom_rf2o`(원 자세) 의 첫 위치를 기준으로 SEC 동안 최대 · 끝 이동, `/odom_rf2o` · `/odom_rf2o/gated` 속도 최대 · 0.02 m/s 넘는 표본 수. 래퍼는 시작 전 · 끝 31 s 뒤 `/tmp/sensors.log` 의 게이트 누계 줄을 잡아 차를 보게 하고(30 s 로그 간격을 넘기려 31 s 대기), bag(`/scan /tf /tf_static /imu/data /wheel_odom /odom_rf2o /odom_rf2o/gated /odometry/filtered /odometry/ekf_a`)을 기록 · tgz.
- 판정 문턱: EKF B 최대 이동 ≤ 2 cm(§9 선언). 출력 [`j860_t1.txt`](../debug_log/2026-10-06/outputs/j860_t1.txt) · [`j863_t1b.txt`](../debug_log/2026-10-06/outputs/j863_t1b.txt). 결함: rf2o 원 '자세' 이동은 라이다 위치 · 부호 반대 좌표라 크기만 의미. 지금 다시: bag 이 있어 오프라인 재분석 가능.

### job861_t1scan.py · job863_t1bscan.py — 사람이 스캔에 보였나 (Jetson, bag 읽기)
- 하는 일: bag 의 `/scan` 첫 스캔을 기준으로, 이후 스캔마다 '0.2~2.0 m 안(이번 또는 기준)' 이고 거리 차 > 0.05 m 인 빔 수와 그 각도(차체 기준, + π − 0.04677). 20 개 넘는 스캔의 각도 5~95 백분위.
- 출력: 861 은 **원천 소실**, 863 은 `j863_t1b.txt` 끝 두 줄. 결함: 첫 스캔 대비라 잡음 · 가장자리 점이 섞여 가림 비율이 아니다(§5 모순 6) — 같은 자리 무인 기준선(빈 장면)을 따로 재야 비교 가능.

### occ_scan.py — 합성 몸 그리기 (Jetson, rclpy)
- 부른 형태: `occ_scan.py --ros-args -p use_sim_time:=true -p coverage:=0.5 -p center_deg:=20.0 -p rho:=0.6 [-p amp:=… -p period:=… -p move_deg:=… -p legs:=true]`.
- 하는 일: `/truth_odom` 첫 자세에서 시작 자세 기준 몸 위치를 odom 에 고정 — 정지 몸 = 반경 `body_r` 0.08 원기둥을 중심 `center_deg` · 거리 `rho` 호 위에 `n = int(360° · coverage · rho / (1.6 · 0.08))` 개(26 행), 다리 = 반경 0.06 두 개 간격 0.2 m(28~29 행). 움직임 = 기준 + `amp · sin(2πt/period)` · 방향 `move_deg`(최고 속도 amp · 2π/period — A 0.52 · B 0.47 · C 0.24 · D 0.42 · E 0.63 m/s). `/scan_in` 마다 라이다 위치(중심 앞 0.152)에서 빔과 원의 교점 거리를 구해 원래 거리보다 가깝거나 원래 빔이 무효면 바꿔 `/scan` 으로(57~61 행), 가린 빔 비율을 60 s 마다 로그.
- 계보: a8b61aa1(정지 몸) → 9c5c03be(움직임 · 다리). 결함: 몸이 rf2o 에 '정합 특징' 이 될 수 있음(72 % 결과), 사람 모양 · 움직임은 근거 없는 모형, 진실 대용 자세로 그리므로 그 오차(1.5 cm)만큼 몸이 같이 움직임.

### occ_run.sh · occ_rec.py · job864_occ.sh · job870_occmove.sh · job871_qcal.sh · job876_g4.sh · occ_kill.sh — 합성 재생 묶음 (Jetson)
- occ_run: `DOMAIN COVERAGE OUT [CENTER_DEG RHO EXTRA]` → 시험 EKF launch · occ_scan · occ_rec(sim time, `/odometry/filtered` B · `/truth_odom` T · `/cmd_vel`) → `ros2 bag play /tmp/bag_step1 --clock 100 --topics /scan /tf_static /imu/data /wheel_odom /odometry/filtered /cmd_vel --remap /scan:=/scan_in /odometry/filtered:=/truth_odom` → '도메인 … 게이트 통과 … | 가린 빔 비율' 한 줄 → 프로세스 그룹 정리. 판별: §10~§11 판(게이트 인자 없음) / §12 · 10-07 §1 판(`GQ` · `GV` → `gate_q` · `gate_v`, `gate_csv` — **원천 소실**, §5 모순 3) / 10-07 §4 판(+ `GVREF` 기본 abs).
- 864: 가림 0.0 · 0.15 · 0.3 · 0.5 · 0.7 를 도메인 51~55 동시. 870: A~E 를 61~65 동시(매개는 파일 안). 871: `GQ=log` 로 clean · static50 · A · C · E 를 71~75. 876: `GV=on GQ=off` 로 clean · A · C · D · E 를 81~85, 1 분마다 진행 줄(사용자 요청 — `j901_g4_progress.txt`). occ_kill: `ps` 로 시험 프로세스만 골라 그 프로세스 그룹에 INT → 남으면 KILL → '남은 시험 프로세스 · 라이브 ekf · 게이트' 수 출력.
- 시간: bag_step1 2021 s 를 1 배속 — 한 묶음 약 35 분(5 개 동시 CPU ≈ 79 %, 10-07 §1.0). 결함: 870 의 G1 · G2 줄은 파일로 안 남김(원천 소실).

### occ_eval.py · occm_eval.py · g4_eval.py — 합성 판정 (PC)
- 하는 일: npz 의 T(진실 대용) yaw 미분 \|ω\| < 0.02 가 2 s 넘는 정지 구간을 찾고, 직전 남긴 구간과 yaw 가 60° 넘게 다른 것만 남겨 시작 + 6 단계 = 7 개 → 각 정지 끝 0.5 s 전 B · T 자세로 오른쪽 앞끝(+0.262, −0.165)의 시작 대비 대각 거리 − 줄자 `TAPE` = [44.8, 10.8, 43.3, 16.1, 43.5, 17.6] cm. g4_eval 은 추가로 게이트 csv 의 회전 중(\|w_gyro\| > 0.15) 표본에서 '통과이면서 0.05 < \|(bx, by)\| ≤ 0.10' 을 σ 키움, `g4` 를 버림으로 셈(abs 판정량).
- 출력 [`occ_eval.txt`](../debug_log/2026-10-06/outputs/occ_eval.txt) · [`occm_eval.txt`](../debug_log/2026-10-06/outputs/occm_eval.txt) · [`g4_eval.txt`](../debug_log/2026-10-07/outputs/g4_eval.txt). 결함: 주석 85° vs 코드 60°(모순 4), 진실 대용 자체 오차 1.5 cm, 평균 \|오차\| 는 홀수 단계의 −2.3~−2.9 cm 치우침(10-06 §4.1, 원인 미분리)을 포함 — 3 cm 판정이 그 치우침 위에 얹혀 있음.

### g4_why.py — 남은 오차 분해 (PC)
- 하는 일: T 의 \|ω\| > 0.1 구간(2 s 넘게, 처음 6 개)마다 T 이동 · B 이동 · 차의 크기(cm)를 G4 끔(`occ/occm_*.npz`) · 켬(`g4/g4_*.npz`)으로. clean 은 '끔' 파일 이름이 없어(`'X'`) 켬만. 출력 `g4_eval.txt` 끝 5 줄. 판정 근거: '\|B\| < \|T\| 이고 방향 같음 = 버림 비용, 방향 다름 = 걸러지지 않은 오염'(주석) — 방향은 출력하지 않고 크기만이라 그 구분은 수치로 남지 않음.

### render_day1006.py — 하루 그림 (PC, matplotlib)
- ① `occ_results.png` — 합성 10 조건 평균 \|오차\|(값은 코드 안에 손으로 옮긴 상수 7~10 행) · 원위치 단계 오차(symlog) ② `gate_quality.png` — qcal csv 의 회전 중 \|v\| · q 누적 분포(G4 문턱 0.05 · 0.10 점선). csv 원천 소실이라 ② 는 다시 못 그림.

### job902_load.sh — 재생 부하 (Jetson, 읽기만)
- `top -b -n 2 -d 3` 두 번째 화면의 요약 3 줄 · CPU 상위 14 프로세스 · 도메인 81 · 85 게이트 줄. 출력 원천 소실(SUMMARY §1.0 의 79 % · 19~22 % 에만).

### f2c_g4arc.py · f2c_anal.py · job913_extract.py — 순회 게이트 비용 (Jetson 추출 · PC 분석)
- 913: bag 에서 `/tf`(map→odom · odom→base) · `/odometry/ekf_a` · `/odometry/filtered` 속도 · `/odom_rf2o` · `/odom_rf2o/gated`(+ 공분산 [0] · [7]) · `/cmd_vel` · `/plan` 길이를 수신 시각으로 npz(`x913_f2c{1,2}.npz`, 원천 소실). 래퍼 `job913_run.sh`.
- f2c_anal(③-c 부분): 원 · 게이트 각 메시지 시각의 EKF ω 보간 \|ω\| > 0.15 를 회전으로, '버림 = 회전 중 원 수 − 회전 중 통과 수'(G1 · G2 · G4 모두 포함), σ 키움 = 공분산 [0] > 0.03² × 1.5. 발행률 = 메시지 수 / 길이. ③-b · map→odom 부분은 [rf2o 도입](rf2o-introduction.md) §9.
- f2c_g4arc: 원 rf2o 를 차체 속도로 돌려 \|v\|, 각 원 메시지에 30 ms 안 최근접 게이트 메시지를 짝지어 통과 · 공분산, EKF B 전진 속도 \|v\| < 0.03 이면 제자리 · 아니면 곡선. 출력 [`f2c_g4arc.txt`](../debug_log/2026-10-07/outputs/f2c_g4arc.txt). 결함: §5 모순 2.

### rp_run.sh · job915_rp.sh · rp_eval.py · g4ref_offline.py — 휠 잔차 확인 (Jetson · PC)
- rp_run: `DOMAIN BAG OUT`, 환경 `GV`(기본 on) · `GVREF`(기본 wheel) → 시험 EKF launch(`gate_csv` 포함) · occ_rec · 주행 bag 재생(가림 합성 없음, 라이브 B 를 `/truth_odom` 으로). 915: abs 를 91, wheel 을 92 에 동시, 1 분 진행 줄(`j915_rp_progress.txt`).
- rp_eval: §2.1 ⑥ 의 집계 + 전체 판정 수 + 재생 B 와 라이브 B 를 시작 + 1 s 자세에 맞춰 이동량끼리 비교(실수 6 뒤 판). 출력 [`rp_eval.txt`](../debug_log/2026-10-07/outputs/rp_eval.txt).
- g4ref_offline: 10-06 qcal csv(제자리 회전 합성 5 조건)에서 회전 표본마다 abs · wheel 판정량의 σ 배수(> 0.10 = 버림 ∞, 0.05~0.10 = 1~10 배)를 계산해 '버림 ↔ 통과가 바뀜 또는 배수 차 ≥ 0.5' 수. 출력 [`g4ref_offline.txt`](../debug_log/2026-10-07/outputs/g4ref_offline.txt). 결함: 입력 qcal csv 가 그때 스크래치에 있었고 지금 원천 소실 — D 조건은 qcal 에 없어 판단에서 빠짐.

## 10. 용어
- **G1 자이로 일치**: rf2o 가 낸 회전 속도와 자이로(지금은 EKF ω) 평균의 차가 크면 그 rf2o 측정 전체를 버림. 움직이는 물체가 회전 추정까지 틀어지게 할 때만 잡힌다.
- **G2 정지 검사**: 휠 · 회전이 0 근처인데 rf2o 가 움직였다고 하면 버림. 정지 중 사람 · 가림에 강하다(T1b · 합성의 정지 구간 수천 건).
- **G3 스캔 겹침 품질 q**: 직전 스캔을 rf2o 가 말한 움직임으로 옮겨 이번 스캔과 겹쳤을 때 어긋난 점 비율. 프레임 간 비교라 천천히 움직이는 몸을 못 가른다(기각).
- **G4 회전 중 병진 타당성**: 회전 중 rf2o 병진 속도가 물리적으로 그럴듯한 범위(실제 미끄러짐은 대부분 < 0.05 m/s)를 넘으면 σ 를 키우거나 버림. 10-07 부터 판정량은 '휠이 본 전진을 뺀 나머지'(휠 잔차).
- **σ 키움(soft)**: 측정을 버리지 않고 공분산을 키워 EKF 가 덜 믿게 하는 것. 1~10 배 σ = 1~100 배 분산.
- **실효 몫(근사)**: 두 센서가 같은 상태를 잴 때 EKF 가 각각을 따르는 비율을 1/σ² × 발행률로 어림한 값. 과정 잡음 · 상태 확신을 무시한 근사라 방향만 본다.
- **진실 대용(truth proxy)**: 합성 재생에서 '정답' 으로 쓴 bag 의 라이브 EKF B 자세. 줄자 대비 1.5 cm 라 그보다 작은 차는 가를 수 없다.
- **합성 가림**: 실제 bag 의 라이다 스캔에 가상의 몸(원기둥)을 그려 넣어 같은 회전 · 같은 줄자 정답으로 오염 조건만 바꿔 보는 방법.
- **제자리 회전 vs 곡선 회전**: 휠 전진 속도 < 0.03 m/s 로 도는 것 vs 0.04~0.08 m/s 로 전진하며 도는 것. 실제 순회는 곡선이 대부분(f2c2 회전 표본 505 중 곡선, 제자리 139).
