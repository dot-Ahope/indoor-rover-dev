#!/bin/bash
grep -aE "nav_guard|STUCK" /tmp/nav2.log | tail -6 | cut -c1-200
