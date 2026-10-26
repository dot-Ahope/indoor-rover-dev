#!/bin/bash
# 오프라인 계획기(도메인 42) 잔재 정리 — /tmp/planoff 를 명령줄에 가진 것 + 그 static TF. 주행 스택은 지금 꺼져 있음(로버 안 움직임)
echo "정리 전: $(pgrep -fc '/tmp/planoff/') · tf $(pgrep -fc 'static_transform_publisher --frame-id map --child-frame-id base_link')"
for p in $(pgrep -f '/tmp/planoff/|static_transform_publisher --frame-id map --child-frame-id base_link'); do [ "$p" != "$$" ] && kill -INT $p 2>/dev/null; done
sleep 3
for p in $(pgrep -f '/tmp/planoff/planner_offline|lifecycle_manager_offline|static_transform_publisher --frame-id map --child-frame-id base_link'); do kill -9 $p 2>/dev/null; done
sleep 1; echo "정리 뒤: $(pgrep -fc '/tmp/planoff/planner_offline') · lcm $(pgrep -fc lifecycle_manager_offline) · tf $(pgrep -fc 'static_transform_publisher --frame-id map --child-frame-id base_link')"
