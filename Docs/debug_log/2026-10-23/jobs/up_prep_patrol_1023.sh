#!/bin/bash
# 10-23 §16 /tmp/prep_patrol.sh 를 저장소 Docs/tools 판(vslam 기본 · REPLAN_HZ 환경)으로 교체. 로버 안 움직임
echo "이전 $(sha256sum < /tmp/prep_patrol.sh | cut -c1-10)"
# (base64 본문 생략 — 저장소 Docs/tools/prep_patrol.sh 와 같음)
echo "새 $(sha256sum < /tmp/prep_patrol.sh | cut -c1-10) (기대 9a8a8e3361)"; bash -n /tmp/prep_patrol.sh && echo '문법 OK'
