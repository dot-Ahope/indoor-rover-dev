#!/bin/bash
free -m | head -2; grep -E "MemAvailable|SwapTotal|SwapFree|Shmem:" /proc/meminfo
echo "== RSS 상위(MB)"; ps -eo rss,comm,args --sort=-rss | head -14 | awk '{printf "%6.0f  %s  %s\n", $1/1024, $2, substr($0, index($0,$3), 70)}'
echo "== GPU(tegrastats 1 회)"; timeout 3 tegrastats --interval 1000 2>/dev/null | head -1 | cut -c1-200
