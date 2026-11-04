# 2026-11-03 도구 사용 기록

규약 README §3.3. 로버 주행 없음.

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 뒤 판정 |
|---|---|---|---|---|---|
| §1 | 7 기 묶음 F 가 10-14 '원천 소실' 끝 방향을 bag 으로 다시 셈 | `2026-10-14/jobs/anal_path_endyaw.py` → `outputs/anal_path_endyaw_*.txt` | f2s1 지도 기준 0.0° · 남서(고치기 전) 컨트롤러 0.0° / 계획기 −101.3° | 남서 정체도 TruncatePath 결함 | ✔ |
| §3 | 러너 QoS 블록이 BAG_BE_TRAJ=0 에서도 /tf 를 넣는가 | 블록만 떼어 bash 실행(대화 안, 출력은 §3 에 요약) | 1 · 0 모두 `/tf:` 1 줄 | 고친 판이 맞음 | ✔ (실주행 미확인) |
| §3 | prep 의 PreferForward 편집이 링크를 살리는가 | `jobs/chk_prep_sed_1103.sh` → `outputs/chk_prep_sed_1103.txt` | 15.0 → 그대로 · 링크 유지 / 5.0 → 바꿈 · 링크 유지 | 고친 판이 맞음 | ✔ (Jetson 미확인) |
| §1 | 7 기 카드 머리 표 '관련 문제' 링크 덧붙임 | `jobs/up_issue_links_p7.py`(이미 있으면 건너뜀) | 링크 18 장 | — | ✔ |
| §9 | 8 기 카드 머리 표 '관련 문제' 링크 덧붙임 | `jobs/up_issue_links_p8.py`(값 줄에 이미 있으면 건너뜀) | 34 장 추가 · 4 장 건너뜀 | — | ✔ |
| §9 | ISSUES.md 8 기 표 넣기 | `jobs/up_issues_table_p8.py` → `python Docs/tools/anal_record_index.py` · `chk_record_rules.py` | 색인 SECTIONS 1460 · RUNS 123 · JOBS 1895 · RULES_OK | — | ✔ |
| §11 | 보드 장치 이름이 ttyUSB0 → ttyCH341USB0 로 바뀐 원인 — 드라이버 출처 | `jobs/chk_serial_driver_1103.sh`(Jetson 읽기만, run_jn.sh) | 실행 못 함 — Jetson 핑 100 % 손실 · scp lost connection | — | ✔ 11-04 실행 → §11.1 |
| §11.1 | 커널 패키지가 ch341.ko 를 갖나 · 설치 시각 | `jobs/chk_serial_driver_1104b.sh`(읽기만) → `outputs/chk_serial_driver_1104b.txt` | 패키지 모듈 5 개에 ch341 없음 · ch341.ko 2026-02-27 · 커널 설치 2026-02-20 | 벤더 드라이버 손 설치 | ✔ |
