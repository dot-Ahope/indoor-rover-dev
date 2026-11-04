# 2026-11-04 — Jetson 준비 · push · 주석 정정 · 문제 대장 9 기 (로버 주행 없음)

## §0 하루 시작 (사용자: "jetson 실행했다. 확인 스크립트 실행해라." → "추천 순서대로 진행하라.")
- Jetson 09:09 부팅(uptime 5 분 @ 09:14), 192.168.0.110. 보드 드라이버 확인은 11-03 §11.1 에 적음.
- 순서(사용자 승인): ① Jetson 준비 ② push ③ 8 기 어긋남 · 낡은 주석 정정 ④ 문제 대장 9 기.

## §1 Jetson 준비 — 도구 재전송 · 설치본 링크 복구
- `Docs/tools/up_tools.sh` 고침: 예전 판은 스크래치패드 `tools/`(10-22 소실)를 읽어 옛 판이 올라갈 수 있었다 → 저장소 `Docs/tools` 판을 복사해 올림 · 옛 up950 묶음(job240 등, 지금 안 씀) 뺌 · 끝에 Jetson 쪽 파일 수와 `prep_fast.sh` 의 `--follow-symlinks` 줄 수를 찍음. 실행 결과:
```
  저장소 판 ce1a0bee → …/scratchpad/tools (7 개)
  Jetson /tmp: 7 개 · prep_fast --follow-symlinks 줄 2
```
- 설치본 설정 링크 확인(`jobs/chk_install_links_1104.sh` → `outputs/chk_install_links_1104.txt`): amcl · nvblox_local · BT xml 2 개는 링크, **nav2_params.yaml 만 일반 파일**(2026-10-29 15:52, 내용은 src 와 같음 · PreferForward 15.0 둘 다) — 10-15 §30 의 옛 `sed -i` 흔적.
- 복구(`jobs/up_install_link_1104.sh` → `outputs/up_install_link_1104.txt`): 내용이 src 와 같을 때만 백업(`/tmp/nav2_params_install_backup_1104.yaml`) 뒤 `ln -s` — "링크로 복구: …/src/rover_navigation/config/nav2_params.yaml". sudo 없음.
- Jetson src ↔ 저장소 비교(`jobs/chk_src_md5_1104.sh` · `chk_src_strip_1104.sh` · `anal_src_strip_md5.py` → `outputs/chk_src_md5_1104.txt` · `chk_src_strip_1104.txt`): 8 파일 중 6 개가 다르지만 주석을 빼면 `pad_relief.py` 만 다름(11-03 §3 노드 기본 mode 'on' → 'off'). 표준 prep 은 이 노드를 안 띄우므로 주행 영향 없음 — Jetson src 는 그대로 둠(다음 배포 때 같이).

## §2 push (사용자 승인 순서 ②)
- `git fetch . feature/smac-hybrid:feature/nvblox-migration` → `git push personal …` : d72968a7..8ec8aa13(두 가지).
- `bash private/publish_public.sh`: "점검: 문구 0 · 옛 이메일 0 · 비공개 경로 0 · 비밀번호 0" → 공개 dev 334d638..120cf0f(원본 8ec8aa13). main 은 그대로(--push-main 안 씀).

## §3 8 기 어긋남 · 낡은 주석 정정 (순서 ③ — 11-03 §9 목록)
- 코드 주석(동작 변경 없음, `jobs/up_comment_fix_1104.py` — 정확한 문자열 치환 · 한 번씩): `nvblox_local.yaml` 통합 거리 꼬리 주석의 1.4 근거 · min_weight 기각 근거 추가 · site_distance 설명 위치 표시 · '먼 비스듬한 첫 관측' → 10-19 §14 분해 · `camera.launch.py` emitter_off '오프라인 확인용' → 운용 기본(launch 기본값은 false) · 데시메이션 '확인 중' → 10-20 §8.3 대책 아님 · `fastdds_udp_only.xml` SHM '원인 제거' 에 10-20 §7.2 범위 정정 · `path_blocked_ahead_condition.cpp` 21 행 '목표 5 에 52 s' → 10-23 §20.7(목표 4) · 러너 `2026-11-03/jobs/job551_f0drive.sh`(+ 스크래치패드 실행본) BAG_IR 조건에 emitter_off. 검사: yaml 읽기 · py_compile · xml 파싱 · bash -n 모두 통과(PARSE_OK). Jetson src 에는 아직 안 올림(주석만 — 다음 배포 때).
- 기록 정정 표시(원문 유지, `jobs/up_record_marks_1104.py` 줄 끝에 '→ 2026-11-04 §3 정정'): 10-19 §23.1 조명 원인 · §22 '남쪽 15.7 cm' · §20 mp4 'git 제외' · 10-21 §11.1 mp4 · 10-20 §9.7 ttyUSB0 · §7.3a 표(표 아래 줄) · 10-22 §21 f2sm3 검증 · 10-23 §17.1 표(표 아래 줄) · §21 15.4 두 줄 · §22.2 Smac 비교 무효 · `Docs/06_planner/SMAC_HYBRID_PLAN.md` §2 · §8.
- 안 한 것(결정 대기 또는 다음): MAC 가림(10-21 SUMMARY 31 행 · `2026-10-22/outputs/chk_wifi_1022.txt` 외 추적 파일 73 개) · mp4 2 개 git 제외 · `prep_fast.sh` 70 행 SHM 오류 검사에 cuvslam · nvblox 로그 넣기 · only_new × 재계획 0.5 Hz 조합 시험.
