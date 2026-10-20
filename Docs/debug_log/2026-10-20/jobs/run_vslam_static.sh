#!/bin/bash
# (10-20 §6.1) L0 정지 시험 — A: 프로젝터 상시 끔 / B: + vslam:=shadow. 각 prep → 20 s → 60 s 측정. B 상태로 둔다. 로버 안 움직임
set +u
for C in ${CONFS:-A B}; do
  echo "########## 구성 $C ##########"
  if [ $C = A ]; then SA="emitter_off:=true"; else SA="emitter_off:=true vslam:=shadow"; fi
  SENSORS_ADD="$SA" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|불합격\|★\|cuVSLAM(컨테이너)\|EKF 위반" | tail -4
  sleep 20
  V0=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log)
  python3 -u /tmp/chk_vslam_live.py 60 2>&1 | grep -av "^\[INFO\]"
  V1=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); echo "  EKF 주기 위반 측정 중 +$((V1 - V0)) (누적 $V1)"
  if [ $C = B ]; then
    echo "  cuvslam_up: $(grep -a 'cuvslam_up' /tmp/sensors.log | tail -2 | tr '\n' ' ' | cut -c1-200)"
    echo "  cuVSLAM 로그: $(grep -aiE 'error|version|tracker|warn|jitter|Delta' /tmp/cuvslam.log | sort | uniq -c | sort -rn | head -6 | cut -c1-150)"
    echo "  vslam_twist: $(grep -a 'vslam_twist' /tmp/sensors.log | tail -2 | cut -c1-140 | tr '\n' ' ')"
  fi
done
