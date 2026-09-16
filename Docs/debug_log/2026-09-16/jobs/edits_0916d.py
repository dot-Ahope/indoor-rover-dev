# 2026-09-16 저녁: DDS 를 루프백에 고정(IP 변경 면역) + 러너/잡에 프로파일 export + stuck_shadow
import sys, re, glob, os
sp = sys.argv[1]; root = 'F:/6_Indoor_Rover/Rover/'
XML_JET = '$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml'
EXPORT = 'export FASTRTPS_DEFAULT_PROFILES_FILE=' + XML_JET + ';'

def edit(path, pairs, must=True):
    s = open(path, encoding='utf-8').read(); n_ok = 0
    for old, new in pairs:
        c = s.count(old)
        if c != 1:
            if must: raise SystemExit('패턴 %d회: %s :: %s' % (c, path, old[:60]))
            continue
        s = s.replace(old, new); n_ok += 1
    open(path, 'w', encoding='utf-8', newline='\n').write(s)
    print('edited %s (%d)' % (os.path.basename(path), n_ok))

# 1) XML: 루프백 화이트리스트
edit(root + 'ros2_ws/src/rover_bringup/config/fastdds_udp_only.xml', [
    ('''      <transport_descriptor>
        <transport_id>udp_only_transport</transport_id>
        <type>UDPv4</type>
      </transport_descriptor>''',
     '''      <transport_descriptor>
        <transport_id>udp_only_transport</transport_id>
        <type>UDPv4</type>
        <!-- 2026-09-16: 루프백에 고정. Wi-Fi AP 가 Jetson 을 끊어(reason 2) 다른 SSID 로 붙으면 IP 가
             192.168.0.101 → 172.30.1.8 로 바뀌는데, 이미 떠 있던 참가자는 옛 IP 로케이터를 계속 광고해
             그 뒤에 뜬 노드(나 새 셸)와 데이터를 주고받지 못한다(09-16 mp4 직후: /scan·/wheel_odom 무수신,
             Nav2 activating 정지). 같은 호스트 안에서만 통신하므로 127.0.0.1 만 쓰면 IP 변화에 면역이다.
             (ROS_LOCALHOST_ONLY 는 rmw 가 SHM 을 다시 켜므로 쓰지 않는다 — 위 SHM 사고 참조) -->
        <interfaceWhiteList>
          <address>127.0.0.1</address>
        </interfaceWhiteList>
      </transport_descriptor>'''),
])
# 2) base.launch.py: 에이전트 컨테이너에도 같은 프로파일 (마운트 + env)
edit(root + 'ros2_ws/src/rover_bringup/launch/base.launch.py', [
    ("             '--net', 'host',\n             '--device', f'{rover_dev}:/dev/rover',\n",
     "             '--net', 'host',\n"
     "             # 2026-09-16: 에이전트의 DDS 참가자도 루프백 고정 프로파일을 쓴다(호스트 노드와 같은 XML 을 마운트).\n"
     "             #   안 하면 에이전트는 Wi-Fi IP 를 광고하고 호스트 노드는 127.0.0.1 만 쓰므로 /cmd_vel 이 보드에 못 간다.\n"
     "             '-v', f'{_FASTDDS_XML}:/fastdds_udp_only.xml:ro',\n"
     "             '-e', 'FASTRTPS_DEFAULT_PROFILES_FILE=/fastdds_udp_only.xml',\n"
     "             '--device', f'{rover_dev}:/dev/rover',\n"),
])
# 3) job 스크립트: export + nav2 launch 에 stuck_shadow
for name in ('job240_clean.sh', 'job249_nav2only.sh', 'job223_btdeploy.sh', 'job156_stop.sh', 'job254_s4run.sh', 'job231_drive.sh'):
    p = sp + '/' + name
    s = open(p, encoding='utf-8').read()
    if 'FASTRTPS_DEFAULT_PROFILES_FILE' not in s:
        s = s.replace('source /opt/ros/humble/setup.bash', EXPORT + ' source /opt/ros/humble/setup.bash', 1)
    if name in ('job240_clean.sh', 'job249_nav2only.sh'):
        s = s.replace('setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &',
                      '# 09-16: MPPI 튜닝 주행 동안 stuck_monitor 는 관찰만(mp4 에서 떨림 명령을 STUCK 으로 오판해 18 s 에 취소). 진행 감시는 progress checker 25 s + 러너 90 s.\n'
                      'setsid nohup ros2 launch rover_navigation navigation.launch.py stuck_shadow:=true > /tmp/nav2.log 2>&1 &')
    open(p, 'w', encoding='utf-8', newline='\n').write(s); print('job patched', name)
# 4) 러너: ssh 명령 문자열의 source 앞에 export
runners = [f for f in glob.glob(sp + '/run_*.sh')]
n = 0
for p in runners:
    s = open(p, encoding='utf-8').read()
    if 'FASTRTPS_DEFAULT_PROFILES_FILE' in s:
        continue
    t = s.replace('"source /opt/ros/humble/setup.bash;', '"' + EXPORT + ' source /opt/ros/humble/setup.bash;')
    t = t.replace("'source /opt/ros/humble/setup.bash;", "'" + EXPORT + " source /opt/ros/humble/setup.bash;")
    t = t.replace('"bash /tmp/', '"' + EXPORT + ' bash /tmp/')
    t = t.replace('"NAME=$NAME bash /tmp/', '"' + EXPORT + ' NAME=$NAME bash /tmp/')
    if t != s:
        open(p, 'w', encoding='utf-8', newline='\n').write(t); n += 1
print('runners patched', n)
