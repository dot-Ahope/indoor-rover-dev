#!/bin/bash
# 10-19 §25: 프로젝터 상시 끔 구성 prep(로버 정지)
SENSORS_ADD="emitter_off:=true" bash /tmp/prep_patrol.sh lite 2>&1 | tail -4
