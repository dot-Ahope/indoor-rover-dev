#!/bin/bash
hostname; uptime; ip -4 -o addr show | grep -v " lo " | cut -c1-80; ls /tmp/job934_prep.sh /tmp/job780_prep_navmap.sh /tmp/bag_f2e2 2>&1 | tail -3; pgrep -fc controller_server; pgrep -fc slam_toolbox
