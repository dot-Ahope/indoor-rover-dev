#!/bin/bash
B=~/rs_build/build.log; grep -a BUILD_EXIT $B; grep -a -c "" $B; grep -a -E "^\#[0-9]+ \[|Building CXX|\[ *[0-9]+%\]" $B | tail -3; tail -3 $B; free -m | sed -n 2p; uptime
