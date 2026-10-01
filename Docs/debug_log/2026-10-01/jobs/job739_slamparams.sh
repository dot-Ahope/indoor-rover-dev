#!/bin/bash
for p in minimum_travel_distance mode; do printf "  %-26s %s\n" $p "$(timeout 15 ros2 param get /slam_toolbox $p 2>&1 | tail -1)"; done
