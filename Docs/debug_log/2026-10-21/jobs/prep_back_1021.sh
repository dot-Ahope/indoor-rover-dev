#!/bin/bash
# 시험 컨테이너 잔여 프로세스 정리 뒤 운용 구성 복귀
docker exec isaac_rs_test bash -c "pkill -9 -f nv_static" 2>/dev/null; sleep 2; echo "nv_static 남은 $(pgrep -fc nv_static_container)"
SENSORS_ADD="emitter_off:=true vslam:=shadow dds_shm:=true" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|PREP_FAIL\|불합격\|★\|위치 추정 검사\|SHM 고아\|cuVSLAM(컨테이너)\|wheel_odom\|nvblox_up" | tail -8
