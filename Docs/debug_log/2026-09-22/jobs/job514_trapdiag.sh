#!/bin/bash
# N6-0 V2 진단: 래퍼(nvblox_up.sh)가 TERM/INT 에 반응하는지 — launch 아래서 뜬 래퍼와 수동 실행 래퍼를 대조
set +u
CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
nvc() { docker exec $CN bash -c "pgrep -fc '^$BIN' || true" 2>/dev/null; }
W=$(pgrep -f "bash .*nvblox_up.sh" | head -1)
echo "## 현재 래퍼 pid: '$W' | nvblox_node $(nvc) 개"
if [ -n "$W" ]; then
  echo "  cmdline: $(tr '\0' ' ' < /proc/$W/cmdline | cut -c1-120)"; grep -E "^(SigIgn|SigCgt|SigBlk|PPid)" /proc/$W/status | tr '\n' ' '; echo
  echo "  자식: $(ps -o pid,stat,cmd --ppid $W | tail -n +2 | cut -c1-80 | tr '\n' '|')"
  kill -TERM $W; for i in $(seq 1 8); do [ "$(nvc)" = "0" ] && break; sleep 1; done; echo "  TERM → $i s 뒤 nvblox_node $(nvc) 개, 래퍼 생존 $(kill -0 $W 2>/dev/null && echo yes || echo no)"
  if [ "$(nvc)" != "0" ] && kill -0 $W 2>/dev/null; then kill -INT $W; sleep 5; echo "  INT → nvblox_node $(nvc) 개, 래퍼 생존 $(kill -0 $W 2>/dev/null && echo yes || echo no)"; fi
  echo "  nav2.log 래퍼 줄: $(grep -a 'nvblox_up' /tmp/nav2.log | tail -3 | cut -c1-100 | tr '\n' '|')"
fi
echo "## 수동 실행 대조(launch 없이)"
for p in $(docker exec $CN bash -c "pgrep -f '^$BIN' || true"); do docker exec $CN kill -9 $p; done; sleep 1
bash ~/ros2_ws/install/rover_navigation/share/rover_navigation/scripts/nvblox_up.sh ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml /tmp/nvblox_diag.log > /tmp/wrap_diag.log 2>&1 &
WP=$!; sleep 6; echo "  수동 래퍼 pid $WP, nvblox_node $(nvc) 개 | $(grep -E '^(SigIgn|SigCgt)' /proc/$WP/status | tr '\n' ' ')"
kill -TERM $WP; for i in $(seq 1 8); do [ "$(nvc)" = "0" ] && break; sleep 1; done; echo "  TERM → $i s 뒤 nvblox_node $(nvc) 개, 래퍼 생존 $(kill -0 $WP 2>/dev/null && echo yes || echo no)"; echo "  wrap_diag.log: $(tail -3 /tmp/wrap_diag.log | cut -c1-100 | tr '\n' '|')"
for p in $(docker exec $CN bash -c "pgrep -f '^$BIN' || true"); do docker exec $CN kill -9 $p; done
echo "## launch 프로세스 신호 처리 확인: ros2 launch 의 자식 생성 방식"
python3 - <<'PY'
import inspect, launch.actions.execute_process as ep
src = inspect.getsource(ep)
for key in ('start_new_session', 'preexec_fn', 'send_signal', 'killpg', 'SIGINT', 'sigterm_timeout'):
    print('  %-18s %s' % (key, src.count(key)))
PY
