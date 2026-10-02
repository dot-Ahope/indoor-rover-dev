#!/bin/bash
python3 -u /tmp/job825_rot.py bag_rot2 2>&1 | grep -av "^\["; ls -la /tmp/bag_rot2 | tail -2
