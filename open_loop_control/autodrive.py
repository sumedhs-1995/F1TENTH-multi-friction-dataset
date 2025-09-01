#!/usr/bin/env python

# Import libraries
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import cv2

################################################################################

# RoboRacer class
class RoboRacer:
    def __init__(self):
        # RoboRacer data
        self.id                       = None
        self.throttle                 = None
        self.steering                 = None
        self.speed                    = None
        self.encoder_ticks            = None
        self.encoder_angles           = None
        self.position                 = None
        self.orientation_quaternion   = None
        self.orientation_euler_angles = None
        self.angular_velocity         = None
        self.linear_acceleration      = None
        self.lidar_scan_rate          = None
        self.lidar_range_array        = None
        self.lidar_intensity_array    = None
        self.front_camera_image       = None
        self.lap_count                = None
        self.lap_time                 = None
        self.last_lap_time            = None
        self.best_lap_time            = None
        self.collision_count          = None
        # RoboRacer commands
        self.cosim_mode         = None
        self.posX_command       = None
        self.posY_command       = None
        self.posZ_command       = None
        self.rotX_command       = None
        self.rotY_command       = None
        self.rotZ_command       = None
        self.rotW_command       = None
        self.throttle_command   = None
        self.steering_command   = None
        self.reset_command      = None
    
    # Parse RoboRacer sensor data
    def parse_data(self, data, verbose=False):
        # Actuator feedbacks
        self.throttle = float(data[self.id + " Throttle"])
        self.steering = float(data[self.id + " Steering"])
        # Speed
        self.speed = float(data[self.id + " Speed"])
        # Wheel encoders
        self.encoder_ticks = np.fromstring(data[self.id + " Encoder Ticks"], dtype=int, sep=' ')
        self.encoder_angles = np.fromstring(data[self.id + " Encoder Angles"], dtype=float, sep=' ')
        # IPS
        self.position = np.fromstring(data[self.id + " Position"], dtype=float, sep=' ')
        # IMU
        self.orientation_quaternion = np.fromstring(data[self.id + " Orientation Quaternion"], dtype=float, sep=' ')
        self.orientation_euler_angles = np.fromstring(data[self.id + " Orientation Euler Angles"], dtype=float, sep=' ')
        self.angular_velocity = np.fromstring(data[self.id + " Angular Velocity"], dtype=float, sep=' ')
        self.linear_acceleration = np.fromstring(data[self.id + " Linear Acceleration"], dtype=float, sep=' ')
        # LIDAR
        self.lidar_scan_rate = float(data[self.id + " LIDAR Scan Rate"])
        self.lidar_range_array = np.fromstring(data[self.id + " LIDAR Range Array"], dtype=float, sep=' ')
        self.lidar_intensity_array = np.array([])
        # Cameras
        self.front_camera_image = cv2.cvtColor(np.asarray(Image.open(BytesIO(base64.b64decode(data[self.id + " Front Camera Image"])))), cv2.COLOR_RGB2BGR)
        # Lap data
        self.lap_count = int(data[self.id + " Lap Count"])
        self.lap_time = float(data[self.id + " Lap Time"])
        self.last_lap_time = float(data[self.id + " Last Lap Time"])
        self.best_lap_time = float(data[self.id + " Best Lap Time"])
        self.collision_count = int(float(data[self.id + " Collisions"]))
        if verbose:
            print('\n--------------------------------')
            print('Receive Data from RoboRacer: ' + self.id)
            print('--------------------------------\n')
            # Monitor RoboRacer data
            print('Throttle: {}'.format(self.throttle))
            print('Steering: {}'.format(self.steering))
            print('Speed: {}'.format(self.speed))
            print('Encoder Ticks:  {} {}'.format(self.encoder_ticks[0],self.encoder_ticks[1]))
            print('Encoder Angles: {} {}'.format(self.encoder_angles[0],self.encoder_angles[1]))
            print('Position: {} {} {}'.format(self.position[0],self.position[1],self.position[2]))
            print('Orientation [Quaternion]: {} {} {} {}'.format(self.orientation_quaternion[0],self.orientation_quaternion[1],self.orientation_quaternion[2],self.orientation_quaternion[3]))
            print('Orientation [Euler Angles]: {} {} {}'.format(self.orientation_euler_angles[0],self.orientation_euler_angles[1],self.orientation_euler_angles[2]))
            print('Angular Velocity: {} {} {}'.format(self.angular_velocity[0],self.angular_velocity[1],self.angular_velocity[2]))
            print('Linear Acceleration: {} {} {}'.format(self.linear_acceleration[0],self.linear_acceleration[1],self.linear_acceleration[2]))
            print('LIDAR Scan Rate: {}'.format(self.lidar_scan_rate))
            print('LIDAR Range Array: \n{}'.format(self.lidar_range_array))
            print('LIDAR Intensity Array: \n{}'.format(self.lidar_intensity_array))
            cv2.imshow(self.id + ' Front Camera Preview', cv2.resize(self.front_camera_image, (640, 360)))
            cv2.waitKey(1)
            # Monitor lap data
            print('Lap Count: {}'.format(self.lap_count))
            print('Lap Time: {}'.format(self.lap_time))
            print('Last Lap Time: {}'.format(self.last_lap_time))
            print('Best Lap Time: {}'.format(self.best_lap_time))
            print('Collision Count: {}'.format(self.collision_count))

    # Generate RoboRacer control commands
    def generate_commands(self, verbose=False):
        if verbose:
            print('\n-------------------------------')
            print('Transmit Data to RoboRacer: ' + self.id)
            print('-------------------------------\n')
            # Monitor RoboRacer control commands
            if self.cosim_mode == 0:
                cosim_mode_str = 'False'
            else:
                cosim_mode_str = 'True'
            print('Co-Simulation Mode: {}'.format(cosim_mode_str))
            print('Position Command: X: {} Y: {} Z: {}'.format(self.posX_command, self.posY_command, self.posZ_command))
            print('Rotation Command: X: {} Y: {} Z: {} Z: {}'.format(self.rotX_command, self.rotY_command, self.rotZ_command, self.rotW_command))
            print('Throttle Command: {}'.format(self.throttle_command))
            print('Steering Command: {}'.format(self.steering_command))
            print('Reset Command: {}'.format(self.reset_command))
        return {str(self.id) + ' CoSim': str(self.cosim_mode),
                str(self.id) + ' PosX': str(self.posX_command), str(self.id) + ' PosY': str(self.posY_command), str(self.id) + ' PosZ': str(self.posZ_command), 
                str(self.id) + ' RotX': str(self.rotX_command), str(self.id) + ' RotY': str(self.rotY_command), str(self.id) + ' RotZ': str(self.rotZ_command), str(self.id) + ' RotW': str(self.rotW_command),
                str(self.id) + ' Throttle': str(self.throttle_command), str(self.id) + ' Steering': str(self.steering_command), 'Reset': str(self.reset_command)}
    
################################################################################