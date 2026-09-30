#!/bin/bash
python3 /tmp/job690_joydrop.py 2>&1 | grep -av "^\["
echo "joy_linux 로그 끝:"; tail -5 /tmp/joy_test.log | cut -c1-200
