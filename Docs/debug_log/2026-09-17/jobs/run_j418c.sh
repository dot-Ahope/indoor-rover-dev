#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'M=/opt/ros/humble/include/nav2_mppi_controller/motion_models.hpp; grep -n "predict\|cvx\|cwz\|clip\|applyConstraints" $M | head -20; sed -n "/virtual void predict/,/^  }/p" $M | head -20'
