#!/bin/bash
echo "===PROCS==="; pgrep -af "job4g|make|tee|cc1|aarch64-linux-gnu-gcc" | cut -c1-160 || echo NONE
echo "===TOP==="; top -bn1 | head -12
echo "===MEM==="; free -h
echo "===OOM/KILL==="; echo '<PW>' | sudo -S -p '' dmesg 2>/dev/null | grep -iE "oom|killed process|out of memory|segfault" | tail -5 || echo NONE
echo "===FULL_LOG==="; cat /tmp/hid_build.log
echo "===TREE_STATE==="
S=/usr/src/kernel/kernel-jammy-src
ls -la $S/.config $S/include/generated/autoconf.h $S/scripts/basic/fixdep 2>&1
ls -la --time-style=+%H:%M:%S $S/Module.symvers $S/modules.order 2>&1 | head
echo "gcc: $(gcc --version | head -1)"; which aarch64-linux-gnu-gcc gcc make bc flex bison
echo "===LAST_MODIFIED_IN_TREE==="; find $S -maxdepth 2 -newer $S/Makefile -printf '%TT %p\n' 2>/dev/null | sort | tail -8
