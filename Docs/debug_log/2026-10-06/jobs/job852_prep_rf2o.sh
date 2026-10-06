#!/bin/bash
# 10-06 R3: rf2o·그림자 EKF 켠 prep
export EXTRA_SENSORS="rf2o:=true shadow:=true"
bash /tmp/job780_prep_navmap.sh
echo "  sensors 인자 확인: $(grep -a "sensors 인자" /tmp/live/current.log | tail -1)"
