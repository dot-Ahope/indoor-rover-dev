#!/bin/bash
# 10-22 §19 f2sm3 그림자 판정 보조: vslam_twist 10 s 통계(버림) · cuVSLAM 프레임 간격 경고 · nav_guard 로그 이상 — 로버 안 움직임
echo "== vslam_twist 10 s 통계"; grep -ah "버림" /tmp/sensors.log | tail -40 | sed 's/^.*\]\s*//' | cut -c1-120
echo "== cuVSLAM 프레임 간격 경고 수: $(grep -aci "delta between\|jitter\|frame.*gap" /tmp/cuvslam.log)"; grep -ai "delta between\|jitter" /tmp/cuvslam.log | tail -3 | cut -c1-200
echo "== nav_guard 로그(오류 · 개입)"; grep -a "nav_guard" /tmp/nav2.log | grep -aiE "error|개입|Traceback|exception" | tail -5 | cut -c1-200; grep -a "nav_guard" /tmp/nav2.log | grep -a "시간 한도" | tail -3 | cut -c1-160
