#!/bin/bash
for i in 1 2 3; do r=$(timeout 15 ros2 param get /stuck_monitor shadow_mode 2>&1 | tail -1); echo "  시도 $i: $r"; echo "$r" | grep -q "Boolean" && break; done
