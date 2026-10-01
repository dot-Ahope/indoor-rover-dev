#!/bin/bash
# 10-01 §8.39: 기본 plugin_lib_names 목록이 박힌 라이브러리 찾기
F=$(grep -l "nav2_rate_controller_bt_node" /opt/ros/humble/lib/*.so /opt/ros/humble/lib/nav2_bt_navigator/* 2>/dev/null | grep -v "rate_controller_bt_node.so"); echo "파일: $F"
for f in $F; do strings $f | grep -E "^nav2_[a-z_]*_bt_node$"; done | sort -u > /tmp/btlibs_default.txt; wc -l < /tmp/btlibs_default.txt
comm -13 /tmp/btlibs_default.txt /tmp/btlibs_installed.txt | tr '\n' ' '; echo " <- 설치됐지만 기본 아님"
comm -23 /tmp/btlibs_default.txt /tmp/btlibs_installed.txt | tr '\n' ' '; echo " <- 기본인데 설치 안 됨"
