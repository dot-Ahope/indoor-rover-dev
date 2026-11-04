---
name: rover-jetson-run
description: Jetson 에서 무엇이든 실행하거나(읽기 확인 포함) 파일을 올릴 때 — run_jn.sh 러너, prep 도구 재전송(up_tools.sh), 재부팅 뒤 복구, 펌웨어 플래시.
---

# rover-jetson-run

규칙 본문은 `Docs/debug_log/README.md` 하나다(이 Skill 은 언제 읽을지와 요지만 — 본문을 여기 복사하지 않는다).

**먼저 README 의 아래 절을 Read 로 연다**:
- 읽을 절: `## 4. Jetson 실행`


요지(원본은 README — 어긋나면 README 가 맞다):
- 실행은 job 파일 + 러너 run_jn.sh(목적 JX_WHY) 로만, 실행 전에 무엇을 · 왜 · 시간 · 볼 곳을 한 줄로 알린다. 주소는 CLAUDE.md 네트워크 줄(JETSON_HOST).
- 러너 · 비밀번호 파일은 가림 없이 읽지 않는다(`sed 's/sshpass -p [^ ]*/sshpass -p <PW>/g'`) — 훅 chk_secret_read 가 막는다. 비밀번호는 명령 문자열에 쓰지 않는다.
- sudo · 호스트 설정 변경 금지. MAC 은 가린다. 처음 보는 주소면 신원(hostname · 커널 · /dev/rover)부터 확인.

