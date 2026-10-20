#!/bin/bash
echo "== UDP 전용 프로파일(run_jn 기본)"; echo "  FASTRTPS=$FASTRTPS_DEFAULT_PROFILES_FILE"
timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average rate|rror" | tail -2
echo "== 프로파일 없음(게이트처럼)"; ( unset FASTRTPS_DEFAULT_PROFILES_FILE; timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average rate|rror|SHM|lock" | tail -3 )
echo "== ros2 데몬"; ps -eo pid,lstart,args | grep -a "[r]os2cli.daemon" | cut -c1-140
echo "  데몬 환경 FASTRTPS: $(for p in $(pgrep -f '[r]os2cli.daemon'); do tr '\0' '\n' < /proc/$p/environ | grep FASTRTPS; done)"
