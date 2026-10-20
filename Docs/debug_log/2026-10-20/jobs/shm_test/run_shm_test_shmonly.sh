#!/bin/bash
# (10-20 §7.3b) 컨테이너 구독을 SHM 전용 프로파일로 — 받으면 SHM 경로 확정
CPROF=/tmp/fastdds_shm_only.xml bash /tmp/run_shm_test.sh 0 30
