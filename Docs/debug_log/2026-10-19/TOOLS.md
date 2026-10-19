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
