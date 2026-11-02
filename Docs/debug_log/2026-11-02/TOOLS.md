# 2026-11-02 도구 사용 기록

규약 README §3.3. 이날은 로버 주행 없음 — 문서 · 규약 · 비밀 처리만. (그날 끝에 몰아 채움 — 규약 위반, 이 날짜부터 생긴 규칙이라 사후 작성)

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 뒤 판정 |
|---|---|---|---|---|---|
| §1 | 문제 대장 5 기 색인 다시 생성 | `Docs/tools/anal_record_index.py` | SECTIONS · RUNS · JOBS 갱신 | 카드 링크 대상이 색인에 다 있음 | ✔ |
| §4 | 규약 점검 도구 첫 실행(10-13 이후 전부) | `Docs/tools/chk_record_rules.py --all` → `outputs/chk_record_rules_all.txt` | 경고 93(N 64 · H 22 · P 4 · T 3) | 실제 작업이 규약 앞머리 밖 이름(`get_` 29)을 계속 씀 | ✔ (사용자: 6 개 유지) |
| §4 | deny 규칙이 실제로 막는지 | `git push --dry-run origin no-such-branch-xyz` | 도구가 거부 | deny 가 즉시 적용됨 | ✔ |
| §5 | 커밋 훅 단위 시험 | `Docs/tools/chk_commit_gate.py` 에 모의 훅 JSON | 누출 → 2 · 비커밋 → 0 · 파일 없음 → 2 · 한글 메시지 → 0 | 첫 판은 stdin cp949 로 깨지면 통과 — 고침 | ✔ |
| §5 | 훅 실세션 시험 | 비밀번호 파일을 잠시 치우고 `echo "git commit …"` | 훅이 막음 | 훅이 세션에 바로 걸림 | ✔ |
| §6 | 공개 저장소 옛 비밀번호 확인 | `jobs/chk_leak_scan_1102.py` | 값 1 종 · 지금 값과 다름 · 공개 dev/main 현재 트리 + 이력 4 커밋, 다른 파일 0 | 다른 세션 평가가 맞음 | ✔ (첫 판 정규식은 흔한 짧은 문자열을 값으로 잘못 뽑음 — `sshpass -p <값> ssh/scp` 로 좁힘) |
| §6 | 옛 값을 비밀번호 파일에 더함 | `jobs/up_pw_old_1102.py` | 줄 수 2 | 게이트가 옛 값도 감시 | ✔ (훅이 바로 settings.local.json 을 잡아 확인) |
| §6 | `commit -a` 대비 시험 | 임시 저장소 + `chk_commit_gate.py`(Claude 훅 · `--git-hook`) | 둘 다 막음, 커밋 수 그대로 | 작업 트리까지 보게 고친 판이 맞음 | ✔ |
| §8 | 공개 이력 다시 쓰기 마른 실행 | `private/publish_public.sh` 의 push 직전 멈춤 판 + `jobs/chk_pub_filtered_1102.sh` | 점검 0·0·0·0 · 846 커밋 · `SSHPASS=<` 1(자리표시) | 다시 써도 됨 | ✔ |
| §8 | 강제 push 뒤 확인 | `git log -p public/dev · public/main` + 비밀번호 파일 검색 | 둘 다 0 · dev = main = 93c12242 | 공개 이력에서 제거됨 | ✔ |
