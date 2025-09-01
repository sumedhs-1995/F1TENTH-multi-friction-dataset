#!/usr/bin/env python

# Import libraries
import socketio
import eventlet
from flask import Flask
import autodrive

################################################################################

# Initialize vehicle(s)
roboracer_1 = autodrive.RoboRacer()
roboracer_1.id = 'V1'

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

        # Co-simulation mode
        roboracer_1.cosim_mode = 0
        # Pose commands (only if cosim_mode==1)
        roboracer_1.posX_command = 1
        roboracer_1.posY_command = 1
        roboracer_1.posZ_command = 0.01
        roboracer_1.rotX_command = 0
        roboracer_1.rotY_command = 0
        roboracer_1.rotZ_command = 0
        roboracer_1.rotW_command = 1
        # Control commands (only if cosim_mode==0)
        roboracer_1.throttle_command = 0.1 # Throttle [-1, 1]
        roboracer_1.steering_command = steering_cmd # Steering [-1, 1]
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
    app = socketio.Middleware(sio, app) # Wrap flask application with socketio's middleware
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app) # Deploy as an eventlet WSGI server
