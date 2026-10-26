#!/bin/bash
# up_bundle — (PC) 오프라인 계획기 비교 묶음 만들기: yaml · query · run 스크립트 · 장면 npz 를 base64 로 담은 스크래치패드 스크립트(run_jn.sh 로 실행) (2026-10-23)
#   인자: yaml 장면.npz 출력묶음.sh
H=$(cd "$(dirname "$0")" && pwd)
{ echo '#!/bin/bash'; echo "mkdir -p /tmp/planoff"
  # 텍스트 파일은 CR 을 빼고 담음 — 2026-10-26: git(core.autocrlf=true)이 체크아웃 때 CRLF 로 바꿔 Jetson bash 가 깨졌고('\r': command not found)
  #   정리 단계가 안 돌아 planner_server 5 개가 도메인 42 에 쌓임 → 그날 D5 첫 결과 무효(SUMMARY 2026-10-26 §1.1)
  echo "base64 -d > /tmp/planoff/planner_offline.yaml <<'B64'"; tr -d '\r' < "$1" | base64 -w0; echo; echo B64
  for f in query_planners.py run_planner_offline.sh; do echo "base64 -d > /tmp/planoff/$f <<'B64'"; tr -d '\r' < "$H/$f" | base64 -w0; echo; echo B64; done
  echo "base64 -d > /tmp/planoff/scenes.npz <<'B64'"; base64 -w0 "$2"; echo; echo B64
  echo 'bash /tmp/planoff/run_planner_offline.sh "$1"'; } > "$3"
