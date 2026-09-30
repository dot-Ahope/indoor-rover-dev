#!/bin/bash
# 09-30 §3 2 회차: 같은 자리에서 0.70 m 후진(0.06 m/s)
python3 /tmp/job680_slambias.py 0.70 -0.06 2>&1 | grep -av "^\["
