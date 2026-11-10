#!/bin/bash
# anal_src_cmp_1110 — 11-10 §0: Jetson src md5(chk_config_1110 의 'SRC' 줄)를 PC 저장소 git HEAD 판과 대조하고, 다른 파일은 Jetson 원문(chk_config_1110b 의 '@@FILE' 블록)과 diff.
#   PC Git Bash 에서 저장소 루트로 실행. 로버 안 움직임 · Jetson 접속 없음. 인자: 없음.
#   판정: md5(CR 제거, 앞 12 자) 같으면 SAME, 다르면 DIFF, Jetson 에만 있으면 'JETSON만', 저장소에만 있으면 'PC만'.
#   출력: outputs/chk_config_1110_cmp.txt(파일별 판정) · outputs/chk_config_1110_diff4.txt(DIFF 파일의 HEAD ↔ Jetson 차이 앞 30 줄).
#   (대화에서 한 줄 명령으로 돌린 것을 그대로 옮김 — 같은 결과를 다시 만들 수 있게)
cd "$(dirname "$0")/../../../.." || exit 1
O=Docs/debug_log/2026-11-10/outputs
grep '^SRC ' $O/chk_config_1110.txt | tr -d '\r' | while read _ h f; do
  p="ros2_ws/src/$f"
  if git cat-file -e "HEAD:$p" 2>/dev/null; then g=$(git show "HEAD:$p" | tr -d '\r' | md5sum | cut -c1-12); [ "$g" = "$h" ] && echo "SAME $f" || echo "DIFF $f (jetson $h · HEAD $g · HEAD 마지막 변경 $(git log -1 --format='%h %ad' --date=format:%m-%d -- "$p"))"
  else echo "JETSON만 $f"; fi
done > $O/chk_config_1110_cmp.txt
git ls-files ros2_ws/src | grep -v '\.stl$' | sed 's|^ros2_ws/src/||' | while read f; do grep -q " $f\$" <(grep '^SRC ' $O/chk_config_1110.txt | tr -d '\r') || echo "PC만 $f"; done >> $O/chk_config_1110_cmp.txt
awk '{print $1}' $O/chk_config_1110_cmp.txt | sort | uniq -c

T=$(mktemp -d)
awk -v d="$T" '/^@@FILE /{f=$2; gsub("/","__",f); out=d"/"f; printf "" > out; print $2, $3, $4 > d"/_meta"; next} /^@@END/{out=""; next} out{print > out}' $O/chk_config_1110b.txt
for m in $(awk '{print $1}' $T/_meta); do
  echo "===== $m  (- HEAD / + Jetson)"
  git show "HEAD:ros2_ws/src/$m" | tr -d '\r' | diff -u - "$T/${m//\//__}" | sed -n '3,$p' | grep -E '^[-+@]' | cut -c1-190 | head -30
done > $O/chk_config_1110_diff4.txt
rm -rf "$T"
