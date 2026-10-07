#!/bin/bash
# 10-07 §5: W3 떨림 TF 지연 — bag 분석 + 11:12:09 외삽 오류 원문(읽기만, 1~2 분)
python3 /tmp/job917_tflag.py /tmp/bag_f2c2 1791338894 /tmp/x917_f2c2.npz 2>&1 | grep -v rosbag2_storage
echo "== 외삽 오류 원문"; grep -a "extrapolation" /tmp/nav2.log | sed -E 's/^\[[a-z_.]+-[0-9]+\] //' | cut -c1-330 | tail -6
echo "== 같은 시각 근처 경고(1791339100~1791339135)"; grep -aE "\[17913391[0-3][0-9]\." /tmp/nav2.log | grep -avE "Message Filter|tick rate" | grep -aiE "warn|error|time|tf|late|old" | sed -E 's/^\[[a-z_.]+-[0-9]+\] //' | cut -c1-220 | tail -12
grep -aE "\[17913391[0-3][0-9]\." /tmp/nav2.log | grep -ac "Message Filter"
