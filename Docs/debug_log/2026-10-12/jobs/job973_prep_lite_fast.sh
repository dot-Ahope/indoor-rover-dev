#!/bin/bash
# 10-12 §13: 빠른 prep 으로 운용 후보 구성(그림자 EKF 끔 + mppi_viz lite + PreferForward 15, B 구성). 로버 안 움직임
export EXTRA_SENSORS="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel" EXTRA_NAV="global_camera:=nvblox replan_hz:=0.5 mppi_viz:=lite" STUCK_SHADOW=true FWD=15.0
bash /tmp/job972_prep_fast.sh
