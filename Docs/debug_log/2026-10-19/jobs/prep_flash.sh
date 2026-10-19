#!/bin/bash
# 10-19 §16: 번갈이 구성 prep(로버 안 움직임)
SENSORS_ADD="emitter_flash:=true stereo_fps:=30" bash /tmp/prep_patrol.sh lite 2>&1 | tail -14
echo "== 카메라 · 분리"; grep -aoE "Open profile: stream_type: (Depth|Infra)[^;]*FPS: [0-9]+" /tmp/sensors.log | sort -u; grep -a "emitter_splitter" /tmp/sensors.log | head -2 | cut -c1-200
