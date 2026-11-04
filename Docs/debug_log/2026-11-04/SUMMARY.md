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
