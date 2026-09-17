#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'sed -n 440,620p /opt/ros/humble/include/nav2_mppi_controller/tools/utils.hpp; echo =====; sed -n 1,140p /opt/ros/humble/include/nav2_mppi_controller/tools/noise_generator.hpp | grep -v "^ *\*\|^ */\*\*\|^$"'
