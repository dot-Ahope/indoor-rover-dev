#!/bin/bash
for nd in /planner_server /bt_navigator; do echo "   timeout: failed to run command ‘ros2’: No such file or directory"; done
python3 /tmp/job658_pathcheck.py 2>&1 | grep -av "^\["
