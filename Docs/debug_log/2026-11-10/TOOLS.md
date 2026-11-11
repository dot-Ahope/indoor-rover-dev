# 2026-11-10 도구 사용 기록

규약 README §3.3. 로버 주행 없음 · 코드 수정 없음. Jetson 실행은 모두 스크래치패드 러너 `run_jn.sh`(JETSON_HOST=<LAN-B>.110, 하루 시작 때 `touch`).

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 뒤 판정 |
|---|---|---|---|---|---|
| §0 | CURRENT_STACK 값이 코드와 같은가 | (대화의 PowerShell 한 번 — 문서가 적은 파일:줄을 뽑음, 원문 없음) | 약 45 값 일치 · 줄 번호 2 곳 한 줄 어긋남 | 문서 최신 | ✔ |
| §1.1 | 어느 주소가 살아 있나 | (PC ping, 비밀번호 안 보냄) | <LAN-A>.8 False · <LAN-B>.110 True | 예약 주소로 돌아옴 | ✔ |
| §1.1~1.4 | 신원 · src md5 · 설치본 · /tmp 도구 · 실행 상태 | `jobs/chk_config_1110.sh` → `outputs/chk_config_1110.txt` | jetson-desktop · 부팅 14:25 · base 만 · /tmp 도구 0/7 · 32 LINK | 재부팅 직후, 스택 미기동 | ✔ |
| §1.4 | src 가 HEAD 와 같은가 | `jobs/anal_src_cmp_1110.sh` → `outputs/chk_config_1110_cmp.txt` · `_diff4.txt` | SAME 58 · DIFF 4 · JETSON만 43(백업) · PC만 0 | 동작 파일은 같음 | ✔ |
| §1.2 | rover-base 가 꺼졌나 | `chk_config_1110.sh` ⑤ `systemctl is-active` | inactive · 사용 설정 빈칸 | 손으로 띄웠나 | ✘(§1.5 ① — 사용자 단위 서비스) |
| §1.3 · §1.4 | 'Up 5 days' 모순 · 차이 4 파일 원문 · 기동 경로 | `jobs/chk_config_1110b.sh` → `outputs/chk_config_1110b.txt` | Created 11-04 · 프로세스 14:25 · 자동 기동 줄 sed 오류 | 부팅 직후 시계(추정) | ？(시계 원인 미확인) |
| §1.5 ① | base.launch 를 누가 띄웠나 | `jobs/chk_config_1110c.sh` → `outputs/chk_config_1110c.txt` | 부모 `systemd --user` · `user: rover-base.service enabled` | 사용자 단위 서비스 | ✔ |
| §1.5 ② | BT 플러그인이 옛 빌드인가 | `jobs/chk_config_1110d.sh` → `outputs/chk_config_1110d.txt` | install = build 링크 · only_new 1 · step 설명 0 | step 0 은 한글 설명이라 못 잡은 것일 수 | ？ → 2 차 |
| §3 | 학습식 6D 자세용 Jetson 자원 | `jobs/chk_ml_capacity_1110.sh` → `outputs/chk_ml_capacity_1110.txt` | 7607 MB 중 6435 가용(스택 없음) · 15W · Isaac ROS 이미지 43 GB 급 | FoundationPose(여유 7.5 GB 요구)는 불가 | ✔(포럼 수치와 대조) |
| §3 | 주행 중 메모리 · GPU | (대화의 PowerShell 집계, 원문 `2026-10-28/outputs/drives/f2tt2/f0_f2tt2/tegra_f2tt2.log`) | RAM 2909~3104 MB · GR3D 평균 10 % | 주행 중 여유 약 4.5 GB(계산) | ？(다른 날 구성) |
| §4 | 주행 성공률 · 사이클타임 표 1 차 | `Docs/tools/anal_drive_results.py`(새 상시 도구) | 91 주행 · 300 목표 · 실패 상태에 SUCCEEDED_XY · (0,0) 소요 39.8~157 s | SUCCEEDED_XY 정체 · 구간 묶음 의심 | ✘(성공을 실패로 셈 · 구간 정의 잘못) |
| §4 | 같은 것, 고친 판(성공 정의 · 취소 원인 · 구간 쌍 · 기간 표) | 같은 도구 → `outputs/anal_drive_results.txt` · `_runs.csv` · `_goals.csv` | 57/91 주행 · 267/300 목표 · 마지막 기간 18/18 · 표준 구간 52 · 49 · 104 s | 성공률은 개선, 시간은 속도 상한(vx_max 0.08)이 정함 | ✔(중복 0) · 시간 원인은 ？(추정) |
| §5 | 주행별 접촉 분류(91) | (에이전트가 날짜별 SUMMARY · anal_contact 를 읽음, 근거 file:line) → `jobs/anal_contacts_table_1110.py` → `outputs/anal_drive_contacts.csv` | 1 차 접촉 11 · 없음 48 · 미상 32 | 바닥 전선 · 코스트맵 지표만 · '확인 필요' 가 섞임 | ✔ 인용 18 줄 대조 일치 · 기준대로 고쳐 장애물 6 · 바닥 4 · 없음 38 · 미상 43 |
| §5 | 성공률 표에 접촉 합치기 | `Docs/tools/anal_drive_results.py`(접촉 csv 읽게 고침) → `outputs/anal_drive_results.txt` | 성공 57 중 장애물 접촉 4 · 접촉 없음 확인 31 | SUCCEEDED ≠ 접촉 없는 성공 | ✔ (첫 열 검사는 내 awk 열 번호 실수 — 11 열이 접촉, csv 로 다시 확인) |
| §1.5 ② | 같은 것, 영문 낱말 · 링크 확인 | `jobs/chk_config_1110d.sh`(덧붙인 판) → `outputs/chk_config_1110d2.txt` | 'step' 1 · `lrwxrwxrwx … -> build/…` | 최신 빌드 | ✔ |
