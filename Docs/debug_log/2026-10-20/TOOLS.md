# 2026-10-20 TOOLS

| 시각 · § | 상황 | 도구 | 값 | 추론 ✔/✘/？ |
|---|---|---|---|---|
| 09:xx · §0 | 하루 시작 | `jobs/chk_day_start_1020.sh` | 재부팅 직후, /tmp prep 없음, f2z1 csv 있음 | ✔ |
| 09:xx · §1 | f2z1 cuVSLAM 판정 | `jobs/get_vso_f2z1.sh` · 10-19 `anal_vslam_cmp.py`(yaw 통계 추가) | IMU 끔: 95 % 25.7 cm · yaw 0.8° vs EKF 57.2 cm · 5.0° | 밝으면 따라감 ✔ · IMU 켬이 나쁜 이유 ？ |
| 10:xx · §2 | B 정지 시험(켬/끔) | `run_box_depth_ab.sh` · `anal_box_static.py` · `fig_box_static.py` | 깊이 아래 절반 65 → 38 %, nvblox 상자 칸 10 → 13 · 면 차 ≤ 0.4 cm · 유령 0 | 정지에선 B 통과 ✔ · 움직일 때 ？ |
| 오후 · §3.1 | f2z2 상자 · cuVSLAM | 10-19 `anal_box_cells_in.py` · `anal_slice_box.py` · `anal_vslam_cmp.py`(정렬 시각 인자) | 복귀 주변 칸 27 · yaw 1.1° vs EKF 3.3° | 끔 = 주변 잡음 칸 ↑ ？(1 회) |
| 오후 · §3.2 | f2z1 도 상자 있었음(사용자) → 면 과장 채움 | 10-19 `anal_slice_box.py` | 북 +4.6/+4.4 · 주변 칸 21 | 주변 잡음 칸 증가 2 회 재현 ✔ |
| 오후 · §4 | cuVSLAM 융합 효과 예상 — 짧은 창 상대 오차 | `jobs/anal_vslam_rpe.py` | 10 s yaw EKF 0.5~1.0° vs cuVSLAM 0.8~1.3°, 상자 옆 위치 EKF ≤ cuVSLAM, W3 회전 EKF 27 vs 12 cm | yaw 만 융합 = 상자 효과 없음(추정) ？ |
| 오후 · §5 | EKF 오프라인 재실행(WSL) — cuVSLAM 속도 융합 V0~V3 | `jobs/mk_ekf_replay_bag.py` · `mk_ekf_replay_params.py` · `run_ekf_replay.sh` · `anal_ekf_replay.py` | V0 vs 기록 f2z1 끝 8.7 cm 차(회전 때만), 재실행끼리 0.2 cm; V2/V3 W3 최대 −34 %, 상자 옆 변화 없음 | yaw 만 융합 무효 ✔ · 병진 융합은 미끄러짐만 ✔ · 실시간과의 차 원인 ？ |
| 오후 · §5.2–5.3 | 재실행을 주행 구성(rf2o + B3)으로 | `mk_ekf_replay_bag.py`(B3 · rf2o) · `mk_ekf_replay_params.py live` | V0 = 기록 EKF 재현(17.0/17.1) · cuVSLAM 병진 W3 −12~29 % · V4(rf2o 대신) 같음 | §5.1 의 V0 는 구성 누락 ✘ → 정정 ✔ |
| 오후 · §6 | cuVSLAM 실시간 그림자 구성 | `rover_bringup` ekf.launch `vslam:=` · `cuvslam_up.sh` · `cuvslam_container.launch.py` · `vslam_twist.py`, `jobs/up_vslam.sh` · `run_vslam_static.sh` · `chk_vslam_live.py` | L0: OpenBLAS 바쁜 대기(코어 2 개) 수정 뒤 CPU +7~9 %p · 13 Hz · 정지 0.3 cm | 그림자 주행 가능(CPU 경계) ？ |
| 오후 · §6.4 | f2v1 그림자 주행 비교 | `anal_ekf_replay.py`(RTOPICS · '-' = 실시간 cuVSLAM) · `chk_f2v1_logs` | W3 27.5 → 22.1 cm(−20 %), /vslam/odom 주행 중 9.5 Hz · 끊김 38 | 효과 ✔ · 입력 빠짐 ✘ — IR 전달 ？ |
| 저녁 · §7.3 | SHM 재기동 시험 | `jobs/shm_test/*`(talker · listener · run_shm_test · chk_shm_path) | 정리 없이 15/15 · clean 30/30 · SHM 전용은 UDP 참가자 발견 못 함 | 종료 방식 문제 ✔ · SHM 경로 ✔ |
| 저녁 · §7.5 | UDP 크기별 빠짐 | `jobs/shm_test/chk_udp_size.sh` | 38 kB 15.0 · 307 kB×2 12.8~14.8 · 614 kB 13.3~14.1 Hz | 깊이 무손실 = 데시메이션 크기 ✔ |
| 저녁 · §8 | 깊이 해상도 정지 A/B | `anal_box_face_points.py` · `run_decim_ab.sh` · `anal_box_static.py` | nvblox 면 차 ≤ 0.7 cm, d4b SLAM −41° | 해상도는 번짐 대책 아님 ✔ · 위치 추정 실패 ？ |
| 저녁 · §9 | N-SHM S1~S3 | `dds_shm:=` · `run_shm_static.sh` · `run_shm_restart.sh` · `chk_udp_drops2.sh` | 13 → 15.0 Hz · 경고 101 → 1 · 재기동 10/10 | SHM 채택 후보 ✔ · 주행 S4 ？ |
| 저녁 · §9.7 | f2sm1 게이트 | `chk_gateb.sh` · `chk_hz_time.sh` | topic hz 첫 출력 4.5~5.6 s(한도 6), 정지 부하 62 % | 게이트 B 한도 12 s ✔ · P 판단 ？ |
