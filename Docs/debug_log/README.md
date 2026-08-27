# 디버깅 로그 — 날짜별 명령·출력·판단 기록

> 목적: Jetson 원격 작업의 **재현성**과 **판단 근거 보존**. 같은 증상 재발 시 당시의 명령·출력·추론을 그대로 다시 볼 수 있게 한다.
> 규약 채택: 2026-08-27 (사용자 제안)

## 구조

```
Docs/debug_log/
  README.md              (본 문서 — 규약)
  YYYY-MM-DD/
    SUMMARY.md           (하루 정리: 한 일 → 결과 → 판단 → 다음 할 일)
    jobs/                (그날 실행한 원격 스크립트 원본 jobNN_*.sh)
    outputs/             (스크립트 실행 출력 캡처 jobNN_*.txt)
```

## 규칙

1. **원격 실행은 항상 스크립트 파일로** (`jobs/`에 보관). 한 줄 ssh 명령도 가능하면 스크립트화한다.
2. **출력은 `outputs/`에 tee** — PC 측 실행 래퍼에서 `| tee Docs/debug_log/<날짜>/outputs/<job>.txt`.
   사용자가 `!` 접두어로 직접 실행한 결과(분류기 차단 우회분)는 Claude가 대화에서 옮겨 적는다.
3. **SUMMARY.md는 하루 마감 시 작성** — 형식: `## 한 일` / `## 결과 (수치)` / `## 판단·결정 (근거)` / `## 미해결·다음`.
   판단 항목에는 **기각된 가설도** 근거와 함께 남긴다 (재추진 방지).
4. 비밀번호·토큰은 스크립트/출력에 남기지 않는다 (`sudo -S` 입력부는 보관 전 마스킹).
5. 파일명: `job<Step><알파벳>_<요지>.txt` (예: `job4g_launch.txt`). 스크립트와 출력의 접두어를 맞춘다.

## 관련 문서
- 작업 지시서: [`../JETSON_SETUP_BRIEF.md`](../JETSON_SETUP_BRIEF.md)
- 이전 프로젝트 케이스북(참고 형식): `C:\Users\magma\Documents\Claude\Projects\Rover\docs\handheld\DEBUG_CASEBOOK.md`
