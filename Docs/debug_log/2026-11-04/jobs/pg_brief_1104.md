You are building after-the-fact daily summary pages ("정리 페이지") for a personal rover project, for dates in Aug–Sep 2026. Repo root F:\6_Indoor_Rover\Rover (Bash tool = Git Bash: /f/6_Indoor_Rover/Rover). Write everything in Korean.

## Read first (in this order)
1. `Docs/debug_log/README.md` §2.3 (본 것 → 추론 → 결론 · 데이터 위치 · 스크립트 핵심 줄 + 실제 출력 발췌 + 원문 경로 · 실수 칸 형식) and §7.1 (page rules). Key rule: **the content source is that day's SUMMARY** (plus files in that date folder, e.g. REPORT.md / BASELINE_STVL.md). Never invent verdicts or numbers that are not in the day's records.
2. Model page: `Docs/debug_log/2026-11-02/jobs/report_1102_body.html` (structure: header eyebrow/h1/lead → "오늘의 판정" verdict cards `.v ok|wait|no` → sections with `.flow` (k/value rows with `<pre class="code">` excerpts + `.note` paths) and `.tbl` tables → 내 실수 in `.pm`/`.flow` cell format → 다음 후보). Also look at one October page with correction marks: `Docs/debug_log/2026-10-26/jobs/report_1026_body.html` (search `c1103`).
3. Builder pattern: `Docs/debug_log/2026-11-03/jobs/fig_report_1103.py` (head = `Docs/debug_log/2026-10-28/jobs/report_1028_head.html`, replace only the `<title>`; body appended; output `figures/day_summary_MMDD.html`).
4. The issue ledger `Docs/issues/` — cards cite these dates and record **later corrections / 기록 어긋남**. Grep `Docs/issues/*.md` for your date (e.g. `09-09 §`) to find corrections. Also grep later SUMMARYs (`Docs/debug_log/2026-1*/SUMMARY.md`) for '→ … 정정' pointers to your date.

## For each of your dates DATE (MMDD = month+day)
- Write `Docs/debug_log/DATE/jobs/report_MMDD_body.html`. Start it with a `<style>` block copying the `.code`, `.flow > span` rules of the 11-02 body, plus this correction class:
  `.c1104{font-weight:600;color:var(--ink);background:var(--tint-warn);border-left:3px solid var(--warn);padding:0 5px;margin-left:3px;border-radius:2px;white-space:normal;font-size:.92em}`
- Eyebrow: `Indoor Rover · DATE · Docs/debug_log/DATE §… · (주행 있음/없음) · 11-04 사후 작성`. Lead paragraph: say plainly this page was built on 2026-11-04 from the day's SUMMARY, and that later corrections are marked.
- Verdict cards: the day's real outcomes (from SUMMARY). Sections: the day's main threads, each with 본 것 → 추론 → 결론, and for each judgement **a short excerpt of the script's key lines and of the actual output**, with repo paths of both (`Docs/debug_log/DATE/jobs/...`, `.../outputs/...`). If the source file is missing, write '원문 없음 — 발췌가 전부' or '원천 소실' (Aug–Sep records often have no outputs; early days say "출력 캡처 없음"). Use what the SUMMARY itself quotes when outputs are missing.
- Mistakes / corrections written in that day's SUMMARY → `.pm`/`.flow` cell format (하려 한 것 · 본 것 · 왜 · 영향 · 알아보는 법 · 데이터) where info exists.
- **Later corrections** (from ledger cards or later SUMMARYs): keep the original statement and append `<span class="c1104">(11-04 정정: … — 근거 경로)</span>`. Count them; mention the count in the lead.
- At the end a short "이후 · 관련 카드" list linking ledger cards as plain paths (`Docs/issues/<card>.md`) — pages are standalone artifacts, so give paths as text in `.mono`, not relative hrefs.
- If the date already has topic pages in `DATE/figures/*.html` (09-21~09-29) or `DATE/day_0930.html`, **do not modify them**; mention them by path in the page ("이 날의 주제 페이지").
- Write `Docs/debug_log/DATE/jobs/fig_report_MMDD.py` (copy the 11-03 builder; header comment line 1 says what/why/PC/로버 안 움직임; title `<title>MM-DD <짧은 이름></title>` — a 2–5 word Korean name specific to the day, not a generic label), run it with `python`, and confirm `figures/day_summary_MMDD.html` is created.
- Size: aim 12–30 KB body. Make every figure/number traceable to the SUMMARY.

## Rules
- Create/edit ONLY: those two jobs files + the generated figures file for your dates. Do not edit SUMMARY, ledger cards, code, README, other dates. No git commits. Do not publish artifacts (the main session publishes).
- Security: never print or write passwords. Old job scripts may contain a literal password or `sshpass -p <value>` — ALWAYS read them through `sed 's/sshpass -p [^ ]*/sshpass -p <PW>/g; s/echo [^|]* | sudo -S/echo <PW> | sudo -S/g'`, and in excerpts show `<PW>`. Before finishing, grep your output files for `sshpass -p [^<]` and `sudo -S` and make sure no secret appears. Never write the private-plan words (pages are published from a public repo). MAC addresses are already masked as `XX` in the repo — keep masked. Do not run anything on the Jetson/network.
- HTML: valid, closed tags, escape `<`, `>`, `&` inside `<pre>`. No external resources besides what the head already loads. No NUL / U+FFFD characters (check with `grep -P '\x00|\xEF\xBF\xBD'`).
- Run `python Docs/tools/chk_record_rules.py` from repo root at the end; fix warnings for your files.
- Scratch files: scratchpad folder of this brief, with your bundle prefix only.

## Report back (concise, Korean)
For each date: page file path, the `<title>`, a one-sentence description (for the gallery card), verdict count, number of 11-04 correction marks, and any 기록 어긋남 you found that is NOT already in a ledger card (with paths). Then checker result.
