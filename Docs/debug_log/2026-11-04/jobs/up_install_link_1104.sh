#!/bin/bash
# 11-04: 설치본 nav2_params.yaml 을 src 링크로 되돌림(10-15 §30 · 옛 prep sed -i 가 끊은 것). 내용이 src 와 같을 때만. 로버 안 움직임 · sudo 없음.
I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
S=~/ros2_ws/src/rover_navigation/config/nav2_params.yaml
if [ -L $I ]; then echo "이미 링크"; exit 0; fi
cmp -s $I $S || { echo "src 와 내용이 달라 안 바꿈"; exit 1; }
cp -p $I /tmp/nav2_params_install_backup_1104.yaml && rm $I && ln -s $S $I && echo "링크로 복구: $(readlink -f $I) (백업 /tmp/nav2_params_install_backup_1104.yaml)"
