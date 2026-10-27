#!/bin/bash
# §17: 수정 층으로 prep 재기동(f2st1 과 같은 구성) → 정지 120 s 확인. 로버 안 움직임
bash /tmp/prep_smac_1027.sh
echo "== 층 라이브러리: $(stat -c '%y' $(readlink -f ~/ros2_ws/install/nvblox_nav2/lib/libnvblox_nav2.so) | cut -c1-19) · 로드 오류 $(grep -ci 'nvblox.*\(error\|failed\)' /tmp/nav2.log)"
python3 /tmp/chk_nvlayer_tffix_1027.py 120
