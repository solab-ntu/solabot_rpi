#!/usr/bin/env python

'''

'''
import rospy
from geometry_msgs.msg import Twist, Vector3
from std_msgs.msg import Float32, Float32MultiArray
import time
import serial

from dynamic_reconfigure.server import Server
# the letters before "Config" should be the same as 3rd argument in gen.generate in .cfg
from solabot_rpi.cfg import decode_vel_serial_outConfig

class SERIAL:


    def __init__(self):

        # general
        self.last_recieved_stamp = None
    	self.pub = rospy.Publisher('cmd_serial', Float32MultiArray, queue_size=1)
        # cmd_vel
        self.last_received_linear = Vector3()
        self.last_received_angular = Vector3()

        # serial
        self.ser = serial.Serial(
        # port='/dev/ttyUSB0',  # PC
        port='/dev/ttyS0',      # rpi
        baudrate = 115200,
        bytesize = serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        timeout = 1
        )

        # dynamic rqt
        self.linear_x_gain = rospy.get_param('~linear_x_gain', 1.0)
        self.linear_y_gain = rospy.get_param('~linear_y_gain', 1.0)
        self.angular_z_gain = rospy.get_param('~angular_z_gain', 1.0)

        # dynamic reconfig
        srv = Server(decode_vel_serial_outConfig, self.dynamic_reconfig_callback)

        # Set the update rate
        rospy.Timer(rospy.Duration(.05), self.timer_callback) # 20hz

        # Set subscribers
        rospy.Subscriber('cmd_vel', Twist, self.sub_cmdvel_update)

    def dynamic_reconfig_callback(self, config, level):
        self.linear_x_gain = config["linear_x_gain"]
        self.linear_y_gain = config["linear_y_gain"]
        self.angular_z_gain = config["angular_z_gain"]
        return config

    def sub_cmdvel_update(self, msg):
        self.last_recieved_stamp = rospy.Time.now()

        # Extract our current cmd_vel information
        self.last_received_linear = msg.linear
        self.last_received_angular = msg.angular
        

    def timer_callback(self, event):
        if self.last_recieved_stamp is None:
            return

        ### decode (according to the manuel of the mecanum car)
	### note that the 'y direction' in the manual is pointing forwards

        #direction
        x_dir = 0 if self.last_received_linear.x > 0 else 1
        y_dir = 1 if self.last_received_linear.y > 0 else 0
        yaw_dir = 0 if self.last_received_angular.z > 0 else 1

        #-------------head, head, mode,x_high,x_low,y_high,y_low,z_high,z_low,direction
        serial_list = [0xff, 0xfe, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        serial_list[4] = int(abs(self.last_received_linear.y*87.76*self.linear_y_gain))
        serial_list[6] = int(abs(self.last_received_linear.x*79.04*self.linear_x_gain))
        serial_list[8] = int(abs(self.last_received_angular.z*97.17*self.angular_z_gain))
        serial_list[9] = 4*y_dir + 2*x_dir + yaw_dir

        # serail write
        values = bytearray(serial_list)
        self.ser.write(values)
        #time.sleep(17.1)

        # for debug
        cmd_serial = Float32MultiArray()
        cmd_serial.data = [0, 0, 0, 0, 0, 0]
        cmd_serial.data[0] = serial_list[6]
        cmd_serial.data[1] = serial_list[4]
        cmd_serial.data[2] = serial_list[8]
        cmd_serial.data[3] = x_dir
        cmd_serial.data[4] = y_dir
        cmd_serial.data[5] = yaw_dir
        self.pub.publish(cmd_serial)

# Start the node
if __name__ == '__main__':
    rospy.init_node("decode_serial")
    node = SERIAL()
    rospy.spin()


