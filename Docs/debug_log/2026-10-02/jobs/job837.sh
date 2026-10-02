#!/bin/bash
cd ~/rf2o_ws/src/rf2o_laser_odometry
grep -n "laser_pose_on_robot\|LaserPoseOnTheRobot\|robot_pose_\|laser_pose_\|PoseUpdate\|kai_loc_\|kai_abs_\|setLaserPose\|getYaw\|tf_laser" src/*.cpp include/*/*.h | head -40
sed -n '/void CLaserOdometry2D::PoseUpdate/,/^}/p' src/CLaserOdometry2D.cpp | head -60
