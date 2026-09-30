#!/bin/bash
bash /tmp/job685_f1_teleop.sh | grep -a "joy\|scale"
python3 /tmp/job697_restore_chk.py 2>&1 | grep -av "^\[" | grep -a "마지막\|/map"
bash /tmp/job695_loadab.sh mapping_mode2
