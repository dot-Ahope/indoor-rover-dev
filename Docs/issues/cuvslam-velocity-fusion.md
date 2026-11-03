# cuVSLAM 병진 속도 융합 — 회전 미끄러짐 · 오프라인 → 그림자 → 기본 채택 (8 기: 10-19 §23 · 10-20 §1 · §3 ~ §6.4 · §9.6 · §9.7 · 10-21 §7 ~ §12.2 · 10-22 §19 · §20 · 10-23 §9 · §10 ~ §11.1 · §16)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **부분 해결(운용 채택)** — 10-23 §16 사용자 결정으로 주 EKF 병진 속도 = cuVSLAM(`prep_patrol.sh` 기본 `ODOM=vslam`). 같은 주행 안 비교(그림자 EKF 대 주 EKF, SLAM 기준 10 s 창)에서 W3 되돌아 회전 최대 창 **−20 %**(f2v1, UDP 로 입력이 빠짐) · **−33 · −41 · −31 · −33 %**(SHM, f2sm1 · f2sm3 · f2pa1 · f2pa2) **측정**. 주 EKF 에 넣은 두 주행(f2von1 · f2von2)은 W3 창 16.8 · 13.2 cm(**측정**, 다른 주행과의 비교). yaw 속도만 넣는 것은 효과 없음(재실행 **측정**). **미끄러짐 자체는 남고**(cuVSLAM 단독 8.7~13.3 cm 아래로 못 내려감), **상자 옆 여유에는 효과 없음**(상자 옆 10 s 창 재실행 −0.3 ~ +1.4 · 그림자 −0.2 ~ +1.5 cm, on 주행 실제 여유 3.3 · 0.3 cm) | 10-19 §23 ~ 10-23 §16 (그 뒤는 §7 '이후') | [10-19 §23](../debug_log/2026-10-19/SUMMARY.md) 사용자 "오프라인 cuVSLAM 비교 진행하라" — 09-29 방향 D(영상 · 라이다 오도메트리 속도를 odom EKF 에, [Isaac · cuVSLAM 평가](isaac-cuvslam-evaluation.md))와 10-20 §1 후보 (C)('cuVSLAM 을 twist 로만 융합해 회전 중 미끄러짐을 잡기')의 실행 | [`ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py) `vslam:=off\|shadow\|on`(커밋 `1269e3e5`, 지금 24~31 · 39~40 · 51~53 · 69~82 · 109~110 행) · 새 [`cuvslam_container.launch.py`](../../ros2_ws/src/rover_bringup/launch/cuvslam_container.launch.py) · [`cuvslam_up.sh`](../../ros2_ws/src/rover_bringup/scripts/cuvslam_up.sh) · [`vslam_twist.py`](../../ros2_ws/src/rover_bringup/scripts/vslam_twist.py) · `CMakeLists.txt` 39 행 install · [`prep_fast.sh`](../tools/prep_fast.sh) 24 행 정리 목록 · 38~39 행 컨테이너 고아 정리 · 73 행 상태 줄 · `dds_shm:=`(커밋 `8e31e2b1` — [카메라 ↔ 컨테이너 SHM](camera-container-shm.md)) · [`prep_patrol.sh`](../tools/prep_patrol.sh) 4~14 행 `ODOM`(커밋 `dcfdb0b6`) · 러너 `job551_f0drive.sh` 게이트 A 의 `ekf_vslam` 예외 · 게이트 B 6 → 12 s([`2026-10-21/jobs/job551_f0drive.sh`](../debug_log/2026-10-21/jobs/job551_f0drive.sh) 9~12 행) · CLAUDE.md §6 오도메트리 줄 | [Isaac · cuVSLAM 평가](isaac-cuvslam-evaluation.md)(09-29 단독 시험 · 프로젝터 충돌) · [rf2o 도입](rf2o-introduction.md)(같은 목적의 앞 수단 — 이 카드로 대체됨) · [rf2o 게이트 · 사람 시험](rf2o-gates-people.md) · [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(겨냥하는 미끄러짐) · [회전 중 장애물 번짐](rotation-obstacle-smear.md) · [회전축 보정 B2 · 회전 분산 B3](icr-b2-b3.md)(B3 = 이 융합의 짝, 39~40 행) · [센서 컨디셔너](sensor-conditioner.md) · [프로젝터 · IR 번갈이](projector-ir-alternation.md)(10-19 IR 조건 — 상시 끔 결정) · [카메라 ↔ 컨테이너 SHM](camera-container-shm.md)(입력 빠짐 해소 — 10-20 §7 · §9.1~§9.5) · [상자 과장의 출처](box-exaggeration-source.md)(상자 옆에 효과 없음의 짝) · [경로 추종 · 재계획 · B0](path-tracking-replan-b0.md)(상자 옆 근접의 실제 몫, 10-23 §12~) · [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md)(같은 주행들의 다른 지표) · [주행 운용 10-19 ~ 10-23](drive-ops-1019-1023.md)(게이트 P · C · 스크래치패드 소실) · [DDS 공유메모리 사고](dds-shm-incident.md) · [정체 감시 stuck_monitor](stuck-monitor.md)(f2von1 stuck 진단 4) · [TF 지연 · W3 흔들림](tf-lag-w3-wobble.md)(멈칫 A 의 같은 서명) |

**한 줄**: 회전 중 옆 · 뒤 미끄러짐을 휠 · 자이로 EKF 가 못 보는 문제(09-23 ~)를, 라이다(rf2o) 대신 카메라 IR 영상 오도메트리 cuVSLAM 의 **병진 속도(vx · vy)** 로 EKF 에 넣어 줄였다. 10-19 오프라인 비교는 번갈이 조건에서 **전 변형 실패**(켠 IR 은 점 무늬에 붙잡혀 이동 0, 끈 IR 은 어두워 특징 없음)였고, 10-20 프로젝터 **상시 끔**(밝은 끈 IR)에서 위치 95 % 26~31 cm · yaw 0.8~1.1° 로 처음 따라갔다. 그 출력을 EKF 에 넣는 오프라인 재실행은 처음에 주행 구성(rf2o · B3)을 빠뜨려 30~35 % 로 과대 판정했다가(§5.2 정정) **12~29 %** 로 고쳤고, yaw 속도만 넣는 것은 자이로(200 Hz)에 가려 효과가 없었다. 실시간 그림자 EKF(TF 안 냄)는 UDP 로 IR 이 빠져 −20 % 에 그쳤고, 카메라 ↔ cuVSLAM 공유메모리 뒤 4 주행에서 −31~−41 % 를 냈다. 10-23 `vslam:=on` 2 주행에서 W3 창 13.2 · 16.8 cm · 멈칫 5 · CPU 70 % 로 기본 채택. 상자 옆 여유 문제는 이 경로로 안 풀린다는 것이 재실행 · 그림자 · on 모두에서 같은 결과였다(그 몫은 [경로 추종](path-tracking-replan-b0.md)).

## 1. 증상 (이 카드가 다루는 질문)
- 회전 중 미끄러짐: 휠 · 자이로 EKF 는 제자리 회전 중 실제 옆 · 뒤 밀림을 거의 못 본다(09-28 180° 당 10~27 cm, 10-02 rot2 SLAM 0.322 vs EKF 0.003 m — [F0-a](f0-rotation-side-slip.md) · [회전 중 번짐](rotation-obstacle-smear.md)). 10-06 rf2o 로 통제 회전은 줄자 대비 1.5 cm 가 됐지만, 순회 주행의 W3 되돌아 회전에서는 rf2o 를 넣은 주 EKF 도 10 s 창 위치 오차가 12~31 cm 였다(이 카드의 측정 — §2 · §2.1 ⑥).
- 10-19 §23 의 질문: 프로젝터 번갈이(켬 · 끔 교대)로 nvblox 깊이와 cuVSLAM 을 한 카메라로 같이 쓸 수 있나 — cuVSLAM 이 이 조건에서 EKF 보다 나은가. (번갈이 · IR 조건의 본줄기는 [프로젝터 · IR 번갈이](projector-ir-alternation.md).)
- 10-20 §4 사용자 질문: cuVSLAM 회전 속도만 EKF 에 넣으면 어떤 결과가 예상되나 → '상자 기억을 밀어내는 짧은 창 오차' 로 다시 잼.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-19 §23 선언 | f2y1 IR bag(번갈이)을 켬 · 끔 프레임으로 나눠 컨테이너(Isaac 3.2, isaac_ros_visual_slam 3.2.6)에서 오프라인 cuVSLAM 4 변형(켬/끔 × IMU 융합 켬/끔), 기준 = SLAM camera_link 자세, 대상 = EKF | — | 판정 C1 vo_state ≥ 95 % · C2 끝 · 95 % 가 EKF 의 절반 이하 | [10-19 SUMMARY §23](../debug_log/2026-10-19/SUMMARY.md) |
| 10-19 §23.1 | 실행(첫 실행은 컨테이너 스크립트 `set -u` 충돌로 cuVSLAM 미실행 → 재실행) | 4 변형 모두 vo_state 100 %, 위치 오차 95 % **469~1592 cm** vs EKF 36 cm. 켬 = 30 s 에 1 m 넘게 움직이는 동안 이동 ≈ 0 · 끔+IMU 끔 = 한 번 (−31, +25 cm, +21°) 튀고 멈춤 · 끔+IMU 켬 = IMU 적분으로 흘러감 | **불합격** — 'vo_state 성공 100 % 는 정확도가 아님'. 켠 IR = 카메라와 함께 도는 점 무늬가 이동을 0 으로 붙잡음(09-29 O3 원리, 측정 확인), 끈 IR = 어두움(LED 조명의 근적외선 부족 — **추정**) | [`anal_vslam_cmp_f2y1.txt`](../debug_log/2026-10-19/outputs/anal_vslam_cmp_f2y1.txt) · 그림 [`vslam_cmp_f2y1.png`](../debug_log/2026-10-19/figures/vslam_cmp_f2y1.png) · 도구 `run_vslam_offline.sh` · `vslam_run_in.sh` · `mk_vslam_bag.py` · `export_vslam.py` · `anal_vslam_cmp.py`(모두 [`2026-10-19/jobs/`](../debug_log/2026-10-19/jobs/)) |
| 10-19 §25 → 10-20 §1 | 프로젝터 **상시 끔** 주행 f2z1 의 IR 로 같은 오프라인(본줄기 [프로젝터 카드](projector-ir-alternation.md)) | IMU 끔: 위치 끝 · 95 % · 최대 **1.5 · 25.7 · 31.6 cm**, yaw \|95 %\| **0.8°**. IMU 켬 7.1 · 29.5 · 34.1 · 1.9°. EKF 59.8 · 57.2 · 60.9 · 5.0°. 복귀 회전 t160~210 오차 변화 cuVSLAM −7.2 · EKF **+18.1 cm** | 'EKF 보다 낫다' IMU 끔 ✔(끝 · 95 % 둘 다 절반 이하), IMU 켬 ✘(경계). 끈 IR 이 밝으면(노출 32 → 65 ms · 게인 16 → 169) 된다 — **측정**. 후보 (C) 'yaw 속도 · twist 로만 융합' 제시 | [`anal_vslam_cmp_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_vslam_cmp_f2z1.txt) · 그림 [`vslam_cmp_f2z1.png`](../debug_log/2026-10-20/figures/vslam_cmp_f2z1.png) · `vslam_f2z1/`(csv) · [`get_vso_f2z1.sh`](../debug_log/2026-10-20/jobs/get_vso_f2z1.sh) |
| 10-20 §3 · §3.1 | f2z2(상시 끔 · 상자 둠) 주행 + 같은 오프라인 | 3/3. **출발 때 SLAM 이 21° 틀림** — map→odom (−0.25, +0.31, −20.9°) → t 12~15 s 에 (−0.02, 0.00, −0.9°)로 고쳐짐. 첫 자세 정렬은 무효 → **정렬 t = 20 s** 로 다시: IMU 끔 f2z1 3.6 · 27.6 · 0.8° / f2z2 9.0 · 31.3 · 1.1°, EKF f2z1 57.5 · 4.3° / f2z2 **13.2** · 3.3° | **재현됨(IMU 끔)**: 95 % 28~31 cm · yaw 0.8~1.1°. 위치는 EKF 가 주행마다 크게 달라(57 vs 13) 'EKF 보다 낫다' f2z1 ✔ · f2z2 ✘, yaw 는 두 번 다 3~4 배 작음. IMU 켬은 f2z2 7.8° 로 불안정 → **쓰지 않음**(원인 미확인 — 카메라 IMU unite 1 의심) | [`anal_vslam_cmp_a20.txt`](../debug_log/2026-10-20/outputs/anal_vslam_cmp_a20.txt) · [`anal_vslam_cmp_f2z2_start.txt`](../debug_log/2026-10-20/outputs/anal_vslam_cmp_f2z2_start.txt)(무효판) · [`vslam_scale.txt`](../debug_log/2026-10-20/outputs/vslam_scale.txt) · [`run_f2z2.txt`](../debug_log/2026-10-20/outputs/run_f2z2.txt) · 상자 표는 [상자 과장 카드](box-exaggeration-source.md) |
| 10-20 §4 | 출발 SLAM 21° — 사용자 판단 '이전 상태 초기화 또는 일시 오류, 다시 나오면 조사'. 짧은 창 상대 오차 `anal_vslam_rpe.py`(Δ 10 s, 1 s 간격) | 10 s 창 95 %: 전 구간 위치 EKF 17.1 / 9.1 vs cuVSLAM 8.1 / 7.6 cm(f2z1 / f2z2), yaw EKF 1.01 / 0.80° vs cuVSLAM 1.06 / 0.97°. 상자 옆 구간은 EKF ≤ cuVSLAM. 최대 창은 두 주행 다 t ≈ 109~121 s = **W3 끝 되돌아 회전**(f2z1 EKF 27 vs cuVSLAM 12 cm) | 예상(**추정**): yaw 만 융합 → 상자 효과 ≈ 0(상자 옆 10 s yaw 차 ≤ 0.5° × 1 m ≈ 1 cm), 병진까지 → 회전 미끄러짐 사건만 줄 것. '상자 과장 대책으로는 근거 약함' → 실시간 전에 EKF 오프라인 재실행이 싸다 | [`anal_vslam_rpe.txt`](../debug_log/2026-10-20/outputs/anal_vslam_rpe.txt) · [`anal_vslam_rpe.py`](../debug_log/2026-10-20/jobs/anal_vslam_rpe.py) |
| 10-20 §5 선언 · §5.1 | PC WSL robot_localization 으로 EKF 4 변형 동시 재생: V0 지금 · V1 + yaw 속도(σ 0.02) · V2 + vx · vy · yaw(σ 0.005 m/s) · V3 + vx · vy. 재현성 기준 먼저(V0 vs 기록 EKF 창 ≤ 1 cm · 끝 ≤ 5 cm), 실시간 구축 조건 = 두 주행 모두 상자 옆 −1.5 cm | f2z1 재현성 **불합격**(창 95 % 17.1 → 20.0 · 끝 58.9 → 67.3 cm, 제자리 회전 때만 어긋남), 재실행끼리는 0.2 cm 안. V2 · V3 W3 최대 28.7 → 18.9 · 14.6 → 10.7 cm(**30~35 %**), V1 무효, 상자 옆 −0.3 ~ +1.4 cm | 실시간과의 차 = 메시지 도착 순서 · 지연(**추정 — 틀림**, §5.2). '30~35 %' 는 **과대**(§5.3). 상자 옆 구축 조건 불충족 | [`anal_ekf_replay_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_f2z1.txt) · [`_f2z1_rep2.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_f2z1_rep2.txt) · [`_f2z2.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_f2z2.txt) · 그림 [`ekf_replay_f2z1.png`](../debug_log/2026-10-20/figures/ekf_replay_f2z1.png) |
| 10-20 §5.2 정정 | 실시간 구성을 짜며 prep 을 읽다 발견 — 순회 prep 은 `rf2o:=true`(EKF odom1 = `/odom_rf2o/gated`) + 컨디셔너 B3 | f2z1 · f2z2 bag `params.txt` 로 odom1 확인(B3 는 launch 코드로) | §5 의 V0 는 '지금 구성' 이 아니었다 → §5.1 판정 **무효**, rf2o · B3 를 넣은 재실행으로 대체. V4 = rf2o 대신 cuVSLAM | 고친 `mk_ekf_replay_bag.py`(B3 순수 회전 휠 f2z1 127 · f2z2 63 개) · `mk_ekf_replay_params.py live` |
| 10-20 §5.3 | 주행 구성으로 다시(V0 ~ V4) | **재현성 통과**: V0 vs 기록 f2z1 17.0/17.1 · 26.5/26.6 · 끝 58.9/58.9, f2z2 9.0/9.0 · 12.1/12.1 · 14.3/14.2 cm, yaw ≤ 0.02°. W3 최대 창 **f2z1 26.5 → 18.7(−29 %) · f2z2 12.1 → 10.7(−12 %)**, 전 구간 95 % −35 · −22 %. V1 무효. **V4 ≈ V3**. 상자 옆 −0.1 ~ +1.4 cm | §5.1 어긋남의 원인 = rf2o · B3 누락(**확정**, 타이밍 추정은 틀림). 정정값 12~29 %(미끄러짐이 클수록 큼). cuVSLAM 이 있으면 rf2o 는 더하는 게 없음 → 운용 후보 V4. 상자 옆 조건은 불충족이나 사용자가 고른 목적(회전 미끄러짐)으로 그림자 시험 진행. 실행 사고: 두 주행을 한 셸에서 이어 돌려 f2z1 의 ekf_node 가 f2z2 에 섞임(메시지 2 배) → 버리고 재실행 | [`anal_ekf_replay_live.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_live.txt) · 그림 [`ekf_replay_live_f2z1.png`](../debug_log/2026-10-20/figures/ekf_replay_live_f2z1.png) · [`_f2z2.png`](../debug_log/2026-10-20/figures/ekf_replay_live_f2z2.png) · [`run_ekf_replay.sh`](../debug_log/2026-10-20/jobs/run_ekf_replay.sh) 21 행(정리 추가) |
| 10-20 §6 | 코드: `ekf.launch.py vslam:=off\|shadow\|on`(기본 off) · `cuvslam_container.launch.py` · `cuvslam_up.sh` · `vslam_twist.py` · prep_fast 정리 · 상태 줄. 전제 = 프로젝터 상시 끔 | — | shadow = 그림자 EKF `ekf_vslam`(V4, TF 안 냄, `/odometry/ekf_vslam`), on = 주 EKF odom1 이 rf2o 대신 cuVSLAM | 커밋 `1269e3e5` · [`up_vslam.sh`](../debug_log/2026-10-20/jobs/up_vslam.sh) |
| 10-20 §6.1 · §6.2 | L0 정지 시험(A 프로젝터 끔 / B + 그림자, 각 60 s) | 1 차 B 전체 CPU 45.1 → **73.1 %**, 범인 **vslam_twist 코어 193 %**(TF 구독 빼도 191 %, 스레드 14 개 — numpy OpenBLAS 일꾼 바쁜 대기). `OPENBLAS_NUM_THREADS=1` 뒤 3 차: cuVSLAM 13.0 · `/vslam/odom` 12.9 Hz · CPU 54.1 vs A 47.0 · 45.1(**+7.1 · +9.0 %p**, 한도 +8) · EKF 위반 +3 · 정지 60 s `ekf_vslam` 0.29 cm | 2 번(CPU)만 경계, 나머지 통과 → 그림자 주행 가능. OpenBLAS 원인은 **추정이나 고침으로 사실상 확인**. 다른 numpy 노드(rf2o_gate · stuck_monitor · scan_deskew · depth_relay)도 같은 위험 — 점검 거리 | [`run_vslam_static.txt`](../debug_log/2026-10-20/outputs/run_vslam_static.txt) · [`run_vslam_static.sh`](../debug_log/2026-10-20/jobs/run_vslam_static.sh) · [`chk_vslam_live.py`](../debug_log/2026-10-20/jobs/chk_vslam_live.py) · `vslam_twist.py` 14~16 행 |
| 10-20 §6.3 · §6.4 | 그림자 주행 f2v1(UDP, 상자 둠, b910). 1 차는 러너 게이트 A 가 `ekf_node = 2 개` 로 불합격 → `ekf_vslam` 예외 추가 뒤 재시도 | 3/3. W3 최대 **27.5 → 22.1 cm(−20 %)** · 전 구간 95 % 19.0 → 12.4 · 상자 옆 3.7 → 4.0 / 3.2 → 3.1. 그러나 `/vslam/odom` bag **9.5 Hz · 0.5 s 넘는 끊김 38**(최대 3.8 s), vslam_twist 10 s 에 버림 4~18. CPU 75.0 %(f2z2 72.9 · f2z1 75.4) | 효과 ✔ · 연속성 **✘**. 입력 빠짐 = 주행 부하에서 호스트 → 컨테이너 IR DDS 전달 누락으로 **추정**(→ 10-20 §7 에서 UDP 소켓 버퍼 넘침으로 측정, [SHM 카드](camera-container-shm.md)). 이름 f2v1 이 10-15 와 겹침(실수) | [`run_f2v1.txt`](../debug_log/2026-10-20/outputs/run_f2v1.txt) · [`chk_f2v1_logs.txt`](../debug_log/2026-10-20/outputs/chk_f2v1_logs.txt) · [`anal_shadow_f2v1.txt`](../debug_log/2026-10-20/outputs/anal_shadow_f2v1.txt) · 그림 [`shadow_f2v1.png`](../debug_log/2026-10-20/figures/shadow_f2v1.png) · [`job551_f0drive_1020.sh`](../debug_log/2026-10-20/jobs/job551_f0drive_1020.sh) 9~10 행 |
| 10-20 §9.6 · §9.7 | SHM 구성(`dds_shm:=true`)으로 그림자 f2sm1 선언(연속성 기준 ≥ 14 Hz · 끊김 ≤ 2 · 버림 ≤ 1/10 s 추가). 세 번 다 게이트에서 멈춤 | 1 차 게이트 B 보드 무발행(USB 재연결) · 2 차 게이트 B 또 — `ros2 topic hz` 첫 출력 4.5~5.6 s(한도 6) · 3 차 게이트 P 정지 부하 **62 %** > 60(f2v1 56) | 그림자 구성(참가자 증가)이 첫 출력을 늦춤(**추정**) → 게이트 B 한도 12 s(도구). P 는 '그림자가 정지 부하를 +6 %p' — L0 의 +7~9 와 같은 크기. 주행 안 함(로버 안 움직임) | [`run_f2sm1_attempt3.txt`](../debug_log/2026-10-20/outputs/run_f2sm1_attempt3.txt) · [`chk_gateb.sh`](../debug_log/2026-10-20/jobs/chk_gateb.sh) · [`chk_hz_time.sh`](../debug_log/2026-10-20/jobs/chk_hz_time.sh) · 게이트 P 한도 65 % 결정은 [운용 카드](drive-ops-1019-1023.md)(10-21 §2) |
| 10-21 §7 | f2sm1 그림자(SHM) 주행 | 3/3. `/vslam/odom` **15.0 Hz** · 0.5 s 넘는 끊김 2(둘 다 bag 시작 t 3.9 s, 최대 0.66 s, cuVSLAM 원 출력 0) · vslam_twist 10 s 마다 142~154 · **버림 0**. W3 **24.1 → 16.1 cm(−33 %)** · 상자 옆 +0.9 · +0.6 · CPU 75.7 % · cuVSLAM 프레임 간격 경고 4 분에 5 회(f2v1 10 s 에 20~30) | §9.6 네 기준 모두 통과. 입력이 안 빠지자 효과가 커짐(−20 → −33 %) — §6.4 추정과 같은 방향. 단 −33 % 는 재실행 예상(−12~29 %)을 약간 넘고 미끄러짐 크기 자체가 주행마다 달라(주 EKF 27.5 vs 24.1) **반복 필요**. 그림자 EKF 의 절대 오차가 W3 뒤 다시 쌓이는 것 = yaw 는 여전히 휠 · 자이로라서(**추정**) | [`run_f2sm1.txt`](../debug_log/2026-10-21/outputs/run_f2sm1.txt) · [`run_meta_f2sm1.txt`](../debug_log/2026-10-21/outputs/run_meta_f2sm1.txt) · [`chk_f2sm1_logs.txt`](../debug_log/2026-10-21/outputs/chk_f2sm1_logs.txt) · [`gaps_f2sm1.txt`](../debug_log/2026-10-21/outputs/gaps_f2sm1.txt) · [`anal_shadow_f2sm1.txt`](../debug_log/2026-10-21/outputs/anal_shadow_f2sm1.txt) · 그림 [`shadow_f2sm1.png`](../debug_log/2026-10-21/figures/shadow_f2sm1.png) · bag `2026-10-21/bags/bag_f2sm1.tgz` |
| 10-21 §8 선언 | 반복 f2sm2 · f2sm3 — 반복 판정: **세 번(f2sm1~3) 모두 ≥ 10 % 이고 평균 ≥ 20 %** 면 `vslam:=on` 시험 | — | — | [10-21 SUMMARY §8](../debug_log/2026-10-21/SUMMARY.md) |
| 10-21 §9 | f2sm2 1 차 — 게이트 C(SLAM stamp 지연 1.05 s > 1.0) 불합격, 1 분 뒤 3 회 정상 | (운용 쪽 — [운용 카드](drive-ops-1019-1023.md)) | 경계값 일시 지연으로 재시도 | [`run_f2sm2_attempt1.txt`](../debug_log/2026-10-21/outputs/run_f2sm2_attempt1.txt) · [`chk_slamlag_1021.txt`](../debug_log/2026-10-21/outputs/chk_slamlag_1021.txt) |
| 10-21 §10 | f2sm2 2 차 — 목표 2(W3) **ABORTED 74.9 s**. 사용자: "사람들이 앞에서 길을 막으며 일부러 방해" | t 115~125 목표 반경 안 라이다 점 101 · 128 → t 128 부터 0 인데 전역 LETHAL 38~40 칸 끝까지. 휠 25.8° vs EKF −18.5°(차 44.3°) | **반복 비교에서 제외**(사용자). 동적 물체 대응의 근거로 사용 — 사람 이야기는 [rf2o 게이트 · 사람 카드](rf2o-gates-people.md) §7 | [`run_f2sm2.txt`](../debug_log/2026-10-21/outputs/run_f2sm2.txt) · [`anal_goal_block_f2sm2.txt`](../debug_log/2026-10-21/outputs/anal_goal_block_f2sm2.txt) · [`chk_abort_f2sm2.txt`](../debug_log/2026-10-21/outputs/chk_abort_f2sm2.txt) |
| 10-21 §11 · §12 | 복귀 f2sm2h · W3 중단 이유 · 복귀 중 멈칫 13 번 분류(0.01 s 시각 맞춤) | 멈칫 A 6(TF 외삽 → follow_path 중단 → 재시작) · B 4(`Control loop missed` 와 0.01~0.09 s — velocity_smoother 0.3 s 시한으로 0 감속 **추정**) · C 2 · D 1. 복귀 113 s 동안 주기 늦음 43, CPU 75 % 대(그림자 구성) | A · B 둘 다 '컨트롤러 주기가 늦다' 와 이어질 수 있음(**미확인**). §11.3 의 '4 번 = 새 경로 전달' 분류는 **틀림** → 실제 B. 이 멈칫 수가 이후 `vslam:=on` 판정 4(부작용)의 기준선이 됨 | [`anal_dip_events_f2sm2h.txt`](../debug_log/2026-10-21/outputs/anal_dip_events_f2sm2h.txt) · [`nav_events_ms.txt`](../debug_log/2026-10-21/outputs/nav_events_ms.txt) · [`chk_tf_extrap.txt`](../debug_log/2026-10-21/outputs/chk_tf_extrap.txt) · [`chk_dip_omega.txt`](../debug_log/2026-10-21/outputs/chk_dip_omega.txt) · [`anal_stops_f2sm2h.txt`](../debug_log/2026-10-21/outputs/anal_stops_f2sm2h.txt) · nav2 로그 **원천 소실**(10-21 §23) |
| 10-22 §19 | f2sm3 선언 — 그날 주행 4 개(f2pr1 · f2dr2 · f2lp1 · f2pi1)는 그림자였으나 러너가 그림자 토픽을 기록하지 않아 W3 를 못 잼 | — | 판정 10-20 §9.6 그대로, 반복은 f2sm3 · f2sm4 까지 | [10-22 SUMMARY §19](../debug_log/2026-10-22/SUMMARY.md) |
| 10-22 §20 | f2sm3(프리셋 3 · 통합 2.0 · 그림자 · SHM) | 3/3. 14.9 Hz · 끊김 0(원 출력 1) · 버림 0. W3 **30.7 → 18.0 cm(−41 %)** · 상자 옆 +1.5 · +0.7 · CPU 75 % | 전부 통과. 반복: f2sm1 −33 · f2sm3 −41 → **f2sm4 한 번 더**. 실수: Git Bash 가 `RTOPICS=/odometry/ekf_vslam` 을 Windows 경로로 바꿈 → `MSYS_NO_PATHCONV=1` | [`anal_shadow_f2sm3.txt`](../debug_log/2026-10-22/outputs/anal_shadow_f2sm3.txt) · [`gaps_f2sm3.txt`](../debug_log/2026-10-22/outputs/gaps_f2sm3.txt) · [`chk_f2sm3_logs.txt`](../debug_log/2026-10-22/outputs/chk_f2sm3_logs.txt) · [`run_f2sm3.txt`](../debug_log/2026-10-22/outputs/run_f2sm3.txt) · 그림 [`shadow_f2sm3.png`](../debug_log/2026-10-22/figures/shadow_f2sm3.png) |
| 10-23 §5.2 · §9 | PathAlign 28 주행 f2pa1 · f2pa2 의 그림자 지표(설정 하나 달라 순수 반복 아님) | W3 24.0 → 16.6(**−31 %**) · 21.5 → 14.3(**−33 %**), 15.0 Hz · 끊김 0 | '같은 주행 안 비교라 컨트롤러 설정이 비율을 크게 바꿀 이유는 적음'(**추정**). 반복으로 셀지는 사용자 결정 → 실제로는 '진행' 지시로 시험 진입(§10). **f2sm4 는 끝내 안 함** | [`anal_shadow_f2pa1.txt`](../debug_log/2026-10-23/outputs/anal_shadow_f2pa1.txt) · [`anal_shadow_f2pa2.txt`](../debug_log/2026-10-23/outputs/anal_shadow_f2pa2.txt) · [`gaps_f2pa1.txt`](../debug_log/2026-10-23/outputs/gaps_f2pa1.txt) · [`gaps_f2pa2.txt`](../debug_log/2026-10-23/outputs/gaps_f2pa2.txt) |
| 10-23 §10 선언 | PathAlign 14 복귀 + `vslam:=on` 주행 f2von1 — 판정 1 안전(3/3 · 연속성) · **2 주 지표 W3 ≤ 20 cm**(이전 주 EKF 21.5~30.7, 그림자 14.3~18.0) · 3 상자 옆(기록) · 4 부작용(멈칫 ≤ 18 · 0.5 s 정지 ≤ 1 · TF 외삽 ≤ 10 · 목표 시간 +15 % 안). 1 이 깨지면 rf2o(shadow)로 복귀 | — | '28 과 on 을 같이 바꾸면 원인 분리 불가' → 하나만 | [`prep_von_1023.sh`](../debug_log/2026-10-23/jobs/prep_von_1023.sh) · [`up_palign_1023.sh`](../debug_log/2026-10-23/jobs/up_palign_1023.sh) |
| 10-23 §10.1 | f2von1 | prep: 주 EKF odom1 = `/vslam/odom` · rf2o 노드 0. 3/3 · 52.8 / 47.7 / 103.5 s. 15.0 Hz · 끊김 0 · 버림 2 가 한 창(41 창 중) · stuck 진단 4. **W3 16.8 cm** · 전 구간 95 % 11.7 · 끝 31.1 · 상자 옆 출발 95 % **7.8**(이전 3.4~4.9). 멈칫 5 · TF 외삽 2 · 주기 늦음 38 · CPU 70 %. 상자 옆 실제 여유 3.3 cm | 판정 2 · 4 ✔, 1 은 버림 한 창이 기준 넘음(경계). stuck 진단 4 = stuck_monitor 가 스캔만 보는 과소 오판 — vslam:=on 과 무관([stuck_monitor](stuck-monitor.md)). 상자 옆 기억 밀림 3.5~4.8 cm **줄지 않음**. 출발 직후 상자 옆 7.8 cm 는 cuVSLAM 단독도 9.0 — 원인 미확인 | [`prep_von_1023_1.txt`](../debug_log/2026-10-23/outputs/prep_von_1023_1.txt) · [`run_f2von1.txt`](../debug_log/2026-10-23/outputs/run_f2von1.txt) · [`gaps_f2von1.txt`](../debug_log/2026-10-23/outputs/gaps_f2von1.txt) · [`chk_vslam_twist_f2von1.txt`](../debug_log/2026-10-23/outputs/chk_vslam_twist_f2von1.txt) · [`anal_ekf_f2von1.txt`](../debug_log/2026-10-23/outputs/anal_ekf_f2von1.txt) · [`anal_motion_window_f2von1.txt`](../debug_log/2026-10-23/outputs/anal_motion_window_f2von1.txt) · [`nav_events_ms_f2von1.txt`](../debug_log/2026-10-23/outputs/nav_events_ms_f2von1.txt) · [`anal_dip_events_f2von1.txt`](../debug_log/2026-10-23/outputs/anal_dip_events_f2von1.txt) · 그림 [`ekf_f2von1.png`](../debug_log/2026-10-23/figures/ekf_f2von1.png) · 상자 옆 수치는 [경로 추종 카드](path-tracking-replan-b0.md) |
| 10-23 §11 · §11.1 | 반복 f2von2(선언: 판정 1 · 2 · 4 통과면 기본 구성 후보) | 3/3 · 51.4 / 49.2 / 103.5 s. 15.0 Hz · 끊김 0 · 버림 0(43 창). **W3 13.2 cm** · 95 % 9.6 · 끝 26.1 · 상자 옆 출발 5.7. 멈칫 5 · TF 외삽 0 · 주기 늦음 48 · CPU 70 %. **상자 옆 실제 여유 0.3 cm** | 1 · 2 · 4 통과 → 기본 구성 후보. 상자 옆 근접은 기억 밀림(+0.8~1.8 cm 로 오히려 작음)보다 'MPPI 가 경로 선 남쪽을 달리는 것' 이 주된 몫 → [경로 추종 카드](path-tracking-replan-b0.md). vslam:=on 이 그것을 키웠는지는 판단 불가(미확인) | [`prep_von_1023_2.txt`](../debug_log/2026-10-23/outputs/prep_von_1023_2.txt) · [`run_f2von2.txt`](../debug_log/2026-10-23/outputs/run_f2von2.txt) · [`gaps_f2von2.txt`](../debug_log/2026-10-23/outputs/gaps_f2von2.txt) · [`chk_vslam_twist_f2von2.txt`](../debug_log/2026-10-23/outputs/chk_vslam_twist_f2von2.txt) · [`anal_ekf_f2von2.txt`](../debug_log/2026-10-23/outputs/anal_ekf_f2von2.txt) · [`nav_events_ms_f2von2.txt`](../debug_log/2026-10-23/outputs/nav_events_ms_f2von2.txt) · 그림 [`ekf_f2von2.png`](../debug_log/2026-10-23/figures/ekf_f2von2.png) |
| 10-23 §16 | **사용자 결정 "vslam on 기본으로 채택"** — `prep_patrol.sh` 기본 `emitter_off:=true vslam:=on dds_shm:=true`(`ODOM=vslam`, 예전은 `ODOM=rf2o`), `REPLAN_HZ` 환경. launch 기본값은 그대로 | Jetson `/tmp/prep_patrol.sh` 6bdd126a30 → 9a8a8e3361(저장소와 같음), `bash -n` OK | 운용 기본은 prep 이 정함. ⚠ Jetson 재부팅 재전송 묶음 `up_prep_1022.sh` 는 옛 prep_patrol 을 담음 → 다음 재전송은 저장소 판으로 | [`up_prep_patrol_1023.txt`](../debug_log/2026-10-23/outputs/up_prep_patrol_1023.txt) · [`up_prep_patrol_1023.sh`](../debug_log/2026-10-23/jobs/up_prep_patrol_1023.sh) · 커밋 `dcfdb0b6` |

### 2.1 근거 발췌 (README §2.3 — 스크립트 핵심 · 나온 결과 · 경로)
**① 번갈이 조건 실패 · 상시 끔 성공(10-19 §23.1 · 10-20 §1)** — 기준 = SLAM 사슬 map→odom ∘ odom→base_link ∘ base_link→camera_link, 첫 자세(또는 t = 20 s)에서만 맞춤.
```python
# Docs/debug_log/2026-10-19/jobs/anal_vslam_cmp.py 3~4 행(머리말) — 정렬 = 각 추정의 첫 시각에서 SLAM 자세에 맞춤(그 뒤 끼워 맞춤 없음)
#   SLAM = map→odom ∘ odom→base_link ∘ base_link→camera_link(정적), EKF = 같은 사슬에서 map→odom 을 첫 시각 값으로 고정한 것.
T_ALIGN = float(sys.argv[4]) if len(sys.argv) > 4 else None   # 10-20 §3: 정렬 시각 — f2z2 는 시작 때 SLAM 위치가 21° 틀렸다가 t≈12 s 에 고쳐짐
```
```
# outputs/anal_vslam_cmp_f2y1.txt (10-19, 번갈이)
  false_vs_off   추적 성공 100.0 % · 위치 오차 끝 204.2 · 95 % 483.2 · 최대 507.7 cm · yaw 오차 끝 -106.0° · …
  false_vs_on    추적 성공 100.0 % · 위치 오차 끝 136.7 · 95 % 588.2 · 최대 652.8 cm · yaw 오차 끝 -169.9° · …
  EKF            추적 성공   nan % · 위치 오차 끝  40.4 · 95 %  36.3 · 최대  40.4 cm · yaw 오차 끝  +5.0° · …
# 2026-10-20/outputs/anal_vslam_cmp_f2z1.txt (상시 끔)
  false_vs_off   추적 성공 100.0 % · 위치 오차 끝   1.5 · 95 %  25.7 · 최대  31.6 cm · yaw 오차 끝  -0.8° · … t160~210 +-7.2 cm
                 yaw 오차 |95 %| 0.8° · |최대| 1.5° · …
  EKF            추적 성공   nan % · 위치 오차 끝  59.8 · 95 %  57.2 · 최대  60.9 cm · yaw 오차 끝  +4.4° · … t160~210 +18.1 cm
# 2026-10-20/outputs/anal_vslam_cmp_a20.txt (정렬 t = 20 s)
#### f2z2 (정렬 t=20 s)
  false_vs_off   … 위치 오차 끝   9.0 · 95 %  31.3 · 최대  36.2 cm · … yaw 오차 |95 %| 1.1°
  true_vs_off    … 위치 오차 끝  61.3 · 95 %  59.3 · 최대  62.0 cm · … yaw 오차 |95 %| 7.8°
  EKF            … 위치 오차 끝  14.2 · 95 %  13.2 · 최대  14.2 cm · … yaw 오차 |95 %| 3.3°
```

**② 짧은 창 상대 오차(10-20 §4)** — Δ 초 동안 추정이 움직인 양을 SLAM 이 본 움직임과 비교(로버 몸 기준 상대 변환 차).
```
# 2026-10-20/outputs/anal_vslam_rpe.txt
#### f2z1 Δ10
  EKF              Δ10 s
    전 구간: 위치 95% 17.1 · 최대 26.6 cm · 옆 최대 23.0 cm · yaw 95% 1.01 · 최대 1.60°
    상자 옆 출발 t18~36: 위치 95% 3.2 · 최대 3.3 cm · 옆 최대 3.0 cm · yaw 95% 1.01 · 최대 1.01°
  cuVSLAM(IMU 끔)   Δ10 s
    전 구간: 위치 95% 8.1 · 최대 12.2 cm · 옆 최대 7.3 cm · yaw 95% 1.06 · 최대 1.54°
    상자 옆 출발 t18~36: 위치 95% 4.5 · 최대 6.5 cm · 옆 최대 6.4 cm · yaw 95% 1.27 · 최대 1.54°
```

**③ EKF 오프라인 재실행 — 입력 · 변형 · 결과(10-20 §5.2 · §5.3)**
```python
# Docs/debug_log/2026-10-20/jobs/mk_ekf_replay_bag.py 47~49 행 — 휠에 컨디셔너와 같은 공분산 + B3(순수 회전이면 vx · vy 분산 0.3²)
cov = np.array(m.twist.covariance, float); cov[0], cov[7], cov[35] = VX_VAR, VY_VAR, VYAW_VAR
w = gy[0] if t * 1e-9 - gy[1] < 0.1 else m.twist.twist.angular.z
if B3 and abs(m.twist.twist.linear.x) < 0.02 and abs(w) > 0.10: cov[0] = cov[7] = ROT_VAR; nb3 += 1
# 같은 파일 65~69 행 — cuVSLAM 자세(base_link 로 옮김) 앞뒤 프레임 중앙 차분, 반 회전 돌려 몸 기준 속도, 0.3 s 넘는 빠짐은 건너뜀
dt = R[k + 1, 0] - R[k - 1, 0]
if dt <= 0 or dt > 0.3: continue
D = np.linalg.inv(P[k - 1]) @ P[k + 1]
# Docs/debug_log/2026-10-20/jobs/mk_ekf_replay_params.py 12 · 17~19 행 — live = 주행 구성(rf2o odom1) + cuVSLAM odom2, V4 = odom1 을 cuVSLAM 으로 바꿈
RF = {'odom1': '/odom_rf2o/gated', 'odom1_config': cfg(True, True), …}
k = 'odom2' if LIVE and c != 'swap' else 'odom1'
if LIVE and c != 'swap': p.update(copy.deepcopy(RF))
```
```
# 2026-10-20/outputs/anal_ekf_replay_live.txt
#### f2z1
  EKF(주행 기록)       전 구간 위치 95% 17.1 · 최대 26.6 cm · … | W3 회전 t105~125 최대 26.6 · 상자 옆 출발 t18~36 95% 3.2 · 상자 옆 복귀 t180~200 95% 2.4 cm | …
  재실행 V0           전 구간 위치 95% 17.0 · 최대 26.5 cm · … | W3 회전 t105~125 최대 26.5 · 상자 옆 출발 t18~36 95% 3.1 · 상자 옆 복귀 t180~200 95% 2.4 cm | …
  재실행 V1           전 구간 위치 95% 17.0 · 최대 26.5 cm · yaw 95% 0.98° | W3 회전 t105~125 최대 26.5 · …
  재실행 V4           전 구간 위치 95% 11.0 · 최대 18.6 cm · … | W3 회전 t105~125 최대 18.6 · 상자 옆 출발 t18~36 95% 3.0 · 상자 옆 복귀 t180~200 95% 3.4 cm | …
#### f2z2
  재실행 V0           전 구간 위치 95%  9.0 · 최대 12.1 cm · … | W3 회전 t105~125 최대 12.1 · 상자 옆 출발 t18~36 95% 4.4 · …
  재실행 V4           전 구간 위치 95%  7.0 · 최대 10.7 cm · … | W3 회전 t105~125 최대 10.7 · 상자 옆 출발 t18~36 95% 5.7 · …
```

**④ L0 — vslam_twist 가 코어 2 개를 먹은 것(10-20 §6.2)**
```python
# ros2_ws/src/rover_bringup/scripts/vslam_twist.py 14~17 행
# 10-20 §6.1: numpy(OpenBLAS)가 작은 4×4 연산마다 일꾼 스레드를 깨워 바쁜 대기 — 이 노드가 스레드 14 개 · 코어 2 개를 먹었다(top 213 %).
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1'); os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np  # noqa: E402
```
```
# 2026-10-20/outputs/run_vslam_static.txt (24 · 53 · 87~92 행)
  프로세스 CPU(코어 1 = 100): cuVSLAM(컨테이너) 7.6 · vslam_twist 192.7 · ekf_vslam 8.4 · …        (1 차)
  프로세스 CPU(코어 1 = 100): cuVSLAM(컨테이너) 7.5 · vslam_twist 191.5 · ekf_vslam 8.3 · …        (2 차, TF 구독 뺌)
측정 60 s · 전체 CPU 54.1 % (6 코어 = 100)                                                          (3 차, 1 스레드)
  /visual_slam/tracking/odometry    13.0 Hz · 처음→끝 이동 0.46 cm
  /odometry/ekf_vslam               30.1 Hz · 처음→끝 이동 0.29 cm
  프로세스 CPU(코어 1 = 100): cuVSLAM(컨테이너) 10.0 · vslam_twist 4.5 · ekf_vslam 11.5 · …
```

**⑤ 그림자 효과 지표(10-20 §6.4 ~ 10-23 §9)** — 10 s 창을 1 s 간격으로 밀며 SLAM 이 본 상대 이동 G 와 추정 E 의 차 X = G⁻¹E 의 평면 크기. 'W3 회전' 은 bag 시각 t105~125 와 겹치는 창의 최대.
```python
# Docs/debug_log/2026-10-20/jobs/anal_ekf_replay.py 64 · 72 · 76 행
SEG = (('W3 회전 t105~125', 105, 125, 'max'), ('상자 옆 출발 t18~36', 18, 36, 95), ('상자 옆 복귀 t180~200', 180, 200, 95))
G = np.linalg.inv(slam(a)) @ slam(a + D); E = np.linalg.inv(est(a)) @ est(a + D); X = np.linalg.inv(G) @ E
k = (O[:, 0] + D > s0) & (O[:, 0] < s1); v = O[k, 1].max() if q == 'max' else np.percentile(O[k, 1], q)
```
```
# 각 outputs/anal_shadow_*.txt 의 W3 열(주 EKF '(주행 기록)' → 그림자 '재실행 EKF_VSLAM' → cuVSLAM 단독)
2026-10-20 f2v1  (UDP)  27.5 → 22.1 → 13.1     상자 옆 출발 3.7 → 4.0 · 복귀 3.2 → 3.1
2026-10-21 f2sm1 (SHM)  24.1 → 16.1 → 11.0     4.3 → 5.2 · 2.5 → 3.1
2026-10-22 f2sm3 (SHM)  30.7 → 18.0 → 13.3     3.4 → 4.9 · 2.9 → 3.6
2026-10-23 f2pa1 (SHM)  24.0 → 16.6 → 12.3     4.7 → 4.5 · 4.2 → 4.2
2026-10-23 f2pa2 (SHM)  21.5 → 14.3 → 10.7     3.4 → 4.6 · 3.7 → 3.8
# outputs/anal_ekf_f2von*.txt (vslam:=on — 주 EKF 자체가 cuVSLAM 융합)
2026-10-23 f2von1       16.8 (cuVSLAM 단독 9.7)   상자 옆 출발 7.8 · 복귀 3.9
2026-10-23 f2von2       13.2 (cuVSLAM 단독 8.7)   상자 옆 출발 5.7 · 복귀 3.6
```
(위 7 줄은 카드 작성 중 각 파일의 같은 열을 옮겨 적은 것 — 원문 줄은 파일에 있다. 예: `anal_shadow_f2sm3.txt` 2~3 행 `EKF(주행 기록) … W3 회전 t105~125 최대 30.7` · `재실행 EKF_VSLAM … W3 회전 t105~125 최대 18.0`.)

**⑥ 입력 연속성 — UDP 대 SHM(10-20 §6.4 · 10-21 §7)**
```
# 2026-10-21/outputs/gaps_f2sm1.txt (anal_topic_gaps.py — bag 기록 시각 기준)
/vslam/odom                          3299 개 · 15.0 Hz · 0.5 s 넘는 끊김 2 · 최대 간격 0.66 s @ t=3.9
/visual_slam/tracking/odometry       3201 개 · 15.0 Hz · 0.5 s 넘는 끊김 0 · 최대 간격 0.25 s @ t=0.9
# 2026-10-21/outputs/chk_f2sm1_logs.txt
== vslam_twist 10 s 통계(주행 11:40:01~11:44:01)
: 출력 149 · 버림 0 (최근 10 s)
# 2026-10-23/outputs/chk_vslam_twist_f2von1.txt (f2von1 판정 1 의 경계)
      1 : 출력 144 · 버림 2 (최근 10 s)
```
f2v1 의 '9.5 Hz · 끊김 38 · 버림 4~18' 원문은 [`chk_f2v1_logs.txt`](../debug_log/2026-10-20/outputs/chk_f2v1_logs.txt) · SUMMARY §6.4(그날 bag 간격 계산 출력 파일은 없음 — `anal_topic_gaps.py` 는 10-21 에 만듦).

**⑦ 지금 운용이 cuVSLAM 을 어떻게 넣나** — 카드 작성 중 근사 계산(rf2o 카드 §2.1 ② 와 같은 식, 과정 잡음 무시): 몫 = (f_vs/σ_vs²) / (f_vs/σ_vs² + f_휠/σ_휠²), f_vs 15 · f_휠 25 Hz, σ_vs 0.005(`vslam_twist.py` 25 행), 휠 σ vx 0.02 · vy 0.01 · 순수 회전 0.3(`conditioner_core.hpp` 22~23 · 47~48 행 + `ekf.launch.py` 40 행).
- 직진 vx: 600 000 / (600 000 + 62 500) = **91 %** · vy: 600 000 / (600 000 + 250 000) = **71 %** · 제자리 회전: 600 000 / (600 000 + 278) = **99.95 %**. rf2o(직진 σ 0.10 → 2~4 %)와 달리 **cuVSLAM 은 직진에서도 병진을 거의 정한다** — 10-20 §5 에서 σ 0.005 를 고를 때는 '옆 미끄러짐 때 휠 vy = 0 보다 믿게' 가 이유였고 직진 몫은 따로 따지지 않았다(기록 없음). 재실행 · 그림자 · on 은 모두 이 σ 로 측정했으므로 위 효과 수치에 이미 포함된 조건이다.

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 번갈이 조건에서 cuVSLAM 이 EKF 보다 낫다 | 10-19 §23 오프라인 4 변형 | 위치 95 % 469~1592 vs EKF 36 cm | **기각(측정)** — 켬은 점 무늬에 붙잡힘(측정), 끔은 어두움(LED 근적외선 부족은 **추정**) |
| 프로젝터 상시 끔(밝은 끈 IR)이면 따라간다 | 10-20 §1 · §3.1 오프라인 2 주행 | IMU 끔 95 % 26~31 cm · yaw 0.8~1.1° 재현 | **지지(측정, 2 회 · 같은 코스)** |
| IMU 융합을 켜면 더 좋다 | 같은 비교 | f2z1 1.9° · f2z2 7.8°(불안정) | **기각** — 원인(unite 1 시각 어긋남)은 **미확인** |
| yaw 속도만 넣으면 회전 · 상자 문제가 준다 | 재실행 V1 | 모든 창 지표 V0 와 같음, 절대 yaw 4.2 → 4.0° | **기각(측정)** — 자이로 200 Hz 가 15 Hz cuVSLAM 을 가림 |
| 병진(vx · vy)을 넣으면 회전 미끄러짐 창이 준다 | 재실행 V2 · V3 · V4(주행 구성) | W3 −12~29 %, 전 구간 −22~35 % | **지지(측정)** — 미끄러짐이 클수록 큼 |
| rf2o 와 cuVSLAM 을 같이 쓰면 더 낫다 | V3(rf2o + cuVSLAM) vs V4(cuVSLAM 만) | 0.1 cm 안에서 같음 | **기각** — rf2o 는 더하는 게 없음 |
| 오도메트리를 고치면 상자 옆 오차가 준다 | 재실행 · 그림자 6 회 · on 2 회의 상자 옆 창 · 실제 여유 | 재실행 −0.3 ~ +1.4 · 그림자 −0.2 ~ +1.5 · on 출발 5.7 ~ 7.8(이전 3.4~4.9) · 실제 여유 3.3 · 0.3 cm | **기각** — 상자 옆 10 s 창은 이미 ≈ 3 cm(SLAM 기준 흔들림 수준), 실제 근접은 경로 추종 몫([경로 추종 카드](path-tracking-replan-b0.md)) |
| 재실행 V0 와 실시간 EKF 의 차는 메시지 도착 순서 · 지연 탓 | §5.2 구성 대조 → §5.3 재실행 | rf2o · B3 를 넣자 17.0/17.1 · 끝 58.9/58.9 | **기각** — 원인은 구성 누락(내 실수 1) |
| 실시간 그림자 효과가 재실행보다 작은 것은 입력 빠짐 탓 | f2v1(UDP, 9.5 Hz) vs SHM 4 회(15 Hz) | −20 % vs −31~−41 % | **지지(정황)** — 주행마다 미끄러짐 크기가 달라(주 EKF 21.5~30.7) 1 : 1 대조는 아님 |
| 그림자 구성이 정지 부하를 올린다 | L0 · f2sm1 게이트 P | +7.1~9.0 %p · 56 → 62 % | **지지(측정)** — 프로세스 합 cuVSLAM 10 · vslam_twist 4.5 · ekf_vslam 11.5(코어 %) |
| `vslam:=on` 이 멈칫 · CPU 를 줄인다 | f2von1 · f2von2 vs 그림자 주행들 | 멈칫 5 · 5 vs 12~14, CPU 70 vs 75~76 % | **지지(측정)이나 원인 분리 안 됨** — 비교 대상이 모두 '그림자 + rf2o' 구성이라 rf2o · rf2o_gate · 그림자 EKF 를 안 띄운 몫(10-22 §18 표: rf2o_gate 12.3 · ekf_node 둘 11.1 · 9.7 코어 % → 6 코어 기준 약 4 %p)과 섞임. 그림자 없는 rf2o 주행(f2z1 75.4 · f2z2 72.9 %)과는 차 2.9~5.4 %p |

## 4. 조치와 효과
- **바꾼 것**: ① 오프라인 비교 · 재실행 도구(10-19 · 10-20 jobs) ② `ekf.launch.py vslam:=` 와 컨테이너 cuVSLAM · 속도 변환 노드(10-20 §6) ③ 러너 게이트 A · B 수정(10-20 §6.4 · §9.7) ④ 공유메모리 경로(별도 카드) ⑤ 운용 기본 `ODOM=vslam`(10-23 §16).
- **효과(측정)**: W3 되돌아 회전 10 s 창 — 재실행 −12~29 %, 그림자(SHM) −31~−41 %(4 회), on 13.2 · 16.8 cm. 전 구간 95 % 그림자 −28~−40 %(5 주행: f2v1 19.0 → 12.4 · f2sm1 16.0 → 10.4 · f2sm3 21.4 → 12.8 · f2pa1 14.0 → 10.1 · f2pa2 13.8 → 9.7), on 9.6 · 11.7 cm. 멈칫 5 · 5 · CPU 70 %(원인 분리 안 됨, §3).
- **한계**: ① 미끄러짐 자체는 그대로 — 실제 회전 중 밀림은 줄지 않았고, EKF 가 '보는 몫' 이 늘었을 뿐. 그림자 · on EKF 는 cuVSLAM 단독(8.7~13.3 cm)보다 여전히 나쁘다(입력이 빠지거나 휠 · 자이로와 섞이는 몫, **추정**) ② yaw 는 여전히 휠 · 자이로 — 절대 yaw 치우침 3.8~4.9°(그림자 · on 모두)는 그대로, SLAM 이 지도 층에서 고침 ③ 상자 옆 여유 효과 없음 ④ 근거 주행은 같은 코스(b910) · 같은 조명 · 같은 날 시간대 — 어두운 곳 · 무늬 없는 벽 · 사람 많은 곳에서 cuVSLAM 이 어떻게 되는지는 미측정(09-29 사람 걸음 1.10 cm 정지 시험만) ⑤ 프로젝터 상시 끔이 전제 — 깊이 품질의 대가는 [유령 칸 카드](ghost-cells-depth-preset.md).

### 지금 코드에서 확인한 것 (11-03, 저장소 기준 — 코드는 바꾸지 않음)
- [`ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py): `vslam` 기본 **off**(109~110 행) — launch 기본은 그대로이고 운용 기본은 prep 이 정한다. `VS_ODOM`(30~31 행) = odom1 `/vslam/odom`, `odom1_config` 의 vx · vy 만 true(yaw 속도 안 씀), `differential false` · `relative false`. `vslam == 'on'` 이면 주 EKF 에 `VS_ODOM`(51~52), `rf2o and vslam != 'on'` 일 때만 rf2o 노드 · 게이트(53 행) — 그래서 `rf2o:=true vslam:=on` 이어도 rf2o 는 안 뜬다(10-23 f2von 이 그 꼴이었음: prep_patrol 옛 기본 `rf2o:=true …` + `SENSORS_ADD="… vslam:=on …"`, prep 출력 `rf2o 노드 0`). **B3 자동 켜짐 39~40 행** `if rf2o or vslam != 'off': cp.update({'rot_cov_enable': True, 'rot_vx_var': 0.3 ** 2, 'rot_vy_var': 0.3 ** 2})`. `vslam != 'off'` 면 `cuvslam_up.sh` + `vslam_twist.py`(69~76, `dds_shm` 이면 `fastdds_shm_udp.xml`), `shadow` 면 `ekf.yaml` + `VS_ODOM` · `publish_tf False` 의 `ekf_vslam` → `/odometry/ekf_vslam`(77~82).
- [`vslam_twist.py`](../../ros2_ws/src/rover_bringup/scripts/vslam_twist.py): 입력 `/visual_slam/tracking/odometry`(sensor_data QoS, 43 행), `/tf_static` 한 번 받고 구독 끊음(49~59), 공분산 vx · vy **0.005²**(25 · 82 행) · yaw 0.02²(EKF 가 안 씀), 거름 `DT_MAX 0.3` · `V_MAX 0.5` · `W_MAX 1.5`(27 · 72 · 77 행), stamp = 가운데 프레임 k(79 행 — 한 프레임 ≈ 67 ms 늦음, 6 행 주석). `TODO(improve): 추적 상태(/visual_slam/status) 연동`(8 행) — 지금은 추적이 실패해도 자세가 튀지만 않으면 그대로 넘김.
- [`cuvslam_container.launch.py`](../../ros2_ws/src/rover_bringup/launch/cuvslam_container.launch.py) 16~21 행: `enable_imu_fusion False` · `rectified_images True` · `image_jitter_threshold_ms 80` · `base_frame camera_link` · TF 발행 둘 다 끔, 입력 `/camera/raw/infra{1,2}/image_rect_raw`(24~25 — `camera.launch.py emitter_off:=true` 가 옮긴 원시 IR, 26~28 행).
- [`ekf.yaml`](../../ros2_ws/src/rover_bringup/config/ekf.yaml): odom0 휠(vx · vy · vyaw, 18~23) · imu0 자이로 한 축(35~40), `smooth_lagged_data` 설정 없음 — 67 ms 늦은 `/vslam/odom` stamp 를 EKF 가 어떻게 처리하는지는 기록에서 확인 안 됨(**미확인**).
- [`prep_patrol.sh`](../tools/prep_patrol.sh) 10~14 행: `ODOM` 기본 **vslam** → `emitter_off:=true vslam:=on dds_shm:=true`, `ODOM=rf2o` → `rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel`. 4~6 행 주석이 10-23 §16 근거를 적음(⚠ 범위 표기 — §5 기록 어긋남 3). [`prep_fast.sh`](../tools/prep_fast.sh) 24 행 정리 목록에 `cuvslam_up.sh vslam_twist`, 38~39 행 컨테이너 안 cuVSLAM 고아 정리, 73 행 상태 줄 `cuVSLAM(컨테이너) · vslam_twist · ekf_vslam` 개수.
- 컨디셔너 B3 문턱: [`conditioner_core.hpp`](../../ros2_ws/src/rover_bringup/include/rover_bringup/conditioner_core.hpp) 43~44 행(`icr_v_max 0.02` · `icr_w_min 0.10`) · 159 · 184 행. 재실행 입력(`mk_ekf_replay_bag.py` 48~49)도 같은 문턱.

## 5. 내 실수 · 기록 어긋남
**실수 1 — 재실행 V0 에 주행 구성(rf2o · B3)을 빠뜨림(10-20 §5 · §5.1 → §5.2)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 지금 EKF 설정에 cuVSLAM 을 더했을 때의 효과를 오프라인으로 |
| 본 것 | V0 가 기록 EKF 를 재현 못 함(f2z1 끝 58.9 → 67.3 cm), 제자리 회전 때만 어긋남. 재실행끼리는 0.2 cm 안 |
| 처음 추론 | 실시간 EKF 가 받은 메시지 도착 순서 · 지연(부하 · DDS) 차이 — 회전 중 휠 vx 를 어느 yaw 로 적분하느냐 |
| 의심한 이유 | 실시간 구성을 짜며 prep 을 읽다가 `ekf.launch rf2o:=true` 를 봄 |
| 판별 | bag `params.txt` 의 odom1 = `/odom_rf2o/gated`, B3 는 launch 39~40 행 → rf2o · B3 를 넣고 재실행 |
| 결론 | 재현성 통과(17.0/17.1 · 58.9/58.9). '30~35 %' → 정정 12~29 %. '어긋남이 회전 때만' 이라는 서명 자체가 '회전 때만 다른 입력(rf2o σ 0.03 · B3 σ 0.3)' 을 가리키고 있었다 |
| 다음에 알아보는 법 | 재실행의 V0 는 **주행 bag 의 params.txt 와 launch 분기**로 만든다(ekf.yaml 만 보지 않는다). 재현성 차가 특정 동작 구간에만 있으면 그 구간에만 바뀌는 입력부터 의심 |
| 스크립트 핵심 | 고친 판 `mk_ekf_replay_bag.py` 49 행 B3 · `TOP` 에 `/odom_rf2o/gated`(35 행), `mk_ekf_replay_params.py` 12 · 17~19 행 |
| 나온 결과 | 무효판 [`anal_ekf_replay_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_f2z1.txt) → 정정판 [`anal_ekf_replay_live.txt`](../debug_log/2026-10-20/outputs/anal_ekf_replay_live.txt) |

**실수 2 — 재실행 노드가 다음 재생에 섞임(10-20 §5.3)**: 두 주행을 한 셸에서 이어 돌리자 `ros2 run` 래퍼만 죽고 f2z1 의 ekf_node 가 살아 f2z2 출력에 섞임(메시지 2 배) → 버리고(`outL_f2z2_contaminated`, 저장소에 없음) 재실행. 고침 [`run_ekf_replay.sh`](../debug_log/2026-10-20/jobs/run_ekf_replay.sh) 21 행 `pkill -INT -f "__node:=ekf_v"`. 알아보는 법: 출력 bag 의 메시지 수가 재생 길이 × 30 Hz 의 2 배면 섞임. (rf2o 카드 실수 1 '이름 pkill' 과 반대 방향 — 이번엔 정리가 **모자라서** 생김.)

**실수 3 — f2v1 이름 재사용(10-20 §6.4)**: 10-15 §3 에 이미 쓴 이름. Jetson bag 은 덮지 않았으나 PC 스크래치패드의 10-15 판 부속 파일(f2v1.csv · tegra · top · proc 로그 · tgz)이 덮임 → 그 원천은 **소실**(10-15 bag 압축 해제본과 `2026-10-15/outputs/*f2v1*` 은 남음). 이후 이름은 전체에서 겹치지 않게(10-20 §9.6 부터 '어디에도 없음 확인' 을 선언에 적음).

**실수 4 — 백그라운드 안에서 다시 `&`(10-20 §9.7)**: f2sm1 3 차를 백그라운드 명령 안에서 `&` 로 띄워 PC 감시 셸이 2 s 만에 끝남(Jetson 러너는 setsid 라 계속). 결과 회수를 따로 함. 원문 [`run_f2sm1_attempt3.txt`](../debug_log/2026-10-20/outputs/run_f2sm1_attempt3.txt).

**실수 5 — Git Bash 경로 변환(10-22 §20)**: `RTOPICS=/odometry/ekf_vslam` 이 `C:/Program Files/Git/odometry/ekf_vslam` 으로 바뀌어 '토픽 없음'. `MSYS_NO_PATHCONV=1`. `anal_ekf_replay.py` 40 행이 그 경우를 '가 bag 에 없음' 으로 멈추게 해 둔 덕에 잘못된 전체 읽기(빈 목록이면 rosbags 는 전부 읽음)로 가지 않았다.

**실수 6 — 멈칫 분류를 1 s 해상도로(10-21 §11.3 → §12.2)**: '4 번 = 새 경로 전달' 은 틀림 → 실제 `Control loop missed`(B). 0.01 s 시각 맞춤 · 주기 늦음 줄을 거르지 않기. 원문 [`anal_dip_events_f2sm2h.txt`](../debug_log/2026-10-21/outputs/anal_dip_events_f2sm2h.txt).

**기록 어긋남**
1. **반복 판정 기준이 선언대로 채워지지 않은 채 다음 단계로 감** — 10-21 §8 선언 '세 번(f2sm1~3) 모두 ≥ 10 % · 평균 ≥ 20 %', 10-22 §20 'f2sm4 한 번 더'. 실제로는 순수 반복 2 회(f2sm1 −33 · f2sm3 −41) + 설정 하나 다른 2 회(f2pa1 −31 · f2pa2 −33)로 10-23 §10 시험에 들어갔다 — 10-23 §10 이 "f2pa1 · f2pa2 를 그림자 반복으로 셀지는 사용자 결정 대신 '진행' 지시로 시험 진입" 이라 스스로 적음. 수치상으론 넷 다 기준을 넘지만 **선언한 기준과 쓴 근거가 다르다**. f2sm4 는 이후에도 없음.
2. **'상자 옆 기억 오차의 근본 대책' 표현** — 10-22 §21 남은 일 1 · 10-23 §9 제안 ② 가 `vslam:=on` 을 '상자 옆 기억 오차 근본 대책' 이라 불렀다. 그러나 10-20 §4 · §5.3 이 측정으로 '상자 과장 대책으로는 근거 약함 · 상자 옆 개선 없음' 이라 결론냈고, 그림자 4 회도 상자 옆 +0.6 ~ +1.5 cm 였다. 10-23 §10.1 · §11.1 결과가 10-20 결론과 같았다(기억 밀림 안 줄음 · 실제 여유 3.3 · 0.3 cm).
3. **채택 근거의 범위 표기(CLAUDE.md §6 · `prep_patrol.sh` 5 행 'rf2o 주 EKF 21.5~30.7')** — 이 범위는 10-21 ~ 10-23 그림자 주행 4 개(f2sm1 24.1 · f2sm3 30.7 · f2pa1 24.0 · f2pa2 21.5)의 주 EKF 값이다. 같은 rf2o 주 EKF 로 잰 다른 주행은 f2z1 26.6 · f2v1 27.5 · **f2z2 12.1 cm**(`anal_ekf_replay_live.txt` · `anal_shadow_f2v1.txt`)로, f2z2 는 vslam:=on 의 13.2 · 16.8 보다 작다. 주행 사이 비교는 미끄러짐 크기가 주행마다 달라 약하고, 강한 근거는 **같은 주행 안의 그림자 비교(−20~−41 %)** 쪽이다. 수치 자체가 틀린 것은 아님.
4. **f2von1 판정 1 의 하위 기준** — 10-23 §10.1 은 'vslam_twist 버림 2 가 한 창 — 기준 ≤ 1/10 s 를 한 창에서 넘음(경계)' 이라 적었는데, §11 선언은 'f2von2 **도** §10 판정 1 · 2 · 4 통과' 라 f2von1 이 1 을 통과한 것처럼 읽힌다. 원문 [`chk_vslam_twist_f2von1.txt`](../debug_log/2026-10-23/outputs/chk_vslam_twist_f2von1.txt) 4 행 `1 : 출력 144 · 버림 2`.
5. 경미: [`anal_vslam_cmp_f2z1.txt`](../debug_log/2026-10-20/outputs/anal_vslam_cmp_f2z1.txt) 마지막 줄은 그림을 `2026-10-19/figures/vslam_cmp_f2z1.png` 에 썼다고 하나 파일은 `2026-10-20/figures/` 에 있다(옮김 — 내용 문제 없음).
6. 경미: CPU 70 %(f2von1 · f2von2)는 SUMMARY 에 수치만 있고 계산 출력 파일이 없다 — 러너가 회수한 `top_f2von1.log` · `top_f2von2.log`(`run_f2von*.txt` 33 행 '회수')는 PC 스크래치패드 쪽이라 저장소에 없음(**원천 저장소 밖**). 비교 대상 75~76 % 는 [`anal_cpu_f2pi1_cmp.txt`](../debug_log/2026-10-22/outputs/anal_cpu_f2pi1_cmp.txt)(f2pi1 76 · f2pr1 74 · f2dr2 76 · f2sm3 75 %)에 있다.
7. 경미: `chk_f2v1_logs.txt` · `chk_f2sm1_logs.txt` 를 낸 스크립트는 저장소 jobs 에 없다(출력만 있음).

## 6. 남은 것 (10-23 시점)
- **yaw 는 여전히 휠 · 자이로** — 절대 yaw 치우침 3.8~4.9° 와 '그림자 EKF 절대 오차가 W3 뒤 다시 쌓임'(10-21 §7)은 그대로. 10-28 '정지 중 yaw 드리프트'(43 분 +16.6°)와도 이어짐(→ [정지 중 yaw 드리프트](stationary-yaw-drift.md), 9 기).
- cuVSLAM 이 약한 조건: 어두운 곳 · 무늬 없는 벽 · 사람이 시야를 크게 가림 · 빠른 회전 — 미측정. `vslam_twist.py` 는 추적 상태를 안 봄(TODO 8 행). 직진에서도 병진의 71~91 % 를 cuVSLAM 이 정하므로(§2.1 ⑦) 실패하면 직진 축척까지 영향(**추정**).
- IMU 융합이 불안정한 이유(카메라 IMU unite 방식) — 미확인.
- 출발 SLAM 21°(10-20 §3.1) · 출발 직후 상자 옆 창이 cuVSLAM 쪽에서 나쁨(f2von1 7.8 · cuVSLAM 단독 9.0) — 원인 미확인.
- 그림자 EKF 가 cuVSLAM 단독만큼 못 내려가는 이유 — '휠 · 자이로와 섞임' 은 추정.
- 다른 numpy 노드의 OpenBLAS 바쁜 대기 점검(10-20 §6.2) — 안 함.
- 멈칫 A(TF 외삽) · B(제어 주기 늦음) — on 에서 5 회로 줄었으나 남음, 기전 미확인([TF 지연 카드](tf-lag-w3-wobble.md)).
- 반복 판정의 f2sm4 · vslam:=on 3 번째 주행 — 없음.

## 7. 이후 (10-26 ~): 다음 시기에서 채움
- 포인터만: 10-26 ~ 28 Smac 주행 · F2.5 시험은 모두 `ODOM=vslam` 기본으로 돌았다(CLAUDE.md §6). 10-28 §16.1 정지 중 yaw 드리프트 — 주 EKF 병진은 cuVSLAM 이지만 yaw 는 자이로라 이 카드의 '남은 것 1' 과 같은 줄기.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2y1 | 번갈이 IR 기록 주행(10-19 §19) → 오프라인 4 변형 실패 | `2026-10-19/outputs/anal_vslam_cmp_f2y1.txt` · `outputs/vslam_f2y1/` · Jetson `~/bags/bag_f2y1_ir`(4.0 GB, 정리 대기) |
| f2z1 · f2z2 | 상시 끔 IR 기록 주행(10-19 §25 · 10-20 §3) → 오프라인 · 재실행 입력 | `2026-10-20/outputs/anal_vslam_cmp_*.txt` · `anal_ekf_replay_*.txt` · `vslam_f2z1/` · `vslam_f2z2/` · bag `2026-10-21/bags/`(f2z1 · f2z2 tgz, 10-21 §23 복사) |
| V0 ~ V4 | EKF 오프라인 재실행 변형 | `2026-10-20/outputs/anal_ekf_replay_live.txt`(정정판) |
| L0 | 정지 그림자 시험 A/B | `2026-10-20/outputs/run_vslam_static.txt` |
| f2v1(10-20) | 그림자 UDP — −20 %, 입력 빠짐 | `2026-10-20/outputs/run_f2v1.txt` · `chk_f2v1_logs.txt` · `anal_shadow_f2v1.txt` · 로그 `f0_f2v1_1020.log` |
| f2sm1 | 그림자 SHM — −33 % | `2026-10-21/outputs/run_f2sm1.txt` · `anal_shadow_f2sm1.txt` · `gaps_f2sm1.txt` · bag `2026-10-21/bags/bag_f2sm1.tgz` |
| f2sm2 · f2sm2h | 사람 방해로 제외 · 복귀 · 멈칫 분류 | `2026-10-21/outputs/run_f2sm2.txt` · `run_f2sm2h.txt` · `anal_dip_events_f2sm2h.txt` |
| f2sm3 | 그림자 SHM — −41 % | `2026-10-22/outputs/anal_shadow_f2sm3.txt` · bag `2026-10-22/bags/bag_f2sm3.tgz` |
| f2pa1 · f2pa2 | PathAlign 28 주행의 그림자 지표 −31 · −33 % | `2026-10-23/outputs/anal_shadow_f2pa*.txt` · bag `2026-10-23/bags/bag_f2pa*.tgz` |
| f2von1 · f2von2 | `vslam:=on` 주 EKF — W3 16.8 · 13.2 cm | `2026-10-23/outputs/anal_ekf_f2von*.txt` · `run_f2von*.txt` · bag `2026-10-23/bags/bag_f2von*.tgz` |
| `anal_vslam_cmp.py` | 오프라인 cuVSLAM vs EKF(SLAM 기준 절대) | `2026-10-19/jobs/` |
| `anal_vslam_rpe.py` | 짧은 창 상대 오차 | `2026-10-20/jobs/` |
| `mk_ekf_replay_bag.py` · `mk_ekf_replay_params.py` · `run_ekf_replay.sh` · `anal_ekf_replay.py` | EKF 재실행 4 단 + 그림자 · on 지표(같은 도구) | `2026-10-20/jobs/` |
| `run_vslam_static.sh` · `chk_vslam_live.py` · `up_vslam.sh` | L0 · 배포 | `2026-10-20/jobs/` |
| `anal_topic_gaps.py` | bag 토픽 간격 | `2026-10-21/jobs/` |
| `anal_dip_events.py` · `anal_stops.py` · `chk_nav_ms.sh` | 멈칫 · 정지 분류 | `2026-10-21/jobs/` |
| `prep_von_1023.sh` · `up_prep_patrol_1023.sh` | on 시험 prep · 기본 채택 배포 | `2026-10-23/jobs/` |

## 9. 도구 해설
### 오프라인 cuVSLAM 4 단 — mk_vslam_bag.py → run_vslam_offline.sh → vslam_run_in.sh → export_vslam.py (Jetson 호스트 + Isaac 컨테이너, 10-19 §23)
- 왜: 기록된 IR 로 cuVSLAM 을 실시간 스택 없이(CPU 경합 배제) 여러 설정으로 돌려 보려고.
- `mk_vslam_bag.py IRbag 주행bag 출력bag [all_off]`(호스트): IR bag(분리 노드가 프로세스 안에서 기록)의 영상을 메타데이터 `frame_emitter_mode` 로 `/off/infra{1,2}/…` · `/on/infra{1,2}/…` 에 나누고(같은 stamp 의 camera_info), `/camera/imu` · 주행 bag 의 `/tf_static` 을 붙임. `all_off` = 상시 끔 기록(10-19 §25)이면 전부 `/off`.
- `run_vslam_offline.sh [이름] [all_off]`: 실시간 스택을 이름 목록으로 내림(base 유지, 로버 정지) → 입력 bag 만들기 → 컨테이너에서 `vslam_run_in.sh true|false` 두 판.
- `vslam_run_in.sh <imu> [입력]`(컨테이너 안): 도메인 42, `vslam_offline.launch.py imu:=…`(끔 · 켬 두 cuVSLAM 동시, `base_frame camera_link`, rectified, TF 끔) → 출력 4 토픽 기록 → 입력 bag 1 배속 `--clock` 재생 → 정리 → `export_vslam.py` 로 변형별 csv + vo_state 요약. `set +u`(4 행) — ROS setup 이 미정의 변수를 써서 첫 실행이 멈춘 뒤 고친 것.
- 출력: Jetson `~/workspaces/isaac_ros-dev/vslam/out_*` → PC `outputs/vslam_<이름>/*.csv`(저장소). 결함: 러너가 끝 정리에서 멈춰 시간 초과(결과는 나옴 — 10-19 §23.1). 재사용: IR bag 이 있으면 가능.

### anal_vslam_cmp.py — 오프라인 cuVSLAM vs EKF 절대 오차 (PC, Python rosbags)
- `anal_vslam_cmp.py 주행bag csv폴더 출력.png [정렬시각]`. 기준 = SLAM 사슬의 camera_link 평면 자세, EKF = 같은 사슬에서 map→odom 을 첫 값으로 고정(= odom 좌표 EKF). 각 추정의 첫 시각(또는 정렬 시각, 10-20 §3 추가)에서 SLAM 자세에 맞추고 그 뒤 끼워 맞춤 없음. 출력 줄: 추적 성공 % · 위치 오차 끝 · 95 % · 최대 · yaw 오차 끝 · 구간 증가(t60~80 · t160~210) · 출력 개수(Hz), 10-20 부터 yaw \|95 %\| 줄 추가.
- 쓰인 곳: 10-19 §23.1(불합격) · 10-20 §1 · §3.1(재현). 결함: 끝 오차는 같은 길 왕복에서 상쇄돼 과소(10-20 §1 이 '95 % 가 공정' 이라 밝힘). 구간 시각 고정. 계보 → `anal_vslam_rpe.py`(상대) → `anal_ekf_replay.py`.

### anal_vslam_rpe.py — 짧은 창 상대 오차 (PC, 10-20 §4)
- `anal_vslam_rpe.py 주행bag csv폴더 [Δ=10]`. 왜(머리말 3~4 행): 상자 기억 밀림은 절대 오차가 아니라 '상자를 본 뒤 지나가는 ≈ 10 s' 에 쌓이는 오도메트리 오차가 만든다(10-19 §14). Δ 창을 1 s 간격으로 밀며 로버 몸 기준 상대 변환 차(위치 · 옆 성분 · yaw), 구간 = 전 구간 · 복귀 회전 t160~210 · 상자 옆 출발 t18~36 · 복귀 t180~200. Δ 10 · 3 두 판.
- 출력 [`anal_vslam_rpe.txt`](../debug_log/2026-10-20/outputs/anal_vslam_rpe.txt). 영향: 'yaw 만 융합은 상자에 무효' 예상 → 재실행으로 확인. 한계: 기준 SLAM 자체가 10 s 창에 2~3 cm 흔들림(추정) — 그 아래 차는 판정 안 함.

### EKF 오프라인 재실행 4 단 (PC WSL ROS Humble · robot_localization, 10-20 §5)
- `mk_ekf_replay_bag.py 주행bag cuVSLAM_csv 출력bag [b3=1]`: 주행 bag 의 `/wheel_odom` 에 컨디셔너 공분산(vx 0.02² · vy 0.01² · vyaw 0.1²) + B3(|vx| < 0.02 · |ω| > 0.10 이면 vx · vy 0.3², ω = 0.1 s 안의 자이로 `−/imu/data y` 아니면 휠) → `/wheel_odom/conditioned`, 기록된 `/imu/data` · `/tf_static` · `/odom_rf2o/gated` 그대로, cuVSLAM csv → base_link 몸 기준 속도 `/vslam/odom`(중앙 차분 · 반 회전, 0.3 s 넘는 빠짐 건너뜀, 공분산 vx · vy 0.005² · yaw 0.02²). 기록 시각 = 원래 bag 시각.
- `mk_ekf_replay_params.py ekf.yaml 출력.yaml [live]`: V0 ~ V3(odom1 = `/vslam/odom` 의 축만 다름), `live` 면 rf2o 를 odom1 · cuVSLAM 을 odom2 로, V4 = odom1 을 cuVSLAM 으로 바꿈. 모두 `publish_tf false` · `use_sim_time true`.
- `run_ekf_replay.sh 입력bag 출력bag params.yaml`: `ROS_LOCALHOST_ONLY=1` · 도메인 87(Jetson 과 안 섞임), EKF 변형마다 `ekf_node __node:=ekf_vN` → `/ekf/vN`, 기록 → `ros2 bag play --clock 100`(1 배속, `/tf_static` transient_local QoS 덮기) → 정리(21 행 `pkill __node:=ekf_v` — 실수 2 뒤 추가).
- `anal_ekf_replay.py 주행bag 재실행bag cuVSLAM_csv|- [그림]`: §2.1 ⑤ 의 10 s 창(1 s 간격, t0 + 20 s 부터) · 구간 3 개 · t = 20 s 정렬 절대 오차. **그림자 · on 주행에도 같은 도구** — `RTOPICS=/odometry/ekf_vslam` 이면 재실행 bag 자리에 주행 bag 을 주고 그 토픽만, cuVSLAM 은 `-` 로 bag 의 `/visual_slam/tracking/odometry`(6~7 · 37~55 행). 이름표 '재실행 EKF_VSLAM' 은 이때 실시간 그림자 EKF.
- 결함 · 한계: ① 'W3 회전' · '상자 옆' 구간이 **bag 시각 고정**(t105~125 · 18~36 · 180~200) — 코스 · 목표 시간이 비슷한 b910 에서만 맞다(목표 1 · 2 합 ≈ 100~105 s). 다른 코스나 출발이 늦은 주행엔 그대로 못 씀 ② 재실행 V0 는 실시간과 다른 입력이면 계통적으로 어긋남(실수 1) — 재현성 기준을 먼저 본다 ③ 기준 SLAM 의 흔들림. 재사용: b910 주행 bag(`/odometry/filtered` · `/tf`)이면 가능 — 10-23 까지 9 주행에 씀.

### run_vslam_static.sh · chk_vslam_live.py — 정지 그림자 시험 (Jetson, 로버 안 움직임, 10-20 §6.1)
- `CONFS="A B" bash run_vslam_static.sh`: A = `SENSORS_ADD="emitter_off:=true"`, B = + `vslam:=shadow` 로 `prep_patrol.sh lite` → 20 s → `chk_vslam_live.py 60` → EKF 주기 위반 수 차(`Failed to meet update rate` in `/tmp/sensors.log`) → B 면 cuvslam_up · cuVSLAM 로그 · vslam_twist 10 s 통계 줄.
- `chk_vslam_live.py [초]`: 노드 1 개로 4 토픽 주기 · 처음 → 끝 이동, `/proc` 로 전체 CPU(6 코어 = 100) · 프로세스별(코어 1 = 100, 명령줄 패턴 `__node:=cuvslam_container` · `vslam_twist.py` · `__node:=ekf_vslam` 등).
- 출력 [`run_vslam_static.txt`](../debug_log/2026-10-20/outputs/run_vslam_static.txt)(1 · 2 · 3 차와 `chk_vtwist.sh` top 발췌). 영향: vslam_twist 193 % 발견 → OpenBLAS 1 스레드. 계보: 10-20 §9.2 SHM 정지 A/B(`run_shm_static.sh`, [SHM 카드](camera-container-shm.md)).

### anal_topic_gaps.py — bag 토픽 간격 (PC, 10-21 §7)
- `anal_topic_gaps.py bag 토픽…` → 토픽마다 개수 · 평균 Hz · 0.5 s 넘는 끊김 · 최대 간격과 그 시각(bag 기록 시각 — 기록기 지연 포함, 10-20 §9.6 '≤ 2' 가 그 몫을 감안). 출력 `gaps_f2sm1.txt` · `gaps_f2sm3.txt` · `gaps_f2pa*.txt` · `gaps_f2von*.txt`.

### anal_dip_events.py · anal_stops.py · chk_nav_ms.sh — 멈칫 · 정지 분류 (PC + Jetson 로그, 10-21 §11.3 · §12.2)
- `anal_stops.py`: EKF |v| < 0.01 · |ω| < 0.05 가 MIN_STOP 넘게 = 정지, 그때 `/cmd_vel` · 앞 라이다 · nav2 사건. `anal_dip_events.py bag nav_events_ms.txt`: `/cmd_vel` 전진 명령이 0.01 아래로 떨어진 묶음(0.5 s 안이면 한 묶음, 20~22 행)마다 앞 2 s ~ 뒤 0.5 s 의 nav2 사건(0.01 s 시각, `chk_nav_ms.sh` 가 Jetson nav2.log 에서 뽑음)과 명령값 흐름. 출력 예 [`anal_dip_events_f2von1.txt`](../debug_log/2026-10-23/outputs/anal_dip_events_f2von1.txt) `== 멈칫 12:27:47.15 … +0.04 s controller_server Exception in transformPose: Lookup would require extrapolation into the future.`(= A). 영향: `vslam:=on` 판정 4 의 멈칫 수. 한계: nav2.log 는 prep 이 덮어 원천 소실되기 쉬움(10-21 §23).

### 러너 게이트 A · B 수정 (Jetson, bash — `job551_f0drive.sh`)
- 10-20 §6.4: 게이트 A '중복 프로세스' 의 `ekf_node` 기대 수 = 1 + `ekf_shadow_a` 수 + `ekf_vslam` 수(10 행). 10-20 §9.7: 게이트 B `timeout 6 → 12 ros2 topic hz /wheel_odom`(12 행 주석). 해설 본체는 [F2 순회 카드 §9](f2-patrol-loc-jump.md) · [운용 카드](drive-ops-1019-1023.md).

## 10. 용어
- **cuVSLAM(isaac_ros_visual_slam)**: NVIDIA 의 스테레오 영상 오도메트리 · SLAM(GPU). 여기선 D455f 좌우 IR(640×480, 15 fps)을 받아 `/visual_slam/tracking/odometry`(camera_link 자세)만 쓰고 TF · 지도는 안 씀.
- **프로젝터(이미터) 상시 끔 · 번갈이**: D455f 의 점 무늬 IR 프로젝터. 켜면 깊이가 좋아지지만 카메라와 함께 움직이는 점이 영상 오도메트리의 '가짜 고정 특징' 이 된다. 번갈이 = 프레임마다 켬 · 끔 교대(10-19), 상시 끔 = 10-21 결정.
- **vo_state**: cuVSLAM 상태 메시지의 추적 성공 표시. '성공' 이어도 이동을 0 으로 내는 경우가 있다(10-19 §23.1).
- **IMU 융합(enable_imu_fusion)**: cuVSLAM 이 카메라 IMU 를 함께 쓰는 설정 — 이 시스템에선 꺼 둠(10-20 §3.1).
- **그림자 EKF(`ekf_vslam`)**: 주 EKF 와 같은 입력에 cuVSLAM 만 더한 두 번째 EKF. TF 를 안 내 제어에 끼어들지 않고 `/odometry/ekf_vslam` 으로만 냄 — 같은 주행 안에서 효과를 비교하는 장치.
- **10 s 창 상대 오차**: 10 s 동안 추정이 움직였다고 한 양과 SLAM 이 본 양의 차. 기억된 장애물이 로버 기준으로 밀리는 크기와 같은 시간 규모라 고름(절대 오차는 SLAM 이 지도 층에서 고침).
- **W3 되돌아 회전**: b910 코스(B → W3 → 출발)에서 W3 목표 도착 뒤 출발점 쪽으로 도는 제자리 회전. 이 코스에서 미끄러짐이 가장 큰 구간이라 주 지표로 씀(bag 시각 t105~125).
- **V0 ~ V4**: EKF 재실행 변형 — V0 주행 구성 · V1 + yaw 속도 · V2 + vx · vy · yaw · V3 + vx · vy · V4 rf2o 대신 cuVSLAM vx · vy(운용 = V4).
- **OpenBLAS 바쁜 대기**: numpy 가 쓰는 선형대수 라이브러리의 일꾼 스레드가 작은 연산마다 깨어나 CPU 를 태우는 현상. `OPENBLAS_NUM_THREADS=1` 로 막음.
