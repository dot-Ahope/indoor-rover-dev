# 2026-11-04 도구 사용 기록

규약 README §3.3. 로버 주행 없음.

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 뒤 판정 |
|---|---|---|---|---|---|
| §1 | 재부팅 뒤 prep 도구 재전송 | `Docs/tools/up_tools.sh`(11-04 고침 — 저장소 판 복사) | Jetson /tmp 7 개 · follow-symlinks 2 줄 | 새 prep 판 올라감 | ✔ |
| §1 | 설치본 설정이 src 링크인가 | `jobs/chk_install_links_1104.sh` → `outputs/chk_install_links_1104.txt` | nav2_params.yaml 만 일반 파일(내용 같음) | 옛 sed -i 흔적 | ✔ |
| §1 | 링크 복구 | `jobs/up_install_link_1104.sh` → `outputs/up_install_link_1104.txt` | 링크로 복구 · 백업 /tmp | — | ✔ |
| §1 | Jetson src 가 저장소와 같은가 | `jobs/chk_src_md5_1104.sh` · `chk_src_strip_1104.sh` · `anal_src_strip_md5.py` → `outputs/chk_src_*_1104.txt` | 6/8 다름, 주석 빼면 pad_relief.py 1 개 | 차이는 주석 + 기본 off | ✔ |
| §3 | 8 기가 찾은 낡은 주석 정정 | `jobs/up_comment_fix_1104.py` | 5 파일 · 문법 검사 통과 | 동작 변경 없음 | ✔ |
| §3 | 기록 어긋남 정정 표시 | `jobs/up_record_marks_1104.py` | 13 곳(표 행 2 곳은 표 아래 줄로) | 원문 유지 | ✔ |
| §4 | 9 기 카드 링크 · 표 | `jobs/up_issue_links_p9.py` · `jobs/up_issues_table_p9.py` → 색인 · 검사 | 링크 25 장 · RULES_OK | — | ✔ |
| §4 | Jetson F2.5 파일 판(ⓐ 배포?) | `jobs/chk_place_md5_1104.sh`(읽기만) | 두 번 lost connection(핑 50 % 손실) — 저장소 판만 `outputs/chk_place_md5_1104_repo.txt` | — | 다음 접속 때 |
| §5 | 9 기 주석 · 문서 정정 | `jobs/up_doc_fix_p9_1104.py` | 6 파일 · YAML 통과 | 동작 변경 없음 | ✔ |
| §6 | MAC 가림 | `jobs/up_mask_mac_1104.py` | 파일 33 · 609 곳 + 1 | 지금 판만 | ✔ |
