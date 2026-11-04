---
name: rover-commit-push
description: 커밋하거나 push · 공개(publish_public.sh) 할 때, 비밀 · 공개 범위를 판단할 때.
---

# rover-commit-push

규칙 본문은 `Docs/debug_log/README.md` 하나다(이 Skill 은 언제 읽을지와 요지만 — 본문을 여기 복사하지 않는다).

**먼저 README 의 아래 절을 Read 로 연다**:
- 읽을 절: `## 8. 비밀 · 공개 · 커밋 · push`


요지(원본은 README — 어긋나면 README 가 맞다):
- push 는 사용자가 지시할 때만, origin 금지. 순서: git fetch . feature/smac-hybrid:feature/nvblox-migration → git push personal … → bash private/publish_public.sh(--push-main · --rewrite 는 사용자 결정).
- 커밋 훅이 비밀번호와 기록 규칙 새 경고를 막는다 — 고치는 명령과 커밋은 따로 실행(훅은 실행 전에 검사). 기준선(rules_baseline.txt)을 다시 쓰는 것은 사용자 확인 뒤.
- 커밋 메시지 끝에 Co-Authored-By · Claude-Session 줄.

