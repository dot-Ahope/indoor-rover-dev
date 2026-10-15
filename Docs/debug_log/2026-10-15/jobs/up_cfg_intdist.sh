#!/bin/bash
# (10-15 §30) nvblox 통합 거리 1.0 · ClearanceBandCritic 끔 설정 배포 — /tmp 의 두 yaml 을 Jetson src 로(원본 백업). 설치본은 src 링크라 다음 기동부터. 로버 안 움직임
D=~/ros2_ws/src/rover_navigation/config; T=$(date +%m%d_%H%M%S)
for f in nvblox_local.yaml nav2_params.yaml; do cp -p $D/$f $D/$f.bak_$T && cp /tmp/$f $D/$f || { echo "배포 실패 $f"; exit 1; }; done
echo "백업 접미사 .bak_$T"
echo "설치본 확인: $(grep -o 'max_integration_distance_m: *[0-9.]*' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml) · $(grep -o 'ClearanceBandCritic: {enabled: [a-z]*' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)"
# ⚠ prep_fast 의 sed -i 가 설치본 nav2_params.yaml 링크를 일반 파일로 바꿔 놓아(그 뒤 src 수정이 안 따라옴) — src 로 다시 링크
I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
[ -L $I ] || { rm -f $I && ln -s $D/nav2_params.yaml $I && echo "설치본 nav2_params 링크 복구"; }
echo "설치본 재확인: $(grep -o 'ClearanceBandCritic: {enabled: [a-z]*' $I) · 링크 $(readlink $I)"
