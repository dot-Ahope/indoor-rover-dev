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
| §1.5 ② | 같은 것, 영문 낱말 · 링크 확인 | `jobs/chk_config_1110d.sh`(덧붙인 판) → `outputs/chk_config_1110d2.txt` | 'step' 1 · `lrwxrwxrwx … -> build/…` | 최신 빌드 | ✔ |
