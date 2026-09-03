#!/bin/bash
set -e
B=$HOME/microros_build/firmware/build
S=/mnt/c/temp_microros
echo "소스: $B"
ls -la "$B/libmicroros.a"
echo "include: $([ -d "$B/include" ] && echo 있음 || echo 없음)"
rm -rf "$S"; mkdir -p "$S/include"
cp "$B/libmicroros.a" "$S/libmicroros.a"
find "$B/include" -name "*.c" -delete 2>/dev/null || true
cp -R "$B/include/." "$S/include/"
# include/X/X/* -> include/X/  평탄화
for d in "$S"/include/*/; do
  n=$(basename "$d")
  if [ -d "$d$n" ]; then cp -r "$d$n"/. "$d" 2>/dev/null || true; rm -rf "$d$n"; fi
done
echo "스테이징 완료: $(du -sh "$S" | cut -f1)"
echo "헤더 수: $(find "$S/include" -name '*.h' | wc -l)"
echo "샘플: $(ls "$S/include" | head -5 | tr '\n' ' ')"
