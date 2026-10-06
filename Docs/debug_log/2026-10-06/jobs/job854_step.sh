#!/bin/bash
python3 -u /tmp/step_rot.py "$1" 2>&1 | grep -av "^\["
