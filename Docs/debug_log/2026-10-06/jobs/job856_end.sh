#!/bin/bash
pkill -INT -f "ros2 bag record -o /tmp/bag_step1"; sleep 4
cd /tmp && tar -czf /tmp/bag_step1.tgz bag_step1 && ls -la /tmp/bag_step1.tgz && cp /tmp/step_state.json /tmp/step_state_1.json
