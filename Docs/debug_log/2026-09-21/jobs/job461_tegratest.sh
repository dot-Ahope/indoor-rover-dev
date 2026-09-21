#!/bin/bash
echo "tegrastats 위치: $(command -v tegrastats)"; timeout 4 tegrastats --interval 1000 2>&1 | head -2 | cut -c1-260; echo "rc=$?"
