# 2026-10-29 도구 (상황 → 도구 → 나온 값 → 그때의 추론, 나중에 ✔/✘/？)

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 판정 |
|---|---|---|---|---|---|
| 0 | 하루 시작 | `jobs/chk_day_start_1029.sh` | 대화 기록: 가동 6 h · 스택 꺼짐 | 밤사이 재부팅 → 밤새 드리프트 원천 소실 | ✔ |
| 0 | 어제 ZUPT 이력 | (grep) | `outputs/zupt_f2pl5_sensors.txt` | 출발 전 ZUPT 정상, 주행 뒤 구간 없음 | ✔ |
| 1~3 | 정지 기록 | `jobs/up_drift_rec_1029.sh` → `jobs/chk_drift_rec_1029.sh` · 회수 `jobs/up_fetch_drift.sh` | `bags/bag_d1.tgz` · `outputs/drift_d1.log` | — | ✔ |
| 2 | 원천별 yaw rate 실시간 | `jobs/chk_yaw_drift.py` | 대화 기록(§2 표): 원시 +2.14 · 조건 +0.02 °/min | ZUPT 가 지움 | ✔ |
| 2 | 맞던 주행의 라이다↔지도 분포 | `jobs/anal_scan_align_bag.py` · `jobs/anal_scan_align_sum.py` | `outputs/scan_align/*` 최소 0.594 · 최대 3.0° · f2pl1 출발 −7° | ⓐ 문턱 0.40 · 4° · 0.03 | ？(실동작 전) |
| 3 | d1 원천 가르기 | `jobs/anal_drift_bag.py` | `outputs/anal_drift_d1.txt` EKF 0.07° | 정지만으로는 재현 안 됨 | ✔ |
| 4 | d2 실행기(미실행) | `jobs/run_d2_1029.sh` | — | — | — |
