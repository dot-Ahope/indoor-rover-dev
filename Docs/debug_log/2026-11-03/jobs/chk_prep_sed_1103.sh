#!/bin/bash
# prep_fast.sh 의 PreferForward 블록만 떼어 임시 링크 파일에 돌려 본다(Linux 심볼릭 링크 유지 확인, 11-03)
P=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/prep_fast_test.sh
BLK=$(sed -n '/^FWD=\${FWD/,/^fi$/p' "$P" | tr -d '\r')
T=$(mktemp -d)
printf 'x:\n  PreferForwardCritic: {enabled: true, cost_power: 1, cost_weight: 15.0, threshold_to_consider: 0.4}\n' > $T/src.yaml
ln -s $T/src.yaml $T/inst.yaml; Y=$T/inst.yaml
for v in 15.0 5.0 5.0; do
  FWD=$v; eval "$BLK"
  echo "FWD=$v -> src $(grep -o 'cost_weight: [0-9.]*' $T/src.yaml) · link $([ -L $Y ] && echo 유지 || echo 끊김)"
done
rm -rf $T
