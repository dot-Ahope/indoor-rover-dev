#!/bin/bash
# 10-27 §9 재부팅 뒤 prep 재전송(Docs/tools: prep_fast · prep_patrol · chk_prep) + 저장소 nav2_params.yaml(tolerance 0.35) 을 Jetson src · 설치본에. 로버 안 움직임.
#   실행본 = PC 가 앞에 붙인 base64 본문(/tmp/<이름>, CR 제거판) + 이 머리. 해시는 git blob(git hash-object) — PC 의 HEAD blob 과 대조.
for f in prep_fast.sh prep_patrol.sh chk_prep.py; do chmod +x /tmp/$f; echo "$f $(git hash-object /tmp/$f | cut -c1-10) CR $(grep -c $'\r' /tmp/$f)"; done
R=~/ros2_ws/src/rover_navigation/config/nav2_params.yaml; I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
echo "이전 src $(sha256sum < $R | cut -c1-12) · 설치본 $(sha256sum < $I | cut -c1-12) $( [ -L $I ] && echo 링크 || echo 일반파일)"
cp /tmp/up_nav2_params.yaml $R; [ -L $I ] || cp $R $I
echo "새 src $(sha256sum < $R | cut -c1-12) · 설치본 $(sha256sum < $I | cut -c1-12) · nav2_params blob $(git hash-object $R | cut -c1-10)"
grep -A2 "    SmacHybrid:" $I | grep tolerance
