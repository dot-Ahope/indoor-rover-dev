#!/bin/bash
echo "  stuck shadow: $(timeout 20 ros2 param get /stuck_monitor shadow_mode 2>&1 | tail -1) · nav_guard d0_window: $(timeout 20 ros2 param get /nav_guard d0_window 2>&1 | tail -1) · nav_guard $(pgrep -fc nav_guard.py) · slam mode $(timeout 20 ros2 param get /slam_toolbox mode 2>&1 | tail -1)"
