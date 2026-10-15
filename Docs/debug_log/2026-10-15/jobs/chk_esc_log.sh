#!/bin/bash
# (10-15 §27) nav2 로그의 탈출 · 복구 · 컨트롤러 실패 줄 — 로버 안 움직임
grep -a "monotone_escape\|Failed to make progress\|collision\|No valid\|Goal failed\|Goal succeeded\|Running backup\|Running wait\|Clearing\|aborted\|Aborting" /tmp/nav2.log | grep -v "Creating\|Configuring\|Activating" | tail -n 40 | cut -c1-260
