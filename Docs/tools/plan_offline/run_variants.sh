#!/bin/bash
# run_variants — (PC) Smac 변형을 **변형마다 따로** planner_server 에 올려 돌리고 결과를 합침 (2026-10-26 §6.2).
#   왜: nav2_smac_planner 1.1.20 의 NodeHybrid · NodeLattice 는 motion_table(cost_penalty · 회전반경 · 운동 모델) · 휴리스틱 표가
#       static 이라 한 프로세스에 Smac 플러그인을 여럿 올리면 서로 설정을 덮음(src/a_star.cpp:115 은 지도 크기가 바뀔 때만 다시 초기화).
#       → 같은 서버에 여러 변형을 올린 비교(10-23 §22.2, 10-26 §3~§5 일부)는 무효. NavFn(GridBased)은 해당 없음.
#   인자: 출력폴더 장면.npz 패딩 오버레이(없으면 -) 변형...   환경 INFL_R · INFL_K 는 gen_yaml 로 전달
#   출력: 출력폴더/run_<변형>.txt · result_<변형>.npz · anal_<변형>.txt, 합친 표 anal_all.txt
H=$(cd "$(dirname "$0")" && pwd); O=$1; SC=$2; PAD=$3; OV=$4; shift 4; mkdir -p "$O"
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
[ "$OV" = - ] && OV=""
for v in "$@"; do
  python -X utf8 "$H/gen_yaml.py" "$O/planner_$v.yaml" "$PAD" "$v" >/dev/null
  bash "$H/up_bundle.sh" "$O/planner_$v.yaml" "$SC" "$S/up_planoff_v.sh"
  MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=1200 JX_WHY='Smac 변형 단독 $v(도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_v.sh GridBased,$v $OV" > "$O/run_$v.txt" 2>&1
  sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' "$O/run_$v.txt" | sed '1d;$d' | tr -d '\r\n ' | base64 -d > "$O/result_$v.npz"
  python -X utf8 -I "$H/anal_plan_compare.py" "$O/result_$v.npz" "$SC" "$O/fig_$v" 2>/dev/null > "$O/anal_$v.txt"
  echo "== $v $(grep -a '적재된' "$O/run_$v.txt" | grep -o 'smac_ws\|/opt/ros' | head -1) $(grep -ac '재구성 일치 1.0000' "$O/run_$v.txt")/6 일치"
done
{ head -1 "$O/anal_$1.txt"; grep -h GridBased "$O/anal_$1.txt"; for v in "$@"; do grep -h "$v " "$O/anal_$v.txt"; grep -h "$v |" "$O/anal_$v.txt"; done | sort -u -k1,1 -k2,2; } > "$O/anal_all.txt"
