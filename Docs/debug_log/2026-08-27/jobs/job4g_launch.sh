#!/bin/bash
rm -f /tmp/hid_build.log
echo '<PW>' | sudo -S -p '' setsid nohup bash /tmp/job4g.sh >/dev/null 2>&1 &
sleep 5
echo "LAUNCHED"; tail -3 /tmp/hid_build.log
