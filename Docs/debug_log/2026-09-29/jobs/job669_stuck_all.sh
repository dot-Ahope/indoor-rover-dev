#!/bin/bash
# 09-29 §13 G3: bag 풀기 후 stuck 판정 전수 조사
cd /tmp; for f in bag_f0a1 bag_f0a2 bag_f0a3 bag_f0a4 bag_f0a5 bag_f0a6 bag_s_fb1 bag_s_fb2 bag_s1 bag_s2 bag_r1 bag_r1b bag_r2 bag_r2b bag_r3; do [ -d $f ] || { [ -f $f.tgz ] && tar xzf $f.tgz; }; done
ls -d /tmp/bag_f0a? /tmp/bag_f0b? /tmp/bag_s1 /tmp/bag_s2 /tmp/bag_r1 /tmp/bag_r1b /tmp/bag_r2 /tmp/bag_r2b /tmp/bag_r3 /tmp/bag_l1 /tmp/bag_l2 /tmp/bag_s_fb1 /tmp/bag_s_fb2 2>/dev/null | tr '\n' ' '; echo
python3 /tmp/job668_stuckscan.py $(ls -d /tmp/bag_f0a? /tmp/bag_f0b? /tmp/bag_s1 /tmp/bag_s2 /tmp/bag_r1 /tmp/bag_r1b /tmp/bag_r2 /tmp/bag_r2b /tmp/bag_r3 /tmp/bag_l1 /tmp/bag_l2 /tmp/bag_s_fb1 /tmp/bag_s_fb2 2>/dev/null) 2>&1 | grep -av "^\["
