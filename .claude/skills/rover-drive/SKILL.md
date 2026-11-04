---
name: rover-drive
description: 로버를 움직이는 주행 · 재생 · 시험을 준비하거나 실행할 때 — prep, 게이트, 러너(run_f0.sh · run_f2c.sh · job551), 판정 선언, bag 회수 · 보관 · 삭제.
---

# rover-drive

규칙 본문은 `Docs/debug_log/README.md` 하나다(이 Skill 은 언제 읽을지와 요지만 — 본문을 여기 복사하지 않는다).

**먼저 README 의 아래 절을 Read 로 연다**:
- 읽을 절: `## 4. Jetson 실행`
- 읽을 절: `## 5. 주행`
- 읽을 절: `## 6. 보관 · 삭제`


요지(원본은 README — 어긋나면 README 가 맞다):
- 로버는 사용자가 "시작" 이라고 한 뒤에만 움직인다.
- 판정 기준을 주행 전에 SUMMARY 새 § 로 선언. 코스 · 게이트의 단일 출처 = Docs/04_navigation/TEST_COURSE_AND_GATES.md.
- 러너에 STAGE · NOTE · GIT_HEAD. 주행 직후 bag 을 PC bags/ 로 회수, GB 급 bag 은 시각화 → 사용자 확인 뒤에만 삭제.

