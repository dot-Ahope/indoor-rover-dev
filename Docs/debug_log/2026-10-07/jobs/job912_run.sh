#!/bin/bash
# 10-07 §2.5: f2c2 목표 5·6 구간 추출(읽기만, 1~2 분)
python3 /tmp/job912_extract.py /tmp/bag_f2c2 1791339064 1791339330 /tmp/x912_f2c2.npz && ls -la /tmp/x912_f2c2.npz
