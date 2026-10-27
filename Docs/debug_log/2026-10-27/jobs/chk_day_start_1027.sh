#!/bin/bash
uptime; iwgetid -r; ls /tmp/prep_fast.sh /tmp/prep_patrol.sh /tmp/chk_prep.py 2>&1 | tr "
" " "; echo; echo "nav2 $(pgrep -fc controller_server) slam $(pgrep -fc slam_toolbox) cam $(pgrep -fc realsense2_camera)"; ls -d ~/smac_ws ~/smac_dbg_ws 2>&1 | tr "
" " "; echo; df -h / | tail -1
