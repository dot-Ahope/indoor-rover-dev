#!/bin/bash
echo "## 래퍼 프로세스들"; for w in $(pgrep -f 'bash .*nvblox_up.sh'); do echo "  pid $w ppid $(ps -o ppid= -p $w | tr -d ' ') etime $(ps -o etimes= -p $w | tr -d ' ') s cmd: $(tr '\0' ' ' < /proc/$w/cmdline | cut -c1-90)"; done
echo "## launch 프로세스"; pgrep -af 'navigation.launch' | cut -c1-100
echo "## 컨테이너 노드"; docker exec isaac_ros_dev-aarch64-container bash -c "ps -eo pid,ppid,etimes,cmd | grep -a 'nvblox_nod[e]' | cut -c1-100"
