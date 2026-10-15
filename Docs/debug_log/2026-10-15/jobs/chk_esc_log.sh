#!/bin/bash
# (10-15 §27) nav2 로그의 monotone_escape 줄 — 로버 안 움직임
grep -a "monotone_escape" /tmp/nav2.log | tail -n 25
