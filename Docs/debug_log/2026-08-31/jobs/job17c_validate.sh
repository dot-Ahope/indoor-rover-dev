#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== foxglove 1개로 정리 ==="
pkill -9 -f foxglove_bridge; sleep 3
setsid nohup ros2 launch rover_bringup foxglove.launch.py > /tmp/fg.log 2>&1 &
sleep 6
echo "  foxglove 프로세스 수: $(pgrep -f foxglove_bridge | wc -l)"
echo "=== joy 정리(cmd_vel 단독화) ==="
pkill -f joy_linux; pkill -f teleop_twist_joy; sleep 1
DPID=$(pgrep -f scan_deskew | head -1); echo "  deskew pid=$DPID"
echo "=== 회전 스크립트(15s) 백그라운드 기동 ==="
cat > /tmp/rot.py << 'PY'
import math,time,numpy as np,rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
rclpy.init();n=rclpy.create_node('rot')
LX,LYAW=0.152,math.pi;XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
clr=[None]
def sc(m):
 r=np.array(m.ranges,np.float32);a=m.angle_min+m.angle_increment*np.arange(len(r));ok=np.isfinite(r)&(r>0.05)
 if ok.sum():
  th=a[ok]+LYAW;px=LX+r[ok]*np.cos(th);py=r[ok]*np.sin(th)
  dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]);dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX]);clr[0]=float(np.min(np.sqrt(dx*dx+dy*dy)))
n.create_subscription(LaserScan,'/scan',sc,qos_profile_sensor_data)
pub=n.create_publisher(Twist,'/cmd_vel',10)
tw=Twist();tw.angular.z=0.6;t0=time.time()
while time.time()-t0<15:
 pub.publish(tw);rclpy.spin_once(n,timeout_sec=0.02)
 if clr[0] is not None and clr[0]<0.05: break
t=Twist()
for _ in range(15): pub.publish(t);time.sleep(0.02)
rclpy.shutdown()
PY
setsid nohup python3 /tmp/rot.py > /tmp/rot.log 2>&1 &
sleep 2
echo "=== 회전 중 deskew CPU 샘플(10s 평균) ==="
top -b -n 10 -d 1 -p ${DPID:-1} 2>/dev/null | awk -v p=${DPID:-1} '$1==p{s+=$9;c++} END{if(c)printf "  deskew CPU(회전중) 평균=%.1f%%, 샘플%d\n",s/c,c; else print "  ?"}'
sleep 4
echo "=== 최종 상위 CPU ==="
top -b -n2 -d1 -o %CPU | awk '/PID +USER/{f++} f==2' | head -7 | awk '{printf "  %-16s %5s%%\n",$12,$9}'
echo "  load: $(cat /proc/loadavg | cut -d' ' -f1-3)"
echo -n "  /scan: "; timeout 4 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
