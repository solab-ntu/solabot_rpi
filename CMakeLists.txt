cmake_minimum_required(VERSION 2.8.3)
project(solabot_rpi)

### Find catkin macros and libraries ###
find_package(catkin REQUIRED COMPONENTS 
	dynamic_reconfigure
	roscpp
	rospy 
	geometry_msgs 
	joy
	tf
	std_msgs
	visualization_msgs
	move_base
	    )


generate_dynamic_reconfigure_options(
 	cfg/decode_vel_serial_out.cfg
)

### Add support for c++11, supported in ROS Kinetic and later version ###
#add_definitions(-std=c+11)

include_directories(${catkin_INCLUDE_DIRS})

catkin_package(
  INCLUDE_DIRS
  CATKIN_DEPENDS roscpp geometry_msgs joy dynamic_reconfigure
  DEPENDS
)


#add_dependencies(cmd_vel_publisher ${PROJECT_NAME}_gencfg)


###########
## Build ##
###########

## Uncomment if the package has a setup.py
#catkin_python_setup()

catkin_install_python(PROGRAMS
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

#############
## Install ##
#############

## Mark executable scripts (Python etc.) for installation
#install(PROGRAMS
#  scripts/jetsoncar_teleop_key
#  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
#)

## Mark executables and/or libraries for installation
#install(TARGETS SOLabot_teleop_joy
# RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
#)

## Mark all other useful stuff for installation
#install(DIRECTORY launch
# DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
#)
