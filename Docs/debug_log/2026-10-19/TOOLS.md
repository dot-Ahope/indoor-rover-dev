# 2026-10-19 TOOLS

| 시각 · § | 상황 | 도구 | 값 | 추론 ✔/✘/？ |
|---|---|---|---|---|
| 10:5x · §0 | 하루 시작 상태 | `jobs/chk_day_start.sh` | 09:38 재부팅, prep 5 개 없음 → 재전송, 디스크 151 GB | ✔ |
| 11:0x · §1 | 깊이 토픽 실측 | `jobs/chk_depth_topic.sh` | 160×120 · 14.99 Hz · 581 KB/s, 발행 reliable+transient_local | decimation ×4 가 깊이 이미지에도 ✔ · 주석 정정 |
| 11:03 · §1 | 정지 30 s 깊이 기록 | `jobs/rec_depth_test.sh` | 427 장 14.98 Hz 누락 0, 16.7 MiB | 기록 부담 없음 ✔ |
| 11:1x · §2 | 깊이 bag → nvblox 재생 | `jobs/run_nvblox_replay.sh` | 깊이 콜백 15.2 Hz, 조각 270 / 29 s | 경로 동작 ✔ · 충실도 ？(R0) |
| 11:3x · §4 | 기존 주행 조각으로 과장 | `jobs/anal_slice_box.py` | 북쪽 면 +5.3~+9.5 cm(코스트맵 판과 같음) | 과장은 nvblox 출력에서 ✔ |
