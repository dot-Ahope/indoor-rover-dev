#!/bin/bash
source /opt/ros/humble/setup.bash; cd /tmp
echo "##### job327 (t 26~60)"; python3 /tmp/job327_mp2why.py /tmp/bag_mp6 0 0 0 34 2>&1 | grep -av 'Opened database' | grep -aE "^ +(2[6-9]|[3-5][0-9]|60)\.0 \||^bag|=== t=34|^\+0\.[0-3]|^-0\.[0-3]|^\+0\.00" | cut -c1-150
echo "##### job345 (후보 궤적)"; python3 /tmp/job345_traj.py /tmp/bag_mp6 30,33,35,37,45,48,55 2>&1 | grep -av 'Opened database' | cut -c1-230
