#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== Nav2 상태 재확인 ==="
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "  %-20s " "$nd"; timeout 8 ros2 lifecycle get "$nd" 2>/dev/null || echo "조회실패"
done
echo -n "  local_costmap: "; timeout 8 ros2 topic hz /local_costmap/costmap 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행"
echo -n "  global_costmap: "; timeout 8 ros2 topic hz /global_costmap/costmap 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행"
echo ""
echo "=== 전방 형상 프로파일 (로버 기준, 중심으로부터 거리) ==="
python3 - << 'PY'
import math, numpy as np, rclpy, time
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMAX,YMAX=0.25,0.165
rclpy.init(); n=rclpy.create_node('pf'); acc=[]
n.create_subscription(LaserScan,'/scan',lambda x: acc.append(x) if len(acc)<5 else None,qos_profile_sensor_data)
t0=time.time()
while len(acc)<5 and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
PX=[];PY=[]
for m in acc:
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12); th=a[ok]+LYAW
    PX.append(LX+r[ok]*np.cos(th)); PY.append(r[ok]*np.sin(th))
px=np.concatenate(PX); py=np.concatenate(PY)
dc=np.hypot(px,py); ang=np.degrees(np.arctan2(py,px))
print("  각도(+좌/-우)  최근접거리")
for c in range(-70,71,10):
    d=np.abs(((ang-c+180)%360)-180); mk=d<6
    if mk.any(): 
        v=np.min(dc[mk])
        bar='#'*int(min(v,2.0)*20)
        print(f"   {c:+4d}deg   {v*100:6.0f}cm  {bar}")
# 로버 폭 밴드 내 전방 최근접 (직진 경로)
band=np.abs(py)<=(YMAX+0.03); sel=band&(px>XMAX)
print(f"\n  ★ 직진 경로상 최근접 장애물: {(np.min(px[sel])-XMAX)*100:.0f}cm (로버 앞면 기준)" if sel.any() else "\n  ★ 직진 경로상 장애물 없음")
# 좌우 통과 가능성: 장애물 옆으로 로버(폭33cm+여유)가 지나갈 틈이 있는지
for side,lo,hi in [("좌측 우회",20,70),("우측 우회",-70,-20)]:
    mk=(ang>=lo)&(ang<hi)
    if mk.any(): print(f"  {side} 방향 최근접: {np.min(dc[mk])*100:.0f}cm")
rclpy.shutdown()
PY
