#!/usr/bin/env python

# Import libraries
import socketio
import eventlet
from flask import Flask
import autodrive as autodrive
import pandas as pd
import argparse
import time
from datetime import datetime
import numpy as np
import asyncio
################################################################################

# Initialize vehicle(s)
roboracer_1 = autodrive.RoboRacer()
roboracer_1.id = 'V1'
position_set = False
maneuver_completion_status = False
recording_status = False

# DataFrame
log = pd.DataFrame({"timestamp":[], "throttle":[], "steering":[], "leftTicks":[], "rightTicks":[], 
                   "posX":[], "posY":[], "posZ":[], "roll":[], "pitch":[], "yaw":[], "speed":[],
                   "angX":[], "angY":[], "angZ":[], "accX":[], "accY":[], "accZ":[]})

#
async def DataRecorder(roboracer_1):
    
    global log, position_set, recording_status, maneuver_completion_status
    if position_set == True:
        log1 = pd.DataFrame({"timestamp":[str(datetime.now())], "throttle":[roboracer_1.throttle_command], "steering":[roboracer_1.steering_command*0.5236], 
                            "leftTicks":[roboracer_1.encoder_angles[0]], "rightTicks":[roboracer_1.encoder_angles[1]], 
                            "posX":[roboracer_1.position[0]], "posY":[roboracer_1.position[1]], "posZ":[roboracer_1.position[2]], 
                            "roll":[roboracer_1.orientation_euler_angles[0]], "pitch":[roboracer_1.orientation_euler_angles[1]], "yaw":[roboracer_1.orientation_euler_angles[2]], 
                            "speed":[roboracer_1.speed], "angX":[roboracer_1.angular_velocity[0]], "angY":[roboracer_1.angular_velocity[1]], "angZ":[roboracer_1.angular_velocity[2]], 
                            "accX":[roboracer_1.linear_acceleration[0]], "accY":[roboracer_1.linear_acceleration[1]], "accZ":[roboracer_1.linear_acceleration[2]]})
        # print(log)
        data_log = pd.concat([log, log1], ignore_index=True)
        log = data_log
        print(maneuver_completion_status)
        if maneuver_completion_status == True and recording_status == False:
            log.to_csv("/home/ssathe/F1TENTH-multi-friction-dataset/friction_0_4/skidpad/ccw/throttle_0_02/steering_0_1047/data.csv")
            # log.to_excel("data.xlsx")
            recording_status = True
    await asyncio.sleep(0.01)
    
    
# async def main():
#     task = asyncio.create_task(DataRecorder(roboracer_1))
#     await task
    
    

# Initialize the server
sio = socketio.Server()

# Flask (web) app
app = Flask(__name__) # '__main__'

# Registering "connect" event handler for the server
@sio.on('connect')
def connect(sid, environ):
    print('Connected!')

# Registering "Bridge" event handler for the server
@sio.on('Bridge')
def bridge(sid, data):
    if data:
        
        ########################################################################
        # PERCEPTION
        ########################################################################

        # Vehicle data
        roboracer_1.parse_data(data, verbose=True)

        '''
        Implement peception stack here.
        '''

        ########################################################################
        # PLANNING
        ########################################################################

        '''
        Implement planning stack here.
        '''

        ########################################################################
        # CONTROL
        ########################################################################

        '''
        Implement control stack here.
        '''
        global maneuver_completion_status
        if maneuver == 'straight':
            t_straight = 100e9 # Time for straight maneuver
            # Straight
            if (time.time_ns() - t_start) <= t_straight:
                throttle_cmd = throttle + np.random.normal(0,throttle_noise) # Constant throttle (with noise)
                steering_cmd = 0 + np.random.normal(0,steering_noise) # Zero steering (with noise)
                print("Time : {:.4f} sec | Throttle : {:.2f} % | Steering : {:.4f} rad".format((time.time_ns()-t_start)/1e9, throttle_cmd*100, min(steering_cmd, 0.5236))) # Verbose
            # Stop
            else:
                throttle_cmd = 0 # Zero throttle
                steering_cmd = 0 # Zero steering
                maneuver_completion_status = True
                print('Straight maneuver completed!') # Verbose
        ################################################################################
        # Skidpad maneuver (constant throttle and constant steering)
        if maneuver == 'skidpad':
            t_skidpad = 100e9 # Time for skidpad maneuver
            # Skidpad
            if (time.time_ns() - t_start) <= t_skidpad:
                throttle_cmd = throttle #+ np.random.normal(0,throttle_noise) # Constant throttle (with noise)
                steering_cmd = steering #+ np.random.normal(0,steering_noise) # Constant steering (with noise)
                print("Time : {:.4f} sec | Throttle : {:.2f} % | Steering : {:.4f} rad".format((time.time_ns()-t_start)/1e9, throttle_cmd*100, min(steering_cmd, 0.5236))) # Verbose
            # Stop
            else:
                throttle_cmd = 0 # Zero throttle
                steering_cmd = 0 # Zero steering
                maneuver_completion_status = True
                print('Skidpad maneuver completed!') # Verbose
        ################################################################################
        # Fishhook maneuver (constant throttle and ramp steering)
        elif maneuver == 'fishhook':
            t_fishhook = 100e9 # Time for fishhook maneuver
            # k_fishhook = 6e-12 # Controls steering rate (e.g. 1e-11 steers slower than 1e-10)
            k_fishhook = 1/t_fishhook
            # Fishhook
            if (time.time_ns() - t_start) <= t_fishhook:
                throttle_cmd = throttle + np.random.normal(0,throttle_noise) # Constant throttle (with noise)
                steering_cmd = k_fishhook*(time.time_ns() - t_start) + np.random.normal(0,steering_noise) # Time-dependent ramp steering (with noise)
                print("Time : {:.4f} sec | Throttle : {:.2f} % | Steering : {:.4f} rad".format((time.time_ns()-t_start)/1e9, throttle_cmd*100, min(steering_cmd, 0.5236))) # Verbose
            # Stop
            else:
                throttle_cmd = 0 # Zero throttle
                steering_cmd = 0 # Zero steering
                maneuver_completion_status = True
                print('Fishhook maneuver completed!') # Verbose
        ################################################################################
        # Slalom maneuver (constant throttle and sinusoidal steering)
        elif maneuver == 'slalom':
            t_straight = 10e9 # Time for driving straight
            #t_straight = (0.5/throttle)*1e9 # Throttle-dependent time for driving straight
            t_slalom = 100e9 # Time for slalom maneuver
            #t_slalom = (5/throttle)*1e9 # Throttle-dependent time for slalom maneuver
            k_slalom = 9e-10 # Controls steering rate (e.g. 9e-10 steers slower than 1e-9)
            # Straight
            if (time.time_ns() - t_start) < t_straight:
                print(True)
                throttle_cmd = throttle + np.random.normal(0,throttle_noise) # Constant throttle (with noise)
                steering_cmd = 0 + np.random.normal(0,steering_noise) # Zero steering (with noise)
                print("Time : {:.4f} sec | Throttle : {:.2f} % | Steering : {:.4f} rad".format((time.time_ns()-t_start)/1e9, throttle_cmd*100, min(steering_cmd, 0.5236))) # Verbose
            # Slalom
            elif (time.time_ns() - t_start) >= t_straight and (time.time_ns() - t_start)<= t_slalom:
                throttle_cmd = throttle + np.random.normal(0,throttle_noise) # Constant throttle (with noise)
                steering_cmd = 1.0*np.cos((4*np.pi/(t_slalom - t_straight))*(time.time_ns() - (t_start + t_straight))) + np.random.normal(0,steering_noise) # Time-dependent sinusoidal steering (with noise)
                print("Time : {:.4f} sec | Throttle : {:.2f} % | Steering : {:.4f} rad".format((time.time_ns()-t_start)/1e9, throttle_cmd*100, min(steering_cmd, 0.5236))) # Verbose
            # Stop
            else:
                throttle_cmd = 0 # Zero throttle
                steering_cmd = 0 # Zero steering
                maneuver_completion_status = True
                print('Slalom maneuver completed!') # Verbose

        global position_set, log, recording_status
        if position_set == False:

            # Co-simulation mode
            roboracer_1.cosim_mode = 1
            # Pose commands (only if cosim_mode==1)
            roboracer_1.posX_command = -100.0
            roboracer_1.posY_command = -100.0
            roboracer_1.posZ_command = 0.01
            roboracer_1.rotX_command = 0.0
            roboracer_1.rotY_command = 0.0
            roboracer_1.rotZ_command = 0.9239
            roboracer_1.rotW_command = -0.3827
            position_set = True
        # Control commands (only if cosim_mode==0)
        
        else:
            roboracer_1.cosim_mode = 0
            roboracer_1.throttle_command = throttle_cmd  # Throttle [-1, 1]
            roboracer_1.steering_command = -steering_cmd  # Steering [-1, 1]
            # print(steering_cmd, throttle_cmd)
            # asyncio.run(DataRecorder(roboracer_1))
    
        # Reset command
        roboracer_1.reset_command = False # Reset {True, False}

        ########################################################################

        json_msg = roboracer_1.generate_commands(verbose=True) # Generate vehicle 1 message

        try:
            sio.emit('Bridge', data=json_msg)
        except Exception as exception_instance:
            print(exception_instance)

################################################################################

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description=__doc__) # Argument parser
    argparser.add_argument(
        '-m', '--maneuver',
        metavar='MANEUVER',
        dest='maneuver',
        choices = {'straight','skidpad','fishhook','slalom'},
        default='skidpad',
        help='select maneuver {straight, skidpad, fishhook, slalom}')
    argparser.add_argument(
        '-d', '--direction',
        metavar='DIRECTION',
        dest='direction',
        choices = {'cw','ccw'},
        default='ccw',
        help='select direction {cw, ccw}')
    argparser.add_argument(
        '-t', '--throttle',
        metavar='THROTTLE',
        dest='throttle',
        default=0.00,
        help='set throttle limit [-1, 1] norm%')
    argparser.add_argument(
        '-s', '--steering',
        metavar='STEERING',
        dest='steering',
        default=0.0,
        help='set steering limit [0, 0.5236] rad')
    argparser.add_argument(
        '-tn', '--throttle_noise',
        metavar='THROTTLE_NOISE',
        dest='throttle_noise',
        default=0.0,
        help='set std dev for noisy throttle [0.001, 0.1] norm%')
    argparser.add_argument(
        '-sn', '--steering_noise',
        metavar='STEERING_NOISE',
        dest='steering_noise',
        default=0.0,
        help='set std dev for noisy steering [0.001, 0.1] rad')
    args = argparser.parse_args()   # Parse the command line arguments (CLIs)
    t_start = time.time_ns()        # Record starting time
    maneuver = 'skidpad'            # Load maneuver
    direction = 'cw'               # Load maneuver direction
    throttle = 0.02                 # Load throttle limit
    steering = 0.2                # Load steering limit
    throttle_noise = float(args.throttle_noise) # Load throttle std dev
    steering_noise = float(args.steering_noise) # Load steering std dev
    settings = None
    
    app = socketio.Middleware(sio, app) # Wrap flask application with socketio's middleware
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app) # Deploy as an eventlet WSGI server
