#!/bin/bash
# 10-07 §11: 컨트롤러가 내는 시각화 토픽 확인(읽기만)
ros2 topic list 2>/dev/null | grep -iE "local_plan|trajector|transformed|optimal|received_global" ; echo "--"
ros2 param list /controller_server 2>/dev/null | grep -iE "visualiz|Visualizer|publish" | head
