# 2026-11-11 도구 사용 기록

규약 README §3.3. 로버 주행 없음. Jetson 실행은 스크래치패드 러너 `run_jn.sh`(JETSON_HOST=<LAN-B>.110).

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 뒤 판정 |
|---|---|---|---|---|---|
| §0 | f2dm2 bag · 러너 원문이 남았나 | `jobs/chk_f2dm2_left_1111.sh` → `outputs/chk_f2dm2_left_1111.txt` | 부팅 10:51:52 · /tmp 에 f2dm2 없음 · 홈 사본 없음 | 재부팅으로 원천 소실 | ✔ |
| §0 | 남은 ROS 로그(launch.log) | `jobs/chk_roslog_f2dm2_1111.sh`(1 차) → `outputs/chk_roslog_f2dm2_1111.txt` | Nav2 launch.log 17 줄 | 노드가 output=screen 이라 launch.log 엔 없음 | ✘ → 노드별 로그로 |
| §0 | 노드별 rcl 로그 | `jobs/chk_roslog_f2dm2_1111.sh`(고친 판) → `outputs/chk_roslog_f2dm2_1111b.txt` | 파일 40 개 · 2752 줄 · 목표 1 · 2 성공, 3 시작 | 목표 단위 재구성 가능 | ✔ |
| §1 | 목표 2 ~ 3 의 사건 순서 | `jobs/chk_roslog_window_1111.sh 17:55:00 17:58:05` → `outputs/chk_roslog_window_1111.txt` | 막힘 정지 3 · Smac 실패 1 · 스무더 충돌 1 · 탈출 1 · 주기 놓침 23 | 출발 방 B → C 물체 옆으로 비용 99 경로 | ？(f2dm1 같은 구간과 비교 전) |
| §5 | 판정 ③ nav2 로그 집계 | `jobs/chk_nav2_run_1111.sh` → `outputs/chk_nav2_f2rr1.txt` | TF 외삽 1 · 막힘 정지 2 · 탈출 1 · 주기 놓침 43 | TF 1 줄 확인 필요 | ✔ |
| §5 | TF 줄 원문 | `jobs/chk_tf_line_1111.sh` → `outputs/chk_tf_line_f2rr1.txt` | Nav2 설정 중(첫 목표 108 s 전) nvblox 층 1 회 | 주행 중 0 | ✔ |
| §5 | 시작 → 출발 시간 | `jobs/chk_live_marks_1111.sh` → `outputs/chk_live_marks_1111.txt` | prep 85 s · 대화 11 s · 게이트 39 s · 첫 목표 8 s | 약 2 분 25 s | ✔ |
| §6 | 탈출 장면 사건 | `jobs/up_nav_events_1111.sh` → `outputs/nav_events_f2rr1.txt` | 127 줄 · 막힘 → 탈출 → 새 목표 0.15 s | 움직임 없는 탈출 | ✔ |
| §6 | 탈출 장면 영상 | `Docs/tools/fig_drive_video.py` → `videos/f2rr1_escape_1500.mp4` · `figures/f2rr1_escape_t*.png` | BT 경로 1 · Smac 경로 10 · 350 프레임 | 상자 띠를 크게 돌아가는 새 경로 | ✔ |
| §7 | 표준 변경 배포 · 기본값 확인 | `jobs/up_std_1111.sh`(base64 내장) → `outputs/up_std_1111.txt` | md5 PC = Jetson · 설치본 링크 · `replan_hz` 0.01 · `planner` smac | 배포 반영 | ✔ |
| §8 | 하루 정리 페이지 조립 | `jobs/fig_report_1111.py`(머리 `2026-10-28/jobs/report_1028_head.html` + 본문 `jobs/report_1111_body.html` + 그림 3 장 data URI) → `figures/day_summary_1111.html` | 902 kB | 게시 원본 | ✔ |
