#!/bin/bash
# 왼손/오른손 판정: 좌측벽(~325mm)·정면벽(~800mm)의 순수 원시 각도(θ_msg) 측정 → 방향성 판정
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
class A(Node):
    def __init__(s): super().__init__('a'); s.acc=[]; s.m=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment)
rclpy.init(); n=A(); t0=time.time()
while time.time()<t0+4: rclpy.spin_once(n,timeout_sec=0.2)
M=np.nanmedian(np.vstack([r for r in n.acc if len(r)==len(n.acc[0])]),axis=0)
a0,ai=n.m; ang=np.degrees(a0+ai*np.arange(len(M)))
print(f"scan: angle_min={math.degrees(a0):.1f} angle_increment={math.degrees(ai):.4f}deg (부호: {'+CCW(오른손 표기)' if ai>0 else '-CW(왼손 표기)'})")
def centroid(lo,hi,label):
    m=np.isfinite(M)&(M>=lo)&(M<hi)
    if m.sum()<3: print(f"  {label}: 검출 실패({m.sum()} beams, {lo}-{hi}m)"); return None
    a=ang[m]
    # 원형 가중(거리 가까울수록 신뢰) 중심
    cx=np.sum(np.cos(np.radians(a))); cy=np.sum(np.sin(np.radians(a)))
    c=math.degrees(math.atan2(cy,cx))
    print(f"  {label}: raw θ={c:+.0f}deg  (범위 {a.min():+.0f}..{a.max():+.0f}, {m.sum()} beams, dist {np.nanmedian(M[m]):.2f}m)")
    return c
print("거리 밴드로 두 벽 분리:")
thL=centroid(0.25,0.45,"좌측벽(~325mm)")
thF=centroid(0.65,0.95,"정면벽(~800mm)")
if thL is not None and thF is not None:
    d=((thL-thF+180)%360)-180
    print(f"\nθ_L - θ_F = {d:+.0f} deg   (ROS: 좌측-정면 = +90 이어야 오른손 일치)")
    if abs(d-90)<45:
        print("=> 오른손 일치 ✅ — 순수 회전으로 해결. yaw = -θ_F(정면→0) 스냅:")
        snap=round(-thF/90.)*90; print(f"   lidar_yaw = {math.radians(snap):+.4f} rad ({snap:+d} deg)")
    elif abs(d+90)<45:
        print("=> 왼손(거울) ✗ — 순수 yaw로 불가. 스캔 뒤집기 필요:")
        print("   rplidar 'inverted:=true' (또는 angle 부호 반전) 후 다시 yaw 조정.")
        print(f"   뒤집으면 θ'=-θ: 좌측벽 {-thL:+.0f}, 정면벽 {-thF:+.0f} → yaw=-(-θ_F)={ -round(-(-thF)/90.)*90:+d}deg 예상")
    else:
        print(f"=> 애매({d:+.0f}) — 배치 재확인(좌측/정면 벽 거리 명확히) 후 재측정")
n.destroy_node(); rclpy.shutdown()
PY
