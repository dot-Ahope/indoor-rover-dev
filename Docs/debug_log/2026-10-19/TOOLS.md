# 2026-10-19 TOOLS

| 시각 · § | 상황 | 도구 | 값 | 추론 ✔/✘/？ |
|---|---|---|---|---|
| 10:5x · §0 | 하루 시작 상태 | `jobs/chk_day_start.sh` | 09:38 재부팅, prep 5 개 없음 → 재전송, 디스크 151 GB | ✔ |
| 11:0x · §1 | 깊이 토픽 실측 | `jobs/chk_depth_topic.sh` | 160×120 · 14.99 Hz · 581 KB/s, 발행 reliable+transient_local | decimation ×4 가 깊이 이미지에도 ✔ · 주석 정정 |
| 11:03 · §1 | 정지 30 s 깊이 기록 | `jobs/rec_depth_test.sh` | 427 장 14.98 Hz 누락 0, 16.7 MiB | 기록 부담 없음 ✔ |
| 11:1x · §2 | 깊이 bag → nvblox 재생 | `jobs/run_nvblox_replay.sh` | 깊이 콜백 15.2 Hz, 조각 270 / 29 s | 경로 동작 ✔ · 충실도 ？(R0) |
| 11:3x · §4 | 기존 주행 조각으로 과장 | `jobs/anal_slice_box.py` | 북쪽 면 +5.3~+9.5 cm(코스트맵 판과 같음) | 과장은 nvblox 출력에서 ✔ |
| 11:1x · §6 | 깊이 기록 주행 f2x1 | `run_f2c.sh`(BAG_DEPTH=1) | 3/3 성공, 깊이 3159 장 누락 0 | ✔ |
| 11:2x · §6 | R0 재생 충실도 | `run_nvblox_replay.sh`(--topics 수정) · `anal_slice_box.py` | 실시간 = 재생(+5.3 · 범위 · 칸 수 같음) | 재생 신뢰 ✔ |
| 11:3x · §6 | 설정 A/B 4 가지 | 같은 도구 · `chk_replay_params.sh` | 통합 1.0 · site 1.0 변화 0, 복셀 0.025 +6.7~+6.9 | 설정으로는 안 줄음 ✘ |
| 11:4x · §7 | nvblox 깊이 전처리 | `chk_nvblox_preproc.sh` · `chk_replay_log.sh` | 켜면 abort(mask rows 0 vs 120) | 3.2.5 에선 못 씀 ✘ |
| 11:5x · §8 | 가장자리 화소 거른 bag | `depth_edge_filter.py` | 22 % 제거, 과장 그대로 +5.3 | 깊이 잡음 가설 ✘ |
| 13:0x · §10 | 원시 깊이 점으로 상자 면 | `anal_box_points.py` | 출발 정면 북 +1.7 · 서 +0.2 cm, 복귀 땐 남동쪽 회전 중에만 보임 · 옆 통과 땐 시야 밖 | 기록 위치 맞음 ✔ · (a) ✘ |
| 13:1x · §11 | 기억 밀림 | `anal_box_memory.py` | 통과 순간 +2.1~+7.3 cm 로버 쪽 | (c) 유력 ✔ |
| 13:2x · §12 | global_frame=map 재생 | `run_nvblox_replay.sh` | +7.0 cm(나빠짐) | 지도 좌표 기억 ✘ |
| 13:3x · §13 | 회전 중 프레임 빼기 | `depth_turn_filter.py` | 27 % 제외, +5.3 · 범위 같음 | 5 cm 척도 한계 ✔ — §6 판정도 재해석 |
| 13:4x · §14 | 연속값 분해 | `anal_box_points.py … 192.4` | 관측 남동 3~5 cm + 기억 북 +2.7~+6.1 → 순 약 +3 cm, + 칸 반올림 | (c) 주원인 ✔ · 복셀 0.025 결과 불일치 ？ |
| 14:0x · §15 | 분리 노드 배포 · 빌드 | `jobs/up_splitter.sh` | 첫 빌드 설치 실패(src 에 pad_relief.py 없음) → 보충 뒤 성공 · 재생 nvblox 고아 4 개 정리 | 재생 스크립트 종료 결함 ✔ 정정 |
| 14:1x · §15 | 분리 S1(정지, 60 fps 번갈이) | `jobs/run_split_s1.sh` · `anal_split_s1.py` | emitter_mode 1 = 실제 끔(깊이 0.32 vs 0.77, IR 점 0.6 vs 5.8) | 메타데이터 값 반대 ✔ → on_mode 0 |
| 14:2x · §15 | S1 재시험(on_mode 0) | 같은 도구 | 오분류 0 · 깊이 29.5 Hz · IR 26.6~26.9 Hz · 분리 CPU 12 % · 카메라 38 % | 나누기 ✔ · 전달 손실 · 카메라 부하 ？ |
| 14:3x · §16 | 번갈이 구성 정지 부하 S2 | `jobs/chk_flash_s2.sh` · `prep_flash.sh`(SENSORS_ADD) | ① CPU 45 % → ② 53 %(IR 21/30 Hz 도착) → ③ 기록 77 % · EKF 위반 +127 · IR 기록 8 Hz | 호스트 DDS 영상 전달 · 기록기가 병목 ✔ · 기록 주행 보류 |
| 15:0x · §17 | 합성 + 프로세스 안 기록 S3 | `chk_flash_s2.sh … 2`(record_path) | IR 도착 21 → 30 Hz · 기록 IR 29.6~29.9 Hz · CPU 54~56 % · EKF 위반 +7/+28 | 합성 효과 ✔ · EKF 기준은 ① 편차(+0~+13)를 몰라 잘못 정함 ？ |
| 15:2x · §18 | 큰 bag 정리 | `jobs/rm_s2_flash.sh` | s2_flash30rec 448 MB 삭제, 남음 146 GB | ✔ |
| 16:0x · §20 | IR 영상 | `fig_ir_extract.py`(Jetson) · `fig_ir_drive_video.py`(PC) | 끔 IR 밝기 20 · FAST 중앙 6, 창가만 수백 | 끈 IR 어둠 ✔ |
| 16:2x · §21~22 | 상자 확대 · 상자 안 칸 | `fig_box_zoom_cmp.py` · `anal_box_cells_in.py` · `anal_box_points.py` | f2y1 상자 안 8 → 1, 회전 중 관측 15.7 cm 남쪽, map→odom +41.7 cm | 미끄러짐 큼 ✔ · 구성 탓 ？ |
| 16:4x · §23 | 오프라인 cuVSLAM 켬/끔 × IMU | `mk_vslam_bag.py` · `run_vslam_offline.sh` · `anal_vslam_cmp.py` | 4 변형 모두 오차 1.4~11 m(EKF 0.4 m), vo_state 100 % 인데도 | 켬 = 0 에 붙잡힘 · 끔 = 못 봄 ✔ — 이 조명에선 못 씀 |
| 17:3x · §24 | IR 노출 · 게인(번갈이) | `run_ir_exposure.sh` · `chk_ir_exposure.py` · `chk_ir_exposure_diag.sh` | 수동 설정 드라이버 거부(errno 84), 자동 노출 끄면 두 프레임 모두 점 무늬 | 번갈이 중 노출 고정 불가 ✔ |
| 17:5x · §24.2 | IR 게인(프로젝터 상시 끔) | `chk_ir_gain_off.sh` | 게인 설정 됨, 밝기 44~45, 4 배 밝게 보면 장면 또렷 | FAST 절대 문턱이 과소 계산 — §20 '특징 없음' 과장 정정 |
